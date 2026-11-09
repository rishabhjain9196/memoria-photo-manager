"""Metadata-only scale checks plus a tiny real-media interactive UI exercise."""
import os
from dataclasses import replace

import pytest

from memoria.engine import albums, catalogue, geography, places
from memoria.engine.db import Library


@pytest.fixture
def indexed(tmp_path):
    lib = Library(tmp_path)
    rows = [
        ("Trip\\India\\a.jpg", "Trip\\India", "a.jpg", ".jpg", "image", 100, "2023-12-31 23:59:59", 28.61, 77.21),
        ("Trip\\India\\Sub\\b.mp4", "Trip\\India\\Sub", "b.mp4", ".mp4", "video", 200, "2024-01-01 00:00:00", 19.07, 72.88),
        ("Trip2\\c.jpg", "Trip2", "c.jpg", ".jpg", "image", 300, "2024-02-29 12:00:00", 48.85, 2.35),
        ("notes", "", "notes", "", "other", 400, None, None, None),
        ("Trip\\India\\d.jpg", "Trip\\India", "d.jpg", ".jpg", "image", 50, None, None, None),
        ("100%_Real\\bad.jpg", "100%_Real", "bad.jpg", ".jpg", "image", 25, "2024-02-28 12:00:00", 200, 77),
    ]
    with lib.transaction() as db:
        db.executemany("INSERT INTO files(rel_path,folder,name,ext,kind,size,taken_at,lat,lon,mtime,analyzed) "
                       "VALUES (?,?,?,?,?,?,?,?,?,1,1)", rows)
        db.execute("INSERT INTO people VALUES (1,'Alice','2026-01-01')")
        for _ in range(2):
            db.execute("INSERT INTO faces(file_id,x,y,w,h,score,emb,person_id) VALUES (1,0,0,1,1,1,?,1)", (bytes(512),))
        db.execute("INSERT INTO face_scans VALUES (3,300,1,0)")
    yield lib
    lib.close()


def ids(lib, filters, sort="newest"):
    return [r["id"] for r in catalogue.page(lib, filters, sort)[0]]


def test_distribution_counts_each_file_once_and_respects_folder_boundaries(indexed):
    filters = catalogue.Filters(kind="all")
    report = catalogue.distribution(indexed, filters)
    assert (report["count"], report["bytes"]) == (6, 1075)
    assert sum(r["bytes"] for r in report["folders"]) == report["bytes"]
    assert sum(r["count"] for r in report["types"]) == report["count"]
    trip = catalogue.distribution(indexed, replace(filters, folder="Trip"))
    assert (trip["count"], trip["bytes"]) == (3, 350)
    assert ids(indexed, replace(filters, folder="Trip\\India", recursive=False), "largest") == [1, 5]
    assert ids(indexed, replace(filters, folder="100%_Real")) == [6]
    assert ids(indexed, replace(filters, extension="")) == [4]


def test_combined_filters_and_literal_search(indexed):
    f = catalogue.Filters(folder="Trip", kind="image", location="gps", faces="any", person=1,
                          min_bytes=100, max_bytes=100, start="2023-12-31", end="2024-01-01")
    assert ids(indexed, f) == [1]  # two faces must not duplicate the file
    assert ids(indexed, replace(f, min_bytes=101, max_bytes=200)) == []
    assert ids(indexed, catalogue.Filters(search="alice")) == [1]
    assert ids(indexed, catalogue.Filters(search="100%_")) == [6]
    assert ids(indexed, catalogue.Filters(search="' OR 1=1 --")) == []
    assert ids(indexed, catalogue.Filters(faces="none")) == [3]
    assert set(ids(indexed, catalogue.Filters(faces="unscanned"))) == {1, 5, 6}
    assert set(ids(indexed, catalogue.Filters(location="none"))) == {5, 6}
    with pytest.raises(ValueError):
        catalogue.where(catalogue.Filters(min_bytes=100, max_bytes=50))


def test_timeline_leap_day_and_album_links(indexed):
    f = catalogue.Filters()
    years = catalogue.timeline(indexed, f)
    assert [(r["key"], r["count"]) for r in years] == [("2023", 1), ("2024", 3)]
    assert [(r["key"], r["count"]) for r in catalogue.timeline(indexed, f, "2024")] == [("2024-01", 1), ("2024-02", 2)]
    assert catalogue.period("2024-02") == ("2024-02-01", "2024-03-01")
    assert catalogue.period("2024-02-29") == ("2024-02-29", "2024-03-01")
    limited = catalogue.in_period(replace(f, start="2024-02-15", end="2024-02-29"), "2024-02")
    assert (limited.start, limited.end) == ("2024-02-15", "2024-02-29")
    aid = albums.create(indexed, "New year", [1, 2])
    linked = catalogue.matching_albums(indexed, catalogue.in_period(f, "2024-01"))
    assert linked == [{"id": aid, "name": "New year", "count": 1}]
    assert ids(indexed, catalogue.in_period(f, "2023-12-31")) == [1]
    indexed.mark_missing([1])
    albums.cleanup(indexed)
    assert indexed.db.execute("SELECT COUNT(*) FROM album_items WHERE album_id=?", (aid,)).fetchone()[0] == 2


def test_offline_map_india_world_and_clicked_cluster(indexed):
    assert geography.in_india(28.61, 77.21)
    assert geography.in_india(19.07, 72.88)
    assert not geography.in_india(27.717, 85.324)  # Kathmandu is not Indian coverage
    india = catalogue.map_data(indexed, catalogue.Filters(folder="Trip"))
    assert india["bounds"] == geography.INDIA and india["gps_count"] == 2
    world = catalogue.map_data(indexed, catalogue.Filters())
    assert world["bounds"] == geography.WORLD and world["gps_count"] == 3
    assert sum(c["count"] for c in world["cells"]) == 3
    for cell in world["cells"]:
        f = catalogue.Filters(bbox=tuple(cell[key] for key in ("south", "north", "west", "east")))
        assert catalogue.page(indexed, f)[1] == cell["count"]


def test_catalogue_scale_is_paged_and_map_is_bounded(indexed):
    with indexed.transaction() as db:
        db.executemany("INSERT INTO files(rel_path,folder,name,ext,kind,size,mtime,lat,lon) "
                       "VALUES (?,'Bulk',?,'.jpg','image',?,1,?,?)",
                       [(f"Bulk\\{i}.jpg", f"{i}.jpg", 30_000_000 + i,
                         (i % 180) - 90, (i % 360) - 180) for i in range(10_000)])
    filters = catalogue.Filters(folder="Bulk")
    first, count, size = catalogue.page(indexed, filters, "largest")
    second, _, _ = catalogue.page(indexed, filters, "largest", catalogue.PAGE_SIZE)
    assert count == 10_000 and size > 300_000_000_000
    assert len(first) == len(second) == 500
    assert first[0]["size"] == 30_009_999
    assert not {r["id"] for r in first} & {r["id"] for r in second}
    mapped = catalogue.map_data(indexed, filters, geography.WORLD)
    assert mapped["gps_count"] == 10_000
    assert len(mapped["cells"]) <= 65 * 41


def test_offline_labels_include_countries_states_and_towns(indexed):
    india = places.map_labels(geography.INDIA)
    assert any("Mumbai" in label["text"] and "Maharashtra" in label["text"] for label in india)
    assert any("Leh" in label["text"] and "Ladakh" in label["text"] for label in india)
    world = places.map_labels(geography.WORLD)
    assert {"India", "France"} <= {label["text"] for label in world}
    assert len(world) <= 160
    bounds = (18.9, 19.3, 72.7, 73.1)
    local = places.map_labels(bounds)
    assert any("Mumbai" in label["text"] for label in local)
    assert all(bounds[0] <= label["lat"] <= bounds[1] and bounds[2] <= label["lon"] <= bounds[3]
               for label in local)
    cells = catalogue.map_data(indexed, catalogue.Filters(folder="Trip"))["cells"]
    assert any("Mumbai" in cell["place"] for cell in cells)
    assert any("Delhi" in cell["place"] for cell in cells)


def test_map_touchpad_wheel_pan_keyboard_and_visible_labels(indexed, tmp_path):
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ.setdefault("QT_QPA_FONTDIR", r"C:\Windows\Fonts")
    from PySide6.QtCore import QPoint, QPointF, Qt
    from PySide6.QtGui import QFont, QWheelEvent
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication
    from memoria.ui import theme
    from memoria.ui.insight_charts import GeoChart
    app = QApplication.instance() or QApplication([])
    app.setFont(QFont("Segoe UI", 10))
    chart = GeoChart()
    chart.resize(900, 700)
    chart.set_data(catalogue.map_data(indexed, catalogue.Filters(folder="Trip")))
    chart.show()
    changed, selected = [], []
    chart.zoomed.connect(changed.append)
    chart.chosen.connect(selected.append)

    def wheel(angle=0, pixels=0, point=None):
        point = point or chart.plot_rect().center()
        event = QWheelEvent(point, QPointF(chart.mapToGlobal(point.toPoint())),
                            QPoint(0, pixels), QPoint(0, angle), Qt.MouseButton.NoButton,
                            Qt.KeyboardModifier.NoModifier, Qt.ScrollPhase.ScrollUpdate, False)
        QApplication.sendEvent(chart, event)
        app.processEvents()

    try:
        app.processEvents()
        assert any("Maharashtra" in text for _, text in chart.label_hits)
        assert 0 < len(chart.label_hits) <= 60
        assert all(not rect.intersects(other) for i, (rect, _) in enumerate(chart.label_hits)
                   for other, _ in chart.label_hits[i + 1:])
        assert chart.grab().save(str(tmp_path / "map-offline-labels.png"))
        start = chart.bounds
        wheel()
        assert chart.bounds == start and not changed  # zero-motion touchpad phases must not zoom out
        wheel(pixels=30)
        assert 17 < chart.bounds[3] - chart.bounds[2] < 34
        wheel(pixels=-30)
        assert chart.bounds == pytest.approx(start)
        wheel(angle=15)
        assert 17 < chart.bounds[3] - chart.bounds[2] < 34  # high-resolution wheel, not a full 2x jump
        wheel(angle=-15)
        assert chart.bounds == pytest.approx(start)
        center = chart.project(chart.cells[0]["lat"], chart.cells[0]["lon"]).toPoint()
        QTest.mousePress(chart, Qt.MouseButton.LeftButton, pos=center)
        QTest.mouseMove(chart, center + QPoint(40, 35))
        QTest.mouseRelease(chart, Qt.MouseButton.LeftButton, pos=center + QPoint(40, 35))
        app.processEvents()
        assert chart.bounds != start and not selected  # dragging a marker must not open its photos
        moved = chart.project(chart.cells[0]["lat"], chart.cells[0]["lon"]).toPoint()
        assert abs(moved.x() - center.x() - 40) <= 1 and abs(moved.y() - center.y() - 35) <= 1
        chart.set_bounds(geography.WORLD)
        app.processEvents()
        wheel(angle=120, point=QPointF(15, 15))  # letterboxed area is still part of the map widget
        assert chart.bounds[3] - chart.bounds[2] == pytest.approx(180)
        QTest.keyClick(chart, Qt.Key.Key_Plus)
        assert chart.bounds[3] - chart.bounds[2] == pytest.approx(90)
        QTest.keyClick(chart, Qt.Key.Key_Minus)
        assert chart.bounds[3] - chart.bounds[2] == pytest.approx(180)
        before = chart.bounds
        QTest.keyClick(chart, Qt.Key.Key_Right)
        assert chart.bounds[2] > before[2]
        for _ in range(12):
            chart.zoom(4)
        assert chart.bounds[3] - chart.bounds[2] == pytest.approx(.01)
        for _ in range(12):
            chart.zoom(-4)
        assert chart.bounds == geography.WORLD
        theme.use("dark")
        app.setStyleSheet(theme.QSS)
        chart.set_bounds(geography.INDIA)
        app.processEvents()
        assert chart.grab().save(str(tmp_path / "map-offline-labels-dark.png"))
    finally:
        chart.close()
        chart.deleteLater()
        app.processEvents()
        theme.use("light")
        app.setStyleSheet(theme.QSS)


def test_zoom_remains_live_during_query_and_stale_results_cannot_reset_view(indexed, monkeypatch):
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    import threading
    import time
    from PySide6.QtWidgets import QApplication
    from memoria.ui.pages.insights import InsightsPage
    from memoria.ui.tasks import TaskRunner
    from memoria.ui.widgets import AppContext
    app = QApplication.instance() or QApplication([])
    ctx = AppContext(TaskRunner())
    ctx.set_library(indexed)
    page = InsightsPage(ctx)
    page.resize(1100, 800)
    page.show()
    entered, release = threading.Event(), threading.Event()
    errors = []
    page.bg.failed.connect(errors.append)

    def wait(predicate, check_view=None):
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            app.processEvents()
            if check_view is not None:
                assert page.map.bounds == check_view
            if predicate():
                return
            time.sleep(.01)
        assert predicate(), errors

    try:
        wait(lambda: page._mapped_key is not None and not page.bg.running)
        page.tabs.setCurrentIndex(2)
        original = catalogue.map_data
        calls = []
        def delayed(lib, filters, bounds):
            calls.append(bounds)
            if len(calls) == 1:
                entered.set()
                if not release.wait(10):
                    raise TimeoutError("Map test gate timed out")
            return original(lib, filters, bounds)
        monkeypatch.setattr(catalogue, "map_data", delayed)
        unwanted = []
        for name in ("distribution", "timeline", "matching_albums"):
            method = getattr(catalogue, name)
            def watched(*args, name=name, method=method):
                unwanted.append(name)
                return method(*args)
            monkeypatch.setattr(catalogue, name, watched)
        page.zoom_in.click()
        wait(entered.is_set)
        assert page.map.isEnabled() and page.zoom_out.isEnabled()
        first = page.map.bounds
        page.zoom_in.click()
        latest = page.map.bounds
        assert latest != first and page.bg.running
        release.set()
        wait(lambda: len(calls) == 2 and not page.bg.running and not page.timer.isActive(), check_view=latest)
        assert not errors and not unwanted
        assert calls == [first, latest]
        page.zoom_out.click()
        assert page.map.bounds[3] - page.map.bounds[2] == pytest.approx(
            (latest[3] - latest[2]) * 2)
    finally:
        release.set()
        page.shutdown()
        page.close()
        page.deleteLater()
        app.processEvents()


def test_interactive_insights_and_filter_navigation(tmp_path, monkeypatch):
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ.setdefault("QT_QPA_FONTDIR", r"C:\Windows\Fonts")
    import time
    from PIL import Image
    from PySide6.QtCore import QPoint, QPointF, Qt
    from PySide6.QtGui import QFont, QWheelEvent
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication
    from memoria.engine import scanner
    from memoria.ui import theme
    from memoria.ui.main_window import MainWindow
    from memoria.ui.widgets import MessageDialog
    from memoria.ui.library_filters import FilterDialog

    app = QApplication.instance() or QApplication([])
    theme.use("light")
    app.setStyleSheet(theme.QSS)
    app.setFont(QFont("Segoe UI", 10))
    for i in range(3):
        Image.new("RGB", (32 + i, 24), ("red", "green", "blue")[i]).save(tmp_path / f"{i}.jpg")
    lib = Library(tmp_path)
    scanner.index(lib)
    lib.db.execute("UPDATE files SET taken_at='2024-02-29 12:00:00', lat=28.61,lon=77.21")
    aid = albums.create(lib, "Leap day", [r["id"] for r in lib.files()])
    before = {p.name: p.read_bytes() for p in tmp_path.glob("*.jpg")}
    window = MainWindow()
    monkeypatch.setattr(MessageDialog, "exec", lambda self: 0)
    window.ctx.set_library(lib)
    window._show_library_ui(True)
    window.resize(1440, 900)
    window.show()

    def idle(page):
        deadline = time.monotonic() + 15
        while (page.bg.running or page.timer.isActive() or not page.tabs.isEnabled()) and time.monotonic() < deadline:
            app.processEvents()
            time.sleep(.01)
        app.processEvents()
        assert page.tabs.isEnabled(), page.status.text()

    def click_item(widget, item):
        QTest.mouseClick(widget.viewport(), Qt.MouseButton.LeftButton, pos=widget.visualItemRect(item).center())

    try:
        window.go("insights")
        page = window.page("insights")
        idle(page)
        assert page.types.topLevelItemCount() == 1
        assert page.map.bounds == geography.INDIA
        assert page.album_list.item(0).data(Qt.ItemDataRole.UserRole) == aid
        assert window.grab().save(str(tmp_path / "insights-storage.png"))
        page.tabs.setCurrentIndex(1)
        click_item(page.time, page.time.topLevelItem(0))
        idle(page)
        assert page.prefix == "2024"
        click_item(page.time, page.time.topLevelItem(0))
        idle(page)
        assert page.prefix == "2024-02"
        assert window.grab().save(str(tmp_path / "insights-timeline.png"))
        click_item(page.time, page.time.topLevelItem(0))
        app.processEvents()
        photos = window.page("photos")
        assert window.current_key == "photos" and len(photos.grid.items()) == 3
        assert photos.filters.start == "2024-02-29"
        photos.sort.setCurrentIndex(photos.sort.findData("largest"))
        assert photos.rows[0]["size"] >= photos.rows[-1]["size"]
        app.processEvents()
        assert window.grab().save(str(tmp_path / "largest-files.png"))
        photos.tree.setCurrentItem(photos.tree.topLevelItem(1))
        photos.kind.setCurrentIndex(photos.kind.findData("video"))
        assert not photos.grid.items()
        assert photos.tree.currentItem().data(0, Qt.ItemDataRole.UserRole) == "2024"
        photos.kind.setCurrentIndex(photos.kind.findData("all"))
        window.go("insights")
        click_item(page.album_list, page.album_list.item(0))
        assert window.current_key == "albums" and window.page("albums")._album()["id"] == aid
        window.go("insights")
        page.tabs.setCurrentIndex(2)
        app.processEvents()
        assert window.grab().save(str(tmp_path / "insights-map.png"))
        lib.db.execute("UPDATE files SET lat=48.85,lon=2.35 WHERE id=(SELECT MAX(id) FROM files)")
        page.refresh()
        idle(page)
        assert page.map.bounds == geography.WORLD
        assert window.grab().save(str(tmp_path / "insights-world.png"))
        center = page.map.plot_rect().center()
        wheel = QWheelEvent(center, QPointF(page.map.mapToGlobal(center.toPoint())), QPoint(), QPoint(0, 120),
                            Qt.MouseButton.NoButton, Qt.KeyboardModifier.NoModifier,
                            Qt.ScrollPhase.NoScrollPhase, False)
        QApplication.sendEvent(page.map, wheel)
        idle(page)
        assert page.map.bounds[3] - page.map.bounds[2] == 180
        page._map_bounds(None)
        idle(page)
        app.processEvents()
        cell = page.map.cells[0]
        QTest.mouseClick(page.map, Qt.MouseButton.LeftButton,
                         pos=page.map.project(cell["lat"], cell["lon"]).toPoint())
        assert window.current_key == "photos" and photos.filters.bbox is not None
        assert len(photos.grid.items()) == cell["count"]
        dlg = FilterDialog(window, lib, photos.filters)
        dlg.show()
        app.processEvents()
        assert dlg.grab().save(str(tmp_path / "library-filters.png"))
        dlg.close()
        window.go("insights")
        theme.use("dark")
        app.setStyleSheet(theme.QSS)
        app.setPalette(theme.qpalette())
        app.processEvents()
        assert window.grab().save(str(tmp_path / "insights-dark.png"))
        assert {p.name: p.read_bytes() for p in tmp_path.glob("*.jpg")} == before
    finally:
        window.close()
        window.deleteLater()
        app.processEvents()
        theme.use("light")
        app.setStyleSheet(theme.QSS)
        app.setPalette(theme.qpalette())
