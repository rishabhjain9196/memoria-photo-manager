"""Duplicate folders: identical and contained folders, reported at the highest level, removed safely."""
import os
import shutil
from pathlib import Path

import pytest

from memoria.engine import actions, duplicates, scanner
from memoria.engine.db import Library

S = os.sep


def _write(root: Path, rel: str, data: bytes) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)


def _blob(n: int) -> bytes:
    return os.urandom(4096 + n * 37)


@pytest.fixture
def tree(tmp_path):
    root = tmp_path / "lib"
    b = {k: _blob(i) for i, k in enumerate("abcvxyzunpqkd")}
    files = {
        # A nested album and a full copy of it on an "old laptop" (with a Thumbs.db in the copy)
        "Albums/Family/Birthday/a.jpg": b["a"], "Albums/Family/Birthday/b.jpg": b["b"],
        "Albums/Family/Picnic/c.jpg": b["c"], "Albums/Family/Picnic/v.mp4": b["v"],
        "Old Laptop/Pictures/Family/Birthday/a.jpg": b["a"], "Old Laptop/Pictures/Family/Birthday/b.jpg": b["b"],
        "Old Laptop/Pictures/Family/Picnic/c.jpg": b["c"], "Old Laptop/Pictures/Family/Picnic/v.mp4": b["v"],
        "Old Laptop/Pictures/Family/Picnic/Thumbs.db": b"\0" * 1024,
        # Camera folder and a USB stick holding a few of its photos
        "Camera/x.jpg": b["x"], "Camera/y.jpg": b["y"], "Camera/z.jpg": b["z"], "Camera/u.jpg": b["u"],
        "USB/picks/x.jpg": b["x"], "USB/picks/y.jpg": b["y"],
        # Also holds the USB photos and is smaller, but looks like a download folder: Camera is preferred
        "Downloads/x.jpg": b["x"], "Downloads/y.jpg": b["y"], "Downloads/d.jpg": b["d"],
        # A folder with one copy and one unique photo: not a duplicate folder
        "Mixed/x.jpg": b["x"], "Mixed/n.jpg": b["n"],
        # Same files under different names
        "Trip/p.jpg": b["p"], "Trip/q.jpg": b["q"], "Trip copy/IMG_1.jpg": b["p"], "Trip copy/IMG_2.jpg": b["q"],
        # Two copies of k in one folder, one in another
        "Dupe/k.jpg": b["k"], "Dupe/k2.jpg": b["k"], "Single/k.jpg": b["k"],
    }
    for rel, data in files.items():
        _write(root, rel.replace("/", S), data)
    (root / "Albums" / "Family" / "Empty").mkdir()
    lib = Library(root)
    scanner.scan(lib)
    yield lib
    lib.close()


def _snapshot(root: Path) -> dict:
    out = {}
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x != ".memoria"]
        rel = os.path.relpath(d, root)
        out[rel + S] = None
        for f in files:
            out[os.path.join(rel, f)] = (Path(d, f).read_bytes())
    return out


def _matches(rep):
    return {(m.kind, tuple(f.path for f in m.folders)) for m in rep.folders}


def test_folders_are_reported_at_the_highest_level(tree):
    rep = duplicates.find_all(tree)
    got = _matches(rep)
    assert got == {
        ("same", ("Albums", "Old Laptop")),                  # not Albums\Family, …\Birthday or …\Pictures
        ("inside", ("USB", "Camera")),                      # USB holds only "picks", so USB itself is shown
        ("same", ("Trip", "Trip copy")),                     # names differ; contents match
        ("inside", ("Single", "Dupe")),
    }
    m = next(m for m in rep.folders if m.folders[0].path == "Albums")
    assert m.keeper == "Albums" and [f.path for f in m.redundant()] == ["Old Laptop"]
    alb, old = m.folders
    assert (alb.files, alb.photos, alb.videos, alb.others, alb.subfolders) == (4, 3, 1, 0, 3)
    assert (old.files, old.photos, old.videos, old.others) == (5, 3, 1, 1)   # Thumbs.db counted, not compared
    assert alb.photo_bytes == sum((tree.root / "Albums" / "Family" / s).stat().st_size
                                  for s in ("Birthday\\a.jpg", "Birthday\\b.jpg", "Picnic\\c.jpg"))
    assert alb.video_bytes == (tree.root / "Albums" / "Family" / "Picnic" / "v.mp4").stat().st_size
    assert old.total_bytes == alb.total_bytes + 1024 and m.wasted() == old.total_bytes


def test_file_groups_exclude_copies_handled_by_folders(tree):
    rep = duplicates.find_all(tree)
    assert len(rep.groups) == 9                                # a b c v x y p q k
    loose = rep.loose_groups()
    names = sorted(sorted(f["rel_path"] for f in g.files) for g in loose)
    assert names == [[f"Camera{S}x.jpg", f"Downloads{S}x.jpg", f"Mixed{S}x.jpg"],
                     [f"Camera{S}y.jpg", f"Downloads{S}y.jpg"], [f"Dupe{S}k.jpg", f"Dupe{S}k2.jpg"]]
    # Choosing to keep the old laptop copy moves the album copies out of the way instead.
    m = next(m for m in rep.folders if m.kind == "same" and m.folders[0].path == "Albums")
    assert [f.path for f in m.redundant({m.id: "Old Laptop"})] == ["Albums"]


def test_folder_cleanup_and_undo_restore_everything(tree):
    before = _snapshot(tree.root)
    rep = duplicates.find_all(tree)
    plan = duplicates.plan_cleanup(tree, rep, folders=[m.id for m in rep.folders],
                                   files=[g.hash for g in rep.loose_groups()])
    assert all(a.guards for a in plan if a.op == "recycle" and not a.src.endswith("Thumbs.db"))
    res = actions.apply(tree, "duplicates", "Remove duplicate folders", plan)
    assert res.failed == 0 and res.skipped == 0
    for gone in ("Old Laptop", "USB", "Trip copy", "Single"):
        assert not (tree.root / gone).exists()
    for kept in ("Albums/Family/Picnic/v.mp4", "Camera/x.jpg", "Trip/p.jpg", "Dupe/k.jpg"):
        assert (tree.root / kept.replace("/", S)).exists()
    assert (tree.root / "Albums" / "Family" / "Empty").is_dir()      # only duplicate folders are removed
    assert not (tree.root / "Mixed" / "x.jpg").exists()               # loose copy of Camera\x.jpg
    assert (tree.root / "Downloads" / "d.jpg").exists()
    scanner.scan(tree)
    again = duplicates.find_all(tree)
    assert again.folders == [] and again.groups == []
    assert actions.undo(tree, res.batch_id).ok
    assert _snapshot(tree.root) == before


def test_changed_keeper_or_new_file_leaves_the_folder(tree):
    rep = duplicates.find_all(tree)
    m = next(m for m in rep.folders if m.kind == "same" and m.folders[0].path == "Albums")
    plan = duplicates.plan_cleanup(tree, rep, folders=[m.id])
    kept = tree.root / "Albums" / "Family" / "Birthday" / "a.jpg"
    st = kept.stat()
    with open(kept, "r+b") as fh:                                       # the copy being kept is edited
        fh.write(b"edited")
    os.utime(kept, ns=(st.st_atime_ns, st.st_mtime_ns))
    _write(tree.root, f"Old Laptop{S}Pictures{S}notes.txt", b"added after the review")
    res = actions.apply(tree, "duplicates", "Remove duplicate folders", plan)
    old = tree.root / "Old Laptop" / "Pictures"
    assert (old / "Family" / "Birthday" / "a.jpg").exists()              # its only identical copy changed
    assert (old / "notes.txt").exists() and old.is_dir()                  # folder not empty → not removed
    assert res.skipped >= 2 and res.failed == 0


def test_folder_without_a_remaining_copy_is_not_planned(tree):
    rep = duplicates.find_all(tree)
    usb = next(m for m in rep.folders if m.kind == "inside" and m.folders[0].path == "USB")
    (tree.root / "Camera" / "x.jpg").unlink()                           # container copy gone; Mixed\x.jpg remains
    (tree.root / "Mixed" / "x.jpg").unlink()
    (tree.root / "Downloads" / "x.jpg").unlink()
    plan = duplicates.plan_cleanup(tree, rep, folders=[usb.id])
    assert plan and all("USB" in a.src for a in plan)                  # the catalogue still lists the copies…
    res = actions.apply(tree, "duplicates", "Remove duplicate folders", plan)
    assert (tree.root / "USB" / "picks" / "x.jpg").exists() and res.skipped >= 1   # …but pre-flight finds them gone
    tree.db.execute("DELETE FROM files WHERE rel_path IN (?, ?, ?)",
                    (f"Camera{S}x.jpg", f"Mixed{S}x.jpg", f"Downloads{S}x.jpg"))
    assert duplicates.plan_cleanup(tree, rep, folders=[usb.id]) == []  # no remaining copy → folder not planned


def test_sample_library_folders_match_ground_truth(library, expected):
    rep = duplicates.find_all(library)
    got = _matches(rep)
    for want in expected["duplicate_folders"]:
        assert (want["kind"], tuple(want["folders"])) in got
    for kind, folders in got:                                          # every reported folder is really covered
        rows = {f: [r for r in library.files() if r["rel_path"].lower().startswith(f.lower() + S)] for f in folders}
        def content(f):
            from collections import Counter
            return Counter(library.abspath(r["rel_path"]).read_bytes() for r in rows[f]
                           if r["size"] and r["name"].lower() not in ("thumbs.db", "desktop.ini", ".ds_store"))
        if kind == "same":
            assert all(content(f) == content(folders[0]) for f in folders)
        else:
            small, big = content(folders[0]), content(folders[1])
            assert all(big[c] >= n for c, n in small.items()) and small != big
    assert not any("Family 2020" in f for _, fs in got for f in fs)     # children of a copied tree are not repeated
    file_level = sorted(sorted(f["rel_path"] for f in g.files) for g in rep.groups)
    assert file_level == expected["duplicate_groups"]
