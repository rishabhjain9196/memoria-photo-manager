"""Non-destructive photo editing: rotate/flip/straighten, crop, adjustments, filters, resize,
format conversion, grid split and join.

Trust rules: a source file is never modified. Every output is rendered at full resolution,
written into a private ``.memoria-work-*`` folder inside the output folder, decoded back to
verify it, given the source's modification time and only then renamed to a unique name
(`` (2)`` suffix if taken). The work folder is always removed, so a failure or cancellation
leaves no partial files behind.

Pipeline order used by :func:`apply` (identical for previews and full-resolution saves):

    transform (rotate → flip → straighten with auto-crop) → crop → auto levels →
    brightness/contrast (tone curve) → saturation → warmth → filter → sharpness → resize

Output formats: Pillow writes JPEG, PNG, WebP, TIFF and BMP. With ``format == "same"`` those
sources keep their format; everything else (HEIC/HEIF, AVIF, GIF, RAW, MPO…) is saved as JPEG.
"""
from __future__ import annotations

import io
import math
import os
import shutil
import uuid
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Optional, Sequence

import numpy as np
from PIL import Image, ImageColor, ImageEnhance, ImageFilter, ImageOps

from .config import longpath
from .media import load_for_display, open_oriented
from .progress import Cancelled, Progress
from .videotools import publish_file, unique_path

FILTERS = {"none": "None", "bw": "Black & white", "sepia": "Sepia", "vivid": "Vivid",
           "warm": "Warm", "cool": "Cool", "fade": "Faded"}
ASPECTS = {"free": None, "original": "original", "1:1": 1.0, "4:5": 0.8, "9:16": 9 / 16,
           "16:9": 16 / 9, "3:2": 1.5, "4:3": 4 / 3}
FORMATS = {"same": "Same as original", "jpeg": "JPEG", "webp": "WebP", "png": "PNG"}

MAX_JOIN_SIDE = 12000
FULL_RES = 1_000_000  # "target" passed to open_oriented so JPEG draft mode never downsamples
_ESTIMATE_SIDE = 1600

_ORIENTATION = 0x0112
_EXIF_IFD = 0x8769
_GPS_IFD = 0x8825
_EXIF_W, _EXIF_H = 0xA002, 0xA003

# Extension → Pillow format for the formats we can write with format == "same".
_WRITABLE_EXT = {".jpg": "JPEG", ".jpeg": "JPEG", ".jpe": "JPEG", ".png": "PNG", ".webp": "WEBP",
                 ".tif": "TIFF", ".tiff": "TIFF", ".bmp": "BMP"}
_FORMAT_EXT = {"jpeg": ".jpg", "webp": ".webp", "png": ".png"}
_ALPHA_FORMATS = {"PNG", "WEBP", "TIFF"}


class PhotoEditError(RuntimeError):
    pass


@dataclass
class PhotoEdit:
    rotate: int = 0               # 0/90/180/270 clockwise
    flip_h: bool = False          # mirror left↔right
    flip_v: bool = False          # mirror top↔bottom
    straighten: float = 0.0       # degrees, -15..15 (positive = clockwise), auto-cropped
    crop: Optional[tuple[float, float, float, float]] = None  # normalized, after transform
    brightness: int = 0           # -100..100
    contrast: int = 0             # -100..100
    saturation: int = 0           # -100..100 (-100 = grayscale)
    warmth: int = 0               # -100..100 (+ warmer/orange, - cooler/blue)
    sharpness: int = 0            # 0..100 (unsharp mask strength)
    auto: bool = False            # auto levels
    filter: str = "none"
    resize_long: Optional[int] = None   # longest side in px (never upscale)
    format: str = "same"
    quality: int = 90             # JPEG/WebP quality 1..100
    strip_gps: bool = False

    def is_identity(self) -> bool:
        """True when saving would be a plain re-save (same pixels, format and default quality)."""
        return (self.rotate % 360 == 0 and not self.flip_h and not self.flip_v
                and abs(self.straighten) < 0.01 and _crop_is_full(self.crop)
                and not (self.brightness or self.contrast or self.saturation or self.warmth
                         or self.sharpness or self.auto)
                and self.filter in ("none", "", None) and not self.resize_long
                and self.format == "same" and self.quality == 90 and not self.strip_gps)

    def copy(self, **changes) -> "PhotoEdit":
        return replace(self, **changes)


class SavedFiles(list):
    """``list[Path]`` of written files, plus ``sources`` (the source of each written file, same
    order) and ``failures``: ``[(source path, error message), …]``."""

    def __init__(self, items=(), failures=None, sources=None):
        super().__init__(items)
        self.failures: list[tuple[Path, str]] = list(failures or [])
        self.sources: list[Path] = list(sources or [])


# ----------------------------------------------------------------------------- loading

def load(path, max_side: Optional[int] = None) -> Image.Image:
    """Upright RGB image; full resolution when ``max_side`` is None."""
    if max_side is None:
        return open_oriented(path, FULL_RES)[0]
    return load_for_display(path, max_side)


def _open_for_save(path: Path, keep_alpha: bool):
    """Full-res upright image (RGB, or RGBA when it has alpha and ``keep_alpha``), Exif, ICC."""
    with Image.open(longpath(path)) as raw:
        exif = raw.getexif()
        for tag in (_EXIF_IFD, _GPS_IFD):  # read sub-IFDs while the file is still open
            if tag in exif:
                exif.get_ifd(tag)
        icc = raw.info.get("icc_profile")
        raw.load()
        img = ImageOps.exif_transpose(raw)
    if icc and (len(icc) < 20 or icc[16:20] != b"RGB "):
        icc = None  # e.g. a CMYK/gray profile would be wrong once converted to RGB
    has_alpha = img.mode in ("RGBA", "LA", "PA") or (img.mode == "P" and "transparency" in img.info)
    if has_alpha:
        img = img.convert("RGBA")
        if not keep_alpha:
            img = _flatten(img)
    elif img.mode != "RGB":
        img = img.convert("RGB")
    return img, exif, icc


def _flatten(img: Image.Image, color=(255, 255, 255)) -> Image.Image:
    if img.mode != "RGBA":
        return img.convert("RGB")
    bg = Image.new("RGB", img.size, color)
    bg.paste(img, mask=img.getchannel("A"))
    return bg


# ----------------------------------------------------------------------------- geometry

def _crop_is_full(crop) -> bool:
    if crop is None:
        return True
    l, t, r, b = crop
    return l <= 0.0005 and t <= 0.0005 and r >= 0.9995 and b >= 0.9995


def _max_rect(w: float, h: float, angle: float) -> tuple[float, float]:
    """Largest axis-aligned rectangle inside a w×h rectangle rotated by ``angle`` radians."""
    if w <= 0 or h <= 0:
        return 0.0, 0.0
    width_longer = w >= h
    long_side, short_side = (w, h) if width_longer else (h, w)
    sin_a, cos_a = abs(math.sin(angle)), abs(math.cos(angle))
    if short_side <= 2.0 * sin_a * cos_a * long_side or abs(sin_a - cos_a) < 1e-10:
        x = 0.5 * short_side
        return (x / sin_a, x / cos_a) if width_longer else (x / cos_a, x / sin_a)
    cos_2a = cos_a * cos_a - sin_a * sin_a
    return (w * cos_a - h * sin_a) / cos_2a, (h * cos_a - w * sin_a) / cos_2a


def _fill(mode: str):
    return {"RGB": (0, 0, 0), "RGBA": (0, 0, 0, 0), "L": 0}.get(mode, 0)


def _straighten(img: Image.Image, degrees: float) -> Image.Image:
    degrees = max(-45.0, min(45.0, float(degrees)))
    if abs(degrees) < 0.01:
        return img
    w, h = img.size
    rot = img.rotate(-degrees, resample=Image.Resampling.BICUBIC, expand=True, fillcolor=_fill(img.mode))
    wr, hr = _max_rect(w, h, math.radians(abs(degrees)))
    # Stay 2 px clear of the rotated edges so interpolation never blends in the fill colour.
    cw, ch = max(1, int(wr) - 4), max(1, int(hr) - 4)
    left = int(round(rot.width / 2 - cw / 2))
    top = int(round(rot.height / 2 - ch / 2))
    return rot.crop((left, top, left + cw, top + ch))


def transform(img: Image.Image, edit: PhotoEdit) -> Image.Image:
    """Rotate (clockwise) → flip → straighten. Used by the UI crop overlay."""
    rot = edit.rotate % 360
    if rot == 90:
        img = img.transpose(Image.Transpose.ROTATE_270)
    elif rot == 180:
        img = img.transpose(Image.Transpose.ROTATE_180)
    elif rot == 270:
        img = img.transpose(Image.Transpose.ROTATE_90)
    if edit.flip_h:
        img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    if edit.flip_v:
        img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    if edit.straighten:
        img = _straighten(img, edit.straighten)
    return img


def crop_box(size: tuple[int, int], crop) -> tuple[int, int, int, int]:
    """Pixel box for a normalized (left, top, right, bottom) crop of an image of ``size``."""
    w, h = size
    if crop is None:
        return 0, 0, w, h
    l, t, r, b = (min(1.0, max(0.0, float(v))) for v in crop)
    if r < l:
        l, r = r, l
    if b < t:
        t, b = b, t
    x0, y0 = int(round(l * w)), int(round(t * h))
    x1, y1 = int(round(r * w)), int(round(b * h))
    x0, y0 = min(x0, w - 1), min(y0, h - 1)
    return x0, y0, max(x1, x0 + 1), max(y1, y0 + 1)


def _crop(img: Image.Image, crop) -> Image.Image:
    if _crop_is_full(crop):
        return img
    return img.crop(crop_box(img.size, crop))


def _resize(img: Image.Image, resize_long: Optional[int]) -> Image.Image:
    if not resize_long or max(img.size) <= resize_long:
        return img
    s = resize_long / max(img.size)
    size = (max(1, round(img.width * s)), max(1, round(img.height * s)))
    return img.resize(size, Image.Resampling.LANCZOS, reducing_gap=3.0)


def crop_for_aspect(width: int, height: int, aspect, base=None) -> tuple[float, float, float, float]:
    """Largest centred normalized crop with pixel aspect ``aspect`` (w/h), optionally inside ``base``.

    ``aspect`` may be a float, ``None`` (free: returns ``base`` or the full frame) or
    ``"original"`` (the aspect of ``width × height``).
    """
    l, t, r, b = base if base is not None else (0.0, 0.0, 1.0, 1.0)
    if aspect is None:
        return (l, t, r, b)
    if aspect == "original":
        aspect = width / height
    aspect = float(aspect)
    bw, bh = (r - l) * width, (b - t) * height
    if bw <= 0 or bh <= 0 or aspect <= 0:
        return (l, t, r, b)
    if bw / bh > aspect:
        cw, ch = bh * aspect, bh
    else:
        cw, ch = bw, bw / aspect
    cx, cy = (l + r) / 2 * width, (t + b) / 2 * height
    return ((cx - cw / 2) / width, (cy - ch / 2) / height, (cx + cw / 2) / width, (cy + ch / 2) / height)


# ----------------------------------------------------------------------------- colour

def _lut(curve: np.ndarray) -> list[int]:
    return np.clip(np.round(curve * 255.0), 0, 255).astype(np.uint8).tolist()


def _tone(img: Image.Image, brightness: float, contrast: float) -> Image.Image:
    if not brightness and not contrast:
        return img
    x = np.arange(256, dtype=np.float64) / 255.0
    if brightness:
        x = x ** (2.0 ** (-brightness / 100.0))   # gamma: +100 → 0.5 (brighter), -100 → 2 (darker)
    if contrast:
        c = 1.0 + contrast / 100.0 if contrast > 0 else 1.0 + 0.8 * contrast / 100.0
        x = (x - 0.5) * c + 0.5
    return img.point(_lut(x) * 3)


def _warmth(img: Image.Image, warmth: float) -> Image.Image:
    if not warmth:
        return img
    k = warmth / 100.0
    x = np.arange(256, dtype=np.float64) / 255.0
    return img.point(_lut(x * (1 + 0.15 * k)) + _lut(x * (1 + 0.04 * k)) + _lut(x * (1 - 0.15 * k)))


def _saturate(img: Image.Image, factor: float) -> Image.Image:
    if abs(factor - 1.0) < 1e-6:
        return img
    if factor <= 0:
        return ImageOps.grayscale(img).convert("RGB")
    return ImageEnhance.Color(img).enhance(factor)


def _apply_filter(img: Image.Image, name: str) -> Image.Image:
    if name in (None, "", "none"):
        return img
    if name == "bw":
        return ImageOps.grayscale(img).convert("RGB")
    if name == "sepia":
        return ImageOps.colorize(ImageOps.grayscale(img), black=(38, 25, 12), white=(255, 244, 222),
                                 mid=(165, 128, 88))
    if name == "vivid":
        return _tone(_saturate(img, 1.35), 0, 12)
    if name == "warm":
        return _warmth(img, 45)
    if name == "cool":
        return _warmth(img, -45)
    if name == "fade":
        x = np.arange(256, dtype=np.float64) / 255.0
        return _saturate(img, 0.75).point(_lut(0.1 + 0.82 * x) * 3)
    raise ValueError(f"Unknown filter: {name}")


def _colour(img: Image.Image, edit: PhotoEdit, ref_long: Optional[float] = None) -> Image.Image:
    if edit.auto:
        img = ImageOps.autocontrast(img, cutoff=0.5)
    img = _tone(img, edit.brightness, edit.contrast)
    img = _saturate(img, 1.0 + max(-100, min(100, edit.saturation)) / 100.0)
    img = _warmth(img, edit.warmth)
    img = _apply_filter(img, edit.filter)
    if edit.sharpness > 0:
        # Radius scales with the image so a preview looks like the full-resolution result.
        radius = max(0.5, (ref_long or max(img.size)) / 2000.0)
        img = img.filter(ImageFilter.UnsharpMask(radius=radius, percent=int(min(100, edit.sharpness) * 1.6),
                                                 threshold=2))
    return img


def apply(img: Image.Image, edit: PhotoEdit) -> Image.Image:
    """Full pipeline (see module docstring). RGBA input keeps its (geometrically edited) alpha."""
    alpha = None
    if img.mode == "RGBA":
        alpha = img.getchannel("A")
        img = img.convert("RGB")
    elif img.mode != "RGB":
        img = img.convert("RGB")
    img = _crop(transform(img, edit), edit.crop)
    img = _resize(_colour(img, edit), edit.resize_long)
    if alpha is not None:
        alpha = _resize(_crop(transform(alpha, edit), edit.crop), edit.resize_long)
        if alpha.size == img.size and alpha.getextrema() != (255, 255):
            img = img.convert("RGBA")
            img.putalpha(alpha)
    return img


# ----------------------------------------------------------------------------- output

def _format_for(src: Path, fmt: str) -> tuple[str, str]:
    """(Pillow format, extension) for the output of ``src`` with edit format ``fmt``."""
    if fmt in _FORMAT_EXT:
        ext = _FORMAT_EXT[fmt]
        return _WRITABLE_EXT[ext], ext
    if fmt not in ("same", "", None):
        raise ValueError(f"Unknown format: {fmt}")
    ext = Path(src).suffix.lower()
    if ext in _WRITABLE_EXT:
        return _WRITABLE_EXT[ext], ext
    return "JPEG", ".jpg"


def output_path(src, out_dir=None, suffix: str = " (edited)", fmt: str = "same") -> Path:
    src = Path(src)
    folder = Path(out_dir) if out_dir is not None else src.parent
    return unique_path(folder / f"{src.stem}{suffix}{_format_for(src, fmt)[1]}")


def _exif_bytes(exif: Optional[Image.Exif], strip_gps: bool, size: tuple[int, int]) -> bytes:
    if exif is None or not len(exif):
        return b""
    try:
        exif[_ORIENTATION] = 1
        if strip_gps and _GPS_IFD in exif:
            del exif[_GPS_IFD]
        if _EXIF_IFD in exif:
            sub = exif.get_ifd(_EXIF_IFD)
            if _EXIF_W in sub:
                sub[_EXIF_W] = size[0]
            if _EXIF_H in sub:
                sub[_EXIF_H] = size[1]
        return exif.tobytes()
    except Exception:
        return b""


def _encode(img: Image.Image, target, pil_format: str, quality: int, exif: bytes = b"",
            icc: Optional[bytes] = None) -> None:
    """Write ``img`` to ``target`` (path or file object). Metadata is dropped if the format rejects it."""
    quality = int(max(1, min(100, quality)))
    if pil_format in ("JPEG", "BMP") and img.mode != "RGB":
        img = _flatten(img)
    params: dict = {}
    if pil_format == "JPEG":
        params = {"quality": quality}
    elif pil_format == "WEBP":
        params = {"quality": quality, "method": 4}
    elif pil_format == "PNG":
        params = {"compress_level": 6}
    elif pil_format == "TIFF":
        params = {"compression": "tiff_lzw"}
    meta: dict = {}
    if pil_format != "BMP":
        if exif:
            meta["exif"] = exif
        if icc:
            meta["icc_profile"] = icc
    try:
        img.save(target, pil_format, **params, **meta)
    except Exception:
        if not meta:
            raise
        if hasattr(target, "seek"):
            target.seek(0)
            target.truncate()
        img.save(target, pil_format, **params)


def _verify(path: Path, size: tuple[int, int]) -> None:
    try:
        with Image.open(path) as im:
            im.load()
            ok = im.size == size
    except Exception as e:
        raise PhotoEditError(f"The edited copy could not be read back ({e}), so it was discarded.") from e
    if not ok:
        raise PhotoEditError("The edited copy came out at the wrong size, so it was discarded.")


def _copy_mtime(src: Path, dst: Path) -> None:
    try:
        st = os.stat(longpath(src))
        os.utime(dst, (st.st_atime, st.st_mtime))
    except OSError:
        pass


def _finish(progress: Optional[Progress], total: int) -> None:
    """Report completion; the outputs already exist, so a late cancel no longer applies."""
    if progress is None:
        return
    try:
        progress.update(total, total, "Done", force=True)
    except Cancelled:
        pass


def _workdir(out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    work = out_dir / f".memoria-work-{uuid.uuid4().hex[:10]}"
    work.mkdir()
    return work


def _publish_all(items: Sequence[tuple[Path, Path]]) -> list[Path]:
    """Publish (tmp, wanted) pairs; if one fails, already-published ones are removed again."""
    done: list[Path] = []
    try:
        for tmp, wanted in items:
            done.append(publish_file(tmp, wanted))
    except BaseException:
        for p in done:
            try:
                p.unlink()
            except OSError:
                pass
        raise
    return done


def _render_to(src: Path, edit: PhotoEdit, pil_format: str, work: Path, progress: Optional[Progress],
               total: int = 4) -> tuple[Path, Image.Image]:
    """Shared save path: decode → edit → encode into ``work`` → verify. Returns (tmp file, image)."""
    if progress is not None:
        progress.update(0, total, f"Reading {src.name}…", force=True)
    try:
        img, exif, icc = _open_for_save(src, keep_alpha=pil_format in _ALPHA_FORMATS)
    except Exception as e:
        raise PhotoEditError(f"Can't open {src.name}: {e}") from e
    if progress is not None:
        progress.update(1, total, "Editing…")
    out = apply(img, edit)
    if progress is not None:
        progress.update(2, total, "Saving…")
    tmp = work / f"output-{uuid.uuid4().hex[:8]}"
    _encode(out, tmp, pil_format, edit.quality, _exif_bytes(exif, edit.strip_gps, out.size), icc)
    if progress is not None:
        progress.update(3, total, "Checking the copy…")
    _verify(tmp, out.size)
    _copy_mtime(src, tmp)
    return tmp, out


def save(src, edit: PhotoEdit, out_dir=None, suffix: str = " (edited)",
         progress: Optional[Progress] = None) -> Path:
    """Render ``edit`` at full resolution into a new file; returns its path.

    Keeps Exif (date, camera…) with Orientation reset to 1 (pixels are upright), drops GPS when
    ``strip_gps``, keeps an RGB ICC profile and copies the source's modification time.
    """
    src = Path(src)
    out_dir = Path(out_dir).absolute() if out_dir is not None else src.absolute().parent
    pil_format, ext = _format_for(src, edit.format)
    work = _workdir(out_dir)
    try:
        tmp, _ = _render_to(src, edit, pil_format, work, progress)
        if progress is not None:
            progress.check()
        dst = publish_file(tmp, out_dir / f"{src.stem}{suffix}{ext}")
        _finish(progress, 4)
        return dst
    finally:
        shutil.rmtree(work, ignore_errors=True)


def save_many(paths, edit: PhotoEdit, out_dir=None, suffix: str = " (edited)",
              progress: Optional[Progress] = None) -> SavedFiles:
    """Apply the same edit to many photos (crop is normalized, so it is interpreted per photo).

    Returns a :class:`SavedFiles` (a ``list[Path]`` of new files; ``.sources`` gives the source of
    each, same order) whose ``failures`` attribute
    lists ``(path, message)`` for photos that could not be saved; the same list is also kept in
    ``save_many.last_failures``. Raises :class:`PhotoEditError` only if every photo failed.
    Cancelling keeps the photos already finished (each is a complete, verified file).
    """
    paths = [Path(p) for p in paths]
    saved = SavedFiles()
    save_many.last_failures = saved.failures
    n = len(paths)
    for i, p in enumerate(paths):
        sub = progress.step(i, n, p.name) if progress is not None else None
        if progress is not None:
            progress.check()
        try:
            saved.append(save(p, edit, out_dir, suffix, sub))
            saved.sources.append(p)
        except Cancelled:
            raise
        except Exception as e:
            saved.failures.append((p, str(e) or type(e).__name__))
    if n and not saved:
        raise PhotoEditError(f"None of the {n} photos could be saved: {saved.failures[0][1]}")
    _finish(progress, 1000)
    return saved


save_many.last_failures = []


def estimate_bytes(img: Image.Image, edit: PhotoEdit, full_size: tuple[int, int], src=None) -> int:
    """Approximate output size in bytes (typically within ±25 % for JPEG; ~0.1 s).

    Encodes a ≤1600 px render in memory and scales it by pixel count, corrected for how
    bytes-per-pixel change with scale: from native-resolution sample tiles when ``img`` is the
    full-resolution image, otherwise extrapolated from the render at full and half size.
    ``img`` is the upright source (full or preview); ``full_size`` its full-resolution size.
    ``src`` (optional) resolves ``format == "same"``; without it JPEG is assumed.
    """
    pil_format = _format_for(Path(src), edit.format)[0] if src is not None else (
        "JPEG" if edit.format in ("same", "", None) else _format_for(Path("x.jpg"), edit.format)[0])
    meta = _metadata_bytes(src) if src is not None else 0
    work = img
    if max(work.size) > _ESTIMATE_SIDE:
        work = work.copy()
        work.thumbnail((_ESTIMATE_SIDE, _ESTIMATE_SIDE), Image.Resampling.BILINEAR, reducing_gap=2.0)
    small = apply(work, edit.copy(resize_long=None))
    scale = max(full_size) / max(work.size)
    geo_w, geo_h = small.width * scale, small.height * scale
    fw, fh = geo_w, geo_h
    if edit.resize_long and max(fw, fh) > edit.resize_long:
        r = edit.resize_long / max(fw, fh)
        fw, fh = fw * r, fh * r
    if edit.resize_long and max(small.size) > edit.resize_long:
        small = _resize(small, edit.resize_long)
    p1 = small.width * small.height
    b1 = _encoded_size(small, pil_format, edit.quality)
    ratio = (fw * fh) / max(1, p1)
    if ratio <= 1.0 or min(small.size) < 64:
        return int(b1 * ratio) + meta
    if max(img.size) >= 0.98 * max(full_size) and work is not img:
        corr = _tile_correction(img, edit, pil_format, fw / geo_w, max(work.size) / max(img.size))
        if corr is not None:
            return int(b1 * ratio * corr * 1.12) + meta  # 1.12: calibrated on real photos
    # Bytes-per-pixel changes with scale (detail gets denser when downscaled, noise gets averaged
    # away). Measure it at half scale too and extrapolate the power law to the full size.
    half = small.resize((max(1, small.width // 2), max(1, small.height // 2)), Image.Resampling.BILINEAR,
                        reducing_gap=2.0)
    p2 = half.width * half.height
    b2 = _encoded_size(half, pil_format, edit.quality)
    alpha = math.log((b1 / p1) / (b2 / p2)) / math.log(p1 / p2) if b1 > 0 and b2 > 0 else 0.0
    alpha = max(-0.35, min(0.35, alpha))
    return int(b1 * ratio * ratio ** alpha) + meta


def _tile_correction(img: Image.Image, edit: PhotoEdit, pil_format: str, target_scale: float,
                     render_scale: float) -> Optional[float]:
    """bpp at the output scale ÷ bpp at the render scale, measured on a mosaic of native tiles."""
    t = 320
    if min(img.size) < 2 * t:
        return None
    colour = PhotoEdit(brightness=edit.brightness, contrast=edit.contrast, saturation=edit.saturation,
                       warmth=edit.warmth, filter=edit.filter, sharpness=edit.sharpness)
    spots = [(fx, fy) for fy in (0.3, 0.7) for fx in (0.2, 0.5, 0.8)]
    mosaic = Image.new("RGB", (3 * t, 2 * t))
    for k, (fx, fy) in enumerate(spots):
        x = min(max(0, int(fx * img.width - t / 2)), img.width - t)
        y = min(max(0, int(fy * img.height - t / 2)), img.height - t)
        mosaic.paste(img.crop((x, y, x + t, y + t)).convert("RGB"), ((k % 3) * t, (k // 3) * t))

    def bpp(s: float, resample, gap: float) -> float:  # s = scale relative to img
        size = (max(16, round(3 * t * s)), max(16, round(2 * t * s)))
        m = mosaic if s >= 0.999 else mosaic.resize(size, resample, reducing_gap=gap)
        m = _colour(m, colour, max(img.size) * s)
        return _encoded_size(m, pil_format, edit.quality) / (m.width * m.height)

    hi = bpp(target_scale, Image.Resampling.LANCZOS, 3.0)
    lo = bpp(render_scale, Image.Resampling.BILINEAR, 2.0)
    if hi <= 0 or lo <= 0:
        return None
    return max(0.3, min(5.0, hi / lo))


def _metadata_bytes(src) -> int:
    try:
        with Image.open(longpath(src)) as im:
            return len(im.info.get("exif") or b"") + len(im.info.get("icc_profile") or b"")
    except Exception:
        return 0


def _encoded_size(img: Image.Image, pil_format: str, quality: int) -> int:
    buf = io.BytesIO()
    _encode(img, buf, pil_format, quality)
    return buf.tell()


# ----------------------------------------------------------------------------- split & join

def split_grid(src, rows: int, cols: int, out_dir=None, edit: Optional[PhotoEdit] = None,
               progress: Optional[Progress] = None) -> list[Path]:
    """Cut a photo into rows × cols pieces (reading order) that tile it exactly. All-or-nothing."""
    src = Path(src)
    rows, cols = int(rows), int(cols)
    if rows < 1 or cols < 1 or rows * cols < 2:
        raise ValueError("Choose at least two pieces")
    edit = edit or PhotoEdit()
    out_dir = Path(out_dir).absolute() if out_dir is not None else src.absolute().parent
    pil_format, ext = _format_for(src, edit.format)
    n = rows * cols
    total = n + 2
    if progress is not None:
        progress.update(0, total, f"Reading {src.name}…", force=True)
    try:
        img, exif, icc = _open_for_save(src, keep_alpha=pil_format in _ALPHA_FORMATS)
    except Exception as e:
        raise PhotoEditError(f"Can't open {src.name}: {e}") from e
    img = apply(img, edit)
    w, h = img.size
    if cols > w or rows > h:
        raise PhotoEditError("The photo is too small for that many pieces")
    xs = [round(i * w / cols) for i in range(cols + 1)]
    ys = [round(j * h / rows) for j in range(rows + 1)]
    work = _workdir(out_dir)
    try:
        items = []
        k = 0
        for j in range(rows):
            for i in range(cols):
                k += 1
                if progress is not None:
                    progress.update(k, total, f"Saving piece {k} of {n}…")
                piece = img.crop((xs[i], ys[j], xs[i + 1], ys[j + 1]))
                tmp = work / f"part-{k}"
                _encode(piece, tmp, pil_format, edit.quality,
                        _exif_bytes(exif, edit.strip_gps, piece.size), icc)
                _verify(tmp, piece.size)
                _copy_mtime(src, tmp)
                items.append((tmp, out_dir / f"{src.stem} (part {k} of {n}){ext}"))
        if progress is not None:
            progress.check()
        result = _publish_all(items)
        _finish(progress, total)
        return result
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _grid_shape(n: int) -> tuple[int, int]:
    cols = math.ceil(math.sqrt(n))
    return math.ceil(n / cols), cols


def join(paths, direction: str = "horizontal", out_dir=None, spacing: int = 0,
         background: str = "#FFFFFF", progress: Optional[Progress] = None) -> Path:
    """Join photos side by side ("horizontal"), stacked ("vertical") or in a near-square "grid".

    horizontal: every photo scaled to the smallest height; vertical: to the smallest width;
    grid: equal cells (median aspect, sized so no photo is enlarged), each photo fitted and
    letterboxed on ``background``. Never upscales; the result is downscaled to ≤ 12000 px.
    Output: ``"<first stem> (joined).jpg"`` (JPEG q92, first photo's Exif, Orientation=1).
    """
    paths = [Path(p) for p in paths]
    if len(paths) < 2:
        raise ValueError("Choose at least two photos to join")
    if direction not in ("horizontal", "vertical", "grid"):
        raise ValueError(f"Unknown direction: {direction}")
    bg = ImageColor.getrgb(background)[:3]
    spacing = max(0, int(spacing))
    n = len(paths)
    total = n + 2
    images = []
    for i, p in enumerate(paths):
        if progress is not None:
            progress.update(i, total, f"Reading {p.name}…", force=i == 0)
        try:
            images.append(load(p))
        except Exception as e:
            raise PhotoEditError(f"Can't open {p.name}: {e}") from e
    with Image.open(longpath(paths[0])) as first:
        exif = first.getexif()
        if _EXIF_IFD in exif:
            exif.get_ifd(_EXIF_IFD)

    if direction == "horizontal":
        hh = min(im.height for im in images)
        sizes = [(max(1, round(im.width * hh / im.height)), hh) for im in images]
        canvas = (sum(s[0] for s in sizes) + spacing * (n - 1), hh)
        cells = []
        x = 0
        for s in sizes:
            cells.append((x, 0, s[0], s[1]))
            x += s[0] + spacing
    elif direction == "vertical":
        ww = min(im.width for im in images)
        sizes = [(ww, max(1, round(im.height * ww / im.width))) for im in images]
        canvas = (ww, sum(s[1] for s in sizes) + spacing * (n - 1))
        cells = []
        y = 0
        for s in sizes:
            cells.append((0, y, s[0], s[1]))
            y += s[1] + spacing
    else:
        rows, cols = _grid_shape(n)
        aspect = float(np.median([im.width / im.height for im in images]))
        ch = min(min(im.height, im.width / aspect) for im in images)
        cw = max(1, int(ch * aspect))
        ch = max(1, int(ch))
        canvas = (cols * cw + spacing * (cols - 1), rows * ch + spacing * (rows - 1))
        cells = [((k % cols) * (cw + spacing), (k // cols) * (ch + spacing), cw, ch) for k in range(n)]

    s = min(1.0, MAX_JOIN_SIDE / max(canvas))
    if s < 1.0:
        canvas = (max(1, int(canvas[0] * s)), max(1, int(canvas[1] * s)))
        cells = [(int(x * s), int(y * s), max(1, int(w * s)), max(1, int(h * s))) for x, y, w, h in cells]
    out = Image.new("RGB", canvas, bg)
    for i, (im, (x, y, w, h)) in enumerate(zip(images, cells)):
        if progress is not None:
            progress.update(n, total, f"Placing photo {i + 1} of {n}…")
        if direction == "grid":
            r = min(w / im.width, h / im.height, 1.0)
            fw, fh = max(1, round(im.width * r)), max(1, round(im.height * r))
            out.paste(im.resize((fw, fh), Image.Resampling.LANCZOS, reducing_gap=3.0),
                      (x + (w - fw) // 2, y + (h - fh) // 2))
        else:
            out.paste(im if im.size == (w, h) else im.resize((w, h), Image.Resampling.LANCZOS, reducing_gap=3.0),
                      (x, y))
        images[i] = None  # free memory early
    out_dir = Path(out_dir).absolute() if out_dir is not None else paths[0].absolute().parent
    work = _workdir(out_dir)
    try:
        if progress is not None:
            progress.update(n + 1, total, "Saving…")
        tmp = work / "joined.jpg"
        _encode(out, tmp, "JPEG", 92, _exif_bytes(exif, False, out.size))
        _verify(tmp, out.size)
        _copy_mtime(paths[0], tmp)
        if progress is not None:
            progress.check()
        dst = publish_file(tmp, out_dir / f"{paths[0].stem} (joined).jpg")
        _finish(progress, total)
        return dst
    finally:
        shutil.rmtree(work, ignore_errors=True)
