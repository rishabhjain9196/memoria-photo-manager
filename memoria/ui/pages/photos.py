"""Browse the library: timeline, search, filters, preview."""
from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (QComboBox, QLineEdit, QMenu, QSplitter, QTreeWidget, QTreeWidgetItem, QWidget)

from ..widgets import PhotoGrid, Preview, button, fmt_date, fmt_n, label, show_in_explorer, open_path, vbox, hbox
from .base import Page

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


class PhotosPage(Page):
    title = "Photos & videos"
    subtitle = "Browse by date. Double-click to open. Select photos and send them to the Story maker."

    def __init__(self, ctx):
        super().__init__(ctx)
        self.story_btn = button("Add to Story maker", on_click=self._to_story)
        self.story_btn.setEnabled(False)
        self.header_actions.addWidget(self.story_btn)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search name, folder or camera")
        self.search.setClearButtonEnabled(True)
        self.kind = QComboBox()
        self.kind.addItems(["Everything", "Photos", "Videos", "Problems"])
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setColumnCount(2)
        self.tree.setColumnWidth(0, 130)
        self.tree.setIndentation(14)
        self.tree.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tree.header().setStretchLastSection(False)
        from PySide6.QtWidgets import QHeaderView
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        left = QWidget()
        left.setLayout(vbox(self.search, self.kind, self.tree, spacing=8))
        left.setFixedWidth(230)

        self.grid = PhotoGrid(ctx.thumbs, cell=156, captions=1)
        self.grid.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.grid.customContextMenuRequested.connect(self._menu)
        self.grid.current_item.connect(lambda it: self.preview.show_row(it))
        self.grid.activated_item.connect(lambda it: open_path(self.lib.abspath(it["rel_path"])))
        self.grid.selectionModel().selectionChanged.connect(self._sel_changed)
        self.count = label("", "small")
        center = QWidget()
        center.setLayout(vbox(self.count, self.grid, spacing=4))
        self.preview = Preview(ctx)

        split = QSplitter()
        split.addWidget(left)
        split.addWidget(center)
        split.addWidget(self.preview)
        split.setStretchFactor(1, 1)
        split.setChildrenCollapsible(False)
        self.body.addWidget(split, 1)

        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(200)
        self._debounce.timeout.connect(self._apply_filter)
        self.search.textChanged.connect(self._debounce.start)
        self.kind.currentIndexChanged.connect(self._apply_filter)
        self.tree.currentItemChanged.connect(lambda *_: self._apply_filter())
        self.rows: list[dict] = []

    def refresh(self) -> None:
        self.rows = [dict(r) for r in self.lib.files("1", order="COALESCE(taken_at,'') DESC, rel_path")]
        self._build_tree()
        self._apply_filter()

    def _build_tree(self) -> None:
        cur = self.tree.currentItem()
        cur_key = cur.data(0, Qt.ItemDataRole.UserRole) if cur else None
        self.tree.blockSignals(True)
        self.tree.clear()
        counts: dict[str, dict[str, int]] = {}
        for r in self.rows:
            if r["kind"] == "other" or r["error"]:
                continue
            t = r["taken_at"] or ""
            y, m = (t[:4], t[5:7]) if t else ("Unknown", "")
            counts.setdefault(y, {})
            counts[y][m] = counts[y].get(m, 0) + 1
        total = sum(sum(v.values()) for v in counts.values())
        all_item = QTreeWidgetItem(["All", f"{total:,}"])
        all_item.setData(0, Qt.ItemDataRole.UserRole, "")
        self.tree.addTopLevelItem(all_item)
        select = all_item
        for y in sorted(counts, reverse=True):
            yi = QTreeWidgetItem([y, f"{sum(counts[y].values()):,}"])
            yi.setData(0, Qt.ItemDataRole.UserRole, y)
            self.tree.addTopLevelItem(yi)
            if cur_key == y:
                select = yi
            for m in sorted(counts[y], reverse=True):
                if not m:
                    continue
                mi = QTreeWidgetItem([MONTHS[int(m) - 1], f"{counts[y][m]:,}"])
                key = f"{y}-{m}"
                mi.setData(0, Qt.ItemDataRole.UserRole, key)
                yi.addChild(mi)
                if cur_key == key:
                    select = mi
        for i in range(self.tree.topLevelItemCount()):
            self.tree.topLevelItem(i).setTextAlignment(1, Qt.AlignmentFlag.AlignRight)
        self.tree.setCurrentItem(select)
        self.tree.blockSignals(False)

    def _apply_filter(self) -> None:
        cur = self.tree.currentItem()
        prefix = cur.data(0, Qt.ItemDataRole.UserRole) if cur else ""
        q = self.search.text().strip().lower()
        kind = self.kind.currentIndex()
        items = []
        for r in self.rows:
            if kind == 0 and (r["kind"] == "other" or r["error"]):
                continue
            if kind == 1 and (r["kind"] != "image" or r["error"]):
                continue
            if kind == 2 and (r["kind"] != "video" or r["error"]):
                continue
            if kind == 3 and not r["error"]:
                continue
            if prefix:
                t = r["taken_at"] or ""
                if prefix == "Unknown" and t:
                    continue
                if prefix != "Unknown" and not t.startswith(prefix):
                    continue
            if q and q not in r["rel_path"].lower() and q not in (r["camera"] or "").lower():
                continue
            items.append({**r, "caption": fmt_date(r["taken_at"]) if r["taken_at"] else r["name"],
                          "tip": f"{r['rel_path']}"})
        self.grid.set_items(items)
        self.count.setText(f"Showing {fmt_n(len(items), 'item')}")
        self.preview.clear()

    def _sel_changed(self, *_):
        sel = [i for i in self.grid.selected_items() if i["kind"] == "image" and not i.get("error")]
        self.story_btn.setEnabled(bool(sel))
        self.story_btn.setText(f"Add {len(sel)} to Story maker" if len(sel) > 1 else "Add to Story maker")

    def _to_story(self) -> None:
        ids = [i["id"] for i in self.grid.selected_items() if i["kind"] == "image" and not i.get("error")]
        if ids:
            self.ctx.story_selection.extend(ids)
            self.ctx.navigate.emit("story")

    def _menu(self, pos) -> None:
        idx = self.grid.indexAt(pos)
        if not idx.isValid():
            return
        it = idx.data(Qt.ItemDataRole.UserRole)
        m = QMenu(self)
        m.addAction("Open", lambda: open_path(self.lib.abspath(it["rel_path"])))
        m.addAction("Show in folder", lambda: show_in_explorer(self.lib.abspath(it["rel_path"])))
        if it["kind"] == "image" and not it.get("error"):
            m.addAction("Add to Story maker", self._to_story)
        m.exec(self.grid.viewport().mapToGlobal(pos))
