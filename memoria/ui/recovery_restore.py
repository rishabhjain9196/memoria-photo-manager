"""Review Recovery destinations and resolve conflicts without overwriting existing files."""
from __future__ import annotations

import os
import threading
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QThread, QTimer, Qt, Signal
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialog, QFileDialog, QHeaderView, QPlainTextEdit,
                               QTreeWidget, QTreeWidgetItem)

from .tasks import LatestCall
from .widgets import button, fmt_n, fmt_size, hbox, label, vbox

if TYPE_CHECKING:
    from ..engine.progress import Progress
    from ..engine.recovery_restore import RestoreConflict, RestorePlan

PAGE_SIZE = 200


class RestoreDialog(QDialog):
    def __init__(self, parent, ctx):
        super().__init__(parent)
        self.ctx, self.lib = ctx, ctx.library
        self.plan: RestorePlan | None = None
        self._closed = False
        self._loading = True
        self._valid = False
        self.offset = 0
        self.setWindowTitle("Restore Recovery to original folders")
        self.resize(1040, 660)
        self.summary = label("Reading Recovery...", "h2", wrap=True)
        self.status = label("", "small", wrap=True)
        self.include_unlogged = QCheckBox("Include files missing from History")
        self.include_unlogged.setChecked(True)
        self.include_unlogged.toggled.connect(self._selection_changed)
        self.ack = QCheckBox("I reviewed the inferred / chosen destinations for files without original logs.")
        self.ack.toggled.connect(self._update)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Recovery file", "Restore destination", "Size", "Origin", "Review"])
        self.tree.setRootIsDecorated(False)
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tree.currentItemChanged.connect(lambda *_: self._update())
        self.previous = button("Previous", on_click=lambda: self._turn(-1))
        self.next = button("Next", on_click=lambda: self._turn(1))
        self.page_note = label("", "small")
        self.map_btn = button("Choose destination for this group...", on_click=self._map)
        self.refresh_btn = button("Refresh preview", on_click=self.refresh)
        self.go_btn = button("Restore available files", "primary", self.accept)
        self.cancel_btn = button("Cancel", on_click=self.reject)
        self.setLayout(vbox(
            self.summary,
            label("Logged locations are preferred. Unlogged locations are inferred only from supported Recovery "
                  "layout, or chosen explicitly below. Ambiguous, offline or unreadable items stay in Recovery. "
                  "Review this preview before restoring; it does not move files.",
                  "muted", wrap=True),
            self.include_unlogged, self.tree,
            hbox(self.previous, self.page_note, None, self.next),
            hbox(self.map_btn, None, self.refresh_btn), self.ack, self.status,
            label("Existing files are never overwritten. Each conflict offers Keep both, Leave in Recovery, or Cancel, "
                  "with an option to reuse the choice for that folder or all remaining conflicts.",
                  "small", wrap=True),
            hbox(None, self.cancel_btn, self.go_btn), margins=(18, 18, 18, 18)))
        self.bg = LatestCall(self)
        self.bg.result.connect(self._loaded)
        self.bg.failed.connect(self._failed)
        self.refresh()

    def _selected_items(self):
        if self.plan is None:
            return []
        return [item for item in self.plan.items
                if self.include_unlogged.isChecked() or item.provenance == "history"]

    def selected_plan(self):
        if self.plan is None or not self._valid or self._loading:
            raise ValueError("The restoration preview is not ready.")
        if any(item.target is not None and not item.issue and item.provenance != "history"
               for item in self._selected_items()) and not self.ack.isChecked():
            raise ValueError("Acknowledge the reviewed inferred destinations before restoring.")
        return replace(self.plan, items=self._selected_items())

    def accept(self):
        if self.go_btn.isEnabled():
            super().accept()

    def refresh(self):
        from ..engine import recovery_restore
        lib, generation = self.lib, self.ctx.generation
        self._loading, self._valid = True, False
        self.ack.setChecked(False)
        self.status.setText("Reading file metadata and History; no originals are being changed.")
        self._update()
        def work():
            try:
                return generation, recovery_restore.preview(lib)
            finally:
                lib.close_thread()
        self.bg.call(work)

    def _loaded(self, result):
        generation, plan = result
        if self._closed:
            return
        if generation != self.ctx.generation:
            self._failed(ValueError("The library changed. Refresh this preview before restoring."))
            return
        self.plan = plan
        self._loading, self._valid = False, True
        self.offset = 0
        notes = []
        if plan.offline_roots:
            notes.append(f"{len(plan.offline_roots)} folder(s) are offline and not included.")
        if plan.errors:
            notes.extend(plan.errors[:5])
            if len(plan.errors) > 5:
                notes.append(f"{len(plan.errors) - 5} additional inspection warnings.")
        self.status.setText("\n".join(notes))
        self._render()
        self._update()

    def _failed(self, error):
        if not self._closed:
            self._loading, self._valid = False, False
            self.status.setText(f"Restoration preview could not finish: {error}")
            self._update()

    def _selection_changed(self):
        self.offset = 0
        self.ack.setChecked(False)
        self._render()
        self._update()

    def _render(self):
        items = self._selected_items()
        self.tree.clear()
        for item in items[self.offset:self.offset + PAGE_SIZE]:
            row = QTreeWidgetItem([str(item.source), str(item.target) if item.target is not None else "Choose destination",
                                   fmt_size(item.size), item.provenance, item.issue or "Eligible for review"])
            row.setData(0, Qt.ItemDataRole.UserRole, item)
            row.setToolTip(0, str(item.source))
            row.setToolTip(1, str(item.target) if item.target is not None else item.issue)
            row.setToolTip(4, item.issue)
            self.tree.addTopLevelItem(row)
        self.page_note.setText(f"Showing {self.offset + 1 if items else 0}-"
                               f"{min(self.offset + PAGE_SIZE, len(items))} of {len(items):,}. "
                               "Restoration includes eligible items on all pages.")
        self.previous.setEnabled(self.offset > 0 and not self._loading)
        self.next.setEnabled(self.offset + PAGE_SIZE < len(items) and not self._loading)

    def _turn(self, direction):
        self.offset = max(0, self.offset + direction * PAGE_SIZE)
        self._render()

    def _update(self, *_):
        items = self._selected_items()
        eligible = [item for item in items if item.target is not None and not item.issue]
        inferred = sum(item.provenance != "history" for item in eligible)
        self.summary.setText(
            f"{fmt_n(len(eligible), 'file')} ({fmt_size(sum(item.size for item in eligible))}) eligible to restore"
            + (f"; {len(items) - len(eligible)} need attention" if len(eligible) != len(items) else ""))
        self.ack.setVisible(inferred > 0)
        self.go_btn.setEnabled(self._valid and not self._loading and bool(eligible)
                               and (not inferred or self.ack.isChecked()))
        current = self.tree.currentItem()
        item = current.data(0, Qt.ItemDataRole.UserRole) if current else None
        self.map_btn.setEnabled(not self._loading and item is not None and bool(item.mapping_group)
                                and item.provenance != "history")
        self.refresh_btn.setEnabled(not self._loading)
        self.include_unlogged.setEnabled(not self._loading)

    def _map(self):
        from ..engine import recovery_restore
        current = self.tree.currentItem()
        if current is None or self.plan is None:
            return
        item = current.data(0, Qt.ItemDataRole.UserRole)
        folder = QFileDialog.getExistingDirectory(self, "Choose the destination for this Recovery group's contents",
                                                    str(self.lib.root))
        if not folder:
            return
        plan, lib, generation, group = self.plan, self.lib, self.ctx.generation, item.mapping_group
        self._loading, self._valid = True, False
        self.ack.setChecked(False)
        self._update()
        def work():
            try:
                return generation, recovery_restore.map_destination(lib, plan, group, folder)
            finally:
                lib.close_thread()
        self.bg.call(work)

    def shutdown(self):
        self._closed = True
        self.bg.wait()


class ConflictDialog(QDialog):
    def __init__(self, parent, conflict):
        super().__init__(parent)
        self.decision = "cancel"
        self.setWindowTitle("Recovery restore conflict")
        self.resize(760, 440)
        details = QPlainTextEdit()
        details.setReadOnly(True)
        details.setPlainText("Recovery sources:\n" + "\n".join(conflict.sources) +
                             "\n\nRestore destinations:\n" + "\n".join(conflict.targets))
        self.scope = QComboBox()
        for text, value in (("This conflict only", "one"), ("This folder's remaining conflicts", "folder"),
                            ("All remaining conflicts", "all")):
            self.scope.addItem(text, value)
        self.keep_btn = button("Keep both", "primary", lambda: self._choose("rename"))
        self.skip_btn = button("Leave in Recovery", on_click=lambda: self._choose("skip"))
        self.cancel_btn = button("Cancel restoration", on_click=self.reject)
        self.setLayout(vbox(
            label("A file already exists at the restore destination", "h2", wrap=True),
            label("Keep both restores a numbered copy without overwriting the existing file. Linked components "
                  "keep a common name. Leave in Recovery skips this item/linked group.", "muted", wrap=True),
            details, hbox(label("Use this choice for:"), self.scope),
            hbox(self.cancel_btn, None, self.skip_btn, self.keep_btn),
            margins=(18, 18, 18, 18)))

    def _choose(self, decision):
        self.decision = decision
        self.accept()


@dataclass
class _ConflictRequest:
    conflict: RestoreConflict
    progress: Progress
    event: threading.Event
    decision: str = "cancel"
    error: Exception | None = None


class ConflictController(QObject):
    """Worker-to-GUI decision bridge; remembered choices live for one restoration only."""
    requested = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._all = None
        self._folders = {}
        self._closed = False
        self.requested.connect(self._answer)

    def resolve(self, conflict, progress):
        if QThread.currentThread() == self.thread():
            raise RuntimeError("Conflict decisions must be requested from a worker, not the GUI thread.")
        if self._closed:
            return "cancel"
        request = _ConflictRequest(conflict, progress, threading.Event())
        self.requested.emit(request)
        while not request.event.wait(.1):
            progress.check()
        if request.error is not None:
            raise RuntimeError(f"The restore conflict dialog could not be shown: {request.error}") from request.error
        return request.decision

    def _answer(self, request):
        if self._closed or request.progress.cancelled:
            request.event.set()
            return
        folder = os.path.normcase(os.path.normpath(request.conflict.folder))
        remembered = self._all or self._folders.get(folder)
        if remembered:
            request.decision = remembered
            request.event.set()
            return
        dialog = timer = None
        try:
            dialog = ConflictDialog(self.parent(), request.conflict)
            timer = QTimer(dialog)
            timer.timeout.connect(lambda: dialog.reject() if request.progress.cancelled else None)
            timer.start(100)
            accepted = dialog.exec() == dialog.DialogCode.Accepted
            request.decision = dialog.decision if accepted else "cancel"
            if accepted and dialog.scope.currentData() == "all":
                self._all = request.decision
            elif accepted and dialog.scope.currentData() == "folder":
                self._folders[folder] = request.decision
        except Exception as error:
            request.error = error  # Re-raised on the task thread and surfaced by TaskRunner.
        finally:
            if timer is not None:
                timer.stop()
            if dialog is not None:
                dialog.deleteLater()
            request.event.set()

    def shutdown(self):
        self._closed = True
