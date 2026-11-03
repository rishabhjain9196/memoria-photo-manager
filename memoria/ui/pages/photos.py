"""Browse the library: timeline, search, filters, preview, viewer and batch actions on a selection."""
from __future__ import annotations

import os
from pathlib import Path, PurePath

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (QComboBox, QFileDialog, QFrame, QHeaderView, QLineEdit, QMenu, QSlider, QSplitter,
                               QTreeWidget, QTreeWidgetItem, QWidget)

from ...engine import batch
from ..widgets import (MessageDialog, PhotoGrid, Preview, Viewer, button, fmt_date, fmt_n, fmt_size, hbox, label,
                       open_path, show_in_explorer, vbox)
from .base import Page, recovery_note, recycle_summary

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
KINDS = ["Everything", "Photos", "Videos", "Problems"]


class PhotosPage(Page):
    title = "Photos & videos"
    subtitle = ("Browse by date. Double-click to view. Select several (Ctrl/Shift-click, Ctrl+A) to act on them "
                "together.")

    def __init__(self, ctx):
        super().__init__(ctx)
        self.zoom = QSlider(Qt.Orientation.Horizontal)
        self.zoom.setRange(110, 280)
        self.zoom.setValue(156)
        self.zoom.setFixedWidth(140)
        self.zoom.setToolTip("Thumbnail size (Ctrl + mouse wheel)")
        self.zoom.valueChanged.connect(self._set_zoom)
        self.header_actions.addWidget(label("Size", "small"))
        self.header_actions.addWidget(self.zoom)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search name, folder or camera")
        self.search.setToolTip("Ctrl+F")
        self.search.setClearButtonEnabled(True)
        self.kind = QComboBox()
        self.kind.addItems(KINDS)
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setColumnCount(2)
        self.tree.setIndentation(14)
        self.tree.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tree.header().setStretchLastSection(False)
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        left = QWidget()
        left.setLayout(vbox(self.search, self.kind, self.tree, spacing=8))
        left.setFixedWidth(230)

        self.grid = PhotoGrid(ctx.thumbs, cell=156, captions=1)
        self.grid.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.grid.customContextMenuRequested.connect(self._menu)
        self.grid.current_item.connect(lambda it: self.preview.show_row(it))
        self.grid.activated_item.connect(self._view)
        self.grid.selectionModel().selectionChanged.connect(self._sel_changed)
        self.grid.viewport().installEventFilter(self)
        self.count = label("", "small")

        # selection bar (batch actions)
        self.sel_bar = QFrame()
        self.sel_bar.setObjectName("selectionBar")
        self.sel_label = label("", "h2")
        self.b_recycle = button("Move to Recovery", on_click=self.recycle_selected, tip="Delete key")
        self.b_more = button("More actions ▾", tip="Story maker, compress, copy, move, show in folder")
        self.more_menu = QMenu(self)
        self.a_edit = self.more_menu.addAction("Edit…", self._to_editor)
        self.a_story = self.more_menu.addAction("Add to Story maker", self._to_story)
        self.a_video = self.more_menu.addAction("Compress videos", self._to_video)
        self.more_menu.addSeparator()
        self.a_copy = self.more_menu.addAction("Copy to folder…", self.copy_selected)
        self.a_move = self.more_menu.addAction("Move to folder in this library…", self.move_selected)
        self.more_menu.addSeparator()
        self.more_menu.addAction("Show in folder", self._show_selected)
        self.b_more.setMenu(self.more_menu)
        self.b_clear = button("Clear", "link", lambda: self.grid.clearSelection())
        self.sel_bar.setLayout(hbox(self.sel_label, None, self.b_more, self.b_recycle, self.b_clear,
                                    spacing=6, margins=(12, 6, 8, 6)))
        self.sel_bar.hide()

        center = QWidget()
        center.setLayout(vbox(self.count, self.sel_bar, self.grid, spacing=6))
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
        QShortcut(QKeySequence("Ctrl+F"), self, activated=lambda: (self.search.setFocus(), self.search.selectAll()))
        QShortcut(QKeySequence("Ctrl+A"), self.grid, activated=self.grid.selectAll)
        QShortcut(QKeySequence("Delete"), self.grid, activated=self.recycle_selected)
        QShortcut(QKeySequence("Return"), self.grid,
                  activated=lambda: self.grid.currentIndex().isValid() and self._view(
                      self.grid.currentIndex().data(Qt.ItemDataRole.UserRole)))
        self.rows: list[dict] = []

    # --------------------------------------------------------------------------- data
    def refresh(self) -> None:
        self.rows = [dict(r) for r in self.lib.files("1", order="COALESCE(taken_at,'') DESC, rel_path")]
        problems = sum(1 for r in self.rows if r["error"] and r["kind"] != "other")
        self.kind.setItemText(3, f"Problems ({problems:,})" if problems else "Problems")
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
                    yi.setExpanded(True)
        self.tree.setCurrentItem(select)
        self.tree.blockSignals(False)

    def _apply_filter(self) -> None:
        cur = self.tree.currentItem()
        prefix = cur.data(0, Qt.ItemDataRole.UserRole) if cur else ""
        q = self.search.text().strip().lower()
        kind = self.kind.currentIndex()
        items = []
        for r in self.rows:
            k, err = r["kind"], r["error"]
            if kind == 0 and (k == "other" or err):
                continue
            if kind == 1 and (k != "image" or err):
                continue
            if kind == 2 and (k != "video" or err):
                continue
            if kind == 3 and not (err and k != "other"):
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
                          "tip": f"{r['rel_path']}\n{fmt_size(r['size'])}"})
        self.grid.set_items(items)
        self.count.setText(f"Showing {fmt_n(len(items), 'item')}")
        self.preview.clear()
        self._sel_changed()

    # --------------------------------------------------------------------------- view / zoom
    def _set_zoom(self, v: int) -> None:
        self.grid.delegate.cell = v
        self.grid.model_.layoutChanged.emit()

    def eventFilter(self, obj, event) -> bool:
        from PySide6.QtCore import QEvent
        if obj is self.grid.viewport() and event.type() == QEvent.Type.Wheel and \
                event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.zoom.setValue(self.zoom.value() + (12 if event.angleDelta().y() > 0 else -12))
            return True
        return super().eventFilter(obj, event)

    def _view(self, it: dict) -> None:
        if it.get("kind") == "video":
            open_path(self.lib.abspath(it["rel_path"]))
            return
        items = [i for i in self.grid.items() if i.get("kind") == "image" and not i.get("error")]
        if it in items:
            Viewer(self, self.ctx, items, items.index(it)).exec()

    # --------------------------------------------------------------------------- selection & batch
    def selected(self) -> list[dict]:
        return self.grid.selected_items()

    def on_busy_changed(self, busy: bool) -> None:
        self._sel_changed()

    def _sel_changed(self, *_):
        sel = self.selected()
        n = len(sel)
        self.sel_bar.setVisible(n > 1)
        if not n:
            return
        size = sum(r["size"] for r in sel)
        photos = [r for r in sel if r["kind"] == "image" and not r.get("error")]
        videos = [r for r in sel if r["kind"] == "video" and not r.get("error")]
        self.sel_label.setText(f"{n:,} selected · {fmt_size(size)}")
        idle = not self.busy
        for w in (self.b_recycle, self.a_copy, self.a_move):
            w.setEnabled(idle)
        self.a_story.setEnabled(bool(photos))
        self.a_story.setText(f"Add {len(photos)} photos to Story maker" if len(photos) > 1 else "Add to Story maker")
        self.a_video.setVisible(bool(videos))
        self.a_video.setText(f"Compress {fmt_n(len(videos), 'video')}")

    def recycle_selected(self) -> None:
        sel = self.selected()
        if not sel or self.busy:
            return
        size = sum(r["size"] for r in sel)
        self.apply_actions(
            "batch", "Move selected to Recovery", batch.plan_recycle(self.lib, sel),
            summary=recycle_summary(len(sel), size),
            details=["Only the items you selected are moved.", "A file that changed since you selected it is skipped."],
            confirm_text=f"Move {fmt_n(len(sel), 'item')}", note=recovery_note(),
            done_message=lambda r: f"Moved {fmt_n(r.done, 'item')} ({fmt_size(r.bytes)}) to Recovery.")

    def copy_selected(self) -> None:
        sel = self.selected()
        if not sel or self.busy:
            return
        dest = QFileDialog.getExistingDirectory(self, f"Copy {fmt_n(len(sel), 'item')} to…", str(Path.home()))
        if not dest:
            return
        try:
            acts = batch.plan_copy_to(self.lib, sel, dest)
        except ValueError as e:
            MessageDialog(self, "Choose another folder", str(e)).exec()
            return
        inside = self._inside_library(dest)
        self.apply_actions(
            "batch", "Copy selected", acts,
            summary=f"{fmt_n(len(acts), 'item')} ({fmt_size(sum(a.size for a in acts))}) will be copied to {dest}.",
            details=["Originals stay where they are.", "Each copy is checked byte for byte.",
                     "If a file with the same name is already there, the copy gets a new name."],
            confirm_text=f"Copy {fmt_n(len(acts), 'item')}",
            note="Undo removes the copies again (only if they are unchanged).",
            done_message=lambda r: f"Copied and verified {fmt_n(r.done, 'item')} ({fmt_size(r.bytes)}).",
            rescan=inside)

    def move_selected(self) -> None:
        sel = self.selected()
        if not sel or self.busy:
            return
        dest = QFileDialog.getExistingDirectory(self, f"Move {fmt_n(len(sel), 'item')} to a folder in this library",
                                                str(self.lib.root))
        if not dest:
            return
        try:
            acts = batch.plan_move_within(self.lib, sel, dest)
        except ValueError as e:
            MessageDialog(self, "Choose a folder inside this library", str(e)).exec()
            return
        if not acts:
            self.ctx.toast_requested.emit("Those items are already in that folder.", "")
            return
        rel = os.path.relpath(dest, self.lib.root)
        self.apply_actions(
            "batch", "Move selected", acts,
            summary=f"{fmt_n(len(acts), 'item')} will be moved to “{'library root' if rel == '.' else rel}”.",
            details=["Names are kept; a number is added only if the name is already taken there.",
                     "Thumbnails, dates and health fingerprints move with the files."],
            confirm_text=f"Move {fmt_n(len(acts), 'item')}",
            note="Every move is recorded. Undo puts each file back exactly where it was.",
            done_message=lambda r: f"Moved {fmt_n(r.done, 'item')}.")

    def _inside_library(self, path: str) -> bool:
        try:
            Path(path).resolve().relative_to(self.lib.root)
            return True
        except ValueError:
            return False

    def _show_selected(self) -> None:
        sel = self.selected()
        if sel:
            show_in_explorer(self.lib.abspath(sel[0]["rel_path"]))

    def _to_story(self) -> None:
        ids = [i["id"] for i in self.selected() if i["kind"] == "image" and not i.get("error")]
        if ids:
            self.ctx.story_selection.extend(ids)
            self.ctx.navigate.emit("story")

    def _to_editor(self) -> None:
        ids = [i["id"] for i in self.selected() if i["kind"] in ("image", "video") and not i.get("error")]
        if ids:
            self.ctx.edit_selection[:] = ids
            self.ctx.navigate.emit("editor")

    def _to_video(self) -> None:
        paths = [str(self.lib.abspath(i["rel_path"])) for i in self.selected() if i["kind"] == "video" and not i.get("error")]
        if paths:
            self.ctx.video_selection[:] = paths
            self.ctx.navigate.emit("video")

    def _menu(self, pos) -> None:
        idx = self.grid.indexAt(pos)
        if not idx.isValid():
            return
        it = idx.data(Qt.ItemDataRole.UserRole)
        sel = self.selected()
        if it not in sel:
            self.grid.setCurrentIndex(idx)
            sel = [it]
        m = QMenu(self)
        if it["kind"] in ("image", "video"):
            m.addAction("View" if it["kind"] == "image" else "Play", lambda: self._view(it))
            m.addAction("Open in default app", lambda: open_path(self.lib.abspath(it["rel_path"])))
        m.addAction("Show in folder", lambda: show_in_explorer(self.lib.abspath(it["rel_path"])))
        m.addSeparator()
        if any(i["kind"] in ("image", "video") and not i.get("error") for i in sel):
            m.addAction("Edit…", self._to_editor)
        if any(i["kind"] == "image" and not i.get("error") for i in sel):
            m.addAction("Add to Story maker", self._to_story)
        if any(i["kind"] == "video" and not i.get("error") for i in sel):
            m.addAction("Compress video" + ("s" if len(sel) > 1 else ""), self._to_video)
        m.addAction("Copy to folder…", self.copy_selected)
        m.addAction("Move to folder…", self.move_selected)
        m.addSeparator()
        m.addAction(f"Move {fmt_n(len(sel), 'item')} to Recovery", self.recycle_selected)
        for a in m.actions()[-4:]:
            a.setEnabled(not self.busy)
        m.exec(self.grid.viewport().mapToGlobal(pos))
