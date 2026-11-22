"""Browse the library: timeline, search, filters, preview, viewer and batch actions on a selection."""
from __future__ import annotations

import os
from dataclasses import replace
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (QComboBox, QDialog, QFileDialog, QFormLayout, QFrame, QHeaderView, QInputDialog, QLineEdit, QMenu, QSlider,
                               QSizePolicy, QSplitter, QTreeWidget, QTreeWidgetItem, QWidget)

from ..motion import Dialog
from ...engine import albums, batch, catalogue, organisation
from ..tasks import LatestCall
from ..library_filters import FilterDialog, KINDS, SORTS, metadata_filter_notes, sort_caption
from ..widgets import (MessageDialog, PhotoGrid, Preview, Viewer, button, fmt_n, fmt_size, hbox, label,
                       open_path, show_in_explorer, vbox)
from .base import Page, recovery_note, recycle_summary

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


class PhotosPage(Page):
    title = "Photos & videos"
    live_index_view = True
    subtitle = ("Browse by date. Double-click to view. Select several (Ctrl/Shift-click, Ctrl+A) to act on them "
                "together. Selection applies to the current page (up to 500 items).")

    def __init__(self, ctx, embedded=False):
        super().__init__(ctx)
        self._closed = False
        self.embedded = embedded
        if embedded:
            def hide_layout(layout):
                for i in range(layout.count()):
                    item = layout.itemAt(i)
                    if item.widget():
                        item.widget().hide()
                    elif item.layout():
                        hide_layout(item.layout())
            hide_layout(self.layout().itemAt(0).layout())
            self.layout().setContentsMargins(0, 0, 0, 0)
        self._query = LatestCall(self)
        self._query.result.connect(self._loaded)
        self._query.failed.connect(self._load_failed)
        self._request = None
        self.filters = catalogue.Filters()
        self.offset = 0
        self._live_deferred = False
        self._progress_counts = {"ready": 0, "pending": 0, "problems": 0}
        self.zoom = QSlider(Qt.Orientation.Horizontal)
        self.zoom.setRange(110, 280)
        self.zoom.setValue(156)
        self.zoom.setFixedWidth(140)
        self.zoom.setToolTip("Thumbnail size (Ctrl + mouse wheel)")
        self.zoom.valueChanged.connect(self._set_zoom)
        if not embedded:
            self.header_actions.addWidget(label("Thumbnails", "small"))
            self.header_actions.addWidget(self.zoom)
        else:
            self.zoom.hide()

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search name, folder, camera or person")
        self.search.setToolTip("Ctrl+F")
        self.search.setClearButtonEnabled(True)
        self.kind = QComboBox()
        for key, text in KINDS:
            self.kind.addItem(text, key)
        self.sort = QComboBox()
        for key, text in SORTS:
            self.sort.addItem(text, key)
        self.sort.setMaxVisibleItems(16)
        self.sort.setToolTip("Unknown metadata sorts last. Resolution means pixel count; bitrate is an overall estimate. "
                             "Choose Videos to exclude photos when sorting video metadata.")
        self.filter_note = label("", "small", wrap=True)
        self.filter_note.setTextFormat(Qt.TextFormat.PlainText)
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setColumnCount(2)
        self.tree.setIndentation(14)
        self.tree.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tree.header().setStretchLastSection(False)
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        left = QWidget()
        left.setLayout(vbox(self.search, self.kind, self.sort,
                            hbox(button("Filters…", on_click=self._filters),
                                 button("Clear", "link", self._clear_filters)),
                            button("Save smart album…", on_click=lambda: self.save_search()),
                            self.filter_note, self.tree, spacing=8))
        left.setFixedWidth(230)

        self.grid = PhotoGrid(ctx.thumbs, cell=156, captions=1)
        self.grid.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.grid.customContextMenuRequested.connect(self._menu)
        self.grid.current_item.connect(lambda it: self.preview.show_row(it))
        self.grid.activated_item.connect(self._view)
        self.grid.selectionModel().selectionChanged.connect(self._sel_changed)
        self.grid.viewport().installEventFilter(self)
        self.count = label("", "small", wrap=True)

        # selection bar (batch actions)
        self.sel_bar = QFrame()
        self.sel_bar.setObjectName("selectionBar")
        self.sel_label = label("", "h2")
        self.b_recycle = button("Move to Recovery", on_click=self.recycle_selected, tip="Delete key")
        self.b_organise = button("Tags / rating…", on_click=self.edit_organisation,
                                 tip="Edit only selected files on this page. Reject never deletes files.")
        self.b_more = button("More actions ▾", tip="Story maker, compress, copy, move, show in folder")
        self.more_menu = QMenu(self)
        self.a_edit = self.more_menu.addAction("Edit…", self._to_editor)
        self.a_story = self.more_menu.addAction("Add to Story maker", self._to_story)
        self.a_video = self.more_menu.addAction("Compress videos", self._to_video)
        self.a_album = self.more_menu.addAction("Add to album…", lambda: self.add_to_album())
        self.more_menu.addSeparator()
        self.a_copy = self.more_menu.addAction("Copy to folder…", self.copy_selected)
        self.a_move = self.more_menu.addAction("Move to folder in this library…", self.move_selected)
        self.more_menu.addSeparator()
        self.more_menu.addAction("Show in folder", self._show_selected)
        self.b_more.setMenu(self.more_menu)
        self.b_clear = button("Clear", "link", lambda: self.grid.clearSelection())
        for b in (self.b_organise, self.b_more, self.b_recycle, self.b_clear):
            b.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)  # never clip button text
        self.sel_bar.setLayout(vbox(hbox(self.sel_label, None, self.b_clear),
                                    hbox(self.b_organise, self.b_more, None, self.b_recycle, spacing=6),
                                    spacing=4, margins=(12, 6, 8, 8)))
        self.sel_bar.hide()

        center = QWidget()
        self.previous = button("Previous", on_click=lambda: self._turn_page(-1))
        self.next = button("Next", on_click=lambda: self._turn_page(1))
        center.setLayout(vbox(hbox(self.count, None, self.previous, self.next),
                             label("Selection and Ctrl+A apply to this page only (up to 500 items).", "small"),
                             self.sel_bar, self.grid, spacing=6))
        self.preview = Preview(ctx, hold_on_index_update=True)

        split = QSplitter()
        split.addWidget(left)
        split.addWidget(center)
        split.addWidget(self.preview)
        split.setStretchFactor(1, 1)
        split.setChildrenCollapsible(False)
        self.index_note = label("", "small", wrap=True)
        self.update_view = button("Update view", on_click=lambda: self.refresh(force=True),
                                  tip="Load the latest ready items; clears the current selection and returns to page 1")
        self.index_notice = QWidget()
        notice_layout = hbox(self.index_note, self.update_view)
        notice_layout.setStretch(0, 1)
        self.index_notice.setLayout(notice_layout)
        self.index_notice.hide()
        self.body.addWidget(self.index_notice)
        self.body.addWidget(split, 1)

        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(200)
        self._debounce.timeout.connect(self._apply_filter)
        self.search.textChanged.connect(self._debounce.start)
        self.kind.currentIndexChanged.connect(self._apply_filter)
        self.sort.currentIndexChanged.connect(self._apply_filter)
        self.tree.currentItemChanged.connect(lambda *_: self._apply_filter())
        QShortcut(QKeySequence("Ctrl+F"), self, activated=lambda: (self.search.setFocus(), self.search.selectAll()))
        QShortcut(QKeySequence("Ctrl+A"), self.grid, activated=self.grid.selectAll)
        QShortcut(QKeySequence("Delete"), self.grid, activated=self.recycle_selected)
        QShortcut(QKeySequence("Return"), self.grid,
                  activated=lambda: self.grid.currentIndex().isValid() and self._view(
                      self.grid.currentIndex().data(Qt.ItemDataRole.UserRole)))
        self.rows: list[dict] = []
        ctx.people_changed.connect(self._mark_stale)
        ctx.albums_changed.connect(self._mark_stale)
        ctx.index_progress.connect(self._mark_stale)

    # --------------------------------------------------------------------------- data
    def _mark_stale(self):
        if hasattr(self, "_query"):
            self._query.invalidate()
            self._request = None
        super()._mark_stale()

    def refresh(self, force: bool = False) -> None:
        if self._closed:
            return
        active_view = bool(self.selected()) or self.offset > 0 or self.grid.verticalScrollBar().value() > 0
        if not force and (self.ctx.indexing or self.ctx.index_update) and active_view:
            self._live_deferred = True
            self._update_index_notice()
            return
        self.stale = False
        problems = self._progress_counts["problems"]
        self.kind.setItemText(3, f"Problems ({problems:,})" if problems else "Problems")
        self._apply_filter()

    def _update_index_notice(self):
        counts = self._progress_counts
        if self.ctx.indexing:
            text = (f"Indexing continues · {counts['ready']:,} ready to browse · "
                    f"{counts['pending']:,} awaiting analysis/metadata. Utilities are temporarily locked.")
        elif counts["pending"]:
            text = (f"Ready photos/videos: {counts['ready']:,}. Awaiting analysis/metadata: {counts['pending']:,}; "
                    "F5 resumes without starting over.")
        else:
            text = "Indexing finished."
        if self._live_deferred:
            text += " View held to preserve your selection/position. Update view clears the selection."
        self.index_note.setText(text)
        self.update_view.setVisible(self._live_deferred)
        self.index_notice.setVisible(self.ctx.indexing or bool(counts["pending"]) or self._live_deferred)

    def _build_tree(self, months) -> None:
        cur = self.tree.currentItem()
        cur_key = cur.data(0, Qt.ItemDataRole.UserRole) if cur else None
        self.tree.blockSignals(True)
        self.tree.clear()
        counts: dict[str, dict[str, int]] = {}
        for r in months:
            t = r["month"] or ""
            y, m = (t[:4], t[5:7]) if t else ("Unknown", "")
            counts.setdefault(y, {})
            counts[y][m] = r["n"]
        if cur_key:
            y, m = ("Unknown", "") if cur_key == "Unknown" else (cur_key[:4], cur_key[5:7])
            counts.setdefault(y, {}).setdefault(m, 0)
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
                if not m or not m.isdigit() or not 1 <= int(m) <= 12:
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

    def _apply_filter(self, *_args) -> None:
        self._debounce.stop()
        self.offset = 0
        self._live_deferred = False
        self._update_index_notice()
        self._load_page()

    def _load_page(self) -> None:
        with self.ctx.diagnostics.measure("browse_page"):
            self._load_page_impl()

    def _load_page_impl(self) -> None:
        if self.lib is None or self._closed:
            return
        filters = self.current_filters()
        base = replace(self.filters, kind=self.kind.currentData(), search=self.search.text().strip(),
                       ready_only=self.kind.currentData() not in ("all", "other"))
        lib, sort, offset = self.lib, self.sort.currentData(), self.offset
        request = (lib, self.ctx.generation, filters, sort, offset)
        self._request = request
        self.count.setText("Loading matching files…")
        self.previous.setEnabled(False)
        self.next.setEnabled(False)
        self.rows = []
        self.grid.set_items([])
        self.preview.clear()
        def work():
            try:
                sql, params = catalogue.where(base)
                months = [dict(r) for r in lib.db.execute(
                    f"SELECT substr(taken_at,1,7) AS month,COUNT(*) AS n FROM files f "
                    f"WHERE {sql} GROUP BY month ORDER BY month DESC LIMIT 1200", params)]
                return request, catalogue.page(lib, filters, sort, offset), months, catalogue.browse_progress(lib)
            finally:
                lib.close_thread()
        self._query.call(work)

    def current_filters(self):
        cur = self.tree.currentItem()
        prefix = cur.data(0, Qt.ItemDataRole.UserRole) if cur else ""
        filters = replace(self.filters, kind=self.kind.currentData(), search=self.search.text().strip(),
                          ready_only=self.kind.currentData() not in ("all", "other"))
        if prefix == "Unknown":
            filters = replace(filters, undated=True)
        elif prefix:
            filters = catalogue.in_period(filters, prefix)
        return filters

    def _load_failed(self, error):
        if not self._request or self._request[:2] != (self.lib, self.ctx.generation):
            return
        self.rows = []
        self.grid.set_items([])
        self.preview.clear()
        self.count.setText("Could not load matching files")
        self.ctx.toast_requested.emit(str(error), "")

    def _loaded(self, result):
        request, page, months, progress = result
        if request != self._request or request[:2] != (self.lib, self.ctx.generation):
            return
        lib, _, filters, sort, offset = request
        self.rows, total, size = page
        self._progress_counts = progress
        problems = progress["problems"]
        self.kind.setItemText(3, f"Problems ({problems:,})" if problems else "Problems")
        self._build_tree(months)
        self._update_index_notice()
        items = [{**r, "caption": sort_caption(r, sort),
                  "tip": f"{lib.display_path(r['rel_path'])}\n{fmt_size(r['size'])} · "
                         f"{r['rating']} stars · {'Favourite · ' if r['favorite'] else ''}{r['review']}"} for r in self.rows]
        if self.ctx.indexing or self.ctx.index_update:
            self.ctx.thumbs.invalidate(r["id"] for r in self.rows)
        self.grid.set_items(items)
        self.count.setText(f"{self.offset + 1 if total else 0:,}–{self.offset + len(items):,} of {total:,} · {fmt_size(size)}")
        self.count.setToolTip("Selection and Ctrl+A apply to this page only (up to 500 items).")
        self.previous.setEnabled(self.offset > 0)
        self.next.setEnabled(self.offset + len(items) < total)
        active = []
        if filters.folder or not filters.recursive:
            active.append(self.lib.display_path(filters.folder) if filters.folder else "Files directly in root")
        if filters.start or filters.end:
            active.append(f"Dates: {filters.start or 'any'} to before {filters.end or 'any'}")
        if filters.min_bytes or filters.max_bytes is not None:
            active.append(f"Size: {fmt_size(filters.min_bytes)}–{fmt_size(filters.max_bytes) if filters.max_bytes is not None else 'any'}")
        if filters.extension is not None:
            active.append(filters.extension or "No extension")
        if filters.location != "all" or filters.bbox:
            active.append("Map area" if filters.bbox else filters.location)
        if filters.person is not None or filters.faces != "all":
            active.append("People / face filter")
        active.extend(metadata_filter_notes(filters))
        self.filter_note.setText("\n".join(active[:5]) + (f"\n+{len(active)-5} more (see Filters…)" if len(active) > 5 else ""))
        self.filter_note.setToolTip("\n".join(active))
        self.preview.clear()
        self._sel_changed()

    def _turn_page(self, direction: int):
        self._live_deferred = False
        self._update_index_notice()
        self.offset = max(0, self.offset + direction * catalogue.PAGE_SIZE)
        self._load_page()

    def _filters(self):
        if self.lib is None:
            return
        dlg = FilterDialog(self, self.lib, replace(self.filters, kind=self.kind.currentData()))
        if dlg.exec():
            self.open_filters(dlg.selected())

    def _clear_filters(self):
        if self.embedded:
            self.open_all_files()
        else:
            self.open_filters(catalogue.Filters())

    def open_filters(self, filters: catalogue.Filters, sort: str | None = None):
        catalogue.where(filters)
        if sort is not None:
            if sort not in catalogue.SORTS:
                raise ValueError("Unknown sort.")
            self.sort.blockSignals(True)
            self.sort.setCurrentIndex(self.sort.findData(sort))
            self.sort.blockSignals(False)
        self.filters = filters
        self.search.blockSignals(True)
        self.kind.blockSignals(True)
        self.search.setText(filters.search)
        self.kind.setCurrentIndex(self.kind.findData(filters.kind))
        self.search.blockSignals(False)
        self.kind.blockSignals(False)
        self.tree.blockSignals(True)
        self.tree.clear()
        self.tree.blockSignals(False)
        self._apply_filter()

    def open_all_files(self):
        self.open_filters(catalogue.Filters(kind="all"), "largest")

    def shutdown(self):
        self._closed = True
        self._debounce.stop()
        self._query.wait()
        self.preview.shutdown()

    def save_search(self, name=None):
        if self.lib is None or self.busy:
            return
        if name is None:
            name, ok = QInputDialog.getText(self, "Save smart album", "Name for these filters and sort:")
            if not ok:
                return
        try:
            aid = albums.create_smart(self.lib, name, self.current_filters(), self.sort.currentData())
        except ValueError as error:
            self.ctx.toast_requested.emit(str(error), "")
            return
        self.ctx.albums_changed.emit()
        self.ctx.toast_requested.emit("Saved smart album. Matches update automatically; no files were copied.", "")
        return aid

    def edit_organisation(self):
        selected = self.selected()
        if not selected or self.busy:
            return
        dialog = Dialog(self)
        dialog.setWindowTitle(f"Organise {len(selected):,} selected files")
        form = QFormLayout()
        if len(selected) == 1:
            current = organisation.state(self.lib, selected[0]["id"])
            summary = label(f"Current: {current['rating']} stars · "
                            f"{'Favourite' if current['favorite'] else 'Not favourite'} · {current['review']}\n"
                            f"Tags: {', '.join(current['tags']) or 'none'}", wrap=True)
            summary.setTextFormat(Qt.TextFormat.PlainText)
            form.addRow(summary)
        rating, favorite, review = QComboBox(), QComboBox(), QComboBox()
        for box in (rating, favorite, review):
            box.addItem("Leave unchanged", None)
        for value in range(6):
            rating.addItem("Unrated" if not value else "★" * value, value)
        for title, value in (("Favourite", True), ("Not favourite", False)):
            favorite.addItem(title, value)
        for value in organisation.REVIEWS:
            review.addItem(value.capitalize(), value)
        add_tags, remove_tags = QLineEdit(), QLineEdit()
        for box in (add_tags, remove_tags):
            box.setPlaceholderText("Comma-separated tag names")
        for title, widget in (("Rating", rating), ("Favourite", favorite), ("Review", review),
                              ("Add tags", add_tags), ("Remove tags", remove_tags)):
            form.addRow(title, widget)
        dialog.setLayout(vbox(label(f"Only these {len(selected):,} selected files on this page are edited. "
                                    "Reject is a mark, never deletion.", wrap=True), form,
                               hbox(None, button("Cancel", on_click=dialog.reject),
                                    button("Apply", "primary", dialog.accept)), margins=(20, 20, 20, 20)))
        if not dialog.exec():
            return
        lib, ids = self.lib, [r["id"] for r in selected]
        changes = dict(rating=rating.currentData(), favorite=favorite.currentData(), review=review.currentData(),
                       add_tags=[t.strip() for t in add_tags.text().split(",") if t.strip()],
                       remove_tags=[t.strip() for t in remove_tags.text().split(",") if t.strip()])
        def work(progress):
            try:
                progress.check()
                return organisation.edit(lib, ids, **changes)
            finally:
                lib.close_thread()
        def done(count):
            self.ctx.library_modified.emit()
            self.ctx.albums_changed.emit()
            self.ctx.toast_requested.emit(f"Updated {count:,} selected files. No originals were changed.", "")
            self._load_page()
        self.run("Updating organisation", work, done)

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
        self.sel_bar.setVisible(n > 0)
        if not n:
            return
        size = sum(r["size"] for r in sel)
        photos = [r for r in sel if r["kind"] == "image" and not r.get("error")]
        videos = [r for r in sel if r["kind"] == "video" and not r.get("error")]
        self.sel_label.setText(f"{n:,} selected · {fmt_size(size)}")
        idle = not self.busy
        for w in (self.b_recycle, self.b_organise, self.a_copy, self.a_move, self.a_edit, self.a_album, self.a_video):
            w.setEnabled(idle)
        self.a_story.setEnabled(idle and bool(photos))
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
        return self.lib.contains(path)

    def _show_selected(self) -> None:
        sel = self.selected()
        if sel:
            show_in_explorer(self.lib.abspath(sel[0]["rel_path"]))

    def _to_story(self) -> None:
        if self.busy:
            return
        ids = [i["id"] for i in self.selected() if i["kind"] == "image" and not i.get("error")]
        if ids:
            self.ctx.story_selection.extend(ids)
            self.ctx.navigate.emit("story")

    def _to_editor(self) -> None:
        if self.busy:
            return
        ids = [i["id"] for i in self.selected() if i["kind"] in ("image", "video") and not i.get("error")]
        if ids:
            self.ctx.edit_selection[:] = ids
            self.ctx.navigate.emit("editor")

    def add_to_album(self, name: str | None = None) -> None:
        if self.busy:
            return
        sel = [i for i in self.selected() if i["kind"] in ("image", "video")]
        if not sel:
            return
        if name is None:
            dlg = QInputDialog(self)
            dlg.setWindowTitle("Add to album")
            dlg.setLabelText(f"Add {fmt_n(len(sel), 'item')} to an album — pick one, or type a new name:")
            # A bounded suggestion list; typing an existing name still finds albums beyond it.
            dlg.setComboBoxItems([r[0] for r in self.lib.db.execute(
                "SELECT name FROM albums WHERE rule_json IS NULL ORDER BY name COLLATE NOCASE LIMIT 100")])
            dlg.setComboBoxEditable(True)
            dlg.setTextValue("")
            if not dlg.exec():
                return
            name = dlg.textValue()
        name = " ".join(name.split())
        if not name:
            return
        a = self.lib.db.execute("SELECT id,name FROM albums WHERE name=? COLLATE NOCASE AND rule_json IS NULL",
                                (name,)).fetchone()
        if a:
            n = albums.add(self.lib, a["id"], [i["id"] for i in sel])
            msg = f"Added {fmt_n(n, 'item')} to “{a['name']}”." if n else f"Already in “{a['name']}”."
        else:
            albums.create(self.lib, name, [i["id"] for i in sel])
            msg = f"Created the album “{name}” with {fmt_n(len(sel), 'item')}."
        self.ctx.albums_changed.emit()
        self.ctx.toast_requested.emit(msg + " No files were moved or copied.", "")

    def _to_video(self) -> None:
        if self.busy:
            return
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
        utility_start = len(m.actions())
        if any(i["kind"] in ("image", "video") and not i.get("error") for i in sel):
            m.addAction("Edit…", self._to_editor)
        if any(i["kind"] == "image" and not i.get("error") for i in sel):
            m.addAction("Add to Story maker", self._to_story)
        if any(i["kind"] == "video" and not i.get("error") for i in sel):
            m.addAction("Compress video" + ("s" if len(sel) > 1 else ""), self._to_video)
        m.addAction("Add to album…", lambda: self.add_to_album())
        m.addAction("Tags / rating / favourite / Pick-Reject…", self.edit_organisation)
        m.addAction("Copy to folder…", self.copy_selected)
        m.addAction("Move to folder…", self.move_selected)
        m.addSeparator()
        m.addAction(f"Move {fmt_n(len(sel), 'item')} to Recovery", self.recycle_selected)
        for a in m.actions()[utility_start:]:
            a.setEnabled(not self.busy)
        m.exec(self.grid.viewport().mapToGlobal(pos))
