"""Paged operation history and Recovery across the library's media folders."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QComboBox, QDialog, QHeaderView, QPlainTextEdit, QSplitter,
                               QTreeWidget, QTreeWidgetItem, QWidget)

from ..motion import Dialog
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
        "recovery_import": "Recovery restoration", "health": "Health check fixes"}
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
    subtitle = "Undo past changes, bring back removed files, or empty Recovery to free up space."

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
        self.batches.setHeaderLabels(["When", "What", "Files", "Size", "Status"])
        self.batches.setRootIsDecorated(False)
        self.batches.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.batches.currentItemChanged.connect(self._select)
        self.ops = QTreeWidget()
        self.ops.setHeaderLabels(["Action", "File", "Now in", "Status"])
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
        bottom_head = hbox(self.detail, self.undo_btn)
        bottom_head.setStretch(0, 1)
        bottom.setLayout(vbox(bottom_head, self.ops,
                              hbox(self.op_prev, self.op_note, None, self.op_next)))
        split = QSplitter(Qt.Orientation.Vertical)
        split.addWidget(top)
        split.addWidget(bottom)
        self.rec_total = label("…", "tileValue")
        self.rec_label = label("Checking Recovery…", "muted", wrap=True)
        self.rec_label.setTextFormat(Qt.TextFormat.PlainText)
        self.rec_notice = label("", "", wrap=True)
        self.rec_notice.setTextFormat(Qt.TextFormat.PlainText)
        self.rec_notice.setStyleSheet(f"color: {theme.WARN};")
        self.rec_notice.hide()
        self.restore_rec = button("Restore all…", "primary", self.restore_recovery,
                                  tip="Put removed files back where they came from.")
        self.empty_btn = button("Empty Recovery…", "danger", self.empty_recovery)
        self.empty_btn.setStyleSheet(
            f"QPushButton#danger:disabled {{ background: {theme.DISABLED_BG}; color: {theme.DISABLED_TEXT}; "
            f"border-color: {theme.BORDER}; }}")
        self.empty_btn.setEnabled(False)
        self.open_rec = button("Open folder", "link", self._open_recovery)
        self.details_rec = button("Details", "link", self._recovery_details)
        self.empty_status = label("", "small", wrap=True)
        self.body.addWidget(Card(vbox(
            hbox(vbox(label("Recovery", "h2"), self.rec_total, spacing=2), None, self.restore_rec, self.empty_btn),
            self.rec_label, self.rec_notice,
            hbox(self.empty_status, None, self.open_rec, self.details_rec))))
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
        self.open_rec.setEnabled(not busy and self.lib is not None)
        self.details_rec.setEnabled(not busy and self._accounting_ready)
        self.restore_rec.setEnabled(not busy and self.lib is not None and self._recovery_count > 0)

    def _empty_control(self, busy):
        report = self._accounting if self._accounting_ready else None
        # Nothing to empty is a quiet, disabled state; unknown or blocked states stay clickable to explain.
        nothing = report is not None and not report.files and not report.blockers()
        self.empty_btn.setEnabled(self.lib is not None and not busy and not nothing)
        if self.lib is None:
            message = "Open a library first."
        elif busy:
            message = "Available when the current task finishes."
        else:
            message = ""
        self.empty_status.setText(message)
        self.empty_btn.setToolTip(message or ("Recovery is empty." if nothing else
                                              "Permanently delete everything in Recovery to free up space."))

    def refresh(self):
        self._batch_offset = 0
        self._load_batches()

    def _load_batches(self):
        lib, generation, offset = self.lib, self.ctx.generation, self._batch_offset
        if lib is None or self._closed:
            return
        self._accounting_ready = False
        self._empty_control(self.busy)
        self.details_rec.setEnabled(False)
        self.rec_label.setText("Checking Recovery…")
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
        self._roots = data["roots"]
        self._offline = sum(not root.online for root in report.roots)
        self.rec_total.setText(f"{fmt_n(report.files, 'file')} · {fmt_size(report.bytes)}"
                               if report.files else "Empty")
        self.rec_label.setText("Files you remove wait here until you restore them or empty Recovery."
                               if report.files else "Files you remove with Memoria will wait here, ready to restore.")
        notices = list(report.blockers())
        if report.review_files and not notices:
            notices.append(f"{fmt_n(report.review_files, 'file')} here didn't come from a Memoria cleanup. "
                           "You'll be asked before it's deleted.")
        self.rec_notice.setText("\n".join(notices))
        self.rec_notice.setVisible(bool(notices))
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

    def _recovery_details(self):
        report = self._accounting
        if report is None:
            return
        dialog = Dialog(self)
        dialog.setWindowTitle("Recovery details")
        text = QPlainTextEdit()
        text.setReadOnly(True)
        where = QComboBox()
        for root in report.roots:
            where.addItem(root.label + ("" if root.online else " (disconnected)"), root.id)
        latest = report.latest

        def show(*_):
            root = next((r for r in report.roots if r.id == where.currentData()), None)
            lines = [f"All media folders: {fmt_n(report.files, 'file')} · {fmt_size(report.bytes)}"]
            if latest:
                lines.append(f"Latest cleanup ({fmt_date(latest.created_at, True)}): {fmt_size(latest.bytes)}")
                lines.append(f"Earlier cleanups: {fmt_size(report.older_bytes)}")
            if report.other_bytes:
                lines.append(f"Other changes: {fmt_size(report.other_bytes)}")
            if report.review_files:
                lines.append(f"Didn't come from a Memoria cleanup: {fmt_n(report.review_files, 'file')} "
                             f"· {fmt_size(report.review_bytes)}")
            if report.legacy_metadata_files:
                lines.append(f"Old Memoria session files: {report.legacy_metadata_files:,}")
            if report.missing_files:
                lines.append(f"Already gone from Recovery: {fmt_n(report.missing_files, 'file')}")
            lines += [f"• {reason}" for reason in report.blockers()]
            if root is not None:
                lines += ["", f"{root.label}: {root.path}",
                          "Disconnected." if not root.online else
                          f"{fmt_n(root.files, 'file')} · {fmt_size(root.bytes)}"
                          + (f" · {root.skipped_links:,} shortcut(s) skipped" if root.skipped_links else "")
                          + (f" · {root.errors:,} item(s) couldn't be read" if root.errors else "")]
                if root.samples:
                    lines += ["", "Worth a look:"] + root.samples
            text.setPlainText("\n".join(lines))

        def open_folder():
            dialog.accept()
            self._open_recovery(where.currentData())
        where.currentIndexChanged.connect(show)
        show()
        dialog.setLayout(vbox(hbox(label("Location:"), where, None), text,
                              hbox(button("Open this folder", on_click=open_folder), None,
                                   button("Close", "primary", dialog.accept)), margins=(18, 18, 18, 18)))
        dialog.resize(780, 480)
        dialog.exec()

    def _select(self, current, previous):
        self._can_undo = False
        self.undo_btn.setEnabled(False)
        if current is None or self.lib is None:
            self.ops.clear()
            self.detail.setText("No changes yet.")
            self.op_note.setText("")
            self.op_prev.setEnabled(False)
            self.op_next.setEnabled(False)
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
        self.undo_btn.setToolTip("Use Restore all to finish this restore." if imported else "")
        accounting = self._accounting.batches.get(data["batch"]["id"]) if self._accounting else None
        parts = [KIND.get(data['batch']['kind'], data['batch']['kind']), fmt_n(self._op_count, 'step')]
        if accounting and accounting.files:
            parts.append(f"{fmt_n(accounting.files, 'file')} ({fmt_size(accounting.bytes)}) still in Recovery")
        if accounting and accounting.missing_files:
            parts.append(f"{fmt_n(accounting.missing_files, 'file')} already gone from Recovery")
        if data["purged"]:
            parts.append("Recovery for this change was emptied")
        self.detail.setText(" · ".join(parts))
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
                return "Recovery › " + str(Path(*relative.parts[1:]))
        try:
            return self.lib.display_path(self.lib.rel(p, resolve=False))
        except ValueError:
            # Outside the library (e.g. an export folder): the end of the path is what identifies it;
            # the full path stays in the tooltip.
            return f"…\\{p.parent.name}\\{p.name}" if p.parent.name else str(p)

    def _reveal(self, item, _column):
        op = item.data(0, Qt.ItemDataRole.UserRole)
        for path in (op["dst"], op["src"]):
            if path and Path(path).exists():
                show_in_explorer(path)
                return

    def _open_recovery(self, source=None):
        lib = self.lib
        if lib is None or self.busy:
            return
        if source is None:
            # The library's own Recovery first, then any connected folder that has one.
            sources = [root.id for root in self._accounting.roots if root.online and root.files] \
                if self._accounting else []
            source = 1 if not sources or 1 in sources else sources[0]
        def work(progress):
            progress.check()
            try:
                return recovery.inspection_path(lib, source)
            except ValueError as error:
                return str(error)
        def opened(path):
            if isinstance(path, str):
                self.ctx.toast_requested.emit("Recovery is empty — there's no folder to open yet."
                                              if "No Recovery folder" in path else path, "")
            else:
                open_path(path)
        self.run("Opening Recovery folder", work, opened, notify_success=False)

    def undo(self):
        current = self.batches.currentItem()
        if current is None or not self._can_undo:
            return
        batch = current.data(0, Qt.ItemDataRole.UserRole)
        dialog = ConfirmDialog(self, "Undo this change?", f"“{batch['title']}” will be reversed.",
                               ["Everything in this change is undone together.",
                                "Copies you've changed since are left as they are."], "Undo")
        if dialog.exec():
            self.window().undo_batch(batch["id"])

    def empty_recovery(self):
        if self.busy or self.lib is None:
            self.ctx.toast_requested.emit("Empty Recovery is available when the current task finishes.", "")
            return
        lib = self.lib
        def done(result):
            count, size = result
            self.ctx.library_modified.emit()
            self.ctx.toast_requested.emit(f"Recovery emptied — {fmt_size(size)} freed.", "")
            self.ctx.notification_requested.emit("operation_complete", count)
        def prepare(progress):
            try:
                progress.update(0, 0, "Getting Recovery ready…", force=True)
                report = recovery.prepare_to_empty(lib)
                progress.check()
                return report
            finally:
                lib.close_thread()
        def review(report):
            if self._closed or self.lib is not lib:
                return
            self.ctx.library_modified.emit()
            if not report.files and not report.blockers():
                self.ctx.toast_requested.emit("Recovery is already empty.", "")
                return
            if not report.can_empty:
                MessageDialog(self, "Can't empty Recovery yet",
                              "\n\n".join(report.blockers()) + "\n\nNothing was deleted.").exec()
                return
            expected = (report.files, report.bytes, report.review_files)
            details = []
            if report.review_files:
                details.append(f"<b>{fmt_n(report.review_files, 'file')} ({fmt_size(report.review_bytes)}) didn't "
                               "come from a Memoria cleanup.</b> To keep anything, cancel and use Restore all.")
            if sum(root.online for root in report.roots) > 1:
                details.append("Includes Recovery on all your media folders.")
            dialog = ConfirmDialog(
                self, "Empty Recovery?",
                f"{fmt_n(report.files, 'file')} ({fmt_size(report.bytes)}) will be deleted forever "
                "to free up space.",
                details, "Delete forever", danger=True, require_ack="I understand this can't be undone", note=None)
            accepted = dialog.exec() == dialog.DialogCode.Accepted and dialog.ack.isChecked()
            dialog.deleteLater()
            if not accepted:
                self.ctx.toast_requested.emit("Nothing was deleted.", "")
                return
            def work(progress):
                try:
                    progress.check()
                    current = recovery.inspect(lib)
                    if not current.can_empty or (current.files, current.bytes, current.review_files) != expected:
                        raise ValueError("Recovery changed while you were deciding, so nothing was deleted. "
                                         "Click Empty Recovery again to see the latest.")
                    return actions.empty_recovery(lib, progress=progress), current.bytes
                finally:
                    lib.close_thread()
            self.run("Emptying Recovery", work, done, notify_success=False)
        self.run("Getting Recovery ready", prepare, review, notify_success=False)

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
            MessageDialog(self, "Can't restore yet", str(error)).exec()
            return
        finally:
            dialog.shutdown()
            dialog.deleteLater()
        lib = self.lib
        controller = ConflictController(self.window())
        self._restore_conflicts = controller
        def work(progress):
            try:
                result = recovery_restore.execute(lib, plan, progress,
                                                  lambda conflict: controller.resolve(conflict, progress))
                try:
                    recovery.tidy(lib)
                except Exception:
                    pass  # Self-cleaning is best effort.
                return result
            finally:
                lib.close_thread()
        def done(result):
            controller.shutdown()
            controller.deleteLater()
            self._restore_conflicts = None
            self.ctx.library_modified.emit()
            message = f"Restored {fmt_n(result.restored, 'file')} ({fmt_size(result.bytes)})."
            if result.skipped:
                message += f" {fmt_n(result.skipped, 'file')} left in Recovery."
            if result.failed:
                message += f" {fmt_n(result.failed, 'file')} couldn't be restored."
            if result.cancelled:
                message = "Restoring stopped. " + message
            self.ctx.toast_requested.emit(message, "")
            self.ctx.notification_requested.emit("operation_partial" if result.skipped or result.failed else
                                                 "task_cancelled" if result.cancelled else "operation_complete",
                                                 result.skipped + result.failed if result.skipped or result.failed
                                                 else 0 if result.cancelled else result.restored)
            if result.failed:
                MessageDialog(self, "Some files couldn't be restored",
                              message + " They're still safe in Recovery.",
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
