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
    assert {"duplicates", "batch"} <= kinds                      # page clean-up and Photos batch action
    assert all(b["status"] == "undone" for b in batches)       # both undone (History button and Ctrl+Z)
    assert actions.recovery_size(check) == (0, 0)
    assert check.db.execute("SELECT COUNT(*) FROM parked_files").fetchone()[0] == 0
    check.close()
    assert {"photos-viewer", "dark-overview", "dark-similar"} <= shots
