"""Manage additional media folders without moving their files or relocating the catalogue."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QFileDialog, QHeaderView, QTreeWidget, QTreeWidgetItem

from .motion import Dialog
from ..engine import roots
from ..engine.db import LibraryUnavailable
from .widgets import button, hbox, label, vbox


class LibraryRootsDialog(Dialog):
    def __init__(self, parent, ctx):
        super().__init__(parent)
        self.ctx, self.lib = ctx, ctx.library
        self.changed = False
        self._working = False
        self.setWindowTitle("Library folders")
        self.resize(880, 480)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Folder", "Location", "Connection"])
        self.tree.setRootIsDecorated(False)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tree.currentItemChanged.connect(lambda *_: self._busy(ctx.runner.busy))
        self.add_btn = button("Add folder...", "primary", self.add)
        self.reconnect_btn = button("Reconnect selected...", on_click=self.reconnect)
        self.check_btn = button("Check connections", on_click=self.check)
        self.close_btn = button("Done", on_click=self.accept)
        self.status = label("", "small", wrap=True)
        self.setLayout(vbox(
            label("One catalogue, multiple media folders", "h2"),
            label("The current library remains the catalogue home and must stay connected. Added folders are "
                  "indexed in place; offline folders retain cached files and thumbnails. Recovery stays on each "
                  "source drive. Reconnect verifies the folder's identity before changing its location.",
                  "muted", wrap=True),
            self.tree, self.status,
            hbox(self.add_btn, self.reconnect_btn, self.check_btn, None, self.close_btn)))
        ctx.runner.busy_changed.connect(self._busy)
        ctx.runner.error.connect(self._failed)
        self._fill()

    def _fill(self):
        selected = self._selected()
        self.tree.clear()
        for root in self.lib.roots():
            item = QTreeWidgetItem([
                root["label"] + (" (catalogue home)" if root["id"] == 1 else ""), root["path"],
                "Available" if root["online"] else "Offline / unavailable"])
            item.setData(0, Qt.ItemDataRole.UserRole, root["id"])
            item.setToolTip(2, root["error"] or "")
            self.tree.addTopLevelItem(item)
            if root["id"] == selected:
                self.tree.setCurrentItem(item)
        self._busy(self.ctx.runner.busy)

    def _selected(self):
        current = self.tree.currentItem()
        return current.data(0, Qt.ItemDataRole.UserRole) if current else None

    def _busy(self, busy):
        self.add_btn.setEnabled(not busy)
        self.check_btn.setEnabled(not busy)
        self.reconnect_btn.setEnabled(not busy and self._selected() not in (None, 1))
        self.close_btn.setEnabled(not busy)

    def _failed(self, _title, message, _details):
        if self._working:
            self._working = False
            self.status.setText(message)

    def _run(self, title, action):
        if self.ctx.runner.busy:
            return
        self._working = True
        self.status.setText(title)
        def work(progress):
            try:
                progress.check()
                return action()
            finally:
                self.lib.close_thread()
        def done(_):
            self._working = False
            self.changed = True
            self._fill()
            self.status.setText("Folders updated. Click Done to refresh the catalogue; no originals were moved.")
        if not self.ctx.runner.run(title, work, done, diagnostic_key="other"):
            self._working = False
            self.status.setText("Wait for the current task to finish.")

    def add(self):
        path = QFileDialog.getExistingDirectory(self, "Add a media folder")
        if path:
            self._run("Registering media folder", lambda: roots.add(self.lib, path))

    def reconnect(self):
        source = self._selected()
        if source in (None, 1):
            return
        path = QFileDialog.getExistingDirectory(self, "Locate the same media folder")
        if path:
            self._run("Reconnecting media folder", lambda: roots.reconnect(self.lib, source, path))

    def check(self):
        def work():
            for root in self.lib.roots():
                try:
                    roots.check(self.lib, root["id"])
                except LibraryUnavailable:
                    continue  # Stored connection errors are displayed in the table.
        self._run("Checking folder connections", work)

    def reject(self):
        if not self._working:
            super().reject()

    def closeEvent(self, event):
        if self._working:
            event.ignore()
        else:
            super().closeEvent(event)
