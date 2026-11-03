import os
import sys
import threading
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from memoria.engine import actions, scanner, videosim  # noqa: E402
from memoria.engine.hashing import full_hash  # noqa: E402
from memoria.engine.progress import Cancelled, Progress  # noqa: E402


def _tree(root: Path) -> dict[str, str]:
    return {str(p.relative_to(root)): full_hash(p) for p in root.rglob("*")
            if p.is_file() and ".memoria" not in p.parts}


def _no_ffmpeg(*a, **k):
    raise AssertionError("ffmpeg should not run: signature was cached")


def _groups(lib, **kw):
    return sorted(videosim.find_similar_videos(lib, **kw), key=lambda g: sorted(f["rel_path"] for f in g.files))


def test_groups_and_best_pick_match_ground_truth(library, expected):
    want = expected["similar_videos"]
    assert len(want) >= 2
    seen = []
    groups = _groups(library, progress=Progress(lambda d, t, m: seen.append((d, t, m)), interval=0))
    assert [sorted(f["rel_path"] for f in g.files) for g in groups] == [w["files"] for w in want]
    for g, w in zip(groups, want):
        best = next(f for f in g.files if f["id"] == g.best_id)
        assert best["rel_path"] == w["best"] == g.files[0]["rel_path"]
        assert not g.burst
        assert g.reasons[g.best_id].startswith("Best pick: ")
        assert all(g.reasons[f["id"]].startswith("Weaker: ") for f in g.files[1:])
        assert g.scores[g.best_id] == max(g.scores.values())
        assert g.reclaimable == sum(f["size"] for f in g.files[1:])
    wa = next(g for g in groups if any("WhatsApp" in f["rel_path"] for f in g.files))
    assert "highest resolution (1280×720)" in wa.reasons[wa.best_id]
    assert "smaller (640×360)" in wa.reasons[wa.files[1]["id"]]
    trim = next(g for g in groups if any("trim" in f["rel_path"] for f in g.files))
    assert "shorter" in trim.reasons[trim.files[1]["id"]]

    grouped = {f["rel_path"] for g in groups for f in g.files}
    unrelated = set(expected["videos"]) - grouped
    assert "Camera Roll\\2024\\VID_20240211_101500.mp4" in unrelated and "iPhone Import\\IMG_5001.MOV" in unrelated
    assert not any(r.startswith("Phone Backup") for r in grouped)       # exact copy collapsed away

    assert seen and all(0 <= d <= t and t > 0 for d, t, _ in seen)
    assert any(m.startswith("Reading videos…") for _, _, m in seen)
    assert seen[-1][0] == seen[-1][1]


def test_byte_identical_copies_are_not_a_group_by_themselves(library, expected):
    trimmed = next(r for w in expected["similar_videos"] for r in w["files"] if "trim" in r)
    original = next(w["best"] for w in expected["similar_videos"] if trimmed in w["files"])
    library.remove_rows([library.file_by_rel(trimmed)["id"]])
    groups = videosim.find_similar_videos(library)
    members = {f["rel_path"] for g in groups for f in g.files}
    assert original not in members and "Phone Backup\\2023\\VID_20230610_090000.mp4" not in members
    assert len(groups) == len(expected["similar_videos"]) - 1


def test_signatures_are_cached(library, monkeypatch):
    first = _groups(library)
    n = library.db.execute("SELECT COUNT(*) FROM video_sigs").fetchone()[0]
    assert n == len(library.files("kind='video' AND error IS NULL AND duration > 0"))
    monkeypatch.setattr(videosim, "_grab_all", _no_ffmpeg)
    monkeypatch.setattr(videosim, "_grab_one", _no_ffmpeg)
    monkeypatch.setattr(videosim.ffmpeg, "run_ffmpeg", _no_ffmpeg)
    second = _groups(library)
    assert [[f["id"] for f in g.files] for g in second] == [[f["id"] for f in g.files] for g in first]


def test_cache_invalidates_when_file_changes(library, expected, monkeypatch):
    videosim.find_similar_videos(library)
    rel = expected["similar_videos"][0]["files"][1]
    p = library.abspath(rel)
    st = p.stat()
    os.utime(p, (st.st_atime, st.st_mtime + 60))
    scanner.index(library)
    calls = []
    real = videosim.signature
    monkeypatch.setattr(videosim, "signature", lambda path, dur: calls.append(Path(path)) or real(path, dur))
    groups = videosim.find_similar_videos(library)
    assert calls == [p]
    assert len(groups) == len(expected["similar_videos"])


def test_cancel_raises_cleanly(library):
    cancel = threading.Event()
    with pytest.raises(Cancelled):
        videosim.find_similar_videos(library, Progress(lambda d, t, m: cancel.set(), cancel, interval=0))
    assert library.db.execute("SELECT COUNT(*) FROM video_sigs").fetchone()[0] >= 0
    assert len(videosim.find_similar_videos(library)) >= 2         # still usable afterwards


def test_frame_distance_and_duration_rules():
    a = [0x0F0F, 0x00FF, 0x1234, 0xFFFF, 0x0, 0x1, 0x3, 0x7]
    assert videosim.frame_distance(a, a) == 0
    shifted = a[1:] + [0x5555]
    assert videosim.frame_distance(a, shifted) == 0                  # one-frame trim alignment
    assert videosim.frame_distance(a, [None] * 8) is None             # nothing comparable
    neg = [-1] * 8                                                    # signed int64 hashes (all bits set)
    assert videosim.frame_distance(neg, [0] * 8) == 64
    assert videosim.durations_close(3.0, 2.1) and not videosim.durations_close(3.0, 1.9)
    assert videosim.durations_close(100.0, 96.0) and not videosim.durations_close(100.0, 95.0)


def test_recycle_apply_and_undo_round_trip(library):
    before = _tree(library.root)
    groups = videosim.find_similar_videos(library)
    victims = [f for g in groups for f in g.files if f["id"] != g.best_id]
    plan = videosim.plan_recycle(library, victims, "Lower-quality copy of a video")
    res = actions.apply(library, "similar_videos", "Remove similar videos", plan)
    assert res.ok and res.done == len(victims) > 0
    for g in groups:
        for f in g.files:
            assert library.abspath(f["rel_path"]).exists() == (f["id"] == g.best_id)
    assert videosim.find_similar_videos(library) == []
    undo = actions.undo(library, res.batch_id)
    assert undo.ok and undo.done == res.done
    assert _tree(library.root) == before
    assert len(videosim.find_similar_videos(library)) == len(groups)
