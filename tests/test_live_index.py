"""Use blocked analysis to prove browsing works before indexing completes."""
import os
import threading
import time

import pytest
from PIL import Image

from memoria.engine import catalogue, scanner
from memoria.engine.db import Library
from memoria.engine.hashing import full_hash


def test_ready_filter_hides_unprocessed_rows_but_keeps_existing_cache(tmp_path):
    lib = Library(tmp_path)
    try:
        with lib.transaction() as db:
            db.execute("INSERT INTO files(rel_path,folder,name,ext,kind,size,mtime,analyzed) "
                       "VALUES ('cached.jpg','','cached.jpg','.jpg','image',10,1,1)")
            db.execute("INSERT INTO files(rel_path,folder,name,ext,kind,size,mtime,analyzed) "
                       "VALUES ('pending.jpg','','pending.jpg','.jpg','image',10,1,0)")
        rows, total, _ = catalogue.page(lib, catalogue.Filters(ready_only=True))
        assert total == 1 and rows[0]["name"] == "cached.jpg"
        # Old cached rows remain viewable even if extended metadata is awaiting a refresh.
        assert catalogue.browse_progress(lib) == {"ready": 1, "pending": 2, "problems": 0}
    finally:
        lib.close()


@pytest.mark.parametrize("cancel", [False, True])
def test_live_photos_before_completion_keep_view_stable_and_actions_locked(tmp_path, monkeypatch, cancel):
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ.setdefault("QT_QPA_FONTDIR", r"C:\Windows\Fonts")
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication, QMenu
    from memoria.ui.main_window import MainWindow
    from memoria.ui import widgets
    from memoria.ui.pages import photos as photos_module

    app = QApplication.instance() or QApplication([])
    root = tmp_path / "library"
    root.mkdir()
    for i, color in enumerate(("red", "blue")):
        Image.new("RGB", (48, 32), color).save(root / f"{i}.jpg")
    before = {p.name: full_hash(p) for p in root.glob("*.jpg")}
    release = threading.Event()
    slow_started = threading.Event()
    original = scanner._analyze_one

    def blocked(path, kind, name, mtime, *rest):
        if name == "1.jpg":
            slow_started.set()
            if not release.wait(20):
                raise RuntimeError("Test analysis gate timed out")
        return original(path, kind, name, mtime, *rest)

    monkeypatch.setattr(scanner, "_analyze_one", blocked)
    monkeypatch.setattr(widgets.MessageDialog, "exec", lambda self: 0)
    window = MainWindow()
    window.resize(1440, 900)
    window._index_refresh.setInterval(50)
    errors = []
    window.runner.error.connect(lambda *args: errors.append(args))
    window.show()

    def wait_for(predicate, seconds=8):
        until = time.monotonic() + seconds
        while not predicate() and time.monotonic() < until:
            app.processEvents()
            time.sleep(.01)
        app.processEvents()
        assert predicate(), errors

    try:
        window.open_library(str(root), "photos")
        page = window.page("photos")
        wait_for(lambda: slow_started.is_set() and len(page.grid.items()) == 1)
        assert window.runner.busy and window.ctx.indexing
        assert page.isEnabled() and page.grid.items()[0]["name"] == "0.jpg"
        assert "ready to browse" in page.index_note.text()
        assert window.task_pct.text() == "50%"  # analysis must not retain the scan phase's 100%
        assert window.ctx.library.file_by_rel("1.jpg")["analyzed"] == 0
        page.grid.setCurrentIndex(page.grid.model_.index(0))
        app.processEvents()
        selected = page.selected()[0]["id"]
        preview = page.preview.row
        assert not page.b_recycle.isEnabled()
        assert not any(action.isEnabled() for action in
                       (page.a_copy, page.a_move, page.a_edit, page.a_story, page.a_video, page.a_album))
        page.recycle_selected()
        page.add_to_album("Must not be created")
        page._to_editor()
        assert not window.ctx.edit_selection
        assert window.ctx.library.db.execute("SELECT COUNT(*) FROM albums").fetchone()[0] == 0
        assert window.ctx.library.db.execute("SELECT COUNT(*) FROM operations").fetchone()[0] == 0
        states = {}
        class InspectMenu(QMenu):
            def exec(self, *args):
                states.update({action.text(): action.isEnabled() for action in self.actions() if not action.isSeparator()})
        monkeypatch.setattr(photos_module, "QMenu", InspectMenu)
        page._menu(page.grid.visualRect(page.grid.model_.index(0)).center())
        assert states["View"] and states["Show in folder"]
        assert all(not enabled for text, enabled in states.items()
                   if text not in ("View", "Open in default app", "Show in folder"))

        seen = []
        real_exec = widgets.Viewer.exec
        def view_exec(viewer):
            seen.append(viewer.current["id"])
            QTimer.singleShot(30, viewer.accept)
            return real_exec(viewer)
        monkeypatch.setattr(widgets.Viewer, "exec", view_exec)
        page._view(page.grid.items()[0])
        assert seen == [selected] and window.runner.busy
        window.go("albums")
        assert not window.page("albums").isEnabled()
        window.go("photos")
        assert page.isEnabled()
        window.lib_label.setText("<b>Sample library</b><br>Generated test media")
        assert window.grab().save(str(tmp_path / "live-index.png"))

        if cancel:
            window.runner.cancel()
        release.set()
        wait_for(lambda: not window.runner.active and not window.ctx.indexing)
        assert not errors
        assert page.selected()[0]["id"] == selected and page.preview.row is preview
        assert page._live_deferred and page.update_view.isVisible()
        assert page.b_recycle.isEnabled()
        assert catalogue.browse_progress(window.ctx.library)["ready"] >= 1
        if cancel:
            window.index_library()
            wait_for(lambda: not window.runner.active and not window.ctx.indexing)
        page.update_view.click()
        wait_for(lambda: not page._query.running)
        assert {row["name"] for row in page.grid.items()} == {"0.jpg", "1.jpg"}
        assert not page.selected() and not page._live_deferred
        assert {p.name: full_hash(p) for p in root.glob("*.jpg")} == before
    finally:
        release.set()
        window.close()
        window.deleteLater()
        app.processEvents()


def test_thumbnail_invalidation_keeps_budget_correct(tmp_path):
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    from PySide6.QtWidgets import QApplication
    from memoria.ui.tasks import TaskRunner
    from memoria.ui.widgets import AppContext
    app = QApplication.instance() or QApplication([])
    Image.new("RGB", (32, 24), "red").save(tmp_path / "photo.jpg")
    lib = Library(tmp_path)
    try:
        scanner.index(lib)
        ctx = AppContext(TaskRunner())
        ctx.set_library(lib)
        fid = lib.files()[0]["id"]
        assert ctx.thumbs.get(fid)
        assert ctx.thumbs.bytes > 0
        ctx.thumbs.invalidate([fid])
        assert ctx.thumbs.bytes == 0
        assert ctx.thumbs.get(fid)
    finally:
        lib.close()
        app.processEvents()
