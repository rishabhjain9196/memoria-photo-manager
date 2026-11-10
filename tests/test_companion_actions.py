"""Linked-asset file publication, compensation, crash recovery and metadata Undo."""
import os

import pytest

from memoria.engine import actions, albums, assets, batch, organisation, roots, scanner
from memoria.engine.db import Library
from memoria.engine.hashing import full_hash
from memoria.engine.progress import Progress


def make_asset(root, stem="IMG"):
    root.mkdir(parents=True, exist_ok=True)
    for suffix, value in ((".jpg", b"photo"), (".mov", b"motion"), (".jpg.xmp", b"edits")):
        (root / (stem + suffix)).write_bytes(value + stem.encode())


@pytest.fixture
def linked(tmp_path):
    root = tmp_path / "library"
    make_asset(root)
    (root / "keeper.jpg").write_bytes((root / "IMG.jpg").read_bytes())
    lib = Library(root)
    scanner.scan(lib)
    yield lib
    lib.close()


def plan(lib, op="recycle", *, stem="IMG", root=None, dest=None):
    source = (root or lib.root) / (stem + ".jpg")
    row = dict(lib.file_by_rel(lib.rel(source)))
    raw = (batch.plan_recycle(lib, [row]) if op == "recycle" else
           batch.plan_copy_to(lib, [row], dest) if op == "copy" else
           batch.plan_move_within(lib, [row], dest))
    return assets.prepare(lib, raw, "batch").actions


def contents(root):
    return {str(path.relative_to(root)): path.read_bytes() for path in root.rglob("*")
            if path.is_file() and ".memoria" not in path.parts}


def execute(lib, planned, progress=None):
    return actions.apply(lib, "batch", "Linked files", planned, progress, companions_reviewed=True)


def test_unprepared_or_unreviewed_companions_are_rejected_without_expansion(linked):
    lib = linked
    before = contents(lib.root)
    raw = batch.plan_recycle(lib, [dict(lib.file_by_rel("IMG.jpg"))])
    with pytest.raises(ValueError, match="review"):
        actions.apply(lib, "batch", "Unreviewed", raw)
    with pytest.raises(ValueError, match="prepared"):
        execute(lib, raw)
    prepared = plan(lib)
    with pytest.raises(ValueError, match="review"):
        actions.apply(lib, "batch", "Unreviewed prepared", prepared)
    with pytest.raises(ValueError, match="incomplete"):
        execute(lib, prepared[:1])
    assert contents(lib.root) == before
    assert not lib.db.execute("SELECT 1 FROM operations").fetchone()


def test_changed_sibling_and_membership_skip_whole_group_before_any_mutation(linked):
    lib = linked
    prepared = plan(lib)
    sidecar = lib.root / "IMG.jpg.xmp"
    stamp = sidecar.stat()
    sidecar.write_bytes(b"otherIMG")  # Same length/mtime; its reviewed hash must still reject it.
    os.utime(sidecar, (stamp.st_atime, stamp.st_mtime))
    before = contents(lib.root)
    result = execute(lib, prepared)
    assert result.done == 0 and result.skipped == 3 and result.failed == 0
    assert contents(lib.root) == before and not lib.db.execute("SELECT 1 FROM parked_files").fetchone()
    scanner.scan(lib)
    prepared = plan(lib)
    (lib.root / "IMG.aae").write_bytes(b"new edits")
    scanner.scan(lib)
    result = execute(lib, prepared)
    assert result.done == 0 and result.skipped == 3
    assert (lib.root / "IMG.aae").read_bytes() == b"new edits"


def test_mid_group_failure_rolls_back_only_that_group(linked, monkeypatch):
    lib = linked
    make_asset(lib.root, "B")
    scanner.scan(lib)
    earlier = plan(lib)
    failing = plan(lib, stem="B")
    before_b = {path.name: path.read_bytes() for path in lib.root.glob("B*")}
    move = actions.safe_move
    def fail(src, dst):
        if src == lib.root / "B.mov":
            raise OSError("injected linked sibling failure")
        move(src, dst)
    monkeypatch.setattr(actions, "safe_move", fail)
    result = execute(lib, earlier + failing)
    assert result.done == 3 and result.failed == 3
    assert {path.name: path.read_bytes() for path in lib.root.glob("B*")} == before_b
    assert not (lib.root / "IMG.jpg").exists()
    assert lib.db.execute("SELECT COUNT(*) FROM parked_files").fetchone()[0] == 3
    failed = [op for op in actions.operations(lib, result.batch_id) if op["asset_group"] == failing[0].asset_group]
    assert {op["status"] for op in failed} == {"failed"}
    assert actions.undo(lib, result.batch_id).done == 3


def test_cancellation_reverses_current_group_and_preserves_earlier_groups(linked, monkeypatch):
    lib = linked
    make_asset(lib.root, "B")
    scanner.scan(lib)
    first, second = plan(lib), plan(lib, stem="B")
    progress = Progress()
    move = actions.safe_move
    def cancel_after_publish(src, dst):
        if src == lib.root / "B.jpg":
            assert lib.db.execute("SELECT COUNT(*) FROM operations WHERE asset_group=? "
                                   "AND status IN ('pending','publishing','published')",
                                   (second[0].asset_group,)).fetchone()[0] == 3
            move(src, dst)
            progress.cancel_event.set()
        else:
            move(src, dst)
    monkeypatch.setattr(actions, "safe_move", cancel_after_publish)
    result = execute(lib, first + second, progress)
    assert result.cancelled and result.failed == 0 and result.done == 3
    assert all((lib.root / ("B" + suffix)).exists() for suffix in (".jpg", ".mov", ".jpg.xmp"))
    assert not (lib.root / "IMG.jpg").exists()


def test_copy_collisions_share_one_suffix_and_undo_preserves_existing_file(linked, tmp_path):
    lib = linked
    dest = tmp_path / "exports"
    dest.mkdir()
    foreign = dest / "IMG.mov"
    foreign.write_bytes(b"unrelated file")
    before = contents(lib.root)
    result = execute(lib, plan(lib, "copy", dest=dest))
    assert result.done == 3 and result.failed == 0
    assert {path.name for path in dest.iterdir()} == {
        "IMG.mov", "IMG (2).jpg", "IMG (2).mov", "IMG (2).jpg.xmp"}
    assert contents(lib.root) == before
    assert actions.undo(lib, result.batch_id).done == 3
    assert list(dest.iterdir()) == [foreign] and foreign.read_bytes() == b"unrelated file"


def test_destination_race_does_not_delete_foreign_or_unstarted_sibling_outputs(linked, tmp_path, monkeypatch):
    lib = linked
    dest = tmp_path / "exports"
    copied = actions.verified_copy
    def race(src, dst, expected=None):
        if src.name == "IMG.mov":
            dst.write_bytes(src.read_bytes())  # Identical bytes are still not our publication.
            (dest / "IMG.jpg.xmp").write_bytes(b"foreign unstarted sibling")
        return copied(src, dst, expected)
    monkeypatch.setattr(actions, "verified_copy", race)
    result = execute(lib, plan(lib, "copy", dest=dest))
    assert result.failed == 3 and result.done == 0
    assert not (dest / "IMG.jpg").exists()
    assert (dest / "IMG.mov").read_bytes() == (lib.root / "IMG.mov").read_bytes()
    assert (dest / "IMG.jpg.xmp").read_bytes() == b"foreign unstarted sibling"


def test_undo_recycle_collisions_restore_whole_asset_under_common_names(linked):
    lib = linked
    before = {row["name"]: row["id"] for row in lib.files() if row["name"].startswith("IMG")}
    result = execute(lib, plan(lib))
    (lib.root / "IMG.mov").write_bytes(b"new file at old path")
    undone = actions.undo(lib, result.batch_id)
    assert undone.done == 3 and undone.failed == 0
    for name, file_id in before.items():
        expected = name.replace("IMG", "IMG (2)", 1)
        assert lib.file(file_id)["name"] == expected
        assert (lib.root / expected).exists()
    assert (lib.root / "IMG.mov").read_bytes() == b"new file at old path"


def test_changed_copied_sibling_blocks_all_undo_deletions(linked, tmp_path):
    lib = linked
    dest = tmp_path / "exports"
    result = execute(lib, plan(lib, "copy", dest=dest))
    (dest / "IMG.mov").write_bytes(b"user edited output")
    before = contents(dest)
    undone = actions.undo(lib, result.batch_id)
    assert undone.done == 0 and undone.failed == 3
    assert contents(dest) == before
    assert {op["status"] for op in actions.operations(lib, result.batch_id)} == {"done"}


@pytest.mark.parametrize("cancel", [False, True])
def test_failed_or_cancelled_copy_undo_restores_all_staged_outputs(linked, tmp_path, monkeypatch, cancel):
    lib = linked
    dest = tmp_path / "exports"
    result = execute(lib, plan(lib, "copy", dest=dest))
    before = contents(dest)
    progress = Progress()
    move = actions.safe_move
    calls = 0
    def interrupted(src, dst):
        nonlocal calls
        if ".memoria-undo-" in dst.name:
            calls += 1
            if calls == 2 and not cancel:
                raise OSError("injected Undo staging failure")
            move(src, dst)
            if cancel:
                progress.cancel_event.set()
        else:
            move(src, dst)
    monkeypatch.setattr(actions, "safe_move", interrupted)
    undone = actions.undo(lib, result.batch_id, progress)
    assert undone.done == 0
    assert undone.cancelled if cancel else undone.failed == 3
    assert contents(dest) == before
    assert {op["status"] for op in actions.operations(lib, result.batch_id)} == {"done"}


def test_partial_apply_crash_reconciles_as_one_rolled_back_group(linked, monkeypatch):
    lib = linked
    before = contents(lib.root)
    move = actions.safe_move
    def crash(src, dst):
        move(src, dst)
        raise SystemExit("simulated interruption")
    with monkeypatch.context() as patch:
        patch.setattr(actions, "safe_move", crash)
        with pytest.raises(SystemExit):
            execute(lib, plan(lib))
    assert lib.db.execute("SELECT COUNT(*) FROM operations WHERE status IN ('pending','publishing')").fetchone()[0] == 3
    assert actions.reconcile(lib) == 3
    assert contents(lib.root) == before
    assert not lib.db.execute("SELECT 1 FROM parked_files").fetchone()
    assert {row[0] for row in lib.db.execute("SELECT status FROM operations")} == {"failed"}


def test_partial_undo_crash_reconciles_to_complete_recovery_group(linked, monkeypatch):
    lib = linked
    result = execute(lib, plan(lib))
    move = actions.safe_move
    def crash(src, dst):
        move(src, dst)
        raise SystemExit("simulated interruption")
    with monkeypatch.context() as patch:
        patch.setattr(actions, "safe_move", crash)
        with pytest.raises(SystemExit):
            actions.undo(lib, result.batch_id)
    assert lib.db.execute("SELECT COUNT(*) FROM operations WHERE status='undo_pending'").fetchone()[0] == 3
    assert actions.reconcile(lib) == 3
    assert not (lib.root / "IMG.jpg").exists()
    assert not (lib.root / "IMG.mov").exists()
    assert not (lib.root / "IMG.jpg.xmp").exists()
    assert lib.db.execute("SELECT COUNT(*) FROM parked_files").fetchone()[0] == 3
    assert {op["status"] for op in actions.operations(lib, result.batch_id)} == {"done"}
    assert actions.undo(lib, result.batch_id).done == 3


def test_partial_copy_undo_crash_restores_staged_outputs(linked, tmp_path, monkeypatch):
    lib = linked
    dest = tmp_path / "exports"
    result = execute(lib, plan(lib, "copy", dest=dest))
    before = contents(dest)
    move = actions.safe_move
    def crash(src, dst):
        move(src, dst)
        raise SystemExit("simulated interruption")
    with monkeypatch.context() as patch:
        patch.setattr(actions, "safe_move", crash)
        with pytest.raises(SystemExit):
            actions.undo(lib, result.batch_id)
    assert actions.reconcile(lib) == 3
    assert contents(dest) == before
    assert {op["status"] for op in actions.operations(lib, result.batch_id)} == {"done"}


def test_undo_holding_cleanup_is_durable_and_retryable(linked, tmp_path, monkeypatch):
    lib = linked
    dest = tmp_path / "exports"
    result = execute(lib, plan(lib, "copy", dest=dest))
    remove = actions.os.remove
    def locked(path):
        if ".memoria-undo-" in str(path):
            raise PermissionError("locked holding copy")
        remove(path)
    with monkeypatch.context() as patch:
        patch.setattr(actions.os, "remove", locked)
        undone = actions.undo(lib, result.batch_id)
    assert undone.done == 3 and any("cleanup remains pending" in text for text in undone.messages)
    assert all(".memoria-undo-" in path.name for path in dest.iterdir())
    actions.reconcile(lib)
    assert not list(dest.iterdir())


def test_rollback_failure_remains_explicit_and_retryable(linked, monkeypatch):
    lib = linked
    before = contents(lib.root)
    move = actions.safe_move
    def broken(src, dst):
        if src == lib.root / "IMG.mov" or ".memoria" in src.parts:
            raise OSError("injected source and rollback failure")
        move(src, dst)
    with monkeypatch.context() as patch:
        patch.setattr(actions, "safe_move", broken)
        result = execute(lib, plan(lib))
    assert result.failed == 3 and any("Rollback incomplete" in text for text in result.messages)
    assert lib.db.execute("SELECT 1 FROM operations WHERE status IN ('publishing','published')").fetchone()
    assert actions.batches(lib)[0]["status"] == "partial"
    actions.reconcile(lib)
    assert contents(lib.root) == before
    assert not lib.db.execute("SELECT 1 FROM operations WHERE status IN ('pending','publishing','published')").fetchone()


def test_linked_undo_uses_reconnected_root_keys(linked, tmp_path):
    lib = linked
    source, moved = tmp_path / "drive", tmp_path / "reconnected"
    make_asset(source, "PHONE")
    root_id = roots.add(lib, source)
    scanner.scan(lib)
    result = execute(lib, plan(lib, stem="PHONE", root=source))
    home = lib.root
    lib.close()
    source.rename(moved)
    reopened = Library(home)
    try:
        roots.reconnect(reopened, root_id, moved)
        undone = actions.undo(reopened, result.batch_id)
        assert undone.done == 3 and undone.failed == 0
        assert all((moved / ("PHONE" + suffix)).exists() for suffix in (".jpg", ".mov", ".jpg.xmp"))
        assert not source.exists()
    finally:
        reopened.close()


def test_linked_cross_root_move_and_undo_preserve_catalogue_ids(linked, tmp_path):
    lib = linked
    dest = tmp_path / "drive"
    dest.mkdir()
    source_id = roots.add(lib, dest)
    original = {row["id"]: row["rel_path"] for row in lib.files() if row["name"].startswith("IMG")}
    prepared = plan(lib, "move", dest=dest)
    result = execute(lib, prepared)
    assert result.done == 3
    assert all(lib.file(file_id)["root_id"] == source_id for file_id in original)
    assert actions.undo(lib, result.batch_id).done == 3
    assert {file_id: lib.file(file_id)["rel_path"] for file_id in original} == original
    assert all(lib.file(file_id)["root_id"] == 1 for file_id in original)


@pytest.mark.parametrize("edit_later", [False, True])
def test_duplicate_merge_and_undo_do_not_inflate_file_counts_or_overwrite_edits(linked, edit_later):
    lib = linked
    source, keeper = lib.file_by_rel("IMG.jpg"), lib.file_by_rel("keeper.jpg")
    first = albums.create(lib, "Source", [source["id"]])
    second = albums.create(lib, "Keeper", [keeper["id"]])
    organisation.edit(lib, [source["id"]], favorite=True, rating=5, review="reject", add_tags=["Source"])
    organisation.edit(lib, [keeper["id"]], rating=3, review="pick", add_tags=["Keeper"])
    before = organisation.state(lib, keeper["id"])
    prepared = plan(lib)
    anchor = next(action for action in prepared if action.file_id == source["id"])
    anchor.merge_into = keeper["id"]
    anchor.guards = [(str(lib.abspath(keeper["rel_path"])), full_hash(lib.abspath(keeper["rel_path"])))]
    result = execute(lib, prepared)
    after = organisation.state(lib, keeper["id"])
    assert after == {"rating": 3, "favorite": True, "review": "pick",
                     "tags": ["Keeper", "Source"], "albums": [first, second]}
    ops = actions.operations(lib, result.batch_id)
    assert result.done == 3 and len(ops) == 4 and result.bytes == sum(a.size for a in prepared)
    assert actions.batches(lib)[0]["files"] == 3
    assert [op["seq"] for op in ops if op["op"] == "metadata"] == [next(
        op["seq"] - 1 for op in ops if op["merge_target"] == keeper["id"])]
    if edit_later:
        organisation.edit(lib, [keeper["id"]], add_tags=["Later edit"])
        current = organisation.state(lib, keeper["id"])
    undone = actions.undo(lib, result.batch_id)
    assert undone.done == 3 and lib.file(source["id"]) is not None
    if edit_later:
        assert undone.failed == 1 and organisation.state(lib, keeper["id"]) == current
        organisation.set_state(lib, keeper["id"], after)
        retry = actions.undo(lib, result.batch_id)
        assert retry.done == retry.bytes == 0 and retry.failed == 0
    else:
        assert undone.failed == 0
    assert organisation.state(lib, keeper["id"]) == before


def test_metadata_merge_failure_rolls_back_linked_files_and_keeper_choices(linked, monkeypatch):
    from memoria.engine import metadata_history
    lib = linked
    source, keeper = lib.file_by_rel("IMG.jpg"), lib.file_by_rel("keeper.jpg")
    organisation.edit(lib, [source["id"]], favorite=True, add_tags=["Source"])
    before_files, before_keeper = contents(lib.root), organisation.state(lib, keeper["id"])
    prepared = plan(lib)
    next(action for action in prepared if action.file_id == source["id"]).merge_into = keeper["id"]
    merge = metadata_history.apply_merge
    def failed(*args, **kwargs):
        merge(*args, **kwargs)
        raise OSError("injected post-merge transaction failure")
    monkeypatch.setattr(metadata_history, "apply_merge", failed)
    result = execute(lib, prepared)
    assert result.done == 0 and result.failed == 3
    assert contents(lib.root) == before_files
    assert organisation.state(lib, keeper["id"]) == before_keeper
    assert not lib.db.execute("SELECT 1 FROM metadata_journal").fetchone()
    assert not lib.db.execute("SELECT 1 FROM operations WHERE op='metadata'").fetchone()
    assert not lib.db.execute("SELECT 1 FROM parked_files").fetchone()
