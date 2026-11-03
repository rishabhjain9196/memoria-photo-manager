"""Interactive crop/preview canvas used by the Editor."""
from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QSizePolicy, QWidget

from . import theme

Crop = tuple[float, float, float, float]
HANDLE = 9
MIN = 0.03


class CropCanvas(QWidget):
    """Shows an image fitted to the widget. In crop mode, draws a draggable crop rectangle.

    The crop is normalized (left, top, right, bottom) in 0..1 of the displayed image. ``aspect`` is
    width/height in image pixels (None = free).
    """
    crop_changed = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(320, 240)
        self.setMouseTracking(True)
        self._pm = QPixmap()
        self.crop: Optional[Crop] = None
        self.crop_mode = False
        self.aspect: Optional[float] = None
        self.message = ""
        self._drag: Optional[str] = None
        self._start: Optional[QPointF] = None
        self._start_crop: Optional[Crop] = None

    # ------------------------------------------------------------------ state
    def set_pixmap(self, pm: Optional[QPixmap]) -> None:
        self._pm = pm if pm is not None else QPixmap()
        self.message = ""
        self.update()

    def set_message(self, text: str) -> None:
        self._pm = QPixmap()
        self.message = text
        self.update()

    def set_crop_mode(self, on: bool, crop: Optional[Crop], aspect: Optional[float]) -> None:
        self.crop_mode, self.crop, self.aspect = on, crop, aspect
        if on and self.crop is None:
            self.crop = (0.0, 0.0, 1.0, 1.0)
        self.setCursor(Qt.CursorShape.CrossCursor if on else Qt.CursorShape.ArrowCursor)
        self.update()

    # ------------------------------------------------------------------ geometry
    def image_rect(self) -> QRectF:
        if self._pm.isNull():
            return QRectF()
        margin = 12
        w, h = self.width() - 2 * margin, self.height() - 2 * margin
        pw, ph = self._pm.width() / self._pm.devicePixelRatio(), self._pm.height() / self._pm.devicePixelRatio()
        s = min(w / pw, h / ph)
        dw, dh = pw * s, ph * s
        return QRectF((self.width() - dw) / 2, (self.height() - dh) / 2, dw, dh)

    def _crop_rect(self) -> QRectF:
        r = self.image_rect()
        l, t, rr, b = self.crop or (0, 0, 1, 1)
        return QRectF(r.left() + l * r.width(), r.top() + t * r.height(), (rr - l) * r.width(), (b - t) * r.height())

    def _to_norm(self, p: QPointF) -> tuple[float, float]:
        r = self.image_rect()
        return (min(1.0, max(0.0, (p.x() - r.left()) / r.width())),
                min(1.0, max(0.0, (p.y() - r.top()) / r.height())))

    def _pixel_aspect(self) -> float:
        """Normalized-units correction: image width/height in pixels."""
        return self._pm.width() / max(1, self._pm.height())

    def _hit(self, pos: QPointF) -> Optional[str]:
        if not self.crop_mode or self.crop is None:
            return None
        c = self._crop_rect()
        pts = {"tl": c.topLeft(), "tr": c.topRight(), "bl": c.bottomLeft(), "br": c.bottomRight(),
               "t": QPointF(c.center().x(), c.top()), "b": QPointF(c.center().x(), c.bottom()),
               "l": QPointF(c.left(), c.center().y()), "r": QPointF(c.right(), c.center().y())}
        for name, p in pts.items():
            if abs(p.x() - pos.x()) <= HANDLE + 3 and abs(p.y() - pos.y()) <= HANDLE + 3:
                return name
        if c.contains(pos):
            return "move"
        return None

    # ------------------------------------------------------------------ mouse
    def mousePressEvent(self, e) -> None:
        if not self.crop_mode or self._pm.isNull():
            return
        pos = e.position()
        self._drag = self._hit(pos) or "new"
        self._start = pos
        self._start_crop = self.crop
        if self._drag == "new":
            x, y = self._to_norm(pos)
            self.crop = (x, y, x, y)
            self._drag = "br"
            self._start_crop = self.crop

    def mouseMoveEvent(self, e) -> None:
        pos = e.position()
        if self._drag is None:
            hit = self._hit(pos)
            cursors = {"tl": Qt.CursorShape.SizeFDiagCursor, "br": Qt.CursorShape.SizeFDiagCursor,
                       "tr": Qt.CursorShape.SizeBDiagCursor, "bl": Qt.CursorShape.SizeBDiagCursor,
                       "t": Qt.CursorShape.SizeVerCursor, "b": Qt.CursorShape.SizeVerCursor,
                       "l": Qt.CursorShape.SizeHorCursor, "r": Qt.CursorShape.SizeHorCursor,
                       "move": Qt.CursorShape.SizeAllCursor}
            if self.crop_mode:
                self.setCursor(cursors.get(hit, Qt.CursorShape.CrossCursor))
            return
        x, y = self._to_norm(pos)
        l, t, r, b = self._start_crop
        if self._drag == "move":
            sx, sy = self._to_norm(self._start)
            dx, dy = x - sx, y - sy
            w, h = r - l, b - t
            nl = min(max(0.0, l + dx), 1.0 - w)
            nt = min(max(0.0, t + dy), 1.0 - h)
            self.crop = (nl, nt, nl + w, nt + h)
        else:
            if "l" in self._drag:
                l = min(x, r - MIN)
            if "r" in self._drag:
                r = max(x, l + MIN)
            if "t" in self._drag:
                t = min(y, b - MIN)
            if "b" in self._drag:
                b = max(y, t + MIN)
            self.crop = self._enforce_aspect((l, t, r, b), self._drag)
        self.update()
        self.crop_changed.emit(self.crop)

    def mouseReleaseEvent(self, e) -> None:
        if self._drag is not None:
            self._drag = None
            l, t, r, b = self.crop
            if r - l < MIN or b - t < MIN:
                self.crop = self._start_crop if self._start_crop and self._start_crop[2] - self._start_crop[0] >= MIN \
                    else (0.0, 0.0, 1.0, 1.0)
            self.update()
            self.crop_changed.emit(self.crop)

    def _enforce_aspect(self, c: Crop, handle: str) -> Crop:
        if not self.aspect:
            return c
        l, t, r, b = c
        pa = self._pixel_aspect()
        want_h = (r - l) * pa / self.aspect          # normalized height that gives the aspect
        if handle in ("t", "b"):                    # vertical edge drag drives width instead
            want_w = (b - t) * self.aspect / pa
            cx = (l + r) / 2
            l, r = cx - want_w / 2, cx + want_w / 2
            if l < 0 or r > 1:
                scale = min((cx - 0) / (want_w / 2) if want_w else 1, (1 - cx) / (want_w / 2) if want_w else 1)
                want_w *= scale
                l, r = cx - want_w / 2, cx + want_w / 2
                h = want_w * pa / self.aspect
                t, b = (b - h, b) if handle == "t" else (t, t + h)
            return (max(0.0, l), max(0.0, t), min(1.0, r), min(1.0, b))
        if "t" in handle:
            t = b - want_h
        else:
            b = t + want_h
        if t < 0 or b > 1:                          # too tall: shrink width to fit
            avail = b if "t" in handle else 1 - t
            want_h = min(want_h, avail)
            want_w = want_h * self.aspect / pa
            if "l" in handle:
                l = r - want_w
            else:
                r = l + want_w
            t, b = (b - want_h, b) if "t" in handle else (t, t + want_h)
        return (max(0.0, l), max(0.0, t), min(1.0, r), min(1.0, b))

    # ------------------------------------------------------------------ paint
    def paintEvent(self, e) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor(theme.PREVIEW_BG))
        if self._pm.isNull():
            p.setPen(QColor(theme.MUTED))
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.message)
            return
        r = self.image_rect()
        p.drawPixmap(r, self._pm, QRectF(self._pm.rect()))
        if not (self.crop_mode and self.crop):
            return
        c = self._crop_rect()
        shade = QColor(0, 0, 0, 130)
        for rect in (QRectF(r.left(), r.top(), r.width(), c.top() - r.top()),
                     QRectF(r.left(), c.bottom(), r.width(), r.bottom() - c.bottom()),
                     QRectF(r.left(), c.top(), c.left() - r.left(), c.height()),
                     QRectF(c.right(), c.top(), r.right() - c.right(), c.height())):
            p.fillRect(rect, shade)
        p.setPen(QPen(QColor(255, 255, 255, 110), 1))
        for i in (1, 2):
            x = c.left() + c.width() * i / 3
            y = c.top() + c.height() * i / 3
            p.drawLine(QPointF(x, c.top()), QPointF(x, c.bottom()))
            p.drawLine(QPointF(c.left(), y), QPointF(c.right(), y))
        p.setPen(QPen(QColor("white"), 2))
        p.drawRect(c)
        p.setBrush(QColor("white"))
        p.setPen(QPen(QColor(theme.ACCENT), 1))
        for pt in (c.topLeft(), c.topRight(), c.bottomLeft(), c.bottomRight(),
                   QPointF(c.center().x(), c.top()), QPointF(c.center().x(), c.bottom()),
                   QPointF(c.left(), c.center().y()), QPointF(c.right(), c.center().y())):
            p.drawRect(QRectF(pt.x() - HANDLE / 2, pt.y() - HANDLE / 2, HANDLE, HANDLE))


def rotate_crop(crop: Optional[Crop], quarter_turns_cw: int) -> Optional[Crop]:
    """Map a normalized crop through clockwise quarter turns of the image."""
    if crop is None:
        return None
    l, t, r, b = crop
    for _ in range(quarter_turns_cw % 4):
        l, t, r, b = 1 - b, l, 1 - t, r
    return (l, t, r, b)


def flip_crop(crop: Optional[Crop], horizontal: bool) -> Optional[Crop]:
    if crop is None:
        return None
    l, t, r, b = crop
    return (1 - r, t, 1 - l, b) if horizontal else (l, 1 - b, r, 1 - t)
