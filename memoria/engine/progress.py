"""Progress reporting and cancellation shared by every long-running engine call."""
from __future__ import annotations

import threading
import time
from typing import Callable, Optional

ProgressCallback = Callable[[int, int, str], None]


class Cancelled(Exception):
    pass


class Progress:
    """Throttled progress reporter with cooperative cancellation."""

    def __init__(self, callback: Optional[ProgressCallback] = None,
                 cancel: Optional[threading.Event] = None, interval: float = 0.08):
        self._cb = callback
        self.cancel_event = cancel or threading.Event()
        self._interval = interval
        self._last = 0.0

    def update(self, done: int, total: int, message: str = "", force: bool = False) -> None:
        if self.cancel_event.is_set():
            raise Cancelled()
        if self._cb is None:
            return
        now = time.monotonic()
        if force or done >= total or now - self._last >= self._interval:
            self._last = now
            self._cb(done, total, message)

    def check(self) -> None:
        if self.cancel_event.is_set():
            raise Cancelled()

    @property
    def cancelled(self) -> bool:
        return self.cancel_event.is_set()


NULL = Progress()
