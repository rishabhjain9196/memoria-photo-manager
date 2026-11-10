"""One scope-wide review when exact media have linked parts that are not identical."""
from __future__ import annotations

import threading

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QCheckBox, QDialog, QHeaderView, QTreeWidget, QTreeWidgetItem

from ..engine import duplicate_cleanup
from ..engine.progress import Progress
from . import theme
from .tasks import LatestCall
from .widgets import button, fmt_n, fmt_size, hbox, label, vbox

PAGE_SIZE = 200


class CleanupReviewDialog(QDialog):
    def __init__(self, parent, ctx, report, hashes, file_choices, folder_choices, initial_plan):
        super().__init__(parent)
        self.ctx, self.lib, self.report = ctx, ctx.library, report
        self.hashes, self.file_choices, self.folder_choices = hashes, file_choices, folder_choices
        self.plan = initial_plan
        self._closed = self._loading = False
        self._valid = True
        self._cancel = threading.Event()
        self.offset = 0
        self.setWindowTitle("Review linked parts across all exact groups" if hashes is None else
                            "Review linked parts in this folder group")
        self.resize(1040, 670)
        self.summary = label("", "h2", wrap=True)
        self.status = label("", "small", wrap=True)
        self.status.setTextFormat(Qt.TextFormat.PlainText)
        self.include_linked = QCheckBox("Include linked parts that may be unique - review them below")
        self.include_linked.toggled.connect(self._load)
        self.ack = QCheckBox("I approve moving the listed linked parts that are not proven duplicates, including unique parts.")
        self.ack.toggled.connect(self._update)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["File to move", "Size", "Review", "Reason"])
        self.tree.setRootIsDecorated(False)
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tree.header().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tree.header().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.page_note = label("", "small", wrap=True)
        self.previous = button("Previous", on_click=lambda: self._turn(-1))
        self.next = button("Next", on_click=lambda: self._turn(1))
        self.go_btn = button("Review move to Recovery...", "primary", self.accept)
        self.cancel_btn = button("Cancel", on_click=self.reject)
        self.setLayout(vbox(
            self.summary,
            label("The photos may be exact duplicates while their linked videos, RAW files or edit sidecars differ. "
                  "Strict bulk cleanup keeps these assets. To include them, enable the option and review every "
                  "listed part; this applies to the whole scope, not one set at a time.", "muted", wrap=True),
            label("At least one verified copy of every matched exact content set remains. Saved Keep choices "
                  "and unchecked reviewed copies stay protected. Additional unique linked parts can leave the "
                  "library only with your acknowledgement; they go to Recovery with Undo.",
                  "muted", wrap=True),
            self.include_linked, self.tree, hbox(self.previous, self.page_note, None, self.next),
            self.ack, self.status, hbox(self.cancel_btn, None, self.go_btn), margins=(18, 18, 18, 18)))
        self.bg = LatestCall(self)
        self.bg.result.connect(self._loaded)
        self.bg.failed.connect(self._failed)
        self._render()
        self._update()

    def _load(self, include):
        self._cancel.set()
        self._cancel = cancel = threading.Event()
        self._loading, self._valid = True, False
        self.ack.setChecked(False)
        self.go_btn.setEnabled(False)
        self.status.setText("Preparing the combined linked-part plan. Nothing is being moved.")
        lib, generation = self.lib, self.ctx.generation
        def work():
            try:
                plan = duplicate_cleanup.plan_cleanup(
                    lib, self.report, hashes=self.hashes, file_choices=self.file_choices,
                    folder_choices=self.folder_choices, include_linked=include, progress=Progress(cancel=cancel))
                return generation, plan
            finally:
                lib.close_thread()
        self.bg.call(work)
        self._update()

    def _loaded(self, result):
        if self._closed:
            return
        generation, plan = result
        if generation != self.ctx.generation:
            self._failed(ValueError("The catalogue changed. Close this review and find duplicates again."))
            return
        self.plan = plan
        self._loading, self._valid = False, True
        self.offset = 0
        self.status.setText("")
        self._render()
        self._update()

    def _failed(self, error):
        if not self._closed:
            self._loading, self._valid = False, False
            self.status.setText(f"The combined plan could not be prepared: {error}")
            self._update()

    def _render(self):
        parts = {part["id"]: part for part in self.plan.review_parts}
        self.tree.clear()
        for action in self.plan.actions[self.offset:self.offset + PAGE_SIZE]:
            part = parts.get(action.file_id)
            unmatched = bool(part and part["unmatched"])
            path = self.lib.display_path(self.lib.rel(action.src, resolve=False))
            item = QTreeWidgetItem([
                path, fmt_size(action.size),
                "Not proven duplicate - may be unique" if unmatched else "Verified redundant content",
                part["reason"] if part else action.reason])
            item.setToolTip(0, action.src)
            item.setToolTip(3, part["reason"] if part else action.reason)
            if unmatched:
                item.setForeground(2, QColor(theme.WARN))
            self.tree.addTopLevelItem(item)
        total = len(self.plan.actions)
        self.page_note.setText(
            f"{self.offset + 1 if total else 0}-{min(self.offset + PAGE_SIZE, total)} of {total:,} files. "
            "The confirmed operation includes all pages in this scope.")
        self.previous.setEnabled(self.offset > 0 and not self._loading)
        self.next.setEnabled(self.offset + PAGE_SIZE < total and not self._loading)

    def _update(self, *_):
        unmatched = [part for part in self.plan.review_parts if part["unmatched"]]
        self.summary.setText(
            f"{fmt_n(len(self.plan.actions), 'file')} ({fmt_size(sum(action.size for action in self.plan.actions))}) "
            f"planned across {self.plan.groups} exact set(s).")
        self.ack.setVisible(bool(unmatched) and self._valid)
        self.go_btn.setEnabled(self._valid and not self._loading and bool(self.plan.actions)
                               and (not unmatched or self.ack.isChecked()))
        if self._valid and not self._loading:
            self.status.setText(
                f"{len(unmatched)} linked part(s) ({fmt_size(sum(part['size'] for part in unmatched))}) "
                f"are not proven duplicates and may be unique. {self.plan.protected_groups} protected set(s); "
                f"{self.plan.linked_skipped} linked asset(s) still excluded."
                + (" Nothing can be moved with the current options." if not self.plan.actions else ""))
        self.tree.setEnabled(not self._loading)
        self.previous.setEnabled(not self._loading and self.offset > 0)
        self.next.setEnabled(not self._loading and self.offset + PAGE_SIZE < len(self.plan.actions))

    def _turn(self, direction):
        self.offset = max(0, self.offset + direction * PAGE_SIZE)
        self._render()

    def accept(self):
        if self.go_btn.isEnabled():
            super().accept()

    def selected_plan(self):
        if self._loading or not self._valid or not self.plan.actions:
            raise ValueError("The combined cleanup review is not ready.")
        if any(part["unmatched"] for part in self.plan.review_parts) and not self.ack.isChecked():
            raise ValueError("Acknowledge the linked parts that may be unique before continuing.")
        return self.plan

    def shutdown(self):
        self._closed = True
        self._cancel.set()
        self.bg.wait()
