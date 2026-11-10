"""Paged checkable plans with explicit, persistent selection across every page."""
from __future__ import annotations

from dataclasses import dataclass, field
from bisect import bisect_right

from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtWidgets import QTreeWidgetItem

from .widgets import button, hbox, label


@dataclass
class ReviewGroup:
    key: str
    title: str
    items: list
    default: bool = True
    size: int = 0
    exceptions: set[int] = field(default_factory=set)
    exception_bytes: int = 0

    @property
    def selected_count(self):
        return len(self.items) - len(self.exceptions) if self.default else len(self.exceptions)

    @property
    def selected_bytes(self):
        return self.size - self.exception_bytes if self.default else self.exception_bytes

    def checked(self, index):
        return self.default != (index in self.exceptions)


class ReviewPages(QObject):
    changed = Signal()
    PAGE_SIZE = 200

    def __init__(self, tree, render, size_of=lambda item: 0):
        super().__init__(tree)
        self.tree, self.render, self.size_of = tree, render, size_of
        self.groups = []
        self.page = 0
        self.total = 0
        self._ends = []
        self._selected_count = 0
        self.selected_groups = 0
        self.info = label("", "small", wrap=True)
        self.previous = button("Previous", on_click=lambda: self.step(-1))
        self.next = button("Next", on_click=lambda: self.step(1))
        self.controls = hbox(self.info, None, self.previous, self.next)
        self.tree.itemChanged.connect(self._changed)

    def set_groups(self, groups):
        self.groups = groups
        self.page = 0
        self.total = sum(len(group.items) for group in groups)
        self._ends = []
        end = 0
        for group in groups:
            end += len(group.items)
            self._ends.append(end)
        self._selected_count = sum(group.selected_count for group in groups)
        self.selected_groups = sum(bool(group.selected_count) for group in groups)
        self._fill()
        self.changed.emit()

    def step(self, delta):
        self.page = max(0, min((max(1, self.total) - 1) // self.PAGE_SIZE, self.page + delta))
        self._fill()

    def _fill(self):
        self.tree.blockSignals(True)
        self.tree.clear()
        begin, end = self.page * self.PAGE_SIZE, (self.page + 1) * self.PAGE_SIZE
        first = bisect_right(self._ends, begin)
        offset = self._ends[first - 1] if first else 0
        for group in self.groups[first:first + self.PAGE_SIZE]:
            if offset >= end:
                break
            left, right = max(0, begin - offset), min(len(group.items), end - offset)
            offset += len(group.items)
            if left >= right:
                continue
            top = QTreeWidgetItem([group.title, "", ""])
            top.setFlags(top.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            top.setData(0, Qt.ItemDataRole.UserRole, ("cat", group.key))
            top._review_group = group
            self._top(top, group)
            self.tree.addTopLevelItem(top)
            for index in range(left, right):
                child = self.render(group.key, group.items[index])
                child._review_index = index
                child.setFlags(child.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                child.setCheckState(0, Qt.CheckState.Checked if group.checked(index) else Qt.CheckState.Unchecked)
                top.addChild(child)
            top.setExpanded(True)
        self.tree.blockSignals(False)
        last = min(self.total, end)
        self.info.setText(f"Showing {begin + 1 if self.total else 0:,}–{last:,} of {self.total:,} planned items. "
                          "Selections persist across pages; a group checkbox selects its entire group.")
        self.previous.setEnabled(self.page > 0)
        self.next.setEnabled(end < self.total)

    @staticmethod
    def _top(top, group):
        count = group.selected_count
        top.setText(0, f"{group.title}  ({count:,} / {len(group.items):,} selected, all pages)")
        top.setCheckState(0, Qt.CheckState.Checked if count == len(group.items) else
                         Qt.CheckState.PartiallyChecked if count else Qt.CheckState.Unchecked)

    def _changed(self, item, column):
        if column != 0:
            return
        self.tree.blockSignals(True)
        top = item if item.parent() is None else item.parent()
        group = top._review_group
        before = group.selected_count
        if item.parent() is None:
            group.default = item.checkState(0) != Qt.CheckState.Unchecked
            group.exceptions.clear()
            group.exception_bytes = 0
            for index in range(item.childCount()):
                item.child(index).setCheckState(0, Qt.CheckState.Checked if group.default else Qt.CheckState.Unchecked)
            top = item
        else:
            top = item.parent()
            group, index = top._review_group, item._review_index
            checked = item.checkState(0) == Qt.CheckState.Checked
            exception = checked != group.default
            if exception != (index in group.exceptions):
                size = self.size_of(group.items[index])
                if exception:
                    group.exceptions.add(index)
                    group.exception_bytes += size
                else:
                    group.exceptions.remove(index)
                    group.exception_bytes -= size
        self._top(top, group)
        self._selected_count += group.selected_count - before
        self.selected_groups += int(bool(group.selected_count)) - int(bool(before))
        self.tree.blockSignals(False)
        self.changed.emit()

    def selected(self):
        return {group.key: [item for index, item in enumerate(group.items) if group.checked(index)]
                for group in self.groups if group.selected_count}

    @property
    def selected_count(self):
        return self._selected_count
