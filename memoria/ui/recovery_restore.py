"""Review Recovery destinations and resolve conflicts without overwriting existing files."""
from __future__ import annotations

import os
import threading
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QThread, QTimer, Qt, Signal
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialog, QFileDialog, QHeaderView, QPlainTextEdit,
                               QTreeWidget, QTreeWidgetItem)

from .motion import Dialog
from .tasks import LatestCall
from .widgets import button, fmt_n, fmt_size, hbox, label, vbox

if TYPE_CHECKING:
    from ..engine.progress import Progress
    from ..engine.recovery_restore import RestoreConflict, RestorePlan

PAGE_SIZE = 200
ORIGIN = {"history": "Where it came from", "inferred": "Matched by folder", "manual": "You chose"}


class RestoreDialog(Dialog):
    def __init__(self, parent, ctx):
        super().__init__(parent)
        self.ctx, self.lib = ctx, ctx.library
        self.plan: RestorePlan | None = None
        self._closed = False
        self._loading = True
        self._valid = False
        self.offset = 0
        self.setWindowTitle("Restore removed files")
        self.resize(1040, 660)
        self.summary = label("Checking Recovery…", "h2", wrap=True)
        self.status = label("", "small", wrap=True)
        self.include_unlogged = QCheckBox("Also restore files Memoria has no record of")
        self.include_unlogged.setChecked(True)
        self.include_unlogged.toggled.connect(self._selection_changed)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["File", "Goes back to", "Size", "How"])
        self.tree.setRootIsDecorated(False)
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tree.currentItemChanged.connect(lambda *_: self._update())
        self.previous = button("Previous", on_click=lambda: self._turn(-1))
        self.next = button("Next", on_click=lambda: self._turn(1))
        self.page_note = label("", "small")
        self.map_btn = button("Choose folder…", on_click=self._map,
                              tip="Pick where the selected file's group should go.")
        self.go_btn = button("Restore", "primary", self.accept)
        self.cancel_btn = button("Cancel", on_click=self.reject)
        self.setLayout(vbox(
            self.summary,
            label("Nothing is ever overwritten. If a file with the same name exists, you'll be asked.",
                  "muted", wrap=True),
            self.tree,
            hbox(self.previous, self.page_note, None, self.next),
            hbox(self.include_unlogged, None, self.map_btn), self.status,
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
            raise ValueError("Recovery is still being checked. Try again in a moment.")
        return replace(self.plan, items=self._selected_items())

    def accept(self):
        if self.go_btn.isEnabled():
            super().accept()

    def refresh(self):
        from ..engine import recovery_restore
        lib, generation = self.lib, self.ctx.generation
        self._loading, self._valid = True, False
        self.status.setText("")
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
            self._failed(ValueError("The library changed. Close this window and try again."))
            return
        self.plan = plan
        self._loading, self._valid = False, True
        self.offset = 0
        notes = []
        if plan.offline_roots:
            notes.append(f"{fmt_n(len(plan.offline_roots), 'disconnected folder')} skipped — connect "
                         f"{'it' if len(plan.offline_roots) == 1 else 'them'} to include those files.")
        if plan.errors:
            notes.append(f"{fmt_n(len(plan.errors), 'item')} couldn't be read and will stay in Recovery.")
        self.status.setText("\n".join(notes))
        self.status.setToolTip("\n".join(plan.errors[:50]))
        self._render()
        self._update()

    def _failed(self, error):
        if not self._closed:
            self._loading, self._valid = False, False
            self.status.setText(f"Couldn't check Recovery: {error}")
            self._update()

    def _selection_changed(self):
        self.offset = 0
        self._render()
        self._update()

    def _where(self, path):
        try:
            return self.lib.display_path(self.lib.rel(path, resolve=False))
        except ValueError:
            return str(path)

    def _render(self):
        items = self._selected_items()
        self.tree.clear()
        for item in items[self.offset:self.offset + PAGE_SIZE]:
            how = item.issue or ORIGIN.get(item.provenance, item.provenance)
            row = QTreeWidgetItem([item.source.name, self._where(item.target) if item.target is not None
                                   else "Select, then Choose folder…", fmt_size(item.size), how])
            row.setData(0, Qt.ItemDataRole.UserRole, item)
            row.setToolTip(0, str(item.source))
            row.setToolTip(1, str(item.target) if item.target is not None else item.issue)
            row.setToolTip(3, item.issue or how)
            self.tree.addTopLevelItem(row)
        self.page_note.setText(f"Showing {self.offset + 1 if items else 0}-"
                               f"{min(self.offset + PAGE_SIZE, len(items))} of {len(items):,}")
        self.previous.setEnabled(self.offset > 0 and not self._loading)
        self.next.setEnabled(self.offset + PAGE_SIZE < len(items) and not self._loading)

    def _turn(self, direction):
        self.offset = max(0, self.offset + direction * PAGE_SIZE)
        self._render()

    def _update(self, *_):
        items = self._selected_items()
        eligible = [item for item in items if item.target is not None and not item.issue]
        waiting = len(items) - len(eligible)
        if self._loading:
            self.summary.setText("Checking Recovery…")
        elif not items:
            self.summary.setText("Nothing to restore.")
        else:
            self.summary.setText(
                f"Restore {fmt_n(len(eligible), 'file')} ({fmt_size(sum(item.size for item in eligible))})"
                + (f" · {waiting:,} need a folder or will stay in Recovery" if waiting else ""))
        self.go_btn.setText(f"Restore {fmt_n(len(eligible), 'file')}" if eligible else "Restore")
        self.go_btn.setEnabled(self._valid and not self._loading and bool(eligible))
        current = self.tree.currentItem()
        item = current.data(0, Qt.ItemDataRole.UserRole) if current else None
        self.map_btn.setEnabled(not self._loading and item is not None and bool(item.mapping_group)
                                and item.provenance != "history")
        self.include_unlogged.setEnabled(not self._loading)

    def _map(self):
        from ..engine import recovery_restore
        current = self.tree.currentItem()
        if current is None or self.plan is None:
            return
        item = current.data(0, Qt.ItemDataRole.UserRole)
        folder = QFileDialog.getExistingDirectory(self, "Where should these files go?", str(self.lib.root))
        if not folder:
            return
        plan, lib, generation, group = self.plan, self.lib, self.ctx.generation, item.mapping_group
        self._loading, self._valid = True, False
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


class ConflictDialog(Dialog):
    def __init__(self, parent, conflict):
        super().__init__(parent)
        self.decision = "cancel"
        self.setWindowTitle("This file already exists")
        self.resize(760, 440)
        details = QPlainTextEdit()
        details.setReadOnly(True)
        details.setPlainText("In Recovery:\n" + "\n".join(conflict.sources) +
                             "\n\nAlready exists at:\n" + "\n".join(conflict.targets))
        self.scope = QComboBox()
        for text, value in (("Just this file", "one"), ("Everything else in this folder", "folder"),
                            ("Everything else", "all")):
            self.scope.addItem(text, value)
        self.keep_btn = button("Keep both", "primary", lambda: self._choose("rename"))
        self.skip_btn = button("Skip", on_click=lambda: self._choose("skip"))
        self.cancel_btn = button("Stop restoring", on_click=self.reject)
        self.setLayout(vbox(
            label("A file with this name already exists", "h2", wrap=True),
            label("Keep both restores it with a number added, e.g. “photo (2).jpg”. Skip leaves it in Recovery.",
                  "muted", wrap=True),
            details, hbox(label("Do the same for:"), self.scope),
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
