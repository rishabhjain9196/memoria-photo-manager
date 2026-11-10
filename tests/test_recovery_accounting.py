"""Generated fixtures only: accounting never inspects a user's Recovery."""
import os
import stat
import subprocess
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from memoria.engine import actions, config, recovery, roots
from memoria.engine.db import Library, LibraryUnavailable


@pytest.fixture
def small_library(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    lib = Library(home)
    try:
        yield lib
    finally:
        lib.close()


def _batch(lib, name, date="2026-01-01", kind="duplicates"):
    lib.db.execute("INSERT INTO batches VALUES (?,?,?,?, 'applied',0,0)", (name, date, kind, name))


def _record(lib, batch, name, *, source=1, size=1, actual=1, status="done", op="recycle"):
    folder = config.recovery_dir(lib.abspath(roots.key_for(source)))
    destination = folder / batch / name
    if actual is not None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(b"x" * actual)
    src = lib.abspath(roots.key_for(source, name))
    lib.db.execute(
        "INSERT INTO operations(batch_id,seq,op,src,dst,size,status,src_key,dst_key) VALUES (?,0,?,?,?,?,?,?,?)",
        (batch, op, str(src), str(destination), size, status, lib.rel(src, resolve=False),
         lib.rel(destination, resolve=False)))
    return destination


def _mock_sizes(monkeypatch, sizes):
    original = recovery._lstat
    def measure(path):
        result = original(path)
        return SimpleNamespace(st_mode=result.st_mode, st_size=sizes.get(Path(path), result.st_size),
                               st_file_attributes=getattr(result, "st_file_attributes", 0))
    monkeypatch.setattr(recovery, "_lstat", measure)


def test_prior_fifty_plus_five_and_orphan_are_not_last_cleanup(small_library, tmp_path, monkeypatch):
    lib = small_library
    second = tmp_path / "second"
    second.mkdir()
    source = roots.add(lib, second, "External")
    gib = 1024 ** 3
    _batch(lib, "old")
    _batch(lib, "new", "2026-02-01")
    sizes = {
        _record(lib, "old", "old-home.jpg", size=48*gib): 48*gib,
        _record(lib, "old", "old-external.jpg", source=source, size=2*gib): 2*gib,
        _record(lib, "new", "new-home.jpg", size=3*gib): 3*gib,
        _record(lib, "new", "new-external.jpg", source=source, size=2*gib): 2*gib,
    }
    orphan = lib.recovery / "orphan.bin"
    orphan.write_bytes(b"x")
    sizes[orphan] = gib
    # Newer exports and zero-byte metadata are not cleanup footprints.
    _batch(lib, "export", "2026-03-01", "albums")
    lib.db.execute("INSERT INTO operations(batch_id,seq,op,src,dst,size,status) "
                   "VALUES ('export',0,'copy','unused',?,999,'done')", (str(tmp_path / "export.jpg"),))
    lib.db.execute("INSERT INTO operations(batch_id,seq,op,src,size,status) "
                   "VALUES ('new',1,'metadata','unused',0,'done')")
    _mock_sizes(monkeypatch, sizes)
    report = recovery.inspect(lib)
    assert (report.files, report.bytes) == (5, 56*gib)
    assert report.latest_id == "new"
    assert (report.latest.recorded_bytes, report.latest.moved_bytes, report.latest.bytes) == (5*gib,)*3
    assert report.older_bytes == 50*gib
    assert (report.untracked_files, report.untracked_bytes) == (1, gib)
    assert [root.bytes for root in report.roots] == [52*gib, 4*gib]
    assert report.complete and not report.safe_to_empty
    assert actions.recovery_size(lib) == (5, 56*gib)
    assert len(report.roots[0].samples) == 1
    assert orphan.read_bytes() == b"x"


def test_fresh_inspection_neither_reads_originals_nor_creates_recovery(small_library, monkeypatch):
    lib = small_library
    original = lib.root / "original.jpg"
    original.write_bytes(b"untouched")
    real_lstat = recovery._lstat
    def guarded(path):
        assert Path(path) != original
        return real_lstat(path)
    monkeypatch.setattr(recovery, "_lstat", guarded)
    monkeypatch.setattr(actions, "full_hash", lambda *args: pytest.fail("Accounting must not hash originals"))
    report = recovery.inspect(lib)
    assert report.complete and (report.files, report.bytes) == (0, 0)
    assert report.latest is None
    assert not lib.recovery.exists()
    with pytest.raises(ValueError, match="Nothing was created"):
        recovery.inspection_path(lib, 1)
    assert not lib.recovery.exists() and original.read_bytes() == b"untouched"


def test_offline_then_reconnect_uses_recorded_root_keys(tmp_path):
    home, added, moved = (tmp_path / name for name in ("home", "added", "moved"))
    home.mkdir()
    added.mkdir()
    lib = Library(home)
    source = roots.add(lib, added)
    _batch(lib, "cleanup")
    _record(lib, "cleanup", "home.jpg", size=2, actual=2)
    _record(lib, "cleanup", "external.jpg", source=source, size=3, actual=3)
    lib.close()
    added.rename(moved)
    lib = Library(home)
    try:
        offline = recovery.inspect(lib)
        assert (offline.files, offline.bytes) == (1, 2)
        assert not offline.complete and not offline.safe_to_empty
        assert not offline.roots[1].online
        assert offline.latest.uncertain_files == 1 and offline.latest.missing_files == 0
        roots.reconnect(lib, source, moved)
        report = recovery.inspect(lib)
        assert report.complete and report.safe_to_empty
        assert (report.files, report.bytes) == (2, 5)
        assert report.latest.bytes == 5 and report.latest.missing_files == 0
        assert report.roots[1].path == config.recovery_dir(moved)
    finally:
        lib.close()


def test_primary_home_must_be_online(small_library):
    marker = config.app_dir(small_library.root) / roots.MARKER
    original = marker.read_bytes()
    marker.write_text('{"catalogue":"other","source":"other"}')
    try:
        with pytest.raises(LibraryUnavailable):
            recovery.inspect(small_library)
        with pytest.raises(LibraryUnavailable):
            actions.recovery_size(small_library)
    finally:
        marker.write_bytes(original)


def test_missing_changed_and_unknown_outputs_are_distinguished(small_library, monkeypatch):
    lib = small_library
    _batch(lib, "cleanup")
    _record(lib, "cleanup", "missing.jpg", size=7, actual=None)
    _record(lib, "cleanup", "changed.jpg", size=2, actual=4)
    denied = _record(lib, "cleanup", "denied.jpg", size=3, actual=3)
    inaccessible = _record(lib, "cleanup", "blocked\\inside.jpg", size=5, actual=5)
    real_lstat, real_scan = recovery._lstat, recovery.os.scandir
    def measure(path):
        if Path(path) == denied:
            raise PermissionError("fixture stat denied")
        return real_lstat(path)
    def scan(path):
        if recovery._key(Path(path)) == recovery._key(inaccessible.parent):
            raise PermissionError("fixture list denied")
        return real_scan(path)
    monkeypatch.setattr(recovery, "_lstat", measure)
    monkeypatch.setattr(recovery.os, "scandir", scan)
    report = recovery.inspect(lib)
    assert (report.files, report.bytes) == (1, 4)
    assert report.latest.missing_files == 1 and report.latest.missing_bytes == 7
    assert report.latest.changed_files == 1 and report.latest.uncertain_files == 2
    assert report.roots[0].errors == 2
    assert not report.complete and not report.safe_to_empty
    assert "Cannot measure" in "\n".join(report.roots[0].samples)


@pytest.mark.parametrize("failure", [PermissionError, OSError])
def test_unreadable_recovery_is_not_empty(small_library, monkeypatch, failure):
    lib = small_library
    _batch(lib, "cleanup")
    _record(lib, "cleanup", "photo.jpg", size=3, actual=3)
    original = recovery._lstat
    def measure(path):
        if Path(path) == lib.recovery:
            raise failure("fixture storage unavailable")
        return original(path)
    monkeypatch.setattr(recovery, "_lstat", measure)
    report = recovery.inspect(lib)
    assert (report.files, report.bytes) == (0, 0)
    assert not report.complete and not report.safe_to_empty
    assert report.latest.uncertain_files == 1 and report.latest.missing_files == 0


@pytest.mark.parametrize("status", ["pending", "publishing", "published", "undo_pending", "undone", "purged"])
def test_interrupted_and_unexpected_retained_files_need_inspection(small_library, status):
    lib = small_library
    _batch(lib, "cleanup")
    _record(lib, "cleanup", "photo.jpg", size=2, actual=2, status=status)
    report = recovery.inspect(lib)
    assert (report.files, report.bytes, report.latest.bytes) == (1, 2, 2)
    assert report.latest.recorded_bytes == 2
    assert report.latest.moved_bytes == (0 if status in {"pending", "publishing"} else 2)
    assert report.complete and not report.safe_to_empty
    assert report.interrupted_ops == int(status in recovery.INTERRUPTED)


def test_undo_and_purge_update_retained_not_recorded_totals(small_library):
    lib = small_library
    source = lib.root / "photo.jpg"
    source.write_bytes(b"generated")
    plan = [actions.Action("recycle", str(source), size=source.stat().st_size)]
    first = actions.apply(lib, "duplicates", "Generated cleanup", plan)
    assert first.done == 1
    report = recovery.inspect(lib)
    assert report.safe_to_empty and report.latest.bytes == 9
    assert actions.undo(lib, first.batch_id).done == 1
    report = recovery.inspect(lib)
    assert (report.files, report.bytes) == (0, 0)
    assert report.latest.moved_bytes == 9 and report.latest.missing_files == 0
    second = actions.apply(lib, "duplicates", "Generated cleanup again", plan)
    # Destructive validation is restricted to this tiny generated fixture.
    assert actions.empty_recovery(lib, [second.batch_id]) == 1
    report = recovery.inspect(lib)
    assert (report.files, report.bytes) == (0, 0)
    assert report.latest.id == second.batch_id and report.latest.moved_bytes == 9
    assert not report.needs_inspection


def test_holding_files_are_bounded_inspection_samples(small_library):
    lib = small_library
    lib.recovery.mkdir()
    for i in range(recovery.SAMPLE_LIMIT + 5):
        (lib.recovery / f"holding-{i}.memoria-tmp").write_bytes(b"x")
    report = recovery.inspect(lib)
    assert report.untracked_files == recovery.SAMPLE_LIMIT + 5
    assert len(report.roots[0].samples) == recovery.SAMPLE_LIMIT
    assert not report.safe_to_empty
    assert len(list(lib.recovery.iterdir())) == recovery.SAMPLE_LIMIT + 5


def test_other_journaled_contents_do_not_become_latest_cleanup(small_library):
    lib = small_library
    _batch(lib, "cleanup")
    _record(lib, "cleanup", "photo.jpg", size=2, actual=2)
    _batch(lib, "copy", "2026-03-01", "albums")
    _record(lib, "copy", "copy.jpg", size=3, actual=3, op="copy")
    report = recovery.inspect(lib)
    assert report.latest_id == "cleanup" and report.latest.bytes == 2
    assert report.other_bytes == 3 and report.untracked_bytes == 0
    assert report.bytes == 5 and not report.safe_to_empty


def test_junction_targets_are_not_traversed_or_double_counted(small_library, tmp_path):
    lib = small_library
    _batch(lib, "cleanup")
    retained = _record(lib, "cleanup", "inside.jpg", size=3, actual=3)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "outside.jpg").write_bytes(b"not Recovery")
    links = [(lib.recovery / "outside-link", outside), (lib.recovery / "inside-link", retained.parent)]
    try:
        for link, target in links:
            if os.name == "nt":
                result = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)],
                                        capture_output=True, text=True)
                assert result.returncode == 0, result.stderr
            else:
                link.symlink_to(target, target_is_directory=True)
        report = recovery.inspect(lib)
        assert (report.files, report.bytes) == (1, 3)
        assert report.roots[0].skipped_links == 2
        assert not report.complete and not report.safe_to_empty
        assert (outside / "outside.jpg").read_bytes() == b"not Recovery"
    finally:
        for link, _ in links:
            if os.name == "nt":
                if link.exists():
                    os.rmdir(link)
            elif link.is_symlink():
                link.unlink()


def test_file_reparse_points_and_recovery_root_links_are_not_counted(small_library, monkeypatch):
    lib = small_library
    _batch(lib, "cleanup")
    retained = _record(lib, "cleanup", "photo.jpg", size=3, actual=3)
    original = recovery._lstat
    blocked = retained
    def measure(path):
        result = original(path)
        return SimpleNamespace(st_mode=result.st_mode, st_size=result.st_size,
                               st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT if Path(path) == blocked else 0)
    monkeypatch.setattr(recovery, "_lstat", measure)
    for blocked in (retained, lib.recovery, lib.recovery.parent):
        report = recovery.inspect(lib)
        assert (report.files, report.bytes) == (0, 0)
        assert report.roots[0].skipped_links == 1
        assert report.latest.uncertain_files == 1 and report.latest.missing_files == 0
        assert not report.complete and not report.safe_to_empty
    with pytest.raises(ValueError, match="link / junction"):
        recovery.inspection_path(lib, 1)


def test_changed_destination_type_and_ambiguous_journal_are_not_double_counted(small_library):
    lib = small_library
    _batch(lib, "cleanup")
    directory = _record(lib, "cleanup", "directory.jpg", size=3, actual=None)
    directory.mkdir(parents=True)
    _record(lib, "cleanup", "reused.jpg", size=2, actual=2)
    _record(lib, "cleanup", "reused.jpg", size=2, actual=None)
    report = recovery.inspect(lib)
    assert (report.files, report.bytes) == (1, 2)
    assert report.latest.changed_files == 1 and report.latest.missing_files == 0
    assert report.latest.uncertain_files == 2 and report.untracked_bytes == 2
    assert not report.safe_to_empty


def _wait(app, predicate):
    deadline = time.monotonic() + 10
    while not predicate() and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(.01)
    app.processEvents()
    assert predicate()


def test_history_and_overview_agree_and_explain_incomplete_emptying(small_library, tmp_path, monkeypatch):
    from PySide6.QtWidgets import QApplication
    from memoria.ui.pages.history import HistoryPage
    from memoria.ui.pages.overview import OverviewPage, _insights
    from memoria.ui.tasks import TaskRunner
    from memoria.ui.widgets import AppContext, ConfirmDialog, MessageDialog, fmt_size
    app = QApplication.instance() or QApplication([])
    lib = small_library
    second = tmp_path / "second"
    second.mkdir()
    roots.add(lib, second, "Other location")
    _batch(lib, "old")
    _record(lib, "old", "old.jpg", size=3, actual=3)
    _batch(lib, "new", "2026-02-01")
    _record(lib, "new", "new.jpg", size=2, actual=2)
    ctx = AppContext(TaskRunner())
    ctx.set_library(lib)
    page, overview = HistoryPage(ctx), OverviewPage(ctx)
    try:
        page.show()
        _wait(app, lambda: page._accounting_ready and "still measured in Recovery" in page.detail.text())
        assert page._recovery_bytes == 5 and page.empty_btn.isEnabled()
        assert "Cumulative Recovery" in page.rec_label.text()
        assert f"Older cleanups still retained: {fmt_size(3)}" in page.rec_label.text()
        assert f"{fmt_size(2)} still in Recovery" in page.rec_label.text()
        assert "cleanup bytes recorded" in page.detail.text()
        page.recovery_root.setCurrentIndex(1)
        assert page._recovery_bytes == 5 and f"{fmt_size(0)} logical bytes" in page.root_note.text()
        assert "NOT totals, Restore all or Empty Recovery scope" in page.root_note.text()
        data = _insights(lib, {"duplicates": [], "similar": [], "organize": SimpleNamespace(items=[])})
        overview._insights(data)
        assert data["recovery"] == (page._recovery_count, page._recovery_bytes)
        original = recovery._lstat
        def measure(path):
            if Path(path) == lib.recovery:
                raise PermissionError("fixture denied")
            return original(path)
        monkeypatch.setattr(recovery, "_lstat", measure)
        page.refresh()
        assert page.empty_btn.isEnabled()  # A click reviews the block; it does not authorize deletion.
        _wait(app, lambda: page._accounting_ready and "INCOMPLETE" in page.rec_label.text())
        assert page._recovery_bytes == 0 and page.empty_btn.isEnabled()
        monkeypatch.setattr(actions, "empty_recovery", lambda *args, **kwargs: pytest.fail("Must not empty"))
        monkeypatch.setattr(ConfirmDialog, "exec", lambda *_: pytest.fail("Unsafe accounting cannot offer deletion"))
        notices = []
        monkeypatch.setattr(MessageDialog, "exec", lambda self: notices.append(self.windowTitle()) or 0)
        page.empty_btn.click()
        _wait(app, lambda: not ctx.runner.busy and bool(notices))
        assert notices == ["Recovery needs attention before emptying"]
        data = _insights(lib, {"duplicates": [], "similar": [], "organize": SimpleNamespace(items=[])})
        overview._insights(data)
        assert not data["recovery_accounting"].complete
    finally:
        page.shutdown()
        overview.shutdown()
        page.close()
        overview.close()
        page.deleteLater()
        overview.deleteLater()
        app.processEvents()


@pytest.fixture
def history_ui(small_library):
    from PySide6.QtGui import QFont
    from PySide6.QtWidgets import QApplication
    from memoria.ui import theme
    from memoria.ui.pages.history import HistoryPage
    from memoria.ui.tasks import TaskRunner
    from memoria.ui.widgets import AppContext
    app = QApplication.instance() or QApplication([])
    app.setFont(QFont("Segoe UI", 10))
    app.setStyle("Fusion")
    theme.use("dark")
    app.setPalette(theme.qpalette())
    app.setStyleSheet(theme.QSS)
    ctx = AppContext(TaskRunner())
    ctx.set_library(small_library)
    page = HistoryPage(ctx)
    page.resize(1400, 900)
    errors = []
    ctx.runner.error.connect(lambda *args: errors.append(args))
    yield app, ctx, page, errors
    ctx.runner.cancel()
    ctx.runner.wait()
    page.shutdown()
    page.close()
    page.deleteLater()
    app.processEvents()


@pytest.mark.parametrize("decision", ["accept", "cancel", "no_ack"])
def test_empty_click_refreshes_stale_accounting_and_requires_acknowledgement(
        small_library, history_ui, monkeypatch, decision):
    from memoria.ui.widgets import ConfirmDialog
    lib = small_library
    app, ctx, page, errors = history_ui
    _batch(lib, "cleanup")
    destination = _record(lib, "cleanup", "photo.jpg", size=3, actual=3)
    _record(lib, "cleanup", "already-restored.jpg", size=2, actual=None, status="undone")
    original = lib.root / "untouched.jpg"
    original.write_bytes(b"original must remain")
    page.show()
    _wait(app, lambda: page._accounting_ready)
    page._accounting_ready = False  # Cached readiness must not turn a review click into a silent no-op.
    page._empty_control(False)
    confirmations = []
    def confirm(dialog):
        confirmations.append(dialog.windowTitle())
        assert not dialog.ok.isEnabled()
        if decision == "accept":
            dialog.ack.setChecked(True)
        return dialog.DialogCode.Rejected if decision == "cancel" else dialog.DialogCode.Accepted
    monkeypatch.setattr(ConfirmDialog, "exec", confirm)
    page.empty_btn.click()
    _wait(app, lambda: bool(confirmations) and not ctx.runner.busy)
    assert not errors, errors
    assert confirmations == ["Permanently delete files in Recovery?"]
    assert destination.exists() == (decision != "accept")
    assert original.read_bytes() == b"original must remain"
    status = lib.db.execute("SELECT status FROM operations WHERE src LIKE '%photo.jpg'").fetchone()[0]
    assert status == ("purged" if decision == "accept" else "done")


@pytest.mark.parametrize("blocker", ["untracked", "changed", "missing", "interrupted"])
def test_click_explains_actual_recovery_blocker_without_offering_deletion(
        small_library, history_ui, monkeypatch, blocker):
    from memoria.ui.widgets import ConfirmDialog, MessageDialog
    lib = small_library
    app, ctx, page, errors = history_ui
    _batch(lib, "cleanup")
    destination = _record(lib, "cleanup", "photo.jpg", size=3, actual=4 if blocker == "changed" else 3,
                          status="published" if blocker == "interrupted" else "done")
    if blocker == "untracked":
        (lib.recovery / "unknown.bin").write_bytes(b"not attributable")
    elif blocker == "missing":
        _record(lib, "cleanup", "missing.jpg", size=2, actual=None)
    expected = {"untracked": "no unambiguous History match", "changed": "differ in size or type",
                "missing": "missing from Recovery", "interrupted": "interrupted operation"}
    report = recovery.inspect(lib)
    assert any(expected[blocker] in message for message in report.empty_blockers())
    monkeypatch.setattr(ConfirmDialog, "exec", lambda *_: pytest.fail("Cannot confirm unsafe permanent deletion"))
    monkeypatch.setattr(actions, "empty_recovery", lambda *args, **kwargs: pytest.fail("Cannot delete blocked contents"))
    messages = []
    class Explain(MessageDialog):
        def __init__(self, parent, title, summary, details):
            super().__init__(parent, title, summary, details)
            messages.append((title, summary, details))
        def exec(self):
            if blocker == "untracked":
                self.show()
                app.processEvents()
                assert self.grab().save(str(lib.root.parent / "empty-recovery-blocked.png"))
            return self.DialogCode.Accepted
    monkeypatch.setattr("memoria.ui.pages.history.MessageDialog", Explain)
    page.show()
    _wait(app, lambda: page._accounting_ready)
    assert page.empty_btn.isEnabled()
    assert "blocked" in page.empty_status.text()
    page.empty_btn.click()
    _wait(app, lambda: bool(messages) and not ctx.runner.busy)
    assert not errors and destination.exists(), errors
    assert expected[blocker] in messages[0][2]
    assert "Nothing was deleted" in messages[0][1]


def test_recovery_change_during_confirmation_blocks_deletion(small_library, history_ui, monkeypatch):
    from memoria.ui.widgets import ConfirmDialog
    lib = small_library
    app, ctx, page, errors = history_ui
    _batch(lib, "cleanup")
    destination = _record(lib, "cleanup", "photo.jpg", size=3, actual=3)
    extra = lib.recovery / "new-untracked.bin"
    def confirm(dialog):
        dialog.ack.setChecked(True)
        extra.write_bytes(b"new contents")
        return dialog.DialogCode.Accepted
    monkeypatch.setattr(ConfirmDialog, "exec", confirm)
    monkeypatch.setattr(actions, "empty_recovery", lambda *args, **kwargs: pytest.fail("Changed Recovery cannot be emptied"))
    page.show()
    _wait(app, lambda: page._accounting_ready)
    page.empty_btn.click()
    _wait(app, lambda: bool(errors) and not ctx.runner.busy)
    assert "Recovery changed" in errors[0][1]
    assert destination.read_bytes() == b"xxx" and extra.read_bytes() == b"new contents"


def test_empty_review_button_explains_active_work(small_library, history_ui):
    app, ctx, page, _ = history_ui
    ctx.set_indexing(True)
    page.on_busy_changed(True)
    assert not page.empty_btn.isEnabled()
    assert "library work is active" in page.empty_status.text()
    assert "Finish or cancel" in page.empty_btn.toolTip()
    ctx.set_indexing(False)
    page.on_busy_changed(False)
    assert page.empty_btn.isEnabled()
