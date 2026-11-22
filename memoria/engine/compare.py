"""Compare the library with another folder (backup drive, old laptop copy…) and sync missing files.

Matching is by content, not name, so renamed or re-organised copies still count as present.
The other folder is only read during comparison; it is written to only when syncing into it.
"""
from __future__ import annotations

import os
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from . import config, disk_speed, roots
from .actions import Action
from .db import Library, LibraryUnavailable
from .hashing import full_hash
from .progress import Progress
from .scanner import walk_files


@dataclass
class OtherFile:
    rel_path: str
    size: int
    mtime: float
    hash: Optional[str] = None


@dataclass
class CompareResult:
    other: Path
    only_here: list[dict] = field(default_factory=list)       # library rows (+ "hash")
    only_there: list[OtherFile] = field(default_factory=list)
    in_both: int = 0
    bytes_only_here: int = 0
    bytes_only_there: int = 0


def compare(lib: Library, other: str | Path, progress: Optional[Progress] = None,
            media_only: bool = True) -> CompareResult:
    progress = progress or Progress()
    other = Path(other).resolve()
    for source in lib.roots():
        root = Path(source["path"])
        if other == root or root in other.parents or other in root.parents:
            raise ValueError("Choose a folder outside all this library's media folders (and not containing them).")
        roots.check(lib, source["id"])
    progress.update(0, 0, "Listing files in the other folder…")
    theirs: list[OtherFile] = []
    cut = len(str(other).rstrip(os.sep)) + 1
    failed = []
    for e in walk_files(other, failed=failed):
        ext = os.path.splitext(e.name)[1].lower()
        if media_only and ext not in config.MEDIA_EXT:
            continue
        try:
            st = e.stat(follow_symlinks=False)
        except OSError as e:
            raise LibraryUnavailable(f"Comparison incomplete: could not read a backup file: {e}") from e
        if st.st_size:
            theirs.append(OtherFile(e.path[cut:], st.st_size, st.st_mtime))
    if failed or not other.is_dir():
        raise LibraryUnavailable("Comparison incomplete: the backup folder or one of its subfolders could not "
                                 "be read. Reconnect the drive or check permissions and try again. No sync was planned.")
    ours = [dict(r) for r in lib.files("kind!='other' AND size>0" if media_only else "size>0")]

    # Only files whose size exists on both sides can possibly match → only those are read.
    their_sizes = defaultdict(list)
    for t in theirs:
        their_sizes[t.size].append(t)
    our_sizes = defaultdict(list)
    for r in ours:
        our_sizes[r["size"]].append(r)
    shared = set(their_sizes) & set(our_sizes)
    ours_c = [r for s in shared for r in our_sizes[s]]
    theirs_c = [t for s in shared for t in their_sizes[s]]
    total = len(ours_c) + len(theirs_c) or 1

    _hash_ours(lib, ours_c, progress, total)
    _hash_theirs(other, theirs_c, progress, len(ours_c), total)
    if any(not r.get("chash") for r in ours_c) or any(not t.hash for t in theirs_c):
        raise LibraryUnavailable("Comparison incomplete: some files could not be fingerprinted. "
                                 "Check that both drives are available and try again.")

    our_hashes = {r["chash"] for r in ours_c if r.get("chash")}
    their_hashes = {t.hash for t in theirs_c if t.hash}
    res = CompareResult(other)
    for r in ours:
        if r["size"] in shared and r.get("chash") in their_hashes:
            res.in_both += 1
        else:
            res.only_here.append(r)
            res.bytes_only_here += r["size"]
    for t in theirs:
        if not (t.size in shared and t.hash in our_hashes):
            res.only_there.append(t)
            res.bytes_only_there += t.size
    res.only_here.sort(key=lambda r: r["rel_path"].lower())
    res.only_there.sort(key=lambda t: t.rel_path.lower())
    progress.update(total, total, "Comparison complete", force=True)
    return res


def _hash_ours(lib: Library, rows: list[dict], progress: Progress, total: int) -> None:
    todo = [r for r in rows if not r.get("chash")]

    def work(r):
        return r, full_hash(lib.abspath(r["rel_path"]))

    updates = []
    for i, (r, h) in enumerate(disk_speed.paced_map(work, todo, lambda r: lib.abspath(r["rel_path"]),
                                                    "Hashing library"), 1):
        r["chash"] = h
        if h:
            updates.append((r["id"], None, h))
        progress.update(i, total, f"Reading library files… {i:,} of {len(todo):,}")
    lib.set_hashes(updates)


def _hash_theirs(root: Path, files: list[OtherFile], progress: Progress, offset: int, total: int) -> None:
    def work(t):
        t.hash = full_hash(root / t.rel_path)
        return t

    for i, _ in enumerate(disk_speed.paced_map(work, files, lambda t: root / t.rel_path, "Reading other folder"), 1):
        progress.update(offset + i, total, f"Reading files in the other folder… {i:,} of {len(files):,}")


def plan_sync(lib: Library, result: CompareResult, to_other: list[dict], to_library: list[OtherFile]) -> list[Action]:
    """Copy actions keeping each file's relative path. Copies are verified; nothing is overwritten."""
    actions = []
    for r in to_other:
        actions.append(Action(op="copy", src=str(lib.abspath(r["rel_path"])),
                              dst=str(result.other / lib.export_rel(r["rel_path"])), size=r["size"],
                              mtime=r["mtime"], hash=r.get("chash"), reason=f"Copy to {result.other}"))
    for t in to_library:
        actions.append(Action(op="copy", src=str(result.other / t.rel_path), dst=str(lib.abspath(t.rel_path)),
                              size=t.size, mtime=t.mtime, hash=t.hash, reason=f"Copy from {result.other}"))
    return actions
