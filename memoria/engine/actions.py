"""Safe file operations: every change is journaled, verified and undoable.

Rules enforced here (the UI relies on them):
* Nothing is ever deleted. "Remove" means *move into the library's Recovery folder*.
* Before acting, each source file is checked against what the user reviewed (size, mtime and,
  for duplicates, a fresh full-content hash). Changed files are skipped, not acted on.
* Copies are written to a temporary name, hash-verified, then renamed. Existing files are
  never overwritten.
* Linked operations are journaled before publication and committed as one group.
  Publication/Undo intents distinguish unstarted siblings from interrupted work.
"""
from __future__ import annotations

import os
import json
import shutil
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from . import config, roots
from .config import longpath as L
from .db import Library, LibraryUnavailable
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
    asset_group: str = ""
    companion_ids: tuple[int, ...] = ()
    companions_locked: bool = False
    merge_into: Optional[int] = None


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
    return datetime.now().isoformat(sep=" ", timespec="microseconds")


def _reviewed_units(lib, planned, kind, reviewed):
    from . import assets
    detected = assets.prepare(lib, planned, kind)
    if detected.groups and not reviewed:
        raise ValueError("Linked photo/video/edit components require explicit group review before execution.")
    units = assets.grouped(planned)
    linked_paths = {candidate.src for candidate in detected.actions if candidate.asset_group}
    for unit in units:
        if not unit[0].asset_group:
            if unit[0].src in linked_paths:
                raise ValueError("This linked asset was not prepared as a complete group. Review it again.")
            if unit[0].companion_ids:
                raise ValueError("Companion identities require a prepared linked group.")
            continue
        if not reviewed or not unit[0].companion_ids:
            raise ValueError("Linked assets must be prepared and explicitly reviewed.")
        expected = unit[0].companion_ids
        ids = []
        for action in unit:
            if (action.companion_ids != expected or action.op != unit[0].op or
                    action.op not in ("copy", "move", "recycle") or not lib.contains(action.src)):
                raise ValueError("The prepared linked asset is inconsistent. Review it again.")
            row = lib.file_by_rel(lib.rel(action.src))
            if row is None:
                raise ValueError("A linked component left the catalogue. Review it again.")
            ids.append(row["id"])
        if tuple(sorted(ids)) != expected:
            raise ValueError("The linked asset is incomplete. No files were changed.")
    return units


def _destinations(lib, unit, batch_id, reserved):
    from . import assets
    proposed = []
    for action in unit:
        src = Path(action.src)
        if action.op == "rmdir":
            return [None]
        if action.op == "recycle":
            if lib.contains(src):
                source, rel = roots.split_key(lib.rel(src))
                folder = config.recovery_dir(lib.abspath(roots.key_for(source))) / batch_id
            else:
                rel, folder = src.name, lib.recovery / batch_id
            proposed.append(folder / rel)
        else:
            if not action.dst:
                raise ValueError("The destination is missing.")
            proposed.append(Path(action.dst))
    return assets.destinations(unit, proposed, reserved)


def _forward_catalogue(lib, op, src, dst, file_id=None):
    if op["op"] not in ("move", "recycle") or not lib.contains(src):
        return
    row = lib.file(file_id) if file_id is not None else lib.file_by_rel(lib.rel(src))
    if row is None:
        return
    if op["op"] == "recycle":
        lib.park_rows([(op["id"], row["id"])])
    elif lib.contains(dst):
        rel = lib.rel(dst)
        folder, name = os.path.split(rel)
        lib.db.execute("UPDATE files SET rel_path=?,folder=?,name=?,root_id=? WHERE id=?",
                       (rel, folder, name, roots.split_key(rel)[0], row["id"]))


def _verified_output(op, path):
    if not op["hash"] or full_hash(path) != op["hash"]:
        raise OSError(f"{path.name} changed or has no fingerprint; left untouched for manual recovery")


def _remove_output_row(lib, path):
    if lib.contains(path):
        row = lib.file_by_rel(lib.rel(path))
        if row is not None:
            lib.remove_rows([row["id"]])


def _rollback_apply(lib, records, reason):
    errors = []
    for saved in reversed(records):
        op = lib.db.execute("SELECT * FROM operations WHERE id=?", (saved["id"],)).fetchone()
        try:
            if op["status"] in ("pending", "failed", "skipped"):
                lib.db.execute("UPDATE operations SET status='failed',error=? WHERE id=?",
                               ("Not published; group rolled back: " + reason, op["id"]))
                continue
            src, dst = _operation_path(lib, op, "src"), _operation_path(lib, op, "dst")
            lib.check_path(src)
            if dst is not None:
                lib.check_path(dst)
            if op["op"] in ("move", "recycle"):
                if dst is not None and _ex(dst):
                    _verified_output(op, dst)
                    if _ex(src):
                        _verified_output(op, src)
                        os.remove(L(dst))  # Interrupted cross-volume move: original still exists.
                    else:
                        safe_move(dst, src)
                elif not _ex(src):
                    raise OSError("Both the source and moved file are missing")
                _undo_catalogue(lib, op, dst, src)
            elif op["op"] == "copy":
                if dst is not None and _ex(dst):
                    _verified_output(op, dst)
                    os.remove(L(dst))
                    _remove_output_row(lib, dst)
            elif op["op"] == "rmdir":
                os.makedirs(L(src), exist_ok=True)
            lib.db.execute("UPDATE operations SET status='failed',error=? WHERE id=?",
                           ("Rolled back: " + reason, op["id"]))
        except Exception as error:
            message = f"Rollback incomplete for operation {op['id']}: {error}"
            errors.append(message)
            lib.db.execute("UPDATE operations SET error=? WHERE id=?", (message, op["id"]))
    return errors


def apply(lib: Library, kind: str, title: str, actions: list[Action],
          progress: Optional[Progress] = None, *, companions_reviewed: bool = False) -> BatchResult:
    from . import assets, metadata_history, organisation
    progress = progress or Progress()
    units = _reviewed_units(lib, actions, kind, companions_reviewed)
    batch_id = datetime.now().strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6]
    res = BatchResult(batch_id)
    db = lib.db
    db.execute("INSERT INTO batches (id, created_at, kind, title, status) VALUES (?,?,?,?,?)",
               (batch_id, _now(), kind, title, "applying"))
    total = len(actions)
    reserved, completed = set(), 0
    try:
        for unit in units:
            progress.update(completed, total, f"{title}… {completed:,} of {total:,}")
            seqs = [2 * (completed + i) + 1 for i in range(len(unit))]
            completed += len(unit)
            problem = None
            try:
                assets.validate_membership(lib, unit)
                verified = set()
                for a in unit:
                    progress.check()
                    src = Path(a.src)
                    lib.check_path(src)
                    for guard, _ in a.guards:
                        lib.check_path(guard)
                    if a.dst:
                        lib.check_path(a.dst)
                    problem = _preflight(a, src, verified)
                    if problem:
                        break
                    if a.op in ("move", "recycle") and not a.hash:
                        a.hash = full_hash(src)
                        if not a.hash:
                            raise OSError("Could not fingerprint the file for safe rollback")
                    if a.file_id is None and lib.contains(src) and a.op in ("move", "recycle"):
                        row = lib.file_by_rel(lib.rel(src))
                        a.file_id = row["id"] if row is not None else None
                    if a.file_id is not None and a.op in ("move", "recycle"):
                        row = lib.file(a.file_id)
                        if row is None or lib.abspath(row["rel_path"]) != src:
                            raise ValueError("The reviewed file identity changed")
                    if a.merge_into is not None:
                        if a.file_id is None or a.op not in ("move", "recycle"):
                            raise ValueError("Only a removed catalogue file can merge organisation")
                        organisation.merged_state(lib, a.file_id, a.merge_into)
                destinations = _destinations(lib, unit, batch_id, reserved) if not problem else []
            except (OSError, ValueError, LibraryUnavailable) as e:
                problem = f"could not check file: {e}"
            if problem:
                res.skipped += len(unit)
                res.messages.append(f"Skipped {'linked asset' if unit[0].asset_group else Path(unit[0].src).name}: {problem}")
                for seq, a in zip(seqs, unit):
                    _log(lib, batch_id, seq, a, None, "skipped", problem)
                continue
            with lib.transaction():
                op_ids = [_log(lib, batch_id, seq, a, dst, "pending")
                          for seq, a, dst in zip(seqs, unit, destinations)]
            records = [lib.db.execute("SELECT * FROM operations WHERE id=?", (op_id,)).fetchone() for op_id in op_ids]
            try:
                for a, dst, op in zip(unit, destinations, records):
                    progress.check()
                    src = Path(a.src)
                    lib.check_path(src)
                    if dst is not None:
                        lib.check_path(dst)
                    if a.asset_group:
                        problem = _preflight(a, src)
                        if problem:
                            raise OSError(problem)
                    db.execute("UPDATE operations SET status='publishing' WHERE id=?", (op["id"],))
                    try:
                        if a.op in ("recycle", "move"):
                            safe_move(src, dst)
                        elif a.op == "copy":
                            verified_copy(src, dst, a.hash)
                        elif a.op == "rmdir":
                            os.rmdir(L(src))
                    except FileExistsError:
                        db.execute("UPDATE operations SET status='failed',error='Destination already exists' WHERE id=?",
                                   (op["id"],))
                        raise
                    db.execute("UPDATE operations SET status='published' WHERE id=?", (op["id"],))
                    _forward_catalogue(lib, op, src, dst, a.file_id)
                    if a.asset_group:
                        progress.check()
                with lib.transaction():
                    db.executemany("UPDATE operations SET status='done' WHERE id=?", [(i,) for i in op_ids])
                    for a, op in zip(unit, records):
                        if a.merge_into is not None:
                            metadata_history.apply_merge(lib, op["id"], a.file_id, a.merge_into, op["seq"] - 1)
                res.done += len(unit)
                res.bytes += sum(a.size for a in unit)
            except Cancelled:
                errors = _rollback_apply(lib, records, "cancelled while processing the linked asset")
                res.messages.extend(errors)
                res.failed += len(errors)
                raise
            except Exception as e:
                res.failed += len(unit)
                res.messages.append(f"Failed {Path(unit[0].src).name}: {e}")
                res.messages.extend(_rollback_apply(lib, records, str(e)))
                if progress.cancelled:
                    res.cancelled = True
                    break
    except Cancelled:
        res.cancelled = True
    finally:
        pending = db.execute("SELECT 1 FROM operations WHERE batch_id=? AND status IN ('pending','publishing','published')",
                             (batch_id,)).fetchone()
        status = "partial" if pending else "applied" if res.done and not res.failed and not res.cancelled else (
            "partial" if res.done else "nothing")
        db.execute("UPDATE batches SET status=?, files=?, bytes=? WHERE id=?",
                   (status, res.done, res.bytes, batch_id))
    if not res.cancelled:
        try:
            progress.update(total, total, f"{title}: done", force=True)
        except Cancelled:
            res.cancelled = True
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
        _log(lib, batch_id, seq, a, Path(dst), "done")
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
    op_id = _log(lib, result.batch_id, seq, a, dst, "pending")
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
    if a.op not in ("copy", "move", "recycle", "rmdir"):
        return "unsupported file operation"
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
    if a.hash and full_hash(src) != a.hash:
        return "file content changed since review"
    if a.op == "copy" and not a.hash:
        a.hash = full_hash(src)
        if not a.hash:
            return "file could not be fingerprinted for a safe copy and Undo"
    return None


def _log(lib, batch_id, seq, a: Action, dst, status, error=None) -> int:
    src_key = lib.rel(a.src) if lib.contains(a.src) else None
    dst_key = lib.rel(dst) if dst is not None and lib.contains(dst) else None
    cur = lib.db.execute(
        "INSERT INTO operations (batch_id,seq,op,src,dst,size,hash,reason,status,error,src_key,dst_key,merge_target,asset_group) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (batch_id, seq, a.op, a.src, str(dst) if dst else None, a.size, a.hash, a.reason, status, error,
         src_key, dst_key, a.merge_into, a.asset_group))
    return cur.lastrowid


def _operation_path(lib: Library, op, column: str) -> Optional[Path]:
    key = op[column + "_key"]
    return lib.abspath(key) if key is not None else (Path(op[column]) if op[column] else None)


# ---------------------------------------------------------------------------------------
# History, undo, recovery
# ---------------------------------------------------------------------------------------
def batches(lib: Library, limit: Optional[int] = None, offset: int = 0) -> list[dict]:
    if offset < 0 or limit is not None and limit < 1:
        raise ValueError("Invalid history page.")
    suffix, params = (" LIMIT ? OFFSET ?", (limit, offset)) if limit is not None else ("", ())
    rows = lib.db.execute("SELECT * FROM batches WHERE status!='nothing' ORDER BY created_at DESC, rowid DESC"
                          + suffix, params).fetchall()
    return [dict(r) for r in rows]


def operations(lib: Library, batch_id: str, limit: Optional[int] = None, offset: int = 0) -> list[dict]:
    if offset < 0 or limit is not None and limit < 1:
        raise ValueError("Invalid operation page.")
    result = []
    suffix, params = (" LIMIT ? OFFSET ?", (batch_id, limit, offset)) if limit is not None else ("", (batch_id,))
    for row in lib.db.execute("SELECT * FROM operations WHERE batch_id=? ORDER BY seq" + suffix, params):
        item = dict(row)
        for column in ("src", "dst"):
            path = _operation_path(lib, row, column)
            item[column] = str(path) if path is not None else None
        result.append(item)
    return result


def _operation_units(ops):
    units, groups = [], {}
    for op in ops:
        key = (op["batch_id"], op["asset_group"])
        if not op["asset_group"] or op["op"] == "metadata":
            units.append([op])
        elif key in groups:
            groups[key].append(op)
        else:
            groups[key] = [op]
            units.append(groups[key])
    return units


def _intent_path(lib, intent, name):
    key = intent.get(name + "_key")
    return lib.abspath(key) if key is not None else Path(intent[name]) if intent.get(name) else None


def _undo_intent(op):
    try:
        value = json.loads(op["error"] or "")
    except (ValueError, TypeError):
        return None
    return value if isinstance(value, dict) and value.get("phase") == "linked_undo" else None


def _rollback_undo(lib, records):
    errors = []
    for op in reversed(records):
        try:
            intent = _undo_intent(op)
            if intent is None:
                raise OSError("The linked Undo intent is unavailable")
            dst = _operation_path(lib, op, "dst")
            source = _intent_path(lib, intent, "target" if op["op"] in ("move", "recycle") else "holding")
            lib.check_path(dst)
            if source is not None:
                lib.check_path(source)
                if _ex(source):
                    if _ex(dst):
                        raise FileExistsError(f"Both {source} and {dst} exist; neither was overwritten")
                    _verified_output({"hash": intent["hash"]}, source)
                    safe_move(source, dst)
                elif not _ex(dst) and not intent.get("absent"):
                    raise OSError(f"Neither {source} nor {dst} exists")
            if op["op"] in ("move", "recycle"):
                _forward_catalogue(lib, op, source, dst)
        except Exception as error:
            errors.append(f"Undo rollback incomplete for operation {op['id']}: {error}")
    if not errors:
        with lib.transaction() as db:
            db.executemany("UPDATE operations SET status='done',error=NULL WHERE id=?", [(op["id"],) for op in records])
    return errors


def _cleanup_undo(lib, op):
    intent = _undo_intent(op)
    if intent is None:
        return
    dst = _operation_path(lib, op, "dst")
    holding = _intent_path(lib, intent, "holding")
    if op["op"] in ("copy", "create"):
        if holding is not None:
            lib.check_path(holding)
            if _ex(holding):
                _verified_output({"hash": intent["hash"]}, holding)
                os.remove(L(holding))
        _remove_output_row(lib, dst)
    lib.db.execute("UPDATE operations SET error=NULL WHERE id=?", (op["id"],))


def _undo_linked(lib, records, progress, messages):
    from . import assets
    moving = records[0]["op"] in ("move", "recycle")
    if any((op["op"] in ("move", "recycle")) != moving for op in records):
        raise ValueError("The linked journal mixes incompatible operations")
    paths, hashes = [], []
    for op in records:
        src, dst = _operation_path(lib, op, "src"), _operation_path(lib, op, "dst")
        lib.check_path(src)
        lib.check_path(dst)
        if moving and not _ex(dst):
            raise FileNotFoundError(f"{dst} is no longer in its moved location")
        digest = full_hash(dst) if _ex(dst) else None
        if _ex(dst) and not digest:
            raise OSError(f"Could not verify {dst}")
        if not moving and _ex(dst):
            _verified_output(op, dst)
        paths.append(src)
        hashes.append(digest)
    targets = assets.destinations([Action("move", str(path)) for path in paths], paths, set()) if moving else []
    intents = []
    for i, op in enumerate(records):
        dst = _operation_path(lib, op, "dst")
        target = targets[i] if moving else None
        holding = None if moving or not _ex(dst) else dst.with_name(dst.name + ".memoria-undo-" + uuid.uuid4().hex)
        intent = {"phase": "linked_undo", "hash": hashes[i], "absent": not _ex(dst)}
        for key, path in (("target", target), ("holding", holding)):
            intent[key] = str(path) if path is not None else None
            intent[key + "_key"] = lib.rel(path) if path is not None and lib.contains(path) else None
        intents.append(intent)
    with lib.transaction() as db:
        db.executemany("UPDATE operations SET status='undo_pending',error=? WHERE id=?",
                       [(json.dumps(intent), op["id"]) for intent, op in zip(intents, records)])
    pending = [lib.db.execute("SELECT * FROM operations WHERE id=?", (op["id"],)).fetchone() for op in records]
    try:
        for op, intent in zip(records, intents):
            progress.check()
            dst = _operation_path(lib, op, "dst")
            lib.check_path(dst)
            if moving:
                target = _intent_path(lib, intent, "target")
                lib.check_path(target)
                _verified_output({"hash": intent["hash"]}, dst)
                safe_move(dst, target)
                _undo_catalogue(lib, op, dst, target)
                if target != _operation_path(lib, op, "src"):
                    messages.append(f"{dst.name} restored as {target.name} to keep the linked names together")
            else:
                holding = _intent_path(lib, intent, "holding")
                if holding is not None:
                    lib.check_path(holding)
                    _verified_output(op, dst)
                    safe_move(dst, holding)
            progress.check()
        with lib.transaction() as db:
            db.executemany("UPDATE operations SET status='undone' WHERE id=?", [(op["id"],) for op in records])
    except BaseException as error:
        if isinstance(error, (Exception, Cancelled)):
            errors = _rollback_undo(lib, pending)
            messages.extend(errors)
            if errors and isinstance(error, Cancelled):
                raise OSError("Cancelled Undo could not fully roll back; retained journal intents need recovery") from error
        raise
    for op in pending:
        try:
            _cleanup_undo(lib, op)
        except Exception as error:
            messages.append(f"Undo completed; verified holding-copy cleanup remains pending: {error}")


def undo(lib: Library, batch_id: str, progress: Optional[Progress] = None) -> BatchResult:
    """Reverse a batch. Moves go back to their original path (or a non-clobbering variant)."""
    progress = progress or Progress()
    res = BatchResult(batch_id)
    ops = lib.db.execute("SELECT * FROM operations WHERE batch_id=? AND status='done' ORDER BY seq DESC",
                         (batch_id,)).fetchall()
    if ops:
        lib.db.execute("UPDATE batches SET status='undoing' WHERE id=?", (batch_id,))
    from . import metadata_history
    total = len(ops)
    for i, unit in enumerate(_operation_units(ops)):
        try:
            progress.update(i, total, f"Undoing… {i:,} of {total:,}")
        except Cancelled:
            res.cancelled = True
            break
        op = unit[0]
        src, dst = _operation_path(lib, op, "src"), _operation_path(lib, op, "dst")
        try:
            if op["op"] == "metadata":
                metadata_history.undo_merge(lib, op["id"])
                continue
            if op["asset_group"]:
                _undo_linked(lib, unit, progress, res.messages)
                res.done += len(unit)
                res.bytes += sum(row["size"] or 0 for row in unit)
                continue
            lib.check_path(src)
            if dst is not None:
                lib.check_path(dst)
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
                    if lib.contains(dst):
                        row = lib.file_by_rel(lib.rel(dst))
                        if row is not None:
                            lib.remove_rows([row["id"]])
            elif op["op"] == "rmdir":
                os.makedirs(L(src), exist_ok=True)
            lib.db.execute("UPDATE operations SET status='undone' WHERE id=?", (op["id"],))
            res.done += 1
            res.bytes += op["size"] or 0
        except Cancelled:
            res.cancelled = True
            break
        except Exception as e:
            res.failed += len(unit)
            res.messages.append(f"Could not undo {src.name}: {e}")
            if progress.cancelled:
                res.cancelled = True
                break
    for source, folder in lib.recovery_folders():
        if lib.db.execute("SELECT online FROM library_roots WHERE id=?", (source,)).fetchone()[0]:
            _prune_empty(folder / batch_id)
    remaining = lib.db.execute("SELECT COUNT(*) FROM operations WHERE batch_id=? AND status IN ('done','undo_pending')",
                               (batch_id,)).fetchone()[0]
    lib.db.execute("UPDATE batches SET status=? WHERE id=?", ("undone" if remaining == 0 else "partial", batch_id))
    if not res.cancelled:
        try:
            progress.update(total, total, "Undo complete", force=True)
        except Cancelled:
            res.cancelled = True
    return res


def _undo_catalogue(lib: Library, op, dst: Path, target: Path) -> None:
    """Keep catalogue rows (analysis, thumbnails, health fingerprints) in step with an undone move."""
    if not lib.contains(target):
        return
    rel_target = lib.rel(target)
    if op["op"] == "recycle":
        lib.restore_parked(op["id"], rel_target)
    elif lib.contains(dst):
        folder, name = os.path.split(rel_target)
        with lib.transaction() as tx:
            if not tx.execute("SELECT 1 FROM files WHERE rel_path=?", (rel_target,)).fetchone():
                tx.execute("UPDATE files SET rel_path=?, folder=?, name=?,root_id=? WHERE rel_path=?",
                           (rel_target, folder, name, roots.split_key(rel_target)[0], lib.rel(dst)))


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
    """Known Recovery on available roots. Offline-root status is shown separately by the UI."""
    files = size = 0
    for source, folder in lib.recovery_folders():
        try:
            roots.check(lib, source)
        except LibraryUnavailable:
            continue
        if not _ex(folder):
            continue
        for dirpath, _, filenames in os.walk(folder):
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
    for source in lib.roots():
        roots.check(lib, source["id"])
    if lib.db.execute("SELECT 1 FROM operations WHERE op='recycle' AND status='done' "
                      "AND merge_target IS NOT NULL AND merge_complete=0").fetchone():
        raise ValueError("Finish the pending organisation merges before emptying Recovery.")
    if lib.db.execute("SELECT 1 FROM operations WHERE status IN ('pending','publishing','published','undo_pending')").fetchone():
        raise ValueError("Resolve interrupted operations before emptying Recovery.")
    if batch_ids and any(Path(b).name != b or b in (".", "..") for b in batch_ids):
        raise ValueError("Invalid Recovery batch identifier.")
    targets = []
    for source, folder in lib.recovery_folders():
        if batch_ids:
            targets.extend((source, folder / b) for b in batch_ids)
        elif _ex(folder):
            targets.extend((source, path) for path in folder.iterdir())
    for i, (source, t) in enumerate(targets):
        progress.update(i, len(targets), f"Deleting from Recovery… {i:,} of {len(targets):,} changes")
        if os.path.isdir(L(t)):
            count = sum(len(fs) for _, _, fs in os.walk(t))
            shutil.rmtree(L(t))
            removed += count
            ops = [row["id"] for row in lib.db.execute(
                "SELECT * FROM operations WHERE batch_id=? AND op='recycle' AND status='done'", (t.name,))
                if _inside(_operation_path(lib, row, "dst"), t)]
            lib.db.executemany("UPDATE operations SET status='purged' WHERE id=?", [(i,) for i in ops])
            lib.drop_parked(ops)
            if not lib.db.execute("SELECT 1 FROM operations WHERE batch_id=? AND op='recycle' AND status='done'",
                                  (t.name,)).fetchone():
                lib.db.execute("UPDATE batches SET status='emptied' WHERE id=? AND status IN ('applied','partial')",
                               (t.name,))
    progress.update(len(targets), len(targets), "Recovery emptied", force=True)
    return removed


def reconcile(lib: Library) -> int:
    """Repair the journal after a crash: resolve operations left in ``pending`` state."""
    from . import metadata_history
    fixed = 0
    for group in lib.db.execute(
            "SELECT DISTINCT batch_id,asset_group FROM operations WHERE asset_group!='' "
            "AND status IN ('pending','publishing','published','undo_pending')").fetchall():
        records = lib.db.execute("SELECT * FROM operations WHERE batch_id=? AND asset_group=? ORDER BY seq",
                                 (group["batch_id"], group["asset_group"])).fetchall()
        if any(op["status"] == "undo_pending" for op in records):
            errors = _rollback_undo(lib, records)
        else:
            errors = _rollback_apply(lib, records, "interrupted linked asset")
        if not errors:
            fixed += len(records)
        lib.db.execute("UPDATE batches SET status='partial' WHERE id=?", (group["batch_id"],))
    for op in lib.db.execute("SELECT * FROM operations WHERE status IN ('pending','publishing','published') OR "
                             "(status='done' AND batch_id IN "
                             "(SELECT id FROM batches WHERE status='applying'))").fetchall():
        if op["asset_group"] or op["op"] == "metadata":
            continue
        src, dst = _operation_path(lib, op, "src"), _operation_path(lib, op, "dst")
        try:
            lib.check_path(src)
            if dst is not None:
                lib.check_path(dst)
        except LibraryUnavailable:
            continue
        src_exists = _ex(src)
        dst_exists = dst is not None and _ex(dst)
        if op["op"] in ("recycle", "move"):
            status = "done" if dst_exists and not src_exists else "failed"
            if status == "done":
                _forward_catalogue(lib, op, src, dst)
        elif op["op"] in ("copy", "create"):
            status = "done" if dst_exists and full_hash(dst) == op["hash"] else "failed"
            tmp = Path(str(dst) + ".memoria-tmp") if dst is not None and op["op"] == "copy" else None
            if tmp and _ex(tmp):
                os.remove(L(tmp))
        else:
            status = "done" if not src_exists else "failed"
        lib.db.execute("UPDATE operations SET status=?, error=COALESCE(error,'interrupted') WHERE id=?",
                       (status, op["id"]))
        lib.db.execute("UPDATE batches SET status='partial' WHERE id=?", (op["batch_id"],))
        fixed += 1
    for op in lib.db.execute("SELECT * FROM operations WHERE status='done' "
                             "AND merge_target IS NOT NULL AND merge_complete=0 ORDER BY batch_id,seq").fetchall():
        try:
            row = lib.db.execute("SELECT file_id FROM parked_files WHERE op_id=?", (op["id"],)).fetchone()
            source_id = row["file_id"] if row is not None else None
            if source_id is None:
                path = _operation_path(lib, op, "dst" if op["op"] == "move" else "src")
                source = lib.file_by_rel(lib.rel(path)) if lib.contains(path) else None
                source_id = source["id"] if source is not None else None
            if source_id is None:
                raise ValueError("The removed source identity is unavailable")
            metadata_history.apply_merge(lib, op["id"], source_id, op["merge_target"], op["seq"] - 1)
            fixed += 1
        except Exception as error:
            lib.db.execute("UPDATE operations SET error=? WHERE id=?",
                           (f"Organisation merge pending: {error}", op["id"]))
    for op in lib.db.execute("SELECT * FROM operations WHERE status='undone' AND error IS NOT NULL").fetchall():
        if _undo_intent(op) is not None:
            try:
                _cleanup_undo(lib, op)
            except (OSError, LibraryUnavailable):
                pass  # Keep the durable cleanup intent; never delete a changed holding copy.
    lib.db.execute("UPDATE batches SET status='partial' WHERE status IN ('applying','undoing')")
    lib.db.execute("UPDATE batches SET files=(SELECT COUNT(*) FROM operations WHERE batch_id=batches.id "
                   "AND status='done' AND op!='metadata'), bytes=COALESCE((SELECT SUM(size) FROM operations WHERE batch_id=batches.id "
                   "AND status='done' AND op!='metadata'),0) WHERE status='partial'")
    return fixed
