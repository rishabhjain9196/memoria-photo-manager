"""Tidy: system junk, empty files, empty folders, unreadable media and non-media files."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from . import config, roots
from .actions import Action
from .db import Library
from .progress import Progress
from .scanner import walk_dirs

CATEGORIES = {
    "junk": ("System and app leftovers", "Thumbs.db, desktop.ini, .DS_Store, ._ files, temporary downloads", True),
    "empty": ("Empty files", "Files with 0 bytes — nothing to lose", True),
    "unreadable": ("Photos and videos with analysis errors",
                   "A codec, access or file problem; not proof of damage. Select a file to review its error.", False),
    "other": ("Non-photo files", "Documents and other files mixed into the library", False),
    "folders": ("Empty folders", "Folders left with nothing in them", True),
}


@dataclass
class TidyReport:
    items: dict[str, list[dict]] = field(default_factory=dict)
    protected_sidecars: int = 0

    def count(self, cat: str) -> int:
        return len(self.items.get(cat, []))

    def size(self, cat: str) -> int:
        return sum(i.get("size") or 0 for i in self.items.get(cat, []))


def is_junk(name: str) -> bool:
    n = name.lower()
    return n in config.JUNK_NAMES or os.path.splitext(n)[1] in config.JUNK_EXT or n.startswith(config.JUNK_PREFIXES)


def is_apple_edit_sidecar(path: str) -> bool:
    return os.path.splitext(path)[1].lower() == ".aae"


def find_tidy(lib: Library, progress: Progress | None = None) -> TidyReport:
    progress = progress or Progress()
    progress.update(0, 2, "Looking for leftovers…")
    rep = TidyReport({k: [] for k in CATEGORIES})
    for r in lib.readable_files():
        r = dict(r)
        if is_apple_edit_sidecar(r["rel_path"]):
            rep.protected_sidecars += 1
        elif is_junk(r["name"]):
            rep.items["junk"].append(r)
        elif r["size"] == 0:
            rep.items["empty"].append(r)
        elif r["kind"] != "other" and r["error"]:
            rep.items["unreadable"].append(r)
        elif r["kind"] == "other":
            rep.items["other"].append(r)
    progress.update(1, 2, "Looking for empty folders…")
    rep.items["folders"] = empty_folders(lib, {r["rel_path"].lower() for c in ("junk", "empty")
                                                for r in rep.items[c]})
    progress.update(2, 2, "Done", force=True)
    return rep


def empty_folders(lib: Library, removing: set[str]) -> list[dict]:
    """Folders with no remaining files once ``removing`` (lower-case rel paths) are gone."""
    counts: dict[str, int] = {}
    for r in lib.files():
        if r["rel_path"].lower() in removing:
            continue
        folder = r["folder"].lower()
        while folder:
            counts[folder] = counts.get(folder, 0) + 1
            folder = os.path.dirname(folder)
    out = []
    for source in lib.roots():
        if not source["online"]:
            continue
        root = source["path"]
        for d in walk_dirs(Path(root)):
            rel = roots.key_for(source["id"], d[len(root) + 1:])
            if counts.get(rel.lower(), 0) == 0:
                out.append({"rel_path": rel, "name": os.path.basename(rel), "size": 0, "folder": os.path.dirname(rel)})
    out.sort(key=lambda x: -x["rel_path"].count(os.sep))  # deepest first so parents empty out
    return out


def plan_actions(lib: Library, report: TidyReport, selected: dict[str, list[dict]]) -> list[Action]:
    """``selected`` maps category → chosen items. Files are recycled first, then folders removed."""
    actions = []
    for cat in ("junk", "empty", "unreadable", "other"):
        for r in selected.get(cat, []):
            if is_apple_edit_sidecar(r["rel_path"]):
                raise ValueError("Apple .AAE edit sidecars are protected from Tidy up. "
                                 "Keep them with your photos. Nothing was moved.")
            actions.append(Action(op="recycle", src=str(lib.abspath(r["rel_path"])), size=r["size"],
                                  mtime=r["mtime"], reason=CATEGORIES[cat][0], file_id=r["id"]))
    folders = sorted(selected.get("folders", []), key=lambda x: -x["rel_path"].count(os.sep))
    for f in folders:
        actions.append(Action(op="rmdir", src=str(lib.abspath(f["rel_path"])), reason="Empty folder"))
    return actions
