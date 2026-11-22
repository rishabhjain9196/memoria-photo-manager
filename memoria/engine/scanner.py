"""Indexing: fast incremental filesystem scan, then parallel media analysis.

Scanning never modifies anything outside ``.memoria``.
"""
from __future__ import annotations

import contextlib
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional

from . import activity, config, dates, disk_speed, ffmpeg, hashing, media, roots, sniff
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
    offline_roots: int = 0


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
    result = ScanResult()
    sources = lib.roots()
    for index, source in enumerate(sources):
        try:
            roots.check(lib, source["id"])
            part = _scan_root(lib, source, progress.step(index, len(sources), f"Scanning {source['label']}"))
        except LibraryUnavailable as error:
            if source["id"] == 1:
                raise
            lib.db.execute("UPDATE library_roots SET online=0,error=? WHERE id=?",
                           (str(error)[:300], source["id"]))
            result.offline_roots += 1
            continue
        for field in ("total", "added", "changed", "removed", "unreadable_folders", "unreadable_files"):
            setattr(result, field, getattr(result, field) + getattr(part, field))
    progress.update(1, 1, f"Scan complete: {result.total:,} files"
                    + (f"; {result.offline_roots} offline folder(s) retained" if result.offline_roots else ""), force=True)
    return result


def _scan_root(lib: Library, source: dict, progress: Progress) -> ScanResult:
    root = source["path"]
    source_id = source["id"]
    cut = len(root.rstrip(os.sep)) + 1
    if not os.path.isdir(root):
        raise LibraryUnavailable(f"The library folder can't be reached ({root}). If it is on an external or "
                                 "network drive, reconnect it and try again. Nothing was changed.")
    existing = {r["rel_path"].lower(): (r["id"], r["size"], r["mtime"])
                for r in lib.db.execute("SELECT id, rel_path, size, mtime FROM files WHERE root_id=?", (source_id,))}
    missing = {r["rel_path"].lower(): r for r in lib.missing()
               if roots.split_key(r["rel_path"])[0] == source_id}
    existing.update({k: (r["id"], r["size"], r["mtime"]) for k, r in missing.items()})
    seen: set[str] = set()
    failed: list[str] = []
    new_rows, changed_ids = [], []
    returned = []
    res = ScanResult()
    for n, entry in enumerate(walk_files(Path(root), failed=failed), 1):
        if n % 500 == 0:
            progress.update(n, 0, f"Scanning… {n:,} files found")
        rel = roots.key_for(source_id, entry.path[cut:])
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
            new_rows.append((rel, folder, name, ext, config.kind_for_ext(ext), st.st_size, st.st_mtime, source_id))
        elif old[1] != st.st_size or abs(old[2] - st.st_mtime) > 0.001:
            changed_ids.append((st.st_size, st.st_mtime, old[0]))
    if root in failed or not os.path.isdir(root):
        raise LibraryUnavailable(f"The library folder stopped responding while it was being read ({root}). "
                                 "Nothing was changed.")
    # Files inside folders that couldn't be read are kept: unreadable is not the same as deleted.
    unreadable = tuple(roots.key_for(source_id, f[cut:]).lower() + os.sep for f in failed)
    removed = [v[0] for k, v in existing.items() if k not in seen and k not in missing
               and not k.startswith(unreadable)]
    res.unreadable_folders = len(failed)

    with lib.transaction() as db:
        for row in returned:
            cols = list(row)
            db.execute(f"INSERT INTO files ({','.join(cols)}) VALUES ({','.join('?' for _ in cols)})",
                       [row[c] for c in cols])
            db.execute("DELETE FROM missing_files WHERE file_id=?", (row["id"],))
        db.executemany("INSERT INTO files (rel_path, folder, name, ext, kind, size, mtime, root_id) "
                       "VALUES (?,?,?,?,?,?,?,?)", new_rows)
        reset = ", ".join(f"{c}=CASE WHEN date_source IN {dates.KEPT} THEN {c} END" if c in ("taken_at", "date_source")
                          else f"{c}=NULL" for c in DERIVED if c != "analyzed")
        db.executemany(f"UPDATE files SET size=?, mtime=?, analyzed=0, {reset} WHERE id=?", changed_ids)
    lib.mark_missing(removed)
    res.added, res.changed, res.removed = len(new_rows), len(changed_ids), len(removed)
    res.total = len(seen)
    progress.update(res.total, res.total, f"Scan complete: {res.total:,} files", force=True)
    return res


def _read_original(path: Path, size: int) -> Optional[bytes]:
    """Whole file in one sequential read, or None when it is too big to hold or changed since the scan."""
    if size > config.IN_MEMORY_READ_LIMIT:
        return None
    with open(config.longpath(path), "rb", buffering=0) as f:
        data = f.read()
    return data if len(data) == size else None


def _analyze_one(path: Path, kind: str, name: str, mtime: float, size: int = -1,
                 gate: Optional[threading.Semaphore] = None) -> dict:
    """Analyse one file. Disk reads happen inside ``gate``; decoding and hashing run outside it.

    Photos are read once: the same bytes give the content hashes (so finding duplicates never
    reads them again) and the decoded preview/metadata.
    """
    gate = gate or contextlib.nullcontext()
    out: dict = {}
    hashes: dict = {}
    data: Optional[bytes] = None
    try:
        if kind == "image":
            with gate:
                data = _read_original(path, size)
            if data is not None:
                hashes["qhash"], hashes["chash"] = hashing.hashes_of_bytes(data)
                out = media.analyze_image(path, data)
            else:
                with gate:
                    out = media.analyze_image(path)
        else:
            with gate:
                info = ffmpeg.probe(path)
                frame = ffmpeg.video_frame(path, at=min(1.0, info.duration / 2), max_side=config.ANALYSIS_SIZE)
            out = {"width": info.width, "height": info.height, "duration": info.duration,
                   "fps": info.fps if info.fps > 0 else None, "video_codec": info.vcodec,
                   "audio_codec": info.acodec}
            if info.creation_time:
                out["taken_at"], out["date_source"] = info.creation_time, "metadata"
            if frame:
                import io
                from PIL import Image
                img = Image.open(io.BytesIO(frame)).convert("RGB")
                out["thumb"] = media.thumbnail_bytes(img)
                out["dhash"] = media.dhash(img.convert("L"))
    except Exception as e:  # unreadable/corrupt files are recorded, never fatal
        message = f"{type(e).__name__}: {e}"[:260]
        try:
            ext = os.path.splitext(name)[1]
            diagnosis = (sniff.identify(data[:65536], len(data), ext, data[-4096:]) if data is not None
                         else sniff.identify_file(path, ext))
        except Exception:
            diagnosis = None
        out = {"error": message + sniff.tag(diagnosis)}
    out.update(hashes)
    if "taken_at" not in out:
        with gate:
            dt = dates.sidecar_date(path)
        if dt:
            out["taken_at"], out["date_source"] = dt, "sidecar"
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
# A date the user chose (in Memoria or iPhone Photos) survives re-analysis (SQLite evaluates CASE against the old row).
_KEEP_MANUAL = {"taken_at": f"taken_at=CASE WHEN date_source IN {dates.KEPT} THEN taken_at ELSE ? END",
                "date_source": f"date_source=CASE WHEN date_source IN {dates.KEPT} THEN date_source ELSE ? END"}
_ANALYSIS_SET = ", ".join(_KEEP_MANUAL.get(c, f"{c}=?") for c in _COLS)
DATES_MARKER = "dates-v2.done"


def analyze(lib: Library, progress: Optional[Progress] = None, workers: int = config.WORKERS) -> AnalyzeResult:
    """Analyse every un-analysed image and video. Resumable: results are committed in batches."""
    progress = progress or Progress()
    rows = lib.db.execute("SELECT id, rel_path, kind, name, mtime, size, root_id FROM files "
                          "WHERE (analyzed=0 OR COALESCE(metadata_version,0)<?) AND kind!='other' "
                          "AND root_id IN (SELECT id FROM library_roots WHERE online=1) "
                          "ORDER BY kind, rel_path", (METADATA_VERSION,)).fetchall()
    total = len(rows)
    res = AnalyzeResult()
    marker = config.app_dir(lib.root) / DATES_MARKER
    if not marker.exists() and lib.db.execute("SELECT 1 FROM files WHERE analyzed=1 LIMIT 1").fetchone() is None:
        # A new catalogue: every file is analysed with the current date sources, so no backfill is needed.
        config.ensure_app_dir(lib.root)
        marker.write_text("New catalogue: every file was analysed with the current date sources.\n")
    others = lib.db.execute("SELECT id, name, mtime FROM files WHERE analyzed=0 AND kind='other'").fetchall()
    if others:
        with lib.transaction() as db:
            for r in others:
                fn_dt = media.date_from_filename(r["name"])
                dt = fn_dt or datetime.fromtimestamp(r["mtime"])
                db.execute("UPDATE files SET analyzed=1, taken_at=?, date_source=? WHERE id=?",
                           (dt.isoformat(sep=" "), "filename" if fn_dt else "modified", r["id"]))
    if not total:
        _improve_dates(lib, progress)
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
                db.execute(f"UPDATE files SET {_ANALYSIS_SET}, analyzed=1, metadata_version=? WHERE id=?",
                           (*vals, METADATA_VERSION, fid))
                if out.get("chash"):
                    db.execute("UPDATE files SET qhash=?, chash=? WHERE id=?", (out["qhash"], out["chash"], fid))
        thumbs = [(fid, out["thumb"]) for fid, out in pending if out.get("thumb")]
        if thumbs:
            t = lib.thumbs_db
            t.execute("BEGIN")
            t.executemany("INSERT OR REPLACE INTO thumbs (file_id, data) VALUES (?,?)", thumbs)
            t.execute("COMMIT")
        pending.clear()
        last_flush = time.monotonic()

    video_workers = max(1, min(4, workers // 2))
    # Decoding uses every CPU worker; reads of originals are rationed per drive (one at a time on
    # a USB hard disk) so the disk streams files instead of seeking between them.
    gates = disk_speed.root_gates(lib)

    def analyze_one(row):
        path = lib.abspath(row["rel_path"])
        lib.check_path(path)
        return _analyze_one(path, row["kind"], row["name"], row["mtime"], row["size"], gates.get(row["root_id"]))

    with activity.pool("Photo decoders", workers), activity.pool("Video readers", video_workers), \
            ThreadPoolExecutor(max_workers=workers) as pool, ThreadPoolExecutor(max_workers=video_workers) as vpool:
        futures = {}
        remaining = iter(rows)

        def submit(r):
            p = vpool if r["kind"] == "video" else pool
            futures[p.submit(analyze_one, r)] = r["id"]

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
    _improve_dates(lib, progress)
    progress.update(total, total, "Analysis complete", force=True)
    return res


def _improve_dates(lib: Library, progress: Progress) -> None:
    """After analysis: give modified-time-only files a better date where one can be found.

    Every run: copy the reliable date of a same-named file in the same folder (cheap, catalogue only).
    Once per library: re-check older catalogue entries for sidecar files, embedded XMP/PNG dates and
    timestamps in file names, which earlier versions didn't read. New files get these during analysis.
    """
    marker = config.app_dir(lib.root) / DATES_MARKER
    if not marker.exists():
        rows = lib.db.execute("SELECT id, rel_path, name, kind, root_id FROM files WHERE date_source='modified' "
                              "AND kind != 'other' AND root_id IN (SELECT id FROM library_roots WHERE online=1) "
                              "ORDER BY rel_path").fetchall()
        gates = disk_speed.root_gates(lib)
        updates = []
        for n, r in enumerate(rows, 1):
            progress.update(n, len(rows), f"Looking for better dates… {n:,} of {len(rows):,}")
            dt, source = media.date_from_filename(r["name"]), "filename"
            if dt is None:
                path = lib.abspath(r["rel_path"])
                with gates.get(r["root_id"]) or contextlib.nullcontext():
                    dt, source = dates.sidecar_date(path), "sidecar"
                    if dt is None and r["kind"] == "image":
                        dt, source = _embedded_date(path), "metadata"
            if dt is not None:
                updates.append((dt.isoformat(sep=" "), source, r["id"]))
        if updates:
            with lib.transaction() as db:
                db.executemany("UPDATE files SET taken_at=?, date_source=? WHERE id=? AND date_source='modified'",
                               updates)
        marker.write_text("Older catalogue entries were checked for sidecar, embedded and file-name dates.\n")
    dates.infer_dates(lib)


def _embedded_date(path: Path) -> Optional[datetime]:
    """PNG creation-time text or an XMP date near the start of the file; never decodes the image."""
    try:
        with open(config.longpath(path), "rb") as f:
            head = f.read(512 * 1024)
    except OSError:
        return None
    dt = dates.xmp_date(head)
    if dt is None and head.startswith(b"\x89PNG"):
        try:
            import io
            from PIL import Image
            with Image.open(io.BytesIO(head)) as img:
                dt = dates.png_text_date(img.info)
        except Exception:
            dt = None
    return dt


def index(lib: Library, progress: Optional[Progress] = None) -> tuple[ScanResult, AnalyzeResult]:
    s = scan(lib, progress)
    a = analyze(lib, progress)
    return s, a
