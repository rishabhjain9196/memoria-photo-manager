"""Albums (events, trips, places, people), offline place names, and export with undo."""
import os
from pathlib import Path

import pytest

from memoria.engine import actions, albums, faces, places


def _snapshot(root):
    return {p: (p.stat().st_size, p.stat().st_mtime) for p in root.rglob("*") if p.is_file() and ".memoria" not in p.parts}


def test_place_names_are_offline_and_sensible():
    assert places.nearest(34.1526, 77.5771).label == "Leh, Ladakh"
    assert places.nearest(28.6139, 77.2090).label == "Delhi"
    assert places.nearest(15.4909, 73.8278).label == "Goa"          # between towns → the region
    assert places.nearest(0.0, -140.0) is None                      # middle of the Pacific
    assert places.nearest(None, None) is None
    assert 1100 < places.distance_km(28.6139, 77.2090, 19.0760, 72.8777) < 1200   # Delhi–Mumbai


def test_date_ranges():
    assert albums.date_range("2019-12-25 10:00:00", "2019-12-25 18:00:00") == "25 Dec 2019"
    assert albums.date_range("2021-03-14 10:00:00", "2021-03-16 09:00:00") == "14–16 Mar 2021"
    assert albums.date_range("2023-06-28 10:00:00", "2023-07-02 09:00:00") == "28 Jun – 2 Jul 2023"
    assert albums.date_range("2019-12-30 10:00:00", "2020-01-02 09:00:00") == "Dec 2019 – Jan 2020"


def test_event_albums_follow_trips_and_skip_copies(library, expected):
    sugg = albums.suggest_events(library)
    names = [s.name for s in sugg]
    assert "Leh, Ladakh · 10–12 Jun 2023" in names                 # three days in one place = one trip
    assert "Delhi · 25 Dec 2019" in names and "Goa · 14 Mar 2021" in names
    rows = {r["id"]: dict(r) for r in library.files()}
    dup_files = {f for g in expected["duplicate_groups"] for f in g}
    for s in sugg:
        rels = [rows[i]["rel_path"] for i in s.file_ids]
        assert not any("Screenshot" in r for r in rels)
        times = [rows[i]["taken_at"] for i in s.file_ids]
        assert times == sorted(times)
        hashes = [rows[i]["chash"] for i in s.file_ids if rows[i]["chash"] and rows[i]["rel_path"] in dup_files]
        assert len(hashes) == len(set(hashes))                      # one copy of each exact duplicate
        assert len(s.file_ids) >= 3
    split = albums.suggest_events(library, albums.EventOptions(trip_days=0))
    assert sum("Jun 2023" in s.name for s in split) >= 2            # without trip logic the days separate


def test_place_and_people_albums(library, expected):
    names = {s.name for s in albums.suggest_places(library)}
    assert {"Delhi", "Leh, Ladakh", "Goa"} <= names
    if not faces.available():
        pytest.skip("face models not available")
    faces.scan(library)
    lincoln = set(expected["people"]["Abraham Lincoln"])
    g = next(g for g in faces.groups(library) if {r["rel_path"] for r in faces.photos_of(library, g.key)} >= lincoln)
    faces.name(library, g.key, "Abraham Lincoln")
    people = albums.suggest_people(library)
    rows = {r["id"]: r["rel_path"] for r in library.files()}
    assert [s.name for s in people] == ["Abraham Lincoln"]
    assert {rows[i] for i in people[0].file_ids} == lincoln


def test_albums_never_touch_files(library):
    before = _snapshot(library.root)
    sugg = albums.suggest_events(library)
    ids = albums.save(library, sugg[:2])
    assert albums.suggest_events(library)[0].exists                # saved suggestions are recognised
    aid = albums.create(library, sugg[0].name, sugg[2].file_ids)
    assert albums.albums(library)[0]["name"] != "" and \
        library.db.execute("SELECT name FROM albums WHERE id=?", (aid,)).fetchone()[0] == f"{sugg[0].name} (2)"
    assert albums.rename(library, aid, "  My   trip ") == "My trip"
    first = albums.items(library, ids[0])
    albums.remove(library, ids[0], [first[0]["id"]])
    assert len(albums.items(library, ids[0])) == len(first) - 1
    assert albums.add(library, ids[0], [first[0]["id"], first[1]["id"]]) == 1
    albums.set_cover(library, ids[0], first[1]["id"])
    assert next(a for a in albums.albums(library) if a["id"] == ids[0])["cover"] == first[1]["id"]
    albums.delete(library, ids)
    assert {a["id"] for a in albums.albums(library)} == {aid}
    assert _snapshot(library.root) == before


def test_export_copies_albums_into_folders_and_undo_removes_them(library, tmp_path):
    sugg = albums.suggest_events(library)
    a1, a2 = albums.save(library, sugg[:2])
    albums.rename(library, a2, 'Trip: "best" / of?')
    dest = tmp_path / "Exports"
    plan = albums.plan_export(library, [a1, a2], dest)
    res = actions.apply(library, "albums", "Export 2 albums", plan)
    assert res.failed == res.skipped == 0
    folders = sorted(p.name for p in dest.iterdir())
    assert folders == sorted([albums.folder_name(sugg[0].name), "Trip- -best- - of-"])
    for a, folder in ((a1, albums.folder_name(sugg[0].name)),):
        for r in albums.items(library, a):
            assert (dest / folder / r["name"]).read_bytes() == library.abspath(r["rel_path"]).read_bytes()
    again = actions.apply(library, "albums", "Export again", albums.plan_export(library, [a1], dest))
    assert again.done == len(albums.items(library, a1))              # nothing overwritten: copies get a number
    assert any(" (2)" in p.name for p in (dest / folders[0]).iterdir())
    assert actions.undo(library, res.batch_id).ok and actions.undo(library, again.batch_id).ok
    assert not [p for p in dest.rglob("*") if p.is_file()]
    with pytest.raises(ValueError):
        albums.plan_export(library, [a1], library.root / ".memoria" / "x")
    assert albums.inside_library(library, library.root / "Exports") and not albums.inside_library(library, dest)


def test_folder_names_are_windows_safe():
    assert albums.folder_name('A/B: C?') == "A-B- C-"
    assert albums.folder_name("CON") == "_CON"
    assert albums.folder_name("Trip. ") == "Trip"
    assert albums.folder_name("") == "Album"


@pytest.mark.parametrize("mode", ["event", "place", "person"])
def test_suggest_button_uses_selected_mode_and_displays_results(library, monkeypatch, mode):
    import sys
    import time
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication
    from memoria.ui.pages.albums import AlbumsPage, MODES
    from memoria.ui.tasks import TaskRunner
    from memoria.ui.widgets import AppContext

    app = QApplication.instance() or QApplication([])
    runner = TaskRunner()
    ctx = AppContext(runner)
    ctx.set_library(library)
    page = AlbumsPage(ctx)
    page.resize(1440, 900)
    page.show()
    page.tabs.setCurrentIndex(1)
    page.mode.setCurrentIndex([key for key, _ in MODES].index(mode))
    app.processEvents()
    before = _snapshot(library.root)
    started, errors, slot_errors = [], [], []
    runner.started.connect(started.append)
    ctx.parallel.started.connect(started.append)
    runner.error.connect(lambda *args: errors.append(args))
    ctx.parallel.error.connect(lambda *args: errors.append(args))
    monkeypatch.setattr(sys, "excepthook", lambda typ, value, tb: slot_errors.append(value))
    try:
        QTest.mouseClick(page.suggest_btn, Qt.MouseButton.LeftButton)
        assert not slot_errors, slot_errors
        assert started == ["Suggesting albums"]
        deadline = time.monotonic() + 10
        while (runner.active or ctx.parallel.tasks or page._suggestion_query.running) and time.monotonic() < deadline:
            app.processEvents()
            time.sleep(.01)
        app.processEvents()
        assert not runner.active and not ctx.parallel.tasks and not errors and not slot_errors, (errors, slot_errors)
        assert page.suggest_btn.isEnabled()
        if mode == "person":
            assert not page.suggestions and not page.save_btn.isEnabled()
            assert page.s_title.text() == "No albums to suggest"
        else:
            assert page.suggestions and page.save_btn.isEnabled()
            assert all(s.kind == mode and len(s.file_ids) >= 3 for s in page.suggestions)
            assert page.s_list.count() == len(page.suggestions)
            assert page.s_grid.items()
        assert not albums.albums(library)  # suggestions require a separate Save click
        assert _snapshot(library.root) == before
    finally:
        runner.cancel()
        runner.wait()
        app.processEvents()
        page.shutdown()
        page.close()
        page.deleteLater()
        app.processEvents()
