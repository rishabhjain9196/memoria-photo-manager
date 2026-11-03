"""Organise into date folders with a full preview of every move."""
from __future__ import annotations

import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QCheckBox, QComboBox, QHeaderView, QStackedWidget, QTreeWidget, QTreeWidgetItem

from ...engine import organize
from ...engine.actions import Action
from .. import theme
from ..widgets import Banner, Card, EmptyState, Tile, button, fmt_date, fmt_n, hbox, label, vbox
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
        self.tree.itemChanged.connect(lambda *_: self._update())
        self.summary = label("")
        self.apply_btn = button("Move files", "primary", self.apply)
        res = vbox(hbox(self.t_move, self.t_place, self.t_skip, spacing=12),
                   Banner("Files are only renamed if a file with the same name already exists in the new folder "
                          "(e.g. “IMG_1234 (2).jpg”). Nothing is overwritten, and you can undo the whole move.", "trust"),
                   self.tree, hbox(self.summary, None, self.apply_btn), spacing=10)
        from PySide6.QtWidgets import QWidget
        w = QWidget()
        w.setLayout(res)
        self.results = w
        self.stack.addWidget(w)
        self.body.addWidget(self.stack, 1)
        self.plan: organize.OrganizePlan | None = None

    def on_busy_changed(self, busy: bool) -> None:
        self.preview_btn.setEnabled(not busy)
        self.apply_btn.setEnabled(not busy and bool(self._chosen()))

    def refresh(self) -> None:
        cached = self.ctx.cached("organize")
        if cached is not None and self.pattern.currentData() == cached.pattern and not self.uncertain.isChecked():
            self._show(cached)
        elif self.plan is not None and not self.busy:
            self.build_plan()

    def build_plan(self) -> None:
        lib, pattern, uncertain = self.lib, self.pattern.currentData(), self.uncertain.isChecked()
        self.run("Planning date folders",
                 lambda p: organize.plan_organize(lib, pattern, uncertain, progress=p), self._show)

    def _show(self, plan) -> None:
        self.plan = plan
        p = self.plan
        self.ctx.set_badge("organize", len(p.items))
        self.t_move.set(f"{len(p.items):,}")
        self.t_place.set(f"{p.already_in_place:,}")
        self.t_skip.set(f"{p.skipped_uncertain:,}", color=theme.WARN if p.skipped_uncertain else None)
        self.tree.blockSignals(True)
        self.tree.clear()
        by_folder: dict[str, list] = {}
        for it in p.items:
            by_folder.setdefault(os.path.dirname(it.dst_rel), []).append(it)
        for folder in sorted(by_folder):
            items = by_folder[folder]
            top = QTreeWidgetItem([f"{folder}   ({len(items)})", "", ""])
            top.setFlags(top.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsAutoTristate)
            f = top.font(0)
            f.setBold(True)
            top.setFont(0, f)
            for it in items:
                src = organize.SOURCE_LABEL.get(it.source, it.source)
                c = QTreeWidgetItem([os.path.basename(it.dst_rel), it.row["folder"] or "(library root)",
                                     f"{it.taken_at:%d %b %Y} · {src}"])
                c.setFlags(c.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                c.setCheckState(0, Qt.CheckState.Checked)
                c.setData(0, Qt.ItemDataRole.UserRole, it)
                c.setToolTip(0, f"{it.src_rel}  →  {it.dst_rel}")
                if it.source == "modified":
                    c.setForeground(2, QColor(theme.WARN))
                top.addChild(c)
            self.tree.addTopLevelItem(top)
        self.tree.blockSignals(False)
        self.stack.setCurrentWidget(self.results)
        self._update()

    def _chosen(self) -> list:
        out = []
        for i in range(self.tree.topLevelItemCount()):
            top = self.tree.topLevelItem(i)
            for j in range(top.childCount()):
                c = top.child(j)
                if c.checkState(0) == Qt.CheckState.Checked:
                    out.append(c.data(0, Qt.ItemDataRole.UserRole))
        return out

    def _update(self) -> None:
        chosen = self._chosen()
        folders = len({os.path.dirname(it.dst_rel) for it in chosen})
        self.summary.setText(f"{fmt_n(len(chosen), 'file')} will move into {fmt_n(folders, 'folder')}"
                             if chosen else "Nothing selected")
        self.apply_btn.setEnabled(bool(chosen) and not self.busy)

    def apply(self) -> None:
        chosen = self._chosen()
        acts = organize.plan_actions(self.lib, chosen)
        empties = organize.empty_folders_after(self.lib, chosen) if self.cleanup.isChecked() else []
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
