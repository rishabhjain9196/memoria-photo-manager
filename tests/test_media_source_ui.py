"""Synthetic UI responsiveness and guarded original-media reads."""
import os
import threading
import time

os.environ["QT_QPA_PLATFORM"] = "offscreen"

import pytest
from PIL import Image
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from memoria.engine.db import Library
from memoria.ui.tasks import TaskRunner
from memoria.ui.widgets import AppContext


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def spin(app, predicate, timeout=15):
    deadline = time.monotonic() + timeout
    while not predicate() and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(.005)
    app.processEvents()
    assert predicate()


@pytest.fixture
def context(tmp_path, app):
    lib = Library(tmp_path)
    ctx = AppContext(TaskRunner())
    ctx.set_library(lib)
    yield ctx
    ctx.runner.wait()
    app.processEvents()
    lib.close()


def test_similar_100k_members_keep_opt_in_and_full_group_scope(context, app, monkeypatch):
    from memoria.engine.similar import SimilarGroup
    from memoria.ui.pages.similar import SimilarPage
    rows = [{"id": i, "name": f"{i}.jpg", "rel_path": f"{i}.jpg", "folder": "",
             "kind": "other", "size": 1, "mtime": 1} for i in range(100_000)]
    groups = [SimilarGroup(rows[:99_000], 0, reasons={0: "Best pick"})]
    groups.extend(SimilarGroup(rows[i:i + 2], i, reasons={i: "Best pick"})
                  for i in range(99_000, 100_000, 2))
    page = SimilarPage(context)
    review = page.photos
    thumbs = []
    monkeypatch.setattr(context.thumbs, "get", lambda fid: thumbs.append(fid))
    try:
        review._show(groups)
        assert review.glist.count() == 200 and len(review.grid.items()) == 500
        assert not review._planned_rows() and not thumbs
        review.grid.model_.toggle(1)
        review._member_step(1)
        review.grid.model_.toggle(1)
        assert {row["id"] for row in review._planned_rows()} == {1, 501}
        review._member_step(-1)
        assert review.grid.items()[1]["checked"]
        review._group_step(1)
        review.glist.setCurrentRow(3)
        absolute = review._index()
        review.grid.setCurrentIndex(review.grid.model_.index(1))
        chosen = review.grid.items()[1]["id"]
        review._make_best()
        assert groups[absolute].best_id == chosen
        assert groups[3].best_id != chosen
        review._group_step(1)
        review._group_step(-1)
        assert review._index() == absolute
        review._mark_all(False)
        assert not review._planned_rows()
        review._mark_all(True)
        assert len(review._planned_rows()) == 100_000 - len(groups)
        assert "Across all pages" in review.summary.text()
    finally:
        page.shutdown()
        page.deleteLater()
        app.processEvents()


def test_blurry_ticks_survive_member_pages_and_bulk_choices_keep_scope(context, app, monkeypatch):
    from memoria.ui.pages.similar import SimilarPage
    page = SimilarPage(context)
    rows = [{"id": i, "name": f"{i}.jpg", "rel_path": f"{i}.jpg", "folder": "",
             "kind": "image", "size": 1, "mtime": 1, "sharpness": 5} for i in range(1001)]
    planned = []
    monkeypatch.setattr(page, "apply_actions", lambda *args, **kwargs: planned.extend(args[2]))
    try:
        page._blurry_loaded((context.library, context.generation, rows))
        assert len(page.bgrid.items()) == 500 and not page._blurry_marked
        page.bgrid.model_.toggle(1)
        page._b_step(1)
        page.bgrid.model_.toggle(1)
        assert page._blurry_marked == {1, 501}
        page._b_mark_all(True)
        assert len(page._blurry_marked) == 1001
        page.apply_blurry()
        assert len(planned) == 1001
        page.find_blurry()
        assert not page._blurry_marked and not page.b_apply.isEnabled()
        spin(app, lambda: not page.blurry_bg.running)
    finally:
        page.shutdown()
        page.deleteLater()
        app.processEvents()


def test_editor_coalesces_guarded_loads_and_rejects_late_library_results(context, app, monkeypatch):
    from memoria.engine import photoedit
    from memoria.ui.pages.editor import EditorPage
    lib = context.library
    for i in range(12):
        Image.new("RGB", (32, 24), "red").save(lib.root / f"{i}.jpg")
    gate, entered = threading.Event(), threading.Event()
    decoded, guards = [], []
    gui_thread = threading.get_ident()

    def decode(path, max_side):
        assert threading.get_ident() != gui_thread
        decoded.append(path.name)
        entered.set()
        assert gate.wait(5)
        return Image.new("RGB", (32, 24), "blue" if path.name == "11.jpg" else "red")

    def check(path):
        guards.append(threading.get_ident())

    monkeypatch.setattr(photoedit, "load", decode)
    monkeypatch.setattr(photoedit, "estimate_bytes", lambda *args, **kwargs: 123)
    monkeypatch.setattr(lib, "check_path", check)
    page = EditorPage(context)
    ticks = []
    timer = QTimer()
    timer.setInterval(5)
    timer.timeout.connect(lambda: ticks.append(1))
    try:
        timer.start()
        page.add_rows([{"path": lib.root / f"{i}.jpg", "kind": "image", "size": 100} for i in range(12)])
        spin(app, entered.is_set)
        for i in range(1, 12):
            page.files.setCurrentRow(i)
        spin(app, lambda: len(ticks) > 5)
        assert decoded == ["0.jpg"]
        gate.set()
        spin(app, lambda: not page.bg.running and not page.est.running and not page._debounce.isActive())
        assert decoded == ["0.jpg", "11.jpg"]
        assert page._base_img.getpixel((0, 0)) == (0, 0, 255)
        assert guards and all(thread != gui_thread for thread in guards)
        gate.clear()
        entered.clear()
        page.files.setCurrentRow(0)
        spin(app, entered.is_set)
        context.library_modified.emit()
        gate.set()
        spin(app, lambda: not page.bg.running)
        assert page._base_img is None
    finally:
        gate.set()
        timer.stop()
        page.shutdown()
        page.deleteLater()
        app.processEvents()


@pytest.mark.parametrize("kind", ["editor", "story", "video"])
def test_exports_guard_registered_sources_before_engine_reads(context, app, monkeypatch, kind):
    from memoria.engine import photoedit, story, videotools
    lib = context.library
    source = lib.root / "source.jpg"
    Image.new("RGB", (32, 24), "red").save(source)
    lib.db.execute("INSERT INTO files(id,rel_path,folder,name,ext,kind,size,mtime,width,height) "
                   "VALUES (1,'source.jpg','','source.jpg','.jpg','image',100,1,32,24)")
    invoked, guards, errors = [], [], []
    context.runner.error.connect(lambda *args: errors.append(args))

    def offline(path):
        guards.append(threading.get_ident())
        raise OSError("Registered source is offline <disk>")

    monkeypatch.setattr(lib, "check_path", offline)
    if kind == "editor":
        from memoria.ui.pages.editor import EditorPage
        page = EditorPage(context)
        page.add_rows([dict(lib.file(1))])
        page.edit().brightness = 10
        monkeypatch.setattr(photoedit, "save", lambda *args, **kwargs: invoked.append("saved"))
        start = page.save
    elif kind == "story":
        from memoria.ui.pages.story import StoryPage
        page = StoryPage(context)
        page.refresh()
        spin(app, lambda: not page.catalogue_bg.running)
        page.add_ids([1])
        monkeypatch.setattr(story, "export_stories", lambda *args, **kwargs: invoked.append("saved"))
        start = page._export
    else:
        from memoria.ui.pages.video import VideoPage
        page = VideoPage(context)
        page._fill([{"key": str(source).lower(), "id": 1, "path": source, "name": source.name, "tip": "",
                     "sub": "", "size": 100, "duration": 1, "width": 32, "height": 24, "external": False}])
        page._checked.add(str(source).lower())
        monkeypatch.setattr(videotools, "compress_many", lambda *args, **kwargs: invoked.append("saved"))
        start = page._compress
    try:
        start()
        spin(app, lambda: not context.runner.active)
        assert not invoked
        assert errors and "offline <disk>" in errors[0][1]
        assert guards and all(thread != threading.get_ident() for thread in guards)
    finally:
        page.shutdown()
        page.deleteLater()
        app.processEvents()


def test_story_preview_guard_is_worker_local_and_errors_visible(context, app, monkeypatch):
    from memoria.engine import story
    from memoria.ui.pages.story import StoryPage
    lib = context.library
    lib.db.execute("INSERT INTO files(id,rel_path,folder,name,ext,kind,size,mtime) "
                   "VALUES (1,'source.jpg','','source.jpg','.jpg','image',100,1)")
    reads, guards = [], []
    monkeypatch.setattr(story, "render_story", lambda *args: reads.append(1))

    def guard(path):
        guards.append(threading.get_ident())
        raise OSError("Source drive changed")

    monkeypatch.setattr(lib, "check_path", guard)
    page = StoryPage(context)
    try:
        page.refresh()
        spin(app, lambda: not page.catalogue_bg.running)
        page.add_ids([1])
        page.preview_timer.stop()
        page._render_preview()
        spin(app, lambda: not page.renderer.running)
        assert not reads and "Source drive changed" in page.preview.text()
        assert guards and all(thread != threading.get_ident() for thread in guards)
    finally:
        page.shutdown()
        page.deleteLater()
        app.processEvents()


def test_video_prober_checks_captured_library_and_closes_worker_connections(context, app, monkeypatch):
    from memoria.ui.pages.video import _Prober
    from memoria.engine import ffmpeg
    lib = context.library
    probed, failures, reads, closed = [], [], [], []
    real_close = lib.close_thread

    def guard(path):
        assert threading.get_ident() != gui
        raise OSError("Offline registered folder")

    def close():
        closed.append(threading.get_ident())
        real_close()

    gui = threading.get_ident()
    monkeypatch.setattr(lib, "check_path", guard)
    monkeypatch.setattr(lib, "close_thread", close)
    monkeypatch.setattr(ffmpeg, "probe", lambda path: reads.append(path))
    prober = _Prober()
    prober.probed.connect(lambda *args: probed.append(args))
    prober.failed.connect(lambda *args: failures.append(args))
    try:
        prober.request("key", lib.root / "source.mp4", True, library=lib)
        spin(app, lambda: bool(probed))
        assert not reads and probed[0][1] is None
        assert "Offline registered folder" in failures[0][1]
        assert closed and all(thread != gui for thread in closed)
    finally:
        prober.stop()
        prober.deleteLater()
        app.processEvents()
