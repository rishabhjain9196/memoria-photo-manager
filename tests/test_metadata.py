"""Extended metadata is read-only, resumable and numerically sorted with unknowns last."""
import json
import os
import sqlite3
from dataclasses import replace

import pytest
from PIL import Image, TiffImagePlugin

from memoria.engine import actions, batch, catalogue, ffmpeg, health, media, scanner
from memoria.engine.db import Library, METADATA_VERSION, MIGRATIONS, SCHEMA, SCHEMA_VERSION
from memoria.engine.hashing import full_hash
from memoria.engine.progress import Cancelled, Progress


def make_photo(path):
    exif = Image.Exif()
    exif[0x0112] = 6
    exif[0x010F], exif[0x0110] = "Canon", "Canon Test"
    rational = TiffImagePlugin.IFDRational
    exif[0x8769] = {0x9003: "2024:02:29 12:00:00", 0x8827: 640, 0x829D: rational(28, 10),
                    0x829A: rational(1, 125), 0x920A: rational(35, 1), 0xA434: "Lens <test>"}
    Image.new("RGB", (48, 32), "orange").save(path, exif=exif.tobytes())
    return path


def test_real_photo_metadata_and_orientation_are_read_only(tmp_path):
    path = make_photo(tmp_path / "photo.jpg")
    before = full_hash(path), path.stat().st_mtime_ns
    lib = Library(tmp_path)
    try:
        scanner.index(lib)
        row = dict(lib.files()[0])
        assert (row["width"], row["height"]) == (32, 48)
        assert row["iso"] == 640
        assert row["aperture"] == pytest.approx(2.8)
        assert row["exposure_seconds"] == pytest.approx(1 / 125)
        assert row["focal_length_mm"] == 35 and row["lens"] == "Lens <test>"
        assert row["metadata_version"] == METADATA_VERSION
        assert scanner.analyze(lib).analyzed == 0
        assert (full_hash(path), path.stat().st_mtime_ns) == before
    finally:
        lib.close()


def test_invalid_optional_exif_is_reported_without_rejecting_image(caplog, monkeypatch):
    image = Image.new("RGB", (8, 8))
    class MalformedExif(dict):
        def get_ifd(self, tag):
            return {0x8827: [], 0x829D: float("nan"), 0x829A: -1, 0x920A: "not a number"} if tag == 0x8769 else {}
    monkeypatch.setattr(image, "getexif", lambda: MalformedExif({0x010F: "Canon"}))
    result = media.read_exif(image)
    assert not set(media.PHOTO_METADATA) & result.keys()
    assert sum("Invalid optional EXIF field" in record.message for record in caplog.records) == 4


def test_schema5_backfill_preserves_identity_and_health(tmp_path):
    path = make_photo(tmp_path / "photo.jpg")
    app_dir = tmp_path / ".memoria"
    app_dir.mkdir()
    db = sqlite3.connect(app_dir / "memoria.db")
    db.executescript(SCHEMA)
    for version in range(2, 6):
        for sql in MIGRATIONS[version]:
            db.execute(sql)
    fingerprint = full_hash(path)
    db.execute("INSERT INTO files(id,rel_path,folder,name,ext,kind,size,mtime,analyzed,baseline_hash) "
               "VALUES (7,'photo.jpg','','photo.jpg','.jpg','image',?,?,1,?)",
               (path.stat().st_size, path.stat().st_mtime, fingerprint))
    db.execute("INSERT INTO albums VALUES (1,'Keep','manual','2024-01-01',7)")
    db.execute("INSERT INTO album_items VALUES (1,7,0)")
    db.execute("PRAGMA user_version=5")
    db.commit()
    db.close()
    lib = Library(tmp_path)
    try:
        assert lib.db.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION
        assert lib.stats()["pending"] == 1
        assert scanner.index(lib)[1].analyzed == 1
        assert lib.file(7)["iso"] == 640 and lib.file(7)["baseline_hash"] == fingerprint
        assert lib.db.execute("SELECT file_id FROM album_items").fetchone()[0] == 7
        assert scanner.index(lib)[1].analyzed == 0
    finally:
        lib.close()


@pytest.mark.parametrize("retained", ["parked", "missing"])
def test_legacy_retained_rows_backfill_on_return(tmp_path, retained):
    path = make_photo(tmp_path / "photo.jpg")
    data, stamp = path.read_bytes(), path.stat().st_mtime
    lib = Library(tmp_path)
    try:
        scanner.index(lib)
        health.run_health(lib)
        original = dict(lib.files()[0])
        if retained == "parked":
            result = actions.apply(lib, "batch", "Recycle", batch.plan_recycle(lib, [original]))
            table = "parked_files"
        else:
            path.unlink()
            scanner.scan(lib)
            table = "missing_files"
        old = json.loads(lib.db.execute(f"SELECT data FROM {table}").fetchone()[0])
        for key in ("metadata_version", "fps", "video_codec", "audio_codec", "iso", "aperture",
                    "exposure_seconds", "focal_length_mm", "lens"):
            old.pop(key)
        lib.db.execute(f"UPDATE {table} SET data=?", (json.dumps(old),))
        if retained == "parked":
            assert actions.undo(lib, result.batch_id).done == 1
        else:
            path.write_bytes(data)
            os.utime(path, (stamp, stamp))
        assert scanner.index(lib)[1].analyzed == 1
        row = lib.file(original["id"])
        assert row["iso"] == 640 and row["baseline_hash"] == original["baseline_hash"]
    finally:
        lib.close()


def test_video_metadata_is_catalogued_without_changing_source(tmp_path):
    path = tmp_path / "clip.mp4"
    result = ffmpeg.run_ffmpeg(["-f", "lavfi", "-i", "testsrc2=size=64x48:rate=24",
                               "-f", "lavfi", "-i", "sine=frequency=440", "-t", "0.5",
                               "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac", str(path)], timeout=30)
    assert result.returncode == 0, result.stderr.decode("utf-8", "replace")
    before = full_hash(path)
    lib = Library(tmp_path)
    try:
        scanner.index(lib)
        row = dict(lib.files()[0])
        assert row["fps"] == 24 and row["video_codec"] == "h264" and row["audio_codec"] == "aac"
        assert row["iso"] is None
        assert catalogue.overall_bitrate(row) == pytest.approx(path.stat().st_size * 8 / row["duration"] / 1e6)
        assert full_hash(path) == before
    finally:
        lib.close()


@pytest.fixture
def mixed(tmp_path):
    lib = Library(tmp_path)
    rows = [
        ("a.mp4", "video", 10_000_000, 2, 1920, 1080, 30, "h264", "aac", None, None, None, None),
        ("b.mp4", "video", 2_000_000, 10, 3840, 2160, 60, "hevc", "", None, None, None, None),
        ("c.jpg", "image", 3_000_000, None, 1600, 2400, None, None, None, 100, 2.8, .004, 35),
        ("d.jpg", "image", 8_000_000, None, 6000, 4000, None, None, None, 800, 8, .5, 85),
        ("e.mp4", "video", 100, 0, None, None, None, None, None, None, None, None, None),
    ]
    with lib.transaction() as db:
        for i, row in enumerate(rows):
            db.execute("INSERT INTO files(rel_path,kind,size,duration,width,height,fps,video_codec,audio_codec,"
                       "iso,aperture,exposure_seconds,focal_length_mm,folder,name,ext,mtime,analyzed,metadata_version) "
                       "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,'',?,?,?,1,?)",
                       (*row, row[0], ".mp4" if row[1] == "video" else ".jpg", 100 + i, METADATA_VERSION))
        db.execute("UPDATE files SET camera='Canon',lens='Lens <test>' WHERE kind='image'")
    yield lib
    lib.close()


@pytest.mark.parametrize("sort,expected", [
    ("duration_desc", [2, 1, 3, 4, 5]), ("duration_asc", [1, 2, 3, 4, 5]),
    ("megapixels_desc", [4, 2, 3, 1, 5]), ("megapixels_asc", [1, 3, 2, 4, 5]),
    ("bitrate_desc", [1, 2, 3, 4, 5]), ("bitrate_asc", [2, 1, 3, 4, 5]),
    ("fps_desc", [2, 1, 3, 4, 5]), ("iso_desc", [4, 3, 1, 2, 5]),
    ("aperture_asc", [3, 4, 1, 2, 5]), ("exposure_asc", [3, 4, 1, 2, 5]),
    ("focal_desc", [4, 3, 1, 2, 5]),
    ("audio_codec", [2, 1, 3, 4, 5]),
])
def test_numeric_sorting_and_missing_last(mixed, sort, expected):
    assert [r["id"] for r in catalogue.page(mixed, catalogue.Filters(), sort)[0]] == expected


def test_combined_technical_filters_and_unknown_audio(mixed):
    filters = catalogue.Filters(min_duration=3, max_duration=10, min_fps=30, max_bitrate=2,
                                min_megapixels=8, orientation="landscape", video_codec="hevc", audio_codec="")
    assert [r["id"] for r in catalogue.page(mixed, filters)[0]] == [2]
    filters = catalogue.Filters(camera="canon", lens="Lens <test>", min_iso=100, max_iso=100,
                                min_aperture=2, max_aperture=3, max_exposure=.004, max_focal=40,
                                min_width=1600, min_height=2000, orientation="portrait")
    assert [r["id"] for r in catalogue.page(mixed, filters)[0]] == [3]
    assert catalogue.page(mixed, replace(filters, camera="Canon' OR 1=1 --"))[1] == 0
    with pytest.raises(ValueError):
        catalogue.where(catalogue.Filters(min_duration=10, max_duration=1))
    with pytest.raises(ValueError):
        catalogue.where(catalogue.Filters(min_fps=float("nan")))


def test_backfill_cancel_resumes_only_uncommitted_rows(tmp_path, monkeypatch):
    lib = Library(tmp_path)
    try:
        with lib.transaction() as db:
            db.executemany("INSERT INTO files(rel_path,folder,name,ext,kind,size,mtime,analyzed) "
                           "VALUES (?,'',?,'.jpg','image',100,1,1)", [(f"{i}.jpg", f"{i}.jpg") for i in range(10)])
        monkeypatch.setattr(scanner, "_analyze_one", lambda *args: {"width": 10, "height": 10, "iso": 100})
        progress = Progress(lambda done, total, msg: progress.cancel_event.set() if done >= 2 else None, interval=0)
        with pytest.raises(Cancelled):
            scanner.analyze(lib, progress, workers=1)
        completed = lib.db.execute("SELECT COUNT(*) FROM files WHERE metadata_version=?", (METADATA_VERSION,)).fetchone()[0]
        assert 0 < completed < 10
        assert scanner.analyze(lib, workers=1).analyzed == 10 - completed
        assert lib.stats()["pending"] == 0
    finally:
        lib.close()


def test_metadata_filter_and_preview_ui(mixed, tmp_path):
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ.setdefault("QT_QPA_FONTDIR", r"C:\Windows\Fonts")
    from PySide6.QtGui import QFont
    from PySide6.QtWidgets import QApplication
    from memoria.ui import theme
    from memoria.ui.library_filters import FilterDialog, sort_caption
    from memoria.ui.pages.photos import PhotosPage
    from memoria.ui.tasks import TaskRunner
    from memoria.ui.widgets import AppContext
    app = QApplication.instance() or QApplication([])
    theme.use("light")
    app.setStyleSheet(theme.QSS)
    app.setFont(QFont("Segoe UI", 10))
    ctx = AppContext(TaskRunner())
    ctx.set_library(mixed)
    page = PhotosPage(ctx)
    page.resize(1200, 780)
    page.show()
    page.refresh()
    page.sort.setCurrentIndex(page.sort.findData("duration_desc"))
    assert page.rows[0]["id"] == 2 and page.rows[-1]["id"] == 5
    page.preview.show_row(page.rows[0])
    assert "60 fps" in page.preview.facts.text() and "No audio stream" in page.preview.facts.text()
    short_clip = {**page.rows[0], "duration": .5}
    page.preview.show_row(short_clip)
    assert "<b>Length</b> 0.5 s" in page.preview.facts.text()
    assert sort_caption(short_clip, "duration_asc") == "0.5 s"
    photo = dict(mixed.file(3))
    page.preview.show_row(photo)
    assert "Lens &lt;test&gt;" in page.preview.facts.text() and "1/250 s" in page.preview.facts.text()
    assert sort_caption(photo, "megapixels_desc") == "1600×2400 · 3.84 MP"
    dlg = FilterDialog(page, mixed, catalogue.Filters())
    dlg.ranges["duration"][0].setValue(3)
    dlg.ranges["bitrate"][1].setValue(2)
    dlg.metadata_text["audio_codec"].setCurrentIndex(dlg.metadata_text["audio_codec"].findData(""))
    page.open_filters(dlg.selected())
    assert [row["id"] for row in page.rows] == [2]
    dlg.show()
    dlg.tabs.setCurrentIndex(1)
    app.processEvents()
    assert dlg.height() <= app.primaryScreen().availableGeometry().height()
    assert dlg.grab().save(str(tmp_path / "metadata-video-filters.png"))
    dlg.tabs.setCurrentIndex(2)
    app.processEvents()
    assert dlg.grab().save(str(tmp_path / "metadata-photo-filters.png"))
    dlg.close()
    page.close()
    dlg.deleteLater()
    page.deleteLater()
    app.processEvents()
