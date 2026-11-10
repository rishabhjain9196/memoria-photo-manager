"""Shared, read-only catalogue filters and bounded aggregates for browsing and Insights."""
from __future__ import annotations

import calendar
import math
import json
from dataclasses import asdict, dataclass, fields, replace
from datetime import date, timedelta
from typing import Optional

from . import geography, places
from .db import Library, METADATA_VERSION

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
RATING = "COALESCE((SELECT m.rating FROM file_metadata m WHERE m.file_id=f.id),0)"
for direction in ("asc", "desc"):
    SORTS[f"rating_{direction}"] = f"{RATING} {direction.upper()}, f.rel_path, f.id"


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
    ready_only: bool = False
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
    min_rating: int = 0
    max_rating: int = 5
    favorite: Optional[bool] = None
    review: str = "all"
    tags: tuple[str, ...] = ()
    tag_mode: str = "all"
    root_id: Optional[int] = None
    availability: str = "all"
    album_id: Optional[int] = None


def _validate_types(filters: Filters) -> None:
    if not isinstance(filters, Filters):
        raise ValueError("Invalid catalogue filters.")
    nullable_text = {"extension", "start", "end", "camera", "lens", "video_codec", "audio_codec"}
    integers = {"min_bytes", "max_bytes", "min_width", "min_height", "person", "root_id", "album_id",
                "min_rating", "max_rating"}
    for field in fields(Filters):
        value = getattr(filters, field.name)
        name = field.name
        if name in ("tags", "bbox"):
            continue
        if name in ("recursive", "undated", "ready_only", "favorite"):
            valid = type(value) is bool or (name == "favorite" and value is None)
        elif name in integers:
            valid = type(value) is int or (name in {"max_bytes", "person", "root_id", "album_id"} and value is None)
        elif name.startswith(("min_", "max_")):
            valid = value is None or type(value) in (int, float)
        else:
            valid = isinstance(value, str) or (name in nullable_text and value is None)
        if not valid:
            raise ValueError(f"Invalid value for {name}.")
    if filters.bbox is not None and (not isinstance(filters.bbox, (tuple, list)) or len(filters.bbox) != 4 or
                                     any(type(v) not in (int, float) for v in filters.bbox)):
        raise ValueError("Invalid GPS bounds.")


def rule(filters: Filters, sort: str = "newest") -> dict:
    """Canonical, versioned saved query. Unknown fields/versions are never silently ignored."""
    where(filters)
    if not isinstance(sort, str) or sort not in SORTS:
        raise ValueError("Unknown sort.")
    return {"version": 1, "filters": asdict(filters), "sort": sort}


def read_rule(value: str | dict) -> tuple[Filters, str]:
    try:
        data = json.loads(value) if isinstance(value, str) else value
        if (not isinstance(data, dict) or set(data) != {"version", "filters", "sort"} or
                type(data["version"]) is not int or data["version"] != 1 or
                not isinstance(data["filters"], dict)):
            raise ValueError("Unsupported saved-search rule.")
        filters = Filters(**data["filters"])
        rule(filters, data["sort"])
        filters = replace(filters, tags=tuple(filters.tags),
                          bbox=tuple(filters.bbox) if filters.bbox is not None else None)
        rule(filters, data["sort"])
        return filters, data["sort"]
    except (TypeError, KeyError, AttributeError, json.JSONDecodeError) as error:
        raise ValueError("Invalid saved-search rule.") from error


def where(filters: Filters) -> tuple[str, list]:
    _validate_types(filters)
    f = filters
    clauses, params = [], []
    for key in ("root_id", "album_id", "person"):
        value = getattr(f, key)
        if value is not None and value <= 0:
            raise ValueError(f"Invalid {key}.")
    if f.root_id is not None:
        clauses.append("f.root_id=?")
        params.append(f.root_id)
    if f.availability not in ("all", "online", "offline"):
        raise ValueError("Unknown folder availability.")
    if f.availability != "all":
        clauses.append("EXISTS (SELECT 1 FROM library_roots r WHERE r.id=f.root_id AND r.online=?)")
        params.append(int(f.availability == "online"))
    if f.album_id is not None:
        clauses.append("EXISTS (SELECT 1 FROM album_items i WHERE i.file_id=f.id AND i.album_id=?)")
        params.append(f.album_id)
    if not 0 <= f.min_rating <= f.max_rating <= 5:
        raise ValueError("Choose a rating range from 0 to 5.")
    if f.min_rating or f.max_rating < 5:
        clauses.append(f"{RATING} BETWEEN ? AND ?")
        params += [f.min_rating, f.max_rating]
    if f.favorite is not None:
        clauses.append("COALESCE((SELECT m.favorite FROM file_metadata m WHERE m.file_id=f.id),0)=?")
        params.append(int(f.favorite))
    if f.review != "all":
        if f.review not in ("unreviewed", "pick", "reject"):
            raise ValueError("Unknown review mark.")
        clauses.append("COALESCE((SELECT m.review FROM file_metadata m WHERE m.file_id=f.id),'unreviewed')=?")
        params.append(f.review)
    from .organisation import tag_names
    names = tag_names(f.tags)
    if f.tag_mode not in ("all", "any"):
        raise ValueError("Choose all or any matching tags.")
    if names:
        terms = ["EXISTS (SELECT 1 FROM file_tags x JOIN tags t ON t.id=x.tag_id "
                 "WHERE x.file_id=f.id AND t.name=? COLLATE NOCASE)" for _ in names]
        clauses.append("(" + (" AND " if f.tag_mode == "all" else " OR ").join(terms) + ")")
        params.extend(names)
    if f.ready_only:
        clauses.append("f.analyzed=1")
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


def browse_progress(lib: Library) -> dict[str, int]:
    row = lib.db.execute(
        "SELECT SUM(kind IN ('image','video') AND analyzed=1 AND error IS NULL) AS ready,"
        "SUM(kind!='other' AND (analyzed=0 OR COALESCE(metadata_version,0)<?)) AS pending,"
        "SUM(kind!='other' AND analyzed=1 AND error IS NOT NULL) AS problems FROM files",
        (METADATA_VERSION,)).fetchone()
    return {key: int(row[key] or 0) for key in row.keys()}


def page(lib: Library, filters: Filters, sort: str = "newest", offset: int = 0) -> tuple[list[dict], int, int]:
    if not isinstance(sort, str) or sort not in SORTS or type(offset) is not int or offset < 0:
        raise ValueError("Invalid sort or page offset.")
    sql, params = where(filters)
    count, size = lib.db.execute(f"SELECT COUNT(*),COALESCE(SUM(size),0) FROM files f WHERE {sql}", params).fetchone()
    rows = lib.db.execute(f"SELECT f.*,COALESCE(m.rating,0) AS rating,COALESCE(m.favorite,0) AS favorite,"
                          f"COALESCE(m.review,'unreviewed') AS review FROM files f "
                          f"LEFT JOIN file_metadata m ON m.file_id=f.id WHERE {sql} ORDER BY {SORTS[sort]} LIMIT ? OFFSET ?",
                          [*params, PAGE_SIZE, offset]).fetchall()
    return [dict(row) for row in rows], count, size


def folders(lib: Library) -> list[str]:
    out = {""}
    for row in lib.db.execute("SELECT DISTINCT folder FROM files"):
        parts = row[0].split("\\") if row[0] else []
        out.update("\\".join(parts[:i]) for i in range(1, len(parts) + 1))
    return sorted(out, key=str.casefold)


def distribution(lib: Library, filters: Filters, limit: Optional[int] = None) -> dict:
    sql, params = where(filters)
    if limit is not None:
        if type(limit) is not int or limit <= 0:
            raise ValueError("Invalid distribution limit.")
        start = len(filters.folder) + 2 if filters.folder else 1
        prefix = filters.folder + "\\" if filters.folder else ""
        children = [dict(row) for row in lib.db.execute(
            "WITH matching AS (SELECT substr(f.folder,?) AS relative,f.size FROM files f "
            f"WHERE {sql}), grouped AS (SELECT CASE WHEN instr(relative,'\\')>0 "
            "THEN substr(relative,1,instr(relative,'\\')-1) ELSE relative END AS child,size FROM matching) "
            "SELECT CASE WHEN child='' THEN ? ELSE ?||child END AS key,child='' AS direct,"
            "CASE WHEN child='' THEN '(Files directly here)' ELSE child END AS label,"
            "COUNT(*) AS count,SUM(size) AS bytes FROM grouped GROUP BY child ORDER BY bytes DESC,key LIMIT ?",
            [start, *params, filters.folder, prefix, limit])]
        types = [dict(row) for row in lib.db.execute(
            f"SELECT f.ext AS key,f.ext AS label,COUNT(*) AS count,SUM(f.size) AS bytes FROM files f "
            f"WHERE {sql} GROUP BY f.ext ORDER BY bytes DESC,f.ext LIMIT ?", [*params, limit])]
        total, size = lib.db.execute(
            f"SELECT COUNT(*),COALESCE(SUM(f.size),0) FROM files f WHERE {sql}", params).fetchone()
        return {"folders": children, "types": types, "count": total, "bytes": size}
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


def matching_albums(lib: Library, filters: Filters, limit: Optional[int] = None) -> list[dict]:
    sql, params = where(filters)
    tail = ""
    if limit is not None:
        if type(limit) is not int or limit <= 0:
            raise ValueError("Invalid album limit.")
        tail = " LIMIT ?"
        params.append(limit)
    return [dict(row) for row in lib.db.execute(
        f"SELECT a.id,a.name,COUNT(*) AS count FROM albums a JOIN album_items i ON i.album_id=a.id "
        f"JOIN files f ON f.id=i.file_id WHERE {sql} GROUP BY a.id ORDER BY count DESC,a.name{tail}", params)]


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
    for cell in cells:
        place = places.nearest(cell["lat"], cell["lon"])
        cell["place"] = f"{place.label}, {place.country}" if place else ""
    return {"bounds": bounds, "cells": cells, "gps_count": gps_count,
           "labels": places.map_labels(bounds),
            "visible_count": sum(c["count"] for c in cells)}
