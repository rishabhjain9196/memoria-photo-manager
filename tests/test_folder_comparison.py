import os
import shutil

import pytest
from PIL import Image

from memoria.engine import actions, assets, duplicates, scanner
from memoria.engine.db import Library


@pytest.fixture
def comparison_library(tmp_path):
    root = tmp_path / "library"
    small, large = root / "Small", root / "Large"
    small.mkdir(parents=True)
    large.mkdir()
    Image.new("RGB", (32, 24), "blue").save(small / "IMG_1.jpg")
    shutil.copy2(small / "IMG_1.jpg", large / "IMG_1.jpg")
    Image.new("RGB", (32, 24), "red").save(large / "unique.jpg")
    for folder in (small, large):
        (folder / "shared.txt").write_bytes(b"shared document")
    (small / "desktop.ini").write_bytes(b"small folder leftover")
    (large / "desktop.ini").write_bytes(b"large folder unique leftover")
    lib = Library(root)
    scanner.scan(lib)
    yield lib
    lib.close()


def _snapshot(lib):
    return {str(path.relative_to(lib.root)): path.read_bytes()
            for path in lib.root.rglob("*") if path.is_file() and ".memoria" not in path.parts}


def _match(report):
    return next(match for match in report.folders if match.kind == "inside" and
                {folder.path for folder in match.folders} == {"Small", "Large"})


@pytest.mark.parametrize("selected", [{"Small"}, {"Large"}, {"Small", "Large"}])
def test_subset_checks_only_move_shared_large_content_and_undo(comparison_library, selected):
    lib = comparison_library
    before = _snapshot(lib)
    report = duplicates.find_all(lib)
    match = _match(report)
    selection = duplicates.plan_folder_selection(lib, report, match, selected)
    moved = {lib.rel(action.src) for action in selection.actions if action.op == "recycle"}
    expected = set()
    if "Small" in selected:
        expected.update(("Small\\IMG_1.jpg", "Small\\shared.txt", "Small\\desktop.ini"))
    if "Large" in selected:
        expected.update(("Large\\IMG_1.jpg", "Large\\shared.txt"))
    assert moved == expected
    assert not any(action.op == "rmdir" and lib.rel(action.src) == "Large" for action in selection.actions)
    prepared = assets.prepare(lib, selection.actions, "duplicates")
    result = actions.apply(lib, "duplicates", "Checked comparison content", prepared.actions, companions_reviewed=True)
    assert result.ok and not result.skipped
    assert _snapshot(lib) == {path: data for path, data in before.items() if path not in expected}
    assert (lib.root / "Large").is_dir()
    assert actions.undo(lib, result.batch_id).ok
    assert _snapshot(lib) == before


def test_unique_linked_video_keeps_its_shared_photo_in_larger_folder(comparison_library):
    lib = comparison_library
    (lib.root / "Large" / "IMG_1.MOV").write_bytes(b"unique live-photo video")
    scanner.scan(lib)
    report = duplicates.find_all(lib)
    selection = duplicates.plan_folder_selection(lib, report, _match(report), {"Small", "Large"})
    assert selection.retained_linked == 1
    moved = {lib.rel(action.src) for action in selection.actions if action.op == "recycle"}
    assert "Large\\IMG_1.jpg" not in moved and "Large\\IMG_1.MOV" not in moved
    assert "Small\\IMG_1.jpg" in moved and "Large\\shared.txt" in moved
    before = _snapshot(lib)
    prepared = assets.prepare(lib, selection.actions, "duplicates")
    result = actions.apply(lib, "duplicates", "Keep unique linked parts", prepared.actions, companions_reviewed=True)
    assert result.ok and not result.skipped
    assert (lib.root / "Large" / "IMG_1.MOV").read_bytes() == b"unique live-photo video"
    assert (lib.root / "Large" / "IMG_1.jpg").exists()
    assert actions.undo(lib, result.batch_id).ok
    assert _snapshot(lib) == before


def test_subset_plan_does_not_absorb_new_files_and_skips_changed_common_file(comparison_library):
    lib = comparison_library
    report = duplicates.find_all(lib)
    (lib.root / "Large" / "new.jpg").write_bytes(b"new unique data")
    path = lib.root / "Large" / "IMG_1.jpg"
    stat = path.stat()
    data = bytearray(path.read_bytes())
    data[-1] ^= 1
    path.write_bytes(data)
    os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
    before = _snapshot(lib)
    selection = duplicates.plan_folder_selection(lib, report, _match(report), {"Large"})
    result = actions.apply(lib, "duplicates", "Shared only", selection.actions)
    assert result.skipped == 1 and not result.failed
    assert (lib.root / "Large" / "new.jpg").read_bytes() == b"new unique data"
    assert path.read_bytes() == bytes(data)
    assert actions.undo(lib, result.batch_id).ok
    assert _snapshot(lib) == before


def test_new_linked_part_is_not_included_in_old_folder_review(comparison_library):
    lib = comparison_library
    report = duplicates.find_all(lib)
    (lib.root / "Small" / "IMG_1.AAE").write_bytes(b"new Apple edit instructions")
    scanner.scan(lib)
    selection = duplicates.plan_folder_selection(lib, report, _match(report), {"Small"})
    moved = {lib.rel(action.src) for action in selection.actions if action.op == "recycle"}
    assert selection.retained_linked == 1
    assert "Small\\IMG_1.jpg" not in moved and "Small\\IMG_1.AAE" not in moved
    assert not any(action.op == "rmdir" and lib.rel(action.src) == "Small" for action in selection.actions)
