"""Application entry point."""
from __future__ import annotations

import os
import sys


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv if argv is None else argv
    if os.name == "nt":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Memoria.PhotoManager")
        except Exception:
            pass
    from PySide6.QtWidgets import QApplication

    from . import theme
    from .main_window import MainWindow

    app = QApplication(argv)
    app.setApplicationName("Memoria")
    app.setOrganizationName("Memoria")
    app.setStyle("Fusion")
    app.setStyleSheet(theme.QSS)
    from pathlib import Path
    from PySide6.QtGui import QIcon
    icon = Path(__file__).resolve().parent / "assets" / "memoria.ico"
    if icon.exists():
        app.setWindowIcon(QIcon(str(icon)))
    win = MainWindow()
    win.show()
    args = [a for a in argv[1:] if not a.startswith("-")]
    if args and os.path.isdir(args[0]):
        win.open_library(args[0])
    else:
        win.restore_last()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
