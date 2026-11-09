"""Exact duplicates: explicit review choices, with recoverable removal and remembered keep decisions."""
from __future__ import annotations

import os
import sqlite3
from pathlib import PurePath
from typing import Optional

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QFont, QIcon
from PySide6.QtWidgets import (QAbstractItemView, QCheckBox, QHeaderView, QListWidget, QListWidgetItem, QSplitter,
                               QStackedWidget, QTreeWidget, QTreeWidgetItem, QWidget)

from ...engine import duplicates
from .. import theme
from ..widgets import (Banner, ConfirmDialog, EmptyState, MessageDialog, PhotoGrid, Preview, Tile, button, fmt_n, fmt_size, hbox, label,
                       show_in_explorer, vbox)
from .base import Page, recovery_note, recycle_summary

COLUMNS = ["Folder", "Total size", "Photos", "Videos", "Other files"]
MAX_CONTENTS = 600


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
        file_view = QWidget()
        file_view.setLayout(vbox(hbox(self.group_title, None, self.keep_btn), self.group_note, self.grid,
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
        folder_view = QWidget()
        folder_view.setLayout(vbox(self.f_title, self.f_note, self.table,
                                   hbox(self.f_contents, None, self.f_open_btn, self.f_keep_btn), self.f_grid,
                                   hbox(self.f_remove_one, self.f_remove_all, self.f_keep_all, None), spacing=6))

        self.detail = QStackedWidget()
        self.detail.addWidget(file_view)
        self.detail.addWidget(folder_view)
        self.file_view, self.folder_view = file_view, folder_view
        split = QSplitter()
        split.addWidget(self.list)
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
        self.apply_btn.setEnabled(not busy and self._has_selection())
        self.list.setEnabled(not busy)
        self.show_previous.setEnabled(not busy)
        self.quick_remove.setEnabled(not busy)
        self._choice_buttons()

    def find(self) -> None:
        lib = self.lib
        self.run("Finding duplicates", lambda p: duplicates.find_all(lib, p), self._show)

    def _show(self, report: duplicates.DuplicateReport) -> None:
        try:
            kept = duplicates.kept_choices(self.lib)
        except sqlite3.Error as error:
            self.report = None
            self.stack.setCurrentWidget(self.empty)
            MessageDialog(self, "Previous duplicate choices unavailable", str(error)).exec()
            return
        self.report = report
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
        if rep is None:
            return
        for match in rep.folders:
            if rep.folder_review_key(match) in self.kept:
                self.folder_removals[match.id] = set()
                self.included_folders.discard(match.id)
        covered = [f.path for m in rep.folders if m.id in self.folder_removals for f in m.folders]
        self.loose = rep.loose_groups(self.folder_keepers, covered)
        hashes = {g.hash for g in self.loose}
        self.included = hashes if reset else (self.included & hashes) | (hashes - self._known)
        self._known = hashes
        self.keepers = {g.hash: self.keepers[g.hash] for g in self.loose if
                        self.keepers.get(g.hash) in {f["id"] for f in g.files}}
        self.file_removals = {k: v for k, v in self.file_removals.items() if k in hashes}
        for group in self.loose:
            if duplicates.file_review_key(group) in self.kept:
                self.file_removals[group.hash] = set()
                self.included.discard(group.hash)
        visible_folders = [m for m in rep.folders if self.show_previous.isChecked() or
                           rep.folder_review_key(m) not in self.kept]
        visible_files = [g for g in self.loose if self.show_previous.isChecked() or
                         duplicates.file_review_key(g) not in self.kept]
        duplicate_ids = {f["id"] for g in rep.groups for f in g.files}
        pending = len({r["id"] for m in rep.folders if rep.folder_review_key(m) not in self.kept
                       for folder in m.redundant(self.folder_keepers) for r in rep.folder_files[folder.path]
                       if r["id"] in duplicate_ids})
        pending += sum(len(g.files) - 1 for g in self.loose if duplicates.file_review_key(g) not in self.kept)
        self.ctx.set_badge("duplicates", pending)
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

        cur = self._current_key()
        self.list.blockSignals(True)
        self.list.clear()
        self.entries = []
        select = None
        if visible_folders:
            self._header(f"DUPLICATE FOLDERS · {len(visible_folders)}")
            for m in visible_folders:
                self._add_folder_item(m)
                if cur == ("folder", m.id):
                    select = self.list.count() - 1
        if visible_files:
            self._header(f"DUPLICATE FILES · {len(visible_files)}" + (" (outside those folders)" if rep.folders else ""))
            for g in visible_files:
                self._add_file_item(g)
                if cur == ("file", g.hash):
                    select = self.list.count() - 1
        self.list.blockSignals(False)
        self.list.setCurrentRow(select if select is not None else 1)
        self._update_summary()

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
        names = ", ".join(f.path for f in red)
        rel = f"Same files as “{keep}”" if m.kind == "same" else f"Everything is also in “{keep}”"
        photos, videos = sum(f.photos for f in red), sum(f.videos for f in red)
        it = QListWidgetItem(f"{names}\n{rel}\n{fmt_n(photos, 'photo')} · {fmt_n(videos, 'video')} · "
                             f"{fmt_size(m.wasted(fk))} duplicate")
        sample = self._sample_id(red[0].path)
        pm = self.ctx.thumbs.get(sample) if sample else None
        if pm:
            it.setIcon(QIcon(pm))
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
        pm = self.ctx.thumbs.get(keeper["id"])
        if pm:
            it.setIcon(QIcon(pm))
        it.setFlags(it.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        it.setCheckState(Qt.CheckState.Checked if g.hash in self.included else Qt.CheckState.Unchecked)
        it.setToolTip("Untick to leave this group exactly as it is")
        if duplicates.file_review_key(g) in self.kept:
            it.setText(it.text() + "\nPreviously kept")
        self.list.addItem(it)
        self.entries.append(("file", g))

    # ------------------------------------------------------------------ folders
    def _folder_rows(self, path: str) -> list:
        return self.lib.files("folder=? OR substr(folder, 1, ?)=?", (path, len(path) + 1, path + os.sep))

    def _sample_id(self, path: str) -> Optional[int]:
        r = self.lib.db.execute("SELECT id FROM files WHERE kind!='other' AND (folder=? OR substr(folder, 1, ?)=?) "
                                "ORDER BY kind='video', rel_path LIMIT 1", (path, len(path) + 1, path + os.sep)).fetchone()
        return r[0] if r else None

    def _show_entry(self, row: int) -> None:
        if row < 0 or row >= len(self.entries):
            return
        kind, obj = self.entries[row]
        if kind == "head":
            if row + 1 < self.list.count():
                self.list.setCurrentRow(row + 1)
            return
        self.preview.clear()
        if kind == "folder":
            self.detail.setCurrentWidget(self.folder_view)
            self._show_folder(obj)
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
        keep = m.keeper_path(fk)
        red = m.redundant(fk)
        targets = self._folder_targets(m)
        if m.kind == "same":
            self.f_title.setText(f"“{red[0].path}” has exactly the same files as “{keep}”" if len(red) == 1
                                 else f"{len(m.folders)} folders with exactly the same files")
        else:
            self.f_title.setText(f"Everything in “{red[0].path}” is also in “{keep}”")
        note = ("Compared byte by byte, including every sub-folder. File names and layout don't matter; Thumbs.db-style "
                "leftovers and empty files are ignored. ")
        note += (f"Bulk plan: {len(targets)} folder(s) marked for Recovery."
                 if targets else "No folders marked in the bulk plan.")
        if len(targets) == len(m.folders):
            note += " WARNING: no folder in this group will stay in the library."
        if self.report.folder_review_key(m) in self.kept:
            note += " This previous keep choice is remembered."
        if not m.suggested:
            names = ", ".join(f"“{f.path}”" for f in red)
            note += f" Not ticked at first because “{keep}” looks like a backup and {names} like the original."
        if m.kind == "same":
            note += " Use “Use as bulk keeper” to change that plan."
        note += " Remove buttons act on this group only, not the other marked groups."
        self.f_note.setText(note)
        self.table.blockSignals(True)
        self.table.clear()
        pick = None
        for f in m.folders:
            role = "→ To Recovery" if f.path in targets else "✓ Kept"
            subs = f" · {fmt_n(f.subfolders, 'sub-folder')}" if f.subfolders else ""
            it = QTreeWidgetItem([f"{f.path}\n{role}{subs}", fmt_size(f.total_bytes),
                                  f"{f.photos:,}\n{fmt_size(f.photo_bytes)}", f"{f.videos:,}\n{fmt_size(f.video_bytes)}",
                                  f"{f.others:,}\n{fmt_size(f.other_bytes)}"])
            for c in range(1, len(COLUMNS)):
                it.setTextAlignment(c, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            reason = (("Explicit choice: to Recovery" if f.path in targets else "Kept by your choice")
                      if m.id in self.folder_removals else m.reason(f, fk))
            it.setToolTip(0, f"{f.path}\n{reason}\n{fmt_n(f.files, 'file')} · {fmt_size(f.total_bytes)}")
            it.setForeground(0, QColor(theme.WARN if f.path in targets else theme.OK))
            it.setData(0, Qt.ItemDataRole.UserRole, f.path)
            self.table.addTopLevelItem(it)
            if f.path == (select or red[0].path):
                pick = it
        self.table.setFixedHeight(34 + 44 * len(m.folders))
        self.table.blockSignals(False)
        self.table.setCurrentItem(pick)
        self._folder_row_selected()

    def _selected_folder(self) -> Optional[str]:
        it = self.table.currentItem()
        return it.data(0, Qt.ItemDataRole.UserRole) if it else None

    def _folder_row_selected(self) -> None:
        m = self._current("folder")
        path = self._selected_folder()
        if m is None or path is None:
            return
        targets = self._folder_targets(m)
        rows = self._folder_rows(path)
        items = []
        for r in rows[:MAX_CONTENTS]:
            sub = str(PurePath(r["folder"]).relative_to(path)) if r["folder"] != path else ""
            kept = path not in targets
            items.append({**dict(r), "caption": r["name"], "sub": sub or "(top of this folder)",
                          "badge": "KEEP" if kept else "MOVE",
                          "badge_kind": "keep" if kept else "muted", "tip": r["rel_path"]})
        self.f_grid.set_items(items)
        more = f" — showing the first {MAX_CONTENTS:,}" if len(rows) > MAX_CONTENTS else ""
        self.f_contents.setText(f"<b>Inside “{PurePath(path).name}”</b> · {fmt_n(len(rows), 'file')}{more}")
        self.f_keep_btn.setVisible(m.kind == "same")
        self._choice_buttons()

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

    def _file_targets(self, g) -> set[int]:
        return (self.file_removals.get(g.hash, {f["id"] for f in g.files if f["id"] != self._keeper(g)["id"]})
                if g.hash in self.included else set())

    def _folder_targets(self, match) -> set[str]:
        return (self.folder_removals.get(match.id, {f.path for f in match.redundant(self.folder_keepers)})
                if match.id in self.included_folders else set())

    def _show_group(self, g: duplicates.DuplicateGroup) -> None:
        targets = self._file_targets(g)
        previous = self.grid.selected_items()
        items = []
        for f in g.files:
            keep = f["id"] not in targets
            reason = "Kept" if keep else "Will move to Recovery"
            explanation = ("explicit review choice" if g.hash in self.file_removals else
                           g.reasons.get(f["id"], ""))
            items.append({**f, "caption": f["name"], "sub": str(PurePath(f["rel_path"]).parent),
                          "badge": "KEEP" if keep else "MOVE",
                          "badge_kind": "keep" if keep else "muted",
                          "tip": f"{f['rel_path']}\n{reason}: {explanation}"})
        self.grid.set_items(items)
        self.group_title.setText(f"{len(g.files)} identical copies of {self._keeper(g)['name']}")
        note = f"Bulk plan: {len(targets)} to Recovery; {len(g.files) - len(targets)} kept. "
        if len(targets) == len(g.files):
            note += "WARNING: no shown copy will stay in the library. "
        if duplicates.file_review_key(g) in self.kept:
            note += "This previous keep choice is remembered. "
        self.group_note.setText(note + "Select a copy for Remove 1. Remove buttons act on this group only; "
                                "the bottom button applies all marked groups.")
        if previous:
            index = next((i for i, f in enumerate(g.files) if f["id"] == previous[0]["id"]), None)
            if index is not None:
                self.grid.setCurrentIndex(self.grid.model_.index(index))
        self._choice_buttons()

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
        if not self._remember(duplicates.file_review_key(g), False):
            return
        self.file_removals.pop(g.hash, None)
        self.included.add(g.hash)
        self.keepers[g.hash] = sel[0]["id"]
        self._rebuild()

    def _review_ready(self):
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
        started = self.apply_actions(
            "duplicates", title, plan, summary=recycle_summary(len(files), sum(a.size for a in files)),
            details=details, confirm_text=f"Move {fmt_n(len(files), 'file')}", note=recovery_note(),
            require_ack=("I understand that no shown copy may remain in the library."
                         if all_selected and not quick else None),
            confirm_action=not quick, before_apply=lambda: duplicates.remember_keep(lib, key, False),
            done_message=result_message, after=finished)
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
            if not self._remember(duplicates.file_review_key(group), True):
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
            if on and not self._remember(duplicates.file_review_key(obj), False):
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
        n_folders = sum(len(self._folder_targets(m)) for m in folders)
        folder_size = sum(f.total_bytes for m in folders for f in m.folders if f.path in self._folder_targets(m))
        file_count = sum(len(self._file_targets(g)) for g in groups)
        file_size = sum(g.size * len(self._file_targets(g)) for g in groups)
        parts = []
        if folders:
            parts.append(f"{fmt_n(n_folders, 'folder')} ({fmt_size(folder_size)})")
        if groups:
            parts.append(f"{fmt_n(file_count, 'copy', 'copies')} ({fmt_size(file_size)})")
        self.summary.setText("Bulk plan: " + " and ".join(parts) if parts else "No groups marked for bulk Apply")
        self.t_space.set(fmt_size(folder_size + file_size))
        self.apply_btn.setEnabled(bool(parts) and not self.busy)

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
