"""History of every change, undo, and the Recovery folder."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QHeaderView, QSplitter, QTreeWidget, QTreeWidgetItem

from ...engine import actions
from .. import theme
from ..widgets import (Banner, Card, ConfirmDialog, button, fmt_date, fmt_n, fmt_size, hbox, label, open_path,
                       show_in_explorer, vbox)
from .base import Page

def status_label(status: str) -> tuple[str, str]:
    return {"applied": ("Done", theme.OK), "partial": ("Partly done", theme.WARN), "undone": ("Undone", theme.MUTED),
            "emptied": ("Done · Recovery emptied", theme.MUTED),
            "applying": ("In progress", theme.WARN)}.get(status, (status, theme.TEXT))


KIND = {"duplicates": "Duplicates", "similar": "Similar / blurry", "tidy": "Tidy up", "organize": "Organise",
        "sync": "Compare & sync", "batch": "Photos & videos", "edit": "Editor",
        "albums": "Albums export", "story": "Story maker", "video": "Video compressor"}
OP = {"recycle": "Moved to Recovery", "move": "Moved", "copy": "Copied", "rmdir": "Removed empty folder",
      "create": "Created"}
OP_STATUS = {"done": "Done", "undone": "Undone", "skipped": "Skipped", "failed": "Failed", "purged": "Deleted from Recovery",
             "pending": "Interrupted"}


class HistoryPage(Page):
    title = "History & recovery"
    subtitle = "Every change Memoria has made to this library. Undo any of them."

    def __init__(self, ctx):
        super().__init__(ctx)
        self.batches = QTreeWidget()
        self.batches.setHeaderLabels(["When", "What", "Files", "Size", "Status"])
        self.batches.setRootIsDecorated(False)
        self.batches.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for c in (0, 2, 3, 4):
            self.batches.header().setSectionResizeMode(c, QHeaderView.ResizeMode.ResizeToContents)
        self.batches.currentItemChanged.connect(self._select)
        self.ops = QTreeWidget()
        self.ops.setHeaderLabels(["Action", "File", "Now at", "Status"])
        self.ops.setRootIsDecorated(False)
        self.ops.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.ops.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.ops.header().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.ops.header().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.ops.itemDoubleClicked.connect(self._reveal)
        self.undo_btn = button("Undo this change", "primary", self.undo)
        self.undo_btn.setEnabled(False)
        self.detail = label("", "muted", wrap=True)
        split = QSplitter(Qt.Orientation.Vertical)
        split.addWidget(self.batches)
        from PySide6.QtWidgets import QWidget
        bottom = QWidget()
        bottom.setLayout(vbox(hbox(self.detail, None, self.undo_btn), self.ops, spacing=6))
        split.addWidget(bottom)
        split.setSizes([300, 400])

        self.rec_label = label("", "")
        self.open_rec = button("Open Recovery folder", on_click=lambda: self.lib and self.lib.recovery.mkdir(
            parents=True, exist_ok=True) or open_path(self.lib.recovery))
        self.empty_btn = button("Empty Recovery…", "danger", self.empty_recovery)
        rec = Card(vbox(hbox(label("Recovery folder", "h2"), None, self.open_rec, self.empty_btn), self.rec_label,
                        spacing=6))
        self.body.addWidget(rec)
        self.body.addWidget(split, 1)

    def on_busy_changed(self, busy: bool) -> None:
        self._select(self.batches.currentItem(), None)
        self.empty_btn.setEnabled(not busy and actions.recovery_size(self.lib)[0] > 0 if self.lib else False)

    def refresh(self) -> None:
        files, size = actions.recovery_size(self.lib)
        self.rec_label.setText(
            f"{fmt_n(files, 'file')} ({fmt_size(size)}) are being kept safe in Recovery. They stay there until you "
            "empty it — only then are they permanently deleted." if files else
            "Recovery is empty.")
        self.empty_btn.setEnabled(files > 0 and not self.busy)
        cur = self.batches.currentItem()
        cur_id = cur.data(0, Qt.ItemDataRole.UserRole)["id"] if cur else None
        self.batches.clear()
        select = None
        all_batches = actions.batches(self.lib)
        newest = all_batches[0]["id"] if all_batches else None
        if newest != getattr(self, "_newest_id", None):
            cur_id = None                      # a new change arrived: show it rather than an older selection
        self._newest_id = newest
        for b in all_batches:
            label_, color = status_label(b["status"])
            it = QTreeWidgetItem([fmt_date(b["created_at"], True), b["title"], f"{b['files']:,}",
                                  fmt_size(b["bytes"]), label_])
            it.setForeground(4, QColor(color))
            it.setData(0, Qt.ItemDataRole.UserRole, b)
            self.batches.addTopLevelItem(it)
            if b["id"] == cur_id or select is None:
                select = it if b["id"] == cur_id or select is None else select
        if self.batches.topLevelItemCount() == 0:
            self.ops.clear()
            self.detail.setText("No changes yet. When you apply a clean-up or organise, it will appear here.")
            self.undo_btn.setEnabled(False)
        else:
            self.batches.setCurrentItem(select)

    def _select(self, cur, _prev) -> None:
        if cur is None or self.lib is None:
            self.undo_btn.setEnabled(False)
            return
        b = cur.data(0, Qt.ItemDataRole.UserRole)
        ops = actions.operations(self.lib, b["id"])
        self.ops.clear()
        for o in ops[:5000]:
            it = QTreeWidgetItem([OP.get(o["op"], o["op"]), self._short(o["src"]), self._short(o["dst"]),
                                  OP_STATUS.get(o["status"], o["status"])])
            it.setToolTip(1, o["src"])
            it.setToolTip(2, o["dst"] or "")
            if o["status"] in ("failed", "skipped"):
                it.setForeground(3, QColor(theme.WARN))
                it.setToolTip(3, o["error"] or "")
            it.setData(0, Qt.ItemDataRole.UserRole, o)
            self.ops.addTopLevelItem(it)
        can_undo = any(o["status"] == "done" for o in ops) and b["status"] != "emptied"
        purged = any(o["status"] == "purged" for o in ops)
        self.undo_btn.setEnabled(can_undo and not self.busy)
        kind = KIND.get(b["kind"], b["kind"])
        self.detail.setText(f"{kind} · {fmt_date(b['created_at'], True)} · {fmt_n(len(ops), 'step')}"
                            + (" · Recovery for this change was emptied, so it can't be undone." if purged else ""))

    def _short(self, path) -> str:
        """Paths inside the library are shown relative to it; Recovery is named as such."""
        if not path:
            return ""
        from pathlib import Path
        p = Path(path)
        try:
            rel = p.relative_to(self.lib.recovery)
            return "Recovery › " + str(Path(*rel.parts[1:])) if len(rel.parts) > 1 else "Recovery"
        except ValueError:
            pass
        try:
            return str(p.relative_to(self.lib.root))
        except ValueError:
            return str(p)

    def _reveal(self, item, _col) -> None:
        o = item.data(0, Qt.ItemDataRole.UserRole)
        from pathlib import Path
        for p in (o["dst"], o["src"]):
            if p and Path(p).exists():
                show_in_explorer(p)
                return

    def undo(self) -> None:
        cur = self.batches.currentItem()
        if cur is None:
            return
        b = cur.data(0, Qt.ItemDataRole.UserRole)
        dlg = ConfirmDialog(self, "Undo this change?", f"“{b['title']}” from {fmt_date(b['created_at'], True)} will be reversed.",
                            ["Moved files go back to where they were. If a file with that name has appeared there "
                             "since, the restored file gets a new name — nothing is overwritten.",
                             "Copies made by Compare & sync are removed only if they are unchanged."],
                            "Undo")
        if dlg.exec():
            self.window().undo_batch(b["id"])

    def empty_recovery(self) -> None:
        files, size = actions.recovery_size(self.lib)
        dlg = ConfirmDialog(self, "Permanently delete files in Recovery?",
                            f"{fmt_n(files, 'file')} ({fmt_size(size)}) will be deleted forever.",
                            ["This permanently deletes the files stored in Recovery.",
                             "Changes whose files are deleted can no longer be undone."],
                            "Delete permanently", danger=True,
                            require_ack="I understand these files cannot be recovered", note=None)
        if not dlg.exec():
            return
        lib = self.lib

        def done(n):
            self.ctx.library_modified.emit()
            self.ctx.toast_requested.emit(f"Recovery emptied: {fmt_n(n, 'file')} deleted.", "")

        self.run("Emptying Recovery", lambda p: actions.empty_recovery(lib, progress=p), done)
