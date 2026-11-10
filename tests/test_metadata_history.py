"""Atomic, metadata-only duplicate merge history with retained stable file IDs."""
import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor

import pytest

from memoria.engine import albums, catalogue, metadata_history, organisation, storage
from memoria.engine.db import Library


@pytest.fixture
def history(tmp_path):
    lib = Library(tmp_path)
    with lib.transaction() as db:
        db.executemany("INSERT INTO files(rel_path,folder,name,ext,kind,size,mtime,analyzed) "
                       "VALUES (?,'',?,'.jpg','image',10,1,1)",
                       [("source.jpg", "source.jpg"), ("keeper.jpg", "keeper.jpg"), ("other.jpg", "other.jpg")])
        db.execute("INSERT INTO batches(id,created_at,kind,title,status,files,bytes) "
                   "VALUES ('duplicates','2026-01-01','duplicates','Remove duplicate','applied',1,10)")
        op = db.execute("INSERT INTO operations(batch_id,seq,op,src,src_key,dst,size,status,merge_target,asset_group) "
                        "VALUES ('duplicates',1,'recycle',?,'source.jpg',?,10,'done',2,'asset')",
                        (str(lib.abspath("source.jpg")), str(tmp_path / ".memoria" / "recovery" / "source.jpg"))).lastrowid
    yield lib, op
    lib.close()


def prepare(lib, op, *, conflicts=True):
    a = albums.create(lib, "Source album", [1])
    b = albums.create(lib, "Keeper album", [2])
    albums.create_smart(lib, "Dynamic, not a membership", catalogue.Filters(min_rating=1))
    organisation.edit(lib, [1], rating=5, favorite=True, review="reject", add_tags=["Travel", "Shared"])
    organisation.edit(lib, [2], rating=3 if conflicts else 0, review="pick" if conflicts else "unreviewed",
                      add_tags=["Keeper", "shared"])
    lib.db.execute("UPDATE files SET baseline_hash='source health fingerprint' WHERE id=1")
    lib.db.execute("INSERT INTO faces(file_id,x,y,w,h,score,emb) VALUES (1,0,0,1,1,1,?)", (b"face data",))
    lib.park_rows([(op, 1)])
    return a, b


def restore_source(lib, op):
    assert lib.restore_parked(op, "source.jpg")
    lib.db.execute("UPDATE operations SET status='undone' WHERE id=?", (op,))


@pytest.mark.parametrize("conflicts", [False, True])
def test_merge_unions_organisation_and_undo_restores_exact_keeper(history, conflicts):
    lib, source_op = history
    source_album, keeper_album = prepare(lib, source_op, conflicts=conflicts)
    before_source = organisation.state(lib, 1)
    before_keeper = organisation.state(lib, 2)
    op = metadata_history.apply_merge(lib, source_op, 1, 2, 0)
    after = organisation.state(lib, 2)
    assert after == {"rating": 3 if conflicts else 5, "favorite": True,
                     "review": "pick" if conflicts else "reject",
                     "tags": ["Keeper", "Shared", "Travel"], "albums": [source_album, keeper_album]}
    assert organisation.state(lib, 1) == before_source
    assert lib.file(2)["baseline_hash"] is None
    assert not lib.db.execute("SELECT 1 FROM faces WHERE file_id=2").fetchone()
    operation = lib.db.execute("SELECT * FROM operations WHERE id=?", (op,)).fetchone()
    assert operation["batch_id"] == "duplicates" and operation["seq"] == 0
    assert operation["op"] == "metadata" and operation["status"] == "done"
    assert operation["src"] == str(lib.abspath("keeper.jpg")) and operation["src_key"] == "keeper.jpg"
    assert operation["dst"] is None and operation["dst_key"] is None and operation["size"] == 0
    assert operation["merge_target"] is None
    assert tuple(lib.db.execute("SELECT files,bytes FROM batches WHERE id='duplicates'").fetchone()) == (1, 10)
    journal = lib.db.execute("SELECT * FROM metadata_journal WHERE op_id=?", (op,)).fetchone()
    assert journal["source_op"] == source_op and journal["file_id"] == 2
    assert json.loads(journal["before_json"]) == before_keeper
    assert json.loads(journal["after_json"]) == after
    restore_source(lib, source_op)
    metadata_history.undo_merge(lib, op)
    assert organisation.state(lib, 2) == before_keeper
    assert organisation.state(lib, 1) == before_source
    assert lib.db.execute("SELECT status FROM operations WHERE id=?", (op,)).fetchone()[0] == "undone"
    organisation.edit(lib, [2], rating=1)
    metadata_history.undo_merge(lib, op)
    assert organisation.state(lib, 2)["rating"] == 1


def test_apply_is_idempotent_including_concurrent_reconcile(history):
    lib, source_op = history
    prepare(lib, source_op)
    def apply():
        try:
            return metadata_history.apply_merge(lib, source_op, 1, 2, 0)
        finally:
            lib.close_thread()
    with ThreadPoolExecutor(max_workers=2) as pool:
        first, second = list(pool.map(lambda _: apply(), range(2)))
    assert first == second
    assert lib.db.execute("SELECT COUNT(*) FROM metadata_journal").fetchone()[0] == 1
    assert lib.db.execute("SELECT merge_complete FROM operations WHERE id=?", (source_op,)).fetchone()[0] == 1
    organisation.edit(lib, [2], rating=1)
    assert metadata_history.apply_merge(lib, source_op, 1, 2, -1) == first
    assert organisation.state(lib, 2)["rating"] == 1
    lib.db.execute("UPDATE operations SET merge_complete=0 WHERE id=?", (source_op,))
    assert metadata_history.apply_merge(lib, source_op, 1, 2, 0) == first
    assert organisation.state(lib, 2)["rating"] == 1
    assert lib.db.execute("SELECT merge_complete FROM operations WHERE id=?", (source_op,)).fetchone()[0] == 1
    with pytest.raises(ValueError, match="does not belong"):
        metadata_history.apply_merge(lib, source_op, 3, 2, 0)


def test_no_change_is_durable_without_metadata_operation(history):
    lib, source_op = history
    lib.park_rows([(source_op, 1)])
    assert metadata_history.apply_merge(lib, source_op, 1, 2, 0) is None
    assert not lib.db.execute("SELECT 1 FROM metadata_journal").fetchone()
    assert not lib.db.execute("SELECT 1 FROM operations WHERE op='metadata'").fetchone()
    assert lib.db.execute("SELECT merge_complete FROM operations WHERE id=?", (source_op,)).fetchone()[0] == 1
    root = lib.root
    lib.close()
    reopened = Library(root)
    try:
        changed = organisation.state(reopened, 1)
        changed["rating"] = 5
        organisation.set_state(reopened, 1, changed)
        assert metadata_history.apply_merge(reopened, source_op, 1, 2, 0) is None
        assert organisation.state(reopened, 2)["rating"] == 0
    finally:
        reopened.close()


def test_apply_failure_rolls_back_state_journal_and_complete_flag(history):
    lib, source_op = history
    prepare(lib, source_op)
    before = organisation.state(lib, 2)
    lib.db.execute("CREATE TEMP TRIGGER fail_completion BEFORE UPDATE OF merge_complete ON operations "
                   "WHEN NEW.merge_complete=1 BEGIN SELECT RAISE(ABORT,'injected merge failure'); END")
    with pytest.raises(sqlite3.IntegrityError, match="injected"):
        metadata_history.apply_merge(lib, source_op, 1, 2, 0)
    assert organisation.state(lib, 2) == before
    assert not lib.db.execute("SELECT 1 FROM metadata_journal").fetchone()
    assert not lib.db.execute("SELECT 1 FROM operations WHERE op='metadata'").fetchone()
    assert lib.db.execute("SELECT merge_complete FROM operations WHERE id=?", (source_op,)).fetchone()[0] == 0
    lib.db.execute("DROP TRIGGER fail_completion")
    assert metadata_history.apply_merge(lib, source_op, 1, 2, 0) is not None


def test_apply_and_undo_participate_in_enclosing_transaction(history):
    lib, source_op = history
    prepare(lib, source_op)
    before = organisation.state(lib, 2)
    with pytest.raises(RuntimeError, match="abort outer"):
        with lib.transaction():
            metadata_history.apply_merge(lib, source_op, 1, 2, 0)
            raise RuntimeError("abort outer")
    assert organisation.state(lib, 2) == before
    assert not lib.db.execute("SELECT 1 FROM metadata_journal").fetchone()
    op = metadata_history.apply_merge(lib, source_op, 1, 2, 0)
    merged = organisation.state(lib, 2)
    restore_source(lib, source_op)
    with pytest.raises(RuntimeError, match="abort outer"):
        with lib.transaction():
            metadata_history.undo_merge(lib, op)
            raise RuntimeError("abort outer")
    assert organisation.state(lib, 2) == merged
    assert lib.db.execute("SELECT status FROM operations WHERE id=?", (op,)).fetchone()[0] == "done"


def test_undo_failure_rolls_back_restored_state(history):
    lib, source_op = history
    prepare(lib, source_op)
    op = metadata_history.apply_merge(lib, source_op, 1, 2, 0)
    merged = organisation.state(lib, 2)
    restore_source(lib, source_op)
    lib.db.execute("CREATE TEMP TRIGGER fail_undo BEFORE UPDATE OF status ON operations "
                   "WHEN NEW.op='metadata' AND NEW.status='undone' "
                   "BEGIN SELECT RAISE(ABORT,'injected undo failure'); END")
    with pytest.raises(sqlite3.IntegrityError, match="injected"):
        metadata_history.undo_merge(lib, op)
    assert organisation.state(lib, 2) == merged
    assert lib.db.execute("SELECT status FROM operations WHERE id=?", (op,)).fetchone()[0] == "done"


@pytest.mark.parametrize("changes", [{"rating": 1}, {"add_tags": ["New choice"]}, {"favorite": False},
                                   {"review": "unreviewed"}])
def test_changed_keeper_refuses_undo_without_overwriting(history, changes):
    lib, source_op = history
    prepare(lib, source_op)
    op = metadata_history.apply_merge(lib, source_op, 1, 2, 0)
    restore_source(lib, source_op)
    organisation.edit(lib, [2], **changes)
    current = organisation.state(lib, 2)
    with pytest.raises(ValueError, match="changed after"):
        metadata_history.undo_merge(lib, op)
    assert organisation.state(lib, 2) == current
    assert lib.db.execute("SELECT status FROM operations WHERE id=?", (op,)).fetchone()[0] == "done"


@pytest.mark.parametrize("source_status", ["done", "purged", "failed", "undone"])
def test_unrestored_or_purged_source_refuses_undo(history, source_status):
    lib, source_op = history
    prepare(lib, source_op)
    op = metadata_history.apply_merge(lib, source_op, 1, 2, 0)
    merged = organisation.state(lib, 2)
    lib.db.execute("UPDATE operations SET status=? WHERE id=?", (source_status, source_op))
    if source_status == "purged":
        lib.drop_parked([source_op])
    # Even an inconsistent 'undone' status cannot discard metadata while the source stays parked.
    with pytest.raises(ValueError, match="Restore the source"):
        metadata_history.undo_merge(lib, op)
    assert organisation.state(lib, 2) == merged


@pytest.mark.parametrize("options", [dict(organisation=True), dict(albums=True),
                                    dict(organisation=True, albums=True)])
def test_reset_snapshots_never_resurrect_cleared_choices(history, options):
    lib, source_op = history
    prepare(lib, source_op)
    before = organisation.state(lib, 2)
    op = metadata_history.apply_merge(lib, source_op, 1, 2, 0)
    storage._clear_catalogue(lib, storage.ResetOptions(thumbnails=False, analysis=False, videos=False, **options))
    assert metadata_history.apply_merge(lib, source_op, 1, 2, 0) == op
    restore_source(lib, source_op)
    metadata_history.undo_merge(lib, op)
    if options.get("organisation"):
        before.update(rating=0, favorite=False, review="unreviewed", tags=[])
    if options.get("albums"):
        before["albums"] = []
    assert organisation.state(lib, 2) == before


def test_forgotten_missing_keeper_supersedes_snapshot_and_never_remerges(history):
    lib, source_op = history
    prepare(lib, source_op)
    op = metadata_history.apply_merge(lib, source_op, 1, 2, 0)
    lib.mark_missing([2])
    storage._clear_catalogue(lib, storage.ResetOptions(thumbnails=False, analysis=False, videos=False, missing=True))
    assert lib.db.execute("SELECT status FROM operations WHERE id=?", (op,)).fetchone()[0] == "superseded"
    assert not lib.db.execute("SELECT 1 FROM metadata_journal WHERE op_id=?", (op,)).fetchone()
    metadata_history.undo_merge(lib, op)
    assert metadata_history.apply_merge(lib, source_op, 1, 2, 0) is None
    assert not lib.db.execute("SELECT 1 FROM file_metadata WHERE file_id=2").fetchone()


def test_multiroot_missing_keeper_uses_logical_key_and_stable_id(history):
    lib, source_op = history
    prepare(lib, source_op)
    source_root = lib.root / "secondary"
    source_root.mkdir()
    lib.db.execute("INSERT INTO library_roots(path,label,token,online) VALUES (?,'Archive','metadata-test-root',0)",
                   (str(source_root),))
    lib._reload_roots()
    lib.db.execute("UPDATE files SET rel_path='@root:2\\keeper.jpg',root_id=2 WHERE id=2")
    lib.mark_missing([2])
    before = organisation.state(lib, 2)
    op = metadata_history.apply_merge(lib, source_op, 1, 2, -1)
    row = lib.db.execute("SELECT src,src_key FROM operations WHERE id=?", (op,)).fetchone()
    assert row["src"] == str(source_root / "keeper.jpg") and row["src_key"] == "@root:2\\keeper.jpg"
    restore_source(lib, source_op)
    metadata_history.undo_merge(lib, op)
    assert organisation.state(lib, 2) == before


def test_invalid_source_identity_and_operation_state_fail_without_changes(history):
    lib, source_op = history
    prepare(lib, source_op)
    before = organisation.state(lib, 2)
    for source_id, keeper_id in ((3, 2), (1, 3), (2, 2), (True, 2), (1, 999)):
        with pytest.raises(ValueError):
            metadata_history.apply_merge(lib, source_op, source_id, keeper_id, 0)
    lib.db.execute("UPDATE operations SET status='pending' WHERE id=?", (source_op,))
    with pytest.raises(ValueError, match="completed"):
        metadata_history.apply_merge(lib, source_op, 1, 2, 0)
    with pytest.raises(ValueError, match="not an organisation"):
        metadata_history.undo_merge(lib, source_op)
    assert organisation.state(lib, 2) == before
    assert not lib.db.execute("SELECT 1 FROM metadata_journal").fetchone()


def test_undo_compares_tag_membership_independently_of_sqlite_case_order(history):
    lib, source_op = history
    organisation.edit(lib, [1], add_tags=["àne"])
    organisation.edit(lib, [2], add_tags=["Été"])
    lib.park_rows([(source_op, 1)])
    op = metadata_history.apply_merge(lib, source_op, 1, 2, 0)
    restore_source(lib, source_op)
    metadata_history.undo_merge(lib, op)
    assert organisation.state(lib, 2)["tags"] == ["Été"]


def test_changed_album_membership_refuses_undo(history):
    lib, source_op = history
    source_album, _ = prepare(lib, source_op)
    op = metadata_history.apply_merge(lib, source_op, 1, 2, 0)
    restore_source(lib, source_op)
    albums.remove(lib, source_album, [2])
    current = organisation.state(lib, 2)
    with pytest.raises(ValueError, match="changed after"):
        metadata_history.undo_merge(lib, op)
    assert organisation.state(lib, 2) == current
