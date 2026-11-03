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
os.environ.setdefault("MEMORIA_PROFILE", "Memoria-Tools")  # never touch the user's real settings
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
    theme.use("light")
    app.setPalette(theme.qpalette())
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
    if interactive_flows:
        win.run_checkup()          # read-only "Check everything" → sidebar badges + cached results
        idle()
    order = ["overview", "photos", "duplicates", "similar", "tidy", "organize", "editor", "story", "video", "health",
             "compare", "history"]
    for i, key in enumerate(order, 1):
        if key not in win.page_classes:
            continue
        win.go(key)
        pump()
        idle()
        page = win.page(key)
        if interactive_flows:
            if key == "photos":
                page.grid.setCurrentIndex(page.grid.model().index(3, 0))
                pump()
                items = [it for it in page.grid.items() if it.get("kind") == "image"]
                v = widgets.Viewer(page, win.ctx, items, 2)
                v.resize(1200, 800)
                v.show()
                pump(0.6)
                shot(v, "photos-viewer")
                v.close()
                sel = page.grid.selectionModel()
                from PySide6.QtCore import QItemSelectionModel
                for r in (3, 4, 5):
                    sel.select(page.grid.model().index(r, 0), QItemSelectionModel.SelectionFlag.Select)
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
                idle()
            elif key == "editor":
                ids = [r["id"] for r in page.lib.files("kind='image' AND error IS NULL AND rel_path LIKE 'DCIM%'",
                                                       order="rel_path")][:2]
                vids = [r["id"] for r in page.lib.files("kind='video' AND error IS NULL", order="rel_path")][:2]
                win.ctx.edit_selection[:] = ids + vids
                page._take_selection()
                page.files.setCurrentRow(0)
                pump(1.5)
                page.p_sliders["brightness"].s.setValue(25)
                page.p_sliders["saturation"].s.setValue(30)
                page.p_aspect.setCurrentIndex(page.p_aspect.findData("4:5"))
                pump(1.5)
                shot(name=f"{i:02d}-{key}-crop")
                page._toggle_crop()          # Done → show the cropped result
                pump(1.5)
                shot(name=f"{i:02d}-{key}-photo")
                page.save()
                idle()
                page.files.setCurrentRow(2)  # first video
                pump(2.5)
                page.timeline.setValue(600)
                page.v_sliders["contrast"].s.setValue(20)
                pump(2.5)
                page._set_trim("end")
                pump(1.0)
                shot(name=f"{i:02d}-{key}-video")
                page.save()
                idle()
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
            for t in range(1, page.tabs.count()):
                page.tabs.setCurrentIndex(t)
                pump()
                if page.videos is not None and page.tabs.currentWidget() is page.videos and interactive_flows:
                    page.videos.grid.setCurrentIndex(page.videos.grid.model().index(0, 0))
                    pump()
                name = "videos" if page.tabs.currentWidget() is page.videos else "blurry"
                shot(name=f"{i:02d}-{key}-{name}")
            page.tabs.setCurrentIndex(0)

    if interactive_flows:
        # Apply a real change end-to-end, then undo it from History.
        # Batch action from Photos & videos (move 3 selected items to Recovery), then Ctrl+Z.
        win.go("photos")
        pump()
        idle()
        ph = win.page("photos")
        from PySide6.QtCore import QItemSelectionModel
        ph.grid.clearSelection()
        for r in (0, 1, 2):
            ph.grid.selectionModel().select(ph.grid.model().index(r, 0), QItemSelectionModel.SelectionFlag.Select)
        pump()
        ph.recycle_selected()
        idle()
        win.undo_last()
        idle()
        win.go("duplicates")
        pump()
        idle()
        page = win.page("duplicates")
        page.apply()
        idle()
        shot(name="20-after-apply-toast", keep_toast=True)
        win.go("history")
        pump()
        shot(name="21-history-after-apply")
        hist = win.page("history")
        hist.undo()
        idle()
        shot(name="22-history-after-undo")
        win.go("overview")
        pump()
        shot(name="23-overview-final")

        # Dark theme: rebuild the window the way the app does when the theme changes.
        from memoria.ui import theme as th
        from memoria.ui.main_window import MainWindow
        win.close()
        pump()
        th.use("dark")
        app.setPalette(th.qpalette())
        app.setStyleSheet(th.QSS)
        win = MainWindow()
        win.resize(1440, 900)
        win.show()
        win.open_library(library)
        idle()
        for key in ("overview", "photos", "duplicates", "similar", "history"):
            win.go(key)
            pump()
            idle()
            pg = win.page(key)
            if key == "duplicates":
                pg.find()
                idle()
            elif key == "similar":
                pg.find()
                idle()
                pg.grid.setCurrentIndex(pg.grid.model().index(0, 0))
                pump()
            elif key == "photos":
                pg.grid.setCurrentIndex(pg.grid.model().index(3, 0))
                pump()
            shot(name=f"dark-{key}")
        th.use("light")
        app.setPalette(th.qpalette())
        app.setStyleSheet(th.QSS)

    win.close()
    pump()
    return ERRORS


if __name__ == "__main__":
    errs = run(sys.argv[1], sys.argv[2])
    print(f"{len(errs)} UI errors")
    for e in errs:
        print(e)
    sys.exit(1 if errs else 0)
