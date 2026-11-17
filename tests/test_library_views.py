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


def test_health_and_compare_large_results_bound_widgets_and_keep_all_selection(tmp_path):
    from PySide6.QtCore import Qt
    from memoria.engine.compare import CompareResult
    from memoria.engine.health import HealthReport
    from memoria.ui.pages.compare import ComparePage
    from memoria.ui.pages.health import HealthPage
    from memoria.ui.tasks import TaskRunner
    from memoria.ui.widgets import AppContext
    app = _app()
    lib = Library(tmp_path)
    ctx = AppContext(TaskRunner())
    ctx.set_library(lib)
    health = HealthPage(ctx)
    compare = ComparePage(ctx)
    try:
        health._show(HealthReport(counts={"edited": 100_000}, checked=100_000,
                                 problems=[{"rel_path": f"p{i}.jpg", "status": "edited", "detail": ""}
                                           for i in range(100_000)]))
        assert health.tree.topLevelItemCount() == 500
        health.next.click()
        assert health.tree.topLevelItem(0).data(1, Qt.ItemDataRole.UserRole) == "p500.jpg"
        rows = [{"id": i + 1, "rel_path": f"p{i}.jpg", "size": 1} for i in range(100_000)]
        compare._show(CompareResult(tmp_path / "backup", only_here=rows, bytes_only_here=100_000))
        assert compare.here.topLevelItem(0).childCount() == 200
        assert compare.here_pages.selected_count == 100_000
        compare.here.topLevelItem(0).child(0).setCheckState(0, Qt.CheckState.Unchecked)
        compare.here_pages.next.click()
        assert compare.here_pages.selected_count == 99_999
        compare.here_pages.previous.click()
        assert compare.here.topLevelItem(0).child(0).checkState(0) == Qt.CheckState.Unchecked
    finally:
        health.deleteLater()
        compare.deleteLater()
        app.processEvents()
        lib.close()
