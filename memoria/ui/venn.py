"""A clickable 2- or 3-set Venn diagram of content shared between libraries."""
from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QSizePolicy, QWidget

from . import theme
from .widgets import fmt_size

LETTERS = "ABC"


def side_colors() -> list[str]:
    return [theme.ACCENT, theme.OK, theme.WARN]


class VennWidget(QWidget):
    region_clicked = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.count = 0
        self.labels: list[str] = []
        self.regions: dict[int, tuple[int, int]] = {}
        self.selected = None
        self._circles: list[tuple[QPointF, float]] = []
        self._anchors: dict[int, QPointF] = {}
        self.setMinimumSize(220, 190)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(220)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_data(self, labels: list[str], regions: dict[int, tuple[int, int]]) -> None:
        self.count, self.labels, self.regions = len(labels), labels, regions
        self.selected = None
        self._layout()
        self.update()

    def select(self, mask) -> None:
        self.selected = mask
        self.update()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._layout()

    def _layout(self) -> None:
        w, h = self.width(), self.height()
        if self.count == 2:
            r = min(w / 3.3, h / 2.3)
            cx, cy = w / 2, h / 2 + 6
            self._circles = [(QPointF(cx - r * 0.55, cy), r), (QPointF(cx + r * 0.55, cy), r)]
        elif self.count == 3:
            r = min((w - 16) / 3.1, (h - 28) / 2.95)
            d = r * 0.62
            cx = w / 2
            cy = (h - 2.93 * r) / 2 + r + 0.5 * d
            self._circles = [(QPointF(cx + d * math.cos(angle), cy + d * math.sin(angle)), r)
                             for angle in (math.radians(210), math.radians(330), math.radians(90))]
        else:
            self._circles = []
        self._anchors = {}
        if not self._circles:
            return
        sums: dict[int, list[float]] = {}
        step = 4
        for x in range(0, w, step):
            for y in range(0, h, step):
                mask = self.mask_at(QPointF(x, y))
                if mask:
                    acc = sums.setdefault(mask, [0.0, 0.0, 0])
                    acc[0] += x
                    acc[1] += y
                    acc[2] += 1
        self._anchors = {mask: QPointF(acc[0] / acc[2], acc[1] / acc[2]) for mask, acc in sums.items()}

    def mask_at(self, point: QPointF) -> int:
        mask = 0
        for side, (centre, radius) in enumerate(self._circles):
            if (point.x() - centre.x()) ** 2 + (point.y() - centre.y()) ** 2 <= radius ** 2:
                mask |= 1 << side
        return mask

    def _region_path(self, mask: int) -> QPainterPath:
        path = None
        for side, (centre, radius) in enumerate(self._circles):
            circle = QPainterPath()
            circle.addEllipse(centre, radius, radius)
            if mask & (1 << side):
                path = circle if path is None else path.intersected(circle)
        for side, (centre, radius) in enumerate(self._circles):
            if not mask & (1 << side) and path is not None:
                circle = QPainterPath()
                circle.addEllipse(centre, radius, radius)
                path = path.subtracted(circle)
        return path or QPainterPath()

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        colors = side_colors()
        for side, (centre, radius) in enumerate(self._circles):
            fill = QColor(colors[side])
            fill.setAlpha(46)
            p.setBrush(fill)
            p.setPen(QPen(QColor(colors[side]), 2))
            p.drawEllipse(centre, radius, radius)
        if self.selected:
            highlight = QColor(theme.ACCENT)
            highlight.setAlpha(120)
            p.setPen(QPen(QColor(theme.TEXT), 2))
            p.setBrush(highlight)
            p.drawPath(self._region_path(self.selected))
        font = QFont(self.font())
        font.setBold(True)
        font.setPointSizeF(11)
        p.setFont(font)
        middle = QPointF(self.width() / 2, self.height() / 2)
        for side, (centre, radius) in enumerate(self._circles):
            dx, dy = centre.x() - middle.x(), centre.y() - middle.y()
            if self.count == 2:
                dx, dy = (-1 if side == 0 else 1), -1.0
            length = math.hypot(dx, dy) or 1
            x = min(max(centre.x() + dx / length * (radius + 8), 10), self.width() - 10)
            y = min(max(centre.y() + dy / length * (radius + 8), 10), self.height() - 10)
            p.setPen(QColor(colors[side]))
            p.drawText(QRectF(x - 10, y - 10, 20, 20), Qt.AlignmentFlag.AlignCenter, LETTERS[side])
        font.setBold(False)
        font.setPointSizeF(9.5)
        p.setFont(font)
        for mask, anchor in self._anchors.items():
            contents, size = self.regions.get(mask, (0, 0))
            p.setPen(QColor(theme.TEXT if contents else theme.MUTED))
            p.drawText(QRectF(anchor.x() - 40, anchor.y() - 16, 80, 16), Qt.AlignmentFlag.AlignCenter, f"{contents:,}")
            if contents:
                p.setPen(QColor(theme.MUTED))
                p.drawText(QRectF(anchor.x() - 40, anchor.y(), 80, 14), Qt.AlignmentFlag.AlignCenter, fmt_size(size))
        p.end()

    def mouseMoveEvent(self, event) -> None:
        mask = self.mask_at(event.position())
        if mask:
            contents, size = self.regions.get(mask, (0, 0))
            names = [LETTERS[side] for side in range(self.count) if mask & (1 << side)]
            missing = [LETTERS[side] for side in range(self.count) if not mask & (1 << side)]
            text = ("In " + " and ".join(names) + (" only" if len(names) == 1 else "")
                    + (f", not in {' or '.join(missing)}" if missing and len(names) > 1 else ""))
            self.setToolTip(f"{text}: {contents:,} distinct items ({fmt_size(size)}). Click to show them.")
        else:
            self.setToolTip("Click a region to show exactly those files.")

    def mousePressEvent(self, event) -> None:
        mask = self.mask_at(event.position())
        if mask:
            self.select(mask)
            self.region_clicked.emit(mask)
