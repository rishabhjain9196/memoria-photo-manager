"""Live view of what the running task is doing, for the task bar.

Engine code registers its worker pools with ``pool()``; drive read gates (``disk_speed``) report how
many readers are active. ``snapshot()`` combines these with process-wide counters (threads, CPU
time and bytes read/written) so the UI can show workers, drive type and I/O speed for any task.
"""
from __future__ import annotations

import contextlib
import itertools
import os
import threading
import time
from typing import Iterable, Iterator, Optional

_lock = threading.Lock()
_pools: dict[int, tuple[str, int]] = {}
_ids = itertools.count(1)


@contextlib.contextmanager
def pool(name: str, workers: int) -> Iterator[None]:
    """Mark a worker pool of ``workers`` threads as running for the duration of the block."""
    key = next(_ids)
    with _lock:
        _pools[key] = (name, max(1, int(workers)))
    try:
        yield
    finally:
        with _lock:
            _pools.pop(key, None)


def pools() -> list[tuple[str, int]]:
    """Running pools as (name, workers), same-named pools merged, in start order."""
    merged: dict[str, int] = {}
    with _lock:
        for name, workers in _pools.values():
            merged[name] = merged.get(name, 0) + workers
    return list(merged.items())


if os.name == "nt":
    import ctypes
    from ctypes import wintypes

    class _IO_COUNTERS(ctypes.Structure):
        _fields_ = [(name, ctypes.c_ulonglong) for name in (
            "ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
            "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]

    _k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _k32.GetCurrentProcess.restype = wintypes.HANDLE
    _k32.GetProcessIoCounters.restype = wintypes.BOOL
    _k32.GetProcessIoCounters.argtypes = [wintypes.HANDLE, ctypes.POINTER(_IO_COUNTERS)]

    def io_counters() -> Optional[tuple[int, int]]:
        """(bytes read, bytes written) by this process so far, or None if unavailable."""
        counters = _IO_COUNTERS()
        if not _k32.GetProcessIoCounters(_k32.GetCurrentProcess(), ctypes.byref(counters)):
            return None
        return counters.ReadTransferCount, counters.WriteTransferCount

    class _THREADENTRY32(ctypes.Structure):
        _fields_ = [("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD), ("th32ThreadID", wintypes.DWORD),
                    ("th32OwnerProcessID", wintypes.DWORD), ("tpBasePri", wintypes.LONG),
                    ("tpDeltaPri", wintypes.LONG), ("dwFlags", wintypes.DWORD)]

    _k32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    _k32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    _k32.Thread32First.argtypes = _k32.Thread32Next.argtypes = [wintypes.HANDLE, ctypes.POINTER(_THREADENTRY32)]
    _k32.CloseHandle.argtypes = [wintypes.HANDLE]

    def _os_threads() -> Optional[int]:
        """Threads in this process, including Qt and native ones that Python doesn't track."""
        snap = _k32.CreateToolhelp32Snapshot(0x4, 0)  # TH32CS_SNAPTHREAD
        if snap in (None, ctypes.c_void_p(-1).value):
            return None
        try:
            entry = _THREADENTRY32(dwSize=ctypes.sizeof(_THREADENTRY32))
            pid, count = os.getpid(), 0
            ok = _k32.Thread32First(snap, ctypes.byref(entry))
            while ok:
                count += entry.th32OwnerProcessID == pid
                ok = _k32.Thread32Next(snap, ctypes.byref(entry))
            return count or None
        finally:
            _k32.CloseHandle(snap)
else:
    def io_counters() -> Optional[tuple[int, int]]:
        try:
            with open("/proc/self/io") as f:
                values = dict(line.split(":", 1) for line in f)
            return int(values["rchar"]), int(values["wchar"])
        except (OSError, KeyError, ValueError):
            return None

    def _os_threads() -> Optional[int]:
        try:
            return len(os.listdir("/proc/self/task"))
        except OSError:
            return None


_thread_cache = [0.0, 0]
_thread_refresh = threading.Lock()


def _refresh_threads() -> None:
    try:
        _thread_cache[1] = _os_threads() or threading.active_count()
    finally:
        _thread_refresh.release()


def thread_count() -> int:
    """Process threads. Counting is slow on Windows (a system-wide snapshot), so it is refreshed at
    most every two seconds on a helper thread and the last value is returned immediately."""
    now = time.monotonic()
    if now - _thread_cache[0] >= 2.0 and _thread_refresh.acquire(blocking=False):
        _thread_cache[0] = now
        threading.Thread(target=_refresh_threads, name="memoria-thread-count", daemon=True).start()
    return _thread_cache[1] or threading.active_count()


def snapshot(paths: Iterable[str] = ()) -> dict:
    """Current activity. ``paths`` (e.g. library folders) add their drives when already detected."""
    from . import disk_speed

    drives = disk_speed.drive_activity()
    known = {d["drive"] for d in drives}
    for path in paths:
        plan = disk_speed.peek(path)
        if plan and plan["drive"] not in known:
            known.add(plan["drive"])
            drives.append({**plan, "active": 0})
    return {
        "time": time.monotonic(),
        "pools": pools(),
        "drives": drives,
        "threads": thread_count(),
        "cpu_seconds": time.process_time(),
        "cpus": os.cpu_count() or 1,
        "io": io_counters(),
    }
