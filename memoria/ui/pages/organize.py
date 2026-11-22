"""Organise into date folders with a full preview of every move."""
from __future__ import annotations

import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QCheckBox, QComboBox, QHeaderView, QStackedWidget, QTreeWidget, QTreeWidgetItem

from ...engine import organize
from ...engine.actions import Action
from .. import theme
from ..review_pages import ReviewGroup, ReviewPages
from ..tasks import LatestCall
from ..widgets import Card, EmptyState, Tile, button, fmt_date, fmt_n, hbox, label, trust_note, vbox
from .base import Page


class OrganizePage(Page):
    title = "Organise by date"
    subtitle = "File photos and videos into year and month folders using the date they were taken."

    def __init__(self, ctx):
        super().__init__(ctx)
        self.pattern = QComboBox()
        for key, (_, example) in organize.PATTERNS.items():
            self.pattern.addItem(f"{example}\\photo.jpg", key)
        self.uncertain = QCheckBox("Also move files whose only date is the file's modified date (often wrong for copies)")
        self.cleanup = QCheckBox("Remove folders that end up empty")
        self.cleanup.setChecked(True)
        self.preview_btn = button("Preview changes", "primary", self.build_plan)
        opts = Card(vbox(label("How should folders be named?", "h2"),
                         hbox(label("Folder layout", "muted"), self.pattern, None),
                         self.uncertain, self.cleanup, hbox(None, self.preview_btn), spacing=8))
        self.body.addWidget(opts)

        self.stack = QStackedWidget()
        self.stack.addWidget(EmptyState("\uE8B7", "See every move before it happens",
                                        "Choose a layout and click Preview. Memoria uses the camera date first, then a "
                                        "date in the file name. Nothing moves until you approve the plan."))
        self.t_move, self.t_place, self.t_skip = Tile(text="Will move"), Tile(text="Already in place"), \
            Tile(text="Skipped — date uncertain")
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["New location", "Currently in", "Date used"])
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tree.header().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.pages = ReviewPages(self.tree, self._render_item)
        self.pages.changed.connect(self._update)
        self.summary = label("")
        self.apply_btn = button("Move files", "primary", self.apply)
        res = vbox(hbox(self.t_move, self.t_place, self.t_skip, spacing=12),
                   self.tree, self.pages.controls,
                   hbox(self.summary, None,
                        trust_note("Nothing is overwritten · undo the whole move",
                                   "Files are only renamed if a file with the same name already exists in the new "
                                   "folder (e.g. “IMG_1234 (2).jpg”). Nothing is overwritten, and you can undo the "
                                   "whole move."), 12, self.apply_btn), spacing=10)
        from PySide6.QtWidgets import QWidget
        w = QWidget()
        w.setLayout(res)
        self.results = w
        self.stack.addWidget(w)
        self.body.addWidget(self.stack, 1)
        self.plan: organize.OrganizePlan | None = None
        self.plan_bg = LatestCall(self)
        self.plan_bg.result.connect(self._apply_ready)
        self.plan_bg.failed.connect(self._plan_failed)
        ctx.library_opened.connect(self.plan_bg.invalidate)
        ctx.library_modified.connect(self.plan_bg.invalidate)

    def on_busy_changed(self, busy: bool) -> None:
        self.preview_btn.setEnabled(not busy)
        self.apply_btn.setEnabled(not busy and bool(self.pages.selected_count))

    def refresh(self) -> None:
        cached = self.ctx.cached("organize")
        if cached is not None and self.pattern.currentData() == cached.pattern and not self.uncertain.isChecked():
            self._show(cached)
        elif self.plan is not None and not self.busy:
            self.build_plan()

    def build_plan(self) -> None:
        lib, pattern, uncertain = self.lib, self.pattern.currentData(), self.uncertain.isChecked()
        generation = self.ctx.generation
        def work(progress):
            try:
                return organize.plan_organize(lib, pattern, uncertain, progress=progress)
            finally:
                lib.close_thread()
        def done(plan):
            if (lib, generation) == (self.lib, self.ctx.generation):
                self._show(plan)
        self.run("Planning date folders",
                 work, done)

    def _show(self, plan) -> None:
        self.plan = plan
        p = self.plan
        self.ctx.set_badge("organize", len(p.items))
        self.t_move.set(f"{len(p.items):,}")
        self.t_place.set(f"{p.already_in_place:,}")
        self.t_skip.set(f"{p.skipped_uncertain:,}", color=theme.WARN if p.skipped_uncertain else None)
        by_folder: dict[str, list] = {}
        for it in p.items:
            by_folder.setdefault(os.path.dirname(it.dst_rel), []).append(it)
        self.pages.set_groups([ReviewGroup(folder, folder, by_folder[folder]) for folder in sorted(by_folder)])
        self.stack.setCurrentWidget(self.results)
        self._update()

    def _chosen(self) -> list:
        return [item for items in self.pages.selected().values() for item in items]

    def _render_item(self, folder, it):
        src = organize.SOURCE_LABEL.get(it.source, it.source)
        child = QTreeWidgetItem([os.path.basename(it.dst_rel), it.row["folder"] or "(library root)",
                                f"{it.taken_at:%d %b %Y} · {src}"])
        child.setData(0, Qt.ItemDataRole.UserRole, it)
        child.setToolTip(0, f"{it.src_rel}  →  {it.dst_rel}")
        if it.source == "modified":
            child.setForeground(2, QColor(theme.WARN))
        return child

    def _update(self) -> None:
        count = self.pages.selected_count
        folders = self.pages.selected_groups
        self.summary.setText((f"{fmt_n(count, 'file')} will move into {fmt_n(folders, 'folder')}"
                              if count else "Nothing selected") + " · Across all pages")
        self.apply_btn.setEnabled(bool(count) and not self.busy)

    def apply(self) -> None:
        if self.busy or self.plan_bg.running:
            return
        chosen = self._chosen()
        lib, generation, cleanup = self.lib, self.ctx.generation, self.cleanup.isChecked()
        self.tree.setEnabled(False)
        self.apply_btn.setEnabled(False)
        self.summary.setText("Preparing the full selection across all pages…")
        def work():
            try:
                acts = organize.plan_actions(lib, chosen)
                empties = organize.empty_folders_after(lib, chosen) if cleanup else []
                return lib, generation, chosen, acts, empties
            finally:
                lib.close_thread()
        self.plan_bg.call(work)

    def _plan_failed(self, error):
        from ..widgets import MessageDialog
        self.tree.setEnabled(True)
        self._update()
        MessageDialog(self, "Could not prepare date folders", str(error)).exec()

    def _apply_ready(self, result):
        lib, generation, chosen, acts, empties = result
        self.tree.setEnabled(True)
        self._update()
        if (lib, generation) != (self.lib, self.ctx.generation) or self.busy:
            self.ctx.toast_requested.emit("The library changed. Review the refreshed plan before moving files.", "")
            return
        for rel in sorted(empties, key=lambda r: -r.count(os.sep)):
            acts.append(Action(op="rmdir", src=str(self.lib.abspath(rel)), reason="Left empty after organising"))
        folders = len({os.path.dirname(it.dst_rel) for it in chosen})
        details = [f"Files are moved inside this library into {fmt_n(folders, 'date folder')}.",
                   "File contents and names stay the same (a number is added only to avoid a clash)."]
        if empties:
            details.append(f"{fmt_n(len(empties), 'folder')} left empty will be removed (undo recreates them).")
        self.apply_actions(
            "organize", "Organise by date", acts,
            summary=f"{fmt_n(len(chosen), 'file')} will be moved into date folders.",
            details=details, confirm_text=f"Move {fmt_n(len(chosen), 'file')}",
            note="Every move is recorded. Undo puts each file back exactly where it was.",
            done_message=lambda r: f"Organised {fmt_n(r.done, 'item')}.")

    def shutdown(self):
        self.plan_bg.wait()
