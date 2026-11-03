"""Compare the library with a backup drive / other folder and copy what's missing."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QFileDialog, QHeaderView, QLineEdit, QStackedWidget, QTabWidget, QTreeWidget,
                               QTreeWidgetItem, QWidget)

from ...engine import compare
from .. import theme
from ..widgets import Banner, Card, EmptyState, Tile, button, fmt_n, fmt_size, hbox, label, vbox
from .base import Page


def _tree() -> QTreeWidget:
    t = QTreeWidget()
    t.setHeaderLabels(["File", "Size"])
    t.setRootIsDecorated(False)
    t.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
    t.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
    return t


class ComparePage(Page):
    title = "Compare & sync"
    subtitle = "Check a backup drive or another folder against this library — by content, so renamed copies still count."

    def __init__(self, ctx):
        super().__init__(ctx)
        self.path = QLineEdit()
        self.path.setPlaceholderText(r"e.g. E:\Photos Backup")
        browse = button("Browse…", on_click=self._browse)
        self.cmp_btn = button("Compare", "primary", self.run_compare)
        self.body.addWidget(Card(vbox(label("Other folder", "h2"), hbox(self.path, browse, self.cmp_btn),
                                      label("The other folder is only read while comparing. It is written to only "
                                            "if you choose to copy files into it.", "small"), spacing=8)))
        self.stack = QStackedWidget()
        self.stack.addWidget(EmptyState("\uE895", "Is everything backed up?",
                                        "Pick your backup folder and Memoria will list photos and videos that exist "
                                        "only in one place. Matching is by file content, not name."))
        self.t_here, self.t_there, self.t_both = Tile(text="Only in this library"), Tile(text="Only in the other folder"), \
            Tile(text="In both")
        self.here = _tree()
        self.there = _tree()
        self.here.itemChanged.connect(lambda *_: self._update())
        self.there.itemChanged.connect(lambda *_: self._update())
        self.copy_out = button("Copy to other folder", "primary", lambda: self.sync(True))
        self.copy_in = button("Copy into this library", "primary", lambda: self.sync(False))
        tabs = QTabWidget()
        w1, w2 = QWidget(), QWidget()
        w1.setLayout(vbox(self.here, hbox(label("Ticked files are copied to the same sub-folder in the other folder.",
                                                 "small"), None, self.copy_out), spacing=8, margins=(0, 8, 0, 0)))
        w2.setLayout(vbox(self.there, hbox(label("Ticked files are copied into this library, keeping their sub-folders.",
                                                 "small"), None, self.copy_in), spacing=8, margins=(0, 8, 0, 0)))
        tabs.addTab(w1, "Missing from the other folder")
        tabs.addTab(w2, "Missing from this library")
        self.tabs = tabs
        res = QWidget()
        res.setLayout(vbox(hbox(self.t_here, self.t_there, self.t_both, spacing=12),
                           Banner("Copies are written to a temporary file, checked byte for byte against the original, "
                                  "and only then given their name. Existing files are never overwritten.", "trust"),
                           tabs, spacing=10))
        self.results = res
        self.stack.addWidget(res)
        self.body.addWidget(self.stack, 1)
        self.result: compare.CompareResult | None = None

    def on_busy_changed(self, busy: bool) -> None:
        self.cmp_btn.setEnabled(not busy)
        self._update()

    def refresh(self) -> None:
        if self.result is not None and Path(self.path.text()).is_dir():
            self.run_compare()

    def _browse(self) -> None:
        p = QFileDialog.getExistingDirectory(self, "Choose the folder to compare with", self.path.text() or "")
        if p:
            self.path.setText(p)

    def run_compare(self) -> None:
        other = self.path.text().strip()
        if not other or not Path(other).is_dir():
            self.ctx.toast_requested.emit("Choose a folder that exists.", "")
            return
        lib = self.lib
        self.run("Comparing", lambda p: compare.compare(lib, other, p), self._show)

    def _show(self, res: compare.CompareResult) -> None:
        self.result = res
        self.t_here.set(f"{len(res.only_here):,}", fmt_size(res.bytes_only_here),
                        theme.WARN if res.only_here else theme.OK)
        self.t_there.set(f"{len(res.only_there):,}", fmt_size(res.bytes_only_there))
        self.t_both.set(f"{res.in_both:,}")
        for tree, rows in ((self.here, [(r["rel_path"], r["size"], r) for r in res.only_here]),
                           (self.there, [(t.rel_path, t.size, t) for t in res.only_there])):
            tree.blockSignals(True)
            tree.clear()
            for rel, size, obj in rows:
                it = QTreeWidgetItem([rel, fmt_size(size)])
                it.setFlags(it.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                it.setCheckState(0, Qt.CheckState.Checked)
                it.setData(0, Qt.ItemDataRole.UserRole, obj)
                tree.addTopLevelItem(it)
            tree.blockSignals(False)
        self.tabs.setTabText(0, f"Missing from the other folder ({len(res.only_here):,})")
        self.tabs.setTabText(1, f"Missing from this library ({len(res.only_there):,})")
        self.stack.setCurrentWidget(self.results)
        self._update()

    def _checked(self, tree: QTreeWidget) -> list:
        return [tree.topLevelItem(i).data(0, Qt.ItemDataRole.UserRole) for i in range(tree.topLevelItemCount())
                if tree.topLevelItem(i).checkState(0) == Qt.CheckState.Checked]

    def _update(self) -> None:
        a, b = self._checked(self.here), self._checked(self.there)
        self.copy_out.setText(f"Copy {fmt_n(len(a), 'file')} to other folder")
        self.copy_in.setText(f"Copy {fmt_n(len(b), 'file')} into this library")
        self.copy_out.setEnabled(bool(a) and not self.busy)
        self.copy_in.setEnabled(bool(b) and not self.busy)

    def sync(self, outward: bool) -> None:
        res = self.result
        rows = self._checked(self.here) if outward else []
        others = [] if outward else self._checked(self.there)
        acts = compare.plan_sync(self.lib, res, rows, others)
        size = sum(a.size for a in acts)
        dest = str(res.other) if outward else str(self.lib.root)
        self.apply_actions(
            "sync", "Copy missing files", acts,
            summary=f"{fmt_n(len(acts), 'file')} ({fmt_size(size)}) will be copied to {dest}.",
            details=["Originals are not moved or changed.", "Each copy is verified byte for byte.",
                     "If a different file already has the same name, the copy gets a new name instead."],
            confirm_text=f"Copy {fmt_n(len(acts), 'file')}",
            note="Undo removes only the copies made here, and only if they are still unchanged.",
            done_message=lambda r: f"Copied and verified {fmt_n(r.done, 'file')} ({fmt_size(r.bytes)}).",
            rescan=not outward)
