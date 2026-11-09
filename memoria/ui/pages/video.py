"""Video compressor: smaller copies of videos for sharing. Originals are never changed."""
from __future__ import annotations

import queue
import threading
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QAbstractTableModel, QEvent, QModelIndex, QObject, QPoint, QRect, QSize, Qt, Signal
from PySide6.QtGui import QColor, QIcon, QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (QAbstractItemView, QButtonGroup, QCheckBox, QComboBox, QDoubleSpinBox,
                               QFileDialog, QHeaderView, QRadioButton, QStyle, QStyledItemDelegate, QTableView, QTableWidget,
                               QTableWidgetItem, QWidget)

from ...engine import config, ffmpeg, videotools
from ...engine.ffmpeg import VideoInfo
from .. import theme
from ..widgets import (Banner, Card, MessageDialog, button, fmt_duration, fmt_n, fmt_size, hbox, label, scroll,
                       show_in_explorer, vbox)
from .base import Page
from .story import OutputFolder, Segmented, _inside

QUALITIES = [("High", "high", "Best quality, moderate savings"),
             ("Balanced", "balanced", "Looks the same on a phone, much smaller"),
             ("Small", "small", "Smallest files, some softness")]
CHIPS = [(16, "16 MB · WhatsApp"), (25, "25 MB · Email"), (100, "100 MB")]
RESOLUTIONS = [("Keep original", None), ("1080p (Full HD)", 1080), ("720p (HD)", 720), ("480p", 480)]
THUMB_W, THUMB_H = 80, 45
COLS = ["", "", "Name", "Length", "Resolution", "Size", "Estimated size"]
C_CHECK, C_THUMB, C_NAME, C_LEN, C_RES, C_SIZE, C_EST = range(7)
R_NAME, R_SIZES, R_SAVED, R_QUALITY, R_STATUS = range(5)
MAX_PENDING_PROBES = 2


def quality_label(ssim: Optional[float]) -> str:
    if ssim is None:
        return ""
    if ssim >= 0.98:
        return "Excellent"
    if ssim >= 0.95:
        return "Very good"
    if ssim >= 0.90:
        return "Good"
    return "Noticeable loss"


def _thumb_pixmap(pm: Optional[QPixmap]) -> QPixmap:
    out = QPixmap(THUMB_W, THUMB_H)
    out.fill(QColor("#2A2E35"))
    if pm is not None and not pm.isNull():
        scaled = pm.scaled(THUMB_W, THUMB_H, Qt.AspectRatioMode.KeepAspectRatio,
                           Qt.TransformationMode.SmoothTransformation)
        p = QPainter(out)
        p.drawPixmap((THUMB_W - scaled.width()) // 2, (THUMB_H - scaled.height()) // 2, scaled)
        p.end()
    return out


SUB_ROLE = Qt.ItemDataRole.UserRole + 1


class _CheckDelegate(QStyledItemDelegate):
    """Clear, consistent checkbox (the native item indicator is too faint on Windows 11)."""

    def paint(self, p: QPainter, option, index) -> None:
        if option.state & QStyle.StateFlag.State_Selected:
            p.fillRect(option.rect, QColor(theme.ACCENT_SOFT))
        checked = index.data(Qt.ItemDataRole.CheckStateRole) == Qt.CheckState.Checked.value or \
            index.data(Qt.ItemDataRole.CheckStateRole) == Qt.CheckState.Checked
        r = QRect(0, 0, 18, 18)
        r.moveCenter(option.rect.center())
        p.save()
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if checked:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(theme.ACCENT))
            p.drawRoundedRect(r, 4, 4)
            p.setPen(QPen(QColor("white"), 2))
            p.drawPolyline([r.topLeft() + QPoint(4, 9), r.topLeft() + QPoint(8, 13), r.topLeft() + QPoint(14, 5)])
        else:
            p.setPen(QPen(QColor("#9AA1AA"), 1.4))
            p.setBrush(QColor("white"))
            p.drawRoundedRect(r.adjusted(0, 0, -1, -1), 4, 4)
        p.restore()

    def editorEvent(self, event, model, option, index) -> bool:  # noqa: N802
        if (event.type() == QEvent.Type.MouseButtonRelease and option.rect.contains(event.position().toPoint())) or \
                (event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Space):
            cur = index.data(Qt.ItemDataRole.CheckStateRole)
            on = cur in (Qt.CheckState.Checked, Qt.CheckState.Checked.value)
            model.setData(index, Qt.CheckState.Unchecked if on else Qt.CheckState.Checked,
                          Qt.ItemDataRole.CheckStateRole)
            return True
        return event.type() in (QEvent.Type.MouseButtonPress, QEvent.Type.MouseButtonDblClick)


class _NameDelegate(QStyledItemDelegate):
    """File name with its folder underneath in muted text."""

    def paint(self, p: QPainter, option, index) -> None:
        if option.state & QStyle.StateFlag.State_Selected:
            p.fillRect(option.rect, QColor(theme.ACCENT_SOFT))
        sub = index.data(SUB_ROLE) or ""
        r = option.rect.adjusted(6, 0, -6, 0)
        fm = option.fontMetrics
        p.save()
        name = fm.elidedText(index.data(Qt.ItemDataRole.DisplayRole) or "", Qt.TextElideMode.ElideMiddle, r.width())
        if sub:
            top = r.center().y() - fm.height()
            p.setPen(QColor(theme.TEXT))
            p.drawText(QRect(r.left(), top, r.width(), fm.height()), Qt.AlignmentFlag.AlignLeft, name)
            f = option.font
            f.setPointSizeF(max(7.0, f.pointSizeF() - 1))
            p.setFont(f)
            p.setPen(QColor(theme.MUTED))
            sub = p.fontMetrics().elidedText(sub, Qt.TextElideMode.ElideMiddle, r.width())
            p.drawText(QRect(r.left(), top + fm.height() + 2, r.width(), fm.height()), Qt.AlignmentFlag.AlignLeft, sub)
        else:
            p.setPen(QColor(theme.TEXT))
            p.drawText(r, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, name)
        p.restore()


@dataclass(frozen=True)
class _Estimate:
    text: str = ""
    note: str = ""
    color: str = ""
    size: float = 0.0
    unknown: int = 0
    impossible: int = 0


class _VideoModel(QAbstractTableModel):
    """Keep row metadata, not one set of Qt items and pixmaps per video."""

    def __init__(self, page):
        super().__init__(page)
        self.page = page

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.page._rows)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(COLS)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                return COLS[section]
            if role == Qt.ItemDataRole.TextAlignmentRole:
                return (Qt.AlignmentFlag.AlignRight if section in (C_LEN, C_RES, C_SIZE, C_EST)
                        else Qt.AlignmentFlag.AlignLeft) | Qt.AlignmentFlag.AlignVCenter
        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        return flags | Qt.ItemFlag.ItemIsUserCheckable if index.column() == C_CHECK else flags

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        row, col = self.page._rows[index.row()], index.column()
        key = row["key"]
        estimate = self.page._estimates.get(key)
        if role == Qt.ItemDataRole.UserRole:
            return key
        if role == SUB_ROLE and col == C_NAME:
            return row["sub"]
        if role == Qt.ItemDataRole.CheckStateRole and col == C_CHECK:
            return Qt.CheckState.Checked if key in self.page._checked else Qt.CheckState.Unchecked
        if role == Qt.ItemDataRole.DecorationRole and col == C_THUMB:
            pm = self.page.ctx.thumbs.get(row["id"]) if row["id"] is not None else row.get("thumb")
            return QIcon(_thumb_pixmap(pm))
        if role == Qt.ItemDataRole.ToolTipRole:
            return estimate.note if col == C_EST and estimate else (
                str(row["path"]) if row["external"] else row["tip"])
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return (Qt.AlignmentFlag.AlignRight if col in (C_LEN, C_RES, C_SIZE, C_EST)
                    else Qt.AlignmentFlag.AlignLeft) | Qt.AlignmentFlag.AlignVCenter
        if role == Qt.ItemDataRole.ForegroundRole:
            return QColor(estimate.color if col == C_EST and estimate and estimate.color else theme.TEXT)
        if role == Qt.ItemDataRole.DisplayRole:
            if col == C_NAME:
                return row["name"]
            if col == C_LEN:
                return fmt_duration(row.get("duration")) or "—"
            if col == C_RES:
                return f"{row['width']}×{row['height']}" if row.get("width") else "—"
            if col == C_SIZE:
                return fmt_size(row["size"]) if row.get("size") else "—"
            if col == C_EST:
                return estimate.text if estimate else ""
        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid() or index.column() != C_CHECK or role != Qt.ItemDataRole.CheckStateRole:
            return False
        key = self.page._rows[index.row()]["key"]
        checked = value in (Qt.CheckState.Checked, Qt.CheckState.Checked.value)
        (self.page._checked.add if checked else self.page._checked.discard)(key)
        self.page._settings_changed()
        return True


class _Prober(QObject):
    """Background ffprobe-style reads (one at a time) so the table never blocks."""
    probed = Signal(str, object, object)  # key, VideoInfo | None, QImage | None

    def __init__(self, parent=None):
        super().__init__(parent)
        self._q: queue.Queue = queue.Queue()
        self._alive = True
        threading.Thread(target=self._loop, name="video-probe", daemon=True).start()

    def request(self, key: str, path: Path, want_frame: bool) -> None:
        self._q.put((key, path, want_frame))

    def stop(self) -> None:
        self._alive = False
        self._q.put(None)

    def _loop(self) -> None:
        while True:
            job = self._q.get()
            if job is None or not self._alive:
                return
            key, path, want_frame = job
            try:
                info = ffmpeg.probe(path)
            except Exception:
                info = None
            img = None
            if want_frame and info is not None:
                try:
                    data = ffmpeg.video_frame(path, at=min(1.0, info.duration / 2), max_side=256)
                    if data:
                        img = QImage.fromData(data, "JPG")
                except Exception:
                    img = None
            if not self._alive:
                return
            try:
                self.probed.emit(key, info, img)
            except RuntimeError:
                return


class VideoPage(Page):
    title = "Video compressor"
    subtitle = "Make smaller copies of videos for sharing — originals are never changed"
    glyph = "\uE714"

    def __init__(self, ctx):
        super().__init__(ctx)
        self._rows: list[dict] = []
        self._row_of: dict[str, int] = {}
        self._external: list[dict] = []
        self._checked: set[str] = set()
        self._info: dict[str, Optional[VideoInfo]] = {}
        self._pending: set[str] = set()
        self._probe_queue: deque[str] = deque()
        self._estimates: dict[str, _Estimate] = {}
        self._total_src = self._total_est = 0.0
        self._unknown = self._impossible = 0
        self._results: list[videotools.CompressResult] = []
        self._closed = False

        self.prober = _Prober(self)
        self.prober.probed.connect(self._probed)
        self.destroyed.connect(self.prober.stop)

        self.body.addWidget(Banner(
            "<b>Your original videos are never changed.</b> Compressed copies are saved as new files and "
            "checked: they must play, have the same length, and be smaller.", "trust"))
        left = vbox(self._build_videos(), self._build_results(), spacing=12)
        left.setStretch(0, 3)
        left.setStretch(1, 2)
        self.body.addLayout(hbox(left, self._build_settings(), spacing=14), 1)
        self._mode_changed()

    # ---------------------------------------------------------------------------- building
    def _build_videos(self) -> QWidget:
        self.table = QTableView()
        self.model = _VideoModel(self)
        self.table.setModel(self.model)
        self.table.verticalHeader().hide()
        self.table.setShowGrid(False)
        self.table.setIconSize(QSize(THUMB_W, THUMB_H))
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.table.setWordWrap(False)
        self.table.verticalHeader().setDefaultSectionSize(THUMB_H + 10)
        h = self.table.horizontalHeader()
        h.setHighlightSections(False)
        h.setMinimumSectionSize(30)
        h.setResizeContentsPrecision(50)
        for col, mode in ((C_CHECK, QHeaderView.ResizeMode.Fixed), (C_THUMB, QHeaderView.ResizeMode.Fixed),
                          (C_NAME, QHeaderView.ResizeMode.Stretch),
                          (C_LEN, QHeaderView.ResizeMode.ResizeToContents),
                          (C_RES, QHeaderView.ResizeMode.ResizeToContents),
                          (C_SIZE, QHeaderView.ResizeMode.ResizeToContents),
                          (C_EST, QHeaderView.ResizeMode.ResizeToContents)):
            h.setSectionResizeMode(col, mode)
        self.table.setColumnWidth(C_CHECK, 34)
        self.table.setColumnWidth(C_THUMB, THUMB_W + 12)
        self.table.setItemDelegateForColumn(C_CHECK, _CheckDelegate(self.table))
        self.table.setItemDelegateForColumn(C_NAME, _NameDelegate(self.table))
        self.table.doubleClicked.connect(self._toggle_row)
        self.count_label = label("", "small")
        self.empty = label("No videos in this library yet. Use “Add files from elsewhere…” to pick some.",
                           "muted", wrap=True)
        self.empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty.hide()
        add = button("Add files from elsewhere…", on_click=self._add_external,
                     tip="Compress videos that are not in this library")
        lay = vbox(hbox(label("Videos", "h2"), self.count_label, None,
                        button("Select all", "link", lambda: self._check_all(True)),
                        button("Select none", "link", lambda: self._check_all(False)), add, spacing=8),
                   self.table, self.empty, spacing=10)
        lay.setStretchFactor(self.table, 1)
        return Card(lay)

    def _build_results(self) -> QWidget:
        self.results = QTableWidget(0, 5)
        self.results.setHorizontalHeaderLabels(["Video", "Before → after", "Saved", "Quality", "Result"])
        self.results.verticalHeader().hide()
        self.results.setShowGrid(False)
        self.results.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.results.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.results.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.results.setWordWrap(False)
        self.results.setTextElideMode(Qt.TextElideMode.ElideMiddle)
        self.results.verticalHeader().setDefaultSectionSize(32)
        h = self.results.horizontalHeader()
        h.setHighlightSections(False)
        h.setSectionResizeMode(R_NAME, QHeaderView.ResizeMode.Stretch)
        for c in (R_SIZES, R_SAVED, R_QUALITY):
            h.setSectionResizeMode(c, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(R_STATUS, QHeaderView.ResizeMode.Stretch)
        h.setMinimumSectionSize(60)
        h.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.results.itemDoubleClicked.connect(lambda _: self._show_result())
        self.results.itemSelectionChanged.connect(
            lambda: self.show_result_btn.setEnabled(bool(self.results.selectedItems())))
        self.results_summary = label("", "small", wrap=True)
        self.show_result_btn = button("Show in folder", on_click=self._show_result)
        self.show_result_btn.setEnabled(False)
        self.open_results_btn = button("Open folder", on_click=lambda: self.output.open_folder())
        lay = vbox(hbox(label("Results", "h2"), None, self.show_result_btn, self.open_results_btn),
                   self.results_summary, self.results, spacing=8)
        lay.setStretchFactor(self.results, 1)
        self.results_card = Card(lay)
        self.results_card.hide()
        return self.results_card

    def _build_settings(self) -> QWidget:
        self.r_quality = QRadioButton("Quality preset")
        self.r_target = QRadioButton("Fit under a size")
        self.r_quality.setChecked(True)
        grp = QButtonGroup(self)
        grp.addButton(self.r_quality)
        grp.addButton(self.r_target)
        grp.buttonToggled.connect(lambda *_: self._mode_changed())
        self.quality = Segmented([q[0] for q in QUALITIES], 1)
        self.quality.changed.connect(lambda *_: (self.r_quality.setChecked(True), self._settings_changed()))
        self.quality_note = label("", "small", wrap=True)

        self.target = QDoubleSpinBox()
        self.target.setRange(1, 4000)
        self.target.setDecimals(0)
        self.target.setValue(25)
        self.target.setSuffix(" MB")
        self.target.setMinimumWidth(100)
        self.target.valueChanged.connect(lambda *_: (self.r_target.setChecked(True), self._settings_changed()))
        self.chips = []
        chip_style = (f"QPushButton {{ border-radius: 12px; padding: 3px 10px; min-height: 16px; font-size: 9pt; }}"
                      f"QPushButton:checked {{ background: {theme.ACCENT_SOFT}; border-color: {theme.ACCENT};"
                      f" color: {theme.ACCENT}; }}")
        for mb, text in CHIPS:
            b = button(text, on_click=lambda _=False, v=mb: self._chip(v))
            b.setCheckable(True)
            b.setStyleSheet(chip_style)
            self.chips.append((mb, b))
        self.target_hint = label("Slower (two passes) but lands just under the size.", "small", wrap=True)
        self.target_box = QWidget()
        chip_row = hbox(*[b for _, b in self.chips], None, spacing=6)
        self.target_box.setLayout(vbox(hbox(self.target, None), chip_row, self.target_hint, spacing=6,
                                       margins=(24, 0, 0, 0)))
        self.quality_box = QWidget()
        self.quality_box.setLayout(vbox(self.quality, self.quality_note, spacing=6, margins=(24, 0, 0, 0)))

        self.resolution = QComboBox()
        for text, val in RESOLUTIONS:
            self.resolution.addItem(text, val)
        self.resolution.setCurrentIndex(1)
        self.resolution.currentIndexChanged.connect(lambda *_: self._settings_changed())
        self.resolution.setToolTip("Portrait phone videos are matched by their shorter side, "
                                   "so a 1080×1920 video counts as 1080p.")
        self.ssim = QCheckBox("Measure quality after compressing (SSIM)")
        self.ssim.setChecked(True)
        self.ssim.setToolTip("Compares every copy with its original frame by frame and reports a quality score.")

        self.output = OutputFolder(config.default_export_dir() / "Compressed videos",
                                   lambda: self.lib.root if self.lib else None)
        self.summary = label("", "", wrap=True)
        self.summary.setStyleSheet("font-weight: 600;")
        self.summary_sub = label("", "small", wrap=True)
        self.compress_btn = button("Compress", "primary", self._compress)
        self.compress_btn.setMinimumHeight(34)

        settings = Card(vbox(label("Compression", "h2"), self.r_quality, self.quality_box, 4,
                             self.r_target, self.target_box, 6,
                             label("Maximum resolution", "muted"), self.resolution, 6,
                             self.ssim, spacing=8))
        out = Card(vbox(self.output, spacing=8))
        inner = QWidget()
        inner.setLayout(vbox(settings, out, None, spacing=12, margins=(0, 0, 10, 0)))
        sa = scroll(inner)
        sa.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # The main action stays visible below the (scrollable) settings.
        action = Card(vbox(self.summary, self.summary_sub, 4, self.compress_btn, spacing=6))
        column = QWidget()
        column.setLayout(vbox(sa, hbox(action, 10), spacing=12))
        column.setFixedWidth(350)
        return column

    # ---------------------------------------------------------------------------- data
    def shutdown(self) -> None:
        self._closed = True
        self._probe_queue.clear()
        self.prober.stop()

    def refresh(self) -> None:
        lib = self.lib
        self.output.check()
        rows: list[dict] = []
        if lib is not None:
            for r in lib.db.execute(
                    "SELECT id,rel_path,folder,name,size,duration,width,height FROM files "
                    "WHERE kind='video' AND error IS NULL ORDER BY COALESCE(taken_at, '') DESC,rel_path"):
                path = lib.abspath(r["rel_path"])
                rows.append({"key": str(path).lower(), "id": r["id"], "path": path, "name": r["name"],
                             "tip": r["rel_path"], "sub": r["folder"] or "Library folder", "size": r["size"], "duration": r["duration"],
                             "width": r["width"], "height": r["height"], "external": False})
        keys = {r["key"] for r in rows}
        self._external = [e for e in self._external if e["key"] not in keys]
        self._fill(rows + self._external)
        self._take_selection()

    def _take_selection(self) -> None:
        """Pick up videos sent from Photos & videos (ticked, ready to compress)."""
        if self.ctx.video_selection:
            paths = [Path(p) for p in self.ctx.video_selection]
            self.ctx.video_selection.clear()
            self._checked = set()
            self.add_external_files(paths)

    def showEvent(self, e) -> None:  # noqa: N802
        super().showEvent(e)
        if not self.stale:
            self._take_selection()

    def _fill(self, rows: list[dict]) -> None:
        self.model.beginResetModel()
        self._rows = rows
        self._row_of = {r["key"]: i for i, r in enumerate(rows)}
        self._checked &= set(self._row_of)
        self._info = {key: info for key, info in self._info.items() if key in self._row_of}
        self._estimates.clear()
        self.model.endResetModel()
        n = len(rows)
        self.count_label.setText(fmt_n(n, "video") if n else "")
        self.empty.setVisible(n == 0)
        self.table.setVisible(n > 0)
        self._settings_changed()

    # ---------------------------------------------------------------------------- selection
    def _toggle_row(self, index: QModelIndex) -> None:
        if index.column() == C_CHECK:
            return
        check = self.model.index(index.row(), C_CHECK)
        self.model.setData(check, Qt.CheckState.Unchecked if check.data(Qt.ItemDataRole.CheckStateRole) ==
                           Qt.CheckState.Checked else Qt.CheckState.Checked, Qt.ItemDataRole.CheckStateRole)

    def _check_all(self, value: bool) -> None:
        self._checked = set(self._row_of) if value else set()
        self._settings_changed()

    def checked_rows(self) -> list[dict]:
        return [r for r in self._rows if r["key"] in self._checked]

    def _add_external(self) -> None:
        exts = " ".join(f"*{e}" for e in sorted(config.VIDEO_EXT))
        files, _ = QFileDialog.getOpenFileNames(self, "Add videos", str(Path.home() / "Videos"),
                                                f"Videos ({exts});;All files (*)")
        self.add_external_files([Path(f) for f in files])

    def add_external_files(self, files: list[Path]) -> None:
        """Add videos that live outside the library (they are checked and probed right away)."""
        known, errors = set(self._row_of), []
        for f in files:
            key = str(f).lower()
            if key in known:
                self._checked.add(key)
                continue
            if not f.is_file():
                errors.append(f"{f.name}: file is unavailable")
                continue
            try:
                size = f.stat().st_size
            except OSError as error:
                errors.append(f"{f.name}: {error}")
                continue
            self._external.append({"key": key, "id": None, "path": f, "name": f.name, "tip": str(f),
                                   "sub": f"Outside the library · {f.parent}", "size": size,
                                   "duration": None, "width": None, "height": None, "external": True})
            self._checked.add(key)
            known.add(key)
        lib_rows = [r for r in self._rows if not r["external"]]
        self._fill(lib_rows + self._external)
        if errors:
            MessageDialog(self, "Some videos could not be added", "Check that the files and drive are available.",
                          "\n".join(errors[:200])).exec()

    # ---------------------------------------------------------------------------- probing / estimates
    def _probed(self, key: str, info: Optional[VideoInfo], img) -> None:
        if self._closed:
            return
        self._pending.discard(key)
        i = self._row_of.get(key)
        if i is None:
            self._queue_probes()
            self._update_summary()
            return
        self._info[key] = info
        r = self._rows[i]
        if info is not None and r["external"]:
            r.update(duration=info.duration, width=info.width, height=info.height)
        if img is not None and not img.isNull():
            r["thumb"] = QPixmap.fromImage(img)
        if key in self._checked:
            self._replace_estimate(r, self.settings())
        self.model.dataChanged.emit(self.model.index(i, C_THUMB), self.model.index(i, C_EST))
        self._queue_probes()
        self._update_summary()

    def settings(self) -> videotools.CompressSettings:
        return videotools.CompressSettings(
            mode="target" if self.r_target.isChecked() else "quality",
            quality=QUALITIES[max(0, self.quality.index())][1],
            target_mb=float(self.target.value()),
            max_height=self.resolution.currentData(),
            measure_quality=self.ssim.isChecked())

    def _mode_changed(self) -> None:
        self._settings_changed()

    def _chip(self, mb: int) -> None:
        self.r_target.setChecked(True)
        self.target.setValue(mb)

    def _settings_changed(self) -> None:
        s = self.settings()
        self.quality_note.setText(QUALITIES[max(0, self.quality.index())][2])
        for mb, b in self.chips:
            b.setChecked(s.mode == "target" and abs(s.target_mb - mb) < 0.5)
        self._estimates.clear()
        self._total_src = self._total_est = 0.0
        self._unknown = self._impossible = 0
        self._probe_queue.clear()
        for r in self.checked_rows():
            self._total_src += r["size"] or 0
            self._replace_estimate(r, s)
            if r["key"] not in self._info and r["key"] not in self._pending:
                self._probe_queue.append(r["key"])
        self._queue_probes()
        if self._rows:
            self.model.dataChanged.emit(self.model.index(0, C_CHECK),
                                        self.model.index(len(self._rows) - 1, C_EST))
        self._update_summary()

    def _queue_probes(self) -> None:
        while not self._closed and self._probe_queue and len(self._pending) < MAX_PENDING_PROBES:
            key = self._probe_queue.popleft()
            if key in self._checked and key in self._row_of and key not in self._info and key not in self._pending:
                row = self._rows[self._row_of[key]]
                self._pending.add(key)
                self.prober.request(key, row["path"], row["external"])

    def _estimate(self, row, settings) -> _Estimate:
        key = row["key"]
        if key not in self._info:
            return _Estimate("Checking…", color=theme.MUTED, unknown=1)
        info = self._info[key]
        if info is None:
            return _Estimate("Can't read", "FFmpeg could not read this video.", theme.DANGER, unknown=1)
        estimate = videotools.estimate(info, settings)
        if estimate.get("est_mb") is None:
            return _Estimate("Unknown", estimate["note"], theme.MUTED, unknown=1)
        size = estimate["est_mb"] * videotools.MB
        counted = min(size, row["size"] or size)
        if not estimate["feasible"]:
            return _Estimate(f"≈ {fmt_size(size)} · too small", estimate["note"], theme.WARN, counted, impossible=1)
        if settings.mode == "target" and row["size"] and row["size"] <= settings.target_mb * videotools.MB:
            return _Estimate(f"Already under {settings.target_mb:g} MB",
                             "This video already fits; a copy would not be smaller.", theme.MUTED, counted)
        if row["size"] and size >= row["size"] * .9:
            return _Estimate("Already compact", f"≈ {fmt_size(size)}. {estimate['note']}", theme.MUTED, counted)
        percent = f"  −{(1 - size / row['size']) * 100:.0f}%" if row["size"] else ""
        return _Estimate(f"≈ {fmt_size(size)}{percent}", estimate["note"], size=counted)

    def _replace_estimate(self, row, settings) -> None:
        key = row["key"]
        before = self._estimates.get(key, _Estimate())
        after = self._estimate(row, settings)
        self._estimates[key] = after
        self._total_est += after.size - before.size
        self._unknown += after.unknown - before.unknown
        self._impossible += after.impossible - before.impossible

    def _update_summary(self) -> None:
        n = len(self._checked)
        if not n:
            self.summary.setText("Tick the videos you want to compress.")
            self.summary_sub.setText("")
        else:
            text = f"{fmt_n(n, 'video')} · {fmt_size(self._total_src)}"
            if self._total_est and not self._unknown:
                text += f" → about {fmt_size(self._total_est)}"
            self.summary.setText(text)
            sub = []
            if self._unknown:
                sub.append("Working out the estimate…" if self._pending & self._checked or self._probe_queue else
                           f"{fmt_n(self._unknown, 'video')} could not be estimated.")
            if self._impossible:
                sub.append(f"The size limit is too small for {fmt_n(self._impossible, 'video')}; "
                           "they will be as small as possible while staying watchable.")
            if not sub:
                sub.append("Estimates are approximate; the result depends on the footage.")
            self.summary_sub.setText(" ".join(sub))
        self.compress_btn.setText(f"Compress {fmt_n(n, 'video')}" if n else "Compress")
        self.compress_btn.setEnabled(n > 0 and not self.busy)

    # ---------------------------------------------------------------------------- compress
    def on_busy_changed(self, busy: bool) -> None:
        self.compress_btn.setEnabled(not busy and bool(self._checked))

    def _compress(self) -> None:
        rows = self.checked_rows()
        if not rows:
            return
        out = self.output.path()
        if self.lib is not None and _inside(out, config.app_dir(self.lib.root)):
            MessageDialog(self, "Choose another folder",
                          "That folder belongs to Memoria's own catalogue. Please pick a normal folder.").exec()
            return
        files = [r["path"] for r in rows]
        settings = self.settings()
        from ...engine import actions
        lib = self.lib

        def work(progress):
            with actions.created_batch(lib, "video", "Compress videos"):
                return videotools.compress_many(files, out, settings, progress)

        def cancelled():
            self.ctx.library_modified.emit()
            self.ctx.toast_requested.emit("Compression stopped. Videos that had already finished were kept "
                                          f"in {out}.", "")

        if not self.run(f"Compressing {fmt_n(len(files), 'video')}", work, self._show_results, cancelled,
                        notify_success=False):
            self.ctx.toast_requested.emit("Another task is still running. Try again when it has finished.", "")

    def _show_results(self, results: list[videotools.CompressResult]) -> None:
        self.ctx.library_modified.emit()
        self._results = list(results)
        t = self.results
        t.setRowCount(len(results))
        ok = [r for r in results if r.ok]
        for i, r in enumerate(results):
            def cell(col, text, color=None, tip="", right=False):
                it = QTableWidgetItem(text)
                it.setToolTip(tip or text)
                if color:
                    it.setForeground(QColor(color))
                if right:
                    it.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                t.setItem(i, col, it)
            cell(R_NAME, r.src.name, tip=str(r.dst or r.src))
            if r.ok:
                cell(R_SIZES, f"{fmt_size(r.src_bytes)} → {fmt_size(r.dst_bytes)}")
                cell(R_SAVED, f"{r.saved_pct:.0f}%", theme.OK, right=True)
                cell(R_QUALITY, f"{r.ssim:.3f} · {quality_label(r.ssim)}" if r.ssim is not None else "Not measured",
                     None if r.ssim is None or r.ssim >= 0.9 else theme.WARN,
                     tip="SSIM compares the copy with the original: 1.000 means identical.")
                cell(R_STATUS, "✓ Saved", theme.OK, tip=f"{r.dst.name}\n{r.message}")
            else:
                cell(R_SIZES, fmt_size(r.src_bytes))
                cell(R_SAVED, "—", right=True)
                cell(R_QUALITY, "")
                cell(R_STATUS, r.message, theme.WARN)
        src_total = sum(r.src_bytes for r in ok)
        dst_total = sum(r.dst_bytes for r in ok)
        if ok:
            msg = (f"Compressed {fmt_n(len(ok), 'video')}: {fmt_size(src_total)} → {fmt_size(dst_total)} "
                   f"(saved {(1 - dst_total / src_total) * 100:.0f}%).")
        else:
            msg = "No compressed copies were made."
        failed = len(results) - len(ok)
        if failed:
            msg += f" {fmt_n(failed, 'video')} kept as original only — see Result."
        self.results_summary.setText(msg + " Double-click a row to show the file.")
        self.results_card.show()
        self.ctx.toast_requested.emit(msg, "")
        self.ctx.notification_requested.emit("operation_partial" if failed else "compression_complete",
                                              failed if failed else len(ok))

    def _show_result(self) -> None:
        rows = {i.row() for i in self.results.selectedItems()}
        if not rows:
            return
        r = self._results[min(rows)]
        target = r.dst if r.dst and r.dst.exists() else r.src
        show_in_explorer(target)
