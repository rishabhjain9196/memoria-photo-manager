"""Read-only tasks side by side, changes waiting for them, and browse & find windows."""
import os
import threading
import time

from PIL import Image

from memoria.engine.db import Library


def _app():
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    from PySide6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])


def _spin(app, predicate, timeout=10):
    deadline = time.monotonic() + timeout
    while not predicate() and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.01)
    app.processEvents()
    assert predicate()


def test_read_only_tasks_overlap_and_a_change_waits_for_them():
    from memoria.ui.tasks import TaskRunner
    from memoria.ui.widgets import AppContext
    app = _app()
    runner = TaskRunner()
    ctx = AppContext(runner)
    release = threading.Event()
    running, order = set(), []

    def search(name):
        def work(progress):
            running.add(name)
            release.wait(5)
            order.append(name)
        return work

    assert ctx.parallel.run("Finding duplicates", search("dup"), diagnostic_key="duplicates")
    assert ctx.parallel.run("Finding similar photos", search("sim"), diagnostic_key="similar")
    assert not ctx.parallel.run("Finding duplicates", search("again"), diagnostic_key="duplicates")
    _spin(app, lambda: running == {"dup", "sim"})        # both read at the same time

    assert runner.run("Moving files", lambda p: order.append("move"), diagnostic_key="other")
    assert runner.busy and runner.waiting                # accepted, but waits for the searches
    assert not ctx.parallel.run("Health check", search("health"), diagnostic_key="health")
    release.set()
    _spin(app, lambda: not runner.active)
    assert order[-1] == "move" and set(order[:2]) == {"dup", "sim"}


def test_background_tasks_pause_while_a_change_runs():
    from memoria.ui.tasks import TaskRunner
    from memoria.ui.widgets import AppContext
    app = _app()
    runner = TaskRunner()
    ctx = AppContext(runner)
    stop, progressed = threading.Event(), []

    def background(progress):
        while not stop.is_set():
            progress.check()            # blocks while held
            progressed.append(time.monotonic())
            time.sleep(0.01)

    ctx.parallel.run("Fingerprinting photos", background, diagnostic_key="index", background=True)
    _spin(app, lambda: len(progressed) > 3)
    change_done = threading.Event()

    def change(progress):
        time.sleep(0.3)
        change_done.set()

    assert runner.run("Moving files", change)
    assert not runner.waiting                            # background work doesn't block changes
    time.sleep(0.1)
    held_at = len(progressed)
    time.sleep(0.15)
    assert len(progressed) <= held_at + 1                # held while the change runs
    _spin(app, lambda: change_done.is_set() and not runner.busy)
    _spin(app, lambda: len(progressed) > held_at + 3)    # resumed afterwards
    stop.set()
    _spin(app, lambda: not runner.active)


def test_browse_and_find_window_never_changes_files(tmp_path):
    from memoria.engine import db as dbmod
    from memoria.ui.tasks import TaskRunner
    Image.new("RGB", (20, 20)).save(tmp_path / "a.jpg")
    owner = Library(tmp_path)
    try:
        locks_before = {k: v[1] for k, v in dbmod._LOCKS.items()}
        viewer = Library(tmp_path, viewer=True)
        try:
            assert viewer.viewer and viewer.roots()[0]["path"] == str(tmp_path.resolve())
            assert {k: v[1] for k, v in dbmod._LOCKS.items()} == locks_before   # takes no lock
            runner = TaskRunner()
            runner.viewer = True
            refused = []
            runner.refused.connect(refused.append)
            assert not runner.run("Moving files", lambda p: None)
            assert refused and not runner.busy
        finally:
            viewer.close()
        assert {k: v[1] for k, v in dbmod._LOCKS.items()} == locks_before       # and releases none
    finally:
        owner.close()
