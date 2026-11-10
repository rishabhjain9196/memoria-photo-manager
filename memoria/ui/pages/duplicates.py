"""Choose what moves in one duplicate group; recommendations never override the user's checks."""
from __future__ import annotations

import sqlite3
from pathlib import PurePath

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QCheckBox, QComboBox, QFrame, QHeaderView, QListWidget, QListWidgetItem, QSizePolicy, QSplitter,
                               QStackedWidget, QTreeWidget, QTreeWidgetItem, QWidget)

from ...engine import assets, catalogue, duplicate_cleanup, duplicates
from .. import theme
from ..tasks import LatestCall
from ..widgets import (Banner, ConfirmDialog, MessageDialog, PhotoGrid, Preview, Viewer, button, fmt_n,
                       fmt_size, hbox, label, scroll, vbox)
from .base import Page, recovery_note, recycle_summary

GROUP_PAGE = 200
COPY_PAGE = 200


class ComparisonPane(QFrame):
    changed = Signal(object, bool)

    def __init__(self, ctx):
        super().__init__()
        self.ctx, self.key = ctx, None
        self._recommended = False
        self.setObjectName("card")
        self.setMinimumWidth(180)
        self.title = label("", "h2", wrap=True)
        self.title.setTextFormat(Qt.TextFormat.PlainText)
        self.recommendation = label("", "small", wrap=True)
        self.recommendation.setStyleSheet(f"color:{theme.OK};font-weight:600")
        self.path = label("", "muted", wrap=True)
        self.path.setTextFormat(Qt.TextFormat.PlainText)
        self.facts = label("", "", wrap=True)
        self.remove_check = QCheckBox("Move to Recovery")
        self.remove_check.toggled.connect(self._toggled)
        self.preview = Preview(ctx, 240)
        self.preview.setMinimumWidth(0)
        self.preview.setMaximumWidth(16777215)
        self.preview.image.setMinimumHeight(140)
        self.preview.image.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.preview.title.hide()
        self.preview_scroll = scroll(self.preview)
        self.preview_scroll.setMinimumHeight(160)
        self.preview_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.samples = PhotoGrid(ctx.thumbs, cell=110, captions=1)
        self.samples.activated_item.connect(self._view_sample)
        self.browse = button("Browse folder contents", on_click=self._browse)
        self.setLayout(vbox(self.recommendation, self.title, self.path, self.facts, self.remove_check,
                            self.preview_scroll, self.samples, self.browse, spacing=6, margins=(10, 10, 10, 10)))
        self.layout().setStretchFactor(self.preview_scroll, 1)
        self.layout().setStretchFactor(self.samples, 1)

    def show_member(self, member, selected):
        self.key = member["key"]
        self.title.setText(member["name"])
        self._recommended = member["recommended"]
        path = self.ctx.library.display_path(member["path"])
        self.path.setText(path if len(path) <= 100 else path[:35] + "..." + path[-62:])
        self.path.setToolTip(path)
        self.facts.setText(member["facts"])
        self.remove_check.blockSignals(True)
        self.remove_check.setText("Move shared files only" if member.get("shared_only") else "Move to Recovery")
        self.remove_check.setChecked(selected)
        self.remove_check.blockSignals(False)
        self.update_intent()
        folder = member["kind"] == "folder"
        self.preview_scroll.setVisible(not folder)
        self.samples.setVisible(folder)
        self.browse.setVisible(folder)
        if folder:
            self.preview.clear()
            self.samples.set_items(member.get("samples", []))
        else:
            self.samples.set_items([])
            self.preview.show_row(member["row"])

    def clear(self):
        self.key = None
        self.preview.clear()
        self.samples.set_items([])

    def update_intent(self):
        selected = self.remove_check.isChecked()
        text = ("Recommended keep - overridden" if selected else "Recommended to keep") if self._recommended else (
            "Selected for Recovery" if selected else "Kept by you")
        self.recommendation.setText(text)
        self.recommendation.setStyleSheet(f"color:{theme.WARN if selected else theme.OK};font-weight:600")

    def _toggled(self, checked):
        self.update_intent()
        self.changed.emit(self.key, checked)

    def _browse(self):
        if isinstance(self.key, str):
            self.ctx.browse_requested.emit(catalogue.Filters(folder=self.key, kind="all"))

    def _view_sample(self, row):
        items = self.samples.items()
        viewer = Viewer(self, self.ctx, items, next(i for i, item in enumerate(items) if item["id"] == row["id"]))
        viewer.resize(1100, 780)
        viewer.exec()

    def shutdown(self):
        self.preview.shutdown()


class DuplicatesPage(Page):
    title = "Duplicates"
    subtitle = ("Review exact copies by folder or individually. Group cleanup keeps a verified copy; "
                "selected-copy removal affects only the comparison shown.")

    def __init__(self, ctx):
        super().__init__(ctx)
        self.report = None
        self.groups, self.entries, self.members = [], [], []
        self._keys, self.kept, self.selected = {}, set(), set()
        self._current_group = None
        self._signature = None
        self._current_collection = None
        self.file_choices, self.folder_choices = {}, {}
        self.group_offset = self.copy_offset = 0
        self.set_offset = 0
        self._token = 0
        self._closed = self._loading = self._moving = False
        self._selection_plan = None
        self.find_btn = button("Find duplicates", "primary", self.find)
        self.show_previous = QCheckBox("Show kept groups")
        self.show_previous.toggled.connect(lambda _: self._show(self.report) if self.report is not None else None)
        self.header_actions.addWidget(self.find_btn)
        self.header_actions.addWidget(self.show_previous)
        self.grouping = QComboBox()
        self.grouping.addItem("Group exact files by folders", "folders")
        self.grouping.addItem("Individual duplicate sets", "individual")
        self.grouping.setToolTip("Folder grouping includes partial overlap and repeated files within one folder; "
                                 "it does not treat different-looking files as duplicates.")
        self.grouping.currentIndexChanged.connect(lambda _: self._show(self.report) if self.report is not None else None)

        self.list = QListWidget()
        self.list.setMinimumWidth(220)
        self.list.setMaximumWidth(310)
        self.list.setTextElideMode(Qt.TextElideMode.ElideMiddle)
        self.list.currentRowChanged.connect(self._select_group)
        self.group_scope = label("", "small", wrap=True)
        self.group_previous = button("Previous", on_click=lambda: self._group_step(-1))
        self.group_next = button("Next", on_click=lambda: self._group_step(1))
        left = QWidget()
        left.setLayout(vbox(self.grouping, self.list, self.group_scope, hbox(self.group_previous, self.group_next), spacing=6))

        self.case_title = label("Find duplicates to begin", "h2", wrap=True)
        self.case_note = label("", "muted", wrap=True)
        self.detail = QStackedWidget()
        self.empty = label("Select a group on the left.", "muted", wrap=True)
        self.detail.addWidget(self.empty)
        self.panes = [ComparisonPane(ctx) for _ in range(3)]
        for pane in self.panes:
            pane.changed.connect(self._checked)
        self.pane_view = QWidget()
        self.pane_view.setLayout(hbox(*self.panes, spacing=8))
        self.detail.addWidget(self.pane_view)

        self.copies = QTreeWidget()
        self.copies.setHeaderLabels(["Move", "Copy / location", "Size", "Recommendation"])
        self.copies.setRootIsDecorated(False)
        self.copies.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.copies.itemChanged.connect(self._table_checked)
        self.copies.currentItemChanged.connect(self._table_preview)
        self.copy_scope = label("", "small", wrap=True)
        self.copy_previous = button("Previous copies", on_click=lambda: self._copy_step(-1))
        self.copy_next = button("Next copies", on_click=lambda: self._copy_step(1))
        self.many_preview = ComparisonPane(ctx)
        self.many_preview.changed.connect(self._checked)
        table_panel = QWidget()
        table_panel.setLayout(vbox(self.copies, self.copy_scope,
                                   hbox(self.copy_previous, None, self.copy_next), spacing=6))
        self.many_view = QSplitter()
        self.many_view.addWidget(table_panel)
        self.many_view.addWidget(self.many_preview)
        self.many_view.setStretchFactor(0, 2)
        self.many_view.setStretchFactor(1, 1)
        self.detail.addWidget(self.many_view)
        self.collection_title = label("", "h2", wrap=True)
        self.collection_scope = label("", "small", wrap=True)
        self.sets = QTreeWidget()
        self.sets.setHeaderLabels(["Exact duplicate set", "Copies", "Redundant size"])
        self.sets.setRootIsDecorated(False)
        self.sets.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.sets.setMaximumHeight(110)
        self.sets.currentItemChanged.connect(self._select_set)
        self.set_previous = button("Previous sets", on_click=lambda: self._set_step(-1))
        self.set_next = button("Next sets", on_click=lambda: self._set_step(1))
        self.collection_panel = QWidget()
        collection_header = hbox(self.collection_title, None)
        collection_header.setStretch(0, 1)
        collection_footer = hbox(self.collection_scope, None, self.set_previous, self.set_next)
        collection_footer.setStretch(0, 1)
        self.collection_panel.setLayout(vbox(collection_header, self.sets, collection_footer, spacing=4))
        self.collection_panel.hide()
        self.single_set_btn = button("Move this set only...", on_click=self._apply_current_set,
                                     tip="Move checked copies from only the highlighted set, not the other sets in this folder group.")
        self.single_set_btn.hide()
        comparison_header = hbox(self.case_title, None, self.single_set_btn)
        comparison_header.setStretch(0, 1)
        right = QWidget()
        right.setLayout(vbox(self.collection_panel, comparison_header, self.case_note, self.detail, spacing=6))
        split = QSplitter()
        split.addWidget(left)
        split.addWidget(right)
        split.setStretchFactor(1, 1)
        split.setChildrenCollapsible(False)

        self.selection_note = label("Nothing selected.", "", wrap=True)
        self.action_note = label("", "small", wrap=True)
        self.move_btn = button("Move selected to Recovery", "primary", self.apply)
        self.clean_all_btn = button("Clean all exact groups...", on_click=self.clean_all)
        self.clean_all_btn.setToolTip("Review one combined plan across every page. Always keeps a verified copy "
                                     "and respects kept groups; never deletes every copy.")
        self.keep_all = button("Keep these copies", on_click=self.keep)
        self.quick_remove = QCheckBox("Quick remove")
        self.quick_remove.setToolTip("Optional, this window only. Linked parts and subset-side changes still require review.")
        self.quick_remove.toggled.connect(self._quick_changed)
        self.quick_warning = label("Quick remove is on. Ordinary exact-copy selections act without another popup.",
                                   "small", wrap=True)
        self.quick_warning.hide()
        self.body.addWidget(Banner("Checked = move to Recovery. Unchecked = keep. Recommendations are optional.", "info"))
        self.body.addWidget(split, 1)
        self.body.addWidget(self.selection_note)
        self.body.addWidget(self.quick_warning)
        self.body.addWidget(self.action_note)
        self.body.addLayout(hbox(self.quick_remove, self.keep_all, None, self.clean_all_btn, self.move_btn))

        self.groups_bg, self.detail_bg, self.plan_bg = LatestCall(self), LatestCall(self), LatestCall(self)
        self.groups_bg.result.connect(self._groups_ready)
        self.detail_bg.result.connect(self._members_ready)
        self.plan_bg.result.connect(self._plan_ready)
        for worker in (self.groups_bg, self.detail_bg, self.plan_bg):
            worker.failed.connect(self._failed)
        ctx.runner.finished.connect(self._finished)
        self.on_busy_changed(False)

    def _mark_stale(self):
        self._token += 1
        for worker in (self.groups_bg, self.detail_bg, self.plan_bg):
            worker.invalidate()
        self._selection_plan = None
        for pane in (*self.panes, self.many_preview):
            pane.clear()
        super()._mark_stale()

    def shutdown(self):
        self._closed = True
        for worker in (self.groups_bg, self.detail_bg, self.plan_bg):
            worker.wait()
        for pane in (*self.panes, self.many_preview):
            pane.shutdown()

    def refresh(self):
        cached = self.ctx.cached("duplicate_report")
        if cached is not None:
            self._show(cached)
        elif self.report is not None and not self.busy:
            self.find()

    def find(self):
        lib = self.lib
        self.run("Finding duplicates", lambda progress: duplicates.find_all(lib, progress), self._show)

    def on_busy_changed(self, busy):
        self.find_btn.setEnabled(not busy)
        self.show_previous.setEnabled(not busy)
        self.grouping.setEnabled(not busy and not self._loading)
        self.quick_remove.setEnabled(not busy)
        self.list.setEnabled(not busy and not self._loading)
        self.group_previous.setEnabled(not busy and not self._loading and self.group_offset > 0)
        self.group_next.setEnabled(not busy and not self._loading and
                                   self.group_offset + GROUP_PAGE < len(self.groups))
        self.detail.setEnabled(not busy and not self._loading)
        self.collection_panel.setEnabled(not busy and not self._loading)
        collection = self._current_collection is not None
        current_ready = self._selection_plan is not None and self._selection_plan["files"] > 0
        self.single_set_btn.setVisible(collection)
        self.single_set_btn.setEnabled(not busy and not self._loading and current_ready)
        self.clean_all_btn.setEnabled(not busy and not self._loading and self.report is not None
                                      and bool(self.report.groups))
        self.keep_all.setEnabled(not busy and self._current_group is not None and not self._loading)
        self.keep_all.setText("Keep this set" if collection else "Keep these copies")
        self.move_btn.setText("Move folder group to Recovery..." if collection else "Move selected to Recovery")
        self.move_btn.setToolTip(
            "Review redundant copies across every set/page in this folder group. Keeps verified survivors; "
            "saved keeps and unchecked copies are protected. Always confirms the combined total."
            if collection else "Move only the checked copies in the comparison shown.")
        self.move_btn.setEnabled(not busy and not self._loading and (collection or current_ready))

    @staticmethod
    def _group_key(kind, group):
        return kind, group.hash if kind == "file" else group.id

    def _show(self, report):
        if self.report is not report:
            self.file_choices.clear()
            self.folder_choices.clear()
        self.report = report
        self.detail_bg.invalidate()
        self.plan_bg.invalidate()
        self._token += 1
        token, generation, show_kept, lib = self._token, self.ctx.generation, self.show_previous.isChecked(), self.lib
        grouped = self.grouping.currentData() == "folders"
        self._loading = True
        self._selection_plan = None
        self.on_busy_changed(self.busy)
        self.case_title.setText("Preparing comparisons...")
        def work():
            try:
                kept = duplicates.kept_choices(lib)
                groups = [("folder", group) for group in report.folders]
                groups += [("file", group) for group in report.loose_groups()]
                keys = {self._group_key(kind, group): report.folder_review_key(group) if kind == "folder"
                        else duplicates.file_review_key(group) for kind, group in groups}
                visible = [(kind, group) for kind, group in groups
                           if show_kept or keys[self._group_key(kind, group)] not in kept]
                if grouped:
                    folders = [(kind, group) for kind, group in visible if kind == "folder"]
                    collections = duplicate_cleanup.group_by_folders([group for kind, group in visible if kind == "file"])
                    visible = folders + [("collection", collection) if len(collection.groups) > 1
                                         else ("file", collection.groups[0]) for collection in collections]
                duplicate_ids = {row["id"] for group in report.groups for row in group.files}
                folder_ids = {row["id"] for kind, group in groups if kind == "folder"
                              and keys[self._group_key(kind, group)] not in kept
                              for folder in group.redundant() for row in report.folder_files[folder.path]
                              if row["id"] in duplicate_ids}
                pending = len(folder_ids) + sum(len(group.files) - 1 for kind, group in groups if kind == "file"
                                               and keys[self._group_key(kind, group)] not in kept)
                return token, generation, kept, keys, visible, pending
            finally:
                lib.close_thread()
        self.groups_bg.call(work)

    def _groups_ready(self, result):
        token, generation, kept, keys, groups, pending = result
        if self._closed or token != self._token or generation != self.ctx.generation:
            return
        self.kept, self._keys, self.groups = kept, keys, groups
        self.group_offset = 0
        self._loading = False
        self.ctx.set_badge("duplicates", pending)
        self._render_groups()

    def _render_groups(self):
        self.list.blockSignals(True)
        self.list.clear()
        self.entries = self.groups[self.group_offset:self.group_offset + GROUP_PAGE]
        for kind, group in self.entries:
            if kind == "folder":
                names = " / ".join(folder.name for folder in group.folders[:2])
                text = f"{names}\n{'Subset' if group.kind == 'inside' else 'Matching content'} - {len(group.folders)} folders"
            elif kind == "collection":
                names = [self.lib.display_path(path) or "Library root" for path in group.folders]
                heading = "Within " + names[0] if len(names) == 1 else "Shared files: " + " / ".join(names[:2])
                if len(names) > 2:
                    heading += f" + {len(names) - 2} folders"
                text = f"{heading}\n{len(group.groups):,} exact sets - {fmt_size(group.wasted)} redundant"
            else:
                text = f"{group.files[0]['name']}\nExact duplicate files - {len(group.files)} copies"
            if kind != "collection" and self._keys[self._group_key(kind, group)] in self.kept:
                text += " - kept"
            item = QListWidgetItem(text)
            if kind == "collection":
                item.setToolTip("\n".join(self.lib.display_path(path) or "Library root" for path in group.folders[:12])
                                + "\nOnly byte-identical file sets are grouped. Unique files stay.")
            self.list.addItem(item)
        self.list.blockSignals(False)
        end = self.group_offset + len(self.entries)
        self.group_scope.setText(f"{self.group_offset + 1 if self.entries else 0}-{end} of {len(self.groups):,} groups")
        self.group_previous.setEnabled(self.group_offset > 0)
        self.group_next.setEnabled(end < len(self.groups))
        if self.entries:
            self.list.setCurrentRow(0)
        else:
            self._current_group = None
            self._current_collection = None
            self.collection_panel.hide()
            self._selection_plan = None
            self.members = []
            self.detail.setCurrentWidget(self.empty)
            self.case_title.setText("Kept groups are hidden" if self.kept else "No duplicate groups found")
            self.case_note.setText("Show kept groups to review previous choices." if self.kept else "")
            self.selection_note.setText("Nothing selected.")
        self.on_busy_changed(self.busy)

    def _group_step(self, direction):
        self.group_offset = max(0, self.group_offset + direction * GROUP_PAGE)
        self._render_groups()

    def _select_group(self, index):
        if not 0 <= index < len(self.entries):
            return
        kind, group = self.entries[index]
        self._current_collection = group if kind == "collection" else None
        self.collection_panel.setVisible(kind == "collection")
        if kind == "collection":
            self.set_offset = 0
            self.collection_title.setText("Duplicates within one folder" if len(group.folders) == 1 else
                                          "Shared exact files between folders")
            self._render_sets()
            return
        self._open_comparison(kind, group)

    def _render_sets(self):
        collection = self._current_collection
        if collection is None:
            return
        self.sets.blockSignals(True)
        self.sets.clear()
        shown = collection.groups[self.set_offset:self.set_offset + GROUP_PAGE]
        for group in shown:
            item = QTreeWidgetItem([group.files[0]["name"], str(len(group.files)), fmt_size(group.wasted)])
            item.setData(0, Qt.ItemDataRole.UserRole, group)
            self.sets.addTopLevelItem(item)
        self.sets.blockSignals(False)
        self.collection_scope.setText(
            f"{self.set_offset + 1}-{self.set_offset + len(shown)} of {len(collection.groups):,} exact sets. "
            "The main action cleans this whole folder group, across all pages, keeping verified copies.")
        self.set_previous.setEnabled(self.set_offset > 0)
        self.set_next.setEnabled(self.set_offset + GROUP_PAGE < len(collection.groups))
        if shown:
            self.sets.setCurrentItem(self.sets.topLevelItem(0))

    def _select_set(self, current, previous):
        if current is not None:
            self._open_comparison("file", current.data(0, Qt.ItemDataRole.UserRole))

    def _set_step(self, direction):
        self.set_offset = max(0, self.set_offset + direction * GROUP_PAGE)
        self._render_sets()

    def _open_comparison(self, kind, group):
        self.plan_bg.invalidate()
        self._current_group = (kind, group)
        self._signature = self._keys[self._group_key(kind, group)]
        self._token += 1
        token, generation, lib, report = self._token, self.ctx.generation, self.lib, self.report
        self._selection_plan = None
        self._loading = True
        self.copy_offset = 0
        self.case_title.setText("Loading comparison...")
        self.selection_note.setText("Calculating shared and unique content...")
        self.on_busy_changed(self.busy)
        def work():
            try:
                if kind == "file":
                    members = [{"key": row["id"], "name": row["name"], "path": row["rel_path"], "kind": "file",
                                "size": row["size"], "row": row, "recommended": row["id"] == group.keeper_id,
                                "facts": f"{fmt_size(row['size'])} - byte-identical content\n"
                                         + group.reasons.get(row["id"], "Choose the location you prefer to keep.")
                                         .replace("Kept: ", "Recommendation: ", 1)}
                               for row in group.files]
                    title = "Exact duplicate files"
                    note = "Full-content hashes match. Keep the recommended copy, override it, or select every copy."
                else:
                    members = []
                    for item in duplicates.folder_comparison(report, group):
                        folder = item["folder"]
                        large = group.kind == "inside" and folder.path == group.folders[1].path
                        facts = (f"{fmt_n(folder.files, 'file')} - {fmt_size(folder.total_bytes)} total\n"
                                 f"Shared: {len(item['shared']):,} files ({fmt_size(item['shared_bytes'])})\n"
                                 f"Unique / unmatched: {len(item['unique']):,} files ({fmt_size(item['unique_bytes'])})")
                        if large:
                            facts += "\nOnly shared files can be moved. Unique files and this folder stay."
                            if item["unique"]:
                                facts += "\nUnique examples: " + ", ".join(row["name"] for row in item["unique"][:3])
                        members.append({"key": folder.path, "path": folder.path, "name": folder.name, "kind": "folder",
                                        "size": folder.total_bytes, "recommended": folder.path == group.keeper,
                                        "shared_only": large, "facts": facts, "samples": []})
                    title = "Subset: the smaller folder's content is inside the larger" if group.kind == "inside" else \
                        "Matching folder content - 100% meaningful-content overlap"
                    note = ("The smaller folder is selected by default. Selecting the larger moves shared content only; "
                            "unique files stay. Selecting both removes shared copies on both sides."
                            if group.kind == "inside" else
                            "File names and layout may differ. System leftovers and empty files are ignored for the match.")
                return token, generation, members, title, note
            finally:
                lib.close_thread()
        self.detail_bg.call(work)

    def _members_ready(self, result):
        token, generation, members, title, note = result
        if self._closed or token != self._token or generation != self.ctx.generation:
            return
        self.members = members
        kind, group = self._current_group
        choices = self.file_choices.get(group.hash) if kind == "file" else self.folder_choices.get(group.id)
        self.selected = (set() if self._signature in self.kept else set(choices) if choices is not None
                         else {m["key"] for m in members if not m["recommended"]})
        self.case_title.setText(title)
        self.case_note.setText(note + " Checked means move; unchecked means keep.")
        self._loading = False
        if len(members) <= 3:
            self.detail.setCurrentWidget(self.pane_view)
            for index, pane in enumerate(self.panes):
                pane.setVisible(index < len(members))
                if index < len(members):
                    self._show_member(pane, members[index])
        else:
            self.detail.setCurrentWidget(self.many_view)
            self._render_copies()
        self._calculate()
        self.on_busy_changed(self.busy)

    def _show_member(self, pane, member):
        if member["kind"] == "folder" and not member["samples"]:
            rows = self.report.folder_files[member["key"]]
            sample_ids = [row["id"] for row in rows
                          if PurePath(row["name"]).suffix.lower() not in (".aae", ".xmp")][:6]
            member["samples"] = [{**dict(row), "caption": row["name"]}
                                 for file_id in sample_ids if (row := self.lib.file(file_id)) is not None]
        pane.show_member(member, member["key"] in self.selected)

    def _render_copies(self):
        self.copies.blockSignals(True)
        self.copies.clear()
        shown = self.members[self.copy_offset:self.copy_offset + COPY_PAGE]
        for member in shown:
            checked = member["key"] in self.selected
            recommendation = ("Recommended keep - overridden" if checked else "Recommended keep") \
                if member["recommended"] else ("Selected for Recovery" if checked else "Kept by you")
            item = QTreeWidgetItem(["", self.lib.display_path(member["path"]), fmt_size(member["size"]),
                                   recommendation])
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(0, Qt.CheckState.Checked if member["key"] in self.selected else Qt.CheckState.Unchecked)
            item.setData(0, Qt.ItemDataRole.UserRole, member)
            if member["recommended"]:
                item.setForeground(3, QColor(theme.OK))
            self.copies.addTopLevelItem(item)
        self.copies.blockSignals(False)
        self.copy_scope.setText(f"Showing {self.copy_offset + 1}-{self.copy_offset + len(shown)} of "
                               f"{len(self.members):,} copies. Checks persist across pages in this group only.")
        self.copy_previous.setEnabled(self.copy_offset > 0)
        self.copy_next.setEnabled(self.copy_offset + COPY_PAGE < len(self.members))
        if shown:
            self.copies.setCurrentItem(self.copies.topLevelItem(0))

    def _copy_step(self, direction):
        self.copy_offset = max(0, self.copy_offset + direction * COPY_PAGE)
        self._render_copies()

    def _table_preview(self, current, previous):
        if current is not None:
            self._show_member(self.many_preview, current.data(0, Qt.ItemDataRole.UserRole))

    def _table_checked(self, item, column):
        if column == 0:
            member = item.data(0, Qt.ItemDataRole.UserRole)
            self._checked(member["key"], item.checkState(0) == Qt.CheckState.Checked)

    def _checked(self, key, checked):
        if key is None:
            return
        if checked:
            self.selected.add(key)
        else:
            self.selected.discard(key)
        if self._current_group is not None:
            kind, group = self._current_group
            choices = self.file_choices if kind == "file" else self.folder_choices
            choices[group.hash if kind == "file" else group.id] = set(self.selected)
        self.copies.blockSignals(True)
        for index in range(self.copies.topLevelItemCount()):
            item = self.copies.topLevelItem(index)
            if item.data(0, Qt.ItemDataRole.UserRole)["key"] == key:
                item.setCheckState(0, Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
                recommended = item.data(0, Qt.ItemDataRole.UserRole)["recommended"]
                item.setText(3, ("Recommended keep - overridden" if checked else "Recommended keep")
                             if recommended else ("Selected for Recovery" if checked else "Kept by you"))
        self.copies.blockSignals(False)
        if self.many_preview.key == key:
            self.many_preview.remove_check.blockSignals(True)
            self.many_preview.remove_check.setChecked(checked)
            self.many_preview.remove_check.blockSignals(False)
            self.many_preview.update_intent()
        self._calculate()

    def _calculate(self):
        self.plan_bg.invalidate()
        self._token += 1
        token, generation = self._token, self.ctx.generation
        self._selection_plan = None
        self.on_busy_changed(self.busy)
        if self._current_group is None or not self.selected:
            self.selection_note.setText(
                "This set: nothing selected. The folder-group action can still clean other sets; "
                "its combined total is confirmed first." if self._current_collection is not None else
                "Nothing selected. No files will move.")
            return
        kind, group = self._current_group
        chosen, lib, report = set(self.selected), self.lib, self.report
        self.selection_note.setText("Calculating this set's preview, including linked components..." if
                                    self._current_collection is not None else
                                    "Calculating the complete move, including linked components...")
        def work():
            try:
                if kind == "file":
                    plan = duplicates.plan_removal(lib, [group], removals={group.hash: chosen})
                    retained = unique = 0
                else:
                    selection = duplicates.plan_folder_selection(lib, report, group, chosen)
                    plan, retained, unique = selection.actions, selection.retained_linked, selection.unique_kept
                files, size, extra = assets.footprint(lib, plan)
                return {"token": token, "generation": generation, "actions": plan, "files": files, "bytes": size,
                        "extra": extra, "retained": retained, "unique": unique}
            finally:
                lib.close_thread()
        self.plan_bg.call(work)

    def _plan_ready(self, plan):
        if self._closed or plan["token"] != self._token or plan["generation"] != self.ctx.generation:
            return
        self._selection_plan = plan
        text = ("This set only: " if self._current_collection is not None else "Planned move: ") + \
            f"{fmt_n(plan['files'], 'file')} ({fmt_size(plan['bytes'])}) to Recovery."
        if plan["extra"]:
            text += f" Includes {plan['extra']} linked component(s), not just the displayed photos."
        if plan["unique"]:
            text += f" {plan['unique']} unique/unmatched file(s) in the larger folder stay untouched."
        if plan["retained"]:
            text += f" {plan['retained']} shared file(s) are kept with unique or unreviewed linked parts."
        if self._current_collection is not None:
            text += " The main action reviews the combined total for every set in this folder group."
        self.selection_note.setText(text)
        self.on_busy_changed(self.busy)

    def _failed(self, error):
        if not self._closed:
            self._loading = False
            self._selection_plan = None
            self.selection_note.setText(f"Review could not finish: {error}")
            self.on_busy_changed(self.busy)

    def apply(self):
        if self._current_collection is not None:
            self.clean_folder_group()
        else:
            self._apply_current_set()

    def _apply_current_set(self):
        if self.busy or self._selection_plan is None or not self._selection_plan["files"]:
            return
        kind, group = self._current_group
        plan = self._selection_plan
        signature, lib = self._signature, self.lib
        all_selected = len(self.selected) == len(self.members)
        subset = kind == "folder" and group.kind == "inside"
        details = ["Only this group's checked copies/content are affected. Other groups are not included.",
                   "Reviewed files are checked again. Recovery is cumulative across earlier cleanups."]
        if subset:
            details.append("Only shared files are eligible on the larger side. Its unique files and containing folder stay.")
        if plan["retained"]:
            details.append(f"{plan['retained']} shared files are retained to avoid separating unique/unreviewed linked parts.")
        if all_selected:
            details.append("Every shown copy is selected." if not subset else
                           "Shared copies from both folders are selected; unique content in the larger folder stays.")
        def declined():
            self._moving = False
            self.action_note.setText("Nothing moved. Your checkboxes are unchanged.")
        def done(result):
            self.action_note.setText(
                f"This change moved {fmt_size(result.bytes)} to Recovery. "
                "The total in History also includes older Recovery contents."
                + (" Some items were skipped or failed; review History." if result.failed or result.skipped else ""))
        started = self.apply_actions(
            "duplicates", "Move selected duplicate content to Recovery", plan["actions"],
            summary=recycle_summary(plan["files"], plan["bytes"]), details=details,
            confirm_text=f"Move {fmt_n(plan['files'], 'file')}", note=recovery_note(),
            require_ack=("I understand all selected shared copies may leave the library." if all_selected else None),
            confirm_action=not self.quick_remove.isChecked() or subset,
            before_apply=lambda: duplicates.remember_keep(lib, signature, False),
            done_message=lambda result: f"Moved {fmt_size(result.bytes)} from this comparison to Recovery.",
            after=done, on_declined=declined)
        if started:
            self._moving = True
            self.action_note.setText("Reviewing the selected content...")

    def keep(self):
        if self.busy or self._signature is None or self._loading:
            return
        try:
            duplicates.remember_keep(self.lib, self._signature, True)
        except (OSError, sqlite3.Error) as error:
            MessageDialog(self, "Duplicate choice not saved", str(error)).exec()
            return
        self.action_note.setText("Kept all copies in this group. No files were moved.")
        self._show(self.report)

    def clean_folder_group(self):
        if self._current_collection is not None:
            self._clean_redundant({group.hash for group in self._current_collection.groups})

    def clean_all(self):
        self._clean_redundant(None)

    def _clean_redundant(self, hashes):
        if self.busy or self.report is None or self._loading:
            return
        lib, report = self.lib, self.report
        file_choices = {key: set(value) for key, value in self.file_choices.items()}
        folder_choices = {key: set(value) for key, value in self.folder_choices.items()}
        if hashes is not None:
            for group in self._current_collection.groups:
                scope = {row["id"] for row in group.files}
                chosen = file_choices.get(group.hash, scope - {group.keeper_id}) & scope
                if chosen == scope:
                    chosen.discard(group.keeper_id)
                file_choices[group.hash] = chosen
        title = "Clean all exact duplicate groups" if hashes is None else "Clean this exact folder group"
        def work(progress):
            try:
                progress.update(0, 0, "Choosing verified survivors and protecting linked components...", force=True)
                plan = duplicate_cleanup.plan_cleanup(lib, report, hashes=hashes, file_choices=file_choices,
                                                      folder_choices=folder_choices, progress=progress)
                progress.check()
                return plan
            finally:
                lib.close_thread()
        def ready(plan):
            include_linked = False
            if plan.linked_skipped:
                from ..duplicate_cleanup_review import CleanupReviewDialog
                dialog = CleanupReviewDialog(self, self.ctx, report, hashes, file_choices, folder_choices, plan)
                try:
                    if dialog.exec() != dialog.DialogCode.Accepted:
                        self.action_note.setText("Cleanup cancelled. No files moved.")
                        return
                    plan = dialog.selected_plan()
                    include_linked = dialog.include_linked.isChecked()
                except ValueError as error:
                    MessageDialog(self, "Review the combined linked parts", str(error)).exec()
                    return
                finally:
                    dialog.shutdown()
                    dialog.deleteLater()
            if not plan.actions:
                message = (
                    f"No redundant copies can be removed with these choices. {plan.protected_groups} kept set(s); "
                    f"{plan.linked_skipped} linked asset(s) need individual review. Nothing moved.")
                self.action_note.setText(message)
                MessageDialog(self, "No copies are eligible for this cleanup", message,
                              "Saved Keep choices and unchecked reviewed copies are protected. "
                              "No files were moved. Review those choices or find duplicates again.").exec()
                return
            size = sum(action.size for action in plan.actions)
            details = [
                f"Scope: {'all exact duplicate groups across every page' if hashes is None else 'this folder collection, all its sets/pages'}.",
                f"{plan.groups} exact content set(s) affected. At least one verified copy of every content is retained.",
                "Saved Keep choices and unchecked copies you reviewed are protected. Keep-one safety wins even "
                "if every copy was checked in an individual comparison.",
                ("You explicitly included linked parts that may be unique. The next confirmation covers this "
                 "entire scope, not each set individually." if include_linked else
                 "Unique files, system leftovers and empty folders are not removed by this action. "
                 "Only complete, verified-equivalent linked assets can be removed together."),
                f"{plan.protected_groups} protected set(s); {plan.linked_skipped} linked asset(s) left for individual review.",
                "This always asks for confirmation, even with Quick remove. Originals go to Recovery; "
                "this move does not free disk space until Recovery is explicitly emptied.",
            ]
            unmatched = [part for part in plan.review_parts if part["unmatched"]]
            if unmatched:
                details.insert(2, f"<b>{len(unmatched)} linked part(s) ({fmt_size(sum(part['size'] for part in unmatched))}) "
                               "are not proven duplicates and may be unique. They were included in your combined review.</b>")
            self.apply_actions(
                "duplicates", title, plan.actions,
                summary=f"{fmt_n(len(plan.actions), 'file')} ({fmt_size(size)}) will move; verified survivors remain.",
                details=details, confirm_text=f"Move {fmt_n(len(plan.actions), 'file')}", note=recovery_note(),
                require_ack=("I approve moving the reviewed linked parts that may be unique." if unmatched else None),
                confirm_action=True, done_message=lambda result: f"Moved {fmt_size(result.bytes)} from the reviewed duplicate cleanup.",
                after=lambda result: self.action_note.setText(
                    f"This cleanup moved {fmt_size(result.bytes)}. Verified copies were retained."
                    + (" Review skipped/failed items in History." if result.failed or result.skipped else "")),
                on_declined=lambda: self.action_note.setText("Cleanup cancelled. No files moved."))
        self.run("Planning " + title, work, ready, notify_success=False)

    def _quick_changed(self, checked):
        accepted = False
        if checked and not self.busy:
            dialog = ConfirmDialog(
                self, "Enable quick removal for this window?",
                "Ordinary exact-copy selections will move straight to Recovery.",
                ["Only the current group is affected. Selecting every copy can leave none in the library.",
                 "Subset comparisons and linked components still require review. Undo needs intact Recovery."],
                "Enable quick remove", danger=True,
                require_ack="I understand checked copies, including all copies, may be moved without another popup.")
            accepted = dialog.exec() == dialog.DialogCode.Accepted and dialog.ack.isChecked()
            dialog.deleteLater()
        self.quick_remove.blockSignals(True)
        self.quick_remove.setChecked(accepted)
        self.quick_remove.blockSignals(False)
        self.quick_warning.setVisible(accepted)

    def _finished(self, outcome):
        if not self._moving or outcome == "ok" and self.ctx.runner.title.startswith("Preparing "):
            return
        self._moving = False
        if outcome != "ok":
            self.action_note.setText("Removal did not finish. Check the error and History before retrying.")
