"""Health check: prove files are intact.

The first check records a fingerprint (full-content hash) for every file. Later checks re-read
each file and compare:
* same size and modified time but different content → silent damage (bit rot, bad sector, sync bug)
* different modified time → the file was edited on purpose; the fingerprint is refreshed
* photos are also decoded to catch truncated or corrupt images
"""
from __future__ import annotations

import contextlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import xxhash

from . import config, disk_speed, sniff
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
    offline_roots: int = 0


def _decode_ok(path, data: Optional[bytes] = None) -> Optional[str]:
    import io
    from PIL import Image
    try:
        from .config import longpath
        with Image.open(io.BytesIO(data) if data is not None else longpath(path)) as im:
            if im.format == "JPEG":
                im.draft("RGB", (256, 256))
            im.load()
        return None
    except Exception as e:
        return f"{type(e).__name__}: {e}"[:200]


def run_health(lib: Library, progress: Optional[Progress] = None, decode_images: bool = True) -> HealthReport:
    progress = progress or Progress()
    scan(lib, progress)
    rows = [dict(r) for r in lib.readable_files()]
    rep = HealthReport(counts={k: 0 for k in STATUS_LABEL})
    rep.offline_roots = sum(not source["online"] for source in lib.roots())
    missing = lib.missing()
    rep.counts["missing"] = len(missing)
    rep.problems.extend({**r, "status": "missing", "detail": "Not found at its last known location. "
                         "The catalogue and fingerprint are retained in case it returns."} for r in missing)
    total = len(rows)
    total_bytes = sum(r["size"] for r in rows) or 1

    def check(r, gate):
        p = lib.abspath(r["rel_path"])
        lib.check_path(p)
        # One paced read per file: the same bytes are hashed and (for photos) test-decoded.
        try:
            data = disk_speed.read_original(p, gate)
        except OSError:
            return r, "unreadable", "File could not be read", None
        if data is not None:
            h = xxhash.xxh3_128(data).hexdigest()
        else:
            with gate or contextlib.nullcontext():
                h = full_hash(p)
        if h is None:
            return r, "unreadable", "File could not be read", None
        err = None
        if decode_images and r["kind"] == "image":
            if data is not None:
                err = _decode_ok(p, data)
            else:
                with gate or contextlib.nullcontext():
                    err = _decode_ok(p)
        if err:
            err += sniff.tag(sniff.identify(data[:65536], len(data), r["ext"], data[-4096:]) if data is not None
                             else sniff.identify_file(p, r["ext"]))
        elif r["error"] and r["kind"] == "video":
            diagnosis = sniff.identify_file(p, r["ext"])
            if diagnosis:
                err = r["error"].split(" [content:")[0] + sniff.tag(diagnosis)
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
    for i, (r, status, detail, h) in enumerate(disk_speed.paced_map(
            check, rows, lambda r: lib.abspath(r["rel_path"]), "Health readers", hold_gate=False), 1):
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
    order = {"damaged": 0, "unreadable": 1, "missing": 2, "edited": 3}
    rep.problems.sort(key=lambda p: (order[p["status"]], p["rel_path"]))
    progress.update(total_bytes, total_bytes, "Health check complete", force=True)
    return rep


def last_checked(lib: Library) -> Optional[str]:
    return lib.db.execute("SELECT MAX(checked_at) FROM files").fetchone()[0]


def plan_extension_fixes(lib: Library, problems: list[dict]):
    """Rename actions for files whose content is a known photo/video type under the wrong extension.

    Each file keeps its folder and name; only the extension changes ("IMG_1.jpg" → "IMG_1.mp4",
    or "IMG_1 (2).mp4" if that name is taken). Applied through the journal, so Undo renames back.
    """
    import os
    from .actions import Action
    acts, taken = [], set()
    for p in problems:
        content = sniff.parse_tag(p.get("detail") or p.get("error"))
        if not content or content[0] != "wrong_ext" or not content[1]:
            continue
        src = str(lib.abspath(p["rel_path"]))
        stem = os.path.splitext(src)[0]
        dst, n = stem + content[1], 1
        while os.path.lexists(config.longpath(dst)) or dst.lower() in taken:
            n += 1
            dst = f"{stem} ({n}){content[1]}"
        taken.add(dst.lower())
        acts.append(Action(op="move", src=src, dst=dst, size=p["size"], mtime=p["mtime"], hash=p.get("chash"),
                           file_id=p["id"], reason=f"Content is really {content[1]}"))
    return acts
