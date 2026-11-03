"""Exact duplicates: review groups, choose what to keep, move copies to Recovery."""
from __future__ import annotations

from pathlib import PurePath

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QSplitter, QStackedWidget, QWidget

from ...engine import duplicates
from .. import theme
from ..widgets import (Banner, EmptyState, PhotoGrid, Preview, Tile, button, fmt_n, fmt_size, hbox, label, vbox)
from .base import Page, recovery_note, recycle_summary


class DuplicatesPage(Page):
    title = "Duplicates"
    subtitle = "Exact copies of the same file, proven by comparing every byte. Keep one, move the rest to Recovery."

    def __init__(self, ctx):
        super().__init__(ctx)
        self.find_btn = button("Find duplicates", "primary", self.find)
        self.header_actions.addWidget(self.find_btn)
        self.groups: list[duplicates.DuplicateGroup] = []
        self.keepers: dict[str, int] = {}
        self.included: set[str] = set()

        self.stack = QStackedWidget()
        self.empty = EmptyState("\uE8C8", "Find exact copies",
                                "Memoria compares file contents byte by byte — names don't matter. Only files that "
                                "share a size are read, so this is quick. Nothing is changed until you approve it.",
                                button("Find duplicates", "primary", self.find))
        self.none = EmptyState("\uE73E", "No duplicates", "Every photo and video in this library is unique.")
        self.stack.addWidget(self.empty)
        self.stack.addWidget(self.none)

        self.t_groups, self.t_copies, self.t_space = Tile(text="Groups"), Tile(text="Extra copies"), Tile(text="Space to free")
        self.list = QListWidget()
        self.list.setIconSize(QSize(56, 56))
        self.list.setFixedWidth(330)
        self.list.currentRowChanged.connect(self._show_group)
        self.list.itemChanged.connect(self._group_toggled)
        self.grid = PhotoGrid(ctx.thumbs, cell=170, captions=2)
        self.grid.setSelectionMode(PhotoGrid.SelectionMode.SingleSelection)
        self.grid.current_item.connect(self._file_selected)
        self.keep_btn = button("Keep this copy instead", on_click=self._keep_selected)
        self.keep_btn.setEnabled(False)
        self.group_title = label("", "h2")
        self.group_note = label("", "muted", wrap=True)
        self.preview = Preview(ctx, 300)
        right = QWidget()
        right.setLayout(vbox(hbox(self.group_title, None, self.keep_btn), self.group_note, self.grid, spacing=6))
        split = QSplitter()
        split.addWidget(self.list)
        split.addWidget(right)
        split.addWidget(self.preview)
        split.setStretchFactor(1, 1)
        split.setChildrenCollapsible(False)
        self.summary = label("", "")
        self.apply_btn = button("Move copies to Recovery", "primary", self.apply)
        sel_all = button("Include all", "link", lambda: self._set_all(True))
        sel_none = button("Include none", "link", lambda: self._set_all(False))
        results = QWidget()
        results.setLayout(vbox(hbox(self.t_groups, self.t_copies, self.t_space, spacing=12),
                               Banner(recovery_note(), "trust"), split,
                               hbox(sel_all, sel_none, 12, self.summary, None, self.apply_btn), spacing=10))
        self.stack.addWidget(results)
        self.results = results
        self.body.addWidget(self.stack, 1)

    def refresh(self) -> None:
        if self.groups:
            self.find()  # library changed (e.g. after apply/undo) → recompute; hashes are cached so it's fast
        else:
            self.stack.setCurrentWidget(self.empty)

    def on_busy_changed(self, busy: bool) -> None:
        self.find_btn.setEnabled(not busy)
        self.apply_btn.setEnabled(not busy and bool(self._planned()))

    def find(self) -> None:
        lib = self.lib
        self.run("Finding duplicates", lambda p: duplicates.find_duplicates(lib, p), self._show)

    def _show(self, groups) -> None:
        self.groups = groups
        self.keepers = {k: v for k, v in self.keepers.items() if any(g.hash == k for g in groups)}
        self.included = {g.hash for g in groups}
        if not groups:
            self.stack.setCurrentWidget(self.none)
            return
        self.stack.setCurrentWidget(self.results)
        copies = sum(len(g.files) - 1 for g in groups)
        self.t_groups.set(f"{len(groups):,}")
        self.t_copies.set(f"{copies:,}")
        self.t_space.set(fmt_size(sum(g.wasted for g in groups)), color=theme.OK)
        self.list.blockSignals(True)
        self.list.clear()
        for g in groups:
            keeper = self._keeper(g)
            it = QListWidgetItem(f"{keeper['name']}\n{len(g.files)} copies · {fmt_size(g.size)} each")
            pm = self.ctx.thumbs.get(keeper["id"])
            if pm:
                it.setIcon(QIcon(pm))
            it.setFlags(it.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            it.setCheckState(Qt.CheckState.Checked)
            it.setToolTip("Untick to leave this group exactly as it is")
            self.list.addItem(it)
        self.list.blockSignals(False)
        self.list.setCurrentRow(0)
        self._update_summary()

    def _keeper(self, g) -> dict:
        kid = self.keepers.get(g.hash, g.keeper_id)
        return next(f for f in g.files if f["id"] == kid)

    def _show_group(self, row: int) -> None:
        if row < 0 or row >= len(self.groups):
            return
        g = self.groups[row]
        kid = self._keeper(g)["id"]
        items = []
        for f in g.files:
            keep = f["id"] == kid
            reason = "Kept" if keep else ("Will move to Recovery" if g.hash in self.included else "Left as is")
            items.append({**f, "caption": f["name"], "sub": str(PurePath(f["rel_path"]).parent),
                          "badge": "KEEP" if keep else ("COPY" if g.hash in self.included else ""),
                          "badge_kind": "keep" if keep else "muted",
                          "tip": f"{f['rel_path']}\n{reason}: {g.reasons.get(f['id'], '') if not keep else 'chosen to keep'}"})
        self.grid.set_items(items)
        self.group_title.setText(f"{len(g.files)} identical copies of {self._keeper(g)['name']}")
        why = g.reasons.get(next(f["id"] for f in g.files if f["id"] != kid), "")
        auto = " (chosen by you)" if g.hash in self.keepers else ""
        self.group_note.setText(f"Keeping the copy in “{PurePath(self._keeper(g)['rel_path']).parent or 'library root'}”{auto}. "
                                f"Other copies: {why.lower()}. Select a different photo and click “Keep this copy instead” to change.")
        self.preview.clear()
        self.keep_btn.setEnabled(False)

    def _file_selected(self, it: dict) -> None:
        self.preview.show_row(it)
        row = self.list.currentRow()
        if 0 <= row < len(self.groups):
            self.keep_btn.setEnabled(it["id"] != self._keeper(self.groups[row])["id"])

    def _keep_selected(self) -> None:
        row = self.list.currentRow()
        sel = self.grid.selected_items()
        if row < 0 or not sel:
            return
        g = self.groups[row]
        self.keepers[g.hash] = sel[0]["id"]
        self._show_group(row)
        self._update_summary()

    def _group_toggled(self, item: QListWidgetItem) -> None:
        g = self.groups[self.list.row(item)]
        if item.checkState() == Qt.CheckState.Checked:
            self.included.add(g.hash)
        else:
            self.included.discard(g.hash)
        if self.list.row(item) == self.list.currentRow():
            self._show_group(self.list.currentRow())
        self._update_summary()

    def _set_all(self, on: bool) -> None:
        for i in range(self.list.count()):
            self.list.item(i).setCheckState(Qt.CheckState.Checked if on else Qt.CheckState.Unchecked)

    def _planned(self):
        if not self.groups or self.lib is None:
            return []
        return duplicates.plan_removal(self.lib, [g for g in self.groups if g.hash in self.included], self.keepers)

    def _update_summary(self) -> None:
        plan = self._planned()
        size = sum(a.size for a in plan)
        kept = len([g for g in self.groups if g.hash in self.included])
        self.summary.setText(f"{fmt_n(len(plan), 'copy', 'copies')} ({fmt_size(size)}) will move to Recovery · "
                             f"{fmt_n(kept, 'original')} kept" if plan else "No groups included")
        self.apply_btn.setEnabled(bool(plan) and not self.busy)

    def apply(self) -> None:
        plan = self._planned()
        size = sum(a.size for a in plan)
        groups = len([g for g in self.groups if g.hash in self.included])
        self.apply_actions(
            "duplicates", "Move duplicate copies to Recovery", plan,
            summary=recycle_summary(len(plan), size),
            details=[f"One copy of each of {fmt_n(groups, 'file')} is kept where it is.",
                     "Right before moving, each copy is re-read to confirm it is still identical to the one being "
                     "kept. Anything that changed is skipped."],
            confirm_text=f"Move {fmt_n(len(plan), 'copy', 'copies')}", note=recovery_note(),
            done_message=lambda r: f"Moved {fmt_n(r.done, 'duplicate copy', 'duplicate copies')} "
                                   f"({fmt_size(r.bytes)}) to Recovery.")
