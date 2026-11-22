"""Compare this library with up to two others (phone backup, external drive) and sync by content."""
from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QImage, QPixmap
from PySide6.QtWidgets import (QButtonGroup, QCheckBox, QComboBox, QFileDialog, QFrame, QHeaderView, QInputDialog,
                               QLabel, QLineEdit, QListWidget, QListWidgetItem, QRadioButton, QSizePolicy, QSplitter,
                               QStackedWidget, QTabWidget, QTreeWidget, QTreeWidgetItem, QWidget)

from ...engine import libsync
from .. import theme
from ..motion import Dialog
from ..review_pages import ReviewGroup, ReviewPages
from ..tasks import LatestCall
from ..venn import VennWidget, side_colors
from ..widgets import (Banner, Card, EmptyState, HelpToggle, MessageDialog, button, fmt_date, fmt_n, fmt_size, hbox,
                       label, open_path, scroll, show_in_explorer, vbox)
from .base import Page

FILES_PER_FOLDER = 400
ENTRY_ROLE = Qt.ItemDataRole.UserRole
NODE_ROLE = Qt.ItemDataRole.UserRole + 1
LAZY_ROLE = Qt.ItemDataRole.UserRole + 2


def _also_in(entry: libsync.Entry, count: int) -> str:
    others = [libsync.letter(side) for side in libsync.bits(entry.mask) if side != entry.side and side < count]
    return ", ".join(others) if others else "-"


def _preview_image(path, kind: str):
    """A small QImage of a photo or a video frame, read off the UI thread; None if it can't be shown."""
    try:
        if kind == "photo":
            from ...engine.media import load_for_display
            img = load_for_display(path, 440)
            try:
                return QImage(img.tobytes(), img.width, img.height, img.width * 3, QImage.Format.Format_RGB888).copy()
            finally:
                img.close()
        if kind == "video":
            from ...engine import ffmpeg
            frame = ffmpeg.video_frame(path, 1.0, 440)
            return QImage.fromData(frame) if frame else None
    except Exception:
        return None
    return None


class SidePane(QFrame):
    """One library's matching files, grouped: a folder whose files all match is one row."""

    def __init__(self, page: "ComparePage", side: int):
        super().__init__()
        self.page, self.side = page, side
        self.cmp = None
        self.setObjectName("card")
        self.title = label("", "h2")
        self.summary = label("", "small", wrap=True)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Folder / file", "Details"])
        self.tree.setIndentation(14)
        self.tree.header().setStretchLastSection(False)
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tree.itemExpanded.connect(self._expanded)
        self.tree.currentItemChanged.connect(self._current)
        self.setLayout(vbox(self.title, self.summary, self.tree, spacing=4, margins=(10, 10, 10, 10)))

    def show_tree(self, cmp: libsync.Comparison, accept) -> None:
        self.cmp = cmp
        participant = cmp.participants[self.side]
        self.title.setText(f"{libsync.letter(self.side)} · {participant.label}")
        self.title.setStyleSheet(f"color:{side_colors()[self.side]}")
        root = cmp.tree(self.side, accept)
        self.tree.clear()
        if not root.matching:
            self.summary.setText(f"Nothing in {libsync.letter(self.side)} matches this view.")
            return
        self.summary.setText(
            f"{fmt_n(root.matching, 'file')} ({fmt_size(root.bytes)}) of {root.total:,}"
            + (" - every file in this library." if root.complete else
               ". \"all\" marks a folder whose files all match."))
        self._fill(self.tree.invisibleRootItem(), root, depth=0)

    def _folder_item(self, node: libsync.FolderNode) -> QTreeWidgetItem:
        count = f"all {node.matching:,}" if node.complete else f"{node.matching:,} of {node.total:,}"
        item = QTreeWidgetItem([node.name, f"{count} · {fmt_size(node.bytes)}"])
        item.setData(0, NODE_ROLE, node)
        item.setToolTip(0, node.rel + ("\nEvery file in this folder and its subfolders matches this view."
                                       if node.complete else "\nOnly some files here match; they are listed inside."))
        if node.complete:
            item.setForeground(0, QColor(side_colors()[self.side]))
            item.setForeground(1, QColor(side_colors()[self.side]))
        return item

    def _fill(self, parent: QTreeWidgetItem, node: libsync.FolderNode, depth: int) -> None:
        for child in sorted(node.folders.values(), key=lambda item: item.name.lower()):
            if not child.matching:
                continue
            item = self._folder_item(child)
            parent.addChild(item)
            if child.complete:
                item.addChild(QTreeWidgetItem(["Loading..."]))
                item.setData(0, LAZY_ROLE, True)
            else:
                self._fill(item, child, depth + 1)
                item.setExpanded(depth < 2)
        files = sorted(node.files, key=lambda entry: entry.name.lower())
        for entry in files[:FILES_PER_FOLDER]:
            also = _also_in(entry, self.cmp.count)
            item = QTreeWidgetItem([entry.name, fmt_size(entry.size) + ("" if also == "-" else f" · also {also}")])
            item.setData(0, ENTRY_ROLE, entry)
            item.setToolTip(0, entry.rel)
            parent.addChild(item)
        if len(files) > FILES_PER_FOLDER:
            parent.addChild(QTreeWidgetItem([f"... and {len(files) - FILES_PER_FOLDER:,} more files in this folder"]))

    def _expanded(self, item: QTreeWidgetItem) -> None:
        if item.data(0, LAZY_ROLE):
            item.setData(0, LAZY_ROLE, False)
            item.takeChildren()
            self._fill(item, item.data(0, NODE_ROLE), depth=3)

    def _current(self, current, previous) -> None:
        if current is not None:
            self.page.show_entry(current.data(0, ENTRY_ROLE), current.data(0, NODE_ROLE), self.side)


class PlanReviewDialog(Dialog):
    """A paged, checkable list of exactly what will be copied or moved."""

    def __init__(self, parent, title: str, summary: str, groups: list[ReviewGroup], columns: list[str], render,
                 size_of, confirm_text: str, note: str, note_kind: str = "trust", danger: bool = False):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(960, 620)
        self.confirm_text = confirm_text
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(columns)
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for column in range(1, len(columns)):
            self.tree.header().setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)
        self.pages = ReviewPages(self.tree, render, size_of)
        self.ok = button(confirm_text, "danger" if danger else "primary", self.accept)
        self.pages.changed.connect(self._update)
        self.setLayout(vbox(label(title, "h2"), label(summary, wrap=True), self.tree, self.pages.controls,
                            Banner(note, note_kind),
                            hbox(None, button("Cancel", on_click=self.reject), self.ok), margins=(18, 18, 18, 18)))
        self.pages.set_groups(groups)

    def _update(self) -> None:
        count = self.pages.selected_count
        self.ok.setText(self.confirm_text.replace("{n}", fmt_n(count, "file")))
        self.ok.setEnabled(bool(count))

    def selected(self) -> list:
        return [item for items in self.pages.selected().values() for item in items]


class ComparePage(Page):
    title = "Compare & sync"
    subtitle = ("Compare this library with a phone backup, laptop or external drive - up to three libraries. "
                "Matching is by file content, so renamed or reorganised copies still count.")

    def __init__(self, ctx):
        super().__init__(ctx)
        self.result: libsync.Comparison | None = None
        self.view = ("all", 0)
        self.profiles: list[dict] = []
        self._pending_profile = None

        # setup --------------------------------------------------------------------------
        self.a_path = label("", "muted")
        self.paths = [QLineEdit(), QLineEdit()]
        self.paths[0].setPlaceholderText(r"Library B, e.g. E:\Phone backup")
        self.paths[1].setPlaceholderText(r"Library C, e.g. F:\Photos archive")
        browse_b = button("Browse...", on_click=lambda: self._browse(0))
        browse_c = button("Browse...", on_click=lambda: self._browse(1))
        self.add_c = button("+ Add a third library", "link", self._show_c)
        self.remove_c = button("Remove", "link", self._hide_c)
        self.row_c = QWidget()
        self.row_c.setLayout(hbox(self._badge(2), self.paths[1], browse_c, self.remove_c))
        self.row_c.hide()
        self.master = QComboBox()
        self.master.setToolTip("Fingerprints of B and C are cached in this library so the next comparison is fast. "
                               "A compatible Memoria catalogue inside B or C is always reused read-only.")
        self.media_only = QCheckBox("Photos and videos only")
        self.media_only.setChecked(True)
        self.profile = QComboBox()
        self.profile.setMinimumWidth(220)
        self.profile.activated.connect(self._load_profile)
        self.save_profile = button("Save relationship...", on_click=self._save_profile,
                                   tip="Remember these libraries and sync settings, e.g. \"Phone -> Laptop backup\".")
        self.delete_profile = button("Delete", on_click=self._delete_profile)
        self.cmp_btn = button("Compare", "primary", self.run_compare)
        for edit in self.paths:
            edit.textChanged.connect(self._paths_changed)
        setup = vbox(
            hbox(label("Libraries", "h2"), None, label("Saved relationships", "small"), self.profile,
                 self.save_profile, self.delete_profile),
            hbox(self._badge(0), label("This library", ""), self.a_path, None),
            hbox(self._badge(1), self.paths[0], browse_b),
            self.row_c,
            hbox(self.add_c, None, label("Store comparison index in", "small"), self.master, 12, self.media_only,
                 12, self.cmp_btn),
            spacing=8)
        self.body.addWidget(Card(setup))

        # results ------------------------------------------------------------------------
        self.stack = QStackedWidget()
        self.stack.addWidget(EmptyState(
            "\uE895", "Which photos are where?",
            "Add your phone backup, old laptop folder or external drive as library B (and optionally C), then "
            "Compare. You'll see what exists only in each library, what is shared, a folder-to-folder mapping, "
            "and you can copy just the missing files - one way or both ways."))

        self.index_info = label("", "small", wrap=True)
        self.index_info.setTextFormat(Qt.TextFormat.RichText)
        self.venn = VennWidget()
        self.venn.region_clicked.connect(lambda mask: self._set_view(("region", mask)))
        self.filters = QListWidget()
        self.filters.setMinimumHeight(200)
        self.filters.setWordWrap(True)
        self.filters.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.filters.currentItemChanged.connect(self._filter_chosen)
        overview = QWidget()
        overview.setLayout(vbox(label("Overview", "h2"), self.venn,
                                label("Show (or click a region above)", "small"), self.filters,
                                label("Indexes", "small"), self.index_info, spacing=6))
        overview_scroll = scroll(overview)
        overview_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        overview_scroll.setMinimumWidth(280)
        overview_scroll.setMaximumWidth(340)

        self.view_title = label("", "h2", wrap=True)
        self.panes = [SidePane(self, side) for side in range(libsync.MAX_LIBRARIES)]
        pane_row = QWidget()
        pane_row.setLayout(hbox(*self.panes, spacing=8))
        self.entry_info = label("Select a file to see it and where each copy lives.", "small", wrap=True)
        self.entry_info.setTextFormat(Qt.TextFormat.RichText)
        self.preview_img = QLabel()
        self.preview_img.setFixedSize(220, 165)
        self.preview_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_img.setStyleSheet(f"background:{theme.PREVIEW_BG}; border-radius:8px; color:{theme.MUTED};")
        self.preview_open = button("Open", on_click=lambda: self._open_entry(False))
        self.preview_show = button("Show in folder", on_click=lambda: self._open_entry(True))
        self._preview_entry = None
        for b in (self.preview_open, self.preview_show):
            b.setEnabled(False)
        preview_card = Card(hbox(self.preview_img, vbox(self.entry_info, None, hbox(self.preview_open,
                                                                                    self.preview_show, None)),
                                 spacing=12))
        self.preview_bg = LatestCall(self)
        self.preview_bg.result.connect(self._preview_loaded)
        files_tab = QWidget()
        files_tab.setLayout(vbox(self.view_title, pane_row, preview_card, spacing=6, margins=(0, 8, 0, 0)))
        self.map_from, self.map_to = QComboBox(), QComboBox()
        self.map_from.currentIndexChanged.connect(self._render_mapping)
        self.map_to.currentIndexChanged.connect(self._render_mapping)
        self.mapping = QTreeWidget()
        self.mapping.setRootIsDecorated(False)
        self.mapping.setHeaderLabels(["Folder", "Best matching folder", "Shared files", "% of folder", "% of match",
                                      "New files go to (merge)"])
        for column in (0, 1, 5):
            self.mapping.header().setSectionResizeMode(column, QHeaderView.ResizeMode.Stretch)
        mapping_tab = QWidget()
        mapping_tab.setLayout(vbox(
            hbox(label("Folders in", "small"), self.map_from, label("matched to", "small"), self.map_to, None),
            label("Each folder is paired with the folder in the other library that holds most of the same photos. "
                  "When at least half of a folder's files are already there, sync merges new files into that "
                  "folder; otherwise it creates the same folder path as in the source.", "small", wrap=True),
            self.mapping, spacing=6, margins=(0, 8, 0, 0)))
        self.tabs = QTabWidget()
        self.tabs.addTab(files_tab, "Files side by side")
        self.tabs.addTab(mapping_tab, "Folder mapping")

        # actions: one panel acting on the selected region ------------------------------------
        self.sel_title = label("", "h2", wrap=True)
        self.sel_counts = label("", "small", wrap=True)
        self.side_group = QButtonGroup(self)
        self.side_buttons = [QRadioButton() for _ in range(libsync.MAX_LIBRARIES)]
        side_row = QWidget()
        side_layout = vbox(spacing=2)
        for side, radio in enumerate(self.side_buttons):
            self.side_group.addButton(radio, side)
            radio.toggled.connect(self._update_actions)
            side_layout.addWidget(radio)
        side_row.setLayout(side_layout)
        self.type_boxes: dict[str, QCheckBox] = {}
        types_row = QWidget()
        from PySide6.QtWidgets import QGridLayout
        types_layout = QGridLayout()
        types_layout.setContentsMargins(0, 0, 0, 0)
        types_layout.setHorizontalSpacing(10)
        types_layout.setVerticalSpacing(2)
        for index, (kind, title, tip) in enumerate((
                ("photo", "Photos", ""), ("video", "Videos", ""),
                ("sidecar", "Sidecars", "Small edit/metadata files next to photos (.AAE, .XMP…). Apple .AAE files "
                 "hold Photos-app edits; they are often only on the phone backup."),
                ("other", "Other files", ""))):
            box = QCheckBox(title)
            box.setChecked(True)
            box.setToolTip(tip)
            box.toggled.connect(self._update_actions)
            self.type_boxes[kind] = box
            types_layout.addWidget(box, index // 2, index % 2)
        types_row.setLayout(types_layout)

        self.target = QComboBox()
        self.target.setToolTip("Where the copies go. Only content the destination doesn't already have is copied.")
        self.merge = QRadioButton("Merge into matching folders")
        self.merge.setToolTip("New files go into the folder that already holds most of the same photos "
                              "(see Folder mapping).")
        self.mirror = QRadioButton("Recreate the source folders")
        self.mirror.setToolTip("New files go to the same folder path they have in the source library.")
        self.merge.setChecked(True)
        placement = QButtonGroup(self)
        placement.addButton(self.merge)
        placement.addButton(self.mirror)
        self.both_ways = QCheckBox("Also copy back what this library is missing")
        self.copy_summary = label("", "small", wrap=True)
        self.copy_btn = button("Copy…", "primary", self.review_copy)
        self.layout_ref = QComboBox()
        self.layout_ref.setToolTip("Shared files are moved so each sits at the same folder and name as in this library.")
        self.layout_summary = label("", "small", wrap=True)
        self.layout_btn = button("Rearrange…", on_click=self.review_layout)
        self.move_btn = button("Move into a folder…", on_click=self.review_move)
        self.album_btn = button("Make an album…", on_click=self.make_album,
                                tip="Album of these files in this library, to tag, date, edit or export them together.")
        self.remove_summary = label("", "small", wrap=True)
        self.remove_btn = button("Move to Recovery…", "danger", self.review_removal)
        for widget in (self.target, self.layout_ref):
            widget.currentIndexChanged.connect(self._update_actions)
        for widget in (self.merge, self.both_ways):
            widget.toggled.connect(self._update_actions)

        def section(title, *items):
            return vbox(label(title, "small"), *items, spacing=4)
        act_card = Card(vbox(
            label("Act on these files", "small"), self.sel_title, self.sel_counts,
            section("Copies in", side_row), section("File types", types_row),
            section("Copy to another library", hbox(self.target, self.copy_btn), self.merge, self.mirror,
                    self.both_ways, self.copy_summary),
            section("Give the same folder layout as", hbox(self.layout_ref, self.layout_btn), self.layout_summary),
            section("Reorganise or edit", hbox(self.move_btn, self.album_btn, None)),
            section("Delete", hbox(self.remove_btn, None), self.remove_summary),
            HelpToggle("Nothing changes until you review and confirm. Copies never overwrite, moves keep every file, "
                       "and Move to Recovery puts files in that library's own Recovery folder, so everything can be "
                       "undone from History & recovery.", "Safe by design — review first, undo anytime"),
            spacing=10))
        actions = QWidget()
        actions.setLayout(vbox(act_card, None, spacing=10))
        actions_scroll = scroll(actions)
        actions_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        actions_scroll.setMinimumWidth(320)
        actions_scroll.setMaximumWidth(380)
        for combo in (self.target, self.layout_ref):
            combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
            combo.setMinimumContentsLength(12)
            combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        split = QSplitter()
        split.addWidget(overview_scroll)
        split.addWidget(self.tabs)
        split.addWidget(actions_scroll)
        split.setStretchFactor(1, 1)
        split.setChildrenCollapsible(False)
        self.results = split
        self.stack.addWidget(split)
        self.body.addWidget(self.stack, 1)
        self._paths_changed()

    @staticmethod
    def _badge(side: int):
        badge = label(libsync.letter(side), "")
        badge.setFixedWidth(22)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(f"background:{side_colors()[side]};color:white;border-radius:6px;font-weight:600;")
        return badge

    # setup ----------------------------------------------------------------------------------
    def refresh(self) -> None:
        if self.lib is not None:
            self.a_path.setText(str(self.lib.root))
            self.profiles = libsync.load_profiles(self.lib)
            self._fill_profiles()
        if self.result is not None and self._others():
            self.run_compare()

    def on_busy_changed(self, busy: bool) -> None:
        self.cmp_btn.setEnabled(not busy and bool(self._others()))
        self._update_actions()

    def _browse(self, index: int) -> None:
        path = QFileDialog.getExistingDirectory(self, "Choose the library or folder to compare with",
                                                self.paths[index].text() or "")
        if path:
            self.paths[index].setText(os.path.normpath(path))

    def _show_c(self) -> None:
        self.row_c.show()
        self.add_c.hide()
        self._paths_changed()

    def _hide_c(self) -> None:
        self.paths[1].clear()
        self.row_c.hide()
        self.add_c.show()
        self._paths_changed()

    def _others(self) -> list[str]:
        others = [self.paths[0].text().strip()]
        if not self.row_c.isHidden():
            others.append(self.paths[1].text().strip())
        return [path for path in others if path]

    def _paths_changed(self) -> None:
        current = self.master.currentIndex()
        self.master.blockSignals(True)
        self.master.clear()
        self.master.addItem("A - this library", 0)
        for index, text in enumerate(self._others(), 1):
            self.master.addItem(f"{libsync.letter(index)} - {Path(text).name or text}", index)
        self.master.setCurrentIndex(max(0, min(current, self.master.count() - 1)))
        self.master.blockSignals(False)
        self.cmp_btn.setEnabled(not self.busy and bool(self._others()))

    def _fill_profiles(self) -> None:
        self.profile.blockSignals(True)
        self.profile.clear()
        self.profile.addItem("Choose..." if self.profiles else "None saved yet", None)
        for item in self.profiles:
            self.profile.addItem(item["name"], item["name"])
        self.profile.blockSignals(False)
        self.delete_profile.setEnabled(False)

    def profile_data(self) -> dict:
        return {"others": self._others(), "master": self.master.currentData() or 0,
                "media_only": self.media_only.isChecked(),
                "mode": "two-way" if self.both_ways.isChecked() else "one-way",
                "source": self.side_group.checkedId() if self.side_group.checkedId() >= 0 else 1,
                "target": self.target.currentData() if self.target.count() else 0,
                "placement": "merge" if self.merge.isChecked() else "mirror"}

    def _save_profile(self) -> None:
        if not self._others():
            MessageDialog(self, "Choose a library first", "Add library B before saving a relationship.").exec()
            return
        name, ok = QInputDialog.getText(self, "Save relationship", "Name, e.g. Phone -> Laptop (one-way backup):",
                                        text=self.profile.currentData() or "")
        if ok and name.strip():
            self.profiles = libsync.save_profile(self.lib, {"name": name.strip(), **self.profile_data()})
            self._fill_profiles()
            self.profile.setCurrentIndex(self.profile.findData(name.strip()))
            self.delete_profile.setEnabled(True)
            self.ctx.toast_requested.emit(f"Saved \"{name.strip()}\".", "")

    def _delete_profile(self) -> None:
        name = self.profile.currentData()
        if name:
            self.profiles = libsync.delete_profile(self.lib, name)
            self._fill_profiles()

    def _load_profile(self, index: int) -> None:
        name = self.profile.itemData(index)
        profile = next((item for item in self.profiles if item["name"] == name), None)
        self.delete_profile.setEnabled(profile is not None)
        if profile is None:
            return
        others = list(profile.get("others") or [])[:2]
        self.paths[0].setText(others[0] if others else "")
        if len(others) > 1:
            self._show_c()
            self.paths[1].setText(others[1])
        else:
            self._hide_c()
        self.master.setCurrentIndex(max(0, self.master.findData(profile.get("master", 0))))
        self.media_only.setChecked(bool(profile.get("media_only", True)))
        self._pending_profile = profile
        self.run_compare()

    def _apply_profile_actions(self) -> None:
        profile, self._pending_profile = self._pending_profile, None
        if not profile:
            return
        self.both_ways.setChecked(profile.get("mode") == "two-way")
        source = profile.get("source", 1)
        if 0 <= source < len(self.side_buttons) and self.side_buttons[source].isVisible():
            self.side_buttons[source].setChecked(True)
        self.target.setCurrentIndex(max(0, self.target.findData(profile.get("target", 0))))
        (self.mirror if profile.get("placement") == "mirror" else self.merge).setChecked(True)

    # comparing ------------------------------------------------------------------------------
    def run_compare(self) -> None:
        others = self._others()
        if not others:
            self.ctx.toast_requested.emit("Choose library B first.", "")
            return
        lib, master, media_only = self.lib, self.master.currentData() or 0, self.media_only.isChecked()

        def work(progress):
            try:
                return libsync.compare(lib, others, master=master, media_only=media_only, progress=progress)
            finally:
                lib.close_thread()
        self.run("Comparing libraries", work, self.show_result, read_only=True)

    def show_result(self, cmp: libsync.Comparison) -> None:
        previous = self.result
        self.result = cmp
        rows, details = [], []
        kinds = {"library": "this library's catalogue", "catalogue": "its Memoria catalogue (read-only)",
                 "index": "comparison index"}
        for side, (participant, info) in enumerate(zip(cmp.participants, cmp.info)):
            rows.append(
                f"<b style='color:{side_colors()[side]}'>{libsync.letter(side)} · {participant.label}</b>"
                f" - {info.files:,} files, {kinds[info.source]}; {info.reused:,} fingerprints reused, "
                f"{info.hashed:,} read now")
            details.append(f"{libsync.letter(side)}: {participant.root}\n{info.detail}\nIndex: {info.location}")
        rows.append(f"Index kept in {libsync.letter(cmp.master)}. All libraries use the same full-content "
                    "fingerprint, so results are comparable.")
        self.index_info.setText("<br>".join(rows))
        self.index_info.setToolTip("\n\n".join(details))
        self.venn.set_data([participant.label for participant in cmp.participants], cmp.regions())
        for side, pane in enumerate(self.panes):
            pane.setVisible(side < cmp.count)
        keep = {combo: combo.currentData() for combo in (self.target, self.layout_ref, self.map_from, self.map_to)}
        defaults = {self.target: 0, self.layout_ref: 0, self.map_from: 1, self.map_to: 0}
        same_shape = previous is not None and previous.count == cmp.count
        for combo, default in defaults.items():
            combo.blockSignals(True)
            combo.clear()
            for side, participant in enumerate(cmp.participants):
                combo.addItem(f"{libsync.letter(side)} - {participant.label}", side)
            wanted = keep[combo] if same_shape and keep[combo] is not None else default
            combo.setCurrentIndex(max(0, combo.findData(wanted)))
            combo.blockSignals(False)
        if not same_shape:
            self.view = ("all", 0)
        self._apply_profile_actions()
        self._fill_filters()
        self._render_mapping()
        self.stack.setCurrentWidget(self.results)
        self._update_actions()

    def _fill_filters(self) -> None:
        cmp = self.result
        letters = [libsync.letter(side) for side in range(cmp.count)]
        union, inter = " or ".join(letters), " ∩ ".join(letters)
        options = [(f"Everything (in {union})", ("all", 0)), (f"In all {cmp.count} ({inter})", ("every", 0))]
        if cmp.count == 3:
            options.append(("In two or more (shared)", ("shared", 0)))
        options += [(f"Only in {letters[side]}", ("only", side)) for side in range(cmp.count)]
        if cmp.count == 3:   # with two libraries "missing from A" is the same as "only in B"
            options += [(f"Missing from {letters[side]}", ("missing", side)) for side in range(cmp.count)]
        regions = cmp.regions()
        self.filters.blockSignals(True)
        self.filters.clear()
        for text, view in options:
            accept = cmp.predicate(*view)
            contents = sum(value[0] for mask, value in regions.items() if accept(mask))
            size = sum(value[1] for mask, value in regions.items() if accept(mask))
            item = QListWidgetItem(f"{text}\n{fmt_n(contents, 'item')} - {fmt_size(size)}")
            item.setData(ENTRY_ROLE, view)
            self.filters.addItem(item)
        self.filters.blockSignals(False)
        index = next((i for i in range(self.filters.count())
                      if tuple(self.filters.item(i).data(ENTRY_ROLE)) == self.view), None)
        if index is None and self.view[0] != "region":
            index = 0
        if index is not None:
            self.filters.blockSignals(True)
            self.filters.setCurrentRow(index)
            self.filters.blockSignals(False)
            self._set_view(tuple(self.filters.item(index).data(ENTRY_ROLE)))
        else:
            self._set_view(self.view)

    def _filter_chosen(self, current, previous) -> None:
        if current is not None:
            self._set_view(tuple(current.data(ENTRY_ROLE)))

    def _view_text(self, view) -> str:
        kind, value = view
        letters = [libsync.letter(side) for side in range(self.result.count)]
        if kind == "all":
            return "Everything in any library"
        if kind == "every":
            return f"In all of {', '.join(letters)}"
        if kind == "shared":
            return "In two or more libraries"
        if kind == "only":
            return f"Only in {letters[value]}"
        if kind == "missing":
            return f"Missing from {letters[value]} - shown where they exist"
        inside = [letters[side] for side in libsync.bits(value) if side < len(letters)]
        outside = [letter for letter in letters if letter not in inside]
        return f"In {' and '.join(inside)}" + (f", not in {' or '.join(outside)}" if outside else "")

    def _set_view(self, view) -> None:
        if self.result is None:
            return
        self.view = tuple(view)
        if self.view[0] == "region":
            self.filters.blockSignals(True)
            self.filters.setCurrentRow(-1)
            self.filters.blockSignals(False)
            self.venn.select(self.view[1])
        else:
            self.venn.select(None)
        self.view_title.setText(self._view_text(self.view))
        accept = self.result.predicate(*self.view)
        for side in range(self.result.count):
            self.panes[side].show_tree(self.result, accept)
        self.entry_info.setText("Select a file to see it and where each copy lives.")
        self._preview_entry = None
        self.preview_img.setPixmap(QPixmap())
        self.preview_img.setText("")
        for b in (self.preview_open, self.preview_show):
            b.setEnabled(False)
        self._choose_side()
        self._update_actions()

    def _choose_side(self) -> None:
        """Offer only libraries that have files in this view; prefer the one the view is about."""
        cmp = self.result
        accept = cmp.predicate(*self.view)
        counts = [len(cmp.matching(side, accept)) for side in range(cmp.count)]
        kind, value = self.view
        preferred = value if kind == "only" else 0
        current = self.side_group.checkedId()
        for side, radio in enumerate(self.side_buttons):
            radio.blockSignals(True)
            radio.setVisible(side < cmp.count and counts[side] > 0)
            if side < cmp.count:
                radio.setText(f"{libsync.letter(side)} · {cmp.participants[side].label} — {fmt_n(counts[side], 'file')}")
            radio.blockSignals(False)
        if current < 0 or current >= cmp.count or not counts[current] or kind == "only":
            current = preferred if preferred < cmp.count and counts[preferred] else next(
                (s for s in range(cmp.count) if counts[s]), 0)
        self.side_buttons[current].blockSignals(True)
        self.side_buttons[current].setChecked(True)
        self.side_buttons[current].blockSignals(False)

    def show_entry(self, entry, node, side: int) -> None:
        cmp = self.result
        if entry is None:
            if node is not None:
                self.entry_info.setText(
                    f"<b>{libsync.letter(side)}: {node.rel or cmp.participants[side].label}</b><br>{node.matching:,} of "
                    f"{node.total:,} files match this view ({fmt_size(node.bytes)}).")
            return
        from html import escape
        places = []
        for other in range(cmp.count):
            copies = [entry] if other == side else [copy for copy in cmp.copies(entry) if copy.side == other]
            where = "; ".join(escape(copy.rel) for copy in copies[:3]) + (f" (+{len(copies) - 3})" if len(copies) > 3 else "")
            color = side_colors()[other]
            places.append(f"<span style='color:{color}'><b>{libsync.letter(other)}</b></span> "
                          f"{where or '<i>missing</i>'}")
        from datetime import datetime
        when = fmt_date(datetime.fromtimestamp(entry.mtime).isoformat(sep=" "), True) if entry.mtime else ""
        self.entry_info.setText(f"<b>{escape(entry.name)}</b> · {fmt_size(entry.size)} · modified {when}"
                                f"<br>{'<br>'.join(places)}")
        self._preview_entry = entry
        for b in (self.preview_open, self.preview_show):
            b.setEnabled(True)
        self.preview_img.setText("Loading…")
        self.preview_img.setPixmap(QPixmap())
        path, kind = entry.path, libsync.Comparison.kind(entry)
        self.preview_bg.call(lambda: (entry, _preview_image(path, kind)))

    def _preview_loaded(self, result) -> None:
        entry, image = result
        if entry is not self._preview_entry:
            return
        if image is None or image.isNull():
            self.preview_img.setPixmap(QPixmap())
            self.preview_img.setText("No preview for this file")
            return
        self.preview_img.setText("")
        self.preview_img.setPixmap(QPixmap.fromImage(image).scaled(
            self.preview_img.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def _open_entry(self, reveal: bool) -> None:
        entry = self._preview_entry
        if entry is not None:
            (show_in_explorer if reveal else open_path)(entry.path)

    def _render_mapping(self, *_) -> None:
        cmp = self.result
        self.mapping.clear()
        if cmp is None:
            return
        source, target = self.map_from.currentData(), self.map_to.currentData()
        if source is None or target is None or source == target:
            return
        for row in cmp.mapping_rows(source, target)[:5000]:
            destination = cmp.destination_folder(source, target, row.folder, "merge")
            item = QTreeWidgetItem([
                row.folder or "(library root)", row.match or "(library root)" if row.shared else "-",
                f"{row.shared:,} of {row.total:,}", f"{row.coverage:.0%}" if row.shared else "-",
                f"{row.match_coverage:.0%}" if row.shared else "-", destination or "(library root)"])
            if row.shared and row.coverage >= libsync.MAPPING_COVERAGE:
                item.setForeground(1, QColor(theme.OK))
            self.mapping.addTopLevelItem(item)

    # actions --------------------------------------------------------------------------------
    def _side(self) -> int:
        side = self.side_group.checkedId()
        return side if self.result is not None and 0 <= side < self.result.count else 0

    def _types(self) -> set[str]:
        return {kind for kind, box in self.type_boxes.items() if box.isChecked()}

    def _view_entries(self, side: int, typed: bool = True):
        entries = self.result.matching(side, self.result.predicate(*self.view))
        if typed:
            kinds = self._types()
            entries = [entry for entry in entries if libsync.Comparison.kind(entry) in kinds]
        return entries

    def selection(self) -> list[libsync.Entry]:
        """The files the actions apply to: the chosen library's files in this view, of the ticked types."""
        return self._view_entries(self._side()) if self.result is not None else []

    def _excluded(self, source: int, target: int) -> set[str]:
        cmp = self.result
        return set(libsync.load_exclusions(self.lib, cmp.participants[source].root, cmp.participants[target].root))

    def _others_of(self, side: int) -> None:
        """Copy/layout targets are the other libraries."""
        cmp = self.result
        for combo in (self.target, self.layout_ref):
            keep = combo.currentData()
            combo.blockSignals(True)
            combo.clear()
            for other in range(cmp.count):
                if other != side:
                    combo.addItem(f"{libsync.letter(other)} - {cmp.participants[other].label}", other)
            combo.setCurrentIndex(max(0, combo.findData(keep)))
            combo.blockSignals(False)

    def copy_plan(self) -> list[libsync.CopyItem]:
        cmp = self.result
        side, target = self._side(), self.target.currentData()
        if cmp is None or target is None or side == target:
            return []
        placement = "merge" if self.merge.isChecked() else "mirror"
        items = list(cmp.plan_copy(side, target, placement, self.selection(), self._excluded(side, target)))
        if self.both_ways.isChecked():
            items.extend(cmp.plan_copy(target, side, placement, self._view_entries(target), self._excluded(target, side)))
        return items

    def _update_actions(self, *_) -> None:
        cmp = self.result
        controls = (self.copy_btn, self.layout_btn, self.move_btn, self.album_btn, self.remove_btn)
        if cmp is None:
            for control in controls:
                control.setEnabled(False)
            return
        side = self._side()
        self._others_of(side)
        letter_ = libsync.letter(side)
        everything = self._view_entries(side, typed=False)
        chosen = self.selection()
        counts = {kind: 0 for kind in self.type_boxes}
        for entry in everything:
            counts[libsync.Comparison.kind(entry)] += 1
        for kind, box in self.type_boxes.items():
            box.setText(f"{box.text().split(' (')[0]} ({counts[kind]:,})")
        self.sel_title.setText(self._view_text(self.view))
        self.sel_counts.setText(f"{fmt_n(len(chosen), 'file')} in {letter_} ({fmt_size(sum(e.size for e in chosen))}) "
                                f"of {len(everything):,} in this view")
        idle = not self.busy

        items = self.copy_plan()
        wanted = [item for item in items if not item.excluded]
        skipped = len(items) - len(wanted)
        if wanted:
            new_folders = len({(item.target, item.folder.lower()) for item in wanted if not item.merged})
            text = (f"{fmt_n(len(wanted), 'file')} ({fmt_size(sum(item.entry.size for item in wanted))}) to copy"
                    + (f", {fmt_n(new_folders, 'new folder')}" if new_folders else "") + ".")
        else:
            text = "Nothing new to copy - the destination already has this content."
        if skipped:
            text += (f" {fmt_n(skipped, 'file')} ({fmt_size(sum(i.entry.size for i in items if i.excluded))}) "
                     "you chose to keep only where they are - review to change.")
        self.copy_summary.setText(text)
        self.copy_btn.setEnabled(bool(items) and idle)

        ref = self.layout_ref.currentData()
        moves, extra = cmp.plan_match_layout(side, ref, chosen) if ref is not None else ([], 0)
        shared = sum(1 for entry in chosen if entry.hash and ref is not None and entry.mask & (1 << ref))
        self.layout_summary.setText(
            (f"{fmt_n(len(moves), 'file')} in {letter_} would move to the same folder and name as in "
             f"{libsync.letter(ref)}; {shared - len(moves) - extra:,} already match." if moves else
             f"Shared files in {letter_} already sit where they are in {libsync.letter(ref)}." if shared else
             f"No files here are also in {libsync.letter(ref)}.") if ref is not None else "")
        self.layout_btn.setEnabled(bool(moves) and idle)
        self.move_btn.setEnabled(bool(chosen) and idle)
        self.album_btn.setVisible(cmp.participants[side].current)
        self.album_btn.setEnabled(bool(chosen) and idle and all(entry.file_id for entry in chosen[:1]))

        unique = sum(1 for entry in chosen if not any(c.side != side for c in cmp.copies(entry)))
        self.remove_summary.setText(
            (f"{fmt_n(len(chosen), 'file')} to {letter_}'s Recovery folder"
             + (f"; {fmt_n(unique, 'file')} {'has' if unique == 1 else 'have'} no copy in the other libraries"
                if unique else "; every one has a copy in another library") + ".") if chosen else "Nothing selected.")
        self.remove_btn.setEnabled(bool(chosen) and idle)

    def _review_groups(self, pairs, size=lambda pair: pair[0].size):
        folders: dict[str, list] = {}
        for pair in pairs:
            folders.setdefault(pair[0].folder, []).append(pair)
        return [ReviewGroup(folder, folder or "(library root)", members, size=sum(size(m) for m in members))
                for folder, members in sorted(folders.items(), key=lambda item: item[0].lower())]

    @staticmethod
    def _render(pair):
        entry, action = pair[0], pair[1]
        row = QTreeWidgetItem([entry.name, fmt_size(entry.size), action.reason])
        row.setToolTip(0, entry.rel)
        return row

    def review_copy(self) -> None:
        items = self.copy_plan()
        if not items:
            return
        from ..sync_review import CopyReviewDialog
        dialog = CopyReviewDialog(self, self.result, items)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return
        chosen, skipped = dialog.selected(), dialog.skipped()
        if dialog.remember.isChecked():
            cmp = self.result
            for source, target in {(item.entry.side, item.target) for item in items}:
                libsync.update_exclusions(
                    self.lib, cmp.participants[source].root, cmp.participants[target].root,
                    add=[item.entry for item in skipped if (item.entry.side, item.target) == (source, target)],
                    remove=[item.entry for item in chosen if (item.entry.side, item.target) == (source, target)])
            self._update_actions()
        if not chosen:
            self.ctx.toast_requested.emit("Saved. Nothing was copied.", "")
            return
        self.apply_actions(
            "sync", "Copy missing files", [item.action for item in chosen],
            summary=f"{fmt_n(len(chosen), 'file')} ({fmt_size(sum(item.entry.size for item in chosen))}) will be copied.",
            details=["Originals are not moved or changed.", "Each copy is verified byte for byte."],
            confirm_text=f"Copy {fmt_n(len(chosen), 'file')}", confirm_action=False,
            note="Undo removes only the copies made here, and only if they are still unchanged.",
            done_message=lambda r: f"Copied and verified {fmt_n(r.done, 'file')} ({fmt_size(r.bytes)}).",
            rescan=any(item.target == 0 for item in chosen))

    def review_layout(self) -> None:
        cmp, side, ref = self.result, self._side(), self.layout_ref.currentData()
        if cmp is None or ref is None:
            return
        moves, extra = cmp.plan_match_layout(side, ref, self.selection())
        if not moves:
            return
        participant = cmp.participants[side]
        dialog = PlanReviewDialog(
            self, f"Give {libsync.letter(side)} the same folder layout as {libsync.letter(ref)}",
            f"{fmt_n(len(moves), 'file')} in {libsync.letter(side)} · {participant.label} move to the folder and "
            f"name they have in {libsync.letter(ref)} · {cmp.participants[ref].label}. Files only in "
            f"{libsync.letter(side)} stay where they are" + (f"; {fmt_n(extra, 'extra copy', 'extra copies')} of the "
                                                             "same content also stay" if extra else "") + ".",
            self._review_groups(moves), ["File", "Size", "Moves to"], lambda _key, pair: self._render(pair),
            lambda pair: pair[0].size, "Move {n}",
            "Files are moved, not copied: nothing is deleted or overwritten, and names already used get \" (2)\". "
            "Undo puts every file back.", note_kind="trust")
        if dialog.exec() != dialog.DialogCode.Accepted:
            return
        chosen = [action for _, action in dialog.selected()]
        self.apply_actions(
            "sync", f"Match {libsync.letter(side)} to {libsync.letter(ref)}'s folders", chosen,
            summary=f"{fmt_n(len(chosen), 'file')} will be moved within {participant.label}.",
            details=["Each file is checked again before it moves.", "Nothing is overwritten."],
            confirm_text=f"Move {fmt_n(len(chosen), 'file')}", confirm_action=False,
            note="Undo from History & recovery puts each file back.",
            done_message=lambda r: f"Moved {fmt_n(r.done, 'file')} to match {libsync.letter(ref)}.",
            rescan=participant.current)

    def review_move(self) -> None:
        cmp, side = self.result, self._side()
        chosen = self.selection()
        if cmp is None or not chosen:
            return
        root = cmp.participants[side].root
        path = QFileDialog.getExistingDirectory(self, f"Move {len(chosen):,} files into which folder of "
                                                      f"{libsync.letter(side)}?", str(root))
        if not path:
            return
        target = Path(path).resolve()
        if target != root and root not in target.parents:
            MessageDialog(self, "Choose a folder inside the same library",
                          f"Files can only be moved within {libsync.letter(side)} ({root}). Use Copy to another "
                          "library to put them somewhere else.").exec()
            return
        folder = "" if target == root else str(target.relative_to(root))
        moves = cmp.plan_move_into(side, chosen, folder)
        if not moves:
            self.ctx.toast_requested.emit("Those files are already in that folder.", "")
            return
        dialog = PlanReviewDialog(
            self, f"Move into {folder or root.name}",
            f"{fmt_n(len(moves), 'file')} move into {folder or 'the library folder'}, keeping their names.",
            self._review_groups(moves), ["File", "Size", "Reason"], lambda _key, pair: self._render(pair),
            lambda pair: pair[0].size, "Move {n}", "Nothing is overwritten; Undo puts every file back.",
            note_kind="trust")
        if dialog.exec() != dialog.DialogCode.Accepted:
            return
        acts = [action for _, action in dialog.selected()]
        self.apply_actions(
            "sync", f"Move files into {folder or root.name}", acts,
            summary=f"{fmt_n(len(acts), 'file')} will be moved.", details=["Nothing is overwritten."],
            confirm_text=f"Move {fmt_n(len(acts), 'file')}", confirm_action=False,
            note="Undo from History & recovery.", done_message=lambda r: f"Moved {fmt_n(r.done, 'file')}.",
            rescan=cmp.participants[side].current)

    def make_album(self) -> None:
        chosen = [entry for entry in self.selection() if entry.file_id]
        if not chosen:
            return
        name, ok = QInputDialog.getText(self, "Make an album", f"Name for an album of {len(chosen):,} files:",
                                        text=self._view_text(self.view))
        if not ok or not name.strip():
            return
        from ...engine import albums
        lib, ids = self.lib, [entry.file_id for entry in chosen]

        def work(progress):
            try:
                return albums.create(lib, name.strip(), ids)
            finally:
                lib.close_thread()

        def done(album_id):
            self.ctx.albums_changed.emit()
            self.ctx.album_requested.emit(album_id)
        self.run("Making an album", work, done)

    def review_removal(self) -> None:
        cmp, side = self.result, self._side()
        if cmp is None:
            return
        plan = cmp.plan_recycle(side, self.selection())
        if not plan:
            return
        unique = sum(1 for _, _, alone in plan if alone)
        participant = cmp.participants[side]
        where = ("this library's Recovery folder" if participant.current
                 else f"{libsync.letter(side)}'s own Recovery folder ({participant.root}\\.memoria\\recovery)")
        dialog = PlanReviewDialog(
            self, f"Move to Recovery from {libsync.letter(side)} · {participant.label}",
            f"{fmt_n(len(plan), 'file')} ({fmt_size(sum(entry.size for entry, _, _ in plan))}). "
            + (f"{fmt_n(unique, 'file')} {'has' if unique == 1 else 'have'} no copy in the other compared "
               "libraries — untick any you want to keep. " if unique else
               "Each has an identical copy in another library, which is checked again first. "),
            self._review_groups(plan), ["File", "Size", "Why"], lambda _key, item: self._render(item),
            lambda item: item[0].size, "Move {n} to Recovery",
            f"<b>Nothing is deleted.</b> Files move to {where}. Undo them from <b>History &amp; recovery</b> in "
            "this library.", note_kind="warn", danger=True)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return
        chosen = dialog.selected()
        alone = sum(1 for _, _, only in chosen if only)
        self.apply_actions(
            "sync", f"Move to Recovery from {libsync.letter(side)}", [action for _, action, _ in chosen],
            summary=f"{fmt_n(len(chosen), 'file')} will be moved to Recovery.",
            details=([f"{fmt_n(alone, 'file')} exist only here among the compared libraries."] if alone else
                     ["Each kept copy in another library is checked again before a file moves."])
            + [f"Files go to {where}."],
            confirm_text=f"Move {fmt_n(len(chosen), 'file')}", confirm_action=bool(alone),
            require_ack=(f"I understand {fmt_n(alone, 'file')} {'has' if alone == 1 else 'have'} no other copy; "
                         "they go to Recovery and can be restored." if alone else None),
            note="Undo from History & recovery.",
            done_message=lambda r: f"Moved {fmt_n(r.done, 'file')} ({fmt_size(r.bytes)}) to Recovery.",
            rescan=participant.current)
