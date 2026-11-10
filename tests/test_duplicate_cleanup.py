"""Bulk exact cleanup preserves content, review choices, and complete linked assets."""
import json
import os
import time
from pathlib import Path

import pytest

from memoria.engine import actions, albums, assets, duplicates, organisation, roots, scanner
from memoria.engine import duplicate_cleanup as cleanup
from memoria.engine.db import Library, LibraryUnavailable
from memoria.engine.hashing import full_hash
from memoria.engine.progress import Cancelled, Progress


@pytest.fixture
def make_library(tmp_path):
    opened = []

    def make(files):
        root = tmp_path / f"library-{len(opened)}"
        root.mkdir()
        for name, value in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(value)
        lib = Library(root)
        opened.append(lib)
        scanner.scan(lib)
        return lib

    yield make
    for lib in opened:
        lib.close()


def snapshot(lib):
    return {str(path.relative_to(lib.root)): path.read_bytes()
            for path in lib.root.rglob("*") if path.is_file() and ".memoria" not in path.parts}


def execute(lib, plan):
    return actions.apply(lib, "duplicates", "Bulk exact cleanup", plan.actions, companions_reviewed=True)


def find_group(report, path):
    return next(group for group in report.groups if any(row["rel_path"] == path for row in group.files))


def assert_safe(plan):
    gone = {action.file_id for action in plan.actions}
    paths = {os.path.normcase(action.src) for action in plan.actions}
    assert all(action.op == "recycle" and action.hash and action.mtime is not None
               and action.companions_locked and action.guards and action.merge_into not in gone
               for action in plan.actions)
    assert all(os.path.normcase(path) not in paths for action in plan.actions for path, _ in action.guards)


def metadata_group(digest, folders, size=1):
    return duplicates.DuplicateGroup(
        digest, size, [{"folder": path, "id": index} for index, path in enumerate(folders)], 0)


def test_folder_collections_include_same_folder_and_partial_overlaps():
    first = metadata_group("a", ["Camera", "Backup"], 30)
    second = metadata_group("b", ["BACKUP", "camera"], 20)
    same = metadata_group("c", ["Trip", "Trip"], 40)
    overlap = metadata_group("d", ["Camera", "Third"], 10)
    result = cleanup.group_by_folders([first, second, same, overlap])
    assert [collection.wasted for collection in result] == [50, 40, 10]
    assert result[0].groups == [first, second]
    assert tuple(path.casefold() for path in result[0].folders) == ("backup", "camera")
    assert result[1].folders == ("Trip",)
    assert len(result[2].folders) == 2  # A partial overlap is not an all-folder component.
    reverse = cleanup.group_by_folders([second, first])[0]
    assert reverse.id == result[0].id and reverse.folders == result[0].folders
    assert cleanup.group_by_folders([]) == []
    tied = cleanup.group_by_folders([same, metadata_group("e", ["Z", "Y"], 40)])
    assert tied[0].groups == [same]


def test_100k_metadata_rows_create_one_collection_not_folder_pairs():
    group = metadata_group("content", [f"Folder {index:06}" for index in range(100_000)])
    started = time.monotonic()
    result = cleanup.group_by_folders([group])
    assert len(result) == 1 and len(result[0].folders) == 100_000
    assert result[0].folders == tuple(sorted(row["folder"] for row in group.files))
    assert time.monotonic() - started < 15


def test_all_groups_keep_copies_and_undo_restores_bytes_catalogue_and_organisation(make_library):
    lib = make_library({
        "one.jpg": b"same photo", "two.jpg": b"same photo", "three.jpg": b"same photo",
        r"Left\photo.jpg": b"other photo", r"Right\photo.jpg": b"other photo",
        r"Left\note.txt": b"same note", r"Right\note.txt": b"same note",
        r"Left\empty.jpg": b"", r"Right\Thumbs.db": b"system data",
        r"Right\unique.jpg": b"unique photo",
    })
    report = duplicates.find_all(lib)
    before, catalogued = snapshot(lib), [dict(row) for row in lib.files()]
    source = lib.file_by_rel("two.jpg")["id"]
    albums.create(lib, "Personal", [source])
    organisation.edit(lib, [source], rating=5, favorite=True, add_tags=["Trip"])
    states = {row["id"]: organisation.state(lib, row["id"]) for row in catalogued}
    plan = cleanup.plan_cleanup(lib, report)
    assert plan.groups == len(report.groups) == 2
    assert len(plan.actions) == 3 and not plan.linked_skipped
    assert_safe(plan)
    result = execute(lib, plan)
    assert result.done == 3 and not result.skipped and not result.failed
    for group in report.groups:
        assert any(lib.abspath(row["rel_path"]).exists() for row in group.files)
    merged = next(action.merge_into for action in plan.actions if action.file_id == source)
    assert organisation.state(lib, merged)["tags"] == ["Trip"]
    assert (lib.root / "Left" / "note.txt").exists()
    assert (lib.root / "Right" / "Thumbs.db").exists()
    assert (lib.root / "Left" / "empty.jpg").exists()
    assert (lib.root / "Right").is_dir()
    undone = actions.undo(lib, result.batch_id)
    assert undone.done == 3 and not undone.failed
    assert snapshot(lib) == before
    assert [dict(row) for row in lib.files()] == catalogued
    assert {fid: organisation.state(lib, fid) for fid in states} == states


def test_scope_and_empty_scope_never_add_other_duplicates_or_new_ordinary_files(make_library):
    lib = make_library({"a.jpg": b"first", "b.jpg": b"first", "c.jpg": b"second", "d.jpg": b"second"})
    report = duplicates.find_all(lib)
    first = find_group(report, "a.jpg")
    (lib.root / "new.jpg").write_bytes(b"first")
    scanner.scan(lib)
    plan = cleanup.plan_cleanup(lib, report, hashes={first.hash})
    assert plan.groups == 1 and len(plan.actions) == 1
    assert {action.file_id for action in plan.actions} <= {row["id"] for row in first.files}
    assert cleanup.plan_cleanup(lib, report, hashes=set()).actions == []
    result = execute(lib, plan)
    assert result.done == 1 and (lib.root / "new.jpg").exists()
    assert (lib.root / "c.jpg").exists() and (lib.root / "d.jpg").exists()


@pytest.mark.parametrize("all_checked", [False, True])
def test_file_overrides_protect_unchecked_and_still_keep_one_when_all_checked(make_library, all_checked):
    lib = make_library({"a.jpg": b"photo", "b.jpg": b"photo", "c.jpg": b"photo"})
    report = duplicates.find_all(lib)
    group = report.groups[0]
    chosen = {row["id"] for row in group.files} if all_checked else {group.keeper_id}
    plan = cleanup.plan_cleanup(lib, report, file_choices={group.hash: chosen})
    removed = {action.file_id for action in plan.actions}
    assert removed <= chosen and len(removed) == (2 if all_checked else 1)
    assert_safe(plan)
    result = execute(lib, plan)
    assert result.done == len(removed)
    assert any(lib.abspath(row["rel_path"]).exists() for row in group.files)


def test_saved_full_and_loose_subset_choices_remain_protected(make_library):
    lib = make_library({
        r"Left\photo.jpg": b"photo", r"Right\photo.jpg": b"photo", "outside.jpg": b"photo",
        "a.jpg": b"second", "b.jpg": b"second",
    })
    report = duplicates.find_all(lib)
    full = find_group(report, "a.jpg")
    loose = next(group for group in report.loose_groups() if any(
        row["rel_path"] == "outside.jpg" for row in group.files))
    assert len(loose.files) == 2
    signatures = {duplicates.file_review_key(full), duplicates.file_review_key(loose)}
    for signature in signatures:
        duplicates.remember_keep(lib, signature, True)
    all_checked = {group.hash: {row["id"] for row in group.files} for group in report.groups}
    plan = cleanup.plan_cleanup(lib, report, file_choices=all_checked)
    protected = {row["id"] for group in (full, loose) for row in group.files}
    assert not protected.intersection(action.file_id for action in plan.actions)
    assert len(plan.actions) == 1 and plan.protected_groups == 2
    assert duplicates.kept_choices(lib) == signatures
    assert execute(lib, plan).done == 1
    assert all(lib.file(fid) is not None for fid in protected)


def test_saved_folder_keep_wins_conflicting_checked_files_and_folders(make_library):
    lib = make_library({r"Left\a.jpg": b"photo", r"Right\a.jpg": b"photo", "outside.jpg": b"photo"})
    report = duplicates.find_all(lib)
    match = next(match for match in report.folders if match.kind == "same")
    signature = report.folder_review_key(match)
    duplicates.remember_keep(lib, signature, True)
    plan = cleanup.plan_cleanup(
        lib, report, file_choices={report.groups[0].hash: {row["id"] for row in report.groups[0].files}},
        folder_choices={match.id: {folder.path for folder in match.folders}})
    assert [Path(action.src).name for action in plan.actions] == ["outside.jpg"]
    assert plan.protected_groups == 1 and duplicates.kept_choices(lib) == {signature}
    assert execute(lib, plan).done == 1


def test_collection_checked_scope_protects_hidden_whole_folder_copies(make_library):
    lib = make_library({r"Left\a.jpg": b"photo", r"Right\a.jpg": b"photo", "outside.jpg": b"photo"})
    report = duplicates.find_all(lib)
    group = report.loose_groups()[0]
    assert len(group.files) == 2 and len(report.groups[0].files) == 3
    chosen = {row["id"] for row in group.files} - {group.keeper_id}
    plan = cleanup.plan_cleanup(lib, report, hashes={group.hash}, file_choices={group.hash: chosen})
    assert {action.file_id for action in plan.actions} == chosen
    assert plan.protected_groups == 1


@pytest.mark.parametrize("both", [False, True])
def test_inside_folder_selection_protects_unique_larger_contents(make_library, both):
    lib = make_library({
        r"Holder\shared.jpg": b"shared", r"Holder\unique.jpg": b"unique",
        r"Subset\shared.jpg": b"shared", "outside.jpg": b"unique",
    })
    report = duplicates.find_all(lib)
    match = next(match for match in report.folders if match.kind == "inside")
    assert match.folders[1].path == "Holder"
    chosen = {folder.path for folder in match.folders} if both else {"Holder"}
    plan = cleanup.plan_cleanup(lib, report, folder_choices={match.id: chosen})
    assert str(lib.root / "Holder" / "unique.jpg") not in {action.src for action in plan.actions}
    assert len(plan.actions) == 2
    assert_safe(plan)
    if not both:
        assert str(lib.root / "Holder" / "shared.jpg") in {action.src for action in plan.actions}
    assert execute(lib, plan).done == 2


def test_overlapping_folder_recommendations_never_point_at_another_removal(make_library):
    lib = make_library({r"A\a.jpg": b"photo", r"B\b.jpg": b"photo", r"C\c.jpg": b"photo"})
    report = duplicates.find_all(lib)
    report.folders = [
        duplicates.FolderMatch("same", [duplicates.FolderInfo("A"), duplicates.FolderInfo("B")], "A"),
        duplicates.FolderMatch("same", [duplicates.FolderInfo("B"), duplicates.FolderInfo("C")], "B"),
        duplicates.FolderMatch("same", [duplicates.FolderInfo("A"), duplicates.FolderInfo("C")], "C"),
    ]
    choices = {match.id: {folder.path for folder in match.folders} for match in report.folders}
    plan = cleanup.plan_cleanup(lib, report, folder_choices=choices)
    assert len(plan.actions) == 2
    assert_safe(plan)
    assert execute(lib, plan).done == 2
    assert len(lib.files()) == 1


def test_unchecked_folder_and_file_protections_are_unioned(make_library):
    lib = make_library({r"Left\a.jpg": b"photo", r"Right\a.jpg": b"photo", "outside.jpg": b"photo"})
    report = duplicates.find_all(lib)
    match, group = report.folders[0], report.groups[0]
    chosen_folder = match.keeper
    chosen_id = lib.file_by_rel(chosen_folder + r"\a.jpg")["id"]
    plan = cleanup.plan_cleanup(
        lib, report, file_choices={group.hash: {row["id"] for row in group.files} - {chosen_id}},
        folder_choices={match.id: {chosen_folder}})
    assert [Path(action.src).name for action in plan.actions] == ["outside.jpg"]
    assert execute(lib, plan).done == 1
    assert lib.file(chosen_id) is not None
    assert len(lib.files()) == 2


def asset_files(*, different=None, third=False):
    result = {}
    for folder in ("Original", "Backup", "Third") if third else ("Original", "Backup"):
        for suffix, data in ((".jpg", b"photo"), (".mov", b"motion"), (".aae", b"edits")):
            result[f"{folder}\\IMG{suffix}"] = data + (b" unique" if (folder, suffix) == different else b"")
    return result


@pytest.mark.parametrize("partial_folders", [False, True])
def test_fully_equivalent_linked_assets_are_prepared_with_whole_survivor_guards(make_library, partial_folders):
    files = asset_files(third=True)
    if partial_folders:
        files.update({r"Original\unique.txt": b"one", r"Backup\unique.txt": b"two", r"Third\unique.txt": b"three"})
    lib = make_library(files)
    report = duplicates.find_all(lib)
    before = snapshot(lib)
    plan = cleanup.plan_cleanup(lib, report)
    assert len(plan.actions) == 6 and plan.groups == 2 and plan.linked_skipped == 0
    assert_safe(plan)
    assert len(assets.grouped(plan.actions)) == 2
    assert all(len(action.guards) == 3 and len(action.companion_ids) == 3 for action in plan.actions)
    preferred = report.folders[0].keeper if report.folders else "Original"
    assert all(preferred in guard for action in plan.actions for guard, _ in action.guards)
    result = execute(lib, plan)
    assert result.done == 6 and not result.skipped and not result.failed
    assert actions.undo(lib, result.batch_id).done == 6
    assert snapshot(lib) == before


@pytest.mark.parametrize("suffix", [".aae", ".mov", ".dng"])
def test_unique_linked_component_blocks_assets_but_not_unrelated_duplicates(make_library, suffix):
    files = asset_files(different=("Backup", suffix))
    if suffix == ".dng":
        files[r"Backup\IMG.dng"] = b"unique raw"
    else:
        original = files[f"Original\\IMG{suffix}"]
        files[f"Backup\\IMG{suffix}"] = bytes(value ^ 1 for value in original)
    files.update({"other.jpg": b"unrelated", "other copy.jpg": b"unrelated"})
    lib = make_library(files)
    report = duplicates.find_all(lib)
    plan = cleanup.plan_cleanup(lib, report)
    assert len(plan.actions) == 1 and plan.groups == 1 and plan.linked_skipped == 2
    assert Path(plan.actions[0].src).name == "other copy.jpg"
    before = snapshot(lib)
    assert execute(lib, plan).done == 1
    assert all(lib.abspath(path).read_bytes() == value for path, value in before.items() if "IMG" in path)


def test_linked_media_outside_hash_scope_is_never_silently_removed(make_library):
    lib = make_library(asset_files())
    report = duplicates.find_all(lib)
    photo = find_group(report, r"Original\IMG.jpg")
    plan = cleanup.plan_cleanup(lib, report, hashes={photo.hash})
    assert not plan.actions and plan.linked_skipped == 2


def test_protected_component_keeps_whole_unit_without_counting_normal_keepers_as_skips(make_library):
    lib = make_library(asset_files(third=True))
    report = duplicates.find_all(lib)
    photo = find_group(report, r"Original\IMG.jpg")
    protected = lib.file_by_rel(r"Backup\IMG.jpg")["id"]
    chosen = {row["id"] for row in photo.files} - {protected}
    plan = cleanup.plan_cleanup(lib, report, file_choices={photo.hash: chosen})
    assert len(plan.actions) == 6 and not plan.linked_skipped and plan.protected_groups == 1
    assert all("Backup" in path for action in plan.actions for path, _ in action.guards)
    assert_safe(plan)
    assert execute(lib, plan).done == 6


def test_new_catalogued_companion_after_report_is_not_added_to_bulk(make_library):
    lib = make_library(asset_files())
    report = duplicates.find_all(lib)
    (lib.root / "Backup" / "IMG.xmp").write_bytes(b"new companion")
    scanner.scan(lib)
    plan = cleanup.plan_cleanup(lib, report)
    assert not plan.actions and plan.linked_skipped == 2


def test_stale_sidecar_snapshot_is_not_replaced_with_fresh_matching_hashes(make_library):
    lib = make_library(asset_files())
    report = duplicates.find_all(lib)
    for folder in ("Original", "Backup"):
        path = lib.root / folder / "IMG.aae"
        stat = path.stat()
        path.write_bytes(b"other")
        os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
    plan = cleanup.plan_cleanup(lib, report)
    assert not plan.actions and plan.linked_skipped == 2
    assert all((lib.root / folder / "IMG.jpg").exists() for folder in ("Original", "Backup"))


@pytest.mark.parametrize("linked", [False, True])
def test_new_catalogued_companion_after_plan_fails_closed(make_library, linked):
    lib = make_library(asset_files() if linked else {r"A\a.jpg": b"photo", r"Backup\b.jpg": b"photo"})
    plan = cleanup.plan_cleanup(lib, duplicates.find_all(lib))
    path = Path(next(action.src for action in plan.actions if action.src.endswith(".jpg"))).with_suffix(".xmp")
    path.write_bytes(b"new companion")
    scanner.scan(lib)
    before = snapshot(lib)
    with pytest.raises(ValueError, match="component|review"):
        execute(lib, plan)
    assert snapshot(lib) == before


@pytest.mark.parametrize("target", ["source", "keeper", "sidecar", "keeper-sidecar"])
def test_changed_hash_at_execution_skips_without_losing_original_bytes(make_library, target):
    lib = make_library(asset_files() if "sidecar" in target else {"a.jpg": b"photo", "b.jpg": b"photo"})
    plan = cleanup.plan_cleanup(lib, duplicates.find_all(lib))
    action = next(action for action in plan.actions if action.src.endswith(".aae")) if "sidecar" in target else plan.actions[0]
    path = Path(next(path for path, _ in action.guards if path.endswith(".aae"))
                if target == "keeper-sidecar" else action.guards[0][0] if target == "keeper" else action.src)
    before_stat = path.stat()
    value = bytearray(path.read_bytes())
    value[-1] ^= 1
    path.write_bytes(value)
    os.utime(path, ns=(before_stat.st_atime_ns, before_stat.st_mtime_ns))
    before = snapshot(lib)
    result = execute(lib, plan)
    assert result.done == 0 and result.skipped == len(plan.actions) and not result.failed
    assert snapshot(lib) == before


def test_catalogue_key_change_after_review_is_rejected(make_library):
    lib = make_library({"a.jpg": b"photo", "b.jpg": b"photo"})
    report = duplicates.find_all(lib)
    lib.db.execute("UPDATE files SET rel_path='renamed.jpg',name='renamed.jpg' WHERE rel_path='b.jpg'")
    with pytest.raises(ValueError, match="changed"):
        cleanup.plan_cleanup(lib, report)


@pytest.mark.parametrize("failure", [None, "offline", "identity"])
def test_cross_root_duplicates_validate_identity_and_keep_survivor(make_library, tmp_path, failure):
    lib = make_library({"a.jpg": b"photo"})
    other = tmp_path / "external"
    other.mkdir()
    (other / "b.jpg").write_bytes(b"photo")
    source = roots.add(lib, other)
    scanner.scan(lib)
    report = duplicates.find_all(lib)
    if failure == "offline":
        lib.db.execute("UPDATE library_roots SET online=0 WHERE id=?", (source,))
    elif failure == "identity":
        marker = other / ".memoria" / roots.MARKER
        data = json.loads(marker.read_text())
        data["source"] = "different-volume"
        marker.write_text(json.dumps(data))
    if failure:
        with pytest.raises(LibraryUnavailable):
            cleanup.plan_cleanup(lib, report)
        assert (lib.root / "a.jpg").read_bytes() == (other / "b.jpg").read_bytes() == b"photo"
    else:
        plan = cleanup.plan_cleanup(lib, report)
        assert len(plan.actions) == 1
        assert_safe(plan)
        result = execute(lib, plan)
        assert result.done == 1 and not result.skipped
        assert sum(path.exists() for path in (lib.root / "a.jpg", other / "b.jpg")) == 1
        assert actions.undo(lib, result.batch_id).done == 1
        assert (lib.root / "a.jpg").read_bytes() == (other / "b.jpg").read_bytes() == b"photo"


def test_root_goes_offline_after_plan_cannot_be_a_survivor(make_library, tmp_path):
    lib = make_library({"a copy.jpg": b"photo"})
    other = tmp_path / "external"
    other.mkdir()
    (other / "a.jpg").write_bytes(b"photo")
    source = roots.add(lib, other)
    scanner.scan(lib)
    plan = cleanup.plan_cleanup(lib, duplicates.find_all(lib))
    assert Path(plan.actions[0].src).name == "a copy.jpg"
    lib.db.execute("UPDATE library_roots SET online=0 WHERE id=?", (source,))
    result = execute(lib, plan)
    assert result.done == 0 and result.skipped == 1
    assert (lib.root / "a copy.jpg").exists()


@pytest.mark.parametrize("suffix", [".aae", ".mov", ".dng"])
def test_combined_linked_review_includes_flagged_parts_and_undoes_one_scope(make_library, suffix):
    files = asset_files(different=("Backup", suffix))
    if suffix == ".dng":
        files[r"Backup\IMG.dng"] = b"unique raw"
    lib = make_library(files)
    report = duplicates.find_all(lib)
    photo = find_group(report, r"Original\IMG.jpg")
    source = lib.file_by_rel(r"Backup\IMG.jpg")["id"]
    choices = {photo.hash: {source}}
    strict = cleanup.plan_cleanup(lib, report, hashes={photo.hash}, file_choices=choices)
    assert not strict.actions and strict.linked_skipped and not strict.review_parts
    organisation.edit(lib, [source], favorite=True, add_tags=["Reviewed copy"])
    albums.create(lib, "Source album", [source])
    before, catalogued = snapshot(lib), [dict(row) for row in lib.files()]
    states = {row["id"]: organisation.state(lib, row["id"]) for row in catalogued}

    plan = cleanup.plan_cleanup(lib, report, hashes={photo.hash}, file_choices=choices, include_linked=True)
    assert len(plan.actions) == (4 if suffix == ".dng" else 3) and not plan.linked_skipped
    assert_safe(plan)
    assert {part["id"] for part in plan.review_parts} == {action.file_id for action in plan.actions}
    assert sum(part["size"] for part in plan.review_parts) == sum(action.size for action in plan.actions)
    unmatched = [part for part in plan.review_parts if part["unmatched"]]
    assert len(unmatched) == 1 and unmatched[0]["rel_path"] == f"Backup\\IMG{suffix}"
    assert "not proven duplicate / may be unique" in unmatched[0]["reason"]
    extra = next(action for action in plan.actions if action.file_id == unmatched[0]["id"])
    assert extra.merge_into is None and extra.hash == full_hash(extra.src)
    with pytest.raises(ValueError, match="review"):
        actions.apply(lib, "duplicates", "Not acknowledged", plan.actions)
    result = execute(lib, plan)
    assert result.done == len(plan.actions) and not result.skipped and not result.failed
    assert result.bytes == sum(part["size"] for part in plan.review_parts)
    keeper = next(action.merge_into for action in plan.actions if action.file_id == source)
    assert organisation.state(lib, keeper)["tags"] == ["Reviewed copy"]
    for group in report.groups:
        assert any(lib.abspath(row["rel_path"]).exists() for row in group.files)
    undone = actions.undo(lib, result.batch_id)
    assert undone.done == len(plan.actions) and not undone.failed
    assert snapshot(lib) == before and [dict(row) for row in lib.files()] == catalogued
    assert {fid: organisation.state(lib, fid) for fid in states} == states


def test_combined_review_retains_whole_unit_for_overlapping_out_of_scope_hash(make_library):
    lib = make_library({
        r"KeepA\a.jpg": b"first photo", r"CopyB\b.jpg": b"first photo", r"CopyB\b.mov": b"shared motion",
        r"CopyC\c.jpg": b"second photo", r"CopyC\c.mov": b"shared motion", r"KeepD\d.jpg": b"second photo",
    })
    report = duplicates.find_all(lib)
    first, second = find_group(report, r"CopyB\b.jpg"), find_group(report, r"CopyC\c.jpg")
    video = find_group(report, r"CopyB\b.mov")
    chosen = {group.hash: {lib.file_by_rel(path)["id"]}
              for group, path in ((first, r"CopyB\b.jpg"), (second, r"CopyC\c.jpg"))}
    plan = cleanup.plan_cleanup(lib, report, hashes={first.hash, second.hash},
                                file_choices=chosen, include_linked=True)
    assert len(plan.actions) == 2 and plan.linked_skipped == 1 and plan.groups == 2
    assert "preserve a verified exact-content copy" in plan.linked_reasons[0]
    assert not any(part["unmatched"] for part in plan.review_parts)
    assert_safe(plan)
    assert execute(lib, plan).done == 2
    for group in (first, second, video):
        assert any(lib.abspath(row["rel_path"]).exists() for row in group.files)


@pytest.mark.parametrize("linked", [False, True])
def test_combined_review_does_not_label_proven_duplicates_as_unmatched(make_library, linked):
    lib = make_library(asset_files() if linked else {"a.jpg": b"photo", "b.jpg": b"photo", "c.jpg": b"photo"})
    report = duplicates.find_all(lib)
    strict = cleanup.plan_cleanup(lib, report)
    plan = cleanup.plan_cleanup(lib, report, include_linked=True)
    assert {action.file_id for action in plan.actions} == {action.file_id for action in strict.actions}
    assert not any(part["unmatched"] for part in plan.review_parts) and not plan.linked_skipped
    assert bool(plan.review_parts) == linked
    assert_safe(plan)
    assert execute(lib, plan).done == len(plan.actions)


@pytest.mark.parametrize("protection", ["unchecked-file", "saved-file", "unchecked-folder", "saved-folder"])
def test_combined_linked_review_cannot_override_protected_components(make_library, protection):
    lib = make_library(asset_files())
    report = duplicates.find_all(lib)
    photo, video = find_group(report, r"Backup\IMG.jpg"), find_group(report, r"Backup\IMG.mov")
    backup = lib.file_by_rel(r"Backup\IMG.jpg")["id"]
    choices, folders, saved = {photo.hash: {backup}}, {}, set()
    if protection == "unchecked-file":
        choices[video.hash] = {lib.file_by_rel(r"Original\IMG.mov")["id"]}
    elif protection == "saved-file":
        saved.add(duplicates.file_review_key(video))
    else:
        match = report.folders[0]
        if protection == "unchecked-folder":
            folders[match.id] = {"Original"}
        else:
            saved.add(report.folder_review_key(match))
    for signature in saved:
        duplicates.remember_keep(lib, signature, True)
    before = snapshot(lib)
    plan = cleanup.plan_cleanup(lib, report, hashes={photo.hash}, file_choices=choices,
                                folder_choices=folders, include_linked=True)
    assert not plan.actions and not plan.review_parts
    if protection.endswith("file"):
        assert plan.linked_skipped == 1 and "protected" in plan.linked_reasons[0]
    assert duplicates.kept_choices(lib) == saved and snapshot(lib) == before


def test_combined_review_protects_hidden_copies_and_never_adds_unrelated_scope(make_library):
    files = asset_files(different=("Backup", ".aae"))
    files.update({"hidden.jpg": b"photo", "one.jpg": b"unrelated", "two.jpg": b"unrelated"})
    lib = make_library(files)
    report = duplicates.find_all(lib)
    photo = find_group(report, "hidden.jpg")
    source = lib.file_by_rel(r"Backup\IMG.jpg")["id"]
    plan = cleanup.plan_cleanup(lib, report, hashes={photo.hash},
                                file_choices={photo.hash: {source}}, include_linked=True)
    assert len(plan.actions) == 3 and all("Backup" in action.src for action in plan.actions)
    assert_safe(plan)
    assert execute(lib, plan).done == 3
    for path in ("hidden.jpg", "one.jpg", "two.jpg", r"Original\IMG.jpg"):
        assert lib.abspath(path).exists()
    assert not cleanup.plan_cleanup(lib, report, hashes=set(), include_linked=True).actions


@pytest.mark.parametrize("change", ["new", "missing", "same-stamp"])
def test_combined_review_blocks_stale_membership_and_content_but_keeps_other_work(make_library, change):
    files = asset_files()
    files.update({"one.jpg": b"unrelated", "two.jpg": b"unrelated"})
    lib = make_library(files)
    report = duplicates.find_all(lib)
    photo = find_group(report, r"Backup\IMG.jpg")
    source = lib.file_by_rel(r"Backup\IMG.jpg")["id"]
    path = lib.root / "Backup" / "IMG.aae"
    if change == "new":
        path.with_suffix(".xmp").write_bytes(b"new part")
        scanner.scan(lib)
    elif change == "missing":
        path.unlink()
        scanner.scan(lib)
    else:
        stamp = path.stat()
        path.write_bytes(b"other")
        os.utime(path, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
    plan = cleanup.plan_cleanup(lib, report, file_choices={photo.hash: {source}}, include_linked=True)
    assert len(plan.actions) == 1 and plan.linked_skipped >= 1 and plan.linked_reasons
    assert Path(plan.actions[0].src).name in {"one.jpg", "two.jpg"}
    assert not plan.review_parts


@pytest.mark.parametrize("change", ["new", "source-part", "keeper"])
def test_combined_plan_is_locked_against_changes_before_execution(make_library, change):
    lib = make_library(asset_files(different=("Backup", ".aae")))
    report = duplicates.find_all(lib)
    photo = find_group(report, r"Backup\IMG.jpg")
    source = lib.file_by_rel(r"Backup\IMG.jpg")["id"]
    plan = cleanup.plan_cleanup(lib, report, hashes={photo.hash},
                                file_choices={photo.hash: {source}}, include_linked=True)
    path = lib.root / ("Original" if change == "keeper" else "Backup") / (
        "IMG.jpg" if change == "keeper" else "IMG.xmp" if change == "new" else "IMG.aae")
    if change == "new":
        path.write_bytes(b"new linked part")
        scanner.scan(lib)
    else:
        stamp = path.stat()
        value = bytes(byte ^ 1 for byte in path.read_bytes())
        path.write_bytes(value)
        os.utime(path, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
    before = snapshot(lib)
    if change == "new":
        with pytest.raises(ValueError, match="component|review"):
            execute(lib, plan)
    else:
        result = execute(lib, plan)
        assert result.done == 0 and result.skipped == 3 and not result.failed
    assert snapshot(lib) == before


@pytest.mark.parametrize("failure", [None, "offline", "identity"])
def test_combined_cross_root_review_validates_identity_and_undo(make_library, tmp_path, failure):
    lib = make_library({"a.jpg": b"photo"})
    external = tmp_path / "external"
    external.mkdir()
    (external / "b.jpg").write_bytes(b"photo")
    (external / "b.aae").write_bytes(b"unmatched edits")
    source = roots.add(lib, external)
    scanner.scan(lib)
    report = duplicates.find_all(lib)
    group = report.groups[0]
    chosen = {lib.file_by_rel(roots.key_for(source, "b.jpg"))["id"]}
    if failure == "offline":
        lib.db.execute("UPDATE library_roots SET online=0 WHERE id=?", (source,))
    elif failure == "identity":
        marker = external / ".memoria" / roots.MARKER
        data = json.loads(marker.read_text())
        data["source"] = "different-volume"
        marker.write_text(json.dumps(data))
    if failure:
        with pytest.raises(LibraryUnavailable):
            cleanup.plan_cleanup(lib, report, file_choices={group.hash: chosen}, include_linked=True)
    else:
        plan = cleanup.plan_cleanup(lib, report, file_choices={group.hash: chosen}, include_linked=True)
        assert len(plan.actions) == 2 and sum(part["unmatched"] for part in plan.review_parts) == 1
        assert_safe(plan)
        result = execute(lib, plan)
        assert result.done == 2 and not result.skipped and not result.failed
        assert actions.undo(lib, result.batch_id).done == 2
    assert (lib.root / "a.jpg").read_bytes() == (external / "b.jpg").read_bytes() == b"photo"
    assert (external / "b.aae").read_bytes() == b"unmatched edits"


@pytest.mark.parametrize("include_linked", [False, True])
def test_cleanup_planning_obeys_cancellation_before_any_work(make_library, include_linked):
    lib = make_library({"a.jpg": b"photo", "b.jpg": b"photo"})
    report = duplicates.find_all(lib)
    progress = Progress()
    progress.cancel_event.set()
    with pytest.raises(Cancelled):
        cleanup.plan_cleanup(lib, report, include_linked=include_linked, progress=progress)
    assert len(lib.files()) == 2 and not lib.db.execute("SELECT 1 FROM operations").fetchone()


@pytest.mark.parametrize("include_linked", [False, True])
def test_linked_hashing_cancels_between_small_chunks_without_writes(make_library, monkeypatch, include_linked):
    lib = make_library(asset_files())
    report, before = duplicates.find_all(lib), snapshot(lib)
    progress, reads = Progress(), []
    real_open = open

    class CancelOnRead:
        def __init__(self, stream):
            self.stream = stream

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return self.stream.__exit__(*args)

        def readinto(self, buffer):
            count = self.stream.readinto(buffer)
            reads.append(count)
            progress.cancel_event.set()
            return count

    def interrupt(path, *args, **kwargs):
        stream = real_open(path, *args, **kwargs)
        return CancelOnRead(stream) if str(path).lower().endswith(".aae") else stream

    monkeypatch.setattr(cleanup, "open", interrupt, raising=False)
    monkeypatch.setattr(cleanup, "CHUNK", 2)
    with pytest.raises(Cancelled):
        cleanup.plan_cleanup(lib, report, include_linked=include_linked, progress=progress)
    assert reads and max(reads) <= 2
    assert snapshot(lib) == before and not lib.db.execute("SELECT 1 FROM operations").fetchone()
