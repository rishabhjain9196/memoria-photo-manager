"""FFmpeg helpers: probing, video thumbnails and frames. Uses the imageio-ffmpeg binary."""
from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Optional

CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0


@lru_cache(maxsize=1)
def ffmpeg_exe() -> Optional[str]:
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        from shutil import which

        return which("ffmpeg")


def run_ffmpeg(args: list[str], timeout: Optional[float] = None, **kw) -> subprocess.CompletedProcess:
    exe = ffmpeg_exe()
    if not exe:
        raise RuntimeError("FFmpeg is not available. Install the 'imageio-ffmpeg' package.")
    return subprocess.run([exe, "-hide_banner", "-nostdin", *args], capture_output=True,
                          timeout=timeout, creationflags=CREATE_NO_WINDOW, **kw)


@dataclass
class VideoInfo:
    duration: float = 0.0
    width: int = 0
    height: int = 0
    fps: float = 0.0
    vcodec: str = ""
    acodec: str = ""
    bitrate_kbps: int = 0
    audio_kbps: int = 0
    rotation: int = 0
    creation_time: Optional[datetime] = None

    @property
    def has_audio(self) -> bool:
        return bool(self.acodec)


_DUR = re.compile(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)")
_BR = re.compile(r"Duration:.*?bitrate:\s*(\d+)\s*kb/s")
_VID = re.compile(r"Stream #\S+.*?Video:\s*(\w+).*?(\d{2,5})x(\d{2,5})")
_FPS = re.compile(r"(\d+(?:\.\d+)?)\s*fps")
_AUD = re.compile(r"Stream #\S+.*?Audio:\s*(\w+)(?:.*?(\d+)\s*kb/s)?")
_CT = re.compile(r"creation_time\s*:\s*(\d{4}-\d{2}-\d{2})[T ](\d{2}:\d{2}:\d{2})")
_ROT = re.compile(r"(?:rotate\s*:\s*|rotation of\s*)(-?\d+)")


def probe(path: str | Path) -> VideoInfo:
    proc = run_ffmpeg(["-i", str(path)], timeout=60)
    text = proc.stderr.decode("utf-8", "replace")
    info = VideoInfo()
    if m := _DUR.search(text):
        info.duration = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])
    if m := _BR.search(text):
        info.bitrate_kbps = int(m[1])
    for line in text.splitlines():
        if "Video:" in line and not info.vcodec and (m := _VID.search(line)):
            info.vcodec, info.width, info.height = m[1], int(m[2]), int(m[3])
            if f := _FPS.search(line):
                info.fps = float(f[1])
        elif "Audio:" in line and not info.acodec and (m := _AUD.search(line)):
            info.acodec = m[1]
            info.audio_kbps = int(m[2]) if m[2] else 0
    if m := _ROT.search(text):
        info.rotation = int(m[1]) % 360
        if info.rotation in (90, 270):
            info.width, info.height = info.height, info.width
    if m := _CT.search(text):
        try:
            dt = datetime.strptime(f"{m[1]} {m[2]}", "%Y-%m-%d %H:%M:%S")
            if dt.year >= 1990:
                info.creation_time = dt
        except ValueError:
            pass
    if not info.vcodec:
        raise ValueError("No video stream found")
    return info


def video_frame(path: str | Path, at: float = 1.0, max_side: int = 512) -> Optional[bytes]:
    """Grab one frame as JPEG bytes, scaled so the longest side is ``max_side``."""
    vf = f"scale='if(gt(iw,ih),{max_side},-2)':'if(gt(iw,ih),-2,{max_side})'"
    proc = run_ffmpeg(["-ss", f"{max(0.0, at):.2f}", "-i", str(path), "-frames:v", "1", "-vf", vf,
                       "-f", "image2pipe", "-vcodec", "mjpeg", "-q:v", "4", "-"], timeout=60)
    if proc.returncode != 0 or not proc.stdout:
        if at > 0:
            return video_frame(path, 0.0, max_side)
        return None
    return proc.stdout
