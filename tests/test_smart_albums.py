"""Dynamic saved queries and bounded album/photo browsing using metadata-only scale fixtures."""
import time
from dataclasses import replace

import pytest

from memoria.engine import albums, catalogue, organisation
from memoria.engine.db import Library


@pytest.fixture
def smart_library(tmp_path):
    lib = Library(tmp_path)
    with lib.transaction() as db:
        db.executemany("INSERT INTO files(rel_path,folder,name,ext,kind,size,mtime,analyzed,taken_at) "
                       "VALUES (?,'Trip',?,'.jpg','image',?,1,1,'2024-01-02')",
                       [(f"Trip\\{i}.jpg", f"{i}.jpg", i * 10) for i in range(1, 4)])
    yield lib
    lib.close()


def test_smart_rules_are_dynamic_persistent_and_do_not_copy_membership(smart_library):
    lib = smart_library
    organisation.edit(lib, [1], rating=4, favorite=True, add_tags=["Travel", "Family"])
    filters = catalogue.Filters(min_rating=3, favorite=True, tags=("travel",), search="Trip",
                                start="2024-01-01", end="2025-01-01", min_bytes=5)
    aid = albums.create_smart(lib, "Best travel", filters, "largest")
    assert [r["id"] for r in albums.item_page(lib, aid)[0]] == [1]
    assert lib.db.execute("SELECT COUNT(*) FROM album_items").fetchone()[0] == 0
    organisation.edit(lib, [2], rating=5, favorite=True, add_tags=["Travel"])
    assert [r["id"] for r in albums.items(lib, aid)] == [2, 1]
    assert albums.albums(lib)[0]["items"] == 2
    organisation.edit(lib, [1], review="reject")
    albums.update_smart(lib, aid, replace(filters, review="pick"), "name")
    assert albums.item_page(lib, aid)[1] == 0
    organisation.edit(lib, [2], review="pick")
    assert albums.item_page(lib, aid)[1] == 1
    value = lib.db.execute("SELECT rule_json FROM albums WHERE id=?", (aid,)).fetchone()[0]
    restored, sort = catalogue.read_rule(value)
    assert restored == replace(filters, review="pick") and sort == "name"
    lib.mark_missing([2])
    assert albums.item_page(lib, aid)[1] == 0
    albums.delete(lib, [aid])
    assert lib.file(1) is not None
    assert organisation.state(lib, 1)["review"] == "reject"


def test_combined_tags_roots_and_availability_are_parameterized(smart_library):
    lib = smart_library
    lib.db.execute("INSERT INTO library_roots(path,label,token,online) VALUES ('Z:\\Offline','Archive','test-root',0)")
    lib.db.execute("UPDATE files SET root_id=2 WHERE id=2")
    organisation.edit(lib, [1, 2], rating=5, favorite=True, review="pick", add_tags=["One"])
    organisation.edit(lib, [2, 3], add_tags=["Two"])
    filters = catalogue.Filters(tags=("one", "two"), tag_mode="all", min_rating=4, favorite=True,
                                review="pick", root_id=2, availability="offline")
    assert [r["id"] for r in catalogue.page(lib, filters)[0]] == [2]
    assert catalogue.page(lib, replace(filters, availability="online"))[1] == 0
    assert catalogue.page(lib, catalogue.Filters(tags=("one", "two"), tag_mode="any"))[1] == 3
    assert catalogue.page(lib, catalogue.Filters(tags=("' OR 1=1 --",)))[1] == 0
    assert catalogue.page(lib, catalogue.Filters(max_rating=0))[1] == 1
    assert catalogue.page(lib, catalogue.Filters(review="unreviewed"))[1] == 1
    assert [r["id"] for r in catalogue.page(lib, catalogue.Filters(), "rating_desc")[0]] == [1, 2, 3]


@pytest.mark.parametrize("patch", [
    {"version": 99}, {"version": True}, {"sort": "DROP TABLE files"},
    {"filters": {"sql": "1=1"}}, {"filters": {"min_rating": 6}}, {"filters": {"tags": "tag"}},
    {"filters": {"favorite": "true"}}, {"filters": {"bbox": [1, 2]}},
    {"filters": {"root_id": -1}}, {"filters": {"min_duration": float("nan")}},
    {"filters": {"review": "delete"}}, {"filters": {"min_bytes": "10"}},
])
def test_invalid_rules_are_rejected_without_writing(smart_library, patch):
    value = {"version": 1, "filters": {}, "sort": "newest", **patch}
    with pytest.raises(ValueError):
        catalogue.read_rule(value)
    assert smart_library.db.execute("SELECT COUNT(*) FROM albums").fetchone()[0] == 0


def test_smart_albums_reject_manual_membership(smart_library):
    lib = smart_library
    aid = albums.create_smart(lib, "Query", catalogue.Filters())
    for fn, args in ((albums.add, [1]), (albums.remove, [1]), (albums.set_cover, 1)):
        with pytest.raises(ValueError, match="rules"):
            fn(lib, aid, args)
    with pytest.raises(ValueError):
        albums.create_smart(lib, "Nested", catalogue.Filters(album_id=aid))
    with pytest.raises(ValueError):
        albums.create(lib, "Invalid", [999])
    assert lib.db.execute("SELECT COUNT(*) FROM albums").fetchone()[0] == 1


def wait(app, predicate, timeout=15):
    deadline = time.monotonic() + timeout
    while not predicate() and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(.005)
    app.processEvents()
    assert predicate()


def test_100k_catalogue_and_album_ui_are_bounded_and_async(smart_library):
    from PySide6.QtWidgets import QApplication
    from memoria.ui.pages.albums import AlbumsPage
    from memoria.ui.pages.photos import PhotosPage
    from memoria.ui.tasks import TaskRunner
    from memoria.ui.widgets import AppContext
    lib = smart_library
    with lib.transaction() as db:
        db.executemany("INSERT INTO files(rel_path,folder,name,ext,kind,size,mtime,analyzed) "
                       "VALUES (?,'Bulk',?,'.txt','other',?,1,0)",
                       ((f"Bulk\\{i}.txt", f"{i}.txt", i + 100) for i in range(100_000)))
        db.executemany("INSERT INTO albums(name,kind,created_at) VALUES (?,'manual','2026-01-01')",
                       ((f"Album {i:05d}",) for i in range(10_000)))
        db.execute("INSERT INTO album_items(album_id,file_id,pos) SELECT 1,id,id FROM files")
    first, count, _ = catalogue.page(lib, catalogue.Filters(kind="all"), "largest")
    assert len(first) == 500 and count == 100_003
    listing, count, _ = albums.list_page(lib)
    assert len(listing) == 100 and count == 10_000
    assert albums.item_page(lib, 1)[1] == 100_003
    app = QApplication.instance() or QApplication([])
    ctx = AppContext(TaskRunner())
    ctx.set_library(lib)
    photos, page = PhotosPage(ctx, embedded=True), AlbumsPage(ctx)
    try:
        photos.open_all_files()
        wait(app, lambda: not photos._query.running)
        assert len(photos.rows) == 500 and photos.rows[0]["kind"] == "other"
        assert photos.rows[0]["size"] == 100_099
        photos.grid.selectAll()
        assert len(photos.selected()) == 500
        photos._turn_page(1)
        wait(app, lambda: not photos._query.running)
        assert len(photos.rows) == 500 and not photos.selected()
        page.refresh()
        wait(app, lambda: not page._albums_query.running and not page._items_query.running)
        assert page.a_list.count() == 100 and len(page.a_grid.items()) == 500
        page.open_album(9999)
        wait(app, lambda: not page._albums_query.running and not page._items_query.running)
        assert page._album()["id"] == 9999
        suggestions = [albums.Suggestion(str(i), "event", list(range(1, 2001))) for i in range(1000)]
        page._show_suggestions(suggestions)
        wait(app, lambda: not page._suggestion_query.running)
        assert page.s_list.count() == 100 and len(page.s_grid.items()) == 500
        page._turn_suggestions(1)
        wait(app, lambda: not page._suggestion_query.running)
        assert page.s_list.count() == 100
        page._check_all(False)
        assert not page._chosen()
    finally:
        photos._query.wait()
        for worker in (page._albums_query, page._items_query, page._suggestion_query):
            worker.wait()
        photos.close()
        page.close()
        photos.deleteLater()
        page.deleteLater()
        app.processEvents()


def test_photos_saves_current_search_sort_and_edits_selection(smart_library, monkeypatch):
    from PySide6.QtWidgets import QApplication, QComboBox, QDialog
    from memoria.ui.pages.photos import PhotosPage
    from memoria.ui.tasks import TaskRunner
    from memoria.ui.widgets import AppContext
    app = QApplication.instance() or QApplication([])
    ctx = AppContext(TaskRunner())
    ctx.set_library(smart_library)
    page = PhotosPage(ctx)
    try:
        page.open_filters(catalogue.Filters(search="Trip", min_bytes=15), "largest")
        wait(app, lambda: not page._query.running)
        aid = page.save_search("Saved from Photos")
        assert [r["id"] for r in albums.items(smart_library, aid)] == [3, 2]
        page.grid.setCurrentIndex(page.grid.model_.index(0, 0))
        def accepted(dialog):
            for box in dialog.findChildren(QComboBox):
                pick = box.findData("reject")
                if pick >= 0:
                    box.setCurrentIndex(pick)
            return QDialog.DialogCode.Accepted
        monkeypatch.setattr(QDialog, "exec", accepted)
        page.b_organise.click()
        wait(app, lambda: not ctx.runner.active)
        assert organisation.state(smart_library, 3)["review"] == "reject"
        assert organisation.state(smart_library, 2)["review"] == "unreviewed"
        assert smart_library.file(3) is not None
        wait(app, lambda: not page._query.running)
    finally:
        page._query.wait()
        page.close()
        page.deleteLater()
        app.processEvents()


def test_bounded_distribution_keeps_totals(smart_library):
    lib = smart_library
    lib.db.execute("UPDATE files SET folder='Elsewhere',ext='.png' WHERE id=3")
    full = catalogue.distribution(lib, catalogue.Filters())
    limited = catalogue.distribution(lib, catalogue.Filters(), limit=1)
    assert len(limited["folders"]) == len(limited["types"]) == 1
    assert (limited["count"], limited["bytes"]) == (full["count"], full["bytes"])


def test_hidden_photos_drop_stale_generation_results(smart_library, monkeypatch):
    import threading
    from PySide6.QtWidgets import QApplication
    from memoria.ui.pages.photos import PhotosPage
    from memoria.ui.tasks import TaskRunner
    from memoria.ui.widgets import AppContext
    app = QApplication.instance() or QApplication([])
    ctx = AppContext(TaskRunner())
    ctx.set_library(smart_library)
    page = PhotosPage(ctx)
    entered, release = threading.Event(), threading.Event()
    original = catalogue.page
    def blocked(*args):
        entered.set()
        assert release.wait(5)
        return original(*args)
    monkeypatch.setattr(catalogue, "page", blocked)
    try:
        page.open_all_files()
        assert entered.wait(2)  # GUI call returned even though the catalogue read is blocked.
        ctx.library_modified.emit()
        release.set()
        wait(app, lambda: not page._query.running)
        assert page.stale and page.rows == []
        page.refresh()
        wait(app, lambda: not page._query.running)
        assert len(page.rows) == 3
    finally:
        release.set()
        page.shutdown()
        page.deleteLater()
        app.processEvents()


def test_smart_export_still_protects_internal_storage_and_originals(smart_library, tmp_path):
    lib = smart_library
    source = lib.abspath("Trip\\1.jpg")
    source.parent.mkdir()
    source.write_bytes(b"0123456789")
    aid = albums.create_smart(lib, "Best", catalogue.Filters(search="1.jpg"))
    plan = albums.plan_export(lib, [aid], tmp_path / "Exports")
    assert len(plan) == 1 and plan[0].op == "copy" and plan[0].src == str(source)
    assert source.read_bytes() == b"0123456789"
    with pytest.raises(ValueError):
        albums.plan_export(lib, [aid], tmp_path / ".MEMORIA" / "Exports")
