"""Where a photo's date comes from, beyond the camera's own EXIF date.

Order of trust, best first:

- ``manual``    set by the user in Memoria (kept across rescans until cleared)
- ``exif``      camera date inside the photo
- ``metadata``  date inside a video, or an embedded XMP/PNG creation date
- ``sidecar``   Google Takeout ``.json`` or XMP sidecar file next to the photo
- ``filename``  a date or timestamp in the file name
- ``inferred``  copied from a file with the same name in the same folder that has a reliable date
                (for example the HEIC of a Live Photo, or the original of an edited copy)
- ``modified``  the file's modified time — often the copy/download date, so treated as uncertain
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

LABELS = {"manual": "Set in Memoria", "exif": "Camera date", "metadata": "Embedded date", "sidecar": "Sidecar file",
          "filename": "Date in file name", "inferred": "From matching file", "modified": "File modified date (less reliable)"}
SHORT_LABELS = {"manual": "set in Memoria", "exif": "camera", "metadata": "embedded metadata", "sidecar": "sidecar file",
                "filename": "file name", "inferred": "matching file", "modified": "file date — may be inaccurate"}
SOURCES = frozenset(LABELS)
# Precise enough to group bursts (seconds matter).
PRECISE = ("exif", "metadata", "sidecar", "manual")
# Good enough for albums, timelines and organising by date.
RELIABLE = ("exif", "metadata", "sidecar", "filename", "inferred", "manual")

_MIN_YEAR = 1990


def _plausible(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    return dt if _MIN_YEAR <= dt.year <= datetime.now().year + 1 else None


def _from_epoch(seconds: float) -> Optional[datetime]:
    try:
        return _plausible(datetime.fromtimestamp(seconds))
    except (OverflowError, OSError, ValueError):
        return None


def parse_iso(value: str) -> Optional[datetime]:
    """ISO-8601 / EXIF-style text to a naive local datetime (timezone offsets converted to local time)."""
    s = value.strip().replace("\x00", "")
    m = re.match(r"(\d{4})[-:](\d\d)[-:](\d\d)(?:[T ](\d\d):(\d\d)(?::(\d\d))?(?:\.\d+)?)?\s*(Z|[+-]\d\d:?\d\d)?", s)
    if not m:
        return None
    try:
        dt = datetime(int(m[1]), int(m[2]), int(m[3]), int(m[4] or 0), int(m[5] or 0), int(m[6] or 0))
    except ValueError:
        return None
    if m[7]:
        tz = timezone.utc if m[7] == "Z" else datetime.strptime(m[7].replace(":", ""), "%z").tzinfo
        dt = dt.replace(tzinfo=tz).astimezone().replace(tzinfo=None)
    return _plausible(dt)


# --------------------------------------------------------------------------- embedded XMP / PNG text
_XMP_DATE = re.compile(rb"(?:exif:DateTimeOriginal|photoshop:DateCreated|xmp:CreateDate)"
                       rb"\s*(?:=\s*[\"']|>)\s*(\d{4}-\d\d-\d\d(?:T[\d:.]+(?:Z|[+-]\d\d:?\d\d)?)?)")


def xmp_date(data: bytes, limit: int = 512 * 1024) -> Optional[datetime]:
    """Capture date from an XMP packet embedded in the first ``limit`` bytes of a file."""
    head = data[:limit]
    if b"<x:xmpmeta" not in head and b"xmlns:xmp" not in head:
        return None
    m = _XMP_DATE.search(head)
    return parse_iso(m[1].decode("ascii", "replace")) if m else None


def png_text_date(info: dict) -> Optional[datetime]:
    """PNG ``Creation Time`` / ``date:create`` text chunks (common for screenshots and exports)."""
    for key in ("Creation Time", "creation_time", "date:create"):
        value = info.get(key)
        if isinstance(value, str):
            dt = parse_iso(value)
            if dt:
                return dt
            for fmt in ("%a, %d %b %Y %H:%M:%S", "%d %b %Y %H:%M:%S"):
                try:
                    return _plausible(datetime.strptime(value.strip()[:25].rstrip(" +-0123456789:"), fmt))
                except ValueError:
                    continue
    return None


# --------------------------------------------------------------------------- sidecar files
def _takeout_candidates(path: Path) -> list[Path]:
    """Google Takeout sidecar names for ``path`` (including its 46-character truncation and "(1)" copies)."""
    name, folder = path.name, path.parent
    out = [folder / f"{name}.json", folder / f"{name}.supplemental-metadata.json", folder / f"{path.stem}.json"]
    if len(name) > 46:
        out.append(folder / f"{name[:46]}.json")
    copy = re.match(r"^(.*)\((\d+)\)(\.[^.]+)$", name)
    if copy:  # Takeout names the copy "IMG.jpg(1).json"
        out.append(folder / f"{copy[1]}{copy[3]}({copy[2]}).json")
    return out


def sidecar_date(path: str | Path) -> Optional[datetime]:
    """Date from a Google Takeout JSON or an XMP sidecar next to ``path``; None if there isn't one."""
    path = Path(path)
    for candidate in _takeout_candidates(path):
        try:
            with open(candidate, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError):
            continue
        for key in ("photoTakenTime", "creationTime"):
            stamp = (data.get(key) or {}).get("timestamp") if isinstance(data, dict) else None
            try:
                dt = _from_epoch(float(stamp)) if stamp not in (None, "", "0") else None
            except (TypeError, ValueError):
                dt = None
            if dt:
                return dt
    for candidate in (path.with_suffix(".xmp"), path.parent / f"{path.name}.xmp"):
        try:
            with open(candidate, "rb") as f:
                dt = xmp_date(f.read(256 * 1024))
        except OSError:
            continue
        if dt:
            return dt
    return None


# --------------------------------------------------------------------------- file names
_EPOCH = re.compile(r"(?<!\d)(1[0-9]{9})(\d{3})?(?!\d)")


def epoch_from_filename(name: str) -> Optional[datetime]:
    """Unix timestamps in names such as ``FB_IMG_1577836800000.jpg`` or ``received_1577836800.jpeg``."""
    m = _EPOCH.search(Path(name).stem)
    return _from_epoch(int(m[1])) if m else None


# --------------------------------------------------------------------------- inference
_COPY_SUFFIX = re.compile(r"(?:\s*\(\d+\)|[-_ ](?:edited|edit|copy|bearbeitet|modifi[ée])|~\d+)$", re.I)


def base_stem(name: str) -> str:
    """File stem without copy/edit suffixes, lower-cased: ``IMG_1234 (1)-edited.jpg`` → ``img_1234``."""
    stem = Path(name).stem
    while True:
        shorter = _COPY_SUFFIX.sub("", stem)
        if shorter == stem:
            return stem.lower()
        stem = shorter


def infer_dates(lib, file_ids: Optional[Iterable[int]] = None) -> int:
    """Give files that only have a modified-time date the reliable date of a same-named file in the
    same folder (Live Photo HEIC+MOV, RAW+JPEG, an edited copy and its original). Returns the count."""
    rows = lib.db.execute("SELECT id, folder, name, taken_at, date_source FROM files "
                          "WHERE kind != 'other' AND taken_at IS NOT NULL").fetchall()
    known: dict[tuple[str, str], tuple[int, str]] = {}
    rank = {s: i for i, s in enumerate(PRECISE)}
    for r in rows:
        if r["date_source"] in PRECISE:
            key = ((r["folder"] or "").lower(), base_stem(r["name"]))
            best = known.get(key)
            if best is None or rank[r["date_source"]] < best[0]:
                known[key] = (rank[r["date_source"]], r["taken_at"])
    wanted = set(file_ids) if file_ids is not None else None
    updates = []
    for r in rows:
        if r["date_source"] != "modified" or (wanted is not None and r["id"] not in wanted):
            continue
        found = known.get(((r["folder"] or "").lower(), base_stem(r["name"])))
        if found:
            updates.append((found[1], r["id"]))
    if updates:
        with lib.transaction() as db:
            db.executemany("UPDATE files SET taken_at=?, date_source='inferred' WHERE id=? AND date_source='modified'",
                           updates)
    return len(updates)


# --------------------------------------------------------------------------- manual dates
def set_manual(lib, file_ids: Iterable[int], when: Optional[datetime]) -> int:
    """Set (or, with ``None``, clear) a user-chosen date for files. Clearing re-reads the detected date
    at the next rescan. Only the catalogue changes; the files themselves are never edited."""
    ids = [int(i) for i in file_ids]
    if not ids:
        return 0
    with lib.transaction() as db:
        if when is None:
            db.executemany("UPDATE files SET analyzed=0, date_source=NULL WHERE id=? AND date_source='manual'",
                           [(i,) for i in ids])
        else:
            value = when.replace(microsecond=0).isoformat(sep=" ")
            db.executemany("UPDATE files SET taken_at=?, date_source='manual' WHERE id=?", [(value, i) for i in ids])
    return len(ids)
