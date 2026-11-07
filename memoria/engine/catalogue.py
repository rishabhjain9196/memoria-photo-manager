"""Shared, read-only catalogue filters and bounded aggregates for browsing and Insights."""
from __future__ import annotations

import calendar
import math
from dataclasses import dataclass, replace
from datetime import date, timedelta
from typing import Optional

from . import geography
from .db import Library

PAGE_SIZE = 500
SORTS = {"newest": "NULLIF(f.taken_at,'') IS NULL, f.taken_at DESC, f.rel_path, f.id",
         "oldest": "NULLIF(f.taken_at,'') IS NULL, f.taken_at, f.rel_path, f.id",
         "largest": "f.size DESC, f.rel_path, f.id", "smallest": "f.size, f.rel_path, f.id",
         "name": "f.name COLLATE NOCASE, f.rel_path, f.id",
         "modified_newest": "f.mtime DESC, f.rel_path, f.id", "modified_oldest": "f.mtime, f.rel_path, f.id",
         "format": "f.ext COLLATE NOCASE, f.rel_path, f.id"}
METRICS = {
    "duration": "CASE WHEN f.kind='video' AND f.duration>0 THEN f.duration END",
    "megapixels": "CASE WHEN f.width>0 AND f.height>0 THEN f.width*1.0*f.height/1000000 END",
    "bitrate": "CASE WHEN f.kind='video' AND f.duration>0 THEN f.size*8.0/f.duration/1000000 END",
    "fps": "CASE WHEN f.kind='video' AND f.fps>0 THEN f.fps END",
    "iso": "CASE WHEN f.kind='image' AND f.iso>0 THEN f.iso END",
    "aperture": "CASE WHEN f.kind='image' AND f.aperture>0 THEN f.aperture END",
    "exposure": "CASE WHEN f.kind='image' AND f.exposure_seconds>0 THEN f.exposure_seconds END",
    "focal": "CASE WHEN f.kind='image' AND f.focal_length_mm>0 THEN f.focal_length_mm END",
}
for key, expression in METRICS.items():
    for direction in ("asc", "desc"):
        SORTS[f"{key}_{direction}"] = f"({expression}) IS NULL, ({expression}) {direction.upper()}, f.rel_path, f.id"
for key in ("camera", "lens", "video_codec", "audio_codec"):
    SORTS[key] = f"NULLIF(f.{key},'') IS NULL, f.{key} COLLATE NOCASE, f.rel_path, f.id"
SORTS["audio_codec"] = ("(f.kind!='video' OR f.audio_codec IS NULL), "
                        "f.audio_codec COLLATE NOCASE, f.rel_path, f.id")
GPS = "f.lat BETWEEN -90 AND 90 AND f.lon BETWEEN -180 AND 180"


@dataclass(frozen=True)
class Filters:
    folder: str = ""
    recursive: bool = True
    kind: str = "media"
    extension: Optional[str] = None
    search: str = ""
    start: Optional[str] = None
    end: Optional[str] = None  # exclusive
    undated: bool = False
    min_bytes: int = 0
    max_bytes: Optional[int] = None
    location: str = "all"  # all / gps / none
    bbox: Optional[tuple[float, float, float, float]] = None
    faces: str = "all"  # all / any / none / unscanned
    person: Optional[int] = None
    orientation: str = "all"
    camera: Optional[str] = None
    lens: Optional[str] = None
    video_codec: Optional[str] = None
    audio_codec: Optional[str] = None
    min_width: int = 0
    min_height: int = 0
    min_duration: Optional[float] = None
    max_duration: Optional[float] = None
    min_megapixels: Optional[float] = None
    max_megapixels: Optional[float] = None
    min_bitrate: Optional[float] = None
    max_bitrate: Optional[float] = None
    min_fps: Optional[float] = None
    max_fps: Optional[float] = None
    min_iso: Optional[float] = None
    max_iso: Optional[float] = None
    min_aperture: Optional[float] = None
    max_aperture: Optional[float] = None
    min_exposure: Optional[float] = None
    max_exposure: Optional[float] = None
    min_focal: Optional[float] = None
    max_focal: Optional[float] = None


def where(filters: Filters) -> tuple[str, list]:
    f = filters
    clauses, params = [], []
    if f.kind in ("media", "image", "video"):
        clauses += ["f.kind IN ('image','video')" if f.kind == "media" else "f.kind=?",
                    "f.error IS NULL"]
        if f.kind != "media":
            params.append(f.kind)
    elif f.kind == "problems":
        clauses += ["f.kind IN ('image','video')", "f.error IS NOT NULL"]
    elif f.kind == "other":
        clauses.append("f.kind='other'")
    elif f.kind != "all":
        raise ValueError(f"Unknown media type: {f.kind}")
    if f.folder or not f.recursive:
        if f.recursive:
            prefix = f.folder.rstrip("\\") + "\\"
            clauses.append("(f.folder=? COLLATE NOCASE OR substr(f.folder,1,?)=? COLLATE NOCASE)")
            params += [f.folder, len(prefix), prefix]
        else:
            clauses.append("f.folder=? COLLATE NOCASE")
            params.append(f.folder)
    if f.extension is not None:
        clauses.append("f.ext=? COLLATE NOCASE")
        params.append(f.extension)
    if f.search.strip():
        clauses.append("(instr(lower(f.rel_path),?)>0 OR instr(lower(COALESCE(f.camera,'')),?)>0 OR "
                       "EXISTS (SELECT 1 FROM faces x JOIN people p ON p.id=x.person_id "
                       "WHERE x.file_id=f.id AND x.ignored=0 AND instr(lower(p.name),?)>0))")
        params += [f.search.strip().lower()] * 3
    if f.start and f.end and f.start >= f.end:
        raise ValueError("The end date must be after the start date.")
    for bound, operator in ((f.start, ">="), (f.end, "<")):
        if bound:
            date.fromisoformat(bound)
            clauses.append(f"f.taken_at {operator} ?")
            params.append(bound)
    if f.undated:
        clauses.append("(f.taken_at IS NULL OR f.taken_at='')")
    if f.min_bytes < 0 or f.max_bytes is not None and f.max_bytes < f.min_bytes:
        raise ValueError("Choose a non-negative size range with maximum at least minimum.")
    clauses.append("f.size>=?")
    params.append(f.min_bytes)
    if f.max_bytes is not None:
        clauses.append("f.size<=?")
        params.append(f.max_bytes)
    if f.location == "gps" or f.bbox is not None:
        if f.location == "none":
            raise ValueError("Clear the selected map area before choosing files without GPS.")
        clauses.append(GPS)
    elif f.location == "none":
        clauses.append(f"NOT COALESCE(({GPS}),0)")
    elif f.location != "all":
        raise ValueError(f"Unknown location filter: {f.location}")
    if f.bbox is not None:
        south, north, west, east = f.bbox
        if not (-90 <= south <= north <= 90 and -180 <= west <= east <= 180):
            raise ValueError("Invalid GPS bounds.")
        clauses.append("f.lat BETWEEN ? AND ? AND f.lon BETWEEN ? AND ?")
        params += [south, north, west, east]
    if f.faces == "any":
        clauses.append("EXISTS (SELECT 1 FROM faces x WHERE x.file_id=f.id AND x.ignored=0)")
    elif f.faces == "none":
        clauses.append("EXISTS (SELECT 1 FROM face_scans x WHERE x.file_id=f.id AND x.faces=0 "
                       "AND x.size=f.size AND x.mtime=f.mtime)")
    elif f.faces == "unscanned":
        clauses.append("f.kind='image' AND NOT EXISTS (SELECT 1 FROM face_scans x WHERE x.file_id=f.id "
                       "AND x.size=f.size AND x.mtime=f.mtime)")
    elif f.faces != "all":
        raise ValueError(f"Unknown face filter: {f.faces}")
    if f.person is not None:
        clauses.append("EXISTS (SELECT 1 FROM faces x WHERE x.file_id=f.id AND x.person_id=? AND x.ignored=0)")
        params.append(f.person)
    for key in ("camera", "lens", "video_codec", "audio_codec"):
        value = getattr(f, key)
        if value is not None:
            clauses.append(f"f.{key}=? COLLATE NOCASE")
            params.append(value)
            if key.endswith("codec"):
                clauses.append("f.kind='video'")
    for key in ("width", "height"):
        value = getattr(f, f"min_{key}")
        if value < 0:
            raise ValueError("Minimum dimensions cannot be negative.")
        if value:
            clauses.append(f"f.{key}>=?")
            params.append(value)
    if f.orientation != "all":
        if f.orientation not in ("landscape", "portrait", "square"):
            raise ValueError("Unknown orientation.")
        operator = {"landscape": ">", "portrait": "<", "square": "="}[f.orientation]
        clauses += ["f.width>0 AND f.height>0", f"f.width {operator} f.height"]
    for key, expression in METRICS.items():
        low, high = getattr(f, f"min_{key}"), getattr(f, f"max_{key}")
        if any(value is not None and (not math.isfinite(value) or value < 0) for value in (low, high)) or (
                low is not None and high is not None and low > high):
            raise ValueError(f"Choose a valid minimum/maximum for {key}.")
        for value, operator in ((low, ">="), (high, "<=")):
            if value is not None:
                clauses.append(f"({expression}) {operator} ?")
                params.append(value)
    return " AND ".join(clauses), params


def overall_bitrate(row) -> Optional[float]:
    """Estimated overall Mbps, including audio/container bytes, not a video quality score."""
    duration = row.get("duration")
    if row.get("kind") == "video" and duration and duration > 0:
        return row["size"] * 8 / duration / 1_000_000
    return None


def page(lib: Library, filters: Filters, sort: str = "newest", offset: int = 0) -> tuple[list[dict], int, int]:
    if sort not in SORTS or offset < 0:
        raise ValueError("Invalid sort or page offset.")
    sql, params = where(filters)
    count, size = lib.db.execute(f"SELECT COUNT(*),COALESCE(SUM(size),0) FROM files f WHERE {sql}", params).fetchone()
    rows = lib.db.execute(f"SELECT f.* FROM files f WHERE {sql} ORDER BY {SORTS[sort]} LIMIT ? OFFSET ?",
                          [*params, PAGE_SIZE, offset]).fetchall()
    return [dict(row) for row in rows], count, size


def folders(lib: Library) -> list[str]:
    out = {""}
    for row in lib.db.execute("SELECT DISTINCT folder FROM files"):
        parts = row[0].split("\\") if row[0] else []
        out.update("\\".join(parts[:i]) for i in range(1, len(parts) + 1))
    return sorted(out, key=str.casefold)


def distribution(lib: Library, filters: Filters) -> dict:
    sql, params = where(filters)
    children = {}
    for row in lib.db.execute(f"SELECT f.folder,COUNT(*) AS count,SUM(f.size) AS bytes FROM files f "
                              f"WHERE {sql} GROUP BY f.folder", params):
        relative = row["folder"][len(filters.folder):].lstrip("\\")
        child = (filters.folder + "\\" if filters.folder else "") + relative.split("\\")[0] if relative else filters.folder
        key = (child, not bool(relative))
        item = children.setdefault(key, {"key": child, "direct": not bool(relative),
                                         "label": "(Files directly here)" if not relative else relative.split("\\")[0],
                                         "count": 0, "bytes": 0})
        item["count"] += row["count"]
        item["bytes"] += row["bytes"]
    types = [dict(row) for row in lib.db.execute(
        f"SELECT f.ext AS key, f.ext AS label,COUNT(*) AS count,SUM(f.size) AS bytes FROM files f "
        f"WHERE {sql} GROUP BY f.ext ORDER BY bytes DESC, f.ext", params)]
    return {"folders": sorted(children.values(), key=lambda r: (-r["bytes"], r["key"])), "types": types,
            "count": sum(r["count"] for r in types), "bytes": sum(r["bytes"] for r in types)}


def period(prefix: str) -> tuple[Optional[str], Optional[str]]:
    if not prefix:
        return None, None
    if len(prefix) == 4:
        start = date(int(prefix), 1, 1)
        end = date(start.year + 1, 1, 1)
    elif len(prefix) == 7:
        start = date.fromisoformat(prefix + "-01")
        end = start + timedelta(days=calendar.monthrange(start.year, start.month)[1])
    elif len(prefix) == 10:
        start = date.fromisoformat(prefix)
        end = start + timedelta(days=1)
    else:
        raise ValueError("Choose a year, month or day.")
    return start.isoformat(), end.isoformat()


def in_period(filters: Filters, prefix: str) -> Filters:
    start, end = period(prefix)
    return replace(filters, start=max(filter(None, (filters.start, start)), default=None),
                   end=min(filter(None, (filters.end, end)), default=None))


def timeline(lib: Library, filters: Filters, prefix: str = "") -> list[dict]:
    sql, params = where(in_period(filters, prefix))
    length = 4 if not prefix else 7 if len(prefix) == 4 else 10
    return [dict(row) for row in lib.db.execute(
        f"SELECT substr(f.taken_at,1,?) AS key,COUNT(*) AS count,SUM(f.size) AS bytes FROM files f WHERE {sql} "
        "AND f.kind IN ('image','video') AND f.taken_at IS NOT NULL AND f.taken_at!='' "
        "GROUP BY key ORDER BY key", [length, *params])]


def matching_albums(lib: Library, filters: Filters) -> list[dict]:
    sql, params = where(filters)
    return [dict(row) for row in lib.db.execute(
        f"SELECT a.id,a.name,COUNT(*) AS count FROM albums a JOIN album_items i ON i.album_id=a.id "
        f"JOIN files f ON f.id=i.file_id WHERE {sql} GROUP BY a.id ORDER BY count DESC,a.name", params)]


def map_data(lib: Library, filters: Filters, bounds=None) -> dict:
    geography.countries()  # Validate the bundled map before the UI attempts to paint it.
    sql, params = where(filters)
    sql += f" AND f.kind IN ('image','video') AND {GPS}"
    gps_count = lib.db.execute(f"SELECT COUNT(*) FROM files f WHERE {sql}", params).fetchone()[0]
    if bounds is None:
        domestic = all(geography.in_india(r[0], r[1]) for r in
                       lib.db.execute(f"SELECT DISTINCT f.lat,f.lon FROM files f WHERE {sql}", params))
        bounds = geography.INDIA if domestic else geography.WORLD
    south, north, west, east = bounds
    if not (-90 <= south < north <= 90 and -180 <= west < east <= 180):
        raise ValueError("Invalid map viewport.")
    cells = [dict(row) for row in lib.db.execute(
        f"SELECT CAST((f.lon-?)/? AS INTEGER) AS x,CAST((f.lat-?)/? AS INTEGER) AS y,"
        "AVG(f.lat) AS lat,AVG(f.lon) AS lon,MIN(f.lat) AS south,MAX(f.lat) AS north,"
        f"MIN(f.lon) AS west,MAX(f.lon) AS east,COUNT(*) AS count FROM files f WHERE {sql} "
        "AND f.lat BETWEEN ? AND ? AND f.lon BETWEEN ? AND ? GROUP BY x,y",
        [west, (east - west) / 64, south, (north - south) / 40, *params, south, north, west, east])]
    return {"bounds": bounds, "cells": cells, "gps_count": gps_count,
            "visible_count": sum(c["count"] for c in cells)}
