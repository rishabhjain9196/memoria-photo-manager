"""Regression tests for the safety fixes in 1.1 (catalogue integrity, locking, schema, long paths)."""
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

from memoria.engine import actions, albums, batch, compare, duplicates, health, organize, scanner
from memoria.engine.config import longpath
from memoria.engine.db import SCHEMA_VERSION, Library, LibraryInUse, LibraryTooNew, LibraryUnavailable

ROOT = Path(__file__).resolve().parent.parent


def snapshot_rows(lib: Library) -> dict[str, tuple]:
    return {r["rel_path"]: (r["id"], r["baseline_hash"], r["dhash"], r["analyzed"]) for r in lib.files()}


# ------------------------------------------------------------------------- unreachable folders
def test_unplugged_drive_does_not_wipe_catalogue(library, monkeypatch):
    before = snapshot_rows(library)
    real_isdir = os.path.isdir
    monkeypatch.setattr(scanner.os.path, "isdir", lambda p: False if str(p) == str(library.root) else real_isdir(p))
    with pytest.raises(LibraryUnavailable):
        scanner.scan(library)
    monkeypatch.undo()
    assert snapshot_rows(library) == before


def test_unreadable_folder_keeps_its_rows(library, monkeypatch):
    target = str(library.root / "DCIM" / "101CANON")
    under = [r["rel_path"] for r in library.files("rel_path LIKE 'DCIM\\101CANON\\%'")]
    assert under
    real = scanner.os.scandir

    def flaky(path):
        if os.path.normcase(str(path)) == os.path.normcase(longpath(target)):
            raise PermissionError("denied")
        return real(path)

    monkeypatch.setattr(scanner.os, "scandir", flaky)
    res = scanner.scan(library)
    assert res.removed == 0 and res.unreadable_folders == 1
    assert all(library.file_by_rel(r) is not None for r in under)


def test_files_really_deleted_are_still_removed(library):
    victim = library.files("kind='image' AND error IS NULL")[0]
    os.remove(library.abspath(victim["rel_path"]))
    assert scanner.scan(library).removed == 1
    assert library.file_by_rel(victim["rel_path"]) is None


# ------------------------------------------------------------------------- undo keeps catalogue
def test_recycle_undo_keeps_ids_thumbnails_and_fingerprints(library):
    health.run_health(library)
    before = snapshot_rows(library)
    groups = duplicates.find_duplicates(library)
    plan = duplicates.plan_removal(library, groups)
    moved = {a.file_id for a in plan}
    res = actions.apply(library, "duplicates", "Remove", plan)
    assert res.done == len(plan)
    assert all(library.file(i) is None for i in moved)
    assert all(library.thumbnail(i) for i in moved if before)  # thumbnails survive while parked
    actions.undo(library, res.batch_id)
    assert snapshot_rows(library) == before
    rescan = scanner.scan(library)
    assert (rescan.added, rescan.changed, rescan.removed) == (0, 0, 0)
    assert health.run_health(library).counts["new"] == 0


def test_organize_undo_keeps_ids(library):
    before = snapshot_rows(library)
    plan = organize.plan_organize(library)
    res = actions.apply(library, "organize", "Organise", organize.plan_actions(library, plan.items))
    assert res.done == len(plan.items)
    actions.undo(library, res.batch_id)
    assert snapshot_rows(library) == before


def test_empty_recovery_drops_parked_rows(library):
    groups = duplicates.find_duplicates(library)
    plan = duplicates.plan_removal(library, groups)
    res = actions.apply(library, "duplicates", "Remove", plan)
    assert library.db.execute("SELECT COUNT(*) FROM parked_files").fetchone()[0] == res.done
    actions.empty_recovery(library, [res.batch_id])
    assert library.db.execute("SELECT COUNT(*) FROM parked_files").fetchone()[0] == 0
    assert all(library.thumbnail(a.file_id) is None for a in plan)


# ------------------------------------------------------------------------- locking
def test_library_is_locked_against_other_processes(library):
    code = ("import sys; sys.path.insert(0, r'%s');"
            "from memoria.engine.db import Library, LibraryInUse\n"
            "try:\n Library(r'%s'); print('OPENED')\nexcept LibraryInUse: print('LOCKED')") % (ROOT, library.root)
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=60).stdout
    assert "LOCKED" in out


def test_lock_is_reentrant_in_process_and_released_on_close(library):
    again = Library(library.root)        # same process: allowed (e.g. reopening from Recent)
    again.close()
    library.close()
    code = ("import sys; sys.path.insert(0, r'%s');"
            "from memoria.engine.db import Library\nLibrary(r'%s').close(); print('OPENED')") % (ROOT, library.root)
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=60).stdout
    assert "OPENED" in out


# ------------------------------------------------------------------------- schema
def test_schema_version_and_migration_from_v1(tmp_path):
    from memoria.engine.db import SCHEMA
    app_dir = tmp_path / ".memoria"
    app_dir.mkdir()
    db = sqlite3.connect(app_dir / "memoria.db")
    db.executescript(SCHEMA)
    db.close()
    lib = Library(tmp_path)
    assert lib.db.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION
    lib.db.execute("SELECT COUNT(*) FROM parked_files")
    lib.close()


def test_refuses_catalogue_from_newer_version(tmp_path):
    Library(tmp_path).close()
    db = sqlite3.connect(tmp_path / ".memoria" / "memoria.db")
    db.execute("PRAGMA user_version=999")
    db.commit()
    db.close()
    with pytest.raises(LibraryTooNew):
        Library(tmp_path)
    # The lock must be released after a failed open.
    db = sqlite3.connect(tmp_path / ".memoria" / "memoria.db")
    db.execute(f"PRAGMA user_version={SCHEMA_VERSION}")
    db.commit()
    db.close()
    Library(tmp_path).close()


# ------------------------------------------------------------------------- long paths
@pytest.mark.skipif(os.name != "nt", reason="Windows path-length limit")
def test_paths_longer_than_260_characters(library):
    src = next(r for r in library.files("kind='image' AND error IS NULL AND ext='.jpg'"))
    deep = library.root
    while len(str(deep)) < 300:
        deep = deep / ("very long folder name " * 2).strip()
    os.makedirs(longpath(deep), exist_ok=True)
    target = deep / "deep photo.jpg"
    with open(longpath(library.abspath(src["rel_path"])), "rb") as a, open(longpath(target), "wb") as b:
        b.write(a.read())
    assert len(str(target)) > 260
    scanner.index(library)
    row = library.file_by_rel(str(target.relative_to(library.root)))
    assert row is not None and row["analyzed"] == 1 and row["error"] is None and row["width"] > 0
    groups = [g for g in duplicates.find_duplicates(library) if any(f["id"] == row["id"] for f in g.files)]
    assert groups, "deep copy should be found as a duplicate"
    res = actions.apply(library, "duplicates", "Remove", duplicates.plan_removal(library, groups))
    assert res.ok and res.done >= 1
    assert actions.undo(library, res.batch_id).ok
    assert os.path.exists(longpath(target))


@pytest.fixture
def tiny_library(tmp_path):
    root = tmp_path / "tiny"
    root.mkdir()
    (root / "one.txt").write_bytes(b"original")
    lib = Library(root)
    scanner.scan(lib)
    yield lib
    lib.close()


def test_copy_undo_rejects_modified_and_legacy_unverified_outputs(tiny_library, tmp_path):
    lib = tiny_library
    row = dict(lib.files()[0])
    res = actions.apply(lib, "batch", "Copy", batch.plan_copy_to(lib, [row], tmp_path / "export"))
    op = actions.operations(lib, res.batch_id)[0]
    assert op["hash"]
    dst = Path(op["dst"])
    dst.write_bytes(b"edited by user")
    assert actions.undo(lib, res.batch_id).failed == 1
    assert dst.read_bytes() == b"edited by user"
    lib.db.execute("UPDATE operations SET hash=NULL WHERE id=?", (op["id"],))
    assert actions.undo(lib, res.batch_id).failed == 1
    assert dst.exists()


def test_recycle_import_undo_preserves_album_identity(tiny_library):
    lib = tiny_library
    row = dict(lib.files()[0])
    aid = albums.create(lib, "Original", [row["id"]])
    res = actions.apply(lib, "batch", "Recycle", batch.plan_recycle(lib, [row]))
    (lib.root / "two.txt").write_bytes(b"unrelated")
    scanner.scan(lib)
    assert lib.file_by_rel("two.txt")["id"] != row["id"]
    assert actions.undo(lib, res.batch_id).ok
    assert lib.file_by_rel("one.txt")["id"] == row["id"]
    assert lib.db.execute("SELECT f.name FROM files f JOIN album_items i ON i.file_id=f.id "
                          "WHERE i.album_id=?", (aid,)).fetchone()[0] == "one.txt"


def test_failed_stat_keeps_catalogue(tiny_library, monkeypatch):
    lib = tiny_library
    before = snapshot_rows(lib)
    def denied(*args, **kwargs):
        raise PermissionError("test access failure")
    monkeypatch.setattr(scanner._Entry, "stat", denied)
    res = scanner.scan(lib)
    assert res.unreadable_files == 1 and res.removed == 0
    assert snapshot_rows(lib) == before


def test_missing_survives_rescan_and_return_preserves_fingerprint(tiny_library):
    lib = tiny_library
    health.run_health(lib)
    before = dict(lib.files()[0])
    p = lib.root / "one.txt"
    contents, st = p.read_bytes(), p.stat()
    p.unlink()
    scanner.scan(lib)
    report = health.run_health(lib)
    assert report.counts["missing"] == 1
    assert report.problems[0]["rel_path"] == "one.txt"
    (lib.root / "new.txt").write_bytes(b"new")
    scanner.scan(lib)
    assert lib.file_by_rel("new.txt")["id"] != before["id"]
    p.write_bytes(contents)
    os.utime(p, (st.st_atime, st.st_mtime))
    scanner.scan(lib)
    assert lib.file_by_rel("one.txt")["id"] == before["id"]
    assert lib.file_by_rel("one.txt")["baseline_hash"] == before["baseline_hash"]
    assert health.run_health(lib).counts["missing"] == 0


def test_reconcile_crash_between_move_and_catalogue(tiny_library, monkeypatch):
    lib = tiny_library
    health.run_health(lib)
    row = dict(lib.files()[0])
    original = actions.safe_move
    def crash(src, dst):
        original(src, dst)
        raise SystemExit("test interruption")
    with monkeypatch.context() as m:
        m.setattr(actions, "safe_move", crash)
        with pytest.raises(SystemExit):
            actions.apply(lib, "batch", "Recycle", batch.plan_recycle(lib, [row]))
    assert actions.reconcile(lib) == 1
    entry = actions.batches(lib)[0]
    assert entry["files"] == 1
    scanner.scan(lib)
    assert actions.undo(lib, entry["id"]).ok
    assert lib.file_by_rel("one.txt")["baseline_hash"] == row["baseline_hash"]


def test_locked_recovery_retains_history_and_undo(tiny_library, monkeypatch):
    lib = tiny_library
    res = actions.apply(lib, "batch", "Recycle", batch.plan_recycle(lib, [dict(lib.files()[0])]))
    def locked(*args, **kwargs):
        raise PermissionError("test locked file")
    with monkeypatch.context() as m:
        m.setattr(actions.shutil.os, "unlink", locked)
        with pytest.raises(PermissionError):
            actions.empty_recovery(lib)
    assert actions.operations(lib, res.batch_id)[0]["status"] == "done"
    assert actions.undo(lib, res.batch_id).done == 1


def test_unavailable_backup_never_reports_complete(tiny_library, tmp_path, monkeypatch):
    with pytest.raises(LibraryUnavailable):
        compare.compare(tiny_library, tmp_path / "not-present")
    backup = tmp_path / "backup"
    backup.mkdir()
    sub = backup / "unreadable"
    sub.mkdir()
    real = scanner.os.scandir
    def denied(path):
        if str(path) == str(sub):
            raise PermissionError("test subfolder unavailable")
        return real(path)
    monkeypatch.setattr(scanner.os, "scandir", denied)
    with pytest.raises(LibraryUnavailable):
        compare.compare(tiny_library, backup)


def test_published_output_survives_cancel_in_history(tiny_library, tmp_path):
    from memoria.engine.progress import Cancelled
    from memoria.engine.videotools import publish_file
    temp = tmp_path / "temp"
    temp.write_bytes(b"finished output")
    with pytest.raises(Cancelled):
        with actions.created_batch(tiny_library, "edit", "Edit") as result:
            dst = publish_file(temp, tmp_path / "edited.txt")
            raise Cancelled()
    assert result.done == 1 and dst.exists()
    assert actions.undo(tiny_library, result.batch_id).done == 1
    assert not dst.exists()


def test_created_output_crash_reconciliation(tiny_library, tmp_path, monkeypatch):
    from memoria.engine.videotools import publish_file
    temp, dest = tmp_path / "temp", tmp_path / "created.txt"
    temp.write_bytes(b"created")
    rename = os.rename
    def crash(src, dst):
        rename(src, dst)
        raise SystemExit("test crash after publication")
    with pytest.raises(SystemExit):
        with actions.created_batch(tiny_library, "story", "Story"):
            with monkeypatch.context() as m:
                m.setattr(os, "rename", crash)
                publish_file(temp, dest)
    assert actions.reconcile(tiny_library) == 1
    entry = actions.batches(tiny_library)[0]
    assert entry["files"] == 1
    assert actions.undo(tiny_library, entry["id"]).done == 1
    assert not dest.exists()


def test_v3_migration_reserves_recovered_ids(tmp_path):
    import json
    from memoria.engine.db import SCHEMA, MIGRATIONS
    folder = tmp_path / ".memoria"
    folder.mkdir()
    db = sqlite3.connect(folder / "memoria.db")
    db.row_factory = sqlite3.Row
    db.executescript(SCHEMA)
    for step in (2, 3):
        for sql in MIGRATIONS[step]:
            db.execute(sql)
    db.execute("INSERT INTO files(id,rel_path,folder,name,ext,kind,size,mtime) "
               "VALUES (99,'parked.txt','','parked.txt','.txt','other',4,1)")
    row = dict(db.execute("SELECT * FROM files").fetchone())
    db.execute("INSERT INTO parked_files VALUES (1,99,?)", (json.dumps(row),))
    db.execute("INSERT INTO album_items VALUES (1,99,0)")
    db.execute("DELETE FROM files")
    db.execute("PRAGMA user_version=3")
    db.commit()
    db.close()
    lib = Library(tmp_path)
    try:
        (tmp_path / "new.txt").write_bytes(b"new")
        scanner.scan(lib)
        assert lib.file_by_rel("new.txt")["id"] > 99
        assert lib.restore_parked(1, "parked.txt")
        assert lib.file_by_rel("parked.txt")["id"] == 99
    finally:
        lib.close()
