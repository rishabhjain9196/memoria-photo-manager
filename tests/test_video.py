import hashlib
import os
import sys
import threading
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from memoria.engine import ffmpeg  # noqa: E402
from memoria.engine import videotools as vt  # noqa: E402
from memoria.engine.progress import Cancelled, Progress  # noqa: E402


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _make_clip(path: Path, args: list[str]) -> Path:
    proc = ffmpeg.run_ffmpeg(["-y", *args, str(path)], timeout=120)
    assert proc.returncode == 0, proc.stderr.decode("utf-8", "replace")[-800:]
    return path


@pytest.fixture(scope="module")
def clips(tmp_path_factory):
    d = tmp_path_factory.mktemp("clips")
    landscape = _make_clip(d / "holiday.mp4", [
        "-f", "lavfi", "-i", "testsrc2=size=1280x720:rate=30", "-f", "lavfi", "-i", "sine=frequency=440",
        "-t", "4", "-c:v", "libx264", "-preset", "ultrafast", "-b:v", "8M", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k"])
    portrait = _make_clip(d / "phone.mp4", [
        "-f", "lavfi", "-i", "testsrc2=size=720x1280:rate=30", "-t", "3",
        "-c:v", "libx264", "-preset", "ultrafast", "-b:v", "6M", "-pix_fmt", "yuv420p"])
    tiny = _make_clip(d / "tiny.mp4", [
        "-f", "lavfi", "-i", "testsrc2=size=320x240:rate=30", "-t", "2",
        "-c:v", "libx264", "-preset", "veryslow", "-b:v", "40k", "-pix_fmt", "yuv420p"])
    return {"landscape": landscape, "portrait": portrait, "tiny": tiny}


def test_quality_mode_shrinks_verifies_and_never_overwrites(clips, tmp_path):
    src = clips["landscape"]
    before = _sha(src)
    out = tmp_path / "out"
    seen = []
    r1 = vt.compress(src, out, vt.CompressSettings(), Progress(lambda d, t, m: seen.append((d, t))))
    r2 = vt.compress(src, out, vt.CompressSettings())

    for r in (r1, r2):
        assert r.ok, r.message
        assert r.dst is not None and r.dst.exists()
        assert r.dst_bytes == r.dst.stat().st_size < r.src_bytes == src.stat().st_size
        assert abs(r.duration_dst - r.duration_src) <= max(0.5, 0.02 * r.duration_src)
        assert r.ssim is not None and 0.9 < r.ssim <= 1.0
        assert "smaller" in r.message and "SSIM" in r.message and "→" in r.message
        assert r.saved_pct > 30
        info = ffmpeg.probe(r.dst)
        assert (info.width, info.height) == (1280, 720)
        assert info.vcodec == "h264" and info.has_audio
    assert r1.dst.name == "holiday (compressed).mp4"
    assert r2.dst.name == "holiday (compressed) (2).mp4"
    assert sorted(os.listdir(out)) == ["holiday (compressed) (2).mp4", "holiday (compressed).mp4"]
    assert _sha(src) == before
    assert seen and seen[-1][0] == seen[-1][1]
    assert all(b[0] >= a[0] for a, b in zip(seen, seen[1:]))


def test_target_mode_fits_small_target(clips, tmp_path):
    src = clips["landscape"]
    settings = vt.CompressSettings(mode="target", target_mb=1.0, measure_quality=False)
    est = vt.estimate(ffmpeg.probe(src), settings)
    assert est["feasible"] and est["est_mb"] <= 1.0
    r = vt.compress(src, tmp_path, settings)
    assert r.ok, r.message
    assert r.dst_bytes <= 1.15 * vt.MB
    assert r.ssim is None
    assert not [p for p in tmp_path.iterdir() if p.name.startswith(".")]  # passlogs cleaned up
    assert [p.name for p in tmp_path.iterdir()] == ["holiday (compressed).mp4"]


def test_portrait_without_audio_is_downscaled_by_short_side(clips, tmp_path):
    src = clips["portrait"]
    before = _sha(src)
    r = vt.compress(src, tmp_path, vt.CompressSettings(max_height=480, quality="small"))
    assert r.ok, r.message
    info = ffmpeg.probe(r.dst)
    assert info.width == 480 and info.height % 2 == 0 and abs(info.height - 853) <= 2
    assert not info.has_audio
    assert _sha(src) == before


def test_keeps_original_when_not_smaller(clips, tmp_path):
    r = vt.compress(clips["tiny"], tmp_path, vt.CompressSettings(quality="high", max_height=None))
    assert not r.ok and r.dst is None
    assert r.message == "Compressed copy was not smaller; kept original only"
    assert list(tmp_path.iterdir()) == []


def test_cancel_removes_partial_output(clips, tmp_path):
    src = clips["landscape"]
    before = _sha(src)
    cancel = threading.Event()
    progress = Progress(lambda d, t, m: cancel.set(), cancel)
    with pytest.raises(Cancelled):
        vt.compress(src, tmp_path, vt.CompressSettings(mode="target", target_mb=1.0), progress)
    assert list(tmp_path.iterdir()) == []
    assert _sha(src) == before


def test_estimate_flags_impossible_target(clips):
    info = ffmpeg.probe(clips["landscape"])
    est = vt.estimate(info, vt.CompressSettings(mode="target", target_mb=0.02))
    assert est["feasible"] is False
    assert "too small" in est["note"]
    q = vt.estimate(info, vt.CompressSettings())
    assert q["est_mb"] > 0 and q["note"]


def test_compress_many_reports_each_file(clips, tmp_path):
    seen = []
    results = vt.compress_many([clips["portrait"], clips["tiny"], tmp_path / "missing.mp4"], tmp_path / "o",
                               vt.CompressSettings(quality="small", measure_quality=False),
                               Progress(lambda d, t, m: seen.append((d, t, m))))
    assert [r.ok for r in results] == [True, False, False]
    assert seen[-1][0] == seen[-1][1] == 3000
    assert all(b[0] >= a[0] for a, b in zip(seen, seen[1:]))
