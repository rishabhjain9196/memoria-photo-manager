"""Progress reporting and cancellation shared by every long-running engine call."""
from __future__ import annotations

import threading
import time
from typing import Callable, Optional

ProgressCallback = Callable[[int, int, str], None]


class Cancelled(Exception):
    pass


class Progress:
    """Throttled progress reporter with cooperative cancellation.

    ``total == 0`` means "unknown amount of work" (the UI shows a moving bar).
    """

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
        if force or (total and done >= total) or now - self._last >= self._interval:
            self._last = now
            self._cb(done, total, message)

    def check(self) -> None:
        if self.cancel_event.is_set():
            raise Cancelled()

    @property
    def cancelled(self) -> bool:
        return self.cancel_event.is_set()

    def step(self, index: int, count: int, label: str) -> "StepProgress":
        """Progress for step ``index`` (0-based) of ``count`` sequential steps, scaled into this one."""
        return StepProgress(self, index, count, label)


class StepProgress(Progress):
    """Maps a sub-task's progress onto its slice of a parent's 0–1000 scale."""

    SCALE = 1000

    def __init__(self, parent: Progress, index: int, count: int, label: str):
        super().__init__(None, parent.cancel_event)
        self.parent, self.index, self.count, self.label = parent, index, count, label

    def update(self, done: int, total: int, message: str = "", force: bool = False) -> None:
        frac = min(1.0, done / total) if total else 0.0
        overall = int(self.SCALE * (self.index + frac) / self.count)
        text = f"Step {self.index + 1} of {self.count} · {self.label}"
        if message:
            text += f" — {message}"
        self.parent.update(overall, self.SCALE, text, force)


NULL = Progress()
