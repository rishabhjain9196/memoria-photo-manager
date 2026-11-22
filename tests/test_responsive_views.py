"""Synthetic large catalogues and deliberately delayed reads; no personal media."""
import io
import os
import threading
import time
from datetime import datetime

os.environ["QT_QPA_PLATFORM"] = "offscreen"

import pytest
from PIL import Image
from PySide6.QtCore import QCoreApplication, QEvent, QTimer, Qt
from PySide6.QtWidgets import QApplication

from memoria.engine.db import Library
from memoria.ui.tasks import LatestCall, TaskRunner
from memoria.ui.widgets import AppContext, Preview, Viewer


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def spin(app, predicate, timeout=20):
    deadline = time.monotonic() + timeout
    while not predicate() and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(.005)
    app.processEvents()
    assert predicate(), "Background request did not settle"


@pytest.fixture
def context(tmp_path, app):
    lib = Library(tmp_path)
    ctx = AppContext(TaskRunner())
    ctx.set_library(lib)
    yield ctx
    ctx.runner.wait()
    app.processEvents()
    lib.close()


@pytest.fixture(scope="module")
def large_library(tmp_path_factory, app):
    lib = Library(tmp_path_factory.mktemp("responsive-catalogue"))
    with lib.transaction() as db:
        db.executemany(
            "INSERT INTO files(id,rel_path,folder,name,ext,kind,size,mtime,taken_at,date_source) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            ((i, f"source\\{i:06}.jpg", "source", f"{i:06}.jpg", ".jpg",
              "image" if i <= 85_000 else "other", i, 1, "2024-01-02 12:00:00", "exif")
             for i in range(1, 100_001)))
        db.execute("INSERT INTO people VALUES (1,'Many photos','2024-01-01')")
        db.executemany(
            "INSERT INTO faces(id,file_id,x,y,w,h,score,emb,person_id,cluster) VALUES (?,?,0,0,1,1,1,?,?,?)",
            ((i, i, b"", 1 if i <= 85_000 else None, None if i <= 85_000 else i)
             for i in range(1, 100_001)))
    yield lib
    lib.close()


def test_preview_coalesces_decodes_and_keeps_gui_alive(context, app, monkeypatch):
    from memoria.engine import media
    ctx, lib = context, context.library
    gate, started = threading.Event(), threading.Event()
    calls, check_threads, close_threads = [], [], []
    gui_thread = threading.get_ident()
    real_close = lib.close_thread

    def decode(path, edge):
        calls.append(path.name)
        assert threading.get_ident() != gui_thread
        started.set()
        assert gate.wait(5)
        return Image.new("RGB", (20, 20), "blue" if path.name == "49.jpg" else "red")

    def close():
        close_threads.append(threading.get_ident())
        real_close()

    monkeypatch.setattr(media, "load_for_display", decode)
    monkeypatch.setattr(lib, "check_path", lambda path: check_threads.append(threading.get_ident()))
    monkeypatch.setattr(lib, "close_thread", close)
    preview = Preview(ctx)
    ticks = []
    timer = QTimer()
    timer.setInterval(5)
    timer.timeout.connect(lambda: ticks.append(1))
    timer.start()
    try:
        preview.show_row({"rel_path": "0.jpg", "kind": "image"})
        spin(app, started.is_set)
        for i in range(1, 50):
            preview.show_row({"rel_path": f"{i}.jpg", "kind": "image"})
        spin(app, lambda: len(ticks) >= 5)
        assert calls == ["0.jpg"]
        assert "Loading" in preview.image.text()
        gate.set()
        spin(app, lambda: not preview.loader.running)
        assert calls == ["0.jpg", "49.jpg"]
        assert preview.image.pixmap().toImage().pixelColor(0, 0).blue() == 255
        assert check_threads and all(thread != gui_thread for thread in check_threads)
        assert len(close_threads) == 2 and all(thread != gui_thread for thread in close_threads)
    finally:
        gate.set()
        timer.stop()
        preview.shutdown()
        preview.deleteLater()
        app.processEvents()


def test_preview_error_cached_fallback_and_offline_guard(context, app, monkeypatch):
    from memoria.engine import media
    lib = context.library
    encoded = io.BytesIO()
    Image.new("RGB", (20, 20), "green").save(encoded, "JPEG")
    lib.thumbs_db.execute("INSERT INTO thumbs VALUES(1,?)", (encoded.getvalue(),))
    attempts = []

    def decode(path, edge):
        attempts.append(path)
        raise RuntimeError("decoder <HEVC> not available")

    monkeypatch.setattr(media, "load_for_display", decode)
    preview = Preview(context)
    row = {"id": 1, "rel_path": "missing.jpg", "kind": "image"}
    try:
        preview.show_row(row)
        spin(app, lambda: not preview.loader.running)
        assert not preview.image.pixmap().isNull()
        assert "decoder &lt;HEVC&gt; not available" in preview.facts.text()
        assert "before assuming damage" in preview.facts.text()
        attempts.clear()

        def offline(path):
            raise OSError("Registered drive is offline <disk>")

        monkeypatch.setattr(lib, "check_path", offline)
        preview.show_row(row)
        spin(app, lambda: not preview.loader.running)
        assert not attempts, "Offline originals must never be decoded from another drive"
        assert "offline &lt;disk&gt;" in preview.facts.text()
        assert not preview.image.pixmap().isNull()
        opened = []
        monkeypatch.setattr("memoria.ui.widgets.open_path", opened.append)
        preview._open()
        spin(app, lambda: not preview.access.running)
        assert not opened and "offline &lt;disk&gt;" in preview.facts.text()
    finally:
        preview.shutdown()
        preview.deleteLater()
        app.processEvents()


def test_held_index_preview_preserves_row_but_rejects_old_decode(context, app, monkeypatch):
    from PySide6.QtGui import QImage
    gate, entered = threading.Event(), threading.Event()
    reads = []

    def decode(lib, row, edge):
        index = len(reads)
        reads.append(index)
        entered.set()
        assert gate.wait(5)
        image = QImage(20, 20, QImage.Format.Format_RGB32)
        image.fill(Qt.GlobalColor.red if index == 0 else Qt.GlobalColor.blue)
        return image, ""

    monkeypatch.setattr("memoria.ui.widgets.read_image", decode)
    preview = Preview(context, hold_on_index_update=True)
    row = {"rel_path": "held.jpg", "kind": "image"}
    try:
        preview.show_row(row)
        spin(app, entered.is_set)
        old_request = preview._request
        context.index_update = True
        context.library_modified.emit()
        context.index_update = False
        assert preview.row is row and preview._request != old_request
        gate.set()
        spin(app, lambda: not preview.loader.running)
        assert reads == [0, 1]
        assert preview.image.pixmap().toImage().pixelColor(0, 0).blue() == 255
        held_image = preview.image.pixmap().cacheKey()
        context.index_update = True
        context.library_modified.emit()
        context.index_update = False
        assert preview.row is row and preview.image.pixmap().cacheKey() == held_image
        assert reads == [0, 1]
        context.library_modified.emit()
        assert preview.row is None
        preview.show_row(row)
        context.index_update = True
        context.set_library(None)
        assert preview.row is None
    finally:
        context.index_update = False
        gate.set()
        preview.shutdown()
        preview.deleteLater()
        app.processEvents()


def test_viewer_navigation_rejects_late_results_after_close_and_generation(context, app, monkeypatch):
    from memoria.engine import media
    gate, started = threading.Event(), threading.Event()
    calls = []

    def decode(path, edge):
        calls.append(path.name)
        started.set()
        assert gate.wait(5)
        return Image.new("RGB", (16, 20), "red")

    monkeypatch.setattr(media, "load_for_display", decode)
    rows = [{"rel_path": f"{i}.jpg", "kind": "image", "name": f"{i}.jpg"} for i in range(100)]
    viewer = Viewer(None, context, rows, 0)
    try:
        spin(app, started.is_set)
        for _ in range(99):
            viewer.step(1)
        assert viewer.index == 99 and calls == ["0.jpg"]
        viewer.reject()
        gate.set()
        spin(app, lambda: not viewer.loader.running)
        assert viewer._pixmap.isNull() and calls == ["0.jpg"]
        viewer._load()
        context.library_modified.emit()
        spin(app, lambda: not viewer.loader.running)
        assert viewer._pixmap.isNull()
        assert "Library changed" in viewer.image.text()
    finally:
        gate.set()
        viewer.shutdown()
        viewer.deleteLater()
        app.processEvents()


def test_latest_read_parent_destruction_drops_pending_work(app):
    from PySide6.QtCore import QObject
    parent = QObject()
    call = LatestCall(parent)
    gate, started = threading.Event(), threading.Event()
    invoked = []

    def first():
        started.set()
        gate.wait(5)
        return 1

    try:
        call.call(first)
        spin(app, started.is_set)
        call.call(lambda: invoked.append("must not run"))
        parent.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        assert call._pending is None
    finally:
        gate.set()
        from memoria.ui.tasks import _read_threads
        spin(app, lambda: not _read_threads)
    assert not invoked


def test_people_queries_are_paged_at_100k_and_delayed_io_is_responsive(large_library, app, monkeypatch):
    from memoria.ui import people_queries as queries
    from memoria.ui.pages.people import PeoplePage
    ctx = AppContext(TaskRunner())
    ctx.set_library(large_library)
    page = PeoplePage(ctx)
    page.min_photos = 1
    gui_thread = threading.get_ident()
    original = queries.group_page
    requests = []

    def delayed(*args):
        requests.append(threading.get_ident())
        time.sleep(.15)
        return original(*args)

    monkeypatch.setattr(queries, "group_page", delayed)
    ticks = []
    timer = QTimer()
    timer.setInterval(10)
    timer.timeout.connect(lambda: ticks.append(1))
    timer.start()
    try:
        begin = time.monotonic()
        page.refresh()
        assert time.monotonic() - begin < .12
        spin(app, lambda: not page.bg.running and not page.contents_bg.running)
        assert len(ticks) >= 5
        assert requests and all(thread != gui_thread for thread in requests)
        assert page.group_total == 15_001
        assert page.list.count() == queries.GROUP_PAGE
        assert len(page.grid.items()) == queries.PHOTO_PAGE
        assert page.faces.count() == queries.FACE_PAGE
        assert "85,000" in page.photo_scope.text() and "all pages" in page.photo_scope.text()
        from memoria.engine import albums
        album_ids = []
        monkeypatch.setattr(albums, "create", lambda lib, name, ids, kind: album_ids.extend(ids) or 42)
        page.make_album()
        spin(app, lambda: not ctx.runner.active)
        assert len(album_ids) == 85_000, "Make album must retain all-person scope, not just the visible page"
        first = page.grid.items()[0]["id"]
        page._content_step("photo", 1)
        spin(app, lambda: not page.contents_bg.running)
        assert len(page.grid.items()) == queries.PHOTO_PAGE
        assert page.grid.items()[0]["id"] != first
        page.search.setText("does not exist")
        page.search.setText("Many photos")
        spin(app, lambda: not page.search_timer.isActive() and not page.bg.running and not page.contents_bg.running)
        assert page.list.count() == 1
        assert page.group_total == 1 and page._current().key == "p1"
    finally:
        timer.stop()
        page.shutdown()
        page.deleteLater()
        app.processEvents()


def test_100k_tidy_and_organize_keep_full_selection_with_bounded_items(large_library, app):
    from memoria.engine import organize, tidy
    from memoria.ui.pages.tidy import TidyPage
    from memoria.ui.pages.organize import OrganizePage
    ctx = AppContext(TaskRunner())
    ctx.set_library(large_library)
    rows = [dict(row) for row in large_library.db.execute("SELECT * FROM files ORDER BY id")]
    tidy_page, organize_page = TidyPage(ctx), OrganizePage(ctx)
    try:
        tidy_page._show(tidy.TidyReport({"junk": rows}))
        top = tidy_page.tree.topLevelItem(0)
        assert top.childCount() == 200
        assert tidy_page._selected_count() == 100_000
        top.child(0).setCheckState(0, Qt.CheckState.Unchecked)
        tidy_page.pages.step(1)
        assert tidy_page._selected_count() == 99_999
        assert "99,999" in tidy_page.summary.text()
        tidy_page.tree.topLevelItem(0).setCheckState(0, Qt.CheckState.Unchecked)
        assert tidy_page._selected_count() == 0
        tidy_page.tree.topLevelItem(0).setCheckState(0, Qt.CheckState.Checked)
        assert len(tidy_page._selected()["junk"]) == 100_000
        tidy_page.pages.step(-1)
        assert tidy_page.tree.topLevelItem(0).child(0).checkState(0) == Qt.CheckState.Checked
        items = [organize.OrganizeItem(row, f"2024\\{row['name']}", datetime(2024, 1, 2), "exif")
                 for row in rows]
        organize_page._show(organize.OrganizePlan(items, 5, 6, "year"))
        assert organize_page.tree.topLevelItem(0).childCount() == 200
        assert organize_page.t_move.value.text() == "100,000"
        organize_page.tree.topLevelItem(0).child(0).setCheckState(0, Qt.CheckState.Unchecked)
        organize_page.pages.step(499)
        assert len(organize_page._chosen()) == 99_999
        assert "99,999" in organize_page.summary.text() and "Across all pages" in organize_page.summary.text()
    finally:
        tidy_page.shutdown()
        organize_page.shutdown()
        tidy_page.deleteLater()
        organize_page.deleteLater()
        app.processEvents()


def test_insights_all_files_reuses_browser_with_full_totals_and_safe_actions(large_library, app, monkeypatch):
    from memoria.engine import catalogue
    from memoria.ui.pages.insights import InsightsPage
    ctx = AppContext(TaskRunner())
    ctx.set_library(large_library)
    page = InsightsPage(ctx)
    try:
        assert "All files" in [page.tabs.tabText(i) for i in range(page.tabs.count())]
        page._all_files()
        browser = page.files_page
        spin(app, lambda: not browser._query.running)
        assert browser.filters.kind == "all" and not browser.filters.folder
        assert browser.sort.currentData() == "largest"
        assert len(browser.grid.items()) == catalogue.PAGE_SIZE
        assert browser.rows[0]["id"] == 100_000 and browser.rows[0]["kind"] == "other"
        assert "100,000" in browser.count.text()
        assert page.tabs.currentWidget() is page._files_tab
        assert "Nothing here changes" not in page.subtitle
        large_library.db.execute("UPDATE files SET iso=100 WHERE id=1")
        large_library.db.execute("UPDATE files SET iso=800 WHERE id=2")
        for sort, expected in (("iso_asc", [1, 2]), ("iso_desc", [2, 1])):
            browser.open_filters(catalogue.Filters(kind="all"), sort)
            spin(app, lambda: not browser._query.running)
            assert [row["id"] for row in browser.rows[:2]] == expected
            assert browser.rows[2]["iso"] is None
        browser.open_all_files()
        spin(app, lambda: not browser._query.running)
        first_page = browser.rows[0]["id"]
        browser._turn_page(1)
        spin(app, lambda: not browser._query.running)
        assert browser.rows[0]["id"] < first_page and len(browser.rows) == catalogue.PAGE_SIZE
        selected = [
            {"id": 1, "rel_path": "source\\1.jpg", "kind": "image", "size": 1},
            {"id": 2, "rel_path": "source\\2.mp4", "kind": "video", "size": 2},
            {"id": 3, "rel_path": "source\\3.txt", "kind": "other", "size": 3},
            {"id": 4, "rel_path": "source\\4.mp4", "kind": "video", "error": "Unsupported", "size": 4}]
        for row in selected:
            row["mtime"] = 1
        monkeypatch.setattr(browser, "selected", lambda: selected)
        destinations = []
        ctx.navigate.connect(destinations.append)
        browser._to_video()
        assert ctx.video_selection == [str(large_library.abspath("source\\2.mp4"))]
        assert destinations == ["video"]
        actions = []
        monkeypatch.setattr(browser, "apply_actions", lambda *args, **kwargs: actions.extend(args[2]))
        browser.recycle_selected()
        assert len(actions) == 4 and all(action.op == "recycle" for action in actions)
    finally:
        page.shutdown()
        page.deleteLater()
        app.processEvents()
        large_library.db.execute("UPDATE files SET iso=NULL WHERE id IN (1,2)")


@pytest.mark.parametrize("kind", ["tidy", "organize"])
def test_full_plan_preparation_does_not_block_gui(context, app, monkeypatch, kind):
    from memoria.engine import organize, tidy
    from memoria.ui.pages.organize import OrganizePage
    from memoria.ui.pages.tidy import TidyPage
    row = {"id": 1, "rel_path": "photo.jpg", "name": "photo.jpg", "folder": "",
           "kind": "image", "size": 20, "mtime": 1}
    page = TidyPage(context) if kind == "tidy" else OrganizePage(context)
    if kind == "tidy":
        page._show(tidy.TidyReport({"junk": [row]}))
        engine = tidy
    else:
        page.cleanup.setChecked(False)
        page._show(organize.OrganizePlan(
            [organize.OrganizeItem(row, "2024\\photo.jpg", datetime(2024, 1, 1), "exif")], 0, 0, "year"))
        engine = organize
    gui_thread = threading.get_ident()
    ticks, calls = [], []
    timer = QTimer()
    timer.setInterval(5)
    timer.timeout.connect(lambda: ticks.append(1))

    def prepare(*args):
        assert threading.get_ident() != gui_thread
        time.sleep(.15)
        return []

    monkeypatch.setattr(engine, "plan_actions", prepare)
    monkeypatch.setattr(page, "apply_actions", lambda *args, **kwargs: calls.append(args[0]))
    try:
        timer.start()
        start = time.monotonic()
        page.apply()
        assert time.monotonic() - start < .12
        spin(app, lambda: not page.plan_bg.running)
        assert len(ticks) >= 5 and calls == [kind]
    finally:
        timer.stop()
        page.shutdown()
        page.deleteLater()
        app.processEvents()
