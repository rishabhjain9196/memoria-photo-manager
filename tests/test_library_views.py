import os
import time
from pathlib import Path

from memoria.engine.db import Library


def _app():
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    from PySide6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])


def _wait(app, predicate):
    deadline = time.monotonic() + 10
    while not predicate() and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(.01)
    app.processEvents()
    assert predicate()


def test_library_folder_controls_register_without_moving_originals(tmp_path, monkeypatch):
    from PySide6.QtWidgets import QFileDialog
    from memoria.ui.library_roots import LibraryRootsDialog
    from memoria.ui.tasks import TaskRunner
    from memoria.ui.widgets import AppContext
    app = _app()
    home, added = tmp_path / "home", tmp_path / "phone"
    home.mkdir()
    added.mkdir()
    (added / "photo.jpg").write_bytes(b"untouched original")
    lib = Library(home)
    runner = TaskRunner()
    ctx = AppContext(runner)
    ctx.set_library(lib)
    dialog = LibraryRootsDialog(None, ctx)
    errors = []
    runner.error.connect(lambda *args: errors.append(args))
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *args: str(added))
    try:
        dialog.show()
        dialog.add_btn.click()
        _wait(app, lambda: not runner.busy)
        assert not errors and dialog.changed
        assert dialog.tree.topLevelItemCount() == 2
        assert Path(lib.roots()[1]["path"]) == added
        assert (added / "photo.jpg").read_bytes() == b"untouched original"
        assert not lib.files()  # Registration schedules scanning after this dialog is closed.
    finally:
        dialog.close()
        dialog.deleteLater()
        app.processEvents()
        lib.close()


def test_history_bounds_operations_and_pages_full_batch(tmp_path):
    from PySide6.QtCore import Qt
    from memoria.ui.pages.history import HistoryPage, OP_PAGE
    from memoria.ui.tasks import TaskRunner
    from memoria.ui.widgets import AppContext
    app = _app()
    lib = Library(tmp_path)
    with lib.transaction() as db:
        db.execute("INSERT INTO batches VALUES ('large','2026-01-01','batch','Large change','applied',100000,100000)")
        db.executemany("INSERT INTO operations(batch_id,seq,op,src,dst,size,status,src_key) "
                       "VALUES ('large',?,'copy',?,?,1,'done','source.jpg')",
                       ((i, str(tmp_path / "source.jpg"), str(tmp_path.parent / f"export-{i}.jpg"))
                        for i in range(100_000)))
    ctx = AppContext(TaskRunner())
    ctx.set_library(lib)
    page = HistoryPage(ctx)
    page.resize(1400, 900)
    try:
        page.show()
        _wait(app, lambda: page.ops.topLevelItemCount() == OP_PAGE)
        assert page._op_count == 100_000 and page.undo_btn.isEnabled()
        assert "100,000 steps" in page.detail.text()
        page.op_next.click()
        _wait(app, lambda: "501-" in page.op_note.text())
        assert page.ops.topLevelItemCount() == OP_PAGE
        assert page.ops.topLevelItem(0).data(0, Qt.ItemDataRole.UserRole)["seq"] == 500
    finally:
        page.shutdown()
        page.close()
        page.deleteLater()
        app.processEvents()
        lib.close()


def test_health_large_results_bound_widgets(tmp_path):
    from PySide6.QtCore import Qt
    from memoria.engine.health import HealthReport
    from memoria.ui.pages.health import HealthPage
    from memoria.ui.tasks import TaskRunner
    from memoria.ui.widgets import AppContext
    app = _app()
    lib = Library(tmp_path)
    ctx = AppContext(TaskRunner())
    ctx.set_library(lib)
    health = HealthPage(ctx)
    try:
        health._show(HealthReport(counts={"edited": 100_000}, checked=100_000,
                                 problems=[{"rel_path": f"p{i}.jpg", "status": "edited", "detail": ""}
                                           for i in range(100_000)]))
        assert health.tree.topLevelItemCount() == 500
        health.next.click()
        assert health.tree.topLevelItem(0).data(1, Qt.ItemDataRole.UserRole) == "p500.jpg"
    finally:
        health.deleteLater()
        app.processEvents()
        lib.close()


def test_compare_page_shows_grouped_panes_and_copies_only_the_delta(tmp_path, monkeypatch):
    from PySide6.QtCore import Qt
    from memoria.engine import libsync, scanner
    from memoria.ui.pages import compare as compare_ui
    from memoria.ui.tasks import TaskRunner
    from memoria.ui.widgets import AppContext
    app = _app()
    home, phone, drive = tmp_path / "laptop", tmp_path / "phone", tmp_path / "drive"
    files = {home: {r"Backup\a.jpg": b"a", r"Backup\b.jpg": b"b"},
             phone: {r"DCIM\a.jpg": b"a", r"DCIM\b.jpg": b"b", r"DCIM\new.jpg": b"new", r"Trip\t1.jpg": b"t1",
                     r"Trip\t2.jpg": b"t2"},
             drive: {r"Old\a.jpg": b"a", r"Old\x.jpg": b"xx"}}
    for root, content in files.items():
        for name, data in content.items():
            (root / name).parent.mkdir(parents=True, exist_ok=True)
            (root / name).write_bytes(data)
    lib = Library(home)
    scanner.scan(lib)
    runner = TaskRunner()
    ctx = AppContext(runner)
    ctx.set_library(lib)
    page = compare_ui.ComparePage(ctx)
    page.resize(1500, 950)
    errors = []
    runner.error.connect(lambda *args: errors.append(args))
    monkeypatch.setattr(compare_ui.PlanReviewDialog, "exec", lambda self: self.DialogCode.Accepted)
    try:
        page.show()
        page.paths[0].setText(str(phone))
        page.add_c.click()
        page.paths[1].setText(str(drive))
        page.cmp_btn.click()
        _wait(app, lambda: page.result is not None and not runner.busy)
        assert not errors and page.result.count == 3
        assert all(pane.isVisible() for pane in page.panes)
        only_b = next(i for i in range(page.filters.count())
                      if page.filters.item(i).data(Qt.ItemDataRole.UserRole) == ("only", 1))
        page.filters.setCurrentRow(only_b)
        tree = page.panes[1].tree
        top = {tree.topLevelItem(i).text(0): tree.topLevelItem(i).text(1) for i in range(tree.topLevelItemCount())}
        assert top["Trip"].startswith("all 2") and top["DCIM"].startswith("1 of 3")
        assert page.panes[0].tree.topLevelItemCount() == 0
        page.venn.region_clicked.emit(0b011)
        assert page.view == ("region", 0b011) and "not in C" in page.view_title.text()

        page.source.setCurrentIndex(page.source.findData(1))
        page.target.setCurrentIndex(page.target.findData(0))
        assert "3 files" in page.copy_summary.text()
        from memoria.ui import sync_review

        def choose(dialog):
            dialog.show()
            top = dialog.tree.topLevelItem(0)
            folders = {top.child(i).text(0): top.child(i) for i in range(top.childCount())}
            assert set(folders) == {"DCIM", "Trip"} and folders["Trip"].text(2) == "2"
            folders["Trip"].setCheckState(0, Qt.CheckState.Unchecked)   # keep the trip only on the phone
            assert top.checkState(0) == Qt.CheckState.PartiallyChecked and top.text(2) == "1 of 3"
            folders["DCIM"].setExpanded(True)
            assert folders["DCIM"].child(0).text(0) == "new.jpg" and "Backup" in folders["DCIM"].child(0).text(3)
            assert dialog.remember.isChecked() and dialog.ok.text() == "Copy 1 file"
            return dialog.DialogCode.Accepted
        monkeypatch.setattr(sync_review.CopyReviewDialog, "exec", choose)
        page.copy_btn.click()
        _wait(app, lambda: (home / "Backup" / "new.jpg").exists() and not runner.busy)
        assert not (home / "Trip").exists() and (phone / "DCIM" / "new.jpg").exists() and not errors
        _wait(app, lambda: page.result is not None and not runner.busy and "Nothing new to copy" in page.copy_summary.text())
        assert "2 files" in page.copy_summary.text() and "keep only where they are" in page.copy_summary.text()

        page.remove_from.setCurrentIndex(page.remove_from.findData(2))
        assert "1 file" in page.remove_summary.text()
        page.remove_btn.click()
        _wait(app, lambda: not (drive / "Old" / "a.jpg").exists() and not runner.busy)
        assert (drive / "Old" / "x.jpg").exists() and list((drive / ".memoria" / "recovery").rglob("a.jpg"))

        monkeypatch.setattr(compare_ui.QInputDialog, "getText", lambda *args, **kwargs: ("Phone backup", True))
        page.save_profile.click()
        saved = libsync.load_profiles(lib)
        assert saved[0]["name"] == "Phone backup" and saved[0]["others"] == [str(phone), str(drive)]
    finally:
        page.close()
        page.deleteLater()
        app.processEvents()
        lib.close()
