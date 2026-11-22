"""Constants shared by the engine: media types, library layout and tuning."""
from __future__ import annotations

import os
from pathlib import Path

APP_DIR_NAME = ".memoria"
DB_NAME = "memoria.db"
THUMBS_DB_NAME = "thumbs.db"
RECOVERY_DIR_NAME = "recovery"

IMAGE_EXT = {
    ".jpg", ".jpeg", ".jpe", ".png", ".bmp", ".gif", ".webp", ".tif", ".tiff",
    ".heic", ".heif", ".avif",
}
RAW_EXT = {".raw", ".cr2", ".cr3", ".nef", ".arw", ".dng", ".orf", ".rw2", ".raf"}
VIDEO_EXT = {
    ".mp4", ".mov", ".m4v", ".avi", ".mkv", ".3gp", ".wmv", ".mts", ".m2ts", ".webm", ".vob",
}
MEDIA_EXT = IMAGE_EXT | RAW_EXT | VIDEO_EXT

# Files that operating systems and photo apps leave behind. Safe to tidy away.
JUNK_NAMES = {"thumbs.db", "desktop.ini", ".ds_store", "picasa.ini", ".picasa.ini",
              "zbthumbnail.info", "ehthumbs.db", "ehthumbs_vista.db"}
JUNK_EXT = {".tmp", ".part", ".crdownload"}
JUNK_PREFIXES = ("._",)

THUMB_SIZE = 256
ANALYSIS_SIZE = 512

# Quick-hash sampling is only used to *rule out* duplicates cheaply.
# Anything acted on is always confirmed with a full-content hash.
SAMPLE_BYTES = 64 * 1024
SAMPLE_POINTS = 5

CPU_COUNT = os.cpu_count() or 4
WORKERS = max(2, min(12, CPU_COUNT))
# Photos up to this size are read into memory once and hashed + decoded from that copy.
IN_MEMORY_READ_LIMIT = 128 * 1024 * 1024


def kind_for_ext(ext: str) -> str:
    ext = ext.lower()
    if ext in IMAGE_EXT or ext in RAW_EXT:
        return "image"
    if ext in VIDEO_EXT:
        return "video"
    return "other"


def app_dir(library: Path) -> Path:
    return Path(library) / APP_DIR_NAME


def ensure_app_dir(library: Path) -> Path:
    d = app_dir(library)
    created = not d.exists()
    d.mkdir(parents=True, exist_ok=True)
    if created and os.name == "nt":
        try:
            import ctypes
            ctypes.windll.kernel32.SetFileAttributesW(str(d), 0x02)  # FILE_ATTRIBUTE_HIDDEN
        except Exception:
            pass
    return d


def recovery_dir(library: Path) -> Path:
    return app_dir(library) / RECOVERY_DIR_NAME


def default_export_dir() -> Path:
    return Path.home() / "Pictures" / "Memoria Exports"


def longpath(p) -> str:
    """Absolute path usable beyond Windows' 260-character limit (``\\\\?\\`` prefix when needed)."""
    s = os.fspath(p)
    if os.name != "nt" or len(s) < 240 or s.startswith("\\\\?\\"):
        return s
    s = os.path.abspath(s)
    return "\\\\?\\UNC\\" + s[2:] if s.startswith("\\\\") else "\\\\?\\" + s
