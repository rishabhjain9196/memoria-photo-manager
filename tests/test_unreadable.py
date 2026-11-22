import os
import shutil

from PIL import Image

from memoria.engine import actions, duplicates, health, scanner, sniff
from memoria.engine.db import Library
from memoria.engine.hashing import full_hash


def test_identify_explains_common_unreadable_files():
    jpeg = b"\xff\xd8\xff\xe0" + b"x" * 100
    assert sniff.identify(b"", 0, ".jpg")["code"] == "empty"
    assert sniff.identify(b"\x00" * 5000, 5000, ".jpg")["code"] == "zeros"
    assert sniff.identify(b"<!DOCTYPE html><html>", 21, ".jpg")["code"] == "html"
    assert sniff.identify(jpeg, 104, ".jpg", tail=jpeg)["code"] == "truncated"
    assert sniff.identify(jpeg + b"\xff\xd9", 106, ".jpeg", tail=jpeg + b"\xff\xd9") is None
    mp4 = b"\x00\x00\x00\x18ftypisom" + b"\x00" * 50
    wrong = sniff.identify(mp4, len(mp4), ".jpg")
    assert (wrong["code"], wrong["fix_ext"]) == ("wrong_ext", ".mp4")
    assert sniff.identify(mp4, len(mp4), ".mov") is None
    assert sniff.parse_tag("UnidentifiedImageError: x" + sniff.tag(wrong)) == ("wrong_ext", ".mp4")


def test_wrong_extension_is_explained_and_fixed_with_undo(tmp_path):
    data = b"\x00\x00\x00\x18ftypisom" + os.urandom(2000)
    (tmp_path / "clip.jpg").write_bytes(data)
    Image.new("RGB", (40, 30)).save(tmp_path / "fine.jpg")
    lib = Library(tmp_path)
    try:
        scanner.index(lib)
        assert "[content: wrong_ext .mp4]" in lib.file_by_rel("clip.jpg")["error"]
        report = health.run_health(lib)
        acts = health.plan_extension_fixes(lib, report.problems)
        assert [os.path.basename(a.dst) for a in acts] == ["clip.mp4"]
        result = actions.apply(lib, "health", "Fix file extensions", acts)
        assert result.done == 1 and (tmp_path / "clip.mp4").read_bytes() == data and not (tmp_path / "clip.jpg").exists()
        actions.undo(lib, result.batch_id)
        assert (tmp_path / "clip.jpg").read_bytes() == data and not (tmp_path / "clip.mp4").exists()
    finally:
        lib.close()


def test_background_fingerprinting_fills_older_catalogues(tmp_path):
    for i in range(3):
        Image.new("RGB", (60, 40), (i * 40, 10, 10)).save(tmp_path / f"p{i}.jpg")
    lib = Library(tmp_path)
    try:
        scanner.index(lib)
        with lib.transaction() as db:   # as catalogued by an older version
            db.execute("UPDATE files SET chash=NULL, qhash=NULL")
        assert duplicates.missing_fingerprints(lib) == 3
        assert duplicates.fingerprint_missing(lib) == 3
        assert duplicates.missing_fingerprints(lib) == 0
        assert all(r["chash"] == full_hash(tmp_path / r["rel_path"]) for r in lib.files())
    finally:
        lib.close()
