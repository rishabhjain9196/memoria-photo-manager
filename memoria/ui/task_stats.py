"""Live statistics for the running task: counts, speed, elapsed (excluding pauses) and time left."""
from __future__ import annotations

import time
from collections import deque
from typing import Callable, Optional

from .widgets import fmt_size

WINDOW = 8.0        # seconds of recent work used for the speed
MIN_ETA_SECONDS = 2.0


def fmt_secs(seconds: float) -> str:
    s = int(seconds)
    if s < 60:
        return f"{s} s"
    if s < 3600:
        return f"{s // 60} min {s % 60:02d} s"
    return f"{s // 3600} h {s % 3600 // 60:02d} min"


class TaskStats:
    def __init__(self, clock: Callable[[], float] = time.monotonic):
        self.clock = clock
        self.start()

    def start(self) -> None:
        self.started = self.clock()
        self.paused_total = 0.0
        self.paused_at: Optional[float] = None
        self.fraction: Optional[float] = None
        self.detail: dict = {}
        self.samples: deque = deque()

    # pausing ------------------------------------------------------------------------------
    @property
    def paused(self) -> bool:
        return self.paused_at is not None

    def pause(self) -> None:
        if self.paused_at is None:
            self.paused_at = self.clock()

    def resume(self) -> None:
        if self.paused_at is not None:
            self.paused_total += self.clock() - self.paused_at
            self.paused_at = None
            self.samples.clear()  # speed restarts after a pause instead of averaging the idle gap

    def elapsed(self) -> float:
        now = self.paused_at if self.paused_at is not None else self.clock()
        return max(0.0, now - self.started - self.paused_total)

    # progress -----------------------------------------------------------------------------
    def update(self, fraction: Optional[float], detail: Optional[dict] = None) -> None:
        self.fraction = fraction
        if detail is not None:
            if self.detail.get("items", (0, None))[1] != detail.get("items", (0, None))[1]:
                self.samples.clear()   # a new phase with different units
            self.detail = detail
        if self.paused:
            return
        now = self.elapsed()
        items = self.detail.get("items", (0, 0))[0]
        size = self.detail.get("bytes", (0, 0))[0]
        self.samples.append((now, items, size))
        while len(self.samples) > 2 and now - self.samples[0][0] > WINDOW:
            self.samples.popleft()

    def rates(self) -> tuple[Optional[float], Optional[float]]:
        """(items per second, bytes per second) over the recent window."""
        if len(self.samples) < 2:
            return None, None
        (t0, i0, b0), (t1, i1, b1) = self.samples[0], self.samples[-1]
        if t1 - t0 < 0.5:
            return None, None
        dt = t1 - t0
        return (i1 - i0) / dt, ((b1 - b0) / dt if "bytes" in self.detail else None)

    def remaining(self) -> Optional[float]:
        if self.elapsed() < MIN_ETA_SECONDS:
            return None
        item_rate, byte_rate = self.rates()
        if "bytes" in self.detail and byte_rate:
            done, total = self.detail["bytes"]
            return max(0.0, (total - done) / byte_rate)
        if "items" in self.detail and item_rate:
            done, total = self.detail["items"]
            return max(0.0, (total - done) / item_rate)
        if self.fraction and 0.02 < self.fraction < 1:
            return self.elapsed() * (1 - self.fraction) / self.fraction
        return None

    # text ---------------------------------------------------------------------------------
    def counts_text(self) -> str:
        parts = []
        if "items" in self.detail:
            done, total = self.detail["items"]
            unit = self.detail.get("unit", "item")
            parts.append(f"{done:,} of {total:,} {unit}{'' if total == 1 else 's'}")
        if "bytes" in self.detail:
            done, total = self.detail["bytes"]
            parts.append(f"{fmt_size(done)} of {fmt_size(total)}")
        return " · ".join(parts)

    def speed_text(self) -> str:
        if self.paused:
            return ""
        item_rate, byte_rate = self.rates()
        parts = []
        if byte_rate is not None:
            parts.append(f"{fmt_size(byte_rate)}/s")
        if item_rate is not None and "items" in self.detail:
            unit = self.detail.get("unit", "item")
            parts.append(f"{item_rate:.1f} {unit}s/s" if item_rate < 10 else f"{item_rate:,.0f} {unit}s/s")
        return " · ".join(parts)

    def time_text(self) -> str:
        text = f"{fmt_secs(self.elapsed())} elapsed"
        if self.paused:
            return text + " · paused"
        left = self.remaining()
        if left is not None and (self.fraction or 0) < 0.999:
            text += f" · about {fmt_secs(left)} left"
        return text
