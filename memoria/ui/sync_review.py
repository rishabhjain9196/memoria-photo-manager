"""Review a sync as a folder tree: see every folder and file being copied, untick what should stay put."""
from __future__ import annotations

import os
from collections import defaultdict

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QCheckBox, QHeaderView, QSpinBox, QTreeWidget, QTreeWidgetItem

from ..engine import config, libsync
from . import theme
from .motion import Dialog
from .widgets import Banner, button, fmt_n, fmt_size, hbox, label, vbox

FILES_PER_FOLDER = 2000
NODE_ROLE = Qt.ItemDataRole.UserRole
ITEM_ROLE = Qt.ItemDataRole.UserRole + 1


class _Node:
    __slots__ = ("name", "parent", "folders", "items", "total", "bytes", "off", "off_bytes", "widget", "loaded",
                 "destinations")

    def __init__(self, name, parent=None):
        self.name, self.parent = name, parent
        self.folders: dict[str, _Node] = {}
        self.items: list[int] = []
        self.total = self.bytes = self.off = self.off_bytes = 0
        self.widget = None
        self.loaded = False
        self.destinations: set = set()


class CopyReviewDialog(Dialog):
    def __init__(self, parent, cmp: libsync.Comparison, items: list[libsync.CopyItem]):
        super().__init__(parent)
        self.cmp, self.items = cmp, items
        self.off = {index for index, item in enumerate(items) if item.excluded}
        self.setWindowTitle("Choose what to copy")
        self.resize(1080, 720)

        self.roots: list[_Node] = []
        by_direction = defaultdict(list)
        for index, item in enumerate(items):
            by_direction[(item.entry.side, item.target)].append(index)
        for (source, target), indexes in sorted(by_direction.items()):
            root = _Node(f"{libsync.letter(source)} → {libsync.letter(target)}:  copy from "
                         f"{cmp.participants[source].label} to {cmp.participants[target].label}")
            for index in indexes:
                node = root
                for part in [part for part in items[index].entry.folder.split(os.sep) if part]:
                    node = node.folders.setdefault(part.lower(), _Node(part, node))
                node.items.append(index)
            self._totals(root)
            self.roots.append(root)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Folder / file", "Size", "Files", "Copied to"])
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for column in (1, 2):
            self.tree.header().setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)
        self.tree.header().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.tree.header().resizeSection(3, 300)
        self.tree.itemExpanded.connect(self._expanded)
        self.tree.itemChanged.connect(self._changed)
        self.tree.blockSignals(True)
        for root in self.roots:
            self._add_folder(self.tree.invisibleRootItem(), root, depth=0)
        self.tree.blockSignals(False)

        self.limit = QSpinBox()
        self.limit.setRange(1, 1_000_000)
        self.limit.setValue(500)
        self.limit.setSuffix(" MB")
        self.summary = label("", "h2", wrap=True)
        self.remember = QCheckBox("Remember unticked files: keep them only in their current library and don't offer "
                                  "them again for this pair")
        self.remember.setChecked(True)
        self.remember.toggled.connect(lambda _: self._update())
        self.ok = button("Copy", "primary", self.accept)
        remembered = len(self.off)
        self.setLayout(vbox(
            label("Choose what to copy", "h2"),
            label("Every folder and file that would be copied is listed by its folder in the source library. Untick a "
                  "folder to skip everything inside it, or untick single files - for example large videos that are "
                  "fine to keep only on the drive." + (f" {fmt_n(remembered, 'file')} you skipped before "
                                                       "start unticked." if remembered else ""), "muted", wrap=True),
            hbox(button("Untick all videos", on_click=self._untick_videos),
                 button("Untick files over", on_click=self._untick_large), self.limit,
                 button("Tick everything", on_click=lambda: self._set_all(False)), None),
            self.tree, self.summary, self.remember,
            Banner("Copies are written to a temporary file, verified byte for byte and only then named. Existing "
                   "files are never overwritten - a name clash gets a new name. Undo removes only these copies.",
                   "trust"),
            hbox(None, button("Cancel", on_click=self.reject), self.ok), spacing=8, margins=(18, 18, 18, 18)))
        self._update()

    # model ----------------------------------------------------------------------------------
    def _totals(self, node: _Node) -> None:
        node.total = len(node.items)
        node.bytes = sum(self.items[index].entry.size for index in node.items)
        node.off = sum(index in self.off for index in node.items)
        node.off_bytes = sum(self.items[index].entry.size for index in node.items if index in self.off)
        node.destinations = {(self.items[index].target, self.items[index].folder) for index in node.items}
        for child in node.folders.values():
            self._totals(child)
            node.total += child.total
            node.bytes += child.bytes
            node.off += child.off
            node.off_bytes += child.off_bytes
            if len(node.destinations) < 2:
                node.destinations |= child.destinations

    def _subtree(self, node: _Node):
        yield node
        for child in node.folders.values():
            yield from self._subtree(child)

    def _set(self, indexes, off: bool) -> None:
        for index in indexes:
            if off:
                self.off.add(index)
            else:
                self.off.discard(index)

    # widgets --------------------------------------------------------------------------------
    def _destination(self, node: _Node) -> str:
        if len(node.destinations) != 1:
            return "several folders"
        target, folder = next(iter(node.destinations))
        return f"{libsync.letter(target)}: {folder or '(library root)'}"

    def _add_folder(self, parent: QTreeWidgetItem, node: _Node, depth: int) -> None:
        item = QTreeWidgetItem([node.name, "", "", self._destination(node)])
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item.setData(0, NODE_ROLE, node)
        if depth == 0:
            font = QFont(item.font(0))
            font.setBold(True)
            item.setFont(0, font)
        node.widget = item
        parent.addChild(item)
        self._paint_folder(node)
        for child in sorted(node.folders.values(), key=lambda value: value.name.lower()):
            self._add_folder(item, child, depth + 1)
        if node.items:
            if depth < 2:
                self._load_files(node)
            else:
                item.addChild(QTreeWidgetItem(["Loading..."]))
        item.setExpanded(depth < 2)

    def _paint_folder(self, node: _Node) -> None:
        item = node.widget
        if item is None:
            return
        on, on_bytes = node.total - node.off, node.bytes - node.off_bytes
        item.setCheckState(0, Qt.CheckState.Unchecked if on == 0 else
                           Qt.CheckState.Checked if node.off == 0 else Qt.CheckState.PartiallyChecked)
        item.setText(1, fmt_size(node.bytes) if not node.off else f"{fmt_size(on_bytes)} of {fmt_size(node.bytes)}")
        item.setText(2, f"{node.total:,}" if not node.off else f"{on:,} of {node.total:,}")
        color = QColor(theme.MUTED) if on == 0 else QColor(theme.TEXT)
        for column in (0, 1, 2):
            item.setForeground(column, color)

    def _file_row(self, index: int) -> QTreeWidgetItem:
        copy = self.items[index]
        entry = copy.entry
        row = QTreeWidgetItem([entry.name, fmt_size(entry.size), "",
                               f"{libsync.letter(copy.target)}: {copy.folder or '(library root)'}"
                               + ("" if copy.merged else "  (new folder)")])
        row.setFlags(row.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        row.setData(0, ITEM_ROLE, index)
        row.setCheckState(0, Qt.CheckState.Unchecked if index in self.off else Qt.CheckState.Checked)
        row.setToolTip(0, f"{libsync.letter(entry.side)}: {entry.rel}\n-> {copy.action.dst}"
                       + ("\nYou chose before to keep this only where it is." if copy.excluded else ""))
        if copy.excluded:
            row.setText(2, "skipped before")
        return row

    def _load_files(self, node: _Node) -> None:
        if node.loaded:
            return
        node.loaded = True
        item = node.widget
        for position in reversed(range(item.childCount())):
            if item.child(position).data(0, NODE_ROLE) is None:
                item.takeChild(position)
        ordered = sorted(node.items, key=lambda index: self.items[index].entry.name.lower())
        for index in ordered[:FILES_PER_FOLDER]:
            item.addChild(self._file_row(index))
        if len(ordered) > FILES_PER_FOLDER:
            item.addChild(QTreeWidgetItem([f"... {len(ordered) - FILES_PER_FOLDER:,} more files - use the folder "
                                           "checkbox or the buttons above for them"]))

    def _expanded(self, item: QTreeWidgetItem) -> None:
        node = item.data(0, NODE_ROLE)
        if node is not None and not node.loaded and node.items:
            self.tree.blockSignals(True)
            self._load_files(node)
            self.tree.blockSignals(False)

    def _refresh(self, nodes) -> None:
        self.tree.blockSignals(True)
        for node in nodes:
            self._paint_folder(node)
            if node.loaded:
                for position in range(node.widget.childCount()):
                    child = node.widget.child(position)
                    index = child.data(0, ITEM_ROLE)
                    if index is not None:
                        child.setCheckState(0, Qt.CheckState.Unchecked if index in self.off else Qt.CheckState.Checked)
        self.tree.blockSignals(False)
        self._update()

    def _recount(self, nodes) -> None:
        for root in self.roots:
            self._totals(root)
        self._refresh(nodes)

    def _changed(self, item: QTreeWidgetItem, column: int) -> None:
        if column != 0:
            return
        index = item.data(0, ITEM_ROLE)
        if index is not None:
            self._set([index], item.checkState(0) == Qt.CheckState.Unchecked)
            node = item.parent().data(0, NODE_ROLE)
            ancestors = []
            while node is not None:
                ancestors.append(node)
                node = node.parent
            self._recount(ancestors)
            return
        node = item.data(0, NODE_ROLE)
        if node is None:
            return
        off = item.checkState(0) == Qt.CheckState.Unchecked
        subtree = list(self._subtree(node))
        self._set([index for child in subtree for index in child.items], off)
        ancestors = []
        parent = node.parent
        while parent is not None:
            ancestors.append(parent)
            parent = parent.parent
        self._recount(subtree + ancestors)

    def _all_nodes(self):
        for root in self.roots:
            yield from self._subtree(root)

    def _untick_videos(self) -> None:
        self._set([index for index, item in enumerate(self.items)
                   if os.path.splitext(item.entry.name)[1].lower() in config.VIDEO_EXT], True)
        self._recount(list(self._all_nodes()))

    def _untick_large(self) -> None:
        limit = self.limit.value() * 1024 * 1024
        self._set([index for index, item in enumerate(self.items) if item.entry.size > limit], True)
        self._recount(list(self._all_nodes()))

    def _set_all(self, off: bool) -> None:
        self._set(range(len(self.items)), off)
        self._recount(list(self._all_nodes()))

    def _update(self) -> None:
        chosen = [item for index, item in enumerate(self.items) if index not in self.off]
        skipped = len(self.items) - len(chosen)
        size = sum(item.entry.size for item in chosen)
        skipped_size = sum(item.entry.size for item in self.items) - size
        self.summary.setText(
            f"Copy {fmt_n(len(chosen), 'file')} ({fmt_size(size)})"
            + (f" · skip {fmt_n(skipped, 'file')} ({fmt_size(skipped_size)}), which stay only where they are"
               if skipped else ""))
        self.ok.setText(f"Copy {fmt_n(len(chosen), 'file')}" if chosen else
                        ("Save choices" if self.remember.isChecked() else "Copy"))
        self.ok.setEnabled(bool(chosen) or self.remember.isChecked())

    def selected(self) -> list[libsync.CopyItem]:
        return [item for index, item in enumerate(self.items) if index not in self.off]

    def skipped(self) -> list[libsync.CopyItem]:
        return [item for index, item in enumerate(self.items) if index in self.off]
