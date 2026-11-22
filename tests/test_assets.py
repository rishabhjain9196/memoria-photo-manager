import os
import time

import pytest

from memoria.engine import assets, batch, scanner
from memoria.engine.actions import Action
from memoria.engine.db import Library


@pytest.fixture
def asset_library(tmp_path):
    root = tmp_path / "library"
    root.mkdir()
    for name in ("IMG_1.HEIC", "IMG_1.MOV", "IMG_1.AAE", "IMG_2.JPG", "IMG_2.DNG", "IMG_2.DNG.xmp",
                 "unrelated.jpg"):
        (root / name).write_bytes(name.encode())
    lib = Library(root)
    scanner.scan(lib)
    yield lib
    lib.close()


def test_prepare_groups_live_photo_and_raw_sidecars_without_absorbing_other_files(asset_library):
    lib = asset_library
    selected = [dict(lib.file_by_rel(name)) for name in ("IMG_1.HEIC", "IMG_2.JPG")]
    prepared = assets.prepare(lib, batch.plan_recycle(lib, selected), "batch")
    assert len(prepared.groups) == 2 and prepared.extra_files == 4
    assert {lib.rel(action.src) for action in prepared.actions} == {
        "IMG_1.HEIC", "IMG_1.MOV", "IMG_1.AAE", "IMG_2.JPG", "IMG_2.DNG", "IMG_2.DNG.xmp"}
    assert len(assets.grouped(prepared.actions)) == 2
    for unit in assets.grouped(prepared.actions):
        assets.validate_membership(lib, unit)
    assert all(lib.abspath(name).exists() for name in ("IMG_1.AAE", "IMG_1.HEIC", "IMG_1.MOV"))


def test_companion_copy_keeps_each_album_destination_and_shared_collision_name(asset_library, tmp_path):
    lib = asset_library
    selected = [dict(lib.file_by_rel("IMG_1.HEIC"))]
    first, second = tmp_path / "first", tmp_path / "second"
    first.mkdir()
    (first / "IMG_1.MOV").write_bytes(b"existing video must not be overwritten")
    planned = batch.plan_copy_to(lib, selected, first) + batch.plan_copy_to(lib, selected, second)
    prepared = assets.prepare(lib, planned, "albums")
    assert len(prepared.groups) == 2 and len(prepared.actions) == 6
    reserved = set()
    for unit in assets.grouped(prepared.actions):
        from pathlib import Path
        destinations = assets.destinations(unit, [Path(action.dst) for action in unit], reserved)
        if destinations[0].parent == first:
            assert {path.name for path in destinations} == {"IMG_1 (2).HEIC", "IMG_1 (2).MOV", "IMG_1 (2).AAE"}
        else:
            assert {path.name for path in destinations} == {"IMG_1.HEIC", "IMG_1.MOV", "IMG_1.AAE"}


def test_linked_selection_refuses_conflicting_keeper_and_stale_folder_snapshot(asset_library):
    lib = asset_library
    selected = [dict(lib.file_by_rel("IMG_1.HEIC"))]
    planned = batch.plan_recycle(lib, selected)
    planned[0].guards = [(str(lib.abspath("IMG_1.MOV")), "reviewed-hash")]
    with pytest.raises(ValueError, match="surviving copy"):
        assets.prepare(lib, planned, "duplicates")
    planned[0].guards = []
    planned[0].companions_locked = True
    with pytest.raises(ValueError, match="folder snapshot"):
        assets.prepare(lib, planned, "duplicates")
    with pytest.raises(ValueError, match="Tidy"):
        assets.prepare(lib, batch.plan_recycle(lib, selected), "tidy")


def test_linked_plan_detects_new_catalogued_component_after_review(asset_library):
    lib = asset_library
    prepared = assets.prepare(lib, batch.plan_recycle(lib, [dict(lib.file_by_rel("IMG_1.HEIC"))]), "batch")
    (lib.root / "IMG_1.xmp").write_bytes(b"new edit data")
    scanner.scan(lib)
    with pytest.raises(ValueError, match="changed after review"):
        assets.validate_membership(lib, prepared.actions)


def test_linked_files_require_confirmation_even_when_quick_mode_skips_it(asset_library, monkeypatch):
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    from PySide6.QtWidgets import QApplication
    from memoria.ui.pages import base
    from memoria.ui.tasks import TaskRunner
    from memoria.ui.widgets import AppContext
    app = QApplication.instance() or QApplication([])
    runner = TaskRunner()
    ctx = AppContext(runner)
    ctx.set_library(asset_library)
    page = base.Page(ctx)
    prompts, mutations, declined, errors = [], [], [], []
    runner.error.connect(lambda *args: errors.append(args))
    monkeypatch.setattr(base, "confirm", lambda *args, **kwargs: prompts.append((args, kwargs)) or False)
    plan = batch.plan_recycle(asset_library, [dict(asset_library.file_by_rel("IMG_1.HEIC"))])
    try:
        assert page.apply_actions(
            "batch", "Move selected files", plan, summary="One selected photo", details=[], confirm_text="Move 1 file",
            note=base.recovery_note(), done_message=lambda _: "Moved", confirm_action=False,
            before_apply=lambda: mutations.append(True), on_declined=lambda: declined.append(True))
        deadline = time.monotonic() + 10
        while runner.active and time.monotonic() < deadline:
            app.processEvents()
            time.sleep(.01)
        app.processEvents()
        assert not runner.active and not errors
        assert len(prompts) == 1 and prompts[0][1]["require_ack"]
        assert len(prompts[0][1]["file_ids"]) == 3
        assert prompts[0][0][4] == "Move 3 files"
        assert declined == [True] and not mutations
        assert all(asset_library.abspath(name).exists() for name in ("IMG_1.HEIC", "IMG_1.MOV", "IMG_1.AAE"))
    finally:
        runner.cancel()
        runner.wait()
        page.deleteLater()
        app.processEvents()
