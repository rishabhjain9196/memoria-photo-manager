"""Large synthetic duplicate reviews stay bounded without changing action scope."""
import os
import threading
import time

os.environ["QT_QPA_PLATFORM"] = "offscreen"

import pytest
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QApplication

from memoria.engine import duplicates
from memoria.engine.db import Library
from memoria.ui.pages.duplicates import DuplicatesPage, GROUP_PAGE, MAX_CONTENTS
from memoria.ui.tasks import TaskRunner
from memoria.ui.widgets import AppContext


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def spin(app, predicate, timeout=20):
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


def context(lib):
    ctx = AppContext(TaskRunner())
    ctx.set_library(lib)
    return ctx


def settle(app, page):
    spin(app, lambda: not page.review_bg.running and not page.contents_bg.running)


def test_100k_review_group_paging_preserves_keeps_bulk_scope_and_direct_removal(catalogue, app, monkeypatch):
    lib, rows = catalogue
    groups = [duplicates.DuplicateGroup("large", 10, rows[:99_000], rows[0]["id"])]
    groups.extend(duplicates.DuplicateGroup(f"pair-{i}", 10, rows[i:i + 2], rows[i]["id"])
                  for i in range(99_000, 100_000, 2))
    report = duplicates.DuplicateReport(groups, [])
    page = DuplicatesPage(context(lib))
    reads = []
    monkeypatch.setattr(page.ctx.thumbs, "get", lambda fid: reads.append(fid))
    calls = []
    monkeypatch.setattr(page, "_remove_group", lambda kind, group, targets: calls.append((kind, group.hash, targets)))
    original = page._build_review
    workers = []
    gui_thread = threading.get_ident()

    def delayed(*args):
        workers.append(threading.get_ident())
        time.sleep(.12)
        return original(*args)

    monkeypatch.setattr(page, "_build_review", delayed)
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
        assert len(ticks) >= 5 and all(worker != gui_thread for worker in workers)
        assert len(page.visible_groups) == 501
        assert page.list.count() <= GROUP_PAGE + 2
        assert len(page.grid.items()) == MAX_CONTENTS
        assert len(page._chosen()[1]) == 501 and not reads
        page._file_step(1)
        selected = page.grid.items()[3]
        assert selected["id"] == 504
        page.grid.setCurrentIndex(page.grid.model_.index(3))
        page._choose_file("one")
        assert calls[-1] == ("file", "large", {504})
        page._choose_file("all")
        assert calls[-1][1] == "large" and len(calls[-1][2]) == 99_000
        assert page._file_targets(groups[0]) != calls[-1][2], "Direct removal must not rewrite the bulk plan"
        page._group_step(1)
        assert page.group_offset == GROUP_PAGE
        page.list.setCurrentRow(17)
        selected_key = page._current_key()
        page.list.currentItem().setCheckState(Qt.CheckState.Unchecked)
        assert selected_key[1] not in page.included
        settle(app, page)
        assert page._current_key() == selected_key and page.group_offset == GROUP_PAGE
        assert len(page._chosen()[1]) == 500
        page._group_step(1)
        assert page.list.count() == 102
        page._group_step(-1)
        assert page._current_key() == selected_key
        page._set_all(False)
        settle(app, page)
        assert page._chosen() == ([], [])
        page._set_all(True)
        settle(app, page)
        assert len(page._chosen()[1]) == 501
        page._group_step(-1)
        page.list.setCurrentRow(1)
        page._choose_file("keep")
        settle(app, page)
        assert groups[0].hash not in page.included and len(page.visible_groups) == 500
        page.show_previous.setChecked(True)
        settle(app, page)
        assert len(page.visible_groups) == 501
        page._set_all(True)
        settle(app, page)
        assert groups[0].hash not in page.included
        assert "Across all pages" in page.summary.text()
    finally:
        timer.stop()
        page.shutdown()
        page.deleteLater()
        app.processEvents()
        duplicates.remember_keep(lib, duplicates.file_review_key(groups[0]), False)


def test_folder_pages_bound_queries_coalesce_delayed_reads_and_reject_stale_results(catalogue, app, monkeypatch):
    lib, rows = catalogue
    folders = [duplicates.FolderInfo("Large", files=100_000, others=100_000, other_bytes=1_000_000)]
    folders.extend(duplicates.FolderInfo(f"Folder{i:03}", files=1, others=1, other_bytes=10)
                   for i in range(1, 650))
    match = duplicates.FolderMatch("same", folders, "Large")
    report = duplicates.DuplicateReport([], [match],
        folder_files={folder.path: rows if folder.path == "Large" else [] for folder in folders},
        folder_signatures={folder.path: "synthetic-proof" for folder in folders})
    page = DuplicatesPage(context(lib))
    original = page._folder_rows
    gate, entered = threading.Event(), threading.Event()
    calls, sizes, thread_ids = [], [], []

    def delayed(lib, path, offset):
        calls.append((path, offset))
        thread_ids.append(threading.get_ident())
        entered.set()
        assert gate.wait(5)
        total, result = original(lib, path, offset)
        sizes.append(len(result))
        return total, result

    monkeypatch.setattr(page, "_folder_rows", delayed)
    try:
        page._show(report)
        spin(app, entered.is_set)
        assert page.table.topLevelItemCount() == MAX_CONTENTS
        page.table.setCurrentItem(page.table.topLevelItem(3))
        page.table.setCurrentItem(page.table.topLevelItem(0))
        assert len(calls) == 1
        gate.set()
        settle(app, page)
        assert [path for path, _ in calls] == ["Folder001", "Large"]
        assert all(size <= MAX_CONTENTS for size in sizes)
        assert all(thread != threading.get_ident() for thread in thread_ids)
        assert len(page.f_grid.items()) == MAX_CONTENTS
        assert "100,000" in page.f_contents.text() and page.f_grid.items()[0]["id"] == 1
        page._contents_step(1)
        settle(app, page)
        assert page.f_grid.items()[0]["id"] == 501
        page._folder_step(1)
        settle(app, page)
        assert page.table.topLevelItemCount() == 150
        assert "650" in page.folder_scope.text()
        page._folder_step(-1)
        settle(app, page)
        gate.clear()
        entered.clear()
        page.table.setCurrentItem(page.table.topLevelItem(0))
        spin(app, entered.is_set)
        page.ctx.library_modified.emit()
        gate.set()
        settle(app, page)
        assert not page.f_grid.items(), "An obsolete generation must not repaint the folder contents"
    finally:
        gate.set()
        page.shutdown()
        page.deleteLater()
        app.processEvents()


def test_obsolete_large_review_cannot_replace_a_new_report(catalogue, app, monkeypatch):
    lib, rows = catalogue
    old = duplicates.DuplicateReport(
        [duplicates.DuplicateGroup("old", 10, rows, rows[0]["id"])], [])
    page = DuplicatesPage(context(lib))
    original = page._build_review
    gate, entered = threading.Event(), threading.Event()

    def delayed(report, *args):
        if report is old:
            entered.set()
            assert gate.wait(5)
        return original(report, *args)

    monkeypatch.setattr(page, "_build_review", delayed)
    try:
        page._show(old)
        spin(app, entered.is_set)
        current = duplicates.DuplicateReport([], [])
        page._show(current)
        gate.set()
        settle(app, page)
        assert page.report is current
        assert page.list.count() == 0 and not page.visible_groups
        assert page.stack.currentWidget() is page.none
    finally:
        gate.set()
        page.shutdown()
        page.deleteLater()
        app.processEvents()
