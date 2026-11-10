"""Reviewable, same-folder companion groups. Detection never changes a file."""
from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field, replace
from pathlib import Path

from . import config
from .db import Library
from .hashing import full_hash

SIDECARS = {".aae", ".xmp"}
_COLUMNS = "id,rel_path,folder,name,ext,kind,size,mtime,chash,root_id"


def _stem(name: str) -> str:
    stem, suffix = os.path.splitext(name)
    if suffix.lower() in SIDECARS and os.path.splitext(stem)[1].lower() in config.MEDIA_EXT:
        stem = os.path.splitext(stem)[0]
    return stem


def _components(rows: list[dict]) -> list[dict]:
    images = [row for row in rows if row["kind"] == "image"]
    videos = [row for row in rows if row["kind"] == "video"]
    sidecars = [row for row in rows if row["ext"].lower() in SIDECARS]
    raw = [row for row in images if row["ext"].lower() in config.RAW_EXT]
    rendered = [row for row in images if row["ext"].lower() in config.IMAGE_EXT]
    if not images or not (videos or sidecars or raw and rendered):
        return []
    return sorted(images + videos + sidecars, key=lambda row: (row["kind"] != "image", row["id"]))


def _index(lib: Library, folders: set[str]) -> dict[tuple[str, str], list[dict]]:
    grouped = {}
    ordered = sorted(folders)
    for offset in range(0, len(ordered), 400):
        chunk = ordered[offset:offset + 400]
        rows = lib.db.execute(f"SELECT {_COLUMNS} FROM files WHERE folder IN ({','.join('?' for _ in chunk)})", chunk)
        for row in rows:
            row = dict(row)
            if row["name"].startswith("._") or row["kind"] == "other" and row["ext"].lower() not in SIDECARS:
                continue
            grouped.setdefault((row["folder"].lower(), _stem(row["name"]).lower()), []).append(row)
    return {key: members for key, rows in grouped.items() if (members := _components(rows))}


@dataclass
class Prepared:
    actions: list
    groups: list[list[dict]]
    extra_files: int
    merges: list[dict] = field(default_factory=list)


def prepare(lib: Library, planned: list, kind: str) -> Prepared:
    """Include reviewed companions, preserving separate copies exported to different albums."""
    from .actions import Action
    rows_by_path = {}
    for action in planned:
        if action.op not in ("copy", "move", "recycle") or not lib.contains(action.src):
            continue
        key = lib.rel(action.src)
        row = lib.file_by_rel(key)
        if row is not None:
            rows_by_path[action.src] = dict(row)
    index = _index(lib, {row["folder"] for row in rows_by_path.values()})
    guards = {os.path.normcase(path) for action in planned for path, _ in action.guards}
    units, order, standalone, groups = {}, [], [], []
    for action in planned:
        row = rows_by_path.get(action.src)
        members = index.get((row["folder"].lower(), _stem(row["name"]).lower())) if row else None
        if not members:
            standalone.append(action)
            continue
        if kind == "tidy":
            raise ValueError("A selected file has linked photo/video/edit components. Tidy will not separate or "
                             "remove this asset. Review it in Photos & videos instead.")
        destination = str(Path(action.dst).parent) if action.op == "copy" else ""
        key = (tuple(member["id"] for member in members), destination)
        if key not in units:
            units[key] = (members, [])
            order.append(key)
        units[key][1].append(action)
    out, extra = [], 0
    for key in order:
        members, originals = units[key]
        if len({action.op for action in originals}) != 1:
            raise ValueError("Linked components have conflicting operations. Review the asset as one group.")
        by_id = {rows_by_path[action.src]["id"]: action for action in originals}
        anchor = next((by_id[row["id"]] for row in members if row["id"] in by_id and row["kind"] == "image"),
                      originals[0])
        ids = tuple(sorted(row["id"] for row in members))
        token = hashlib.sha256(repr(key).encode("utf-8")).hexdigest()[:20]
        if anchor.op in ("move", "recycle") and any(
                os.path.normcase(str(lib.abspath(row["rel_path"]))) in guards for row in members):
            raise ValueError("A linked component is also marked as a surviving copy. Review the conflicting "
                             "duplicate groups before removing this asset.")
        if any(action.companions_locked for action in originals) and not set(ids) <= by_id.keys():
            raise ValueError("A linked component was not in the reviewed folder snapshot. Find duplicates again.")
        destination_stem = _stem(Path(anchor.dst).name) if anchor.dst else ""
        for row in members:
            original = by_id.get(row["id"])
            if original is None:
                extra += 1
                digest = row["chash"]
                if row["ext"].lower() in SIDECARS:
                    digest = full_hash(lib.abspath(row["rel_path"]))
                    if digest is None:
                        raise OSError("A linked edit sidecar could not be read. The asset was left unchanged.")
                original = Action(
                    op=anchor.op, src=str(lib.abspath(row["rel_path"])), size=row["size"], mtime=row["mtime"],
                    hash=digest,
                    reason="Linked photo/video/edit component; explicitly reviewed", file_id=row["id"])
            destination = None
            if anchor.dst:
                tail = row["name"][len(_stem(row["name"])):]
                destination = str(Path(anchor.dst).parent / (destination_stem + tail))
            out.append(replace(original, dst=destination, file_id=row["id"], asset_group=token, companion_ids=ids))
        groups.append(members)
    # Empty-folder removal runs only after every reviewed file unit.
    out.extend(action for action in standalone if action.op != "rmdir")
    out.extend(action for action in standalone if action.op == "rmdir")
    merges = []
    from . import organisation
    for action in out:
        if action.merge_into is not None:
            before, after = organisation.merged_state(lib, action.file_id, action.merge_into)
            if before != after:
                merges.append({"source": Path(action.src).name, "keeper": action.merge_into,
                               "before": before, "after": after})
    return Prepared(out, groups, extra, merges)


def validate_membership(lib: Library, unit: list) -> None:
    expected = unit[0].companion_ids
    if not expected:
        return
    row = lib.file(expected[0])
    if row is None:
        raise ValueError("A linked component is no longer in the catalogue. Review the asset again.")
    index = _index(lib, {row["folder"]})
    members = index.get((row["folder"].lower(), _stem(row["name"]).lower()), [])
    if tuple(sorted(member["id"] for member in members)) != expected:
        raise ValueError("The linked components changed after review. No files in this asset were moved.")


def grouped(planned: list) -> list[list]:
    result, groups = [], {}
    for action in planned:
        if not action.asset_group:
            result.append([action])
        else:
            if action.asset_group not in groups:
                groups[action.asset_group] = []
                result.append(groups[action.asset_group])
            groups[action.asset_group].append(action)
    return result


def destinations(unit: list, proposed: list[Path], reserved: set[str]) -> list[Path]:
    """Use one collision suffix for every component of a copied/moved asset."""
    if len(unit) == 1 or unit[0].op == "recycle":
        from .actions import _unique
        result = []
        for path in proposed:
            candidate = _unique(path)
            while os.path.normcase(str(candidate)) in reserved:
                candidate = candidate.with_name(candidate.stem + " (2)" + candidate.suffix)
            result.append(candidate)
            reserved.add(os.path.normcase(str(candidate)))
        return result
    stem = _stem(proposed[0].name)
    tails = [path.name[len(_stem(path.name)):] for path in proposed]
    for number in range(1, 10_000):
        name = stem if number == 1 else f"{stem} ({number})"
        result = [path.parent / (name + tail) for path, tail in zip(proposed, tails)]
        if all(not os.path.exists(config.longpath(path)) and os.path.normcase(str(path)) not in reserved
               for path in result):
            reserved.update(os.path.normcase(str(path)) for path in result)
            return result
    raise FileExistsError("Could not allocate a common destination name for the linked asset.")
