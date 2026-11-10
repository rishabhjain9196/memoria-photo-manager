"""Paged operation history and Recovery across the library's media folders."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QComboBox, QDialog, QHeaderView, QPlainTextEdit, QSplitter,
                               QTreeWidget, QTreeWidgetItem, QWidget)

from ...engine import actions, recovery
from .. import theme
from ..tasks import LatestCall
from ..widgets import Card, ConfirmDialog, MessageDialog, button, fmt_date, fmt_n, fmt_size, hbox, label, open_path, show_in_explorer, vbox
from .base import Page

BATCH_PAGE = 200
OP_PAGE = 500
KIND = {"duplicates": "Duplicates", "similar": "Similar / blurry", "tidy": "Tidy up", "organize": "Organise",
        "sync": "Compare & sync", "batch": "Photos & videos", "edit": "Editor",
        "albums": "Albums export", "story": "Story maker", "video": "Video compressor",
        "recovery_import": "Recovery restoration"}
OP = {"recycle": "Moved to Recovery", "move": "Moved", "copy": "Copied", "rmdir": "Removed empty folder",
      "create": "Created", "metadata": "Merged organisation"}
OP_STATUS = {"done": "Done", "undone": "Undone", "skipped": "Skipped", "failed": "Failed",
             "purged": "Deleted from Recovery", "pending": "Interrupted", "superseded": "Cleared by reset",
             "publishing": "Interrupted publication", "published": "Published; completion pending",
             "undo_pending": "Undo interrupted"}


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
        self._accounting = None
        self._accounting_ready = False
        self._can_undo = False
        self._restore_conflicts = None
        self.batches = QTreeWidget()
        self.batches.setHeaderLabels(["When", "What", "Recorded items", "Recorded size", "Status"])
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
        self.rec_label.setTextFormat(Qt.TextFormat.PlainText)
        self.root_note = label("", "small", wrap=True)
        self.root_note.setTextFormat(Qt.TextFormat.PlainText)
        self.recovery_root = QComboBox()
        self.recovery_root.currentIndexChanged.connect(self._show_root)
        self.inspect_rec = button("Inspect accounting", on_click=self._inspect_recovery)
        self.refresh_rec = button("Refresh accounting", on_click=self.refresh)
        self.restore_rec = button("Restore all available...", "primary", self.restore_recovery)
        self.open_rec = button("Open Recovery folder", on_click=self._open_recovery)
        self.empty_btn = button("Empty Recovery...", "danger", self.empty_recovery)
        self.empty_btn.setStyleSheet(
            f"QPushButton#danger:disabled {{ background: {theme.DISABLED_BG}; color: {theme.DISABLED_TEXT}; "
            f"border-color: {theme.BORDER}; }}")
        self.empty_btn.setEnabled(False)
        self.empty_status = label("", "small", wrap=True)
        self.body.addWidget(Card(vbox(hbox(label("Recovery — all media folders", "h2"), None,
                                          self.refresh_rec, self.restore_rec, self.empty_btn), self.empty_status, self.rec_label,
                                     hbox(label("Open / inspect location:", "small"), self.recovery_root, None,
                                          self.inspect_rec, self.open_rec), self.root_note)))
        self.body.addWidget(split, 1)
        self.bg, self.op_bg = LatestCall(self), LatestCall(self)
        self.bg.result.connect(self._show_batches)
        self.bg.failed.connect(lambda error: self.rec_label.setText(f"History could not be read: {error}"))
        self.op_bg.result.connect(self._show_ops)
        self.op_bg.failed.connect(lambda error: self.detail.setText(f"Steps could not be read: {error}"))
        ctx.runner.finished.connect(self._restore_finished)
        self.on_busy_changed(False)

    def shutdown(self):
        self._closed = True
        if self._restore_conflicts is not None:
            self._restore_conflicts.shutdown()
        self.bg.wait()
        self.op_bg.wait()

    def on_busy_changed(self, busy):
        if busy:
            self._accounting_ready = False
            self.stale = True
        self.undo_btn.setEnabled(self._can_undo and not busy)
        self._empty_control(busy)
        self.open_rec.setEnabled(not busy and self.recovery_root.count() > 0)
        self.inspect_rec.setEnabled(not busy and self._accounting_ready)
        self.refresh_rec.setEnabled(not busy)
        self.restore_rec.setEnabled(not busy and self.lib is not None and self._recovery_count > 0)

    def _empty_control(self, busy):
        self.empty_btn.setEnabled(self.lib is not None and not busy)
        if self.lib is None:
            message = "Open a library before reviewing Recovery."
        elif busy:
            message = ("Empty Recovery is unavailable while library work is active. Finish or cancel the current "
                       "task first; unfinished rebuilds must be resolved.")
        elif self._accounting_ready and self._accounting and self._accounting.needs_inspection:
            message = "Permanent deletion is blocked. Click Empty Recovery to see the specific reasons; nothing will be deleted."
        elif self._accounting_ready and self._accounting and not self._accounting.files:
            message = "No Recovery files are currently measured. Clicking Empty Recovery checks again before doing anything."
        else:
            message = "Empty Recovery first checks every location, then asks for permanent-deletion acknowledgement if safe."
        self.empty_status.setText(message)
        self.empty_btn.setToolTip(message)

    def refresh(self):
        self._batch_offset = 0
        self._load_batches()

    def _load_batches(self):
        lib, generation, offset = self.lib, self.ctx.generation, self._batch_offset
        if lib is None or self._closed:
            return
        self._accounting_ready = False
        self._empty_control(self.busy)
        self.inspect_rec.setEnabled(False)
        self.rec_label.setText("Reading Recovery accounting — previous totals are not current...")
        def work():
            try:
                accounting = recovery.inspect(lib)
                return {"generation": generation, "offset": offset,
                        "recovery": (accounting.files, accounting.bytes), "accounting": accounting, "roots": lib.roots(),
                        "count": lib.db.execute("SELECT COUNT(*) FROM batches WHERE status!='nothing'").fetchone()[0],
                        "batches": actions.batches(lib, BATCH_PAGE, offset)}
            finally:
                lib.close_thread()
        self.bg.call(work)

    def _show_batches(self, data):
        if self._closed or data["generation"] != self.ctx.generation or data["offset"] != self._batch_offset:
            return
        self._recovery_count, self._recovery_bytes = data["recovery"]
        self._accounting = report = data["accounting"]
        self._accounting_ready = True
        self._offline = sum(not root.online for root in report.roots)
        latest = report.latest
        blockers = report.empty_blockers()
        self.rec_label.setText(
            f"Cumulative Recovery across all available roots: {fmt_n(report.files, 'measured file')} "
            f"({fmt_size(report.bytes)} logical bytes). Not just the last cleanup.\n"
            + (f"Latest cleanup ({fmt_date(latest.created_at, True)}): {fmt_size(latest.moved_bytes)} recorded as moved; "
               f"{fmt_size(latest.bytes)} still in Recovery."
               + (f" Planned/recorded: {fmt_size(latest.recorded_bytes)}."
                  if latest.recorded_bytes != latest.moved_bytes else "") + "\n"
               if latest else "No recorded cleanup. Any contents below are accounted independently of the journal.\n")
            + f"Older cleanups still retained: {fmt_size(report.older_bytes)}. "
            f"Other journaled contents: {fmt_size(report.other_bytes)}. "
            f"Untracked / ambiguously matched: {fmt_n(report.untracked_files, 'file')} "
            f"({fmt_size(report.untracked_bytes)}).\n"
            + ("INCOMPLETE — totals are measured lower bounds, not empty-storage confirmation. "
               f"{self._offline} root(s) offline; unreadable items / skipped links are not included. "
               if not report.complete else "")
            + ("Inspection needed: " + " ".join(blockers[:2])
               + (" Additional reasons are available by clicking Empty Recovery." if len(blockers) > 2 else "")
               + " Permanent deletion remains blocked. " if report.needs_inspection else "")
            + (f"{report.interrupted_ops} interrupted journal step(s). " if report.interrupted_ops else "")
            + (f"{report.pending_merges} organisation merge(s) pending. " if report.pending_merges else "")
            + "Moving here frees no disk space. Logical bytes are not allocated disk space. "
            "Empty Recovery permanently deletes across ALL registered media folders.")
        self.rec_label.setToolTip(latest.title if latest else "")
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
            if batch["kind"] == "recovery_import":
                text = "Restored" if batch["status"] == "undone" else "Restoration prepared / remaining"
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

    def _show_root(self, *_):
        root = self._selected_root()
        if root is None:
            self.root_note.setText("")
            return
        self.root_note.setText(
            f"This location: {fmt_n(root.files, 'measured file')} / {fmt_size(root.bytes)} logical bytes; "
            f"untracked {fmt_n(root.untracked_files, 'file')} / {fmt_size(root.untracked_bytes)}. "
            + ("Offline / unavailable. " if not root.online else "Incomplete scan. " if not root.complete else "")
            + "Picker only changes Open / Inspect, NOT totals, Restore all or Empty Recovery scope.")

    def _selected_root(self):
        return next((root for root in self._accounting.roots
                     if root.id == self.recovery_root.currentData()), None) if self._accounting else None

    def _inspect_recovery(self):
        root = self._selected_root()
        if root is None:
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Recovery accounting — local inspection")
        text = QPlainTextEdit()
        text.setReadOnly(True)
        text.setPlainText(
            f"Location: {root.label}\n{root.path}\n\n"
            f"Measured: {root.files:,} files / {root.bytes:,} logical bytes\n"
            f"Untracked / ambiguous: {root.untracked_files:,} files / {root.untracked_bytes:,} bytes\n"
            f"Online: {root.online}; complete scan: {root.complete}\n"
            f"Skipped links / junctions: {root.skipped_links:,}; read errors: {root.errors:,}\n\n"
            f"Up to {recovery.SAMPLE_LIMIT} local inspection examples (not an exhaustive file list):\n"
            + ("\n".join(root.samples) if root.samples else "No exceptional items observed at this location.")
            + "\n\nOpen the existing Recovery folder to inspect the full contents locally. "
            "No filenames need to be uploaded. Interrupted / holding files are left untouched. "
            "Size checks cannot detect same-size content changes. Refresh after operations finish.")
        dialog.setLayout(vbox(text, hbox(None, button("Close", on_click=dialog.accept))))
        dialog.resize(780, 480)
        dialog.exec()

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
        imported = data["batch"]["kind"] == "recovery_import"
        for op in data["ops"]:
            state = ("Restored" if op["status"] == "undone" else "Awaiting restoration") \
                if imported and op["status"] in ("done", "undone") else OP_STATUS.get(op["status"], op["status"])
            item = QTreeWidgetItem([OP.get(op["op"], op["op"]), self._short(op["src"]),
                                   self._short(op["dst"]), state])
            item.setToolTip(1, op["src"] or "")
            item.setToolTip(2, op["dst"] or "")
            item.setToolTip(3, op["error"] or "")
            item.setData(0, Qt.ItemDataRole.UserRole, op)
            self.ops.addTopLevelItem(item)
        self._op_count = data["count"]
        self._can_undo = data["done"] > 0 and data["batch"]["status"] != "emptied" and not imported
        self.undo_btn.setToolTip("Use Restore all available to finish this restoration with conflict choices."
                                if imported else "")
        accounting = self._accounting.batches.get(data["batch"]["id"]) if self._accounting else None
        self.detail.setText(f"{KIND.get(data['batch']['kind'], data['batch']['kind'])} - "
                            f"{fmt_n(self._op_count, 'step')}. Undo applies to the whole change."
                            + (" Some Recovery files were permanently deleted." if data["purged"] else "")
                            + (f"\nThis change: {fmt_size(accounting.recorded_bytes)} cleanup bytes recorded; "
                               f"{fmt_n(accounting.files, 'file')} / {fmt_size(accounting.bytes)} still measured "
                               f"in Recovery. Missing: {accounting.missing_files} "
                               f"({fmt_size(accounting.missing_bytes)} recorded); size/type changed: "
                               f"{accounting.changed_files}; unknown: {accounting.uncertain_files}; "
                               f"unexpected state: {accounting.unexpected_files}."
                               if accounting else "\nNo Recovery destinations recorded for this change.")
                            + (" Recovery accounting is incomplete." if self._accounting and not self._accounting.complete
                               else ""))
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
            return recovery.inspection_path(lib, source)
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
        if self.busy or self.lib is None:
            self.ctx.toast_requested.emit("Finish the current library task or rebuild before emptying Recovery.", "")
            return
        lib = self.lib
        def done(count):
            self.ctx.library_modified.emit()
            self.ctx.toast_requested.emit(f"Recovery emptied: {fmt_n(count, 'file')} deleted.", "")
            self.ctx.notification_requested.emit("operation_complete", count)
        def inspect(progress):
            try:
                progress.update(0, 0, "Checking Recovery before permanent deletion...", force=True)
                report = recovery.inspect(lib)
                progress.check()
                return report
            finally:
                lib.close_thread()
        def review(report):
            if self._closed or self.lib is not lib:
                return
            if not report.safe_to_empty:
                blockers = report.empty_blockers()
                title = "Recovery needs attention before emptying" if blockers else "Recovery is empty"
                message = ("Nothing was deleted. Permanent deletion is blocked for the reasons below."
                           if blockers else "No Recovery files were found. Nothing was deleted.")
                self.empty_status.setText(message)
                MessageDialog(self, title, message, "\n\n".join(blockers) +
                              ("\n\nCounts can overlap. Done/Restored labels describe past operations, not a guarantee "
                               "that current Recovery contents match History. Inspect accounting shows local examples. "
                               "Restoring files is different from permanently emptying Recovery."
                               if blockers else "")).exec()
                return
            expected = (report.files, report.bytes)
            dialog = ConfirmDialog(
                self, "Permanently delete files in Recovery?",
                f"{fmt_n(report.files, 'file')} ({fmt_size(report.bytes)} logical bytes) will be deleted forever.",
                ["This deletes Recovery on all registered media folders.",
                 "Deleted Recovery files can no longer be restored. Cancelling leaves everything in place."],
                "Delete permanently", danger=True, require_ack="I understand these files cannot be recovered", note=None)
            accepted = dialog.exec() == dialog.DialogCode.Accepted and dialog.ack.isChecked()
            dialog.deleteLater()
            if not accepted:
                self.ctx.toast_requested.emit("Nothing was deleted from Recovery.", "")
                return
            def work(progress):
                try:
                    progress.check()
                    current = recovery.inspect(lib)
                    if not current.safe_to_empty or (current.files, current.bytes) != expected:
                        raise ValueError("Recovery changed or needs inspection. Nothing was deleted. "
                                         "Check accounting and review the new result before emptying.")
                    return actions.empty_recovery(lib, progress=progress)
                finally:
                    lib.close_thread()
            self.run("Emptying Recovery", work, done, notify_success=False)
        self.run("Checking Recovery for emptying", inspect, review, notify_success=False)

    def restore_recovery(self):
        if self.busy or self.lib is None:
            return
        from ..recovery_restore import ConflictController, RestoreDialog
        from ...engine import recovery_restore
        dialog = RestoreDialog(self.window(), self.ctx)
        try:
            if dialog.exec() != dialog.DialogCode.Accepted:
                return
            plan = dialog.selected_plan()
        except ValueError as error:
            MessageDialog(self, "Review Recovery destinations", str(error)).exec()
            return
        finally:
            dialog.shutdown()
            dialog.deleteLater()
        lib = self.lib
        controller = ConflictController(self.window())
        self._restore_conflicts = controller
        def work(progress):
            try:
                return recovery_restore.execute(lib, plan, progress,
                                                lambda conflict: controller.resolve(conflict, progress))
            finally:
                lib.close_thread()
        def done(result):
            controller.shutdown()
            controller.deleteLater()
            self._restore_conflicts = None
            self.ctx.library_modified.emit()
            message = (f"Restored {fmt_n(result.restored, 'file')} ({fmt_size(result.bytes)}). "
                       f"{result.skipped} skipped; {result.failed} failed. Remaining files were not emptied.")
            if result.cancelled:
                message = "Restoration stopped. " + message
            self.ctx.toast_requested.emit(message, "")
            self.ctx.notification_requested.emit("operation_partial" if result.skipped or result.failed else
                                                 "task_cancelled" if result.cancelled else "operation_complete",
                                                 result.skipped + result.failed if result.skipped or result.failed
                                                 else 0 if result.cancelled else result.restored)
            if result.skipped or result.failed or result.messages:
                MessageDialog(self, "Recovery restoration results", message,
                              "\n".join(result.messages[:200])).exec()
        if not self.run("Restoring Recovery", work, done, notify_success=False):
            controller.shutdown()
            controller.deleteLater()
            self._restore_conflicts = None

    def _restore_finished(self, outcome):
        if outcome != "ok" and self._restore_conflicts is not None:
            self._restore_conflicts.shutdown()
            self._restore_conflicts.deleteLater()
            self._restore_conflicts = None
            self.ctx.library_modified.emit()
