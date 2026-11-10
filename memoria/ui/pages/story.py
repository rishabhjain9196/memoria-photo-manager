"""Story maker: Instagram stories, carousels and story videos made from library photos."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from PySide6.QtCore import QEvent, QObject, QRectF, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QIcon, QImage, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import (QAbstractItemView, QButtonGroup, QCheckBox, QComboBox, QDoubleSpinBox,
                               QFileDialog, QFormLayout, QFrame, QLabel, QLineEdit, QListView, QListWidget,
                               QListWidgetItem, QPushButton, QSizePolicy, QWidget)

from ...engine import config, story
from .. import theme
from ..tasks import LatestCall
from ..widgets import (Banner, Card, MessageDialog, PhotoGrid, button, fmt_date, fmt_n, hbox, label, open_path,
                       scroll, show_in_explorer, vbox)
from .base import Page


# ------------------------------------------------------------------------------ shared small widgets
# (VideoPage imports Segmented, ElidedLabel and OutputFolder from here.)

class Segmented(QFrame):
    """Windows-11 style segmented control. ``changed`` emits the selected index."""
    changed = Signal(int)

    def __init__(self, options: list[str], index: int = 0, parent=None):
        super().__init__(parent)
        self.setObjectName("segmented")
        self.setStyleSheet(
            f"#segmented {{ background: {theme.SEGMENT_BG}; border-radius: 8px; }}"
            f"#segmented QPushButton {{ background: transparent; border: 1px solid transparent; border-radius: 6px;"
            f" padding: 5px 10px; color: {theme.MUTED}; }}"
            f"#segmented QPushButton:hover {{ color: {theme.TEXT}; }}"
            f"#segmented QPushButton:checked {{ background: {theme.CARD}; border: 1px solid {theme.SEGMENT_BORDER};"
            f" color: {theme.TEXT}; font-weight: 600; }}")
        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        lay = hbox(spacing=2, margins=(3, 3, 3, 3))
        for i, text in enumerate(options):
            b = QPushButton(text)
            b.setCheckable(True)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            self.group.addButton(b, i)
            lay.addWidget(b)
        self.setLayout(lay)
        self.group.button(index).setChecked(True)
        self.group.idClicked.connect(self.changed)

    def index(self) -> int:
        return self.group.checkedId()

    def set_index(self, i: int) -> None:
        self.group.button(i).setChecked(True)
        self.changed.emit(i)


class ElidedLabel(QLabel):
    """Single-line label that elides long text (paths) in the middle."""

    def __init__(self, text: str = "", obj: str = ""):
        super().__init__()
        if obj:
            self.setObjectName(obj)
        self._full = text
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.setText(text)

    def setText(self, text: str) -> None:  # noqa: N802 - Qt naming
        self._full = text
        self.setToolTip(text)
        self._elide()

    def full_text(self) -> str:
        return self._full

    def resizeEvent(self, e) -> None:  # noqa: N802
        super().resizeEvent(e)
        self._elide()

    def _elide(self) -> None:
        w = max(20, self.width() - 2)
        super().setText(self.fontMetrics().elidedText(self._full, Qt.TextElideMode.ElideMiddle, w))


def _inside(path: Path, root: Path) -> bool:
    try:
        Path(path).resolve().relative_to(Path(root).resolve())
        return True
    except (ValueError, OSError):
        return False


class OutputFolder(QWidget):
    """"Save to" row: shows the folder, lets the user change/open it, warns about library folders."""
    changed = Signal(object)

    def __init__(self, default: Path, library_root: Callable[[], Optional[Path]], parent=None):
        super().__init__(parent)
        self._root = library_root
        self._path = Path(default)
        self.path_label = ElidedLabel(str(self._path))
        self.path_label.setMinimumWidth(80)
        change = button("Change…", on_click=self._choose, tip="Choose where new files are saved")
        self.open_btn = button("Open folder", "link", self.open_folder)
        self.warn = Banner("", "warn")
        self.warn.hide()
        lay = vbox(hbox(label("Save to", "muted"), None, self.open_btn),
                   hbox(self.path_label, change, spacing=8), self.warn, spacing=4)
        self.setLayout(lay)

    def path(self) -> Path:
        return self._path

    def set_path(self, p: Path) -> None:
        self._path = Path(p)
        self.path_label.setText(str(self._path))
        self.check()
        self.changed.emit(self._path)

    def check(self) -> None:
        root = self._root()
        inside = root is not None and _inside(self._path, root)
        self.warn.setText("This folder is inside your library, so the new files will be added to it "
                          "the next time the library is scanned.")
        self.warn.setVisible(inside)

    def _choose(self) -> None:
        start = str(self._path if self._path.exists() else self._path.parent)
        chosen = QFileDialog.getExistingDirectory(self, "Choose where to save", start)
        if not chosen:
            return
        root = self._root()
        if root is not None and _inside(Path(chosen), config.app_dir(root)):
            MessageDialog(self, "Choose another folder",
                          "That folder belongs to Memoria's own catalogue. Please pick a normal folder.").exec()
            return
        self.set_path(Path(chosen))

    def open_folder(self) -> None:
        try:
            self._path.mkdir(parents=True, exist_ok=True)
        except OSError:
            return
        open_path(self._path)


class _BackgroundRenderer(QObject):
    """Bounded latest-only rendering with an owned, waitable worker lifetime."""
    ready = Signal(int, object, str)  # generation, QImage | None, note-or-error

    def __init__(self, parent=None):
        super().__init__(parent)
        self._alive = True
        self._call = LatestCall(self)
        self._call.result.connect(lambda value: self.ready.emit(*value))

    def request(self, generation: int, fn: Callable[[], tuple]) -> None:
        if not self._alive:
            return
        def work():
            try:
                img, note = fn()
                rgb = img.convert("RGB")
                try:
                    image = QImage(rgb.tobytes(), rgb.width, rgb.height, rgb.width * 3,
                                   QImage.Format.Format_RGB888).copy()
                finally:
                    rgb.close()
                    img.close()
                return generation, image, note
            except Exception as error:
                return generation, None, f"Can't preview: {error}"
        self._call.call(work)

    def stop(self) -> None:
        self._alive = False
        self._call.wait()

    def invalidate(self):
        self._call.invalidate()

    @property
    def running(self):
        return self._call.running


def square_icon(pm: Optional[QPixmap], side: int) -> QIcon:
    out = QPixmap(side, side)
    out.fill(Qt.GlobalColor.transparent)
    if pm is not None and not pm.isNull():
        scaled = pm.scaled(side, side, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                           Qt.TransformationMode.SmoothTransformation)
        p = QPainter(out)
        p.drawPixmap((side - scaled.width()) // 2, (side - scaled.height()) // 2, scaled)
        p.end()
    return QIcon(out)


# ------------------------------------------------------------------------------ page
MODES = ("Story images", "Carousel", "Story video")
BACKGROUNDS = [("Blurred photo", "blur"), ("Black", "black"), ("White", "white")]
FITS = [("Show whole photo", "fit"), ("Fill frame", "fill")]
SHAPES = [("Portrait 4:5", story.POST), ("Square 1:1", story.SQUARE)]
PREVIEW_W, PREVIEW_H = 270, 480
_ICON = 64
_CELL = 118


class _PreviewLabel(QLabel):
    """Keeps the last rendered image and rescales it to whatever room the page has (max 270×480)."""

    def __init__(self):
        super().__init__()
        self._img: Optional[QImage] = None
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWordWrap(True)
        self.setMinimumSize(170, 302)
        self.setMaximumSize(PREVIEW_W, PREVIEW_H)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._message_style = f"background: {theme.SUBTLE}; border-radius: 10px; color: {theme.MUTED}; padding: 12px;"
        self.setStyleSheet(self._message_style)

    def has_image(self) -> bool:
        return self._img is not None

    def set_message(self, text: str) -> None:
        self._img = None
        self.setStyleSheet(self._message_style)
        self.setPixmap(QPixmap())
        self.setText(text)

    def set_image(self, img: QImage) -> None:
        self._img = img
        self.setStyleSheet("background: transparent;")
        self.setText("")
        self._rescale()

    def resizeEvent(self, e) -> None:  # noqa: N802
        super().resizeEvent(e)
        self._rescale()

    def _rescale(self) -> None:
        if self._img is None:
            return
        dpr = self.devicePixelRatioF()
        r = self.contentsRect()
        w, h = max(1, r.width()), max(1, r.height())
        img = self._img.scaled(int(w * dpr), int(h * dpr), Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)
        # Rounded "phone screen" frame so white backgrounds stay visible on the white card.
        pm = QPixmap(img.size())
        pm.fill(Qt.GlobalColor.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        rect = QRectF(0.5, 0.5, img.width() - 1, img.height() - 1)
        radius = 8 * dpr
        path.addRoundedRect(rect, radius, radius)
        p.setClipPath(path)
        p.drawImage(0, 0, img)
        p.setClipping(False)
        p.setPen(QPen(QColor(theme.INPUT_BORDER), dpr))
        p.drawPath(path)
        p.end()
        pm.setDevicePixelRatio(dpr)
        self.setPixmap(pm)


class StoryPage(Page):
    title = "Story maker"
    subtitle = "Turn photos into Instagram stories, carousels and story videos"
    glyph = "\uE786"

    def __init__(self, ctx):
        super().__init__(ctx)
        self._all: list[dict] = []
        self._by_id: dict[int, dict] = {}
        self._music: Optional[Path] = None
        self._last_outputs: list[Path] = []
        self._generation = 0
        self._syncing = False
        self._closed = False
        self._preview_library = None
        self._picker_offset = 0
        self.catalogue_bg = LatestCall(self)
        self.catalogue_bg.result.connect(self._catalogue_loaded)
        self.catalogue_bg.failed.connect(lambda error: self.picker_count.setText(f"Could not load photos: {error}"))

        self.renderer = _BackgroundRenderer(self)
        self.renderer.ready.connect(self._preview_ready)
        self.destroyed.connect(self.renderer.stop)
        self.preview_timer = QTimer(self)
        self.preview_timer.setSingleShot(True)
        self.preview_timer.setInterval(250)
        self.preview_timer.timeout.connect(self._render_preview)

        self.body.addLayout(hbox(self._build_picker(), self._build_options(), self._build_preview(), spacing=14),
                            1)
        self._mode_changed(0)

    def shutdown(self):
        self._closed = True
        self.preview_timer.stop()
        self.renderer.stop()
        self.catalogue_bg.wait()

    def _mark_stale(self):
        self._generation += 1
        self.renderer.invalidate()
        self.catalogue_bg.invalidate()
        self.preview_timer.stop()
        self.preview.set_message("Library changed. Updating the story…")
        super()._mark_stale()

    # ---------------------------------------------------------------------------- building
    def _build_picker(self) -> QWidget:
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search by name or folder")
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self._apply_filter)
        self.month = QComboBox()
        self.month.setMinimumWidth(130)
        self.month.currentIndexChanged.connect(self._apply_filter)
        self.grid = PhotoGrid(self.ctx.thumbs, cell=_CELL, captions=1)
        self.grid.model_.checked_changed.connect(self._grid_checked)
        self.grid.activated_item.connect(self._toggle_item)
        self.grid.viewport().installEventFilter(self)
        self.picker_count = label("", "small")
        self.picker_previous = button("Previous", on_click=lambda: self._picker_step(-1))
        self.picker_next = button("Next", on_click=lambda: self._picker_step(1))
        self.picker_empty = label("No photos match.", "muted")
        self.picker_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.picker_empty.hide()
        lay = vbox(hbox(label("Photos", "h2"), None, self.picker_count),
                   hbox(self.search, self.month),
                   self.grid, self.picker_empty,
                   hbox(self.picker_previous, self.picker_next, None), spacing=10)
        lay.setStretchFactor(self.grid, 1)
        card = Card(lay)
        card.setMinimumWidth(300)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        return card

    def _build_options(self) -> QWidget:
        # selected strip
        self.strip = QListWidget()
        self.strip.setViewMode(QListView.ViewMode.IconMode)
        self.strip.setFlow(QListView.Flow.LeftToRight)
        self.strip.setWrapping(True)
        self.strip.setResizeMode(QListView.ResizeMode.Adjust)
        self.strip.setMovement(QListView.Movement.Snap)
        self.strip.setIconSize(QSize(_ICON, _ICON))
        self.strip.setGridSize(QSize(_ICON + 8, _ICON + 8))
        self.strip.setSpacing(0)
        self.strip.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.strip.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.strip.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.strip.setFixedHeight(2 * (_ICON + 8) + 8)
        self.strip.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        m = self.strip.model()
        for sig in (m.rowsMoved, m.rowsInserted, m.rowsRemoved):
            sig.connect(self._selection_changed)
        self.strip.itemSelectionChanged.connect(self._update_strip_buttons)
        self.sel_title = label("Selected", "h2")
        self.remove_btn = button("Remove", on_click=self._remove_selected, tip="Remove the highlighted photos")
        self.clear_btn = button("Clear", "link", self._clear_selection)
        self.strip_hint = label("Tick photos on the left. Drag here to change the order.", "small", wrap=True)

        # output kind + options
        self.mode_seg = Segmented(list(MODES))
        self.mode_seg.changed.connect(self._mode_changed)

        self.template = QComboBox()
        for tid, text in story.TEMPLATES.items():
            self.template.addItem(text, tid)
        self.shape = QComboBox()
        for text, size in SHAPES:
            self.shape.addItem(text, size)
        self.background = QComboBox()
        for text, val in BACKGROUNDS:
            self.background.addItem(text, val)
        self.fit = QComboBox()
        for text, val in FITS:
            self.fit.addItem(text, val)
        self.caption = QLineEdit()
        self.caption.setPlaceholderText("Optional text")
        self.caption.setMaxLength(160)
        self.caption_pos = QComboBox()
        self.caption_pos.addItem("Bottom", "bottom")
        self.caption_pos.addItem("Top", "top")
        self.panorama = QCheckBox("Split into seamless slides")
        self.spp = QDoubleSpinBox()
        self.spp.setRange(1.0, 15.0)
        self.spp.setSingleStep(0.5)
        self.spp.setValue(3.0)
        self.spp.setSuffix(" s")
        self.transition = QDoubleSpinBox()
        self.transition.setRange(0.0, 2.0)
        self.transition.setSingleStep(0.1)
        self.transition.setValue(0.6)
        self.transition.setSuffix(" s")
        self.ken_burns = QCheckBox("Slow zoom (Ken Burns)")
        self.ken_burns.setChecked(True)
        self.music_label = ElidedLabel("No music", "muted")
        self.music_btn = button("Choose…", on_click=self._choose_music)
        self.music_clear = button("Remove", "link", self._clear_music)
        self.music_clear.hide()
        self.music_row = music_row = QWidget()
        music_row.setLayout(hbox(self.music_label, self.music_btn, self.music_clear, spacing=6))

        self.form = QFormLayout()
        self.form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.form.setHorizontalSpacing(10)
        self.form.setVerticalSpacing(8)
        self.form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.form.addRow("Layout", self.template)
        self.form.addRow("Slide shape", self.shape)
        self.form.addRow("Panorama", self.panorama)
        self.form.addRow("Background", self.background)
        self.form.addRow("Photo", self.fit)
        self.form.addRow("Caption", self.caption)
        self.form.addRow("Position", self.caption_pos)
        self.form.addRow("Each photo", self.spp)
        self.form.addRow("Crossfade", self.transition)
        self.form.addRow("", self.ken_burns)
        self.form.addRow("Music", music_row)

        for w in (self.template, self.shape, self.background, self.fit, self.caption_pos):
            w.currentIndexChanged.connect(self._options_changed)
        for w in (self.panorama, self.ken_burns):
            w.toggled.connect(self._options_changed)
        for w in (self.spp, self.transition):
            w.valueChanged.connect(self._options_changed)
        self.caption.textChanged.connect(self._options_changed)

        default = config.default_export_dir() / "Stories"
        self.output = OutputFolder(default, lambda: self.lib.root if self.lib else None)
        self.summary = label("", "", wrap=True)
        self.summary.setStyleSheet("font-weight: 600;")
        self.export_btn = button("Export", "primary", self._export)
        self.export_btn.setMinimumHeight(34)
        self.result_label = label("", "small", wrap=True)
        self.show_btn = button("Show files", "link", self._show_outputs)
        self.show_btn.hide()

        sel_card = Card(vbox(hbox(self.sel_title, None, self.remove_btn, self.clear_btn, spacing=6),
                             self.strip, self.strip_hint, spacing=8))
        opt_card = Card(vbox(label("Make", "h2"), self.mode_seg, 4, self.form, spacing=8))
        out_card = Card(vbox(self.output, spacing=8))
        inner = QWidget()
        inner.setLayout(vbox(sel_card, opt_card, out_card, None, spacing=12, margins=(0, 0, 10, 0)))
        sa = scroll(inner)
        sa.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        sa.setFixedWidth(366)
        return sa

    def _build_preview(self) -> QWidget:
        self.preview = _PreviewLabel()
        self.preview_note = label("", "small")
        lay = vbox(hbox(label("Preview", "h2"), None, self.preview_note),
                   self.preview, 4,
                   self.summary, self.export_btn,
                   hbox(self.result_label, self.show_btn, spacing=4), spacing=8)
        lay.setStretchFactor(self.preview, 1)
        card = Card(lay)
        card.setFixedWidth(PREVIEW_W + 34)
        return card

    def eventFilter(self, obj, event) -> bool:  # noqa: N802
        if event.type() == QEvent.Type.Resize and obj is self.grid.viewport():
            self._fit_grid_cells()
        return super().eventFilter(obj, event)

    def _fit_grid_cells(self) -> None:
        """Stretch picker cells so the columns fill the width instead of leaving a gap."""
        avail = self.grid.viewport().width() - 2 * self.grid.spacing()
        cols = max(1, avail // (_CELL + 2 * self.grid.spacing()))
        cell = max(_CELL, avail // cols - 2 * self.grid.spacing())
        if cell != self.grid.delegate.cell:
            self.grid.delegate.cell = cell
            self.grid.doItemsLayout()

    # ---------------------------------------------------------------------------- data
    def refresh(self) -> None:
        lib = self.lib
        self.output.check()
        if lib is None:
            self._all, self._by_id = [], {}
            self._set_strip([])
            self._apply_filter()
            return
        generation = self.ctx.generation
        self.picker_count.setText("Reading photos…")
        def work():
            try:
                rows = lib.db.execute("SELECT id,name,rel_path,folder,taken_at FROM files "
                                      "WHERE kind='image' AND error IS NULL "
                                      "ORDER BY COALESCE(taken_at,'') DESC,rel_path")
                items = [{
                    "id": r["id"], "caption": r["name"], "rel_path": r["rel_path"], "kind": "image",
                    "folder": r["folder"] or "", "month": (r["taken_at"] or "")[:7],
                    "sub": fmt_date(r["taken_at"]) if r["taken_at"] else "", "checked": False,
                    "tip": lib.display_path(r["rel_path"]),
                } for r in rows]
                return lib, generation, items
            finally:
                lib.close_thread()
        self.catalogue_bg.call(work)

    def _catalogue_loaded(self, result):
        lib, generation, items = result
        if self._closed or (lib, generation) != (self.lib, self.ctx.generation):
            return
        selected = self.selected_ids()
        self._all = items
        self._by_id = {it["id"]: it for it in self._all}
        # rebuild the strip: keep the user's order, drop files that disappeared, then add new picks
        ids = [i for i in selected if i in self._by_id]
        for fid in self.ctx.story_selection:
            if fid in self._by_id and fid not in ids:
                ids.append(fid)
        self.ctx.story_selection.clear()
        chosen = set(ids)
        for it in self._all:
            it["checked"] = it["id"] in chosen
        self._fill_months()
        self._set_strip(ids)
        self._apply_filter()

    def _fill_months(self) -> None:
        current = self.month.currentData()
        months = sorted({it["month"] for it in self._all if it["month"]}, reverse=True)
        self.month.blockSignals(True)
        self.month.clear()
        self.month.addItem("All dates", None)
        for m in months:
            try:
                text = datetime.strptime(m, "%Y-%m").strftime("%B %Y")
            except ValueError:
                text = m
            self.month.addItem(text, m)
        if any(not it["month"] for it in self._all):
            self.month.addItem("No date", "")
        idx = self.month.findData(current)
        self.month.setCurrentIndex(max(0, idx))
        self.month.blockSignals(False)

    def _apply_filter(self, reset=True) -> None:
        if reset is not False:
            self._picker_offset = 0
        q = self.search.text().strip().lower()
        month = self.month.currentData()
        items = [it for it in self._all
                 if (not q or q in it["caption"].lower() or q in it["folder"].lower())
                 and (month is None or it["month"] == month)]
        self._picker_offset = min(self._picker_offset, max(0, (len(items) - 1) // 500) * 500)
        visible = items[self._picker_offset:self._picker_offset + 500]
        self.grid.set_items(visible)
        total = len(self._all)
        end = self._picker_offset + len(visible)
        self.picker_count.setText(f"{self._picker_offset + 1 if visible else 0:,}–{end:,} of "
                                  f"{len(items):,} matching photos · selections persist across pages")
        self.picker_previous.setEnabled(self._picker_offset > 0)
        self.picker_next.setEnabled(end < len(items))
        self.picker_empty.setText("No photos in this library yet." if not total else "No photos match.")
        self.picker_empty.setVisible(not items)
        self.grid.setVisible(bool(items))

    def _picker_step(self, delta):
        self._picker_offset = max(0, self._picker_offset + delta * 500)
        self._apply_filter(False)

    def showEvent(self, e) -> None:  # noqa: N802
        super().showEvent(e)  # refreshes first if the library changed
        if self.ctx.story_selection and not self.catalogue_bg.running:
            ids = list(self.ctx.story_selection)
            self.ctx.story_selection.clear()
            self.add_ids(ids)

    # ---------------------------------------------------------------------------- selection
    def selected_ids(self) -> list[int]:
        return [self.strip.item(i).data(Qt.ItemDataRole.UserRole) for i in range(self.strip.count())]

    def selected_paths(self) -> list[Path]:
        lib = self.lib
        if lib is None:
            return []
        return [lib.abspath(self._by_id[i]["rel_path"]) for i in self.selected_ids() if i in self._by_id]

    def add_ids(self, ids: list[int]) -> None:
        """Append library photos to the selection (used by refresh and external callers)."""
        if self.catalogue_bg.running and not self._by_id:
            self.ctx.story_selection.extend(i for i in ids if i not in self.ctx.story_selection)
            return
        current = self.selected_ids()
        new = [i for i in ids if i in self._by_id and i not in current]
        for i in new:
            self._by_id[i]["checked"] = True
        self._set_strip(current + new)
        self.grid.viewport().update()

    def _make_strip_item(self, fid: int) -> QListWidgetItem:
        it = self._by_id[fid]
        item = QListWidgetItem(square_icon(self.ctx.thumbs.get(fid), _ICON), "")
        item.setData(Qt.ItemDataRole.UserRole, fid)
        item.setToolTip(it["rel_path"])
        item.setSizeHint(QSize(_ICON + 8, _ICON + 8))
        item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsDragEnabled)
        return item

    def _set_strip(self, ids: list[int]) -> None:
        self._syncing = True
        self.strip.clear()
        for fid in ids:
            self.strip.addItem(self._make_strip_item(fid))
        self._syncing = False
        self._selection_changed()

    def _grid_checked(self) -> None:
        if self._syncing:
            return
        current = self.selected_ids()
        visible = self.grid.items()
        add = [it["id"] for it in visible if it.get("checked") and it["id"] not in current]
        drop = {it["id"] for it in visible if not it.get("checked") and it["id"] in current}
        if add or drop:
            self._set_strip([i for i in current if i not in drop] + add)

    def _toggle_item(self, item: dict) -> None:
        for row, it in enumerate(self.grid.items()):
            if it is item:
                self.grid.model_.toggle(row)
                return

    def _remove_selected(self) -> None:
        rows = sorted({self.strip.row(i) for i in self.strip.selectedItems()})
        if not rows:
            return
        ids = self.selected_ids()
        keep = [fid for r, fid in enumerate(ids) if r not in rows]
        for r in rows:
            self._by_id[ids[r]]["checked"] = False
        self._set_strip(keep)
        self.grid.viewport().update()

    def _clear_selection(self) -> None:
        for it in self._all:
            it["checked"] = False
        self._set_strip([])
        self.grid.viewport().update()

    def keyPressEvent(self, e) -> None:  # noqa: N802
        if e.key() == Qt.Key.Key_Delete and self.strip.hasFocus():
            self._remove_selected()
            return
        super().keyPressEvent(e)

    def _update_strip_buttons(self) -> None:
        self.remove_btn.setEnabled(bool(self.strip.selectedItems()))

    def _selection_changed(self, *args) -> None:
        if self._syncing:
            return
        n = self.strip.count()
        self.sel_title.setText(f"Selected ({n})" if n else "Selected")
        self.clear_btn.setVisible(n > 0)
        self.strip_hint.setText("Drag photos here to change the order." if n > 1 else
                                "Tick photos on the left to add them here.")
        self._update_strip_buttons()
        self._options_changed()

    # ---------------------------------------------------------------------------- options
    def _mode_changed(self, mode: int) -> None:
        for w in (self.template,):
            self.form.setRowVisible(w, mode == 0)
        for w in (self.shape, self.panorama):
            self.form.setRowVisible(w, mode == 1)
        for w in (self.spp, self.transition, self.ken_burns, self.music_row):
            self.form.setRowVisible(w, mode == 2)
        self.result_label.setText("")
        self.show_btn.hide()
        self.output.check()
        self._options_changed()

    def style_options(self) -> story.StyleOptions:
        return story.StyleOptions(background=self.background.currentData(), fit=self.fit.currentData(),
                                  caption=self.caption.text().strip(),
                                  caption_position=self.caption_pos.currentData())

    def _plan(self) -> tuple[int, str]:
        """(number of outputs, human summary) for the current selection and options."""
        n = self.strip.count()
        mode = self.mode_seg.index()
        if n == 0:
            return 0, "Pick photos to get started."
        if mode == 0:
            tid = self.template.currentData()
            slots = story.template_slots(tid)
            k = -(-n // slots)
            text = f"{fmt_n(n, 'photo')} → {fmt_n(k, 'story', 'stories')}"
            if slots > 1:
                text += f" ({self.template.currentText().lower()})"
                if n % slots:
                    text += f"; the last one uses {fmt_n(n % slots, 'photo')}"
            return k, text
        if mode == 1:
            if self.panorama.isChecked() and n == 1:
                k = self._panorama_count()
                return k, (f"1 wide photo → {k} seamless slides" if k else "1 wide photo → seamless slides")
            return n, f"{fmt_n(n, 'photo')} → {fmt_n(n, 'carousel slide')}"
        secs = story.story_video_duration(n, self.spp.value(), self.transition.value())
        return 1, f"{fmt_n(n, 'photo')} → one {secs:.0f} s story video"

    def _panorama_count(self) -> int:
        ids = self.selected_ids()
        it = self._by_id.get(ids[0]) if ids else None
        row = self.lib.file(ids[0]) if (it and self.lib) else None
        if row is None or not row["width"] or not row["height"]:
            return 0
        return story.panorama_slide_count(row["width"], row["height"], self.shape.currentData())

    def _options_changed(self, *args) -> None:
        self._generation += 1
        self.renderer.invalidate()
        n = self.strip.count()
        mode = self.mode_seg.index()
        self.panorama.setEnabled(n == 1)
        if n != 1 and self.panorama.isChecked():
            self.panorama.blockSignals(True)
            self.panorama.setChecked(False)
            self.panorama.blockSignals(False)
        self.panorama.setToolTip("" if n == 1 else "Available when exactly one photo is selected")
        _, text = self._plan()
        self.summary.setText(text)
        self.export_btn.setText(("Export stories", "Export carousel", "Make video")[mode])
        self.export_btn.setEnabled(n > 0 and not self.busy)
        self.preview_timer.start()

    def _choose_music(self) -> None:
        f, _ = QFileDialog.getOpenFileName(self, "Choose music", str(Path.home() / "Music"),
                                           "Audio (*.mp3 *.m4a *.aac *.wav *.flac *.ogg *.opus *.wma);;All files (*)")
        if f:
            self._music = Path(f)
            self.music_label.setText(self._music.name)
            self.music_label.setObjectName("")
            self.music_label.setStyleSheet("")
            self.music_clear.show()

    def _clear_music(self) -> None:
        self._music = None
        self.music_label.setText("No music")
        self.music_clear.hide()

    # ---------------------------------------------------------------------------- preview
    def _render_preview(self) -> None:
        if self._closed:
            return
        paths = self.selected_paths()
        self._generation += 1
        if not paths:
            self.preview.set_message("Pick photos to see a preview")
            self.preview_note.setText("")
            return
        mode = self.mode_seg.index()
        style = self.style_options()
        half = lambda s: (s[0] // 2, s[1] // 2)  # noqa: E731 - previews render at half size (same look)
        if mode == 0:
            tid = self.template.currentData()
            slots = story.template_slots(tid)
            total = -(-len(paths) // slots)
            group = paths[:slots]
            fn = lambda: (story.render_story(group, tid, style, half(story.STORY)),  # noqa: E731
                          f"Story 1 of {total}")
        elif mode == 1:
            size = self.shape.currentData()
            if self.panorama.isChecked() and len(paths) == 1:
                def fn(p=paths[0]):
                    slides = story.render_carousel([p], style, half(size), panorama=True)
                    return slides[0], f"Slide 1 of {len(slides)}"
            else:
                fn = lambda p=paths[0], n=len(paths): (  # noqa: E731
                    story.render_story([p], "single", style, half(size)), f"Slide 1 of {n}")
        else:
            fn = lambda p=paths[0]: (story.render_story([p], "single", style, half(story.STORY)),  # noqa: E731
                                     "First frame")
        if not self.preview.has_image():
            self.preview.set_message("Rendering preview…")
        lib, generation = self.lib, self.ctx.generation
        self._preview_library = (lib, generation)
        inputs = group if mode == 0 else paths[:1]
        render = fn
        def guarded_render():
            try:
                if lib is not None:
                    if lib._lock_key is None:
                        raise RuntimeError("The source library is closed.")
                    for path in inputs:
                        lib.check_path(path)
                return render()
            finally:
                if lib is not None:
                    lib.close_thread()
        self.renderer.request(self._generation, guarded_render)

    def _preview_ready(self, generation: int, qimg, note: str) -> None:
        if self._closed or generation != self._generation or self._preview_library != (self.lib, self.ctx.generation):
            return
        if qimg is None:
            self.preview.set_message(note)
            self.preview_note.setText("")
            return
        self.preview.set_image(qimg)
        self.preview_note.setText(note)

    # ---------------------------------------------------------------------------- export
    def on_busy_changed(self, busy: bool) -> None:
        self.export_btn.setEnabled(not busy and self.strip.count() > 0)

    def _export(self) -> None:
        paths = self.selected_paths()
        if not paths:
            return
        out = self.output.path()
        if self.lib is not None and self.lib.in_app_storage(out):
            MessageDialog(self, "Choose another folder",
                          "That folder belongs to Memoria's own catalogue. Please pick a normal folder.").exec()
            return
        mode = self.mode_seg.index()
        style = self.style_options()
        if mode == 0:
            tid = self.template.currentData()
            title = "Making stories"

            def work(p):
                return story.export_stories(paths, tid, style, out, story.STORY, p)

            def message(res):
                return f"Saved {fmt_n(len(res), 'story', 'stories')} to {out}"
        elif mode == 1:
            size, pano = self.shape.currentData(), self.panorama.isChecked() and len(paths) == 1
            title = "Making carousel"

            def work(p):
                return story.export_carousel(paths, style, out, size, pano, p)

            def message(res):
                return f"Saved {fmt_n(len(res), 'carousel slide')} to {out}"
        else:
            spp, tr, kb, music = self.spp.value(), self.transition.value(), self.ken_burns.isChecked(), self._music
            title = "Making story video"

            def work(p):
                return [story.make_story_video(paths, out, spp, tr, kb, style, story.STORY, 30, music, p)]

            def message(res):
                return f"Saved “{res[0].name}” to {out}"

        def done(res):
            self._last_outputs = list(res)
            msg = message(res)
            self.result_label.setText(msg.replace(str(out), f"“{out.name}”"))
            self.show_btn.setVisible(bool(res))
            self.ctx.library_modified.emit()
            self.ctx.toast_requested.emit(msg, created[0].batch_id if created[0] and created[0].done else "")
            self.ctx.notification_requested.emit("story_complete", len(res))

        def cancelled():
            self.result_label.setText("Stopped. Nothing was saved.")
            self.show_btn.hide()
            self.ctx.library_modified.emit()

        self.result_label.setText("")
        self.show_btn.hide()
        from ...engine import actions
        lib = self.lib
        created = [None]
        export = work
        inputs = paths + ([self._music] if mode == 2 and self._music is not None else [])

        def journaled_work(prog):
            try:
                if lib is not None:
                    if lib._lock_key is None:
                        raise RuntimeError("The source library is closed.")
                    for path in inputs:
                        lib.check_path(path)
                    lib.check_path(out)
                with actions.created_batch(lib, "story", title) as batch:
                    created[0] = batch
                    return export(prog)
            finally:
                if lib is not None:
                    lib.close_thread()

        if not self.run(title, journaled_work, done, cancelled, notify_success=False):
            self.ctx.toast_requested.emit("Another task is still running. Try again when it has finished.", "")

    def _show_outputs(self) -> None:
        existing = [p for p in self._last_outputs if Path(p).exists()]
        if existing:
            show_in_explorer(existing[0])
        else:
            self.output.open_folder()
