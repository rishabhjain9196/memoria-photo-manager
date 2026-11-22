"""Disk media detection and per-drive read limits.

Spinning hard disks lose most of their throughput when several threads read different files at
once (the heads seek back and forth). ``io_gate`` hands out one shared semaphore per volume, sized
for the media, so every feature that reads originals takes turns on a hard disk while CPU work
(decoding, hashing bytes already in memory) stays fully parallel.

Set ``MEMORIA_IO_WORKERS`` to override the detected read concurrency.
"""
from __future__ import annotations

import ctypes
import os
import threading
import time
from pathlib import Path
from typing import Optional

_IOCTL_STORAGE_QUERY_PROPERTY = 0x002D1400
_StorageDeviceProperty = 0
_StorageDeviceSeekPenaltyProperty = 7
_StorageDeviceTrimProperty = 8
_DRIVE_REMOTE = 4

_BUS_TYPES = {
    0: "Unknown", 1: "SCSI", 2: "ATAPI", 3: "ATA", 4: "1394", 5: "SSA",
    6: "Fibre", 7: "USB", 8: "RAID", 9: "iSCSI", 10: "SAS", 11: "SATA",
    12: "SD", 13: "MMC", 14: "Virtual", 15: "FileBackedVirtual",
    16: "Spaces", 17: "NVMe", 18: "SCM", 19: "UFS"
}

if os.name == "nt":
    from ctypes import wintypes

    class _STORAGE_PROPERTY_QUERY(ctypes.Structure):
        _fields_ = [
            ("PropertyId", wintypes.DWORD),
            ("QueryType", wintypes.DWORD),
            ("AdditionalParameters", wintypes.BYTE * 1),
        ]

    class _BOOL_DESCRIPTOR(ctypes.Structure):
        """DEVICE_SEEK_PENALTY_DESCRIPTOR and DEVICE_TRIM_DESCRIPTOR share this layout."""
        _fields_ = [
            ("Version", wintypes.DWORD),
            ("Size", wintypes.DWORD),
            ("Value", wintypes.BOOLEAN),
        ]

    class _STORAGE_DEVICE_DESCRIPTOR(ctypes.Structure):
        _fields_ = [
            ("Version", wintypes.DWORD),
            ("Size", wintypes.DWORD),
            ("DeviceType", wintypes.BYTE),
            ("DeviceTypeModifier", wintypes.BYTE),
            ("RemovableMedia", wintypes.BOOLEAN),
            ("CommandQueueing", wintypes.BOOLEAN),
            ("VendorIdOffset", wintypes.DWORD),
            ("ProductIdOffset", wintypes.DWORD),
            ("ProductRevisionOffset", wintypes.DWORD),
            ("SerialNumberOffset", wintypes.DWORD),
            ("BusType", wintypes.DWORD),
            ("RawPropertiesLength", wintypes.DWORD),
            ("RawDeviceProperties", wintypes.BYTE * 512),
        ]

    _k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _k32.CreateFileW.restype = wintypes.HANDLE
    _k32.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
                                 wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    _k32.DeviceIoControl.restype = wintypes.BOOL
    _k32.DeviceIoControl.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD,
                                     wintypes.LPVOID, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD),
                                     wintypes.LPVOID]
    _k32.CloseHandle.argtypes = [wintypes.HANDLE]
    _k32.GetVolumePathNameW.restype = wintypes.BOOL
    _k32.GetVolumePathNameW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
    _k32.GetVolumeNameForVolumeMountPointW.restype = wintypes.BOOL
    _k32.GetVolumeNameForVolumeMountPointW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
    _k32.GetDriveTypeW.restype = wintypes.UINT
    _k32.GetDriveTypeW.argtypes = [wintypes.LPCWSTR]
    _INVALID_HANDLE = ctypes.c_void_p(-1).value


def _volume_of(path: str) -> tuple[str, Optional[str], bool]:
    """(cache key, device path to query, is_network) for the volume holding ``path``.

    Uses the real mount point, so folders mounted from another disk are measured as that disk.
    """
    if os.name != "nt":
        return os.path.abspath(path).split(os.sep)[0] or os.sep, None, False
    buf = ctypes.create_unicode_buffer(1024)
    if not _k32.GetVolumePathNameW(path, buf, len(buf)):
        drive = os.path.splitdrive(path)[0]
        return drive.lower() or path.lower(), (f"\\\\.\\{drive}" if drive.endswith(":") else None), False
    mount = buf.value
    if mount.startswith("\\\\") and not mount.startswith("\\\\?\\") or _k32.GetDriveTypeW(mount) == _DRIVE_REMOTE:
        return mount.lower(), None, True
    guid = ctypes.create_unicode_buffer(64)
    if _k32.GetVolumeNameForVolumeMountPointW(mount, guid, len(guid)):
        device = "\\\\.\\" + guid.value[4:].rstrip("\\")
    elif mount[1:2] == ":":
        device = f"\\\\.\\{mount[:2]}"
    else:
        device = None
    return mount.lower(), device, False


def _query_bool(handle, property_id: int) -> Optional[bool]:
    query = _STORAGE_PROPERTY_QUERY(PropertyId=property_id, QueryType=0)
    desc = _BOOL_DESCRIPTOR()
    returned = wintypes.DWORD(0)
    if _k32.DeviceIoControl(handle, _IOCTL_STORAGE_QUERY_PROPERTY, ctypes.byref(query), ctypes.sizeof(query),
                            ctypes.byref(desc), ctypes.sizeof(desc), ctypes.byref(returned), None) \
            and returned.value >= ctypes.sizeof(desc):
        return bool(desc.Value)
    return None


def _query_windows_volume(device: str) -> dict:
    """Seek penalty, TRIM support, bus type and product name via IOCTL_STORAGE_QUERY_PROPERTY."""
    handle = _k32.CreateFileW(device, 0, 1 | 2, None, 3, 0, None)
    if handle in (None, 0, _INVALID_HANDLE):
        return {}
    try:
        bus_name, product = "Unknown", ""
        query = _STORAGE_PROPERTY_QUERY(PropertyId=_StorageDeviceProperty, QueryType=0)
        desc = _STORAGE_DEVICE_DESCRIPTOR()
        returned = wintypes.DWORD(0)
        if _k32.DeviceIoControl(handle, _IOCTL_STORAGE_QUERY_PROPERTY, ctypes.byref(query), ctypes.sizeof(query),
                                ctypes.byref(desc), ctypes.sizeof(desc), ctypes.byref(returned), None):
            bus_name = _BUS_TYPES.get(desc.BusType, f"Type_{desc.BusType}")
            # The descriptor may report a Size larger than our buffer; only read what was returned.
            raw = ctypes.string_at(ctypes.addressof(desc), min(returned.value, ctypes.sizeof(desc)))
            if 0 < desc.ProductIdOffset < len(raw):
                product = raw[desc.ProductIdOffset:].split(b"\x00")[0].decode("ascii", "replace").strip()
        return {
            "seek_penalty": _query_bool(handle, _StorageDeviceSeekPenaltyProperty),
            "trim": _query_bool(handle, _StorageDeviceTrimProperty),
            "bus_type": bus_name,
            "product": product,
        }
    finally:
        _k32.CloseHandle(handle)


def _measure_read_latency(folder_path: Path, max_samples: int = 3) -> float:
    """Average milliseconds to open and read 4 KiB from up to ``max_samples`` files (0.0 = no sample).

    Recently read files come from the OS cache, so a low value proves nothing; only a high value
    is trusted (as a sign of a seeking disk).
    """
    try:
        latencies: list[float] = []
        for p in folder_path.rglob("*"):
            if len(latencies) >= max_samples:
                break
            if not p.is_file() or p.name.startswith("."):
                continue
            t0 = time.perf_counter()
            try:
                with open(p, "rb") as fp:
                    fp.read(4096)
            except OSError:
                continue
            latencies.append((time.perf_counter() - t0) * 1000)
        return sum(latencies) / len(latencies) if latencies else 0.0
    except Exception:
        return 0.0


def _classify(info: dict, path_obj: Path, network: bool) -> dict:
    cpu_count = os.cpu_count() or 4
    seek, trim = info.get("seek_penalty"), info.get("trim")
    bus = "Network" if network else info.get("bus_type", "Unknown")
    product = info.get("product", "")
    latency_ms = 0.0
    if network:
        media = "unknown"
    elif seek is True:
        media = "hdd"
    elif seek is False:
        media = "ssd"
    elif bus == "USB" and trim is not True:
        media = "hdd"  # most USB enclosures without a clear answer are portable hard disks
    elif bus == "NVMe" or trim is True:
        media = "ssd"
    else:
        latency_ms = _measure_read_latency(path_obj)
        media = "hdd" if latency_ms > 20.0 else "unknown"

    if media == "hdd":
        workers = 1 if bus == "USB" else 2
        video_workers = 1
        tier = f"Mechanical HDD ({product or bus})"
    elif bus == "NVMe":
        workers = max(4, min(12, cpu_count))
        video_workers = max(1, min(4, workers // 2))
        tier = f"NVMe SSD ({product})" if product else "NVMe High-Speed SSD"
    elif media == "ssd":
        workers = max(2, min(8, cpu_count))
        video_workers = max(1, min(3, workers // 2))
        tier = f"SSD ({product or bus})" if (product or bus != "Unknown") else "Solid State Drive"
    else:
        # Unknown media is treated cautiously: two readers barely slow an SSD and spare a hard disk.
        workers, video_workers = 2, 1
        tier = "Network folder" if network else "Standard Storage"

    override = os.environ.get("MEMORIA_IO_WORKERS", "").strip()
    if override.isdigit() and int(override) > 0:
        workers = int(override)
        video_workers = max(1, min(video_workers, workers))
    return {
        "is_hdd": media == "hdd",
        "is_ssd": media == "ssd",
        "bus_type": bus,
        "product": product,
        "tier": tier,
        "workers": workers,
        "video_workers": video_workers,
        "latency_ms": round(latency_ms, 2),
    }


class _Gate:
    """Per-volume read semaphore that also counts active readers for the task bar."""

    def __init__(self, plan: dict):
        self.plan = plan
        self._sem = threading.BoundedSemaphore(plan["workers"])
        self.active = 0
        self.last_used = 0.0

    def acquire(self) -> bool:
        self._sem.acquire()
        with _lock:
            self.active += 1
            self.last_used = time.monotonic()
        return True

    def release(self) -> None:
        with _lock:
            self.active -= 1
            self.last_used = time.monotonic()
        self._sem.release()

    def __enter__(self):
        return self.acquire()

    def __exit__(self, *exc) -> None:
        self.release()


_cache: dict[str, dict] = {}
_paths: dict[str, str] = {}
_gates: dict[str, _Gate] = {}
_lock = threading.Lock()


def detect_disk(path: str | Path) -> dict:
    """Detect the storage media behind ``path`` and recommend read concurrency.

    Returns a dict with: path, drive, is_hdd, is_ssd, bus_type, product, tier,
    workers (concurrent file reads), video_workers, latency_ms. Cached per volume.
    """
    path_obj = Path(path).resolve()
    key, device, network = _volume_of(str(path_obj))
    with _lock:
        cached = _cache.get(key)
    if cached is None:
        info: dict = {}
        if device:
            try:
                info = _query_windows_volume(device)
            except Exception:
                info = {}
        cached = _classify(info, path_obj, network)
        cached["drive"] = key
        with _lock:
            cached = _cache.setdefault(key, cached)
    with _lock:
        _paths[str(path)] = _paths[str(path_obj)] = key
    return {"path": str(path_obj), **cached}


def peek(path: str | Path) -> Optional[dict]:
    """The cached plan for ``path`` if it was detected before; never touches the disk."""
    with _lock:
        key = _paths.get(str(path))
        return dict(_cache[key]) if key in _cache else None


def io_gate(path: str | Path) -> _Gate:
    """Shared gate limiting concurrent original-file reads on the volume holding ``path``."""
    plan = detect_disk(path)
    with _lock:
        gate = _gates.get(plan["drive"])
        if gate is None:
            gate = _gates[plan["drive"]] = _Gate(plan)
    return gate


def drive_activity(recent: float = 5.0) -> list[dict]:
    """Drives whose gate is in use or was used in the last ``recent`` seconds, with active readers."""
    now = time.monotonic()
    with _lock:
        return [{**gate.plan, "active": gate.active} for gate in _gates.values()
                if gate.active or now - gate.last_used <= recent]


def root_gates(lib) -> dict[int, _Gate]:
    """{library root id: read gate} for every registered library folder."""
    return {source["id"]: io_gate(source["path"]) for source in lib.roots()}


def read_workers(lib, root_ids=None) -> int:
    """Total concurrent reads worth scheduling across the given (default: all) library folders."""
    seen, total = set(), 0
    for source in lib.roots():
        if root_ids is not None and source["id"] not in root_ids:
            continue
        plan = detect_disk(source["path"])
        if plan["drive"] not in seen:
            seen.add(plan["drive"])
            total += plan["workers"]
    return max(1, total)


def reset_cache() -> None:
    """Forget detected drives (e.g. after a drive is swapped under the same letter)."""
    with _lock:
        _cache.clear()
        _paths.clear()
        _gates.clear()
