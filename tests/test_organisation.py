"""User organisation persists independently of scans, derived data and media bytes."""
import json
from dataclasses import replace

import pytest

from memoria.engine import albums, organisation, scanner, storage
from memoria.engine.db import Library


@pytest.fixture
def organised(tmp_path):
    root = tmp_path / "library"
    root.mkdir()
    lib = Library(root)
    with lib.transaction() as db:
        db.executemany("INSERT INTO files(rel_path,folder,name,ext,kind,size,mtime,analyzed) "
                       "VALUES (?,'',?,'.jpg','image',10,1,1)", [(f"{i}.jpg", f"{i}.jpg") for i in range(3)])
    yield lib
    lib.close()


def test_snapshot_merge_is_pure_and_preserves_keeper_choices(organised):
    lib = organised
    first = albums.create(lib, "Source album", [1])
    second = albums.create(lib, "Keeper album", [2])
    organisation.edit(lib, [1], rating=5, favorite=True, review="reject", add_tags=["Trip", "BLUE"])
    organisation.edit(lib, [2], rating=3, review="pick", add_tags=["blue", "Keeper"])
    lib.db.execute("UPDATE files SET baseline_hash='do not copy' WHERE id=1")
    before_source = organisation.state(lib, 1)
    changes = lib.db.total_changes
    before, after = organisation.merged_state(lib, 1, 2)
    assert lib.db.total_changes == changes
    assert after == {"rating": 3, "favorite": True, "review": "pick",
                     "tags": ["BLUE", "Keeper", "Trip"], "albums": [first, second]}
    assert organisation.state(lib, 1) == before_source
    with lib.transaction():
        organisation.set_state(lib, 2, after)
    assert organisation.state(lib, 2) == after
    assert lib.file(2)["baseline_hash"] is None
    organisation.set_state(lib, 2, before)
    assert organisation.state(lib, 2) == before
    before, after = organisation.merged_state(lib, 1, 3)
    assert after["rating"] == 5 and after["review"] == "reject"
    organisation.set_state(lib, 3, after)
    root = lib.root
    lib.close()
    reopened = Library(root)
    try:
        assert organisation.state(reopened, 3) == after
    finally:
        reopened.close()


def test_retained_ids_and_cleanup_never_reassign_metadata(organised):
    lib = organised
    aid = albums.create(lib, "Retained", [1, 2])
    organisation.edit(lib, [1, 2], rating=4, add_tags=["Keep"])
    lib.mark_missing([1])
    parked = dict(lib.file(2))
    lib.db.execute("INSERT INTO parked_files VALUES (99,2,?)", (json.dumps(parked),))
    lib.db.execute("DELETE FROM files WHERE id=2")
    snapshot = organisation.state(lib, 2)
    organisation.set_state(lib, 1, snapshot)
    albums.cleanup(lib)
    assert organisation.state(lib, 1)["albums"] == [aid]
    assert organisation.state(lib, 2)["rating"] == 4
    with pytest.raises(ValueError, match="no longer"):
        organisation.edit(lib, [1], rating=1)
    lib.db.execute("DELETE FROM missing_files")
    organisation.cleanup(lib)
    assert lib.db.execute("SELECT COUNT(*) FROM file_metadata WHERE file_id=1").fetchone()[0] == 0
    assert lib.db.execute("SELECT COUNT(*) FROM file_tags WHERE file_id=1").fetchone()[0] == 0
    assert organisation.state(lib, 2) == snapshot


@pytest.mark.parametrize("changes", [
    {"rating": -1}, {"rating": 6}, {"rating": True}, {"rating": "5"},
    {"favorite": 2}, {"review": "delete"}, {"add_tags": [""]}, {"add_tags": "tag"},
    {"add_tags": ["bad\nname"]},
])
def test_invalid_batch_is_atomic(organised, changes):
    before = organisation.state(organised, 1)
    with pytest.raises(ValueError):
        organisation.edit(organised, [1, 2], **changes)
    assert organisation.state(organised, 1) == before
    with pytest.raises(ValueError):
        organisation.edit(organised, [1, 999], rating=5)
    assert organisation.state(organised, 1) == before


def test_state_rejects_bad_ids_and_smart_membership(organised):
    from memoria.engine import catalogue
    smart = albums.create_smart(organised, "Dynamic", catalogue.Filters())
    value = organisation.state(organised, 1)
    with pytest.raises(ValueError):
        organisation.set_state(organised, 1, {**value, "albums": [smart]})
    for bad in (True, "1", 0, -1, 999):
        with pytest.raises(ValueError):
            organisation.state(organised, bad)
    with pytest.raises(ValueError):
        organisation.set_state(organised, 1, {**value, "baseline_hash": "not organisation"})


def test_reset_preserves_organisation_unless_explicit_and_forget_cleans_links(organised, monkeypatch):
    lib = organised
    organisation.edit(lib, [1, 2], rating=5, favorite=True, review="pick", add_tags=["Family"])
    snapshot = organisation.state(lib, 1)
    monkeypatch.setattr(scanner, "index", lambda *args: None)
    storage.reset(lib, storage.ResetOptions())
    assert organisation.state(lib, 1) == snapshot
    lib.mark_missing([2])
    storage.reset(lib, storage.ResetOptions(thumbnails=False, analysis=False, videos=False, missing=True))
    assert not lib.db.execute("SELECT 1 FROM file_tags WHERE file_id=2").fetchone()
    assert not lib.db.execute("SELECT 1 FROM file_metadata WHERE file_id=2").fetchone()
    assert organisation.state(lib, 1) == snapshot
    storage.reset(lib, replace(storage.ResetOptions(), organisation=True))
    assert organisation.state(lib, 1) == {"rating": 0, "favorite": False, "review": "unreviewed",
                                          "tags": [], "albums": []}


def test_reset_organisation_requires_explicit_ui_acknowledgement():
    from PySide6.QtWidgets import QApplication
    from memoria.ui.storage_dialog import StorageDialog
    app = QApplication.instance() or QApplication([])
    dialog = StorageDialog(None, {"catalogue": 0, "thumbnails": 0})
    assert not dialog.boxes["organisation"].isChecked()
    dialog.boxes["organisation"].setChecked(True)
    assert not dialog.go_btn.isEnabled()
    dialog.ack.setChecked(True)
    assert dialog.go_btn.isEnabled()
    assert dialog.options().organisation
    dialog.close()
    dialog.deleteLater()
    app.processEvents()


@pytest.mark.parametrize("category", ["organisation", "albums", "missing"])
def test_reset_sanitizes_only_selected_metadata_journal_fields(organised, monkeypatch, category):
    lib = organised
    aid = albums.create(lib, "Keep unless reset", [1])
    organisation.edit(lib, [1], rating=5, favorite=True, review="pick", add_tags=["Travel"])
    snapshot = organisation.state(lib, 1)
    lib.db.execute("INSERT INTO batches(id,created_at,kind,title,status) "
                   "VALUES ('test','2026-01-01','duplicates','Test journal','applied')")
    op_id = lib.db.execute("INSERT INTO operations(batch_id,seq,op,src,status) "
                           "VALUES ('test',0,'metadata','0.jpg','done')").lastrowid
    lib.db.execute("INSERT INTO metadata_journal(op_id,file_id,before_json,after_json) VALUES (?,1,?,?)",
                   (op_id, json.dumps(snapshot), json.dumps(snapshot)))
    if category == "missing":
        lib.mark_missing([1])
    monkeypatch.setattr(scanner, "index", lambda *args: None)
    storage.reset(lib, replace(storage.ResetOptions(thumbnails=False, analysis=False, videos=False), **{category: True}))
    row = lib.db.execute("SELECT * FROM metadata_journal WHERE op_id=?", (op_id,)).fetchone()
    if category == "missing":
        assert row is None
        assert lib.db.execute("SELECT status FROM operations WHERE id=?", (op_id,)).fetchone()[0] == "superseded"
    else:
        for key in ("before_json", "after_json"):
            saved = json.loads(row[key])
            assert saved["albums"] == ([] if category == "albums" else [aid])
            assert saved["rating"] == (0 if category == "organisation" else 5)
            assert saved["favorite"] == (category != "organisation")
            assert saved["review"] == ("unreviewed" if category == "organisation" else "pick")
            assert saved["tags"] == ([] if category == "organisation" else ["Travel"])
