"""Run engine calls on a background thread with progress, cancellation and error reporting.

Only one task runs at a time; pages check ``runner.busy`` and listen to ``busy_changed`` so the
user can never start two conflicting file operations.
"""
from __future__ import annotations

import threading
import traceback
from typing import Any, Callable, Optional

from PySide6.QtCore import QObject, QThread, Signal

from ..engine.progress import Cancelled, Progress


class _Worker(QThread):
    progressed = Signal(int, int, str)
    succeeded = Signal(object)
    failed = Signal(str, str)
    was_cancelled = Signal()

    def __init__(self, fn: Callable[[Progress], Any], cancel: threading.Event):
        super().__init__()
        self._fn = fn
        self._cancel = cancel

    def run(self) -> None:
        prog = Progress(lambda d, t, m: self.progressed.emit(d, t, m), self._cancel)
        try:
            result = self._fn(prog)
        except Cancelled:
            self.was_cancelled.emit()
            return
        except Exception as e:  # surfaced to the user, never swallowed
            self.failed.emit(f"{type(e).__name__}: {e}", traceback.format_exc())
            return
        if self._cancel.is_set() and result is None:
            self.was_cancelled.emit()
        else:
            self.succeeded.emit(result)


class TaskRunner(QObject):
    started = Signal(str)
    progressed = Signal(int, int, str)
    finished = Signal(str)          # outcome: "ok" | "failed" | "cancelled"
    error = Signal(str, str, str)   # title, message, details
    busy_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker: Optional[_Worker] = None
        self._cancel = threading.Event()
        self.title = ""

    @property
    def busy(self) -> bool:
        return self._worker is not None

    def run(self, title: str, fn: Callable[[Progress], Any],
            on_done: Optional[Callable[[Any], None]] = None,
            on_cancel: Optional[Callable[[], None]] = None) -> bool:
        if self.busy:
            return False
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
        self._worker = None
        if w is not None:
            w.wait(2000)
            w.deleteLater()
        self.finished.emit(outcome)
        self.busy_changed.emit(False)

    def wait(self) -> None:
        if self._worker is not None:
            self._worker.wait()
