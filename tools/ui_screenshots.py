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
    from PySide6.QtCore import QObject, QTimer
    from PySide6.QtWidgets import QApplication, QDialog

    from memoria.ui import theme
    from memoria.ui.main_window import MainWindow
    from memoria.ui import widgets
    from memoria.ui.tasks import BackgroundCall, LatestCall

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
        end = time.monotonic() + timeout
        quiet_since = None
        while time.monotonic() < end:
            app.processEvents()
            busy = win.runner.busy or any(
                worker.running for worker in win.findChildren(QObject)
                if isinstance(worker, (BackgroundCall, LatestCall)))
            if busy:
                quiet_since = None
            elif quiet_since is None:
                quiet_since = time.monotonic()
            elif time.monotonic() - quiet_since >= .35:
                return
            time.sleep(.01)
        raise RuntimeError(f"UI work did not finish: {win.runner.title}")

    def click_task(control):
        if not control.isVisible() or not control.isEnabled():
            raise RuntimeError(f"Task button is unavailable: {control.text()}")
        control.click()
        if not win.runner.busy:
            raise RuntimeError(f"Button did not start a task: {control.text()}")
        idle()

    def insights_idle(page, timeout=30):
        end = time.time() + timeout
        while (page.bg.running or page.timer.isActive() or not page.tabs.isEnabled()) and time.time() < end:
            pump(0.05)
        if not page.tabs.isEnabled() or page.bg.running:
            raise RuntimeError(f"Insights did not finish: {page.status.text()}")
        pump()

    def shot(widget=None, name="shot", keep_toast=False):
        if not keep_toast and widget is None:
            win.toast.hide()
        if widget is None and os.environ.get("MEMORIA_SHOT_LABEL"):
            win.lib_label.setText(os.environ["MEMORIA_SHOT_LABEL"])
        (widget or win).grab().save(str(outdir / f"{name}.png"))

    if os.environ.get("MEMORIA_SHOT_LABEL"):
        win.welcome.set_recent([])
    shot(name="00-welcome")
    win.open_library(library)
    idle()
    if interactive_flows:
        win.go("overview")
        click_task(win.page("overview").check_btn)
    order = ["overview", "photos", "duplicates", "similar", "tidy", "organize", "editor", "story", "video", "health",
             "compare", "history", "people", "albums", "insights"]
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
                click_task(page.find_btn)
                page.f_grid.setCurrentIndex(page.f_grid.model().index(0, 0))
                pump(0.4)
                shot(name=f"{i:02d}-duplicates-folders")
                row = next(r for r, (k, _) in enumerate(page.entries) if k == "file")
                page.list.setCurrentRow(row)
                pump()
                page.grid.setCurrentIndex(page.grid.model().index(1, 0))
                pump()
            elif key == "similar":
                click_task(page.photos.find_btn)
                page.grid.setCurrentIndex(page.grid.model().index(0, 0))
                pump()
            elif key == "organize":
                click_task(page.preview_btn)
            elif key == "editor":
                ids = [r["id"] for r in page.lib.files("kind='image' AND error IS NULL AND rel_path LIKE 'DCIM%'",
                                                       order="rel_path")][:2]
                vids = [r["id"] for r in page.lib.files("kind='video' AND error IS NULL AND rel_path LIKE 'Camera Roll%'",
                                                        order="rel_path")][:2]
                win.ctx.edit_selection[:] = ids + vids
                page._take_selection()
                page.files.setCurrentRow(0)
                pump(1.5)
                page.p_sliders["brightness"].s.setValue(25)
                page.p_sliders["saturation"].s.setValue(30)
                page.p_aspect.setCurrentIndex(page.p_aspect.findData("4:5"))
                pump(1.5)
                shot(name=f"{i:02d}-{key}-crop")
                page.p_crop_btn.click()      # Done → show the cropped result
                pump(1.5)
                shot(name=f"{i:02d}-{key}-photo")
                click_task(page.save_btn)
                page.files.setCurrentRow(2)  # first video
                pump(2.5)
                page.timeline.setValue(600)
                page.v_sliders["contrast"].s.setValue(20)
                pump(2.5)
                page.set_end_btn.click()
                pump(1.0)
                shot(name=f"{i:02d}-{key}-video")
                click_task(page.save_btn)
            elif key == "story":
                page.output.set_path(outdir.parent / "Stories")
                if os.environ.get("MEMORIA_SHOT_LABEL"):
                    page.output.path_label.setText(r"D:\Memoria Exports\Stories")
                ids = [r["id"] for r in page.lib.files("kind='image' AND error IS NULL AND rel_path LIKE 'DCIM%'",
                                                       order="rel_path")][:4]
                page.add_ids(ids)
                page.template.setCurrentIndex(page.template.findData("grid4"))
                page.caption.setText("Weekend in the hills")
                pump(3.0)
            elif key == "video":
                page.output.set_path(outdir.parent / "Compressed videos")
                if os.environ.get("MEMORIA_SHOT_LABEL"):
                    page.output.path_label.setText(r"D:\Memoria Exports\Compressed videos")
                page._check_all(True)
                pump(2.0)
                shot(name=f"{i:02d}-{key}-selected")
                click_task(page.compress_btn)
            elif key == "health":
                click_task(page.run_btn)
            elif key == "people":
                import json
                from memoria.engine import faces as _faces
                click_task(page.find_btn)
                exp = Path(library) / "expected.json"
                want = json.loads(exp.read_text()).get("people", {}) if exp.exists() else {}
                for person in ("Abraham Lincoln", "Mark Twain"):
                    files = set(want.get(person, []))
                    for g in page.shown:
                        got = {r["rel_path"] for r in _faces.photos_of(page.lib, g.key)}
                        if not g.named and files and len(got & files) * 2 > len(got):
                            page.list.setCurrentRow(page.shown.index(g))
                            page.name_group(person)
                            break
                pump()
                unnamed = next((r for r, g in enumerate(page.shown) if not g.named), None)
                if unnamed is not None:
                    page.list.setCurrentRow(unnamed)
                    pump()
                    page.faces.item(0).setSelected(True)
                    page.like_btn.click()
                    pump(0.5)
                    shot(name=f"{i:02d}-{key}-lookalike")
                page.list.setCurrentRow(0)
                pump(0.5)
                page.grid.setCurrentIndex(page.grid.model().index(0, 0))
                pump(0.5)
            elif key == "albums":
                page.tabs.setCurrentIndex(1)
                page.mode.setCurrentIndex(0)
                click_task(page.suggest_btn)
                trip = next((r for r, s in enumerate(page.suggestions) if "–" in s.name and "·" in s.name), 0)
                page.s_list.setCurrentRow(trip)
                pump(0.5)
                shot(name=f"{i:02d}-{key}-make")
                page.save_btn.click()
                idle()
                page.tabs.setCurrentIndex(1)
                page.mode.setCurrentIndex(2)
                click_task(page.suggest_btn)
                page.save_btn.click()
                idle()
                page.tabs.setCurrentIndex(0)
                pump()
                row = next((r for r, a in enumerate(page.saved) if "–" in a["name"] and "·" in a["name"]), 0)
                page.a_list.setCurrentRow(row)
                pump(0.5)
                page.export([page.saved[row]["id"]], str(outdir.parent / "Album exports"))
                idle()
                win.undo_last()      # exported copies are removed again by History's Undo
                idle()
                win.go(key)
                pump()
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
                click_task(page.cmp_btn)
                if os.environ.get("MEMORIA_SHOT_LABEL"):
                    page.path.setText(r"E:\Photos Backup")
            elif key == "history" and os.environ.get("MEMORIA_SHOT_LABEL"):
                original_short = page._short
                page._short = lambda path, short=original_short: short(path).replace(
                    str(Path(library).parent), r"D:\Sample outputs")
                page.refresh()
            elif key == "insights":
                from memoria.engine import catalogue, geography, storage
                from memoria.ui.library_filters import FilterDialog
                from memoria.ui.storage_dialog import StorageDialog
                insights_idle(page)
                shot(name="insights-storage")
                page.tabs.setCurrentIndex(3)
                idle()
                shot(name="insights-files")
                page.tabs.setCurrentIndex(1)
                page._period("2023")
                insights_idle(page)
                shot(name="insights-timeline")
                page.tabs.setCurrentIndex(2)
                page._map_bounds(geography.INDIA)
                insights_idle(page)
                shot(name="insights-india")
                page._map_bounds(geography.WORLD)
                insights_idle(page)
                shot(name="insights-world")
                win.browse_filtered(catalogue.Filters())
                photos = win.page("photos")
                photos.sort.setCurrentIndex(photos.sort.findData("largest"))
                pump()
                shot(name="photos-largest")
                filters = FilterDialog(win, win.ctx.library, photos.filters)
                filters.show()
                pump()
                shot(filters, "library-filters")
                filters.tabs.setCurrentIndex(1)
                pump()
                shot(filters, "library-filters-video")
                filters.tabs.setCurrentIndex(2)
                pump()
                shot(filters, "library-filters-camera")
                filters.close()
                photos.kind.setCurrentIndex(photos.kind.findData("video"))
                photos.sort.setCurrentIndex(photos.sort.findData("duration_desc"))
                photos.grid.setCurrentIndex(photos.grid.model().index(0, 0))
                pump()
                shot(name="photos-video-metadata")
                photos.kind.setCurrentIndex(photos.kind.findData("media"))
                photos.sort.setCurrentIndex(photos.sort.findData("newest"))
                reset = StorageDialog(win, storage.usage(win.ctx.library))
                reset.show()
                pump()
                shot(reset, "storage-reset")
                reset.preset(True)
                pump()
                shot(reset, "storage-reset-hard")
                reset.close()
                win.go(key)
                pump()
        shot(name=f"{i:02d}-{key}")
        if key == "similar":
            for t in range(1, page.tabs.count()):
                page.tabs.setCurrentIndex(t)
                pump()
                if page.videos is not None and page.tabs.currentWidget() is page.videos and interactive_flows:
                    click_task(page.videos.find_btn)
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
        click_task(ph.b_recycle)
        win.undo_last()
        idle()
        win.go("duplicates")
        pump()
        idle()
        page = win.page("duplicates")
        click_task(page.apply_btn)
        shot(name="20-after-apply-toast", keep_toast=True)
        win.go("history")
        pump()
        shot(name="21-history-after-apply")
        hist = win.page("history")
        click_task(hist.undo_btn)
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
        for key in ("overview", "photos", "duplicates", "similar", "history", "insights"):
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
            elif key == "insights":
                from memoria.engine import geography
                pg.tabs.setCurrentIndex(2)
                pg._map_bounds(geography.WORLD)
                insights_idle(pg)
            elif key == "history" and os.environ.get("MEMORIA_SHOT_LABEL"):
                original_short = pg._short
                pg._short = lambda path, short=original_short: short(path).replace(
                    str(Path(library).parent), r"D:\Sample outputs")
                pg.refresh()
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
