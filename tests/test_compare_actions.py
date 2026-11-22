import os
from datetime import datetime

from PIL import Image

from memoria.engine import actions, libsync, organize, scanner
from memoria.engine.db import Library


def _write(root, files):
    for rel, data in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_bytes(data)


def _tree(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file() and ".memoria" not in p.parts}


def test_drive_gets_the_laptops_folder_layout_and_undo_restores_it(tmp_path):
    laptop, drive = tmp_path / "laptop", tmp_path / "drive"
    _write(laptop, {r"2023\Goa\x.jpg": b"x" * 10, r"2023\Goa\y.jpg": b"y" * 10, r"2023\Goa\z.jpg": b"z" * 10})
    _write(drive, {r"random\x.jpg": b"x" * 10, r"random2\x.jpg": b"x" * 10, r"dump\y_copy.jpg": b"y" * 10,
                   r"dump\only.jpg": b"o" * 10, r"2023\Goa\z.jpg": b"z" * 10})
    before = _tree(drive)
    lib = Library(laptop)
    try:
        scanner.scan(lib)
        cmp = libsync.compare(lib, [drive], media_only=False)
        moves, extra = cmp.plan_match_layout(1, 0, cmp.entries[1])
        planned = {entry.rel: os.path.relpath(action.dst, drive) for entry, action in moves}
        moved_x = next(rel for rel in planned if rel.endswith("x.jpg"))    # one of the two identical copies
        assert planned == {r"dump\y_copy.jpg": r"2023\Goa\y.jpg", moved_x: r"2023\Goa\x.jpg"}
        assert extra == 1                                     # the other copy of x is left in place
        left_x = r"random\x.jpg" if moved_x == r"random2\x.jpg" else r"random2\x.jpg"
        result = actions.apply(lib, "sync", "Match layout", [action for _, action in moves])
        after = _tree(drive)
        assert result.done == 2 and after[r"2023\Goa\y.jpg"] == b"y" * 10 and r"dump\only.jpg" in after
        assert after[left_x] == b"x" * 10 and moved_x not in after
        actions.undo(lib, result.batch_id)
        assert _tree(drive) == before
    finally:
        lib.close()


def test_sidecars_only_on_the_drive_can_be_cleared_to_its_recovery(tmp_path):
    laptop, drive = tmp_path / "laptop", tmp_path / "drive"
    _write(laptop, {r"Pics\IMG_1.JPG": b"photo"})
    _write(drive, {r"DCIM\IMG_1.JPG": b"photo", r"DCIM\IMG_1.AAE": b"<plist>edit</plist>", r"DCIM\IMG_2.JPG": b"two"})
    lib = Library(laptop)
    try:
        scanner.scan(lib)
        cmp = libsync.compare(lib, [drive])
        only_drive = cmp.matching(1, cmp.predicate("only", 1))
        sidecars = [e for e in only_drive if libsync.Comparison.kind(e) == "sidecar"]
        assert [e.name for e in sidecars] == ["IMG_1.AAE"]
        plan = cmp.plan_recycle(1, sidecars)
        assert [(entry.name, unique) for entry, _, unique in plan] == [("IMG_1.AAE", True)]
        shared = cmp.plan_recycle(1, cmp.matching(1, cmp.predicate("every")))
        assert [(entry.name, unique, bool(action.guards)) for entry, action, unique in shared] == [("IMG_1.JPG", False, True)]
        result = actions.apply(lib, "sync", "Clear sidecars", [action for _, action, _ in plan])
        assert result.done == 1 and not (drive / "DCIM" / "IMG_1.AAE").exists()
        assert (drive / "DCIM" / "IMG_2.JPG").exists() and list((drive / ".memoria" / "recovery").rglob("IMG_1.AAE"))
    finally:
        lib.close()


def _photo(path, when: datetime):
    img = Image.new("RGB", (40, 30))
    exif = img.getexif()
    exif.get_ifd(0x8769)[0x9003] = when.strftime("%Y:%m:%d %H:%M:%S")
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, exif=exif)


def test_events_layout_groups_photos_taken_together(tmp_path):
    for i in range(3):
        _photo(tmp_path / "random" / f"xmas{i}.jpg", datetime(2019, 12, 25, 10 + i))
        _photo(tmp_path / "dump" / f"trip{i}.jpg", datetime(2021, 3, 14, 9 + i))
    _photo(tmp_path / "dump" / "lonely.jpg", datetime(2022, 7, 1, 12))
    lib = Library(tmp_path)
    try:
        scanner.index(lib)
        plan = organize.plan_organize(lib, "events")
        folders = {item.row["name"]: os.path.dirname(item.dst_rel) for item in plan.items}
        assert {folders[f"xmas{i}.jpg"] for i in range(3)} == {os.path.join("2019", "2019-12-25")}
        assert {folders[f"trip{i}.jpg"] for i in range(3)} == {os.path.join("2021", "2021-03-14")}
        assert folders["lonely.jpg"] == os.path.join("2022", "2022-07")   # too few photos for an event folder
    finally:
        lib.close()
