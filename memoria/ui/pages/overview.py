"""Overview: what's in the library and what each tool can do for it."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QWidget

from ...engine import actions, health, organize, similar, tidy
from .. import theme
from ..widgets import Banner, Tile, button, fmt_date, fmt_n, fmt_size, glyph_label, hbox, label, scroll, vbox
from .base import Page


class ToolCard(QFrame):
    def __init__(self, glyph: str, title: str, key: str, ctx):
        super().__init__()
        self.setObjectName("card")
        self.status = label("", "muted", wrap=True)
        self.btn = button("Open", on_click=lambda: ctx.navigate.emit(key))
        lay = vbox(hbox(glyph_label(glyph, 20, theme.ACCENT), label(title, "h2"), None), self.status, None,
                   hbox(None, self.btn), spacing=6, margins=(16, 14, 16, 12))
        self.setLayout(lay)
        self.setMinimumHeight(130)

    def set(self, text: str, highlight: bool = False) -> None:
        self.status.setText(text)
        self.btn.setObjectName("primary" if highlight else "")
        self.btn.style().unpolish(self.btn)
        self.btn.style().polish(self.btn)


class OverviewPage(Page):
    title = "Overview"
    subtitle = "Your library at a glance"

    def __init__(self, ctx):
        super().__init__(ctx)
        self.rescan_btn = button("Rescan library", on_click=lambda: self.window().index_library(),
                                 tip="Look for new, changed or removed files (only reads files)")
        self.header_actions.addWidget(self.rescan_btn)
        self.t_photos, self.t_videos, self.t_size, self.t_span = Tile(text="Photos"), Tile(text="Videos"), \
            Tile(text="Library size"), Tile(text="Covers")
        tiles = hbox(self.t_photos, self.t_videos, self.t_size, self.t_span, spacing=12)
        self.trust = Banner("", "trust")
        self.pending = Banner("", "info")
        grid = QGridLayout()
        grid.setSpacing(12)
        specs = [("\uE8C8", "Duplicates", "duplicates"), ("\uE734", "Similar & best shots", "similar"),
                 ("\uE74D", "Tidy up", "tidy"), ("\uE8B7", "Organise by date", "organize"),
                 ("\uEA18", "Health check", "health"), ("\uE81C", "History & recovery", "history"),
                 ("\uE786", "Story maker", "story"), ("\uE714", "Video compressor", "video"),
                 ("\uE895", "Compare & sync", "compare")]
        self.cards = {}
        for i, (g, t, k) in enumerate(specs):
            c = ToolCard(g, t, k, ctx)
            self.cards[k] = c
            grid.addWidget(c, i // 3, i % 3)
        content = QWidget()
        content.setLayout(vbox(tiles, self.pending, self.trust, 4, label("What Memoria can do for this library", "h2"),
                               grid, None, spacing=12))
        self.body.addWidget(scroll(content))

    def on_busy_changed(self, busy: bool) -> None:
        self.rescan_btn.setEnabled(not busy)

    def refresh(self) -> None:
        lib = self.lib
        st = lib.stats()
        self.t_photos.set(f"{st['images']:,}")
        self.t_videos.set(f"{st['videos']:,}")
        self.t_size.set(fmt_size(st["bytes"]), f"{st['files']:,} files in total")
        first, last = st["first"], st["last"]
        if first and last:
            self.t_span.set(f"{first[:4]}–{last[:4]}" if first[:4] != last[:4] else first[:4],
                            f"{fmt_date(first)} to {fmt_date(last)}")
        else:
            self.t_span.set("—")
        self.pending.setVisible(bool(st["pending"]))
        self.pending.setText(f"Memoria is still reading {fmt_n(st['pending'], 'file')}. Results below will "
                             "fill in as it goes.")
        rf, rs = actions.recovery_size(lib)
        self.trust.setText(
            f"<b>Your files are safe.</b> Memoria has only read this library unless you approved a change. "
            f"Recovery holds {fmt_n(rf, 'file')} ({fmt_size(rs)}); every change is listed in History and can be undone.")

        blurry = len(similar.find_blurry(lib))
        maybe_dupes = lib.db.execute(
            "SELECT COUNT(*) FROM files WHERE kind!='other' AND size>0 AND size IN "
            "(SELECT size FROM files WHERE kind!='other' AND size>0 GROUP BY size HAVING COUNT(*)>1)").fetchone()[0]
        self.cards["duplicates"].set(
            f"{fmt_n(maybe_dupes, 'file')} might have exact copies. Check to be sure — files are compared byte by byte."
            if maybe_dupes else "No exact copies possible: every file has a unique size.", bool(maybe_dupes))
        self.cards["similar"].set(
            f"Find bursts and near-identical shots and keep the best one. {fmt_n(blurry, 'photo')} look blurry."
            if blurry else "Find bursts and near-identical shots and keep the best one.", bool(blurry))
        rep = tidy.find_tidy(lib)
        n_tidy = rep.count("junk") + rep.count("empty") + rep.count("folders")
        self.cards["tidy"].set(
            f"{fmt_n(rep.count('junk'), 'leftover file')}, {fmt_n(rep.count('empty'), 'empty file')} and "
            f"{fmt_n(rep.count('folders'), 'empty folder')} can be tidied away." if n_tidy
            else "Nothing to tidy — no junk files or empty folders.", bool(n_tidy))
        plan = organize.plan_organize(lib)
        self.cards["organize"].set(
            f"{fmt_n(len(plan.items), 'file')} could be filed into year/month folders. You'll see every move first."
            if plan.items else "Everything with a reliable date is already in date folders.")
        last_chk = health.last_checked(lib)
        self.cards["health"].set(f"Last checked {fmt_date(last_chk, True)}." if last_chk else
                                 "Never checked. Record fingerprints now so future damage can be spotted.",
                                 not last_chk)
        n_batches = len(actions.batches(lib))
        self.cards["history"].set(f"{fmt_n(n_batches, 'change')} recorded. Undo any of them." if n_batches
                                  else "No changes made yet.")
        self.cards["story"].set("Make Instagram stories, carousels and story videos from your photos.")
        self.cards["video"].set(f"{fmt_n(st['videos'], 'video')} in this library. Make smaller copies for sharing."
                                if st["videos"] else "Make smaller copies of videos for sharing.")
        self.cards["compare"].set("Check a backup drive or old laptop folder against this library and copy what's missing.")
