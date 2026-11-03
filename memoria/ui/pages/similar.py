"""Similar photos & bursts, similar videos — each with an explained best pick — and a blurry-photo review."""
from __future__ import annotations

from pathlib import PurePath
from typing import Callable

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QComboBox, QListWidget, QListWidgetItem, QSplitter, QStackedWidget, QTabWidget, QWidget

from ...engine import similar
from .. import theme
from ..widgets import (Banner, EmptyState, PhotoGrid, Preview, Tile, button, fmt_duration, fmt_n, fmt_size, hbox,
                       label, vbox)
from .base import Page, recovery_note, recycle_summary

try:
    from ...engine import videosim
except ImportError:  # pragma: no cover
    videosim = None


class GroupReview(QWidget):
    """Find → review groups (best pick + reasons, tick boxes) → move ticked items to Recovery."""

    def __init__(self, page: "SimilarPage", *, noun: str, cache_key: str, finder: Callable, find_label: str,
                 empty_title: str, empty_text: str, none_text: str, burst_tile: bool):
        super().__init__()
        self.page, self.ctx = page, page.ctx
        self.noun, self.cache_key, self.finder = noun, cache_key, finder
        self.groups: list[similar.SimilarGroup] = []
        self.marked: dict[int, set[int]] = {}
        self.find_btn = button(find_label, "primary", self.find)
        self.stack = QStackedWidget()
        self.empty = EmptyState("\uE734", empty_title, empty_text, button(find_label, "primary", self.find))
        self.none = EmptyState("\uE73E", f"No similar {noun}s", none_text)
        self.stack.addWidget(self.empty)
        self.stack.addWidget(self.none)

        self.t_groups = Tile(text="Groups")
        self.t_second = Tile(text="Bursts" if burst_tile else "Space you could free")
        self.t_marked = Tile(text="Selected to move")
        self.burst_tile = burst_tile
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
        hint = label(f"Ticked {noun}s will move to Recovery. Click a tick box to change it; Space toggles the "
                     "selected one.", "small")
        self.preview = Preview(self.ctx, 300)
        right = QWidget()
        right.setLayout(vbox(hbox(self.g_title, None, self.best_btn), self.g_reason, hint, self.grid, spacing=6))
        split = QSplitter()
        split.addWidget(self.glist)
        split.addWidget(right)
        split.addWidget(self.preview)
        split.setStretchFactor(1, 1)
        split.setChildrenCollapsible(False)
        self.summary = label("")
        self.apply_btn = button("Move selected to Recovery", "primary", self.apply)
        keep_best_all = button("Keep only best in every group", "link", lambda: self._mark_all(True))
        clear_all = button("Untick everything", "link", lambda: self._mark_all(False))
        res = QWidget()
        res.setLayout(vbox(hbox(self.t_groups, self.t_second, self.t_marked, spacing=12), split,
                           hbox(keep_best_all, clear_all, 12, self.summary, None, self.apply_btn), spacing=10))
        self.results = res
        self.stack.addWidget(res)
        self.setLayout(vbox(hbox(label("Groups are suggestions; nothing moves until you confirm.", "muted"), None,
                                 self.find_btn), self.stack, spacing=10, margins=(0, 10, 0, 0)))

    # ------------------------------------------------------------------------ lifecycle
    def refresh(self) -> None:
        cached = self.ctx.cached(self.cache_key)
        if cached is not None:
            self._show(cached)
        elif self.groups and self.page.tabs.currentWidget() is self and not self.page.busy:
            self.find()   # library changed: refresh the visible results (hashes are cached, so it's quick)
        else:
            self.groups, self.marked = [], {}
            self.stack.setCurrentWidget(self.empty)

    def on_busy_changed(self, busy: bool) -> None:
        self.find_btn.setEnabled(not busy)
        self.apply_btn.setEnabled(not busy and bool(self._planned_rows()))

    def find(self) -> None:
        lib = self.ctx.library
        self.page.run(f"Finding similar {self.noun}s", lambda p: self.finder(lib, p), self._show)

    def _show(self, groups) -> None:
        self.groups = groups
        self.marked = {i: {f["id"] for f in g.files if f["id"] != g.best_id} for i, g in enumerate(groups)}
        self.page.update_badge()
        if not groups:
            self.stack.setCurrentWidget(self.none)
            return
        self.stack.setCurrentWidget(self.results)
        self.t_groups.set(f"{len(groups):,}")
        if self.burst_tile:
            self.t_second.set(f"{sum(g.burst for g in groups):,}")
        else:
            self.t_second.set(fmt_size(sum(g.reclaimable for g in groups)))
        self.glist.clear()
        for g in groups:
            best = next(f for f in g.files if f["id"] == g.best_id)
            kind = "Burst" if g.burst else "Similar"
            it = QListWidgetItem(f"{kind} · {len(g.files)} {self.noun}s\n{best['name']}")
            pm = self.ctx.thumbs.get(best["id"])
            if pm:
                it.setIcon(QIcon(pm))
            self.glist.addItem(it)
        self.glist.setCurrentRow(0)
        self._update_summary()

    # ------------------------------------------------------------------------ group view
    def _show_group(self, row: int) -> None:
        if not (0 <= row < len(self.groups)):
            return
        g = self.groups[row]
        marked = self.marked[row]
        items = []
        for f in g.files:
            best = f["id"] == g.best_id
            items.append({**f, "caption": f["name"], "badge": "BEST" if best else "", "badge_kind": "best",
                          "checked": f["id"] in marked, "dim_unchecked": False,
                          "sub": g.reasons.get(f["id"], "").replace("Best pick: ", "").replace("Weaker: ", ""),
                          "sub_color": theme.OK if best else theme.MUTED,
                          "tip": f"{f['rel_path']}\n{g.reasons.get(f['id'], '')}"})
        self.grid.set_items(items)
        kind = "Burst" if g.burst else f"Similar {self.noun}s"
        self.g_title.setText(f"{kind}: {len(g.files)} {self.noun}s")
        self.g_reason.setText("✓ " + g.reasons[g.best_id])
        self.best_btn.setEnabled(False)
        self.preview.clear()

    def _file_selected(self, it: dict) -> None:
        row = self.glist.currentRow()
        g = self.groups[row] if 0 <= row < len(self.groups) else None
        extra = ""
        if g:
            color = theme.OK if it["id"] == g.best_id else theme.MUTED
            extra = f"<span style='color:{color}'>{g.reasons.get(it['id'], '')}</span>"
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
                ids = ids - {g.best_id}   # never move every item of a group
            rows.extend(f for f in g.files if f["id"] in ids)
        return rows

    def _update_summary(self) -> None:
        rows = self._planned_rows()
        size = sum(r["size"] for r in rows)
        self.t_marked.set(f"{len(rows):,}", fmt_size(size))
        self.summary.setText(f"{fmt_n(len(rows), self.noun)} ({fmt_size(size)}) will move to Recovery"
                             if rows else "Nothing selected")
        self.apply_btn.setEnabled(bool(rows) and not self.page.busy)

    def apply(self) -> None:
        rows = self._planned_rows()
        size = sum(r["size"] for r in rows)
        kept = sum(1 for i in range(len(self.groups)) if self.marked.get(i))
        self.page.apply_actions(
            "similar", f"Move similar {self.noun}s to Recovery",
            similar.plan_recycle(self.ctx.library, rows, "Similar to a better one"),
            summary=recycle_summary(len(rows), size),
            details=[f"The best pick in each of {fmt_n(kept, 'group')} stays where it is.",
                     f"These {self.noun}s are similar, not identical — make sure you're happy with the selection.",
                     f"A {self.noun} that changed since you reviewed it is skipped."],
            confirm_text=f"Move {fmt_n(len(rows), self.noun)}", note=recovery_note(),
            done_message=lambda r: f"Moved {fmt_n(r.done, self.noun)} ({fmt_size(r.bytes)}) to Recovery.")


class SimilarPage(Page):
    title = "Similar & best shots"
    subtitle = ("Bursts, look-alike photos and similar videos, with the best one picked for you — and why. "
                "Plus a review of blurry photos.")

    def __init__(self, ctx):
        super().__init__(ctx)
        self.photos = GroupReview(
            self, noun="photo", cache_key="similar", finder=lambda lib, p: similar.find_similar(lib, progress=p),
            find_label="Find similar photos", empty_title="Find bursts and look-alikes",
            empty_text="Memoria groups photos that look the same — burst shots, retakes and resized copies (like "
                       "WhatsApp forwards) — and suggests the best one using sharpness, exposure, faces and resolution.",
            none_text="No bursts or look-alike photos were found.", burst_tile=True)
        self.tabs = QTabWidget()
        self.tabs.addTab(self.photos, "Similar photos and bursts")
        self.videos = None
        if videosim is not None:
            self.videos = GroupReview(
                self, noun="video", cache_key="similar_videos",
                finder=lambda lib, p: videosim.find_similar_videos(lib, p),
                find_label="Find similar videos", empty_title="Find re-encoded and trimmed copies",
                empty_text="Memoria compares frames from across each video, so compressed, resized or slightly "
                           "trimmed copies (like WhatsApp forwards) are found even though their bytes differ. The "
                           "best copy is picked by resolution, quality and length.",
                none_text="No videos look like copies of each other.", burst_tile=False)
            self.tabs.addTab(self.videos, "Similar videos")
        self.tabs.addTab(self._build_blurry(), "Blurry photos")
        self.body.addWidget(self.tabs, 1)

    # compatibility helpers used by tools/ui_screenshots.py and tests
    @property
    def grid(self):
        return self.photos.grid

    def find(self) -> None:
        self.photos.find()

    def reviews(self) -> list[GroupReview]:
        return [r for r in (self.photos, self.videos) if r is not None]

    def refresh(self) -> None:
        for r in self.reviews():
            r.refresh()
        self.find_blurry()

    def on_busy_changed(self, busy: bool) -> None:
        for r in self.reviews():
            r.on_busy_changed(busy)
        self.b_apply.setEnabled(not busy and bool(self.bgrid.model_.checked()))

    def update_badge(self) -> None:
        self.ctx.set_badge("similar", sum(sum(len(g.files) - 1 for g in r.groups) for r in self.reviews()))

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
        rows = similar.find_blurry(self.lib, similar.BLUR_PRESETS[self.sens.currentData()])
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
