"""Diagnostics must work from caches and must never export sensitive catalogue contents."""
import json
import os
import threading
import time
from pathlib import Path

import pytest

from memoria.engine import diagnostics, scanner
from memoria.engine.db import Library, METADATA_VERSION

SECRET = "PRIVATE_SENTINEL_DO_NOT_EXPORT"


@pytest.fixture
def cached_library(tmp_path):
    root = tmp_path / SECRET
    root.mkdir()
    photo = root / f"{SECRET}.jpg"
    photo.write_bytes(b"untouched private media")
    lib = Library(root)
    with lib.transaction() as db:
        db.execute("INSERT INTO files(rel_path,folder,name,ext,kind,size,mtime,analyzed,metadata_version,"
                   "taken_at,camera,lens,lat,lon,width,height,error,baseline_hash,date_source) "
                   "VALUES (?,?,?,?,?,1000,1,1,?,'2024-06-15 12:34:56',?,?,12.3456789,98.7654321,4000,3000,?,?,?)",
                   (photo.name, SECRET, photo.name, ".jpg", "image", METADATA_VERSION, SECRET, SECRET,
                    "PermissionError: " + SECRET, SECRET, "exif"))
        db.execute("INSERT INTO files(rel_path,folder,name,ext,kind,size,mtime,analyzed,metadata_version,"
                   "duration,fps,video_codec,audio_codec,date_source) VALUES (?,?,?,?,?,1000000,1,1,?,60,30,?,?,?)",
                   (SECRET + ".mp4", SECRET, SECRET, "." + SECRET, "video", METADATA_VERSION,
                    SECRET, SECRET, SECRET))
        db.execute("INSERT INTO people VALUES (1,?,'2024-01-01')", (SECRET,))
        db.execute("INSERT INTO faces(file_id,x,y,w,h,score,emb,person_id) VALUES (1,0,0,1,1,1,?,1)",
                   (SECRET.encode(),))
        db.execute("INSERT INTO albums(id,name,kind,created_at,cover_id) VALUES (1,?,'manual','2024-01-01',1)", (SECRET,))
        db.execute("INSERT INTO album_items VALUES (1,1,0)")
        db.execute("INSERT INTO batches VALUES ('batch','2024-01-01','batch',?,'partial',0,0)", (SECRET,))
        db.execute("INSERT INTO operations(batch_id,seq,op,src,dst,hash,reason,status,error) "
                   "VALUES ('batch',0,'copy',?,?,?,?, 'failed',?)", (SECRET, SECRET, SECRET, SECRET, SECRET))
    yield lib
    lib.close()


def test_cached_report_has_no_sensitive_values_or_media_reads(cached_library, monkeypatch):
    lib = cached_library
    def forbidden(*args, **kwargs):
        raise AssertionError("Diagnostics must not scan or analyse media")
    monkeypatch.setattr(scanner, "index", forbidden)
    monkeypatch.setattr(scanner, "analyze", forbidden)
    before = lib.db.total_changes
    metrics = diagnostics.Metrics()
    report = diagnostics.build_report(lib, metrics, "a" * 40)
    text = json.dumps(report)
    for private in (SECRET, str(lib.root), "2024-06-15", "12.3456789", "98.7654321"):
        assert private not in text
    assert lib.db.total_changes == before
    assert (lib.root / f"{SECRET}.jpg").read_bytes() == b"untouched private media"
    assert report["library"]["files"] == 2 and report["library"]["awaiting_analysis"] == 0
    assert report["library"]["with_valid_gps"] == 1
    assert report["error_categories"] == {"permission": 1}
    assert report["errors_by_format"] == {".jpg": {"permission": 1}}
    assert report["format_storage"]["other"] == {"files": 1, "bytes": 1000000}
    assert report["distributions"]["video_codecs"] == {"other": 1}
    assert report["operation_outcomes"]["failed"] == 1
    assert report["timings"] == {}  # old performance cannot be reconstructed


def test_metrics_are_opt_in_bounded_and_reject_raw_labels():
    metrics = diagnostics.Metrics()
    metrics.record("index", "ok", 1, .2)
    assert metrics.snapshot() == {}
    metrics.reset(True)
    for _ in range(1000):
        metrics.record("index", "ok", 2, .5)
    snapshot = metrics.snapshot()
    assert len(snapshot) == 1 and snapshot["index"]["count"] == 1000
    assert snapshot["index"]["wall_seconds_mean"] == 2
    assert len(json.dumps(snapshot)) < 1000
    with pytest.raises(ValueError):
        metrics.record(SECRET, "ok", 1, 0)
    with pytest.raises(ValueError):
        metrics.record("index", "ok", float("nan"), 0)
    generation = metrics.generation
    metrics.reset(True)
    metrics.record("index", "ok", 1, 0, generation)
    assert metrics.snapshot() == {}


@pytest.mark.skipif(os.name != "nt", reason="Windows process counters")
def test_windows_memory_sampling_is_real_and_unavailability_is_explicit(monkeypatch):
    memory = diagnostics.process_memory()
    assert memory["available"]
    assert memory["lifetime_peak_working_set_mib"] >= memory["working_set_mib"] > 0
    assert diagnostics.physical_memory_gib() > 0
    def unavailable(*args, **kwargs):
        raise OSError("test restricted process counter")
    monkeypatch.setattr(diagnostics.ctypes, "WinDLL", unavailable)
    assert diagnostics.process_memory() == {"available": False, "scope": "app_process_only"}


def test_atomic_reports_keep_previous_snapshot_on_failure(tmp_path, monkeypatch):
    metrics = diagnostics.Metrics()
    path = tmp_path / "reports" / "report.json"
    assert not metrics.publish(path, {"safe": 1}, metrics.generation)
    assert not path.parent.exists()
    metrics.reset(True)
    assert metrics.publish(path, {"safe": 1}, metrics.generation)
    def fail(*args):
        raise PermissionError(SECRET)
    with monkeypatch.context() as m:
        m.setattr(diagnostics.os, "replace", fail)
        with pytest.raises(PermissionError):
            metrics.publish(path, {"safe": 2}, metrics.generation)
    assert json.loads(path.read_text()) == {"safe": 1}
    assert list(path.parent.iterdir()) == [path]


def test_disabling_during_write_prevents_publication(tmp_path, monkeypatch):
    metrics = diagnostics.Metrics()
    metrics.reset(True)
    path = tmp_path / "report.json"
    metrics.publish(path, {"prior": 1}, metrics.generation)
    real_dump = diagnostics.json.dump
    def stop_after_write(*args, **kwargs):
        real_dump(*args, **kwargs)
        metrics.reset(False)
    monkeypatch.setattr(diagnostics.json, "dump", stop_after_write)
    assert not metrics.publish(path, {"new": 2}, metrics.generation)
    assert json.loads(path.read_text()) == {"prior": 1}
    assert list(tmp_path.iterdir()) == [path]


@pytest.fixture
def app():
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ.setdefault("QT_QPA_FONTDIR", r"C:\Windows\Fonts")
    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QFont
    from memoria.ui import theme
    instance = QApplication.instance() or QApplication([])
    instance.setFont(QFont("Segoe UI", 10))
    theme.use("light")
    instance.setStyleSheet(theme.QSS)
    instance.setPalette(theme.qpalette())
    return instance


def pump_until(app, predicate):
    end = time.monotonic() + 10
    while not predicate() and time.monotonic() < end:
        app.processEvents()
        time.sleep(.01)
    app.processEvents()
    assert predicate()


def test_task_timings_never_capture_titles_or_error_text(app):
    from memoria.ui.tasks import TaskRunner
    runner = TaskRunner()
    metrics = diagnostics.Metrics()
    metrics.reset(True)
    runner.measured.connect(metrics.record)
    def fail(progress):
        raise PermissionError(SECRET)
    runner.run(SECRET, fail, diagnostic_key="index")
    pump_until(app, lambda: not runner.busy)
    runner.report_measurement()
    snapshot = metrics.snapshot()
    assert snapshot["index"]["count"] == 1 and snapshot["index"]["outcomes"]["failed"] == 1
    assert SECRET not in json.dumps(snapshot)


def test_existing_cache_and_in_progress_task_record_in_checkout(app, cached_library, tmp_path, monkeypatch):
    from PySide6.QtCore import QSettings
    from memoria.ui.diagnostics import DiagnosticsController, DiagnosticsDialog
    from memoria.ui.tasks import TaskRunner
    from memoria.ui.widgets import AppContext
    root = tmp_path / "checkout"
    settings = QSettings(str(tmp_path / "local-settings.ini"), QSettings.Format.IniFormat)
    ctx = AppContext(TaskRunner())
    controller = DiagnosticsController(ctx, settings, root=root)
    ctx.set_library(cached_library)
    assert not controller.enabled and not root.exists()
    event = threading.Event()
    ctx.runner.run(SECRET, lambda p: event.wait(15), diagnostic_key="index")
    dialog = DiagnosticsDialog(None, controller)
    try:
        dialog.record.setChecked(True)  # opt in while a task is already running
        controller.refresh()
        pump_until(app, lambda: controller.latest is not None and controller._writer is None)
        path = controller.path
        assert path.is_relative_to(root / "diagnostics" / "reports")
        report = json.loads(path.read_text())
        assert report["task_in_progress"]["operation"] == "index"
        assert report["library"]["files"] == 2 and SECRET not in path.read_text()
        event.set()
        pump_until(app, lambda: not ctx.runner.busy)
        controller.refresh()
        pump_until(app, lambda: controller._writer is None and "index" in (controller.latest or {}).get("timings", {}))
        assert controller.latest["task_in_progress"] is None
        assert controller.latest["timings"]["index"]["count"] == 1
        assert dialog.refresh_btn.isEnabled()
        controller._timer.stop()
        for _ in range(100):
            ctx.diagnostics.record("preview", "ok", .01, 0)
        assert not controller._timer.isActive()  # browsing metrics wait for the periodic snapshot
        controller.refresh()
        pump_until(app, lambda: controller._writer is None and
                   (controller.latest or {}).get("timings", {}).get("preview", {}).get("count") == 100)
        assert SECRET not in dialog.preview.toPlainText()
        dialog.show()
        app.processEvents()
        assert dialog.height() <= app.primaryScreen().availableGeometry().height()
        assert dialog.grab().save(str(tmp_path / "diagnostics-preview.png"))
        dialog.record.setChecked(False)
        assert path.exists()
        saved = path.read_bytes()
        controller.refresh()
        app.processEvents()
        assert path.read_bytes() == saved
        assert settings.value("diagnostics_libraries", [], list) == []
    finally:
        event.set()
        ctx.runner.wait()
        controller.close()
        dialog.close()
        dialog.deleteLater()
        controller.deleteLater()
        app.processEvents()


def test_failed_report_is_visible_and_does_not_replace_previous(app, cached_library, tmp_path, monkeypatch):
    from PySide6.QtCore import QSettings
    from memoria.ui.diagnostics import DiagnosticsController
    from memoria.ui.tasks import TaskRunner
    from memoria.ui.widgets import AppContext
    ctx = AppContext(TaskRunner())
    controller = DiagnosticsController(ctx, QSettings(str(tmp_path / "prefs.ini"), QSettings.Format.IniFormat),
                                       root=tmp_path / "checkout")
    ctx.set_library(cached_library)
    controller.set_enabled(True)
    controller.refresh()
    pump_until(app, lambda: controller.latest is not None and controller._writer is None)
    before = controller.path.read_bytes()
    def fail(*args, **kwargs):
        raise OSError(SECRET)
    with monkeypatch.context() as m:
        m.setattr(diagnostics, "build_report", fail)
        controller.refresh()
        pump_until(app, lambda: controller._writer is None)
        assert "could not be saved" in controller.status and SECRET not in controller.status
        assert controller.path.read_bytes() == before
    controller.set_enabled(False)
    controller.close()
    controller.deleteLater()
    app.processEvents()


def test_library_switch_does_not_publish_an_old_inflight_report(app, cached_library, tmp_path, monkeypatch):
    from PySide6.QtCore import QSettings
    from memoria.ui.diagnostics import DiagnosticsController
    from memoria.ui.tasks import TaskRunner
    from memoria.ui.widgets import AppContext
    ctx = AppContext(TaskRunner())
    settings = QSettings(str(tmp_path / "prefs.ini"), QSettings.Format.IniFormat)
    controller = DiagnosticsController(ctx, settings, root=tmp_path / "checkout")
    ctx.set_library(cached_library)
    gate = threading.Event()
    real = diagnostics.build_report
    def blocked(*args):
        gate.wait(15)
        return real(*args)
    monkeypatch.setattr(diagnostics, "build_report", blocked)
    controller.set_enabled(True)
    controller.refresh()
    old_path = controller.path
    other_root = tmp_path / "different-library"
    other_root.mkdir()
    other = Library(other_root)
    try:
        ctx.set_library(other)
        assert not controller.enabled
        gate.set()
        pump_until(app, lambda: controller._writer is None)
        assert not old_path.exists()
        assert controller.latest is None
        assert len(settings.value("diagnostics_libraries", [], list)) == 1
    finally:
        gate.set()
        controller.close()
        other.close()
        controller.deleteLater()
        app.processEvents()
