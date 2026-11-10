import json
import sqlite3
from pathlib import Path

import pytest
from PIL import Image

from memoria.engine import actions, batch, roots, scanner
from memoria.engine.db import Library, MIGRATIONS, SCHEMA, SCHEMA_VERSION


def _photo(path: Path, color="red"):
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (48, 32), color).save(path)


def test_added_roots_keep_distinct_paths_and_original_ids(tmp_path):
    home, added = tmp_path / "home", tmp_path / "phone"
    _photo(home / "same.jpg")
    _photo(added / "same.jpg", "blue")
    with_home = Library(home)
    try:
        scanner.index(with_home)
        first = with_home.file_by_rel("same.jpg")["id"]
        source = roots.add(with_home, added, "iPhone")
        scanner.index(with_home)
        key = roots.key_for(source, "same.jpg")
        second = with_home.file_by_rel(key)
        assert second["id"] != first and second["root_id"] == source
        assert with_home.file_by_rel("same.jpg")["id"] == first
        assert with_home.abspath(key) == added / "same.jpg"
        assert with_home.rel(added / "same.jpg") == key
        assert with_home.display_path(key) == "iPhone\\same.jpg"
        assert with_home.thumbnail(second["id"])
        assert with_home.contains(added / "new.jpg")
        with pytest.raises(ValueError):
            with_home.abspath("@root:999\\same.jpg")
        with pytest.raises(ValueError):
            with_home.abspath("..\\outside.jpg")
    finally:
        with_home.close()


def test_offline_root_reconnect_preserves_cache_and_rebases_undo(tmp_path):
    home, source, moved = tmp_path / "home", tmp_path / "drive", tmp_path / "reconnected"
    _photo(home / "home.jpg")
    _photo(source / "one.jpg")
    _photo(source / "two.jpg", "blue")
    lib = Library(home)
    root_id = roots.add(lib, source)
    scanner.index(lib)
    row = dict(lib.file_by_rel(roots.key_for(root_id, "one.jpg")))
    cached = dict(lib.file_by_rel(roots.key_for(root_id, "two.jpg")))
    result = actions.apply(lib, "batch", "Move one linked-root photo", batch.plan_recycle(lib, [row]))
    assert result.done == 1
    assert (source / ".memoria" / "recovery" / result.batch_id / "one.jpg").exists()
    lib.close()
    source.rename(moved)
    lib = Library(home)
    try:
        scan = scanner.scan(lib)
        assert scan.offline_roots == 1
        assert lib.file(cached["id"])["rel_path"] == cached["rel_path"]
        assert lib.thumbnail(cached["id"])
        assert not lib.missing()
        assert [row["rel_path"] for row in lib.readable_files()] == ["home.jpg"]
        with pytest.raises(RuntimeError, match="offline"):
            lib.check_path(lib.abspath(cached["rel_path"]))
        assert actions.undo(lib, result.batch_id).failed == 1
        assert not source.exists()
        roots.reconnect(lib, root_id, moved)
        assert actions.undo(lib, result.batch_id).ok
        assert lib.file(row["id"])["rel_path"] == row["rel_path"]
        assert (moved / "one.jpg").exists() and not source.exists()
        scanner.index(lib)
        assert lib.stats()["files"] == 3
    finally:
        lib.close()


def test_wrong_drive_identity_cannot_remove_or_empty_recovery(tmp_path):
    home, source = tmp_path / "home", tmp_path / "drive"
    _photo(home / "home.jpg")
    _photo(source / "one.jpg")
    lib = Library(home)
    try:
        root_id = roots.add(lib, source)
        scanner.index(lib)
        row = dict(lib.file_by_rel(roots.key_for(root_id, "one.jpg")))
        marker = source / ".memoria" / roots.MARKER
        old = marker.read_text()
        marker.write_text(json.dumps({"catalogue": "different", "source": "different"}))
        result = actions.apply(lib, "batch", "Reviewed file", batch.plan_recycle(lib, [row]))
        assert result.done == 0 and result.skipped == 1
        assert (source / "one.jpg").exists()
        with pytest.raises(RuntimeError, match="Reconnect"):
            actions.empty_recovery(lib)
        marker.write_text(old)
        scanner.scan(lib)
        assert lib.file(row["id"]) is not None
    finally:
        lib.close()


def test_cross_root_move_and_recovery_purge_keep_journal_consistent(tmp_path):
    home, source = tmp_path / "home", tmp_path / "drive"
    _photo(home / "one.jpg")
    _photo(source / "two.jpg", "blue")
    lib = Library(home)
    try:
        root_id = roots.add(lib, source)
        scanner.index(lib)
        first = dict(lib.file_by_rel("one.jpg"))
        move = actions.apply(lib, "batch", "Move between roots", batch.plan_move_within(lib, [first], source))
        assert move.ok and lib.file(first["id"])["root_id"] == root_id
        assert actions.undo(lib, move.batch_id).ok and lib.file(first["id"])["root_id"] == 1
        rows = [dict(row) for row in lib.files()]
        recycled = actions.apply(lib, "batch", "Both roots", batch.plan_recycle(lib, rows))
        assert recycled.done == 2 and actions.recovery_size(lib)[0] == 2
        assert actions.empty_recovery(lib, [recycled.batch_id]) == 2
        assert actions.recovery_size(lib) == (0, 0)
        assert {op["status"] for op in actions.operations(lib, recycled.batch_id)} == {"purged"}
        assert not lib.db.execute("SELECT 1 FROM parked_files").fetchone()
    finally:
        lib.close()


def test_root_registration_rejects_overlap_and_separate_catalogues(tmp_path):
    home, added, separate = tmp_path / "home", tmp_path / "added", tmp_path / "separate"
    for path in (home / "child", added, separate):
        path.mkdir(parents=True)
    lib = Library(home)
    other = Library(separate)
    try:
        with pytest.raises(ValueError, match="overlap"):
            roots.add(lib, home / "child")
        with pytest.raises(ValueError, match="separate"):
            roots.add(lib, separate)
        roots.add(lib, added)
        with pytest.raises(ValueError, match="owning library"):
            Library(added)
        assert not (added / ".memoria" / "memoria.db").exists()
    finally:
        other.close()
        lib.close()


def test_v7_upgrade_preserves_metadata_and_journal_paths(tmp_path):
    (tmp_path / ".memoria").mkdir()
    path = tmp_path / "photo.jpg"
    _photo(path)
    db = sqlite3.connect(tmp_path / ".memoria" / "memoria.db")
    db.executescript(SCHEMA)
    for version in range(2, 8):
        for sql in MIGRATIONS[version]:
            db.execute(sql)
    db.execute("PRAGMA user_version=7")
    db.execute("INSERT INTO files(id,rel_path,folder,name,ext,kind,size,mtime,chash,metadata_version) "
               "VALUES (42,'photo.jpg','','photo.jpg','.jpg','image',1,1,'confirmed',1)")
    db.execute("INSERT INTO batches VALUES ('old','2026-01-01','batch','Old','applied',1,1)")
    db.execute("INSERT INTO operations(batch_id,seq,op,src,dst,status) VALUES ('old',0,'copy',?,?,'done')",
               (str(path), str(tmp_path / "copy.jpg")))
    db.commit()
    db.close()
    lib = Library(tmp_path)
    try:
        assert lib.db.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION
        assert lib.file(42)["chash"] == "confirmed" and lib.file(42)["root_id"] == 1
        op = lib.db.execute("SELECT * FROM operations").fetchone()
        assert op["src_key"] == "photo.jpg" and op["dst_key"] == "copy.jpg"
    finally:
        lib.close()
