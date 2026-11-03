"""Instagram story / carousel / story-video maker.

Everything is rendered with Pillow; story videos are rendered frame by frame in Python and
piped as raw RGB into ffmpeg. Source photos are only ever read.
"""
from __future__ import annotations

import os
import queue
import shutil
import subprocess
import threading
import uuid
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional, Sequence, Union

import numpy as np
from PIL import Image, ImageColor, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from . import ffmpeg
from .media import open_oriented
from .progress import Progress
from .videotools import publish_file

STORY = (1080, 1920)
POST = (1080, 1350)
SQUARE = (1080, 1080)

TEMPLATES = {
    "single": "Single photo",
    "duo": "Two photos (stacked)",
    "trio": "Three photos",
    "grid4": "Four-photo grid",
    "before_after": "Before / after",
    "polaroid": "Polaroid",
}
_SLOTS = {"single": 1, "polaroid": 1, "duo": 2, "trio": 3, "grid4": 4, "before_after": 2}
# Template to use when a group has fewer photos than the template needs.
_FALLBACK = {4: "grid4", 3: "trio", 2: "duo", 1: "single"}

LOAD_SIDE = 2200
JPEG_QUALITY = 92
KEN_BURNS_ZOOM = 0.08

ImageSource = Union[str, Path, Image.Image]


@dataclass
class StyleOptions:
    background: str = "blur"     # "blur" | "black" | "white" | "#RRGGBB"
    fit: str = "fit"             # "fit" (whole photo visible) | "fill" (crop to fill, centre-weighted)
    caption: str = ""
    caption_position: str = "bottom"  # "top" | "bottom"
    margin: int = 48             # gap between collage cells / edges (px at 1080 wide)
    rounded: int = 24            # corner radius for photo cards on blur background (0 = none)


def template_slots(template_id: str) -> int:
    try:
        return _SLOTS[template_id]
    except KeyError:
        raise ValueError(f"Unknown template: {template_id!r}") from None


# ----------------------------------------------------------------------------- loading / fonts

def _load(src: ImageSource, max_side: Optional[int] = LOAD_SIDE) -> Image.Image:
    if isinstance(src, Image.Image):
        img = src.convert("RGB")
    else:
        img, _, _ = open_oriented(src, target=max_side or LOAD_SIDE)
    if max_side and max(img.size) > max_side:
        img = img.copy()
        img.thumbnail((max_side, max_side), Image.Resampling.BICUBIC, reducing_gap=3.0)
    return img


_FONT_FILES = {
    "ui": ("seguisb.ttf", "segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"),
    "hand": ("segoepr.ttf", "segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"),
}


@lru_cache(maxsize=64)
def _font(px: int, kind: str = "ui") -> ImageFont.ImageFont:
    fonts_dir = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    for name in _FONT_FILES.get(kind, _FONT_FILES["ui"]):
        for cand in (fonts_dir / name, name):
            try:
                return ImageFont.truetype(str(cand), px)
            except OSError:
                continue
    return ImageFont.load_default(size=px)


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_w: float) -> list[str]:
    lines: list[str] = []
    for para in text.splitlines() or [""]:
        words, cur = para.split(), ""
        for word in words:
            trial = f"{cur} {word}".strip()
            if not cur or draw.textlength(trial, font=font) <= max_w:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return [l for l in lines if l] or [""]


# ----------------------------------------------------------------------------- geometry helpers

def _focus(img: Image.Image) -> tuple[float, float]:
    """Centre-weighted saliency: centroid of edge energy times a centred Gaussian (0..1 coords)."""
    small = img.convert("L")
    small.thumbnail((96, 96), Image.Resampling.BILINEAR)
    a = np.asarray(small, dtype=np.float32)
    if a.shape[0] < 3 or a.shape[1] < 3:
        return 0.5, 0.5
    e = np.zeros_like(a)
    e[:, 1:] += np.abs(np.diff(a, axis=1))
    e[1:, :] += np.abs(np.diff(a, axis=0))
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]].astype(np.float32)
    xx = (xx + 0.5) / a.shape[1]
    yy = (yy + 0.5) / a.shape[0]
    sal = e * np.exp(-((xx - 0.5) ** 2 + (yy - 0.5) ** 2) / (2 * 0.22 ** 2))
    total = float(sal.sum())
    if total < 1e-3:
        return 0.5, 0.5
    return float((sal * xx).sum() / total), float((sal * yy).sum() / total)


def _cover(img: Image.Image, tw: int, th: int, smart: bool = True,
           resample=Image.Resampling.LANCZOS) -> Image.Image:
    """Scale and crop to exactly tw×th, crop window centred on the salient point."""
    w, h = img.size
    scale = max(tw / w, th / h)
    cw, ch = tw / scale, th / scale
    fx, fy = _focus(img) if smart and (cw < w - 1 or ch < h - 1) else (0.5, 0.5)
    x0 = min(max(fx * w - cw / 2, 0.0), w - cw)
    y0 = min(max(fy * h - ch / 2, 0.0), h - ch)
    return img.resize((tw, th), resample, box=(x0, y0, x0 + cw, y0 + ch), reducing_gap=2.0)


def _contain(img: Image.Image, bw: int, bh: int) -> Image.Image:
    w, h = img.size
    s = min(bw / w, bh / h)
    size = (max(1, round(w * s)), max(1, round(h * s)))
    return img.resize(size, Image.Resampling.LANCZOS, reducing_gap=2.0)


@lru_cache(maxsize=16)
def _corner_disc(r: int) -> Image.Image:
    big = Image.new("L", (r * 8, r * 8), 0)
    ImageDraw.Draw(big).ellipse((0, 0, r * 8 - 1, r * 8 - 1), fill=255)
    return big.resize((r * 2, r * 2), Image.Resampling.BOX)


def _round_mask(size: tuple[int, int], r: int) -> Image.Image:
    w, h = size
    r = max(0, min(r, w // 2, h // 2))
    mask = Image.new("L", size, 255)
    if r < 1:
        return mask
    disc = _corner_disc(r)
    mask.paste(disc.crop((0, 0, r, r)), (0, 0))
    mask.paste(disc.crop((r, 0, 2 * r, r)), (w - r, 0))
    mask.paste(disc.crop((0, r, r, 2 * r)), (0, h - r))
    mask.paste(disc.crop((r, r, 2 * r, 2 * r)), (w - r, h - r))
    return mask


def _background(pic: Image.Image, spec: str, size: tuple[int, int]) -> Image.Image:
    W, H = size
    if spec == "blur":
        small = _cover(pic, max(8, W // 10), max(8, H // 10), smart=False,
                       resample=Image.Resampling.BILINEAR)
        small = small.filter(ImageFilter.GaussianBlur(3))
        bg = small.resize(size, Image.Resampling.BICUBIC)
        bg = bg.filter(ImageFilter.BoxBlur(max(2, W // 160)))
        return ImageEnhance.Brightness(bg).enhance(0.55)
    colours = {"black": (0, 0, 0), "white": (255, 255, 255)}
    colour = colours.get(spec)
    if colour is None:
        try:
            colour = ImageColor.getrgb(spec)[:3]
        except (ValueError, AttributeError):
            colour = (0, 0, 0)
    return Image.new("RGB", size, colour)


def _text_pill(canvas: Image.Image, text: str, font, *, cx: Optional[int] = None,
               left: Optional[int] = None, top: Optional[int] = None,
               bottom: Optional[int] = None, max_w: int) -> None:
    """Draw (wrapped) text with a soft shadow on a semi-transparent rounded pill."""
    if not text.strip():
        return
    probe = ImageDraw.Draw(canvas)
    px = font.size if hasattr(font, "size") else 20
    pad_x, pad_y = round(px * 0.65), round(px * 0.4)
    lines = _wrap(probe, text.strip(), font, max_w - 2 * pad_x)
    asc, desc = font.getmetrics()
    line_h = asc + desc
    gap = round(px * 0.18)
    text_w = max(probe.textlength(l, font=font) for l in lines)
    pw = int(min(max_w, text_w + 2 * pad_x))
    ph = int(len(lines) * line_h + (len(lines) - 1) * gap + 2 * pad_y)
    W, H = canvas.size
    x = (cx - pw // 2) if cx is not None else (left or 0)
    y = top if top is not None else (bottom - ph if bottom is not None else (H - ph) // 2)
    x, y = max(0, min(x, W - pw)), max(0, min(y, H - ph))

    layer = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    ImageDraw.Draw(layer).rounded_rectangle((0, 0, pw - 1, ph - 1), radius=min(ph // 2, px),
                                            fill=(0, 0, 0, 135))
    shadow = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    ink = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    sd, td = ImageDraw.Draw(shadow), ImageDraw.Draw(ink)
    off = max(1, px // 22)
    for i, line in enumerate(lines):
        ly = pad_y + i * (line_h + gap)
        sd.text((pw / 2 + off, ly + off), line, font=font, fill=(0, 0, 0, 170), anchor="ma")
        td.text((pw / 2, ly), line, font=font, fill=(255, 255, 255, 255), anchor="ma")
    layer = Image.alpha_composite(layer, shadow.filter(ImageFilter.GaussianBlur(max(1, off))))
    layer = Image.alpha_composite(layer, ink)
    canvas.paste(layer, (x, y), layer)


# ----------------------------------------------------------------------------- composition

def _cells(template: str, W: int, H: int, m: int) -> list[tuple[int, int, int, int]]:
    x0, y0, x1, y1 = m, m, W - m, H - m
    aw, ah = x1 - x0, y1 - y0
    if template == "duo" or (template == "before_after" and H > W):
        hh = (ah - m) // 2
        return [(x0, y0, x1, y0 + hh), (x0, y1 - hh, x1, y1)]
    if template == "before_after":
        hw = (aw - m) // 2
        return [(x0, y0, x0 + hw, y1), (x1 - hw, y0, x1, y1)]
    if template == "trio":
        hh = (ah - m) // 2
        hw = (aw - m) // 2
        return [(x0, y0, x1, y0 + hh), (x0, y1 - hh, x0 + hw, y1), (x1 - hw, y1 - hh, x1, y1)]
    if template == "grid4":
        hh, hw = (ah - m) // 2, (aw - m) // 2
        return [(x0, y0, x0 + hw, y0 + hh), (x1 - hw, y0, x1, y0 + hh),
                (x0, y1 - hh, x0 + hw, y1), (x1 - hw, y1 - hh, x1, y1)]
    return [(x0, y0, x1, y1)]


def _place(canvas: Image.Image, pic: Image.Image, cell, fill: bool, radius: int) -> tuple[int, int, int, int]:
    cx0, cy0, cx1, cy1 = cell
    cw, ch = cx1 - cx0, cy1 - cy0
    if fill:
        im, pos = _cover(pic, cw, ch), (cx0, cy0)
    else:
        im = _contain(pic, cw, ch)
        pos = (cx0 + (cw - im.width) // 2, cy0 + (ch - im.height) // 2)
    canvas.paste(im, pos, _round_mask(im.size, radius) if radius else None)
    return pos[0], pos[1], pos[0] + im.width, pos[1] + im.height


def _caption_offset(W: int, H: int, m: int) -> int:
    # Stories: keep clear of Instagram's own top/bottom UI.
    return round(H * 0.11) if H / W > 1.6 else m + round(W * 0.03)


def _draw_caption(canvas: Image.Image, style: StyleOptions, m: int) -> None:
    if not style.caption.strip():
        return
    W, H = canvas.size
    font = _font(max(12, round(W * 0.045)))
    off = _caption_offset(W, H, m)
    kw = {"top": off} if style.caption_position == "top" else {"bottom": H - off}
    _text_pill(canvas, style.caption, font, cx=W // 2, max_w=W - 2 * m - round(W * 0.04), **kw)


def _polaroid(canvas: Image.Image, pic: Image.Image, style: StyleOptions, m: int) -> None:
    W, H = canvas.size
    aspect = pic.width / pic.height
    pa = 1.0 if style.fit == "fill" else min(max(aspect, 0.8), 1.25)
    cw = W * 0.80
    b, bb = cw * 0.055, cw * 0.26
    ch = b + (cw - 2 * b) / pa + bb
    max_h = H - 2 * m - W * 0.08
    if ch > max_h:
        k = max_h / ch
        cw, b, bb, ch = cw * k, b * k, bb * k, max_h
    cw, ch, b, bb = round(cw), round(ch), round(b), round(bb)
    pw, ph = cw - 2 * b, ch - b - bb
    pad = max(4, W // 270)
    card = Image.new("RGBA", (cw + 2 * pad, ch + 2 * pad), (0, 0, 0, 0))
    card.paste((250, 250, 247, 255), (pad, pad, pad + cw, pad + ch))
    card.paste(_cover(pic, pw, ph, smart=True), (pad + b, pad + b))
    if style.caption.strip():
        d = ImageDraw.Draw(card)
        size = round(bb * 0.30)
        while True:
            font = _font(size, "hand")
            lines = _wrap(d, style.caption.strip(), font, pw)
            asc, desc = font.getmetrics()
            block = len(lines) * (asc + desc)
            if (block <= bb * 0.8 and len(lines) <= 2) or size <= 12:
                break
            size = max(12, round(size * 0.88))
        y = pad + b + ph + (bb - block) / 2
        for line in lines[:3]:
            d.text((pad + cw / 2, y), line, font=font, fill=(45, 45, 50, 255), anchor="ma")
            y += asc + desc
    blur = max(4, W // 60)
    shadow = Image.new("L", (card.width + 4 * blur, card.height + 4 * blur), 0)
    shadow.paste(120, (2 * blur + pad, 2 * blur + pad, 2 * blur + pad + cw, 2 * blur + pad + ch))
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    angle = -3
    card = card.rotate(angle, Image.Resampling.BICUBIC, expand=True)
    shadow = shadow.rotate(angle, Image.Resampling.BICUBIC, expand=True)
    sx, sy = (W - shadow.width) // 2, (H - shadow.height) // 2 + round(W * 0.012)
    canvas.paste((0, 0, 0), (sx, sy, sx + shadow.width, sy + shadow.height), shadow)
    canvas.paste(card, ((W - card.width) // 2, (H - card.height) // 2), card)


def _compose(pics: list[Image.Image], template: str, style: StyleOptions,
             size: tuple[int, int]) -> Image.Image:
    W, H = size
    s = W / 1080
    m = round(style.margin * s)
    radius = round(style.rounded * s) if style.background == "blur" else 0
    canvas = _background(pics[0], style.background, size)
    if template == "polaroid":
        _polaroid(canvas, pics[0], style, m)
        return canvas
    fill = style.fit == "fill"
    if template == "single" and fill:
        canvas.paste(_cover(pics[0], W, H), (0, 0))
    else:
        rects = [_place(canvas, pic, cell, fill, radius)
                 for pic, cell in zip(pics, _cells(template, W, H, m))]
        if template == "before_after":
            font = _font(max(10, round(W * 0.03)))
            inset = round(W * 0.025)
            for label, (rx0, ry0, rx1, _) in zip(("Before", "After"), rects):
                _text_pill(canvas, label, font, left=rx0 + inset, top=ry0 + inset,
                           max_w=max(40, rx1 - rx0 - 2 * inset))
    _draw_caption(canvas, style, m)
    return canvas


def render_story(images: Sequence[ImageSource], template: str, style: Optional[StyleOptions] = None,
                 size: tuple[int, int] = STORY) -> Image.Image:
    """Render one story/post image. Fewer photos than the template needs → simpler template."""
    style = style or StyleOptions()
    need = template_slots(template)
    if not images:
        raise ValueError("No photos to render")
    if len(images) < need:
        template = "single" if template == "before_after" else _FALLBACK[len(images)]
        need = len(images)
    pics = [_load(p) for p in images[:need]]
    return _compose(pics, template, style, (int(size[0]), int(size[1])))


def render_carousel(images: Sequence[ImageSource], style: Optional[StyleOptions] = None,
                    size: tuple[int, int] = POST, panorama: bool = False) -> list[Image.Image]:
    """One slide per photo, or (panorama with exactly one photo) a seamless multi-slide split."""
    style = style or StyleOptions()
    if panorama and len(images) == 1:
        return _panorama_slides(images[0], style, size)
    return [render_story([p], "single", style, size) for p in images]


def panorama_slide_count(width: int, height: int, size: tuple[int, int] = POST) -> int:
    return int(max(2, min(10, round((width / height) / (size[0] / size[1])))))


def _panorama_slides(src: ImageSource, style: StyleOptions, size: tuple[int, int]) -> list[Image.Image]:
    W, H = size
    img = _load(src, max_side=None) if not isinstance(src, Image.Image) else src.convert("RGB")
    n = panorama_slide_count(img.width, img.height, size)
    strip = _cover(img, n * W, H, smart=True)
    slides = [strip.crop((k * W, 0, (k + 1) * W, H)) for k in range(n)]
    if style.caption.strip():
        _draw_caption(slides[0], style, round(style.margin * W / 1080))
    return slides


# ----------------------------------------------------------------------------- export

def _save_jpeg(img: Image.Image, out_dir: Path, name: str) -> Path:
    tmp = out_dir / f".{Path(name).stem}.{uuid.uuid4().hex[:8]}.partial"
    try:
        img.save(tmp, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
        return publish_file(tmp, out_dir / name)
    finally:
        if tmp.exists():
            tmp.unlink()


def _cleanup(paths: list[Path]) -> None:
    for p in paths:
        try:
            p.unlink()
        except OSError:
            pass


def export_stories(images: Sequence[ImageSource], template: str, style: Optional[StyleOptions],
                   out_dir: Path, size: tuple[int, int] = STORY,
                   progress: Optional[Progress] = None) -> list[Path]:
    """Chunk photos into template-sized groups and save each as story-001.jpg, story-002.jpg…

    All-or-nothing: on cancel the files written by this call are removed.
    """
    n = template_slots(template)
    groups = [list(images[i:i + n]) for i in range(0, len(images), n)]
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    try:
        for i, group in enumerate(groups):
            if progress is not None:
                progress.update(i, len(groups), f"Making story {i + 1} of {len(groups)}…")
            img = render_story(group, template, style, size)
            written.append(_save_jpeg(img, out_dir, f"story-{i + 1:03d}.jpg"))
        if progress is not None:
            progress.update(len(groups), len(groups), "Done", force=True)
    except BaseException:
        _cleanup(written)
        raise
    return written


def export_carousel(images: Sequence[ImageSource], style: Optional[StyleOptions], out_dir: Path,
                    size: tuple[int, int] = POST, panorama: bool = False,
                    progress: Optional[Progress] = None) -> list[Path]:
    """Save carousel slides as carousel-01.jpg, carousel-02.jpg… (all-or-nothing on cancel)."""
    style = style or StyleOptions()
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    try:
        if panorama and len(images) == 1:
            if progress is not None:
                progress.update(0, 1, "Splitting panorama…", force=True)
            slides = _panorama_slides(images[0], style, size)
            total = len(slides)
            source = iter(slides)
            render = lambda i: next(source)  # noqa: E731
        else:
            total = len(images)
            render = lambda i: render_story([images[i]], "single", style, size)  # noqa: E731
        for i in range(total):
            if progress is not None:
                progress.update(i, total, f"Making slide {i + 1} of {total}…")
            written.append(_save_jpeg(render(i), out_dir, f"carousel-{i + 1:02d}.jpg"))
        if progress is not None:
            progress.update(total, total, "Done", force=True)
    except BaseException:
        _cleanup(written)
        raise
    return written


# ----------------------------------------------------------------------------- story video

def _even(v: float) -> int:
    return max(2, int(round(v / 2)) * 2)


def story_video_duration(n: int, seconds_per_photo: float = 3.0, transition: float = 0.6) -> float:
    tr = max(0.0, min(transition, seconds_per_photo / 2))
    return n * seconds_per_photo - (n - 1) * tr if n else 0.0


def make_story_video(images: Sequence[ImageSource], out_path_dir: Path, seconds_per_photo: float = 3.0,
                     transition: float = 0.6, ken_burns: bool = True,
                     style: Optional[StyleOptions] = None, size: tuple[int, int] = STORY,
                     fps: int = 30, music: Optional[Path] = None,
                     progress: Optional[Progress] = None) -> Path:
    """Slideshow video with optional Ken Burns motion, crossfades and music → story-video.mp4."""
    if not images:
        raise ValueError("No photos for the video")
    if seconds_per_photo <= 0 or fps <= 0:
        raise ValueError("seconds_per_photo and fps must be positive")
    exe = ffmpeg.ffmpeg_exe()
    if not exe:
        raise RuntimeError("FFmpeg is not available.")
    style = style or StyleOptions()
    W, H = _even(size[0]), _even(size[1])
    n = len(images)
    spp = float(seconds_per_photo)
    tr = max(0.0, min(float(transition), spp / 2))
    step = spp - tr
    duration = story_video_duration(n, spp, tr)
    frames = max(1, int(round(duration * fps)))
    k = 1 + KEN_BURNS_ZOOM if ken_burns else 1.0
    base_size = (_even(W * k), _even(H * k)) if ken_burns else (W, H)

    out_dir = Path(out_path_dir).absolute()
    out_dir.mkdir(parents=True, exist_ok=True)
    work = out_dir / f".memoria-work-{uuid.uuid4().hex[:10]}"
    work.mkdir()
    tmp_out = work / "story-video.mp4"
    log_path = work / "ffmpeg.log"

    cmd = [exe, "-hide_banner", "-nostdin", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-framerate", str(fps), "-i", "pipe:0"]
    if music:
        cmd += ["-i", str(Path(music).absolute())]
    cmd += ["-map", "0:v:0", "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
            "-color_range", "tv"]
    if music:
        fade_start = max(0.0, duration - 1.0)
        cmd += ["-map", "1:a:0?", "-c:a", "aac", "-b:a", "192k",
                "-af", f"afade=t=out:st={fade_start:.3f}:d=1"]
    cmd += ["-t", f"{duration:.3f}", "-movflags", "+faststart", str(tmp_out)]

    try:
        import cv2  # fast multithreaded warp; Pillow fallback below
    except Exception:  # pragma: no cover - opencv is a project dependency
        cv2 = None

    bases: dict[int, np.ndarray] = {}

    def base(i: int) -> np.ndarray:
        # Each photo is rendered once (slightly oversized for Ken Burns) and kept as an array
        # only while it is on screen.
        if i not in bases:
            for old in [j for j in bases if j < i - 1]:
                del bases[old]
            bases[i] = np.array(_compose([_load(images[i])], "single", style, base_size))
        return bases[i]

    def frame_of(i: int, t: float) -> np.ndarray:
        b = base(i)
        if not ken_burns:
            return b
        p = min(max((t - i * step) / spp, 0.0), 1.0)
        z = 1.0 + KEN_BURNS_ZOOM * p
        bh, bw = b.shape[:2]
        ww, wh = bw / z, bh / z
        direction = 1 if i % 2 == 0 else -1
        x0 = min(max(bw / 2 + direction * (bw - ww) / 2 * 0.8 - ww / 2, 0.0), bw - ww)
        y0 = min(max(bh / 2 - (bh - wh) / 2 * 0.4 - wh / 2, 0.0), bh - wh)
        sx, sy = ww / W, wh / H
        if cv2 is not None:
            m = np.array([[sx, 0, x0 + 0.5 * sx - 0.5], [0, sy, y0 + 0.5 * sy - 0.5]], np.float32)
            return cv2.warpAffine(b, m, (W, H), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP,
                                  borderMode=cv2.BORDER_REPLICATE)
        return np.asarray(Image.fromarray(b).resize((W, H), Image.Resampling.BILINEAR,
                                                    box=(x0, y0, x0 + ww, y0 + wh)))

    def blend(a: np.ndarray, b: np.ndarray, alpha: float) -> np.ndarray:
        if cv2 is not None:
            return cv2.addWeighted(a, 1.0 - alpha, b, alpha, 0.0)
        return np.asarray(Image.blend(Image.fromarray(a), Image.fromarray(b), alpha))

    proc: Optional[subprocess.Popen] = None
    pipe_failed = threading.Event()
    frames_q: queue.Queue = queue.Queue(maxsize=4)

    def writer() -> None:
        # Writes overlap with rendering of the next frames.
        while True:
            item = frames_q.get()
            if item is None:
                return
            if pipe_failed.is_set():
                continue
            try:
                proc.stdin.write(memoryview(np.ascontiguousarray(item)).cast("B"))
            except (OSError, ValueError):
                pipe_failed.set()

    try:
        with open(log_path, "wb") as errf:
            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=errf,
                                    cwd=str(work), creationflags=ffmpeg.CREATE_NO_WINDOW)
            assert proc.stdin is not None
            thread = threading.Thread(target=writer, name="story-video-writer", daemon=True)
            thread.start()
            try:
                for f in range(frames):
                    if progress is not None:
                        progress.update(f, frames, "Rendering video…")
                    if pipe_failed.is_set():
                        break
                    t = f / fps
                    i = min(int(t / step + 1e-9) if step > 0 else 0, n - 1)
                    if i > 0 and t < (i - 1) * step + spp:  # crossfade from the previous photo
                        a = min(max((t - i * step) / tr, 0.0), 1.0) if tr > 0 else 1.0
                        frames_q.put(blend(frame_of(i - 1, t), frame_of(i, t), a))
                    else:
                        frames_q.put(frame_of(i, t))
            except BaseException:
                proc.kill()
                raise
            finally:
                frames_q.put(None)
                thread.join()
            try:
                proc.stdin.close()
            except OSError:
                pass
            if progress is not None:
                progress.update(frames, frames, "Finishing video…", force=True)
            proc.wait()
        if proc.returncode != 0 or pipe_failed.is_set() or not tmp_out.exists():
            tail = log_path.read_text("utf-8", "replace").strip().splitlines()[-5:]
            raise RuntimeError("Video encoding failed: " + " | ".join(tail))
        return publish_file(tmp_out, out_dir / "story-video.mp4")
    except BaseException:
        if proc is not None and proc.poll() is None:
            proc.kill()
        if proc is not None:
            proc.wait()
        raise
    finally:
        bases.clear()
        shutil.rmtree(work, ignore_errors=True)
