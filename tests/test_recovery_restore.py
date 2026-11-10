"""Restore only generated tiny fixtures; never inspect a user's media."""
import json
import os
import stat
import subprocess
from dataclasses import replace
from pathlib import Path

import pytest

from memoria.engine import actions, albums, assets, batch, config, organisation, recovery, roots, scanner
from memoria.engine import recovery_restore as restore
from memoria.engine.db import Library
from memoria.engine.progress import Progress


BATCH = "20261110-121314-abcdef"


@pytest.fixture
def lib(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    value = Library(home)
    try:
        yield value
    finally:
        value.close()


def stored(lib, relative="Trip\\photo.jpg", *, container=BATCH, data=b"generated", root=1):
    folder = config.recovery_dir(lib.abspath(roots.key_for(root)))
    path = folder / container / relative if container else folder / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def recycle(lib, names=("Trip\\photo.jpg",), *, merge=None):
    planned = []
    for name in names:
        source = lib.root / name
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_bytes(b"generated " + name.encode())
    scanner.scan(lib)
    for name in names:
        row = dict(lib.file_by_rel(name))
        planned.append(actions.Action("recycle", str(lib.root / name), size=row["size"],
                                      mtime=row["mtime"], file_id=row["id"], merge_into=merge))
    prepared = assets.prepare(lib, planned, "duplicates")
    result = actions.apply(lib, "duplicates", "Generated removal", prepared.actions, companions_reviewed=True)
    assert result.failed == result.skipped == 0
    return result


def test_preview_is_stat_only_and_never_mutates(lib, monkeypatch):
    source = stored(lib)
    before = lib.db.total_changes
    monkeypatch.setattr(restore, "_fingerprint", lambda *args: pytest.fail("No preview hashing"))
    monkeypatch.setattr(actions, "full_hash", lambda *args: pytest.fail("No preview hashing"))
    monkeypatch.setattr(roots, "check", lambda *args: pytest.fail("No mutating root checks"))
    plan = restore.preview(lib)
    assert lib.db.total_changes == before
    assert len(plan.items) == 1 and not plan.errors and not plan.offline_roots
    item = plan.items[0]
    assert item.source == source and item.target == lib.root / "Trip" / "photo.jpg"
    assert item.provenance == "inferred" and item.operation_id is None and not item.issue
    assert source.read_bytes() == b"generated"
    assert not list(lib.db.execute("SELECT id FROM batches"))


def test_empty_preview_does_not_create_recovery(lib):
    assert not lib.recovery.exists()
    assert not restore.preview(lib).items
    assert not lib.recovery.exists()


def test_logged_restore_preserves_identity_organisation_and_only_its_merge(lib):
    source, keeper = lib.root / "source.jpg", lib.root / "keeper.jpg"
    source.write_bytes(b"generated")
    keeper.write_bytes(b"generated")
    scanner.scan(lib)
    source_id = lib.file_by_rel("source.jpg")["id"]
    keeper_id = lib.file_by_rel("keeper.jpg")["id"]
    album = albums.create(lib, "Trip", [source_id])
    organisation.edit(lib, [source_id], rating=5, add_tags=["Travel"], favorite=True)
    before = organisation.state(lib, source_id)
    keeper_before = organisation.state(lib, keeper_id)
    removed = actions.apply(lib, "duplicates", "Generated", [
        actions.Action("recycle", str(source), size=9, file_id=source_id, merge_into=keeper_id)])
    assert removed.done == 1 and organisation.state(lib, keeper_id) != keeper_before
    plan = restore.preview(lib)
    assert plan.items[0].provenance == "history"
    result = restore.execute(lib, plan)
    assert (result.restored, result.bytes, result.failed, result.skipped) == (1, 9, 0, 0), result.messages
    assert lib.file(source_id)["rel_path"] == "source.jpg"
    assert organisation.state(lib, source_id) == before
    assert organisation.state(lib, keeper_id) == keeper_before
    assert album in organisation.state(lib, source_id)["albums"]
    assert source.read_bytes() == keeper.read_bytes() == b"generated"


def test_unlogged_preserves_hierarchy_and_adoption_is_not_cleanup(lib):
    first = stored(lib, "Trip\\Day 1\\photo.jpg", data=b"photo")
    second = stored(lib, "Trip\\Day 2\\clip.mov", data=b"video")
    unknown = stored(lib, "unknown.bin", container="", data=b"untouched")
    result = restore.execute(lib, restore.preview(lib))
    assert (result.restored, result.bytes, result.skipped, result.failed) == (2, 10, 1, 0), result.messages
    assert (lib.root / "Trip" / "Day 1" / "photo.jpg").read_bytes() == b"photo"
    assert (lib.root / "Trip" / "Day 2" / "clip.mov").read_bytes() == b"video"
    assert not first.exists() and not second.exists() and unknown.read_bytes() == b"untouched"
    assert {row[0] for row in lib.db.execute("SELECT kind FROM batches")} == {"recovery_import"}
    for op in lib.db.execute("SELECT * FROM operations"):
        assert op["status"] == "undone" and op["hash"]
        assert json.loads(op["reason"])["adoption"]
    report = recovery.inspect(lib)
    assert report.latest_id is None and report.bytes == 9
    assert not lib.files()  # No invented metadata or automatic media decoding.
    scanner.scan(lib)
    assert len(lib.files()) == 2


@pytest.mark.parametrize("container", ["", "unknown-folder", "20260230-121314-abcdef", "20261110-bogus-abcdef"])
def test_ambiguous_layout_requires_explicit_group_mapping(lib, container):
    source = stored(lib, "photo.jpg", container=container)
    plan = restore.preview(lib)
    assert plan.items[0].target is None and plan.items[0].issue
    base = lib.root / "Chosen"
    mapped = restore.map_destination(lib, plan, plan.items[0].mapping_group, base)
    assert mapped.items[0].provenance == "manual" and not mapped.items[0].issue
    assert plan.items[0].target is None and not base.exists()
    assert restore.execute(lib, mapped).restored == 1
    assert (base / "photo.jpg").read_bytes() == b"generated" and not source.exists()


@pytest.mark.parametrize("decision", ["rename", "skip", "cancel"])
def test_existing_original_conflicts_never_overwrite(lib, decision):
    source = stored(lib, "photo.jpg")
    original = lib.root / "photo.jpg"
    original.write_bytes(b"user original")
    calls = []
    def resolve(conflict):
        calls.append(conflict)
        return decision
    result = restore.execute(lib, restore.preview(lib), resolve_conflict=resolve)
    assert len(calls) == 1
    assert calls[0].folder == str(lib.root)
    assert calls[0].sources == [str(source)] and calls[0].targets == [str(original)]
    assert original.read_bytes() == b"user original"
    assert result.cancelled == (decision == "cancel")
    assert result.restored == int(decision == "rename")
    assert source.exists() == (decision != "rename")
    if decision == "rename":
        assert (lib.root / "photo (2).jpg").read_bytes() == b"generated"
    else:
        assert result.skipped == 1 and not lib.db.execute("SELECT id FROM batches").fetchone()


@pytest.mark.parametrize("logged", [False, True])
@pytest.mark.parametrize("decision", ["rename", "skip", "cancel"])
def test_linked_collision_is_one_decision_with_common_suffix(lib, logged, decision):
    names = ("IMG.jpg", "IMG.mov", "IMG.jpg.xmp", "IMG.aae", "IMG.cr2")
    if logged:
        recycle(lib, names)
    else:
        for name in names:
            stored(lib, name)
    original = lib.root / "IMG.mov"
    original.write_bytes(b"existing")
    calls = []
    result = restore.execute(lib, restore.preview(lib), resolve_conflict=lambda conflict: calls.append(conflict) or decision)
    assert len(calls) == 1 and len(calls[0].sources) == len(names)
    assert result.restored == (len(names) if decision == "rename" else 0), result.messages
    assert original.read_bytes() == b"existing"
    for name in names:
        assert (lib.root / name.replace("IMG", "IMG (2)", 1)).exists() == (decision == "rename")
    if decision != "rename":
        assert len(restore.preview(lib).items) == len(names)


def test_callback_owns_folder_and_all_conflict_scope(lib):
    for name in ("A\\one.jpg", "A\\two.jpg", "B\\one.jpg"):
        stored(lib, name)
        target = lib.root / name
        target.parent.mkdir(exist_ok=True)
        target.write_bytes(b"original")
    calls, prompts, cache = [], [], {}
    def resolve(conflict):
        calls.append(conflict.folder)
        if conflict.folder not in cache:
            prompts.append(conflict.folder)
            cache[conflict.folder] = "rename" if Path(conflict.folder).name == "A" else "skip"
        return cache[conflict.folder]
    result = restore.execute(lib, restore.preview(lib), resolve_conflict=resolve)
    assert result.restored == 2 and result.skipped == 1
    assert len(calls) == 3 and len(prompts) == 2
    # A new execution does not retain policy in the engine.
    result = restore.execute(lib, restore.preview(lib), resolve_conflict=lambda conflict: "rename")
    assert result.restored == 1


def test_changed_recovery_source_after_preview_is_left_in_place(lib):
    source = stored(lib)
    plan = restore.preview(lib)
    source.write_bytes(b"changed after preview")
    result = restore.execute(lib, plan)
    assert result.restored == 0 and result.skipped == 1
    assert source.read_bytes() == b"changed after preview"
    assert not lib.db.execute("SELECT id FROM batches").fetchone()


def test_logged_changed_content_with_same_size_is_not_restored(lib):
    recycle(lib, ["photo.jpg"])
    item = restore.preview(lib).items[0]
    stamp = item.source.stat()
    item.source.write_bytes(b"x" * item.size)
    os.utime(item.source, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
    result = restore.execute(lib, restore.preview(lib))
    assert result.restored == 0 and result.skipped == 1
    assert not (lib.root / "photo.jpg").exists()
    assert item.source.exists()


def test_collision_during_dialog_and_late_publication_are_not_overwritten(lib, monkeypatch):
    source = stored(lib, "photo.jpg")
    original = lib.root / "photo.jpg"
    publish = restore._publish
    calls = []
    injected = False
    def race(src, dst):
        nonlocal injected
        if not injected:
            injected = True
            dst.write_bytes(b"late original")
        return publish(src, dst)
    def resolve(conflict):
        calls.append(conflict)
        (lib.root / "photo (2).jpg").write_bytes(b"appeared during dialog")
        return "rename"
    monkeypatch.setattr(restore, "_publish", race)
    result = restore.execute(lib, restore.preview(lib), resolve_conflict=resolve)
    assert result.restored == 1 and not result.failed, result.messages
    assert len(calls) == 1 and not source.exists()
    assert original.read_bytes() == b"late original"
    assert (lib.root / "photo (2).jpg").read_bytes() == b"appeared during dialog"
    assert (lib.root / "photo (3).jpg").read_bytes() == b"generated"


@pytest.mark.parametrize("unsafe", ["..\\outside", ".memoria\\bad", "sub\\..\\bad"])
def test_mapping_refuses_traversal_and_app_storage(lib, unsafe):
    source = stored(lib, "photo.jpg", container="")
    plan = restore.preview(lib)
    with pytest.raises(ValueError):
        restore.map_destination(lib, plan, plan.items[0].mapping_group, lib.root / unsafe)
    assert source.exists()


def test_mapping_refuses_unregistered_root_and_forged_target(lib, tmp_path):
    source = stored(lib, "photo.jpg")
    plan = restore.preview(lib)
    with pytest.raises(ValueError, match="registered"):
        restore.map_destination(lib, plan, plan.items[0].mapping_group, tmp_path / "outside")
    forged = restore.RestorePlan([replace(plan.items[0], target=source)])
    result = restore.execute(lib, forged)
    assert result.restored == 0 and result.skipped == 1 and source.exists()
    assert not lib.db.execute("SELECT id FROM batches").fetchone()


def test_junction_sources_and_destination_parents_are_refused(lib, tmp_path):
    source = stored(lib, "Linked\\photo.jpg")
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "untouched.jpg").write_bytes(b"original")
    target_link = lib.root / "Linked"
    recovery_link = lib.recovery / "linked-recovery"
    try:
        for link in (target_link, recovery_link):
            if os.name == "nt":
                created = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(outside)],
                                         capture_output=True, text=True)
                assert created.returncode == 0, created.stderr
            else:
                link.symlink_to(outside, target_is_directory=True)
        plan = restore.preview(lib)
        assert len(plan.items) == 1 and plan.items[0].issue and plan.errors
        result = restore.execute(lib, plan)
        assert result.restored == 0 and result.skipped == 1
        assert source.exists() and (outside / "untouched.jpg").read_bytes() == b"original"
        assert not (outside / "photo.jpg").exists()
    finally:
        for link in (target_link, recovery_link):
            if os.path.lexists(link):
                os.rmdir(link) if os.name == "nt" else link.unlink()


def test_file_reparse_source_is_not_enumerated(lib, monkeypatch):
    source = stored(lib)
    original = recovery._lstat
    def marked(path):
        info = original(path)
        if Path(path) != source:
            return info
        class Reparse:
            st_file_attributes = stat.FILE_ATTRIBUTE_REPARSE_POINT
            st_mode = info.st_mode
        return Reparse()
    monkeypatch.setattr(recovery, "_lstat", marked)
    plan = restore.preview(lib)
    assert not plan.items and plan.errors


def test_offline_roots_are_explicit_and_preview_does_not_update_database(lib, tmp_path):
    added = tmp_path / "external"
    added.mkdir()
    root_id = roots.add(lib, added)
    stored(lib, "photo.jpg", root=root_id)
    before = lib.db.total_changes
    marker = config.app_dir(added) / roots.MARKER
    old = marker.with_suffix(".offline")
    marker.rename(old)
    try:
        plan = restore.preview(lib)
        assert len(plan.offline_roots) == 1 and not plan.items
        assert lib.db.total_changes == before
        assert restore.execute(lib, plan).messages
    finally:
        old.rename(marker)
    assert restore.execute(lib, restore.preview(lib)).restored == 1
    assert (added / "photo.jpg").exists()


def test_mixed_copy_move_recycle_batch_restores_only_recovery(lib):
    for name in ("removed.jpg", "copied.jpg", "moved.jpg"):
        (lib.root / name).write_bytes(name.encode())
    scanner.scan(lib)
    exported, moved = lib.root / "export.jpg", lib.root / "ordinary-move.jpg"
    result = actions.apply(lib, "batch", "Mixed generated batch", [
        actions.Action("copy", str(lib.root / "copied.jpg"), str(exported), size=10),
        actions.Action("move", str(lib.root / "moved.jpg"), str(moved), size=9),
        actions.Action("recycle", str(lib.root / "removed.jpg"), size=11)])
    assert result.done == 3
    before = exported.read_bytes(), moved.read_bytes()
    restored = restore.execute(lib, restore.preview(lib))
    assert restored.restored == 1, restored.messages
    assert (exported.read_bytes(), moved.read_bytes()) == before
    assert not (lib.root / "moved.jpg").exists()
    assert {op["status"] for op in actions.operations(lib, result.batch_id) if op["op"] != "recycle"} == {"done"}


def test_cancellation_keeps_completed_units_and_resume_reopens(lib, monkeypatch):
    first = stored(lib, "a.jpg")
    second = stored(lib, "b.jpg")
    progress = Progress()
    original = actions.undo_recovery
    def cancel_after_complete(*args, **kwargs):
        result = original(*args, **kwargs)
        progress.cancel_event.set()
        return result
    with monkeypatch.context() as patch:
        patch.setattr(actions, "undo_recovery", cancel_after_complete)
        result = restore.execute(lib, restore.preview(lib), progress)
    assert result.cancelled and result.restored == 1 and result.skipped == 1
    assert not first.exists() and second.exists()
    home = lib.root
    lib.close()
    reopened = Library(home)
    try:
        result = restore.execute(reopened, restore.preview(reopened))
        assert result.restored == 1
        assert (home / "a.jpg").exists() and (home / "b.jpg").exists()
    finally:
        reopened.close()


def test_cancel_after_adoption_retains_explicit_recoverable_import(lib, monkeypatch):
    source = stored(lib, "photo.jpg")
    progress = Progress()
    adopt = restore._adopt
    def cancel(*args, **kwargs):
        result = adopt(*args, **kwargs)
        progress.cancel_event.set()
        return result
    with monkeypatch.context() as patch:
        patch.setattr(restore, "_adopt", cancel)
        result = restore.execute(lib, restore.preview(lib), progress)
    assert result.cancelled and not result.restored and source.exists()
    op = lib.db.execute("SELECT * FROM operations").fetchone()
    assert op["status"] == "done" and json.loads(op["reason"])["provenance"] == "inferred"
    report = recovery.inspect(lib)
    assert report.latest_id is None and report.other_bytes == 9
    plan = restore.preview(lib)
    assert plan.items[0].operation_id == op["id"] and plan.items[0].provenance == "inferred"
    assert restore.execute(lib, plan).restored == 1
    assert lib.db.execute("SELECT COUNT(*) FROM batches").fetchone()[0] == 1


@pytest.mark.parametrize("logged", [False, True])
def test_interrupted_restore_reconciles_then_resumes_without_losing_metadata(lib, monkeypatch, logged):
    if logged:
        recycle(lib, ["IMG.jpg", "IMG.mov"])
    else:
        stored(lib, "IMG.jpg")
        stored(lib, "IMG.mov")
    move = restore._move
    def crash(*args, **kwargs):
        move(*args, **kwargs)
        raise SystemExit("simulated power loss after publication")
    with monkeypatch.context() as patch:
        patch.setattr(restore, "_move", crash)
        with pytest.raises(SystemExit):
            restore.execute(lib, restore.preview(lib))
    assert lib.db.execute("SELECT COUNT(*) FROM operations WHERE status='undo_pending'").fetchone()[0] == 2
    home = lib.root
    lib.close()
    reopened = Library(home)
    try:
        assert actions.reconcile(reopened) == 2
        assert not (home / "IMG.jpg").exists() and not (home / "IMG.mov").exists()
        if logged:
            assert reopened.db.execute("SELECT COUNT(*) FROM parked_files").fetchone()[0] == 2
        result = restore.execute(reopened, restore.preview(reopened))
        assert result.restored == 2, result.messages
        assert (home / "IMG.jpg").exists() and (home / "IMG.mov").exists()
    finally:
        reopened.close()


def test_missing_linked_component_blocks_whole_logged_unit(lib):
    removed = recycle(lib, ["IMG.jpg", "IMG.mov"])
    ops = actions.operations(lib, removed.batch_id)
    Path(next(op["dst"] for op in ops if op["dst"].endswith(".mov"))).unlink()
    plan = restore.preview(lib)
    assert len(plan.items) == 1 and "incomplete" in plan.items[0].issue
    assert restore.execute(lib, plan).restored == 0
    assert plan.items[0].source.exists()


def test_same_drive_uses_rename_not_copy(lib, monkeypatch):
    stored(lib)
    monkeypatch.setattr(restore.shutil, "copy2", lambda *args, **kwargs: pytest.fail("No whole-file copies"))
    called = []
    publish = restore._publish
    def renamed(source, target):
        called.append((source, target))
        return publish(source, target)
    monkeypatch.setattr(restore, "_publish", renamed)
    assert restore.execute(lib, restore.preview(lib)).restored == 1
    assert len(called) == 1


def test_late_collision_in_second_linked_part_rolls_back_before_one_decision(lib, monkeypatch):
    stored(lib, "IMG.jpg")
    stored(lib, "IMG.mov")
    publish = restore._publish
    injected, calls = False, []
    def race(source, target):
        nonlocal injected
        if target == lib.root / "IMG.mov" and not injected:
            injected = True
            target.write_bytes(b"late foreign movie")
        return publish(source, target)
    monkeypatch.setattr(restore, "_publish", race)
    result = restore.execute(lib, restore.preview(lib), resolve_conflict=lambda conflict: calls.append(conflict) or "rename")
    assert result.restored == 2 and len(calls) == 1, result.messages
    assert (lib.root / "IMG.mov").read_bytes() == b"late foreign movie"
    assert not (lib.root / "IMG.jpg").exists()
    assert (lib.root / "IMG (2).jpg").read_bytes() == b"generated"
    assert (lib.root / "IMG (2).mov").read_bytes() == b"generated"


def test_changed_unlogged_membership_does_not_split_asset(lib):
    source = stored(lib, "IMG.jpg")
    plan = restore.preview(lib)
    movie = stored(lib, "IMG.mov")
    result = restore.execute(lib, plan)
    assert result.restored == 0 and result.skipped == 1
    assert source.exists() and movie.exists()
    assert restore.execute(lib, restore.preview(lib)).restored == 2


def test_cancellation_inside_linked_unit_compensates_all_members(lib, monkeypatch):
    sources = [stored(lib, name) for name in ("IMG.jpg", "IMG.mov")]
    progress = Progress()
    publish = restore._publish
    def cancel(source, target):
        publish(source, target)
        if target == lib.root / "IMG.jpg":
            progress.cancel_event.set()
    with monkeypatch.context() as patch:
        patch.setattr(restore, "_publish", cancel)
        result = restore.execute(lib, restore.preview(lib), progress)
    assert result.cancelled and result.restored == 0 and result.skipped == 2
    assert all(path.exists() for path in sources)
    assert not (lib.root / "IMG.jpg").exists() and not (lib.root / "IMG.mov").exists()
    assert restore.execute(lib, restore.preview(lib)).restored == 2


def test_cancellation_wakes_conflict_wait_without_mutation(lib):
    source = stored(lib, "photo.jpg")
    (lib.root / "photo.jpg").write_bytes(b"original")
    progress = Progress()
    def resolve(conflict):
        progress.cancel_event.set()
        return "rename"
    result = restore.execute(lib, restore.preview(lib), progress, resolve)
    assert result.cancelled and not result.restored and source.exists()
    assert not lib.db.execute("SELECT id FROM operations").fetchone()


def test_manual_mapping_into_registered_other_root_preserves_nested_paths(lib, tmp_path):
    added = tmp_path / "added"
    added.mkdir()
    root_id = roots.add(lib, added)
    stored(lib, "Nested\\a.jpg", container="unknown")
    stored(lib, "Nested\\b.jpg", container="unknown")
    plan = restore.preview(lib)
    plan = restore.map_destination(lib, plan, plan.items[0].mapping_group, added / "Chosen")
    result = restore.execute(lib, plan)
    assert result.restored == 2, result.messages
    assert (added / "Chosen" / "Nested" / "a.jpg").exists()
    assert (added / "Chosen" / "Nested" / "b.jpg").exists()
    assert all(row[0].startswith(f"@root:{root_id}\\") for row in lib.db.execute("SELECT src_key FROM operations"))


def test_metadata_merges_unwind_in_reverse_operation_order(lib):
    for name in ("a.jpg", "z.jpg", "keeper.jpg"):
        (lib.root / name).write_bytes(b"generated")
    scanner.scan(lib)
    keeper = lib.file_by_rel("keeper.jpg")["id"]
    before = organisation.state(lib, keeper)
    planned = []
    for name, tag in (("a.jpg", "Earlier"), ("z.jpg", "Later")):
        fid = lib.file_by_rel(name)["id"]
        organisation.edit(lib, [fid], add_tags=[tag])
        planned.append(actions.Action("recycle", str(lib.root / name), size=9, file_id=fid, merge_into=keeper))
    removed = actions.apply(lib, "duplicates", "Generated", planned)
    assert removed.done == 2
    result = restore.execute(lib, restore.preview(lib))
    assert result.restored == 2, result.messages
    assert organisation.state(lib, keeper) == before


def test_only_dependent_removed_directories_are_marked_restored(lib):
    folder = lib.root / "Trip"
    unrelated = lib.root / "Other empty folder"
    folder.mkdir()
    unrelated.mkdir()
    source = folder / "photo.jpg"
    source.write_bytes(b"generated")
    scanner.scan(lib)
    removed = actions.apply(lib, "duplicates", "Generated", [
        actions.Action("recycle", str(source), size=9),
        actions.Action("rmdir", str(folder)),
        actions.Action("rmdir", str(unrelated))])
    assert removed.done == 3 and not folder.exists() and not unrelated.exists()
    result = restore.execute(lib, restore.preview(lib))
    assert result.restored == 1, result.messages
    rows = {Path(op["src"]).name: op["status"] for op in actions.operations(lib, removed.batch_id)}
    assert rows["Trip"] == "undone" and rows["Other empty folder"] == "done"
    assert not unrelated.exists()


def test_corrupt_logged_destination_is_unresolved_not_silently_inferred(lib):
    removed = recycle(lib, ["photo.jpg"])
    lib.db.execute("UPDATE operations SET src_key='..\\outside.jpg' WHERE batch_id=?", (removed.batch_id,))
    plan = restore.preview(lib)
    assert len(plan.items) == 1 and plan.items[0].target is None and plan.items[0].issue
    assert restore.execute(lib, plan).skipped == 1
    assert plan.items[0].source.exists()


def test_stale_catalogue_destination_does_not_discard_parked_identity(lib):
    removed = recycle(lib, ["photo.jpg"])
    parked_id = lib.db.execute("SELECT file_id FROM parked_files").fetchone()[0]
    original = lib.root / "photo.jpg"
    original.write_bytes(b"later original")
    scanner.scan(lib)
    other_id = lib.file_by_rel("photo.jpg")["id"]
    original.unlink()
    calls = []
    result = restore.execute(lib, restore.preview(lib), resolve_conflict=lambda conflict: calls.append(conflict) or "rename")
    assert result.restored == 1 and len(calls) == 1, result.messages
    assert lib.file(parked_id)["name"] == "photo (2).jpg"
    assert lib.file(other_id)["name"] == "photo.jpg"
    assert actions.operations(lib, removed.batch_id)[0]["status"] == "undone"


def test_staging_names_need_mapping_even_inside_supported_batch_layout(lib):
    source = stored(lib, "Trip\\photo.jpg.memoria-tmp")
    plan = restore.preview(lib)
    assert plan.items[0].target is None and plan.items[0].issue
    assert restore.execute(lib, plan).skipped == 1 and source.exists()


def test_singleton_logged_crash_uses_durable_restore_intent(lib, monkeypatch):
    removed = recycle(lib, ["photo.jpg"])
    move = restore._move
    def crash(*args, **kwargs):
        move(*args, **kwargs)
        raise SystemExit("singleton interruption")
    with monkeypatch.context() as patch:
        patch.setattr(restore, "_move", crash)
        with pytest.raises(SystemExit):
            restore.execute(lib, restore.preview(lib))
    assert actions.reconcile(lib) == 1
    assert actions.operations(lib, removed.batch_id)[0]["status"] == "done"
    assert restore.execute(lib, restore.preview(lib)).restored == 1


def test_legacy_log_without_hash_still_handles_late_collision(lib, monkeypatch):
    removed = recycle(lib, ["photo.jpg"])
    lib.db.execute("UPDATE operations SET hash=NULL WHERE batch_id=?", (removed.batch_id,))
    publish = restore._publish
    raced = False
    def race(source, target):
        nonlocal raced
        if not raced:
            raced = True
            target.write_bytes(b"foreign")
        return publish(source, target)
    monkeypatch.setattr(restore, "_publish", race)
    result = restore.execute(lib, restore.preview(lib), resolve_conflict=lambda conflict: "rename")
    assert result.restored == 1, result.messages
    assert (lib.root / "photo.jpg").read_bytes() == b"foreign"
    assert (lib.root / "photo (2).jpg").exists()


def test_publication_failure_is_reported_and_preserves_recoverable_import(lib, monkeypatch):
    source = stored(lib, "photo.jpg")
    def denied(*args):
        raise PermissionError("generated publication denied")
    monkeypatch.setattr(restore, "_publish", denied)
    result = restore.execute(lib, restore.preview(lib))
    assert result.restored == result.skipped == 0 and result.failed == 1, result.messages
    assert source.exists() and not (lib.root / "photo.jpg").exists()
    assert lib.db.execute("SELECT status FROM operations").fetchone()[0] == "done"
