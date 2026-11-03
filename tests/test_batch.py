"""Batch operations from Photos & videos, and the read-only "Check everything" pass."""
from pathlib import Path

import pytest

from memoria.engine import actions, batch, checkup, scanner
from memoria.engine.hashing import full_hash
from memoria.engine.progress import Progress
from tests.test_engine import tree_snapshot


def pick(lib, n=3):
    return [dict(r) for r in lib.files("kind='image' AND error IS NULL", order="rel_path")[:n]]


def test_copy_to_folder_is_verified_and_undoable(library, tmp_path):
    rows = pick(library)
    dest = tmp_path / "Export"
    dest.mkdir()
    (dest / rows[0]["name"]).write_bytes(b"someone else's file")       # name clash must not be overwritten
    before_lib = tree_snapshot(library.root)
    res = actions.apply(library, "batch", "Copy", batch.plan_copy_to(library, rows, dest))
    assert res.ok and res.done == 3
    assert (dest / rows[0]["name"]).read_bytes() == b"someone else's file"
    copies = sorted(p for p in dest.iterdir() if p.read_bytes() != b"someone else's file")
    assert sorted(full_hash(p) for p in copies) == sorted(full_hash(library.abspath(r["rel_path"])) for r in rows)
    assert tree_snapshot(library.root) == before_lib                    # originals untouched
    actions.undo(library, res.batch_id)
    assert [p.name for p in dest.iterdir()] == [rows[0]["name"]]


def test_move_within_library_keeps_rows_and_undoes(library):
    rows = pick(library)
    ids = {r["id"] for r in rows}
    dest = library.root / "Favourites"
    dest.mkdir()
    before = tree_snapshot(library.root)
    res = actions.apply(library, "batch", "Move", batch.plan_move_within(library, rows, dest))
    assert res.ok and res.done == 3
    for r in rows:
        moved = library.file(r["id"])
        assert moved["rel_path"] == f"Favourites\\{r['name']}" and moved["analyzed"] == 1
    s = scanner.scan(library)
    assert (s.added, s.removed) == (0, 0)
    actions.undo(library, res.batch_id)
    assert {library.file_by_rel(r["rel_path"])["id"] for r in rows} == ids
    assert tree_snapshot(library.root) == before


def test_move_outside_library_is_refused(library, tmp_path):
    with pytest.raises(ValueError):
        batch.plan_move_within(library, pick(library), tmp_path)
    with pytest.raises(ValueError):
        batch.plan_copy_to(library, pick(library), library.root / ".memoria")


def test_batch_recycle_and_undo(library):
    rows = pick(library, 5)
    before = tree_snapshot(library.root)
    res = actions.apply(library, "batch", "Recycle", batch.plan_recycle(library, rows))
    assert res.done == 5 and all(library.file(r["id"]) is None for r in rows)
    actions.undo(library, res.batch_id)
    assert tree_snapshot(library.root) == before
    assert all(library.file(r["id"]) is not None for r in rows)


def test_checkup_is_read_only_and_matches_ground_truth(library, expected):
    before = tree_snapshot(library.root)
    seen = []
    prog = Progress(lambda d, t, m: seen.append((d, t, m)), interval=0)
    c = checkup.run(library, prog)
    assert tree_snapshot(library.root) == before
    got = sorted(sorted(f["rel_path"] for f in g.files) for g in c.results["duplicates"])
    assert got == expected["duplicate_groups"]
    assert len(c.results["similar"]) == len(expected["bursts"]) + len(expected["near_duplicates"])
    if "similar_videos" in expected:
        assert len(c.results["similar_videos"]) == len(expected["similar_videos"])
    assert c.counts["tidy"] == len(expected["junk"]) + len(expected["empty_files"]) + len(expected["empty_folders"])
    assert set(expected["blurry"]) <= {r["rel_path"] for r in c.results["blurry"]}
    assert seen and all(t in (0, 1000) for _, t, _ in seen)
    assert max(d for d, t, _ in seen if t) == 1000 and any(m.startswith("Step ") for _, _, m in seen)
