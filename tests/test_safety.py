"""Regression tests for the safety fixes in 1.1 (catalogue integrity, locking, schema, long paths)."""
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

from memoria.engine import actions, duplicates, health, organize, scanner
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
    lib = Library(tmp_path)
    assert lib.db.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION
    lib.db.execute("DROP TABLE parked_files")
    lib.db.execute("PRAGMA user_version=0")      # what a 1.0 catalogue looks like
    lib.close()
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
