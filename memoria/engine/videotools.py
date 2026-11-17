"""Smart video compressor (libx264 + AAC) with verification and quality measurement.

Source files are never modified. Every output is written into a private work folder inside
the chosen output folder and only renamed into place once it has been verified.
"""
from __future__ import annotations

import math
import os
import re
import shutil
import subprocess
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from . import actions, ffmpeg
from .ffmpeg import VideoInfo, probe
from .progress import Cancelled, Progress

MB = 1024 * 1024
QUALITY_CRF = {"high": 20, "balanced": 24, "small": 28}
# Rough bits-per-pixel-per-frame that x264 tends to land on at each CRF (for estimates only).
_BPP = {"high": 0.09, "balanced": 0.055, "small": 0.032}
MIN_VIDEO_KBPS = 150
_PAYLOAD_SHARE = 0.97  # leave a little of the target for MP4 container overhead
_TOTAL = 1000  # progress units per file
_SSIM_MAX_FRAMES = 600
_SSIM_RE = re.compile(r"All:\s*([0-9.]+)")


@dataclass
class CompressSettings:
    mode: str = "quality"        # "quality" | "target"
    quality: str = "balanced"    # "high" (crf 20) | "balanced" (crf 24) | "small" (crf 28)
    target_mb: float = 25.0      # used when mode == "target": two-pass ABR to fit under target
    max_height: Optional[int] = 1080  # limit for the *shorter* side (portrait-safe); None = keep
    audio_kbps: int = 128
    measure_quality: bool = True  # compute SSIM between source and output


@dataclass
class CompressResult:
    src: Path
    dst: Optional[Path]
    src_bytes: int
    dst_bytes: int
    duration_src: float
    duration_dst: float
    ssim: Optional[float]
    ok: bool
    message: str

    @property
    def saved_pct(self) -> float:
        if not self.ok or not self.src_bytes or not self.dst_bytes:
            return 0.0
        return round((1 - self.dst_bytes / self.src_bytes) * 100, 1)


class FFmpegFailed(RuntimeError):
    pass


# ----------------------------------------------------------------------------- file helpers

def unique_path(path: Path) -> Path:
    """``path`` if free, else ``name (2).ext``, ``name (3).ext``…"""
    path = Path(path)
    if not path.exists():
        return path
    n = 2
    while True:
        cand = path.with_name(f"{path.stem} ({n}){path.suffix}")
        if not cand.exists():
            return cand
        n += 1


def publish_file(tmp: Path, wanted: Path) -> Path:
    """Rename a finished temp file to a unique name next to ``wanted``; never overwrites."""
    while True:
        dst = unique_path(wanted)
        try:
            with actions.record_output(tmp, dst):
                if os.name == "nt":
                    os.rename(tmp, dst)  # fails if dst exists
                else:
                    os.link(tmp, dst)  # fails if dst exists
                    os.unlink(tmp)
            return dst
        except FileExistsError:
            continue


def fmt_mb(n: int) -> str:
    return f"{n / MB:.1f} MB"


# ----------------------------------------------------------------------------- planning

def _output_dims(info: VideoInfo, max_height: Optional[int]) -> tuple[int, int]:
    w, h = info.width, info.height
    short = min(w, h)
    if max_height and short > max_height:
        s = max_height / short
        return max(2, round(w * s / 2) * 2), max(2, round(h * s / 2) * 2)
    return w // 2 * 2, h // 2 * 2


def _audio_kbps(info: VideoInfo, settings: CompressSettings) -> int:
    if not info.has_audio:
        return 0
    a = settings.audio_kbps
    if info.audio_kbps:
        a = min(a, max(info.audio_kbps, 48))
    return a


def _target_rates(info: VideoInfo, settings: CompressSettings) -> tuple[int, int, bool]:
    """(video_kbps, audio_kbps, feasible) for target-size mode."""
    dur = max(info.duration, 0.1)
    total_kbps = settings.target_mb * MB * 8 * _PAYLOAD_SHARE / dur / 1000
    a = _audio_kbps(info, settings)
    v = total_kbps - a
    if a > 64 and v < 400:
        a = 64
        v = total_kbps - a
    feasible = v >= MIN_VIDEO_KBPS
    return int(max(v, MIN_VIDEO_KBPS)), a, feasible


def estimate(info: VideoInfo, settings: CompressSettings) -> dict:
    """Quick size estimate without encoding. Returns {"est_mb", "note", ...}."""
    w, h = _output_dims(info, settings.max_height)
    dur = info.duration
    src_mb = info.bitrate_kbps * 1000 * dur / 8 / MB if info.bitrate_kbps and dur else None
    out = {"width": w, "height": h, "feasible": True, "src_mb": round(src_mb, 1) if src_mb else None}
    if dur <= 0:
        out.update(est_mb=None, video_kbps=None, audio_kbps=None,
                   note="Unknown duration; can't estimate the size.")
        return out
    if settings.mode == "target":
        v, a, feasible = _target_rates(info, settings)
        est = min(settings.target_mb, (v + a) * 1000 * dur / 8 / MB)
        out.update(video_kbps=v, audio_kbps=a, feasible=feasible)
        if not feasible:
            need = (MIN_VIDEO_KBPS + min(a, 64)) * 1000 * dur / 8 / MB / _PAYLOAD_SHARE
            est = (v + a) * 1000 * dur / 8 / MB
            note = (f"{settings.target_mb:g} MB is too small for a {dur:.0f} s video — it needs at least "
                    f"{need:.1f} MB to stay watchable. The result will be larger than the target.")
        elif src_mb and src_mb <= settings.target_mb:
            note = "This video is already under the target size; savings may be small."
        else:
            note = f"Two-pass encode to fit under {settings.target_mb:g} MB (video ≈ {v} kbps, {w}×{h})."
        out.update(est_mb=round(est, 3), note=note)
        return out
    fps = info.fps if info.fps and info.fps < 241 else 30.0
    v = _BPP.get(settings.quality, _BPP["balanced"]) * w * h * fps / 1000
    src_v = info.bitrate_kbps - info.audio_kbps if info.bitrate_kbps else 0
    if src_v > 0:
        v = min(v, src_v * 0.9)
    a = _audio_kbps(info, settings)
    est = (v + a) * 1000 * dur / 8 / MB
    note = f"Estimate only ({w}×{h}); the real size depends on how much motion and detail there is."
    if src_mb and est > src_mb * 0.85:
        note = "This video is already compact; savings will probably be small."
    out.update(est_mb=round(est, 3), video_kbps=int(v), audio_kbps=a, note=note)
    return out


# ----------------------------------------------------------------------------- ffmpeg runner

def _tail(path: Path, lines: int = 6) -> str:
    try:
        text = path.read_text("utf-8", "replace").strip().splitlines()
    except OSError:
        return ""
    return " | ".join(l.strip() for l in text[-lines:])


def _run(args: list[str], cwd: Path, log: Path, duration: float,
         progress: Optional[Progress], base: float, span: float, message: str) -> None:
    """Run ffmpeg with machine-readable progress; maps output time onto [base, base+span]."""
    exe = ffmpeg.ffmpeg_exe()
    if not exe:
        raise FFmpegFailed("FFmpeg is not available.")
    cmd = [exe, "-hide_banner", "-nostdin", "-y", "-progress", "pipe:1", "-nostats", *args]
    with open(log, "wb") as errf:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=errf, stdin=subprocess.DEVNULL,
                                cwd=str(cwd), creationflags=ffmpeg.CREATE_NO_WINDOW)
        try:
            assert proc.stdout is not None
            for raw in proc.stdout:
                key, _, val = raw.decode("ascii", "replace").strip().partition("=")
                if key in ("out_time_us", "out_time_ms"):
                    try:
                        t = int(val) / 1e6
                    except ValueError:
                        continue
                    frac = min(max(t / duration, 0.0), 1.0) if duration > 0 else 0.0
                    if progress is not None:
                        progress.update(int(base + span * frac), _TOTAL, message)
                elif key == "progress" and progress is not None:
                    progress.check()
            proc.wait()
        except BaseException:
            proc.kill()
            proc.wait()
            raise
        finally:
            if proc.stdout:
                proc.stdout.close()
    if proc.returncode != 0:
        raise FFmpegFailed(_tail(log) or f"ffmpeg exited with code {proc.returncode}")


def _measure_ssim(src: Path, out: Path, info: VideoInfo, out_w: int, out_h: int, work: Path,
                  progress: Optional[Progress], base: float, span: float) -> Optional[float]:
    frames = info.duration * (info.fps or 30)
    step = max(1, math.ceil(frames / _SSIM_MAX_FRAMES))
    pre = f"framestep={step}," if step > 1 else ""
    graph = (f"[0:v]{pre}setpts=PTS-STARTPTS,format=yuv420p[d];"
             f"[1:v]{pre}scale={out_w}:{out_h}:flags=bicubic,setpts=PTS-STARTPTS,format=yuv420p[s];"
             f"[d][s]ssim")
    log = work / "ssim.log"
    try:
        _run(["-i", str(out.absolute()), "-i", str(src.absolute()), "-lavfi", graph, "-an", "-f", "null", os.devnull],
             work, log, info.duration, progress, base, span, "Measuring quality…")
    except FFmpegFailed:
        return None
    m = None
    for m in _SSIM_RE.finditer(log.read_text("utf-8", "replace")):
        pass
    if not m:
        return None
    try:
        return round(float(m[1]), 4)
    except ValueError:
        return None


# ----------------------------------------------------------------------------- compress

def compress(src: Path, out_dir: Path, settings: CompressSettings,
             progress: Optional[Progress] = None) -> CompressResult:
    src, out_dir = Path(src), Path(out_dir).absolute()
    try:
        src_bytes = src.stat().st_size
    except OSError as e:
        return CompressResult(src, None, 0, 0, 0.0, 0.0, None, False, f"Can't open the video: {e}")
    fail = lambda msg, dur=0.0, dur2=0.0: CompressResult(  # noqa: E731
        src, None, src_bytes, 0, dur, dur2, None, False, msg)
    if progress is not None:
        progress.update(0, _TOTAL, f"Reading {src.name}…", force=True)
    try:
        info = probe(src)
    except Exception as e:
        return fail(f"Can't read the video: {e}")
    if info.duration <= 0:
        return fail("Can't tell how long this video is; skipped.")

    w, h = _output_dims(info, settings.max_height)
    a_kbps = _audio_kbps(info, settings)
    encode_span = _TOTAL * (0.85 if settings.measure_quality else 1.0)
    two_pass = settings.mode == "target"
    target_note = ""
    if two_pass:
        v_kbps, a_kbps, feasible = _target_rates(info, settings)
        if not feasible:
            target_note = f"; {settings.target_mb:g} MB was too small, used the lowest watchable bitrate"

    out_dir.mkdir(parents=True, exist_ok=True)
    work = out_dir / f".memoria-work-{uuid.uuid4().hex[:10]}"
    work.mkdir()
    tmp_out = work / "output.mp4"
    try:
        vf = [] if (w, h) == (info.width, info.height) else ["-vf", f"scale={w}:{h}:flags=lanczos"]
        video = ["-map", "0:v:0", *vf, "-c:v", "libx264", "-pix_fmt", "yuv420p"]
        audio = ["-map", "0:a:0", "-c:a", "aac", "-b:a", f"{a_kbps}k"] if info.has_audio else []
        tail = ["-map_metadata", "0", "-movflags", "+faststart", "-max_muxing_queue_size", "1024",
                "-sn", "-dn", str(tmp_out.name)]
        inp = ["-i", str(src.absolute())]
        try:
            if two_pass:
                rate = ["-b:v", f"{v_kbps}k", "-preset", "medium", "-passlogfile", "x264pass"]
                half = encode_span / 2
                _run([*inp, *video, *rate, "-pass", "1", "-an", "-f", "null", os.devnull],
                     work, work / "pass1.log", info.duration, progress, 0, half, "Analysing (pass 1 of 2)…")
                _run([*inp, *video, *rate, "-pass", "2", *audio, *tail],
                     work, work / "pass2.log", info.duration, progress, half, half, "Compressing (pass 2 of 2)…")
            else:
                crf = QUALITY_CRF.get(settings.quality, QUALITY_CRF["balanced"])
                _run([*inp, *video, "-crf", str(crf), "-preset", "medium", *audio, *tail],
                     work, work / "encode.log", info.duration, progress, 0, encode_span, "Compressing…")
        except FFmpegFailed as e:
            return fail(f"Compression failed: {e}", info.duration)

        try:
            out_info = probe(tmp_out)
        except Exception:
            return fail("The compressed copy could not be read back, so it was discarded.", info.duration)
        tol = max(0.5, 0.02 * info.duration)
        if abs(out_info.duration - info.duration) > tol:
            return fail(f"The compressed copy is {out_info.duration:.1f} s long instead of "
                        f"{info.duration:.1f} s, so it was discarded.", info.duration, out_info.duration)
        dst_bytes = tmp_out.stat().st_size
        if dst_bytes >= src_bytes:
            return fail("Compressed copy was not smaller; kept original only",
                        info.duration, out_info.duration)

        ssim = None
        if settings.measure_quality:
            ssim = _measure_ssim(src, tmp_out, info, out_info.width, out_info.height, work,
                                 progress, encode_span, _TOTAL - encode_span)

        dst = publish_file(tmp_out, out_dir / f"{src.stem} (compressed).mp4")
        try:
            st = src.stat()
            os.utime(dst, (st.st_atime, st.st_mtime))
        except OSError:
            pass
        pct = (1 - dst_bytes / src_bytes) * 100
        msg = f"{fmt_mb(src_bytes)} → {fmt_mb(dst_bytes)} ({pct:.0f}% smaller)"
        if ssim is not None:
            msg += f", quality SSIM {ssim:.3f}"
        if two_pass and dst_bytes > settings.target_mb * MB:
            msg += target_note or f"; slightly over the {settings.target_mb:g} MB target"
        if progress is not None:
            progress.update(_TOTAL, _TOTAL, "Done", force=True)
        return CompressResult(src, dst, src_bytes, dst_bytes, info.duration, out_info.duration,
                              ssim, True, msg)
    except Cancelled:
        raise
    except Exception as e:
        return fail(f"Compression failed: {e}")
    finally:
        shutil.rmtree(work, ignore_errors=True)


class _SubProgress(Progress):
    """Maps one file's 0..total progress onto a slice of a batch-wide Progress."""

    def __init__(self, parent: Progress, index: int, count: int, label: str):
        super().__init__(None, parent.cancel_event, pause=parent.pause_event)
        self._parent, self._index, self._count, self._label = parent, index, count, label

    def update(self, done: int, total: int, message: str = "", force: bool = False, detail=None) -> None:
        frac = min(max(done / total, 0.0), 1.0) if total else 0.0
        self._parent.update(int((self._index + frac) * _TOTAL), self._count * _TOTAL,
                            f"{self._label} ({self._index + 1}/{self._count}) — {message}", force, detail=detail)


def compress_many(files: list[Path], out_dir: Path, settings: CompressSettings,
                  progress: Optional[Progress] = None) -> list[CompressResult]:
    results: list[CompressResult] = []
    n = len(files)
    for i, f in enumerate(files):
        f = Path(f)
        if progress is not None:
            progress.check()
        sub = _SubProgress(progress, i, n, f.name) if progress is not None else None
        try:
            results.append(compress(f, out_dir, settings, sub))
        except Cancelled:
            raise
        except Exception as e:  # pragma: no cover - compress already reports failures
            size = f.stat().st_size if f.exists() else 0
            results.append(CompressResult(f, None, size, 0, 0.0, 0.0, None, False, f"Failed: {e}"))
    if progress is not None and n:
        progress.update(n * _TOTAL, n * _TOTAL, "Done", force=True)
    return results
