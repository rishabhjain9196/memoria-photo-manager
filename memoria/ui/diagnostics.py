"""Per-device/library opt-in and repository-local aggregate reports. No upload or git mutations."""
import json
import os
import uuid

from PySide6.QtCore import QObject, QThread, QTimer, Signal, Slot, Qt
from PySide6.QtWidgets import QCheckBox, QDialog, QPlainTextEdit

from ..engine import diagnostics
from .widgets import button, hbox, label, show_in_explorer, vbox


class _ReportWorker(QThread):
    ready = Signal(int, object)
    failed = Signal(int, str)

    def __init__(self, lib, metrics, path, revision, active, root):
        super().__init__()
        self.lib, self.metrics, self.path = lib, metrics, path
        self.generation = metrics.generation
        self.revision, self.active = revision, active
        self.root = root

    def run(self):
        try:
            revision = self.revision or diagnostics.source_revision(self.root)
            report = diagnostics.build_report(self.lib, self.metrics, revision, self.active)
            if self.metrics.publish(self.path, report, self.generation):
                self.ready.emit(self.generation, report)
        except Exception as error:
            # Raw exception text may include a private path. Keep it out of diagnostics.
            self.failed.emit(self.generation, type(error).__name__)
        finally:
            self.lib.close_thread()


class DiagnosticsController(QObject):
    updated = Signal()
    problem = Signal(str)

    def __init__(self, ctx, settings, parent=None, *, root=None):
        super().__init__(parent)
        self.ctx, self.settings = ctx, settings
        self.root = root if root is not None else diagnostics.repository_root()
        self.path = None
        self.latest = None
        self.status = "Recording is off. Open a library and opt in to create a report."
        self._writer = None
        self._dirty = False
        self._closing = False
        self._revision = None
        self._last_error = ""
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(1500)
        self._timer.timeout.connect(self.refresh)
        self._heartbeat = QTimer(self)
        self._heartbeat.setInterval(60_000)
        self._heartbeat.timeout.connect(self.refresh)
        ctx.library_opened.connect(self.library_changed)
        ctx.library_modified.connect(self.schedule)
        ctx.runner.measured.connect(self.measured)
        ctx.runner.started.connect(self.schedule)
        if ctx.library is not None:
            self.library_changed()

    @property
    def enabled(self):
        return self.ctx.diagnostics.enabled

    def _library_key(self):
        return os.path.normcase(str(self.ctx.library.root)) if self.ctx.library else None

    def library_changed(self):
        self._timer.stop()
        self._heartbeat.stop()
        self.latest, self._last_error = None, ""
        self.path = self.root / "diagnostics" / "reports" / f"report-{uuid.uuid4().hex[:12]}.json" if self.root else None
        consent = self.settings.value("diagnostics_libraries", [], list) or []
        self._configure(self._library_key() in consent and self.path is not None)

    def _configure(self, enabled):
        self.ctx.diagnostics.reset(enabled)
        if enabled:
            self._last_error = ""
            self._heartbeat.start()
            self.status = "Recording locally. Preparing an aggregate report from the existing catalogue…"
            self.refresh()
        else:
            self._timer.stop()
            self._heartbeat.stop()
            self._dirty = False
            self.status = "Recording is off. Existing report files are not deleted."
        self.updated.emit()

    def set_enabled(self, enabled):
        key = self._library_key()
        if key is None or self.root is None:
            raise ValueError("Open a library in a source checkout before enabling repository diagnostics.")
        if self.path is None or enabled and not self.enabled:
            self.path = self.root / "diagnostics" / "reports" / f"report-{uuid.uuid4().hex[:12]}.json"
            self.latest = None
        consent = set(self.settings.value("diagnostics_libraries", [], list) or [])
        if enabled:
            consent.add(key)
        else:
            consent.discard(key)
        self.settings.setValue("diagnostics_libraries", sorted(consent))
        self._configure(enabled)

    @Slot(str, str, float, float)
    def measured(self, operation, outcome, wall, cpu):
        self.ctx.diagnostics.record(operation, outcome, wall, cpu)
        self.schedule()

    @Slot()
    def schedule(self):
        if self.enabled and not self._closing:
            self._dirty = True
            self._timer.start()

    @Slot()
    def refresh(self):
        if not self.enabled or self.ctx.library is None or self.path is None or self._closing:
            return
        if self._writer is not None:
            self._dirty = True
            return
        try:
            inside = self.path.resolve().is_relative_to(self.root.resolve())
        except OSError as error:
            self._failed(self.ctx.diagnostics.generation, type(error).__name__)
            return
        if not inside:
            self._failed(self.ctx.diagnostics.generation, "Report path leaves the checkout")
            return
        self._dirty = False
        self.status = "Updating aggregate diagnostics from the catalogue…"
        worker = _ReportWorker(self.ctx.library, self.ctx.diagnostics, self.path, self._revision,
                               self.ctx.runner.active_measurement(), self.root)
        self._writer = worker
        worker.ready.connect(self._ready)
        worker.failed.connect(self._failed)
        worker.finished.connect(self._finished)
        self.updated.emit()
        worker.start()

    @Slot(int, object)
    def _ready(self, generation, report):
        if generation != self.ctx.diagnostics.generation or self._closing:
            return
        self.latest = report
        self._revision = report["git_head"]
        self._last_error = ""
        self.status = "Report saved locally. Turn recording off, then review it before adding it to git."
        self.updated.emit()

    @Slot(int, str)
    def _failed(self, generation, error):
        if generation != self.ctx.diagnostics.generation or self._closing:
            return
        self.status = f"Diagnostics could not be saved ({error}). Any previous report remains; media was not changed."
        if error != self._last_error:
            self.problem.emit(self.status)
        self._last_error = error
        self.updated.emit()

    @Slot()
    def _finished(self):
        worker, self._writer = self._writer, None
        if worker:
            worker.deleteLater()
        self.updated.emit()
        if self._dirty:
            self.schedule()

    def close(self):
        self._closing = True
        self._timer.stop()
        self._heartbeat.stop()
        if self._writer:
            self._writer.wait()
        if self.enabled and self.ctx.library and self.path:
            try:
                if not self.path.resolve().is_relative_to(self.root.resolve()):
                    raise ValueError("Report path leaves the checkout")
                report = diagnostics.build_report(self.ctx.library, self.ctx.diagnostics, self._revision)
                self.ctx.diagnostics.publish(self.path, report, self.ctx.diagnostics.generation)
            except Exception as error:
                return f"Diagnostics could not be saved ({type(error).__name__}). Previous reports remain."
        return None


class DiagnosticsDialog(QDialog):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Local diagnostics")
        self.resize(740, 670)
        self.record = QCheckBox("Record aggregate diagnostics for this library on this device")
        self.record.setChecked(controller.enabled)
        self.record.setEnabled(controller.ctx.library is not None and controller.root is not None)
        self.record.toggled.connect(controller.set_enabled)
        self.status = label("", "small", wrap=True)
        self.destination = label("", "small", wrap=True)
        self.destination.setTextFormat(Qt.TextFormat.PlainText)
        self.preview = QPlainTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setPlaceholderText("Enable recording to generate a report from the existing catalogue. "
                                        "No media rescan is needed.")
        self.refresh_btn = button("Refresh report", on_click=controller.refresh)
        self.open_btn = button("Show report in folder", on_click=self._show_file)
        self.setLayout(vbox(
            label("Local diagnostics — review before sharing", "h2"),
            label("Reports contain aggregate counts, size/format/codec distributions, error categories, timings and "
                  "basic system/process-memory information. No photos, filenames, paths, capture dates, GPS coordinates, "
                  "person/camera names, embeddings, content hashes or raw error traces are included.",
                  wrap=True),
            label("Counts can still reveal information about your collection. Reports stay in this repository; "
                  "the app never stages, commits or uploads them. Recording starts now and includes the current task "
                  "when it finishes; past timings cannot be reconstructed. Turn recording off before editing or "
                  "committing reports.", "small", wrap=True),
            self.record, self.destination, self.status, self.preview,
            hbox(self.refresh_btn, self.open_btn, None, button("Close", on_click=self.accept)),
            margins=(20, 18, 20, 18)))
        self.layout().setStretchFactor(self.preview, 1)
        controller.updated.connect(self._update)
        self._update()

    def _update(self):
        c = self.controller
        self.record.blockSignals(True)
        self.record.setChecked(c.enabled)
        self.record.blockSignals(False)
        self.status.setText(c.status)
        self.destination.setText(f"Repository report: {c.path.relative_to(c.root)}" if c.path else
                                 "Use run.ps1 from a source checkout and open a library to record in its repository.")
        self.refresh_btn.setEnabled(c.enabled and c._writer is None)
        self.open_btn.setEnabled(c.path is not None and c.path.is_file())
        if c.latest is not None:
            self.preview.setPlainText(json.dumps(c.latest, indent=2, sort_keys=True))
        else:
            self.preview.clear()

    def _show_file(self):
        if self.controller.path and self.controller.path.is_file():
            show_in_explorer(self.controller.path)
        else:
            self.status.setText("The report file is no longer there. Enable recording and refresh to generate another.")
            self.open_btn.setEnabled(False)
