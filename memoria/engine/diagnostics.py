"""Opt-in aggregate diagnostics. Never serialize catalogue rows, paths or arbitrary strings."""
from __future__ import annotations

import ctypes
import json
import math
import os
import platform
import re
import shutil
import subprocess
import threading
import time
import uuid
from contextlib import contextmanager
from pathlib import Path

from .. import __version__
from . import catalogue, config
from .db import METADATA_VERSION, SCHEMA_VERSION, Library
from .progress import Cancelled

OPERATIONS = frozenset(("index", "reset", "checkup", "undo", "sample", "other", "photos", "people",
                       "duplicates", "similar", "tidy", "organize", "albums", "editor", "story",
                       "video", "health", "compare", "history", "overview", "insights", "browse_page", "preview"))
VIDEO_CODECS = frozenset(("h264", "hevc", "av1", "vp8", "vp9", "mpeg4", "mpeg2video", "mjpeg",
                         "prores", "dnxhd", "wmv3", "vc1", "theora", "rawvideo", "png"))
AUDIO_CODECS = frozenset(("aac", "mp3", "opus", "vorbis", "flac", "alac", "ac3", "eac3", "dts", "pcm"))
FORMATS = config.MEDIA_EXT | {".pdf", ".txt", ".json", ".xmp", ".aae", ".db", ".ini"}
OUTCOMES = frozenset(("ok", "failed", "cancelled"))


def repository_root():
    root = Path(__file__).resolve().parents[2]
    return root if (root / "pyproject.toml").is_file() and (root / "memoria").is_dir() else None


def source_revision(root: Path) -> str | None:
    try:
        result = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True,
                                text=True, timeout=5,
                                creationflags=0x08000000 if os.name == "nt" else 0)
    except (OSError, subprocess.TimeoutExpired):
        return None
    revision = result.stdout.strip()
    return revision if result.returncode == 0 and re.fullmatch(r"[a-f0-9]{40}", revision) else None


def process_memory() -> dict:
    if os.name == "nt":
        from ctypes import wintypes
        class Counters(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("faults", wintypes.DWORD)] + [
                (name, ctypes.c_size_t) for name in
                ("peak", "working", "peak_paged", "paged", "peak_nonpaged", "nonpaged", "pagefile", "peak_pagefile")]
        try:
            kernel = ctypes.WinDLL("kernel32", use_last_error=True)
            psapi = ctypes.WinDLL("psapi", use_last_error=True)
            kernel.GetCurrentProcess.restype = wintypes.HANDLE
            psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
            counters = Counters()
            counters.cb = ctypes.sizeof(counters)
            if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
                raise OSError("Memory sampling unavailable")
            return {"available": True, "working_set_mib": round(counters.working / 1024**2, 1),
                    "lifetime_peak_working_set_mib": round(counters.peak / 1024**2, 1),
                    "scope": "app_process_only"}
        except OSError:
            return {"available": False, "scope": "app_process_only"}
    return {"available": False, "scope": "app_process_only"}


def physical_memory_gib():
    if os.name != "nt":
        return None
    from ctypes import wintypes
    class MemoryStatus(ctypes.Structure):
        _fields_ = [("length", wintypes.DWORD), ("load", wintypes.DWORD)] + [
            (name, ctypes.c_ulonglong) for name in
            ("total", "available", "pagefile", "available_pagefile", "virtual", "available_virtual", "extended")]
    status = MemoryStatus()
    status.length = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        return None
    return round(status.total / 1024**3)


class Metrics:
    """Fixed operation keys and aggregate counters only; no per-event log or raw task titles."""
    def __init__(self):
        self._lock = threading.Lock()
        self.enabled = False
        self.generation = 0
        self._values = {}

    def reset(self, enabled: bool) -> None:
        with self._lock:
            self.enabled = enabled
            self.generation += 1
            self._values.clear()

    def record(self, operation: str, outcome: str, wall: float, cpu: float, generation=None) -> None:
        if operation not in OPERATIONS or outcome not in OUTCOMES:
            raise ValueError("Invalid diagnostic operation or outcome")
        if any(not math.isfinite(value) or value < 0 for value in (wall, cpu)):
            raise ValueError("Invalid diagnostic duration")
        with self._lock:
            if not self.enabled or generation is not None and generation != self.generation:
                return
            row = self._values.setdefault(operation, {"count": 0, "wall_seconds_total": 0.0,
                                                       "wall_seconds_max": 0.0, "app_cpu_seconds_total": 0.0,
                                                       "outcomes": {key: 0 for key in sorted(OUTCOMES)}})
            row["count"] += 1
            row["outcomes"][outcome] += 1
            row["wall_seconds_total"] += wall
            row["wall_seconds_max"] = max(row["wall_seconds_max"], wall)
            row["app_cpu_seconds_total"] += cpu

    @contextmanager
    def measure(self, operation: str):
        with self._lock:
            enabled, generation = self.enabled, self.generation
        if not enabled:
            yield
            return
        wall, cpu, outcome = time.perf_counter(), time.process_time(), "ok"
        try:
            yield
        except Cancelled:
            outcome = "cancelled"
            raise
        except BaseException:
            outcome = "failed"
            raise
        finally:
            self.record(operation, outcome, time.perf_counter() - wall, time.process_time() - cpu, generation)

    def snapshot(self) -> dict:
        with self._lock:
            result = json.loads(json.dumps(self._values))
        for row in result.values():
            row["wall_seconds_mean"] = row["wall_seconds_total"] / row["count"]
            for key, value in list(row.items()):
                if isinstance(value, float):
                    row[key] = round(value, 3)
        return result

    def publish(self, path: Path, report: dict, generation: int) -> bool:
        """Publish atomically only if the same library is still opted in."""
        with self._lock:
            if not self.enabled or generation != self.generation:
                return False
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_name(f".{path.stem}-{uuid.uuid4().hex}.tmp")
        try:
            with temp.open("x", encoding="utf-8") as file:
                json.dump(report, file, indent=2, sort_keys=True, allow_nan=False)
                file.write("\n")
                file.flush()
                os.fsync(file.fileno())
            with self._lock:
                if not self.enabled or generation != self.generation:
                    return False
                os.replace(temp, path)
            return True
        finally:
            temp.unlink(missing_ok=True)


def _histogram(db, expression: str, bounds: tuple, labels: tuple, where="1") -> dict:
    case = f"CASE WHEN ({expression}) IS NULL OR ({expression})<0 THEN 'unknown' "
    params = []
    for bound, label in zip(bounds, labels):
        case += f"WHEN ({expression})<? THEN ? "
        params += [bound, label]
    case += "ELSE ? END"
    params.append(labels[-1])
    return {row[0]: row[1] for row in db.execute(
        f"SELECT {case} AS bucket,COUNT(*) FROM files f WHERE {where} GROUP BY bucket", params)}


def _category(column: str, allowed, *, audio=False) -> tuple[str, list]:
    values = sorted(allowed)
    sql = f"CASE WHEN {column} IS NULL THEN 'unknown' "
    if audio:
        sql += f"WHEN {column}='' THEN 'no_audio' WHEN substr(lower({column}),1,4)='pcm_' THEN 'pcm' "
    sql += f"WHEN lower({column}) IN ({','.join('?' for _ in values)}) THEN lower({column}) ELSE 'other' END"
    return sql, values


def _safe_groups(db, column: str, allowed: frozenset, where="1", *, audio=False) -> dict:
    expression, params = _category(column, allowed, audio=audio)
    return dict(db.execute(f"SELECT {expression} AS bucket,COUNT(*) FROM files WHERE {where} GROUP BY bucket", params))


def build_report(lib: Library, metrics: Metrics, revision=None, active_task=None) -> dict:
    """Read an aggregate snapshot only. No EXIF values, rows, messages or content hashes are exported."""
    db = lib.db
    db.execute("BEGIN")
    try:
        row = db.execute(
            "SELECT COUNT(*) AS files,COALESCE(SUM(size),0) AS bytes,"
            "SUM(kind='image') AS photos,SUM(kind='video') AS videos,SUM(kind NOT IN ('image','video')) AS other_files,"
            "SUM(kind!='other' AND (analyzed=0 OR COALESCE(metadata_version,0)<?)) AS awaiting_analysis,"
            "SUM(error IS NOT NULL) AS errors,"
            "SUM(width>0 AND height>0) AS with_dimensions,"
            "SUM(lat BETWEEN -90 AND 90 AND lon BETWEEN -180 AND 180) AS with_valid_gps,"
            "SUM(camera IS NOT NULL AND camera!='') AS with_camera,"
            "SUM(iso>0) AS with_iso,SUM(aperture>0) AS with_aperture,"
            "SUM(exposure_seconds>0) AS with_exposure,SUM(focal_length_mm>0) AS with_focal_length,"
            "SUM(kind='video' AND fps>0) AS with_reported_fps FROM files", (METADATA_VERSION,)).fetchone()
        summary = {key: int(row[key] or 0) for key in row.keys()}
        for table in ("missing_files", "parked_files", "faces", "face_scans", "albums", "album_items"):
            summary[f"{table}_records"] = db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        summary["folders"] = db.execute("SELECT COUNT(DISTINCT folder) FROM files").fetchone()[0]
        distributions = {
            "formats": _safe_groups(db, "ext", frozenset(FORMATS)),
            "video_codecs": _safe_groups(db, "video_codec", VIDEO_CODECS, "kind='video'"),
            "audio_codecs": _safe_groups(db, "audio_codec", AUDIO_CODECS, "kind='video'", audio=True),
            "date_sources": _safe_groups(db, "date_source", frozenset(("exif", "metadata", "filename", "modified"))),
            "file_size": _histogram(db, "f.size", (1024**2, 10*1024**2, 100*1024**2, 1024**3),
                                    ("under_1_MiB", "1_to_10_MiB", "10_to_100_MiB", "100_MiB_to_1_GiB", "1_GiB_or_more")),
            "megapixels": _histogram(db, catalogue.METRICS["megapixels"], (1, 4, 12, 24, 48),
                                     ("under_1", "1_to_4", "4_to_12", "12_to_24", "24_to_48", "48_or_more"),
                                     "kind IN ('image','video')"),
            "video_duration": _histogram(db, catalogue.METRICS["duration"], (10, 60, 300, 1800, 7200),
                                         ("under_10_s", "10_to_60_s", "1_to_5_min", "5_to_30_min", "30_to_120_min",
                                          "2_hours_or_more"), "kind='video'"),
            "video_overall_mbps": _histogram(db, catalogue.METRICS["bitrate"], (1, 5, 20, 50),
                                             ("under_1", "1_to_5", "5_to_20", "20_to_50", "50_or_more"), "kind='video'"),
            "video_fps": _histogram(db, catalogue.METRICS["fps"], (24, 31, 61),
                                    ("under_24", "24_to_under_31", "31_to_under_61", "61_or_more"), "kind='video'"),
        }
        error_case = ("CASE WHEN error LIKE 'PermissionError:%' THEN 'permission' "
                      "WHEN error LIKE 'FileNotFoundError:%' THEN 'not_found' "
                      "WHEN error LIKE 'UnidentifiedImageError:%' THEN 'image_unidentified' "
                      "WHEN error LIKE '%truncated%' THEN 'truncated' "
                      "WHEN error LIKE '%No video stream found%' THEN 'no_video_stream' "
                      "WHEN error LIKE 'TimeoutExpired:%' THEN 'timeout' ELSE 'other' END")
        errors = dict(db.execute(f"SELECT {error_case} AS category,COUNT(*) FROM files "
                                 "WHERE error IS NOT NULL GROUP BY category"))
        errors_by_format = {}
        format_sql, format_params = _category("ext", FORMATS)
        for key, category, count in db.execute(f"SELECT {format_sql} AS format,{error_case} AS category,COUNT(*) FROM files "
                                                "WHERE error IS NOT NULL GROUP BY format,category", format_params):
            group = errors_by_format.setdefault(key, {})
            group[category] = group.get(category, 0) + count
        format_storage = {}
        for key, count, size in db.execute(
                f"SELECT {format_sql} AS format,COUNT(*),SUM(size) FROM files GROUP BY format", format_params):
            group = format_storage.setdefault(key, {"files": 0, "bytes": 0})
            group["files"] += count
            group["bytes"] += int(size or 0)
        outcome_sql, outcome_params = _category("status", ("pending", "done", "failed", "skipped", "undone", "purged"))
        outcomes = dict(db.execute(
            f"SELECT {outcome_sql} AS category,COUNT(*) FROM operations GROUP BY category", outcome_params))
        db.execute("COMMIT")
    except BaseException:
        db.execute("ROLLBACK")
        raise
    system = {"os": "Windows" if os.name == "nt" else "Other", "python": platform.python_version(),
              "logical_cpus": os.cpu_count(), "physical_memory_gib": physical_memory_gib(),
              "process_memory": process_memory()}
    if os.name == "nt":
        import sys
        version = sys.getwindowsversion()
        system["windows_version"] = f"{version.major}.{version.minor}.{version.build}"
    try:
        disk = shutil.disk_usage(lib.root)
        system["library_disk"] = {"available": True, "free_gib_floor": disk.free // 1024**3,
                                  "total_gib_floor": disk.total // 1024**3,
                                  "location": "network" if str(lib.root).startswith("\\\\") else "local_or_mapped"}
        if os.name == "nt":
            from ctypes import wintypes
            get_type = ctypes.windll.kernel32.GetDriveTypeW
            get_type.argtypes = [wintypes.LPCWSTR]
            get_type.restype = wintypes.UINT
            system["library_disk"]["drive_kind"] = {2: "removable", 3: "fixed", 4: "network",
                                                       5: "optical", 6: "ramdisk"}.get(get_type(lib.root.anchor), "unknown")
    except OSError:
        system["library_disk"] = {"available": False}
    if revision is not None and not re.fullmatch(r"[a-f0-9]{40}", revision):
        raise ValueError("Invalid source revision")
    if active_task is not None:
        if active_task["operation"] not in OPERATIONS or not math.isfinite(active_task["elapsed_seconds"]):
            raise ValueError("Invalid active task measurement")
        active_task = {"operation": active_task["operation"],
                       "elapsed_seconds": round(max(0, active_task["elapsed_seconds"]), 3)}
    return {"report_schema": 1, "app_version": __version__, "git_head": revision,
            "catalogue_schema": SCHEMA_VERSION, "system": system, "library": summary,
            "distributions": distributions, "format_storage": format_storage,
            "error_categories": errors, "errors_by_format": errors_by_format, "operation_outcomes": outcomes,
            "timings": metrics.snapshot(), "task_in_progress": active_task,
            "measurement_notes": ["No media or per-file records are included.",
                                  "App CPU and memory exclude FFmpeg child processes.",
                                  "Per-operation CPU deltas can include overlapping UI/background work.",
                                  "Git HEAD does not identify uncommitted source changes.",
                                  "Drive kind does not distinguish an SSD from a hard disk.",
                                  "Timing outcome ok means the worker returned, not that every file succeeded.",
                                  "Reports may be incomplete while indexing or after interruption."]}
