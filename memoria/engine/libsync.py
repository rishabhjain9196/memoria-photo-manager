"""Compare up to three libraries by content, then plan copy-only sync or cross-library cleanup.

Library A is always the open library and uses its own catalogue. B and C are any folders, for
example a phone backup or an external drive:

* If a folder already has a compatible Memoria catalogue, its fingerprints are reused read-only
  when the file's size and modification time still match.
* All other fingerprints are kept in a small comparison index stored in the *master* library the
  user chooses, so the other drive is not written to unless it is the master.

Only files whose size exists in at least two libraries are fingerprinted. Every fingerprint is a
full-content xxh3-128 hash, the same one Memoria uses everywhere, so the results are comparable.

Sync is copy-only: nothing is overwritten or removed. Removing duplicates moves files into the
owning library's Recovery folder and is recorded in this library's History so it can be undone.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sqlite3
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, Optional

from . import activity, assets, config
from .actions import Action
from .db import SCHEMA_VERSION, Library, LibraryUnavailable
from .hashing import full_hash
from .progress import Progress
from .scanner import walk_files

LETTERS = "ABC"
MAX_LIBRARIES = 3
INDEX_VERSION = 1
HASH_ALGORITHM = "xxh3-128"
PROFILES_FILE = "sync-profiles.json"
EXCLUSIONS_FILE = "sync-exclusions.json"
_HASH = re.compile(r"[0-9a-f]{32}")
# A source folder maps onto a destination folder when at least this share of its files are there.
MAPPING_COVERAGE = 0.5


@dataclass
class Participant:
    root: Path
    label: str
    current: bool = False


@dataclass
class IndexInfo:
    source: str                 # "library" | "catalogue" | "index"
    detail: str
    files: int = 0
    reused: int = 0
    hashed: int = 0
    location: str = ""


@dataclass(eq=False)
class Entry:
    side: int
    rel: str
    size: int
    mtime: float
    path: Path
    hash: Optional[str] = None
    file_id: Optional[int] = None
    mask: int = 0

    @property
    def folder(self) -> str:
        return os.path.dirname(self.rel)

    @property
    def name(self) -> str:
        return os.path.basename(self.rel)


@dataclass
class FolderNode:
    name: str
    rel: str
    folders: dict = field(default_factory=dict)
    files: list = field(default_factory=list)
    total: int = 0
    matching: int = 0
    bytes: int = 0

    @property
    def complete(self) -> bool:
        """Every file under this folder (recursively) matches the filter."""
        return self.total > 0 and self.matching == self.total


@dataclass
class FolderMatch:
    folder: str
    match: str
    shared: int
    total: int
    match_total: int

    @property
    def coverage(self) -> float:
        return self.shared / self.total if self.total else 0.0

    @property
    def match_coverage(self) -> float:
        return self.shared / self.match_total if self.match_total else 0.0


@dataclass
class CopyItem:
    entry: Entry
    target: int        # destination library
    folder: str        # destination folder relative to the destination library
    merged: bool       # the destination folder already exists
    action: Action
    excluded: bool = False   # remembered as "keep only in the source"


def content_key(entry: Entry) -> str:
    """Stable identity of a file's content for remembered sync exclusions."""
    return entry.hash or f"{entry.rel.lower()}|{entry.size}"


@dataclass
class RemovalPlan:
    actions: list[Action]
    items: list[Entry]
    kept_linked: int = 0


def letter(side: int) -> str:
    return LETTERS[side]


def bits(mask: int) -> list[int]:
    return [side for side in range(MAX_LIBRARIES) if mask & (1 << side)]


def _linkable(name: str) -> bool:
    ext = os.path.splitext(name)[1].lower()
    return ext in config.MEDIA_EXT or ext in assets.SIDECARS


def _wanted(name: str, media_only: bool) -> bool:
    ext = os.path.splitext(name)[1].lower()
    if name.startswith(config.JUNK_PREFIXES) or name.lower() in config.JUNK_NAMES or ext in config.JUNK_EXT:
        return False
    return not media_only or _linkable(name)


class Comparison:
    def __init__(self, participants: list[Participant], entries: list[list[Entry]], info: list[IndexInfo],
                 media_only: bool, master: int):
        self.participants, self.entries, self.info = participants, entries, info
        self.media_only, self.master = media_only, master
        self.count = len(participants)
        self.full = (1 << self.count) - 1
        self.by_hash: dict[str, list[Entry]] = defaultdict(list)
        for side in entries:
            for entry in side:
                if entry.hash:
                    self.by_hash[entry.hash].append(entry)
        masks: dict[str, int] = {}
        for digest, copies in self.by_hash.items():
            mask = 0
            for copy in copies:
                mask |= 1 << copy.side
            masks[digest] = mask
        for side in entries:
            for entry in side:
                entry.mask = (masks[entry.hash] if entry.hash else 0) | (1 << entry.side)
        self.folder_paths: list[dict[str, Path]] = []
        for index, side in enumerate(entries):
            known = {"": participants[index].root}
            for entry in side:
                known.setdefault(entry.folder.lower(), entry.path.parent)
            self.folder_paths.append(known)
        self._maps: dict[tuple[int, int], dict[str, FolderMatch]] = {}

    # statistics ---------------------------------------------------------------------------
    def regions(self) -> dict[int, tuple[int, int]]:
        """Distinct content per exact Venn region: {mask: (contents, bytes)}."""
        counted: dict[int, list[int]] = defaultdict(lambda: [0, 0])
        seen = set()
        for side in self.entries:
            for entry in side:
                key = entry.hash or id(entry)
                if key in seen:
                    continue
                seen.add(key)
                counted[entry.mask][0] += 1
                counted[entry.mask][1] += entry.size
        return {mask: (value[0], value[1]) for mask, value in counted.items()}

    def predicate(self, kind: str, value: int = 0) -> Callable[[int], bool]:
        if kind == "all":
            return lambda mask: True
        if kind == "every":
            return lambda mask: mask == self.full
        if kind == "only":
            return lambda mask: mask == 1 << value
        if kind == "missing":
            return lambda mask: not mask & (1 << value)
        if kind == "shared":
            return lambda mask: mask & (mask - 1) != 0
        if kind == "region":
            return lambda mask: mask == value
        raise ValueError(f"Unknown filter: {kind}")

    def matching(self, side: int, accept: Callable[[int], bool]) -> list[Entry]:
        return [entry for entry in self.entries[side] if accept(entry.mask)]

    def tree(self, side: int, accept: Callable[[int], bool]) -> FolderNode:
        """The side's folders with recursive totals; only matching files are listed."""
        root = FolderNode(self.participants[side].label, "")
        for entry in self.entries[side]:
            node = root
            node.total += 1
            hit = accept(entry.mask)
            if hit:
                node.matching += 1
                node.bytes += entry.size
            parts = [part for part in entry.folder.split(os.sep) if part]
            for depth, part in enumerate(parts):
                key = part.lower()
                child = node.folders.get(key)
                if child is None:
                    child = node.folders[key] = FolderNode(part, os.sep.join(parts[:depth + 1]))
                node = child
                node.total += 1
                if hit:
                    node.matching += 1
                    node.bytes += entry.size
            if hit:
                node.files.append(entry)
        return root

    def copies(self, entry: Entry) -> list[Entry]:
        return [copy for copy in self.by_hash.get(entry.hash, ()) if copy is not entry] if entry.hash else []

    # folder mapping -----------------------------------------------------------------------
    def folder_map(self, source: int, target: int) -> dict[str, FolderMatch]:
        """For each source folder, the target folder holding most of its content."""
        key = (source, target)
        if key in self._maps:
            return self._maps[key]
        totals = [defaultdict(int), defaultdict(int)]
        for index, side in enumerate((source, target)):
            for entry in self.entries[side]:
                totals[index][entry.folder.lower()] += 1
        pairs: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        names: dict[str, str] = {}
        for entry in self.entries[source]:
            if not entry.hash or not entry.mask & (1 << target):
                continue
            folders = {copy.folder.lower(): copy.folder for copy in self.by_hash[entry.hash] if copy.side == target}
            for lowered, folder in folders.items():
                pairs[entry.folder.lower()][lowered] += 1
                names[lowered] = folder
        result = {}
        display = {entry.folder.lower(): entry.folder for entry in self.entries[source]}
        for folder, candidates in pairs.items():
            best, shared = max(candidates.items(), key=lambda item: (item[1], -len(item[0]), item[0]))
            result[folder] = FolderMatch(display[folder], names[best], shared, totals[0][folder], totals[1][best])
        self._maps[key] = result
        return result

    def mapping_rows(self, source: int, target: int) -> list[FolderMatch]:
        mapped = self.folder_map(source, target)
        totals = defaultdict(int)
        display = {}
        for entry in self.entries[source]:
            totals[entry.folder.lower()] += 1
            display.setdefault(entry.folder.lower(), entry.folder)
        rows = [mapped.get(folder) or FolderMatch(display[folder], "", 0, total, 0)
                for folder, total in totals.items()]
        return sorted(rows, key=lambda row: row.folder.lower())

    def destination_folder(self, source: int, target: int, folder: str, placement: str = "merge") -> str:
        """Where files from ``folder`` go: into the folder already holding most of that content,
        under a mapped parent folder, or at the same relative path as in the source."""
        if placement == "merge":
            mapped = self.folder_map(source, target)
            current, rest = folder, []
            while True:
                match = mapped.get(current.lower())
                if match is not None and match.shared >= max(1, math.ceil(MAPPING_COVERAGE * match.total)):
                    return os.path.join(match.match, *reversed(rest)) if rest else match.match
                if not current:
                    break
                rest.append(os.path.basename(current))
                current = os.path.dirname(current)
        return folder

    def folder_exists(self, side: int, folder: str) -> bool:
        if folder.lower() in self.folder_paths[side]:
            return True
        return os.path.isdir(config.longpath(self.participants[side].root / folder))

    def _folder_path(self, side: int, folder: str) -> Path:
        return self.folder_paths[side].get(folder.lower()) or self.participants[side].root / folder

    # plans --------------------------------------------------------------------------------
    def plan_copy(self, source: int, target: int, placement: str = "merge",
                  entries: Optional[Iterable[Entry]] = None, excluded: Optional[set[str]] = None) -> list[CopyItem]:
        """Copy content present in ``source`` but absent from ``target`` (one copy per content).

        Items whose content key is in ``excluded`` are still returned, marked ``excluded``.
        """
        if source == target:
            raise ValueError("Choose two different libraries.")
        pool = self.entries[source] if entries is None else [entry for entry in entries if entry.side == source]
        seen, items = set(), []
        label = f"{letter(source)} ({self.participants[source].label}) to {letter(target)} ({self.participants[target].label})"
        for entry in sorted(pool, key=lambda item: item.rel.lower()):
            if entry.mask & (1 << target):
                continue
            key = entry.hash or id(entry)
            if key in seen:
                continue
            seen.add(key)
            folder = self.destination_folder(source, target, entry.folder, placement)
            destination = self._folder_path(target, folder) / entry.name
            action = Action(op="copy", src=str(entry.path), dst=str(destination), size=entry.size,
                            mtime=entry.mtime, hash=entry.hash, reason=f"Copy missing content from {label}")
            items.append(CopyItem(entry, target, folder, self.folder_exists(target, folder), action,
                                  bool(excluded) and content_key(entry) in excluded))
        return items

    def plan_removal(self, side: int, entries: Optional[Iterable[Entry]] = None) -> RemovalPlan:
        """Move ``side``'s copies of content that another library also holds to that side's Recovery.

        A photo is only removed together with all of its same-name linked parts (Live Photo video,
        RAW, edit sidecar); otherwise the whole asset is kept.
        """
        pool = self.entries[side] if entries is None else [entry for entry in entries if entry.side == side]
        candidates = {id(entry): entry for entry in pool
                      if entry.hash and entry.mask & ~(1 << side) & self.full}
        units: dict[tuple[str, str], list[Entry]] = defaultdict(list)
        for entry in self.entries[side]:
            if _linkable(entry.name):
                units[(entry.folder.lower(), assets._stem(entry.name).lower())].append(entry)
        blocked, kept_units = set(), 0
        for members in units.values():
            if len(members) < 2 or not any(id(member) in candidates for member in members):
                continue
            if not all(id(member) in candidates for member in members):
                blocked.update(id(member) for member in members)
                kept_units += 1
        participant = self.participants[side]
        actions, items = [], []
        for entry in sorted(candidates.values(), key=lambda item: item.rel.lower()):
            if id(entry) in blocked:
                continue
            keeper = next(copy for copy in self.by_hash[entry.hash] if copy.side != side)
            actions.append(Action(
                op="recycle", src=str(entry.path), size=entry.size, mtime=entry.mtime, hash=entry.hash,
                guards=[(str(keeper.path), entry.hash)], file_id=entry.file_id,
                recovery_root=None if participant.current else str(participant.root),
                reason=f"Also in {letter(keeper.side)} ({self.participants[keeper.side].label}) at {keeper.rel}"))
            items.append(entry)
        return RemovalPlan(actions, items, kept_units)

    # file types and general plans ---------------------------------------------------------------
    @staticmethod
    def kind(entry: Entry) -> str:
        """``photo`` | ``video`` | ``sidecar`` (.AAE, .XMP… edit and metadata files) | ``other``."""
        ext = os.path.splitext(entry.name)[1].lower()
        if ext in assets.SIDECARS:
            return "sidecar"
        kind = config.kind_for_ext(ext)
        return {"image": "photo", "video": "video"}.get(kind, "other")

    def plan_recycle(self, side: int, entries: Iterable[Entry]) -> list[tuple[Entry, Action, bool]]:
        """Move ``side``'s selected files to that library's Recovery: [(entry, action, unique)].

        Content that another library also holds keeps a guard (that copy must still exist, unchanged);
        ``unique`` marks content that exists nowhere else, which the caller must confirm explicitly.
        """
        participant = self.participants[side]
        out = []
        for entry in sorted((e for e in entries if e.side == side), key=lambda e: e.rel.lower()):
            keeper = next((copy for copy in self.copies(entry) if copy.side != side), None)
            guards = [(str(keeper.path), entry.hash)] if keeper is not None and entry.hash else []
            reason = (f"Also in {letter(keeper.side)} ({self.participants[keeper.side].label}) at {keeper.rel}"
                      if keeper is not None else "Only copy of this content in the compared libraries")
            out.append((entry, Action(op="recycle", src=str(entry.path), size=entry.size, mtime=entry.mtime,
                                      hash=entry.hash, guards=guards, file_id=entry.file_id,
                                      recovery_root=None if participant.current else str(participant.root),
                                      reason=reason), keeper is None))
        return out

    def _free_name(self, side: int, rel: str, taken: set[str]) -> str:
        stem, ext = os.path.splitext(rel)
        candidate, n = rel, 1
        while candidate.lower() in taken or os.path.lexists(config.longpath(self.participants[side].root / candidate)):
            n += 1
            candidate = f"{stem} ({n}){ext}"
        taken.add(candidate.lower())
        return candidate

    def _occupied(self, side: int, moving: set[int]) -> set[str]:
        return {e.rel.lower() for e in self.entries[side] if id(e) not in moving}

    def plan_move_into(self, side: int, entries: Iterable[Entry], folder: str) -> list[tuple[Entry, Action]]:
        """Move ``side``'s selected files into ``folder`` (relative to that library), keeping names."""
        pool = sorted((e for e in entries if e.side == side), key=lambda e: e.rel.lower())
        taken = self._occupied(side, {id(e) for e in pool})
        root, out = self.participants[side].root, []
        for entry in pool:
            if entry.folder.lower() == folder.lower():
                continue
            rel = self._free_name(side, os.path.join(folder, entry.name), taken)
            out.append((entry, Action(op="move", src=str(entry.path), dst=str(root / rel), size=entry.size,
                                      mtime=entry.mtime, hash=entry.hash, file_id=entry.file_id,
                                      reason=f"Move into {folder or 'the library folder'}")))
        return out

    def plan_match_layout(self, side: int, reference: int, entries: Iterable[Entry]) -> tuple[list[tuple[Entry, Action]], int]:
        """Rearrange ``side`` so content shared with ``reference`` sits at the same folder and name as there.

        Returns (moves, extra copies left in place). Only one copy per content moves; a name already
        used by different content gets " (2)". Files only in ``side`` are not touched.
        """
        pool = sorted((e for e in entries if e.side == side and e.hash and e.mask & (1 << reference)),
                      key=lambda e: e.rel.lower())
        chosen, extra = {}, 0
        for entry in pool:
            if entry.hash in chosen:
                extra += 1
            else:
                chosen[entry.hash] = entry
        moving = {id(e) for e in chosen.values()}
        taken = self._occupied(side, moving)
        root, out = self.participants[side].root, []
        for digest, entry in chosen.items():
            refs = sorted((c for c in self.by_hash[digest] if c.side == reference),
                          key=lambda c: (c.name.lower() != entry.name.lower(), c.rel.lower()))
            target_rel = refs[0].rel
            if entry.rel.lower() == target_rel.lower():
                taken.add(entry.rel.lower())
                continue
            rel = self._free_name(side, target_rel, taken)
            out.append((entry, Action(op="move", src=str(entry.path), dst=str(root / rel), size=entry.size,
                                      mtime=entry.mtime, hash=entry.hash, file_id=entry.file_id,
                                      reason=f"Same place as in {letter(reference)}: {target_rel}")))
        return out, extra


# building ---------------------------------------------------------------------------------
def _overlaps(a: Path, b: Path) -> bool:
    return a == b or a in b.parents or b in a.parents


def _validate(lib: Library, others: list[Path]) -> list[Path]:
    resolved = []
    for raw in others:
        path = Path(raw).resolve()
        if not path.is_dir():
            raise LibraryUnavailable(f"{path} is not available. Reconnect the drive or choose another folder.")
        for source in lib.roots():
            if _overlaps(path, Path(source["path"]).resolve()):
                raise ValueError(f"{path} overlaps this library's folders. Choose a separate library or drive folder.")
        for other in resolved:
            if _overlaps(path, other):
                raise ValueError("Choose separate folders: one library is inside another.")
        resolved.append(path)
    if not 1 <= len(resolved) <= MAX_LIBRARIES - 1:
        raise ValueError("Compare this library with one or two other libraries.")
    return resolved


def index_location(master_root: Path) -> Path:
    return config.app_dir(master_root) / "compare"


def _index_file(master_root: Path, root: Path) -> Path:
    digest = hashlib.sha1(os.path.normcase(str(root)).encode("utf-8")).hexdigest()[:16]
    return index_location(master_root) / f"{digest}.sqlite"


def _open_index(master_root: Path, root: Path) -> tuple[sqlite3.Connection, str]:
    config.ensure_app_dir(master_root)
    location = index_location(master_root)
    location.mkdir(parents=True, exist_ok=True)
    path = _index_file(master_root, root)
    conn = sqlite3.connect(str(path), timeout=30)
    conn.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    meta = dict(conn.execute("SELECT key, value FROM meta"))
    note = "updated"
    if meta and (meta.get("version") != str(INDEX_VERSION) or meta.get("algorithm") != HASH_ALGORITHM):
        conn.execute("DROP TABLE IF EXISTS files")
        conn.execute("DELETE FROM meta")
        note = "rebuilt (it was made by a different version)"
    elif not meta:
        note = "created"
    conn.execute("CREATE TABLE IF NOT EXISTS files (rel TEXT PRIMARY KEY COLLATE NOCASE, size INTEGER NOT NULL, "
                 "mtime REAL NOT NULL, chash TEXT)")
    conn.executemany("INSERT OR REPLACE INTO meta VALUES (?,?)",
                     [("version", str(INDEX_VERSION)), ("algorithm", HASH_ALGORITHM), ("root", str(root))])
    conn.commit()
    return conn, note


def read_catalogue(root: Path) -> tuple[Optional[dict], str]:
    """Fingerprints from an existing Memoria catalogue in ``root``, read-only, or why not."""
    path = config.app_dir(root) / config.DB_NAME
    if not path.is_file():
        return None, "no Memoria catalogue"
    for mode in ("ro", "ro&immutable=1"):
        try:
            conn = sqlite3.connect(f"{path.as_uri()}?mode={mode}", uri=True, timeout=5)
            try:
                version = conn.execute("PRAGMA user_version").fetchone()[0]
                if version > SCHEMA_VERSION:
                    return None, f"catalogue v{version} is from a newer Memoria, not reused"
                if version < 1:
                    return None, "catalogue is empty"
                columns = {row[1] for row in conn.execute("PRAGMA table_info(files)")}
                where = "root_id=1" if "root_id" in columns else "1"
                rows = conn.execute(f"SELECT rel_path, size, mtime, chash FROM files WHERE chash IS NOT NULL AND {where}")
                found = {rel.lower(): (size, mtime, digest) for rel, size, mtime, digest in rows
                         if isinstance(digest, str) and _HASH.fullmatch(digest)}
                return found, f"Memoria catalogue v{version} reused read-only"
            finally:
                conn.close()
        except sqlite3.Error:
            continue
    return None, "Memoria catalogue could not be read"


def _walk(root: Path, side: int, media_only: bool, progress: Progress) -> list[Entry]:
    failed: list[str] = []
    cut = len(str(root).rstrip(os.sep)) + 1
    found = []
    for number, item in enumerate(walk_files(root, failed=failed), 1):
        if number % 500 == 0:
            progress.update(0, 0, f"Listing {root.name or root}... {number:,} files")
        if not _wanted(item.name, media_only):
            continue
        try:
            stat = item.stat(follow_symlinks=False)
        except OSError as error:
            raise LibraryUnavailable(f"Comparison incomplete: could not read {item.path}: {error}") from error
        if stat.st_size:
            found.append(Entry(side, item.path[cut:], stat.st_size, stat.st_mtime, Path(item.path)))
    if failed or not root.is_dir():
        raise LibraryUnavailable(f"Comparison incomplete: {root} or one of its folders could not be read. "
                                 "Reconnect the drive or check permissions. Nothing was changed.")
    return found


def _library_entries(lib: Library, media_only: bool) -> list[Entry]:
    where = ("size>0 AND (kind!='other' OR ext IN ('.aae','.xmp'))" if media_only else "size>0")
    found = []
    for row in lib.readable_files(where):
        if not _wanted(row["name"], media_only):
            continue
        found.append(Entry(0, lib.export_rel(row["rel_path"]), row["size"], row["mtime"],
                           lib.abspath(row["rel_path"]), row["chash"], row["id"]))
    return found


def compare(lib: Library, others: list[str | Path], master: int = 0, media_only: bool = True,
            progress: Optional[Progress] = None, labels: Optional[list[str]] = None) -> Comparison:
    """Compare the open library (A) with one or two other folders (B, C)."""
    progress = progress or Progress()
    paths = _validate(lib, [Path(path) for path in others])
    participants = [Participant(lib.root, lib.root.name or str(lib.root), True)]
    for index, path in enumerate(paths):
        name = (labels[index + 1] if labels and len(labels) > index + 1 and labels[index + 1] else path.name or str(path))
        participants.append(Participant(path, name))
    if not 0 <= master < len(participants):
        raise ValueError("Choose which library stores the comparison index.")
    master_root = participants[master].root
    progress.update(0, 0, "Reading this library's catalogue...", force=True)
    entries = [_library_entries(lib, media_only)]
    info = [IndexInfo("library", f"This library's catalogue (schema v{SCHEMA_VERSION})", len(entries[0]),
                      reused=sum(entry.hash is not None for entry in entries[0]), location=str(config.app_dir(lib.root)))]
    indexes = []
    for side, path in enumerate(paths, 1):
        progress.check()
        found = _walk(path, side, media_only, progress)
        catalogue, catalogue_note = read_catalogue(path)
        conn, index_note = _open_index(master_root, path)
        stored = {row[0].lower(): (row[1], row[2], row[3]) for row in conn.execute("SELECT rel, size, mtime, chash FROM files")}
        reused = 0
        for entry in found:
            for cache in (catalogue or {}, stored):
                cached = cache.get(entry.rel.lower())
                if cached and cached[0] == entry.size and abs(cached[1] - entry.mtime) < 0.001 and cached[2] \
                        and _HASH.fullmatch(cached[2]):
                    entry.hash = cached[2]
                    reused += 1
                    break
        note = catalogue_note[:1].upper() + catalogue_note[1:]
        detail = (note + "; " if catalogue is not None else note + ". ") + f"comparison index {index_note}"
        info.append(IndexInfo("catalogue" if catalogue is not None else "index", detail, len(found), reused=reused,
                              location=str(_index_file(master_root, path))))
        entries.append(found)
        indexes.append(conn)
    try:
        sizes = defaultdict(int)
        for side in entries:
            for entry in side:
                sizes[entry.size] += 1
        # Any repeated size can hide identical content, including repeats inside one library,
        # which must be copied only once.
        todo = [entry for side in entries for entry in side
                if entry.hash is None and sizes[entry.size] > 1]
        _fingerprint(todo, progress)
        if any(entry.hash is None for entry in todo):
            missing = next(entry for entry in todo if entry.hash is None)
            raise LibraryUnavailable(f"Comparison incomplete: {missing.path} could not be read. "
                                     "Check that every drive is connected and try again. Nothing was changed.")
        lib.set_hashes([(entry.file_id, None, entry.hash) for entry in todo if entry.side == 0])
        for side, conn in enumerate(indexes, 1):
            hashed = [entry for entry in todo if entry.side == side]
            info[side].hashed = len(hashed)
            live = {entry.rel.lower() for entry in entries[side]}
            with conn:
                conn.executemany("INSERT OR REPLACE INTO files VALUES (?,?,?,?)",
                                 [(entry.rel, entry.size, entry.mtime, entry.hash) for entry in entries[side]])
                stale = [(rel,) for (rel,) in conn.execute("SELECT rel FROM files") if rel.lower() not in live]
                conn.executemany("DELETE FROM files WHERE rel=?", stale)
                conn.execute("INSERT OR REPLACE INTO meta VALUES ('updated', datetime('now'))")
        info[0].hashed = sum(entry.side == 0 for entry in todo)
    finally:
        for conn in indexes:
            conn.close()
    progress.update(1, 1, "Comparison complete", force=True)
    return Comparison(participants, entries, info, media_only, master)


def _fingerprint(todo: list[Entry], progress: Progress) -> None:
    if not todo:
        return
    total = len(todo)

    def work(entry):
        progress.check()
        entry.hash = full_hash(entry.path)
        return entry

    with activity.pool("Fingerprinting", max(2, config.WORKERS // 2)), \
            ThreadPoolExecutor(max_workers=max(2, config.WORKERS // 2)) as pool:
        for number, _ in enumerate(pool.map(work, todo), 1):
            progress.update(number, total, f"Fingerprinting files that could match... {number:,} of {total:,}")


# saved relationships ----------------------------------------------------------------------
def _profiles_path(lib: Library) -> Path:
    return config.app_dir(lib.root) / PROFILES_FILE


def load_profiles(lib: Library) -> list[dict]:
    try:
        data = json.loads(_profiles_path(lib).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return [item for item in data if isinstance(item, dict) and isinstance(item.get("name"), str)] \
        if isinstance(data, list) else []


def save_profile(lib: Library, profile: dict) -> list[dict]:
    name = str(profile.get("name", "")).strip()
    if not name:
        raise ValueError("Give the relationship a name.")
    profiles = [item for item in load_profiles(lib) if item["name"].casefold() != name.casefold()]
    profiles.append({**profile, "name": name})
    profiles.sort(key=lambda item: item["name"].casefold())
    _write_profiles(lib, profiles)
    return profiles


def delete_profile(lib: Library, name: str) -> list[dict]:
    profiles = [item for item in load_profiles(lib) if item["name"].casefold() != name.casefold()]
    _write_profiles(lib, profiles)
    return profiles


def _write_profiles(lib: Library, profiles: list[dict]) -> None:
    _write_json(_profiles_path(lib), profiles)


def _write_json(path: Path, data) -> None:
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, indent=2), encoding="utf-8")
    os.replace(temporary, path)


# remembered "keep only in the source" choices ------------------------------------------------
def _exclusions_path(lib: Library) -> Path:
    return config.app_dir(lib.root) / EXCLUSIONS_FILE


def pair_key(source_root: Path, target_root: Path) -> str:
    return f"{os.path.normcase(str(Path(source_root).resolve()))}=>{os.path.normcase(str(Path(target_root).resolve()))}"


def _load_all_exclusions(lib: Library) -> dict:
    try:
        data = json.loads(_exclusions_path(lib).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def load_exclusions(lib: Library, source_root: Path, target_root: Path) -> dict[str, dict]:
    """Content keys the user chose to keep only in ``source_root`` when syncing to ``target_root``."""
    found = _load_all_exclusions(lib).get(pair_key(source_root, target_root), {})
    return found if isinstance(found, dict) else {}


def update_exclusions(lib: Library, source_root: Path, target_root: Path,
                      add: Iterable[Entry] = (), remove: Iterable[Entry] = ()) -> dict[str, dict]:
    data = _load_all_exclusions(lib)
    key = pair_key(source_root, target_root)
    current = dict(data.get(key) or {})
    for entry in remove:
        current.pop(content_key(entry), None)
    for entry in add:
        current[content_key(entry)] = {"rel": entry.rel, "size": entry.size}
    if current:
        data[key] = current
    else:
        data.pop(key, None)
    _write_json(_exclusions_path(lib), data)
    return current
