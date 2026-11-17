"""Choose how a scope-wide cleanup treats photos whose linked parts are not identical.

Both plans are prepared before this dialog opens, so it always lists real files. It is shown only
when including linked parts would move more than the strict, verified-duplicates-only plan.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QGuiApplication
from PySide6.QtWidgets import QButtonGroup, QCheckBox, QHeaderView, QRadioButton, QTreeWidget, QTreeWidgetItem

from . import theme
from .motion import Dialog
from .widgets import Banner, button, fmt_n, fmt_size, hbox, label, vbox

PAGE_SIZE = 200


class CleanupReviewDialog(Dialog):
    def __init__(self, parent, ctx, strict_plan, linked_plan, scope: str):
        super().__init__(parent)
        self.ctx, self.lib = ctx, ctx.library
        self.strict, self.linked = strict_plan, linked_plan
        self.offset = 0
        self.setWindowTitle("Some duplicates have linked parts that differ")
        screen = (parent.screen() if parent is not None else None) or QGuiApplication.primaryScreen()
        available = screen.availableGeometry() if screen is not None else None
        self.resize(min(1040, available.width() - 40) if available else 1040,
                    min(700, available.height() - 60) if available else 700)

        strict_ids = {action.file_id for action in strict_plan.actions}
        linked_ids = {action.file_id for action in linked_plan.actions}
        parts = {part["id"]: part for part in linked_plan.review_parts}
        self.unmatched = [part for part in linked_plan.review_parts if part["unmatched"]]
        self.rows = []
        for action in linked_plan.actions:
            part = parts.get(action.file_id)
            self.rows.append((action, part, "Both options" if action.file_id in strict_ids else "Option 2 only"))
        self.rows += [(action, None, "Option 1 only") for action in strict_plan.actions
                      if action.file_id not in linked_ids]

        strict_size = sum(action.size for action in strict_plan.actions)
        linked_size = sum(action.size for action in linked_plan.actions)
        self.strict_option = QRadioButton(
            f"1. Move only verified duplicates - {fmt_n(len(strict_plan.actions), 'file')} ({fmt_size(strict_size)})"
            if strict_plan.actions else
            "1. Move only verified duplicates - nothing qualifies: every set here has linked parts that differ")
        self.strict_option.setEnabled(bool(strict_plan.actions))
        self.include_linked = QRadioButton(
            f"2. Also move the linked parts - {fmt_n(len(linked_plan.actions), 'file')} ({fmt_size(linked_size)})"
            + (f", {len(self.unmatched)} may be unique" if self.unmatched else ""))
        group = QButtonGroup(self)
        group.addButton(self.strict_option)
        group.addButton(self.include_linked)
        (self.strict_option if strict_plan.actions else self.include_linked).setChecked(True)
        self.strict_option.toggled.connect(self._update)
        self.ack = QCheckBox(f"I reviewed the {len(self.unmatched)} linked part(s) marked \"may be unique\" "
                             "and want them moved to Recovery too.")
        self.ack.toggled.connect(self._update)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["File", "Folder", "Size", "Status", "Moved by"])
        self.tree.setRootIsDecorated(False)
        self.tree.setTextElideMode(Qt.TextElideMode.ElideMiddle)
        self.tree.header().setStretchLastSection(False)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for column in (0, 2, 3, 4):
            self.tree.header().setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)
        self.page_note = label("", "small")
        self.previous = button("Previous", on_click=lambda: self._turn(-1))
        self.next = button("Next", on_click=lambda: self._turn(1))
        kept = linked_plan.linked_reasons
        self.kept_note = label(
            (f"{fmt_n(len(kept), 'asset')} stay in both options: " + "; ".join(kept[:3])
             + (f"; and {len(kept) - 3} more." if len(kept) > 3 else ".")) if kept else "", "small", wrap=True)
        self.kept_note.setTextFormat(Qt.TextFormat.PlainText)
        self.kept_note.setVisible(bool(kept))
        self.status = label("", "small", wrap=True)
        self.go_btn = button("Continue...", "primary", self.accept)
        self.cancel_btn = button("Cancel", on_click=self.reject)
        self.setLayout(vbox(
            label("Some duplicates have linked parts that differ", "h2"),
            label(f"Scope: {scope}.", "muted", wrap=True),
            Banner("<b>What are linked parts?</b> Phones and cameras save some photos as several files with the "
                   "same name: a Live Photo video (.MOV), a RAW + JPEG pair, or an edit file (.AAE/.XMP). Memoria "
                   "always moves a photo together with its linked parts. Here the photos are exact duplicates, but "
                   "some of their linked parts are not identical to the copy being kept, so they may be unique.",
                   "info"),
            label("Choose what to move", "h2"), self.strict_option, self.include_linked,
            self.tree, hbox(self.previous, self.page_note, None, self.next), self.kept_note,
            self.ack, self.status, hbox(None, self.cancel_btn, self.go_btn), spacing=8, margins=(18, 18, 18, 18)))
        self._render()
        self._update()

    @property
    def plan(self):
        return self.linked if self.include_linked.isChecked() else self.strict

    def _render(self):
        self.tree.clear()
        for action, part, option in self.rows[self.offset:self.offset + PAGE_SIZE]:
            unmatched = bool(part and part["unmatched"])
            path = self.lib.display_path(self.lib.rel(action.src, resolve=False))
            folder, _, name = path.rpartition("\\")
            reason = part["reason"] if part else action.reason
            item = QTreeWidgetItem([name, folder or "(library root)", fmt_size(action.size),
                                    "Linked part - may be unique" if unmatched else
                                    "Linked part - verified duplicate" if part else "Verified duplicate", option])
            item.setToolTip(0, action.src)
            item.setToolTip(1, folder)
            item.setToolTip(3, reason)
            if unmatched:
                item.setForeground(3, QColor(theme.WARN))
            self.tree.addTopLevelItem(item)
        total = len(self.rows)
        self.page_note.setText(f"{self.offset + 1 if total else 0}-{min(self.offset + PAGE_SIZE, total)} of "
                               f"{total:,} files. Each option covers every page of this scope.")
        paged = total > PAGE_SIZE
        for widget in (self.previous, self.next):
            widget.setVisible(paged)
        self.previous.setEnabled(self.offset > 0)
        self.next.setEnabled(self.offset + PAGE_SIZE < total)

    def _update(self, *_):
        linked = self.include_linked.isChecked()
        needs_ack = linked and bool(self.unmatched)
        self.ack.setVisible(needs_ack)
        plan = self.plan
        ready = bool(plan.actions) and (not needs_ack or self.ack.isChecked())
        self.go_btn.setEnabled(ready)
        self.go_btn.setText(f"Continue with {fmt_n(len(plan.actions), 'file')}..." if plan.actions else "Continue...")
        if needs_ack and not self.ack.isChecked():
            self.status.setText("Tick the confirmation above to include parts that may be unique.")
        else:
            self.status.setText("Next you'll see a final confirmation. Files go to Recovery and can be undone.")

    def _turn(self, direction):
        self.offset = max(0, self.offset + direction * PAGE_SIZE)
        self._render()

    def accept(self):
        if self.go_btn.isEnabled():
            super().accept()

    def selected_plan(self):
        plan = self.plan
        if not plan.actions:
            raise ValueError("Nothing can be moved with this option.")
        if plan is self.linked and self.unmatched and not self.ack.isChecked():
            raise ValueError("Acknowledge the linked parts that may be unique before continuing.")
        return plan

    def shutdown(self):
        pass
