"""Multi-library comparison: cached fingerprints, Venn regions, grouped views and copy-only sync."""
import os
import sqlite3
from pathlib import Path

import pytest

from memoria.engine import actions, config, libsync, scanner
from memoria.engine.db import SCHEMA_VERSION, Library
from memoria.engine.hashing import full_hash


def write(root: Path, files: dict) -> Path:
    for name, data in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return root


@pytest.fixture
def libraries(tmp_path):
    opened = []

    def make(main: dict, *others: dict):
        lib = Library(write(tmp_path / "laptop", main))
        opened.append(lib)
        scanner.scan(lib)
        return lib, [write(tmp_path / name, files) for name, files in zip(("phone", "drive"), others)]

    yield make
    for lib in opened:
        lib.close()


def region(cmp, *sides):
    return cmp.regions().get(sum(1 << side for side in sides), (0, 0))[0]


def test_three_way_regions_and_masks_match_content_not_names(libraries):
    lib, (phone, drive) = libraries(
        {r"2023\a.jpg": b"aaa", r"2023\b.jpg": b"bbb", "only-laptop.jpg": b"laptop"},
        {r"DCIM\renamed-a.jpg": b"aaa", r"DCIM\c.jpg": b"ccc", r"DCIM\new.jpg": b"phone"},
        {r"Backup\a.jpg": b"aaa", r"Backup\b.jpg": b"bbb", r"Backup\c.jpg": b"ccc"})
    cmp = libsync.compare(lib, [phone, drive])
    assert region(cmp, 0, 1, 2) == 1          # a
    assert region(cmp, 0, 2) == 1             # b
    assert region(cmp, 1, 2) == 1             # c
    assert region(cmp, 0) == region(cmp, 1) == 1 and region(cmp, 2) == 0
    missing = cmp.matching(1, cmp.predicate("missing", 0))
    assert {entry.name for entry in missing} == {"c.jpg", "new.jpg"}
    every = cmp.matching(2, cmp.predicate("every"))
    assert [entry.name for entry in every] == ["a.jpg"]


def test_fingerprints_are_cached_in_the_master_and_reused(libraries):
    lib, (phone,) = libraries({"a.jpg": b"same"}, {"x.jpg": b"same", "y.jpg": b"different"})
    first = libsync.compare(lib, [phone])
    assert first.info[1].hashed == 1 and first.info[1].reused == 0
    assert list(libsync.index_location(lib.root).glob("*.sqlite"))
    assert not (phone / config.APP_DIR_NAME).exists()  # the other drive is never written to
    again = libsync.compare(lib, [phone])
    assert again.info[1].hashed == 0 and again.info[1].reused == 1
    other = libsync.compare(lib, [phone], master=1)
    assert other.info[1].location.startswith(str(phone))
    assert list(libsync.index_location(phone).glob("*.sqlite"))


def test_compatible_catalogue_is_reused_and_newer_one_is_not(libraries, tmp_path):
    lib, (phone,) = libraries({"a.jpg": b"same"}, {"x.jpg": b"same"})
    other = Library(phone)
    scanner.index(other)
    row = other.file_by_rel("x.jpg")
    other.set_hashes([(row["id"], None, full_hash(phone / "x.jpg"))])
    other.close()
    cmp = libsync.compare(lib, [phone])
    assert cmp.info[1].source == "catalogue" and cmp.info[1].reused == 1 and cmp.info[1].hashed == 0
    db = sqlite3.connect(str(config.app_dir(phone) / config.DB_NAME))
    db.execute(f"PRAGMA user_version={SCHEMA_VERSION + 1}")
    db.close()
    for index in libsync.index_location(lib.root).glob("*.sqlite"):
        index.unlink()
    newer = libsync.compare(lib, [phone])
    assert newer.info[1].source == "index" and "newer" in newer.info[1].detail and newer.info[1].hashed == 1
    assert region(newer, 0, 1) == 1


def test_changed_file_is_fingerprinted_again(libraries):
    lib, (phone,) = libraries({"a.jpg": b"same"}, {"x.jpg": b"same"})
    libsync.compare(lib, [phone])
    (phone / "x.jpg").write_bytes(b"sAme")
    stamp = (phone / "x.jpg").stat()
    os.utime(phone / "x.jpg", (stamp.st_atime, stamp.st_mtime + 5))
    cmp = libsync.compare(lib, [phone])
    assert cmp.info[1].hashed == 1 and region(cmp, 0, 1) == 0


def test_grouped_tree_collapses_folders_whose_files_all_match(libraries):
    lib, (phone,) = libraries(
        {"keep.jpg": b"k"},
        {r"Trip\Day1\a.jpg": b"1", r"Trip\Day2\b.jpg": b"2", r"Mixed\c.jpg": b"3", r"Mixed\d.jpg": b"k"})
    cmp = libsync.compare(lib, [phone])
    tree = cmp.tree(1, cmp.predicate("only", 1))
    trip, mixed = tree.folders["trip"], tree.folders["mixed"]
    assert trip.complete and trip.matching == 2 and trip.folders["day1"].complete
    assert not mixed.complete and mixed.matching == 1 and [entry.name for entry in mixed.files] == ["c.jpg"]
    assert not tree.complete and tree.matching == 3 and tree.total == 4


def test_delta_copy_merges_into_the_matching_folder_and_creates_others(libraries):
    lib, (phone,) = libraries(
        {r"Phone backup\2024\a.jpg": b"a", r"Phone backup\2024\b.jpg": b"b"},
        {r"DCIM\Camera\a.jpg": b"a", r"DCIM\Camera\b.jpg": b"b", r"DCIM\Camera\new.jpg": b"new",
         r"DCIM\Camera\copy-of-new.jpg": b"new", r"WhatsApp\w.jpg": b"w"})
    cmp = libsync.compare(lib, [phone])
    rows = {row.folder: row for row in cmp.mapping_rows(1, 0)}
    assert rows[r"DCIM\Camera"].match == r"Phone backup\2024" and rows[r"DCIM\Camera"].shared == 2
    items = cmp.plan_copy(1, 0)
    placed = {item.entry.name: (item.folder, item.merged) for item in items}
    assert len(items) == 2  # one copy per content
    assert placed["copy-of-new.jpg"] == (r"Phone backup\2024", True) or placed["new.jpg"] == (r"Phone backup\2024", True)
    assert placed["w.jpg"] == ("WhatsApp", False)
    mirrored = {item.entry.name: item.folder for item in cmp.plan_copy(1, 0, "mirror")}
    assert mirrored["w.jpg"] == "WhatsApp" and set(mirrored.values()) >= {r"DCIM\Camera"}
    result = actions.apply(lib, "sync", "Copy delta", [item.action for item in items])
    assert result.done == 2 and not result.failed
    assert (lib.root / "WhatsApp" / "w.jpg").read_bytes() == b"w"
    assert (phone / "WhatsApp" / "w.jpg").exists()  # copy-only: the source is untouched
    assert actions.undo(lib, result.batch_id).done == 2
    assert not (lib.root / "WhatsApp" / "w.jpg").exists()


def test_two_way_sync_between_two_other_libraries_never_overwrites(libraries):
    lib, (phone, drive) = libraries({"z.jpg": b"z"}, {"p.jpg": b"p", "same.jpg": b"one"}, {"d.jpg": b"d", "same.jpg": b"two"})
    cmp = libsync.compare(lib, [phone, drive])
    items = cmp.plan_copy(1, 2) + cmp.plan_copy(2, 1)
    result = actions.apply(lib, "sync", "Two-way", [item.action for item in items])
    assert result.done == 4 and not result.failed
    assert (phone / "same.jpg").read_bytes() == b"one" and (drive / "same.jpg").read_bytes() == b"two"
    assert (phone / "same (2).jpg").read_bytes() == b"two" and (drive / "same (2).jpg").read_bytes() == b"one"
    assert (phone / "d.jpg").exists() and (drive / "p.jpg").exists()


def test_removing_duplicates_from_another_library_uses_its_recovery_and_undoes(libraries):
    lib, (drive,) = libraries({"a.jpg": b"a"}, {r"Old\a copy.jpg": b"a", r"Old\unique.jpg": b"u"})
    cmp = libsync.compare(lib, [drive])
    plan = cmp.plan_removal(1)
    assert [entry.name for entry in plan.items] == ["a copy.jpg"]
    result = actions.apply(lib, "sync", "Remove copies", plan.actions)
    assert result.done == 1
    moved = list((config.recovery_dir(drive)).rglob("a copy.jpg"))
    assert len(moved) == 1 and not (drive / "Old" / "a copy.jpg").exists()
    assert (drive / "Old" / "unique.jpg").exists() and (lib.root / "a.jpg").exists()
    assert actions.undo(lib, result.batch_id).done == 1
    assert (drive / "Old" / "a copy.jpg").read_bytes() == b"a"
    assert not any(config.recovery_dir(drive).rglob("*.jpg"))


def test_removal_keeps_assets_whose_linked_parts_are_not_all_duplicates(libraries):
    lib, (drive,) = libraries({"IMG_1.HEIC": b"photo", "IMG_2.HEIC": b"two", "IMG_2.MOV": b"motion"},
                              {"IMG_1.HEIC": b"photo", "IMG_1.MOV": b"other motion",
                               "IMG_2.HEIC": b"two", "IMG_2.MOV": b"motion"})
    cmp = libsync.compare(lib, [drive])
    plan = cmp.plan_removal(1)
    assert sorted(entry.name for entry in plan.items) == ["IMG_2.HEIC", "IMG_2.MOV"]
    assert plan.kept_linked == 1


def test_removal_guard_skips_when_the_kept_copy_changed(libraries):
    lib, (drive,) = libraries({"a.jpg": b"a"}, {"a.jpg": b"a"})
    cmp = libsync.compare(lib, [drive])
    plan = cmp.plan_removal(1)
    (lib.root / "a.jpg").write_bytes(b"changed")
    result = actions.apply(lib, "sync", "Remove copies", plan.actions)
    assert result.done == 0 and result.skipped == 1 and (drive / "a.jpg").exists()


def test_overlapping_or_missing_libraries_are_rejected(libraries, tmp_path):
    lib, (phone,) = libraries({"a.jpg": b"a"}, {"a.jpg": b"a"})
    with pytest.raises(ValueError):
        libsync.compare(lib, [lib.root / "sub"] if (lib.root / "sub").mkdir() is None else [])
    with pytest.raises(ValueError):
        libsync.compare(lib, [phone, phone])
    with pytest.raises(Exception):
        libsync.compare(lib, [tmp_path / "unplugged"])


def test_remembered_exclusions_are_marked_per_pair(libraries):
    lib, (phone, drive) = libraries({"a.jpg": b"a"}, {"wedding.mp4": b"huge video", "p.jpg": b"pp"}, {"d.jpg": b"d"})
    cmp = libsync.compare(lib, [phone, drive])
    video = next(entry for entry in cmp.entries[1] if entry.name == "wedding.mp4")
    libsync.update_exclusions(lib, phone, lib.root, add=[video])
    excluded = set(libsync.load_exclusions(lib, phone, lib.root))
    items = {item.entry.name: item.excluded for item in cmp.plan_copy(1, 0, excluded=excluded)}
    assert items == {"wedding.mp4": True, "p.jpg": False}
    assert not libsync.load_exclusions(lib, phone, drive)  # another destination is unaffected
    libsync.update_exclusions(lib, phone, lib.root, remove=[video])
    assert not libsync.load_exclusions(lib, phone, lib.root)


def test_profiles_round_trip(libraries):
    lib, _ = libraries({"a.jpg": b"a"})
    libsync.save_profile(lib, {"name": "Phone -> Laptop", "others": ["E:\\Phone"], "mode": "one-way"})
    libsync.save_profile(lib, {"name": "phone -> laptop", "others": ["F:\\Phone"], "mode": "one-way"})
    profiles = libsync.load_profiles(lib)
    assert len(profiles) == 1 and profiles[0]["others"] == ["F:\\Phone"]
    assert libsync.delete_profile(lib, "PHONE -> LAPTOP") == []
