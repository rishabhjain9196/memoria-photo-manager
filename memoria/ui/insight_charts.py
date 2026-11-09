"""Accessible bar lists and a bounded, offline GPS plot."""
import math

from PySide6.QtCore import QPointF, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QTransform
from PySide6.QtWidgets import QApplication, QHeaderView, QStyledItemDelegate, QTreeWidget, QTreeWidgetItem, QWidget

from ..engine import geography, places
from . import theme
from .widgets import fmt_size


class _Bars(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if index.column() == 1:
            fraction = index.data(Qt.ItemDataRole.UserRole) or 0
            painter.save()
            rect = QRectF(option.rect).adjusted(2, 5, -2, -5)
            rect.setWidth(rect.width() * fraction)
            painter.fillRect(rect, QColor(theme.ACCENT_SOFT))
            painter.restore()
        super().paint(painter, option, index)


class BarChart(QTreeWidget):
    chosen = Signal(dict)

    def __init__(self, title: str, metric: str):
        super().__init__()
        self.value_key = metric
        self.setHeaderLabels([title, "Size" if metric == "bytes" else "Count", "Files" if metric == "bytes" else "Size"])
        self.setRootIsDecorated(False)
        self.setUniformRowHeights(True)
        self.setItemDelegate(_Bars(self))
        self.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.header().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.header().setStretchLastSection(False)
        self.itemClicked.connect(lambda item, _: self.chosen.emit(item.data(0, Qt.ItemDataRole.UserRole)))
        self.setAccessibleName(title)

    def set_rows(self, rows):
        self.clear()
        maximum = max((row[self.value_key] for row in rows), default=0) or 1
        for row in rows:
            name = row.get("label") or row["key"] or "(no extension)"
            size, count = fmt_size(row["bytes"]), f"{row['count']:,}"
            item = QTreeWidgetItem([name, size if self.value_key == "bytes" else count,
                                    count if self.value_key == "bytes" else size])
            item.setData(0, Qt.ItemDataRole.UserRole, row)
            item.setData(1, Qt.ItemDataRole.UserRole, row[self.value_key] / maximum)
            item.setToolTip(0, f"{name}: {count} files, {size}. Select to explore.")
            item.setSizeHint(0, QSize(0, 34))
            self.addTopLevelItem(item)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space) and self.currentItem():
            self.chosen.emit(self.currentItem().data(0, Qt.ItemDataRole.UserRole))
        else:
            super().keyPressEvent(event)


class GeoChart(QWidget):
    chosen = Signal(dict)
    zoomed = Signal(tuple)

    def __init__(self):
        super().__init__()
        self.bounds = geography.INDIA
        self.cells = []
        self.hits = []
        self.outlines = []
        self.labels = []
        self.label_hits = []
        self._ready = False
        self._press = None
        self._dragged = False
        self.setMinimumSize(320, 220)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.setAccessibleName("Offline photo locations; matching locations are also listed beside the map")

    def set_data(self, data):
        if not self._ready:
            for country in geography.countries():
                path = QPainterPath()
                path.setFillRule(Qt.FillRule.OddEvenFill)
                for polygon in country["polygons"]:
                    for ring in polygon:
                        for i, (lon, lat) in enumerate(ring):
                            if i == 0:
                                path.moveTo(lon, lat)
                            else:
                                path.lineTo(lon, lat)
                        path.closeSubpath()
                self.outlines.append((country["code"], path, path.boundingRect()))
        self._ready = True
        self.bounds, self.cells = data["bounds"], data["cells"]
        self.labels = data["labels"]
        self.hits = []
        self.update()

    def clear_points(self):
        self.cells, self.hits = [], []
        self.update()

    def set_bounds(self, bounds):
        if bounds == self.bounds:
            return
        self.bounds = bounds
        if self._ready:
            self.labels = places.map_labels(bounds)
        self.hits, self.label_hits = [], []
        self.update()

    def plot_rect(self):
        south, north, west, east = self.bounds
        available = QRectF(self.rect()).adjusted(10, 10, -10, -10)
        scale = min(available.width() / (east - west), available.height() / (north - south))
        width, height = (east - west) * scale, (north - south) * scale
        return QRectF(available.center().x() - width / 2, available.center().y() - height / 2, width, height)

    def project(self, lat, lon):
        south, north, west, east = self.bounds
        rect = self.plot_rect()
        return QPointF(rect.left() + (lon - west) / (east - west) * rect.width(),
                       rect.bottom() - (lat - south) / (north - south) * rect.height())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(theme.BG))
        rect = self.plot_rect()
        painter.setClipRect(rect)
        south, north, west, east = self.bounds
        sx, sy = rect.width() / (east - west), rect.height() / (north - south)
        transform = QTransform(sx, 0, 0, -sy, rect.left() - west * sx, rect.bottom() + south * sy)
        painter.save()
        painter.setWorldTransform(transform)
        pen = QPen(QColor(theme.INPUT_BORDER), 0.8)
        pen.setCosmetic(True)
        painter.setPen(pen)
        viewport = QRectF(west, south, east - west, north - south)
        for code, path, extent in self.outlines:
            if extent.intersects(viewport):
                painter.setBrush(QColor(theme.ACCENT_SOFT if code == "IND" else theme.CARD))
                painter.drawPath(path)
        painter.restore()
        self.hits = []
        occupied = []
        for cell in self.cells:
            point = transform.map(QPointF(cell["lon"], cell["lat"]))
            if not rect.contains(point):
                continue
            radius = min(16, 5 + math.log2(cell["count"] + 1))
            painter.setPen(QPen(QColor(theme.CARD), 1))
            painter.setBrush(QColor(theme.ACCENT))
            painter.drawEllipse(point, radius, radius)
            if cell["count"] > 1:
                painter.setPen(QColor("#FFFFFF"))
                painter.drawText(QRectF(point.x() - 20, point.y() - 12, 40, 24),
                                 Qt.AlignmentFlag.AlignCenter, str(cell["count"]))
            self.hits.append((point, radius, cell))
            occupied.append(QRectF(point.x() - radius - 3, point.y() - radius - 3,
                                   2 * radius + 6, 2 * radius + 6))
        self.label_hits = []
        metrics = painter.fontMetrics()
        for label in self.labels:
            point = transform.map(QPointF(label["lon"], label["lat"]))
            text = metrics.elidedText(label["text"], Qt.TextElideMode.ElideRight, 250)
            width, height = metrics.horizontalAdvance(text) + 8, metrics.height() + 4
            options = (QRectF(point.x() + 21, point.y() - height / 2, width, height),
                       QRectF(point.x() - width - 21, point.y() - height / 2, width, height),
                       QRectF(point.x() - width / 2, point.y() + 21, width, height))
            target = next((r for r in options if rect.contains(r) and
                           not any(r.intersects(other) for other in occupied)), None)
            if target is None:
                continue
            painter.setPen(Qt.PenStyle.NoPen)
            background = QColor(theme.CARD)
            background.setAlpha(220)
            painter.setBrush(background)
            painter.drawRoundedRect(target, 3, 3)
            painter.setPen(QColor(theme.TEXT))
            painter.drawText(target, Qt.AlignmentFlag.AlignCenter, text)
            occupied.append(target.adjusted(-3, -3, 3, 3))
            self.label_hits.append((target, label["text"]))
            if len(self.label_hits) >= 60:
                break
        painter.end()

    def _hit(self, point):
        return next((cell for center, radius, cell in reversed(self.hits)
                     if (point.x() - center.x()) ** 2 + (point.y() - center.y()) ** 2 <= (radius + 4) ** 2), None)

    def mouseMoveEvent(self, event):
        if self._press is not None and event.buttons() & Qt.MouseButton.LeftButton:
            delta = event.position() - self._press
            if self._dragged or abs(delta.x()) + abs(delta.y()) >= QApplication.startDragDistance():
                self._dragged = True
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                south, north, west, east = self._press_bounds
                self._view(south + delta.y() / self._press_rect.height() * (north - south),
                           west - delta.x() / self._press_rect.width() * (east - west),
                           east - west, north - south)
            event.accept()
            return
        cell = self._hit(event.position())
        name = f" Near {cell['place']}." if cell and cell.get("place") else ""
        label = next((text for rect, text in self.label_hits if rect.contains(event.position())), "")
        self.setToolTip(f"{cell['count']:,} files in this group.{name} "
                        f"Centre: {cell['lat']:.4f}, {cell['lon']:.4f}. Click to browse."
                        if cell else label or "Scroll or use +/− to zoom. Drag to pan. Arrow keys move the map.")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setFocus()
            self._press = event.position()
            self._press_bounds, self._press_rect = self.bounds, self.plot_rect()
            self._dragged = False
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            cell = None if self._dragged else self._hit(event.position())
            self._press = None
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            if cell:
                self.chosen.emit(cell)
            event.accept()

    def _view(self, south, west, width, height):
        west = max(-180, min(180 - width, west))
        south = max(-90, min(90 - height, south))
        bounds = (south, min(90, south + height), west, min(180, west + width))
        if bounds != self.bounds:
            self.set_bounds(bounds)
            self.zoomed.emit(bounds)

    def zoom(self, steps, anchor=None):
        rect = self.plot_rect()
        anchor = anchor if anchor is not None else rect.center()
        south, north, west, east = self.bounds
        fx = max(0, min(1, (anchor.x() - rect.left()) / rect.width()))
        fy = max(0, min(1, (rect.bottom() - anchor.y()) / rect.height()))
        lon, lat = west + fx * (east - west), south + fy * (north - south)
        factor = 2 ** -max(-4, min(4, steps))
        width = max(.01, min(360, (east - west) * factor))
        height = max(.01, min(180, (north - south) * factor))
        self._view(lat - fy * height, lon - fx * width, width, height)

    def wheelEvent(self, event):
        delta = event.pixelDelta().y() or event.angleDelta().y()
        if not delta:
            event.ignore()
            return
        self.zoom(delta / 120, event.position())
        event.accept()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Plus, Qt.Key.Key_Equal, Qt.Key.Key_Minus):
            self.zoom(-1 if event.key() == Qt.Key.Key_Minus else 1)
        elif event.key() in (Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down):
            south, north, west, east = self.bounds
            dx = -0.2 if event.key() == Qt.Key.Key_Left else 0.2 if event.key() == Qt.Key.Key_Right else 0
            dy = 0.2 if event.key() == Qt.Key.Key_Up else -0.2 if event.key() == Qt.Key.Key_Down else 0
            self._view(south + dy * (north - south), west + dx * (east - west), east - west, north - south)
        else:
            super().keyPressEvent(event)
