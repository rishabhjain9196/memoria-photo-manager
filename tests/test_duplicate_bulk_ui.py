import os
import shutil
import time

import pytest
from PIL import Image

from memoria.engine import actions, duplicates, scanner
from memoria.engine.db import Library


def _idle(app, window):
    from memoria.ui.tasks import LatestCall
    deadline = time.monotonic() + 20
    quiet = None
    while time.monotonic() < deadline:
        app.processEvents()
        if window.runner.busy or any(worker.running for worker in window.findChildren(LatestCall)):
            quiet = None
        elif quiet is None:
            quiet = time.monotonic()
        elif time.monotonic() - quiet > .05:
            return
        time.sleep(.005)
    raise AssertionError("Grouped duplicate UI did not finish")


def _snapshot(lib):
    return {str(path.relative_to(lib.root)): path.read_bytes()
            for path in lib.root.rglob("*") if path.is_file() and ".memoria" not in path.parts}


@pytest.fixture
def library(tmp_path):
    root = tmp_path / "library"
    for folder in ("Camera", "Backup", "Downloads"):
        (root / folder).mkdir(parents=True)
    for name, color in (("trip", "red"), ("party", "blue")):
        Image.new("RGB", (36, 24), color).save(root / "Camera" / f"{name}.jpg")
        shutil.copy2(root / "Camera" / f"{name}.jpg", root / "Backup" / f"{name} copy.jpg")
    Image.new("RGB", (36, 24), "yellow").save(root / "Camera" / "unique-camera.jpg")
    Image.new("RGB", (36, 24), "green").save(root / "Backup" / "unique-backup.jpg")
    for name, color in (("download", "purple"), ("sent", "orange")):
        Image.new("RGB", (36, 24), color).save(root / "Downloads" / f"{name}.jpg")
        shutil.copy2(root / "Downloads" / f"{name}.jpg", root / "Downloads" / f"{name} (1).jpg")
    lib = Library(root)
    scanner.index(lib)
    yield lib
    lib.close()


def _window(lib):
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ.setdefault("QT_QPA_FONTDIR", r"C:\Windows\Fonts")
    from PySide6.QtGui import QFont
    from PySide6.QtWidgets import QApplication
    from memoria.ui import theme
    from memoria.ui.main_window import MainWindow
    app = QApplication.instance() or QApplication([])
    app.setFont(QFont("Segoe UI", 10))
    theme.use("light")
    app.setStyle("Fusion")
    app.setPalette(theme.qpalette())
    app.setStyleSheet(theme.QSS)
    window = MainWindow()
    window.resize(1440, 900)
    window.ctx.set_library(lib)
    window._show_library_ui(True)
    window.show()
    window.go("duplicates")
    page = window.page("duplicates")
    page._show(duplicates.find_all(lib))
    _idle(app, window)
    return app, window, page


def test_folder_cleanup_confirms_only_its_collection_and_undoes(library, tmp_path, monkeypatch):
    from memoria.ui.pages import base
    app, window, page = _window(library)
    before = _snapshot(library)
    errors, confirmations = [], []
    window.runner.error.connect(lambda *args: errors.append(args))
    def accept(parent, title, summary, details, text, **kwargs):
        confirmations.append((title, kwargs["file_ids"], details))
        return True
    monkeypatch.setattr(base, "confirm", accept)
    try:
        assert len(page.entries) == 2 and all(kind == "collection" for kind, _ in page.entries)
        assert not page.report.folders  # Each folder pair has unique files; this is partial overlap.
        index = next(i for i, (_, collection) in enumerate(page.entries) if len(collection.folders) == 1)
        page.list.setCurrentRow(index)
        _idle(app, window)
        assert page._current_collection.folders == ("Downloads",)
        assert page.sets.topLevelItemCount() == 2
        assert page.move_btn.text() == "Move folder group to Recovery..."
        assert page.single_set_btn.isVisible()
        assert "This set only:" in page.selection_note.text()
        for pane in page.panes[:2]:
            assert pane.preview.width() <= pane.preview_scroll.viewport().width()
            assert pane.preview.image.geometry().bottom() < pane.preview.open_btn.mapTo(
                pane.preview, pane.preview.open_btn.rect().topLeft()).y()
        window.lib_label.setText("<b>Sample library</b><br>Generated test media")
        assert window.grab().save(str(tmp_path / "duplicates-folder-grouping.png"))
        page.move_btn.click()
        _idle(app, window)
        assert not errors and len(confirmations) == 1, errors
        assert confirmations[0][0] == "Clean this exact folder group"
        assert len(confirmations[0][1]) == 2
        assert len(actions.batches(library)) == 1
        remaining = _snapshot(library)
        assert len(before) - len(remaining) == 2
        assert {path: data for path, data in before.items() if not path.startswith("Downloads\\")} == {
            path: data for path, data in remaining.items() if not path.startswith("Downloads\\")}
        assert len([path for path in remaining if path.startswith("Downloads\\")]) == 2
        window.undo_batch(window.toast.batch_id)
        _idle(app, window)
        assert not errors and _snapshot(library) == before
    finally:
        window.close()
        window.deleteLater()
        app.processEvents()


def test_clean_all_protects_kept_sets_and_user_overrides_and_always_confirms(library, tmp_path, monkeypatch):
    from memoria.ui.pages import base, duplicates as duplicate_ui
    from memoria.ui.widgets import ConfirmDialog
    app, window, page = _window(library)
    before = _snapshot(library)
    prompts, errors = [], []
    window.runner.error.connect(lambda *args: errors.append(args))
    class Consent(ConfirmDialog):
        def exec(self):
            self.ack.setChecked(True)
            return self.DialogCode.Accepted
    monkeypatch.setattr(duplicate_ui, "ConfirmDialog", Consent)
    permit = False
    def confirm(parent, title, summary, details, text, **kwargs):
        prompts.append((title, kwargs["file_ids"]))
        if title == "Clean all exact duplicate groups":
            dialog = ConfirmDialog(parent, title, summary, details, text, **kwargs)
            dialog.show()
            app.processEvents()
            assert dialog.grab().save(str(tmp_path / "duplicates-clean-all-confirm.png"))
            dialog.close()
            dialog.deleteLater()
        return permit
    monkeypatch.setattr(base, "confirm", confirm)
    try:
        index = next(i for i, (_, collection) in enumerate(page.entries) if len(collection.folders) == 2)
        page.list.setCurrentRow(index)
        _idle(app, window)
        kept_group = page._current_group[1]
        kept_paths = {row["rel_path"] for row in kept_group.files}
        page.keep_all.click()
        _idle(app, window)
        page.show_previous.setChecked(True)
        _idle(app, window)
        index = next(i for i, (_, collection) in enumerate(page.entries) if len(collection.folders) == 1)
        page.list.setCurrentRow(index)
        _idle(app, window)
        override_group = page._current_group[1]
        chosen_keeper = next(member for member in page.members if not member["recommended"])
        for pane in page.panes:
            if pane.key is not None and pane.isVisible():
                pane.remove_check.setChecked(pane.key != chosen_keeper["key"])
        _idle(app, window)
        page.quick_remove.setChecked(True)
        assert page.quick_remove.isChecked()
        page.clean_all_btn.click()
        _idle(app, window)
        assert not errors and len(prompts) == 1 and _snapshot(library) == before
        assert duplicates.file_review_key(kept_group) in duplicates.kept_choices(library)
        permit = True
        page.clean_all_btn.click()
        _idle(app, window)
        assert not errors and len(prompts) == 2, errors
        assert prompts[-1][0] == "Clean all exact duplicate groups"
        remaining = _snapshot(library)
        assert len(before) - len(remaining) == 3
        assert kept_paths <= remaining.keys() and chosen_keeper["path"] in remaining
        for group in page.report.groups:
            assert len(group.files) >= 2  # only deliberately kept duplicates remain after refresh
        assert (library.root / "Camera" / "unique-camera.jpg").exists()
        assert (library.root / "Backup" / "unique-backup.jpg").exists()
        window.undo_batch(window.toast.batch_id)
        _idle(app, window)
        assert not errors and _snapshot(library) == before
        assert duplicates.file_review_key(kept_group) in duplicates.kept_choices(library)
    finally:
        window.close()
        window.deleteLater()
        app.processEvents()


def test_folder_collection_does_not_remove_copies_hidden_by_another_folder_match(library, monkeypatch):
    from memoria.ui.pages import base
    shutil.copytree(library.root / "Backup", library.root / "Mirror")
    scanner.index(library)
    before = _snapshot(library)
    app, window, page = _window(library)
    errors = []
    window.runner.error.connect(lambda *args: errors.append(args))
    monkeypatch.setattr(base, "confirm", lambda *args, **kwargs: True)
    try:
        assert page.report.folders
        index = next(i for i, (kind, collection) in enumerate(page.entries)
                     if kind == "collection" and len(collection.folders) == 2)
        page.list.setCurrentRow(index)
        _idle(app, window)
        displayed_paths = {row["rel_path"] for group in page._current_collection.groups for row in group.files}
        hashes = {group.hash for group in page._current_collection.groups}
        hidden_paths = {row["rel_path"] for group in page.report.groups if group.hash in hashes
                        for row in group.files} - displayed_paths
        assert hidden_paths
        page.move_btn.click()
        _idle(app, window)
        assert not errors, errors
        after = _snapshot(library)
        assert hidden_paths <= after.keys()
        assert set(before) - set(after) <= displayed_paths
        assert len(before) - len(after) == 2
        window.undo_batch(window.toast.batch_id)
        _idle(app, window)
        assert not errors and _snapshot(library) == before
    finally:
        window.close()
        window.deleteLater()
        app.processEvents()


@pytest.mark.parametrize("single_set", [False, True])
def test_group_and_explicit_set_actions_have_distinct_scopes(library, monkeypatch, single_set):
    from memoria.ui.pages import base
    app, window, page = _window(library)
    before = _snapshot(library)
    errors, confirmations = [], []
    window.runner.error.connect(lambda *args: errors.append(args))
    monkeypatch.setattr(base, "confirm",
                        lambda parent, title, *args, **kwargs: confirmations.append(title) or True)
    try:
        page.list.setCurrentRow(next(i for i, (_, collection) in enumerate(page.entries)
                                     if len(collection.folders) == 1))
        _idle(app, window)
        current_paths = {row["rel_path"] for row in page._current_group[1].files}
        if single_set:
            page.single_set_btn.click()
        else:
            for pane in page.panes:
                if pane.key is not None and pane.isVisible():
                    pane.remove_check.setChecked(False)
            _idle(app, window)
            assert page.move_btn.isEnabled() and not page.single_set_btn.isEnabled()
            assert "other sets" in page.selection_note.text()
            page.move_btn.click()
        _idle(app, window)
        assert not errors and len(confirmations) == 1, errors
        assert confirmations[0] == ("Move selected duplicate content to Recovery" if single_set else
                                    "Clean this exact folder group")
        after = _snapshot(library)
        removed = set(before) - set(after)
        assert len(removed) == 1 and len(actions.batches(library)) == 1
        if single_set:
            assert removed <= current_paths
        else:
            assert not removed.intersection(current_paths)
            assert all(path.startswith("Downloads\\") for path in removed)
        window.undo_batch(window.toast.batch_id)
        _idle(app, window)
        assert not errors and _snapshot(library) == before
    finally:
        window.close()
        window.deleteLater()
        app.processEvents()


def _add_different_edit_sidecars(lib):
    for folder in ("Camera", "Backup", "Downloads"):
        for photo in (lib.root / folder).glob("*.jpg"):
            if not photo.name.startswith("unique"):
                photo.with_suffix(".AAE").write_bytes(("unique edit " + str(photo.relative_to(lib.root))).encode())
    scanner.index(lib)


@pytest.mark.parametrize("all_groups", [False, True])
def test_linked_bulk_review_handles_the_entire_scope_in_one_batch(library, tmp_path, monkeypatch, all_groups):
    from memoria.ui import duplicate_cleanup_review as review_ui
    from memoria.ui.pages import base
    _add_different_edit_sidecars(library)
    before = _snapshot(library)
    app, window, page = _window(library)
    errors, reviews, confirmations = [], [], []
    window.runner.error.connect(lambda *args: errors.append(args))
    class Review(review_ui.CleanupReviewDialog):
        def exec(self):
            self.show()
            app.processEvents()
            assert not self.plan.actions and self.plan.linked_skipped > 0
            assert not self.go_btn.isEnabled()
            self.include_linked.setChecked(True)
            _idle(app, window)
            assert self._valid and not self._loading, self.status.text()
            assert len(self.plan.actions) == (8 if all_groups else 4)
            unmatched = [part for part in self.plan.review_parts if part["unmatched"]]
            assert len(unmatched) == (4 if all_groups else 2)
            assert not self.go_btn.isEnabled() and self.ack.isVisible()
            with pytest.raises(ValueError, match="Acknowledge"):
                self.selected_plan()
            reviews.append(len(self.plan.actions))
            self.ack.setChecked(True)
            assert self.go_btn.isEnabled()
            assert self.grab().save(str(tmp_path / "duplicate-linked-bulk-review.png"))
            self.go_btn.click()
            return self.result()
    monkeypatch.setattr(review_ui, "CleanupReviewDialog", Review)
    monkeypatch.setattr(base, "confirm", lambda *args, **kwargs: confirmations.append(kwargs) or True)
    try:
        page.list.setCurrentRow(next(i for i, (_, collection) in enumerate(page.entries)
                                     if len(collection.folders) == 1))
        _idle(app, window)
        (page.clean_all_btn if all_groups else page.move_btn).click()
        _idle(app, window)
        assert not errors, errors
        assert reviews == [8 if all_groups else 4]
        assert len(confirmations) == 1 and confirmations[0]["require_ack"]
        assert len(actions.batches(library)) == 1
        remaining = _snapshot(library)
        assert len(before) - len(remaining) == (8 if all_groups else 4)
        if not all_groups:
            assert all(path.startswith("Downloads\\") for path in set(before) - set(remaining))
        for path, data in before.items():
            if "unique-" in path:
                assert remaining[path] == data
        window.undo_batch(window.toast.batch_id)
        _idle(app, window)
        assert not errors and _snapshot(library) == before
    finally:
        window.close()
        window.deleteLater()
        app.processEvents()


def test_empty_bulk_plan_explains_protected_sets_instead_of_silently_returning(library, monkeypatch):
    from memoria.ui.widgets import MessageDialog
    app, window, page = _window(library)
    notices = []
    monkeypatch.setattr(MessageDialog, "exec", lambda self: notices.append(self.windowTitle()) or self.DialogCode.Accepted)
    try:
        for group in page.report.groups:
            duplicates.remember_keep(library, duplicates.file_review_key(group), True)
        before = _snapshot(library)
        page.clean_all_btn.click()
        _idle(app, window)
        assert notices == ["No copies are eligible for this cleanup"]
        assert "Nothing moved" in page.action_note.text()
        assert not actions.batches(library) and _snapshot(library) == before
    finally:
        window.close()
        window.deleteLater()
        app.processEvents()


def test_cancelling_combined_linked_review_moves_nothing(library, monkeypatch):
    from memoria.ui import duplicate_cleanup_review as review_ui
    from memoria.ui.pages import base
    _add_different_edit_sidecars(library)
    before = _snapshot(library)
    app, window, page = _window(library)
    class CancelReview(review_ui.CleanupReviewDialog):
        def exec(self):
            self.show()
            self.include_linked.setChecked(True)
            _idle(app, window)
            assert self.plan.actions and not self.go_btn.isEnabled()
            with pytest.raises(ValueError, match="Acknowledge"):
                self.selected_plan()
            return self.DialogCode.Rejected
    monkeypatch.setattr(review_ui, "CleanupReviewDialog", CancelReview)
    monkeypatch.setattr(base, "confirm", lambda *args, **kwargs: pytest.fail("Cancelled review cannot execute"))
    try:
        page.clean_all_btn.click()
        _idle(app, window)
        assert _snapshot(library) == before and not actions.batches(library)
        assert "cancelled" in page.action_note.text()
    finally:
        window.close()
        window.deleteLater()
        app.processEvents()
