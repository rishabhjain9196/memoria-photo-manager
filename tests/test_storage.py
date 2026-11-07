"""Reset tests use tiny media and fault injection, never a second full-size library."""
import json
import os
import sqlite3
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pytest
from PIL import Image

from memoria.engine import actions, albums, batch, health, scanner, storage
from memoria.engine.db import Library
from memoria.engine.hashing import full_hash
from memoria.engine.progress import Cancelled, Progress


@pytest.fixture
def catalogue(tmp_path):
    root = tmp_path / "library"
    root.mkdir()
    for i, color in enumerate(("red", "green", "blue")):
        Image.new("RGB", (32, 24), color).save(root / f"{i}.jpg")
    lib = Library(root)
    scanner.index(lib)
    health.run_health(lib)
    rows = [dict(r) for r in lib.files()]
    albums.create(lib, "Keep this album", [r["id"] for r in rows])
    lib.db.execute("INSERT INTO people VALUES (1,'Keep this name','2026-01-01')")
    for row in rows:
        lib.db.execute("INSERT INTO faces(file_id,x,y,w,h,score,emb,person_id,confirmed) "
                       "VALUES (?,0,0,1,1,1,?,1,1)", (row["id"], bytes(512)))
        lib.db.execute("INSERT INTO face_scans VALUES (?,?,?,1)", (row["id"], row["size"], row["mtime"]))
    lib.db.execute("CREATE TABLE video_sigs(file_id INTEGER PRIMARY KEY, sig TEXT)")
    lib.db.execute("INSERT INTO video_sigs VALUES (?,'test')", (rows[0]["id"],))
    result = actions.apply(lib, "batch", "Recycle", batch.plan_recycle(lib, [rows[1]]))
    (root / rows[2]["rel_path"]).unlink()
    scanner.scan(lib)
    yield lib, rows, result.batch_id
    lib.close()


def media_snapshot(lib):
    return {str(p.relative_to(lib.root)): (full_hash(p), p.stat().st_mtime_ns)
            for p in lib.root.rglob("*.jpg")}


def test_safe_rebuild_keeps_media_metadata_and_undo(catalogue):
    lib, rows, bid = catalogue
    before = media_snapshot(lib)
    ops = actions.operations(lib, bid)
    storage.reset(lib, storage.ResetOptions())
    assert storage.pending(lib) is None
    assert media_snapshot(lib) == before
    assert actions.operations(lib, bid) == ops
    assert lib.file(rows[0]["id"])["baseline_hash"] == rows[0]["baseline_hash"]
    assert lib.thumbnail(rows[0]["id"])
    assert lib.db.execute("SELECT name FROM people").fetchone()[0] == "Keep this name"
    assert lib.db.execute("SELECT COUNT(*) FROM album_items").fetchone()[0] == 3
    assert lib.db.execute("SELECT COUNT(*) FROM faces").fetchone()[0] == 3
    assert lib.missing()[0]["id"] == rows[2]["id"]
    assert actions.undo(lib, bid).ok
    restored = lib.file(rows[1]["id"])
    assert restored["baseline_hash"] == rows[1]["baseline_hash"]
    assert restored["analyzed"] == 0
    scanner.index(lib)
    assert lib.thumbnail(rows[1]["id"])


def test_hard_reset_only_clears_catalogue_selections(catalogue):
    lib, rows, bid = catalogue
    before = media_snapshot(lib)
    options = storage.ResetOptions(people=True, albums=True, health=True, missing=True)
    storage.reset(lib, options)
    assert media_snapshot(lib) == before
    for table in ("people", "faces", "face_scans", "face_rejects", "albums", "album_items", "video_sigs", "missing_files"):
        assert lib.db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 0
    assert lib.file(rows[0]["id"])["baseline_hash"] is None
    parked = json.loads(lib.db.execute("SELECT data FROM parked_files").fetchone()[0])
    assert parked["baseline_hash"] is None
    assert actions.undo(lib, bid).done == 1
    assert lib.file(rows[1]["id"])["id"] == rows[1]["id"]
    assert full_hash(lib.abspath(rows[1]["rel_path"])) == rows[1]["baseline_hash"]


@pytest.mark.parametrize("category", ["people", "albums", "health", "missing"])
def test_custom_reset_leaves_unselected_data(catalogue, category):
    lib, rows, _ = catalogue
    options = storage.ResetOptions(thumbnails=False, analysis=False, videos=False)
    storage.reset(lib, replace(options, **{category: True}))
    assert bool(lib.db.execute("SELECT 1 FROM people").fetchone()) == (category != "people")
    assert bool(lib.db.execute("SELECT 1 FROM albums").fetchone()) == (category != "albums")
    assert bool(lib.file(rows[0]["id"])["baseline_hash"]) == (category != "health")
    assert bool(lib.missing()) == (category != "missing")
    assert lib.db.execute("SELECT COUNT(*) FROM video_sigs").fetchone()[0] == 1


def test_reset_transaction_failure_rolls_back(catalogue):
    lib, rows, _ = catalogue
    lib.db.execute("CREATE TEMP TRIGGER deny_reset BEFORE DELETE ON albums BEGIN "
                   "SELECT RAISE(ABORT,'test write failure'); END")
    with pytest.raises(sqlite3.IntegrityError, match="test write failure"):
        storage.reset(lib, storage.ResetOptions(people=True, albums=True))
    assert storage.pending(lib) is None
    assert lib.db.execute("SELECT name FROM people").fetchone()[0] == "Keep this name"
    assert lib.file(rows[0]["id"])["analyzed"] == 1


def test_process_death_after_commit_can_resume(catalogue):
    lib, rows, bid = catalogue
    before = media_snapshot(lib)
    root = lib.root
    lib.close()
    code = (
        "import os\n"
        "from memoria.engine import storage\n"
        "from memoria.engine.db import Library\n"
        f"lib = Library({str(root)!r})\n"
        "storage._clear_caches = lambda *args: os._exit(73)\n"
        "storage.reset(lib, storage.ResetOptions())\n"
    )
    proc = subprocess.run([sys.executable, "-c", code], cwd=Path(__file__).resolve().parents[1],
                          capture_output=True, text=True, timeout=30)
    assert proc.returncode == 73, proc.stderr
    reopened = Library(root)
    try:
        assert storage.pending(reopened)["phase"] == "caches"
        storage.resume(reopened)
        assert storage.pending(reopened) is None
        assert media_snapshot(reopened) == before
        assert reopened.file(rows[0]["id"])["baseline_hash"] == rows[0]["baseline_hash"]
        assert actions.undo(reopened, bid).done == 1
    finally:
        reopened.close()


def test_cancel_rebuild_retry_does_not_clear_twice(catalogue, monkeypatch):
    lib, _, _ = catalogue
    def cancelled(*args):
        raise Cancelled()
    with monkeypatch.context() as m:
        m.setattr(scanner, "index", cancelled)
        with pytest.raises(Cancelled):
            storage.reset(lib, storage.ResetOptions(people=True))
    assert storage.pending(lib)["phase"] == "rebuild"
    lib.db.execute("INSERT INTO people VALUES (2,'New name after clear','2026-01-01')")
    storage.resume(lib)
    assert lib.db.execute("SELECT name FROM people").fetchone()[0] == "New name after clear"


def test_cancel_before_reset_changes_nothing(catalogue):
    lib, rows, _ = catalogue
    progress = Progress()
    progress.cancel_event.set()
    with pytest.raises(Cancelled):
        storage.reset(lib, storage.ResetOptions(people=True), progress)
    assert storage.pending(lib) is None
    assert lib.file(rows[0]["id"])["analyzed"] == 1
    assert lib.db.execute("SELECT COUNT(*) FROM people").fetchone()[0] == 1


def test_resume_discovers_media_changes_during_interruption(catalogue, monkeypatch):
    lib, rows, _ = catalogue
    def cancelled(*args):
        raise Cancelled()
    with monkeypatch.context() as m:
        m.setattr(scanner, "index", cancelled)
        with pytest.raises(Cancelled):
            storage.reset(lib, storage.ResetOptions())
    changed = lib.abspath(rows[0]["rel_path"])
    Image.new("RGB", (48, 36), "purple").save(changed)
    Image.new("RGB", (24, 24), "yellow").save(lib.root / "new.jpg")
    scan, _ = storage.resume(lib)
    assert scan.changed == 1 and scan.added == 1
    assert lib.file(rows[0]["id"])["width"] == 48
    assert lib.file(rows[0]["id"])["baseline_hash"] == rows[0]["baseline_hash"]
    assert lib.file_by_rel("new.jpg")["analyzed"] == 1
    assert storage.pending(lib) is None


def test_low_space_and_failed_compaction_are_recoverable(catalogue, monkeypatch):
    lib, rows, _ = catalogue
    from collections import namedtuple
    Usage = namedtuple("Usage", "total used free")
    with monkeypatch.context() as m:
        m.setattr(storage.shutil, "disk_usage", lambda _: Usage(100, 100, 0))
        with pytest.raises(OSError, match="Not enough free space"):
            storage.reset(lib, storage.ResetOptions(compact=True))
    assert storage.pending(lib) is None
    assert lib.file(rows[0]["id"])["analyzed"] == 1
    def failed(*args):
        raise OSError("test disk full during compaction")
    with monkeypatch.context() as m:
        m.setattr(storage, "_compact", failed)
        with pytest.raises(OSError, match="test disk full"):
            storage.reset(lib, storage.ResetOptions(compact=True))
    assert storage.pending(lib)["phase"] == "compact"
    storage.resume(lib, skip_compact=True)
    assert storage.pending(lib) is None


def test_storage_compaction_reclaims_space(catalogue):
    lib, _, _ = catalogue
    with lib.transaction() as db:
        db.execute("INSERT INTO video_sigs VALUES (999, zeroblob(2097152))")
    before = storage.usage(lib)["catalogue"]
    options = storage.ResetOptions(thumbnails=False, analysis=False, videos=True, compact=True)
    storage.reset(lib, options)
    assert storage.usage(lib)["catalogue"] < before - 1024 * 1024
