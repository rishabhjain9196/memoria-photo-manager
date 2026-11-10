"""Tidy up: system junk, empty files and folders, unreadable media, stray documents."""
from __future__ import annotations

from html import escape

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHeaderView, QSplitter, QTreeWidget, QTreeWidgetItem

from ...engine import tidy
from ..review_pages import ReviewGroup, ReviewPages
from ..tasks import LatestCall
from ..widgets import Banner, MessageDialog, Preview, button, fmt_date, fmt_n, fmt_size, hbox, label, show_in_explorer
from .base import Page, recovery_note


class TidyPage(Page):
    title = "Tidy up"
    subtitle = "Clear out leftovers that operating systems and apps scatter through photo folders."

    def __init__(self, ctx):
        super().__init__(ctx)
        self.rescan_btn = button("Check again", on_click=self.refresh)
        self.header_actions.addWidget(self.rescan_btn)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["What", "Size", "Location"])
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tree.header().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tree.currentItemChanged.connect(self._current)
        self.tree.itemDoubleClicked.connect(self._open)
        self.preview = Preview(ctx, 300)
        split = QSplitter()
        split.addWidget(self.tree)
        split.addWidget(self.preview)
        split.setStretchFactor(0, 1)
        split.setChildrenCollapsible(False)
        self.summary = label("")
        self.pages = ReviewPages(self.tree, self._render_item, lambda item: item.get("size") or 0)
        self.pages.changed.connect(self._update)
        self.apply_btn = button("Tidy selected", "primary", self.apply)
        self.body.addWidget(Banner(recovery_note() + " Categories that need a closer look start unticked.", "trust"))
        self.sidecar_note = label("", "muted", wrap=True)
        self.sidecar_note.hide()
        self.body.addWidget(self.sidecar_note)
        self.body.addWidget(split, 1)
        self.body.addLayout(self.pages.controls)
        self.body.addLayout(hbox(self.summary, None, self.apply_btn))
        self.report: tidy.TidyReport | None = None
        self.plan_bg = LatestCall(self)
        self.plan_bg.result.connect(self._apply_ready)
        self.plan_bg.failed.connect(self._plan_failed)
        self.ctx.library_opened.connect(self._invalidate)
        self.ctx.library_modified.connect(self._invalidate)

    def on_busy_changed(self, busy: bool) -> None:
        self.apply_btn.setEnabled(not busy and not self.plan_bg.running and bool(self._selected_count()))
        self.rescan_btn.setEnabled(not busy)

    def refresh(self) -> None:
        cached = self.ctx.cached("tidy")
        if cached is not None:
            self._show(cached)
            return
        lib = self.lib
        generation = self.ctx.generation
        def work(progress):
            try:
                return tidy.find_tidy(lib, progress)
            finally:
                lib.close_thread()
        def done(report):
            if (lib, generation) == (self.lib, self.ctx.generation):
                self._show(report)
        if not self.run("Looking for leftovers", work, done):
            self.stale = True

    def _show(self, report: tidy.TidyReport) -> None:
        self.report = report
        self.sidecar_note.setText(
            f"Protected: {fmt_n(report.protected_sidecars, 'Apple .AAE edit sidecar')} left untouched. "
            "These can preserve Apple photo edits; Memoria does not apply those edits.")
        self.sidecar_note.setVisible(report.protected_sidecars > 0)
        self.ctx.set_badge("tidy", report.count("junk") + report.count("empty") + report.count("folders"))
        groups = []
        for cat, (title, desc, default) in tidy.CATEGORIES.items():
            items = self.report.items.get(cat, [])
            if not items:
                continue
            groups.append(ReviewGroup(cat, title, items, default, report.size(cat)))
        self.preview.clear()
        self.pages.set_groups(groups)
        if self.tree.topLevelItemCount() == 0:
            empty = QTreeWidgetItem(["Nothing to tidy — this library is clean.", "", ""])
            self.tree.addTopLevelItem(empty)
        self._update()

    def _selected(self) -> dict[str, list[dict]]:
        return self.pages.selected()

    def _render_item(self, cat, it):
        child = QTreeWidgetItem([it["name"] or it["rel_path"], fmt_size(it["size"]) if cat != "folders" else "",
                                 it["folder"] or "(library root)"])
        child.setData(0, Qt.ItemDataRole.UserRole, ("item", cat, it))
        child.setToolTip(0, it["rel_path"])
        return child

    def _selected_count(self) -> int:
        return self.pages.selected_count

    def _update(self) -> None:
        files = sum(g.selected_count for g in self.pages.groups if g.key != "folders")
        folders = sum(g.selected_count for g in self.pages.groups if g.key == "folders")
        size = sum(g.selected_bytes for g in self.pages.groups if g.key != "folders")
        parts = []
        if files:
            parts.append(f"{fmt_n(files, 'file')} ({fmt_size(size)}) to Recovery")
        if folders:
            parts.append(f"{fmt_n(folders, 'empty folder')} removed")
        self.summary.setText((" · ".join(parts) if parts else "Nothing selected") + " · Across all pages")
        self.apply_btn.setEnabled(bool(parts) and not self.busy)

    def _current(self, cur, _prev) -> None:
        data = cur.data(0, Qt.ItemDataRole.UserRole) if cur else None
        if data and data[0] == "item" and data[1] != "folders":
            error = data[2].get("error")
            extra = (f"<b>Recorded analysis error</b><br>{escape(error)}<br>"
                     "This is not proof of damage. Check the codec, file access and original before removing it."
                     if error else "")
            self.preview.show_row(data[2], extra)
        else:
            self.preview.clear()

    def _open(self, item, _col) -> None:
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and data[0] == "item":
            show_in_explorer(self.lib.abspath(data[2]["rel_path"]))

    def apply(self) -> None:
        if self.busy or self.plan_bg.running or self.report is None:
            return
        sel = self._selected()
        if any(tidy.is_apple_edit_sidecar(row["rel_path"])
               for category, rows in sel.items() if category != "folders" for row in rows):
            MessageDialog(self, "Tidy selection needs review",
                          "Apple .AAE edit sidecars are protected from Tidy up. "
                          "Keep them with your photos. Nothing was moved.").exec()
            return
        lib, generation, report = self.lib, self.ctx.generation, self.report
        self.apply_btn.setEnabled(False)
        self.tree.setEnabled(False)
        self.summary.setText("Preparing the full selection across all pages…")
        def work():
            try:
                return lib, generation, sel, tidy.plan_actions(lib, report, sel)
            finally:
                lib.close_thread()
        self.plan_bg.call(work)

    def _plan_failed(self, error):
        self.tree.setEnabled(True)
        self._update()
        MessageDialog(self, "Tidy selection needs review", str(error)).exec()

    def _apply_ready(self, result):
        lib, generation, sel, acts = result
        self.tree.setEnabled(True)
        self._update()
        if (lib, generation) != (self.lib, self.ctx.generation) or self.busy:
            self.ctx.toast_requested.emit("The library changed. Review the refreshed Tidy selection before applying.", "")
            return
        files = [a for a in acts if a.op == "recycle"]
        folders = [a for a in acts if a.op == "rmdir"]
        details = []
        for cat, items in sel.items():
            details.append(f"{tidy.CATEGORIES[cat][0]}: {len(items):,}")
        if folders:
            details.append("Folders are only removed if they are still empty at that moment; undo recreates them.")
        self.apply_actions(
            "tidy", "Tidy up", acts,
            summary=f"{fmt_n(len(files), 'file')} ({fmt_size(sum(a.size for a in files))}) will be moved to Recovery"
                    + (f" and {fmt_n(len(folders), 'empty folder')} removed." if folders else "."),
            details=details, confirm_text="Tidy up", note=recovery_note(),
            done_message=lambda r: f"Tidied {fmt_n(r.done, 'item')}.")

    def _invalidate(self):
        self.plan_bg.invalidate()
        self.tree.setEnabled(True)
        self.preview.clear()

    def shutdown(self):
        self.plan_bg.wait()
        self.preview.shutdown()
