"""Drive the real UI offscreen against a library and save a screenshot of every page.

    python tools/ui_screenshots.py LIBRARY_COPY OUT_DIR

Used for visual review and as an end-to-end smoke test (exits non-zero on any UI exception).
Set MEMORIA_SHOT_LABEL to replace the sidebar's library path (e.g. for documentation images).
"""
from __future__ import annotations

import os
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
if os.name == "nt":
    os.environ.setdefault("QT_QPA_FONTDIR", os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"))

ERRORS: list[str] = []


def _hook(t, v, tb):
    ERRORS.append("".join(traceback.format_exception(t, v, tb)))
    sys.__excepthook__(t, v, tb)


def run(library: str, out: str, interactive_flows: bool = True) -> list[str]:
    sys.excepthook = _hook
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication, QDialog

    from memoria.ui import theme
    from memoria.ui.main_window import MainWindow
    from memoria.ui import widgets

    app = QApplication.instance() or QApplication([])
    app.setStyle("Fusion")
    app.setStyleSheet(theme.QSS)
    outdir = Path(out)
    outdir.mkdir(parents=True, exist_ok=True)

    # Auto-accept confirmation dialogs (and tick acknowledgement boxes) during the scripted run.
    def auto_exec(self):
        if hasattr(self, "ack"):
            self.ack.setChecked(True)
        shot(self, f"dialog-{self.windowTitle()[:30]}")
        return QDialog.DialogCode.Accepted
    widgets.ConfirmDialog.exec = auto_exec
    widgets.MessageDialog.exec = lambda self: (ERRORS.append("MessageDialog: " + self.windowTitle()), 1)[1]

    win = MainWindow()
    win.resize(1440, 900)
    win.show()

    def pump(sec=0.15):
        end = time.time() + sec
        while time.time() < end:
            app.processEvents()
            time.sleep(0.01)

    def idle(timeout=300):
        end = time.time() + timeout
        pump(0.05)
        while win.runner.busy and time.time() < end:
            app.processEvents()
            time.sleep(0.02)
        pump(0.3)

    def shot(widget=None, name="shot", keep_toast=False):
        if not keep_toast and widget is None:
            win.toast.hide()
        if widget is None and os.environ.get("MEMORIA_SHOT_LABEL"):
            win.lib_label.setText(os.environ["MEMORIA_SHOT_LABEL"])
        (widget or win).grab().save(str(outdir / f"{name}.png"))

    shot(name="00-welcome")
    win.open_library(library)
    idle()
    order = ["overview", "photos", "duplicates", "similar", "tidy", "organize", "story", "video", "health",
             "compare", "history"]
    for i, key in enumerate(order, 1):
        if key not in win.pages:
            continue
        win.go(key)
        pump()
        idle()
        page = win.pages[key]
        if interactive_flows:
            if key == "photos":
                page.grid.setCurrentIndex(page.grid.model().index(3, 0))
                pump()
            elif key == "duplicates":
                page.find()
                idle()
                page.grid.setCurrentIndex(page.grid.model().index(1, 0))
                pump()
            elif key == "similar":
                page.find()
                idle()
                page.grid.setCurrentIndex(page.grid.model().index(0, 0))
                pump()
            elif key == "organize":
                page.build_plan()
                pump()
            elif key == "story":
                ids = [r["id"] for r in page.lib.files("kind='image' AND error IS NULL AND rel_path LIKE 'DCIM%'",
                                                       order="rel_path")][:4]
                page.add_ids(ids)
                page.template.setCurrentIndex(page.template.findData("grid4"))
                page.caption.setText("Weekend in the hills")
                pump(3.0)
            elif key == "video":
                page._check_all(True)
                pump(2.0)
                shot(name=f"{i:02d}-{key}-selected")
                page._compress()
                idle()
            elif key == "health":
                page.check()
                idle()
            elif key == "compare":
                other = Path(library).parent / "Other Backup"
                if not other.exists():
                    import shutil
                    rows = page.lib.files("kind='image' AND error IS NULL")[:20]
                    for r in rows:
                        d = other / "Phone" / r["name"]
                        d.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(page.lib.abspath(r["rel_path"]), d)
                page.path.setText(str(other))
                page.run_compare()
                idle()
        shot(name=f"{i:02d}-{key}")
        if key == "similar":
            page.tabs.setCurrentIndex(1)
            pump()
            shot(name=f"{i:02d}-{key}-blurry")
            page.tabs.setCurrentIndex(0)

    if interactive_flows:
        # Apply a real change end-to-end, then undo it from History.
        win.go("duplicates")
        pump()
        idle()
        page = win.pages["duplicates"]
        page.apply()
        idle()
        shot(name="20-after-apply-toast", keep_toast=True)
        win.go("history")
        pump()
        shot(name="21-history-after-apply")
        hist = win.pages["history"]
        hist.undo()
        idle()
        shot(name="22-history-after-undo")
        win.go("overview")
        pump()
        shot(name="23-overview-final")

    win.close()
    pump()
    return ERRORS


if __name__ == "__main__":
    errs = run(sys.argv[1], sys.argv[2])
    print(f"{len(errs)} UI errors")
    for e in errs:
        print(e)
    sys.exit(1 if errs else 0)
