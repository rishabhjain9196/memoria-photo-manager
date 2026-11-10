"""End-to-end UI smoke test: drives every page offscreen, applies a change and undoes it."""
import os
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))


def test_every_page_runs_without_errors(pristine_library, tmp_path):
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    lib = tmp_path / "library"
    shutil.copytree(pristine_library, lib)
    import ui_screenshots
    from memoria.engine import actions
    from memoria.engine.db import Library

    errors = ui_screenshots.run(str(lib), str(tmp_path / "shots"))
    assert errors == []
    shots = {p.stem for p in (tmp_path / "shots").glob("*.png")}
    assert {"01-overview", "03-duplicates", "04-similar", "21-history-after-apply", "22-history-after-undo"} <= shots

    check = Library(lib)
    batches = actions.batches(check)
    kinds = {b["kind"] for b in batches}
    assert {"duplicates", "batch", "edit", "albums", "video"} <= kinds
    for b in batches:
        if b["kind"] == "video":
            outputs = [Path(o["dst"]) for o in actions.operations(check, b["id"]) if o["status"] == "done"]
            assert outputs and all(p.exists() for p in outputs)
            assert actions.undo(check, b["id"]).ok
            assert not any(p.exists() for p in outputs)
    batches = actions.batches(check)
    dup = next(b for b in batches if b["kind"] == "duplicates")
    removed = [o["src"] for o in actions.operations(check, dup["id"]) if o["op"] == "rmdir" and o["status"] == "undone"]
    assert any(p.endswith("Old Laptop") for p in removed)        # a whole duplicate folder was removed, then restored
    assert (lib / "Old Laptop" / "Pictures" / "Family 2020").is_dir()
    assert all(b["status"] == "undone" for b in batches if b["kind"] != "edit")
    edits = [b for b in batches if b["kind"] == "edit"]
    assert len(edits) == 2 and all(b["status"] == "applied" for b in edits)
    created = [Path(o["dst"]) for b in edits for o in actions.operations(check, b["id"])]
    assert created and all(p.exists() and "(edited)" in p.name for p in created)
    before = {p: p.stat().st_size for p in lib.rglob("*") if p.is_file() and ".memoria" not in p.parts and p not in created}
    for b in edits:
        assert actions.undo(check, b["id"]).ok
    assert not any(p.exists() for p in created)               # Undo removes only the edited copies
    after = {p: p.stat().st_size for p in lib.rglob("*") if p.is_file() and ".memoria" not in p.parts}
    assert after == before                                     # originals untouched
    assert actions.recovery_size(check) == (0, 0)
    assert check.db.execute("SELECT COUNT(*) FROM parked_files").fetchone()[0] == 0
    check.close()
    assert {"photos-viewer", "dark-overview", "dark-similar", "07-editor-crop", "07-editor-video"} <= shots
    assert {"13-people", "13-people-lookalike", "14-albums", "14-albums-make"} <= shots
    assert {"insights-storage", "insights-files", "insights-timeline", "insights-india", "insights-world",
            "dark-insights", "photos-largest", "library-filters", "storage-reset", "storage-reset-hard"} <= shots
    assert {"library-filters-video", "library-filters-camera", "photos-video-metadata"} <= shots
    check = Library(lib)
    assert check.db.execute("SELECT COUNT(*) FROM files WHERE iso>0 AND aperture>0 AND exposure_seconds>0").fetchone()[0] > 0
    names = {r[0] for r in check.db.execute("SELECT name FROM people")}
    assert names == {"Abraham Lincoln", "Mark Twain"}                     # named in the People page
    saved = {r[0] for r in check.db.execute("SELECT name FROM albums")}
    assert "Leh, Ladakh · 10–12 Jun 2023" in saved and {"Abraham Lincoln", "Mark Twain"} <= saved
    check.close()
    exported = tmp_path / "Album exports"
    assert exported.is_dir() and not [p for p in exported.rglob("*") if p.is_file()]   # export undone


def test_thumbnail_budget_invalidation_and_single_selection(tmp_path):
    import time
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    from PIL import Image
    from PySide6.QtWidgets import QApplication
    from memoria.engine import scanner, similar
    from memoria.engine.db import Library
    from memoria.ui.tasks import TaskRunner
    from memoria.ui.widgets import AppContext, ThumbCache
    from memoria.ui.pages.photos import PhotosPage
    from memoria.ui.pages.similar import SimilarPage

    app = QApplication.instance() or QApplication([])
    lib = Library(tmp_path)
    ctx = AppContext(TaskRunner())
    ctx.set_library(lib)
    ctx.thumbs = ThumbCache(ctx, max_bytes=256 * 256 * 4)
    try:
        for i in range(3):
            Image.new("RGB", (256, 256), "red").save(tmp_path / f"{i}.jpg")
        scanner.index(lib)
        rows = lib.files()
        for row in rows:
            assert ctx.thumbs.get(row["id"]) is not None
            assert ctx.thumbs.bytes <= ctx.thumbs.max_bytes
        fid = rows[-1]["id"]
        before = ctx.thumbs.get(fid).toImage().pixelColor(0, 0)
        path = lib.abspath(rows[-1]["rel_path"])
        Image.new("RGB", (256, 256), "blue").save(path)
        os.utime(path, (rows[-1]["mtime"] + 10, rows[-1]["mtime"] + 10))
        scanner.index(lib)
        ctx.library_modified.emit()
        assert ctx.thumbs.get(fid).toImage().pixelColor(0, 0) != before
        page = PhotosPage(ctx)
        page.refresh()
        deadline = time.monotonic() + 10
        while page._query.running and time.monotonic() < deadline:
            app.processEvents()
            time.sleep(.005)
        app.processEvents()
        page.grid.setCurrentIndex(page.grid.model_.index(0))
        assert len(page.selected()) == 1
        assert not page.sel_bar.isHidden()
        review = SimilarPage(ctx)
        review.photos._show([similar.rank_group([dict(r) for r in rows[:2]])])
        assert review.photos._planned_rows() == []
        assert not review.photos.apply_btn.isEnabled()
        review.photos._mark_all(True)
        assert len(review.photos._planned_rows()) == 1
        review.deleteLater()
        page.shutdown()
        page.deleteLater()
        app.processEvents()
    finally:
        lib.close()


def test_tidy_protects_sidecars_and_explains_analysis_errors(tmp_path, monkeypatch):
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication
    from memoria.engine import scanner, tidy
    from memoria.engine.db import Library
    from memoria.ui.pages.tidy import TidyPage
    from memoria.ui.tasks import TaskRunner
    from memoria.ui.widgets import AppContext, MessageDialog

    app = QApplication.instance() or QApplication([])
    root = tmp_path / "library"
    root.mkdir()
    (root / "IMG_1.AAE").write_bytes(b"<plist>Apple editing instructions</plist>")
    (root / "IMG_2.HEIF").write_bytes(b"incomplete test photo")
    lib = Library(root)
    runner = TaskRunner()
    ctx = AppContext(runner)
    ctx.set_library(lib)
    page = TidyPage(ctx)
    page.resize(1400, 850)
    page.stale = False
    try:
        scanner.index(lib)
        page.show()
        for error in ("UnidentifiedImageError: codec <HEVC> not available",
                      "RuntimeError: decoder <HEVC> not available"):
            lib.db.execute("UPDATE files SET error=? WHERE rel_path='IMG_2.HEIF'", (error,))
            page._show(tidy.find_tidy(lib))
            app.processEvents()
            assert page.sidecar_note.isVisible() and "1 Apple .AAE" in page.sidecar_note.text()
            assert page.tree.topLevelItemCount() == 1
            group = page.tree.topLevelItem(0)
            assert group.data(0, Qt.ItemDataRole.UserRole) == ("cat", "unreadable")
            child = group.child(0)
            assert child.checkState(0) == Qt.CheckState.Unchecked
            page.tree.setCurrentItem(child)
            assert "not proof of damage" in page.preview.facts.text()
            assert "&lt;HEVC&gt; not available" in page.preview.facts.text()
            assert "codec" in page.preview.facts.text()
            assert not page.apply_btn.isEnabled()
        assert page.grab().save(str(tmp_path / "tidy-sidecars.png"))
        notices = []
        monkeypatch.setattr(MessageDialog, "exec", lambda self: notices.append(self.windowTitle()) or 0)
        monkeypatch.setattr(page, "_selected", lambda: {"other": [dict(lib.file_by_rel("IMG_1.AAE"))]})
        page.apply()
        assert notices == ["Tidy selection needs review"]
        assert not runner.busy
        assert (root / "IMG_1.AAE").read_bytes() == b"<plist>Apple editing instructions</plist>"
        assert (root / "IMG_2.HEIF").read_bytes() == b"incomplete test photo"
    finally:
        page.close()
        page.deleteLater()
        app.processEvents()
        lib.close()


def test_storage_dialog_requires_ack_for_destructive_choices(tmp_path):
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    from PySide6.QtWidgets import QApplication
    from memoria.engine.storage import ResetOptions
    from memoria.ui.storage_dialog import StorageDialog
    app = QApplication.instance() or QApplication([])
    dlg = StorageDialog(None, {"catalogue": 1024, "thumbnails": 2048})
    dlg.show()
    app.processEvents()
    assert dlg.height() <= app.primaryScreen().availableGeometry().height()
    assert dlg.grab().save(str(tmp_path / "storage-reset.png"))
    assert dlg.options() == ResetOptions()
    assert dlg.go_btn.isEnabled()
    dlg.preset(True)
    app.processEvents()
    assert dlg.width() <= app.primaryScreen().availableGeometry().width()
    assert dlg.grab().save(str(tmp_path / "storage-reset-hard.png"))
    assert not dlg.go_btn.isEnabled()
    assert dlg.options().people and dlg.options().albums and dlg.options().health
    dlg.ack.setChecked(True)
    assert dlg.go_btn.isEnabled()
    dlg.preset(False)
    assert not dlg.options().people and not dlg.options().health
    for box in dlg.boxes.values():
        box.setChecked(False)
    assert not dlg.go_btn.isEnabled()
    dlg.deleteLater()
    app.processEvents()


def test_storage_reset_window_flow(tmp_path, monkeypatch):
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    import time
    from PIL import Image
    from PySide6.QtWidgets import QApplication, QDialog
    from memoria.engine import storage
    from memoria.ui.main_window import MainWindow
    from memoria.ui.storage_dialog import StorageDialog
    from memoria.ui.widgets import MessageDialog

    app = QApplication.instance() or QApplication([])
    Image.new("RGB", (32, 24), "red").save(tmp_path / "photo.jpg")
    window = MainWindow()
    errors = []
    window.runner.error.connect(lambda *args: errors.append(args))
    monkeypatch.setattr(MessageDialog, "exec", lambda self: QDialog.DialogCode.Rejected)

    def idle():
        end = time.monotonic() + 30
        while window.runner.busy and time.monotonic() < end:
            app.processEvents()
            time.sleep(.01)
        app.processEvents()
        assert not window.runner.busy and not errors

    try:
        window.open_library(str(tmp_path))
        idle()
        old_id = window.ctx.library.files()[0]["id"]
        monkeypatch.setattr(StorageDialog, "exec", lambda self: QDialog.DialogCode.Accepted)
        window.manage_storage()
        idle()
        assert storage.pending(window.ctx.library) is None
        assert not window.ctx.maintenance
        assert window.stack.isEnabled() and window.storage_btn.isEnabled()
        assert window.current_key == "overview"
        assert window.ctx.library.files()[0]["id"] == old_id
        # A previous process can stop after metadata clearing and before cache clearing.
        storage._clear_catalogue(window.ctx.library, storage.ResetOptions())
        window.open_library(str(tmp_path))
        idle()
        assert storage.pending(window.ctx.library) is None
        assert not window.ctx.maintenance and window.stack.isEnabled()
    finally:
        window.close()
        window.deleteLater()
        app.processEvents()
