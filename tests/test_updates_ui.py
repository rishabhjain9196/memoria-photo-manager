import json
import os
import time
from pathlib import Path
from types import SimpleNamespace

import pytest


def _info(root, *, dirty=(), ahead=0, behind=2):
    return SimpleNamespace(repo=root, branch="main", remote="origin", upstream="origin/main",
                           local_head="a" * 40, remote_head="b" * 40, ahead=ahead, behind=behind,
                           dirty=list(dirty), changed_manifests=("requirements.txt",),
                           can_update=bool(behind and not ahead and not dirty),
                           summary="Updates available." if behind else "Up to date.")


def _wait(app, predicate):
    deadline = time.monotonic() + 8
    while not predicate() and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(.005)
    app.processEvents()
    assert predicate()


@pytest.fixture
def ui(tmp_path, monkeypatch):
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ.setdefault("QT_QPA_FONTDIR", r"C:\Windows\Fonts")
    from PySide6.QtCore import QSettings
    from PySide6.QtGui import QFont
    from PySide6.QtWidgets import QApplication
    from memoria.ui import theme
    from memoria.ui.main_window import MainWindow
    app = QApplication.instance() or QApplication([])
    app.setFont(QFont("Segoe UI", 10))
    app.setStyle("Fusion")
    theme.use("light")
    app.setPalette(theme.qpalette())
    app.setStyleSheet(theme.QSS)
    settings = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)
    monkeypatch.setattr(theme, "settings", lambda: settings)
    window = MainWindow()
    window.show()
    yield app, window, tmp_path
    window.close()
    window.deleteLater()
    app.processEvents()


def test_update_check_is_opt_in_and_does_not_install(ui, monkeypatch):
    from memoria.ui import updates
    app, window, root = ui
    controller = window.updates
    calls = []
    monkeypatch.setattr(updates.app_updates, "check", lambda: calls.append("check") or _info(root))
    monkeypatch.setattr(updates.app_updates, "launch_update",
                        lambda *_: pytest.fail("Checking must not install or restart"))
    assert not controller.automatic
    controller.startup_check()
    app.processEvents()
    assert calls == []
    controller.set_automatic(True)
    controller.startup_check()
    _wait(app, lambda: not controller.working)
    assert calls == ["check"] and controller.can_install
    assert window.settings.value("updates/check_on_startup", False, type=bool)
    assert "available" in window.updates_btn.text()
    controller.set_automatic(False)
    controller.startup_check()
    assert calls == ["check"]


def test_updates_screen_checks_now_and_explains_blockers(ui, monkeypatch):
    from memoria.ui import updates
    app, window, root = ui
    controller = window.updates
    monkeypatch.setattr(updates.app_updates, "check",
                        lambda: _info(root, dirty=[" M requirements.txt", "?? diagnostics/reports/new.json"]))
    dialog = updates.UpdatesDialog(window, controller)
    try:
        dialog.show()
        assert not controller.working and not dialog.install_btn.isEnabled()
        dialog.check_btn.click()
        _wait(app, lambda: not controller.working)
        assert "Local changes prevent updating" in dialog.details.toPlainText()
        assert "requirements.txt" in dialog.details.toPlainText()
        assert not dialog.install_btn.isEnabled()
        controller.info = _info(root)
        window.ctx.maintenance = True
        dialog.refresh()
        assert not dialog.install_btn.isEnabled() and "Library work is active" in dialog.details.toPlainText()
        monkeypatch.setattr(updates.ConfirmDialog, "exec", lambda *_: pytest.fail("No install while rebuilding"))
        assert not controller.install()
        window.ctx.maintenance = False
        dialog.refresh()
        assert dialog.install_btn.isEnabled()
        if os.environ.get("MEMORIA_SHOT_LABEL"):
            controller.info = _info(Path(r"C:\Memoria"))
            controller.status = controller.info.summary
            dialog.refresh()
        assert dialog.grab().save(str(root / "application-updates.png"))
    finally:
        window.ctx.maintenance = False
        dialog.close()
        dialog.deleteLater()
        app.processEvents()


def test_update_check_failure_is_not_reported_as_up_to_date(ui, monkeypatch):
    from memoria.ui import updates
    app, window, _ = ui
    def failed():
        raise updates.app_updates.UpdateError("Upstream cannot be reached")
    monkeypatch.setattr(updates.app_updates, "check", failed)
    window.updates.check()
    _wait(app, lambda: not window.updates.working)
    assert "cannot be reached" in window.updates.status
    assert window.updates.info is None and not window.updates.can_install
    assert window.isEnabled()


def _handoff(root):
    directory = root / "update handoff"
    directory.mkdir()
    return SimpleNamespace(directory=directory, ready=directory / "ready", cancel=directory / "cancel",
                           result=directory / "result.json", log=directory / "update.log", pid=12345)


def test_pull_and_restart_waits_for_ready_handoff_before_closing(ui, monkeypatch):
    from memoria.ui import updates
    app, window, root = ui
    controller = window.updates
    controller.info = _info(root)
    handoff = _handoff(root)
    launches, closes = [], []
    monkeypatch.setattr(updates.ConfirmDialog, "exec", lambda self: self.DialogCode.Accepted)
    monkeypatch.setattr(updates.app_updates, "launch_update",
                        lambda info: launches.append(info) or handoff)
    with monkeypatch.context() as patch:
        patch.setattr(window, "close", lambda: closes.append(True) or True)
        assert controller.install()
        _wait(app, lambda: controller._handoff is not None)
        assert len(launches) == 1 and not closes and not window.isEnabled()
        handoff.ready.write_text("ready")
        _wait(app, lambda: bool(closes))
        assert closes == [True] and controller._armed and not controller.timer.isActive()
        assert not handoff.cancel.exists()


@pytest.mark.parametrize("reason", ["busy", "helper_failed", "timeout"])
def test_failed_update_handoff_keeps_app_open_and_signals_cancellation(ui, monkeypatch, reason):
    from memoria.ui import updates
    app, window, root = ui
    controller = window.updates
    controller.info = _info(root)
    handoff = _handoff(root)
    monkeypatch.setattr(updates.ConfirmDialog, "exec", lambda self: self.DialogCode.Accepted)
    monkeypatch.setattr(updates.app_updates, "launch_update", lambda *_: handoff)
    with monkeypatch.context() as patch:
        patch.setattr(window, "close", lambda: pytest.fail("Blocked update must not close the app"))
        assert controller.install()
        _wait(app, lambda: controller._handoff is not None)
        if reason == "busy":
            window.ctx.indexing = True
            handoff.ready.write_text("ready")
        elif reason == "helper_failed":
            handoff.result.write_text(json.dumps({"phase": "failed", "error": "Checkout changed"}))
        else:
            controller._deadline = time.monotonic() - 1
        controller._poll_handoff()
        assert handoff.cancel.exists()
        assert not controller.pending and not controller._armed and window.isEnabled()
        assert "did not proceed" in controller.status
        window.ctx.indexing = False


def test_declining_pull_confirmation_leaves_app_and_checkout_alone(ui, monkeypatch):
    from memoria.ui import updates
    _, window, root = ui
    window.updates.info = _info(root)
    monkeypatch.setattr(updates.ConfirmDialog, "exec", lambda self: self.DialogCode.Rejected)
    monkeypatch.setattr(updates.app_updates, "launch_update",
                        lambda *_: pytest.fail("Declined update cannot launch the helper"))
    assert not window.updates.install()
    assert not window.updates.pending and window.isEnabled()
