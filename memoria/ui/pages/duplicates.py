"""Exact duplicates: whole duplicate folders first, then single files. Keep one, move the rest to Recovery."""
from __future__ import annotations

import os
from pathlib import PurePath
from typing import Optional

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QFont, QIcon
from PySide6.QtWidgets import (QAbstractItemView, QHeaderView, QListWidget, QListWidgetItem, QSplitter,
                               QStackedWidget, QTreeWidget, QTreeWidgetItem, QWidget)

from ...engine import duplicates
from .. import theme
from ..widgets import (Banner, EmptyState, PhotoGrid, Preview, Tile, button, fmt_n, fmt_size, hbox, label,
                       show_in_explorer, vbox)
from .base import Page, recovery_note, recycle_summary

COLUMNS = ["Folder", "Total size", "Photos", "Videos", "Other files"]
MAX_CONTENTS = 600


class DuplicatesPage(Page):
    title = "Duplicates"
    subtitle = ("Exact copies, proven by comparing every byte. Whole duplicate folders are shown first, then single "
                "files. Keep one, move the rest to Recovery.")

    def __init__(self, ctx):
        super().__init__(ctx)
        self.find_btn = button("Find duplicates", "primary", self.find)
        self.header_actions.addWidget(self.find_btn)
        self.report: Optional[duplicates.DuplicateReport] = None
        self.loose: list[duplicates.DuplicateGroup] = []
        self.keepers: dict[str, int] = {}               # file group hash → file id kept
        self.folder_keepers: dict[str, str] = {}        # folder match id → folder kept
        self.included: set[str] = set()                 # file group hashes
        self.included_folders: set[str] = set()         # folder match ids
        self._known: set[str] = set()
        self.entries: list[tuple[str, object]] = []     # per list row: ("head"|"folder"|"file", item)

        self.stack = QStackedWidget()
        self.empty = EmptyState("\uE8C8", "Find exact copies",
                                "Memoria compares file contents byte by byte — names don't matter. Folders whose "
                                "files all exist in another folder are shown as whole folders. Only files that share "
                                "a size are read, so this is quick. Nothing is changed until you approve it.",
                                button("Find duplicates", "primary", self.find))
        self.none = EmptyState("\uE73E", "No duplicates", "Every photo and video in this library is unique.")
        self.stack.addWidget(self.empty)
        self.stack.addWidget(self.none)

        self.t_folders = Tile(text="Duplicate folders")
        self.t_copies = Tile(text="Extra file copies")
        self.t_space = Tile(text="Space to free")
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
        self.keep_btn = button("Keep this copy instead", on_click=self._keep_selected)
        self.keep_btn.setEnabled(False)
        self.group_title = label("", "h2")
        self.group_note = label("", "muted", wrap=True)
        file_view = QWidget()
        file_view.setLayout(vbox(hbox(self.group_title, None, self.keep_btn), self.group_note, self.grid, spacing=6))

        # -- whole-folder view
        self.f_title = label("", "h2", wrap=True)
        self.f_note = label("", "muted", wrap=True)
        self.f_keep_btn = button("Keep this folder instead", on_click=self._keep_folder,
                                 tip="Keep the selected folder and move the other copy to Recovery")
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
        folder_view = QWidget()
        folder_view.setLayout(vbox(self.f_title, self.f_note, self.table,
                                   hbox(self.f_contents, None, self.f_open_btn, self.f_keep_btn), self.f_grid, spacing=6))

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
        self.apply_btn = button("Move duplicates to Recovery", "primary", self.apply)
        sel_all = button("Include all", "link", lambda: self._set_all(True))
        sel_none = button("Include none", "link", lambda: self._set_all(False))
        results = QWidget()
        lay = vbox(hbox(self.t_folders, self.t_copies, self.t_space, spacing=12), Banner(recovery_note(), "trust"), split,
                   hbox(sel_all, sel_none, 12, self.summary, None, self.apply_btn), spacing=10)
        lay.setStretchFactor(split, 1)
        results.setLayout(lay)
        self.stack.addWidget(results)
        self.results = results
        self.body.addWidget(self.stack, 1)

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

    def find(self) -> None:
        lib = self.lib
        self.run("Finding duplicates", lambda p: duplicates.find_all(lib, p), self._show)

    def _show(self, report: duplicates.DuplicateReport) -> None:
        self.report = report
        self.ctx.set_badge("duplicates", sum(len(g.files) - 1 for g in report.groups))
        ids = {m.id for m in report.folders}
        self.folder_keepers = {k: v for k, v in self.folder_keepers.items() if k in ids}
        self.included_folders = {m.id for m in report.folders if m.suggested}
        self._rebuild(reset=True)

    def _rebuild(self, reset: bool = False) -> None:
        """Recompute the file groups left once duplicate folders are accounted for, and refill the list."""
        rep = self.report
        self.loose = rep.loose_groups(self.folder_keepers)
        hashes = {g.hash for g in self.loose}
        self.included = hashes if reset else (self.included & hashes) | (hashes - self._known)
        self._known = hashes
        self.keepers = {k: v for k, v in self.keepers.items() if k in hashes}
        if not rep.folders and not self.loose:
            self.stack.setCurrentWidget(self.none)
            return
        self.stack.setCurrentWidget(self.results)
        fk = self.folder_keepers
        self.t_folders.set(f"{sum(len(m.redundant(fk)) for m in rep.folders):,}")
        self.t_copies.set(f"{sum(len(g.files) - 1 for g in self.loose):,}")
        self.t_space.set(fmt_size(sum(m.wasted(fk) for m in rep.folders) + sum(g.wasted for g in self.loose)),
                         color=theme.OK)

        cur = self._current_key()
        self.list.blockSignals(True)
        self.list.clear()
        self.entries = []
        select = None
        if rep.folders:
            self._header(f"DUPLICATE FOLDERS · {len(rep.folders)}")
            for m in rep.folders:
                self._add_folder_item(m)
                if cur == ("folder", m.id):
                    select = self.list.count() - 1
        if self.loose:
            self._header(f"DUPLICATE FILES · {len(self.loose)}" + (" (outside those folders)" if rep.folders else ""))
            for g in self.loose:
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
        inc = m.id in self.included_folders
        if m.kind == "same":
            self.f_title.setText(f"“{red[0].path}” has exactly the same files as “{keep}”" if len(red) == 1
                                 else f"{len(m.folders)} folders with exactly the same files")
        else:
            self.f_title.setText(f"Everything in “{red[0].path}” is also in “{keep}”")
        names = ", ".join(f"“{f.path}”" for f in red)
        note = ("Compared byte by byte, including every sub-folder. File names and layout don't matter; Thumbs.db-style "
                "leftovers and empty files are ignored. ")
        note += (f"{names} ({fmt_size(m.wasted(fk))}) will move to Recovery as a whole folder."
                 if inc else "Not included — nothing here will change. Tick it in the list to include it.")
        if not m.suggested:
            note += f" Not ticked at first because “{keep}” looks like a backup and {names} like the original."
        if m.kind == "same":
            note += " To keep a different one, select it in the table and click “Keep this folder instead”."
        self.f_note.setText(note)
        self.table.blockSignals(True)
        self.table.clear()
        pick = None
        for f in m.folders:
            role = "✓ Kept" if f.path == keep else ("→ To Recovery" if inc else "Left as is")
            subs = f" · {fmt_n(f.subfolders, 'sub-folder')}" if f.subfolders else ""
            it = QTreeWidgetItem([f"{f.path}\n{role}{subs}", fmt_size(f.total_bytes),
                                  f"{f.photos:,}\n{fmt_size(f.photo_bytes)}", f"{f.videos:,}\n{fmt_size(f.video_bytes)}",
                                  f"{f.others:,}\n{fmt_size(f.other_bytes)}"])
            for c in range(1, len(COLUMNS)):
                it.setTextAlignment(c, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            it.setToolTip(0, f"{f.path}\n{m.reason(f, fk)}\n{fmt_n(f.files, 'file')} · {fmt_size(f.total_bytes)}")
            it.setForeground(0, QColor(theme.OK if f.path == keep else theme.WARN if inc else theme.MUTED))
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
        keep = m.keeper_path(self.folder_keepers)
        inc = m.id in self.included_folders
        rows = self._folder_rows(path)
        items = []
        for r in rows[:MAX_CONTENTS]:
            sub = str(PurePath(r["folder"]).relative_to(path)) if r["folder"] != path else ""
            kept = path == keep
            items.append({**dict(r), "caption": r["name"], "sub": sub or "(top of this folder)",
                          "badge": "KEEP" if kept else ("COPY" if inc else ""),
                          "badge_kind": "keep" if kept else "muted", "tip": r["rel_path"]})
        self.f_grid.set_items(items)
        more = f" — showing the first {MAX_CONTENTS:,}" if len(rows) > MAX_CONTENTS else ""
        self.f_contents.setText(f"<b>Inside “{PurePath(path).name}”</b> · {fmt_n(len(rows), 'file')}{more}")
        self.f_keep_btn.setVisible(m.kind == "same")
        self.f_keep_btn.setEnabled(m.kind == "same" and path != keep and not self.busy)

    def _keep_folder(self) -> None:
        m = self._current("folder")
        path = self._selected_folder()
        if m is None or path is None:
            return
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
        return next(f for f in g.files if f["id"] == kid)

    def _show_group(self, g: duplicates.DuplicateGroup) -> None:
        kid = self._keeper(g)["id"]
        inc = g.hash in self.included
        items = []
        for f in g.files:
            keep = f["id"] == kid
            reason = "Kept" if keep else ("Will move to Recovery" if inc else "Left as is")
            items.append({**f, "caption": f["name"], "sub": str(PurePath(f["rel_path"]).parent),
                          "badge": "KEEP" if keep else ("COPY" if inc else ""),
                          "badge_kind": "keep" if keep else "muted",
                          "tip": f"{f['rel_path']}\n{reason}: {g.reasons.get(f['id'], '') if not keep else 'chosen to keep'}"})
        self.grid.set_items(items)
        self.group_title.setText(f"{len(g.files)} identical copies of {self._keeper(g)['name']}")
        why = g.reasons.get(next(f["id"] for f in g.files if f["id"] != kid), "")
        auto = " (chosen by you)" if g.hash in self.keepers else ""
        self.group_note.setText(f"Keeping the copy in “{PurePath(self._keeper(g)['rel_path']).parent or 'library root'}”{auto}. "
                                f"Other copies: {why.lower()}. Select a different photo and click “Keep this copy instead” to change.")
        self.keep_btn.setEnabled(False)

    def _file_selected(self, it: dict) -> None:
        self.preview.show_row(it)
        g = self._current("file")
        if g is not None:
            self.keep_btn.setEnabled(it["id"] != self._keeper(g)["id"])

    def _keep_selected(self) -> None:
        g = self._current("file")
        sel = self.grid.selected_items()
        if g is None or not sel:
            return
        self.keepers[g.hash] = sel[0]["id"]
        self._show_group(g)
        self._update_summary()

    # ------------------------------------------------------------------ selection & apply
    def _toggled(self, item: QListWidgetItem) -> None:
        row = self.list.row(item)
        kind, obj = self.entries[row]
        on = item.checkState() == Qt.CheckState.Checked
        if kind == "folder":
            (self.included_folders.add if on else self.included_folders.discard)(obj.id)
        elif kind == "file":
            (self.included.add if on else self.included.discard)(obj.hash)
        if row == self.list.currentRow():
            self._show_entry(row)
        self._update_summary()

    def _set_all(self, on: bool) -> None:
        for i in range(self.list.count()):
            it = self.list.item(i)
            if it.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                it.setCheckState(Qt.CheckState.Checked if on else Qt.CheckState.Unchecked)

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
        fk = self.folder_keepers
        n_folders = sum(len(m.redundant(fk)) for m in folders)
        parts = []
        if folders:
            parts.append(f"{fmt_n(n_folders, 'folder')} ({fmt_size(sum(m.wasted(fk) for m in folders))})")
        if groups:
            parts.append(f"{fmt_n(sum(len(g.files) - 1 for g in groups), 'copy', 'copies')} "
                         f"({fmt_size(sum(g.wasted for g in groups))})")
        self.summary.setText(" and ".join(parts) + " will move to Recovery" if parts else "Nothing included")
        self.apply_btn.setEnabled(bool(parts) and not self.busy)

    def _plan(self):
        folders, groups = self._chosen()
        return duplicates.plan_cleanup(self.lib, self.report, folders=[m.id for m in folders],
                                       folder_keepers=self.folder_keepers, files=[g.hash for g in groups],
                                       file_keepers=self.keepers)

    def apply(self) -> None:
        if self.report is None or not self._has_selection():
            return
        plan = self._plan()
        files = [a for a in plan if a.op == "recycle"]
        size = sum(a.size for a in files)
        folders, groups = self._chosen()
        wanted = self.report.redundant_folders(self.folder_keepers, {m.id for m in folders})
        planned = {os.path.normcase(a.src) for a in plan if a.op == "rmdir"}
        n_folders = sum(os.path.normcase(str(self.lib.abspath(p))) in planned for p in wanted)
        dropped = len(wanted) - n_folders
        copies = sum(len(g.files) - 1 for g in groups)
        details = []
        if n_folders:
            details.append(f"{fmt_n(n_folders, 'whole folder')} with everything inside. Every file in them has an "
                           "identical copy that stays in the library; the emptied folders are then removed.")
        if dropped:
            details.append(f"{fmt_n(dropped, 'folder')} left out: some of {'its' if dropped == 1 else 'their'} files no "
                           "longer have a copy elsewhere.")
        if copies:
            details.append(f"{fmt_n(copies, 'single copy', 'single copies')} of other files; one copy of each is kept "
                           "where it is.")
        details.append("Right before moving, each file is re-read and compared with the copy being kept. Anything "
                       "that changed is skipped, and a folder is only removed once it is empty.")
        self.apply_actions(
            "duplicates", "Move duplicates to Recovery", plan,
            summary=recycle_summary(len(files), size), details=details,
            confirm_text=f"Move {fmt_n(len(files), 'file')}", note=recovery_note(),
            done_message=lambda r: f"Moved duplicates to Recovery ({fmt_size(r.bytes)})"
                                   + (f", including {fmt_n(n_folders, 'whole folder')}." if n_folders else "."))
