"""Albums: let Memoria suggest albums by event, place or person; keep, edit and export them."""
from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (QCheckBox, QComboBox, QFileDialog, QInputDialog, QLineEdit, QListWidget, QListWidgetItem,
                               QSpinBox, QSplitter, QStackedWidget, QTabWidget, QWidget)

from ...engine import albums, catalogue, config
from ..library_filters import FilterDialog, SORTS
from ..tasks import LatestCall
from ..widgets import (Banner, EmptyState, PhotoGrid, Preview, Viewer, button, confirm, fmt_n, fmt_size, hbox,
                       label, vbox)
from .base import Page

TRUST = ("<b>Albums don't move or copy anything.</b> An album only records which photos and videos belong to it, so "
         "a photo can be in many albums and deleting an album never touches the photos. Export makes copies in a "
         "folder you choose — and History can undo that.")
MODES = [("event", "Events & trips"), ("place", "Places"), ("person", "People")]


class AlbumsPage(Page):
    title = "Albums"
    subtitle = ("Group photos and videos into albums without moving them. Let Memoria suggest albums by event, place "
                "or person, then export any of them to folders.")

    def __init__(self, ctx):
        super().__init__(ctx)
        self.export_all_btn = button("Export all albums…", on_click=lambda: self.export(None),
                                     tip="Copy every album into its own folder")
        self.header_actions.addWidget(self.export_all_btn)
        self.saved: list[dict] = []
        self.suggestions: list[albums.Suggestion] = []
        self.album_offset = self.item_offset = self.suggestion_offset = self.suggestion_item_offset = 0
        self.album_total = 0
        self._suggestion_checks = set()
        self._albums_query, self._items_query, self._suggestion_query = (LatestCall(self) for _ in range(3))
        self._albums_query.result.connect(self._loaded_albums)
        self._items_query.result.connect(self._loaded_items)
        self._suggestion_query.result.connect(self._loaded_suggestion_items)
        for query in (self._albums_query, self._items_query, self._suggestion_query):
            query.failed.connect(lambda error: ctx.toast_requested.emit(str(error), ""))
        ctx.albums_changed.connect(self._mark_stale)
        ctx.people_changed.connect(self._mark_stale)

        self.tabs = QTabWidget()
        # -- your albums
        self.a_list = QListWidget()
        self.a_list.setIconSize(QSize(56, 56))
        self.a_list.setFixedWidth(300)
        self.a_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.a_list.setTextElideMode(Qt.TextElideMode.ElideRight)
        self.a_list.currentRowChanged.connect(self._show_album)
        self.a_title = label("", "h2")
        self.a_info = label("", "muted", wrap=True)
        self.rename_btn = button("Rename…", on_click=lambda: self.rename())
        self.export_btn = button("Export…", "primary", on_click=lambda: self.export([self._album()["id"]])
                                 if self._album() else None)
        self.delete_btn = button("Delete album…", on_click=self.delete)
        self.remove_btn = button("Remove from album", on_click=self.remove_selected,
                                 tip="Take the selected items out of this album (the files are not touched)")
        self.cover_btn = button("Use as cover", on_click=self.set_cover)
        self.rules_btn = button("Edit rules…", on_click=self.edit_rules)
        self.a_grid = PhotoGrid(ctx.thumbs, cell=150, captions=1)
        self.a_grid.current_item.connect(lambda it: self.preview.show_row(it))
        self.a_grid.activated_item.connect(lambda it: self._view(self.a_grid, it))
        self.a_grid.selectionModel().selectionChanged.connect(self._a_sel)
        a_detail = QWidget()
        self.item_previous = button("Previous", on_click=lambda: self._turn_items(-1))
        self.item_next = button("Next", on_click=lambda: self._turn_items(1))
        self.item_count = label("", "small")
        a_detail.setLayout(vbox(hbox(self.a_title, None, self.rules_btn, self.rename_btn, self.delete_btn, self.export_btn),
                                self.a_info, hbox(self.item_count, None, self.cover_btn, self.remove_btn,
                                                 self.item_previous, self.item_next), self.a_grid, spacing=6))
        a_split = QSplitter()
        album_left = QWidget()
        self.album_previous = button("Previous albums", on_click=lambda: self._turn_albums(-1))
        self.album_next = button("Next albums", on_click=lambda: self._turn_albums(1))
        self.album_count = label("", "small")
        album_left.setLayout(vbox(self.a_list, self.album_count, hbox(self.album_previous, self.album_next)))
        a_split.addWidget(album_left)
        a_split.addWidget(a_detail)
        a_split.setStretchFactor(1, 1)
        a_split.setChildrenCollapsible(False)
        self.a_stack = QStackedWidget()
        self.a_empty = EmptyState("\uE7AA", "No albums yet",
                                  "Let Memoria suggest albums from your photos' dates, places and people — or select "
                                  "photos in Photos & videos and choose “Add to album…”.",
                                  button("Make albums", "primary", lambda: self.tabs.setCurrentIndex(1)))
        self.a_stack.addWidget(self.a_empty)
        self.a_stack.addWidget(a_split)
        self.tabs.addTab(self.a_stack, "Your albums")

        # -- make albums
        self.mode = QComboBox()
        for _, text in MODES:
            self.mode.addItem(text)
        self.mode.currentIndexChanged.connect(self._mode_changed)
        self.gap = QSpinBox()
        self.gap.setRange(1, 72)
        self.gap.setValue(8)
        self.gap.setSuffix(" hours")
        self.gap.setToolTip("Photos taken further apart than this start a new album — except on a trip, where photos "
                            "in one place stay together for up to 3 days")
        self.min_items = QSpinBox()
        self.min_items.setRange(1, 100)
        self.min_items.setValue(3)
        self.videos = QCheckBox("Include videos")
        self.videos.setChecked(True)
        self.gap_label = label("New album after")
        self.suggest_btn = button("Suggest albums", "primary", lambda: self.suggest())
        options = hbox(self.mode, 12, self.gap_label, self.gap, 12, label("At least"), self.min_items,
                       label("items"), 12, self.videos, None, self.suggest_btn, spacing=6)
        self.s_list = QListWidget()
        self.s_list.setIconSize(QSize(48, 48))
        self.s_list.setFixedWidth(360)
        self.s_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.s_list.currentRowChanged.connect(self._show_suggestion)
        self.s_list.itemChanged.connect(self._suggestion_edited)
        self.s_title = label("", "h2")
        self.s_info = label("", "muted", wrap=True)
        self.s_grid = PhotoGrid(ctx.thumbs, cell=130, captions=1)
        self.s_grid.current_item.connect(lambda it: self.preview.show_row(it))
        self.s_grid.activated_item.connect(lambda it: self._view(self.s_grid, it))
        s_detail = QWidget()
        self.s_item_count = label("", "small")
        self.s_item_previous = button("Previous", on_click=lambda: self._turn_suggestion_items(-1))
        self.s_item_next = button("Next", on_click=lambda: self._turn_suggestion_items(1))
        s_detail.setLayout(vbox(self.s_title, self.s_info,
                               hbox(self.s_item_count, None, self.s_item_previous, self.s_item_next),
                               self.s_grid, spacing=6))
        s_split = QSplitter()
        suggestion_left = QWidget()
        self.s_previous = button("Previous albums", on_click=lambda: self._turn_suggestions(-1))
        self.s_next = button("Next albums", on_click=lambda: self._turn_suggestions(1))
        suggestion_left.setLayout(vbox(self.s_list, hbox(self.s_previous, self.s_next)))
        s_split.addWidget(suggestion_left)
        s_split.addWidget(s_detail)
        s_split.setStretchFactor(1, 1)
        s_split.setChildrenCollapsible(False)
        self.s_hint = label("", "muted", wrap=True)
        self.s_summary = label("")
        self.save_btn = button("Save albums", "primary", self.save)
        sel_all = button("Include all", "link", lambda: self._check_all(True))
        sel_none = button("Include none", "link", lambda: self._check_all(False))
        make = QWidget()
        lay = vbox(options, self.s_hint, s_split, hbox(sel_all, sel_none, 12, self.s_summary, None, self.save_btn),
                   spacing=10, margins=(0, 10, 0, 0))
        lay.setStretchFactor(s_split, 1)
        make.setLayout(lay)
        self.tabs.addTab(make, "Make albums")

        self.preview = Preview(ctx, 280)
        split = QSplitter()
        split.addWidget(self.tabs)
        split.addWidget(self.preview)
        split.setStretchFactor(0, 1)
        split.setChildrenCollapsible(False)
        self.body.addWidget(Banner(TRUST, "trust"))
        self.body.addWidget(split, 1)
        self._mode_changed()
        self._update_summary()

    # ------------------------------------------------------------------ lifecycle
    def _mark_stale(self):
        for key in ("_albums_query", "_items_query", "_suggestion_query"):
            if hasattr(self, key):
                getattr(self, key).invalidate()
        super()._mark_stale()

    def refresh(self) -> None:
        cur = self._album()
        cur_id = cur["id"] if cur else None
        if cur_id is not None and not self.lib.db.execute("SELECT 1 FROM albums WHERE id=?", (cur_id,)).fetchone():
            cur_id = None
        self._request_albums(cur_id)

    def _request_albums(self, album_id=None):
        if self.lib is None:
            return
        lib, offset, generation = self.lib, self.album_offset, self.ctx.generation
        def work():
            try:
                return lib, generation, album_id, albums.list_page(lib, offset, album_id=album_id)
            finally:
                lib.close_thread()
        self._albums_query.call(work)

    def _loaded_albums(self, result):
        lib, generation, cur_id, page = result
        if (lib, generation) != (self.lib, self.ctx.generation):
            return
        self.saved, self.album_total, self.album_offset = page
        self.a_list.blockSignals(True)
        self.a_list.clear()
        select = 0
        for i, a in enumerate(self.saved):
            when = albums.date_range(a["start"], a["end"]) if a["start"] else ""
            when = "" if when in a["name"] else f" · {when}"
            detail = "Smart album · updates automatically" if a["rule_json"] is not None else (
                f"{fmt_n(a['photos'], 'photo')} · {fmt_n(a['videos'], 'video')}{when}")
            it = QListWidgetItem(f"{a['name']}\n{detail}")
            self.a_list.addItem(it)
            if a["id"] == cur_id:
                select = i
        self.a_list.blockSignals(False)
        self.album_count.setText(f"{self.album_offset + 1 if self.album_total else 0:,}–"
                                 f"{self.album_offset + len(self.saved):,} of {self.album_total:,} albums")
        self.album_previous.setEnabled(self.album_offset > 0)
        self.album_next.setEnabled(self.album_offset + len(self.saved) < self.album_total)
        self.export_all_btn.setEnabled(bool(self.album_total) and not self.busy)
        if not self.saved:
            self.a_stack.setCurrentWidget(self.a_empty)
            self.a_grid.set_items([])
            self._items_query.invalidate()
            self.preview.clear()
            return
        self.a_stack.setCurrentIndex(1)
        self.a_list.blockSignals(True)
        self.a_list.setCurrentRow(select)
        self.a_list.blockSignals(False)
        self._show_album(select)

    def on_busy_changed(self, busy: bool) -> None:
        self.suggest_btn.setEnabled(not busy)
        self.export_all_btn.setEnabled(not busy and bool(self.saved))
        self.export_btn.setEnabled(not busy and self._album() is not None)
        for widget in (self.rename_btn, self.delete_btn, self.rules_btn):
            widget.setEnabled(not busy)
        self._a_sel()
        self._update_summary()

    # ------------------------------------------------------------------ your albums
    def _album(self) -> Optional[dict]:
        row = self.a_list.currentRow()
        return self.saved[row] if 0 <= row < len(self.saved) else None

    def open_album(self, album_id: int) -> None:
        self.tabs.setCurrentIndex(0)
        self._request_albums(album_id)

    def _turn_albums(self, direction):
        self.album_offset = max(0, self.album_offset + direction * albums.ALBUM_PAGE_SIZE)
        self._request_albums()

    def _show_album(self, row: int) -> None:
        self.item_offset = 0
        self._request_items()

    def _turn_items(self, direction):
        self.item_offset = max(0, self.item_offset + direction * catalogue.PAGE_SIZE)
        self._request_items()

    def _request_items(self):
        a = self._album()
        if a is None:
            return
        self.a_title.setText(a["name"])
        self.rules_btn.setVisible(a["rule_json"] is not None)
        self.a_info.setText("Loading album…")
        self.a_grid.set_items([])
        self.item_previous.setEnabled(False)
        self.item_next.setEnabled(False)
        lib, aid, offset, generation = self.lib, a["id"], self.item_offset, self.ctx.generation
        def work():
            try:
                return lib, generation, aid, offset, albums.item_page(lib, aid, offset)
            finally:
                lib.close_thread()
        self._items_query.call(work)

    def _loaded_items(self, result):
        lib, generation, aid, offset, page = result
        a = self._album()
        if (lib, generation) != (self.lib, self.ctx.generation) or a is None or a["id"] != aid:
            return
        rows, total, size = page
        self.a_info.setText(f"{total:,} matching items · {fmt_size(size)}. "
                            + ("Smart album: matches update automatically. " if a["rule_json"] is not None else "")
                            + "Files stay where they are. Selection applies only to this page (up to 500 items).")
        self.item_count.setText(f"{offset + 1 if total else 0:,}–{offset + len(rows):,} of {total:,}")
        self.item_previous.setEnabled(offset > 0)
        self.item_next.setEnabled(offset + len(rows) < total)
        self.a_grid.set_items([{**r, "caption": r["name"], "tip": lib.display_path(r["rel_path"])} for r in rows])
        self.preview.clear()
        self._a_sel()

    def _a_sel(self, *_) -> None:
        n = len(self.a_grid.selected_items())
        static = bool(self._album() and self._album()["rule_json"] is None)
        self.remove_btn.setEnabled(n > 0 and static and not self.busy)
        self.cover_btn.setEnabled(n == 1 and static and not self.busy)

    def edit_rules(self):
        a = self._album()
        if a is None or a["rule_json"] is None or self.busy:
            return
        filters, sort = catalogue.read_rule(a["rule_json"])
        dialog = FilterDialog(self, self.lib, filters)
        sort_box = QComboBox()
        for key, title in SORTS:
            sort_box.addItem(title, key)
        sort_box.setCurrentIndex(sort_box.findData(sort))
        search_box = QLineEdit(filters.search)
        dialog.layout().insertLayout(0, hbox(label("Search"), search_box, label("Sort"), sort_box))
        if dialog.exec():
            from dataclasses import replace
            albums.update_smart(self.lib, a["id"], replace(dialog.selected(), search=search_box.text()),
                                sort_box.currentData())
            self.ctx.albums_changed.emit()
            self.refresh()

    def rename(self, name: Optional[str] = None) -> None:
        a = self._album()
        if a is None or self.busy:
            return
        if name is None:
            name, ok = QInputDialog.getText(self, "Rename album", "Album name:", text=a["name"])
            if not ok:
                return
        try:
            albums.rename(self.lib, a["id"], name)
        except ValueError as e:
            self.ctx.toast_requested.emit(str(e), "")
            return
        self.refresh()
        self.ctx.albums_changed.emit()

    def delete(self) -> None:
        a = self._album()
        if a is None or self.busy:
            return
        if not confirm(self, f"Delete the album “{a['name']}”?",
                       "Only the album definition is deleted. All its files stay exactly where they are.",
                       [], "Delete album"):
            return
        albums.delete(self.lib, [a["id"]])
        self._request_albums()
        self.ctx.albums_changed.emit()
        self.ctx.toast_requested.emit(f"Deleted the album “{a['name']}”. No files were touched.", "")

    def remove_selected(self) -> None:
        a = self._album()
        sel = self.a_grid.selected_items()
        if a is None or not sel or self.busy or a["rule_json"] is not None:
            return
        albums.remove(self.lib, a["id"], [r["id"] for r in sel])
        self.refresh()
        self.ctx.albums_changed.emit()
        self.ctx.toast_requested.emit(f"Took {fmt_n(len(sel), 'item')} out of “{a['name']}”. The files are unchanged.", "")

    def set_cover(self) -> None:
        a = self._album()
        sel = self.a_grid.selected_items()
        if a is None or len(sel) != 1 or self.busy or a["rule_json"] is not None:
            return
        albums.set_cover(self.lib, a["id"], sel[0]["id"])
        self.refresh()
        self.ctx.albums_changed.emit()

    def export(self, album_ids: Optional[list[int]], dest: Optional[str] = None) -> None:
        if self.busy or self.lib is None:
            return
        ids = album_ids if album_ids is not None else [r[0] for r in self.lib.db.execute("SELECT id FROM albums")]
        if not ids:
            return
        if dest is None:
            start = config.default_export_dir()
            dest = QFileDialog.getExistingDirectory(self, "Export albums into this folder",
                                                    str(start if start.exists() else start.parent))
            if not dest:
                return
        lib = self.lib
        def work(progress):
            try:
                progress.check()
                return albums.plan_export(lib, ids, dest)
            finally:
                lib.close_thread()
        self.run("Preparing album export", work, lambda plan: self._export_ready(ids, dest, plan),
                 notify_success=False)

    def _export_ready(self, ids, dest, plan):
        if not plan:
            self.ctx.toast_requested.emit("Those albums are empty — nothing to export.", "")
            return
        names = [a["name"] for a in self.saved if a["id"] in ids]
        inside = albums.inside_library(self.lib, dest)
        shown = ", ".join(f"“{albums.folder_name(n)}”" for n in names[:3]) + (f" and {len(names) - 3} more" if len(names) > 3 else "")
        details = [f"One folder per album in {dest}: {shown}.",
                   "Originals stay where they are. Each copy is checked byte for byte.",
                   "Nothing is overwritten — if a name is taken, the copy gets a number."]
        if inside:
            details.insert(0, "<b>This folder is inside your library</b>, so the copies will also show up as "
                              "duplicates. A folder outside the library is usually better.")
        size = sum(a.size for a in plan)
        self.apply_actions(
            "albums", f"Export {fmt_n(len(ids), 'album')}", plan,
            summary=f"{fmt_n(len(plan), 'file')} ({fmt_size(size)}) will be copied into {fmt_n(len(ids), 'album folder')}.",
            details=details, confirm_text=f"Export {fmt_n(len(ids), 'album')}",
            note="Every export is recorded. Undo in History removes the copies again (the album folders stay, empty).",
            done_message=lambda r: f"Exported {fmt_n(len(ids), 'album')} ({fmt_n(r.done, 'file')}) to {dest}.",
            rescan=inside)

    # ------------------------------------------------------------------ make albums
    def _mode(self) -> str:
        return MODES[self.mode.currentIndex()][0]

    def _mode_changed(self, *_) -> None:
        m = self._mode()
        for w in (self.gap_label, self.gap):
            w.setVisible(m == "event")
        self.videos.setVisible(m != "person")
        self.s_hint.setText({
            "event": "Photos taken close together become one album. A trip — photos in one place over a few days — "
                     "stays together. Albums are named after the place (looked up offline) and the dates.",
            "place": "One album per town or region, across all years. Only photos with a location are used.",
            "person": "One album per person you have named on the People page."}[m])

    def suggest(self, mode: Optional[str] = None) -> None:
        if mode is not None:
            self.mode.setCurrentIndex([k for k, _ in MODES].index(mode))
        m, lib = self._mode(), self.lib
        opts = albums.EventOptions(gap_hours=self.gap.value(), min_items=self.min_items.value(),
                                   include_videos=self.videos.isChecked())

        def work(p):
            try:
                if m == "event":
                    return albums.suggest_events(lib, opts, p)
                if m == "place":
                    return albums.suggest_places(lib, opts.min_items, opts.include_videos, p)
                return albums.suggest_people(lib, opts.min_items)
            finally:
                lib.close_thread()
        self.run("Suggesting albums", work, self._show_suggestions)

    def _show_suggestions(self, sugg: list[albums.Suggestion]) -> None:
        self.suggestions = sugg
        self._suggestion_checks = {i for i, s in enumerate(sugg) if not s.exists}
        self.suggestion_offset = 0
        self._render_suggestions()

    def _turn_suggestions(self, direction):
        self.suggestion_offset = max(0, self.suggestion_offset + direction * albums.ALBUM_PAGE_SIZE)
        self._render_suggestions()

    def _render_suggestions(self):
        sugg = self.suggestions[self.suggestion_offset:self.suggestion_offset + albums.ALBUM_PAGE_SIZE]
        self.s_list.blockSignals(True)
        self.s_list.clear()
        for index, s in enumerate(sugg, self.suggestion_offset):
            it = QListWidgetItem(s.name)
            it.setFlags(it.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEditable)
            it.setCheckState(Qt.CheckState.Checked if index in self._suggestion_checks else Qt.CheckState.Unchecked)
            it.setToolTip(f"{s.detail}" + (" · already saved as an album" if s.exists else "") +
                          "\nDouble-click to rename")
            self.s_list.addItem(it)
        self.s_list.blockSignals(False)
        self.s_previous.setEnabled(self.suggestion_offset > 0)
        self.s_next.setEnabled(self.suggestion_offset + len(sugg) < len(self.suggestions))
        if sugg:
            self.s_list.setCurrentRow(0)
        else:
            self.s_grid.set_items([])
            self.preview.clear()
            self.s_title.setText("No albums to suggest")
            self.s_info.setText("Try a smaller minimum, a longer pause — or name people on the People page."
                                if self._mode() != "place" else "No photos with a location were found.")
        self._update_summary()

    def _show_suggestion(self, row: int) -> None:
        self.suggestion_item_offset = 0
        self._request_suggestion_items(row)

    def _turn_suggestion_items(self, direction):
        self.suggestion_item_offset = max(0, self.suggestion_item_offset + direction * catalogue.PAGE_SIZE)
        self._request_suggestion_items(self.s_list.currentRow())

    def _request_suggestion_items(self, row):
        row += self.suggestion_offset
        if not 0 <= row < len(self.suggestions):
            return
        s = self.suggestions[row]
        self.s_title.setText(s.name)
        when = albums.date_range(s.start, s.end) if s.start else ""
        self.s_info.setText(f"{s.detail}" + (f" · {when}" if when and when not in s.name else "") +
                            (" · already saved as an album" if s.exists else "") +
                            ". Double-click the name in the list to change it.")
        offset = self.suggestion_item_offset
        ids = s.file_ids[offset:offset + catalogue.PAGE_SIZE]
        self.s_item_count.setText(f"{offset + 1 if ids else 0:,}–{offset + len(ids):,} of {len(s.file_ids):,} items")
        self.s_item_previous.setEnabled(offset > 0)
        self.s_item_next.setEnabled(offset + len(ids) < len(s.file_ids))
        self.s_grid.set_items([])
        lib, generation = self.lib, self.ctx.generation
        def work():
            try:
                rows = {r["id"]: dict(r) for r in lib.db.execute(
                    f"SELECT * FROM files WHERE id IN ({','.join('?' for _ in ids)})", ids)}
                return lib, generation, row, [{**rows[i], "caption": rows[i]["name"], "tip": lib.display_path(rows[i]["rel_path"])}
                                  for i in ids if i in rows]
            finally:
                lib.close_thread()
        self._suggestion_query.call(work)

    def _loaded_suggestion_items(self, result):
        lib, generation, row, rows = result
        if (lib, generation) == (self.lib, self.ctx.generation) and row == self.suggestion_offset + self.s_list.currentRow():
            self.s_grid.set_items(rows)

    def _suggestion_edited(self, item: QListWidgetItem) -> None:
        row = self.s_list.row(item) + self.suggestion_offset
        if 0 <= row < len(self.suggestions):
            name = " ".join(item.text().split())
            if name:
                self.suggestions[row].name = name
            if item.checkState() == Qt.CheckState.Checked:
                self._suggestion_checks.add(row)
            else:
                self._suggestion_checks.discard(row)
            if row == self.s_list.currentRow() + self.suggestion_offset:
                self.s_title.setText(self.suggestions[row].name)
        self._update_summary()

    def _check_all(self, on: bool) -> None:
        self._suggestion_checks = set(range(len(self.suggestions))) if on else set()
        self._render_suggestions()

    def _chosen(self) -> list[albums.Suggestion]:
        return [self.suggestions[i] for i in sorted(self._suggestion_checks)]

    def _update_summary(self) -> None:
        chosen = self._chosen()
        n = sum(len(s.file_ids) for s in chosen)
        self.s_summary.setText(f"{fmt_n(len(chosen), 'album')} with {fmt_n(n, 'item')} will be saved. No files are "
                               "moved or copied." if chosen else "No albums selected")
        self.save_btn.setText(f"Save {fmt_n(len(chosen), 'album')}" if chosen else "Save albums")
        self.save_btn.setEnabled(bool(chosen) and not self.busy)

    def save(self) -> None:
        chosen = self._chosen()
        if not chosen or self.busy:
            return
        lib = self.lib
        def work(progress):
            try:
                for i, suggestion in enumerate(chosen):
                    progress.check()
                    albums.save(lib, [suggestion])
                    suggestion.exists = True
                    progress.update(i + 1, len(chosen), "Saving albums")
            finally:
                lib.close_thread()
        def done(_=None):
            self._show_suggestions(self.suggestions)
            self.ctx.albums_changed.emit()
            self.tabs.setCurrentIndex(0)
            self.ctx.toast_requested.emit("Saved albums. No files were moved or copied.", "")
        self.run("Saving albums", work, done, on_cancel=done)

    def _view(self, grid: PhotoGrid, it: dict) -> None:
        items = grid.items()
        v = Viewer(self, self.ctx, items, next((i for i, x in enumerate(items) if x["id"] == it["id"]), 0))
        v.resize(1200, 800)
        v.exec()

    def shutdown(self):
        for worker in (self._albums_query, self._items_query, self._suggestion_query):
            worker.wait()
        self.preview.shutdown()
