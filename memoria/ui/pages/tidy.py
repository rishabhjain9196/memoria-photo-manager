"""Tidy up: system junk, empty files and folders, unreadable media, stray documents."""
from __future__ import annotations

from html import escape

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHeaderView, QSplitter, QTreeWidget, QTreeWidgetItem

from ...engine import tidy
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
        self.tree.itemChanged.connect(lambda *_: self._update())
        self.tree.currentItemChanged.connect(self._current)
        self.tree.itemDoubleClicked.connect(self._open)
        self.preview = Preview(ctx, 300)
        split = QSplitter()
        split.addWidget(self.tree)
        split.addWidget(self.preview)
        split.setStretchFactor(0, 1)
        split.setChildrenCollapsible(False)
        self.summary = label("")
        self.apply_btn = button("Tidy selected", "primary", self.apply)
        self.body.addWidget(Banner(recovery_note() + " Categories that need a closer look start unticked.", "trust"))
        self.sidecar_note = label("", "muted", wrap=True)
        self.sidecar_note.hide()
        self.body.addWidget(self.sidecar_note)
        self.body.addWidget(split, 1)
        self.body.addLayout(hbox(self.summary, None, self.apply_btn))
        self.report: tidy.TidyReport | None = None

    def on_busy_changed(self, busy: bool) -> None:
        self.apply_btn.setEnabled(not busy and bool(self._selected_count()))
        self.rescan_btn.setEnabled(not busy)

    def refresh(self) -> None:
        cached = self.ctx.cached("tidy")
        if cached is not None:
            self._show(cached)
            return
        lib = self.lib
        if not self.run("Looking for leftovers", lambda p: tidy.find_tidy(lib, p), self._show):
            self.stale = True

    def _show(self, report: tidy.TidyReport) -> None:
        self.report = report
        self.sidecar_note.setText(
            f"Protected: {fmt_n(report.protected_sidecars, 'Apple .AAE edit sidecar')} left untouched. "
            "These can preserve Apple photo edits; Memoria does not apply those edits.")
        self.sidecar_note.setVisible(report.protected_sidecars > 0)
        self.ctx.set_badge("tidy", report.count("junk") + report.count("empty") + report.count("folders"))
        self.tree.blockSignals(True)
        self.tree.clear()
        for cat, (title, desc, default) in tidy.CATEGORIES.items():
            items = self.report.items.get(cat, [])
            if not items:
                continue
            top = QTreeWidgetItem([f"{title}  ({len(items):,})", fmt_size(self.report.size(cat)) if cat != "folders" else "", desc])
            top.setFlags(top.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsAutoTristate)
            top.setData(0, Qt.ItemDataRole.UserRole, ("cat", cat))
            f = top.font(0)
            f.setBold(True)
            top.setFont(0, f)
            for it in items:
                child = QTreeWidgetItem([it["name"] or it["rel_path"], fmt_size(it["size"]) if cat != "folders" else "",
                                         it["folder"] or "(library root)"])
                child.setFlags(child.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                child.setCheckState(0, Qt.CheckState.Checked if default else Qt.CheckState.Unchecked)
                child.setData(0, Qt.ItemDataRole.UserRole, ("item", cat, it))
                child.setToolTip(0, it["rel_path"])
                top.addChild(child)
            self.tree.addTopLevelItem(top)
            top.setExpanded(len(items) <= 12)
        self.tree.blockSignals(False)
        if self.tree.topLevelItemCount() == 0:
            empty = QTreeWidgetItem(["Nothing to tidy — this library is clean.", "", ""])
            self.tree.addTopLevelItem(empty)
        self._update()

    def _selected(self) -> dict[str, list[dict]]:
        out: dict[str, list[dict]] = {}
        for i in range(self.tree.topLevelItemCount()):
            top = self.tree.topLevelItem(i)
            for j in range(top.childCount()):
                c = top.child(j)
                if c.checkState(0) == Qt.CheckState.Checked:
                    _, cat, it = c.data(0, Qt.ItemDataRole.UserRole)
                    out.setdefault(cat, []).append(it)
        return out

    def _selected_count(self) -> int:
        return sum(len(v) for v in self._selected().values())

    def _update(self) -> None:
        sel = self._selected()
        files = sum(len(v) for k, v in sel.items() if k != "folders")
        folders = len(sel.get("folders", []))
        size = sum(i["size"] or 0 for k, v in sel.items() if k != "folders" for i in v)
        parts = []
        if files:
            parts.append(f"{fmt_n(files, 'file')} ({fmt_size(size)}) to Recovery")
        if folders:
            parts.append(f"{fmt_n(folders, 'empty folder')} removed")
        self.summary.setText(" · ".join(parts) if parts else "Nothing selected")
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
        sel = self._selected()
        try:
            acts = tidy.plan_actions(self.lib, self.report, sel)
        except ValueError as error:
            MessageDialog(self, "Tidy selection needs review", str(error)).exec()
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
