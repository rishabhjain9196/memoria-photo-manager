"""Exact duplicates: explicit review choices, with recoverable removal and remembered keep decisions."""
from __future__ import annotations

import os
import sqlite3
from pathlib import PurePath
from typing import Optional

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (QAbstractItemView, QCheckBox, QHeaderView, QListWidget, QListWidgetItem, QSplitter,
                               QStackedWidget, QTreeWidget, QTreeWidgetItem, QWidget)

from ...engine import duplicates
from .. import theme
from ..tasks import LatestCall
from ..widgets import (Banner, ConfirmDialog, EmptyState, MessageDialog, PhotoGrid, Preview, Tile, button, fmt_n, fmt_size, hbox, label,
                       show_in_explorer, vbox)
from .base import Page, recovery_note, recycle_summary

COLUMNS = ["Folder", "Total size", "Photos", "Videos", "Other files"]
GROUP_PAGE = 200
MAX_CONTENTS = 500


class DuplicatesPage(Page):
    title = "Duplicates"
    subtitle = ("Exact copies, proven by comparing every byte. Whole duplicate folders are shown first, then single "
                "files. Choose what to keep; removals go to Recovery, not permanent deletion.")

    def __init__(self, ctx):
        super().__init__(ctx)
        self.find_btn = button("Find duplicates", "primary", self.find)
        self.header_actions.addWidget(self.find_btn)
        self.show_previous = QCheckBox("Show previous choices")
        self.show_previous.setToolTip("Show unchanged groups previously marked Keep both/all. They stay excluded "
                                     "until you explicitly change their choice.")
        self.show_previous.toggled.connect(lambda _: self._rebuild())
        self.header_actions.addWidget(self.show_previous)
        self.report: Optional[duplicates.DuplicateReport] = None
        self.loose: list[duplicates.DuplicateGroup] = []
        self.keepers: dict[str, int] = {}               # file group hash → file id kept
        self.folder_keepers: dict[str, str] = {}        # folder match id → folder kept
        self.included: set[str] = set()                 # file group hashes
        self.included_folders: set[str] = set()         # folder match ids
        self._known: set[str] = set()
        self.file_removals: dict[str, set[int]] = {}
        self.folder_removals: dict[str, set[str]] = {}
        self.kept: set[str] = set()
        self._group_action_running = False
        self.entries: list[tuple[str, object]] = []     # per list row: ("head"|"folder"|"file", item)
        self.visible_groups = []
        self._group_selections = {}
        self.group_offset = self.file_offset = self.folder_offset = self.contents_offset = 0
        self._detail_key = self._contents_path = None
        self._file_keys = {}
        self._closed = False
        self._building = False
        self._large_report = False
        self.review_bg, self.contents_bg = LatestCall(self), LatestCall(self)
        self.review_bg.result.connect(self._review_loaded)
        self.review_bg.failed.connect(self._review_failed)
        self.contents_bg.result.connect(self._contents_loaded)
        self.contents_bg.failed.connect(self._contents_failed)

        self.stack = QStackedWidget()
        self.empty = EmptyState("\uE8C8", "Find exact copies",
                                "Memoria compares file contents byte by byte — names don't matter. Folders whose "
                                "files all exist in another folder are shown as whole folders. Only files that share "
                                "a size are compared; matched folder leftovers are also fingerprinted for safety. "
                                "Nothing is changed until you approve it.",
                                button("Find duplicates", "primary", self.find))
        self.none = EmptyState("\uE73E", "No duplicates", "Every photo and video in this library is unique.")
        self.stack.addWidget(self.empty)
        self.stack.addWidget(self.none)
        self.kept_empty = EmptyState("\uE73E", "Previous keep choices are hidden",
                                    "These unchanged duplicate groups were marked Keep both/all. New or changed "
                                    "groups will appear for review. Removal choices are never replayed automatically.",
                                    button("Show previous choices", on_click=lambda: self.show_previous.setChecked(True)))
        self.stack.addWidget(self.kept_empty)

        self.t_folders = Tile(text="Duplicate folders")
        self.t_copies = Tile(text="Extra file copies")
        self.t_space = Tile(text="Bulk plan size")
        self.list = QListWidget()
        self.list.setIconSize(QSize(48, 48))
        self.list.setFixedWidth(340)
        self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.list.setTextElideMode(Qt.TextElideMode.ElideMiddle)
        self.list.currentRowChanged.connect(self._show_entry)
        self.list.itemChanged.connect(self._toggled)
        self.group_scope = label("", "small", wrap=True)
        self.group_previous = button("Previous groups", on_click=lambda: self._group_step(-1))
        self.group_next = button("Next groups", on_click=lambda: self._group_step(1))
        group_panel = QWidget()
        group_panel.setLayout(vbox(self.list, self.group_scope,
                                   hbox(self.group_previous, self.group_next), spacing=6))
        group_panel.setFixedWidth(360)
        self.preview = Preview(ctx, 300)

        # -- single-file group view
        self.grid = PhotoGrid(ctx.thumbs, cell=170, captions=2)
        self.grid.setSelectionMode(PhotoGrid.SelectionMode.SingleSelection)
        self.grid.current_item.connect(self._file_selected)
        self.keep_btn = button("Use as bulk keeper", on_click=self._keep_selected,
                               tip="Choose the copy retained by the bulk plan below. This does not move files.")
        self.keep_btn.setEnabled(False)
        self.group_title = label("", "h2", wrap=True)
        self.group_note = label("", "muted", wrap=True)
        self.remove_one = button("Remove 1", on_click=lambda: self._choose_file("one"),
                                 tip="Move only the selected copy to Recovery, then refresh this group.")
        self.remove_all = button("Remove both", "danger", on_click=lambda: self._choose_file("all"))
        self.keep_all = button("Keep both", on_click=lambda: self._choose_file("keep"))
        self.file_scope = label("", "small", wrap=True)
        self.file_previous = button("Previous copies", on_click=lambda: self._file_step(-1))
        self.file_next = button("Next copies", on_click=lambda: self._file_step(1))
        file_view = QWidget()
        file_view.setLayout(vbox(hbox(self.group_title, None, self.keep_btn), self.group_note, self.grid,
                                 hbox(self.file_scope, None, self.file_previous, self.file_next),
                                 hbox(self.remove_one, self.remove_all, self.keep_all, None), spacing=6))

        # -- whole-folder view
        self.f_title = label("", "h2", wrap=True)
        self.f_note = label("", "muted", wrap=True)
        self.f_keep_btn = button("Use as bulk keeper", on_click=self._keep_folder,
                                 tip="Choose the folder retained by the bulk plan below. This does not move files.")
        self.f_open_btn = button("Show in folder", on_click=self._open_folder)
        self.table = QTreeWidget()
        self.table.setColumnCount(len(COLUMNS))
        self.table.setHeaderLabels(COLUMNS)
        self.table.setRootIsDecorated(False)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.itemSelectionChanged.connect(self._folder_row_selected)
        self.table.itemDoubleClicked.connect(lambda *_: self._open_folder())
        hdr = self.table.header()
        hdr.setStretchLastSection(False)
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for c in range(1, len(COLUMNS)):
            hdr.setSectionResizeMode(c, QHeaderView.ResizeMode.ResizeToContents)
        self.f_contents = label("")
        self.f_grid = PhotoGrid(ctx.thumbs, cell=130, captions=2)
        self.f_grid.setSelectionMode(PhotoGrid.SelectionMode.SingleSelection)
        self.f_grid.current_item.connect(self.preview.show_row)
        self.f_remove_one = button("Remove 1", on_click=lambda: self._choose_folder("one"),
                                   tip="Move only the selected duplicate folder to Recovery, then refresh the list.")
        self.f_remove_all = button("Remove both", "danger", on_click=lambda: self._choose_folder("all"))
        self.f_keep_all = button("Keep both", on_click=lambda: self._choose_folder("keep"))
        self.folder_scope = label("", "small", wrap=True)
        self.folder_previous = button("Previous folders", on_click=lambda: self._folder_step(-1))
        self.folder_next = button("Next folders", on_click=lambda: self._folder_step(1))
        self.contents_previous = button("Previous files", on_click=lambda: self._contents_step(-1))
        self.contents_next = button("Next files", on_click=lambda: self._contents_step(1))
        folder_view = QWidget()
        folder_view.setLayout(vbox(self.f_title, self.f_note, self.table,
                                   hbox(self.folder_scope, None, self.folder_previous, self.folder_next),
                                   hbox(self.f_contents, None, self.f_open_btn, self.f_keep_btn), self.f_grid,
                                   hbox(self.contents_previous, self.contents_next, None),
                                   hbox(self.f_remove_one, self.f_remove_all, self.f_keep_all, None), spacing=6))

        self.detail = QStackedWidget()
        self.detail.addWidget(file_view)
        self.detail.addWidget(folder_view)
        self.file_view, self.folder_view = file_view, folder_view
        split = QSplitter()
        split.addWidget(group_panel)
        split.addWidget(self.detail)
        split.addWidget(self.preview)
        split.setStretchFactor(1, 1)
        split.setChildrenCollapsible(False)
        self.summary = label("", "")
        self.apply_btn = button("Apply marked groups…", "primary", self.apply,
                                tip="Confirm the combined bulk plan for all included groups. Quick mode does not skip this.")
        self.quick_remove = QCheckBox("Quick remove: skip confirmation popups")
        self.quick_remove.setToolTip("Ask once when enabling, then Remove 1/both/all acts on the current group "
                                     "without further confirmation. Resets with this library window. Errors still appear.")
        self.quick_remove.toggled.connect(self._quick_changed)
        self.quick_warning = Banner(
            "<b>Quick remove is on.</b> Remove buttons move the current group's chosen items immediately, including "
            "all copies. Undo works until Recovery is emptied. Bulk Apply and Empty Recovery still ask.", "warn")
        self.quick_warning.hide()
        self.action_note = label("", "small", wrap=True)
        sel_all = button("Include all", "link", lambda: self._set_all(True),
                         tip="Use suggested removals. Previous Keep choices stay excluded; Remove all is not restored.")
        sel_none = button("Include none", "link", lambda: self._set_all(False),
                          tip="Exclude every group for this review. Use Keep both/all to remember a choice.")
        results = QWidget()
        lay = vbox(hbox(self.t_folders, self.t_copies, self.t_space, spacing=12), Banner(recovery_note(), "trust"),
                   hbox(self.quick_remove, None), self.quick_warning, self.action_note, split,
                   hbox(sel_all, sel_none, 12, self.summary, None, self.apply_btn), spacing=10)
        lay.setStretchFactor(split, 1)
        results.setLayout(lay)
        self.stack.addWidget(results)
        self.results = results
        self.body.addWidget(self.stack, 1)
        self.ctx.runner.finished.connect(self._group_finished)

    # ------------------------------------------------------------------ lifecycle
    def _mark_stale(self) -> None:
        self.review_bg.invalidate()
        self.contents_bg.invalidate()
        self._building = False
        self.preview.clear()
        self.grid.set_items([])
        self.f_grid.set_items([])
        super()._mark_stale()

    def shutdown(self):
        self._closed = True
        self.review_bg.wait()
        self.contents_bg.wait()
        self.preview.shutdown()

    def refresh(self) -> None:
        cached = self.ctx.cached("duplicate_report")
        if cached is not None:
            self._show(cached)
        elif self.report is not None and not self.busy:
            self.find()  # library changed (e.g. after apply/undo) → recompute; hashes are cached so it's fast
        else:
            self.report = None
            self.stack.setCurrentWidget(self.empty)

    def on_busy_changed(self, busy: bool) -> None:
        self.find_btn.setEnabled(not busy)
        self.apply_btn.setEnabled(not busy and not self._building and self._has_selection())
        self.list.setEnabled(not busy and not self._building)
        self.show_previous.setEnabled(not busy)
        self.quick_remove.setEnabled(not busy)
        self._choice_buttons()

    def find(self) -> None:
        lib = self.lib
        generation = self.ctx.generation
        def work(progress):
            try:
                return duplicates.find_all(lib, progress)
            finally:
                lib.close_thread()
        self.run("Finding duplicates", work,
                 lambda report: self._show(report) if (lib, generation) == (self.lib, self.ctx.generation) else None)

    def _show(self, report: duplicates.DuplicateReport) -> None:
        try:
            kept = duplicates.kept_choices(self.lib)
        except sqlite3.Error as error:
            self.report = None
            self.stack.setCurrentWidget(self.empty)
            MessageDialog(self, "Previous duplicate choices unavailable", str(error)).exec()
            return
        self.report = report
        self._large_report = len(report.groups) + len(report.folders) > GROUP_PAGE or sum(
            len(group.files) for group in report.groups) > 5000 or sum(
            len(match.folders) for match in report.folders) > MAX_CONTENTS or sum(
            folder.files for match in report.folders for folder in match.folders) > 5000
        self.kept = kept
        self.file_removals.clear()
        self.folder_removals.clear()
        ids = {m.id for m in report.folders}
        self.folder_keepers = {k: v for k, v in self.folder_keepers.items() if k in ids}
        self.included_folders = {m.id for m in report.folders if m.suggested}
        self._rebuild(reset=True)

    def _rebuild(self, reset: bool = False) -> None:
        """Recompute the file groups left once duplicate folders are accounted for, and refill the list."""
        rep = self.report
        if rep is None or self._closed:
            return
        lib, generation, current = self.lib, self.ctx.generation, self._current_key()
        state = dict(folder_keepers=dict(self.folder_keepers), keepers=dict(self.keepers),
                     included=set(self.included), included_folders=set(self.included_folders),
                     known=set(self._known), file_removals=dict(self.file_removals),
                     folder_removals=dict(self.folder_removals), kept=set(self.kept))
        self.contents_bg.invalidate()
        self.preview.clear()
        self._building = True
        self.list.setEnabled(False)
        self.show_previous.setEnabled(False)
        self.detail.setEnabled(False)
        self.apply_btn.setEnabled(False)
        self.group_scope.setText("Preparing all duplicate groups…")
        previous = self.show_previous.isChecked()
        def work():
            return lib, generation, rep, current, self._build_review(rep, state, reset, previous)
        if self._large_report:
            self.review_bg.call(work)
        else:
            self.review_bg.invalidate()
            self._review_loaded(work())

    @staticmethod
    def _build_review(rep, state, reset, show_previous):
        folder_removals, included_folders = state["folder_removals"], state["included_folders"]
        kept, folder_keepers = state["kept"], state["folder_keepers"]
        folder_keys = {match.id: rep.folder_review_key(match) for match in rep.folders}
        for match in rep.folders:
            if folder_keys[match.id] in kept:
                folder_removals[match.id] = set()
                included_folders.discard(match.id)
        covered = [f.path for m in rep.folders if m.id in folder_removals for f in m.folders]
        loose = rep.loose_groups(folder_keepers, covered)
        hashes = {g.hash for g in loose}
        included = set(hashes) if reset else (state["included"] & hashes) | (hashes - state["known"])
        keepers = {g.hash: state["keepers"][g.hash] for g in loose if
                   state["keepers"].get(g.hash) in {f["id"] for f in g.files}}
        file_removals = {k: v for k, v in state["file_removals"].items() if k in hashes}
        file_keys = {g.hash: duplicates.file_review_key(g) for g in loose}
        for group in loose:
            if file_keys[group.hash] in kept:
                file_removals[group.hash] = set()
                included.discard(group.hash)
        visible_folders = [m for m in rep.folders if show_previous or folder_keys[m.id] not in kept]
        visible_files = [g for g in loose if show_previous or file_keys[g.hash] not in kept]
        duplicate_ids = {f["id"] for g in rep.groups for f in g.files}
        pending = len({r["id"] for m in rep.folders if folder_keys[m.id] not in kept
                       for folder in m.redundant(folder_keepers) for r in rep.folder_files[folder.path]
                       if r["id"] in duplicate_ids})
        pending += sum(len(g.files) - 1 for g in loose if file_keys[g.hash] not in kept)
        return dict(loose=loose, included=included, known=hashes, keepers=keepers, file_removals=file_removals,
                    folder_removals=folder_removals, included_folders=included_folders, file_keys=file_keys,
                    visible_folders=visible_folders, visible_files=visible_files, pending=pending)

    def _review_loaded(self, result):
        lib, generation, rep, current, state = result
        if self._closed or rep is not self.report or (lib, generation) != (self.lib, self.ctx.generation):
            return
        for name in ("loose", "included", "keepers", "file_removals", "folder_removals", "included_folders"):
            setattr(self, name, state[name])
        self._known, self._file_keys = state["known"], state["file_keys"]
        self._building = False
        self.list.setEnabled(not self.busy)
        self.show_previous.setEnabled(not self.busy)
        self.detail.setEnabled(True)
        visible_folders, visible_files = state["visible_folders"], state["visible_files"]
        self.visible_groups = [("folder", match) for match in visible_folders] + [
            ("file", group) for group in visible_files]
        self.ctx.set_badge("duplicates", state["pending"])
        if not visible_folders and not visible_files:
            self.list.blockSignals(True)
            self.entries = []
            self.list.clear()
            self.list.blockSignals(False)
            self.stack.setCurrentWidget(self.kept_empty if rep.folders or self.loose else self.none)
            self._update_summary()
            return
        self.stack.setCurrentWidget(self.results)
        fk = self.folder_keepers
        self.t_folders.set(f"{sum(len(m.redundant(fk)) for m in visible_folders):,}")
        self.t_copies.set(f"{sum(len(g.files) - 1 for g in visible_files):,}")

        selected = next((index for index, (kind, obj) in enumerate(self.visible_groups)
                         if current == (kind, obj.id if kind == "folder" else obj.hash)), None)
        if selected is not None:
            self.group_offset = selected // GROUP_PAGE * GROUP_PAGE
        self.group_offset = min(self.group_offset, (len(self.visible_groups) - 1) // GROUP_PAGE * GROUP_PAGE)
        self._fill_groups(current)
        self._update_summary()

    def _review_failed(self, error):
        self._building = False
        self.group_scope.setText(f"Could not prepare duplicate groups: {error}")
        self.list.setEnabled(False)
        self.show_previous.setEnabled(not self.busy)
        self.detail.setEnabled(False)

    def _fill_groups(self, current=None):
        self.list.blockSignals(True)
        self.list.clear()
        self.entries = []
        select = None
        previous_kind = None
        for kind, obj in self.visible_groups[self.group_offset:self.group_offset + GROUP_PAGE]:
            if kind != previous_kind:
                self._header("DUPLICATE FOLDERS" if kind == "folder" else "DUPLICATE FILES")
                previous_kind = kind
            (self._add_folder_item if kind == "folder" else self._add_file_item)(obj)
            if current == (kind, obj.id if kind == "folder" else obj.hash):
                select = self.list.count() - 1
        self.list.blockSignals(False)
        self.list.setCurrentRow(select if select is not None else 1)
        end = min(len(self.visible_groups), self.group_offset + GROUP_PAGE)
        self.group_scope.setText(f"Groups {self.group_offset + 1:,}–{end:,} of {len(self.visible_groups):,}. "
                                 "Include all/none and bulk Apply cover every page.")
        self.group_previous.setEnabled(self.group_offset > 0)
        self.group_next.setEnabled(end < len(self.visible_groups))

    def _group_step(self, delta):
        if self._building or not self.visible_groups:
            return
        self._group_selections[self.group_offset] = self._current_key()
        self.group_offset = max(0, min((len(self.visible_groups) - 1) // GROUP_PAGE * GROUP_PAGE,
                                       self.group_offset + delta * GROUP_PAGE))
        self._fill_groups(self._group_selections.get(self.group_offset))

    def _current_key(self):
        row = self.list.currentRow()
        if 0 <= row < len(self.entries):
            kind, obj = self.entries[row]
            return (kind, obj.id if kind == "folder" else obj.hash) if kind != "head" else None
        return None

    def _header(self, text: str) -> None:
        it = QListWidgetItem(text)
        it.setFlags(Qt.ItemFlag.NoItemFlags)
        f = QFont(it.font())
        f.setBold(True)
        f.setPointSizeF(max(7.5, f.pointSizeF() - 1))
        it.setFont(f)
        it.setForeground(QColor(theme.MUTED))
        it.setSizeHint(QSize(0, 30))
        self.list.addItem(it)
        self.entries.append(("head", None))

    def _add_folder_item(self, m: duplicates.FolderMatch) -> None:
        fk = self.folder_keepers
        red = m.redundant(fk)
        keep = m.keeper_path(fk)
        names = ", ".join(self.lib.display_path(f.path) for f in red[:3])
        if len(red) > 3:
            names += f", +{len(red) - 3:,} folders"
        display_keep = self.lib.display_path(keep)
        rel = f"Same files as “{display_keep}”" if m.kind == "same" else f"Everything is also in “{display_keep}”"
        photos, videos = sum(f.photos for f in red), sum(f.videos for f in red)
        it = QListWidgetItem(f"{names}\n{rel}\n{fmt_n(photos, 'photo')} · {fmt_n(videos, 'video')} · "
                             f"{fmt_size(m.wasted(fk))} duplicate")
        it.setFlags(it.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        it.setCheckState(Qt.CheckState.Checked if m.id in self.included_folders else Qt.CheckState.Unchecked)
        it.setToolTip("Untick to leave these folders exactly as they are")
        if self.report.folder_review_key(m) in self.kept:
            it.setText(it.text() + "\nPreviously kept")
        self.list.addItem(it)
        self.entries.append(("folder", m))

    def _add_file_item(self, g: duplicates.DuplicateGroup) -> None:
        keeper = self._keeper(g)
        it = QListWidgetItem(f"{keeper['name']}\n{len(g.files)} copies · {fmt_size(g.size)} each")
        it.setFlags(it.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        it.setCheckState(Qt.CheckState.Checked if g.hash in self.included else Qt.CheckState.Unchecked)
        it.setToolTip("Untick to leave this group exactly as it is")
        if self._file_keys.get(g.hash) in self.kept:
            it.setText(it.text() + "\nPreviously kept")
        self.list.addItem(it)
        self.entries.append(("file", g))

    # ------------------------------------------------------------------ folders
    @staticmethod
    def _folder_rows(lib, path, offset):
        condition = "folder=? OR substr(folder, 1, ?)=?"
        params = (path, len(path) + 1, path + os.sep)
        total = lib.db.execute(f"SELECT COUNT(*) FROM files WHERE {condition}", params).fetchone()[0]
        rows = [dict(row) for row in lib.db.execute(
            f"SELECT * FROM files WHERE {condition} ORDER BY rel_path LIMIT ? OFFSET ?",
            (*params, MAX_CONTENTS, offset))]
        return total, rows

    def _show_entry(self, row: int) -> None:
        if row < 0 or row >= len(self.entries):
            return
        kind, obj = self.entries[row]
        if kind == "head":
            if row + 1 < self.list.count():
                self.list.setCurrentRow(row + 1)
            return
        key = kind, obj.id if kind == "folder" else obj.hash
        selected_folder = self._selected_folder() if key == self._detail_key and kind == "folder" else None
        if key != self._detail_key:
            self.file_offset = self.folder_offset = self.contents_offset = 0
            self._contents_path = None
            self.grid.set_items([])
        self._detail_key = key
        self.contents_bg.invalidate()
        self.f_grid.set_items([])
        self.preview.clear()
        if kind == "folder":
            self.detail.setCurrentWidget(self.folder_view)
            self._show_folder(obj, select=selected_folder)
        else:
            self.detail.setCurrentWidget(self.file_view)
            self._show_group(obj)

    def _current(self, kind: str):
        row = self.list.currentRow()
        if 0 <= row < len(self.entries) and self.entries[row][0] == kind:
            return self.entries[row][1]
        return None

    def _show_folder(self, m: duplicates.FolderMatch, select: Optional[str] = None) -> None:
        fk = self.folder_keepers
        match_id = m.id
        keep = m.keeper_path(fk)
        red = m.redundant(fk)
        targets = self._folder_targets(m)
        if m.kind == "same":
            self.f_title.setText(f"“{self.lib.display_path(red[0].path)}” has exactly the same files as "
                                 f"“{self.lib.display_path(keep)}”" if len(red) == 1
                                 else f"{len(m.folders)} folders with exactly the same files")
        else:
            self.f_title.setText(f"Everything in “{self.lib.display_path(red[0].path)}” is also in "
                                 f"“{self.lib.display_path(keep)}”")
        note = ("Compared byte by byte, including every sub-folder. File names and layout don't matter; Thumbs.db-style "
                "leftovers and empty files are ignored. ")
        note += (f"Bulk plan: {len(targets)} folder(s) marked for Recovery."
                 if targets else "No folders marked in the bulk plan.")
        if len(targets) == len(m.folders):
            note += " WARNING: no folder in this group will stay in the library."
        if self.report.folder_review_key(m) in self.kept:
            note += " This previous keep choice is remembered."
        if not m.suggested:
            names = ", ".join(f"“{self.lib.display_path(f.path)}”" for f in red[:3])
            note += f" Not ticked at first because “{self.lib.display_path(keep)}” looks like a backup and {names} like the original."
        if m.kind == "same":
            note += " Use “Use as bulk keeper” to change that plan."
        note += " Remove all/Keep all cover every folder in this group across pages, not other marked groups."
        self.f_note.setText(note)
        self.table.blockSignals(True)
        self.table.clear()
        pick = None
        if select:
            index = next((index for index, folder in enumerate(m.folders) if folder.path == select), 0)
            self.folder_offset = index // MAX_CONTENTS * MAX_CONTENTS
        self.folder_offset = min(self.folder_offset, (len(m.folders) - 1) // MAX_CONTENTS * MAX_CONTENTS)
        visible = m.folders[self.folder_offset:self.folder_offset + MAX_CONTENTS]
        for f in visible:
            role = "→ To Recovery" if f.path in targets else "✓ Kept"
            subs = f" · {fmt_n(f.subfolders, 'sub-folder')}" if f.subfolders else ""
            display_path = self.lib.display_path(f.path)
            it = QTreeWidgetItem([f"{display_path}\n{role}{subs}", fmt_size(f.total_bytes),
                                  f"{f.photos:,}\n{fmt_size(f.photo_bytes)}", f"{f.videos:,}\n{fmt_size(f.video_bytes)}",
                                  f"{f.others:,}\n{fmt_size(f.other_bytes)}"])
            for c in range(1, len(COLUMNS)):
                it.setTextAlignment(c, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            reason = (("Explicit choice: to Recovery" if f.path in targets else "Kept by your choice")
                      if match_id in self.folder_removals else
                      "Kept" if f.path == keep else f"Same files also exist in “{self.lib.display_path(keep)}”")
            it.setToolTip(0, f"{display_path}\n{reason}\n{fmt_n(f.files, 'file')} · {fmt_size(f.total_bytes)}")
            it.setForeground(0, QColor(theme.WARN if f.path in targets else theme.OK))
            it.setData(0, Qt.ItemDataRole.UserRole, f.path)
            self.table.addTopLevelItem(it)
            if f.path == (select or red[0].path):
                pick = it
        self.table.setFixedHeight(34 + 44 * min(5, len(visible)))
        self.table.setCurrentItem(pick or self.table.topLevelItem(0))
        self.table.blockSignals(False)
        end = self.folder_offset + len(visible)
        self.folder_scope.setText(f"Folders {self.folder_offset + 1:,}–{end:,} of {len(m.folders):,}")
        self.folder_previous.setEnabled(self.folder_offset > 0)
        self.folder_next.setEnabled(end < len(m.folders))
        self._folder_row_selected()

    def _folder_step(self, delta):
        match = self._current("folder")
        if match is not None:
            self.folder_offset = max(0, min((len(match.folders) - 1) // MAX_CONTENTS * MAX_CONTENTS,
                                            self.folder_offset + delta * MAX_CONTENTS))
            self._show_folder(match)

    def _selected_folder(self) -> Optional[str]:
        it = self.table.currentItem()
        return it.data(0, Qt.ItemDataRole.UserRole) if it else None

    def _folder_row_selected(self) -> None:
        m = self._current("folder")
        path = self._selected_folder()
        if m is None or path is None:
            return
        if path != self._contents_path:
            self.contents_offset = 0
            self._contents_path = path
        targets, offset = self._folder_targets(m), self.contents_offset
        lib, generation, report = self.lib, self.ctx.generation, self.report
        request = (lib, generation, report, m.id, path, offset)
        self.f_grid.set_items([])
        self.preview.clear()
        self.f_contents.setText(f"Loading files inside “{self.lib.display_path(path)}”…")
        self.contents_previous.setEnabled(False)
        self.contents_next.setEnabled(False)
        self.f_keep_btn.setVisible(m.kind == "same")
        self._choice_buttons()
        kept = path not in targets
        def work():
            try:
                total, rows = self._folder_rows(lib, path, offset)
                return request, kept, total, rows
            finally:
                lib.close_thread()
        self.contents_bg.call(work)

    def _contents_loaded(self, result):
        request, kept, total, rows = result
        lib, generation, report, key, path, offset = request
        match = self._current("folder")
        if (self._closed or self._building or report is not self.report
                or (lib, generation) != (self.lib, self.ctx.generation)
                or not match or match.id != key or path != self._selected_folder() or offset != self.contents_offset):
            return
        items = []
        for r in rows:
            sub = str(PurePath(r["folder"]).relative_to(path)) if r["folder"] != path else ""
            items.append({**dict(r), "caption": r["name"], "sub": sub or "(top of this folder)",
                          "badge": "KEEP" if kept else "MOVE",
                          "badge_kind": "keep" if kept else "muted", "tip": lib.display_path(r["rel_path"])})
        self.f_grid.set_items(items)
        self.f_contents.setText(f"Inside “{self.lib.display_path(path)}” · Files "
                                f"{offset + 1 if rows else 0:,}–{offset + len(rows):,} of {total:,}")
        self.contents_previous.setEnabled(offset > 0)
        self.contents_next.setEnabled(offset + len(rows) < total)

    def _contents_failed(self, error):
        if not self._closed:
            self.f_contents.setText(f"Could not load folder files: {error}")

    def _contents_step(self, delta):
        self.contents_offset = max(0, self.contents_offset + delta * MAX_CONTENTS)
        self._folder_row_selected()

    def _keep_folder(self) -> None:
        if not self._review_ready():
            return
        m = self._current("folder")
        path = self._selected_folder()
        if m is None or path is None:
            return
        if not self._remember(self.report.folder_review_key(m), False):
            return
        self.folder_removals.pop(m.id, None)
        self.included_folders.add(m.id)
        self.folder_keepers[m.id] = path
        self._rebuild()
        self._show_folder(m, select=path)

    def _open_folder(self) -> None:
        path = self._selected_folder()
        if path and self.lib:
            show_in_explorer(self.lib.abspath(path))

    # ------------------------------------------------------------------ single files
    def _keeper(self, g) -> dict:
        kid = self.keepers.get(g.hash, g.keeper_id)
        return next((f for f in g.files if f["id"] == kid), g.files[0])

    def _file_key(self, group):
        return self._file_keys.get(group.hash) or duplicates.file_review_key(group)

    def _file_targets(self, g) -> set[int]:
        if g.hash not in self.included:
            return set()
        if g.hash in self.file_removals:
            return self.file_removals[g.hash]
        keeper = self.keepers.get(g.hash, g.keeper_id)
        return {f["id"] for f in g.files if f["id"] != keeper}

    def _folder_targets(self, match) -> set[str]:
        key = match.id
        if key not in self.included_folders:
            return set()
        if key in self.folder_removals:
            return self.folder_removals[key]
        return {f.path for f in match.redundant(self.folder_keepers)}

    def _show_group(self, g: duplicates.DuplicateGroup) -> None:
        targets = self._file_targets(g)
        previous = self.grid.selected_items()
        items = []
        self.file_offset = min(self.file_offset, (len(g.files) - 1) // MAX_CONTENTS * MAX_CONTENTS)
        visible = g.files[self.file_offset:self.file_offset + MAX_CONTENTS]
        for f in visible:
            keep = f["id"] not in targets
            reason = "Kept" if keep else "Will move to Recovery"
            explanation = ("explicit review choice" if g.hash in self.file_removals else
                           g.reasons.get(f["id"], ""))
            items.append({**f, "caption": f["name"], "sub": self.lib.display_path(f["folder"]) or "(library root)",
                          "badge": "KEEP" if keep else "MOVE",
                          "badge_kind": "keep" if keep else "muted",
                          "tip": f"{f['rel_path']}\n{reason}: {explanation}"})
        self.grid.set_items(items)
        self.group_title.setText(f"{len(g.files)} identical copies of {self._keeper(g)['name']}")
        note = f"Bulk plan: {len(targets)} to Recovery; {len(g.files) - len(targets)} kept. "
        if len(targets) == len(g.files):
            note += "WARNING: no shown copy will stay in the library. "
        if self._file_keys.get(g.hash) in self.kept:
            note += "This previous keep choice is remembered. "
        self.group_note.setText(note + "Select a copy for Remove 1. Remove all/Keep all cover every copy in this "
                                "group across pages; the bottom button applies all marked groups.")
        if previous:
            index = next((i for i, f in enumerate(visible) if f["id"] == previous[0]["id"]), None)
            if index is not None:
                self.grid.setCurrentIndex(self.grid.model_.index(index))
        end = self.file_offset + len(visible)
        self.file_scope.setText(f"Copies {self.file_offset + 1:,}–{end:,} of {len(g.files):,}")
        self.file_previous.setEnabled(self.file_offset > 0)
        self.file_next.setEnabled(end < len(g.files))
        self._choice_buttons()

    def _file_step(self, delta):
        group = self._current("file")
        if group is not None:
            self.file_offset = max(0, min((len(group.files) - 1) // MAX_CONTENTS * MAX_CONTENTS,
                                          self.file_offset + delta * MAX_CONTENTS))
            self.preview.clear()
            self._show_group(group)

    def _file_selected(self, it: dict) -> None:
        self.preview.show_row(it)
        self._choice_buttons()

    def _keep_selected(self) -> None:
        if not self._review_ready():
            return
        g = self._current("file")
        sel = self.grid.selected_items()
        if g is None or not sel:
            return
        if not self._remember(self._file_key(g), False):
            return
        self.file_removals.pop(g.hash, None)
        self.included.add(g.hash)
        self.keepers[g.hash] = sel[0]["id"]
        self._rebuild()

    def _review_ready(self):
        if self._building:
            self.ctx.toast_requested.emit("Wait for duplicate groups to finish updating.", "")
            return False
        if self.busy:
            self.ctx.toast_requested.emit("Wait for the current task to finish before changing duplicate choices.", "")
            return False
        if self.report is None:
            self.ctx.toast_requested.emit("Find duplicates before changing review choices.", "")
            return False
        return True

    def _remember(self, key, keep):
        try:
            duplicates.remember_keep(self.lib, key, keep)
        except sqlite3.Error as error:
            MessageDialog(self, "Duplicate choice not saved", str(error)).exec()
            return False
        (self.kept.add if keep else self.kept.discard)(key)
        return True

    def _quick_changed(self, enabled):
        accepted = False
        if enabled and self._review_ready():
            dialog = ConfirmDialog(
                self, "Enable quick removal for this library window?",
                "Remove 1 and Remove both/all will move the current group's selected items straight to Recovery.",
                ["Other marked groups are not included.",
                 "<b>Remove both/all can leave no copy of that group in the library.</b>",
                 "Undo is available only while Recovery remains intact. Errors and partial failures still appear.",
                 "Bulk Apply, Empty Recovery and other tools keep their confirmations."],
                "Enable quick remove", danger=True,
                require_ack="I understand that quick Remove both/all may leave no copy in the library.")
            accepted = dialog.exec() == dialog.DialogCode.Accepted and dialog.ack.isChecked()
            dialog.deleteLater()
        self.quick_remove.blockSignals(True)
        self.quick_remove.setChecked(accepted)
        self.quick_remove.blockSignals(False)
        self.quick_warning.setVisible(accepted)
        self.action_note.setText("Quick remove enabled for this library window." if accepted else
                                 "Quick remove is off. Group removal asks for confirmation.")

    def _group_finished(self, outcome):
        if self._group_action_running:
            if outcome == "ok" and self.ctx.runner.title.startswith("Preparing "):
                return
            if outcome == "failed":
                self.action_note.setText("Removal did not finish. Review the error details and History.")
            elif outcome == "cancelled":
                self.action_note.setText("Removal stopped. Completed changes remain in History.")
            self._group_action_running = False

    def _remove_group(self, kind, group, targets):
        lib = self.lib
        try:
            if kind == "file":
                plan = duplicates.plan_removal(lib, [group], self.keepers, removals={group.hash: targets})
                key = duplicates.file_review_key(group)
                all_selected = len(targets) == len(group.files)
            else:
                choices = {**self.folder_removals, group.id: targets}
                plan = duplicates.plan_cleanup(lib, self.report, folders=[group.id],
                                               folder_keepers=self.folder_keepers,
                                               file_removals=self.file_removals, folder_removals=choices)
                key = self.report.folder_review_key(group)
                all_selected = len(targets) == len(group.folders)
        except (ValueError, OSError, sqlite3.Error) as error:
            MessageDialog(self, "Duplicate choices need another review", str(error)).exec()
            return
        files = [action for action in plan if action.op == "recycle"]
        if not files:
            self.action_note.setText("Nothing can be moved safely with this choice. Find duplicates again.")
            return
        details = ["<b>Only the current group is affected.</b> Other marked groups are not included.",
                   "Reviewed file information and hashes are checked again. Changed files are skipped.",
                   "The duplicate list refreshes when the operation finishes."]
        if all_selected:
            details.append("<b>Every shown copy in this group is selected. No shown copy will be kept.</b>")
        elif kind == "folder":
            details.append("Only the selected folder is moved; a proven copy is retained outside it.")
        else:
            details.append("Only the selected copy is moved; another proven copy is retained.")
        quick = self.quick_remove.isChecked()
        title = "Move this duplicate group to Recovery" if all_selected else "Move selected duplicate to Recovery"
        def result_message(result):
            return (f"Moved selected items to Recovery ({fmt_size(result.bytes)})." if result.done else
                    "No items were moved.")
        def finished(result):
            self.action_note.setText(("Stopped part-way. " if result.cancelled else "") + result_message(result) +
                                     (" Some items were skipped or failed; review the results."
                                      if result.skipped or result.failed else " Duplicate results are refreshing."))
        def declined():
            self._group_action_running = False
            self.action_note.setText("No files moved. This group's previous choice is unchanged.")
        started = self.apply_actions(
            "duplicates", title, plan, summary=recycle_summary(len(files), sum(a.size for a in files)),
            details=details, confirm_text=f"Move {fmt_n(len(files), 'file')}", note=recovery_note(),
            require_ack=("I understand that no shown copy may remain in the library."
                         if all_selected and not quick else None),
            confirm_action=not quick, before_apply=lambda: duplicates.remember_keep(lib, key, False),
            done_message=result_message, after=finished, on_declined=declined)
        if started:
            self._group_action_running = True
            self.action_note.setText("Checking the selected items and moving them to Recovery…")
        else:
            self.action_note.setText("No files moved. This group's previous choice is unchanged.")

    def _choose_file(self, mode):
        if not self._review_ready():
            return
        group = self._current("file")
        selected = self.grid.selected_items()
        if group is None or (mode == "one" and not selected):
            self.ctx.toast_requested.emit("Select the duplicate copy you want to remove first.", "")
            return
        if mode == "keep":
            if not self._remember(self._file_key(group), True):
                return
            self.file_removals[group.hash] = set()
            self.included.discard(group.hash)
            self._rebuild()
            self.action_note.setText("Keep choice saved. No files moved." +
                                     (" This group stays visible because Show previous choices is on."
                                      if self.show_previous.isChecked() else ""))
        else:
            self._remove_group("file", group, {selected[0]["id"]} if mode == "one" else
                               {f["id"] for f in group.files})

    def _choose_folder(self, mode):
        if not self._review_ready():
            return
        match, selected = self._current("folder"), self._selected_folder()
        if match is None or selected is None:
            self.ctx.toast_requested.emit("Select a duplicate folder first.", "")
            return
        if match.kind != "same" and (mode == "all" or mode == "one" and selected == match.keeper):
            self.ctx.toast_requested.emit("The containing folder can hold unique files. It cannot be removed here.", "")
            return
        if mode == "keep":
            if not self._remember(self.report.folder_review_key(match), True):
                return
            self.folder_removals[match.id] = set()
            self.included_folders.discard(match.id)
            self._rebuild()
            self.action_note.setText("Keep choice saved. No files moved." +
                                     (" This group stays visible because Show previous choices is on."
                                      if self.show_previous.isChecked() else ""))
        else:
            self._remove_group("folder", match, {selected} if mode == "one" else
                               {f.path for f in match.folders})

    def _choice_buttons(self):
        group = self._current("file")
        selected = self.grid.selected_items()
        self.remove_one.setEnabled(group is not None and bool(selected) and not self.busy)
        for btn in (self.remove_all, self.keep_all):
            btn.setEnabled(group is not None and not self.busy)
        self.keep_btn.setEnabled(group is not None and bool(selected) and not self.busy)
        if group:
            suffix = "both" if len(group.files) == 2 else f"all ({len(group.files)})"
            self.remove_all.setText(f"Remove {suffix}")
            self.keep_all.setText(f"Keep {suffix}")
        match, path = self._current("folder"), self._selected_folder()
        self.f_keep_all.setEnabled(match is not None and not self.busy)
        self.f_remove_one.setEnabled(match is not None and path is not None and not self.busy and
                                     (match.kind == "same" or path != match.keeper))
        self.f_remove_all.setEnabled(match is not None and match.kind == "same" and not self.busy)
        self.f_keep_btn.setEnabled(match is not None and match.kind == "same" and path is not None and not self.busy)
        if match:
            suffix = "both" if len(match.folders) == 2 else f"all ({len(match.folders)})"
            self.f_remove_all.setText(f"Remove {suffix}")
            self.f_keep_all.setText(f"Keep {suffix}")
            self.f_remove_all.setToolTip("Only identical folders can all be removed; containing folders may hold unique files.")

    # ------------------------------------------------------------------ selection & apply
    def _toggled(self, item: QListWidgetItem) -> None:
        if not self._review_ready():
            return
        row = self.list.row(item)
        kind, obj = self.entries[row]
        on = item.checkState() == Qt.CheckState.Checked
        if kind == "folder":
            if on and not self._remember(self.report.folder_review_key(obj), False):
                self._rebuild()
                return
            self.folder_removals.pop(obj.id, None)
            (self.included_folders.add if on else self.included_folders.discard)(obj.id)
        elif kind == "file":
            if on and not self._remember(self._file_key(obj), False):
                self._rebuild()
                return
            self.file_removals.pop(obj.hash, None)
            (self.included.add if on else self.included.discard)(obj.hash)
        self._rebuild()

    def _set_all(self, on: bool) -> None:
        if not self._review_ready() or self.report is None:
            return
        self.file_removals.clear()
        self.folder_removals.clear()
        self._known = {g.hash for g in self.report.groups}
        self.included = set(self._known) if on else set()
        self.included_folders = {m.id for m in self.report.folders} if on else set()
        self._rebuild()

    def _chosen(self):
        rep = self.report
        if rep is None:
            return [], []
        return ([m for m in rep.folders if m.id in self.included_folders],
                [g for g in self.loose if g.hash in self.included])

    def _has_selection(self) -> bool:
        folders, groups = self._chosen()
        return bool(folders or groups)

    def _update_summary(self) -> None:
        folders, groups = self._chosen()
        n_folders = folder_size = file_count = file_size = 0
        for match in folders:
            targets = self._folder_targets(match)
            n_folders += len(targets)
            folder_size += sum(folder.total_bytes for folder in match.folders if folder.path in targets)
        for group in groups:
            count = len(self._file_targets(group))
            file_count += count
            file_size += group.size * count
        parts = []
        if folders:
            parts.append(f"{fmt_n(n_folders, 'folder')} ({fmt_size(folder_size)})")
        if groups:
            parts.append(f"{fmt_n(file_count, 'copy', 'copies')} ({fmt_size(file_size)})")
        self.summary.setText(("Bulk plan: " + " and ".join(parts) if parts else
                              "No groups marked for bulk Apply") + " · Across all pages")
        self.t_space.set(fmt_size(folder_size + file_size))
        self.apply_btn.setEnabled(bool(parts) and not self.busy and not self._building)

    def _plan(self):
        folders, groups = self._chosen()
        return duplicates.plan_cleanup(self.lib, self.report, folders=[m.id for m in folders],
                                       folder_keepers=self.folder_keepers, files=[g.hash for g in groups],
                                       file_keepers=self.keepers, file_removals=self.file_removals,
                                       folder_removals=self.folder_removals)

    def apply(self) -> None:
        if not self._review_ready() or self.report is None or not self._has_selection():
            return
        try:
            plan = self._plan()
        except (ValueError, OSError, sqlite3.Error) as error:
            MessageDialog(self, "Duplicate choices need another review", str(error)).exec()
            return
        if not plan:
            self.ctx.toast_requested.emit("Nothing can be moved safely with these choices. Find duplicates again.", "")
            return
        files = [a for a in plan if a.op == "recycle"]
        size = sum(a.size for a in files)
        folders, groups = self._chosen()
        wanted = self.report.redundant_folders(self.folder_keepers, {m.id for m in folders}, self.folder_removals)
        planned = {os.path.normcase(a.src) for a in plan if a.op == "rmdir"}
        n_folders = sum(os.path.normcase(str(self.lib.abspath(p))) in planned for p in wanted)
        dropped = len(wanted) - n_folders
        copies = sum(len(self._file_targets(g)) for g in groups)
        all_selected = (any(len(self._folder_targets(m)) == len(m.folders) for m in folders) or
                        any(len(self._file_targets(g)) == len(g.files) for g in groups))
        details = []
        if n_folders:
            details.append(f"{fmt_n(n_folders, 'whole folder')} selected. Reviewed files move to Recovery; "
                           "folders are removed only once empty. Newly added files are not included in Remove all.")
        if dropped:
            details.append(f"{fmt_n(dropped, 'folder')} left out: some of {'its' if dropped == 1 else 'their'} files no "
                           "longer have a copy elsewhere or are protected by a keep choice.")
        if copies:
            details.append(f"{fmt_n(copies, 'single copy', 'single copies')} selected from individual file groups.")
        details.append("File size, modified time and recorded content hashes are rechecked before moving. "
                       "Changed files are skipped. Normal removal also verifies a copy being kept.")
        if all_selected:
            details.append("<b>Remove both/all is selected: no shown copy will be kept for those groups.</b> "
                           "This can remove the last copy from the library. Undo depends on keeping Recovery intact.")
        self.apply_actions(
            "duplicates", "Move duplicates to Recovery", plan,
            summary=recycle_summary(len(files), size), details=details,
            confirm_text=f"Move {fmt_n(len(files), 'file')}",
            note=("Files move to Recovery, not permanent deletion. Undo is available only while Recovery is intact. "
                  "Do not empty Recovery until you have checked the results and your separate backup."
                  if all_selected else recovery_note()),
            require_ack=("I understand that selected groups may have no copy left in the library."
                         if all_selected else None),
            done_message=lambda r: f"Moved duplicates to Recovery ({fmt_size(r.bytes)})"
                                   + (f", including {fmt_n(n_folders, 'whole folder')}." if n_folders else "."))
