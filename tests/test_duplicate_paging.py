"""Adaptive duplicate comparisons remain bounded and reject obsolete background results."""
import os
import threading
import time

os.environ["QT_QPA_PLATFORM"] = "offscreen"

import pytest
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QApplication

from memoria.engine import assets, duplicates
from memoria.engine.db import Library
from memoria.ui.pages.duplicates import COPY_PAGE, DuplicatesPage, GROUP_PAGE
from memoria.ui.tasks import TaskRunner
from memoria.ui.widgets import AppContext


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def spin(app, predicate, timeout=30):
    deadline = time.monotonic() + timeout
    while not predicate() and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(.005)
    app.processEvents()
    assert predicate()


@pytest.fixture(scope="module")
def catalogue(tmp_path_factory, app):
    lib = Library(tmp_path_factory.mktemp("duplicate-catalogue"))
    with lib.transaction() as db:
        db.executemany("INSERT INTO files(id,rel_path,folder,name,ext,kind,size,mtime,chash) "
                       "VALUES (?,?,?,?,?,'other',10,1,'same')",
                       ((i, f"Large\\{i:06}.dat", "Large", f"{i:06}.dat", ".dat")
                        for i in range(1, 100_001)))
    rows = [dict(row) for row in lib.db.execute("SELECT * FROM files ORDER BY id")]
    yield lib, rows
    lib.close()


def make_page(lib):
    ctx = AppContext(TaskRunner())
    ctx.set_library(lib)
    page = DuplicatesPage(ctx)
    page.resize(1400, 900)
    page.show()
    return page


def settle(app, page):
    spin(app, lambda: not any(worker.running for worker in (page.groups_bg, page.detail_bg, page.plan_bg)))


def test_100k_review_is_paged_and_checks_apply_only_to_the_current_group(catalogue, app, monkeypatch):
    lib, rows = catalogue
    groups = [duplicates.DuplicateGroup("large", 10, rows[:99_000], rows[0]["id"])]
    groups.extend(duplicates.DuplicateGroup(f"pair-{i}", 10, rows[i:i + 2], rows[i]["id"])
                  for i in range(99_000, 100_000, 2))
    report = duplicates.DuplicateReport(groups, [])
    page = make_page(lib)
    reads = []
    monkeypatch.setattr(page.ctx.thumbs, "get", lambda fid: reads.append(fid))
    ticks = []
    timer = QTimer()
    timer.setInterval(5)
    timer.timeout.connect(lambda: ticks.append(1))
    timer.start()
    try:
        started = time.monotonic()
        page._show(report)
        assert time.monotonic() - started < .1
        settle(app, page)
        assert ticks
        assert len(page.groups) == 501 and page.list.count() == GROUP_PAGE
        assert page.detail.currentWidget() is page.many_view
        assert page.copies.topLevelItemCount() == COPY_PAGE
        assert len(reads) < 10  # previews only; no thumbnail request per duplicate
        page.copies.topLevelItem(1).setCheckState(0, Qt.CheckState.Unchecked)
        settle(app, page)
        assert 2 not in page.selected and page._selection_plan["files"] == 98_998
        page.copy_next.click()
        assert page.copies.topLevelItem(0).data(0, Qt.ItemDataRole.UserRole)["key"] == 201
        page.copy_previous.click()
        assert page.copies.topLevelItem(1).checkState(0) == Qt.CheckState.Unchecked
        page.group_next.click()
        settle(app, page)
        assert page.group_offset == GROUP_PAGE and page.list.count() == GROUP_PAGE
        assert len(page.selected) == 1 and page._selection_plan["files"] == 1
        assert page.detail.currentWidget() is page.pane_view
        page.group_next.click()
        settle(app, page)
        assert page.list.count() == 101
        page.group_previous.click()
        settle(app, page)
        page.group_previous.click()
        settle(app, page)
        assert page.group_offset == 0 and page._current_group[1].hash == "large"
        page.keep_all.click()
        settle(app, page)
        assert len(page.groups) == 500
        page.show_previous.setChecked(True)
        settle(app, page)
        assert len(page.groups) == 501 and not page.selected
        assert not page.move_btn.isEnabled()
    finally:
        timer.stop()
        page.shutdown()
        page.deleteLater()
        app.processEvents()
        duplicates.remember_keep(lib, duplicates.file_review_key(groups[0]), False)


def test_delayed_footprint_cannot_replace_the_new_comparison(catalogue, app, monkeypatch):
    lib, rows = catalogue
    first = duplicates.DuplicateGroup("first", 10, rows[:4], rows[0]["id"])
    second = duplicates.DuplicateGroup("second", 10, rows[4:7], rows[4]["id"])
    page = make_page(lib)
    gate, entered = threading.Event(), threading.Event()
    original = assets.footprint
    calls = []
    def blocked(lib, plan):
        ids = {action.file_id for action in plan if action.file_id is not None}
        calls.append(ids)
        if ids == {2, 3, 4}:
            entered.set()
            assert gate.wait(5)
        return original(lib, plan)
    monkeypatch.setattr(assets, "footprint", blocked)
    try:
        page._show(duplicates.DuplicateReport([first, second], []))
        spin(app, entered.is_set)
        page.list.setCurrentRow(1)
        spin(app, lambda: len(page.members) == 3)
        gate.set()
        settle(app, page)
        assert [member["key"] for member in page.members] == [5, 6, 7]
        assert page._selection_plan["files"] == 2 and page.selected == {6, 7}
        assert calls == [{2, 3, 4}, {6, 7}]
        assert all(pane.isVisible() for pane in page.panes)
    finally:
        gate.set()
        page.shutdown()
        page.deleteLater()
        app.processEvents()


def test_obsolete_group_preparation_cannot_replace_a_new_report(catalogue, app, monkeypatch):
    lib, rows = catalogue
    group = duplicates.DuplicateGroup("old", 10, rows, rows[0]["id"])
    old = duplicates.DuplicateReport([group], [])
    page = make_page(lib)
    original = duplicates.file_review_key
    gate, entered = threading.Event(), threading.Event()
    def blocked(value):
        if value is group:
            entered.set()
            assert gate.wait(5)
        return original(value)
    monkeypatch.setattr(duplicates, "file_review_key", blocked)
    try:
        page._show(old)
        spin(app, entered.is_set)
        current = duplicates.DuplicateReport([], [])
        page._show(current)
        gate.set()
        settle(app, page)
        assert page.report is current and not page.groups and page.list.count() == 0
        assert not page.move_btn.isEnabled()
    finally:
        gate.set()
        page.shutdown()
        page.deleteLater()
        app.processEvents()


def test_unchecking_every_copy_discards_a_pending_plan_failure(catalogue, app, monkeypatch):
    lib, rows = catalogue
    page = make_page(lib)
    gate, entered = threading.Event(), threading.Event()
    def blocked(*_):
        entered.set()
        assert gate.wait(5)
        raise ValueError("obsolete selection failed")
    monkeypatch.setattr(assets, "footprint", blocked)
    try:
        page._show(duplicates.DuplicateReport(
            [duplicates.DuplicateGroup("pair", 10, rows[:2], rows[0]["id"])], []))
        spin(app, entered.is_set)
        page.panes[1].remove_check.setChecked(False)
        assert not page.selected
        gate.set()
        settle(app, page)
        assert "No files will move" in page.selection_note.text()
        assert "obsolete" not in page.selection_note.text()
        assert not page.move_btn.isEnabled()
    finally:
        gate.set()
        page.shutdown()
        page.deleteLater()
        app.processEvents()
