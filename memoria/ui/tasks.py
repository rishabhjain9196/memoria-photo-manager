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
    succeeded = Signal(object)
    failed = Signal(str, str)
    was_cancelled = Signal()

    def __init__(self, fn: Callable[[Progress], Any], cancel: threading.Event):
        super().__init__()
        self._fn = fn
        self._cancel = cancel
        self.wall_seconds = self.cpu_seconds = 0.0
        self.outcome = "failed"

    def run(self) -> None:
        prog = Progress(lambda d, t, m: self.progressed.emit(d, t, m), self._cancel)
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
    finished = Signal(str)          # outcome: "ok" | "failed" | "cancelled"
    error = Signal(str, str, str)   # title, message, details
    busy_changed = Signal(bool)
    measured = Signal(str, str, float, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker: Optional[_Worker] = None
        self._cancel = threading.Event()
        self.title = ""
        self._diagnostic_key = "other"
        self._diagnostic_started = 0.0
        self._measurement_reported = True

    @property
    def busy(self) -> bool:
        return self._worker is not None

    def run(self, title: str, fn: Callable[[Progress], Any],
            on_done: Optional[Callable[[Any], None]] = None,
            on_cancel: Optional[Callable[[], None]] = None, *, diagnostic_key: str = "other") -> bool:
        if self.busy:
            return False
        if diagnostic_key not in OPERATIONS:
            raise ValueError("Unknown diagnostic task category")
        self._diagnostic_key = diagnostic_key
        self._diagnostic_started = time.perf_counter()
        self._measurement_reported = False
        self.title = title
        self._cancel = threading.Event()
        w = _Worker(fn, self._cancel)
        self._worker = w
        w.progressed.connect(self.progressed)

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
        self.started.emit(title)
        self.busy_changed.emit(True)
        w.start()
        return True

    def cancel(self) -> None:
        self._cancel.set()

    def _finish(self, outcome: str) -> None:
        w = self._worker
        if w is not None:
            w.wait(2000)
            self.report_measurement()
            w.deleteLater()
        self._worker = None
        self.finished.emit(outcome)
        self.busy_changed.emit(False)

    def wait(self) -> None:
        if self._worker is not None:
            self._worker.wait()

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
