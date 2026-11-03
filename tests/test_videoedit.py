import hashlib
import io
import sys
import threading
import time
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from memoria.engine import ffmpeg  # noqa: E402
from memoria.engine import videoedit as ve  # noqa: E402
from memoria.engine.progress import Cancelled, Progress  # noqa: E402


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _make_clip(path: Path, args: list[str]) -> Path:
    proc = ffmpeg.run_ffmpeg(["-y", *args, str(path)], timeout=120)
    assert proc.returncode == 0, proc.stderr.decode("utf-8", "replace")[-800:]
    return path


def _img(data: bytes) -> np.ndarray:
    return np.asarray(Image.open(io.BytesIO(data)).convert("RGB")).astype(np.int16)


def _close(a: float, b: float) -> bool:
    return abs(a - b) <= max(0.5, 0.03 * b)


@pytest.fixture(scope="module")
def clips(tmp_path_factory):
    d = tmp_path_factory.mktemp("veclips")
    landscape = _make_clip(d / "beach.mp4", [
        "-f", "lavfi", "-i", "testsrc2=size=640x360:rate=30", "-f", "lavfi", "-i", "sine=frequency=440",
        "-t", "4", "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "96k", "-metadata", "creation_time=2021-05-06T07:08:09Z"])
    portrait = _make_clip(d / "phone.mp4", [
        "-f", "lavfi", "-i", "testsrc2=size=360x640:rate=30", "-t", "3",
        "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p"])
    hashes = {p: _sha(p) for p in (landscape, portrait)}
    yield {"landscape": landscape, "portrait": portrait}
    for p, h in hashes.items():  # no test may ever touch a source
        assert _sha(p) == h
    assert sorted(x.name for x in d.iterdir()) == ["beach.mp4", "phone.mp4"]


def test_display_rotated_source_is_baked_upright(clips, tmp_path):
    """A phone clip stored landscape with a 90° display flag (common for phone videos)."""
    rotated = _make_clip(tmp_path / "flagged.mp4", ["-display_rotation", "90", "-i", str(clips["landscape"]),
                                                   "-c", "copy"])
    info = ffmpeg.probe(rotated)
    assert (info.width, info.height, info.rotation) == (360, 640, 90)
    out = ffmpeg.probe(ve.export(rotated, ve.VideoEdit(end=1.0), tmp_path / "o"))
    assert (out.width, out.height, out.rotation) == (360, 640, 0)
    out = ffmpeg.probe(ve.export(rotated, ve.VideoEdit(end=1.0, rotate=90), tmp_path / "o"))
    assert (out.width, out.height, out.rotation) == (640, 360, 0)
    joined = ffmpeg.probe(ve.join([rotated, clips["portrait"]], tmp_path / "o"))
    assert (joined.width, joined.height, joined.rotation) == (360, 640, 0)
    assert _img(ve.preview_frame(rotated, 1.0)).shape[:2] == (640, 360)


def _no_work_dirs(folder: Path) -> bool:
    return not [p for p in folder.rglob(".memoria-work-*")]


def test_edit_model_and_planning(clips):
    e = ve.VideoEdit()
    assert e.is_identity() and not e.copy(speed=2.0).is_identity() and not e.copy(mute=True).is_identity()
    assert e.copy(crop=(0, 0, 1, 1)).is_identity() and e.copy(start=1).start == 1 and e.start == 0
    assert ve.SPEEDS == (0.5, 1.0, 1.5, 2.0)
    info = ffmpeg.probe(clips["landscape"])
    assert ve.output_duration(info, e) == pytest.approx(info.duration)
    assert ve.output_duration(info, e.copy(start=1, end=3, speed=2.0)) == pytest.approx(1.0)
    assert ve.filter_graph(info, e) == "null"
    g = ve.filter_graph(info, e.copy(rotate=90, flip_h=True, crop=(0.1, 0.1, 0.5, 0.5), brightness=20,
                                      speed=2.0, max_height=100))
    parts = g.split(",")
    assert parts[0] == "transpose=1" and parts[1] == "hflip" and parts[2].startswith("crop=")
    assert parts[3].startswith("eq=brightness=") and parts[4].startswith("scale=") and parts[-1].startswith("setpts=")
    with pytest.raises(ve.VideoEditError):
        ve.output_duration(info, e.copy(start=3, end=2))


def test_trim_and_never_overwrite(clips, tmp_path):
    src = clips["landscape"]
    seen = []
    a = ve.export(src, ve.VideoEdit(start=1.0, end=3.0), tmp_path, progress=Progress(lambda d, t, m: seen.append((d, t))))
    b = ve.export(src, ve.VideoEdit(start=1.0, end=3.0), tmp_path)
    assert a.name == "beach (edited).mp4" and b.name == "beach (edited) (2).mp4"
    for p in (a, b):
        info = ffmpeg.probe(p)
        assert _close(info.duration, 2.0) and info.has_audio and (info.width, info.height) == (640, 360)
        assert info.vcodec == "h264"
    assert seen and all(t == 1000 for _, t in seen) and seen[-1][0] == 1000
    assert all(y[0] >= x[0] for x, y in zip(seen, seen[1:]))
    assert a.stat().st_mtime == pytest.approx(src.stat().st_mtime, abs=0.01)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["beach (edited) (2).mp4", "beach (edited).mp4"]


def test_default_output_folder_is_source_folder(tmp_path, clips):
    src = tmp_path / "copy.mp4"
    src.write_bytes(clips["portrait"].read_bytes())
    out = ve.export(src, ve.VideoEdit(end=1.0, quality="small"))
    assert out.parent == tmp_path and out.name == "copy (edited).mp4"


@pytest.mark.parametrize("speed,start,end,expected", [(2.0, 0.0, None, 2.0), (0.5, 0.0, 1.5, 3.0)])
def test_speed_changes_duration_and_keeps_audio(clips, tmp_path, speed, start, end, expected):
    out = ve.export(clips["landscape"], ve.VideoEdit(start=start, end=end, speed=speed), tmp_path)
    info = ffmpeg.probe(out)
    assert _close(info.duration, expected) and info.has_audio


def test_rotate_crop_mute_and_max_height(clips, tmp_path):
    src = clips["landscape"]
    r = ffmpeg.probe(ve.export(src, ve.VideoEdit(end=1.0, rotate=90, mute=True), tmp_path))
    assert (r.width, r.height) == (360, 640) and not r.has_audio
    c = ffmpeg.probe(ve.export(src, ve.VideoEdit(end=1.0, crop=(0.1, 0.1, 0.433, 0.777)), tmp_path))
    assert c.width % 2 == 0 and c.height % 2 == 0
    assert abs(c.width - 0.333 * 640) <= 2 and abs(c.height - 0.677 * 360) <= 2 and c.has_audio
    m = ffmpeg.probe(ve.export(clips["portrait"], ve.VideoEdit(end=1.0, max_height=180), tmp_path))
    assert m.width == 180 and m.height == 320 and not m.has_audio
    info = ffmpeg.probe(src)
    assert ve.output_size(info, ve.VideoEdit(rotate=270, crop=(0, 0, 0.5, 0.5))) == (180, 320)


def test_preview_frame_is_fast_and_applies_filters(clips):
    src = clips["landscape"]
    ve.preview_frame(src, 0.0)  # warm-up (process start, disk cache)
    t0 = time.perf_counter()
    plain = ve.preview_frame(src, 2.0)
    elapsed = time.perf_counter() - t0
    assert plain[:2] == b"\xff\xd8" and elapsed < 1.5
    a = _img(plain)
    assert a.shape[:2] == (360, 640)
    flipped = _img(ve.preview_frame(src, 2.0, ve.VideoEdit(flip_h=True)))
    assert np.abs(flipped - a[:, ::-1]).mean() < 6
    assert np.abs(flipped - a).mean() > 20
    bright = _img(ve.preview_frame(src, 2.0, ve.VideoEdit(brightness=60)))
    assert bright.mean() > a.mean() + 15
    rot = _img(ve.preview_frame(src, 2.0, ve.VideoEdit(rotate=90, crop=(0, 0, 0.5, 0.5))))
    assert abs(rot.shape[0] - 320) <= 2 and abs(rot.shape[1] - 180) <= 2
    uncropped = _img(ve.preview_frame(src, 2.0, ve.VideoEdit(rotate=90, crop=(0, 0, 0.5, 0.5)), crop=False))
    assert uncropped.shape[:2] == (640, 360)
    small = _img(ve.preview_frame(src, 2.0, max_side=320))
    assert small.shape[:2] == (180, 320)


def test_split_points_and_helpers(clips, tmp_path):
    src = clips["landscape"]
    parts = ve.split(src, [2.5, 1.0, 10.0, -1.0], tmp_path / "a")
    assert [p.name for p in parts] == [f"beach (part {i} of 3).mp4" for i in (1, 2, 3)]
    durs = [ffmpeg.probe(p).duration for p in parts]
    assert _close(sum(durs), 4.0) and _close(durs[0], 1.0) and _close(durs[1], 1.5)
    assert all(ffmpeg.probe(p).has_audio for p in parts)

    eq = ve.split_equal(clips["portrait"], 3, tmp_path / "b")
    assert len(eq) == 3 and all(_close(ffmpeg.probe(p).duration, 1.0) for p in eq)
    every = ve.split_every(src, 1.5, tmp_path / "c", edit=ve.VideoEdit(end=3.5))
    assert [round(ffmpeg.probe(p).duration, 1) for p in every] == pytest.approx([1.5, 1.5, 0.5], abs=0.15)
    with pytest.raises(ve.VideoEditError):
        ve.split(src, [5.0, 0.0], tmp_path / "d")
    assert _no_work_dirs(tmp_path)


def test_join_landscape_and_portrait(clips, tmp_path):
    out = ve.join([clips["landscape"], clips["portrait"]], tmp_path)
    assert out.name == "beach (joined).mp4"
    info = ffmpeg.probe(out)
    assert (info.width, info.height) == (640, 360)
    assert _close(info.duration, 7.0) and info.has_audio and info.vcodec == "h264"
    assert round(info.fps) == 30
    # the portrait clip is letterboxed: its last frame has black bars left and right
    a = _img(ve.preview_frame(out, 6.0))
    assert a[:, :100].mean() < 20 and a[:, 270:370].mean() > 40
    assert _no_work_dirs(tmp_path)


def test_extract_frame(clips, tmp_path):
    out = ve.extract_frame(clips["landscape"], 1.5, tmp_path)
    assert out.name == "beach (frame 0m01s).jpg"
    with Image.open(out) as im:
        assert im.size == (640, 360) and im.format == "JPEG"
        dto = im.getexif().get_ifd(0x8769).get(0x9003)
    assert dto == "2021:05:06 07:08:10"
    again = ve.extract_frame(clips["portrait"], 0.2, tmp_path)
    assert Image.open(again).size == (360, 640)


def test_cancelled_export_and_split_leave_nothing(clips, tmp_path):
    cancel = threading.Event()

    def cb(done, total, msg):
        if done > 0:
            cancel.set()

    with pytest.raises(Cancelled):
        ve.export(clips["landscape"], ve.VideoEdit(rotate=180), tmp_path, progress=Progress(cb, cancel))
    cancel.clear()
    with pytest.raises(Cancelled):
        ve.split(clips["landscape"], [1.0, 2.0], tmp_path,
                 progress=Progress(lambda d, t, m: d > 400 and cancel.set(), cancel))
    assert list(tmp_path.iterdir()) == []
