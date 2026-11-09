"""Offline place names: the nearest town or city to a GPS position.

Uses a bundled list of every place with 15,000+ people from GeoNames (https://www.geonames.org,
CC BY 4.0). Nothing is looked up online, so photo locations never leave this computer.
"""
from __future__ import annotations

import gzip
import threading
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional

import numpy as np

DATA = Path(__file__).with_name("data") / "places.tsv.gz"
EARTH_KM = 6371.0
_lock = threading.Lock()
_table: Optional[tuple[list[tuple[str, str, str, int]], np.ndarray, np.ndarray]] = None


@dataclass(frozen=True)
class Place:
    name: str
    region: str
    country: str
    lat: float
    lon: float
    population: int
    distance_km: float

    @property
    def label(self) -> str:
        """Short name for albums: "Leh, Ladakh", "Delhi", "Paris, Île-de-France"; away from towns
        (> 8 km) the region ("Goa") or "Near <town>"."""
        if self.distance_km > 8:
            return self.region or f"Near {self.name}"
        if self.region and self.region.lower() not in self.name.lower():
            return f"{self.name}, {self.region}"
        return self.name


def _load():
    global _table
    with _lock:
        if _table is None:
            meta, lat, lon = [], [], []
            with gzip.open(DATA, "rt", encoding="utf-8") as fh:
                for line in fh:
                    if line.startswith("#"):
                        continue
                    name, region, country, la, lo, pop = line.rstrip("\n").split("\t")
                    meta.append((name, region, country, int(pop)))
                    lat.append(float(la))
                    lon.append(float(lo))
            _table = (meta, np.radians(np.array(lat)), np.radians(np.array(lon)))
    return _table


def distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = np.radians(lat1), np.radians(lat2)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lon2 - lon1) / 2) ** 2
    return float(2 * EARTH_KM * np.arcsin(np.sqrt(a)))


def nearest(lat: float, lon: float, max_km: float = 75.0) -> Optional[Place]:
    """The best-known place near (lat, lon): among towns within a few km of the closest one, the
    most populous (so central Delhi is "Delhi", not a suburb). None if nothing is within ``max_km``."""
    if lat is None or lon is None:
        return None
    meta, la, lo = _load()
    p, q = np.radians(lat), np.radians(lon)
    # Latitude alone safely excludes distant towns, including across the date line and near poles.
    candidates = np.flatnonzero(np.abs(la - p) <= (max_km + 12.0) / EARTH_KM)
    if not len(candidates):
        return None
    la, lo = la[candidates], lo[candidates]
    a = np.sin((la - p) / 2) ** 2 + np.cos(p) * np.cos(la) * np.sin((lo - q) / 2) ** 2
    d = 2 * EARTH_KM * np.arcsin(np.sqrt(np.clip(a, 0, 1)))
    i = int(np.argmin(d))
    if d[i] > max_km:
        return None
    near = np.flatnonzero(d <= d[i] + 12.0)
    j = int(max(near, key=lambda k: meta[candidates[k]][3]))
    index = candidates[j]
    name, region, country, pop = meta[index]
    return Place(name, region, country, float(np.degrees(la[j])), float(np.degrees(lo[j])), pop, float(d[j]))


@lru_cache(maxsize=1)
def _map_places() -> tuple[Place, ...]:
    meta, la, lo = _load()
    return tuple(sorted((Place(name, region, country, float(np.degrees(la[i])), float(np.degrees(lo[i])),
                              pop, 0.0) for i, (name, region, country, pop) in enumerate(meta)),
                        key=lambda place: -place.population))


def map_labels(bounds: tuple[float, float, float, float], limit: int = 160) -> list[dict]:
    """Bounded label candidates, anchored at settlements rather than invented region centres."""
    south, north, west, east = bounds
    country_view, region_view = east - west > 90, east - west > 12
    seen, labels = set(), []
    for place in _map_places():
        if not (south <= place.lat <= north and west <= place.lon <= east):
            continue
        key = (place.country,) if country_view else (
            (place.country, place.region or place.name) if region_view else
            (place.country, place.region, place.name))
        if key in seen:
            continue
        seen.add(key)
        labels.append({"lat": place.lat, "lon": place.lon,
                       "text": place.country if country_view else place.label})
        if len(labels) >= limit:
            break
    return labels
