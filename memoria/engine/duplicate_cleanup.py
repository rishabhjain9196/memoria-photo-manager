"""Folder collections and conservative exact-content bulk cleanup.

Planning does not scan or change the catalogue. Linked components are fingerprinted
as complete assets; execution must still use the shared, freshly verifying action
engine, with companion review enabled. Unmatched linked parts require a separate,
explicitly acknowledged review; they are never included by default.
"""
from __future__ import annotations

import hashlib
import json
import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

import xxhash

from . import assets, config, duplicates, roots
from .actions import Action
from .db import Library
from .hashing import CHUNK
from .progress import Progress


def _ordered_keys(values):
    """Byte-radix ordering keeps collection construction linear in path text."""
    pending = [(0, [(value.encode("utf-8"), value) for value in values])]
    result = []
    while pending:
        offset, items = pending.pop()
        if len(items) == 1:
            result.append(items[0][1])
            continue
        buckets = defaultdict(list)
        for encoded, value in items:
            if offset == len(encoded):
                result.append(value)
            else:
                buckets[encoded[offset]].append((encoded, value))
        pending.extend((offset + 1, buckets[key]) for key in sorted(buckets, reverse=True))
    return result


@dataclass
class FolderCollection:
    folders: tuple[str, ...]
    groups: list[duplicates.DuplicateGroup]
    id: str = field(init=False)

    def __post_init__(self):
        names = {}
        for path in self.folders:
            key = path.casefold()
            names[key] = min(path, names.get(key, path))
        keys = _ordered_keys(names)
        self.folders = tuple(names[key] for key in keys)
        self.id = "collection:" + hashlib.sha256(
            json.dumps(keys, ensure_ascii=True, separators=(",", ":")).encode("ascii")).hexdigest()

    @property
    def wasted(self) -> int:
        return sum(group.wasted for group in self.groups)


def group_by_folders(groups: list[duplicates.DuplicateGroup]) -> list[FolderCollection]:
    """Collect content sets with the same containing directories, not folder pairs.

    Same-folder repeats form a one-directory collection. Membership says nothing
    about unique contents in those directories. Work is linear in input path text,
    plus sorting the resulting collections by reclaimable bytes.
    """
    grouped, names = {}, {}
    for group in groups:
        directories = set()
        for row in group.files:
            path = row["folder"]
            key = path.casefold()
            directories.add(key)
            names[key] = min(path, names.get(key, path))
        grouped.setdefault(frozenset(directories), []).append(group)
    result = [FolderCollection(tuple(names[key] for key in paths), members)
              for paths, members in grouped.items()]
    return sorted(result, key=lambda collection: collection.wasted, reverse=True)


@dataclass
class CleanupPlan:
    actions: list[Action]
    groups: int = 0
    protected_groups: int = 0
    linked_skipped: int = 0
    review_parts: list[dict] = field(default_factory=list)
    linked_reasons: list[str] = field(default_factory=list)


_SNAPSHOT = ("id", "rel_path", "folder", "name", "size", "mtime")
_IDENTITY = ("ext", "kind", "root_id")
_STALE = "Duplicate contents changed since review. Find duplicates again."


def _same_snapshot(reviewed, current):
    return (all(reviewed[key] == current[key] for key in _SNAPSHOT)
            and all(key not in reviewed or reviewed[key] == current[key] for key in _IDENTITY)
            and (not current["chash"] or not reviewed.get("chash")
                 or current["chash"] == reviewed["chash"]))


def _validate_rows(lib, rows, progress):
    identifiers = list(rows)
    for offset in range(0, len(identifiers), 400):
        progress.check()
        chunk = identifiers[offset:offset + 400]
        current = {row["id"]: row for row in lib.db.execute(
            f"SELECT * FROM files WHERE id IN ({','.join('?' for _ in chunk)})", chunk)}
        if any(fid not in current or not _same_snapshot(rows[fid], current[fid]) for fid in chunk):
            raise ValueError(_STALE)


def _choices(lib, report, file_choices, folder_choices, progress):
    protected, recommended = set(), set()
    kept = duplicates.kept_choices(lib)
    groups = {group.hash: group for group in report.groups}
    matches = {match.id: match for match in report.folders}
    if not file_choices.keys() <= groups.keys() or not folder_choices.keys() <= matches.keys():
        raise ValueError("Duplicate choices no longer match this review. Find duplicates again.")
    for group in report.groups:
        progress.check()
        ids = {row["id"] for row in group.files}
        if duplicates.file_review_key(group) in kept:
            protected.update(ids)
        if group.hash in file_choices:
            chosen = file_choices[group.hash]
            if not chosen <= ids:
                raise ValueError("File choices no longer match this review. Find duplicates again.")
            protected.update(ids - chosen)
    # A saved loose review can protect only a subset of a full content group.
    if any(key.startswith("file:") for key in kept):
        for group in report.loose_groups():
            progress.check()
            if duplicates.file_review_key(group) in kept:
                protected.update(row["id"] for row in group.files)
    for match in report.folders:
        progress.check()
        members = {folder.path.casefold(): folder.path for folder in match.folders}
        complete = all(path in report.folder_files and path in report.folder_signatures
                       for path in members.values())
        saved = complete and report.folder_review_key(match) in kept
        explicit = match.id in folder_choices
        chosen = {path.casefold() for path in folder_choices.get(match.id, ())}
        if explicit and (not chosen <= members.keys()
                         or any(path not in report.folder_files for path in members.values())):
            raise ValueError("Folder choices no longer match this review. Find duplicates again.")
        for key, path in members.items():
            rows = report.folder_files.get(path, ())
            if saved or explicit and key not in chosen:
                protected.update(row["id"] for row in rows)
            if key == match.keeper_path().casefold():
                recommended.update(row["id"] for row in rows)
        if explicit and match.kind == "inside":
            larger = match.folders[1].path
            comparisons = duplicates.folder_comparison(report, match)
            protected.update(row["id"] for item in comparisons if item["folder"].path == larger
                             for row in item["unique"])
    return protected, recommended


def _fingerprint_component(lib, row, progress):
    """Fingerprint a reviewed stat snapshot, cancellably, on a worker."""
    try:
        progress.check()
        path = lib.abspath(row["rel_path"])
        lib.check_path(path)
        before = os.stat(config.longpath(path))
        if before.st_size != row["size"] or before.st_mtime != row["mtime"]:
            return None
        digest = xxhash.xxh3_128()
        with open(config.longpath(path), "rb", buffering=0) as stream:
            buffer = bytearray(CHUNK)
            view = memoryview(buffer)
            while True:
                progress.check()
                count = stream.readinto(buffer)
                if not count:
                    break
                digest.update(view[:count])
        digest = digest.hexdigest()
        progress.check()
        after = os.stat(config.longpath(path))
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            return None
        if row.get("chash") and digest != row["chash"]:
            return None
        return digest
    except OSError:
        return None
    finally:
        lib.close_thread()


def _fingerprints(lib, rows, progress):
    result = {}
    if rows:
        with ThreadPoolExecutor(max_workers=min(config.WORKERS, len(rows))) as pool:
            values = pool.map(lambda row: _fingerprint_component(lib, row, progress), rows.values())
            for index, (fid, digest) in enumerate(zip(rows, values), 1):
                result[fid] = digest
                progress.update(index, len(rows), "Verifying linked cleanup contents")
    return result


def _component_key(row):
    return row["ext"].casefold(), row["size"], row["chash"]


def _linked_units(lib, report, rows, protected, progress):
    units = assets.linked_groups(lib, list(rows.values()))
    frozen = {row["id"] for unit in units for row in unit}
    snapshots = {row["id"]: row for items in report.folder_files.values() for row in items}
    covered_folders = {path.casefold() for path in report.folder_files}
    eligible, skipped, sidecars = [], 0, {}
    for unit in units:
        progress.check()
        members, safe = [], True
        for current in unit:
            fid = current["id"]
            if current["kind"] != "other":
                reviewed = rows.get(fid)
                if reviewed is None or not _same_snapshot(reviewed, current):
                    safe = False
                    break
                members.append({**current, **reviewed})
            else:
                reviewed = snapshots.get(fid)
                in_snapshot = any(parent.casefold() in covered_folders
                                  for parent in duplicates._parents(current["folder"]))
                if ((reviewed is None and in_snapshot)
                        or (reviewed is not None and not _same_snapshot(reviewed, current))):
                    safe = False
                    break
                member = {**current, **(reviewed or {})}
                members.append(member)
        if safe:
            eligible.append(members)
            sidecars.update((row["id"], row) for row in members if row["kind"] == "other")
        elif not protected.intersection(row["id"] for row in unit):
            skipped += 1
    if sidecars:
        values = _fingerprints(lib, sidecars, progress)
        for fid, row in sidecars.items():
            row["chash"] = values[fid]
    complete = defaultdict(list)
    for unit in eligible:
        if any(not row["chash"] for row in unit):
            if not protected.intersection(row["id"] for row in unit):
                skipped += 1
            continue
        complete[tuple(sorted(_component_key(row) for row in unit))].append(unit)
    return complete, frozen, skipped, units


def _prepared(lib, planned, removing, rows, reviewed, original_units, progress):
    _validate_rows(lib, reviewed, progress)
    current_units = assets.linked_groups(lib, list(rows.values()))
    membership = lambda units: {tuple(sorted(row["id"] for row in unit)) for unit in units}
    if membership(current_units) != membership(original_units):
        raise ValueError("Linked contents changed since review. Find duplicates again.")
    progress.check()
    prepared = assets.prepare(lib, planned, "duplicates")
    gone = {os.path.normcase(action.src) for action in prepared.actions}
    if (prepared.extra_files or {action.file_id for action in prepared.actions} != removing
            or any(os.path.normcase(path) in gone for action in prepared.actions for path, _ in action.guards)
            or any(action.merge_into in removing for action in prepared.actions)):
        raise ValueError("Linked duplicate choices conflict. Find duplicates again.")
    progress.check()
    return prepared.actions


def _asset_key(row):
    return row["folder"].lower(), assets._stem(row["name"]).lower()


def _reviewed_membership(snapshots, progress):
    grouped = defaultdict(list)
    for row in snapshots.values():
        progress.check()
        ext = os.path.splitext(row["name"])[1].lower()
        if row["name"].startswith("._") or ext not in config.MEDIA_EXT | assets.SIDECARS:
            continue
        kind = "image" if ext in config.IMAGE_EXT | config.RAW_EXT else "video" if ext in config.VIDEO_EXT else "other"
        grouped[_asset_key(row)].append({**row, "ext": ext, "kind": kind})
    return {key: {row["id"] for row in members} for key, items in grouped.items()
            if (members := assets._components(items))}


def _plan_linked_review(lib, report, selected, rows, protected, recommended, progress):
    """Expand only redundant selected media, then monotonically retain unsafe units."""
    known = {}
    for group in report.groups:
        progress.check()
        for row in group.files:
            snapshot = {**row, "chash": group.hash}
            if row["size"] != group.size or row["id"] in known and known[row["id"]] != snapshot:
                raise ValueError(_STALE)
            known[row["id"]] = snapshot
    snapshots = {row["id"]: row for items in report.folder_files.values() for row in items}
    snapshots.update(known)
    historical = _reviewed_membership(snapshots, progress)
    covered = {path.lower() for path in report.folder_files}

    def rank(row):
        return row["id"] not in recommended, duplicates.keeper_score(row)

    keepers, candidates = set(), set()
    for group in selected:
        progress.check()
        fixed = [row for row in group.files if row["id"] in protected]
        keepers.add(min(fixed or group.files, key=rank)["id"])
        candidates.update(row["id"] for row in group.files if row["id"] not in protected)
    candidates -= keepers
    original_units = assets.linked_groups(lib, list(rows.values()))
    unit_for, units, linked = {}, {}, set()
    for unit in original_units:
        key = tuple(sorted(row["id"] for row in unit))
        units[key] = unit
        linked.add(key)
        unit_for.update((fid, key) for fid in key)
    for fid, row in rows.items():
        if fid not in unit_for:
            unit_for[fid] = (fid,)
            units[(fid,)] = [row]
            if _asset_key(row) in historical:
                linked.add((fid,))
    attempted = {unit_for[fid] for fid in candidates}
    active, blocked, normalized = set(attempted), {}, {}
    locked = protected | keepers

    def retain(key, reason):
        active.discard(key)
        if key in attempted and key in linked:
            blocked.setdefault(key, f"{units[key][0]['rel_path']}: {reason}")

    for key, unit in units.items():
        progress.check()
        if key in active and locked.intersection(key):
            retain(key, "a saved/unchecked component or required surviving copy is protected")
        expected = historical.get(_asset_key(unit[0]), set())
        if not expected <= set(key):
            retain(key, "linked membership changed since the duplicate review")
            continue
        members = []
        for current in unit:
            reviewed = snapshots.get(current["id"])
            in_snapshot = any(parent.lower() in covered for parent in duplicates._parents(current["folder"]))
            if ((reviewed is None and in_snapshot)
                    or (reviewed is not None and not _same_snapshot(reviewed, current))):
                retain(key, "linked contents changed since the duplicate review")
                break
            members.append({**current, **(reviewed or {})})
        else:
            normalized[key] = members

    potential = {row["id"]: row for key in active for row in normalized[key]}
    affected = [group for group in report.groups if any(row["id"] in potential for row in group.files)]
    verifying = {**potential, **{row["id"]: known[row["id"]] for group in affected for row in group.files}}
    # Optional counterpart proofs come only from the same reviewed asset inventory.
    # Names establish membership, never equivalence: every usable hash is read fresh.
    extra_shapes = {(row["ext"].lower(), row["size"]) for fid, row in potential.items() if fid not in known}
    for unit in normalized.values():
        for row in unit:
            if (row["ext"].lower(), row["size"]) in extra_shapes:
                verifying.setdefault(row["id"], row)
    _validate_rows(lib, verifying, progress)
    fingerprints = _fingerprints(lib, verifying, progress)
    for key in list(active):
        if any(not fingerprints.get(fid) for fid in key):
            if key not in linked:
                raise ValueError(_STALE)
            retain(key, "a linked component changed or could not be fingerprinted")
    removing = {fid for key in active for fid in key}

    # An out-of-scope exact video/RAW group can be touched by expansion too. Only
    # decrease removals: retaining one entire source unit can never break an
    # earlier group's surviving-copy invariant.
    for group in affected:
        progress.check()
        if not any(row["id"] in removing for row in group.files):
            continue
        survivors = [row for row in group.files if row["id"] not in removing and fingerprints.get(row["id"])]
        if not survivors:
            survivor = min((row for row in group.files if fingerprints.get(row["id"])), key=rank)
            key = unit_for[survivor["id"]]
            retain(key, "the whole asset must stay to preserve a verified exact-content copy")
            removing.difference_update(key)

    proven = {fid: {**row, "chash": fingerprints[fid]} for fid, row in verifying.items()
              if fingerprints.get(fid)}
    by_component = defaultdict(list)
    for fid, row in proven.items():
        if fid not in removing:
            by_component[_component_key(row)].append(row)
    survivor_for = {}
    for group in affected:
        if any(row["id"] in removing for row in group.files):
            survivor = min((proven[row["id"]] for row in group.files
                            if row["id"] not in removing and row["id"] in proven), key=rank)
            survivor_for.update((row["id"], survivor) for row in group.files if row["id"] in removing)

    planned, parts, reviewed = [], [], {}
    for key, unit in normalized.items():
        progress.check()
        if key not in active:
            continue
        matches = {}
        for current in unit:
            row = proven[current["id"]]
            matches[row["id"]] = survivor_for.get(row["id"])
            if matches[row["id"]] is None:
                equivalents = by_component.get(_component_key(row), ())
                if equivalents:
                    matches[row["id"]] = min(equivalents, key=rank)
        guards = list(dict.fromkeys((str(lib.abspath(keeper["rel_path"])), keeper["chash"])
                                   for keeper in matches.values() if keeper is not None))
        if not guards:
            raise ValueError("No verified surviving copy remains for this linked selection.")
        for current in unit:
            row, keeper = proven[current["id"]], matches[current["id"]]
            reason = (f"Exact duplicate; verified copy kept at {keeper['rel_path']}" if keeper else
                      "Linked component; not proven duplicate / may be unique")
            planned.append(Action(
                op="recycle", src=str(lib.abspath(row["rel_path"])), size=row["size"],
                mtime=row["mtime"], hash=row["chash"], guards=list(guards), reason=reason,
                file_id=row["id"], merge_into=keeper["id"] if keeper else None, companions_locked=True))
            reviewed[row["id"]] = row
            if keeper:
                reviewed[keeper["id"]] = keeper
            if key in linked:
                parts.append({name: row[name] for name in ("id", "rel_path", "size", "kind")} |
                             {"reason": reason, "unmatched": keeper is None})
    prepared = _prepared(lib, planned, removing, rows, reviewed, original_units, progress)
    return CleanupPlan(
        prepared, groups=sum(any(row["id"] in removing for row in group.files) for group in report.groups),
        protected_groups=sum(any(row["id"] in protected for row in group.files) for group in selected),
        linked_skipped=len(blocked), review_parts=parts, linked_reasons=list(blocked.values()))


def plan_cleanup(lib: Library, report: duplicates.DuplicateReport,
                 hashes: set[str] | None = None,
                 file_choices: dict[str, set[int]] | None = None,
                 folder_choices: dict[str, set[str]] | None = None,
                 include_linked: bool = False, progress: Progress | None = None) -> CleanupPlan:
    """Plan redundant exact media copies, always leaving a verified survivor.

    ``None`` scopes to every full report group; an empty set scopes to none.
    Checked choices permit removal; unchecked and saved Keep choices protect
    content, including whole linked units. Protection always wins. The returned
    actions are companion-locked and already prepared for shared confirmation.
    ``include_linked`` is only for a combined explicit review: every unmatched
    ``review_parts`` entry must be shown and acknowledged before execution.
    """
    progress = progress or Progress()
    progress.check()
    available = {group.hash: group for group in report.groups}
    wanted = set(available) if hashes is None else set(hashes)
    if not wanted <= available.keys():
        raise ValueError("Duplicate groups no longer match this review. Find duplicates again.")
    if not wanted:
        return CleanupPlan([])
    selected = [group for group in report.groups if group.hash in wanted]
    rows = {}
    for group in selected:
        progress.check()
        for row in group.files:
            snapshot = {**row, "chash": group.hash}
            if row["size"] != group.size or row["id"] in rows and rows[row["id"]] != snapshot:
                raise ValueError(_STALE)
            rows[row["id"]] = snapshot
    protected, recommended = _choices(lib, report, file_choices or {}, folder_choices or {}, progress)
    _validate_rows(lib, rows, progress)
    for source in {roots.split_key(row["rel_path"])[0] for row in rows.values()}:
        progress.check()
        lib.check_path(lib.abspath(roots.key_for(source)))

    if include_linked:
        return _plan_linked_review(lib, report, selected, rows, protected, recommended, progress)
    equivalent, linked, skipped, original_units = _linked_units(lib, report, rows, protected, progress)
    planned, removing, reviewed_components = [], set(), dict(rows)

    def rank(row):
        return row["id"] not in recommended, duplicates.keeper_score(row)

    def unit_rank(unit):
        media = [row for row in unit if row["kind"] != "other"]
        return (-sum(row["id"] in recommended for row in media),
                min(duplicates.keeper_score(row) for row in media))

    def removal(row, keeper, guards):
        planned.append(Action(
            op="recycle", src=str(lib.abspath(row["rel_path"])), size=row["size"],
            mtime=row["mtime"], hash=row["chash"], guards=list(guards),
            reason=f"Exact duplicate; verified copy kept at {keeper['rel_path']}",
            file_id=row["id"], merge_into=keeper["id"], companions_locked=True))
        removing.add(row["id"])
        reviewed_components[row["id"]] = row
        reviewed_components[keeper["id"]] = keeper

    for units in equivalent.values():
        progress.check()
        retained = [unit for unit in units if protected.intersection(row["id"] for row in unit)]
        if len(units) == 1:
            skipped += not bool(retained)
            continue
        keeper = min(retained or units, key=unit_rank)
        guards = [(str(lib.abspath(row["rel_path"])), row["chash"]) for row in keeper]
        pairs = sorted(keeper, key=lambda row: (_component_key(row), row["id"]))
        for unit in units:
            if unit is keeper or protected.intersection(row["id"] for row in unit):
                continue
            for row, survivor in zip(sorted(unit, key=lambda row: (_component_key(row), row["id"])), pairs):
                removal(row, survivor, guards)

    # All linked members are frozen before ordinary per-hash decisions. In
    # particular, a guard can never be a companion of another removal.
    for group in selected:
        progress.check()
        surviving = [rows[row["id"]] for row in group.files if row["id"] not in removing]
        fixed = [row for row in surviving if row["id"] in protected or row["id"] in linked]
        keeper = min(fixed or surviving, key=rank)
        guards = [(str(lib.abspath(keeper["rel_path"])), group.hash)]
        for row in surviving:
            if row["id"] != keeper["id"] and row["id"] not in protected and row["id"] not in linked:
                removal(row, keeper, guards)

    prepared = _prepared(lib, planned, removing, rows, reviewed_components, original_units, progress)
    return CleanupPlan(
        prepared,
        groups=sum(any(row["id"] in removing for row in group.files) for group in selected),
        protected_groups=sum(any(row["id"] in protected for row in group.files) for group in selected),
        linked_skipped=skipped)
