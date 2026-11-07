"""Albums: named sets of photos and videos, kept in the catalogue — no file is moved or copied.

Album suggestions come from when photos were taken (events and trips), where (offline place names)
and who is in them (named people). Exporting copies albums into folders with verified copies,
journaled so History can undo it.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, Optional

from . import config, duplicates, faces, places
from .actions import Action
from .db import Library
from .progress import Progress

RELIABLE = ("exif", "metadata", "filename")
_SCREENSHOT = re.compile(r"screen ?shot|screen_\d|screenrecord", re.I)
_BAD_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


@dataclass
class Suggestion:
    name: str
    kind: str                      # "event" | "place" | "person"
    file_ids: list[int]
    start: Optional[str] = None
    end: Optional[str] = None
    place: Optional[str] = None
    exists: bool = False           # a saved album already holds exactly these items
    detail: str = ""

    @property
    def cover_id(self) -> int:
        return self.file_ids[len(self.file_ids) // 3] if self.file_ids else 0


@dataclass
class EventOptions:
    gap_hours: float = 8.0         # a pause this long starts a new event…
    trip_days: float = 3.0         # …unless the photos stay in one place (a trip) and the pause is shorter than this
    place_km: float = 40.0
    min_items: int = 3
    include_videos: bool = True


# ----------------------------------------------------------------------------- helpers
def _dt(s: str) -> datetime:
    return datetime.fromisoformat(s[:19])


def date_range(start: str, end: str) -> str:
    """"25 Dec 2019", "14–16 Mar 2021", "28 Jun – 2 Jul 2023", "Dec 2019 – Jan 2020"."""
    a, b = _dt(start), _dt(end)
    if a.date() == b.date():
        return f"{a.day} {a:%b %Y}"
    if (a.year, a.month) == (b.year, b.month):
        return f"{a.day}–{b.day} {a:%b %Y}"
    if a.year == b.year:
        return f"{a.day} {a:%b} – {b.day} {b:%b %Y}"
    return f"{a:%b %Y} – {b:%b %Y}"


def _year_span(start: str, end: str) -> str:
    a, b = start[:4], end[:4]
    return a if a == b else f"{a}–{b}"


class _PlaceCache:
    def __init__(self):
        self._c: dict[tuple[float, float], Optional[places.Place]] = {}

    def __call__(self, lat, lon) -> Optional[places.Place]:
        if lat is None or lon is None:
            return None
        k = (round(lat, 2), round(lon, 2))
        if k not in self._c:
            self._c[k] = places.nearest(lat, lon)
        return self._c[k]


def _candidates(lib: Library, include_videos: bool = True, progress: Optional[Progress] = None) -> list[dict]:
    """Dated photos (and videos) worth putting in albums: no screenshots, no damaged files, and one
    copy of each exact duplicate."""
    kinds = "('image','video')" if include_videos else "('image')"
    rows = [dict(r) for r in lib.files(f"kind IN {kinds} AND error IS NULL AND size>0 AND taken_at IS NOT NULL "
                                       f"AND date_source IN {RELIABLE}", order="taken_at, rel_path")]
    rows = [r for r in rows if not _SCREENSHOT.search(r["name"]) and not _SCREENSHOT.search(r["folder"])]
    drop = set()
    for members in duplicates.confirm_identical(lib, rows, progress, "Skipping exact copies").values():
        keep = min(members, key=duplicates.keeper_score)
        drop.update(m["id"] for m in members if m["id"] != keep["id"])
    return [r for r in rows if r["id"] not in drop]


def _place_name(items: list[dict], where: _PlaceCache) -> Optional[str]:
    labels = [p.label for p in (where(r["lat"], r["lon"]) for r in items) if p]
    if not labels or len(labels) * 3 < len(items):
        return None
    return Counter(labels).most_common(1)[0][0]


def _mark_existing(lib: Library, out: list[Suggestion]) -> list[Suggestion]:
    saved = {frozenset(r[1].split(",")) for r in lib.db.execute(
        "SELECT album_id, GROUP_CONCAT(file_id) FROM album_items GROUP BY album_id") if r[1]}
    for s in out:
        s.exists = frozenset(str(i) for i in s.file_ids) in saved
    return out


# ----------------------------------------------------------------------------- suggestions
def suggest_events(lib: Library, opts: Optional[EventOptions] = None,
                   progress: Optional[Progress] = None) -> list[Suggestion]:
    """Photos taken close together in time become one album; a trip (photos in one place over a few
    days) stays together through the nights. Named after the place when known, and the dates."""
    opts = opts or EventOptions()
    rows = _candidates(lib, opts.include_videos, progress)
    where = _PlaceCache()
    events: list[list[dict]] = []
    cur: list[dict] = []
    last_place: Optional[places.Place] = None
    for r in rows:
        p = where(r["lat"], r["lon"])
        if cur:
            gap = _dt(r["taken_at"]) - _dt(cur[-1]["taken_at"])
            same_place = (p is not None and last_place is not None and
                          places.distance_km(p.lat, p.lon, last_place.lat, last_place.lon) <= opts.place_km)
            if gap > timedelta(hours=opts.gap_hours) and not (same_place and gap <= timedelta(days=opts.trip_days)):
                events.append(cur)
                cur, last_place = [], None
        cur.append(r)
        last_place = p or last_place
    if cur:
        events.append(cur)
    out = []
    for ev in events:
        if len(ev) < opts.min_items:
            continue
        start, end = ev[0]["taken_at"], ev[-1]["taken_at"]
        place = _place_name(ev, where)
        when = date_range(start, end)
        photos = sum(r["kind"] == "image" for r in ev)
        out.append(Suggestion(f"{place} · {when}" if place else when, "event", [r["id"] for r in ev], start, end,
                              place, detail=f"{photos} photos, {len(ev) - photos} videos"))
    return _mark_existing(lib, out)


def suggest_places(lib: Library, min_items: int = 3, include_videos: bool = True,
                   progress: Optional[Progress] = None) -> list[Suggestion]:
    """One album per place (nearest town or region), across all years."""
    where = _PlaceCache()
    by: dict[str, list[dict]] = {}
    for r in _candidates(lib, include_videos, progress):
        p = where(r["lat"], r["lon"])
        if p:
            by.setdefault(p.label, []).append(r)
    out = []
    for label, items in sorted(by.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        if len(items) < min_items:
            continue
        start, end = items[0]["taken_at"], items[-1]["taken_at"]
        out.append(Suggestion(label, "place", [r["id"] for r in items], start, end, label,
                              detail=f"{len(items)} items, {_year_span(start, end)}"))
    return _mark_existing(lib, out)


def suggest_people(lib: Library, min_items: int = 1) -> list[Suggestion]:
    """One album per named person (name people on the People page first)."""
    out = []
    for g in faces.groups(lib):
        if not g.named:
            continue
        rows = sorted(faces.photos_of(lib, g.key), key=lambda r: (r["taken_at"] or "", r["rel_path"]))
        if len(rows) < min_items:
            continue
        dated = [r["taken_at"] for r in rows if r["taken_at"]]
        out.append(Suggestion(g.name, "person", [r["id"] for r in rows], min(dated, default=None),
                              max(dated, default=None), detail=f"{len(rows)} photos"))
    return _mark_existing(lib, out)


# ----------------------------------------------------------------------------- saved albums
def _unique_name(lib: Library, name: str, skip: Optional[int] = None) -> str:
    taken = {r[0].lower() for r in lib.db.execute("SELECT name FROM albums WHERE id IS NOT ?", (skip,))}
    base, n, out = name, 2, name
    while out.lower() in taken:
        out = f"{base} ({n})"
        n += 1
    return out


def create(lib: Library, name: str, file_ids: Iterable[int], kind: str = "manual") -> int:
    name = " ".join(name.split()) or "Untitled album"
    ids = list(dict.fromkeys(file_ids))
    with lib.transaction() as tx:
        aid = tx.execute("INSERT INTO albums (name, kind, created_at, cover_id) VALUES (?,?,?,?)",
                         (_unique_name(lib, name), kind, datetime.now().isoformat(sep=" ", timespec="seconds"),
                          ids[len(ids) // 3] if ids else None)).lastrowid
        tx.executemany("INSERT OR IGNORE INTO album_items (album_id, file_id, pos) VALUES (?,?,?)",
                       [(aid, f, i) for i, f in enumerate(ids)])
    return aid


def save(lib: Library, suggestions: Iterable[Suggestion]) -> list[int]:
    return [create(lib, s.name, s.file_ids, s.kind) for s in suggestions]


def albums(lib: Library) -> list[dict]:
    """Saved albums with live item counts, date range and cover, newest content first."""
    out = []
    for r in lib.db.execute(
            "SELECT a.id, a.name, a.kind, a.created_at, a.cover_id, COUNT(f.id) AS items, "
            "SUM(f.kind='image') AS photos, SUM(f.kind='video') AS videos, SUM(f.size) AS bytes, "
            "MIN(f.taken_at) AS start, MAX(f.taken_at) AS end, MIN(f.id) AS any_id "
            "FROM albums a LEFT JOIN album_items i ON i.album_id=a.id LEFT JOIN files f ON f.id=i.file_id "
            "GROUP BY a.id ORDER BY COALESCE(MAX(f.taken_at), '') DESC, a.name"):
        d = dict(r)
        alive = lib.db.execute("SELECT 1 FROM files WHERE id=?", (d["cover_id"],)).fetchone() if d["cover_id"] else None
        d["cover"] = d["cover_id"] if alive else d["any_id"]
        d["photos"], d["videos"], d["bytes"] = d["photos"] or 0, d["videos"] or 0, d["bytes"] or 0
        out.append(d)
    return out


def items(lib: Library, album_id: int) -> list[dict]:
    return [dict(r) for r in lib.db.execute(
        "SELECT f.* FROM album_items i JOIN files f ON f.id=i.file_id WHERE i.album_id=? "
        "ORDER BY COALESCE(f.taken_at, ''), i.pos", (album_id,))]


def rename(lib: Library, album_id: int, name: str) -> str:
    name = " ".join(name.split())
    if not name:
        raise ValueError("Type a name.")
    name = _unique_name(lib, name, skip=album_id)
    lib.db.execute("UPDATE albums SET name=? WHERE id=?", (name, album_id))
    return name


def add(lib: Library, album_id: int, file_ids: Iterable[int]) -> int:
    start = lib.db.execute("SELECT COALESCE(MAX(pos), -1) + 1 FROM album_items WHERE album_id=?", (album_id,)).fetchone()[0]
    with lib.transaction() as tx:
        before = tx.total_changes
        tx.executemany("INSERT OR IGNORE INTO album_items (album_id, file_id, pos) VALUES (?,?,?)",
                       [(album_id, f, start + i) for i, f in enumerate(file_ids)])
        return tx.total_changes - before


def remove(lib: Library, album_id: int, file_ids: Iterable[int]) -> None:
    """Take items out of an album (the files themselves are not touched)."""
    with lib.transaction() as tx:
        tx.executemany("DELETE FROM album_items WHERE album_id=? AND file_id=?", [(album_id, f) for f in file_ids])


def set_cover(lib: Library, album_id: int, file_id: int) -> None:
    lib.db.execute("UPDATE albums SET cover_id=? WHERE id=?", (file_id, album_id))


def delete(lib: Library, album_ids: Iterable[int]) -> None:
    """Delete albums (only the album — its photos and videos stay exactly where they are)."""
    with lib.transaction() as tx:
        for a in album_ids:
            tx.execute("DELETE FROM album_items WHERE album_id=?", (a,))
            tx.execute("DELETE FROM albums WHERE id=?", (a,))


def cleanup(lib: Library) -> None:
    """Drop album entries of files that are gone for good (files in Recovery keep theirs, for Undo)."""
    lib.db.execute("DELETE FROM album_items WHERE file_id NOT IN "
                   "(SELECT id FROM files UNION SELECT file_id FROM parked_files UNION SELECT file_id FROM missing_files)")


# ----------------------------------------------------------------------------- export
def folder_name(name: str) -> str:
    """A Windows-safe folder name for an album."""
    s = _BAD_CHARS.sub("-", name).strip().rstrip(". ")
    if s.upper().split(".")[0] in {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)),
                                   *(f"LPT{i}" for i in range(1, 10))}:
        s = "_" + s
    return s[:120] or "Album"


def plan_export(lib: Library, album_ids: Iterable[int], dest: str | Path) -> list[Action]:
    """Verified copies of each album into ``dest\\<album name>``. Nothing is overwritten (names get a
    number); originals are not touched."""
    dest = Path(dest).resolve()
    if config.APP_DIR_NAME in dest.parts:
        raise ValueError("Choose a folder outside Memoria's own .memoria folder.")
    acts, used = [], set()
    names = {r["id"]: r["name"] for r in lib.db.execute("SELECT id, name FROM albums")}
    for aid in album_ids:
        base = folder_name(names.get(aid, "Album"))
        sub, n = base, 2
        while sub.lower() in used:
            sub = f"{base} ({n})"
            n += 1
        used.add(sub.lower())
        for r in items(lib, aid):
            acts.append(Action(op="copy", src=str(lib.abspath(r["rel_path"])), dst=str(dest / sub / r["name"]),
                               size=r["size"], hash=r.get("chash"), reason=f"Album “{names.get(aid)}” exported"))
    return acts


def inside_library(lib: Library, dest: str | Path) -> bool:
    try:
        Path(dest).resolve().relative_to(lib.root)
        return True
    except ValueError:
        return False
