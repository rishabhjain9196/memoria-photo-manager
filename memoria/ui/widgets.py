"""Reusable widgets: page scaffold, tiles, banners, photo grid, preview, dialogs, toast."""
from __future__ import annotations

import os
from html import escape
import subprocess
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from PySide6.QtCore import (QAbstractListModel, QModelIndex, QObject, QPoint, QRect, QRectF, QSize, Qt,
                            QTimer, Signal)
from PySide6.QtGui import (QBrush, QColor, QDesktopServices, QFont, QFontDatabase, QImage, QPainter,
                           QPainterPath, QPen, QPixmap)
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import (QAbstractItemView, QCheckBox, QDialog, QFrame, QGraphicsDropShadowEffect, QGridLayout,
                               QHBoxLayout, QLabel, QListView, QPushButton, QScrollArea, QSizePolicy, QStyle,
                               QStyledItemDelegate, QVBoxLayout, QWidget)

from . import motion
from .motion import Dialog
from . import theme
from .tasks import LatestCall
from .image_loader import checked_path, read_image
from ..engine.db import Library


# ------------------------------------------------------------------------------ formatting
def fmt_size(n: float) -> str:
    n = float(n or 0)
    for unit in ("bytes", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{int(n)} bytes" if unit == "bytes" else f"{n:,.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def fmt_n(n: int, word: str, plural: Optional[str] = None) -> str:
    n = int(n or 0)
    return f"{n:,} {word if n == 1 else (plural or word + 's')}"


def fmt_date(s: Optional[str], with_time: bool = False) -> str:
    if not s:
        return "—"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return s
    return dt.strftime("%d %b %Y, %H:%M") if with_time else dt.strftime("%d %b %Y")


def fmt_duration(sec: Optional[float]) -> str:
    if not sec or sec <= 0:
        return ""
    if sec < 1:
        return f"{sec:g} s"
    sec = int(round(sec))
    return f"{sec // 3600}:{sec % 3600 // 60:02d}:{sec % 60:02d}" if sec >= 3600 else f"{sec // 60}:{sec % 60:02d}"


def friendly_error(err: Optional[str]) -> str:
    """Plain-language version of a technical read/decode error."""
    if not err:
        return ""
    e = err.lower()
    if "truncated" in e or "premature end" in e:
        return "The file is incomplete — it was probably cut off during a copy or download."
    if "cannot identify image" in e or "unidentifiedimageerror" in e:
        return ("Memoria couldn't decode this image. Its format or codec may be unsupported, "
                "or the file may be incomplete or damaged.")
    if "no video stream" in e:
        return "No playable video was found in this file."
    if "permission" in e or "access is denied" in e:
        return "Windows didn't allow Memoria to read this file."
    if "could not be read" in e:
        return "The file could not be read from the drive."
    return "Memoria couldn't read this file. Check its format/codec and access before assuming it is damaged."


# ------------------------------------------------------------------------------ icons
_ICON_FAMILY: Optional[str] = None


def icon_family() -> str:
    global _ICON_FAMILY
    if _ICON_FAMILY is None:
        fams = set(QFontDatabase.families())
        _ICON_FAMILY = theme.ICON_FONT if theme.ICON_FONT in fams else (
            theme.ICON_FONT_FALLBACK if theme.ICON_FONT_FALLBACK in fams else "")
    return _ICON_FAMILY


def glyph_label(glyph: str, size: int = 16, color: str = theme.TEXT) -> QLabel:
    lab = QLabel(glyph if icon_family() else "")
    f = QFont(icon_family() or "Segoe UI")
    f.setPixelSize(size)
    lab.setFont(f)
    lab.setStyleSheet(f"color: {color}; background: transparent;")
    lab.setFixedWidth(size + 8)
    return lab


def icon_chip(glyph: str, color: str, size: int = 16, box: int = 30) -> QLabel:
    """A rounded, softly tinted square holding a coloured icon — the visual cue for a section or status."""
    lab = glyph_label(glyph, size, color)
    lab.setObjectName("iconChip")
    lab.setFixedSize(box, box)
    lab.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lab.setStyleSheet(f"color: {color}; background: {theme.soft(color)}; border-radius: {box // 3}px;")
    if not icon_family():
        lab.hide()
    return lab


# ------------------------------------------------------------------------------ OS helpers
def show_in_explorer(path: str | Path) -> None:
    path = str(path)
    if os.name == "nt":
        subprocess.Popen(["explorer", "/select,", os.path.normpath(path)])
    else:
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(path).parent)))


def open_path(path: str | Path) -> None:
    QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))


# ------------------------------------------------------------------------------ layout helpers
def label(text: str = "", obj: str = "", wrap: bool = False) -> QLabel:
    lab = QLabel(text)
    if obj:
        lab.setObjectName(obj)
    lab.setWordWrap(wrap)
    if wrap:
        lab.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
    return lab


def button(text: str, kind: str = "", on_click: Optional[Callable] = None, tip: str = "") -> QPushButton:
    b = QPushButton(text)
    if kind:
        b.setObjectName(kind)
    if on_click:
        b.clicked.connect(on_click)
    if tip:
        b.setToolTip(tip)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    return b


def hbox(*items, spacing: int = 8, margins=(0, 0, 0, 0)) -> QHBoxLayout:
    lay = QHBoxLayout()
    lay.setSpacing(spacing)
    lay.setContentsMargins(*margins)
    for it in items:
        if it is None:
            lay.addStretch(1)
        elif isinstance(it, int):
            lay.addSpacing(it)
        elif isinstance(it, QWidget):
            lay.addWidget(it)
        else:
            lay.addLayout(it)
    return lay


def vbox(*items, spacing: int = 8, margins=(0, 0, 0, 0)) -> QVBoxLayout:
    lay = QVBoxLayout()
    lay.setSpacing(spacing)
    lay.setContentsMargins(*margins)
    for it in items:
        if it is None:
            lay.addStretch(1)
        elif isinstance(it, int):
            lay.addSpacing(it)
        elif isinstance(it, QWidget):
            lay.addWidget(it)
        else:
            lay.addLayout(it)
    return lay


class Card(QFrame):
    def __init__(self, layout=None, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        if layout is not None:
            layout.setContentsMargins(16, 14, 16, 14)
            self.setLayout(layout)


class Banner(QLabel):
    """Coloured explanatory strip: kind ∈ trust | warn | info | danger."""

    def __init__(self, text: str, kind: str = "trust"):
        super().__init__(text)
        self.setObjectName({"trust": "trust", "warn": "warnBox", "info": "infoBox", "danger": "dangerBox"}[kind])
        self.setWordWrap(True)
        self.setTextFormat(Qt.TextFormat.RichText)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)


def trust_note(short: str, full: str = "") -> QLabel:
    """A one-line green reassurance shown beside an action button; the full explanation is the tooltip."""
    lab = QLabel(f"✓  {short}")
    lab.setObjectName("trustNote")
    lab.setToolTip(full or short)
    return lab


class HelpToggle(QWidget):
    """A small "How it works" link that reveals an explanation only when the user asks for it."""

    def __init__(self, text: str, title: str = "How it works", kind: str = "info"):
        super().__init__()
        self.title = title
        self.link = button("", "link", self.toggle)
        self.link.setToolTip("Show or hide the explanation")
        self.banner = Banner(text, kind)
        self.banner.hide()
        lay = vbox(hbox(self.link, None), self.banner, spacing=4)
        self.setLayout(lay)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self._label()

    def _label(self) -> None:
        self.link.setText(f"ⓘ  {self.title}  {'▾' if self.expanded else '▸'}")

    @property
    def expanded(self) -> bool:
        return not self.banner.isHidden()

    def toggle(self) -> None:
        self.banner.setVisible(not self.expanded)
        self._label()

    def setText(self, text: str) -> None:
        self.banner.setText(text)

    def text(self) -> str:
        return self.banner.text()


class Tile(QFrame):
    def __init__(self, value: str = "—", text: str = "", sub: str = "", glyph: str = "", color: str = ""):
        super().__init__()
        self.setObjectName("tile")
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self.value = label(value, "tileValue")
        self.text = label(text, "tileLabel")
        self.sub = label(sub or " ", "small")
        lay = vbox(self.text, self.value, self.sub, spacing=2)
        lay.setContentsMargins(14, 10, 14, 10)
        if glyph:
            chip = icon_chip(glyph, color or theme.ACCENT, 15, 28)
            outer = hbox(lay, None, chip, spacing=8)
            outer.setAlignment(chip, Qt.AlignmentFlag.AlignTop)
            lay.setContentsMargins(0, 0, 0, 0)
            outer.setContentsMargins(14, 10, 12, 10)
            self.setLayout(outer)
        else:
            self.setLayout(lay)
        self.setMinimumWidth(130)

    def set(self, value: str, sub: str = "", color: Optional[str] = None) -> None:
        """``color`` marks the tile's status: the number and a stripe on the left edge use it."""
        self.value.setText(value)
        self.value.setStyleSheet(f"color: {color};" if color else "")
        self.setStyleSheet(f"#tile {{ border-left: 4px solid {color}; }}" if color else "")
        self.sub.setText(sub or " ")


class EmptyState(QWidget):
    def __init__(self, glyph: str, title: str, text: str, action: Optional[QPushButton] = None):
        super().__init__()
        g = glyph_label(glyph, 40, theme.MUTED)
        g.setFixedWidth(60)
        g.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t = label(title, "h2")
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text = label(text, "muted", wrap=True)
        self.text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text.setMaximumWidth(520)
        lay = vbox(None, hbox(None, g, None), t, hbox(None, self.text, None), spacing=10)
        if action:
            lay.addLayout(hbox(None, action, None))
        lay.addStretch(1)
        self.setLayout(lay)


def scroll(widget: QWidget) -> QScrollArea:
    sa = QScrollArea()
    sa.setWidgetResizable(True)
    sa.setWidget(widget)
    sa.setFrameShape(QFrame.Shape.NoFrame)
    return sa


# ------------------------------------------------------------------------------ app context
class AppContext(QObject):
    """Shared state handed to every page."""
    library_opened = Signal()
    library_modified = Signal()       # files moved/copied/indexed — pages should refresh
    toast_requested = Signal(str, str)  # message, batch_id to offer Undo ("" for none)
    navigate = Signal(str)
    badges_changed = Signal(dict)     # page key → count shown in the sidebar
    checkup_requested = Signal()
    people_changed = Signal()         # faces found / named — Photos search and Albums suggestions follow
    albums_changed = Signal()         # albums created, edited or deleted
    browse_requested = Signal(object)
    album_requested = Signal(int)
    indexing_changed = Signal(bool)
    index_progress = Signal()
    notification_requested = Signal(str, int)

    def __init__(self, runner):
        super().__init__()
        self.runner = runner
        from ..engine.diagnostics import Metrics
        self.diagnostics = Metrics()
        self.library: Optional[Library] = None
        self.maintenance = False
        self.indexing = False
        self.index_update = False
        self.thumbs = ThumbCache(self)
        self.story_selection: list[int] = []
        self.video_selection: list[str] = []
        self.edit_selection: list[int] = []
        self.generation = 0
        self._results: dict = {}
        self._results_gen = -1
        self.badges: dict[str, int] = {}
        # Connected first, so every other listener sees the new generation.
        self.library_modified.connect(self._on_modified)

    def set_library(self, lib: Optional[Library]) -> None:
        if self.library is not None and self.library is not lib:
            self.library.close()
        self.library = lib
        self.indexing = False
        from ..engine import storage
        self.maintenance = lib is not None and storage.pending(lib) is not None
        self.thumbs.clear()
        self._results, self._results_gen = {}, -1
        self.generation += 1
        self.set_badges({})
        self.library_opened.emit()

    def set_indexing(self, value: bool) -> None:
        self.indexing = value
        self.indexing_changed.emit(value)

    def _on_modified(self) -> None:
        self.thumbs.clear()
        self.generation += 1
        if self._results_gen != self.generation:
            self._results = {}
            if self.badges:
                self.set_badges({})

    # results of "Check everything", valid until the library changes again ---------------
    def store_results(self, results: dict) -> None:
        """Store results that stay valid through the library_modified signal emitted next."""
        self._results = dict(results)
        self._results_gen = self.generation + 1

    def cached(self, key: str):
        return self._results.get(key) if self._results_gen == self.generation else None

    def set_badges(self, counts: dict) -> None:
        self.badges = {k: v for k, v in counts.items() if v}
        self.badges_changed.emit(self.badges)

    def set_badge(self, key: str, count: int) -> None:
        b = dict(self.badges)
        b[key] = count
        self.set_badges(b)


class ThumbCache:
    def __init__(self, ctx: AppContext, capacity: int = 4000, max_bytes: int = 64 * 1024 * 1024):
        self.ctx = ctx
        self.capacity = capacity
        self.max_bytes = max_bytes
        self.bytes = 0
        self._cache: OrderedDict[int, Optional[QPixmap]] = OrderedDict()

    def clear(self) -> None:
        self._cache.clear()
        self.bytes = 0

    def invalidate(self, file_ids) -> None:
        for file_id in file_ids:
            pixmap = self._cache.pop(file_id, None)
            if pixmap is not None:
                self.bytes -= pixmap.width() * pixmap.height() * max(1, pixmap.depth() // 8)

    def get(self, file_id: int) -> Optional[QPixmap]:
        if file_id in self._cache:
            self._cache.move_to_end(file_id)
            return self._cache[file_id]
        lib = self.ctx.library
        pm = None
        if lib is not None:
            data = lib.thumbnail(file_id)
            if data:
                pm = QPixmap()
                if not pm.loadFromData(data, "JPG"):
                    pm = None
        if pm is not None:
            self._cache[file_id] = pm
            self.bytes += pm.width() * pm.height() * max(1, pm.depth() // 8)
            while self._cache and (len(self._cache) > self.capacity or self.bytes > self.max_bytes):
                _, old = self._cache.popitem(last=False)
                self.bytes -= old.width() * old.height() * max(1, old.depth() // 8)
        return pm


# ------------------------------------------------------------------------------ photo grid
class PhotoModel(QAbstractListModel):
    """Items are dicts with at least ``id``; optional: caption, sub, badge, badge_kind, checked, kind, duration."""
    checked_changed = Signal()

    def __init__(self, thumbs: ThumbCache, parent=None):
        super().__init__(parent)
        self.thumbs = thumbs
        self.items: list[dict] = []

    def set_items(self, items: list[dict]) -> None:
        self.beginResetModel()
        self.items = items
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.items)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        it = self.items[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            return it.get("caption", "")
        if role == Qt.ItemDataRole.DecorationRole:
            return self.thumbs.get(it["id"]) if it.get("id") is not None else None
        if role == Qt.ItemDataRole.UserRole:
            return it
        if role == Qt.ItemDataRole.ToolTipRole:
            return it.get("tip") or it.get("rel_path")
        return None

    def toggle(self, row: int) -> None:
        it = self.items[row]
        if it.get("checked") is None:
            return
        it["checked"] = not it["checked"]
        idx = self.index(row)
        self.dataChanged.emit(idx, idx)
        self.checked_changed.emit()

    def set_all_checked(self, value: bool) -> None:
        for it in self.items:
            if it.get("checked") is not None:
                it["checked"] = value
        if self.items:
            self.dataChanged.emit(self.index(0), self.index(len(self.items) - 1))
        self.checked_changed.emit()

    def checked(self) -> list[dict]:
        return [it for it in self.items if it.get("checked")]




class PhotoDelegate(QStyledItemDelegate):
    def __init__(self, cell: int = 168, captions: int = 2, parent=None):
        super().__init__(parent)
        self.cell = cell
        self.captions = captions

    def sizeHint(self, option, index) -> QSize:
        return QSize(self.cell, self.cell + (18 * self.captions if self.captions else 0) + 8)

    def checkbox_rect(self, rect: QRect) -> QRect:
        return QRect(rect.left() + 10, rect.top() + 10, 20, 20)

    def paint(self, p: QPainter, option, index) -> None:
        it = index.data(Qt.ItemDataRole.UserRole)
        r = option.rect.adjusted(4, 4, -4, -4)
        p.save()
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        selected = bool(option.state & QStyle.StateFlag.State_Selected)
        img_rect = QRect(r.left(), r.top(), r.width(), r.width())
        path = QPainterPath()
        path.addRoundedRect(QRectF(img_rect), 8, 8)
        p.fillPath(path, QColor(theme.PLACEHOLDER))
        pm = index.data(Qt.ItemDataRole.DecorationRole)
        dim = it.get("checked") is False and it.get("dim_unchecked")
        if pm is not None and not pm.isNull():
            scaled = pm.scaled(img_rect.size(), Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)
            x = img_rect.left() + (img_rect.width() - scaled.width()) // 2
            y = img_rect.top() + (img_rect.height() - scaled.height()) // 2
            p.setClipPath(path)
            p.drawPixmap(x, y, scaled)
            p.setClipping(False)
        else:
            p.setPen(QColor(theme.MUTED))
            p.drawText(img_rect, Qt.AlignmentFlag.AlignCenter,
                       "Can't preview" if it.get("error") else ("No preview" if it.get("kind") == "other" else "…"))
        if dim:
            veil = QColor(theme.CARD)
            veil.setAlpha(140)
            p.fillPath(path, veil)
        if it.get("kind") == "video":
            tag = f"▶ {fmt_duration(it.get('duration'))}".strip()
            fm = p.fontMetrics()
            w = fm.horizontalAdvance(tag) + 12
            tr = QRect(img_rect.right() - w - 6, img_rect.bottom() - 24, w, 18)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(0, 0, 0, 160))
            p.drawRoundedRect(tr, 4, 4)
            p.setPen(QColor("white"))
            p.drawText(tr, Qt.AlignmentFlag.AlignCenter, tag)
        if it.get("badge"):
            bg, fg = theme.badge_colors(it.get("badge_kind", "info"))
            f = p.font()
            f.setBold(True)
            f.setPointSizeF(8)
            p.setFont(f)
            fm = p.fontMetrics()
            w = fm.horizontalAdvance(it["badge"]) + 14
            br = QRect(img_rect.right() - w - 6, img_rect.top() + 8, w, 20)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(bg))
            p.drawRoundedRect(br, 10, 10)
            p.setPen(QColor(fg))
            p.drawText(br, Qt.AlignmentFlag.AlignCenter, it["badge"])
            p.setFont(option.font)
        if it.get("checked") is not None:
            cb = self.checkbox_rect(r)
            p.setPen(QPen(QColor("white"), 2))
            p.setBrush(QColor(theme.ACCENT) if it["checked"] else QColor(0, 0, 0, 90))
            p.drawRoundedRect(cb, 5, 5)
            if it["checked"]:
                p.setPen(QPen(QColor("white"), 2.4))
                p.drawPolyline([QPoint(cb.left() + 5, cb.center().y()), QPoint(cb.left() + 9, cb.bottom() - 5),
                                QPoint(cb.right() - 4, cb.top() + 5)])
        if selected:
            p.setPen(QPen(QColor(theme.ACCENT), 3))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(QRectF(img_rect).adjusted(1.5, 1.5, -1.5, -1.5), 8, 8)
        if self.captions:
            p.setPen(QColor(theme.TEXT))
            fm = p.fontMetrics()
            cap = fm.elidedText(it.get("caption", ""), Qt.TextElideMode.ElideMiddle, r.width())
            p.drawText(QRect(r.left(), img_rect.bottom() + 4, r.width(), 18), Qt.AlignmentFlag.AlignLeft, cap)
            if self.captions > 1 and it.get("sub"):
                p.setPen(QColor(it.get("sub_color", theme.MUTED)))
                sub = fm.elidedText(it["sub"], Qt.TextElideMode.ElideRight, r.width())
                p.drawText(QRect(r.left(), img_rect.bottom() + 22, r.width(), 18), Qt.AlignmentFlag.AlignLeft, sub)
        p.restore()

    def editorEvent(self, event, model, option, index):
        from PySide6.QtCore import QEvent
        if event.type() == QEvent.Type.MouseButtonRelease:
            it = index.data(Qt.ItemDataRole.UserRole)
            if it.get("checked") is not None and self.checkbox_rect(option.rect.adjusted(4, 4, -4, -4)).adjusted(
                    -6, -6, 6, 6).contains(event.position().toPoint()):
                model.toggle(index.row())
                return True
        return False


class PhotoGrid(QListView):
    activated_item = Signal(dict)
    current_item = Signal(dict)

    def __init__(self, thumbs: ThumbCache, cell: int = 168, captions: int = 2, parent=None):
        super().__init__(parent)
        self.model_ = PhotoModel(thumbs, self)
        self.setModel(self.model_)
        self.delegate = PhotoDelegate(cell, captions, self)
        self.setItemDelegate(self.delegate)
        self.setViewMode(QListView.ViewMode.IconMode)
        self.setResizeMode(QListView.ResizeMode.Adjust)
        self.setMovement(QListView.Movement.Static)
        self.setUniformItemSizes(True)
        self.setSpacing(2)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.verticalScrollBar().setSingleStep(24)
        self.setLayoutMode(QListView.LayoutMode.Batched)
        self.setBatchSize(400)
        self.setStyleSheet("QListView { border: none; background: transparent; }")
        self.doubleClicked.connect(lambda i: self.activated_item.emit(i.data(Qt.ItemDataRole.UserRole)))
        self.selectionModel().currentChanged.connect(
            lambda cur, _: cur.isValid() and self.current_item.emit(cur.data(Qt.ItemDataRole.UserRole)))

    def set_items(self, items: list[dict]) -> None:
        self.model_.set_items(items)

    def items(self) -> list[dict]:
        return self.model_.items

    def selected_items(self) -> list[dict]:
        return [i.data(Qt.ItemDataRole.UserRole) for i in sorted(self.selectedIndexes(), key=lambda i: i.row())]

    def keyPressEvent(self, e) -> None:
        if e.key() == Qt.Key.Key_Space and self.currentIndex().isValid():
            self.model_.toggle(self.currentIndex().row())
            return
        super().keyPressEvent(e)


# ------------------------------------------------------------------------------ preview
class Preview(QFrame):
    """Large preview of one file with its key facts."""

    def __init__(self, ctx: AppContext, width: int = 340, *, hold_on_index_update: bool = False):
        super().__init__()
        self.ctx = ctx
        self._hold_on_index_update = hold_on_index_update
        self.setObjectName("card")
        self.setFixedWidth(width)
        self.image = QLabel()
        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image.setMinimumHeight(240)
        self.image.setStyleSheet(f"background: {theme.PREVIEW_BG}; border-radius: 8px;")
        self.title = label("", "h2", wrap=True)
        self.facts = QLabel()
        self.facts.setWordWrap(True)
        self.facts.setTextFormat(Qt.TextFormat.RichText)
        self.facts.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.facts.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.open_btn = button("Open", on_click=self._open)
        self.show_btn = button("Show in folder", on_click=self._show)
        details = scroll(self.facts)
        details.setMinimumHeight(100)
        lay = vbox(self.image, self.title, details, hbox(self.open_btn, self.show_btn, None), spacing=10)
        lay.setStretchFactor(details, 1)
        lay.setContentsMargins(14, 14, 14, 14)
        self.setLayout(lay)
        self.row: Optional[dict] = None
        self.loader = LatestCall(self)
        self.loader.result.connect(self._loaded)
        self.loader.failed.connect(self._load_failed)
        self.access = LatestCall(self)
        self.access.result.connect(self._external_ready)
        self.access.failed.connect(self._load_failed)
        self._request = None
        self._facts = ""
        ctx.library_opened.connect(self.clear)
        ctx.library_modified.connect(self._library_modified)
        self.clear()

    def _library_modified(self) -> None:
        if (self._hold_on_index_update and self.ctx.index_update and self.row is not None
                and self._request is not None and self._request[0] is self.ctx.library):
            # Photos deliberately holds its selected row while indexing. Retain the
            # displayed snapshot, but never accept work from the previous generation.
            pending = self.image.pixmap().isNull() and self.image.text() == "Loading preview…"
            self.loader.invalidate()
            self.access.invalidate()
            lib = self.ctx.library
            self._request = (lib, self.ctx.generation, self.row["rel_path"])
            if pending:
                request, snapshot = self._request, dict(self.row)
                self.loader.call(lambda: (request, read_image(lib, snapshot, 900)))
            return
        self.clear()

    def clear(self) -> None:
        self.loader.invalidate()
        self.access.invalidate()
        self._request = None
        self.row = None
        self.image.setPixmap(QPixmap())
        self.image.setText("Select a photo to see details")
        self.title.setText("")
        self.facts.setText("")
        self.open_btn.setEnabled(False)
        self.show_btn.setEnabled(False)

    def show_row(self, row: dict, extra: str = "") -> None:
        with self.ctx.diagnostics.measure("preview"):
            self._show_row(row, extra)

    def _show_row(self, row: dict, extra: str = "") -> None:
        lib = self.ctx.library
        if lib is None or row is None or row.get("rel_path") is None:
            self.clear()
            return
        self.row = row
        self.access.invalidate()
        self.image.setPixmap(QPixmap())
        self.image.setText("Loading preview…")
        request = (lib, self.ctx.generation, row["rel_path"])
        self._request = request
        snapshot = dict(row)
        self.loader.call(lambda: (request, read_image(lib, snapshot, 900)))
        self.title.setText(row.get("name") or Path(row["rel_path"]).name)
        facts = []
        src = {"exif": "camera", "metadata": "video metadata", "filename": "file name",
               "modified": "file date — may be inaccurate"}.get(row.get("date_source") or "", "")
        if row.get("taken_at"):
            facts.append(f"<b>Taken</b> {fmt_date(row['taken_at'], True)} <span style='color:{theme.MUTED}'>({src})</span>")
        if row.get("width"):
            facts.append(f"<b>Size</b> {row['width']}×{row['height']} · {fmt_size(row.get('size'))}")
        else:
            facts.append(f"<b>Size</b> {fmt_size(row.get('size'))}")
        if row.get("duration") and row["duration"] > 0:
            facts.append(f"<b>Length</b> {fmt_duration(row['duration'])}")
        if row.get("ext"):
            facts.append(f"<b>Format</b> {escape(row['ext'].lstrip('.').upper())}")
        if row.get("mtime") is not None:
            facts.append(f"<b>Modified</b> {fmt_date(datetime.fromtimestamp(row['mtime']).isoformat(), True)}")
        if row.get("kind") == "video":
            from ..engine.catalogue import overall_bitrate
            rate = overall_bitrate(row)
            if rate is not None:
                facts.append(f"<b>Overall bitrate</b> ≈{rate:.3f} Mbps <span style='color:{theme.MUTED}'>(incl. audio/overhead)</span>")
            if row.get("fps"):
                facts.append(f"<b>Frame rate</b> {row['fps']:g} fps (reported)")
            if row.get("video_codec"):
                facts.append(f"<b>Video codec</b> {escape(row['video_codec'])}")
            if row.get("audio_codec") is not None:
                facts.append(f"<b>Audio</b> {escape(row['audio_codec']) or 'No audio stream'}")
        if row.get("camera"):
            facts.append(f"<b>Camera</b> {escape(row['camera'])}")
        if row.get("lens"):
            facts.append(f"<b>Lens</b> {escape(row['lens'])}")
        if row.get("iso"):
            facts.append(f"<b>ISO</b> {row['iso']:g}")
        if row.get("aperture"):
            facts.append(f"<b>Aperture</b> f/{row['aperture']:g}")
        if row.get("exposure_seconds"):
            sec = row["exposure_seconds"]
            facts.append(f"<b>Exposure</b> " + (f"1/{1/sec:g} s" if sec < 1 else f"{sec:g} s"))
        if row.get("focal_length_mm"):
            facts.append(f"<b>Focal length</b> {row['focal_length_mm']:g} mm (actual)")
        if row.get("lat") is not None:
            facts.append(f"<b>Location</b> {row['lat']:.4f}, {row['lon']:.4f}")
        if row.get("error"):
            facts.append(f"<span style='color:{theme.DANGER}'><b>Problem</b> {friendly_error(row['error'])}</span>")
        facts.append(f"<span style='color:{theme.MUTED}'>{escape(row['rel_path'])}</span>")
        if extra:
            facts.append(extra)
        self._facts = "<br>".join(facts)
        self.facts.setText(self._facts)
        self.open_btn.setEnabled(row.get("kind") in ("image", "video"))
        self.open_btn.setToolTip("" if row.get("kind") in ("image", "video") else
                                 "Only photos and videos can be opened from Memoria. Use Show in folder.")
        self.show_btn.setEnabled(True)

    def _loaded(self, result) -> None:
        request, (image, error) = result
        if request != self._request or request[:2] != (self.ctx.library, self.ctx.generation):
            return
        if image.isNull():
            self.image.setText("Could not load preview" if error else "No preview available")
        else:
            w = self.width() - 28
            self.image.setPixmap(QPixmap.fromImage(image).scaled(
                w, int(w * .85), Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation))
        if error:
            self._load_failed(error)

    def _load_failed(self, error) -> None:
        if not self._request or self._request[:2] != (self.ctx.library, self.ctx.generation):
            return
        if self.image.pixmap().isNull():
            self.image.setText("Could not load preview")
        self.facts.setText(self._facts + f"<br><b>Preview unavailable</b><br>{escape(str(error))}<br>"
                           "Check the format/codec and file access before assuming damage. "
                           "A cached preview may be shown.")

    def shutdown(self) -> None:
        self.loader.wait()
        self.access.wait()

    def _open(self):
        if self.row and self.ctx.library and self.row.get("kind") in ("image", "video"):
            self._external("open")

    def _show(self):
        if self.row and self.ctx.library:
            self._external("show")

    def _external(self, action):
        lib, request, key = self.ctx.library, self._request, self.row["rel_path"]
        self.access.call(lambda: (request, action, checked_path(lib, key)))

    def _external_ready(self, result):
        request, action, path = result
        if request == self._request and request[:2] == (self.ctx.library, self.ctx.generation):
            (open_path if action == "open" else show_in_explorer)(path)


# ------------------------------------------------------------------------------ dialogs
class ConfirmDialog(Dialog):
    """States exactly what will happen before any file is touched."""

    def __init__(self, parent, title: str, summary: str, details: list[str], confirm_text: str,
                 danger: bool = False, require_ack: Optional[str] = None, note: Optional[str] = None,
                 note_kind: str = "trust", thumbs: Optional["ThumbCache"] = None,
                 file_ids: Optional[list[int]] = None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedWidth(580)     # a fixed width lets wrapped text claim the height it needs
        t = label(title, "h2")
        s = label(summary, wrap=True)
        lay = vbox(t, s, spacing=12, margins=(22, 20, 22, 18))
        if thumbs is not None and file_ids:
            lay.addLayout(self._strip(thumbs, file_ids))
        if details:
            d = QLabel("<ul style='margin-left:-20px'>" + "".join(f"<li>{x}</li>" for x in details) + "</ul>")
            d.setTextFormat(Qt.TextFormat.RichText)
            d.setWordWrap(True)
            lay.addWidget(d)
        if note:
            lay.addWidget(Banner(note, note_kind))
        self.ok = button(confirm_text, "danger" if danger else "primary", self.accept)
        cancel = button("Cancel", on_click=self.reject)
        if require_ack:
            self.ack = QCheckBox(require_ack)
            self.ack.toggled.connect(self.ok.setEnabled)
            self.ok.setEnabled(False)
            lay.addWidget(self.ack)
        lay.addSpacing(6)
        lay.addLayout(hbox(None, cancel, self.ok))
        self.setLayout(lay)
        cancel.setFocus()

    def showEvent(self, e) -> None:
        super().showEvent(e)
        h = self.layout().totalHeightForWidth(self.width())
        if h > 0:
            self.setFixedHeight(h)

    @staticmethod
    def _strip(thumbs: "ThumbCache", file_ids: list[int], limit: int = 7) -> QHBoxLayout:
        """A row of thumbnails of the affected files, so the user sees exactly what is about to move."""
        row = QHBoxLayout()
        row.setSpacing(8)
        for fid in file_ids[:limit]:
            pm = thumbs.get(fid)
            cell = QLabel()
            cell.setFixedSize(56, 56)
            canvas = QPixmap(56, 56)
            canvas.fill(Qt.GlobalColor.transparent)
            p = QPainter(canvas)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            path = QPainterPath()
            path.addRoundedRect(QRectF(0, 0, 56, 56), 8, 8)
            p.fillPath(path, QColor(theme.PLACEHOLDER))
            if pm is not None and not pm.isNull():
                img = pm.scaled(56, 56, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                Qt.TransformationMode.SmoothTransformation)
                p.setClipPath(path)
                p.drawPixmap((56 - img.width()) // 2, (56 - img.height()) // 2, img)
            p.end()
            cell.setPixmap(canvas)
            row.addWidget(cell)
        if len(file_ids) > limit:
            row.addWidget(label(f"+{len(file_ids) - limit:,} more", "muted"))
        row.addStretch(1)
        return row


def confirm(parent, title, summary, details, confirm_text, **kw) -> bool:
    return ConfirmDialog(parent, title, summary, details, confirm_text, **kw).exec() == QDialog.DialogCode.Accepted


class Viewer(Dialog):
    """Full-size viewer with ← / → navigation through a list of library items."""

    def __init__(self, parent, ctx: "AppContext", items: list[dict], index: int):
        super().__init__(parent)
        self.ctx, self.items, self.index = ctx, [i for i in items if i.get("rel_path")], 0
        self.setWindowTitle("Memoria — viewer")
        self.setStyleSheet("QDialog { background: #111214; } QLabel { color: #E6E8EB; }")
        self.image = QLabel()
        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.caption = QLabel()
        self.caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        prev_b = button("‹  Previous", on_click=lambda: self.step(-1), tip="Left arrow")
        next_b = button("Next  ›", on_click=lambda: self.step(1), tip="Right arrow")
        open_b = button("Open in default app", on_click=self._open_external)
        show_b = button("Show in folder", on_click=lambda: self._external("show"))
        close_b = button("Close", on_click=self.close, tip="Esc")
        lay = vbox(self.image, self.caption, hbox(prev_b, next_b, None, open_b, show_b, close_b),
                   spacing=10, margins=(16, 16, 16, 14))
        lay.setStretch(0, 1)
        self.setLayout(lay)
        self._pixmap = QPixmap()
        self.loader = LatestCall(self)
        self.loader.result.connect(self._loaded)
        self.loader.failed.connect(self._load_failed)
        self.access = LatestCall(self)
        self.access.result.connect(self._external_ready)
        self.access.failed.connect(self._load_failed)
        self._request = None
        self._library = ctx.library
        self.finished.connect(lambda *_: (self.loader.invalidate(), self.access.invalidate()))
        ctx.library_opened.connect(self._invalidate)
        ctx.library_modified.connect(self._invalidate)
        if self.items:
            target = items[index] if 0 <= index < len(items) else None
            self.index = next((n for n, it in enumerate(self.items) if it is target), 0)
        self.resize(parent.window().size() * 0.92 if parent else QSize(1200, 800))
        self._load()

    @property
    def current(self) -> Optional[dict]:
        return self.items[self.index] if self.items else None

    def step(self, delta: int) -> None:
        if self.items:
            self.index = (self.index + delta) % len(self.items)
            self._load()

    def _load(self) -> None:
        it = self.current
        if it is None or self.ctx.library is not self._library or self._library is None:
            return
        self._pixmap = QPixmap()
        self.access.invalidate()
        self.image.clear()
        self.image.setText("Loading preview…")
        lib = self._library
        request = (lib, self.ctx.generation, self.index)
        self._request = request
        snapshot, edge = dict(it), min(2400, max(self.width(), self.height(), 1600))
        self.loader.call(lambda: (request, read_image(lib, snapshot, edge)))
        when = fmt_date(it.get("taken_at"), True) if it.get("taken_at") else ""
        extra = "  ·  ▶ video — use “Open in default app” to play" if it.get("kind") == "video" else ""
        self._caption = (f"<b>{escape(it.get('name', ''))}</b>   {escape(when)}   "
                         f"<span style='color:#A1A7B0'>{self.index + 1} of {len(self.items)}{extra}</span>")
        if it.get("error"):
            self._caption += f"<br>{escape(it['error'])}"
        self.caption.setText(self._caption)

    def _loaded(self, result) -> None:
        request, (image, error) = result
        if request != self._request or request[:2] != (self.ctx.library, self.ctx.generation):
            return
        self._pixmap = QPixmap.fromImage(image)
        if image.isNull():
            self.image.setText("Could not load preview" if error else "No preview available")
        else:
            self._fit()
        if error:
            self._load_failed(error)

    def _load_failed(self, error) -> None:
        if not self._request or self._request[:2] != (self.ctx.library, self.ctx.generation):
            return
        if self._pixmap.isNull():
            self.image.setText("Could not load preview")
        self.caption.setText(self._caption + f"<br>{escape(str(error))}<br>"
                             "Check format/codec and access before assuming damage. A cached preview may be shown.")

    def _invalidate(self) -> None:
        self.loader.invalidate()
        self.access.invalidate()
        self._request = None
        self.items = []
        self._pixmap = QPixmap()
        self.image.clear()
        self.image.setText("Library changed. Close this viewer and select the file again.")

    def shutdown(self) -> None:
        self.loader.wait()
        self.access.wait()

    def _fit(self) -> None:
        if not self._pixmap.isNull():
            self.image.setPixmap(self._pixmap.scaled(self.image.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                                     Qt.TransformationMode.SmoothTransformation))

    def resizeEvent(self, e) -> None:
        super().resizeEvent(e)
        self._fit()

    def keyPressEvent(self, e) -> None:
        if e.key() in (Qt.Key.Key_Right, Qt.Key.Key_Down, Qt.Key.Key_PageDown, Qt.Key.Key_Space):
            self.step(1)
        elif e.key() in (Qt.Key.Key_Left, Qt.Key.Key_Up, Qt.Key.Key_PageUp, Qt.Key.Key_Backspace):
            self.step(-1)
        else:
            super().keyPressEvent(e)

    def _open_external(self) -> None:
        if (self.current and self.ctx.library is self._library
                and self.current.get("kind") in ("image", "video")):
            self._external("open")

    def _external(self, action):
        if not self.current or self.ctx.library is not self._library:
            return
        lib, request, key = self._library, self._request, self.current["rel_path"]
        self.access.call(lambda: (request, action, checked_path(lib, key)))

    def _external_ready(self, result):
        request, action, path = result
        if request == self._request and request[:2] == (self.ctx.library, self.ctx.generation):
            (open_path if action == "open" else show_in_explorer)(path)


class MessageDialog(Dialog):
    def __init__(self, parent, title: str, text: str, details: str = ""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(460)
        lay = vbox(label(title, "h2"), label(text, wrap=True), spacing=12, margins=(22, 20, 22, 18))
        if details:
            from PySide6.QtWidgets import QPlainTextEdit
            box = QPlainTextEdit(details)
            box.setReadOnly(True)
            box.setMaximumHeight(200)
            lay.addWidget(box)
        lay.addLayout(hbox(None, button("OK", "primary", self.accept)))
        self.setLayout(lay)


class Toast(QFrame):
    """Bottom notification with an optional Undo button."""
    undo_clicked = Signal(str)

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName("toast")
        self.msg = QLabel()
        self.msg.setWordWrap(True)
        self.undo_btn = QPushButton("Undo")
        self.undo_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.undo_btn.clicked.connect(self._undo)
        close = QPushButton("✕")
        close.setCursor(Qt.CursorShape.PointingHandCursor)
        close.clicked.connect(self.hide)
        lay = hbox(self.msg, self.undo_btn, close, spacing=12, margins=(16, 10, 10, 10))
        lay.setStretch(0, 1)
        self.setLayout(lay)
        self.batch_id = ""
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(theme.SHADOW))
        self.setGraphicsEffect(shadow)
        self.hide()

    def show_message(self, text: str, batch_id: str = "", seconds: int = 10) -> None:
        self.msg.setText(text)
        self.batch_id = batch_id
        self.undo_btn.setVisible(bool(batch_id))
        appearing = not self.isVisible()
        target = self._place()
        self.show()
        self.raise_()
        if appearing:
            motion.slide_in(self, target)
        else:
            self.move(target)
        self.timer.start(seconds * 1000)

    def _place(self) -> QPoint:
        par = self.parentWidget()
        w = min(640, par.width() - 300)
        self.setFixedWidth(max(360, w))
        self.adjustSize()
        return QPoint(par.width() - self.width() - 24, par.height() - self.height() - 70)

    def reposition(self) -> None:
        self.move(self._place())

    def _undo(self):
        self.hide()
        if self.batch_id:
            self.undo_clicked.emit(self.batch_id)
