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
from contextlib import contextmanager
from contextvars import ContextVar
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
    verified: set = set()
    try:
        for seq, a in enumerate(actions):
            progress.update(seq, total, f"{title}… {seq:,} of {total:,}")
            src = Path(a.src)
            try:
                problem = _preflight(a, src, verified)
            except OSError as e:
                problem = f"could not check file: {e}"
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
                if a.file_id is not None:
                    if a.op == "recycle":
                        lib.park_rows([(op_id, a.file_id)])
                    elif a.op == "move" and _inside(dst, lib.root):
                        rel = str(dst.relative_to(lib.root))
                        folder, name = os.path.split(rel)
                        db.execute("UPDATE files SET rel_path=?, folder=?, name=? WHERE id=?",
                                   (rel, folder, name, a.file_id))
                db.execute("UPDATE operations SET status='done' WHERE id=?", (op_id,))
                res.done += 1
                res.bytes += a.size
            except Exception as e:
                res.failed += 1
                res.messages.append(f"Failed {src.name}: {e}")
                interrupted = a.op in ("move", "recycle") and _ex(dst) and not _ex(src)
                db.execute("UPDATE operations SET status=?, error=? WHERE id=?",
                           ("pending" if interrupted else "failed", str(e)[:300], op_id))
    except Cancelled:
        res.cancelled = True
    finally:
        status = "applied" if res.done and not res.failed and not res.cancelled else (
            "partial" if res.done else "nothing")
        db.execute("UPDATE batches SET status=?, files=?, bytes=? WHERE id=?",
                   (status, res.done, res.bytes, batch_id))
    if not res.cancelled:
        progress.update(total, total, f"{title}: done", force=True)
    return res


def record_created(lib: Library, kind: str, title: str, items: list[tuple[str, str]]) -> BatchResult:
    """Journal files that a tool has just created (edited copies, split parts…) so History can undo them.

    ``items`` are (source path, new file path). Undo removes a new file only if its content is unchanged.
    """
    batch_id = datetime.now().strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6]
    res = BatchResult(batch_id)
    db = lib.db
    db.execute("INSERT INTO batches (id, created_at, kind, title, status) VALUES (?,?,?,?,?)",
               (batch_id, _now(), kind, title, "applying"))
    for seq, (src, dst) in enumerate(items):
        size = os.path.getsize(L(dst)) if _ex(dst) else 0
        a = Action(op="create", src=str(src), dst=str(dst), size=size, hash=full_hash(dst),
                   reason=f"Created from {Path(src).name}")
        _log(db, batch_id, seq, a, Path(dst), "done")
        res.done += 1
        res.bytes += size
    db.execute("UPDATE batches SET status=?, files=?, bytes=? WHERE id=?",
               ("applied" if res.done else "nothing", res.done, res.bytes, batch_id))
    return res


_output_batch: ContextVar[Optional[tuple[Library, BatchResult, str]]] = ContextVar("output_batch", default=None)


@contextmanager
def created_batch(lib: Optional[Library], kind: str, title: str):
    """Journal publications as they happen, including outputs kept after cancellation."""
    if lib is None:
        yield None
        return
    result = BatchResult(datetime.now().strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6])
    lib.db.execute("INSERT INTO batches (id,created_at,kind,title,status) VALUES (?,?,?,?,?)",
                   (result.batch_id, _now(), kind, title, "applying"))
    token = _output_batch.set((lib, result, title))
    try:
        yield result
    finally:
        _output_batch.reset(token)
        # Some all-or-nothing exporters remove completed outputs when cancelled.
        for op in operations(lib, result.batch_id):
            if op["status"] == "done" and not _ex(op["dst"]):
                lib.db.execute("UPDATE operations SET status='undone' WHERE id=?", (op["id"],))
        done = [o for o in operations(lib, result.batch_id) if o["status"] == "done"]
        result.done, result.bytes = len(done), sum(o["size"] for o in done)
        pending = lib.db.execute("SELECT COUNT(*) FROM operations WHERE batch_id=? AND status='pending'",
                                 (result.batch_id,)).fetchone()[0]
        lib.db.execute("UPDATE batches SET status=?,files=?,bytes=? WHERE id=?",
                       ("partial" if pending else "applied" if done else "nothing",
                        result.done, result.bytes, result.batch_id))


@contextmanager
def record_output(tmp: Path, dst: Path):
    """Write durable intent and fingerprint before an exporter publishes its temp file."""
    active = _output_batch.get()
    if active is None:
        yield
        return
    lib, result, title = active
    fingerprint = full_hash(tmp)
    if not fingerprint:
        raise OSError(f"Cannot verify {tmp.name}; output was not published")
    a = Action("create", str(dst), str(dst), os.path.getsize(L(tmp)), hash=fingerprint, reason=title)
    seq = lib.db.execute("SELECT COUNT(*) FROM operations WHERE batch_id=?", (result.batch_id,)).fetchone()[0]
    op_id = _log(lib.db, result.batch_id, seq, a, dst, "pending")
    try:
        yield
    except FileExistsError:
        lib.db.execute("UPDATE operations SET status='failed',error='Name already taken' WHERE id=?", (op_id,))
        raise
    else:
        lib.db.execute("UPDATE operations SET status='done' WHERE id=?", (op_id,))


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
    if a.op == "copy" and not a.hash:
        a.hash = full_hash(src)
        if not a.hash:
            return "file could not be fingerprinted for a safe copy and Undo"
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
            elif op["op"] in ("copy", "create"):
                if _ex(dst):
                    # Only remove the copy/new file when it still matches the content we wrote.
                    if not op["hash"]:
                        raise OSError(f"{dst.name} has no recorded fingerprint; left in place for manual review")
                    if full_hash(dst) != op["hash"]:
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
            count = sum(len(fs) for _, _, fs in os.walk(t))
            shutil.rmtree(L(t))
            removed += count
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
    for op in lib.db.execute("SELECT * FROM operations WHERE status='pending' OR "
                             "(status='done' AND batch_id IN "
                             "(SELECT id FROM batches WHERE status='applying'))").fetchall():
        src_exists = _ex(op["src"])
        dst_exists = bool(op["dst"]) and _ex(op["dst"])
        if op["op"] in ("recycle", "move"):
            status = "done" if dst_exists and not src_exists else "failed"
            if status == "done" and _inside(Path(op["src"]), lib.root):
                row = lib.file_by_rel(lib.rel(op["src"]))
                if row is not None:
                    if op["op"] == "recycle":
                        lib.park_rows([(op["id"], row["id"])])
                    elif _inside(Path(op["dst"]), lib.root):
                        rel = lib.rel(op["dst"])
                        folder, name = os.path.split(rel)
                        lib.db.execute("UPDATE files SET rel_path=?, folder=?, name=? WHERE id=?",
                                       (rel, folder, name, row["id"]))
        elif op["op"] in ("copy", "create"):
            status = "done" if dst_exists and full_hash(op["dst"]) == op["hash"] else "failed"
            tmp = Path(str(op["dst"]) + ".memoria-tmp") if op["dst"] and op["op"] == "copy" else None
            if tmp and _ex(tmp):
                os.remove(L(tmp))
        else:
            status = "done" if not src_exists else "failed"
        lib.db.execute("UPDATE operations SET status=?, error=COALESCE(error,'interrupted') WHERE id=?",
                       (status, op["id"]))
        lib.db.execute("UPDATE batches SET status='partial' WHERE id=?", (op["batch_id"],))
        fixed += 1
    lib.db.execute("UPDATE batches SET status='partial' WHERE status='applying'")
    lib.db.execute("UPDATE batches SET files=(SELECT COUNT(*) FROM operations WHERE batch_id=batches.id "
                   "AND status='done'), bytes=COALESCE((SELECT SUM(size) FROM operations WHERE batch_id=batches.id "
                   "AND status='done'),0) WHERE status='partial'")
    return fixed
