"""End-to-end UI smoke test: drives every page offscreen, applies a change and undoes it."""
import os
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))


def test_every_page_runs_without_errors(pristine_library, tmp_path):
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    lib = tmp_path / "library"
    shutil.copytree(pristine_library, lib)
    import ui_screenshots
    from memoria.engine import actions
    from memoria.engine.db import Library

    errors = ui_screenshots.run(str(lib), str(tmp_path / "shots"))
    assert errors == []
    shots = {p.stem for p in (tmp_path / "shots").glob("*.png")}
    assert {"01-overview", "03-duplicates", "04-similar", "21-history-after-apply", "22-history-after-undo"} <= shots

    check = Library(lib)
    batches = actions.batches(check)
    kinds = {b["kind"] for b in batches}
    assert {"duplicates", "batch", "edit"} <= kinds              # clean-up, Photos batch action, Editor saves
    assert all(b["status"] == "undone" for b in batches if b["kind"] != "edit")
    edits = [b for b in batches if b["kind"] == "edit"]
    assert len(edits) == 2 and all(b["status"] == "applied" for b in edits)
    created = [Path(o["dst"]) for b in edits for o in actions.operations(check, b["id"])]
    assert created and all(p.exists() and "(edited)" in p.name for p in created)
    before = {p: p.stat().st_size for p in lib.rglob("*") if p.is_file() and ".memoria" not in p.parts and p not in created}
    for b in edits:
        assert actions.undo(check, b["id"]).ok
    assert not any(p.exists() for p in created)               # Undo removes only the edited copies
    after = {p: p.stat().st_size for p in lib.rglob("*") if p.is_file() and ".memoria" not in p.parts}
    assert after == before                                     # originals untouched
    assert actions.recovery_size(check) == (0, 0)
    assert check.db.execute("SELECT COUNT(*) FROM parked_files").fetchone()[0] == 0
    check.close()
    assert {"photos-viewer", "dark-overview", "dark-similar", "07-editor-crop", "07-editor-video"} <= shots
