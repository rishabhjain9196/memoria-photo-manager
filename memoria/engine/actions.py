"""Safe file operations: every change is journaled, verified and undoable.

Rules enforced here (the UI relies on them):
* Nothing is ever deleted. "Remove" means *move into the library's Recovery folder*.
* Before acting, each source file is checked against what the user reviewed (size, mtime and,
  for duplicates, a fresh full-content hash). Changed files are skipped, not acted on.
* Copies are written to a temporary name, hash-verified, then renamed. Existing files are
  never overwritten.
* Each operation is written to the journal as ``pending`` before it runs and ``done`` after,
  so an interrupted batch can be reconciled and undone.
"""
from __future__ import annotations

import os
import shutil
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from .config import longpath as L
from .db import Library
from .hashing import full_hash
from .progress import Cancelled, Progress


@dataclass
class Action:
    op: str                      # "recycle" | "move" | "copy" | "rmdir"
    src: str                     # absolute path
    dst: Optional[str] = None    # absolute path (move/copy); computed for recycle
    size: int = 0
    mtime: Optional[float] = None
    hash: Optional[str] = None   # if set, src must still have this full hash
    guards: list[tuple[str, str]] = field(default_factory=list)  # (path, hash) that must still exist
    reason: str = ""
    file_id: Optional[int] = None


@dataclass
class BatchResult:
    batch_id: str
    done: int = 0
    skipped: int = 0
    failed: int = 0
    bytes: int = 0
    messages: list[str] = field(default_factory=list)
    cancelled: bool = False

    @property
    def ok(self) -> bool:
        return self.failed == 0


def _ex(p) -> bool:
    return os.path.exists(L(p))


def _unique(path: Path) -> Path:
    if not _ex(path):
        return path
    stem, suffix = path.stem, path.suffix
    for i in range(2, 10_000):
        cand = path.with_name(f"{stem} ({i}){suffix}")
        if not _ex(cand):
            return cand
    raise FileExistsError(str(path))


def _same_volume(a: Path, b: Path) -> bool:
    return os.path.splitdrive(str(a.resolve()))[0].lower() == os.path.splitdrive(str(b.resolve()))[0].lower()


def verified_copy(src: Path, dst: Path, expected: Optional[str] = None) -> str:
    """Copy src→dst via a temp file and verify content. Returns the hash. Never overwrites."""
    expected = expected or full_hash(src)
    if expected is None:
        raise OSError(f"Cannot read {src}")
    os.makedirs(L(dst.parent), exist_ok=True)
    tmp = dst.with_name(dst.name + ".memoria-tmp")
    try:
        shutil.copy2(L(src), L(tmp))
        got = full_hash(tmp)
        if got != expected:
            raise OSError(f"Verification failed copying {src.name} (content mismatch)")
        if _ex(dst):
            raise FileExistsError(str(dst))
        os.rename(L(tmp), L(dst))
    finally:
        if _ex(tmp):
            os.remove(L(tmp))
    return expected


def safe_move(src: Path, dst: Path) -> None:
    os.makedirs(L(dst.parent), exist_ok=True)
    if _ex(dst):
        raise FileExistsError(str(dst))
    if _same_volume(src, dst.parent):
        os.rename(L(src), L(dst))
    else:
        verified_copy(src, dst)
        os.remove(L(src))


def _now() -> str:
    return datetime.now().isoformat(sep=" ", timespec="seconds")


def apply(lib: Library, kind: str, title: str, actions: list[Action],
          progress: Optional[Progress] = None) -> BatchResult:
    progress = progress or Progress()
    batch_id = datetime.now().strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6]
    res = BatchResult(batch_id)
    db = lib.db
    db.execute("INSERT INTO batches (id, created_at, kind, title, status) VALUES (?,?,?,?,?)",
               (batch_id, _now(), kind, title, "applying"))
    recycle_root = lib.recovery / batch_id
    total = len(actions)
    parked: list[tuple[int, int]] = []
    moved_rows: list[tuple[str, str, str, int]] = []
    verified: set = set()
    try:
        for seq, a in enumerate(actions):
            progress.update(seq, total, f"{title}… {seq:,} of {total:,}")
            src = Path(a.src)
            problem = _preflight(a, src, verified)
            if problem:
                res.skipped += 1
                res.messages.append(f"Skipped {src.name}: {problem}")
                _log(db, batch_id, seq, a, None, "skipped", problem)
                continue
            if a.op == "recycle":
                try:
                    rel = src.resolve().relative_to(lib.root)
                except ValueError:
                    rel = Path(src.name)
                dst = _unique(recycle_root / rel)
            elif a.op in ("move", "copy"):
                dst = _unique(Path(a.dst))
            else:
                dst = None
            op_id = _log(db, batch_id, seq, a, dst, "pending")
            try:
                if a.op in ("recycle", "move"):
                    safe_move(src, dst)
                elif a.op == "copy":
                    verified_copy(src, dst, a.hash)
                elif a.op == "rmdir":
                    os.rmdir(L(src))
                db.execute("UPDATE operations SET status='done' WHERE id=?", (op_id,))
                res.done += 1
                res.bytes += a.size
                if a.file_id is not None:
                    if a.op == "recycle":
                        parked.append((op_id, a.file_id))
                    elif a.op == "move" and _inside(dst, lib.root):
                        rel = str(dst.relative_to(lib.root))
                        folder, name = os.path.split(rel)
                        moved_rows.append((rel, folder, name, a.file_id))
            except Exception as e:
                res.failed += 1
                res.messages.append(f"Failed {src.name}: {e}")
                db.execute("UPDATE operations SET status='failed', error=? WHERE id=?", (str(e)[:300], op_id))
    except Cancelled:
        res.cancelled = True
    finally:
        lib.park_rows(parked)
        if moved_rows:
            with lib.transaction() as tx:
                tx.executemany("UPDATE files SET rel_path=?, folder=?, name=? WHERE id=?", moved_rows)
        status = "applied" if res.done and not res.failed and not res.cancelled else (
            "partial" if res.done else "nothing")
        db.execute("UPDATE batches SET status=?, files=?, bytes=? WHERE id=?",
                   (status, res.done, res.bytes, batch_id))
    if not res.cancelled:
        progress.update(total, total, f"{title}: done", force=True)
    return res


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root)
        return True
    except ValueError:
        return False


def _preflight(a: Action, src: Path, verified: Optional[set] = None) -> Optional[str]:
    verified = verified if verified is not None else set()
    for gpath, ghash in a.guards:
        if (gpath, ghash) in verified:
            continue
        if not _ex(gpath):
            return f"the copy being kept ({Path(gpath).name}) is missing"
        if full_hash(gpath) != ghash:
            return f"the copy being kept ({Path(gpath).name}) has changed"
        verified.add((gpath, ghash))
    if a.op == "rmdir":
        if not os.path.isdir(L(src)):
            return "folder no longer exists"
        if os.listdir(L(src)):
            return "folder is no longer empty"
        return None
    if not _ex(src):
        return "file no longer exists"
    st = os.stat(L(src))
    if a.size and st.st_size != a.size:
        return "file size changed since review"
    if a.mtime is not None and abs(st.st_mtime - a.mtime) > 0.001:
        return "file was modified since review"
    if a.hash and a.op != "copy" and full_hash(src) != a.hash:
        return "file content changed since review"
    return None


def _log(db, batch_id, seq, a: Action, dst, status, error=None) -> int:
    cur = db.execute("INSERT INTO operations (batch_id, seq, op, src, dst, size, hash, reason, status, error) "
                     "VALUES (?,?,?,?,?,?,?,?,?,?)",
                     (batch_id, seq, a.op, a.src, str(dst) if dst else None, a.size, a.hash, a.reason, status, error))
    return cur.lastrowid


# ---------------------------------------------------------------------------------------
# History, undo, recovery
# ---------------------------------------------------------------------------------------
def batches(lib: Library) -> list[dict]:
    rows = lib.db.execute("SELECT * FROM batches WHERE status!='nothing' ORDER BY created_at DESC, id DESC").fetchall()
    return [dict(r) for r in rows]


def operations(lib: Library, batch_id: str) -> list[dict]:
    return [dict(r) for r in lib.db.execute(
        "SELECT * FROM operations WHERE batch_id=? ORDER BY seq", (batch_id,))]


def undo(lib: Library, batch_id: str, progress: Optional[Progress] = None) -> BatchResult:
    """Reverse a batch. Moves go back to their original path (or a non-clobbering variant)."""
    progress = progress or Progress()
    res = BatchResult(batch_id)
    ops = lib.db.execute("SELECT * FROM operations WHERE batch_id=? AND status='done' ORDER BY seq DESC",
                         (batch_id,)).fetchall()
    total = len(ops)
    for i, op in enumerate(ops):
        try:
            progress.update(i, total, f"Undoing… {i:,} of {total:,}")
        except Cancelled:
            res.cancelled = True
            break
        src, dst = Path(op["src"]), Path(op["dst"]) if op["dst"] else None
        try:
            if op["op"] in ("recycle", "move"):
                if not _ex(dst):
                    raise FileNotFoundError(f"{dst.name} is no longer in its moved location")
                target = src if not _ex(src) else _unique(src)
                if target != src:
                    res.messages.append(f"{src.name} restored as {target.name} (a file with that name exists)")
                safe_move(dst, target)
                _undo_catalogue(lib, op, dst, target)
            elif op["op"] == "copy":
                if _ex(dst):
                    # Only remove the copy when it still matches the source content exactly.
                    if op["hash"] and full_hash(dst) != op["hash"]:
                        raise OSError(f"{dst.name} was modified after copying; left in place")
                    os.remove(L(dst))
                    if _inside(dst, lib.root):
                        row = lib.file_by_rel(str(dst.relative_to(lib.root)))
                        if row is not None:
                            lib.remove_rows([row["id"]])
            elif op["op"] == "rmdir":
                os.makedirs(L(src), exist_ok=True)
            lib.db.execute("UPDATE operations SET status='undone' WHERE id=?", (op["id"],))
            res.done += 1
            res.bytes += op["size"] or 0
        except Exception as e:
            res.failed += 1
            res.messages.append(f"Could not undo {src.name}: {e}")
    _prune_empty(lib.recovery / batch_id)
    remaining = lib.db.execute("SELECT COUNT(*) FROM operations WHERE batch_id=? AND status='done'",
                               (batch_id,)).fetchone()[0]
    lib.db.execute("UPDATE batches SET status=? WHERE id=?", ("undone" if remaining == 0 else "partial", batch_id))
    if not res.cancelled:
        progress.update(total, total, "Undo complete", force=True)
    return res


def _undo_catalogue(lib: Library, op, dst: Path, target: Path) -> None:
    """Keep catalogue rows (analysis, thumbnails, health fingerprints) in step with an undone move."""
    if not _inside(target, lib.root):
        return
    rel_target = str(target.relative_to(lib.root))
    if op["op"] == "recycle":
        lib.restore_parked(op["id"], rel_target)
    elif _inside(dst, lib.root):
        folder, name = os.path.split(rel_target)
        with lib.transaction() as tx:
            if not tx.execute("SELECT 1 FROM files WHERE rel_path=?", (rel_target,)).fetchone():
                tx.execute("UPDATE files SET rel_path=?, folder=?, name=? WHERE rel_path=?",
                           (rel_target, folder, name, str(dst.relative_to(lib.root))))


def _prune_empty(folder: Path) -> None:
    if not os.path.isdir(L(folder)):
        return
    for dirpath, dirnames, filenames in os.walk(folder, topdown=False):
        if not os.listdir(dirpath):
            try:
                os.rmdir(L(dirpath))
            except OSError:
                pass


def recovery_size(lib: Library) -> tuple[int, int]:
    files = size = 0
    if _ex(lib.recovery):
        for dirpath, _, filenames in os.walk(lib.recovery):
            for f in filenames:
                files += 1
                try:
                    size += os.path.getsize(os.path.join(dirpath, f))
                except OSError:
                    pass
    return files, size


def empty_recovery(lib: Library, batch_ids: Optional[list[str]] = None,
                   progress: Optional[Progress] = None) -> int:
    """Permanently delete files in Recovery. The only destructive operation in Memoria."""
    progress = progress or Progress()
    removed = 0
    targets = [lib.recovery / b for b in batch_ids] if batch_ids else (
        list(lib.recovery.iterdir()) if _ex(lib.recovery) else [])
    for i, t in enumerate(targets):
        progress.update(i, len(targets), f"Deleting from Recovery… {i:,} of {len(targets):,} changes")
        if os.path.isdir(L(t)):
            for _, _, fs in os.walk(t):
                removed += len(fs)
            shutil.rmtree(L(t), ignore_errors=True)
            ops = [r[0] for r in lib.db.execute("SELECT id FROM operations WHERE batch_id=? AND op='recycle' "
                                                "AND status='done'", (t.name,))]
            lib.db.execute("UPDATE batches SET status='emptied' WHERE id=? AND status IN ('applied','partial')",
                           (t.name,))
            lib.db.execute("UPDATE operations SET status='purged' WHERE batch_id=? AND op='recycle' "
                           "AND status='done'", (t.name,))
            lib.drop_parked(ops)
    progress.update(len(targets), len(targets), "Recovery emptied", force=True)
    return removed


def reconcile(lib: Library) -> int:
    """Repair the journal after a crash: resolve operations left in ``pending`` state."""
    fixed = 0
    for op in lib.db.execute("SELECT * FROM operations WHERE status='pending'").fetchall():
        src_exists = _ex(op["src"])
        dst_exists = bool(op["dst"]) and _ex(op["dst"])
        if op["op"] in ("recycle", "move"):
            status = "done" if dst_exists and not src_exists else "failed"
        elif op["op"] == "copy":
            status = "done" if dst_exists and full_hash(op["dst"]) == op["hash"] else "failed"
            tmp = Path(str(op["dst"]) + ".memoria-tmp") if op["dst"] else None
            if tmp and _ex(tmp):
                os.remove(L(tmp))
        else:
            status = "done" if not src_exists else "failed"
        lib.db.execute("UPDATE operations SET status=?, error=COALESCE(error,'interrupted') WHERE id=?",
                       (status, op["id"]))
        lib.db.execute("UPDATE batches SET status='partial' WHERE id=? AND status='applying'", (op["batch_id"],))
        fixed += 1
    lib.db.execute("UPDATE batches SET status='partial' WHERE status='applying'")
    return fixed
