"""Non-destructive video editing: trim, rotate/flip, crop, colour, speed, mute, resize, split,
join and frame extraction (FFmpeg: libx264 + AAC).

Trust rules (same as :mod:`videotools`): sources are never modified; every output is encoded
into a private ``.memoria-work-*`` folder inside the output folder, probed and checked against
the expected duration (± max(0.5 s, 3 %)), given the source's modification time and only then
renamed to a unique name. The work folder is always removed, so failures and cancellations
leave nothing behind. Multi-file operations (split) are all-or-nothing.

Video filter chain built by :func:`filter_graph` (FFmpeg auto-rotates the input first, so all
geometry is relative to the upright display frame)::

    transpose (rotate 90 → transpose=1, 180 → hflip,vflip, 270 → transpose=2)
    → hflip / vflip → crop=W:H:X:Y (even, in the rotated frame)
    → eq=brightness=B:contrast=C:saturation=S → scale=W:H (max_height on the shorter side; even
    dims) → setsar=1 → setpts=PTS/speed

Audio: ``atempo`` (chained so each factor stays within 0.5–2.0) for speed, removed with mute.
Trimming uses input seeking (``-ss start -t length`` before ``-i``), which is frame-accurate
when re-encoding.
"""
from __future__ import annotations

import io
import os
import shutil
import uuid
from dataclasses import dataclass, replace
from datetime import timedelta
from pathlib import Path
from typing import Optional

from . import ffmpeg
from .ffmpeg import VideoInfo, probe
from .progress import Cancelled, Progress
from .videotools import QUALITY_CRF, FFmpegFailed, _run, publish_file

SPEEDS = (0.5, 1.0, 1.5, 2.0)
_TOTAL = 1000            # progress units used by videotools._run
_MIN_PART = 0.1          # split points closer than this to a boundary are ignored
_JOIN_MAX_SHORT = 1080
_JOIN_FPS = 30
_AUDIO_KBPS = 160


class VideoEditError(RuntimeError):
    pass


@dataclass
class VideoEdit:
    start: float = 0.0
    end: Optional[float] = None          # None = to the end
    rotate: int = 0                      # 0/90/180/270 clockwise
    flip_h: bool = False
    flip_v: bool = False
    crop: Optional[tuple[float, float, float, float]] = None  # normalized, after rotate/flip
    brightness: int = 0                  # -100..100 → eq brightness ±0.25
    contrast: int = 0                    # -100..100 → eq contrast 0.5..1.5
    saturation: int = 0                  # -100..100 → eq saturation 0..2
    speed: float = 1.0
    mute: bool = False
    max_height: Optional[int] = None     # limit for the SHORTER side (portrait-safe), even dims
    quality: str = "balanced"            # high|balanced|small → CRF 20/24/28

    def is_identity(self) -> bool:
        return (self.start <= 0 and self.end is None and self.rotate % 360 == 0
                and not self.flip_h and not self.flip_v and _crop_is_full(self.crop)
                and not (self.brightness or self.contrast or self.saturation)
                and abs(self.speed - 1.0) < 1e-9 and not self.mute and not self.max_height
                and self.quality == "balanced")

    def copy(self, **changes) -> "VideoEdit":
        return replace(self, **changes)


# ----------------------------------------------------------------------------- planning

def _crop_is_full(crop) -> bool:
    if crop is None:
        return True
    l, t, r, b = crop
    return l <= 0.0005 and t <= 0.0005 and r >= 0.9995 and b >= 0.9995


def _span(info: VideoInfo, edit: VideoEdit) -> tuple[float, float]:
    """(start, end) in the original timeline, clamped to the video."""
    dur = max(info.duration, 0.0)
    start = min(max(0.0, float(edit.start or 0.0)), dur)
    end = dur if edit.end is None else min(max(float(edit.end), 0.0), dur)
    if end <= start:
        raise VideoEditError("The trimmed video would be empty")
    return start, end


def output_duration(info: VideoInfo, edit: VideoEdit) -> float:
    start, end = _span(info, edit)
    return (end - start) / (edit.speed or 1.0)


def _rotated_dims(info: VideoInfo, edit: VideoEdit) -> tuple[int, int]:
    w, h = info.width, info.height
    return (h, w) if edit.rotate % 360 in (90, 270) else (w, h)


def _crop_px(w: int, h: int, crop) -> Optional[tuple[int, int, int, int]]:
    """Even-sized pixel crop (cw, ch, x, y) inside a w×h frame, or None for no crop."""
    if _crop_is_full(crop):
        return None
    l, t, r, b = (min(1.0, max(0.0, float(v))) for v in crop)
    l, r = min(l, r), max(l, r)
    t, b = min(t, b), max(t, b)
    cw = max(2, int(round((r - l) * w)) // 2 * 2)
    ch = max(2, int(round((b - t) * h)) // 2 * 2)
    cw, ch = min(cw, w // 2 * 2), min(ch, h // 2 * 2)
    x = min(max(0, int(round(l * w))), w - cw)
    y = min(max(0, int(round(t * h))), h - ch)
    return cw, ch, x, y


def output_size(info: VideoInfo, edit: VideoEdit) -> tuple[int, int]:
    """Final (width, height) of :func:`export` — always even."""
    w, h = _rotated_dims(info, edit)
    c = _crop_px(w, h, edit.crop)
    if c:
        w, h = c[0], c[1]
    short = min(w, h)
    if edit.max_height and short > edit.max_height:
        s = edit.max_height / short
        return max(2, round(w * s / 2) * 2), max(2, round(h * s / 2) * 2)
    return max(2, w // 2 * 2), max(2, h // 2 * 2)


def _geometry_filters(info: VideoInfo, edit: VideoEdit, crop: bool = True, exact: bool = True) -> list[str]:
    f: list[str] = []
    rot = edit.rotate % 360
    if rot == 90:
        f.append("transpose=1")
    elif rot == 180:
        f += ["hflip", "vflip"]
    elif rot == 270:
        f.append("transpose=2")
    if edit.flip_h:
        f.append("hflip")
    if edit.flip_v:
        f.append("vflip")
    if crop and not _crop_is_full(edit.crop):
        if exact:
            cw, ch, x, y = _crop_px(*_rotated_dims(info, edit), edit.crop)
            f.append(f"crop={cw}:{ch}:{x}:{y}")
        else:  # resolution-independent form, used for quick previews
            l, t, r, b = edit.crop
            f.append(f"crop=w=iw*{r - l:.5f}:h=ih*{b - t:.5f}:x=iw*{l:.5f}:y=ih*{t:.5f}")
    return f


def _eq_filter(edit: VideoEdit) -> Optional[str]:
    if not (edit.brightness or edit.contrast or edit.saturation):
        return None
    b = max(-100, min(100, edit.brightness)) / 100 * 0.25
    c = 1 + max(-100, min(100, edit.contrast)) / 100 * 0.5
    s = 1 + max(-100, min(100, edit.saturation)) / 100
    return f"eq=brightness={b:.4f}:contrast={c:.4f}:saturation={s:.4f}"


def filter_graph(info: VideoInfo, edit: VideoEdit) -> str:
    """The ``-vf`` chain used by :func:`export` (see the module docstring); ``"null"`` if empty."""
    f = _geometry_filters(info, edit)
    if eq := _eq_filter(edit):
        f.append(eq)
    w, h = _rotated_dims(info, edit)
    c = _crop_px(w, h, edit.crop)
    if c:
        w, h = c[0], c[1]
    ow, oh = output_size(info, edit)
    if (ow, oh) != (w, h):
        f.append(f"scale={ow}:{oh}:flags=lanczos")
    if f:
        f.append("setsar=1")
    if abs((edit.speed or 1.0) - 1.0) > 1e-9:
        f.append(f"setpts=(PTS-STARTPTS)/{edit.speed:g}")
    return ",".join(f) or "null"


def _atempo(speed: float) -> str:
    parts = []
    while speed > 2.0:
        parts.append(2.0)
        speed /= 2.0
    while speed < 0.5:
        parts.append(0.5)
        speed /= 0.5
    parts.append(speed)
    return ",".join(f"atempo={p:.6g}" for p in parts)


# ----------------------------------------------------------------------------- helpers

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


def _out_dir(src: Path, out_dir) -> Path:
    return Path(out_dir).absolute() if out_dir is not None else src.absolute().parent


def _probe(src: Path) -> VideoInfo:
    try:
        info = probe(src)
    except Exception as e:
        raise VideoEditError(f"Can't read {src.name}: {e}") from e
    if info.duration <= 0:
        raise VideoEditError(f"Can't tell how long {src.name} is")
    return info


def _tolerance(duration: float) -> float:
    return max(0.5, 0.03 * duration)


def _verify(path: Path, expected: float, want_audio: Optional[bool] = None) -> VideoInfo:
    try:
        info = probe(path)
    except Exception as e:
        raise VideoEditError("The new video could not be read back, so it was discarded.") from e
    if abs(info.duration - expected) > _tolerance(expected):
        raise VideoEditError(f"The new video is {info.duration:.1f} s long instead of {expected:.1f} s, "
                             "so it was discarded.")
    if want_audio is not None and info.has_audio != want_audio:
        raise VideoEditError("The new video's sound track is not as expected, so it was discarded.")
    if info.rotation:  # rotation is always baked into the pixels; a leftover flag would turn it again
        raise VideoEditError("The new video came out with the wrong orientation, so it was discarded.")
    return info


def _copy_mtime(src: Path, dst: Path) -> None:
    try:
        st = src.stat()
        os.utime(dst, (st.st_atime, st.st_mtime))
    except OSError:
        pass


def _encode(src: Path, info: VideoInfo, edit: VideoEdit, tmp: Path, work: Path,
            progress: Optional[Progress], base: float, span: float, message: str) -> float:
    """Encode ``src`` with ``edit`` into ``tmp``, verify it; returns the expected duration."""
    start, end = _span(info, edit)
    expected = (end - start) / (edit.speed or 1.0)
    seek = ["-ss", f"{start:.3f}"] if start > 0 else []
    if edit.end is not None and end < info.duration - 1e-3:
        seek += ["-t", f"{end - start:.3f}"]
    audio = info.has_audio and not edit.mute
    crf = QUALITY_CRF.get(edit.quality, QUALITY_CRF["balanced"])
    args = [*seek, "-i", str(src.absolute()), "-map", "0:v:0", "-vf", filter_graph(info, edit),
            "-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-pix_fmt", "yuv420p"]
    if audio:
        args += ["-map", "0:a:0", "-c:a", "aac", "-b:a", f"{_AUDIO_KBPS}k"]
        if abs((edit.speed or 1.0) - 1.0) > 1e-9:
            args += ["-af", _atempo(edit.speed)]
    else:
        args.append("-an")
    args += ["-map_metadata", "0", "-movflags", "+faststart", "-max_muxing_queue_size", "1024",
             "-sn", "-dn", str(tmp)]
    try:
        _run(args, work, work / f"{tmp.stem}.log", expected, progress, base, span, message)
    except FFmpegFailed as e:
        raise VideoEditError(f"Encoding failed: {e}") from e
    _verify(tmp, expected, audio)
    return expected


# ----------------------------------------------------------------------------- preview

def preview_frame(path, t: float, edit: Optional[VideoEdit] = None, max_side: int = 720,
                  crop: bool = True) -> Optional[bytes]:
    """JPEG bytes of the frame at ``t`` (original timeline) with the edit's visual filters.

    ``crop=False`` returns the rotated/flipped frame without the crop (for the crop overlay).
    """
    edit = edit or VideoEdit()
    f = _geometry_filters(VideoInfo(), edit, crop=crop, exact=False)
    f.append(f"scale='if(gt(iw,ih),min(iw,{max_side}),-2)':'if(gt(iw,ih),-2,min(ih,{max_side}))'")
    if eq := _eq_filter(edit):
        f.append(eq)
    for at in (max(0.0, t), max(0.0, t - 1.0)):
        proc = ffmpeg.run_ffmpeg(["-ss", f"{at:.3f}", "-i", str(path), "-frames:v", "1", "-an", "-sn",
                                  "-vf", ",".join(f), "-f", "image2pipe", "-vcodec", "mjpeg",
                                  "-q:v", "3", "-"], timeout=60)
        if proc.returncode == 0 and proc.stdout:
            return proc.stdout
        if at <= 0:
            break
    return None


# ----------------------------------------------------------------------------- export

def export(src, edit: VideoEdit, out_dir=None, suffix: str = " (edited)",
           progress: Optional[Progress] = None) -> Path:
    """Encode an edited copy ``"<stem> (edited).mp4"``; returns its path."""
    src = Path(src)
    out = _out_dir(src, out_dir)
    if progress is not None:
        progress.update(0, _TOTAL, f"Reading {src.name}…", force=True)
    info = _probe(src)
    work = _workdir(out)
    try:
        tmp = work / "output.mp4"
        _encode(src, info, edit, tmp, work, progress, 0, _TOTAL, "Saving video…")
        _copy_mtime(src, tmp)
        if progress is not None:
            progress.check()
        dst = publish_file(tmp, out / f"{src.stem}{suffix}.mp4")
        _finish(progress, _TOTAL)
        return dst
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _publish_all(items: list[tuple[Path, Path]]) -> list[Path]:
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


def split(src, points: list[float], out_dir=None, edit: Optional[VideoEdit] = None,
          progress: Optional[Progress] = None) -> list[Path]:
    """Cut at ``points`` (seconds, original timeline) into ``"<stem> (part i of n).mp4"`` files.

    Points outside (start, end) of ``edit`` are ignored. Each part is re-encoded (frame-accurate)
    with the edit's other settings and verified. All-or-nothing on failure or cancellation.
    """
    src = Path(src)
    edit = edit or VideoEdit()
    if progress is not None:
        progress.update(0, _TOTAL, f"Reading {src.name}…", force=True)
    info = _probe(src)
    start, end = _span(info, edit)
    cuts = sorted({round(float(p), 3) for p in points if start + _MIN_PART < float(p) < end - _MIN_PART})
    cuts = [c for i, c in enumerate(cuts) if i == 0 or c - cuts[i - 1] >= _MIN_PART]
    if not cuts:
        raise VideoEditError("There is nothing to split: no cut points inside the video")
    bounds = [start, *cuts, end]
    n = len(bounds) - 1
    out = _out_dir(src, out_dir)
    weights = [bounds[i + 1] - bounds[i] for i in range(n)]
    total_len = sum(weights)
    work = _workdir(out)
    try:
        items = []
        base = 0.0
        for i in range(n):
            part = edit.copy(start=bounds[i], end=bounds[i + 1])
            tmp = work / f"part-{i + 1}.mp4"
            span = _TOTAL * weights[i] / total_len
            _encode(src, info, part, tmp, work, progress, base, span, f"Saving part {i + 1} of {n}…")
            _copy_mtime(src, tmp)
            items.append((tmp, out / f"{src.stem} (part {i + 1} of {n}).mp4"))
            base += span
        if progress is not None:
            progress.check()
        result = _publish_all(items)
        _finish(progress, _TOTAL)
        return result
    finally:
        shutil.rmtree(work, ignore_errors=True)


def split_equal(src, parts: int, out_dir=None, edit: Optional[VideoEdit] = None,
                progress: Optional[Progress] = None) -> list[Path]:
    """Split into ``parts`` pieces of equal length."""
    parts = int(parts)
    if parts < 2:
        raise VideoEditError("Choose at least two parts")
    edit = edit or VideoEdit()
    start, end = _span(_probe(Path(src)), edit)
    step = (end - start) / parts
    return split(src, [start + i * step for i in range(1, parts)], out_dir, edit, progress)


def split_every(src, seconds: float, out_dir=None, edit: Optional[VideoEdit] = None,
                progress: Optional[Progress] = None) -> list[Path]:
    """Split into pieces of ``seconds`` each (the last one may be shorter, but not tiny)."""
    seconds = float(seconds)
    if seconds <= 0:
        raise VideoEditError("Choose a positive length")
    edit = edit or VideoEdit()
    start, end = _span(_probe(Path(src)), edit)
    points = []
    k = 1
    while start + k * seconds < end - max(_MIN_PART, 0.25):
        points.append(start + k * seconds)
        k += 1
    if not points:
        raise VideoEditError(f"The video is not longer than {seconds:g} s")
    return split(src, points, out_dir, edit, progress)


# ----------------------------------------------------------------------------- join

def _join_size(info: VideoInfo) -> tuple[int, int]:
    w, h = info.width, info.height
    short = min(w, h)
    if short > _JOIN_MAX_SHORT:
        s = _JOIN_MAX_SHORT / short
        w, h = w * s, h * s
    return max(2, int(round(w / 2)) * 2), max(2, int(round(h / 2)) * 2)


def join(paths, out_dir=None, progress: Optional[Progress] = None) -> Path:
    """Concatenate clips in order into ``"<first stem> (joined).mp4"``.

    Every clip is fitted (letterboxed with black) into the first clip's display size (shorter
    side ≤ 1080, even), 30 fps, yuv420p; audio is AAC 48 kHz stereo and clips without sound get
    silence (no audio track at all if none of the clips has sound).
    """
    paths = [Path(p) for p in paths]
    if len(paths) < 2:
        raise VideoEditError("Choose at least two videos to join")
    if progress is not None:
        progress.update(0, _TOTAL, "Reading videos…", force=True)
    infos = [_probe(p) for p in paths]
    W, H = _join_size(infos[0])
    any_audio = any(i.has_audio for i in infos)
    inputs: list[str] = []
    graph: list[str] = []
    concat_in = ""
    for k, (p, info) in enumerate(zip(paths, infos)):
        d = info.duration
        inputs += ["-i", str(p.absolute())]
        graph.append(f"[{k}:v:0]scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos,"
                     f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,fps={_JOIN_FPS},"
                     f"format=yuv420p,trim=duration={d:.3f},setpts=PTS-STARTPTS,"
                     f"sidedata=mode=delete:type=DISPLAYMATRIX[v{k}]")
        concat_in += f"[v{k}]"
        if any_audio:
            if info.has_audio:
                graph.append(f"[{k}:a:0]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,"
                             f"apad,atrim=duration={d:.3f},asetpts=PTS-STARTPTS[a{k}]")
            else:
                graph.append(f"anullsrc=r=48000:cl=stereo,atrim=duration={d:.3f},asetpts=PTS-STARTPTS[a{k}]")
            concat_in += f"[a{k}]"
    n = len(paths)
    graph.append(f"{concat_in}concat=n={n}:v=1:a={1 if any_audio else 0}[v]" + ("[a]" if any_audio else ""))
    expected = sum(i.duration for i in infos)
    out = _out_dir(paths[0], out_dir)
    work = _workdir(out)
    try:
        tmp = work / "joined.mp4"
        args = [*inputs, "-filter_complex", ";".join(graph), "-map", "[v]",
                "-c:v", "libx264", "-preset", "medium", "-crf", str(QUALITY_CRF["balanced"] - 1),
                "-pix_fmt", "yuv420p", "-r", str(_JOIN_FPS)]
        if any_audio:
            args += ["-map", "[a]", "-c:a", "aac", "-b:a", f"{_AUDIO_KBPS}k", "-ar", "48000", "-ac", "2"]
        args += ["-map_metadata", "0", "-movflags", "+faststart", "-max_muxing_queue_size", "1024", str(tmp)]
        try:
            _run(args, work, work / "join.log", expected, progress, 0, _TOTAL, f"Joining {n} videos…")
        except FFmpegFailed as e:
            raise VideoEditError(f"Joining failed: {e}") from e
        _verify(tmp, expected, any_audio)
        _copy_mtime(paths[0], tmp)
        if progress is not None:
            progress.check()
        dst = publish_file(tmp, out / f"{paths[0].stem} (joined).mp4")
        _finish(progress, _TOTAL)
        return dst
    finally:
        shutil.rmtree(work, ignore_errors=True)


# ----------------------------------------------------------------------------- frames

def _stamp(t: float) -> str:
    s = int(max(0.0, t))
    return f"{s // 60}m{s % 60:02d}s"


def extract_frame(src, t: float, out_dir=None) -> Path:
    """Save the frame at ``t`` as a full-resolution JPEG (quality 95), ``"<stem> (frame 0m12s).jpg"``.

    The JPEG's DateTimeOriginal is the video's creation time + ``t`` when known.
    """
    from PIL import Image

    src = Path(src)
    info = _probe(src)
    t = min(max(0.0, float(t)), max(0.0, info.duration - 0.05))
    data = b""
    for at in (t, max(0.0, t - 0.5), 0.0):
        proc = ffmpeg.run_ffmpeg(["-ss", f"{at:.3f}", "-i", str(src.absolute()), "-frames:v", "1", "-an",
                                  "-sn", "-f", "image2pipe", "-vcodec", "png", "-"], timeout=120)
        if proc.returncode == 0 and proc.stdout:
            data = proc.stdout
            break
    if not data:
        raise VideoEditError(f"Couldn't read a frame from {src.name}")
    img = Image.open(io.BytesIO(data)).convert("RGB")
    exif = Image.Exif()
    if info.creation_time:
        exif[0x0112] = 1
        exif[0x8769] = {0x9003: (info.creation_time + timedelta(seconds=t)).strftime("%Y:%m:%d %H:%M:%S")}
    out = _out_dir(src, out_dir)
    work = _workdir(out)
    try:
        tmp = work / "frame.jpg"
        img.save(tmp, "JPEG", quality=95, exif=exif.tobytes() if len(exif) else b"")
        with Image.open(tmp) as check:
            check.load()
            if check.size != img.size:
                raise VideoEditError("The saved frame could not be verified")
        _copy_mtime(src, tmp)
        return publish_file(tmp, out / f"{src.stem} (frame {_stamp(t)}).jpg")
    finally:
        shutil.rmtree(work, ignore_errors=True)

