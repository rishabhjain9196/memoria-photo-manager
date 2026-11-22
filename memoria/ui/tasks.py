"""Run engine calls on a background thread with progress, cancellation and error reporting.

Only one task runs at a time; pages check ``runner.busy`` and listen to ``busy_changed`` so the
user can never start two conflicting file operations.
"""
from __future__ import annotations

import threading
import time
import traceback
from typing import Any, Callable, Optional

from PySide6.QtCore import QCoreApplication, QObject, QThread, Signal

from ..engine.progress import Cancelled, Progress
from ..engine.diagnostics import OPERATIONS


class _Worker(QThread):
    progressed = Signal(int, int, str)
    detailed = Signal(object)
    succeeded = Signal(object)
    failed = Signal(str, str)
    was_cancelled = Signal()

    def __init__(self, fn: Callable[[Progress], Any], cancel: threading.Event, pause: threading.Event):
        super().__init__()
        self._fn = fn
        self._cancel = cancel
        self._pause = pause
        self.wall_seconds = self.cpu_seconds = 0.0
        self.outcome = "failed"

    def run(self) -> None:
        prog = Progress(lambda d, t, m: self.progressed.emit(d, t, m), self._cancel, pause=self._pause,
                        detail_callback=lambda detail: self.detailed.emit(detail))
        wall, cpu = time.perf_counter(), time.process_time()
        result, error = None, None
        try:
            result = self._fn(prog)
            self.outcome = "cancelled" if self._cancel.is_set() and result is None else "ok"
        except Cancelled:
            self.outcome = "cancelled"
        except Exception as e:  # surfaced to the user, never swallowed
            error = (f"{type(e).__name__}: {e}", traceback.format_exc())
        finally:
            self.wall_seconds = time.perf_counter() - wall
            self.cpu_seconds = time.process_time() - cpu
        if error is not None:
            self.failed.emit(*error)
        elif self.outcome == "cancelled":
            self.was_cancelled.emit()
        else:
            self.succeeded.emit(result)


class TaskRunner(QObject):
    started = Signal(str)
    progressed = Signal(int, int, str)
    detailed = Signal(object)       # {"items": (done, total), "bytes": (done, total), "unit": "file"} or {}
    paused_changed = Signal(bool)
    finished = Signal(str)          # outcome: "ok" | "failed" | "cancelled"
    error = Signal(str, str, str)   # title, message, details
    busy_changed = Signal(bool)
    measured = Signal(str, str, float, float)
    refused = Signal(str)           # a change was not started (browse & find window)

    VIEWER_REFUSAL = ("This window only browses and finds. Make this change in the Memoria window that opened "
                      "the library first.")

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker: Optional[_Worker] = None
        self._pending: Optional[tuple] = None
        self._cancel = threading.Event()
        self._pause = threading.Event()
        self.title = ""
        self._diagnostic_key = "other"
        self._diagnostic_started = 0.0
        self._measurement_reported = True
        self.parallel: Optional["ParallelTasks"] = None
        self.refusal = ""
        self.viewer = False    # a browse & find window: never changes files

    @property
    def busy(self) -> bool:
        return self._worker is not None or self._pending is not None

    @property
    def waiting(self) -> bool:
        """A change is waiting for read-only tasks to finish before it starts."""
        return self._pending is not None

    @property
    def active(self) -> bool:
        """Anything at all is running or waiting: a change, or a read-only task beside it."""
        return self.busy or bool(self.parallel is not None and self.parallel.tasks)

    @property
    def paused(self) -> bool:
        return self._pause.is_set()

    def run(self, title: str, fn: Callable[[Progress], Any],
            on_done: Optional[Callable[[Any], None]] = None,
            on_cancel: Optional[Callable[[], None]] = None, *, diagnostic_key: str = "other") -> bool:
        if self.busy:
            self.refusal = self.title
            return False
        if self.viewer:
            self.refusal = self.VIEWER_REFUSAL
            self.refused.emit(self.VIEWER_REFUSAL)
            return False
        if diagnostic_key not in OPERATIONS:
            raise ValueError("Unknown diagnostic task category")
        self.title = title
        searches = self.parallel.foreground() if self.parallel is not None else []
        if searches:
            # Changes never run while a search is still reading the library: wait for it (new searches
            # can't start meanwhile), then start automatically. Cancel drops the waiting change.
            self._pending = (title, fn, on_done, on_cancel, diagnostic_key)
            self.started.emit(title)
            self.busy_changed.emit(True)
            self.progressed.emit(0, 0, f"Waiting for “{searches[0].title}” to finish (it only reads files)…")
            self.parallel.changed.connect(self._start_pending)
            return True
        self._start(title, fn, on_done, on_cancel, diagnostic_key)
        return True

    def _start_pending(self) -> None:
        if self._pending is None or (self.parallel is not None and self.parallel.foreground()):
            return
        self.parallel.changed.disconnect(self._start_pending)
        pending, self._pending = self._pending, None
        self._start(*pending, announce=False)

    def _start(self, title, fn, on_done, on_cancel, diagnostic_key, announce: bool = True) -> None:
        self._diagnostic_key = diagnostic_key
        self._diagnostic_started = time.perf_counter()
        self._measurement_reported = False
        self.title = title
        self._cancel = threading.Event()
        self._pause = threading.Event()
        w = _Worker(fn, self._cancel, self._pause)
        self._worker = w
        w.progressed.connect(self.progressed)
        w.detailed.connect(self.detailed)

        def done(result):
            self._finish("ok")
            if on_done:
                on_done(result)

        def failed(msg, details):
            self._finish("failed")
            self.error.emit(title, msg, details)

        def cancelled():
            self._finish("cancelled")
            if on_cancel:
                on_cancel()

        w.succeeded.connect(done)
        w.failed.connect(failed)
        w.was_cancelled.connect(cancelled)
        if self.parallel is not None:
            self.parallel.hold_background(True)
        if announce:
            self.started.emit(title)
            self.busy_changed.emit(True)
        else:
            self.progressed.emit(0, 0, "Starting…")
        w.start()

    def cancel(self) -> None:
        if self._pending is not None and self._worker is None:
            on_cancel = self._pending[3]
            self._pending = None
            self.parallel.changed.disconnect(self._start_pending)
            self.finished.emit("cancelled")
            self.busy_changed.emit(False)
            if on_cancel:
                on_cancel()
            return
        self._cancel.set()
        if self._pause.is_set():
            self._pause.clear()
            self.paused_changed.emit(False)

    def pause(self) -> None:
        """Hold the running task at its next safe point (between files or copy chunks)."""
        if self._worker is not None and not self._pause.is_set():
            self._pause.set()
            self.paused_changed.emit(True)

    def resume(self) -> None:
        if self._pause.is_set():
            self._pause.clear()
            self.paused_changed.emit(False)

    def _finish(self, outcome: str) -> None:
        if self._pause.is_set():
            self._pause.clear()
            self.paused_changed.emit(False)
        w = self._worker
        if w is not None:
            w.wait(2000)
            self.report_measurement()
            w.deleteLater()
        self._worker = None
        if self.parallel is not None:
            self.parallel.hold_background(False)
        self.finished.emit(outcome)
        self.busy_changed.emit(False)

    def wait(self) -> None:
        """Wait for the running change and any read-only tasks running beside it."""
        if self._worker is not None:
            self._worker.wait()
        if self.parallel is not None:
            self.parallel.wait()

    def report_measurement(self) -> None:
        w = self._worker
        if w is not None and not w.isRunning() and not self._measurement_reported:
            self._measurement_reported = True
            self.measured.emit(self._diagnostic_key, w.outcome, w.wall_seconds, w.cpu_seconds)

    def active_measurement(self):
        if self._worker is None:
            return None
        return {"operation": self._diagnostic_key,
                "elapsed_seconds": time.perf_counter() - self._diagnostic_started}


class ParallelTask:
    """One read-only task in the parallel lane, with the latest progress it reported."""

    def __init__(self, task_id: int, title: str, key: str, background: bool):
        self.id, self.title, self.key, self.background = task_id, title, key, background
        self.cancel = threading.Event()
        self.pause = threading.Event()        # set by the user
        self.held = False                     # paused because a change is running
        self.done = self.total = 0
        self.message = "Starting…"
        self.detail: dict = {}
        self.started = time.monotonic()
        self.worker: Optional[_Worker] = None

    @property
    def fraction(self) -> Optional[float]:
        return min(1.0, self.done / self.total) if self.total else None


class ParallelTasks(QObject):
    """Read-only tasks (finding duplicates, similar photos, health check, people…) that run side by side.

    They never move, copy or delete files, so several can run at once. A task that changes files
    (TaskRunner) can't start while one of these is running, and background tasks (such as
    fingerprinting) are held while a change runs, then resume.
    """
    changed = Signal()                   # a task started or finished
    started = Signal(str)                # title
    progressed = Signal(int)             # task id
    error = Signal(str, str, str)

    def __init__(self, runner: TaskRunner, parent=None):
        super().__init__(parent)
        self.runner = runner
        runner.parallel = self
        self.tasks: dict[int, ParallelTask] = {}
        self._ids = 0
        self.refusal = ""

    def foreground(self) -> list[ParallelTask]:
        return [t for t in self.tasks.values() if not t.background]

    def running(self, title: str) -> bool:
        return any(t.title == title for t in self.tasks.values())

    def run(self, title: str, fn: Callable[[Progress], Any], on_done: Optional[Callable[[Any], None]] = None,
            on_cancel: Optional[Callable[[], None]] = None, *, diagnostic_key: str = "other",
            background: bool = False) -> bool:
        if self.runner.busy:
            self.refusal = self.runner.title
            return False
        if self.running(title):
            self.refusal = title
            return False
        if diagnostic_key not in OPERATIONS:
            raise ValueError("Unknown diagnostic task category")
        self._ids += 1
        task = ParallelTask(self._ids, title, diagnostic_key, background)
        worker = _Worker(fn, task.cancel, task.pause)
        task.worker = worker
        self.tasks[task.id] = task

        def progressed(done, total, message):
            task.done, task.total, task.message = done, total, message
            self.progressed.emit(task.id)

        def detailed(detail):
            task.detail = detail or {}

        def finish(outcome, callback=None, *args):
            worker.wait(2000)
            self.tasks.pop(task.id, None)
            self.runner.measured.emit(diagnostic_key, worker.outcome, worker.wall_seconds, worker.cpu_seconds)
            worker.deleteLater()
            self.changed.emit()
            self.runner.busy_changed.emit(self.runner.busy)  # pages re-check what they may start
            if callback:
                callback(*args)

        worker.progressed.connect(progressed)
        worker.detailed.connect(detailed)
        worker.succeeded.connect(lambda result: finish("ok", on_done, result) if on_done else finish("ok"))
        worker.failed.connect(lambda msg, details: finish("failed", self.error.emit, title, msg, details))
        worker.was_cancelled.connect(lambda: finish("cancelled", on_cancel) if on_cancel else finish("cancelled"))
        self.changed.emit()
        self.started.emit(title)
        worker.start()
        return True

    def cancel(self, task_id: int) -> None:
        task = self.tasks.get(task_id)
        if task:
            task.cancel.set()
            task.pause.clear()

    def toggle_pause(self, task_id: int) -> None:
        task = self.tasks.get(task_id)
        if task and not task.held:
            (task.pause.clear if task.pause.is_set() else task.pause.set)()
            self.progressed.emit(task_id)

    def hold_background(self, hold: bool) -> None:
        """Pause background tasks while a change runs (they read the files being changed), then resume."""
        for task in self.tasks.values():
            if task.background and task.held != hold:
                task.held = hold
                (task.pause.set if hold else task.pause.clear)()
                self.progressed.emit(task.id)

    def cancel_all(self) -> None:
        for task in list(self.tasks.values()):
            self.cancel(task.id)

    def wait(self) -> None:
        for task in list(self.tasks.values()):
            if task.worker is not None:
                task.worker.wait()


class _CallThread(QThread):
    done = Signal(int, object, object)

    def __init__(self, token: int, fn: Callable[[], Any]):
        super().__init__()
        self.token, self.fn = token, fn

    def run(self) -> None:
        try:
            self.done.emit(self.token, self.fn(), None)
        except Exception as e:  # reported to the caller
            self.done.emit(self.token, None, e)


class BackgroundCall(QObject):
    """Run small read-only computations off the UI thread; only the latest call's result is delivered.

    Used for page insights. Never use it for anything that changes files — those go through TaskRunner.
    """
    result = Signal(object)
    failed = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._token = 0
        self._threads: list[_CallThread] = []

    @property
    def running(self) -> bool:
        return any(t.isRunning() for t in self._threads)

    def call(self, fn: Callable[[], Any]) -> None:
        self._token += 1
        t = _CallThread(self._token, fn)
        t.done.connect(self._done)
        t.finished.connect(lambda t=t: self._reap(t))
        self._threads.append(t)
        t.start()

    def _done(self, token: int, value, error) -> None:
        if token != self._token:
            return
        if error is not None:
            self.failed.emit(error)
        else:
            self.result.emit(value)

    def _reap(self, t: _CallThread) -> None:
        if t in self._threads:
            self._threads.remove(t)
        t.deleteLater()

    def wait(self) -> None:
        for t in list(self._threads):
            t.wait()


_read_threads: set[_CallThread] = set()
_quit_hook = False


def _wait_reads() -> None:
    for thread in list(_read_threads):
        thread.wait()


def _release_read(thread) -> None:
    _read_threads.discard(thread)
    thread.deleteLater()


class LatestCall(QObject):
    """One running read and one replaceable pending read, with stale-result rejection.

    Workers must not touch widgets and must close their own SQLite connections.
    Destruction invalidates delivery without blocking the GUI; application exit waits
    for outstanding reads so a running QThread is never destroyed.
    """
    result = Signal(object)
    failed = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        global _quit_hook
        if not _quit_hook and QCoreApplication.instance() is not None:
            QCoreApplication.instance().aboutToQuit.connect(_wait_reads)
            _quit_hook = True
        self._token = 0
        self._thread = None
        self._pending = None
        self._alive = True
        self.destroyed.connect(lambda *_: self._destroyed())

    def _destroyed(self, *_):
        self._alive = False
        self.invalidate()

    @property
    def running(self) -> bool:
        return self._thread is not None or self._pending is not None

    def invalidate(self) -> None:
        self._token += 1
        self._pending = None

    def call(self, fn: Callable[[], Any]) -> None:
        if not self._alive:
            return
        self._token += 1
        self._pending = (self._token, fn)
        if self._thread is None:
            self._start()

    def _start(self) -> None:
        if self._pending is None or not self._alive:
            return
        token, fn = self._pending
        self._pending = None
        thread = _CallThread(token, fn)
        self._thread = thread
        _read_threads.add(thread)
        thread.done.connect(self._done)
        thread.finished.connect(self._finished)
        thread.finished.connect(lambda thread=thread: _release_read(thread))
        thread.start()

    def _done(self, token, value, error) -> None:
        if not self._alive or token != self._token:
            return
        if error is not None:
            self.failed.emit(error)
        else:
            self.result.emit(value)

    def _finished(self) -> None:
        self._thread = None
        self._start()

    def wait(self) -> None:
        self.invalidate()
        if self._thread is not None:
            self._thread.wait()
