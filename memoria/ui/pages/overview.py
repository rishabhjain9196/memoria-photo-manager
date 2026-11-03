"""Overview: what's in the library and what each tool can do for it."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QWidget

from ...engine import actions, health, organize, similar, tidy
from .. import theme
from ..tasks import BackgroundCall
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
        self.updating = label("", "small")
        self.rescan_btn = button("Rescan library", on_click=lambda: self.window().index_library(),
                                 tip="Look for new, changed or removed files (only reads files) — F5")
        self.check_btn = button("Check everything", "primary", lambda: self.ctx.checkup_requested.emit(),
                                tip="Find duplicates, similar photos and videos, blurry photos, leftovers and "
                                    "files to organise in one go. Reads only — nothing is changed.")
        for w in (self.updating, self.rescan_btn, self.check_btn):
            self.header_actions.addWidget(w)
        ctx.people_changed.connect(self._mark_stale)
        ctx.albums_changed.connect(self._mark_stale)
        self.t_photos, self.t_videos, self.t_size, self.t_span = Tile(text="Photos"), Tile(text="Videos"), \
            Tile(text="Library size"), Tile(text="Covers")
        tiles = hbox(self.t_photos, self.t_videos, self.t_size, self.t_span, spacing=12)
        self.trust = Banner("", "trust")
        self.pending = Banner("", "info")
        grid = QGridLayout()
        grid.setSpacing(12)
        specs = [("\uE8C8", "Duplicates", "duplicates"), ("\uE734", "Similar & best shots", "similar"),
                 ("\uE74D", "Tidy up", "tidy"), ("\uE8B7", "Organise by date", "organize"),
                 ("\uE7AA", "Albums", "albums"), ("\uE716", "People", "people"),
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
        self.bg = BackgroundCall(self)
        self.bg.result.connect(self._insights)
        self.bg.failed.connect(lambda e: self.updating.setText(""))

    def on_busy_changed(self, busy: bool) -> None:
        self.rescan_btn.setEnabled(not busy)
        self.check_btn.setEnabled(not busy)

    def shutdown(self) -> None:
        self.bg.wait()

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
        self.cards["story"].set("Make Instagram stories, carousels and story videos from your photos.")
        self.cards["video"].set(f"{fmt_n(st['videos'], 'video')} in this library. Make smaller copies for sharing."
                                if st["videos"] else "Make smaller copies of videos for sharing.")
        self.cards["compare"].set("Check a backup drive or old laptop folder against this library and copy what's missing.")
        from ...engine import albums, faces
        n_albums = len(albums.albums(lib))
        self.cards["albums"].set(f"{fmt_n(n_albums, 'album')}. Make more from dates, places or people." if n_albums else
                                 "Let Memoria suggest albums by event, trip, place or person — no files are moved.")
        fs = faces.status(lib)
        self.cards["people"].set(
            f"{fmt_n(fs['people'], 'person', 'people')} named. Search for anyone to see all their photos." if fs["people"]
            else f"{fmt_n(fs['faces'], 'face')} found — name people to find all their photos." if fs["faces"]
            else "Find the people in your photos, name them, and see every photo of someone.",
            bool(fs["pending"] and fs["faces"]))
        cached = {k: self.ctx.cached(k) for k in ("duplicates", "duplicate_report", "similar", "similar_videos", "tidy",
                                                "organize")}
        self.updating.setText("Updating…")
        self.bg.call(lambda: _insights(lib, cached))

    def _insights(self, d: dict) -> None:
        self.updating.setText("")
        rf, rs = d["recovery"]
        self.trust.setText(
            f"<b>Your files are safe.</b> Memoria has only read this library unless you approved a change. "
            f"Recovery holds {fmt_n(rf, 'file')} ({fmt_size(rs)}); every change is listed in History and can be undone.")
        if d["dup_groups"] is not None:
            n = d["dup_copies"]
            nf = d["dup_folders"]
            self.cards["duplicates"].set(f"{fmt_n(n, 'extra copy', 'extra copies')} found in {fmt_n(d['dup_groups'], 'group')}"
                                         + (f", including {fmt_n(nf, 'whole duplicate folder')}." if nf else ".")
                                         if n else "No exact copies — every file is unique.", bool(n))
        else:
            m = d["maybe_dupes"]
            self.cards["duplicates"].set(
                f"{fmt_n(m, 'file')} might have exact copies. Check to be sure — files are compared byte by byte."
                if m else "No exact copies possible: every file has a unique size.", bool(m))
        blurry = d["blurry"]
        if d["similar_groups"] is not None:
            g = d["similar_groups"]
            self.cards["similar"].set(f"{fmt_n(g, 'group')} of similar photos or videos to review"
                                      + (f"; {fmt_n(blurry, 'photo')} look blurry." if blurry else "."), bool(g or blurry))
        else:
            self.cards["similar"].set(
                f"Find bursts, look-alike photos and similar videos, and keep the best. {fmt_n(blurry, 'photo')} look blurry."
                if blurry else "Find bursts, look-alike photos and similar videos, and keep the best.", bool(blurry))
        t = d["tidy"]
        n_tidy = t["junk"] + t["empty"] + t["folders"]
        self.cards["tidy"].set(
            f"{fmt_n(t['junk'], 'leftover file')}, {fmt_n(t['empty'], 'empty file')} and "
            f"{fmt_n(t['folders'], 'empty folder')} can be tidied away." if n_tidy
            else "Nothing to tidy — no junk files or empty folders.", bool(n_tidy))
        o = d["organize"]
        self.cards["organize"].set(
            f"{fmt_n(o, 'file')} could be filed into year/month folders. You'll see every move first."
            if o else "Everything with a reliable date is already in date folders.")
        last_chk = d["health"]
        self.cards["health"].set(f"Last checked {fmt_date(last_chk, True)}." if last_chk else
                                 "Never checked. Record fingerprints now so future damage can be spotted.",
                                 not last_chk)
        n_batches = d["batches"]
        self.cards["history"].set(f"{fmt_n(n_batches, 'change')} recorded. Undo any of them." if n_batches
                                  else "No changes made yet.")


def _insights(lib, cached: dict) -> dict:
    """Read-only summary for the tool cards (runs on a background thread)."""
    try:
        d = {"recovery": actions.recovery_size(lib), "blurry": len(similar.find_blurry(lib)),
             "health": health.last_checked(lib), "batches": len(actions.batches(lib))}
        d["maybe_dupes"] = lib.db.execute(
            "SELECT COUNT(*) FROM files WHERE kind!='other' AND size>0 AND size IN "
            "(SELECT size FROM files WHERE kind!='other' AND size>0 GROUP BY size HAVING COUNT(*)>1)").fetchone()[0]
        dups = cached.get("duplicates")
        d["dup_groups"] = len(dups) if dups is not None else None
        d["dup_copies"] = sum(len(g.files) - 1 for g in dups) if dups is not None else None
        rep = cached.get("duplicate_report")
        d["dup_folders"] = len(rep.folders) if rep is not None else 0
        sims = cached.get("similar")
        d["similar_groups"] = (len(sims) + len(cached.get("similar_videos") or [])) if sims is not None else None
        rep = cached.get("tidy") or tidy.find_tidy(lib)
        d["tidy"] = {k: rep.count(k) for k in ("junk", "empty", "folders")}
        plan = cached.get("organize") or organize.plan_organize(lib)
        d["organize"] = len(plan.items)
        return d
    finally:
        lib.close_thread()
