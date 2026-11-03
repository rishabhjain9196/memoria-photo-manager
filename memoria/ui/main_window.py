"""Main window: sidebar navigation, page stack, task bar, toast, library lifecycle."""
from __future__ import annotations

import os
import shutil
from pathlib import Path

from PySide6.QtCore import QSettings, Qt, QTimer
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (QButtonGroup, QFileDialog, QFrame, QHBoxLayout, QLabel, QMainWindow,
                               QProgressBar, QPushButton, QStackedWidget, QVBoxLayout, QWidget)

from .. import __version__
from ..engine import actions, scanner
from ..engine.db import Library
from . import theme
from .tasks import TaskRunner
from .widgets import (AppContext, Banner, MessageDialog, Toast, button, fmt_n, glyph_label, hbox, icon_family,
                      label, vbox)

NAV = [
    ("LIBRARY", [("overview", "Overview", "\uE80F"), ("photos", "Photos & videos", "\uE91B")]),
    ("CLEAN UP", [("duplicates", "Duplicates", "\uE8C8"), ("similar", "Similar & best shots", "\uE734"),
                  ("tidy", "Tidy up", "\uE74D")]),
    ("ORGANISE", [("organize", "Organise by date", "\uE8B7")]),
    ("CREATE", [("story", "Story maker", "\uE786"), ("video", "Video compressor", "\uE714")]),
    ("PROTECT", [("health", "Health check", "\uEA18"), ("compare", "Compare & sync", "\uE895"),
                 ("history", "History & recovery", "\uE81C")]),
]


def _sample_dir() -> Path:
    base = os.environ.get("LOCALAPPDATA") or str(Path.home())
    return Path(base) / "Memoria" / "Sample Library"


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
        self.recent = QVBoxLayout()
        card = QFrame()
        card.setObjectName("card")
        inner = vbox(title, sub, 8, points, 8, hbox(choose, sample, None), 8, self.recent, spacing=10,
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
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Memoria")
        self.resize(1360, 860)
        self.setMinimumSize(1100, 700)
        self.settings = QSettings("Memoria", "Memoria")
        self.runner = TaskRunner(self)
        self.ctx = AppContext(self.runner)
        self.pages: dict[str, QWidget] = {}
        self.nav_buttons: dict[str, QPushButton] = {}
        self._build()
        self.runner.started.connect(self._task_started)
        self.runner.progressed.connect(self._task_progress)
        self.runner.finished.connect(self._task_finished)
        self.runner.error.connect(self._task_error)
        self.ctx.toast_requested.connect(self.toast.show_message)
        self.ctx.navigate.connect(self.go)
        self.toast.undo_clicked.connect(self.undo_batch)
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
            from PySide6.QtGui import QPixmap
            logo.setPixmap(QPixmap(str(logo_path)).scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio,
                                                          Qt.TransformationMode.SmoothTransformation))
        sl.addLayout(hbox(8, logo, label("Memoria", "appTitle"), None, spacing=8))
        self.lib_label = label("No library open", "libraryLabel", wrap=True)
        self.lib_label.setContentsMargins(14, 4, 8, 0)
        sl.addWidget(self.lib_label)
        change = button("Change library…", "link", self.choose_library)
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
                text = text.replace("&", "&&")
                b = QPushButton(f"  {text}")
                b.setObjectName("nav")
                b.setCheckable(True)
                b.setCursor(Qt.CursorShape.PointingHandCursor)
                if fam:
                    lay = QHBoxLayout(b)
                    lay.setContentsMargins(10, 0, 0, 0)
                    g = glyph_label(glyph, 15, theme.MUTED)
                    g.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
                    lay.addWidget(g)
                    lay.addStretch(1)
                    b.setText(f"         {text}")
                b.clicked.connect(lambda _=False, k=key: self.go(k))
                group.addButton(b)
                self.nav_buttons[key] = b
                nl.addWidget(b)
        sl.addWidget(self.nav_container)
        sl.addStretch(1)
        sl.addWidget(label(f"Version {__version__} · offline · no tracking", "small"))

        self.stack = QStackedWidget()
        self.stack.setObjectName("content")
        self.welcome = WelcomePage(self)
        self.stack.addWidget(self.welcome)
        from .pages import (compare, duplicates, health, history, organize, overview, photos, similar,
                            tidy)
        page_classes = {"overview": overview.OverviewPage, "photos": photos.PhotosPage,
                        "duplicates": duplicates.DuplicatesPage, "similar": similar.SimilarPage,
                        "tidy": tidy.TidyPage, "organize": organize.OrganizePage,
                        "health": health.HealthPage, "compare": compare.ComparePage,
                        "history": history.HistoryPage}
        try:
            from .pages.story import StoryPage
            page_classes["story"] = StoryPage
        except ImportError:
            pass
        try:
            from .pages.video import VideoPage
            page_classes["video"] = VideoPage
        except ImportError:
            pass
        for key, cls in page_classes.items():
            page = cls(self.ctx)
            self.pages[key] = page
            self.stack.addWidget(page)
        for key, b in self.nav_buttons.items():
            b.setVisible(key in self.pages)

        # task bar
        self.task_bar = QFrame()
        self.task_bar.setObjectName("taskBar")
        self.task_title = label("", "h2")
        self.task_msg = label("", "muted")
        self.task_progress = QProgressBar()
        self.task_progress.setTextVisible(False)
        self.task_progress.setFixedHeight(6)
        self.cancel_btn = button("Cancel", on_click=self._cancel)
        tb = vbox(hbox(self.task_title, self.task_msg, None, self.cancel_btn), self.task_progress, spacing=6,
                  margins=(28, 10, 28, 12))
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

    def resizeEvent(self, e) -> None:
        super().resizeEvent(e)
        if self.toast.isVisible():
            self.toast.reposition()

    # ---------------------------------------------------------------------------- navigation
    def go(self, key: str) -> None:
        if self.ctx.library is None or key not in self.pages:
            return
        self.stack.setCurrentWidget(self.pages[key])
        self.nav_buttons[key].setChecked(True)
        self.settings.setValue("last_page", key)

    def _show_library_ui(self, has_lib: bool) -> None:
        self.nav_container.setEnabled(has_lib)
        if not has_lib:
            self.welcome.set_recent(self.settings.value("recent", [], list) or [])
            self.stack.setCurrentWidget(self.welcome)
            for b in self.nav_buttons.values():
                b.setChecked(False)

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
        recent = [str(lib.root)] + [p for p in (self.settings.value("recent", [], list) or []) if p != str(lib.root)]
        self.settings.setValue("recent", recent[:8])
        self.settings.setValue("library", str(lib.root))
        self._show_library_ui(True)
        self.go(page)
        if fixed:
            self.toast.show_message(f"Memoria was interrupted last time. {fmt_n(fixed, 'unfinished change')} "
                                    "were checked and recorded in History, where you can undo them.")
        self.index_library()

    def index_library(self) -> None:
        lib = self.ctx.library
        if lib is None:
            return

        def work(prog):
            return scanner.index(lib, prog)

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
            if bits:
                self.toast.show_message("Library updated: " + ", ".join(bits) + ".", seconds=6)

        self.runner.run("Reading your library", work, done, on_cancel=self.ctx.library_modified.emit)

    def open_sample(self) -> None:
        if self.runner.busy:
            return
        dest = _sample_dir()

        def work(prog):
            from ..samplelib import build
            prog.update(0, 0, "Generating realistic sample photos, duplicates, bursts and videos…")
            if dest.exists():
                shutil.rmtree(dest)
            build(dest)
            return str(dest)

        self.runner.run("Creating the sample library", work, lambda p: self.open_library(p))

    def restore_last(self) -> None:
        last = self.settings.value("library", "")
        if last and Path(last).is_dir():
            self.open_library(last, self.settings.value("last_page", "overview") or "overview")

    # ---------------------------------------------------------------------------- undo
    def undo_batch(self, batch_id: str) -> None:
        lib = self.ctx.library
        if lib is None:
            return

        def work(prog):
            res = actions.undo(lib, batch_id, prog)
            scanner.index(lib, prog)
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
        self.task_title.setText(title)
        self.task_msg.setText("Starting…")
        self.task_progress.setRange(0, 0)
        self.cancel_btn.setEnabled(True)
        self.cancel_btn.setText("Cancel")
        self.task_bar.show()
        self.nav_container.setEnabled(True)

    def _task_progress(self, done: int, total: int, msg: str) -> None:
        if total > 0:
            self.task_progress.setRange(0, 1000)
            self.task_progress.setValue(int(1000 * min(done, total) / total))
        else:
            self.task_progress.setRange(0, 0)
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
        if self.ctx.library:
            self.ctx.library.close()
        super().closeEvent(e)
