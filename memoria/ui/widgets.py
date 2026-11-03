"""Reusable widgets: page scaffold, tiles, banners, photo grid, preview, dialogs, toast."""
from __future__ import annotations

import os
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
from PySide6.QtWidgets import (QAbstractItemView, QCheckBox, QDialog, QFrame, QGridLayout, QHBoxLayout,
                               QLabel, QListView, QPushButton, QScrollArea, QSizePolicy, QStyle,
                               QStyledItemDelegate, QVBoxLayout, QWidget)

from . import theme
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
    if not sec:
        return ""
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
        return "This isn't a picture Memoria can read (it may be empty, damaged or not really an image)."
    if "no video stream" in e:
        return "No playable video was found in this file."
    if "permission" in e or "access is denied" in e:
        return "Windows didn't allow Memoria to read this file."
    if "could not be read" in e:
        return "The file could not be read from the drive."
    return "The file couldn't be opened. It may be damaged."


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


class Tile(QFrame):
    def __init__(self, value: str = "—", text: str = "", sub: str = ""):
        super().__init__()
        self.setObjectName("tile")
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self.value = label(value, "tileValue")
        self.text = label(text, "tileLabel")
        self.sub = label(sub or " ", "small")
        lay = vbox(self.text, self.value, self.sub, spacing=2)
        lay.setContentsMargins(14, 10, 14, 10)
        self.setLayout(lay)
        self.setMinimumWidth(130)

    def set(self, value: str, sub: str = "", color: Optional[str] = None) -> None:
        self.value.setText(value)
        self.value.setStyleSheet(f"color: {color};" if color else "")
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

    def __init__(self, runner):
        super().__init__()
        self.runner = runner
        self.library: Optional[Library] = None
        self.thumbs = ThumbCache(self)
        self.story_selection: list[int] = []

    def set_library(self, lib: Optional[Library]) -> None:
        if self.library is not None:
            self.library.close()
        self.library = lib
        self.thumbs.clear()
        self.library_opened.emit()


class ThumbCache:
    def __init__(self, ctx: AppContext, capacity: int = 4000):
        self.ctx = ctx
        self.capacity = capacity
        self._cache: OrderedDict[int, Optional[QPixmap]] = OrderedDict()

    def clear(self) -> None:
        self._cache.clear()

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
            if len(self._cache) > self.capacity:
                self._cache.popitem(last=False)
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


BADGE_COLORS = {"keep": (theme.OK, "white"), "best": (theme.OK, "white"), "warn": (theme.WARN, "white"),
                "info": (theme.ACCENT, "white"), "muted": ("#6B7280", "white")}


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
        p.fillPath(path, QColor("#E9EBEF"))
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
            p.fillPath(path, QColor(255, 255, 255, 120))
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
            bg, fg = BADGE_COLORS.get(it.get("badge_kind", "info"), BADGE_COLORS["info"])
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

    def __init__(self, ctx: AppContext, width: int = 340):
        super().__init__()
        self.ctx = ctx
        self.setObjectName("card")
        self.setFixedWidth(width)
        self.image = QLabel()
        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image.setMinimumHeight(240)
        self.image.setStyleSheet("background: #F0F2F5; border-radius: 8px;")
        self.title = label("", "h2", wrap=True)
        self.facts = QLabel()
        self.facts.setWordWrap(True)
        self.facts.setTextFormat(Qt.TextFormat.RichText)
        self.facts.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.open_btn = button("Open", on_click=self._open)
        self.show_btn = button("Show in folder", on_click=self._show)
        lay = vbox(self.image, self.title, self.facts, hbox(self.open_btn, self.show_btn, None), None, spacing=10)
        lay.setContentsMargins(14, 14, 14, 14)
        self.setLayout(lay)
        self.row: Optional[dict] = None
        self.clear()

    def clear(self) -> None:
        self.row = None
        self.image.setPixmap(QPixmap())
        self.image.setText("Select a photo to see details")
        self.title.setText("")
        self.facts.setText("")
        self.open_btn.setEnabled(False)
        self.show_btn.setEnabled(False)

    def show_row(self, row: dict, extra: str = "") -> None:
        lib = self.ctx.library
        if lib is None or row is None or row.get("rel_path") is None:
            self.clear()
            return
        self.row = row
        path = lib.abspath(row["rel_path"])
        pm = None
        if row.get("kind") == "image" and not row.get("error"):
            try:
                from ..engine.media import load_for_display
                img = load_for_display(path, 900)
                qimg = QImage(img.tobytes(), img.width, img.height, img.width * 3, QImage.Format.Format_RGB888)
                pm = QPixmap.fromImage(qimg.copy())
            except Exception:
                pm = None
        if pm is None and row.get("id") is not None:
            pm = self.ctx.thumbs.get(row["id"])
        w = self.width() - 28
        if pm is not None:
            self.image.setPixmap(pm.scaled(w, int(w * 0.85), Qt.AspectRatioMode.KeepAspectRatio,
                                           Qt.TransformationMode.SmoothTransformation))
        else:
            self.image.setPixmap(QPixmap())
            self.image.setText("No preview available")
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
        if row.get("duration"):
            facts.append(f"<b>Length</b> {fmt_duration(row['duration'])}")
        if row.get("camera"):
            facts.append(f"<b>Camera</b> {row['camera']}")
        if row.get("lat") is not None:
            facts.append(f"<b>Location</b> {row['lat']:.4f}, {row['lon']:.4f}")
        if row.get("error"):
            facts.append(f"<span style='color:{theme.DANGER}'><b>Problem</b> {friendly_error(row['error'])}</span>")
        facts.append(f"<span style='color:{theme.MUTED}'>{row['rel_path']}</span>")
        if extra:
            facts.append(extra)
        self.facts.setText("<br>".join(facts))
        self.open_btn.setEnabled(True)
        self.show_btn.setEnabled(True)

    def _open(self):
        if self.row and self.ctx.library:
            open_path(self.ctx.library.abspath(self.row["rel_path"]))

    def _show(self):
        if self.row and self.ctx.library:
            show_in_explorer(self.ctx.library.abspath(self.row["rel_path"]))


# ------------------------------------------------------------------------------ dialogs
class ConfirmDialog(QDialog):
    """States exactly what will happen before any file is touched."""

    def __init__(self, parent, title: str, summary: str, details: list[str], confirm_text: str,
                 danger: bool = False, require_ack: Optional[str] = None, note: Optional[str] = None,
                 note_kind: str = "trust"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(480)
        t = label(title, "h2")
        s = label(summary, wrap=True)
        lay = vbox(t, s, spacing=12, margins=(22, 20, 22, 18))
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


def confirm(parent, title, summary, details, confirm_text, **kw) -> bool:
    return ConfirmDialog(parent, title, summary, details, confirm_text, **kw).exec() == QDialog.DialogCode.Accepted


class MessageDialog(QDialog):
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
        self.hide()

    def show_message(self, text: str, batch_id: str = "", seconds: int = 10) -> None:
        self.msg.setText(text)
        self.batch_id = batch_id
        self.undo_btn.setVisible(bool(batch_id))
        self.reposition()
        self.show()
        self.raise_()
        self.timer.start(seconds * 1000)

    def reposition(self) -> None:
        par = self.parentWidget()
        w = min(640, par.width() - 300)
        self.setFixedWidth(max(360, w))
        self.adjustSize()
        self.move(par.width() - self.width() - 24, par.height() - self.height() - 70)

    def _undo(self):
        self.hide()
        if self.batch_id:
            self.undo_clicked.emit(self.batch_id)
