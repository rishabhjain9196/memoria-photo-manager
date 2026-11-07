"""Engine tests against the generated library's ground truth (tools/make_test_library.py)."""
import os
import shutil
from pathlib import Path

import pytest

from memoria.engine import actions, compare, duplicates, health, organize, scanner, similar, tidy
from memoria.engine.config import SAMPLE_BYTES, SAMPLE_POINTS
from memoria.engine.db import Library
from memoria.engine.hashing import full_hash, quick_hash
from memoria.engine.progress import Cancelled, Progress


def tree_snapshot(root: Path) -> dict[str, str]:
    """{relative path: content hash} for every file outside .memoria."""
    out = {}
    for p in root.rglob("*"):
        if p.is_file() and ".memoria" not in p.parts:
            out[str(p.relative_to(root))] = full_hash(p)
    return out


def all_content(lib: Library) -> list[str]:
    """Multiset of content hashes in the library *and* Recovery — must never shrink."""
    return sorted(full_hash(p) for p in lib.root.rglob("*")
                  if p.is_file() and (".memoria" not in p.parts or "recovery" in p.parts))


# --------------------------------------------------------------------------- hashing / scan
def test_quick_hash_is_only_a_prefilter(tmp_path):
    a, b = tmp_path / "a.bin", tmp_path / "b.bin"
    data = bytearray(os.urandom(SAMPLE_BYTES * SAMPLE_POINTS * 4))
    a.write_bytes(data)
    data[SAMPLE_BYTES + 10] ^= 0xFF  # change a byte between sample windows
    b.write_bytes(data)
    assert quick_hash(a, len(data)) == quick_hash(b, len(data))
    assert full_hash(a) != full_hash(b)


def test_scan_is_incremental(library):
    again = scanner.scan(library)
    assert (again.added, again.changed, again.removed) == (0, 0, 0)
    f = library.files("kind='image' AND error IS NULL")[0]
    p = library.abspath(f["rel_path"])
    os.utime(p, (p.stat().st_atime, p.stat().st_mtime + 10))
    (library.root / "Scans" / "scan_001.jpg").unlink()
    res = scanner.scan(library)
    assert (res.added, res.changed, res.removed) == (0, 1, 1)
    assert library.file(f["id"])["analyzed"] == 0
    scanner.analyze(library)
    assert library.file(f["id"])["analyzed"] == 1


def test_index_counts_and_errors(library, expected):
    st = library.stats()
    assert st["files"] == expected["total_files"]
    assert st["pending"] == 0
    errors = {r["rel_path"] for r in library.files("error IS NOT NULL")}
    assert set(expected["corrupt"]) <= errors
    assert not errors & set(expected["dates"])


def test_dates_and_sources(library, expected):
    for rel, want in expected["dates"].items():
        row = library.file_by_rel(rel)
        assert row is not None, rel
        assert (row["taken_at"], row["date_source"]) == (want["date"], want["source"]), rel
    for rel in expected["uncertain_dates"]:
        assert library.file_by_rel(rel)["date_source"] == "modified"


def test_rotated_photos_are_reported_upright(library, expected):
    for rel in expected["rotated"]:
        r = library.file_by_rel(rel)
        assert r["height"] > r["width"]


def test_heic_and_video_analysis(library, expected):
    for rel in expected["heic"]:
        r = library.file_by_rel(rel)
        assert r["error"] is None and r["width"] > 0 and library.thumbnail(r["id"])
    for rel in expected["videos"]:
        r = library.file_by_rel(rel)
        assert r["error"] is None and r["duration"] > 1 and library.thumbnail(r["id"]), rel


# --------------------------------------------------------------------------- duplicates
def test_duplicate_groups_match_ground_truth(library, expected):
    groups = duplicates.find_duplicates(library)
    got = sorted(sorted(f["rel_path"] for f in g.files) for g in groups)
    assert got == expected["duplicate_groups"]
    for g in groups:
        keeper = next(f for f in g.files if f["id"] == g.keeper_id)
        assert not keeper["rel_path"].startswith(("Phone Backup", "Downloads")), keeper["rel_path"]


def test_large_duplicates_are_removed_regression(library, expected):
    """Files > 1.28 MB were skipped by the old CLI because of a sampled/full hash mismatch."""
    groups = [g for g in duplicates.find_duplicates(library)
              if any(f["rel_path"] in expected["large_duplicates"] for f in g.files)]
    assert groups and all(g.size > 1_300_000 for g in groups)
    res = actions.apply(library, "duplicates", "Remove duplicates", duplicates.plan_removal(library, groups))
    assert res.done == len(groups) and res.skipped == 0 and res.failed == 0


def test_duplicate_removal_and_undo(library):
    before_tree = tree_snapshot(library.root)
    before_content = all_content(library)
    groups = duplicates.find_duplicates(library)
    plan = duplicates.plan_removal(library, groups)
    res = actions.apply(library, "duplicates", "Remove duplicates", plan)
    assert res.ok and res.done == sum(len(g.files) - 1 for g in groups)
    assert all_content(library) == before_content          # nothing destroyed, only moved
    assert duplicates.find_duplicates(library) == []
    for g in groups:                                       # keepers untouched
        assert library.abspath(next(f for f in g.files if f["id"] == g.keeper_id)["rel_path"]).exists()
    undo = actions.undo(library, res.batch_id)
    assert undo.ok and undo.done == res.done
    assert tree_snapshot(library.root) == before_tree
    assert actions.batches(library)[0]["status"] == "undone"


def test_duplicate_removal_skips_changed_files(library):
    groups = duplicates.find_duplicates(library)
    g0, g1 = groups[0], groups[1]
    keeper = library.abspath(next(f for f in g0.files if f["id"] == g0.keeper_id)["rel_path"])
    with open(keeper, "r+b") as fh:                        # keeper edited after review
        fh.seek(100)
        fh.write(b"edited")
    dup = library.abspath(next(f for f in g1.files if f["id"] != g1.keeper_id)["rel_path"])
    st = dup.stat()
    with open(dup, "r+b") as fh:                           # duplicate edited, mtime restored
        fh.seek(200)
        fh.write(b"edited")
    os.utime(dup, (st.st_atime, st.st_mtime))
    res = actions.apply(library, "duplicates", "Remove duplicates", duplicates.plan_removal(library, groups))
    assert res.skipped >= len(g0.files) - 1 + 1
    assert keeper.exists() and dup.exists()
    assert any("has changed" in m for m in res.messages)
    assert any("content changed" in m for m in res.messages)


def test_user_can_choose_keeper_and_exclude(library):
    groups = duplicates.find_duplicates(library)
    g = next(g for g in groups if len(g.files) >= 3)
    other = next(f for f in g.files if f["id"] != g.keeper_id)
    excluded = next(f for f in g.files if f["id"] not in (g.keeper_id, other["id"]))
    plan = duplicates.plan_removal(library, [g], keepers={g.hash: other["id"]}, excluded={excluded["id"]})
    assert [a.file_id for a in plan] == [g.keeper_id]


# --------------------------------------------------------------------------- similar / best shot
def test_bursts_grouped_and_best_frame_chosen(library, expected):
    groups = similar.find_similar(library)
    by_member = {f["rel_path"]: g for g in groups for f in g.files}
    for burst in expected["bursts"]:
        g = by_member[burst["files"][0]]
        assert sorted(f["rel_path"] for f in g.files) == sorted(burst["files"])
        assert g.burst
        best = next(f for f in g.files if f["id"] == g.best_id)
        assert best["rel_path"] == burst["best"]
        assert "sharpest" in g.reasons[g.best_id]


def test_near_duplicates_prefer_original(library, expected):
    groups = similar.find_similar(library)
    by_member = {f["rel_path"]: g for g in groups for f in g.files}
    for nd in expected["near_duplicates"]:
        g = by_member[nd["files"][0]]
        assert sorted(f["rel_path"] for f in g.files) == nd["files"]
        assert next(f for f in g.files if f["id"] == g.best_id)["rel_path"] == nd["best"]
        assert not g.burst


def test_similar_excludes_exact_copies_and_screenshots(library, expected):
    groups = similar.find_similar(library)
    members = [f["rel_path"] for g in groups for f in g.files]
    assert len(members) == len(set(members))
    dup_files = {r for grp in expected["duplicate_groups"] for r in grp}
    for g in groups:
        assert sum(f["rel_path"] in dup_files for f in g.files) <= 1
    assert not any("Screenshot" in m for m in members)
    assert len(groups) == len(expected["bursts"]) + len(expected["near_duplicates"])


def test_blurry_detection(library, expected):
    found = {r["rel_path"] for r in similar.find_blurry(library)}
    assert set(expected["blurry"]) <= found
    sharp_originals = {r for r, d in expected["dates"].items() if "BURST" not in r} - set(expected["blurry"])
    assert not found & sharp_originals


# --------------------------------------------------------------------------- organise
def test_organize_plan_apply_undo(library, expected):
    before = tree_snapshot(library.root)
    plan = organize.plan_organize(library, "year_month")
    srcs = {it.src_rel for it in plan.items}
    assert not srcs & set(expected["uncertain_dates"])     # mtime-only dates are skipped by default
    assert not srcs & set(expected["corrupt"])
    for it in plan.items:
        dt = it.taken_at
        assert it.dst_rel.startswith(f"{dt:%Y}\\{dt:%Y-%m}\\")
    dsts = [it.dst_rel.lower() for it in plan.items]
    assert len(dsts) == len(set(dsts))                       # name clashes resolved, nothing overwritten
    res = actions.apply(library, "organize", "Organise", organize.plan_actions(library, plan.items))
    assert res.ok and res.done == len(plan.items)
    for it in plan.items:
        assert library.abspath(it.dst_rel).exists()
        assert library.file_by_rel(it.dst_rel) is not None
    assert sorted(tree_snapshot(library.root).values()) == sorted(before.values())
    assert organize.plan_organize(library, "year_month").items == []
    actions.undo(library, res.batch_id)
    assert tree_snapshot(library.root) == before


def test_organize_include_uncertain(library, expected):
    plan = organize.plan_organize(library, "year", include_uncertain=True)
    assert set(expected["uncertain_dates"]) <= {it.src_rel for it in plan.items}


# --------------------------------------------------------------------------- tidy
def test_tidy_categories_match(library, expected):
    rep = tidy.find_tidy(library)
    names = {k: sorted(i["rel_path"] for i in v) for k, v in rep.items.items()}
    assert names["junk"] == sorted(expected["junk"])
    assert names["empty"] == sorted(expected["empty_files"])
    assert names["unreadable"] == sorted(expected["corrupt"])
    assert names["other"] == sorted(expected["non_media"])
    assert sorted(names["folders"]) == sorted(expected["empty_folders"])


def test_tidy_apply_and_undo(library):
    before = tree_snapshot(library.root)
    rep = tidy.find_tidy(library)
    chosen = {k: v for k, v in rep.items.items() if tidy.CATEGORIES[k][2]}  # defaults only
    res = actions.apply(library, "tidy", "Tidy", tidy.plan_actions(library, rep, chosen))
    assert res.ok
    assert not (library.root / "New folder").exists()
    assert not (library.root / "Old Stuff").exists()
    assert (library.root / "Documents" / "notes.md").exists()   # non-default category untouched
    actions.undo(library, res.batch_id)
    assert tree_snapshot(library.root) == before
    assert (library.root / "Old Stuff" / "Empty Album").is_dir()


# --------------------------------------------------------------------------- health
def test_health_baseline_then_detect_damage(library, expected):
    first = health.run_health(library)
    assert first.counts["new"] > 0 and first.counts["damaged"] == 0
    assert {p["rel_path"] for p in first.problems if p["status"] == "unreadable"} >= set(expected["corrupt"])
    second = health.run_health(library)
    assert second.counts["new"] == 0 and second.counts["ok"] == first.counts["new"]

    target = library.abspath(expected["rotated"][0])
    st = target.stat()
    data = bytearray(target.read_bytes())
    data[len(data) // 2] ^= 0x01                            # silent bit flip, same size and mtime
    target.write_bytes(bytes(data))
    os.utime(target, (st.st_atime, st.st_mtime))
    edited = library.abspath(expected["blurry"][0])
    with open(edited, "ab") as fh:
        fh.write(b"\0")
    third = health.run_health(library)
    status = {p["rel_path"]: p["status"] for p in third.problems}
    assert status[expected["rotated"][0]] == "damaged"
    assert status[expected["blurry"][0]] == "edited"
    assert health.run_health(library).counts["damaged"] == 1  # damage stays flagged


# --------------------------------------------------------------------------- compare / sync
def test_compare_and_sync_both_ways(library, tmp_path):
    other = tmp_path / "Backup Drive"
    rows = library.files("kind!='other' AND error IS NULL AND size>0")
    keep = rows[: len(rows) // 2]
    for r in keep:                                           # renamed + re-foldered copies still match
        dst = other / "Old Laptop" / f"copy-of-{r['name']}"
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists():
            shutil.copy2(library.abspath(r["rel_path"]), dst)
    extra = other / "Only On Backup" / "extra.jpg"
    extra.parent.mkdir(parents=True)
    shutil.copy2(library.abspath(rows[0]["rel_path"]), extra)
    with open(extra, "ab") as fh:
        fh.write(b"different")
    before_other = tree_snapshot(other)

    res = compare.compare(library, other)
    assert tree_snapshot(other) == before_other               # comparison is read-only
    assert [t.rel_path for t in res.only_there] == ["Only On Backup\\extra.jpg"]
    keep_hashes = {full_hash(library.abspath(r["rel_path"])) for r in keep}
    assert all(full_hash(library.abspath(r["rel_path"])) not in keep_hashes for r in res.only_here)
    assert res.in_both >= len(keep)

    plan = compare.plan_sync(library, res, res.only_here, res.only_there)
    out = actions.apply(library, "sync", "Sync", plan)
    assert out.ok and out.done == len(plan)
    scanner.scan(library)
    again = compare.compare(library, other)
    assert again.only_here == [] and again.only_there == []
    actions.undo(library, out.batch_id)
    assert tree_snapshot(other) == before_other


def test_compare_rejects_overlapping_folders(library):
    with pytest.raises(ValueError):
        compare.compare(library, library.root / "DCIM")


# --------------------------------------------------------------------------- safety primitives
def test_verified_copy_never_leaves_bad_file(tmp_path):
    src = tmp_path / "a.jpg"
    src.write_bytes(os.urandom(5000))
    dst = tmp_path / "out" / "a.jpg"
    with pytest.raises(OSError):
        actions.verified_copy(src, dst, expected="0" * 32)
    assert not dst.exists() and not list((tmp_path / "out").glob("*.memoria-tmp"))


def test_never_overwrites(library):
    a, b = library.files("kind='image' AND error IS NULL")[:2]
    act = actions.Action(op="move", src=str(library.abspath(a["rel_path"])), dst=str(library.abspath(b["rel_path"])),
                         size=a["size"], mtime=a["mtime"], file_id=a["id"])
    res = actions.apply(library, "organize", "Move", [act])
    assert res.done == 1
    assert library.abspath(b["rel_path"]).exists()
    moved = actions.operations(library, res.batch_id)[0]["dst"]
    assert moved != str(library.abspath(b["rel_path"])) and Path(moved).exists()


def test_reconcile_interrupted_batch(library):
    f = library.files("kind='image' AND error IS NULL")[0]
    src = library.abspath(f["rel_path"])
    dst = library.recovery / "crash" / f["name"]
    dst.parent.mkdir(parents=True)
    os.rename(src, dst)                                      # move happened, then "power cut"
    library.db.execute("INSERT INTO batches VALUES ('crash','2026-01-01','duplicates','x','applying',0,0)")
    library.db.execute("INSERT INTO operations (batch_id, seq, op, src, dst, size, status) "
                       "VALUES ('crash',0,'recycle',?,?,?,'pending')", (str(src), str(dst), f["size"]))
    assert actions.reconcile(library) == 1
    assert actions.batches(library)[0]["status"] == "partial"
    actions.undo(library, "crash")
    assert src.exists()


def test_cancel_stops_cleanly(library):
    groups = duplicates.find_duplicates(library)
    plan = duplicates.plan_removal(library, groups)
    prog = Progress(callback=lambda d, t, m: prog.cancel_event.set() if d >= 1 else None, interval=0)
    res = actions.apply(library, "duplicates", "Remove", plan, prog)
    assert res.cancelled and 0 < res.done < len(plan)
    assert actions.undo(library, res.batch_id).ok


def test_empty_recovery_is_explicit(library):
    groups = duplicates.find_duplicates(library)
    res = actions.apply(library, "duplicates", "Remove", duplicates.plan_removal(library, groups))
    files, size = actions.recovery_size(library)
    assert files == res.done and size == res.bytes
    assert actions.empty_recovery(library, [res.batch_id]) == res.done
    assert actions.recovery_size(library) == (0, 0)
    assert actions.batches(library)[0]["status"] == "emptied"


def test_large_analysis_backlog_has_bounded_submission(tmp_path, monkeypatch):
    from concurrent.futures import Future
    lib = Library(tmp_path)
    queued = set()
    peak = 0

    class TrackedFuture(Future):
        def result(self, *args, **kwargs):
            queued.discard(self)
            return super().result(*args, **kwargs)

    class ImmediatePool:
        def __init__(self, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def submit(self, *args):
            nonlocal peak
            future = TrackedFuture()
            future.set_result({"width": 10, "height": 10})
            queued.add(future)
            peak = max(peak, len(queued))
            return future

    try:
        with lib.transaction() as db:
            db.executemany("INSERT INTO files(rel_path,folder,name,ext,kind,size,mtime) "
                           "VALUES (?,'',?,'.jpg','image',30000000,1)",
                           [(f"{i}.jpg", f"{i}.jpg") for i in range(10_000)])
        monkeypatch.setattr(scanner, "ThreadPoolExecutor", ImmediatePool)
        result = scanner.analyze(lib, workers=2)
        assert result.analyzed == 10_000
        assert peak <= 6 and not queued
        assert lib.stats()["pending"] == 0
    finally:
        lib.close()


def test_dense_similarity_does_not_retain_all_pairs():
    import tracemalloc
    import numpy as np
    n = 1000
    tracemalloc.start()
    try:
        count = sum(1 for _ in similar.similar_pairs(np.zeros(n, dtype=np.int64),
                                                    np.zeros(n), 10, 3, 16))
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert count == n * (n - 1) // 2
    assert peak < 40 * 1024 * 1024
