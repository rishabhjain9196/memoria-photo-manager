"""Explicit duplicate choices never bypass reviewed-file checks or permanent-deletion safeguards."""
import os
import shutil
import sqlite3
import threading

import pytest
from PIL import Image

from memoria.engine import actions, duplicates, scanner, storage
from memoria.engine.db import Library, MIGRATIONS, SCHEMA, SCHEMA_VERSION
from memoria.engine.hashing import full_hash
from memoria.engine.progress import Progress


@pytest.fixture
def library(tmp_path):
    root = tmp_path / "library"
    root.mkdir()
    for folder in ("Left", "Right", "Holder", "Subset"):
        (root / folder).mkdir()
    Image.new("RGB", (32, 24), "red").save(root / "one.jpg")
    for name in ("two.jpg", "three.jpg"):
        shutil.copy2(root / "one.jpg", root / name)
    Image.new("RGB", (32, 24), "blue").save(root / "Left" / "photo.jpg")
    shutil.copy2(root / "Left" / "photo.jpg", root / "Right" / "photo.jpg")
    for folder in ("Left", "Right"):
        (root / folder / "note.txt").write_bytes(b"identical non-media contents")
    (root / "Left" / "empty.jpg").write_bytes(b"")
    (root / "Right" / "Thumbs.db").write_bytes(b"test leftover")
    Image.new("RGB", (32, 24), "green").save(root / "Holder" / "photo.jpg")
    shutil.copy2(root / "Holder" / "photo.jpg", root / "Subset" / "photo.jpg")
    Image.new("RGB", (32, 24), "yellow").save(root / "Holder" / "unique.jpg")
    lib = Library(root)
    scanner.index(lib)
    yield lib
    lib.close()


def snapshot(lib):
    return {str(p.relative_to(lib.root)): p.read_bytes() for p in lib.root.rglob("*")
            if p.is_file() and ".memoria" not in p.parts}


def file_group(report):
    return next(g for g in report.loose_groups() if any(f["rel_path"] == "one.jpg" for f in g.files))


def folder_group(report):
    return next(m for m in report.folders if m.kind == "same")


@pytest.mark.parametrize("all_copies", [False, True])
def test_selected_or_all_files_remain_undoable(library, all_copies):
    before = snapshot(library)
    report = duplicates.find_all(library)
    group = file_group(report)
    chosen = {f["id"] for f in group.files} if all_copies else {group.keeper_id}
    plan = duplicates.plan_cleanup(library, report, files=[group.hash], file_removals={group.hash: chosen})
    assert {a.file_id for a in plan} == chosen
    assert all(bool(a.guards) != all_copies and a.hash == group.hash for a in plan)
    result = actions.apply(library, "duplicates", "Explicit review", plan)
    assert result.done == len(chosen) and not result.failed and not result.skipped
    assert sum(library.abspath(f["rel_path"]).exists() for f in group.files) == 3 - len(chosen)
    assert actions.undo(library, result.batch_id).done == len(chosen)
    assert snapshot(library) == before


@pytest.mark.parametrize("interruption", ["cancel", "changed"])
def test_all_files_keep_changed_or_unfinished_work_safe(library, interruption, monkeypatch):
    report = duplicates.find_all(library)
    group = file_group(report)
    plan = duplicates.plan_cleanup(library, report, files=[group.hash],
                                   file_removals={group.hash: {f["id"] for f in group.files}})
    before = snapshot(library)
    stop = threading.Event()
    if interruption == "changed":
        path = library.abspath(group.files[0]["rel_path"])
        stat = path.stat()
        data = bytearray(path.read_bytes())
        data[-1] ^= 1
        path.write_bytes(data)
        os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
        before[str(path.relative_to(library.root))] = bytes(data)
    if interruption == "cancel":
        move = actions.safe_move
        def move_then_cancel(src, dst):
            move(src, dst)
            stop.set()
        monkeypatch.setattr(actions, "safe_move", move_then_cancel)
    progress = Progress(cancel=stop)
    result = actions.apply(library, "duplicates", "Explicit all", plan, progress)
    assert not result.failed
    if interruption == "cancel":
        assert result.cancelled and result.done == 1
    else:
        assert result.skipped == 1 and result.done == 2 and path.exists()
    assert actions.undo(library, result.batch_id).done == result.done
    assert snapshot(library) == before


@pytest.mark.parametrize("all_folders", [False, True])
def test_selected_or_all_identical_folders_and_undo(library, all_folders):
    before = snapshot(library)
    report = duplicates.find_all(library)
    match = folder_group(report)
    chosen = {f.path for f in match.folders} if all_folders else {match.keeper}
    plan = duplicates.plan_cleanup(library, report, folders=[match.id], folder_removals={match.id: chosen})
    moved = [a for a in plan if a.op == "recycle"]
    assert {a.src for a in moved} == {str(library.abspath(r["rel_path"])) for p in chosen
                                     for r in report.folder_files[p]}
    assert all(a.hash for a in moved if a.src.endswith(("photo.jpg", "note.txt")))
    result = actions.apply(library, "duplicates", "Explicit folders", plan)
    assert not result.failed and not result.skipped
    assert all(not library.abspath(path).exists() for path in chosen)
    assert actions.undo(library, result.batch_id).done == result.done
    assert snapshot(library) == before


def test_all_folders_exclude_new_files_and_skip_changed_files(library):
    report = duplicates.find_all(library)
    match = folder_group(report)
    added = library.root / "Left" / "new.jpg"
    Image.new("RGB", (24, 24), "purple").save(added)
    scanner.scan(library)  # even newly catalogued files are not part of the old explicit-all review
    plan = duplicates.plan_cleanup(library, report, folders=[match.id],
                                   folder_removals={match.id: {f.path for f in match.folders}})
    assert str(added) not in {a.src for a in plan}
    changed = library.root / "Right" / "photo.jpg"
    stat = changed.stat()
    data = bytearray(changed.read_bytes())
    data[-1] ^= 1
    changed.write_bytes(data)
    os.utime(changed, ns=(stat.st_atime_ns, stat.st_mtime_ns))
    formerly_empty = library.root / "Left" / "empty.jpg"
    empty_stat = formerly_empty.stat()
    formerly_empty.write_bytes(b"new contents must not be discarded")
    os.utime(formerly_empty, ns=(empty_stat.st_atime_ns, empty_stat.st_mtime_ns))
    before = snapshot(library)
    result = actions.apply(library, "duplicates", "Explicit all folders", plan)
    assert result.skipped >= 3 and not result.failed
    assert added.exists() and changed.exists() and formerly_empty.exists()
    assert actions.undo(library, result.batch_id).done == result.done
    assert snapshot(library) == before


def test_containing_folder_and_cross_group_survivors_are_protected(library):
    shutil.copy2(library.root / "Left" / "photo.jpg", library.root / "outside.jpg")
    scanner.scan(library)
    report = duplicates.find_all(library)
    inside = next(m for m in report.folders if m.kind == "inside")
    with pytest.raises(ValueError, match="unique"):
        duplicates.plan_cleanup(library, report, folders=[inside.id],
                                 folder_removals={inside.id: {f.path for f in inside.folders}})
    match = folder_group(report)
    group = next(g for g in report.loose_groups() if any(f["rel_path"] == "outside.jpg" for f in g.files))
    plan = duplicates.plan_cleanup(library, report, folders=[match.id], files=[group.hash],
                                   file_removals={group.hash: {f["id"] for f in group.files}})
    assert not any(a.op == "rmdir" for a in plan)  # ordinary folder cleanup must still leave a proven copy
    gone = {a.src for a in plan if a.op == "recycle"}
    assert all(path not in gone for a in plan for path, _ in a.guards)
    result = actions.apply(library, "duplicates", "Mixed choices", plan)
    remaining = [p for p in library.root.rglob("*.jpg") if ".memoria" not in p.parts and full_hash(p) == group.hash]
    assert remaining and not result.failed


def test_kept_choices_persist_but_new_members_are_reviewed_again(library):
    before = snapshot(library)
    report = duplicates.find_all(library)
    file_key = duplicates.file_review_key(file_group(report))
    folder_key = report.folder_review_key(folder_group(report))
    for key in (file_key, folder_key):
        duplicates.remember_keep(library, key, True)
    library.close()
    reopened = Library(library.root)
    try:
        scanner.scan(reopened)
        again = duplicates.find_all(reopened)
        assert duplicates.file_review_key(file_group(again)) == file_key
        assert again.folder_review_key(folder_group(again)) == folder_key
        assert duplicates.kept_choices(reopened) == {file_key, folder_key}
        storage.reset(reopened, storage.ResetOptions())
        assert duplicates.kept_choices(reopened) == {file_key, folder_key}
        assert snapshot(reopened) == before
        shutil.copy2(reopened.root / "one.jpg", reopened.root / "four.jpg")
        shutil.copytree(reopened.root / "Left", reopened.root / "Third")
        scanner.scan(reopened)
        new = duplicates.find_all(reopened)
        assert duplicates.file_review_key(file_group(new)) not in duplicates.kept_choices(reopened)
        assert new.folder_review_key(folder_group(new)) not in duplicates.kept_choices(reopened)
        storage.reset(reopened, storage.ResetOptions(thumbnails=False, analysis=False, videos=False,
                                                     duplicate_choices=True))
        assert not duplicates.kept_choices(reopened)
        assert (reopened.root / "four.jpg").exists()
    finally:
        reopened.close()


def test_version_six_catalogue_upgrades_without_losing_files(tmp_path):
    root = tmp_path / "library"
    data = root / ".memoria"
    data.mkdir(parents=True)
    db = sqlite3.connect(data / "memoria.db")
    db.executescript(SCHEMA)
    for version, statements in MIGRATIONS.items():
        if version <= 6:
            for statement in statements:
                db.execute(statement)
    db.execute("INSERT INTO files(rel_path,folder,name,ext,kind,size,mtime,metadata_version) "
               "VALUES ('kept.jpg','','kept.jpg','.jpg','image',42,1,1)")
    db.execute("PRAGMA user_version=6")
    db.commit()
    db.close()
    lib = Library(root)
    try:
        assert lib.db.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION
        assert lib.file_by_rel("kept.jpg")["metadata_version"] == 1
        assert not duplicates.kept_choices(lib)
    finally:
        lib.close()


def test_history_orders_same_timestamp_actions_by_creation_not_random_id(library):
    with library.transaction() as db:
        db.execute("INSERT INTO batches VALUES ('z-first','2026-01-01 12:00:00','duplicates','First','applied',1,1)")
        db.execute("INSERT INTO batches VALUES ('a-second','2026-01-01 12:00:00','duplicates','Second','applied',1,1)")
    assert [batch["id"] for batch in actions.batches(library)] == ["a-second", "z-first"]


def _wait_review(app, window):
    import time
    from memoria.ui.tasks import LatestCall
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        app.processEvents()
        if not window.runner.active and not any(worker.running for worker in window.findChildren(LatestCall)):
            app.processEvents()
            return
        time.sleep(.01)
    raise AssertionError("Duplicate review did not finish")


def _check_panes(page, keys):
    for pane in page.panes:
        if pane.key is not None and pane.isVisible():
            pane.remove_check.setChecked(pane.key in keys)


def test_review_controls_persistence_and_remove_all_acknowledgement(library, tmp_path, monkeypatch):
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ.setdefault("QT_QPA_FONTDIR", r"C:\Windows\Fonts")
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QFont
    from PySide6.QtWidgets import QApplication
    from memoria.ui import theme
    from memoria.ui.main_window import MainWindow
    from memoria.ui.pages import base
    from memoria.ui.widgets import ConfirmDialog, MessageDialog
    app = QApplication.instance() or QApplication([])
    app.setFont(QFont("Segoe UI", 10))
    theme.use("light")
    app.setStyleSheet(theme.QSS)
    window = MainWindow()
    window.resize(1440, 900)
    window.ctx.set_library(library)
    window._show_library_ui(True)
    window.show()
    window.go("duplicates")
    page = window.page("duplicates")
    report = duplicates.find_all(library)
    page._show(report)
    _wait_review(app, window)

    def select(kind, key):
        index = next(i for i, (k, obj) in enumerate(page.entries) if k == kind and
                     (obj.hash if kind == "file" else obj.id) == key)
        page.list.setCurrentRow(index)
        _wait_review(app, window)

    confirmations = []
    def deny_confirmation(parent, title, summary, details, text, **kwargs):
        confirmations.append((title, kwargs["file_ids"], kwargs["require_ack"]))
        dialog = ConfirmDialog(parent, title, summary, details, text, **kwargs)
        if kwargs["require_ack"]:
            assert kwargs["danger"] and not dialog.ok.isEnabled()
            dialog.ok.click()
            assert dialog.result() != dialog.DialogCode.Accepted
            dialog.ack.setChecked(True)
            assert dialog.ok.isEnabled()
            dialog.show()
            app.processEvents()
            assert dialog.grab().save(str(tmp_path / "duplicates-remove-all-confirm.png"))
        dialog.close()
        dialog.deleteLater()
        return False
    monkeypatch.setattr(base, "confirm", deny_confirmation)
    failures = []
    monkeypatch.setattr(MessageDialog, "exec", lambda dialog: failures.append(dialog.windowTitle()) or 0)
    def idle():
        _wait_review(app, window)
    try:
        group = file_group(report)
        select("file", group.hash)
        _check_panes(page, {group.files[0]["id"]})
        idle()
        page.move_btn.click()
        idle()
        assert confirmations[-1][1] == [group.files[0]["id"]] and not confirmations[-1][2]
        assert page.selected == {group.files[0]["id"]}
        assert not actions.batches(library)
        _check_panes(page, {row["id"] for row in group.files})
        idle()
        page.move_btn.click()
        idle()
        assert len(confirmations[-1][1]) == 3 and confirmations[-1][2]
        assert not actions.batches(library)
        window.lib_label.setText("<b>Sample library</b><br>Generated test media")
        window.toast.hide()
        assert window.grab().save(str(tmp_path / "duplicates-file-choices.png"))
        page.keep_all.click()
        idle()
        assert all(kind != "file" or obj.hash != group.hash for kind, obj in page.entries)
        assert duplicates.file_review_key(group) in duplicates.kept_choices(library)
        page.show_previous.setChecked(True)
        idle()
        select("file", group.hash)
        assert not page.selected
        _check_panes(page, {row["id"] for row in group.files})
        idle()
        page.move_btn.click()
        idle()
        assert duplicates.file_review_key(group) in duplicates.kept_choices(library)  # cancel preserves the keep
        page._show(duplicates.find_all(library))
        idle()
        select("file", group.hash)
        assert not page.selected  # a cancelled removal never replaces the remembered keep

        match = folder_group(page.report)
        select("folder", match.id)
        _check_panes(page, {folder.path for folder in match.folders})
        idle()
        page.move_btn.click()
        idle()
        assert len(confirmations[-1][1]) == sum(f.files for f in match.folders) and confirmations[-1][2]
        window.toast.hide()
        assert window.grab().save(str(tmp_path / "duplicates-folder-choices.png"))
        assert not actions.batches(library)
        page.keep_all.click()
        idle()
        assert page.report.folder_review_key(match) in duplicates.kept_choices(library)
        inside = next(m for m in page.report.folders if m.kind == "inside")
        select("folder", inside.id)
        assert page.selected == {inside.folders[0].path}
        larger = next(pane for pane in page.panes if pane.key == inside.folders[1].path)
        assert "shared files only" in larger.remove_check.text()
        window.ctx.set_indexing(True)
        assert not page.keep_all.isEnabled() and not page.move_btn.isEnabled()
        window.ctx.set_indexing(False)
        library.db.execute("CREATE TEMP TRIGGER reject_keep BEFORE INSERT ON duplicate_kept BEGIN "
                           "SELECT RAISE(ABORT,'test write failure'); END")
        before = duplicates.kept_choices(library)
        page.keep_all.click()
        assert failures == ["Duplicate choice not saved"] and duplicates.kept_choices(library) == before
    finally:
        window.close()
        window.deleteLater()
        app.processEvents()


@pytest.mark.parametrize("quick", [False, True])
def test_group_removal_executes_only_current_group_refreshes_and_undoes(library, tmp_path, monkeypatch, quick):
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ.setdefault("QT_QPA_FONTDIR", r"C:\Windows\Fonts")
    from PySide6.QtWidgets import QApplication
    from memoria.ui.main_window import MainWindow
    from memoria.ui.pages import base, duplicates as duplicate_ui
    from memoria.ui.widgets import ConfirmDialog, MessageDialog
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.resize(1440, 900)
    window.ctx.set_library(library)
    window._show_library_ui(True)
    window.show()
    window.go("duplicates")
    page = window.page("duplicates")
    page._show(duplicates.find_all(library))
    _wait_review(app, window)
    window.lib_label.setText("<b>Sample library</b><br>Generated test media")
    window.toast.hide()
    before = snapshot(library)
    errors, confirmations = [], []
    window.runner.error.connect(lambda *args: errors.append(args))
    monkeypatch.setattr(MessageDialog, "exec", lambda self: 0)

    def confirm(parent, title, summary, details, text, **kwargs):
        confirmations.append((title, kwargs.get("require_ack"), kwargs.get("file_ids")))
        assert not quick, "Quick group actions must not open another confirmation"
        return True
    monkeypatch.setattr(base, "confirm", confirm)

    class QuickConsent(ConfirmDialog):
        allow = False

        def exec(self):
            assert not self.ok.isEnabled() and not self.ack.isChecked()
            if not self.allow:
                return self.DialogCode.Rejected
            self.ack.setChecked(True)
            assert self.ok.isEnabled()
            return self.DialogCode.Accepted
    monkeypatch.setattr(duplicate_ui, "ConfirmDialog", QuickConsent)

    def idle():
        _wait_review(app, window)
        assert not errors, errors

    def select(kind, key):
        index = next(i for i, (k, obj) in enumerate(page.entries) if k == kind and
                     (obj.hash if kind == "file" else obj.id) == key)
        page.list.setCurrentRow(index)
        idle()

    try:
        assert not page.quick_remove.isChecked()
        if quick:
            page.quick_remove.setChecked(True)
            assert not page.quick_remove.isChecked()
            QuickConsent.allow = True
            page.quick_remove.setChecked(True)
            assert page.quick_remove.isChecked() and page.quick_warning.isVisible()
            assert window.grab().save(str(tmp_path / "duplicates-quick-mode.png"))
        group = file_group(page.report)
        select("file", group.hash)
        removed = group.files[0]["rel_path"]
        _check_panes(page, {group.files[0]["id"]})
        idle()
        page.move_btn.click()
        idle()
        assert snapshot(library) == {path: data for path, data in before.items() if path != removed}
        assert len(next(g for g in page.report.loose_groups() if g.hash == group.hash).files) == 2
        first_batch = actions.batches(library)[0]["id"]
        assert window.toast.batch_id == first_batch
        if not quick:
            assert len(confirmations[-1][2]) == 1 and not confirmations[-1][1]

        select("file", group.hash)
        _check_panes(page, {member["key"] for member in page.members})
        idle()
        page.move_btn.click()
        idle()
        assert not any(g.hash == group.hash for g in page.report.loose_groups())
        roots = {f["rel_path"] for f in group.files}
        assert snapshot(library) == {path: data for path, data in before.items() if path not in roots}
        second_batch = actions.batches(library)[0]["id"]
        assert second_batch != first_batch and window.toast.batch_id == second_batch
        if quick:
            assert not confirmations
        else:
            assert len(confirmations[-1][2]) == 2 and confirmations[-1][1]

        assert len(actions.batches(library)) == 2  # no unselected group was executed

        window.undo_batch(second_batch)
        idle()
        window.undo_batch(first_batch)
        idle()
        assert snapshot(library) == before

        for remove_all in (False, True):
            match = folder_group(page.report)
            select("folder", match.id)
            paths = {f.path for f in match.folders} if remove_all else {match.keeper}
            _check_panes(page, paths)
            idle()
            page.move_btn.click()
            idle()
            assert snapshot(library) == {path: data for path, data in before.items()
                                         if not any(path.startswith(folder + os.sep) for folder in paths)}
            assert not any(m.id == match.id for m in page.report.folders)
            batch_id = window.toast.batch_id
            assert batch_id
            window.undo_batch(batch_id)
            idle()
            assert snapshot(library) == before

        if quick:
            group = file_group(page.report)
            select("file", group.hash)
            _check_panes(page, {group.files[0]["id"]})
            idle()
            path = library.abspath(group.files[0]["rel_path"])
            stat = path.stat()
            altered = bytearray(path.read_bytes())
            altered[-1] ^= 1
            path.write_bytes(altered)
            os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
            page.move_btn.click()
            idle()
            assert path.read_bytes() == bytes(altered)
            assert actions.recovery_size(library) == (0, 0)
            assert "skipped" in page.action_note.text()

        fresh_page = duplicate_ui.DuplicatesPage(window.ctx)
        assert not fresh_page.quick_remove.isChecked()  # consent is not persistent
        fresh_page.shutdown()
        fresh_page.deleteLater()
        page.quick_remove.setChecked(False)
        assert not page.quick_warning.isVisible()
    finally:
        window.close()
        window.deleteLater()
        app.processEvents()


def test_subset_panes_remove_common_content_only_even_when_both_are_checked(library, tmp_path, monkeypatch):
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    from PySide6.QtWidgets import QApplication
    from memoria.ui.main_window import MainWindow
    from memoria.ui.pages import base, duplicates as duplicate_ui
    from memoria.ui.widgets import ConfirmDialog
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.resize(1440, 900)
    window.ctx.set_library(library)
    window._show_library_ui(True)
    window.show()
    window.go("duplicates")
    page = window.page("duplicates")
    page._show(duplicates.find_all(library))
    _wait_review(app, window)
    before = snapshot(library)
    prompts, errors = [], []
    window.runner.error.connect(lambda *args: errors.append(args))
    monkeypatch.setattr(base, "confirm", lambda *args, **kwargs: prompts.append(kwargs) or True)
    class Consent(ConfirmDialog):
        def exec(self):
            self.ack.setChecked(True)
            return self.DialogCode.Accepted
    monkeypatch.setattr(duplicate_ui, "ConfirmDialog", Consent)
    try:
        page.quick_remove.setChecked(True)
        assert page.quick_remove.isChecked()
        for both in (False, True):
            match = next(group for group in page.report.folders if group.kind == "inside")
            page.list.setCurrentRow(next(i for i, (kind, group) in enumerate(page.entries)
                                         if kind == "folder" and group.id == match.id))
            _wait_review(app, window)
            assert page.selected == {match.folders[0].path}
            paths = {folder.path for folder in match.folders} if both else {match.folders[1].path}
            _check_panes(page, paths)
            _wait_review(app, window)
            assert "unique" in page.selection_note.text()
            removed = {library.rel(action.src) for action in page._selection_plan["actions"] if action.op == "recycle"}
            assert "Holder\\unique.jpg" not in removed
            assert "Holder\\photo.jpg" in removed
            if both:
                assert "Subset\\photo.jpg" in removed
                window.lib_label.setText("<b>Sample library</b><br>Generated test media")
                assert window.grab().save(str(tmp_path / "duplicates-subset.png"))
            previous = len(prompts)
            page.move_btn.click()
            _wait_review(app, window)
            assert not errors
            assert len(prompts) == previous + 1  # subset review cannot be skipped by Quick remove
            assert bool(prompts[-1]["require_ack"]) == both
            assert snapshot(library) == {path: data for path, data in before.items() if path not in removed}
            assert (library.root / "Holder" / "unique.jpg").exists()
            window.undo_batch(window.toast.batch_id)
            _wait_review(app, window)
            assert not errors and snapshot(library) == before
    finally:
        window.close()
        window.deleteLater()
        app.processEvents()


def test_four_copy_table_moves_only_checked_rows(library, tmp_path, monkeypatch):
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication
    from memoria.ui.main_window import MainWindow
    from memoria.ui.pages import base
    shutil.copy2(library.root / "one.jpg", library.root / "four.jpg")
    scanner.index(library)
    before = snapshot(library)
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.resize(1440, 900)
    window.ctx.set_library(library)
    window._show_library_ui(True)
    window.show()
    window.go("duplicates")
    page = window.page("duplicates")
    page._show(duplicates.find_all(library))
    _wait_review(app, window)
    monkeypatch.setattr(base, "confirm", lambda *args, **kwargs: True)
    try:
        group = file_group(page.report)
        assert len(group.files) == 4
        page.list.setCurrentRow(next(i for i, (kind, obj) in enumerate(page.entries)
                                     if kind == "file" and obj.hash == group.hash))
        _wait_review(app, window)
        assert page.detail.currentWidget() is page.many_view
        chosen = page.copies.topLevelItem(1).data(0, Qt.ItemDataRole.UserRole)
        for index in range(page.copies.topLevelItemCount()):
            item = page.copies.topLevelItem(index)
            item.setCheckState(0, Qt.CheckState.Checked if index == 1 else Qt.CheckState.Unchecked)
        _wait_review(app, window)
        assert page.selected == {chosen["key"]} and page._selection_plan["files"] == 1
        window.lib_label.setText("<b>Sample library</b><br>Generated test media")
        assert window.grab().save(str(tmp_path / "duplicates-many.png"))
        page.move_btn.click()
        _wait_review(app, window)
        assert snapshot(library) == {path: data for path, data in before.items() if path != chosen["path"]}
        window.undo_batch(window.toast.batch_id)
        _wait_review(app, window)
        assert snapshot(library) == before
    finally:
        window.close()
        window.deleteLater()
        app.processEvents()
