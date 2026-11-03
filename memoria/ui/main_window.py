"""Main window: sidebar navigation, page stack, task bar, toast, shortcuts and library lifecycle."""
from __future__ import annotations

import os
import shutil
import time
from pathlib import Path

from PySide6.QtCore import QSettings, Qt, Signal
from PySide6.QtGui import QKeySequence, QPixmap, QShortcut
from PySide6.QtWidgets import (QButtonGroup, QComboBox, QFileDialog, QFrame, QHBoxLayout, QLabel, QMainWindow,
                               QProgressBar, QPushButton, QStackedWidget, QVBoxLayout, QWidget)

from .. import __version__
from ..engine import actions, scanner
from ..engine.db import Library, LibraryInUse, LibraryTooNew
from . import theme
from .tasks import TaskRunner
from .widgets import (AppContext, Banner, ConfirmDialog, MessageDialog, Toast, button, fmt_date, fmt_n,
                      glyph_label, hbox, icon_family, label, vbox)

NAV = [
    ("LIBRARY", [("overview", "Overview", "\uE80F"), ("photos", "Photos & videos", "\uE91B")]),
    ("CLEAN UP", [("duplicates", "Duplicates", "\uE8C8"), ("similar", "Similar & best shots", "\uE734"),
                  ("tidy", "Tidy up", "\uE74D")]),
    ("ORGANISE", [("organize", "Organise by date", "\uE8B7")]),
    ("CREATE", [("editor", "Editor", "\uE70F"), ("story", "Story maker", "\uE786"),
                ("video", "Video compressor", "\uE714")]),
    ("PROTECT", [("health", "Health check", "\uEA18"), ("compare", "Compare & sync", "\uE895"),
                 ("history", "History & recovery", "\uE81C")]),
]
NAV_KEYS = [k for _, items in NAV for k, _, _ in items]


def page_classes() -> dict:
    from .pages import compare, duplicates, health, history, organize, overview, photos, similar, tidy
    classes = {"overview": overview.OverviewPage, "photos": photos.PhotosPage,
               "duplicates": duplicates.DuplicatesPage, "similar": similar.SimilarPage,
               "tidy": tidy.TidyPage, "organize": organize.OrganizePage,
               "health": health.HealthPage, "compare": compare.ComparePage, "history": history.HistoryPage}
    try:
        from .pages.editor import EditorPage
        classes["editor"] = EditorPage
    except ImportError:
        pass
    try:
        from .pages.story import StoryPage
        classes["story"] = StoryPage
    except ImportError:
        pass
    try:
        from .pages.video import VideoPage
        classes["video"] = VideoPage
    except ImportError:
        pass
    return classes


def _sample_dir() -> Path:
    base = os.environ.get("LOCALAPPDATA") or str(Path.home())
    return Path(base) / "Memoria" / "Sample Library"


def _fmt_secs(s: float) -> str:
    s = int(s)
    if s < 60:
        return f"{s} s"
    if s < 3600:
        return f"{s // 60} min {s % 60:02d} s"
    return f"{s // 3600} h {s % 3600 // 60:02d} min"


class WelcomePage(QWidget):
    def __init__(self, window: "MainWindow"):
        super().__init__()
        title = label("Welcome to Memoria", "pageTitle")
        sub = label("A private photo and video manager for your Windows PC. Everything stays on this computer.",
                    "pageSubtitle", wrap=True)
        points = Banner(
            "<b>Built to be trusted</b><br>"
            "• Memoria only <b>reads</b> your photos while it looks around.<br>"
            "• Before changing anything it shows you exactly what will happen, and asks.<br>"
            "• It never deletes: removed files go to a Recovery folder, and every change can be undone.<br>"
            "• Its catalogue lives in a hidden <i>.memoria</i> folder inside the library you choose.", "trust")
        choose = button("Choose photo folder…", "primary", window.choose_library)
        sample = button("Try it on a sample library", on_click=window.open_sample,
                        tip="Creates a realistic, generated test library in your AppData folder")
        tip = label("Tip: you can also drag a folder onto this window.", "small")
        self.recent = QVBoxLayout()
        card = QFrame()
        card.setObjectName("card")
        inner = vbox(title, sub, 8, points, 8, hbox(choose, sample, None), tip, 8, self.recent, spacing=10,
                     margins=(32, 28, 32, 28))
        card.setLayout(inner)
        card.setMaximumWidth(760)
        self.setLayout(vbox(None, hbox(None, card, None), None, margins=(40, 40, 40, 40)))
        self.window_ = window

    def set_recent(self, paths: list[str]) -> None:
        while self.recent.count():
            item = self.recent.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        paths = [p for p in paths if Path(p).is_dir()][:5]
        if paths:
            self.recent.addWidget(label("Recent libraries", "small"))
        for p in paths:
            b = button(p, "link", lambda _=False, p=p: self.window_.open_library(p))
            self.recent.addWidget(b, alignment=Qt.AlignmentFlag.AlignLeft)


class MainWindow(QMainWindow):
    theme_change_requested = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Memoria")
        self.resize(1360, 860)
        self.setMinimumSize(1100, 700)
        self.setAcceptDrops(True)
        self.settings = theme.settings()
        self.runner = TaskRunner(self)
        self.ctx = AppContext(self.runner)
        self.page_classes = page_classes()
        self.pages: dict[str, QWidget] = {}
        self.nav_buttons: dict[str, QPushButton] = {}
        self.nav_badges: dict[str, QLabel] = {}
        self.current_key = ""
        self._task_started_at = 0.0
        self._build()
        self._shortcuts()
        self.runner.started.connect(self._task_started)
        self.runner.progressed.connect(self._task_progress)
        self.runner.finished.connect(self._task_finished)
        self.runner.error.connect(self._task_error)
        self.runner.busy_changed.connect(lambda busy: self.theme_combo.setEnabled(not busy))
        self.ctx.toast_requested.connect(self.toast.show_message)
        self.ctx.navigate.connect(self.go)
        self.ctx.badges_changed.connect(self._update_badges)
        self.ctx.checkup_requested.connect(self.run_checkup)
        self.toast.undo_clicked.connect(self.undo_batch)
        geo = self.settings.value("geometry")
        if geo is not None:
            self.restoreGeometry(geo)
        self._show_library_ui(False)

    # ---------------------------------------------------------------------------- layout
    def _build(self) -> None:
        side = QFrame()
        side.setObjectName("sidebar")
        side.setFixedWidth(250)
        sl = QVBoxLayout(side)
        sl.setContentsMargins(10, 16, 10, 12)
        sl.setSpacing(2)
        logo = QLabel()
        logo_path = Path(__file__).resolve().parent / "assets" / "memoria.png"
        if logo_path.exists():
            logo.setPixmap(QPixmap(str(logo_path)).scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio,
                                                          Qt.TransformationMode.SmoothTransformation))
        sl.addLayout(hbox(8, logo, label("Memoria", "appTitle"), None, spacing=8))
        self.lib_label = label("No library open", "libraryLabel", wrap=True)
        self.lib_label.setContentsMargins(14, 4, 8, 0)
        sl.addWidget(self.lib_label)
        change = button("Change library…", "link", self.choose_library, tip="Ctrl+O")
        sl.addLayout(hbox(8, change, None))
        sl.addSpacing(6)
        group = QButtonGroup(self)
        group.setExclusive(True)
        self.nav_container = QWidget()
        nl = QVBoxLayout(self.nav_container)
        nl.setContentsMargins(0, 0, 0, 0)
        nl.setSpacing(1)
        fam = icon_family()
        for heading, items in NAV:
            nl.addWidget(label(heading, "navGroup"))
            for key, text, glyph in items:
                if key not in self.page_classes:
                    continue
                n = NAV_KEYS.index(key) + 1
                shown = text.replace("&", "&&")
                b = QPushButton(f"         {shown}" if fam else f"  {shown}")
                b.setObjectName("nav")
                b.setCheckable(True)
                b.setCursor(Qt.CursorShape.PointingHandCursor)
                b.setToolTip(f"{text}  (Ctrl+{n % 10})" if n <= 10 else text)
                lay = QHBoxLayout(b)
                lay.setContentsMargins(10, 0, 8, 0)
                if fam:
                    g = glyph_label(glyph, 15, theme.MUTED)
                    g.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
                    lay.addWidget(g)
                lay.addStretch(1)
                badge = QLabel("")
                badge.setObjectName("navBadge")
                badge.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
                badge.hide()
                lay.addWidget(badge)
                self.nav_badges[key] = badge
                b.clicked.connect(lambda _=False, k=key: self.go(k))
                group.addButton(b)
                self.nav_buttons[key] = b
                nl.addWidget(b)
        sl.addWidget(self.nav_container)
        sl.addStretch(1)
        self.theme_combo = QComboBox()
        for mode, text in theme.MODES.items():
            self.theme_combo.addItem(text, mode)
        self.theme_combo.setCurrentIndex(max(0, self.theme_combo.findData(theme.MODE)))
        self.theme_combo.currentIndexChanged.connect(
            lambda _: self.theme_change_requested.emit(self.theme_combo.currentData()))
        sl.addLayout(hbox(4, label("Theme", "small"), self.theme_combo, spacing=8))
        sl.addSpacing(4)
        sl.addWidget(label(f"Version {__version__} · offline · no tracking", "small"))

        self.stack = QStackedWidget()
        self.stack.setObjectName("content")
        self.welcome = WelcomePage(self)
        self.stack.addWidget(self.welcome)

        # task bar
        self.task_bar = QFrame()
        self.task_bar.setObjectName("taskBar")
        self.task_title = label("", "h2")
        self.task_msg = label("", "muted")
        self.task_msg.setMinimumWidth(80)
        self.task_pct = label("", "h2")
        self.task_eta = label("", "small")
        self.task_progress = QProgressBar()
        self.task_progress.setTextVisible(False)
        self.task_progress.setFixedHeight(6)
        self.cancel_btn = button("Cancel", on_click=self._cancel, tip="Esc")
        tb = vbox(hbox(self.task_title, self.task_msg, None, self.task_eta, 10, self.task_pct, 10, self.cancel_btn),
                  self.task_progress, spacing=6, margins=(28, 10, 28, 12))
        self.task_bar.setLayout(tb)
        self.task_bar.hide()

        right = QWidget()
        right.setObjectName("content")
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)
        rl.addWidget(self.stack, 1)
        rl.addWidget(self.task_bar)
        root = QWidget()
        lay = QHBoxLayout(root)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.addWidget(side)
        lay.addWidget(right, 1)
        self.setCentralWidget(root)
        self.toast = Toast(root)

    def _shortcuts(self) -> None:
        for i, key in enumerate(NAV_KEYS[:10]):
            QShortcut(QKeySequence(f"Ctrl+{(i + 1) % 10}"), self, activated=lambda k=key: self.go(k))
        QShortcut(QKeySequence("F5"), self, activated=self.index_library)
        QShortcut(QKeySequence("Ctrl+O"), self, activated=self.choose_library)
        QShortcut(QKeySequence("Ctrl+Z"), self, activated=self.undo_last)
        QShortcut(QKeySequence("Escape"), self, activated=lambda: self.runner.busy and self._cancel())

    def resizeEvent(self, e) -> None:
        super().resizeEvent(e)
        if self.toast.isVisible():
            self.toast.reposition()

    # ---------------------------------------------------------------------------- navigation
    def page(self, key: str):
        """The page for ``key``, created on first use (keeps start-up fast)."""
        if key not in self.pages and key in self.page_classes:
            p = self.page_classes[key](self.ctx)
            self.pages[key] = p
            self.stack.addWidget(p)
        return self.pages.get(key)

    def go(self, key: str) -> None:
        if self.ctx.library is None or key not in self.page_classes:
            return
        self.stack.setCurrentWidget(self.page(key))
        self.nav_buttons[key].setChecked(True)
        self.current_key = key
        self.settings.setValue("last_page", key)

    def _show_library_ui(self, has_lib: bool) -> None:
        self.nav_container.setEnabled(has_lib)
        if not has_lib:
            self.welcome.set_recent(self.settings.value("recent", [], list) or [])
            self.stack.setCurrentWidget(self.welcome)
            for b in self.nav_buttons.values():
                b.setChecked(False)

    def _update_badges(self, counts: dict) -> None:
        for key, badge in self.nav_badges.items():
            n = counts.get(key)
            badge.setVisible(bool(n))
            badge.setText(f"{n:,}" if n else "")

    # ---------------------------------------------------------------------------- drag & drop
    def dragEnterEvent(self, e) -> None:
        urls = e.mimeData().urls() if e.mimeData().hasUrls() else []
        if len(urls) == 1 and urls[0].isLocalFile() and Path(urls[0].toLocalFile()).is_dir() and not self.runner.busy:
            e.acceptProposedAction()

    def dropEvent(self, e) -> None:
        self.open_library(e.mimeData().urls()[0].toLocalFile())

    # ---------------------------------------------------------------------------- library
    def choose_library(self) -> None:
        if self.runner.busy:
            return
        start = str(self.ctx.library.root) if self.ctx.library else str(Path.home() / "Pictures")
        path = QFileDialog.getExistingDirectory(self, "Choose the folder that holds your photos", start)
        if path:
            self.open_library(path)

    def open_library(self, path: str, page: str = "overview") -> None:
        if self.runner.busy:
            return
        try:
            lib = Library(path)
        except LibraryInUse:
            MessageDialog(self, "This library is already open",
                          "Another Memoria window is using this library. Close it first, so two windows can "
                          "never change the same files at the same time.").exec()
            return
        except LibraryTooNew as e:
            MessageDialog(self, "Please update Memoria", str(e)).exec()
            return
        except Exception as e:
            MessageDialog(self, "Can't open this folder", str(e)).exec()
            return
        fixed = actions.reconcile(lib)
        self.ctx.set_library(lib)
        parent = str(lib.root.parent)
        if len(parent) > 34:
            parent = parent[:12] + "…" + parent[-20:]
        self.lib_label.setText(f"<b style='color:{theme.TEXT}'>{lib.root.name or lib.root}</b><br>{parent}")
        self.lib_label.setToolTip(str(lib.root))
        self.setWindowTitle(f"{lib.root.name or lib.root} — Memoria")
        recent = [str(lib.root)] + [p for p in (self.settings.value("recent", [], list) or []) if p != str(lib.root)]
        self.settings.setValue("recent", recent[:8])
        self.settings.setValue("library", str(lib.root))
        self._show_library_ui(True)
        self.go(page if page in self.page_classes else "overview")
        if fixed:
            self.toast.show_message(f"Memoria was interrupted last time. {fmt_n(fixed, 'unfinished change')} "
                                    "were checked and recorded in History, where you can undo them.")
        self.index_library()

    def index_library(self) -> None:
        lib = self.ctx.library
        if lib is None or self.runner.busy:
            return

        def done(res):
            s, a = res
            self.ctx.library_modified.emit()
            bits = []
            if s.added:
                bits.append(f"{s.added:,} new")
            if s.changed:
                bits.append(f"{s.changed:,} changed")
            if s.removed:
                bits.append(f"{s.removed:,} no longer there")
            if s.unreadable_folders:
                bits.append(f"{fmt_n(s.unreadable_folders, 'folder')} couldn't be read (kept as they were)")
            if bits:
                self.toast.show_message("Library updated: " + ", ".join(bits) + ".", seconds=6)

        self.runner.run("Reading your library", lambda prog: scanner.index(lib, prog), done,
                        on_cancel=self.ctx.library_modified.emit)

    def run_checkup(self) -> None:
        """Run every finder in one read-only pass; pages and sidebar badges use the results."""
        lib = self.ctx.library
        if lib is None or self.runner.busy:
            return
        from ..engine import checkup

        def done(c):
            self.ctx.store_results(c.results)
            self.ctx.library_modified.emit()
            self.ctx.set_badges({"duplicates": c.counts.get("duplicates", 0),
                                 "similar": c.counts.get("similar", 0) + c.counts.get("similar_videos", 0),
                                 "tidy": c.counts.get("tidy", 0), "organize": c.counts.get("organize", 0)})
            groups = len(c.results.get("similar", [])) + len(c.results.get("similar_videos", []))
            parts = [fmt_n(c.counts.get("duplicates", 0), "extra copy", "extra copies"),
                     fmt_n(groups, "similar group"), fmt_n(c.counts.get("blurry", 0), "blurry photo"),
                     f"{fmt_n(c.counts.get('tidy', 0), 'item')} to tidy"]
            self.toast.show_message("Check-up complete: " + ", ".join(parts) + ". Nothing was changed.", seconds=12)

        self.runner.run("Checking everything", lambda prog: checkup.run(lib, prog), done)

    def open_sample(self) -> None:
        if self.runner.busy:
            return
        dest = _sample_dir()

        def work(prog):
            from ..samplelib import build
            prog.update(0, 0, "Preparing…")
            if dest.exists():
                shutil.rmtree(dest)
            try:
                build(dest, progress=lambda d, t, m: prog.update(d, t, m))
            except TypeError:  # generator without progress support
                build(dest)
            return str(dest)

        self.runner.run("Creating the sample library", work, lambda p: self.open_library(p))

    def restore_last(self) -> None:
        last = self.settings.value("library", "")
        if last and Path(last).is_dir():
            self.open_library(last, self.settings.value("last_page", "overview") or "overview")

    # ---------------------------------------------------------------------------- undo
    def undo_last(self) -> None:
        lib = self.ctx.library
        if lib is None or self.runner.busy:
            return
        last = next((b for b in actions.batches(lib) if b["status"] in ("applied", "partial")), None)
        if last is None:
            self.toast.show_message("There is nothing to undo.", seconds=4)
            return
        dlg = ConfirmDialog(self, "Undo the last change?",
                            f"“{last['title']}” from {fmt_date(last['created_at'], True)} will be reversed "
                            f"({fmt_n(last['files'], 'file')}).",
                            ["Files go back to where they were. Nothing is overwritten."], "Undo")
        if dlg.exec():
            self.undo_batch(last["id"])

    def undo_batch(self, batch_id: str) -> None:
        lib = self.ctx.library
        if lib is None:
            return

        def work(prog):
            res = actions.undo(lib, batch_id, prog.step(0, 2, "Restoring files"))
            scanner.index(lib, prog.step(1, 2, "Updating the catalogue"))
            return res

        def done(res):
            self.ctx.library_modified.emit()
            msg = f"Undone: {fmt_n(res.done, 'change')} reversed."
            if res.failed:
                MessageDialog(self, "Some changes could not be undone", "Those files were left where they are.",
                              "\n".join(res.messages)).exec()
            elif res.messages:
                msg += " " + res.messages[0]
            self.toast.show_message(msg)

        self.runner.run("Undoing", work, done)

    # ---------------------------------------------------------------------------- task bar
    def _task_started(self, title: str) -> None:
        self._task_started_at = time.monotonic()
        self.task_title.setText(title)
        self.task_msg.setText("Starting…")
        self.task_pct.setText("")
        self.task_eta.setText("")
        self.task_progress.setRange(0, 0)
        self.cancel_btn.setEnabled(True)
        self.cancel_btn.setText("Cancel")
        self.task_bar.show()

    def _task_progress(self, done: int, total: int, msg: str) -> None:
        elapsed = time.monotonic() - self._task_started_at
        if total > 0:
            frac = min(1.0, done / total)
            self.task_progress.setRange(0, 1000)
            self.task_progress.setValue(int(1000 * frac))
            self.task_pct.setText(f"{frac:.0%}")
            if 0.03 < frac < 0.995 and elapsed > 2:
                self.task_eta.setText(f"{_fmt_secs(elapsed)} elapsed · about {_fmt_secs(elapsed * (1 - frac) / frac)} left")
            else:
                self.task_eta.setText(f"{_fmt_secs(elapsed)} elapsed" if elapsed > 2 else "")
        else:
            self.task_progress.setRange(0, 0)
            self.task_pct.setText("")
            self.task_eta.setText(f"{_fmt_secs(elapsed)} elapsed" if elapsed > 2 else "")
        self.task_msg.setText(msg)

    def _task_finished(self, outcome: str) -> None:
        self.task_bar.hide()
        if outcome == "cancelled":
            self.toast.show_message("Stopped. Anything already done is recorded in History.", seconds=6)

    def _task_error(self, title: str, msg: str, details: str) -> None:
        MessageDialog(self, f"{title} didn't finish", msg + "\n\nNo files were left half-changed: every "
                      "completed step is recorded in History.", details).exec()

    def _cancel(self) -> None:
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setText("Stopping…")
        self.runner.cancel()

    def closeEvent(self, e) -> None:
        if self.runner.busy:
            self.runner.cancel()
            self.runner.wait()
        self.settings.setValue("geometry", self.saveGeometry())
        for p in self.pages.values():
            stop = getattr(p, "shutdown", None)
            if callable(stop):
                stop()
        if self.ctx.library:
            self.ctx.library.close()
            self.ctx.library = None
        super().closeEvent(e)
