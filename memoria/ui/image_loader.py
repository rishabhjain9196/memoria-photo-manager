"""Bounded read-only image requests. QPixmap creation remains on the GUI thread."""
from __future__ import annotations

from PySide6.QtGui import QImage


def read_image(lib, row: dict, edge: int) -> tuple[QImage, str]:
    """Return a display image and any original-read error (even with a cached fallback)."""
    image, error = QImage(), ""
    try:
        if lib._lock_key is None:
            return image, "This library was closed before its preview could be read."
        if row.get("kind") == "image" and not row.get("error"):
            try:
                from ..engine.media import load_for_display
                path = lib.abspath(row["rel_path"])
                lib.check_path(path)
                decoded = load_for_display(path, min(edge, 2400))
                try:
                    image = QImage(decoded.tobytes(), decoded.width, decoded.height,
                                   decoded.width * 3, QImage.Format.Format_RGB888).copy()
                finally:
                    decoded.close()
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
        if image.isNull() and row.get("id") is not None:
            data = lib.thumbnail(row["id"])
            if data:
                image = QImage.fromData(data)
                if image.isNull() and not error:
                    error = "The cached preview could not be decoded."
        return image, error
    finally:
        lib.close_thread()


def checked_path(lib, key):
    """Resolve and verify a source before handing it to an external application."""
    try:
        if lib._lock_key is None:
            raise RuntimeError("This library is closed.")
        path = lib.abspath(key)
        lib.check_path(path)
        return str(path)
    finally:
        lib.close_thread()
