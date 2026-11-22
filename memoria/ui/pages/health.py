"""Health check: fingerprints, silent-damage detection, unreadable files."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QHeaderView, QTreeWidget, QTreeWidgetItem

from ...engine import health
from .. import theme
from ..widgets import (Banner, HelpToggle, Tile, button, fmt_date, fmt_n, fmt_size, friendly_error, hbox, label,
                       show_in_explorer)
from .base import Page



class HealthPage(Page):
    title = "Health check"
    subtitle = "Prove your photos are intact — and catch silent damage from failing drives, bad copies or sync errors."

    def __init__(self, ctx):
        super().__init__(ctx)
        self.report = None
        self._page = 0
        self.run_btn = button("Run health check", "primary", self.check)
        self.header_actions.addWidget(self.run_btn)
        self.explain = HelpToggle(
            "The first check records a fingerprint of every file. Each later check re-reads every "
            "file: if one changed although nobody edited it (same size and date), it is flagged as possibly damaged. "
            "Photos are also opened to make sure they still display. This only reads files.",
            "How it works — this only reads files")
        self.last = label("", "muted")
        specs = [("ok", "Intact", "\uE73E", theme.OK), ("new", "Newly fingerprinted", "\uE928", theme.ACCENT),
                 ("edited", "Edited since last check", "\uE70F", theme.MUTED),
                 ("damaged", "Possibly damaged", "\uE7BA", theme.DANGER),
                 ("unreadable", "Can't be opened", "\uEA39", theme.DANGER), ("missing", "Missing", "\uE9CE", theme.WARN)]
        self.tiles = {k: Tile(text=v, glyph=g, color=c) for k, v, g, c in specs}
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
        self.page_note = label("", "small")
        self.previous = button("Previous", on_click=lambda: self._turn(-1))
        self.next = button("Next", on_click=lambda: self._turn(1))
        self.body.addLayout(hbox(self.previous, self.page_note, None, self.next))
        self.previous.setEnabled(False)
        self.next.setEnabled(False)

    def on_busy_changed(self, busy: bool) -> None:
        self.run_btn.setEnabled(not busy)

    def refresh(self) -> None:
        last = health.last_checked(self.lib)
        self.last.setText(f"Last checked {fmt_date(last, True)}. Double-click a file to show it in Explorer."
                          if last else "This library has never been checked.")
        offline = sum(not source["online"] for source in self.lib.roots())
        if offline:
            self.last.setText(self.last.text() + f" {offline} media folder(s) offline; their cached files are retained "
                              "but not checked.")
        self.run_btn.setText("Run health check" if last else "Record fingerprints now")

    def check(self) -> None:
        lib = self.lib
        self.run("Checking every file", lambda p: health.run_health(lib, p), self._show, notify_success=False)

    def _show(self, rep: health.HealthReport) -> None:
        self.report, self._page = rep, 0
        for k, t in self.tiles.items():
            n = rep.counts.get(k, 0)
            color = theme.DANGER if k in ("damaged", "unreadable") and n else (
                theme.OK if k == "ok" and n else theme.WARN if k == "missing" and n else None)
            t.set(f"{n:,}", color=color)
        self._render_page()
        bad = rep.counts.get("damaged", 0)
        problems = sum(rep.counts.get(k, 0) for k in ("damaged", "missing", "unreadable"))
        if bad:
            self.advice.setText(f"<b>{fmt_n(bad, 'file')} changed without being edited.</b> Restore "
                                f"{'it' if bad == 1 else 'them'} from a backup (Compare &amp; sync can help find a good "
                                "copy) and consider checking the drive for errors.")
        self.advice.setVisible(bool(bad))
        self.ctx.library_modified.emit()
        self.ctx.toast_requested.emit(f"Checked {fmt_n(rep.checked, 'file')} ({fmt_size(rep.bytes)}). "
                                      + ("No problems found in the files checked." if not problems else
                                         f"{fmt_n(problems, 'file')} need attention; see the results.")
                                      + (f" {rep.offline_roots} offline folder(s) were not checked." if rep.offline_roots else ""), "")
        self.ctx.notification_requested.emit("health_problems" if problems else "results_ready", problems)

    def _render_page(self):
        self.tree.clear()
        rows = self.report.problems if self.report else []
        start = self._page * 500
        for p in rows[start:start + 500]:
            detail = friendly_error(p["detail"]) if p["status"] == "unreadable" else (p["detail"] or "")
            it = QTreeWidgetItem([health.STATUS_LABEL[p["status"]], self.lib.display_path(p["rel_path"]), detail])
            it.setToolTip(2, p["detail"] or "")
            it.setForeground(0, QColor({"damaged": theme.DANGER, "unreadable": theme.DANGER}.get(p["status"], theme.MUTED)))
            it.setData(1, Qt.ItemDataRole.UserRole, p["rel_path"])
            self.tree.addTopLevelItem(it)
        self.page_note.setText(f"Showing {start + 1 if rows else 0}-{min(start + 500, len(rows))} "
                               f"of {len(rows):,} results. Totals cover the whole check.")
        self.previous.setEnabled(self._page > 0)
        self.next.setEnabled(start + 500 < len(rows))

    def _turn(self, direction):
        self._page = max(0, self._page + direction)
        self._render_page()
