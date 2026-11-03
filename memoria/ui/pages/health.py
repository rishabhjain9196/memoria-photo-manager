"""Health check: fingerprints, silent-damage detection, unreadable files."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QHeaderView, QTreeWidget, QTreeWidgetItem

from ...engine import health
from .. import theme
from ..widgets import Banner, Tile, button, fmt_date, fmt_n, fmt_size, friendly_error, hbox, label, show_in_explorer
from .base import Page

COLORS = {"damaged": theme.DANGER, "unreadable": theme.DANGER, "edited": theme.MUTED}


class HealthPage(Page):
    title = "Health check"
    subtitle = "Prove your photos are intact — and catch silent damage from failing drives, bad copies or sync errors."

    def __init__(self, ctx):
        super().__init__(ctx)
        self.run_btn = button("Run health check", "primary", self.check)
        self.header_actions.addWidget(self.run_btn)
        self.explain = Banner(
            "<b>How it works.</b> The first check records a fingerprint of every file. Each later check re-reads every "
            "file: if one changed although nobody edited it (same size and date), it is flagged as possibly damaged. "
            "Photos are also opened to make sure they still display. This only reads files.", "info")
        self.last = label("", "muted")
        self.tiles = {k: Tile(text=v) for k, v in [("ok", "Intact"), ("new", "Newly fingerprinted"),
                                                   ("edited", "Edited since last check"),
                                                   ("damaged", "Possibly damaged"), ("unreadable", "Can't be opened"),
                                                   ("missing", "Missing")]}
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Status", "File", "Details"])
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tree.header().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tree.itemDoubleClicked.connect(lambda it, _: show_in_explorer(self.lib.abspath(it.data(1, Qt.ItemDataRole.UserRole))))
        self.advice = Banner("", "danger")
        self.advice.hide()
        self.body.addWidget(self.explain)
        self.body.addLayout(hbox(*self.tiles.values(), spacing=10))
        self.body.addWidget(self.advice)
        self.body.addWidget(self.last)
        self.body.addWidget(self.tree, 1)

    def on_busy_changed(self, busy: bool) -> None:
        self.run_btn.setEnabled(not busy)

    def refresh(self) -> None:
        last = health.last_checked(self.lib)
        self.last.setText(f"Last checked {fmt_date(last, True)}. Double-click a file to show it in Explorer."
                          if last else "This library has never been checked.")
        self.run_btn.setText("Run health check" if last else "Record fingerprints now")

    def check(self) -> None:
        lib = self.lib
        self.run("Checking every file", lambda p: health.run_health(lib, p), self._show)

    def _show(self, rep: health.HealthReport) -> None:
        for k, t in self.tiles.items():
            n = rep.counts.get(k, 0)
            color = theme.DANGER if k in ("damaged", "unreadable") and n else (theme.OK if k == "ok" and n else None)
            t.set(f"{n:,}", color=color)
        self.tree.clear()
        for p in rep.problems:
            detail = friendly_error(p["detail"]) if p["status"] == "unreadable" else (p["detail"] or "")
            it = QTreeWidgetItem([health.STATUS_LABEL[p["status"]], p["rel_path"], detail])
            it.setToolTip(2, p["detail"] or "")
            it.setForeground(0, QColor(COLORS.get(p["status"], theme.TEXT)))
            it.setData(1, Qt.ItemDataRole.UserRole, p["rel_path"])
            self.tree.addTopLevelItem(it)
        bad = rep.counts.get("damaged", 0)
        if bad:
            self.advice.setText(f"<b>{fmt_n(bad, 'file')} changed without being edited.</b> Restore "
                                f"{'it' if bad == 1 else 'them'} from a backup (Compare &amp; sync can help find a good "
                                "copy) and consider checking the drive for errors.")
        self.advice.setVisible(bool(bad))
        self.ctx.library_modified.emit()
        self.ctx.toast_requested.emit(f"Checked {fmt_n(rep.checked, 'file')} ({fmt_size(rep.bytes)}). "
                                      + ("No damage found." if not bad else f"{fmt_n(bad, 'file')} may be damaged."), "")
