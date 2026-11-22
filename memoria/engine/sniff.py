"""Why a photo or video can't be opened: look at the first bytes instead of trusting the extension."""
from __future__ import annotations

import os
import re
from typing import Optional

from .config import longpath

# (signature check, real type, usual extension, kind)
_SIGNATURES = [
    (lambda h: h[:3] == b"\xff\xd8\xff", "JPEG photo", ".jpg", "image"),
    (lambda h: h[:8] == b"\x89PNG\r\n\x1a\n", "PNG image", ".png", "image"),
    (lambda h: h[:6] in (b"GIF87a", b"GIF89a"), "GIF image", ".gif", "image"),
    (lambda h: h[:4] == b"RIFF" and h[8:12] == b"WEBP", "WebP image", ".webp", "image"),
    (lambda h: h[:4] == b"RIFF" and h[8:12] == b"AVI ", "AVI video", ".avi", "video"),
    (lambda h: h[:2] == b"BM", "BMP image", ".bmp", "image"),
    (lambda h: h[:4] in (b"II*\x00", b"MM\x00*"), "TIFF image", ".tif", "image"),
    (lambda h: h[4:8] == b"ftyp" and h[8:12] in (b"heic", b"heix", b"mif1", b"msf1", b"hevc", b"heim", b"heis"),
     "HEIC photo", ".heic", "image"),
    (lambda h: h[4:8] == b"ftyp" and h[8:12] in (b"avif", b"avis"), "AVIF image", ".avif", "image"),
    (lambda h: h[4:8] == b"ftyp" and h[8:12] == b"qt  ", "QuickTime video", ".mov", "video"),
    (lambda h: h[4:8] == b"ftyp" and h[8:11] == b"3gp", "3GP video", ".3gp", "video"),
    (lambda h: h[4:8] == b"ftyp", "MP4 video", ".mp4", "video"),
    (lambda h: h[:4] == b"\x1aE\xdf\xa3", "MKV/WebM video", ".mkv", "video"),
    (lambda h: h[:4] == b"%PDF", "PDF document", ".pdf", "other"),
    (lambda h: h[:2] == b"PK", "ZIP archive", ".zip", "other"),
]
_SAME = {".jpg": {".jpg", ".jpeg", ".jpe"}, ".tif": {".tif", ".tiff"}, ".heic": {".heic", ".heif"},
         ".mp4": {".mp4", ".m4v", ".mov"}, ".mov": {".mov", ".mp4", ".m4v"}, ".mkv": {".mkv", ".webm"}}
_HTML = re.compile(rb"^\s*(<!doctype html|<html|<\?xml|<head|<body|\{\s*\")", re.I)


def identify(head: bytes, size: int, ext: str, tail: bytes = b"") -> Optional[dict]:
    """A diagnosis for an unreadable file, or None when nothing specific is wrong with its content.

    Returns ``{"code", "message", "fix_ext"}``; ``fix_ext`` is set when renaming the file would help.
    """
    ext = ext.lower()
    if size == 0:
        return {"code": "empty", "message": "The file is empty (0 bytes) — its data was never saved.", "fix_ext": None}
    sample = head[:65536]
    if sample and not sample.strip(b"\x00"):
        return {"code": "zeros", "message": "The file contains only zeros — its data was lost, typically in a failed "
                                            "copy, sync or disk recovery.", "fix_ext": None}
    if _HTML.match(sample):
        return {"code": "html", "message": "This is a web page or text saved under a photo name — the download "
                                           "probably failed.", "fix_ext": None}
    for check, real, usual, kind in _SIGNATURES:
        if check(sample):
            if ext in _SAME.get(usual, {usual}):
                if usual == ".jpg" and tail and b"\xff\xd9" not in tail[-1024:]:
                    return {"code": "truncated", "message": "The JPEG ends early — it was probably cut off during a "
                                                            "copy or download.", "fix_ext": None}
                return None
            return {"code": "wrong_ext", "message": f"This is actually a {real} saved with a {ext or 'missing'} "
                                                    f"extension. Renaming it to {usual} lets it open.",
                    "fix_ext": usual if kind in ("image", "video") else None}
    return None


def identify_file(path, ext: Optional[str] = None) -> Optional[dict]:
    """``identify`` for a file on disk (reads 64 KB from each end)."""
    try:
        p = longpath(path)
        size = os.path.getsize(p)
        with open(p, "rb") as f:
            head = f.read(65536)
            tail = b""
            if size > 65536:
                f.seek(max(0, size - 4096))
                tail = f.read(4096)
            else:
                tail = head
    except OSError:
        return None
    return identify(head, size, ext if ext is not None else os.path.splitext(str(path))[1], tail)


def tag(diagnosis: Optional[dict]) -> str:
    """Suffix stored with the error text so the catalogue keeps the diagnosis (``[content: code .ext]``)."""
    if not diagnosis:
        return ""
    return f" [content: {diagnosis['code']}{' ' + diagnosis['fix_ext'] if diagnosis.get('fix_ext') else ''}]"


_TAG = re.compile(r"\[content: (\w+)(?: (\.\w+))?\]")


def parse_tag(error: Optional[str]) -> Optional[tuple[str, Optional[str]]]:
    m = _TAG.search(error or "")
    return (m[1], m[2]) if m else None
