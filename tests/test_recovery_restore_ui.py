import os
import threading
import time
from types import SimpleNamespace

import pytest

from memoria.engine.progress import Cancelled, Progress


def _app():
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ.setdefault("QT_QPA_FONTDIR", r"C:\Windows\Fonts")
    from PySide6.QtGui import QFont
    from PySide6.QtWidgets import QApplication
    from memoria.ui import theme
    app = QApplication.instance() or QApplication([])
    app.setFont(QFont("Segoe UI", 10))
    app.setStyle("Fusion")
    theme.use("light")
    app.setPalette(theme.qpalette())
    app.setStyleSheet(theme.QSS)
    return app


def _resolve(app, controller, conflict, progress=None):
    results, errors = [], []
    def work():
        try:
            results.append(controller.resolve(conflict, progress or Progress()))
        except Exception as error:
            errors.append(error)
    thread = threading.Thread(target=work)
    thread.start()
    deadline = time.monotonic() + 5
    while thread.is_alive() and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(.005)
    thread.join(.2)
    assert not thread.is_alive()
    if errors:
        raise errors[0]
    return results[0]


def _conflict(folder, name="photo.jpg"):
    return SimpleNamespace(folder=folder, sources=[r"C:\Library\.memoria\recovery\batch" + "\\" + name],
                           targets=[folder + "\\" + name])


def test_restore_conflict_choices_are_scoped_to_folder_or_current_operation(monkeypatch, tmp_path):
    from memoria.ui import recovery_restore as ui
    app = _app()
    choices = iter((("rename", "folder"), ("skip", "one"), ("rename", "all"), ("skip", "one")))
    shown = []
    gui_thread = threading.get_ident()
    class ChoiceDialog(ui.ConflictDialog):
        def exec(self):
            assert threading.get_ident() == gui_thread
            decision, scope = next(choices)
            self.scope.setCurrentIndex(self.scope.findData(scope))
            shown.append((decision, scope))
            if len(shown) == 1:
                self.show()
                app.processEvents()
                assert self.grab().save(str(tmp_path / "recovery-restore-conflict.png"))
            (self.keep_btn if decision == "rename" else self.skip_btn).click()
            return self.result()
    monkeypatch.setattr(ui, "ConflictDialog", ChoiceDialog)
    controller = ui.ConflictController()
    try:
        assert _resolve(app, controller, _conflict(r"C:\Library\A")) == "rename"
        assert _resolve(app, controller, _conflict(r"c:\library\a", "second.jpg")) == "rename"
        assert _resolve(app, controller, _conflict(r"C:\Library\B")) == "skip"
        assert _resolve(app, controller, _conflict(r"C:\Library\B", "second.jpg")) == "rename"
        assert _resolve(app, controller, _conflict(r"C:\Library\C")) == "rename"
        assert len(shown) == 3
        fresh = ui.ConflictController()
        try:
            assert _resolve(app, fresh, _conflict(r"C:\Library\A")) == "skip"
            assert len(shown) == 4  # policies are not persisted into the next restoration
        finally:
            fresh.shutdown()
            fresh.deleteLater()
    finally:
        controller.shutdown()
        controller.deleteLater()
        app.processEvents()


def test_restore_cancel_wakes_worker_without_waiting_for_a_gui_popup(monkeypatch):
    from memoria.ui import recovery_restore as ui
    app = _app()
    controller = ui.ConflictController()
    cancel = threading.Event()
    progress = Progress(cancel=cancel)
    errors = []
    shown = []
    monkeypatch.setattr(ui.ConflictDialog, "exec", lambda self: shown.append(True) or self.DialogCode.Rejected)
    def work():
        try:
            controller.resolve(_conflict(r"C:\Library\A"), progress)
        except Cancelled:
            errors.append("cancelled")
    thread = threading.Thread(target=work)
    try:
        thread.start()
        cancel.set()
        thread.join(2)
        assert not thread.is_alive() and errors == ["cancelled"]
        app.processEvents()
        assert not shown
        with pytest.raises(RuntimeError, match="GUI thread"):
            controller.resolve(_conflict(r"C:\Library\A"), Progress())
    finally:
        cancel.set()
        controller.shutdown()
        controller.deleteLater()
        app.processEvents()


def test_restore_popup_failure_is_propagated_instead_of_silently_blocking(monkeypatch):
    from memoria.ui import recovery_restore as ui
    app = _app()
    def broken(*_):
        raise ValueError("dialog creation failed")
    monkeypatch.setattr(ui, "ConflictDialog", broken)
    controller = ui.ConflictController()
    try:
        with pytest.raises(RuntimeError, match="dialog creation failed"):
            _resolve(app, controller, _conflict(r"C:\Library\A"))
    finally:
        controller.shutdown()
        controller.deleteLater()
        app.processEvents()


def _wait_preview(app, dialog):
    deadline = time.monotonic() + 10
    while (dialog.bg.running or dialog._loading) and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(.005)
    app.processEvents()
    assert not dialog.bg.running and not dialog._loading, dialog.status.text()


@pytest.mark.parametrize("container", ["20261110-120000-abcdef", "session_20260609_014409"])
def test_unlogged_restore_preview_requires_acknowledgement_and_does_not_move_files(tmp_path, container):
    from memoria.engine.db import Library
    from memoria.ui.recovery_restore import RestoreDialog
    from memoria.ui.tasks import TaskRunner
    from memoria.ui.widgets import AppContext
    app = _app()
    lib = Library(tmp_path)
    source = lib.recovery / container / "Trip" / "photo.jpg"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"Recovery data")
    ctx = AppContext(TaskRunner())
    ctx.set_library(lib)
    dialog = RestoreDialog(None, ctx)
    try:
        dialog.show()
        _wait_preview(app, dialog)
        assert dialog.plan is not None
        item = next(item for item in dialog.plan.items if item.source == source)
        assert item.target == lib.root / "Trip" / "photo.jpg" and item.provenance == "inferred"
        assert dialog.ack.isVisible() and not dialog.go_btn.isEnabled()
        with pytest.raises(ValueError, match="Acknowledge"):
            dialog.selected_plan()
        dialog.ack.setChecked(True)
        assert dialog.go_btn.isEnabled()
        assert len(dialog.selected_plan().items) == 1
        if os.environ.get("MEMORIA_SHOT_LABEL"):
            for index in range(dialog.tree.topLevelItemCount()):
                display = dialog.tree.topLevelItem(index)
                for column in (0, 1):
                    display.setText(column, display.text(column).replace(str(lib.root), r"D:\Sample library"))
        assert dialog.grab().save(str(tmp_path / "recovery-restore-preview.png"))
        dialog.include_unlogged.setChecked(False)
        assert not dialog.go_btn.isEnabled() and not dialog.selected_plan().items
        assert source.read_bytes() == b"Recovery data" and not item.target.exists()
        assert not lib.db.execute("SELECT 1 FROM operations").fetchone()
    finally:
        dialog.shutdown()
        dialog.close()
        dialog.deleteLater()
        app.processEvents()
        lib.close()


def test_ambiguous_recovery_group_can_be_mapped_explicitly_before_confirmation(tmp_path, monkeypatch):
    from PySide6.QtWidgets import QFileDialog
    from memoria.engine.db import Library
    from memoria.ui.recovery_restore import RestoreDialog
    from memoria.ui.tasks import TaskRunner
    from memoria.ui.widgets import AppContext
    app = _app()
    lib = Library(tmp_path)
    source = lib.recovery / "legacy-unknown" / "photo.jpg"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"Unknown origin")
    target_folder = lib.root / "Chosen destination"
    target_folder.mkdir()
    ctx = AppContext(TaskRunner())
    ctx.set_library(lib)
    dialog = RestoreDialog(None, ctx)
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *args: str(target_folder))
    try:
        dialog.show()
        _wait_preview(app, dialog)
        item = next(item for item in dialog.plan.items if item.source == source)
        assert item.target is None and not dialog.go_btn.isEnabled()
        dialog.tree.setCurrentItem(dialog.tree.topLevelItem(0))
        assert dialog.map_btn.isEnabled()
        dialog.map_btn.click()
        _wait_preview(app, dialog)
        mapped = next(item for item in dialog.plan.items if item.source == source)
        assert mapped.target == target_folder / "photo.jpg" and mapped.provenance == "manual"
        assert not dialog.go_btn.isEnabled()
        dialog.ack.setChecked(True)
        assert dialog.go_btn.isEnabled()
        assert source.read_bytes() == b"Unknown origin" and not mapped.target.exists()
    finally:
        dialog.shutdown()
        dialog.close()
        dialog.deleteLater()
        app.processEvents()
        lib.close()


def test_history_restore_button_restores_logged_and_unlogged_files_with_folder_conflict_policy(tmp_path, monkeypatch):
    from memoria.engine import actions, batch, recovery, scanner
    from memoria.engine.db import Library
    from memoria.ui import recovery_restore as ui
    from memoria.ui.pages.history import HistoryPage
    from memoria.ui.tasks import TaskRunner
    from memoria.ui.widgets import AppContext, MessageDialog
    app = _app()
    lib = Library(tmp_path)
    trip = lib.root / "Trip"
    trip.mkdir()
    original = trip / "photo.jpg"
    original.write_bytes(b"original photo")
    scanner.scan(lib)
    row = dict(lib.file_by_rel("Trip\\photo.jpg"))
    removed = actions.apply(lib, "batch", "Move photo", batch.plan_recycle(lib, [row]))
    assert removed.done == 1
    orphan = lib.recovery / "20261110-000000-abcdef" / "Trip" / "extra.jpg"
    orphan.parent.mkdir(parents=True)
    orphan.write_bytes(b"unlogged photo")
    original.write_bytes(b"existing photo must stay")
    (trip / "extra.jpg").write_bytes(b"existing extra must stay")
    ctx = AppContext(TaskRunner())
    ctx.set_library(lib)
    page = HistoryPage(ctx)
    page.resize(1400, 900)
    errors, dialogs = [], []
    ctx.runner.error.connect(lambda *args: errors.append(args))
    monkeypatch.setattr(MessageDialog, "exec", lambda self: self.DialogCode.Accepted)
    def forbidden_empty(*args, **kwargs):
        raise AssertionError("Restore must not empty Recovery")
    monkeypatch.setattr(actions, "empty_recovery", forbidden_empty)
    real_preview = ui.RestoreDialog
    class Preview(real_preview):
        def exec(self):
            self.show()
            _wait_preview(app, self)
            self.ack.setChecked(True)
            assert self.go_btn.isEnabled()
            self.go_btn.click()
            return self.result()
    class Conflict(ui.ConflictDialog):
        def exec(self):
            dialogs.append(True)
            self.scope.setCurrentIndex(self.scope.findData("folder"))
            self.keep_btn.click()
            return self.result()
    monkeypatch.setattr(ui, "RestoreDialog", Preview)
    monkeypatch.setattr(ui, "ConflictDialog", Conflict)
    try:
        page.show()
        deadline = time.monotonic() + 10
        while not page.restore_rec.isEnabled() and time.monotonic() < deadline:
            app.processEvents()
            time.sleep(.005)
        assert page.restore_rec.isEnabled()
        page.restore_rec.click()
        deadline = time.monotonic() + 15
        while (ctx.runner.busy or page.bg.running or page.op_bg.running) and time.monotonic() < deadline:
            app.processEvents()
            time.sleep(.005)
        app.processEvents()
        assert not ctx.runner.busy and not errors, errors
        assert len(dialogs) == 1
        assert original.read_bytes() == b"existing photo must stay"
        assert (trip / "extra.jpg").read_bytes() == b"existing extra must stay"
        assert (trip / "photo (2).jpg").read_bytes() == b"original photo"
        assert (trip / "extra (2).jpg").read_bytes() == b"unlogged photo"
        assert lib.file_by_rel("Trip\\photo (2).jpg")["id"] == row["id"]
        assert recovery.inspect(lib).files == 0
    finally:
        ctx.runner.cancel()
        ctx.runner.wait()
        page.shutdown()
        page.close()
        page.deleteLater()
        app.processEvents()
        lib.close()


def test_restore_preview_bounds_a_hundred_thousand_entries(tmp_path, monkeypatch):
    from PySide6.QtCore import Qt
    from memoria.engine import recovery_restore
    from memoria.engine.db import Library
    from memoria.ui.recovery_restore import PAGE_SIZE, RestoreDialog
    from memoria.ui.tasks import TaskRunner
    from memoria.ui.widgets import AppContext
    app = _app()
    lib = Library(tmp_path)
    entries = [recovery_restore.RestoreItem(
        source=lib.recovery / "batch" / f"photo-{index}.jpg", target=lib.root / f"photo-{index}.jpg",
        root_id=1, operation_id=index + 1, batch_id="batch", size=1_000_000, mtime=1,
        provenance="history", mapping_group="", relative_path=f"photo-{index}.jpg")
        for index in range(100_000)]
    plan = recovery_restore.RestorePlan(items=entries)
    monkeypatch.setattr(recovery_restore, "preview", lambda lib: plan)
    ctx = AppContext(TaskRunner())
    ctx.set_library(lib)
    dialog = RestoreDialog(None, ctx)
    try:
        dialog.show()
        _wait_preview(app, dialog)
        assert dialog.tree.topLevelItemCount() == PAGE_SIZE
        assert "100,000" in dialog.page_note.text() and dialog.go_btn.isEnabled()
        dialog.next.click()
        assert dialog.tree.topLevelItemCount() == PAGE_SIZE
        assert dialog.tree.topLevelItem(0).data(0, Qt.ItemDataRole.UserRole).source == entries[PAGE_SIZE].source
        assert len(dialog.selected_plan().items) == 100_000
        assert not lib.db.execute("SELECT 1 FROM operations").fetchone()
    finally:
        dialog.shutdown()
        dialog.close()
        dialog.deleteLater()
        app.processEvents()
        lib.close()
