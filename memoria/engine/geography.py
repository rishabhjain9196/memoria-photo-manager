"""Small offline basemap. Natural Earth outlines are approximate, not a geocoding authority."""
import gzip
import json
from functools import lru_cache
from pathlib import Path

INDIA = (6.0, 38.0, 66.0, 100.0)  # south, north, west, east
WORLD = (-90.0, 90.0, -180.0, 180.0)


@lru_cache(maxsize=1)
def countries() -> list[dict]:
    with gzip.open(Path(__file__).with_name("data") / "world-map.json.gz", "rt", encoding="utf-8") as file:
        return json.load(file)


def _inside_ring(lat: float, lon: float, ring: list) -> bool:
    inside = False
    x1, y1 = ring[-1]
    for x2, y2 in ring:
        if (y1 > lat) != (y2 > lat) and lon < (x2 - x1) * (lat - y1) / (y2 - y1) + x1:
            inside = not inside
        x1, y1 = x2, y2
    return inside


def in_india(lat: float, lon: float) -> bool:
    india = next(country for country in countries() if country["code"] == "IND")
    return any(_inside_ring(lat, lon, polygon[0]) and
               not any(_inside_ring(lat, lon, hole) for hole in polygon[1:]) for polygon in india["polygons"])
