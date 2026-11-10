"""Reviewed, non-destructive restoration of journaled and unlogged Recovery files.

Preview reads directory entries, file stats and the journal only. Imports are new
adoption records, never claims about a historical deletion. Existing originals are
never removed or replaced; an unresolved or skipped unit stays in Recovery.
"""
from __future__ import annotations

import errno
import json
import os
import re
import shutil
import stat
import uuid
from dataclasses import dataclass, field, replace
from datetime import datetime
from pathlib import Path
from typing import Callable

import xxhash

from . import actions, assets, config, recovery, roots
from .config import longpath as L
from .db import LibraryUnavailable
from .progress import Cancelled, Progress

_BATCH = re.compile(r"\d{8}-\d{6}-[0-9a-f]{6}")
_LEGACY_SESSION = re.compile(r"session_(\d{8}_\d{6})", re.IGNORECASE)
_MAPPING = "Original location unknown; choose a destination folder for this group."


@dataclass
class RestoreItem:
    source: Path
    target: Path | None
    root_id: int
    operation_id: int | None
    batch_id: str | None
    size: int
    mtime: float
    provenance: str
    mapping_group: str
    relative_path: str
    issue: str = ""
    _snapshot: tuple = field(default=(), repr=False, compare=False)


@dataclass
class RestorePlan:
    items: list[RestoreItem] = field(default_factory=list)
    offline_roots: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class RestoreConflict:
    folder: str
    sources: list[str]
    targets: list[str]


@dataclass
class RestoreResult:
    restored: int = 0
    bytes: int = 0
    skipped: int = 0
    failed: int = 0
    cancelled: bool = False
    messages: list[str] = field(default_factory=list)


def _snapshot(info) -> tuple:
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def _absolute(path: Path) -> Path:
    path = Path(path)
    if not path.is_absolute() or ".." in path.parts:
        raise ValueError("Paths must be absolute and cannot contain traversal.")
    if any(":" in part or part.rstrip(" .") != part for part in path.parts[1:]):
        raise ValueError("Alternate streams and ambiguous Windows path names are not allowed.")
    return Path(os.path.abspath(path))


def _owner(lib, path: Path) -> tuple[int, Path]:
    path = _absolute(path)
    for row in lib.roots():
        home = Path(row["path"])
        if path == home or home in path.parents:
            return row["id"], home
    raise ValueError("The destination must be inside a registered library folder.")


def _chain(path: Path, *, directory: bool = False) -> None:
    """lstat every existing ancestor; missing descendants are allowed, links are not."""
    for current in reversed((path, *path.parents)):
        try:
            info = recovery._lstat(current)
        except FileNotFoundError:
            continue
        if recovery._link(info):
            raise ValueError(f"Link / junction / reparse point refused: {current}")
        if (current != path or directory) and not stat.S_ISDIR(info.st_mode):
            raise ValueError(f"Not a destination directory: {current}")


def _validate_path(lib, path: Path, *, source: bool = False, directory: bool = False) -> int:
    path = _absolute(path)
    root_id, home = _owner(lib, path)
    if source:
        if config.recovery_dir(home) not in path.parents:
            raise ValueError("The source is not a file inside registered Recovery.")
    elif any(part.casefold() == config.APP_DIR_NAME for part in path.parts):
        raise ValueError("Restoration into .memoria is not allowed.")
    if path == home and not directory:
        raise ValueError("A restored file cannot replace its registered root.")
    _chain(path, directory=directory)
    return root_id


def _root_online(lib, row) -> bool:
    # Unlike roots.check this must not update online flags or acquire/create locks.
    home = Path(row["path"])
    try:
        _chain(home, directory=True)
        info = recovery._lstat(home)
        marker = config.app_dir(home) / roots.MARKER
        _chain(marker)
        return stat.S_ISDIR(info.st_mode) and stat.S_ISREG(recovery._lstat(marker).st_mode)
    except (OSError, ValueError):
        return False


def _journal(lib):
    destinations = {}
    for row in lib.db.execute(
            "SELECT o.*,b.kind AS batch_kind FROM operations o JOIN batches b ON b.id=o.batch_id "
            "WHERE o.dst IS NOT NULL OR o.dst_key IS NOT NULL"):
        try:
            path = actions._operation_path(lib, row, "dst")
            destinations.setdefault(recovery._key(_absolute(path)), []).append(row)
        except (ValueError, OSError, TypeError):
            continue
    return destinations


def _layout(root_id: int, relative: Path):
    parts = relative.parts
    group = f"{root_id}:{parts[0]}" if len(parts) > 1 else f"{root_id}:<Recovery root>"
    inside = Path(*parts[1:]) if len(parts) > 1 else relative
    legacy = _LEGACY_SESSION.fullmatch(parts[0]) if len(parts) > 1 else None
    known = len(parts) > 1 and (_BATCH.fullmatch(parts[0]) is not None or legacy is not None)
    if known:
        try:
            timestamp = legacy[1].replace("_", "-") if legacy else parts[0][:15]
            datetime.strptime(timestamp, "%Y%m%d-%H%M%S")
        except ValueError:
            known = False
    return group, str(inside), known


def preview(lib) -> RestorePlan:
    """Inventory all reachable Recovery roots without hashing, decoding or mutation."""
    plan = RestorePlan()
    destinations = _journal(lib)
    for row in lib.roots():
        if not _root_online(lib, row):
            plan.offline_roots.append(f"{row['label']}: {row['path']}")
            continue
        home = Path(row["path"])
        report = recovery.RootAccounting(row["id"], row["label"], config.recovery_dir(home))
        for path, _ in recovery._walk(report, home, set(), set()):
            try:
                info = recovery._lstat(path)
                _validate_path(lib, path, source=True)
                if recovery._link(info) or not stat.S_ISREG(info.st_mode):
                    raise ValueError("Recovery source changed to a non-regular file.")
                group, relative, known = _layout(row["id"], path.relative_to(report.path))
                item = RestoreItem(path, None, row["id"], None, None, info.st_size, info.st_mtime,
                                   "inferred", group, relative, _snapshot=_snapshot(info))
                matches = destinations.get(recovery._key(path), [])
                active = [op for op in matches if op["status"] not in ("undone", "purged", "failed", "skipped")]
                if len(active) == 1:
                    op = active[0]
                    item.operation_id, item.batch_id = op["id"], op["batch_id"]
                    item.provenance = "history"
                    if op["batch_kind"] == "recovery_import":
                        try:
                            adoption = json.loads(op["reason"])
                            item.provenance = adoption["provenance"]
                            item.mapping_group = adoption["mapping_group"]
                            item.relative_path = adoption["relative_path"]
                        except (ValueError, TypeError, KeyError):
                            item.issue = "The Recovery adoption record is unreadable."
                    try:
                        item.target = actions._operation_path(lib, op, "src")
                    except (ValueError, OSError) as error:
                        item.issue = f"Invalid historical destination: {error}"
                    if op["op"] != "recycle" or op["status"] != "done":
                        item.issue = f"Journal operation is {op['op']} / {op['status']}; repair or review it first."
                    elif op["size"] is not None and op["size"] != info.st_size:
                        item.issue = "Recovery file size changed from its journal record."
                elif matches:
                    item.issue = "Ambiguous or inactive journal destination; manual journal review required."
                elif known and not any(token in path.name.casefold()
                                       for token in (".memoria-tmp", ".memoria-undo-", ".memoria-restore-")):
                    item.target = home / relative
                else:
                    item.issue = _MAPPING
                if item.target is not None:
                    try:
                        _validate_path(lib, item.target)
                    except (ValueError, OSError) as error:
                        item.issue = str(error)
                plan.items.append(item)
            except (OSError, ValueError) as error:
                plan.errors.append(f"{path}: {error}")
        plan.errors.extend(report.samples)
    plan.items.sort(key=lambda item: recovery._key(item.source))
    for unit in _units(lib, plan.items):
        ids = {item.operation_id for item in unit}
        for item in unit:
            if item.operation_id is None:
                continue
            op = lib.db.execute("SELECT * FROM operations WHERE id=?", (item.operation_id,)).fetchone()
            if op and op["asset_group"]:
                required = {row[0] for row in lib.db.execute(
                    "SELECT id FROM operations WHERE batch_id=? AND asset_group=? AND status!='undone'",
                    (op["batch_id"], op["asset_group"]))}
                if not required <= ids:
                    item.issue = "The linked Recovery group is incomplete; review its missing components."
        if any(item.issue or item.target is None for item in unit):
            for item in unit:
                if not item.issue:
                    item.issue = "A linked component needs review; the whole group stays in Recovery."
    return plan


def map_destination(lib, plan: RestorePlan, mapping_group: str, destination_folder: Path) -> RestorePlan:
    """Map one unlogged container's relative paths beneath an explicitly chosen base."""
    base = _absolute(Path(destination_folder))
    _validate_path(lib, base, directory=True)
    selected = [item for item in plan.items if item.mapping_group == mapping_group]
    if not selected or any(item.operation_id is not None for item in selected):
        raise ValueError("Choose an unlogged Recovery group; historical destinations cannot be remapped.")
    updated = []
    for item in plan.items:
        if item.mapping_group != mapping_group:
            updated.append(item)
            continue
        if item.issue not in ("", _MAPPING, "A linked component needs review; the whole group stays in Recovery."):
            raise ValueError(item.issue)
        relative = Path(item.relative_path)
        if relative.is_absolute() or relative.drive or ".." in relative.parts:
            raise ValueError("The stored relative path contains traversal.")
        target = base / relative
        _validate_path(lib, target)
        updated.append(replace(item, target=target, provenance="manual", issue=""))
    return RestorePlan(updated, list(plan.offline_roots), list(plan.errors))


def _units(lib, items: list[RestoreItem]) -> list[list[RestoreItem]]:
    result, groups, unlogged = [], {}, {}
    for item in items:
        if item.operation_id is not None:
            op = lib.db.execute("SELECT batch_id,asset_group FROM operations WHERE id=?",
                                (item.operation_id,)).fetchone()
            key = (op["batch_id"], op["asset_group"]) if op and op["asset_group"] else None
            if key is not None:
                if key not in groups:
                    groups[key] = []
                    result.append(groups[key])
                groups[key].append(item)
            else:
                result.append([item])
        else:
            key = (recovery._key(item.source.parent), assets._stem(Path(item.relative_path).name).casefold())
            unlogged.setdefault(key, []).append(item)
    for group in unlogged.values():
        rows = [{"id": n, "kind": config.kind_for_ext(item.source.suffix.lower()),
                 "ext": item.source.suffix.lower()} for n, item in enumerate(group)]
        members = {row["id"] for row in assets._components(rows)}
        if members:
            result.append([item for n, item in enumerate(group) if n in members])
        result.extend([item] for n, item in enumerate(group) if n not in members)
    return result


def _check_item(lib, item: RestoreItem, target: Path):
    if _validate_path(lib, item.source, source=True) != item.root_id:
        raise ValueError("The Recovery root changed after review.")
    destination_root = _validate_path(lib, target)
    roots.check(lib, 1)
    roots.check(lib, item.root_id)
    if destination_root != item.root_id:
        roots.check(lib, destination_root)
    info = recovery._lstat(item.source)
    if (recovery._link(info) or not stat.S_ISREG(info.st_mode)
            or not item._snapshot or _snapshot(info) != item._snapshot):
        raise ValueError(f"{item.source.name} changed after preview; left in Recovery.")
    if recovery._key(item.source) == recovery._key(target):
        raise ValueError("A Recovery file cannot be its own destination.")
    if item.operation_id is not None:
        op = lib.db.execute("SELECT * FROM operations WHERE id=?", (item.operation_id,)).fetchone()
        if (op is None or op["op"] != "recycle" or op["status"] not in ("done", "undo_pending")
                or actions._operation_path(lib, op, "dst") != item.source
                or actions._operation_path(lib, op, "src") != item.target):
            raise ValueError("The selected Recovery journal entry changed after preview.")


def _fingerprint(path: Path, progress: Progress) -> str:
    before = recovery._lstat(path)
    if recovery._link(before) or not stat.S_ISREG(before.st_mode):
        raise ValueError("A link or non-regular file cannot be restored.")
    digest = xxhash.xxh3_128()
    with open(L(path), "rb") as stream:
        # Windows fstat/lstat expose different ctime semantics on some Python builds.
        if _snapshot(os.fstat(stream.fileno()))[:4] != _snapshot(before)[:4]:
            raise ValueError("Recovery source changed while opening it.")
        while True:
            progress.check()
            block = stream.read(4 * 1024 * 1024)
            if not block:
                break
            digest.update(block)
    if _snapshot(recovery._lstat(path)) != _snapshot(before):
        raise ValueError("Recovery source changed while verifying it.")
    return digest.hexdigest()


def _publish(source: Path, target: Path):
    if os.name == "nt":
        os.rename(L(source), L(target))  # Windows rename is atomic and refuses existing targets.
    else:
        os.link(source, target, follow_symlinks=False)  # Atomic no-replace on POSIX too.
        os.unlink(source)


def _move(lib, source: Path, target: Path, progress: Progress, *, rollback: bool = False):
    _validate_path(lib, source, source=not rollback)
    _validate_path(lib, target, source=rollback)
    os.makedirs(L(target.parent), exist_ok=True)
    _chain(target)
    progress.check()
    try:
        _publish(source, target)
        return
    except OSError as error:
        if error.errno != errno.EXDEV and getattr(error, "winerror", None) != 17:
            raise
    # A mapped destination may be on another registered drive. Never use a shared
    # temporary name or delete an existing target, including after a publication race.
    temporary = target.with_name(target.name + ".memoria-restore-" + uuid.uuid4().hex)
    before = _snapshot(recovery._lstat(source))
    temporary_identity = None
    try:
        with open(L(source), "rb") as reader, open(L(temporary), "xb") as writer:
            temporary_identity = _snapshot(os.fstat(writer.fileno()))[:2]
            if _snapshot(os.fstat(reader.fileno()))[:4] != before[:4]:
                raise OSError("Recovery source changed while opening a cross-drive copy.")
            digest = xxhash.xxh3_128()
            while True:
                progress.check()
                block = reader.read(4 * 1024 * 1024)
                if not block:
                    break
                writer.write(block)
                digest.update(block)
            writer.flush()
            os.fsync(writer.fileno())
        if _snapshot(recovery._lstat(source)) != before or _fingerprint(temporary, progress) != digest.hexdigest():
            raise OSError("Cross-drive restoration verification failed; Recovery source retained.")
        shutil.copystat(L(source), L(temporary), follow_symlinks=False)
        _chain(target)
        progress.check()
        _publish(temporary, target)
        if _snapshot(recovery._lstat(source)) != before:
            raise OSError("Recovery source changed during publication; both copies retained.")
        os.unlink(L(source))
    finally:
        if os.path.lexists(L(temporary)):
            info = recovery._lstat(temporary)
            if not recovery._link(info) and _snapshot(info)[:2] == temporary_identity:
                os.unlink(L(temporary))


def _rollback(lib, op, intent):
    """Compensate only attributable publications, never foreign late collisions."""
    source = actions._operation_path(lib, op, "dst")
    target = actions._intent_path(lib, intent, "target")
    _validate_path(lib, source, source=True)
    _validate_path(lib, target)
    lib.check_path(source)
    lib.check_path(target)
    if os.path.lexists(L(source)):
        info = recovery._lstat(source)
        identity = [info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns]
        if identity != intent["identity"] or _fingerprint(source, Progress()) != intent["hash"]:
            raise OSError("Recovery source changed during rollback; both locations left untouched.")
        return  # This component never left Recovery; a target could belong to someone else.
    if not os.path.lexists(L(target)) or _fingerprint(target, Progress()) != intent["hash"]:
        raise OSError("Published restoration cannot be identified; retained journal needs review.")
    info = recovery._lstat(target)
    identity = [info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns]
    if info.st_dev == intent["identity"][0] and identity != intent["identity"]:
        raise OSError("Restored file identity changed; no file was moved during rollback.")
    _move(lib, target, source, Progress(), rollback=True)
    actions._forward_catalogue(lib, op, target, source)


def _adopt(lib, unit: list[RestoreItem], progress: Progress):
    digests = []
    for item in unit:
        _check_item(lib, item, item.target)
        digests.append(_fingerprint(item.source, progress))
    progress.check()
    batch_id = datetime.now().strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6]
    token = "recovery-import-" + uuid.uuid4().hex
    adopted = []
    with lib.transaction() as db:
        for item in unit:
            if db.execute("SELECT 1 FROM operations WHERE dst_key=? COLLATE NOCASE OR dst=? COLLATE NOCASE LIMIT 1",
                          (lib.rel(item.source, resolve=False), str(item.source))).fetchone():
                raise ValueError("A Recovery journal entry appeared after preview; preview again before restoring.")
        db.execute("INSERT INTO batches(id,created_at,kind,title,status,files,bytes) "
                   "VALUES (?,?,'recovery_import','Adopt existing Recovery files for reviewed restoration',"
                   "'applied',?,?)", (batch_id, actions._now(), len(unit), sum(item.size for item in unit)))
        for seq, (item, digest) in enumerate(zip(unit, digests)):
            reason = json.dumps({"adoption": True, "provenance": item.provenance,
                                 "mapping_group": item.mapping_group, "relative_path": item.relative_path})
            op_id = actions._log(lib, batch_id, seq, actions.Action(
                "recycle", str(item.target), size=item.size, hash=digest, reason=reason,
                asset_group=token), item.source, "done")
            adopted.append(replace(item, operation_id=op_id, batch_id=batch_id))
    return adopted


def _check_unlogged_membership(unit):
    if not any(item.provenance in ("inferred", "manual") for item in unit):
        return
    expected = {recovery._key(item.source) for item in unit}
    for folder, stem in {(item.source.parent, assets._stem(item.source.name).casefold()) for item in unit}:
        rows = []
        with os.scandir(L(folder)) as entries:
            for entry in entries:
                if assets._stem(entry.name).casefold() != stem:
                    continue
                path = folder / entry.name
                info = recovery._lstat(path)
                if recovery._link(info) or not stat.S_ISREG(info.st_mode):
                    raise ValueError("A potential linked Recovery component is not a regular file.")
                rows.append({"id": len(rows), "path": path, "ext": path.suffix.lower(),
                             "kind": config.kind_for_ext(path.suffix.lower())})
        if any(recovery._key(row["path"]) not in expected for row in assets._components(rows)):
            raise ValueError("Linked Recovery contents changed after review; preview the complete group again.")


def _occupied(lib, path: Path) -> bool:
    return os.path.lexists(L(path)) or lib.file_by_rel(lib.rel(path, resolve=False)) is not None


def _targets(lib, unit: list[RestoreItem], numbered: bool) -> list[Path]:
    proposed = [item.target for item in unit]
    if not numbered:
        return proposed
    for number in range(2, 10_000):
        result = []
        for path in proposed:
            stem = assets._stem(path.name)
            result.append(path.with_name(f"{stem} ({number}){path.name[len(stem):]}"))
        if all(not _occupied(lib, path) for path in result):
            return result
    raise FileExistsError("No unused common numbered name is available.")


def _restore_unit(lib, unit, progress, resolve_conflict):
    decision = None
    for attempt in range(100):
        progress.check()
        _check_unlogged_membership(unit)
        targets = _targets(lib, unit, decision == "rename")
        if any(_occupied(lib, path) for path in targets):
            if len({recovery._key(path.parent) for path in targets}) != 1:
                raise ValueError("Linked components have different destination folders; review required.")
            if decision is None:
                decision = resolve_conflict(RestoreConflict(
                    str(targets[0].parent), [str(item.source) for item in unit],
                    [str(path) for path in targets])) if resolve_conflict else "skip"
            progress.check()
            if decision == "cancel":
                raise Cancelled()
            if decision == "skip":
                return None
            if decision != "rename":
                raise ValueError("Conflict resolver must return rename, skip or cancel.")
            targets = _targets(lib, unit, True)
        for item, target in zip(unit, targets):
            _check_item(lib, item, target)
        if unit[0].operation_id is None:
            unit = _adopt(lib, unit, progress)
        by_id = {item.operation_id: item for item in unit}
        def validate(op, source, target):
            _check_item(lib, by_id[op["id"]], target)
            if _occupied(lib, target):
                raise FileExistsError(str(target))
        try:
            return actions.undo_recovery(
                lib, list(by_id), targets, progress,
                validate=validate,
                move=lambda source, target: _move(lib, source, target, progress),
                fingerprint=lambda path: _fingerprint(path, progress))
        except FileExistsError:
            # A late collision is also a UI decision. A compensated group may have
            # new ctimes, but its source identities and fingerprints must still match.
            refreshed = []
            for item in unit:
                op = lib.db.execute("SELECT * FROM operations WHERE id=?", (item.operation_id,)).fetchone()
                info = recovery._lstat(item.source)
                if (op["status"] != "done" or _snapshot(info)[:4] != item._snapshot[:4]
                        or op["hash"] and _fingerprint(item.source, progress) != op["hash"]):
                    raise ValueError("A late collision could not be safely retried; review retained Recovery.")
                refreshed.append(replace(item, _snapshot=_snapshot(info)))
            unit = refreshed
    raise OSError("Destination kept changing; Recovery files were left for a later retry.")


def execute(lib, plan: RestorePlan, progress: Progress | None = None,
            resolve_conflict: Callable[[RestoreConflict], str] | None = None) -> RestoreResult:
    """Execute an explicitly confirmed plan, requesting a decision per conflicting unit.

    The callback owns folder/all-remaining policy caching. It must observe the supplied
    Progress's cancellation event while waiting on UI. Missing callbacks leave conflicts
    in Recovery. A subsequent preview includes skipped and interrupted adoption records.
    """
    progress = progress or Progress()
    result = RestoreResult(messages=list(plan.errors))
    result.messages.extend(f"Offline root not restored: {name}" for name in plan.offline_roots)
    units = _units(lib, plan.items)
    order = {row["id"]: (row["created_at"], row["batch_order"], row["seq"]) for row in lib.db.execute(
        "SELECT o.id,o.seq,b.created_at,b.rowid AS batch_order FROM operations o JOIN batches b ON b.id=o.batch_id")}
    units.sort(key=lambda unit: max((order.get(item.operation_id, ("", 0, 0)) for item in unit)), reverse=True)
    completed = 0
    try:
        for unit in units:
            progress.update(completed, len(plan.items), f"Restoring Recovery… {completed:,} of {len(plan.items):,}")
            if any(item.target is None or item.issue for item in unit):
                result.skipped += len(unit)
                result.messages.extend(f"Left in Recovery: {item.source}: {item.issue or 'Unmapped destination'}"
                                       for item in unit)
                completed += len(unit)
                continue
            try:
                for item in unit:
                    _check_item(lib, item, item.target)
                undone = _restore_unit(lib, unit, progress, resolve_conflict)
                if undone is None:
                    result.skipped += len(unit)
                    result.messages.extend(f"Left in Recovery after conflict: {item.source}" for item in unit)
                else:
                    result.restored += undone.done
                    result.bytes += sum(item.size for item in unit)
                    result.messages.extend(undone.messages)
            except Cancelled:
                raise
            except (FileNotFoundError, ValueError, LibraryUnavailable) as error:
                result.skipped += len(unit)
                result.messages.append(f"Left in Recovery ({', '.join(item.source.name for item in unit)}): {error}")
            except Exception as error:
                result.failed += len(unit)
                result.messages.append(f"Could not restore {unit[0].source}: {error}")
            completed += len(unit)
    except Cancelled:
        result.cancelled = True
        remaining = len(plan.items) - result.restored - result.skipped - result.failed
        result.skipped += remaining
        result.messages.append(f"Cancelled; {remaining:,} remaining files were not restored.")
    result.cancelled = result.cancelled or progress.cancelled
    return result
