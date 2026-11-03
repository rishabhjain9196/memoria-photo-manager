"""Similar photos & bursts with an explained best pick, plus blurry-photo review."""
from __future__ import annotations

from pathlib import PurePath

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QButtonGroup, QComboBox, QListWidget, QListWidgetItem, QSplitter, QStackedWidget,
                               QTabWidget, QWidget)

from ...engine import similar
from .. import theme
from ..widgets import (Banner, EmptyState, PhotoGrid, Preview, Tile, button, fmt_n, fmt_size, hbox, label, vbox)
from .base import Page, recovery_note, recycle_summary


class SimilarPage(Page):
    title = "Similar & best shots"
    subtitle = ("Bursts and near-identical photos, with the best one picked for you — and why. "
                "Plus a review of blurry photos.")

    def __init__(self, ctx):
        super().__init__(ctx)
        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_similar(), "Similar groups and bursts")
        self.tabs.addTab(self._build_blurry(), "Blurry photos")
        self.body.addWidget(self.tabs, 1)
        self.groups: list[similar.SimilarGroup] = []
        self.marked: dict[int, set[int]] = {}   # group index → file ids to move

    # ------------------------------------------------------------------------- similar tab
    def _build_similar(self) -> QWidget:
        self.find_btn = button("Find similar photos", "primary", self.find)
        self.s_stack = QStackedWidget()
        self.s_empty = EmptyState("\uE734", "Find bursts and look-alikes",
                                  "Memoria groups photos that look the same — burst shots, retakes and resized "
                                  "copies (like WhatsApp forwards) — and suggests the best one using sharpness, "
                                  "exposure, faces and resolution.", button("Find similar photos", "primary", self.find))
        self.s_none = EmptyState("\uE73E", "No similar photos", "No bursts or look-alike photos were found.")
        self.s_stack.addWidget(self.s_empty)
        self.s_stack.addWidget(self.s_none)

        self.t_groups, self.t_bursts, self.t_marked = Tile(text="Groups"), Tile(text="Bursts"), Tile(text="Selected to move")
        self.glist = QListWidget()
        self.glist.setIconSize(QSize(56, 56))
        self.glist.setFixedWidth(300)
        self.glist.currentRowChanged.connect(self._show_group)
        self.grid = PhotoGrid(self.ctx.thumbs, cell=176, captions=2)
        self.grid.setSelectionMode(PhotoGrid.SelectionMode.SingleSelection)
        self.grid.current_item.connect(self._file_selected)
        self.grid.model_.checked_changed.connect(self._checks_changed)
        self.best_btn = button("Make this the best pick", on_click=self._make_best)
        self.best_btn.setEnabled(False)
        self.g_title = label("", "h2")
        self.g_reason = label("", "", wrap=True)
        self.g_reason.setStyleSheet(f"color: {theme.OK};")
        hint = label("Ticked photos will move to Recovery. Click a tick box to change it.", "small")
        self.preview = Preview(self.ctx, 300)
        right = QWidget()
        right.setLayout(vbox(hbox(self.g_title, None, self.best_btn), self.g_reason, hint, self.grid, spacing=6))
        split = QSplitter()
        split.addWidget(self.glist)
        split.addWidget(right)
        split.addWidget(self.preview)
        split.setStretchFactor(1, 1)
        split.setChildrenCollapsible(False)
        self.s_summary = label("")
        self.s_apply = button("Move selected to Recovery", "primary", self.apply_similar)
        keep_best_all = button("Keep only best in every group", "link", lambda: self._mark_all(True))
        clear_all = button("Untick everything", "link", lambda: self._mark_all(False))
        res = QWidget()
        res.setLayout(vbox(hbox(self.t_groups, self.t_bursts, self.t_marked, spacing=12), split,
                           hbox(keep_best_all, clear_all, 12, self.s_summary, None, self.s_apply), spacing=10))
        self.s_results = res
        self.s_stack.addWidget(res)
        w = QWidget()
        w.setLayout(vbox(hbox(label("Groups are suggestions; nothing moves until you confirm.", "muted"), None,
                              self.find_btn), self.s_stack, spacing=10, margins=(0, 10, 0, 0)))
        return w

    def refresh(self) -> None:
        if self.groups:
            self.find()
        else:
            self.s_stack.setCurrentWidget(self.s_empty)
        self.find_blurry()

    def on_busy_changed(self, busy: bool) -> None:
        self.find_btn.setEnabled(not busy)
        self.s_apply.setEnabled(not busy and bool(self._planned_rows()))
        self.b_apply.setEnabled(not busy and bool(self.bgrid.model_.checked()))

    def find(self) -> None:
        lib = self.lib
        self.run("Finding similar photos", lambda p: similar.find_similar(lib, progress=p), self._show)

    def _show(self, groups) -> None:
        self.groups = groups
        self.marked = {i: {f["id"] for f in g.files if f["id"] != g.best_id} for i, g in enumerate(groups)}
        if not groups:
            self.s_stack.setCurrentWidget(self.s_none)
            return
        self.s_stack.setCurrentWidget(self.s_results)
        self.t_groups.set(f"{len(groups):,}")
        self.t_bursts.set(f"{sum(g.burst for g in groups):,}")
        self.glist.clear()
        for g in groups:
            best = next(f for f in g.files if f["id"] == g.best_id)
            kind = "Burst" if g.burst else "Similar"
            it = QListWidgetItem(f"{kind} · {len(g.files)} photos\n{best['name']}")
            pm = self.ctx.thumbs.get(best["id"])
            if pm:
                it.setIcon(QIcon(pm))
            self.glist.addItem(it)
        self.glist.setCurrentRow(0)
        self._update_summary()

    def _show_group(self, row: int) -> None:
        if not (0 <= row < len(self.groups)):
            return
        g = self.groups[row]
        marked = self.marked[row]
        items = []
        for f in g.files:
            best = f["id"] == g.best_id
            items.append({**f, "caption": f["name"], "badge": "BEST" if best else "",
                          "badge_kind": "best", "checked": f["id"] in marked, "dim_unchecked": False,
                          "sub": g.reasons.get(f["id"], "").replace("Best pick: ", "").replace("Weaker: ", ""),
                          "sub_color": theme.OK if best else theme.MUTED,
                          "tip": f"{f['rel_path']}\n{g.reasons.get(f['id'], '')}"})
        self.grid.set_items(items)
        kind = "Burst" if g.burst else "Similar photos"
        self.g_title.setText(f"{kind}: {len(g.files)} photos")
        self.g_reason.setText("✓ " + g.reasons[g.best_id])
        self.best_btn.setEnabled(False)
        self.preview.clear()

    def _file_selected(self, it: dict) -> None:
        row = self.glist.currentRow()
        g = self.groups[row] if 0 <= row < len(self.groups) else None
        extra = ""
        if g:
            extra = f"<span style='color:{theme.OK if it['id'] == g.best_id else theme.MUTED}'>{g.reasons.get(it['id'], '')}</span>"
            self.best_btn.setEnabled(it["id"] != g.best_id)
        self.preview.show_row(it, extra)

    def _make_best(self) -> None:
        row = self.glist.currentRow()
        sel = self.grid.selected_items()
        if row < 0 or not sel:
            return
        g = self.groups[row]
        g.best_id = sel[0]["id"]
        g.reasons[g.best_id] = "Best pick: chosen by you"
        self.marked[row] = {f["id"] for f in g.files if f["id"] != g.best_id}
        self._show_group(row)
        self._update_summary()

    def _checks_changed(self) -> None:
        row = self.glist.currentRow()
        if 0 <= row < len(self.groups):
            self.marked[row] = {it["id"] for it in self.grid.model_.checked()}
        self._update_summary()

    def _mark_all(self, best_only: bool) -> None:
        for i, g in enumerate(self.groups):
            self.marked[i] = {f["id"] for f in g.files if f["id"] != g.best_id} if best_only else set()
        self._show_group(self.glist.currentRow())
        self._update_summary()

    def _planned_rows(self) -> list[dict]:
        rows = []
        for i, g in enumerate(self.groups):
            ids = self.marked.get(i, set())
            if len(ids) >= len(g.files):
                ids = ids - {g.best_id}   # never move every photo of a group
            rows.extend(f for f in g.files if f["id"] in ids)
        return rows

    def _update_summary(self) -> None:
        rows = self._planned_rows()
        size = sum(r["size"] for r in rows)
        self.t_marked.set(f"{len(rows):,}", fmt_size(size))
        self.s_summary.setText(f"{fmt_n(len(rows), 'photo')} ({fmt_size(size)}) will move to Recovery"
                               if rows else "Nothing selected")
        self.s_apply.setEnabled(bool(rows) and not self.busy)

    def apply_similar(self) -> None:
        rows = self._planned_rows()
        size = sum(r["size"] for r in rows)
        kept = sum(1 for i, g in enumerate(self.groups) if len(self.marked.get(i, ())) > 0)
        self.apply_actions(
            "similar", "Move similar photos to Recovery", similar.plan_recycle(self.lib, rows, "Similar to a better shot"),
            summary=recycle_summary(len(rows), size),
            details=[f"The best pick in each of {fmt_n(kept, 'group')} stays where it is.",
                     "These photos are similar, not identical — make sure you're happy with the selection.",
                     "A photo that changed since you reviewed it is skipped."],
            confirm_text=f"Move {fmt_n(len(rows), 'photo')}", note=recovery_note(),
            done_message=lambda r: f"Moved {fmt_n(r.done, 'photo')} ({fmt_size(r.bytes)}) to Recovery.")

    # ------------------------------------------------------------------------- blurry tab
    def _build_blurry(self) -> QWidget:
        self.sens = QComboBox()
        self.sens.addItem("Only very blurry", "strict")
        self.sens.addItem("Blurry (recommended)", "normal")
        self.sens.addItem("Slightly soft too", "lenient")
        self.sens.setCurrentIndex(1)
        self.sens.currentIndexChanged.connect(self.find_blurry)
        self.bgrid = PhotoGrid(self.ctx.thumbs, cell=170, captions=2)
        self.bgrid.current_item.connect(lambda it: self.bpreview.show_row(it))
        self.bgrid.model_.checked_changed.connect(self._b_summary)
        self.bpreview = Preview(self.ctx, 300)
        self.b_count = label("", "muted")
        self.b_summary_lbl = label("")
        self.b_apply = button("Move ticked to Recovery", "primary", self.apply_blurry)
        sel_all = button("Tick all", "link", lambda: self.bgrid.model_.set_all_checked(True))
        sel_none = button("Untick all", "link", lambda: self.bgrid.model_.set_all_checked(False))
        split = QSplitter()
        split.addWidget(self.bgrid)
        split.addWidget(self.bpreview)
        split.setStretchFactor(0, 1)
        split.setChildrenCollapsible(False)
        w = QWidget()
        w.setLayout(vbox(hbox(label("Sensitivity", "muted"), self.sens, 12, self.b_count, None),
                         Banner("Blur is measured from fine detail. Night shots, fog or intentionally soft photos can "
                                "appear here too — nothing is ticked until you choose.", "info"),
                         split, hbox(sel_all, sel_none, 12, self.b_summary_lbl, None, self.b_apply),
                         spacing=10, margins=(0, 10, 0, 0)))
        return w

    def find_blurry(self) -> None:
        if self.lib is None:
            return
        thr = similar.BLUR_PRESETS[self.sens.currentData()]
        rows = similar.find_blurry(self.lib, thr)
        best = max((r["sharpness"] for r in rows), default=1) or 1
        items = [{**r, "caption": r["name"], "checked": False,
                  "sub": f"Sharpness {r['sharpness']:.0f} · {PurePath(r['rel_path']).parent}"} for r in rows]
        self.bgrid.set_items(items)
        self.b_count.setText(f"{fmt_n(len(rows), 'photo')} found")
        self._b_summary()

    def _b_summary(self) -> None:
        rows = self.bgrid.model_.checked()
        size = sum(r["size"] for r in rows)
        self.b_summary_lbl.setText(f"{fmt_n(len(rows), 'photo')} ({fmt_size(size)}) ticked" if rows else "Nothing ticked")
        self.b_apply.setEnabled(bool(rows) and not self.busy)

    def apply_blurry(self) -> None:
        rows = self.bgrid.model_.checked()
        size = sum(r["size"] for r in rows)
        self.apply_actions(
            "similar", "Move blurry photos to Recovery", similar.plan_recycle(self.lib, rows, "Blurry"),
            summary=recycle_summary(len(rows), size), details=["Only the photos you ticked are moved."],
            confirm_text=f"Move {fmt_n(len(rows), 'photo')}", note=recovery_note(),
            done_message=lambda r: f"Moved {fmt_n(r.done, 'blurry photo')} ({fmt_size(r.bytes)}) to Recovery.")
