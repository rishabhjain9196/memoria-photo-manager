"""Health check: prove files are intact.

The first check records a fingerprint (full-content hash) for every file. Later checks re-read
each file and compare:
* same size and modified time but different content → silent damage (bit rot, bad sector, sync bug)
* different modified time → the file was edited on purpose; the fingerprint is refreshed
* photos are also decoded to catch truncated or corrupt images
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from . import config
from .db import Library
from .hashing import full_hash
from .progress import Progress
from .scanner import scan

STATUS_LABEL = {
    "ok": "Intact",
    "new": "Fingerprint recorded (first check)",
    "edited": "Edited since last check",
    "damaged": "Content changed without being edited — possible damage",
    "unreadable": "Can't be opened",
    "missing": "Missing since last scan",
}


@dataclass
class HealthReport:
    counts: dict[str, int] = field(default_factory=dict)
    problems: list[dict] = field(default_factory=list)   # rows with "status" and "detail"
    checked: int = 0
    bytes: int = 0


def _decode_ok(path) -> Optional[str]:
    from PIL import Image
    try:
        from .config import longpath
        with Image.open(longpath(path)) as im:
            if im.format == "JPEG":
                im.draft("RGB", (256, 256))
            im.load()
        return None
    except Exception as e:
        return f"{type(e).__name__}: {e}"[:200]


def run_health(lib: Library, progress: Optional[Progress] = None, decode_images: bool = True) -> HealthReport:
    progress = progress or Progress()
    sres = scan(lib, progress)
    rows = [dict(r) for r in lib.files()]
    rep = HealthReport(counts={k: 0 for k in STATUS_LABEL})
    rep.counts["missing"] = sres.removed
    total = len(rows)
    total_bytes = sum(r["size"] for r in rows) or 1

    def check(r):
        p = lib.abspath(r["rel_path"])
        h = full_hash(p)
        if h is None:
            return r, "unreadable", "File could not be read", None
        err = _decode_ok(p) if decode_images and r["kind"] == "image" else None
        if r["baseline_hash"] is None:
            status = "new"
        elif r["baseline_size"] == r["size"] and abs((r["baseline_mtime"] or 0) - r["mtime"]) < 0.001:
            status = "ok" if h == r["baseline_hash"] else "damaged"
        else:
            status = "edited"
        detail = ""
        if status == "damaged":
            detail = "Size and modified date are unchanged but the content is different"
        if err and status != "damaged":
            status, detail = "unreadable", err
        return r, status, detail, h

    now = datetime.now().isoformat(sep=" ", timespec="seconds")
    updates, done_bytes = [], 0
    with ThreadPoolExecutor(max_workers=max(2, config.WORKERS // 2)) as pool:
        for i, (r, status, detail, h) in enumerate(pool.map(check, rows), 1):
            done_bytes += r["size"]
            rep.counts[status] += 1
            rep.checked += 1
            if status in ("damaged", "unreadable", "edited"):
                rep.problems.append({**r, "status": status, "detail": detail})
            if h and status != "damaged":
                # Keep the old fingerprint for damaged files so the problem stays visible.
                updates.append((h, r["size"], r["mtime"], now, h, r["id"]))
            progress.update(done_bytes, total_bytes, f"Checking files… {i:,} of {total:,}")
    rep.bytes = done_bytes
    with lib.transaction() as db:
        db.executemany("UPDATE files SET baseline_hash=?, baseline_size=?, baseline_mtime=?, checked_at=?, "
                       "chash=? WHERE id=?", updates)
    order = {"damaged": 0, "unreadable": 1, "edited": 2}
    rep.problems.sort(key=lambda p: (order[p["status"]], p["rel_path"]))
    progress.update(total_bytes, total_bytes, "Health check complete", force=True)
    return rep


def last_checked(lib: Library) -> Optional[str]:
    return lib.db.execute("SELECT MAX(checked_at) FROM files").fetchone()[0]
