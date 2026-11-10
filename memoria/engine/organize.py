"""Organise photos into date folders. Produces a reviewable plan of moves inside the library."""
from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from .actions import Action
from .roots import key_for, split_key
from .db import Library
from .progress import Progress

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
          "October", "November", "December"]

PATTERNS = {
    "year_month": ("{year}\\{year}-{month}", "2024\\2024-07"),
    "year_monthname": ("{year}\\{month} {month_name}", "2024\\07 July"),
    "year_month_day": ("{year}\\{year}-{month}-{day}", "2024\\2024-07-21"),
    "year": ("{year}", "2024"),
}

SOURCE_LABEL = {"exif": "Camera date", "metadata": "Video date", "filename": "Date in file name",
                "modified": "File modified date (less reliable)"}


@dataclass
class OrganizeItem:
    row: dict
    dst_rel: str
    taken_at: datetime
    source: str

    @property
    def src_rel(self) -> str:
        return self.row["rel_path"]


@dataclass
class OrganizePlan:
    items: list[OrganizeItem]
    already_in_place: int
    skipped_uncertain: int
    pattern: str


def folder_for(dt: datetime, pattern_id: str) -> str:
    fmt = PATTERNS[pattern_id][0]
    return fmt.format(year=f"{dt.year:04d}", month=f"{dt.month:02d}", day=f"{dt.day:02d}",
                      month_name=MONTHS[dt.month - 1])


def plan_organize(lib: Library, pattern_id: str = "year_month", include_uncertain: bool = False,
                  root_subfolder: str = "", progress: Optional[Progress] = None) -> OrganizePlan:
    """Plan moves for media files into date folders.

    Files whose only date is the file-modified time are skipped unless ``include_uncertain``
    (copies and downloads reset that date, so it is often wrong).
    """
    progress = progress or Progress()
    progress.update(0, 0, "Reading dates…")
    rows = [dict(r) for r in lib.readable_files("kind!='other' AND taken_at IS NOT NULL AND error IS NULL AND size>0")
            if not r["name"].startswith("._")]
    taken: set[str] = {r["rel_path"].lower() for r in lib.files()}
    items, in_place, uncertain = [], 0, 0
    for n, r in enumerate(rows, 1):
        if n % 2000 == 0:
            progress.update(n, len(rows), f"Planning… {n:,} of {len(rows):,}")
        if r["date_source"] == "modified" and not include_uncertain:
            uncertain += 1
            continue
        dt = datetime.fromisoformat(r["taken_at"])
        folder = os.path.join(root_subfolder, folder_for(dt, pattern_id)) if root_subfolder else folder_for(dt, pattern_id)
        folder = key_for(r["root_id"], folder)
        if r["folder"].lower() == folder.lower():
            in_place += 1
            continue
        dst = os.path.join(folder, r["name"])
        if dst.lower() in taken:
            stem, ext = os.path.splitext(r["name"])
            i = 2
            while os.path.join(folder, f"{stem} ({i}){ext}").lower() in taken:
                i += 1
            dst = os.path.join(folder, f"{stem} ({i}){ext}")
        taken.add(dst.lower())
        items.append(OrganizeItem(r, dst, dt, r["date_source"]))
    items.sort(key=lambda it: (it.dst_rel.lower()))
    progress.update(len(rows), len(rows), "Plan ready", force=True)
    return OrganizePlan(items, in_place, uncertain, pattern_id)


def plan_actions(lib: Library, items: list[OrganizeItem]) -> list[Action]:
    return [Action(op="move", src=str(lib.abspath(it.src_rel)), dst=str(lib.abspath(it.dst_rel)),
                   size=it.row["size"], mtime=it.row["mtime"], file_id=it.row["id"],
                   reason=f"{SOURCE_LABEL.get(it.source, it.source)}: {it.taken_at:%d %b %Y}")
            for it in items]


def empty_folders_after(lib: Library, items: list[OrganizeItem]) -> list[str]:
    """Folders (and their parents) left with nothing in them once the planned moves are done."""
    moving = {it.src_rel.lower() for it in items}
    remaining: dict[str, int] = {}

    def add(folder: str) -> None:
        while folder:
            remaining[folder] = remaining.get(folder, 0) + 1
            folder = os.path.dirname(folder)

    for r in lib.files():
        if r["rel_path"].lower() not in moving:
            add(r["folder"].lower())
    for it in items:
        add(os.path.dirname(it.dst_rel).lower())
    candidates: set[str] = set()
    for m in moving:
        folder = os.path.dirname(m)
        while folder:
            candidates.add(folder)
            folder = os.path.dirname(folder)
    real = {}
    for it in items:
        folder = os.path.dirname(it.src_rel)
        while folder:
            real.setdefault(folder.lower(), folder)
            folder = os.path.dirname(folder)
    return sorted((real[c] for c in candidates if remaining.get(c, 0) == 0 and split_key(real[c])[1]),
                  key=lambda f: (-f.count(os.sep), f))
