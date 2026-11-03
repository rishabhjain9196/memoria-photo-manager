"""Exact duplicates: same bytes, proven by full-content hash.

Funnel for speed: group by size → quick (sampled) hash → full hash. Files with a unique size
are never read. Hashes are cached in the catalogue and invalidated when a file changes.
"""
from __future__ import annotations

import re
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import PurePath
from typing import Optional

from . import config
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


def find_duplicates(lib: Library, progress: Optional[Progress] = None, media_only: bool = True) -> list[DuplicateGroup]:
    where = "kind!='other'" if media_only else "1"
    rows = lib.files(where)
    groups = []
    for h, members in confirm_identical(lib, rows, progress, "Finding exact duplicates").items():
        members = sorted((dict(m) for m in members), key=keeper_score)
        keeper = members[0]
        g = DuplicateGroup(hash=h, size=keeper["size"], files=members, keeper_id=keeper["id"])
        g.reasons[keeper["id"]] = "Kept: best name and location"
        for m in members[1:]:
            g.reasons[m["id"]] = keeper_reason(keeper, m)
        groups.append(g)
    groups.sort(key=lambda g: g.wasted, reverse=True)
    return groups


def plan_removal(lib: Library, groups: list[DuplicateGroup], keepers: Optional[dict[str, int]] = None,
                 excluded: Optional[set[int]] = None) -> list[Action]:
    """Actions moving every non-keeper to Recovery. ``keepers`` overrides keeper per group hash;
    ``excluded`` file ids are left untouched."""
    keepers = keepers or {}
    excluded = excluded or set()
    actions = []
    for g in groups:
        keep_id = keepers.get(g.hash, g.keeper_id)
        keeper = next(f for f in g.files if f["id"] == keep_id)
        kpath = str(lib.abspath(keeper["rel_path"]))
        for f in g.files:
            if f["id"] == keep_id or f["id"] in excluded:
                continue
            actions.append(Action(op="recycle", src=str(lib.abspath(f["rel_path"])), size=f["size"],
                                  mtime=f["mtime"], hash=g.hash, guards=[(kpath, g.hash)],
                                  reason=f"Duplicate of {keeper['rel_path']}", file_id=f["id"]))
    return actions
