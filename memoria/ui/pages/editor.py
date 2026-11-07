"""Editor: crop, rotate, flip, adjust, resize/compress, split and join photos and videos.

Originals are never changed. Every result is a new file, recorded in History so it can be undone.
"""
from __future__ import annotations

import io
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QIcon, QImage, QPixmap
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialog, QDoubleSpinBox, QFileDialog, QFrame, QGridLayout,
                               QLabel, QListWidget, QListWidgetItem, QPushButton, QScrollArea, QSlider, QSpinBox,
                               QSplitter, QWidget)

from ...engine import actions, config
from .. import theme
from ..cropcanvas import CropCanvas, flip_crop, rotate_crop
from ..tasks import BackgroundCall
from ..widgets import (Banner, PhotoGrid, button, fmt_duration, fmt_n, fmt_size, hbox, label, show_in_explorer,
                       vbox)
from .base import Page

try:
    from ...engine import photoedit, videoedit
except ImportError:  # pragma: no cover - engines are part of the app
    photoedit = videoedit = None

RESIZES = [("Original size", None), ("4096 px", 4096), ("3000 px", 3000), ("2048 px", 2048), ("1600 px", 1600),
           ("1080 px", 1080)]
VIDEO_RES = [("Keep original", None), ("1080p", 1080), ("720p", 720), ("480p", 480)]
QUALITY = [("High", "high"), ("Balanced", "balanced"), ("Small", "small")]


def _pil_to_pixmap(img) -> QPixmap:
    img = img.convert("RGB")
    q = QImage(img.tobytes(), img.width, img.height, img.width * 3, QImage.Format.Format_RGB888)
    return QPixmap.fromImage(q.copy())


def _grid2(*widgets) -> QGridLayout:
    g = QGridLayout()
    g.setSpacing(6)
    for i, w in enumerate(widgets):
        g.addWidget(w, i // 2, i % 2)
    return g


def _section(title: str) -> QLabel:
    lab = label(title.upper(), "navGroup")
    lab.setContentsMargins(0, 10, 0, 2)
    return lab


class Slider(QWidget):
    """Labelled slider with a value readout; double-click the label to reset."""

    def __init__(self, text: str, lo: int, hi: int, on_change, scale: float = 1.0, suffix: str = ""):
        super().__init__()
        self.scale, self.suffix = scale, suffix
        self.name = label(text)
        self.value_lbl = label("0", "small")
        self.s = QSlider(Qt.Orientation.Horizontal)
        self.s.setRange(lo, hi)
        self.s.valueChanged.connect(lambda v: (self._show(v), on_change()))
        self.name.mouseDoubleClickEvent = lambda e: self.s.setValue(0)
        self.name.setToolTip("Double-click to reset")
        self.setLayout(vbox(hbox(self.name, None, self.value_lbl), self.s, spacing=2))
        self._show(0)

    def _show(self, v: int) -> None:
        val = v * self.scale
        text = f"{val:+.1f}" if self.scale != 1 else f"{int(val):+d}"
        self.value_lbl.setText(text + self.suffix if v else "0")

    def value(self) -> float:
        return self.s.value() * self.scale

    def set(self, v: float) -> None:
        self.s.blockSignals(True)
        self.s.setValue(int(round(v / self.scale)))
        self.s.blockSignals(False)
        self._show(self.s.value())


class LibraryPicker(QDialog):
    """Pick photos/videos from the library to add to the editor."""

    def __init__(self, parent, ctx):
        super().__init__(parent)
        self.setWindowTitle("Add from library")
        self.resize(900, 640)
        from PySide6.QtWidgets import QLineEdit
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search name or folder")
        self.kind = QComboBox()
        self.kind.addItems(["Photos and videos", "Photos", "Videos"])
        self.grid = PhotoGrid(ctx.thumbs, cell=130, captions=1)
        self.rows = [dict(r) for r in ctx.library.files("kind!='other' AND error IS NULL",
                                                        order="COALESCE(taken_at,'') DESC, rel_path")]
        ok = button("Add selected", "primary", self.accept)
        self.setLayout(vbox(label("Add from library", "h2"), hbox(self.search, self.kind), self.grid,
                            hbox(label("Ctrl/Shift-click to pick several.", "small"), None,
                                 button("Cancel", on_click=self.reject), ok), spacing=10, margins=(18, 16, 18, 14)))
        self.search.textChanged.connect(self._filter)
        self.kind.currentIndexChanged.connect(self._filter)
        self._filter()

    def _filter(self) -> None:
        q = self.search.text().lower()
        k = self.kind.currentIndex()
        items = [{**r, "caption": r["name"]} for r in self.rows
                 if (k == 0 or (k == 1 and r["kind"] == "image") or (k == 2 and r["kind"] == "video"))
                 and (not q or q in r["rel_path"].lower())]
        self.grid.set_items(items)

    def selected(self) -> list[dict]:
        return self.grid.selected_items()


class EditorPage(Page):
    title = "Editor"
    subtitle = "Crop, rotate, flip, adjust, resize, split and join photos and videos — originals are never changed."

    def __init__(self, ctx):
        super().__init__(ctx)
        self.items: list[dict] = []          # {key, path, name, kind, id, size, width, height, duration}
        self.edits: dict[str, object] = {}
        self.current: Optional[dict] = None
        self._base_img = None                # preview-size upright image of the current photo
        self._full_size = (0, 0)
        self._video_info = None
        self._t = 0.0
        self._loading = False

        # ---- files list
        self.files = QListWidget()
        self.files.setIconSize(QSize(48, 48))
        self.files.currentRowChanged.connect(self._select)
        self.files.setMinimumWidth(220)
        add_lib = button("Add from library…", on_click=self._add_from_library)
        add_ext = button("Open files…", on_click=self._add_external)
        remove = button("Remove", "link", self._remove_current)
        left = QWidget()
        left.setLayout(vbox(label("Files", "h2"), self.files, hbox(add_lib, add_ext), hbox(remove, None),
                            spacing=8))
        left.setFixedWidth(250)

        # ---- canvas + timeline
        self.canvas = CropCanvas()
        self.canvas.crop_changed.connect(self._crop_dragged)
        self.canvas.set_message("Add photos or videos to start editing.\n\nTip: select items in Photos & videos and "
                                "choose “Edit”.")
        self.timeline = QSlider(Qt.Orientation.Horizontal)
        self.timeline.setRange(0, 1000)
        self.timeline.valueChanged.connect(self._scrub)
        self.time_lbl = label("", "small")
        self.set_start_btn = button("Set start here", on_click=lambda: self._set_trim("start"))
        self.set_end_btn = button("Set end here", on_click=lambda: self._set_trim("end"))
        self.timeline_row = QWidget()
        self.timeline_row.setLayout(vbox(self.timeline, hbox(self.time_lbl, None, self.set_start_btn,
                                                             self.set_end_btn), spacing=4))
        self.status = label("", "small")
        center = QWidget()
        center.setLayout(vbox(self.canvas, self.timeline_row, self.status, spacing=6))

        # ---- tools
        self.photo_tools = self._build_photo_tools()
        self.video_tools = self._build_video_tools()
        tools = QWidget()
        tools.setLayout(vbox(self.photo_tools, self.video_tools, None, spacing=0))
        sa = QScrollArea()
        sa.setWidgetResizable(True)
        sa.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        sa.setWidget(tools)
        sa.setFixedWidth(330)
        tools.setFixedWidth(312)

        split = QSplitter()
        split.addWidget(left)
        split.addWidget(center)
        split.addWidget(sa)
        split.setStretchFactor(1, 1)
        split.setChildrenCollapsible(False)

        # ---- save bar
        self.dest = QComboBox()
        self.dest.addItem("Next to the original", None)
        self.dest.addItem("Choose a folder…", "choose")
        self.dest.currentIndexChanged.connect(self._dest_changed)
        self._dest_dir: Optional[str] = None
        self.all_box = QCheckBox("")
        self.all_box.setToolTip("Apply the same edits to every photo (or video) in the list")
        self.all_box.toggled.connect(lambda _: self._update_buttons())
        self.reset_btn = button("Reset edits", on_click=self._reset)
        self.save_btn = button("Save edited copy", "primary", self.save)
        self.last_btn = button("Show result", "link", self._show_last)
        self.last_btn.hide()
        self._last_output: Optional[Path] = None
        self.body.addWidget(Banner("<b>Originals are never changed.</b> Edits are saved as new files (for example "
                                   "“IMG_1234 (edited).jpg”) and listed in History, so Undo removes them again.", "trust"))
        self.body.addWidget(split, 1)
        self.body.addLayout(hbox(label("Save to", "muted"), self.dest, 12, self.all_box, None, self.last_btn,
                                 self.reset_btn, self.save_btn))

        self.bg = BackgroundCall(self)
        self.bg.result.connect(self._preview_ready)
        self.bg.failed.connect(lambda e: self.canvas.set_message(f"Can't show a preview: {e}"))
        self.est = BackgroundCall(self)
        self.est.result.connect(self._estimate_ready)
        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(140)
        self._debounce.timeout.connect(self._render)
        self._show_tools(None)

    # ===================================================================== tool panels
    def _build_photo_tools(self) -> QWidget:
        w = QWidget()
        self.p_rot_l = button("⟲ Rotate left", on_click=lambda: self._rotate(-1), tip="Rotate 90° left")
        self.p_rot_r = button("⟳ Rotate right", on_click=lambda: self._rotate(1), tip="Rotate 90° right")
        self.p_flip_h = button("⇋ Mirror", on_click=lambda: self._flip(True), tip="Flip horizontally")
        self.p_flip_v = button("⇵ Flip", on_click=lambda: self._flip(False), tip="Flip vertically")
        self.p_straighten = Slider("Straighten", -150, 150, self._changed, scale=0.1, suffix="°")
        self.p_aspect = QComboBox()
        for key in (photoedit.ASPECTS if photoedit else {"free": None}):
            self.p_aspect.addItem({"free": "Free", "original": "Original shape"}.get(key, key), key)
        self.p_aspect.currentIndexChanged.connect(self._aspect_changed)
        self.p_crop_btn = button("Crop…", on_click=self._toggle_crop)
        self.p_crop_btn.setCheckable(True)
        self.p_crop_reset = button("Reset crop", "link", self._reset_crop)
        self.p_sliders = {k: Slider(t, lo, 100, self._changed) for k, t, lo in
                          (("brightness", "Brightness", -100), ("contrast", "Contrast", -100),
                           ("saturation", "Saturation", -100), ("warmth", "Warmth", -100),
                           ("sharpness", "Sharpness", 0))}
        self.p_auto = QCheckBox("Auto enhance")
        self.p_auto.toggled.connect(self._changed)
        self.p_filter = QComboBox()
        for key, text in (photoedit.FILTERS if photoedit else {"none": "None"}).items():
            self.p_filter.addItem(text, key)
        self.p_filter.currentIndexChanged.connect(self._changed)
        self.p_resize = QComboBox()
        for text, v in RESIZES:
            self.p_resize.addItem(text, v)
        self.p_resize.currentIndexChanged.connect(self._changed)
        self.p_format = QComboBox()
        for key, text in (photoedit.FORMATS if photoedit else {"same": "Same"}).items():
            self.p_format.addItem(text, key)
        self.p_format.currentIndexChanged.connect(self._changed)
        self.p_quality = Slider("Quality", 30, 100, self._changed)
        self.p_quality.set(90)
        self.p_gps = QCheckBox("Remove location (GPS)")
        self.p_gps.setToolTip("The edited copy will not contain where the photo was taken")
        self.p_gps.toggled.connect(self._changed)
        self.p_estimate = label("", "small")
        self.p_rows = QSpinBox()
        self.p_rows.setRange(1, 10)
        self.p_cols = QSpinBox()
        self.p_cols.setRange(1, 10)
        self.p_cols.setValue(3)
        self.p_split_btn = button("Split into pieces", on_click=self._split_photo)
        self.p_join_dir = QComboBox()
        self.p_join_dir.addItem("Side by side", "horizontal")
        self.p_join_dir.addItem("Top to bottom", "vertical")
        self.p_join_dir.addItem("Grid", "grid")
        self.p_join_btn = button("Join photos", on_click=self._join_photos)
        for c in (self.p_aspect, self.p_filter, self.p_resize, self.p_format, self.p_join_dir):
            c.setMinimumContentsLength(10)
            c.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        lay = vbox(_section("Rotate & flip"), _grid2(self.p_rot_l, self.p_rot_r, self.p_flip_h, self.p_flip_v),
                   self.p_straighten,
                   _section("Crop"), hbox(label("Shape", "muted"), self.p_aspect), hbox(self.p_crop_btn, self.p_crop_reset, None),
                   _section("Adjust"), *self.p_sliders.values(), hbox(self.p_auto, None),
                   hbox(label("Filter", "muted"), self.p_filter),
                   _section("Size & compression"), hbox(label("Longest side", "muted"), self.p_resize),
                   hbox(label("Format", "muted"), self.p_format), self.p_quality, self.p_gps, self.p_estimate,
                   _section("Split & join"),
                   hbox(label("Rows", "muted"), self.p_rows, label("Columns", "muted"), self.p_cols, None),
                   hbox(self.p_split_btn, None), hbox(label("Join", "muted"), self.p_join_dir), hbox(self.p_join_btn, None),
                   spacing=6, margins=(4, 0, 8, 8))
        w.setLayout(lay)
        return w

    def _build_video_tools(self) -> QWidget:
        w = QWidget()
        self.v_start = QDoubleSpinBox()
        self.v_end = QDoubleSpinBox()
        for sb in (self.v_start, self.v_end):
            sb.setDecimals(1)
            sb.setSuffix(" s")
            sb.setSingleStep(0.5)
            sb.valueChanged.connect(self._changed)
        self.v_length = label("", "small")
        self.v_split_here = button("Split at playhead", on_click=self._split_here)
        self.v_parts = QSpinBox()
        self.v_parts.setRange(2, 50)
        self.v_split_equal = button("Split into equal parts", on_click=self._split_equal)
        self.v_every = QDoubleSpinBox()
        self.v_every.setRange(1, 3600)
        self.v_every.setValue(15)
        self.v_every.setSuffix(" s")
        self.v_split_every = button("Split every…", on_click=self._split_every)
        self.v_join = button("Join videos", on_click=self._join_videos)
        self.v_rot_l = button("⟲ Rotate left", on_click=lambda: self._rotate(-1))
        self.v_rot_r = button("⟳ Rotate right", on_click=lambda: self._rotate(1))
        self.v_flip_h = button("⇋ Mirror", on_click=lambda: self._flip(True))
        self.v_flip_v = button("⇵ Flip", on_click=lambda: self._flip(False))
        self.v_aspect = QComboBox()
        for key in (photoedit.ASPECTS if photoedit else {"free": None}):
            self.v_aspect.addItem({"free": "Free", "original": "Original shape"}.get(key, key), key)
        self.v_aspect.currentIndexChanged.connect(self._aspect_changed)
        self.v_crop_btn = button("Crop…", on_click=self._toggle_crop)
        self.v_crop_btn.setCheckable(True)
        self.v_crop_reset = button("Reset crop", "link", self._reset_crop)
        self.v_sliders = {k: Slider(t, -100, 100, self._changed) for k, t in
                          (("brightness", "Brightness"), ("contrast", "Contrast"), ("saturation", "Saturation"))}
        self.v_speed = QComboBox()
        for s in (videoedit.SPEEDS if videoedit else (1.0,)):
            self.v_speed.addItem(f"{s:g}×", s)
        self.v_speed.setCurrentIndex(max(0, self.v_speed.findData(1.0)))
        self.v_speed.currentIndexChanged.connect(self._changed)
        self.v_mute = QCheckBox("Remove sound")
        self.v_mute.toggled.connect(self._changed)
        self.v_res = QComboBox()
        for text, v in VIDEO_RES:
            self.v_res.addItem(text, v)
        self.v_res.currentIndexChanged.connect(self._changed)
        self.v_quality = QComboBox()
        for text, v in QUALITY:
            self.v_quality.addItem(text, v)
        self.v_quality.setCurrentIndex(1)
        self.v_quality.currentIndexChanged.connect(self._changed)
        self.v_frame = button("Save frame as photo", on_click=self._save_frame)
        lay = vbox(_section("Trim"), hbox(label("Start", "muted"), self.v_start, label("End", "muted"), self.v_end),
                   self.v_length,
                   _section("Split & join"), hbox(self.v_split_here, None),
                   hbox(self.v_parts, self.v_split_equal, None), hbox(self.v_every, self.v_split_every, None),
                   hbox(self.v_join, None),
                   _section("Rotate & flip"), _grid2(self.v_rot_l, self.v_rot_r, self.v_flip_h, self.v_flip_v),
                   _section("Crop"), hbox(label("Shape", "muted"), self.v_aspect), hbox(self.v_crop_btn, self.v_crop_reset, None),
                   _section("Adjust"), *self.v_sliders.values(), hbox(label("Speed", "muted"), self.v_speed, None),
                   hbox(self.v_mute, None),
                   _section("Size & compression"), hbox(label("Resolution", "muted"), self.v_res),
                   hbox(label("Quality", "muted"), self.v_quality),
                   _section("Frame"), hbox(self.v_frame, None),
                   spacing=6, margins=(4, 0, 8, 8))
        w.setLayout(lay)
        return w

    # ===================================================================== lifecycle
    def refresh(self) -> None:
        self._take_selection()

    def showEvent(self, e) -> None:  # noqa: N802
        super().showEvent(e)
        self._take_selection()

    def on_busy_changed(self, busy: bool) -> None:
        for b in (self.save_btn, self.p_split_btn, self.p_join_btn, self.v_split_here, self.v_split_equal,
                  self.v_split_every, self.v_join, self.v_frame):
            b.setEnabled(not busy and self.current is not None)
        self._update_buttons()

    def shutdown(self) -> None:
        self.bg.wait()
        self.est.wait()

    def _take_selection(self) -> None:
        ids = list(getattr(self.ctx, "edit_selection", []))
        if not ids or self.lib is None:
            return
        self.ctx.edit_selection.clear()
        rows = [self.lib.file(i) for i in ids]
        self.add_rows([dict(r) for r in rows if r is not None])

    # ===================================================================== file list
    def add_rows(self, rows: list[dict]) -> None:
        for r in rows:
            if r.get("kind") not in ("image", "video") or r.get("error"):
                continue
            path = Path(r["path"]) if r.get("path") else self.lib.abspath(r["rel_path"])
            key = str(path).lower()
            if any(it["key"] == key for it in self.items):
                continue
            self.items.append({"key": key, "path": path, "name": path.name, "kind": r["kind"], "id": r.get("id"),
                               "size": r.get("size") or (path.stat().st_size if path.exists() else 0),
                               "duration": r.get("duration")})
            it = QListWidgetItem(f"{path.name}\n{'Video' if r['kind'] == 'video' else 'Photo'} · "
                                 f"{fmt_size(self.items[-1]['size'])}")
            pm = self.ctx.thumbs.get(r["id"]) if r.get("id") is not None else None
            if pm is not None:
                it.setIcon(QIcon(pm))
            self.files.addItem(it)
        if self.files.currentRow() < 0 and self.items:
            self.files.setCurrentRow(0)
        self._update_buttons()

    def _add_from_library(self) -> None:
        if self.lib is None:
            return
        dlg = LibraryPicker(self, self.ctx)
        if dlg.exec():
            self.add_rows(dlg.selected())

    def _add_external(self) -> None:
        exts = " ".join(f"*{e}" for e in sorted(config.IMAGE_EXT | config.VIDEO_EXT))
        files, _ = QFileDialog.getOpenFileNames(self, "Open photos or videos", str(Path.home()),
                                                f"Photos and videos ({exts});;All files (*)")
        rows = []
        for f in files:
            p = Path(f)
            kind = config.kind_for_ext(p.suffix)
            rows.append({"path": str(p), "kind": kind, "size": p.stat().st_size})
        self.add_rows(rows)

    def _remove_current(self) -> None:
        row = self.files.currentRow()
        if 0 <= row < len(self.items):
            self.edits.pop(self.items[row]["key"], None)
            del self.items[row]
            self.files.takeItem(row)
            if not self.items:
                self.current = None
                self._show_tools(None)
                self.canvas.set_message("Add photos or videos to start editing.")
        self._update_buttons()

    def _select(self, row: int) -> None:
        if not (0 <= row < len(self.items)):
            return
        self.current = it = self.items[row]
        self._show_tools(it["kind"])
        self._base_img = None
        self._video_info = None
        self.canvas.set_message("Loading…")
        if it["kind"] == "image":
            path = it["path"]

            def load():
                from PIL import Image
                img = photoedit.load(path, max_side=1600)
                with Image.open(config.longpath(path)) as im:
                    size = im.size
                return img, size

            self.bg.call(lambda: ("load", it["key"], load()))
        else:
            from ...engine import ffmpeg
            self.bg.call(lambda: ("vload", it["key"], ffmpeg.probe(it["path"])))
        self._load_controls()

    def _show_tools(self, kind: Optional[str]) -> None:
        self.photo_tools.setVisible(kind == "image")
        self.video_tools.setVisible(kind == "video")
        self.timeline_row.setVisible(kind == "video")
        self._update_buttons()

    # ===================================================================== edits <-> controls
    def edit(self):
        it = self.current
        if it is None:
            return None
        if it["key"] not in self.edits:
            self.edits[it["key"]] = photoedit.PhotoEdit() if it["kind"] == "image" else videoedit.VideoEdit()
        return self.edits[it["key"]]

    def _load_controls(self) -> None:
        e = self.edit()
        if e is None:
            return
        self._loading = True
        if self.current["kind"] == "image":
            self.p_straighten.set(e.straighten)
            for k, s in self.p_sliders.items():
                s.set(getattr(e, k))
            self.p_auto.setChecked(e.auto)
            self.p_filter.setCurrentIndex(max(0, self.p_filter.findData(e.filter)))
            self.p_resize.setCurrentIndex(max(0, self.p_resize.findData(e.resize_long)))
            self.p_format.setCurrentIndex(max(0, self.p_format.findData(e.format)))
            self.p_quality.set(e.quality)
            self.p_gps.setChecked(e.strip_gps)
        else:
            for k, s in self.v_sliders.items():
                s.set(getattr(e, k))
            self.v_speed.setCurrentIndex(max(0, self.v_speed.findData(e.speed)))
            self.v_mute.setChecked(e.mute)
            self.v_res.setCurrentIndex(max(0, self.v_res.findData(e.max_height)))
            self.v_quality.setCurrentIndex(max(0, self.v_quality.findData(e.quality)))
        self._loading = False
        self._exit_crop()

    def _changed(self, *_) -> None:
        if self._loading or self.current is None:
            return
        e = self.edit()
        if self.current["kind"] == "image":
            e.straighten = self.p_straighten.value()
            for k, s in self.p_sliders.items():
                setattr(e, k, int(s.value()))
            e.auto = self.p_auto.isChecked()
            e.filter = self.p_filter.currentData()
            e.resize_long = self.p_resize.currentData()
            e.format = self.p_format.currentData()
            e.quality = int(self.p_quality.value())
            e.strip_gps = self.p_gps.isChecked()
            self.p_quality.setEnabled(e.format in ("jpeg", "webp", "same"))
        else:
            for k, s in self.v_sliders.items():
                setattr(e, k, int(s.value()))
            e.speed = self.v_speed.currentData()
            e.mute = self.v_mute.isChecked()
            e.max_height = self.v_res.currentData()
            e.quality = self.v_quality.currentData()
            dur = self._video_info.duration if self._video_info else 0
            e.start = min(self.v_start.value(), max(0.0, dur - 0.1))
            end = self.v_end.value()
            e.end = None if (not dur or end >= dur - 0.05) else max(end, e.start + 0.1)
            self._update_length()
        self._update_buttons()
        self._debounce.start()

    def _rotate(self, direction: int) -> None:
        e = self.edit()
        if e is None:
            return
        e.rotate = (e.rotate + 90 * direction) % 360
        e.crop = rotate_crop(e.crop, 1 if direction > 0 else 3)
        self._exit_crop()
        self._update_buttons()
        self._debounce.start()

    def _flip(self, horizontal: bool) -> None:
        e = self.edit()
        if e is None:
            return
        if horizontal:
            e.flip_h = not e.flip_h
        else:
            e.flip_v = not e.flip_v
        e.crop = flip_crop(e.crop, horizontal)
        self._exit_crop()
        self._update_buttons()
        self._debounce.start()

    def _reset(self) -> None:
        if self.current is None:
            return
        self.edits.pop(self.current["key"], None)
        self._load_controls()
        if self.current["kind"] == "video" and self._video_info:
            self._init_trim()
        self._update_buttons()
        self._debounce.start()

    # ===================================================================== crop
    def _aspect_value(self) -> Optional[float]:
        combo = self.p_aspect if self.current and self.current["kind"] == "image" else self.v_aspect
        key = combo.currentData()
        val = photoedit.ASPECTS.get(key) if photoedit else None
        if val == "original":
            w, h = self._transformed_size()
            return w / h if h else None
        return val

    def _transformed_size(self) -> tuple[int, int]:
        e = self.edit()
        if self.current["kind"] == "image":
            w, h = self._full_size
        else:
            w, h = (self._video_info.width, self._video_info.height) if self._video_info else (16, 9)
        return (h, w) if e is not None and e.rotate in (90, 270) else (w, h)

    def _toggle_crop(self) -> None:
        btn = self.p_crop_btn if self.current["kind"] == "image" else self.v_crop_btn
        if self.canvas.crop_mode:
            self._exit_crop()
            self._debounce.start()
            return
        e = self.edit()
        aspect = self._aspect_value()
        crop = e.crop
        if crop is None and aspect and photoedit is not None:
            w, h = self._transformed_size()
            crop = photoedit.crop_for_aspect(w, h, aspect)
        self.canvas.set_crop_mode(True, crop, aspect)
        e.crop = self.canvas.crop
        btn.setChecked(True)
        btn.setText("Done")
        self._render(crop_view=True)

    def _exit_crop(self) -> None:
        if self.canvas.crop_mode:
            self.canvas.set_crop_mode(False, None, None)
        for b in (self.p_crop_btn, self.v_crop_btn):
            b.setChecked(False)
            b.setText("Crop…")

    def _crop_dragged(self, crop) -> None:
        e = self.edit()
        if e is not None:
            e.crop = None if crop == (0.0, 0.0, 1.0, 1.0) else tuple(round(v, 4) for v in crop)
            self._update_buttons()

    def _aspect_changed(self) -> None:
        if self._loading or self.current is None:
            return
        aspect = self._aspect_value()
        e = self.edit()
        if aspect and photoedit is not None:
            w, h = self._transformed_size()
            e.crop = photoedit.crop_for_aspect(w, h, aspect)
        if self.canvas.crop_mode:
            self.canvas.set_crop_mode(True, e.crop, aspect)
        else:
            self._toggle_crop()
        self._update_buttons()

    def _reset_crop(self) -> None:
        e = self.edit()
        if e is None:
            return
        e.crop = None
        if self.canvas.crop_mode:
            self.canvas.set_crop_mode(True, None, self._aspect_value())
        self._update_buttons()
        self._debounce.start()

    # ===================================================================== preview rendering
    def _render(self, crop_view: bool = False) -> None:
        it, e = self.current, self.edit()
        if it is None:
            return
        crop_view = crop_view or self.canvas.crop_mode
        key = it["key"]
        if it["kind"] == "image":
            base = self._base_img
            if base is None:
                return
            snap = e.copy()

            def work():
                img = photoedit.transform(base, snap) if crop_view else photoedit.apply(base, snap)
                return ("img", key, img)

            self.bg.call(work)
            if not crop_view:
                full, src = self._full_size, it["path"]
                self.est.call(lambda: (key, photoedit.estimate_bytes(base, snap, full, src=src)))
        else:
            if self._video_info is None:
                return
            snap, t, path = e.copy(), self._t, it["path"]
            self.bg.call(lambda: ("frame", key, videoedit.preview_frame(path, t, snap, 900, crop=not crop_view)))

    def _preview_ready(self, result) -> None:
        kind, key, value = result
        if self.current is None or key != self.current["key"]:
            return
        if kind == "load":
            img, size = value
            self._base_img, self._full_size = img, size
            self._debounce.start()
        elif kind == "vload":
            self._video_info = value
            self._init_trim()
            self._debounce.start()
        elif kind == "img":
            self.canvas.set_pixmap(_pil_to_pixmap(value))
        elif kind == "frame":
            if value:
                pm = QPixmap()
                pm.loadFromData(value, "JPG")
                self.canvas.set_pixmap(pm)
            else:
                self.canvas.set_message("This frame could not be read.")
        self._update_status()

    def _estimate_ready(self, result) -> None:
        key, n = result
        if self.current is not None and key == self.current["key"]:
            self.p_estimate.setText(f"Estimated size about {fmt_size(n)} (original {fmt_size(self.current['size'])}). "
                                    "Rough guide — the saved file may differ.")

    # ===================================================================== video timeline
    def _init_trim(self) -> None:
        info, e = self._video_info, self.edit()
        dur = info.duration
        self._loading = True
        for sb in (self.v_start, self.v_end):
            sb.setRange(0, dur)
        self.v_start.setValue(e.start)
        self.v_end.setValue(e.end if e.end is not None else dur)
        self._loading = False
        self._t = min(1.0, dur / 2)
        self.timeline.blockSignals(True)
        self.timeline.setValue(int(1000 * self._t / dur) if dur else 0)
        self.timeline.blockSignals(False)
        self._update_length()

    def _scrub(self, v: int) -> None:
        if self._video_info is None:
            return
        self._t = self._video_info.duration * v / 1000
        self._update_status()
        self._debounce.start()

    def _set_trim(self, which: str) -> None:
        if self._video_info is None:
            return
        (self.v_start if which == "start" else self.v_end).setValue(round(self._t, 1))

    def _update_length(self) -> None:
        if self._video_info is None or self.current is None or self.current["kind"] != "video":
            return
        e = self.edit()
        out = videoedit.output_duration(self._video_info, e)
        self.v_length.setText(f"Result: {fmt_duration(out) or '0:00'} long (original {fmt_duration(self._video_info.duration)})")

    def _update_status(self) -> None:
        it = self.current
        if it is None:
            self.status.setText("")
            return
        if it["kind"] == "video" and self._video_info:
            i = self._video_info
            self.time_lbl.setText(f"{self._t:0.1f} s of {i.duration:0.1f} s")
            self.status.setText(f"{it['name']} · {i.width}×{i.height} · {fmt_duration(i.duration)} · {fmt_size(it['size'])}")
        elif it["kind"] == "image" and self._full_size[0]:
            self.status.setText(f"{it['name']} · {self._full_size[0]}×{self._full_size[1]} · {fmt_size(it['size'])}"
                                + ("  —  drag the corners to crop; click Done when finished" if self.canvas.crop_mode else ""))

    # ===================================================================== buttons & destination
    def _update_buttons(self) -> None:
        it = self.current
        photos = [i for i in self.items if i["kind"] == "image"]
        videos = [i for i in self.items if i["kind"] == "video"]
        same = photos if it and it["kind"] == "image" else videos
        self.all_box.setVisible(len(same) > 1)
        noun = "photo" if it and it["kind"] == "image" else "video"
        self.all_box.setText(f"Apply to all {len(same)} {noun}s")
        n = len(same) if self.all_box.isChecked() and len(same) > 1 else 1
        self.save_btn.setText(f"Save {n} edited copies" if n > 1 else "Save edited copy")
        e = self.edit() if it else None
        idle = not self.busy
        self.save_btn.setEnabled(idle and e is not None and not e.is_identity())
        self.reset_btn.setEnabled(e is not None and not e.is_identity())
        self.p_join_btn.setEnabled(idle and len(photos) >= 2)
        self.p_join_btn.setText(f"Join {len(photos)} photos" if len(photos) >= 2 else "Join photos (add 2 or more)")
        self.v_join.setEnabled(idle and len(videos) >= 2)
        self.v_join.setText(f"Join {len(videos)} videos" if len(videos) >= 2 else "Join videos (add 2 or more)")

    def _dest_changed(self) -> None:
        if self.dest.currentData() == "choose":
            d = QFileDialog.getExistingDirectory(self, "Save edited files to…", str(Path.home() / "Pictures"))
            if d:
                self._dest_dir = d
                label_ = f"…\\{Path(d).name}" if len(d) > 28 else d
                if self.dest.count() > 2:
                    self.dest.removeItem(2)
                self.dest.addItem(label_, d)
                self.dest.setCurrentIndex(2)
            else:
                self.dest.setCurrentIndex(0)
        elif self.dest.currentData() is None:
            self._dest_dir = None
        else:
            self._dest_dir = self.dest.currentData()

    def _out_dir(self, src: Path) -> Optional[Path]:
        return Path(self._dest_dir) if self._dest_dir else None

    # ===================================================================== running work
    def _run_outputs(self, title: str, fn, sources_for: callable, failures: Optional[list] = None) -> None:
        """Run ``fn(progress) -> list[Path]`` then journal the new files so History can undo them."""
        lib = self.lib

        def work(prog):
            with actions.created_batch(lib, "edit", title) as batch:
                outputs = fn(prog.step(0, 2, title))
            if not isinstance(outputs, (list, tuple)):
                outputs = [outputs]
            outputs = [Path(p) for p in outputs if p]
            if lib is not None and outputs:
                for p in outputs:
                    lib.db.execute("UPDATE operations SET src=? WHERE batch_id=? AND dst=?",
                                   (str(sources_for(p)), batch.batch_id, str(p)))
                if any(self._inside(lib, p) for p in outputs):
                    from ...engine import scanner
                    scanner.index(lib, prog.step(1, 2, "Adding the new files to the library"))
            return outputs, batch

        def done(res):
            outputs, batch = res
            self.ctx.library_modified.emit()
            if not outputs:
                self.ctx.toast_requested.emit("Nothing was created.", "")
                return
            self._last_output = outputs[0]
            self.last_btn.setText("Show result" if len(outputs) == 1 else f"Show results ({len(outputs)})")
            self.last_btn.show()
            names = outputs[0].name if len(outputs) == 1 else f"{fmt_n(len(outputs), 'file')}"
            self.ctx.toast_requested.emit(f"Saved {names}. The original is unchanged.", batch.batch_id if batch else "")
            if failures:
                from ..widgets import MessageDialog
                MessageDialog(self, "Some files could not be edited",
                              f"{fmt_n(len(failures), 'file')} could not be saved. The originals were not touched.",
                              "\n".join(f"{Path(f).name}: {m}" for f, m in failures)).exec()

        self.run(title, work, done, on_cancel=self.ctx.library_modified.emit)

    @staticmethod
    def _inside(lib, p: Path) -> bool:
        try:
            p.resolve().relative_to(lib.root)
            return True
        except ValueError:
            return False

    def _show_last(self) -> None:
        if self._last_output is not None:
            show_in_explorer(self._last_output)

    def save(self) -> None:
        it, e = self.current, self.edit()
        if it is None or e is None or e.is_identity():
            return
        self._exit_crop()
        same = [i for i in self.items if i["kind"] == it["kind"]]
        targets = same if self.all_box.isChecked() and len(same) > 1 else [it]
        out = self._out_dir(it["path"])
        snap = e.copy()
        paths = [t["path"] for t in targets]
        src_of: dict = {}
        failures: list = []

        if it["kind"] == "image":
            def fn(prog):
                if len(paths) == 1:
                    p = photoedit.save(paths[0], snap, out, progress=prog)
                    src_of[str(p).lower()] = paths[0]
                    return [p]
                res = photoedit.save_many(paths, snap, out, progress=prog)
                for p, s in zip(res, getattr(res, "sources", paths)):
                    src_of[str(p).lower()] = s
                failures.extend(getattr(res, "failures", []))
                return list(res)
        else:
            def fn(prog):
                results = []
                for i, p in enumerate(paths):
                    sub = prog.step(i, len(paths), p.name) if len(paths) > 1 else prog
                    edit_i = snap if p == it["path"] else snap.copy(start=0.0, end=None)
                    r = videoedit.export(p, edit_i, out, progress=sub)
                    src_of[str(r).lower()] = p
                    results.append(r)
                return results

        title = f"Save {fmt_n(len(targets), 'edited copy', 'edited copies')}"
        self._run_outputs(title, fn, lambda p: src_of.get(str(p).lower(), it["path"]), failures)

    # ----------------------------------------------------------------- photo split / join
    def _split_photo(self) -> None:
        it = self.current
        if it is None or it["kind"] != "image":
            return
        rows, cols, e, out = self.p_rows.value(), self.p_cols.value(), self.edit().copy(), self._out_dir(it["path"])
        if rows * cols < 2:
            self.ctx.toast_requested.emit("Choose at least 2 pieces (rows × columns).", "")
            return
        self._run_outputs(f"Split into {rows * cols} pieces",
                          lambda prog: photoedit.split_grid(it["path"], rows, cols, out,
                                                            None if e.is_identity() else e, prog),
                          lambda p: it["path"])

    def _join_photos(self) -> None:
        photos = [i["path"] for i in self.items if i["kind"] == "image"]
        if len(photos) < 2:
            return
        direction, out = self.p_join_dir.currentData(), self._out_dir(photos[0])
        self._run_outputs(f"Join {len(photos)} photos",
                          lambda prog: photoedit.join(photos, direction, out, progress=prog), lambda p: photos[0])

    # ----------------------------------------------------------------- video split / join / frame
    def _split_here(self) -> None:
        it = self.current
        if it is None or it["kind"] != "video" or self._video_info is None:
            return
        t, e, out = self._t, self.edit().copy(), self._out_dir(it["path"])
        if t <= e.start + 0.2 or t >= (e.end or self._video_info.duration) - 0.2:
            self.ctx.toast_requested.emit("Move the playhead inside the video to choose where to split.", "")
            return
        self._run_outputs("Split video", lambda prog: videoedit.split(it["path"], [t], out, e, progress=prog),
                          lambda p: it["path"])

    def _split_equal(self) -> None:
        it = self.current
        if it is None or it["kind"] != "video":
            return
        n, e, out = self.v_parts.value(), self.edit().copy(), self._out_dir(it["path"])
        self._run_outputs(f"Split into {n} parts",
                          lambda prog: videoedit.split_equal(it["path"], n, out, edit=e, progress=prog),
                          lambda p: it["path"])

    def _split_every(self) -> None:
        it = self.current
        if it is None or it["kind"] != "video":
            return
        s, e, out = self.v_every.value(), self.edit().copy(), self._out_dir(it["path"])
        self._run_outputs(f"Split every {s:g} s",
                          lambda prog: videoedit.split_every(it["path"], s, out, edit=e, progress=prog),
                          lambda p: it["path"])

    def _join_videos(self) -> None:
        vids = [i["path"] for i in self.items if i["kind"] == "video"]
        if len(vids) < 2:
            return
        out = self._out_dir(vids[0])
        self._run_outputs(f"Join {len(vids)} videos", lambda prog: videoedit.join(vids, out, progress=prog),
                          lambda p: vids[0])

    def _save_frame(self) -> None:
        it = self.current
        if it is None or it["kind"] != "video":
            return
        t, out = self._t, self._out_dir(it["path"])
        self._run_outputs("Save frame", lambda prog: videoedit.extract_frame(it["path"], t, out),
                          lambda p: it["path"])
