"""Indexing: fast incremental filesystem scan, then parallel media analysis.

Scanning never modifies anything outside ``.memoria``.
"""
from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional

from . import config, ffmpeg, media
from .db import DERIVED, Library
from .progress import Progress


@dataclass
class ScanResult:
    total: int = 0
    added: int = 0
    changed: int = 0
    removed: int = 0


@dataclass
class AnalyzeResult:
    analyzed: int = 0
    errors: int = 0


def walk_files(root: Path, skip_dirs: Optional[set[str]] = None) -> Iterator[os.DirEntry]:
    """Iterative os.scandir walk that skips hidden app folders and does not follow links."""
    skip = {config.APP_DIR_NAME.lower(), "$recycle.bin", "system volume information"}
    if skip_dirs:
        skip |= {s.lower() for s in skip_dirs}
    stack = [str(root)]
    while stack:
        current = stack.pop()
        try:
            with os.scandir(current) as it:
                entries = list(it)
        except OSError:
            continue
        for entry in entries:
            try:
                if entry.is_dir(follow_symlinks=False):
                    if entry.name.lower() not in skip:
                        stack.append(entry.path)
                elif entry.is_file(follow_symlinks=False):
                    yield entry
            except OSError:
                continue


def walk_dirs(root: Path) -> list[str]:
    out = []
    stack = [str(root)]
    skip = {config.APP_DIR_NAME.lower(), "$recycle.bin", "system volume information"}
    while stack:
        current = stack.pop()
        try:
            with os.scandir(current) as it:
                for e in it:
                    if e.is_dir(follow_symlinks=False) and e.name.lower() not in skip:
                        out.append(e.path)
                        stack.append(e.path)
        except OSError:
            continue
    return out


def scan(lib: Library, progress: Optional[Progress] = None) -> ScanResult:
    progress = progress or Progress()
    root = str(lib.root)
    cut = len(root) + 1
    existing = {r["rel_path"].lower(): (r["id"], r["size"], r["mtime"])
                for r in lib.db.execute("SELECT id, rel_path, size, mtime FROM files")}
    seen: set[str] = set()
    new_rows, changed_ids = [], []
    res = ScanResult()
    for n, entry in enumerate(walk_files(lib.root), 1):
        if n % 500 == 0:
            progress.update(n, 0, f"Scanning… {n:,} files found")
        try:
            st = entry.stat(follow_symlinks=False)
        except OSError:
            continue
        rel = entry.path[cut:]
        key = rel.lower()
        seen.add(key)
        old = existing.get(key)
        if old is None:
            folder, name = os.path.split(rel)
            ext = os.path.splitext(name)[1].lower()
            new_rows.append((rel, folder, name, ext, config.kind_for_ext(ext), st.st_size, st.st_mtime))
        elif old[1] != st.st_size or abs(old[2] - st.st_mtime) > 0.001:
            changed_ids.append((st.st_size, st.st_mtime, old[0]))
    removed = [v[0] for k, v in existing.items() if k not in seen]

    with lib.transaction() as db:
        db.executemany("INSERT INTO files (rel_path, folder, name, ext, kind, size, mtime) "
                       "VALUES (?,?,?,?,?,?,?)", new_rows)
        reset = ", ".join(f"{c}=NULL" for c in DERIVED if c != "analyzed")
        db.executemany(f"UPDATE files SET size=?, mtime=?, analyzed=0, {reset} WHERE id=?", changed_ids)
    lib.remove_rows(removed)
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
            out = {"width": info.width, "height": info.height, "duration": round(info.duration, 2)}
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
         "sharpness", "brightness", "contrast", "clipped", "error")


def analyze(lib: Library, progress: Optional[Progress] = None, workers: int = config.WORKERS) -> AnalyzeResult:
    """Analyse every un-analysed image and video. Resumable: results are committed in batches."""
    progress = progress or Progress()
    rows = lib.db.execute("SELECT id, rel_path, kind, name, mtime FROM files "
                          "WHERE analyzed=0 AND kind!='other' ORDER BY kind, rel_path").fetchall()
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
    pending: list[tuple[int, dict]] = []

    def flush():
        if not pending:
            return
        with lib.transaction() as db:
            for fid, out in pending:
                vals = []
                for c in _COLS:
                    v = out.get(c)
                    vals.append(v.isoformat(sep=" ") if isinstance(v, datetime) else v)
                db.execute(f"UPDATE files SET {', '.join(c + '=?' for c in _COLS)}, analyzed=1 WHERE id=?",
                           (*vals, fid))
        thumbs = [(fid, out["thumb"]) for fid, out in pending if out.get("thumb")]
        if thumbs:
            t = lib.thumbs_db
            t.execute("BEGIN")
            t.executemany("INSERT OR REPLACE INTO thumbs (file_id, data) VALUES (?,?)", thumbs)
            t.execute("COMMIT")
        pending.clear()

    video_workers = max(1, min(4, workers // 2))
    with ThreadPoolExecutor(max_workers=workers) as pool, ThreadPoolExecutor(max_workers=video_workers) as vpool:
        futures = {}
        for r in rows:
            p = vpool if r["kind"] == "video" else pool
            futures[p.submit(_analyze_one, lib.abspath(r["rel_path"]), r["kind"], r["name"], r["mtime"])] = r["id"]
        try:
            for done, fut in enumerate(as_completed(futures), 1):
                out = fut.result()
                if "error" in out:
                    res.errors += 1
                res.analyzed += 1
                pending.append((futures[fut], out))
                if len(pending) >= 200:
                    flush()
                progress.update(done, total, f"Analysing photos and videos… {done:,} of {total:,}")
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
