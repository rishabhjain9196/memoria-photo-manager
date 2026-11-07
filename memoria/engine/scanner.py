"""Indexing: fast incremental filesystem scan, then parallel media analysis.

Scanning never modifies anything outside ``.memoria``.
"""
from __future__ import annotations

import os
import time
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional

from . import config, ffmpeg, media
from .db import DERIVED, METADATA_VERSION, Library, LibraryUnavailable
from .progress import Progress


@dataclass
class ScanResult:
    total: int = 0
    added: int = 0
    changed: int = 0
    removed: int = 0
    unreadable_folders: int = 0
    unreadable_files: int = 0


@dataclass
class AnalyzeResult:
    analyzed: int = 0
    errors: int = 0


class _Entry:
    """A found file: real path (without the long-path prefix) plus its cached stat."""
    __slots__ = ("path", "name", "_entry")

    def __init__(self, path: str, entry: os.DirEntry):
        self.path, self.name, self._entry = path, entry.name, entry

    def stat(self, follow_symlinks: bool = False):
        return self._entry.stat(follow_symlinks=follow_symlinks)


def walk_files(root: Path, skip_dirs: Optional[set[str]] = None,
               failed: Optional[list[str]] = None) -> Iterator[_Entry]:
    """Iterative os.scandir walk that skips hidden app folders and does not follow links.

    Folders that cannot be read are appended to ``failed`` so callers never mistake an
    unreadable folder (or an unplugged drive) for deleted files.
    """
    skip = {config.APP_DIR_NAME.lower(), "$recycle.bin", "system volume information"}
    if skip_dirs:
        skip |= {s.lower() for s in skip_dirs}
    stack = [str(root)]
    while stack:
        current = stack.pop()
        try:
            with os.scandir(config.longpath(current)) as it:
                entries = list(it)
        except OSError:
            if failed is not None:
                failed.append(current)
            continue
        for entry in entries:
            try:
                path = os.path.join(current, entry.name)
                if entry.is_dir(follow_symlinks=False):
                    if entry.name.lower() not in skip:
                        stack.append(path)
                elif entry.is_file(follow_symlinks=False):
                    yield _Entry(path, entry)
            except OSError:
                if failed is not None:
                    failed.append(current)
                continue


def walk_dirs(root: Path) -> list[str]:
    out = []
    stack = [str(root)]
    skip = {config.APP_DIR_NAME.lower(), "$recycle.bin", "system volume information"}
    while stack:
        current = stack.pop()
        try:
            with os.scandir(config.longpath(current)) as it:
                for e in it:
                    if e.is_dir(follow_symlinks=False) and e.name.lower() not in skip:
                        path = os.path.join(current, e.name)
                        out.append(path)
                        stack.append(path)
        except OSError:
            continue
    return out


def scan(lib: Library, progress: Optional[Progress] = None) -> ScanResult:
    progress = progress or Progress()
    root = str(lib.root)
    cut = len(root.rstrip(os.sep)) + 1
    if not os.path.isdir(root):
        raise LibraryUnavailable(f"The library folder can't be reached ({root}). If it is on an external or "
                                 "network drive, reconnect it and try again. Nothing was changed.")
    existing = {r["rel_path"].lower(): (r["id"], r["size"], r["mtime"])
                for r in lib.db.execute("SELECT id, rel_path, size, mtime FROM files")}
    missing = {r["rel_path"].lower(): r for r in lib.missing()}
    existing.update({k: (r["id"], r["size"], r["mtime"]) for k, r in missing.items()})
    seen: set[str] = set()
    failed: list[str] = []
    new_rows, changed_ids = [], []
    returned = []
    res = ScanResult()
    for n, entry in enumerate(walk_files(lib.root, failed=failed), 1):
        if n % 500 == 0:
            progress.update(n, 0, f"Scanning… {n:,} files found")
        rel = entry.path[cut:]
        key = rel.lower()
        seen.add(key)
        try:
            st = entry.stat(follow_symlinks=False)
        except OSError:
            res.unreadable_files += 1
            continue
        if key in missing:
            returned.append(missing[key])
        old = existing.get(key)
        if old is None:
            folder, name = os.path.split(rel)
            ext = os.path.splitext(name)[1].lower()
            new_rows.append((rel, folder, name, ext, config.kind_for_ext(ext), st.st_size, st.st_mtime))
        elif old[1] != st.st_size or abs(old[2] - st.st_mtime) > 0.001:
            changed_ids.append((st.st_size, st.st_mtime, old[0]))
    if root in failed or not os.path.isdir(root):
        raise LibraryUnavailable(f"The library folder stopped responding while it was being read ({root}). "
                                 "Nothing was changed.")
    # Files inside folders that couldn't be read are kept: unreadable is not the same as deleted.
    unreadable = tuple(f[cut:].lower() + os.sep for f in failed)
    removed = [v[0] for k, v in existing.items() if k not in seen and k not in missing
               and not k.startswith(unreadable)]
    res.unreadable_folders = len(failed)

    with lib.transaction() as db:
        for row in returned:
            cols = list(row)
            db.execute(f"INSERT INTO files ({','.join(cols)}) VALUES ({','.join('?' for _ in cols)})",
                       [row[c] for c in cols])
            db.execute("DELETE FROM missing_files WHERE file_id=?", (row["id"],))
        db.executemany("INSERT INTO files (rel_path, folder, name, ext, kind, size, mtime) "
                       "VALUES (?,?,?,?,?,?,?)", new_rows)
        reset = ", ".join(f"{c}=NULL" for c in DERIVED if c != "analyzed")
        db.executemany(f"UPDATE files SET size=?, mtime=?, analyzed=0, {reset} WHERE id=?", changed_ids)
    lib.mark_missing(removed)
    res.added, res.changed, res.removed = len(new_rows), len(changed_ids), len(removed)
    res.total = len(seen)
    progress.update(res.total, res.total, f"Scan complete: {res.total:,} files", force=True)
    return res


def _analyze_one(path: Path, kind: str, name: str, mtime: float) -> dict:
    out: dict = {}
    try:
        if kind == "image":
            out = media.analyze_image(path)
        else:
            info = ffmpeg.probe(path)
            out = {"width": info.width, "height": info.height, "duration": info.duration,
                   "fps": info.fps if info.fps > 0 else None, "video_codec": info.vcodec,
                   "audio_codec": info.acodec}
            if info.creation_time:
                out["taken_at"], out["date_source"] = info.creation_time, "metadata"
            frame = ffmpeg.video_frame(path, at=min(1.0, info.duration / 2), max_side=config.ANALYSIS_SIZE)
            if frame:
                import io
                from PIL import Image
                img = Image.open(io.BytesIO(frame)).convert("RGB")
                out["thumb"] = media.thumbnail_bytes(img)
                out["dhash"] = media.dhash(img.convert("L"))
    except Exception as e:  # unreadable/corrupt files are recorded, never fatal
        out = {"error": f"{type(e).__name__}: {e}"[:300]}
    if "taken_at" not in out:
        dt = media.date_from_filename(name)
        if dt:
            out["taken_at"], out["date_source"] = dt, "filename"
        else:
            out["taken_at"], out["date_source"] = datetime.fromtimestamp(mtime), "modified"
    return out


_COLS = ("width", "height", "taken_at", "date_source", "camera", "lat", "lon", "duration", "dhash",
         "sharpness", "brightness", "contrast", "clipped", "error", "fps", "video_codec", "audio_codec",
         "iso", "aperture", "exposure_seconds", "focal_length_mm", "lens")


def analyze(lib: Library, progress: Optional[Progress] = None, workers: int = config.WORKERS) -> AnalyzeResult:
    """Analyse every un-analysed image and video. Resumable: results are committed in batches."""
    progress = progress or Progress()
    rows = lib.db.execute("SELECT id, rel_path, kind, name, mtime FROM files "
                          "WHERE (analyzed=0 OR COALESCE(metadata_version,0)<?) AND kind!='other' "
                          "ORDER BY kind, rel_path", (METADATA_VERSION,)).fetchall()
    total = len(rows)
    res = AnalyzeResult()
    others = lib.db.execute("SELECT id, name, mtime FROM files WHERE analyzed=0 AND kind='other'").fetchall()
    if others:
        with lib.transaction() as db:
            for r in others:
                fn_dt = media.date_from_filename(r["name"])
                dt = fn_dt or datetime.fromtimestamp(r["mtime"])
                db.execute("UPDATE files SET analyzed=1, taken_at=?, date_source=? WHERE id=?",
                           (dt.isoformat(sep=" "), "filename" if fn_dt else "modified", r["id"]))
    if not total:
        return res
    progress.update(0, total, "Analysing photos and videos…", force=True)
    pending: list[tuple[int, dict]] = []
    last_flush = time.monotonic()

    def flush():
        nonlocal last_flush
        if not pending:
            return
        with lib.transaction() as db:
            for fid, out in pending:
                vals = []
                for c in _COLS:
                    v = out.get(c)
                    vals.append(v.isoformat(sep=" ") if isinstance(v, datetime) else v)
                db.execute(f"UPDATE files SET {', '.join(c + '=?' for c in _COLS)}, analyzed=1, metadata_version=? WHERE id=?",
                           (*vals, METADATA_VERSION, fid))
        thumbs = [(fid, out["thumb"]) for fid, out in pending if out.get("thumb")]
        if thumbs:
            t = lib.thumbs_db
            t.execute("BEGIN")
            t.executemany("INSERT OR REPLACE INTO thumbs (file_id, data) VALUES (?,?)", thumbs)
            t.execute("COMMIT")
        pending.clear()
        last_flush = time.monotonic()

    video_workers = max(1, min(4, workers // 2))
    with ThreadPoolExecutor(max_workers=workers) as pool, ThreadPoolExecutor(max_workers=video_workers) as vpool:
        futures = {}
        remaining = iter(rows)

        def submit(r):
            p = vpool if r["kind"] == "video" else pool
            futures[p.submit(_analyze_one, lib.abspath(r["rel_path"]), r["kind"], r["name"], r["mtime"])] = r["id"]

        try:
            for _ in range(2 * (workers + video_workers)):
                r = next(remaining, None)
                if r is not None:
                    submit(r)
            while futures:
                progress.check()
                completed, _ = wait(futures, timeout=0.1, return_when=FIRST_COMPLETED)
                for fut in completed:
                    out = fut.result()
                    if "error" in out:
                        res.errors += 1
                    res.analyzed += 1
                    pending.append((futures.pop(fut), out))
                    if len(pending) >= 200:
                        flush()
                    progress.update(res.analyzed, total,
                                    f"Analysing photos and videos… {res.analyzed:,} of {total:,}")
                    r = next(remaining, None)
                    if r is not None:
                        submit(r)
                if pending and time.monotonic() - last_flush >= 1.0:
                    flush()
                    progress.update(res.analyzed, total,
                                    f"Analysing photos and videos… {res.analyzed:,} of {total:,}", force=True)
        except BaseException:
            for f in futures:
                f.cancel()
            flush()
            raise
    flush()
    progress.update(total, total, "Analysis complete", force=True)
    return res


def index(lib: Library, progress: Optional[Progress] = None) -> tuple[ScanResult, AnalyzeResult]:
    s = scan(lib, progress)
    a = analyze(lib, progress)
    return s, a
