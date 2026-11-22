"""Task progress: pause/resume, live file and byte counts, speed, elapsed and time-left estimates."""
import os
import threading
import time

import pytest

from memoria.engine import actions
from memoria.engine.actions import Action
from memoria.engine.db import Library
from memoria.engine.hashing import full_hash
from memoria.engine.progress import Cancelled, Progress


def test_pause_holds_work_until_resumed_and_cancel_releases_it():
    progress = Progress()
    progress.pause_event.set()
    passed = threading.Event()

    def work():
        try:
            progress.check()
            passed.set()
        except Cancelled:
            pass
    thread = threading.Thread(target=work)
    thread.start()
    time.sleep(0.3)
    assert not passed.is_set()
    progress.pause_event.clear()
    thread.join(2)
    assert passed.is_set()

    progress.pause_event.set()
    stopped = []

    def stop():
        try:
            progress.check()
        except Cancelled:
            stopped.append(True)
    thread = threading.Thread(target=stop)
    thread.start()
    time.sleep(0.2)
    progress.cancel_event.set()
    thread.join(2)
    assert stopped and not thread.is_alive()


def _copies(tmp_path, sizes):
    source = tmp_path / "source"
    source.mkdir()
    (tmp_path / "library").mkdir()
    lib = Library(tmp_path / "library")
    planned = []
    for index, size in enumerate(sizes):
        path = source / f"clip{index}.mp4"
        path.write_bytes(os.urandom(size))
        planned.append(Action(op="copy", src=str(path), dst=str(lib.root / "Copied" / path.name), size=size,
                              mtime=path.stat().st_mtime, hash=full_hash(path)))
    return lib, planned


def test_copy_reports_files_and_bytes_inside_large_files(tmp_path, monkeypatch):
    monkeypatch.setattr(actions, "COPY_CHUNK", 64 * 1024)
    lib, planned = _copies(tmp_path, [600 * 1024, 100 * 1024])
    details = []
    progress = Progress(lambda *args: None, interval=0, detail_callback=details.append)
    try:
        result = actions.apply(lib, "sync", "Copy", planned, progress)
        assert result.done == 2
        byte_steps = [detail["bytes"][0] for detail in details if "bytes" in detail]
        assert all(detail["bytes"][1] == 700 * 1024 for detail in details if "bytes" in detail)
        assert any(0 < done < 600 * 1024 for done in byte_steps)        # mid-file progress
        assert byte_steps == sorted(byte_steps) and byte_steps[-1] == 700 * 1024
        assert details[-1]["items"] == (2, 2)
        assert any(detail.get("items") == (1, 2) for detail in details)
    finally:
        lib.close()


def test_cancel_mid_copy_leaves_no_partial_file(tmp_path, monkeypatch):
    monkeypatch.setattr(actions, "COPY_CHUNK", 64 * 1024)
    lib, planned = _copies(tmp_path, [640 * 1024])
    cancel = threading.Event()

    def stop_halfway(detail):
        if detail.get("bytes", (0, 1))[0] >= 256 * 1024:
            cancel.set()
    progress = Progress(lambda *args: None, cancel, interval=0, detail_callback=stop_halfway)
    try:
        result = actions.apply(lib, "sync", "Copy", planned, progress)
        assert result.cancelled and result.done == 0
        assert not (lib.root / "Copied").exists() or not any((lib.root / "Copied").iterdir())
        assert os.path.exists(planned[0].src)
    finally:
        lib.close()


def test_stats_speed_eta_and_pause_excluded_from_elapsed():
    from memoria.ui.task_stats import TaskStats
    now = [100.0]
    stats = TaskStats(lambda: now[0])
    mb = 1024 * 1024
    stats.update(0.0, {"items": (0, 10), "bytes": (0, 100 * mb), "unit": "file"})
    now[0] += 4
    stats.update(0.2, {"items": (2, 10), "bytes": (20 * mb, 100 * mb), "unit": "file"})
    assert stats.counts_text() == "2 of 10 files · 20.0 MB of 100.0 MB"
    assert stats.speed_text().startswith("5.0 MB/s") and "0.5 files/s" in stats.speed_text()
    assert stats.remaining() == pytest.approx(16)
    assert "4 s elapsed · about 16 s left" == stats.time_text()
    stats.pause()
    now[0] += 60
    assert stats.elapsed() == pytest.approx(4) and stats.time_text().endswith("paused")
    stats.resume()
    now[0] += 1
    assert stats.elapsed() == pytest.approx(5)


def test_system_stats_show_drive_workers_and_disk_speed():
    from memoria.ui.task_stats import TaskStats
    stats = TaskStats(lambda: 0.0)
    mb = 1024 * 1024
    drive = {"drive": "e:\\", "is_hdd": True, "is_ssd": False, "tier": "Mechanical HDD (WD Elements)",
             "workers": 1, "active": 1}
    base = {"pools": [("Photo decoders", 12), ("Video readers", 6)], "drives": [drive], "threads": 23, "cpus": 4}
    stats.system({**base, "time": 10.0, "cpu_seconds": 1.0, "io": (0, 0)})
    stats.system({**base, "time": 12.0, "cpu_seconds": 5.0, "io": (100 * mb, 2 * mb)})
    text = stats.system_text()
    assert "HDD: Mechanical HDD (WD Elements) · 1 of 1 reader busy" in text
    assert "Photo decoders ×12 · Video readers ×6 · 23 threads · CPU 50%" in text
    assert "Disk read 50.0 MB/s · write 1.0 MB/s" in text
    stats.pause()
    assert "Disk read" not in stats.system_text() and "CPU" not in stats.system_text()


def test_task_bar_shows_live_workers_while_running():
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    from PySide6.QtWidgets import QApplication
    from memoria.engine import activity
    from memoria.ui.main_window import MainWindow
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    release = threading.Event()

    def work(progress):
        with activity.pool("Hashing", 3):
            progress.update(1, 2, "Hashing", force=True)
            release.wait(5)
        return "ok"
    try:
        window.runner.run("Hashing files", work)
        deadline = time.monotonic() + 5
        while "Hashing ×3" not in window.task_system.text() and time.monotonic() < deadline:
            app.processEvents()
            time.sleep(0.01)
        assert "Hashing ×3" in window.task_system.text() and "threads" in window.task_system.text()
    finally:
        release.set()
        window.runner.wait()
        window.close()
        window.deleteLater()
        app.processEvents()


def test_task_bar_shows_counts_and_pauses_the_running_task():
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    from PySide6.QtWidgets import QApplication
    from memoria.ui.main_window import MainWindow
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    reached, release = [], threading.Event()

    def work(progress):
        for done in range(1, 6):
            progress.update(done, 5, f"Copying file{done}.jpg", force=True,
                            detail={"items": (done, 5), "bytes": (done * 1024, 5 * 1024), "unit": "file"})
            reached.append(done)
            if done == 2:
                release.wait(5)
            time.sleep(0.02)
        return "ok"

    def spin(predicate, timeout=5):
        deadline = time.monotonic() + timeout
        while not predicate() and time.monotonic() < deadline:
            app.processEvents()
            time.sleep(0.01)
        app.processEvents()
        assert predicate()
    try:
        window.runner.run("Copying files", work)
        spin(lambda: "2 of 5 files" in window.task_counts.text())
        assert "2.0 KB of 5.0 KB" in window.task_counts.text() and window.task_pct.text() == "40%"
        window.pause_btn.click()
        assert window.pause_btn.text() == "Resume" and window.runner.paused
        release.set()
        time.sleep(0.3)
        app.processEvents()
        assert reached == [1, 2]   # held at the next safe point
        assert window.task_msg.text().startswith("Paused") and "paused" in window.task_eta.text()
        window.pause_btn.click()
        spin(lambda: not window.runner.active)
        assert reached == [1, 2, 3, 4, 5] and window.task_bar.isHidden()
    finally:
        release.set()
        window.runner.cancel()
        window.runner.wait()
        window.close()
        window.deleteLater()
        app.processEvents()
