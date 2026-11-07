"""Metadata-only scale checks plus a tiny real-media interactive UI exercise."""
import os
from dataclasses import replace

import pytest

from memoria.engine import albums, catalogue, geography
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
