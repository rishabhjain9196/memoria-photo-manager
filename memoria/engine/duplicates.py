"""Exact duplicates: same bytes, proven by full-content hash.

Funnel for speed: group by size → quick (sampled) hash → full hash. Files with a unique size
are never read. Hashes are cached in the catalogue and invalidated when a file changes.

Whole duplicate folders are found from the same hashes: a folder is a duplicate when another
folder holds exactly the same files ("same") or holds all of them and more ("inside"). Results
are reported at the highest folder level, so a copied tree shows up once, as its top folder.
"""
from __future__ import annotations

import os
import re
import hashlib
import json
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import PurePath
from typing import Iterable, Optional

from . import config, roots
from .actions import Action
from .db import Library
from .hashing import full_hash, quick_hash
from .progress import Progress

_COPY_NAME = re.compile(r"(\(\d+\)|\bcopy\b|- copy|_copy|\bduplicate\b|~\d+)", re.I)
_COPY_FOLDER = re.compile(r"(backup|copy|copies|duplicate|download|whatsapp|telegram|temp|tmp|old|recovered|export)", re.I)


@dataclass
class DuplicateGroup:
    hash: str
    size: int
    files: list[dict]             # rows as dicts, keeper first
    keeper_id: int
    reasons: dict[int, str] = field(default_factory=dict)

    @property
    def wasted(self) -> int:
        return self.size * (len(self.files) - 1)


def _hash_pass(lib: Library, rows: list, fn, column: str, progress: Progress, label: str,
               done_offset: int, total: int) -> dict[int, Optional[str]]:
    out: dict[int, Optional[str]] = {}
    todo = [r for r in rows if not r[column]]
    for r in rows:
        if r[column]:
            out[r["id"]] = r[column]
    if todo:
        def work(r):
            p = lib.abspath(r["rel_path"])
            lib.check_path(p)
            return r["id"], (fn(p, r["size"]) if column == "qhash" else fn(p))
        updates = []
        with ThreadPoolExecutor(max_workers=config.WORKERS) as pool:
            for i, (fid, h) in enumerate(pool.map(work, todo), 1):
                out[fid] = h
                if h:
                    updates.append((fid, h, None) if column == "qhash" else (fid, None, h))
                progress.update(done_offset + i, total, f"{label}… {i:,} of {len(todo):,}")
        lib.set_hashes(updates)
    return out


def confirm_identical(lib: Library, rows: list, progress: Optional[Progress] = None,
                      label: str = "Comparing file contents") -> dict[str, list]:
    """Return {full_hash: [rows]} for rows that have at least one byte-identical partner."""
    progress = progress or Progress()
    by_size = defaultdict(list)
    for r in rows:
        if r["size"] > 0:
            by_size[r["size"]].append(r)
    cands = [r for g in by_size.values() if len(g) > 1 for r in g]
    total = len(cands) * 2 or 1
    q = _hash_pass(lib, cands, quick_hash, "qhash", progress, label, 0, total)
    by_q = defaultdict(list)
    for r in cands:
        if q.get(r["id"]):
            by_q[(r["size"], q[r["id"]])].append(r)
    cands2 = [r for g in by_q.values() if len(g) > 1 for r in g]
    c = _hash_pass(lib, cands2, full_hash, "chash", progress, label, len(cands), total)
    by_c = defaultdict(list)
    for r in cands2:
        if c.get(r["id"]):
            by_c[c[r["id"]]].append(r)
    progress.update(total, total, "Contents compared", force=True)
    return {h: g for h, g in by_c.items() if len(g) > 1}


def keeper_score(row) -> tuple:
    rel = row["rel_path"]
    name = PurePath(rel).stem
    folder = row["folder"]
    penalty = 0.0
    if _COPY_NAME.search(name):
        penalty += 3
    if _COPY_FOLDER.search(folder):
        penalty += 2
    penalty += 0.1 * rel.count("\\")
    return (penalty, row["mtime"], len(rel), rel.lower())


def keeper_reason(keeper, other) -> str:
    kn, on = PurePath(keeper["rel_path"]).stem, PurePath(other["rel_path"]).stem
    if _COPY_NAME.search(on) and not _COPY_NAME.search(kn):
        return "Name looks like a copy"
    if _COPY_FOLDER.search(other["folder"]) and not _COPY_FOLDER.search(keeper["folder"]):
        return "In a backup/download/copy folder"
    if other["mtime"] > keeper["mtime"]:
        return "Newer copy of the same file"
    return "Identical copy"


def _make_group(h: str, members: list) -> DuplicateGroup:
    members = sorted((dict(m) for m in members), key=keeper_score)
    for member in members:
        member["chash"] = h
    keeper = members[0]
    g = DuplicateGroup(hash=h, size=keeper["size"], files=members, keeper_id=keeper["id"])
    g.reasons[keeper["id"]] = "Kept: best name and location"
    for m in members[1:]:
        g.reasons[m["id"]] = keeper_reason(keeper, m)
    return g


def find_duplicates(lib: Library, progress: Optional[Progress] = None, media_only: bool = True) -> list[DuplicateGroup]:
    where = "kind!='other'" if media_only else "1"
    rows = lib.readable_files(where)
    groups = [_make_group(h, m) for h, m in confirm_identical(lib, rows, progress, "Finding exact duplicates").items()]
    groups.sort(key=lambda g: g.wasted, reverse=True)
    return groups


def plan_removal(lib: Library, groups: list[DuplicateGroup], keepers: Optional[dict[str, int]] = None,
                 excluded: Optional[set[int]] = None, *,
                 removals: Optional[dict[str, set[int]]] = None) -> list[Action]:
    """Actions moving every non-keeper to Recovery. ``keepers`` overrides keeper per group hash;
    ``excluded`` file ids are left untouched. Explicit ``removals`` may select every copy;
    those still require their reviewed hash/mtime but intentionally have no surviving-copy guard."""
    keepers = keepers or {}
    excluded = excluded or set()
    actions = []
    for g in groups:
        keep_id = keepers.get(g.hash, g.keeper_id)
        ids = {f["id"] for f in g.files}
        chosen = set((removals or {}).get(g.hash, ids - {keep_id}))
        if not chosen <= ids or keep_id not in ids:
            raise ValueError("Duplicate choices no longer match the reviewed files. Find duplicates again.")
        chosen -= excluded
        remaining = [f for f in g.files if f["id"] not in chosen]
        keeper = next((f for f in remaining if f["id"] == keep_id), None)
        if keeper is None and remaining:
            keeper = min(remaining, key=keeper_score)
        guards = [(str(lib.abspath(keeper["rel_path"])), g.hash)] if keeper else []
        for f in g.files:
            if f["id"] not in chosen:
                continue
            actions.append(Action(op="recycle", src=str(lib.abspath(f["rel_path"])), size=f["size"],
                                  mtime=f["mtime"], hash=g.hash, guards=guards,
                                  reason=f"Duplicate of {keeper['rel_path']}" if keeper else
                                  "All shown copies explicitly selected for Recovery", file_id=f["id"],
                                  merge_into=keeper["id"] if keeper else None))
    return actions


def _signature(value) -> str:
    return hashlib.sha256(json.dumps(value, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()


def _row_signature(rows) -> str:
    return _signature(sorted((r["id"], r["rel_path"], r["size"], r["mtime"], r.get("chash")) for r in rows))


def file_review_key(group: DuplicateGroup) -> str:
    return "file:" + _signature((group.hash, _row_signature(group.files)))


def kept_choices(lib: Library) -> set[str]:
    return {row[0] for row in lib.db.execute("SELECT signature FROM duplicate_kept")}


def remember_keep(lib: Library, signature: str, keep: bool) -> None:
    if keep:
        lib.db.execute("INSERT OR IGNORE INTO duplicate_kept VALUES (?)", (signature,))
    else:
        lib.db.execute("DELETE FROM duplicate_kept WHERE signature=?", (signature,))


# ============================================================================ duplicate folders
@dataclass
class FolderInfo:
    """What a folder holds, counting everything in its sub-folders."""
    path: str                    # relative to the library
    files: int = 0
    subfolders: int = 0
    photos: int = 0
    videos: int = 0
    others: int = 0
    photo_bytes: int = 0
    video_bytes: int = 0
    other_bytes: int = 0

    @property
    def total_bytes(self) -> int:
        return self.photo_bytes + self.video_bytes + self.other_bytes

    @property
    def name(self) -> str:
        return PurePath(self.path).name


@dataclass
class FolderMatch:
    """Whole folders that are duplicates.

    ``same``: the folders hold exactly the same files (byte for byte; names and layout may differ);
    one is kept by default. ``inside``: every file in ``folders[0]`` is also in ``folders[1]``, which holds more.
    """
    kind: str
    folders: list[FolderInfo]
    keeper: str

    @property
    def id(self) -> str:
        return self.kind + ":" + "|".join(sorted(f.path.lower() for f in self.folders))

    def keeper_path(self, keepers: Optional[dict[str, str]] = None) -> str:
        if self.kind == "inside":
            return self.folders[1].path
        k = (keepers or {}).get(self.id)
        return k if k and any(f.path == k for f in self.folders) else self.keeper

    def redundant(self, keepers: Optional[dict[str, str]] = None) -> list[FolderInfo]:
        if self.kind == "inside":
            return [self.folders[0]]
        k = self.keeper_path(keepers)
        return [f for f in self.folders if f.path != k]

    def wasted(self, keepers: Optional[dict[str, str]] = None) -> int:
        return sum(f.total_bytes for f in self.redundant(keepers))

    @property
    def suggested(self) -> bool:
        """Selected by default — except when an original-looking folder sits inside a backup/copy folder."""
        return not (self.kind == "inside" and _COPY_FOLDER.search(self.folders[1].path)
                    and not _COPY_FOLDER.search(self.folders[0].path))

    def reason(self, folder: FolderInfo, keepers: Optional[dict[str, str]] = None) -> str:
        keep = self.keeper_path(keepers)
        if folder.path == keep:
            return "Kept" if self.kind == "same" else "Kept: holds everything in the other folder, and more"
        if self.kind == "inside":
            return f"Every file in it is also in “{keep}”"
        if _COPY_FOLDER.search(folder.path) and not _COPY_FOLDER.search(keep):
            return "Same files; looks like a backup or copy"
        return "Same files as the folder being kept"


@dataclass
class DuplicateReport:
    groups: list[DuplicateGroup]      # every set of identical photos/videos
    folders: list[FolderMatch]        # whole duplicate folders, highest level only
    folder_files: dict[str, list[dict]] = field(default_factory=dict)
    folder_signatures: dict[str, str] = field(default_factory=dict)
    folder_dirs: dict[str, list[str]] = field(default_factory=dict)

    def folder_review_key(self, match: FolderMatch) -> str:
        return "folder:" + _signature((match.id, [self.folder_signatures[f.path] for f in match.folders]))

    def redundant_folders(self, keepers: Optional[dict[str, str]] = None,
                          include: Optional[set[str]] = None,
                          removals: Optional[dict[str, set[str]]] = None) -> list[str]:
        paths = [path for m in self.folders if include is None or m.id in include
                 for path in (removals or {}).get(m.id, {f.path for f in m.redundant(keepers)})]
        return _outermost(paths)

    def loose_groups(self, keepers: Optional[dict[str, str]] = None,
                     covered: Iterable[str] = ()) -> list[DuplicateGroup]:
        """File groups once duplicate folders are accounted for: copies inside a folder listed as a
        duplicate are handled with that folder, not one by one."""
        red = {p.lower() for p in (*self.redundant_folders(keepers), *covered)}
        out = []
        for g in self.groups:
            left = [f for f in g.files if not _under_any(f["folder"], red)]
            if len(left) == len(g.files):
                out.append(g)
            elif len(left) > 1:
                out.append(_make_group(g.hash, left))
        out.sort(key=lambda g: g.wasted, reverse=True)
        return out


def _parents(folder: str):
    """'a\\b\\c' → 'a\\b\\c', 'a\\b', 'a'. The library root is not a folder here."""
    while folder:
        if not roots.split_key(folder)[1]:
            break
        yield folder
        folder = os.path.dirname(folder)


def _within(path: str, folder: str) -> bool:
    return path == folder or path.startswith(folder + os.sep)


def _under_any(folder: str, folders: set[str]) -> bool:
    return bool(folders) and any(p in folders for p in _parents(folder.lower()))


def _outermost(paths: Iterable[str]) -> list[str]:
    uniq = {p.lower(): p for p in paths}
    out, seen = [], set()
    for k in sorted(uniq, key=lambda k: (k.count(os.sep), k)):
        if not any(a in seen for a in _parents(k)):
            seen.add(k)
            out.append(uniq[k])
    return out


def _folder_score(path: str) -> tuple:
    return (2 if _COPY_FOLDER.search(path) else 0, path.count(os.sep), len(path), path.lower())


def find_all(lib: Library, progress: Optional[Progress] = None) -> DuplicateReport:
    """Exact duplicate photos/videos, plus whole folders that duplicate another folder."""
    from .tidy import is_junk
    progress = progress or Progress()
    rows = [dict(r) for r in lib.readable_files()]
    content = [r for r in rows if r["size"] > 0 and not is_junk(r["name"])]
    ident = confirm_identical(lib, content, progress, "Finding exact duplicates")
    groups = []
    for h, members in ident.items():
        media = [m for m in members if m["kind"] != "other"]
        if len(media) > 1:
            groups.append(_make_group(h, media))
    groups.sort(key=lambda g: g.wasted, reverse=True)
    progress.update(1, 1, "Comparing folders…", force=True)
    folders = find_duplicate_folders(rows, ident)
    paths = {f.path.lower(): f.path for match in folders for f in match.folders}
    snapshots = {path: [] for path in paths.values()}
    hashes = {r["id"]: h for h, members in ident.items() for r in members}
    for row in rows:
        matched = [paths[parent] for parent in _parents(row["folder"].lower()) if parent in paths]
        if not matched:
            continue
        snapshot = {key: row[key] for key in ("id", "rel_path", "folder", "name", "size", "mtime")}
        snapshot["chash"] = hashes.get(row["id"])
        if row["size"] == 0 or is_junk(row["name"]):
            snapshot["chash"] = full_hash(lib.abspath(row["rel_path"]))
        for path in matched:
            snapshots[path].append(snapshot)
    from .scanner import walk_dirs
    directory_snapshots = {
        path: [lib.rel(directory) for directory in walk_dirs(lib.abspath(path))]
        for path in snapshots}
    return DuplicateReport(groups, folders, snapshots,
                           {path: _row_signature(items) for path, items in snapshots.items()}, directory_snapshots)


def find_duplicate_folders(rows: list[dict], identical: dict[str, list]) -> list[FolderMatch]:
    """Folders whose files all exist, byte for byte, in one other folder.

    ``identical`` is :func:`confirm_identical`'s output for the same rows. Junk (Thumbs.db…) and
    empty files are ignored when comparing, but counted in sizes and moved with their folder.
    Folders are compared with their sub-folders; a match is only reported for the highest folder,
    so a copied tree appears once.
    """
    from .tidy import is_junk
    cid = {r["id"]: h for h, g in identical.items() for r in g}
    info: dict[str, FolderInfo] = {}
    counts: dict[str, Counter] = defaultdict(Counter)
    unique: dict[str, int] = defaultdict(int)
    where: dict[str, list[str]] = defaultdict(list)        # content id → folder of each copy
    for r in rows:
        disp = r["folder"]
        key = disp.lower()
        c = cid.get(r["id"])
        ignorable = r["size"] == 0 or is_junk(r["name"])
        if c and not ignorable:
            where[c].append(key)
        kind, size = r["kind"], r["size"]
        for k, d in zip(_parents(key), _parents(disp)):
            fi = info.get(k)
            if fi is None:
                fi = info[k] = FolderInfo(d)
            fi.files += 1
            if kind == "image":
                fi.photos += 1
                fi.photo_bytes += size
            elif kind == "video":
                fi.videos += 1
                fi.video_bytes += size
            else:
                fi.others += 1
                fi.other_bytes += size
            if ignorable:
                continue
            if c:
                counts[k][c] += 1
            else:
                unique[k] += 1
    for k in info:
        for a in _parents(os.path.dirname(k)):
            info[a].subfolders += 1

    cand = {k for k in counts if not unique.get(k)}
    sig = {k: frozenset(counts[k].items()) for k in cand}
    top_of: dict[str, str] = {}

    def top(k: str) -> str:
        """Highest folder holding exactly what ``k`` holds (a parent with nothing else in it)."""
        if k not in top_of:
            p = os.path.dirname(k)
            top_of[k] = top(p) if p and p in cand and sig[p] == sig[k] else k
        return top_of[k]

    tops = sorted(k for k in cand if top(k) == k)
    covers: dict[str, set[str]] = defaultdict(set)
    classes: dict[frozenset, list[str]] = defaultdict(list)
    for t in tops:
        classes[sig[t]].append(t)
    same_sets = [m for m in classes.values() if len(m) > 1]
    for members in same_sets:
        for t in members:
            covers[t].update(m for m in members if m != t)

    container: dict[str, str] = {}
    for t in tops:
        ct = counts[t]
        rare = min(ct, key=lambda c: (len(where[c]), c))
        best = None
        for f in where[rare]:
            if _within(f, t):
                continue
            for b in _parents(f):
                if _within(t, b):                      # an ancestor of t: not a separate folder
                    break
                if b in cand and sig[b] == sig[t]:      # identical: reported as "same"
                    break
                cb = counts[b]
                if all(cb[c] >= n for c, n in ct.items()):
                    rank = (_folder_score(info[b].path)[0], info[b].files, b)    # originals first, then smallest
                    if best is None or rank < (_folder_score(info[best].path)[0], info[best].files, best):
                        best = b
                    break
        if best:
            container[t] = best
            covers[t].add(best)

    def implied(f: str, others: list[str]) -> bool:
        """True if a parent of ``f`` is already a duplicate of a folder that holds one of ``others``."""
        for a in _parents(os.path.dirname(f)):
            if a not in cand:
                return False
            if any(_within(o, c) for c in covers.get(top(a), ()) for o in others):
                return True
        return False

    rels = [("same", m) for m in same_sets] + [("inside", [t, b]) for t, b in container.items()]
    rels.sort(key=lambda r: (min(p.count(os.sep) for p in r[1][:1 if r[0] == "inside" else None]), r[0], r[1]))
    redundant: set[str] = set()
    out: list[FolderMatch] = []
    for kind, members in rels:
        if kind == "same":
            kept = sorted(members, key=lambda m: (not _under_any(m, redundant), m))
            for f in list(kept):
                if implied(f, [o for o in kept if o != f]):
                    kept.remove(f)
            if len(kept) < 2:
                continue
            kept.sort(key=lambda k: _folder_score(info[k].path))
            redundant.update(kept[1:])
            out.append(FolderMatch("same", [info[k] for k in kept], info[kept[0]].path))
        else:
            t, b = members
            if _under_any(t, redundant) or implied(t, [b]):
                continue
            redundant.add(t)
            out.append(FolderMatch("inside", [info[t], info[b]], info[b].path))
    out.sort(key=lambda m: (-m.wasted(), m.id))
    return out


def plan_cleanup(lib: Library, report: DuplicateReport, folders: Iterable[str] = (),
                 folder_keepers: Optional[dict[str, str]] = None, files: Iterable[str] = (),
                 file_keepers: Optional[dict[str, int]] = None, excluded: Optional[set[int]] = None, *,
                 file_removals: Optional[dict[str, set[int]]] = None,
                 folder_removals: Optional[dict[str, set[str]]] = None) -> list[Action]:
    """Actions for the chosen duplicate folders (``folders``: match ids) and file groups (``files``:
    hashes of ``report.loose_groups``).

    Every file moved out of a duplicate folder is guarded by an identical copy that stays in the
    library, unless every folder of an identical group was explicitly selected. That exception
    moves only files in the original review snapshot. Containing folders with unique files cannot
    be selected this way. Emptied folders are removed only if nothing else appeared in them.
    """
    from .scanner import walk_dirs
    from .tidy import is_junk
    fk = folder_keepers or {}
    folder_removals, file_removals = folder_removals or {}, file_removals or {}
    matches = {m.id: m for m in report.folders}
    if not folder_removals.keys() <= matches.keys():
        raise ValueError("Folder choices no longer match this review. Find duplicates again.")
    covered, protected, removing, unguarded = [], set(excluded or ()), [], set()
    included = set(folders)
    for match in report.folders:
        members = {f.path for f in match.folders}
        if match.id in folder_removals:
            chosen = folder_removals[match.id]
            allowed = members if match.kind == "same" else {match.folders[0].path}
            if not chosen <= allowed:
                raise ValueError("A containing folder may hold unique files and cannot be removed here.")
            covered.extend(members)
            for path in members - chosen:
                protected.update(r["id"] for r in report.folder_files[path])
        else:
            chosen = {f.path for f in match.redundant(fk)}
        if match.id in included:
            removing.extend(chosen)
            if match.kind == "same" and chosen == members:
                unguarded.update(chosen)
    removing = _outermost(removing)
    loose = report.loose_groups(fk, covered)
    for group in loose:
        if group.hash in file_removals and not file_removals[group.hash]:
            protected.update(f["id"] for f in group.files)
    wanted = set(files)
    file_actions = plan_removal(lib, [g for g in loose if g.hash in wanted], file_keepers, protected,
                                removals=file_removals)
    gone = {a.file_id for a in file_actions}
    rows = [dict(r) for r in lib.files("root_id IN (SELECT id FROM library_roots WHERE online=1)")]

    def owner(r, keys: dict[str, str]) -> Optional[str]:
        for p in _parents(r["folder"].lower()):
            if p in keys:
                return keys[p]
        return None

    while True:
        keys = {p.lower(): p for p in removing}
        mine: dict[str, list[dict]] = defaultdict(list)
        survivors: dict[str, list[dict]] = defaultdict(list)
        for r in rows:
            o = owner(r, keys)
            if o is not None:
                mine[o].append(r)
            elif r["chash"] and r["size"] > 0 and r["id"] not in gone:
                survivors[r["chash"]].append(r)
        bad = next((p for p in removing for r in mine[p]
                    if r["id"] in protected or (p not in unguarded and r["size"] > 0 and
                    not is_junk(r["name"]) and not survivors.get(r["chash"] or ""))), None)
        if bad is None:
            break
        removing.remove(bad)

    actions: list[Action] = []
    for p in removing:
        members = report.folder_files[p] if p in unguarded else mine[p]
        if p in unguarded and any(not r["chash"] for r in members):
            raise ValueError("Some reviewed folder contents could not be fingerprinted. "
                             "Find duplicates again before choosing Remove both/all.")
        for r in sorted(members, key=lambda r: r["rel_path"].lower()):
            src = str(lib.abspath(r["rel_path"]))
            if p in unguarded:
                actions.append(Action(op="recycle", src=src, size=r["size"], mtime=r["mtime"], hash=r["chash"],
                                      reason="All identical folders explicitly selected for Recovery", file_id=r["id"],
                                      companions_locked=True))
            elif r["size"] > 0 and not is_junk(r["name"]):
                keep = min(survivors[r["chash"]], key=keeper_score)
                actions.append(Action(op="recycle", src=src, size=r["size"], mtime=r["mtime"], hash=r["chash"],
                                      guards=[(str(lib.abspath(keep["rel_path"])), r["chash"])],
                                      reason=f"In duplicate folder “{p}”; identical copy kept at {keep['rel_path']}",
                                      file_id=r["id"], merge_into=keep["id"], companions_locked=True))
            else:
                actions.append(Action(op="recycle", src=src, size=r["size"], mtime=r["mtime"],
                                      reason=f"Leftover in duplicate folder “{p}”", file_id=r["id"],
                                      companions_locked=True))
        top_dir = str(lib.abspath(p))
        for d in sorted(walk_dirs(top_dir) + [top_dir], key=lambda d: -d.count(os.sep)):
            actions.append(Action(op="rmdir", src=d, reason=f"Duplicate folder “{p}”, now empty"))
    return actions + file_actions


@dataclass
class FolderSelection:
    actions: list[Action]
    retained_linked: int = 0
    unique_kept: int = 0


def folder_comparison(report: DuplicateReport, match: FolderMatch) -> list[dict]:
    """Verified common content, not filename overlap. Empty/system leftovers are counted separately."""
    from .tidy import is_junk
    meaningful = {
        folder.path: [row for row in report.folder_files[folder.path] if row["size"] > 0 and not is_junk(row["name"])]
        for folder in match.folders}
    hashes = [{row["chash"] for row in meaningful[folder.path] if row["chash"]} for folder in match.folders]
    common = set.intersection(*hashes) if hashes else set()
    result = []
    for folder in match.folders:
        shared = [row for row in meaningful[folder.path] if row["chash"] in common]
        unique = [row for row in meaningful[folder.path] if row["chash"] not in common]
        result.append({"folder": folder, "shared": shared, "unique": unique,
                       "shared_bytes": sum(row["size"] for row in shared),
                       "unique_bytes": sum(row["size"] for row in unique),
                       "leftovers": len(report.folder_files[folder.path]) - len(meaningful[folder.path])})
    return result


def plan_folder_selection(lib: Library, report: DuplicateReport, match: FolderMatch,
                          selected: set[str]) -> FolderSelection:
    """Review one folder group. A selected superset contributes only its verified shared files."""
    from .assets import linked_groups
    from .tidy import is_junk
    members = {folder.path for folder in match.folders}
    if not selected <= members:
        raise ValueError("The selected folders no longer match this comparison. Find duplicates again.")
    comparisons = {item["folder"].path: item for item in folder_comparison(report, match)}
    larger = match.folders[1].path if match.kind == "inside" else None
    candidates = {}
    full_folders = set()
    for path in selected:
        if path == larger:
            rows = comparisons[path]["shared"]
        else:
            rows = report.folder_files[path]
            full_folders.add(path)
        candidates.update((row["id"], row) for row in rows)
    protected = set()
    for group in linked_groups(lib, list(candidates.values())):
        ids = {row["id"] for row in group}
        if not ids <= candidates.keys():
            protected.update(ids & candidates.keys())
    for file_id in protected:
        candidates.pop(file_id)
    survivors = defaultdict(list)
    for path in members:
        for row in report.folder_files[path]:
            if row["id"] not in candidates and row["chash"] and row["size"] > 0 and not is_junk(row["name"]):
                survivors[row["chash"]].append(row)
    planned = []
    for row in sorted(candidates.values(), key=lambda item: item["rel_path"].lower()):
        if not row["chash"]:
            raise ValueError("Some selected contents were not fingerprinted. Find duplicates again before removal.")
        meaningful = row["size"] > 0 and not is_junk(row["name"])
        keep = min(survivors[row["chash"]], key=keeper_score) if meaningful and survivors[row["chash"]] else None
        if meaningful and keep is None and selected != members:
            raise ValueError("A surviving copy could not be verified in the unselected folders. Find duplicates again.")
        planned.append(Action(
            "recycle", str(lib.abspath(row["rel_path"])), size=row["size"], mtime=row["mtime"],
            hash=row["chash"], file_id=row["id"], companions_locked=True,
            guards=[(str(lib.abspath(keep["rel_path"])), row["chash"])] if keep else [],
            merge_into=keep["id"] if keep else None,
            reason="Shared folder content explicitly selected" if row["folder"] == larger or
                   larger and _within(row["folder"], larger) else "Reviewed duplicate folder selected"))
    directories, retained_ancestors = set(), set()
    for path in full_folders:
        directories.add(path)
        directories.update(report.folder_dirs.get(path, ()))
        for row in report.folder_files[path]:
            directories.update(parent for parent in _parents(row["folder"]) if _within(parent, path))
            if row["id"] not in candidates:
                retained_ancestors.update(parent.lower() for parent in _parents(row["folder"]))
    for path in sorted(directories, key=lambda value: (-value.count(os.sep), value)):
        if path.lower() in retained_ancestors:
            continue
        planned.append(Action("rmdir", str(lib.abspath(path)), reason="Reviewed duplicate folder, only if empty"))
    return FolderSelection(planned, len(protected),
                           len(comparisons[larger]["unique"]) if larger and larger in selected else 0)
