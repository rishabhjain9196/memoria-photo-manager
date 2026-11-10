"""Paged operation history and Recovery across the library's media folders."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QComboBox, QHeaderView, QSplitter, QTreeWidget, QTreeWidgetItem, QWidget

from ...engine import actions, config, roots
from .. import theme
from ..tasks import LatestCall
from ..widgets import Card, ConfirmDialog, button, fmt_date, fmt_n, fmt_size, hbox, label, open_path, show_in_explorer, vbox
from .base import Page

BATCH_PAGE = 200
OP_PAGE = 500
KIND = {"duplicates": "Duplicates", "similar": "Similar / blurry", "tidy": "Tidy up", "organize": "Organise",
        "sync": "Compare & sync", "batch": "Photos & videos", "edit": "Editor",
        "albums": "Albums export", "story": "Story maker", "video": "Video compressor"}
OP = {"recycle": "Moved to Recovery", "move": "Moved", "copy": "Copied", "rmdir": "Removed empty folder",
      "create": "Created", "metadata": "Merged organisation"}
OP_STATUS = {"done": "Done", "undone": "Undone", "skipped": "Skipped", "failed": "Failed",
             "purged": "Deleted from Recovery", "pending": "Interrupted", "superseded": "Cleared by reset"}


def status_label(status):
    return {"applied": ("Done", theme.OK), "partial": ("Partly done", theme.WARN),
            "undone": ("Undone", theme.MUTED), "emptied": ("Done - Recovery emptied", theme.MUTED),
            "applying": ("In progress", theme.WARN)}.get(status, (status, theme.TEXT))


class HistoryPage(Page):
    title = "History & recovery"
    subtitle = "Review recorded changes. Undo applies to the whole selected change, not just its displayed steps."

    def __init__(self, ctx):
        super().__init__(ctx)
        self._closed = False
        self._batch_offset = self._op_offset = self._batch_count = self._op_count = 0
        self._recovery_count = self._recovery_bytes = self._offline = 0
        self._can_undo = False
        self.batches = QTreeWidget()
        self.batches.setHeaderLabels(["When", "What", "Files", "Size", "Status"])
        self.batches.setRootIsDecorated(False)
        self.batches.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.batches.currentItemChanged.connect(self._select)
        self.ops = QTreeWidget()
        self.ops.setHeaderLabels(["Action", "File", "Now at", "Status"])
        self.ops.setRootIsDecorated(False)
        for column in (1, 2):
            self.ops.header().setSectionResizeMode(column, QHeaderView.ResizeMode.Stretch)
        self.ops.itemDoubleClicked.connect(self._reveal)
        self.undo_btn = button("Undo this change", "primary", self.undo)
        self.undo_btn.setEnabled(False)
        self.detail = label("", "muted", wrap=True)
        self.batch_note, self.op_note = label("", "small"), label("", "small")
        self.batch_prev = button("Previous changes", on_click=lambda: self._turn_batches(-1))
        self.batch_next = button("Next changes", on_click=lambda: self._turn_batches(1))
        self.op_prev = button("Previous steps", on_click=lambda: self._turn_ops(-1))
        self.op_next = button("Next steps", on_click=lambda: self._turn_ops(1))
        top, bottom = QWidget(), QWidget()
        top.setLayout(vbox(self.batches, hbox(self.batch_prev, self.batch_note, None, self.batch_next)))
        bottom.setLayout(vbox(hbox(self.detail, None, self.undo_btn), self.ops,
                              hbox(self.op_prev, self.op_note, None, self.op_next)))
        split = QSplitter(Qt.Orientation.Vertical)
        split.addWidget(top)
        split.addWidget(bottom)
        self.rec_label = label("Reading available Recovery...", "", wrap=True)
        self.recovery_root = QComboBox()
        self.open_rec = button("Open Recovery folder", on_click=self._open_recovery)
        self.empty_btn = button("Empty Recovery...", "danger", self.empty_recovery)
        self.empty_btn.setEnabled(False)
        self.body.addWidget(Card(vbox(hbox(label("Recovery", "h2"), self.recovery_root, None,
                                          self.open_rec, self.empty_btn), self.rec_label)))
        self.body.addWidget(split, 1)
        self.bg, self.op_bg = LatestCall(self), LatestCall(self)
        self.bg.result.connect(self._show_batches)
        self.bg.failed.connect(lambda error: self.rec_label.setText(f"History could not be read: {error}"))
        self.op_bg.result.connect(self._show_ops)
        self.op_bg.failed.connect(lambda error: self.detail.setText(f"Steps could not be read: {error}"))
        self.on_busy_changed(False)

    def shutdown(self):
        self._closed = True
        self.bg.wait()
        self.op_bg.wait()

    def on_busy_changed(self, busy):
        self.undo_btn.setEnabled(self._can_undo and not busy)
        self.empty_btn.setEnabled(self._recovery_count > 0 and not self._offline and not busy)
        self.open_rec.setEnabled(not busy and self.recovery_root.count() > 0)

    def refresh(self):
        self._batch_offset = 0
        self._load_batches()

    def _load_batches(self):
        lib, generation, offset = self.lib, self.ctx.generation, self._batch_offset
        if lib is None or self._closed:
            return
        self.empty_btn.setEnabled(False)
        def work():
            try:
                recovery = actions.recovery_size(lib)
                return {"generation": generation, "offset": offset, "recovery": recovery, "roots": lib.roots(),
                        "count": lib.db.execute("SELECT COUNT(*) FROM batches WHERE status!='nothing'").fetchone()[0],
                        "batches": actions.batches(lib, BATCH_PAGE, offset)}
            finally:
                lib.close_thread()
        self.bg.call(work)

    def _show_batches(self, data):
        if self._closed or data["generation"] != self.ctx.generation or data["offset"] != self._batch_offset:
            return
        self._recovery_count, self._recovery_bytes = data["recovery"]
        self._offline = sum(not root["online"] for root in data["roots"])
        self.rec_label.setText(
            f"Available Recovery: {fmt_n(self._recovery_count, 'file')} ({fmt_size(self._recovery_bytes)}). "
            "Moving here does not free disk space. Empty Recovery permanently deletes these files."
            + (f" {self._offline} folder(s) offline; their Recovery is not included. Reconnect before emptying."
               if self._offline else ""))
        selected_root = self.recovery_root.currentData()
        self.recovery_root.clear()
        for root in data["roots"]:
            self.recovery_root.addItem(root["label"] + ("" if root["online"] else " (offline)"), root["id"])
        self.recovery_root.setCurrentIndex(max(0, self.recovery_root.findData(selected_root)))
        current = self.batches.currentItem()
        selected = current.data(0, Qt.ItemDataRole.UserRole)["id"] if current else None
        newest = data["batches"][0]["id"] if data["batches"] else None
        if self._batch_offset == 0 and newest != getattr(self, "_newest_id", None):
            selected = newest
            self._newest_id = newest
        self.batches.blockSignals(True)
        self.batches.clear()
        selected_item = None
        for batch in data["batches"]:
            text, color = status_label(batch["status"])
            item = QTreeWidgetItem([fmt_date(batch["created_at"], True), batch["title"],
                                   str(batch["files"]), fmt_size(batch["bytes"]), text])
            item.setForeground(4, QColor(color))
            item.setData(0, Qt.ItemDataRole.UserRole, batch)
            self.batches.addTopLevelItem(item)
            if selected_item is None or batch["id"] == selected:
                selected_item = item
        self.batches.setCurrentItem(selected_item)
        self.batches.blockSignals(False)
        self._batch_count = data["count"]
        self.batch_note.setText(f"{len(data['batches'])} shown of {self._batch_count:,} changes")
        self.batch_prev.setEnabled(self._batch_offset > 0)
        self.batch_next.setEnabled(self._batch_offset + BATCH_PAGE < self._batch_count)
        self._op_offset = 0
        self._select(selected_item, None)
        self.on_busy_changed(self.busy)

    def _select(self, current, previous):
        self._can_undo = False
        self.undo_btn.setEnabled(False)
        if current is None or self.lib is None:
            self.ops.clear()
            self.detail.setText("No changes yet.")
            return
        if current is not previous:
            self._op_offset = 0
        self._load_ops()

    def _load_ops(self):
        current = self.batches.currentItem()
        if current is None or self._closed:
            return
        batch = current.data(0, Qt.ItemDataRole.UserRole)
        lib, generation, offset = self.lib, self.ctx.generation, self._op_offset
        self.detail.setText("Reading change steps...")
        def work():
            try:
                count, done, purged = lib.db.execute(
                    "SELECT COUNT(*),SUM(status='done'),SUM(status='purged') FROM operations WHERE batch_id=?",
                    (batch["id"],)).fetchone()
                return {"generation": generation, "batch": batch, "offset": offset, "count": count,
                        "done": done or 0, "purged": purged or 0,
                        "ops": actions.operations(lib, batch["id"], OP_PAGE, offset)}
            finally:
                lib.close_thread()
        self.op_bg.call(work)

    def _show_ops(self, data):
        current = self.batches.currentItem()
        if self._closed or data["generation"] != self.ctx.generation or current is None or (
                current.data(0, Qt.ItemDataRole.UserRole)["id"] != data["batch"]["id"]) or data["offset"] != self._op_offset:
            return
        self.ops.clear()
        for op in data["ops"]:
            item = QTreeWidgetItem([OP.get(op["op"], op["op"]), self._short(op["src"]),
                                   self._short(op["dst"]), OP_STATUS.get(op["status"], op["status"])])
            item.setToolTip(1, op["src"] or "")
            item.setToolTip(2, op["dst"] or "")
            item.setToolTip(3, op["error"] or "")
            item.setData(0, Qt.ItemDataRole.UserRole, op)
            self.ops.addTopLevelItem(item)
        self._op_count = data["count"]
        self._can_undo = data["done"] > 0 and data["batch"]["status"] != "emptied"
        self.detail.setText(f"{KIND.get(data['batch']['kind'], data['batch']['kind'])} - "
                            f"{fmt_n(self._op_count, 'step')}. Undo applies to the whole change."
                            + (" Some Recovery files were permanently deleted." if data["purged"] else ""))
        self.op_note.setText(f"Steps {self._op_offset + 1 if self._op_count else 0}-"
                            f"{self._op_offset + len(data['ops'])} of {self._op_count:,}")
        self.op_prev.setEnabled(self._op_offset > 0)
        self.op_next.setEnabled(self._op_offset + OP_PAGE < self._op_count)
        self.on_busy_changed(self.busy)

    def _turn_batches(self, direction):
        self._batch_offset = max(0, self._batch_offset + direction * BATCH_PAGE)
        self._load_batches()

    def _turn_ops(self, direction):
        self._op_offset = max(0, self._op_offset + direction * OP_PAGE)
        self._load_ops()

    def _short(self, path):
        if not path:
            return ""
        p = Path(path)
        for source, folder in self.lib.recovery_folders():
            if folder in p.parents:
                relative = p.relative_to(folder)
                return f"Recovery (folder {source}) - " + str(Path(*relative.parts[1:]))
        try:
            return self.lib.display_path(self.lib.rel(p, resolve=False))
        except ValueError:
            return str(p)

    def _reveal(self, item, _column):
        op = item.data(0, Qt.ItemDataRole.UserRole)
        for path in (op["dst"], op["src"]):
            if path and Path(path).exists():
                show_in_explorer(path)
                return

    def _open_recovery(self):
        source, lib = self.recovery_root.currentData(), self.lib
        if source is None or self.busy:
            return
        def work(progress):
            progress.check()
            roots.check(lib, source)
            folder = config.recovery_dir(lib.abspath(roots.key_for(source)))
            folder.mkdir(parents=True, exist_ok=True)
            return folder
        self.run("Opening Recovery folder", work, open_path, notify_success=False)

    def undo(self):
        current = self.batches.currentItem()
        if current is None or not self._can_undo:
            return
        batch = current.data(0, Qt.ItemDataRole.UserRole)
        dialog = ConfirmDialog(self, "Undo this change?", f"{batch['title']} will be reversed.",
                               ["This applies to the whole change, including steps on other pages.",
                                "Reconnect affected media folders first. Changed generated copies are left alone."], "Undo")
        if dialog.exec():
            self.window().undo_batch(batch["id"])

    def empty_recovery(self):
        if self.busy or self._offline or not self._recovery_count:
            return
        dialog = ConfirmDialog(
            self, "Permanently delete files in Recovery?",
            f"{fmt_n(self._recovery_count, 'file')} ({fmt_size(self._recovery_bytes)}) will be deleted forever.",
            ["This deletes Recovery on all registered media folders.",
             "Reconnect every folder first. Deleted Recovery files can no longer be restored."],
            "Delete permanently", danger=True, require_ack="I understand these files cannot be recovered", note=None)
        if not dialog.exec():
            return
        lib = self.lib
        def done(count):
            self.ctx.library_modified.emit()
            self.ctx.toast_requested.emit(f"Recovery emptied: {fmt_n(count, 'file')} deleted.", "")
            self.ctx.notification_requested.emit("operation_complete", count)
        self.run("Emptying Recovery", lambda progress: actions.empty_recovery(lib, progress=progress),
                 done, notify_success=False)
