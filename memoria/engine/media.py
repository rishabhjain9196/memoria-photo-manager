"""Image decoding and analysis: EXIF, capture date, thumbnail, perceptual hash, quality."""
from __future__ import annotations

import io
import re
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image, ImageOps

from .config import ANALYSIS_SIZE, THUMB_SIZE, longpath

try:
    import pillow_heif

    pillow_heif.register_heif_opener()
    HEIF = True
except Exception:  # pragma: no cover - optional
    HEIF = False

Image.MAX_IMAGE_PIXELS = 300_000_000

_EXIF_IFD = 0x8769
_GPS_IFD = 0x8825
_DT_ORIGINAL = 0x9003
_DT_DIGITIZED = 0x9004
_DT = 0x0132
_MAKE = 0x010F
_MODEL = 0x0110
_ORIENTATION = 0x0112

_FILENAME_DATE = re.compile(
    r"(?<!\d)(?P<y>(?:19|20)\d{2})[-_.]?(?P<m>0[1-9]|1[0-2])[-_.]?(?P<d>0[1-9]|[12]\d|3[01])"
    r"(?:(?:[ _T-]|\s+at\s+)?(?P<H>[01]\d|2[0-3])[.:\-]?(?P<M>[0-5]\d)[.:\-]?(?P<S>[0-5]\d))?(?!\d{3})")


def date_from_filename(name: str) -> Optional[datetime]:
    stem = Path(name).stem
    for m in _FILENAME_DATE.finditer(stem):
        try:
            dt = datetime(int(m["y"]), int(m["m"]), int(m["d"]),
                          int(m["H"] or 0), int(m["M"] or 0), int(m["S"] or 0))
        except ValueError:
            continue
        if 1990 <= dt.year <= datetime.now().year + 1:
            return dt
    return None


def _parse_exif_dt(value) -> Optional[datetime]:
    if not value:
        return None
    s = str(value).strip().replace("\x00", "")
    for fmt in ("%Y:%m:%d %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y:%m:%d %H:%M", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.strptime(s[:19], fmt)
            if dt.year >= 1990:
                return dt
        except ValueError:
            continue
    return None


def _gps_to_deg(values, ref) -> Optional[float]:
    try:
        d, m, s = (float(v) for v in values)
        deg = d + m / 60 + s / 3600
        if ref in ("S", "W", b"S", b"W"):
            deg = -deg
        return round(deg, 6)
    except Exception:
        return None


def read_exif(img: Image.Image) -> dict:
    out: dict = {}
    try:
        exif = img.getexif()
    except Exception:
        return out
    if not exif:
        return out
    sub = {}
    try:
        sub = exif.get_ifd(_EXIF_IFD) or {}
    except Exception:
        pass
    dt = (_parse_exif_dt(sub.get(_DT_ORIGINAL)) or _parse_exif_dt(sub.get(_DT_DIGITIZED))
          or _parse_exif_dt(exif.get(_DT)))
    if dt:
        out["taken_at"] = dt
    make = str(exif.get(_MAKE) or "").strip(" \x00")
    model = str(exif.get(_MODEL) or "").strip(" \x00")
    if model:
        out["camera"] = model if make and model.lower().startswith(make.lower().split()[0]) else f"{make} {model}".strip()
    elif make:
        out["camera"] = make
    out["orientation"] = exif.get(_ORIENTATION, 1)
    try:
        gps = exif.get_ifd(_GPS_IFD)
        if gps and 2 in gps and 4 in gps:
            lat = _gps_to_deg(gps[2], gps.get(1))
            lon = _gps_to_deg(gps[4], gps.get(3))
            if lat is not None and lon is not None and not (lat == 0 and lon == 0):
                out["lat"], out["lon"] = lat, lon
    except Exception:
        pass
    return out


def open_oriented(path: str | Path, target: int = ANALYSIS_SIZE) -> tuple[Image.Image, tuple[int, int], dict]:
    """Open an image decoded at reduced resolution (fast for JPEG), upright, in RGB.

    Returns (image, original_size, exif_info). Raises on unreadable files.
    """
    img = Image.open(longpath(path))
    original = img.size
    info = read_exif(img)
    if img.format == "JPEG":
        img.draft("RGB", (target, target))
    img.load()
    if info.get("orientation", 1) in (5, 6, 7, 8):
        original = (original[1], original[0])
    img = ImageOps.exif_transpose(img)
    if img.mode not in ("RGB", "L"):
        if img.mode in ("RGBA", "LA", "P") or "A" in img.getbands():
            img = img.convert("RGBA")
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.getchannel("A"))
            img = bg
        else:
            img = img.convert("RGB")
    elif img.mode == "L":
        img = img.convert("RGB")
    return img, original, info


def dhash(gray: Image.Image) -> int:
    """64-bit difference hash, returned as a signed int so it fits SQLite INTEGER."""
    small = np.asarray(gray.resize((9, 8), Image.Resampling.BOX), dtype=np.int16)
    bits = (small[:, 1:] > small[:, :-1]).flatten()
    value = 0
    for b in bits:
        value = (value << 1) | int(b)
    return value - (1 << 64) if value >= (1 << 63) else value


def quality_metrics(gray: Image.Image) -> dict:
    """Sharpness (variance of Laplacian), brightness, contrast and clipped-pixel share."""
    a = np.asarray(gray, dtype=np.float32)
    lap = (a[1:-1, :-2] + a[1:-1, 2:] + a[:-2, 1:-1] + a[2:, 1:-1] - 4 * a[1:-1, 1:-1])
    clipped = float(np.mean((a <= 4) | (a >= 251)))
    return {
        "sharpness": round(float(lap.var()), 2),
        "brightness": round(float(a.mean()), 2),
        "contrast": round(float(a.std()), 2),
        "clipped": round(clipped, 4),
    }


def thumbnail_bytes(img: Image.Image, size: int = THUMB_SIZE) -> bytes:
    t = img.copy()
    t.thumbnail((size, size), Image.Resampling.BILINEAR, reducing_gap=2.0)
    buf = io.BytesIO()
    t.save(buf, "JPEG", quality=82, optimize=False)
    return buf.getvalue()


def analyze_image(path: str | Path) -> dict:
    img, (w, h), info = open_oriented(path)
    # Always measure at the same scale so small copies don't look "sharper" than their originals.
    scale = ANALYSIS_SIZE / max(img.size)
    size = (max(1, round(img.width * scale)), max(1, round(img.height * scale)))
    work = img.resize(size, Image.Resampling.BILINEAR, reducing_gap=2.0 if scale < 1 else None)
    gray = work.convert("L")
    result = {"width": w, "height": h, "dhash": dhash(gray), "thumb": thumbnail_bytes(work)}
    result.update(quality_metrics(gray))
    for key in ("camera", "lat", "lon"):
        if key in info:
            result[key] = info[key]
    if "taken_at" in info:
        result["taken_at"] = info["taken_at"]
        result["date_source"] = "exif"
    return result


def load_for_display(path: str | Path, max_side: int) -> Image.Image:
    img, _, _ = open_oriented(path, target=max_side)
    if max(img.size) > max_side:
        img.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
    return img


_FACE_LOCAL = threading.local()


def count_faces(path: str | Path) -> Optional[int]:
    """Frontal face count using OpenCV's bundled Haar cascade (None if unavailable)."""
    try:
        import cv2
        cascade = getattr(_FACE_LOCAL, "cascade", None)
        if cascade is None:
            cascade = _FACE_LOCAL.cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        img, _, _ = open_oriented(path, target=640)
        img.thumbnail((640, 640))
        gray = np.asarray(img.convert("L"))
        faces = cascade.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=6, minSize=(32, 32))
        return int(len(faces))
    except Exception:
        return None
