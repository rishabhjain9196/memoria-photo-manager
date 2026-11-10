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


@pytest.fixture
def compressor_ui(tmp_path, monkeypatch):
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ.setdefault("QT_QPA_FONTDIR", r"C:\Windows\Fonts")
    from PySide6.QtCore import QObject, Signal
    from PySide6.QtWidgets import QApplication
    from memoria.engine.db import Library
    from memoria.ui.pages import video
    from memoria.ui.tasks import TaskRunner
    from memoria.ui.widgets import AppContext

    class Prober(QObject):
        probed = Signal(str, object, object)
        failed = Signal(str, str)

        def __init__(self, parent):
            super().__init__(parent)
            self.requests = []

        def request(self, key, path, frame, *, library=None):
            self.requests.append((key, path, frame))

        def stop(self):
            pass

    app = QApplication.instance() or QApplication([])
    monkeypatch.setattr(video, "_Prober", Prober)
    lib = Library(tmp_path)
    ctx = AppContext(TaskRunner())
    ctx.set_library(lib)
    page = video.VideoPage(ctx)
    yield app, lib, ctx, page
    page.shutdown()
    page.close()
    page.deleteLater()
    app.processEvents()
    lib.close()


def _catalogue_videos(lib, count):
    with lib.transaction() as db:
        db.executemany("INSERT INTO files(rel_path,folder,name,ext,kind,size,mtime,duration,width,height,"
                       "analyzed,metadata_version) VALUES (?,'',?,'.mp4','video',1000000,1,10,1920,1080,1,1)",
                       [(f"{i:05}.mp4", f"{i:05}.mp4") for i in range(count)])


def test_compressor_large_list_only_loads_visible_thumbnails(compressor_ui, monkeypatch):
    from PySide6.QtGui import QPixmap
    from memoria.ui.pages.video import C_NAME
    app, lib, ctx, page = compressor_ui
    _catalogue_videos(lib, 10_000)
    requested = []
    thumb = QPixmap(80, 45)
    thumb.fill()
    monkeypatch.setattr(ctx.thumbs, "get", lambda fid: requested.append(fid) or thumb)
    page._refresh_now()
    assert page.model.rowCount() == 10_000
    assert requested == [] and page.prober.requests == []  # no eager thumbnail decode or media probing
    page.resize(1400, 900)
    page.show()
    app.processEvents()
    assert 0 < len(set(requested)) < 100
    assert not page._checked and not page.compress_btn.isEnabled()
    page.table.scrollTo(page.model.index(9999, C_NAME))
    app.processEvents()
    assert 10_000 in requested and len(set(requested)) < 100
    assert not page.prober.requests


def test_compressor_bounds_probes_and_updates_only_completed_estimate(compressor_ui, monkeypatch):
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from memoria.ui.pages.video import C_CHECK, C_EST, MAX_PENDING_PROBES
    app, lib, ctx, page = compressor_ui
    _catalogue_videos(lib, 1000)
    page._refresh_now()
    page.resize(1400, 900)
    page.show()
    app.processEvents()
    first = page.model.index(0, C_CHECK)
    QTest.mouseClick(page.table.viewport(), Qt.MouseButton.LeftButton, pos=page.table.visualRect(first).center())
    assert first.data(Qt.ItemDataRole.CheckStateRole) == Qt.CheckState.Checked
    page._check_all(True)
    assert len(page.checked_rows()) == 1000  # Select all retains its meaning; this is not pagination
    assert len(page._pending) == len(page.prober.requests) == MAX_PENDING_PROBES
    calls = []
    estimate = vt.estimate
    monkeypatch.setattr(vt, "estimate", lambda info, settings: calls.append(settings.mode) or estimate(info, settings))
    info = ffmpeg.VideoInfo(duration=10, width=1920, height=1080, fps=30, bitrate_kbps=800)
    page.r_target.setChecked(True)  # results arriving later must use the current settings
    key = page.prober.requests[0][0]
    page.prober.probed.emit(key, info, None)
    assert calls == ["target"] and page._unknown == 999
    assert len(page._pending) == MAX_PENDING_PROBES
    assert len(page.prober.requests) == MAX_PENDING_PROBES + 1
    assert page.model.index(page._row_of[key], C_EST).data() == "Already under 25 MB"
    failed = page.prober.requests[1][0]
    page.prober.probed.emit(failed, None, None)
    assert page.model.index(page._row_of[failed], C_EST).data() == "Can't read"
    assert page._unknown == 999 and len(calls) == 1
    page._check_all(False)
    submitted = len(page.prober.requests)
    for pending in list(page._pending):
        page.prober.probed.emit(pending, info, None)
    assert len(page.prober.requests) == submitted and not page._probe_queue
    assert page._unknown == 0 and not page.compress_btn.isEnabled()
    assert first.data(Qt.ItemDataRole.CheckStateRole) == Qt.CheckState.Unchecked


def test_compressor_external_selection_with_empty_catalogue_and_shutdown(compressor_ui, tmp_path):
    from PySide6.QtGui import QImage
    from memoria.ui.pages.video import C_LEN, C_RES
    app, lib, ctx, page = compressor_ui
    path = tmp_path / "external.mp4"
    path.write_bytes(b"synthetic probe input")
    ctx.video_selection = [str(path), str(path)]
    page._refresh_now()
    import time
    deadline = time.monotonic() + 5
    while page.input_bg.running and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(.005)
    assert not ctx.video_selection and len(page.checked_rows()) == page.model.rowCount() == 1
    assert len(page.prober.requests) == 1 and page.prober.requests[0][2]
    key = page.prober.requests[0][0]
    image = QImage(32, 24, QImage.Format.Format_RGB32)
    image.fill(0)
    info = ffmpeg.VideoInfo(duration=12, width=640, height=480, fps=30)
    page.prober.probed.emit(key, info, image)
    assert page.model.index(0, C_LEN).data() == "0:12"
    assert page.model.index(0, C_RES).data() == "640×480"
    assert not page._rows[0]["thumb"].isNull()
    page.shutdown()
    page.prober.probed.emit(key, None, None)
    assert page._info[key] is info
    assert path.read_bytes() == b"synthetic probe input"


def test_compressor_rejects_probe_from_previous_catalogue_generation(compressor_ui):
    from memoria.ui.pages.video import C_EST
    app, lib, ctx, page = compressor_ui
    _catalogue_videos(lib, 1)
    page._refresh_now()
    page._check_all(True)
    key = page.prober.requests[0][0]
    old = ffmpeg.VideoInfo(duration=1, width=100, height=100)
    ctx.library_modified.emit()
    page.prober.failed.emit(key, "Old drive failure")
    page.prober.probed.emit(key, old, None)
    assert key not in page._info and key not in page._probe_errors
    assert len(page.prober.requests) == 2
    current = ffmpeg.VideoInfo(duration=10, width=1920, height=1080, fps=30)
    page.prober.probed.emit(key, current, None)
    assert page._info[key] is current
    assert page.model.index(0, C_EST).data() != "Can't read"
