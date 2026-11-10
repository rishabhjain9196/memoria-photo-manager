"""Verify notification delivery without sending any real desktop messages."""
import os
import time
from types import SimpleNamespace

import pytest
from PIL import Image


@pytest.fixture
def qt(tmp_path, monkeypatch):
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ.setdefault("QT_QPA_FONTDIR", r"C:\Windows\Fonts")
    from PySide6.QtCore import QObject, QSettings, Signal
    from PySide6.QtGui import QFont
    from PySide6.QtWidgets import QApplication
    from memoria.ui import theme

    class Tray(QObject):
        messageClicked = Signal()
        activated = Signal(object)

        def __init__(self, parent):
            super().__init__(parent)
            self.messages = []
            self.visible = False

        def setIcon(self, icon):
            self.icon = icon

        def setToolTip(self, text):
            self.tooltip = text

        def setContextMenu(self, menu):
            self.menu = menu

        def show(self):
            self.visible = True

        def hide(self):
            self.visible = False

        def showMessage(self, title, text, icon, duration):
            self.messages.append((title, text, icon, duration))

    app = QApplication.instance() or QApplication([])
    app.setFont(QFont("Segoe UI", 10))
    settings = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)
    monkeypatch.setattr(theme, "settings", lambda: settings)
    return app, settings, Tray


@pytest.mark.parametrize("mode,foreground,desktop,recorded", [
    ("background", True, 0, 1), ("background", False, 1, 1),
    ("always", True, 1, 1), ("always", False, 1, 1),
    ("in-app", False, 0, 1), ("off", False, 0, 0),
])
def test_delivery_modes(qt, mode, foreground, desktop, recorded):
    from PySide6.QtWidgets import QMainWindow
    from memoria.ui.notifications import CATEGORIES, NotificationManager
    app, settings, Tray = qt
    owner = QMainWindow()
    tray = Tray(owner)
    manager = NotificationManager(owner, settings, tray=tray, foreground=lambda: foreground)
    try:
        manager.configure(mode, CATEGORIES)
        manager.notify("index_complete")
        assert len(tray.messages) == desktop
        assert len(manager.recent) == manager.unread == recorded
        assert tray.visible == (mode in ("background", "always"))
    finally:
        manager.close()
        owner.close()


def test_preferences_fallback_bounded_history_and_shutdown(qt):
    from PySide6.QtWidgets import QMainWindow
    from memoria.ui.notifications import NotificationManager
    app, settings, Tray = qt
    owner = QMainWindow()
    manager = NotificationManager(owner, settings)
    try:
        assert manager.tray is None  # offscreen must never send OS notifications
        manager.configure("background", ["health"])
        manager.notify("index_complete")
        assert not manager.recent
        for i in range(60):
            manager.notify("health_problems", i + 1)
        assert len(manager.recent) == manager.unread == 50
        assert "60" in manager.recent[0]["text"] and "11" in manager.recent[-1]["text"]
        restored = NotificationManager(owner, settings)
        assert restored.mode == "background" and restored.enabled_events == {"health"}
        assert not restored.recent
        restored.close()
        with pytest.raises(ValueError):
            manager.notify("PRIVATE_FILENAME.jpg")
        with pytest.raises(ValueError):
            manager.notify("health_problems", "PRIVATE_RAW_ERROR")
        manager.close()
        manager.notify("health_problems", 99)
        assert "60" in manager.recent[0]["text"]
        manager.clear()
        assert not manager.recent and not manager.unread
    finally:
        owner.close()


def test_app_modal_counts_as_foreground_but_minimised_does_not(qt, monkeypatch):
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QMainWindow
    from memoria.ui import notifications
    app, settings, Tray = qt
    owner = QMainWindow()
    tray = Tray(owner)
    # An active application can have an inactive main window while its own viewer/dialog has focus.
    active_app = SimpleNamespace(applicationState=lambda: Qt.ApplicationState.ApplicationActive)
    monkeypatch.setattr(notifications, "QApplication", SimpleNamespace(instance=lambda: active_app))
    manager = notifications.NotificationManager(owner, settings, tray=tray)
    try:
        assert not owner.isActiveWindow()
        manager.notify("operation_complete")
        assert not tray.messages
        owner.showMinimized()
        manager.notify("operation_complete")
        assert len(tray.messages) == 1
    finally:
        manager.close()
        owner.close()


def test_settings_dialog_updates_preferences_and_recent_events(qt, tmp_path):
    from PySide6.QtWidgets import QMainWindow
    from memoria.ui import theme
    from memoria.ui.notifications import NotificationManager, NotificationsDialog
    app, settings, Tray = qt
    owner = QMainWindow()
    manager = NotificationManager(owner, settings, tray=Tray(owner), foreground=lambda: True)
    manager.notify("index_complete")
    dialog = NotificationsDialog(owner, manager)
    dialog.setStyleSheet(theme.QSS)
    dialog.show()
    dialog.activateWindow()
    app.processEvents()
    try:
        assert manager.unread == 0 and dialog.history.topLevelItemCount() == 1
        dialog.mode.setCurrentIndex(dialog.mode.findData("in-app"))
        dialog.events["health"].setChecked(False)
        manager.notify("health_problems", 2)
        assert dialog.history.topLevelItemCount() == 1
        manager.notify("operation_partial", 1)
        assert dialog.history.topLevelItemCount() == 2 and manager.unread == 0
        assert dialog.grab().save(str(tmp_path / "notifications.png"))
        assert settings.value("notifications_mode") == "in-app"
        assert "health" not in settings.value("notifications_events", [], list)
        manager.clear()
        assert dialog.history.topLevelItemCount() == 0
    finally:
        dialog.close()
        dialog.deleteLater()
        manager.close()
        owner.close()
        app.processEvents()


def test_real_tasks_route_once_keep_undo_and_hide_private_details(qt, tmp_path, monkeypatch):
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QDialog
    from memoria.engine import actions, photoedit, storage
    from memoria.engine.hashing import full_hash
    from memoria.engine.progress import Cancelled
    from memoria.ui.main_window import MainWindow
    from memoria.ui.notifications import NotificationManager
    from memoria.ui.pages import base
    from memoria.ui.widgets import MessageDialog
    app, settings, Tray = qt
    monkeypatch.setattr(NotificationManager, "_native_tray", lambda self: Tray(self))
    monkeypatch.setattr(NotificationManager, "_is_foreground", lambda self: False)
    monkeypatch.setattr(MessageDialog, "exec", lambda self: 0)
    monkeypatch.setattr(base, "confirm", lambda *args, **kwargs: True)
    root = tmp_path / "PRIVATE_LIBRARY"
    root.mkdir()
    source = root / "PRIVATE_PHOTO.jpg"
    Image.new("RGB", (48, 32), "red").save(source)
    original_hash = full_hash(source)
    window = MainWindow()
    window.show()
    events, toasts = [], []
    window.ctx.notification_requested.connect(lambda key, count: events.append((key, count)))
    window.ctx.toast_requested.connect(lambda text, batch: toasts.append((text, batch)))

    def wait():
        until = time.monotonic() + 15
        while (window.runner.busy or window.ctx.indexing) and time.monotonic() < until:
            app.processEvents()
            time.sleep(.01)
        app.processEvents()
        assert not window.runner.busy and not window.ctx.indexing

    def expect(key, count=0):
        wait()
        assert events == [(key, count)]
        events.clear()

    def apply(plan):
        window.page("photos").apply_actions(
            "copy", "PRIVATE_TASK_TITLE", plan, summary="Copy", details=[],
            confirm_text="Copy", note="", done_message=lambda result: "Copied")

    def cancel(prog):
        raise Cancelled()

    def fail(prog):
        raise OSError("PRIVATE_ERROR_DETAIL")

    try:
        window.open_library(str(root), "photos")
        expect("index_complete")
        lib = window.ctx.library
        output = tmp_path / "export" / source.name
        apply([actions.Action("copy", str(source), str(output), size=source.stat().st_size,
                              mtime=source.stat().st_mtime)])
        expect("operation_complete", 1)
        assert output.exists()
        assert toasts[-1][1] and window.toast.batch_id == toasts[-1][1]
        assert len(toasts) == 1  # generic completion must not replace the actionable Undo toast

        apply([actions.Action("copy", str(source), str(output), size=source.stat().st_size + 1)])
        expect("operation_partial", 1)
        with monkeypatch.context() as patch:
            patch.setattr(actions, "apply", lambda *args, **kwargs: actions.BatchResult("", cancelled=True))
            apply([actions.Action("copy", str(source), str(output))])
            expect("task_cancelled")

        window.runner.run("PRIVATE_TASK_TITLE", cancel)
        expect("task_cancelled")
        window.runner.run("PRIVATE_TASK_TITLE", fail)
        expect("task_failed")

        bad = root / "PRIVATE_BAD.jpg"
        bad.write_bytes(b"not an image")
        window.page("health").check()
        expect("health_problems", 1)

        failures = []
        def edit(prog):
            result = photoedit.save_many([source, bad], photoedit.PhotoEdit(), tmp_path / "edited", progress=prog)
            failures.extend(result.failures)
            return result
        window.page("editor")._run_outputs("PRIVATE_TASK_TITLE", edit, lambda path: source, failures)
        expect("operation_partial", 1)
        assert window.toast.batch_id

        options = storage.ResetOptions(thumbnails=False, analysis=False, videos=False)
        storage._clear_catalogue(lib, options)
        window._reset_state()
        window.runner.run("PRIVATE_TASK_TITLE", cancel)
        expect("rebuild_paused")
        window.runner.run("PRIVATE_TASK_TITLE", fail)
        expect("rebuild_failed")  # not a second, misleading "paused" event as well
        window.index_library()
        expect("index_issues")  # invalid media produces a warning, not unconditional success
        storage._clear_catalogue(lib, options)
        window._reset_state()
        window.index_library()
        expect("rebuild_complete")

        assert full_hash(source) == original_hash
        assert all("PRIVATE_" not in title + text for title, text, *_ in window.notifications.tray.messages)
        window.showMinimized()
        window.notifications.tray.menu.actions()[0].trigger()
        app.processEvents()
        assert not window.isMinimized()
        window.showMinimized()
        window.notifications.tray.messageClicked.emit()
        app.processEvents()
        assert not window.isMinimized()
        dialog = QDialog(window)
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        dialog.show()
        app.processEvents()
        window.notifications.tray.messageClicked.emit()
        assert dialog.isVisible()  # clicking never bypasses a safety dialog or runs an action
        dialog.close()
        window.close()
        delivered = len(window.notifications.tray.messages)
        window.ctx.notification_requested.emit("task_cancelled", 0)
        assert len(window.notifications.tray.messages) == delivered
        assert not window.notifications.tray.visible
    finally:
        window.close()
        window.deleteLater()
        app.processEvents()
