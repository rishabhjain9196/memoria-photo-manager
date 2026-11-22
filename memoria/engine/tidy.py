"""Tidy: system junk, empty files, empty folders, unreadable media and non-media files."""
from __future__ import annotations

import os
import re
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
    "orphan_sidecars": ("Edit sidecars without their photo",
                        ".AAE / .XMP files whose photo or video is no longer in the same folder — usually left "
                        "behind by moves or duplicate clean-up. Sidecars next to their photo stay protected.", True),
    "unreadable": ("Photos and videos with analysis errors",
                   "A codec, access or file problem; not proof of damage. Select a file to review its error.", False),
    "other": ("Non-photo files", "Documents and other files mixed into the library", False),
    "folders": ("Empty folders", "Folders left with nothing in them", True),
}
SIDECAR_EXT = {".aae", ".xmp"}
_APPLE_VARIANT = re.compile(r"^(img)_[eo](\d+)$")   # IMG_E1234 (edited render), IMG_O1234 → IMG_1234


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


def _media_stem(name: str) -> str:
    """The photo a file or sidecar belongs to: ``IMG_E1234.HEIC``, ``IMG_1234.AAE`` and ``IMG_1234.JPG.xmp``
    all give ``img_1234``."""
    stem = os.path.splitext(name)[0]
    if os.path.splitext(stem)[1].lower() in config.MEDIA_EXT:   # IMG_1.JPG.xmp
        stem = os.path.splitext(stem)[0]
    stem = stem.lower()
    m = _APPLE_VARIANT.match(stem)
    return f"{m[1]}_{m[2]}" if m else stem


def find_tidy(lib: Library, progress: Progress | None = None) -> TidyReport:
    progress = progress or Progress()
    progress.update(0, 2, "Looking for leftovers…")
    rep = TidyReport({k: [] for k in CATEGORIES})
    rows = [dict(r) for r in lib.readable_files()]
    media = {(r["folder"].lower(), _media_stem(r["name"])) for r in rows
             if (r["kind"] != "other" or os.path.splitext(r["name"])[1].lower() in config.MEDIA_EXT)
             and r["size"] > 0 and not r["name"].startswith("._")}
    for r in rows:
        sidecar = os.path.splitext(r["name"])[1].lower() in SIDECAR_EXT and not r["name"].startswith("._")
        if sidecar and (r["folder"].lower(), _media_stem(r["name"])) not in media:
            rep.items["orphan_sidecars"].append(r)
        elif sidecar or is_apple_edit_sidecar(r["rel_path"]):
            rep.protected_sidecars += is_apple_edit_sidecar(r["rel_path"])
        elif is_junk(r["name"]):
            rep.items["junk"].append(r)
        elif r["size"] == 0:
            rep.items["empty"].append(r)
        elif r["kind"] != "other" and r["error"]:
            rep.items["unreadable"].append(r)
        elif r["kind"] == "other":
            rep.items["other"].append(r)
    progress.update(1, 2, "Looking for empty folders…")
    rep.items["folders"] = empty_folders(lib, {r["rel_path"].lower() for c in ("junk", "empty", "orphan_sidecars")
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
    for cat in ("junk", "empty", "orphan_sidecars", "unreadable", "other"):
        for r in selected.get(cat, []):
            if is_apple_edit_sidecar(r["rel_path"]) and cat != "orphan_sidecars":
                raise ValueError("Apple .AAE edit sidecars are protected from Tidy up. "
                                 "Keep them with your photos. Nothing was moved.")
            actions.append(Action(op="recycle", src=str(lib.abspath(r["rel_path"])), size=r["size"],
                                  mtime=r["mtime"], reason=CATEGORIES[cat][0], file_id=r["id"]))
    folders = sorted(selected.get("folders", []), key=lambda x: -x["rel_path"].count(os.sep))
    for f in folders:
        actions.append(Action(op="rmdir", src=str(lib.abspath(f["rel_path"])), reason="Empty folder"))
    return actions
