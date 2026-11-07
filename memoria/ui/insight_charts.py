"""Accessible bar lists and a bounded, offline GPS plot."""
import math

from PySide6.QtCore import QPointF, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QHeaderView, QStyledItemDelegate, QTreeWidget, QTreeWidgetItem, QWidget

from ..engine import geography
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
        self.setMinimumSize(320, 220)
        self.setMouseTracking(True)
        self.setAccessibleName("Offline photo locations; matching locations are also listed beside the map")

    def set_data(self, data):
        self.outlines = geography.countries()
        self.bounds, self.cells = data["bounds"], data["cells"]
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
        painter.setClipRect(self.plot_rect())
        painter.setPen(QPen(QColor(theme.INPUT_BORDER), 0.8))
        for country in self.outlines:
            painter.setBrush(QColor(theme.ACCENT_SOFT if country["code"] == "IND" else theme.CARD))
            path = QPainterPath()
            path.setFillRule(Qt.FillRule.OddEvenFill)
            for polygon in country["polygons"]:
                for ring in polygon:
                    for i, (lon, lat) in enumerate(ring):
                        point = self.project(lat, lon)
                        if i == 0:
                            path.moveTo(point)
                        else:
                            path.lineTo(point)
                    path.closeSubpath()
            painter.drawPath(path)
        self.hits = []
        for cell in self.cells:
            point = self.project(cell["lat"], cell["lon"])
            radius = min(16, 5 + math.log2(cell["count"] + 1))
            painter.setPen(QPen(QColor(theme.CARD), 1))
            painter.setBrush(QColor(theme.ACCENT))
            painter.drawEllipse(point, radius, radius)
            if cell["count"] > 1:
                painter.setPen(QColor("#FFFFFF"))
                painter.drawText(QRectF(point.x() - 20, point.y() - 12, 40, 24),
                                 Qt.AlignmentFlag.AlignCenter, str(cell["count"]))
            self.hits.append((point, radius, cell))
        painter.end()

    def _hit(self, point):
        return next((cell for center, radius, cell in reversed(self.hits)
                     if (point.x() - center.x()) ** 2 + (point.y() - center.y()) ** 2 <= (radius + 4) ** 2), None)

    def mouseMoveEvent(self, event):
        cell = self._hit(event.position())
        self.setToolTip(f"{cell['count']:,} files near {cell['lat']:.4f}, {cell['lon']:.4f}. Click to browse."
                        if cell else "Mouse wheel to zoom. Use India, World or Auto to reset the view.")

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            cell = self._hit(event.position())
            if cell:
                self.chosen.emit(cell)

    def wheelEvent(self, event):
        rect = self.plot_rect()
        if not rect.contains(event.position()):
            return
        south, north, west, east = self.bounds
        fx = (event.position().x() - rect.left()) / rect.width()
        fy = (rect.bottom() - event.position().y()) / rect.height()
        lon, lat = west + fx * (east - west), south + fy * (north - south)
        factor = 0.5 if event.angleDelta().y() > 0 else 2.0
        width = max(.01, min(360, (east - west) * factor))
        height = max(.01, min(180, (north - south) * factor))
        west = max(-180, min(180 - width, lon - fx * width))
        south = max(-90, min(90 - height, lat - fy * height))
        self.bounds = (south, south + height, west, west + width)
        self.zoomed.emit(self.bounds)
        event.accept()
