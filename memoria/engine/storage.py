"""Selective catalogue maintenance. Never removes originals, Recovery or the operation journal."""
from __future__ import annotations

import json
import os
import shutil
from dataclasses import asdict, dataclass
from typing import Optional

from . import actions, config, scanner
from .db import DERIVED, Library
from .progress import Progress


@dataclass(frozen=True)
class ResetOptions:
    thumbnails: bool = True
    analysis: bool = True
    videos: bool = True
    people: bool = False
    albums: bool = False
    health: bool = False
    missing: bool = False
    duplicate_choices: bool = False
    compact: bool = False


def pending(lib: Library):
    return lib.db.execute("SELECT * FROM storage_reset WHERE id=1").fetchone()


def usage(lib: Library) -> dict[str, int]:
    """Allocated catalogue/cache bytes, including SQLite sidecars; no traversal of media."""
    out = {}
    for key, path in (("catalogue", lib.db_path), ("thumbnails", lib.thumbs_path)):
        size = 0
        for suffix in ("", "-wal", "-shm"):
            try:
                size += os.stat(config.longpath(str(path) + suffix)).st_size
            except FileNotFoundError:
                continue
        out[key] = size
    return out


def _check_space(lib: Library) -> None:
    required = max(db.execute("PRAGMA page_count").fetchone()[0] *
                   db.execute("PRAGMA page_size").fetchone()[0] for db in (lib.db, lib.thumbs_db))
    # VACUUM may need both a temporary database and a new WAL before checkpointing.
    if shutil.disk_usage(config.app_dir(lib.root)).free < 2 * required + 16 * 1024 * 1024:
        raise OSError("Not enough free space to shrink database files safely. Uncheck "
                      "'Shrink storage files' and retry. Cleared space can still be reused by Memoria.")


def _clear_catalogue(lib: Library, options: ResetOptions) -> None:
    fields = {}
    if options.analysis:
        fields.update({key: None for key in DERIVED})
    if options.analysis or options.thumbnails:
        fields["analyzed"] = 0
    if options.health:
        fields.update({key: None for key in
                       ("baseline_hash", "baseline_size", "baseline_mtime", "checked_at")})
    forgotten = {"files": [], "faces": []}
    with lib.transaction() as db:
        if fields:
            db.execute("UPDATE files SET " + ",".join(f"{key}=?" for key in fields), tuple(fields.values()))
            # Undo/return must not resurrect analysis or fingerprints the user chose to clear.
            for table, key in (("parked_files", "op_id"), ("missing_files", "file_id")):
                for row in db.execute(f"SELECT {key},data FROM {table}").fetchall():
                    data = json.loads(row["data"])
                    data.update(fields)
                    db.execute(f"UPDATE {table} SET data=? WHERE {key}=?", (json.dumps(data), row[key]))
        if options.videos and db.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='video_sigs'").fetchone():
            db.execute("DELETE FROM video_sigs")
        if options.missing:
            forgotten["files"] = [r[0] for r in db.execute("SELECT file_id FROM missing_files")]
            forgotten["faces"] = [r[0] for r in db.execute(
                "SELECT id FROM faces WHERE file_id IN (SELECT file_id FROM missing_files)")]
            db.execute("DELETE FROM face_rejects WHERE face_id IN "
                       "(SELECT id FROM faces WHERE file_id IN (SELECT file_id FROM missing_files))")
            for table in ("faces", "face_scans", "album_items"):
                db.execute(f"DELETE FROM {table} WHERE file_id IN (SELECT file_id FROM missing_files)")
            db.execute("UPDATE albums SET cover_id=NULL WHERE cover_id IN (SELECT file_id FROM missing_files)")
            db.execute("DELETE FROM missing_files")
        if options.people:
            for table in ("face_rejects", "faces", "face_scans", "people"):
                db.execute(f"DELETE FROM {table}")
        if options.albums:
            db.execute("DELETE FROM album_items")
            db.execute("DELETE FROM albums")
        if options.duplicate_choices:
            db.execute("DELETE FROM duplicate_kept")
        db.execute("INSERT INTO storage_reset VALUES (1,?,'caches',?)",
                   (json.dumps(asdict(options)), json.dumps(forgotten)))


def _clear_caches(lib: Library, options: ResetOptions, forgotten: dict) -> None:
    db = lib.thumbs_db
    db.execute("BEGIN IMMEDIATE")
    try:
        if options.thumbnails:
            db.execute("DELETE FROM thumbs")
        if options.people:
            db.execute("DELETE FROM face_thumbs")
        db.executemany("DELETE FROM thumbs WHERE file_id=?", [(i,) for i in forgotten["files"]])
        db.executemany("DELETE FROM face_thumbs WHERE face_id=?", [(i,) for i in forgotten["faces"]])
        db.execute("COMMIT")
    except BaseException:
        db.execute("ROLLBACK")
        raise


def _compact(lib: Library, progress: Progress) -> None:
    _check_space(lib)
    for i, db in enumerate((lib.db, lib.thumbs_db)):
        progress.update(i, 2, "Shrinking catalogue storage (may need temporary disk space)", force=True)
        if db.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()[0]:
            raise OSError("Catalogue storage is busy. Retry Storage & reset when other work has finished.")
        db.execute("VACUUM")
        if db.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()[0]:
            raise OSError("The storage checkpoint is busy. Retry Storage & reset.")


def reset(lib: Library, options: ResetOptions, progress: Optional[Progress] = None):
    """Commit selections atomically, then resume the durable reset state machine."""
    progress = progress or Progress()
    progress.check()
    if pending(lib) is not None:
        raise RuntimeError("A reset is already unfinished. Resume it before starting a different reset.")
    if not any(asdict(options).values()):
        raise ValueError("Select something to clear or shrink.")
    if options.compact:
        _check_space(lib)
    actions.reconcile(lib)
    _clear_catalogue(lib, options)
    return resume(lib, progress)


def resume(lib: Library, progress: Optional[Progress] = None, *, skip_compact: bool = False):
    """Retry only unfinished phases. Rebuilding is incremental; clearing never repeats after it."""
    progress = progress or Progress()
    state = pending(lib)
    if state is None:
        return scanner.index(lib, progress)
    options = ResetOptions(**json.loads(state["options"]))
    phase = state["phase"]
    if phase not in ("caches", "compact", "rebuild"):
        raise RuntimeError(f"Unknown reset phase: {phase}. Catalogue left unchanged.")
    if phase == "caches":
        progress.update(0, 3, "Clearing selected caches", force=True)
        _clear_caches(lib, options, json.loads(state["forgotten"]))
        lib.db.execute("UPDATE storage_reset SET phase='compact' WHERE id=1")
        phase = "compact"
    if phase == "compact":
        if options.compact and not skip_compact:
            _compact(lib, progress.step(1, 3, "Reclaiming storage"))
        lib.db.execute("UPDATE storage_reset SET phase='rebuild' WHERE id=1")
    result = scanner.index(lib, progress.step(2, 3, "Rebuilding catalogue"))
    lib.db.execute("DELETE FROM storage_reset WHERE id=1")
    return result
