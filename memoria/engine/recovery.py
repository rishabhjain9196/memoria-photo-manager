"""Read-only, no-follow accounting of Recovery, not allocated disk space.

The journal records intent/history; only regular files observed in Recovery contribute
to retained bytes. No originals are read, no hashes are computed and no folders are made.
"""
from __future__ import annotations

import os
import stat
from dataclasses import dataclass, field
from pathlib import Path

from . import config, roots
from .config import longpath as L
from .db import LibraryUnavailable

SAMPLE_LIMIT = 20
INTERRUPTED = {"pending", "publishing", "published", "undo_pending"}
MOVED = {"done", "published", "undo_pending", "undone", "purged"}
RECORDED = MOVED | INTERRUPTED


@dataclass
class BatchAccounting:
    id: str
    title: str
    created_at: str
    cleanup: bool = False
    recorded_files: int = 0
    recorded_bytes: int = 0
    moved_files: int = 0
    moved_bytes: int = 0
    files: int = 0
    bytes: int = 0
    missing_files: int = 0
    missing_bytes: int = 0
    changed_files: int = 0
    uncertain_files: int = 0
    unexpected_files: int = 0


@dataclass
class RootAccounting:
    id: int
    label: str
    path: Path
    online: bool = True
    complete: bool = True
    files: int = 0
    bytes: int = 0
    untracked_files: int = 0
    untracked_bytes: int = 0
    skipped_links: int = 0
    errors: int = 0
    samples: list[str] = field(default_factory=list)

    def note(self, message: str) -> None:
        if len(self.samples) < SAMPLE_LIMIT:
            self.samples.append(message)


@dataclass
class RecoveryAccounting:
    roots: list[RootAccounting] = field(default_factory=list)
    batches: dict[str, BatchAccounting] = field(default_factory=dict)
    latest_id: str | None = None
    journal_complete: bool = True
    interrupted_ops: int = 0
    pending_merges: int = 0

    @property
    def files(self) -> int:
        return sum(root.files for root in self.roots)

    @property
    def bytes(self) -> int:
        return sum(root.bytes for root in self.roots)

    @property
    def complete(self) -> bool:
        return self.journal_complete and all(root.online and root.complete for root in self.roots)

    @property
    def latest(self) -> BatchAccounting | None:
        return self.batches.get(self.latest_id)

    @property
    def older_bytes(self) -> int:
        return sum(batch.bytes for batch in self.batches.values() if batch.cleanup and batch.id != self.latest_id)

    @property
    def other_bytes(self) -> int:
        return sum(batch.bytes for batch in self.batches.values() if not batch.cleanup)

    @property
    def untracked_files(self) -> int:
        return sum(root.untracked_files for root in self.roots)

    @property
    def untracked_bytes(self) -> int:
        return sum(root.untracked_bytes for root in self.roots)

    @property
    def needs_inspection(self) -> bool:
        return bool(not self.complete or self.untracked_files or self.interrupted_ops or self.pending_merges
                    or any(batch.missing_files or batch.changed_files or batch.uncertain_files
                           or batch.unexpected_files for batch in self.batches.values()))

    @property
    def safe_to_empty(self) -> bool:
        # This is only a UI gate, not authority to delete. Existing engine guards still apply.
        return bool(self.files and not self.needs_inspection)


def _key(path: Path) -> str:
    return os.path.normcase(os.path.abspath(path))


def _link(info) -> bool:
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def _lstat(path: Path):
    return os.lstat(L(path))


def inspection_path(lib, source: int) -> Path:
    """Return an existing, non-linked Recovery location; never create one."""
    roots.check(lib, 1)
    roots.check(lib, source)
    home = lib.abspath(roots.key_for(source))
    folder = config.recovery_dir(home)
    for path in (home, *[home / Path(*folder.relative_to(home).parts[:i])
                        for i in range(1, len(folder.relative_to(home).parts) + 1)]):
        try:
            info = _lstat(path)
        except FileNotFoundError as error:
            raise ValueError("No Recovery folder exists at this location. Nothing was created.") from error
        if _link(info) or not stat.S_ISDIR(info.st_mode):
            raise ValueError("Recovery contains a link / junction or non-directory. Inspect its parent locally.")
    return folder


def _walk(root: RootAccounting, home: Path, blocked: set[str], directories: set[str]):
    """Yield regular files only; any inaccessible subtree stays explicitly unknown."""
    def block(path, message, *, link=False):
        root.complete = False
        root.skipped_links += int(link)
        root.errors += int(not link)
        blocked.add(_key(path))
        root.note(f"{message}: {path}")

    # Checking every ancestor below the registered home also catches a replaced .memoria.
    try:
        info = _lstat(home)
    except OSError as error:
        block(home, f"Unreadable ({error})")
        return
    if _link(info):
        block(home, "Link / junction / reparse point not followed", link=True)
        return
    path = home
    for part in root.path.relative_to(home).parts:
        path /= part
        try:
            info = _lstat(path)
        except FileNotFoundError:
            return
        except OSError as error:
            block(path, f"Unreadable ({error})")
            return
        if _link(info):
            block(path, "Link / junction / reparse point not followed", link=True)
            return
        if not stat.S_ISDIR(info.st_mode):
            block(path, "Expected Recovery directory")
            return

    pending = [root.path]
    while pending:
        directory = pending.pop()
        try:
            # Recheck queued directories: they may have changed since being discovered.
            info = _lstat(directory)
            if _link(info) or not stat.S_ISDIR(info.st_mode):
                block(directory, "Changed directory / link not followed", link=_link(info))
                continue
            directories.add(_key(directory))
            with os.scandir(L(directory)) as entries:
                for entry in entries:
                    path = directory / entry.name
                    try:
                        info = _lstat(path)
                    except OSError as error:
                        block(path, f"Cannot measure ({error})")
                        continue
                    if _link(info):
                        block(path, "Link / junction / reparse point not followed", link=True)
                    elif stat.S_ISDIR(info.st_mode):
                        pending.append(path)
                    elif stat.S_ISREG(info.st_mode):
                        yield path, info.st_size
                    else:
                        block(path, "Non-regular item not measured")
        except OSError as error:
            block(directory, f"Cannot list ({error})")


def inspect(lib) -> RecoveryAccounting:
    """Return one all-root snapshot, with bounded local inspection samples per root.

    Sizes are logical file lengths (hard-linked entries count per path), not disk
    allocation or savings. Size equality does not prove content equality. A changing
    filesystem cannot provide an atomic snapshot; refresh after operations finish.
    """
    from .actions import _operation_path

    # The catalogue home is required even if all the retained files are on other roots.
    roots.check(lib, 1)
    report = RecoveryAccounting()
    folders = dict(lib.recovery_folders())
    homes = {}
    for source in lib.roots():
        root = RootAccounting(source["id"], source["label"], folders[source["id"]])
        homes[root.id] = Path(source["path"])
        try:
            if root.id != 1:
                roots.check(lib, root.id)
        except LibraryUnavailable as error:
            root.online = root.complete = False
            root.note(f"Offline / unavailable: {error}")
        report.roots.append(root)

    report.interrupted_ops = lib.db.execute(
        "SELECT COUNT(*) FROM operations WHERE status IN ('pending','publishing','published','undo_pending')"
    ).fetchone()[0]
    report.pending_merges = lib.db.execute(
        "SELECT COUNT(*) FROM operations WHERE op='recycle' AND status='done' "
        "AND merge_target IS NOT NULL AND merge_complete=0").fetchone()[0]
    destinations = {}
    # Exports outside Recovery are irrelevant, even when newer than the last cleanup.
    needle = f"%{config.APP_DIR_NAME}\\{config.RECOVERY_DIR_NAME}\\%"
    rows = lib.db.execute(
        "SELECT o.*,b.title,b.created_at,b.kind AS batch_kind FROM operations o JOIN batches b ON b.id=o.batch_id "
        "WHERE o.op='recycle' OR (o.op IN ('move','copy','create') AND "
        "replace(COALESCE(o.dst_key,o.dst,''),'/','\\') LIKE ?) "
        "ORDER BY b.created_at DESC,b.rowid DESC,o.id DESC", (needle,))
    for op in rows:
        batch = report.batches.setdefault(op["batch_id"], BatchAccounting(
            op["batch_id"], op["title"], op["created_at"]))
        cleanup = op["op"] == "recycle" and op["status"] in RECORDED and op["batch_kind"] != "recovery_import"
        if cleanup:
            batch.cleanup = True
            batch.recorded_files += 1
            batch.recorded_bytes += op["size"] or 0
            if op["status"] in MOVED:
                batch.moved_files += 1
                batch.moved_bytes += op["size"] or 0
            if report.latest_id is None:
                report.latest_id = batch.id
        try:
            destination = _operation_path(lib, op, "dst")
            if destination is not None:
                destination = Path(os.path.abspath(destination))
            owner = next((root for root in report.roots
                          if destination is not None and root.path in destination.parents), None)
        except (ValueError, OSError):
            owner = None
        if owner is None:
            if cleanup:
                batch.uncertain_files += 1
                report.journal_complete = False
            continue
        destinations.setdefault(_key(destination), []).append((op, owner, batch))

    seen = set()
    blocked = set()
    directories = set()
    for root in report.roots:
        if not root.online:
            blocked.add(_key(root.path))
            continue
        for path, size in _walk(root, homes[root.id], blocked, directories):
            root.files += 1
            root.bytes += size
            key = _key(path)
            seen.add(key)
            matches = destinations.get(key, [])
            # Reused destinations cannot be attributed confidently to either operation.
            active = [match for match in matches if match[0]["status"] in RECORDED - {"undone", "purged"}]
            match = active[0] if len(active) == 1 else matches[0] if len(matches) == 1 else None
            if match is None:
                root.untracked_files += 1
                root.untracked_bytes += size
                root.note(f"{'Ambiguous journal destination' if matches else 'Untracked / holding file'}: {path}")
                for _, _, batch in matches:
                    batch.uncertain_files += 1
                continue
            op, _, batch = match
            batch.files += 1
            batch.bytes += size
            if op["size"] is not None and size != op["size"]:
                batch.changed_files += 1
                root.note(f"Size changed (recorded {op['size']:,}; now {size:,} bytes): {path}")
            if op["status"] not in {"done", "published"}:
                batch.unexpected_files += 1
            if op["status"] != "done":
                root.note(f"Inspect journal state '{op['status']}': {path}")
            relative = path.relative_to(root.path)
            if (op["batch_kind"] == "recovery_import" or op["op"] != "recycle"
                    or len(relative.parts) < 2 or relative.parts[0] != batch.id):
                batch.unexpected_files += 1
                root.note(f"Journaled file outside the normal cleanup layout; inspect before emptying: {path}")

    for key, matches in destinations.items():
        if key in seen:
            continue
        unknown = any(str(parent) in blocked for parent in (Path(key), *Path(key).parents))
        for op, root, batch in matches:
            if op["status"] not in {"done", *INTERRUPTED}:
                continue
            if key in directories:
                batch.changed_files += 1
                root.note(f"Recorded file is now a directory: {key}")
            elif unknown or op["status"] != "done":
                batch.uncertain_files += 1
            else:
                batch.missing_files += 1
                batch.missing_bytes += op["size"] or 0
                root.note(f"Recorded destination missing ({op['size'] or 0:,} recorded bytes): {key}")
    return report
