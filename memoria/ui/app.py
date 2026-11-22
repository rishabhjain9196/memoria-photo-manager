"""Application entry point."""
from __future__ import annotations

import os
import sys
from pathlib import Path


def self_test(report: str) -> int:
    """Check bundled models and data inside a packaged build (used by tools/verify_build.ps1)."""
    import json
    from ..engine import faces, places
    out = {}
    try:
        sample = sorted((Path(faces.__file__).parent.parent / "sample_faces").glob("lincoln_*.jpg"))[0]
        found = faces.detect(sample)
        out["faces"] = len(found)
        out["place"] = places.nearest(34.1526, 77.5771).label
    except Exception as e:  # pragma: no cover - reported to the caller
        out["error"] = repr(e)
    Path(report).write_text(json.dumps(out), encoding="utf-8")
    return 0 if out.get("faces") == 1 and out.get("place") == "Leh, Ladakh" else 1


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv if argv is None else argv
    if len(argv) == 3 and argv[1] == "--self-test":
        return self_test(argv[2])
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
        if old is None or old.runner.busy or old.updates.pending:
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
        win.open_library(args[0], viewer="--browse" in argv)
    elif "--new-window" not in argv:
        win.restore_last()
    def startup_updates():
        from ..engine import app_updates
        from .widgets import MessageDialog
        try:
            app_updates.mark_restart_ready()
        except app_updates.UpdateError as error:
            MessageDialog(state["win"], "Update restart status could not be recorded", str(error)).exec()
        if state["win"] is not None and not state["win"]._closing:
            state["win"].updates.startup_check()
    QTimer.singleShot(0, startup_updates)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
