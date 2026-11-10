"""People: find faces, name people, and see every photo someone is in."""
from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (QAbstractItemView, QInputDialog, QLineEdit, QListView, QListWidget, QListWidgetItem,
                               QMenu, QSplitter, QStackedWidget, QWidget)

from ...engine import albums, faces
from .. import people_queries as queries
from ..tasks import LatestCall
from ..widgets import (Banner, EmptyState, PhotoGrid, Preview, Viewer, button, confirm, fmt_n, hbox, label, vbox)
from .base import Page

TRUST = ("<b>Private by design.</b> Faces are found and recognised on this computer by small open models. Face "
         "data stays in this library's catalogue — nothing is uploaded — and photos are never changed. "
         "You can forget all face data at any time.")
class PeoplePage(Page):
    title = "People"
    subtitle = "Find the people in your photos, name them, and see every photo someone is in."

    def __init__(self, ctx):
        super().__init__(ctx)
        self.find_btn = button("Find people", "primary", self.find, tip="Look for faces in new or changed photos")
        self.more_btn = button("More")
        menu = QMenu(self)
        self.small_action = menu.addAction("Show faces seen in only one photo", self._toggle_small)
        self.small_action.setCheckable(True)
        menu.addAction("Unhide hidden groups", self.unhide)
        menu.addSeparator()
        menu.addAction("Forget all face data…", self.forget_all)
        self.more_btn.setMenu(menu)
        self.header_actions.addWidget(self.more_btn)
        self.header_actions.addWidget(self.find_btn)
        self.groups: list[faces.Group] = []
        self.shown = []
        self.min_photos = 2
        self.mode = "person"          # "person" | "similar"

        self.stack = QStackedWidget()
        if faces.available():
            self.empty = EmptyState("\uE716", "Find the people in your photos",
                                    "Memoria looks for faces in your photos and groups the ones that look alike. "
                                    "Give a group a name and you can find every photo of that person. Everything "
                                    "happens on this computer; photos are never changed.",
                                    button("Find people", "primary", self.find))
        else:  # pragma: no cover - models are bundled
            self.empty = EmptyState("\uE716", "Face recognition isn't available",
                                    "The face models are missing from this installation.")
        self.none = EmptyState("\uE716", "No faces found", "None of the photos checked so far has a recognisable face.")
        self.stack.addWidget(self.empty)
        self.stack.addWidget(self.none)

        self.status = label("", "muted")
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search people")
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self._search_changed)
        self.list = QListWidget()
        self.list.setIconSize(QSize(56, 56))
        self.list.currentRowChanged.connect(self._show_group)
        left = QWidget()
        self.group_scope = label("", "small", wrap=True)
        self.group_prev = button("Previous", on_click=lambda: self._group_step(-1))
        self.group_next = button("Next", on_click=lambda: self._group_step(1))
        left.setLayout(vbox(self.search, self.list, self.group_scope,
                           hbox(self.group_prev, self.group_next), spacing=8))
        left.setFixedWidth(280)

        self.g_title = label("", "h2")
        self.g_info = label("", "muted", wrap=True)
        self.name_btn = button("Name…", "primary", lambda: self.name_group())
        self.merge_btn = button("Same person as…")
        self.merge_menu = QMenu(self)
        self.merge_btn.setMenu(self.merge_menu)
        self.hide_btn = button("Hide", on_click=self.hide_group, tip="Hide this group (strangers, statues, posters…)")
        self.album_btn = button("Make album", on_click=self.make_album, tip="Save these photos as an album")
        self.faces = QListWidget()
        self.faces.setViewMode(QListView.ViewMode.IconMode)
        self.faces.setIconSize(QSize(72, 72))
        self.faces.setGridSize(QSize(84, 84))
        self.faces.setFlow(QListView.Flow.LeftToRight)
        self.faces.setWrapping(False)
        self.faces.setFixedHeight(104)
        self.faces.setMovement(QListView.Movement.Static)
        self.faces.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.faces.itemSelectionChanged.connect(self._faces_selected)
        self.not_btn = button("Not this person", on_click=self.not_this_person,
                              tip="Remove the selected faces; they won't be matched to this person again")
        self.like_btn = button("Find look-alikes", on_click=self.find_similar,
                               tip="Photos with a face like the selected one, across the whole library")
        self.back_btn = button("← Back", "link", self._back)
        self.grid = PhotoGrid(ctx.thumbs, cell=150, captions=1)
        self.grid.current_item.connect(lambda it: self.preview.show_row(it))
        self.grid.activated_item.connect(self._view)
        self.preview = Preview(ctx, 280)
        self.photo_scope = label("", "small", wrap=True)
        self.photo_prev = button("Previous photos", on_click=lambda: self._content_step("photo", -1))
        self.photo_next = button("Next photos", on_click=lambda: self._content_step("photo", 1))
        self.face_scope = label("", "small", wrap=True)
        self.face_prev = button("Previous faces", on_click=lambda: self._content_step("face", -1))
        self.face_next = button("Next faces", on_click=lambda: self._content_step("face", 1))
        detail = QWidget()
        detail.setLayout(vbox(hbox(self.back_btn, self.g_title, None), self.g_info,
                              hbox(self.name_btn, self.merge_btn, self.album_btn, self.hide_btn, None),
                              hbox(label("<b>Faces</b>"), None, self.like_btn, self.not_btn), self.faces,
                              hbox(self.face_scope, None, self.face_prev, self.face_next),
                              self.grid, hbox(self.photo_scope, None, self.photo_prev, self.photo_next), spacing=6))
        split = QSplitter()
        split.addWidget(left)
        split.addWidget(detail)
        split.addWidget(self.preview)
        split.setStretchFactor(1, 1)
        split.setChildrenCollapsible(False)
        results = QWidget()
        lay = vbox(Banner(TRUST, "trust"), self.status, split, spacing=10)
        lay.setStretchFactor(split, 1)
        results.setLayout(lay)
        self.results = results
        self.stack.addWidget(results)
        self.body.addWidget(self.stack, 1)
        self._closed = False
        self.group_offset = self.photo_offset = self.face_offset = 0
        self.group_total = 0
        self._covers = {}
        self._similar_rows = []
        self._select_name = None
        self.bg, self.contents_bg = LatestCall(self), LatestCall(self)
        self.bg.result.connect(self._groups_loaded)
        self.bg.failed.connect(self._failed)
        self.contents_bg.result.connect(self._contents_loaded)
        self.contents_bg.failed.connect(self._failed)
        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(180)
        self.search_timer.timeout.connect(self.refresh)
        ctx.library_opened.connect(self._invalidate)
        ctx.library_modified.connect(self._invalidate)

    # ------------------------------------------------------------------ lifecycle
    def refresh(self) -> None:
        if self._closed or self.lib is None:
            return
        if not faces.available():
            self.stack.setCurrentWidget(self.empty)
            return
        lib, generation = self.lib, self.ctx.generation
        minimum, search, offset = self.min_photos, self.search.text(), self.group_offset
        self.stack.setCurrentWidget(self.results)
        self.status.setText("Reading people…")
        self.contents_bg.invalidate()
        self.list.setEnabled(False)
        self.grid.set_items([])
        self.faces.clear()
        self.preview.clear()
        def work():
            try:
                return (lib, generation, queries.group_page(lib, minimum, search, offset))
            finally:
                lib.close_thread()
        self.bg.call(work)

    def _groups_loaded(self, result):
        lib, generation, data = result
        if self._closed or (lib, generation) != (self.lib, self.ctx.generation):
            return
        st = data["status"]
        scanned = st["photos"] - st["pending"]
        if scanned == 0 and st["faces"] == 0:
            self.stack.setCurrentWidget(self.empty)
            return
        self.groups, self._covers = data["groups"], data["covers"]
        self.group_total, self.group_offset = data["total"], data["offset"]
        self.list.setEnabled(True)
        self._update_status(st)
        if not self.groups and not self.search.text().strip():
            self.stack.setCurrentWidget(self.none)
            return
        self.stack.setCurrentWidget(self.results)
        self._fill_list()

    def _update_status(self, st: Optional[dict] = None) -> None:
        st = st or getattr(self, "_status", {})
        self._status = st
        if not st:
            return
        text = (f"{fmt_n(st['photos'] - st['pending'], 'photo')} checked · {fmt_n(st['faces'], 'face')} · "
                f"{fmt_n(st['people'], 'person named', 'people named')}")
        if st["pending"]:
            text += f" · {fmt_n(st['pending'], 'new photo')} not checked yet — click Find people"
        self.status.setText(text)

    def on_busy_changed(self, busy: bool) -> None:
        self.find_btn.setEnabled(not busy and faces.available())

    def find(self) -> None:
        lib = self.lib
        def work(progress):
            try:
                return faces.scan(lib, progress)
            finally:
                lib.close_thread()
        self.run("Finding people", work, self._found)

    def _found(self, res: faces.ScanResult) -> None:
        self.refresh()
        self.ctx.people_changed.emit()
        self.ctx.toast_requested.emit(
            f"Checked {fmt_n(res.checked, 'photo')} and found {fmt_n(res.faces, 'face')}." if res.checked else
            "All photos were already checked.", "")

    # ------------------------------------------------------------------ list
    def _label(self, g: faces.Group) -> str:
        return g.name or "Unnamed person"

    def _fill_list(self) -> None:
        cur = self._current()
        key = cur.key if cur else None
        self.list.blockSignals(True)
        self.list.clear()
        self.shown = self.groups
        select = 0
        for i, g in enumerate(self.shown):
            sub = fmt_n(g.photos, "photo") + ("" if g.named else " · click Name… to name")
            it = QListWidgetItem(f"{self._label(g)}\n{sub}")
            image = self._covers.get(g.cover)
            if image is not None and not image.isNull():
                it.setIcon(QIcon(QPixmap.fromImage(image)))
            self.list.addItem(it)
            if g.key == key:
                select = i
            if self._select_name and (g.name or "").casefold() == self._select_name.casefold():
                select = i
        self._select_name = None
        self.group_scope.setText(f"People {self.group_offset + 1 if self.shown else 0:,}–"
                                 f"{self.group_offset + len(self.shown):,} of {self.group_total:,}. "
                                 "Search finds people across all pages.")
        self.group_prev.setEnabled(self.group_offset > 0)
        self.group_next.setEnabled(self.group_offset + len(self.shown) < self.group_total)
        self.list.blockSignals(False)
        if self.shown:
            self.list.blockSignals(True)
            self.list.setCurrentRow(select)
            self.list.blockSignals(False)
            self._show_group(select)
        else:
            self.grid.set_items([])
            self.faces.clear()
            self.g_title.setText("No one matches")
            self.g_info.setText("")

    def _search_changed(self):
        self.group_offset = 0
        self.bg.invalidate()
        self.contents_bg.invalidate()
        self.search_timer.start()

    def _group_step(self, delta):
        self.group_offset = max(0, self.group_offset + delta * queries.GROUP_PAGE)
        self.refresh()

    def _current(self) -> Optional[faces.Group]:
        row = self.list.currentRow()
        shown = getattr(self, "shown", [])
        return shown[row] if 0 <= row < len(shown) else None

    def _show_group(self, row: int) -> None:
        g = self._current()
        if g is None:
            return
        self.mode = "person"
        self._similar_rows = []
        self.photo_offset = self.face_offset = 0
        self.back_btn.setVisible(False)
        self.g_title.setText(self._label(g))
        self.g_info.setText(
            f"{fmt_n(g.photos, 'photo')} with {fmt_n(g.faces, 'face')}. " +
            ("Photos are matched automatically; remove any that aren't this person with “Not this person”."
             if g.named else "These faces look alike. Name them to find every photo of this person — or use "
                             "“Same person as…” if they're already named."))
        self.name_btn.setText("Rename…" if g.named else "Name…")
        self.hide_btn.setText("Remove name" if g.named else "Hide")
        self.merge_menu.clear()
        others = [o for o in self.groups if o.named and o.key != g.key]
        for o in others:
            self.merge_menu.addAction(o.name, lambda o=o: self.merge_into(o))
        self.merge_menu.addAction("Choose another name…", self.name_group)
        self.merge_btn.setEnabled(True)
        self._load_contents()

    def _load_contents(self):
        g = self._current()
        if g is None or self.lib is None:
            return
        lib, generation = self.lib, self.ctx.generation
        photo_offset, face_offset, key = self.photo_offset, self.face_offset, g.key
        self.photo_scope.setText("Loading photos…")
        self.face_scope.setText("Loading faces…")
        self.grid.set_items([])
        self.faces.clear()
        self.preview.clear()
        self._faces_selected()
        def work():
            try:
                return (lib, generation, key, queries.group_contents(lib, key, photo_offset, face_offset))
            finally:
                lib.close_thread()
        self.contents_bg.call(work)

    def _contents_loaded(self, result):
        lib, generation, key, data = result
        group = self._current()
        if self._closed or (lib, generation) != (self.lib, self.ctx.generation) or not group or group.key != key:
            return
        if self.mode == "similar":
            self._similar_rows = data["photos"]
            self.photo_offset = 0
            self._show_similar()
            return
        for r in data["faces"]:
            it = QListWidgetItem()
            image = data["thumbs"][r["face_id"]]
            if not image.isNull():
                it.setIcon(QIcon(QPixmap.fromImage(image)))
            it.setToolTip(r["rel_path"])
            it.setData(Qt.ItemDataRole.UserRole, r["face_id"])
            self.faces.addItem(it)
        rows = data["photos"]
        self.grid.set_items([{**r, "caption": r["name"], "tip": r["rel_path"]} for r in rows])
        self.photo_scope.setText(f"Photos {self.photo_offset + 1 if rows else 0:,}–"
                                 f"{self.photo_offset + len(rows):,} of {group.photos:,}. Make album includes all pages.")
        self.face_scope.setText(f"Faces {self.face_offset + 1 if data['faces'] else 0:,}–"
                                f"{self.face_offset + len(data['faces']):,} of {group.faces:,}. "
                                "Corrections apply to selected faces on this page.")
        self.photo_prev.setEnabled(self.photo_offset > 0)
        self.photo_next.setEnabled(self.photo_offset + len(rows) < group.photos)
        self.face_prev.setEnabled(self.face_offset > 0)
        self.face_next.setEnabled(self.face_offset + len(data["faces"]) < group.faces)
        self._faces_selected()

    def _content_step(self, kind, delta):
        if self.mode != "person":
            if kind == "photo":
                self.photo_offset = max(0, min(
                    max(0, (len(self._similar_rows) - 1) // queries.PHOTO_PAGE) * queries.PHOTO_PAGE,
                    self.photo_offset + delta * queries.PHOTO_PAGE))
                self._show_similar()
            return
        if kind == "photo":
            self.photo_offset = max(0, self.photo_offset + delta * queries.PHOTO_PAGE)
        else:
            self.face_offset = max(0, self.face_offset + delta * queries.FACE_PAGE)
        self._load_contents()

    def _show_similar(self):
        rows = self._similar_rows[self.photo_offset:self.photo_offset + queries.PHOTO_PAGE]
        self.preview.clear()
        self.grid.set_items([{**r, "caption": f"{round(r['similarity'] * 100)}% alike", "tip": r["rel_path"]}
                             for r in rows])
        self.g_info.setText(f"{len(self._similar_rows):,} matching photos (top 2,000 at most), most alike first. "
                            "Make album saves these matching results across all pages.")
        self.photo_scope.setText(f"Photos {self.photo_offset + 1 if rows else 0:,}–"
                                 f"{self.photo_offset + len(rows):,} of {len(self._similar_rows):,} look-alikes. "
                                 "Photo selection applies to this page.")
        self.photo_prev.setEnabled(self.photo_offset > 0)
        self.photo_next.setEnabled(self.photo_offset + len(rows) < len(self._similar_rows))

    def _invalidate(self):
        self.bg.invalidate()
        self.contents_bg.invalidate()
        self.search_timer.stop()
        self.preview.clear()
        self.grid.set_items([])
        self.faces.clear()
        self.groups = []
        self._similar_rows = []
        self.shown = []
        self.list.clear()
        if self.isVisible() and self.can_refresh:
            self.refresh()

    def _failed(self, error):
        self.status.setText(f"Could not load people: {error}")
        self.list.setEnabled(True)

    def shutdown(self):
        self._closed = True
        self.search_timer.stop()
        self.bg.wait()
        self.contents_bg.wait()
        self.preview.shutdown()

    def _faces_selected(self) -> None:
        n = len(self.faces.selectedItems())
        g = self._current()
        self.not_btn.setEnabled(n > 0 and self.mode == "person" and g is not None and not self.busy)
        self.like_btn.setEnabled(n == 1 and not self.busy)

    def _view(self, it: dict) -> None:
        items = self.grid.items()
        v = Viewer(self, self.ctx, items, next((i for i, x in enumerate(items) if x["id"] == it["id"]), 0))
        v.resize(1200, 800)
        v.exec()

    # ------------------------------------------------------------------ actions
    def _names(self) -> list[str]:
        return sorted({g.name for g in self.groups if g.named}, key=str.lower)

    def name_group(self, name: Optional[str] = None) -> None:
        g = self._current()
        if g is None:
            return
        if name is None:
            dlg = QInputDialog(self)
            dlg.setWindowTitle("Name this person" if not g.named else "Rename")
            dlg.setLabelText("Name (type any existing name to join the two; suggestions are from this page):")
            dlg.setComboBoxItems(self._names())
            dlg.setComboBoxEditable(True)
            dlg.setTextValue(g.name or "")
            if not dlg.exec():
                return
            name = dlg.textValue()
        try:
            faces.name(self.lib, g.key, name)
        except ValueError as e:
            self.ctx.toast_requested.emit(str(e), "")
            return
        self._after_change(f"Named {fmt_n(g.photos, 'photo')} “{' '.join(name.split())}”.", name)

    def merge_into(self, other: faces.Group) -> None:
        g = self._current()
        if g is None:
            return
        faces.merge(self.lib, g.key, other.id)
        self._after_change(f"Added {fmt_n(g.photos, 'photo')} to {other.name}.", other.name)

    def hide_group(self) -> None:
        g = self._current()
        if g is None:
            return
        if g.named:
            if not confirm(self, f"Remove the name “{g.name}”?", "The faces stay, as an unnamed group.",
                           ["Photos are not changed.", "Corrections you made for this person are forgotten."],
                           "Remove name"):
                return
            faces.forget_person(self.lib, g.id)
            faces.cluster(self.lib)
            self._after_change(f"Removed the name “{g.name}”.")
        else:
            faces.hide(self.lib, g.key)
            self._after_change("Hidden. Use More ▸ Unhide hidden groups to see it again.")

    def not_this_person(self) -> None:
        ids = [it.data(Qt.ItemDataRole.UserRole) for it in self.faces.selectedItems()]
        g = self._current()
        if not ids or g is None:
            return
        faces.not_this_person(self.lib, ids)
        self._after_change(f"Removed {fmt_n(len(ids), 'face')} from {self._label(g)}.", g.name)

    def find_similar(self) -> None:
        sel = self.faces.selectedItems()
        if len(sel) != 1:
            return
        face_id = sel[0].data(Qt.ItemDataRole.UserRole)
        lib, generation, key = self.lib, self.ctx.generation, self._current().key
        self.mode = "similar"
        self._similar_rows = []
        self.back_btn.setVisible(True)
        self.g_title.setText("Look-alikes")
        self.g_info.setText("Finding look-alikes…")
        self.grid.set_items([])
        for control in (self.photo_prev, self.photo_next, self.face_prev, self.face_next):
            control.setEnabled(False)
        def work():
            try:
                return lib, generation, key, {"photos": queries.similar_page(lib, face_id)}
            finally:
                lib.close_thread()
        self.contents_bg.call(work)
        self._faces_selected()

    def _back(self) -> None:
        self._show_group(self.list.currentRow())

    def make_album(self) -> None:
        g = self._current()
        items = self.grid.items()
        if g is None or not items:
            return
        name, lib, key = g.name or "Unnamed person", self.lib, g.key
        displayed = [r["id"] for r in self._similar_rows] if self.mode == "similar" else None
        def work(progress):
            try:
                ids = displayed if displayed is not None else queries.group_ids(lib, key)
                return albums.create(lib, name, ids, "person"), len(ids)
            finally:
                lib.close_thread()
        def done(result):
            self.ctx.albums_changed.emit()
            self.ctx.toast_requested.emit(f"Saved album “{name}” with {fmt_n(result[1], 'item')}.", "")
        self.run("Saving people album", work, done)

    def _toggle_small(self) -> None:
        self.min_photos = 1 if self.small_action.isChecked() else 2
        self.refresh()

    def unhide(self) -> None:
        n = faces.unhide_all(self.lib)
        faces.cluster(self.lib)
        self.refresh()
        self.ctx.toast_requested.emit(f"{fmt_n(n, 'hidden face')} shown again." if n else "Nothing was hidden.", "")

    def _after_change(self, msg: str, select_name: Optional[str] = None) -> None:
        self._select_name = select_name
        if select_name:
            self.search.blockSignals(True)
            self.search.clear()
            self.search.blockSignals(False)
            self.group_offset = 0
        self.refresh()
        self.ctx.people_changed.emit()
        self.ctx.toast_requested.emit(msg, "")

    def forget_all(self) -> None:
        if not confirm(self, "Forget all face data?", "Every face, name and correction in this library is deleted "
                       "from Memoria's catalogue.", ["Photos are not changed.",
                                                     "Finding people again starts from scratch."],
                       "Forget face data", danger=True):
            return
        faces.forget_all(self.lib)
        self.ctx.people_changed.emit()
        self.refresh()
        self.ctx.toast_requested.emit("All face data was forgotten.", "")
