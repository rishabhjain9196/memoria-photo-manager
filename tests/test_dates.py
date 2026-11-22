import json
import os
from datetime import datetime

from PIL import Image
from PIL.PngImagePlugin import PngInfo

from memoria.engine import dates, media, scanner
from memoria.engine.db import Library

TAKEN = datetime(2019, 12, 25, 10, 11, 12)


def _jpeg(path, xmp: bytes = b""):
    Image.new("RGB", (64, 48), (90, 120, 150)).save(path, "JPEG", xmp=xmp) if xmp else \
        Image.new("RGB", (64, 48), (90, 120, 150)).save(path, "JPEG")
    os.utime(path, (1_700_000_000, 1_700_000_000))   # a "copied in 2023" modified time


def _index(root):
    lib = Library(root)
    scanner.index(lib)
    return lib


def test_new_date_sources_are_used_before_the_modified_time(tmp_path):
    _jpeg(tmp_path / "takeout.jpg")
    (tmp_path / "takeout.jpg.supplemental-metadata.json").write_text(
        json.dumps({"photoTakenTime": {"timestamp": str(int(TAKEN.timestamp()))}}))
    _jpeg(tmp_path / "xmp_sidecar.jpg")
    (tmp_path / "xmp_sidecar.xmp").write_text(
        '<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:Description exif:DateTimeOriginal="2019-12-25T10:11:12"/></x:xmpmeta>')
    _jpeg(tmp_path / "embedded.jpg",
          xmp=b'<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:Description xmp:CreateDate="2019-12-25T10:11:12"/></x:xmpmeta>')
    info = PngInfo()
    info.add_text("Creation Time", "2019-12-25T10:11:12")
    Image.new("RGB", (32, 32)).save(tmp_path / "screen.png", pnginfo=info)
    _jpeg(tmp_path / f"FB_IMG_{int(TAKEN.timestamp())}000.jpg")
    lib = _index(tmp_path)
    try:
        got = {r["name"]: (r["date_source"], r["taken_at"]) for r in lib.files()}
        assert got["takeout.jpg"] == ("sidecar", "2019-12-25 10:11:12")
        assert got["xmp_sidecar.jpg"] == ("sidecar", "2019-12-25 10:11:12")
        assert got["embedded.jpg"] == ("metadata", "2019-12-25 10:11:12")
        assert got["screen.png"] == ("metadata", "2019-12-25 10:11:12")
        assert got[f"FB_IMG_{int(TAKEN.timestamp())}000.jpg"] == ("filename", "2019-12-25 10:11:12")
    finally:
        lib.close()


def test_same_named_file_lends_its_date_and_manual_dates_survive_rescans(tmp_path):
    img = Image.new("RGB", (64, 48))
    exif = img.getexif()
    exif.get_ifd(0x8769)[0x9003] = "2019:12:25 10:11:12"
    img.save(tmp_path / "IMG_0001.jpg", exif=exif)
    _jpeg(tmp_path / "IMG_0001 (1)-edited.jpg")
    _jpeg(tmp_path / "unrelated.jpg")
    lib = _index(tmp_path)
    try:
        edited = lib.file_by_rel("IMG_0001 (1)-edited.jpg")
        assert (edited["date_source"], edited["taken_at"]) == ("inferred", "2019-12-25 10:11:12")
        unrelated = lib.file_by_rel("unrelated.jpg")
        assert unrelated["date_source"] == "modified"

        dates.set_manual(lib, [unrelated["id"]], datetime(2005, 6, 7, 8, 9))
        p = tmp_path / "unrelated.jpg"
        os.utime(p, (p.stat().st_atime, p.stat().st_mtime + 60))   # changed file → re-analysed
        scanner.index(lib)
        row = lib.file(unrelated["id"])
        assert (row["date_source"], row["taken_at"]) == ("manual", "2005-06-07 08:09:00")

        dates.set_manual(lib, [unrelated["id"]], None)
        scanner.index(lib)
        assert lib.file(unrelated["id"])["date_source"] == "modified"
    finally:
        lib.close()


def test_existing_catalogues_get_new_dates_once_without_reanalysis(tmp_path):
    _jpeg(tmp_path / "old.jpg")
    lib = _index(tmp_path)
    try:
        assert lib.file_by_rel("old.jpg")["date_source"] == "modified"
        # An older catalogue: the sidecar appears later and the backfill marker is missing.
        (tmp_path / "old.jpg.json").write_text(json.dumps({"photoTakenTime": {"timestamp": str(int(TAKEN.timestamp()))}}))
        (tmp_path / ".memoria" / scanner.DATES_MARKER).unlink()
        scanner.analyze(lib)
        assert lib.file_by_rel("old.jpg")["date_source"] == "sidecar"
        assert (tmp_path / ".memoria" / scanner.DATES_MARKER).exists()
    finally:
        lib.close()


def test_filename_epoch_and_copy_suffixes():
    assert media.date_from_filename("received_1577268672.jpeg") == datetime.fromtimestamp(1577268672)
    assert media.date_from_filename("photo_9876543210.jpg") is None
    assert dates.base_stem("IMG_1234 (1)-edited.HEIC") == dates.base_stem("img_1234.mov") == "img_1234"
    assert dates.base_stem("IMG_2.jpg") != dates.base_stem("IMG_3.jpg")
