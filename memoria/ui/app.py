"""Application entry point."""
from __future__ import annotations

import os
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv if argv is None else argv
    if os.name == "nt":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Memoria.PhotoManager")
        except Exception:
            pass
    from PySide6.QtCore import QSettings, QTimer
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import QApplication

    from . import theme
    from .main_window import MainWindow

    app = QApplication(argv)
    app.setApplicationName("Memoria")
    app.setOrganizationName("Memoria")
    app.setStyle("Fusion")
    icon = Path(__file__).resolve().parent / "assets" / "memoria.ico"
    if icon.exists():
        app.setWindowIcon(QIcon(str(icon)))
    settings = theme.settings()
    state: dict = {"win": None}

    def apply_theme(mode: str) -> None:
        theme.use(mode)
        app.setPalette(theme.qpalette())
        app.setStyleSheet(theme.QSS)

    def build() -> MainWindow:
        win = MainWindow()
        win.theme_change_requested.connect(change_theme)
        state["win"] = win
        return win

    def change_theme(mode: str) -> None:
        old: MainWindow = state["win"]
        if old is None or old.runner.busy:
            return
        settings.setValue("theme", mode)
        lib = str(old.ctx.library.root) if old.ctx.library else None
        page = old.current_key or "overview"
        geometry = old.saveGeometry()
        apply_theme(mode)
        new = build()
        new.restoreGeometry(geometry)
        new.show()
        old.close()
        old.deleteLater()
        if lib:
            QTimer.singleShot(0, lambda: new.open_library(lib, page))

    def system_scheme_changed(*_):
        if theme.MODE == "system" and state["win"] is not None:
            change_theme("system")

    apply_theme(settings.value("theme", "system") or "system")
    try:
        app.styleHints().colorSchemeChanged.connect(system_scheme_changed)
    except Exception:
        pass
    win = build()
    win.show()
    args = [a for a in argv[1:] if not a.startswith("-")]
    if args and os.path.isdir(args[0]):
        win.open_library(args[0])
    else:
        win.restore_last()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
