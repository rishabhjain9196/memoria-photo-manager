"""Opt-in upstream checks and a post-exit updater handoff; never mutates media."""
from __future__ import annotations

import json
import time
from datetime import datetime

from PySide6.QtCore import QObject, QSettings, QTimer, Qt, Signal
from PySide6.QtWidgets import QCheckBox, QDialog, QPlainTextEdit

from ..engine import app_updates
from .tasks import LatestCall
from .widgets import ConfirmDialog, button, hbox, label, vbox


class UpdateController(QObject):
    changed = Signal()

    def __init__(self, window):
        super().__init__(window)
        self.window, self.settings = window, window.settings
        self.info = None
        self.status = "Not checked. Use Check for updates to contact your configured Git upstream."
        self.checked_at = ""
        self.working = False
        self.pending = False
        self._closed = self._armed = self._startup = False
        self._operation = ""
        self._handoff = None
        self._deadline = 0.0
        self.bg = LatestCall(self)
        self.bg.result.connect(self._result)
        self.bg.failed.connect(self._failed)
        self.timer = QTimer(self)
        self.timer.setInterval(150)
        self.timer.timeout.connect(self._poll_handoff)
        window.runner.busy_changed.connect(lambda _: self.changed.emit())
        window.ctx.indexing_changed.connect(lambda _: self.changed.emit())

    @property
    def automatic(self):
        return self.settings.value("updates/check_on_startup", False, type=bool)

    @property
    def library_busy(self):
        return self.window.runner.busy or self.window.ctx.indexing or self.window.ctx.maintenance

    @property
    def can_install(self):
        return bool(self.info and self.info.can_update and not self.working and not self.pending
                    and not self.library_busy and not self._closed)

    def set_automatic(self, enabled):
        self.settings.setValue("updates/check_on_startup", bool(enabled))
        self.settings.sync()
        if self.settings.status() != QSettings.Status.NoError:
            self.status = "The startup-check preference could not be saved. Check access to application settings."
        self.changed.emit()

    def startup_check(self):
        if self.automatic and not self._closed:
            self.check(startup=True)

    def check(self, *, startup=False):
        if self._closed or self.working or self.pending:
            return
        self._startup = startup
        self._operation = "check"
        self.working = True
        self.info = None
        self.status = "Checking the configured upstream... This does not change application or media files."
        self.changed.emit()
        self.bg.call(app_updates.check)

    def _result(self, result):
        if self._closed:
            return
        self.working = False
        if self._operation == "check":
            self.info = result
            self.checked_at = datetime.now().strftime("%d %b %Y, %H:%M")
            self.status = result.summary
            if self._startup and result.behind:
                self.window.ctx.toast_requested.emit("Application updates are available. Open Updates to review.", "")
            self.changed.emit()
            return
        self._handoff = result
        self._deadline = time.monotonic() + 30
        self.status = "Waiting for the update window. Memoria will close only after the updater is ready."
        self.timer.start()
        self.changed.emit()

    def _cancel_handoff(self):
        if self._handoff is not None:
            self._handoff.cancel.touch(exist_ok=True)

    def _failed(self, error):
        if self._closed:
            return
        self.working = self.pending = self._armed = False
        self.timer.stop()
        self.status = f"Update did not proceed: {error}"
        try:
            self._cancel_handoff()
        except OSError as cancel_error:
            self.status += f"\nCould not signal the updater to stop: {cancel_error}. Keep this app open."
        self.window.setEnabled(True)
        if self._startup:
            self.window.ctx.toast_requested.emit("Update check failed. Open Updates for details.", "")
        self.changed.emit()

    def install(self):
        if not self.can_install:
            self.status = "Check updates first and finish or cancel active library work before pulling and restarting."
            self.changed.emit()
            return False
        info = self.info
        details = [
            f"Tracking {info.remote}: {info.upstream}; {info.behind} new commit(s). "
            f"{info.local_head[:12]} -> {info.remote_head[:12]}.",
            "The application closes cleanly before the checkout is changed. The update must be a fast-forward.",
            "Local edits, untracked files or diverged history stop the update. Nothing is stashed or discarded.",
            "Changed Python dependencies are installed into this checkout's managed virtual environment.",
            "An update window shows pull/install progress and any errors. Memoria reopens after successful setup; "
            "do not close that update window early.",
            "Your media, catalogue and Recovery are not reset. No photos or library metadata are uploaded.",
        ]
        if info.changed_manifests:
            details.append("Dependency manifests changed: " + ", ".join(info.changed_manifests))
        dialog = ConfirmDialog(self.window, "Pull updates and restart Memoria?",
                               "Install the checked upstream commit, then reopen the application.",
                               details, "Pull and restart")
        accepted = dialog.exec() == dialog.DialogCode.Accepted
        dialog.deleteLater()
        if not accepted:
            return False
        if not self.can_install or self.info is not info:
            self.status = "Application state changed. Finish active work and check updates again."
            self.changed.emit()
            return False
        self.pending = self.working = True
        self._handoff = None
        self._armed = False
        self._startup = False
        self._operation = "launch"
        self.status = "Starting the separate update window..."
        self.window.setEnabled(False)
        self.changed.emit()
        self.bg.call(lambda: app_updates.launch_update(info))
        return True

    def _poll_handoff(self):
        handoff = self._handoff
        if handoff is None or self._closed:
            return
        try:
            if handoff.result.exists():
                outcome = json.loads(handoff.result.read_text(encoding="utf-8"))
                if outcome.get("phase") in ("failed", "cancelled"):
                    raise app_updates.UpdateError(outcome.get("error") or outcome.get("message") or
                                                  "The update helper stopped.")
            if handoff.ready.exists():
                if self.library_busy:
                    raise app_updates.UpdateError("Library work started while the updater was opening. "
                                                  "Finish it before trying again.")
                self._armed = True
                self.timer.stop()
                if not self.window.close():
                    self._armed = False
                    raise app_updates.UpdateError("The application could not close. The update was cancelled.")
            elif time.monotonic() >= self._deadline:
                raise app_updates.UpdateError(
                    f"The update window did not become ready. No pull was authorized. Review {handoff.log}.")
        except (OSError, ValueError, app_updates.UpdateError) as error:
            self._failed(error)

    def shutdown(self):
        self.timer.stop()
        self._closed = True
        self.bg.wait()
        if not self._armed:
            try:
                self._cancel_handoff()
            except OSError as error:
                # The helper also times out without an authorized shutdown.
                self.window.ctx.toast_requested.emit(f"Could not cancel the update helper: {error}", "")


class UpdatesDialog(QDialog):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Application updates")
        self.resize(760, 520)
        self.status = label("", "h2", wrap=True)
        self.status.setTextFormat(Qt.TextFormat.PlainText)
        self.auto = QCheckBox("Automatically check for updates when Memoria opens")
        self.auto.setChecked(controller.automatic)
        self.auto.toggled.connect(controller.set_automatic)
        self.details = QPlainTextEdit()
        self.details.setReadOnly(True)
        self.check_btn = button("Check for updates", on_click=lambda: controller.check())
        self.install_btn = button("Pull and restart", "primary", self._install)
        self.close_btn = button("Close", on_click=self.accept)
        self.setLayout(vbox(
            label("Application updates", "pageTitle"), self.auto,
            label("Off by default. Checks contact the configured Git upstream; photos and library metadata are "
                  "not uploaded. Startup checks never install automatically. Git source checkouts only; packaged "
                  "executables require a separately updated build.", "muted", wrap=True),
            self.status, self.details,
            hbox(self.check_btn, self.install_btn, None, self.close_btn), margins=(20, 20, 20, 20)))
        controller.changed.connect(self.refresh)
        self.refresh()

    def refresh(self):
        controller = self.controller
        self.status.setText(controller.status)
        lines = []
        if controller.checked_at:
            lines.append("Last check: " + controller.checked_at)
        if controller.info is not None:
            info = controller.info
            lines += [f"Checkout: {info.repo}", f"Branch: {info.branch}", f"Remote: {info.remote}", f"Upstream: {info.upstream}",
                      f"Current: {info.local_head}", f"Checked upstream: {info.remote_head}",
                      f"Behind: {info.behind}; ahead: {info.ahead}"]
            if info.dirty:
                lines += ["", "Local changes prevent updating. Save/commit or resolve them manually; "
                          "Memoria will not discard or stash them.", *info.dirty[:20]]
                if len(info.dirty) > 20:
                    lines.append(f"...and {len(info.dirty) - 20} more local changes.")
            if info.changed_manifests:
                lines += ["", "Changed dependency manifests: " + ", ".join(info.changed_manifests)]
        if controller.library_busy:
            lines += ["", "Library work is active. You may check updates now, but installation/restart must wait."]
        if not lines:
            lines.append("Choose Check for updates. No Git operation has been run by opening this screen.")
        self.details.setPlainText("\n".join(lines))
        self.check_btn.setEnabled(not controller.working and not controller.pending)
        self.install_btn.setEnabled(controller.can_install)
        self.auto.setEnabled(not controller.pending)
        self.close_btn.setEnabled(not controller.pending)

    def _install(self):
        if self.controller.install():
            self.accept()
