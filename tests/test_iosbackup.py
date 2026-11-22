import hashlib
import os
import plistlib
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pytest

from memoria.engine import iosbackup, scanner
from memoria.engine.db import Library
from memoria.engine.hashing import full_hash
from memoria.engine.progress import Cancelled, Progress

PHOTO_TIME = datetime(2021, 6, 5, 14, 30).timestamp()


def _mbfile(size: int, mtime: float) -> bytes:
    return plistlib.dumps({
        "$version": 100000, "$archiver": "NSKeyedArchiver", "$top": {"root": plistlib.UID(1)},
        "$objects": ["$null", {"$class": plistlib.UID(2), "Size": size, "LastModified": int(mtime),
                               "Birth": int(mtime), "Mode": 33188},
                     {"$classname": "MBFile", "$classes": ["MBFile", "NSObject"]}],
    }, fmt=plistlib.FMT_BINARY)


def make_backup(root: Path, files: dict[tuple[str, str], bytes], *, encrypted=False, sizes=None) -> Path:
    """A minimal unencrypted iTunes-style backup: Manifest.db + files stored by SHA-1 id."""
    backup = root / "00008140-TESTDEVICE"
    backup.mkdir(parents=True)
    conn = sqlite3.connect(backup / "Manifest.db")
    conn.execute("CREATE TABLE Files (fileID TEXT PRIMARY KEY, domain TEXT, relativePath TEXT, flags INTEGER, file BLOB)")
    for (domain, rel), data in files.items():
        file_id = hashlib.sha1(f"{domain}-{rel}".encode()).hexdigest()
        (backup / file_id[:2]).mkdir(exist_ok=True)
        (backup / file_id[:2] / file_id).write_bytes(data)
        size = (sizes or {}).get(rel, len(data))
        conn.execute("INSERT INTO Files VALUES (?,?,?,1,?)", (file_id, domain, rel, _mbfile(size, PHOTO_TIME)))
    conn.execute("INSERT INTO Files VALUES (?,?,?,2,NULL)", ("f" * 40, "CameraRollDomain", "Media/DCIM"))
    conn.commit()
    conn.close()
    with open(backup / "Info.plist", "wb") as f:
        plistlib.dump({"Device Name": "Test iPhone", "Product Type": "iPhone16,2", "Product Version": "18.1",
                       "Last Backup Date": datetime(2026, 11, 1, 9, 0)}, f)
    with open(backup / "Manifest.plist", "wb") as f:
        plistlib.dump({"IsEncrypted": encrypted, "Lockdown": {"DeviceName": "Test iPhone"}}, f)
    with open(backup / "Status.plist", "wb") as f:
        plistlib.dump({"SnapshotState": "finished"}, f)
    return backup


def snapshot(folder: Path) -> dict[str, tuple[int, float, str]]:
    return {str(p.relative_to(folder)): (p.stat().st_size, p.stat().st_mtime, full_hash(p))
            for p in folder.rglob("*") if p.is_file()}


FILES = {
    ("CameraRollDomain", "Media/DCIM/100APPLE/IMG_0001.HEIC"): b"heic-photo" * 1000,
    ("CameraRollDomain", "Media/DCIM/100APPLE/IMG_0001.MOV"): b"live-video" * 3000,
    ("CameraRollDomain", "Media/DCIM/100APPLE/img_0001.heic"): b"other-photo-same-name-other-case" * 50,
    ("CameraRollDomain", "Media/PhotoData/Photos.sqlite"): b"photos-db",
    ("AppDomainGroup-group.net.whatsapp.WhatsApp.shared", "Message/Media/123@s.whatsapp.net/a/b/pic.jpg"): b"wa-jpg" * 100,
    ("HomeDomain", "Library/Preferences/com.apple.x.plist"): b"pref",
    ("CameraRollDomain", "Media/DCIM/../../../escape.jpg"): b"sneaky",
}


def test_reads_device_details_and_lists_categories(tmp_path):
    backup = make_backup(tmp_path / "Backups", FILES)
    found = iosbackup.find_backups([tmp_path / "Backups"])
    info = next(b for b in found if b.path == backup)
    assert (info.device_name, info.product_type, info.ios_version, info.encrypted, info.complete) == \
        ("Test iPhone", "iPhone16,2", "18.1", False, True)
    entries = iosbackup.list_files(info)
    assert len(entries) == len(FILES)  # folders (flags=2) are not files
    summary = iosbackup.summarize(entries)
    assert summary["camera_roll"][0] == 4 and summary["whatsapp_media"][0] == 1 and summary["system"][0] == 2
    assert {e.mtime for e in entries} == {PHOTO_TIME}


def test_extract_is_safe_complete_and_never_overwrites(tmp_path):
    backup = iosbackup.read_backup(make_backup(tmp_path / "Backups", FILES))
    before = snapshot(backup.path)
    dest = tmp_path / "out"
    (dest / "Camera Roll" / "100APPLE").mkdir(parents=True)
    (dest / "Camera Roll" / "100APPLE" / "IMG_0001.HEIC").write_bytes(b"user's own file")

    result = iosbackup.extract(backup, dest, ["camera_roll", "whatsapp_media"])

    assert snapshot(backup.path) == before                       # backup untouched, no side files
    assert (dest / "Camera Roll" / "100APPLE" / "IMG_0001.HEIC").read_bytes() == b"user's own file"
    folder = dest / "Camera Roll" / "100APPLE"
    assert sorted(p.name.lower() for p in folder.iterdir()) == \
        ["img_0001 (2).heic", "img_0001 (3).heic", "img_0001.heic", "img_0001.mov"]
    renamed = {p.read_bytes() for p in folder.iterdir() if "(" in p.name}
    assert renamed == {b"heic-photo" * 1000, b"other-photo-same-name-other-case" * 50}
    assert (dest / "WhatsApp" / "Media" / "123@s.whatsapp.net" / "a" / "b" / "pic.jpg").is_file()
    assert (dest / "Camera Roll" / "escape.jpg").read_bytes() == b"sneaky"   # '..' can't leave the folder
    assert not (tmp_path / "escape.jpg").exists()
    assert abs((dest / "Camera Roll" / "100APPLE" / "IMG_0001.MOV").stat().st_mtime - PHOTO_TIME) < 2
    assert (result.copied, result.renamed, result.failed) == (5, 2, 0)
    assert not list(dest.rglob("*.part"))


def test_extract_resumes_without_copying_again(tmp_path):
    backup = iosbackup.read_backup(make_backup(tmp_path / "Backups", FILES))
    dest = tmp_path / "out"
    first = iosbackup.extract(backup, dest, ["camera_roll"])
    again = iosbackup.extract(backup, dest, ["camera_roll"])
    assert (again.copied, again.resumed) == (0, first.copied)
    # An interruption after the rename but before the record was saved must not create "(2)" copies.
    (dest / ".memoria" / iosbackup.STATE_NAME).unlink()
    third = iosbackup.extract(backup, dest, ["camera_roll"])
    assert (third.copied, third.resumed) == (0, first.copied)
    assert len([p for p in dest.rglob("*") if p.is_file() and ".memoria" not in p.parts]) == first.copied


def test_cancel_leaves_no_partial_files(tmp_path):
    backup = iosbackup.read_backup(make_backup(tmp_path / "Backups", FILES))
    dest = tmp_path / "out"
    progress = Progress()
    progress.cancel_event.set()
    with pytest.raises(Cancelled):
        iosbackup.extract(backup, dest, ["camera_roll"], progress=progress)
    assert not [p for p in dest.rglob("*") if p.is_file() and ".memoria" not in p.parts]


def test_size_mismatch_is_reported_but_kept(tmp_path):
    rel = "Media/DCIM/100APPLE/IMG_0001.HEIC"
    backup = iosbackup.read_backup(make_backup(tmp_path / "Backups", {("CameraRollDomain", rel): b"x" * 10},
                                               sizes={rel: 99}))
    result = iosbackup.extract(backup, tmp_path / "out", ["camera_roll"])
    assert (result.copied, result.size_mismatches) == (1, 1)
    assert (tmp_path / "out" / "Camera Roll" / "100APPLE" / "IMG_0001.HEIC").read_bytes() == b"x" * 10


def test_encrypted_and_bad_destinations_are_refused(tmp_path):
    encrypted = iosbackup.read_backup(make_backup(tmp_path / "A", FILES, encrypted=True))
    with pytest.raises(iosbackup.BackupError, match="encrypted"):
        iosbackup.list_files(encrypted)
    plain = iosbackup.read_backup(make_backup(tmp_path / "B", FILES))
    with pytest.raises(iosbackup.BackupError, match="outside the backup"):
        iosbackup.extract(plain, plain.path / "out", ["camera_roll"])
    with pytest.raises(iosbackup.BackupError, match="Manifest.db"):
        iosbackup.read_backup(tmp_path)


def test_import_dialog_offers_library_import_and_refuses_encrypted(tmp_path):
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    import time
    from PySide6.QtWidgets import QApplication
    from memoria.ui.ios_import import IosImportDialog
    app = QApplication.instance() or QApplication([])
    plain = iosbackup.read_backup(make_backup(tmp_path / "A", FILES))
    locked = iosbackup.read_backup(make_backup(tmp_path / "B", FILES, encrypted=True))
    (tmp_path / "Library").mkdir()
    lib = Library(tmp_path / "Library")
    dialog = IosImportDialog(None, lib)
    try:
        dialog._finder.invalidate()
        dialog._found([plain, locked])
        deadline = time.monotonic() + 5
        while dialog.entries is None and time.monotonic() < deadline:
            app.processEvents()
            time.sleep(0.01)
        assert dialog.go_btn.isEnabled()
        assert "4 files" in dialog.boxes["camera_roll"].text()     # media only in library mode
        assert not dialog.boxes["system"].isEnabled()
        choice = dialog.choices()
        assert choice["library_mode"] and choice["categories"] == ["camera_roll"]
        assert choice["destination"] == tmp_path / "Library" / "iPhone backups" / "Test iPhone 2026-11-01"
        dialog.picker.setCurrentIndex(1)
        assert "encrypted" in dialog.state.text() and not dialog.go_btn.isEnabled()
    finally:
        dialog.close()
        dialog.deleteLater()
        app.processEvents()
        lib.close()


def test_library_import_skips_photos_already_in_the_library(tmp_path):
    backup = iosbackup.read_backup(make_backup(tmp_path / "Backups", FILES))
    lib_root = tmp_path / "Library"
    lib_root.mkdir()
    (lib_root / "old copy.heic").write_bytes(b"heic-photo" * 1000)
    (lib_root / "same size other bytes.heic").write_bytes(b"HEIC-PHOTO" * 1000)
    lib = Library(lib_root)
    try:
        scanner.scan(lib)  # no analysis: the library hash is computed on demand
        dest = iosbackup.default_library_folder(lib, backup)
        result = iosbackup.extract(backup, dest, iosbackup.MEDIA_CATEGORIES, media_only=True, library=lib)
        assert result.already_in_library == 1
        names = sorted(p.name for p in dest.rglob("*") if p.is_file() and ".memoria" not in p.parts)
        assert names == ["IMG_0001.MOV", "escape.jpg", "img_0001.heic", "pic.jpg"]   # no Photos.sqlite/plist
        assert lib.file_by_rel("old copy.heic")["chash"] == full_hash(lib_root / "old copy.heic")
    finally:
        lib.close()

def _photos_db(tmp_path: Path) -> bytes:
    """A small Photos.sqlite with the iOS 16+ layout (numbered album join table)."""
    path = tmp_path / "Photos.sqlite"
    conn = sqlite3.connect(path)
    conn.executescript("""
        CREATE TABLE ZASSET (Z_PK INTEGER PRIMARY KEY, ZDIRECTORY TEXT, ZFILENAME TEXT, ZDATECREATED REAL,
                             ZFAVORITE INTEGER, ZHIDDEN INTEGER, ZTRASHEDSTATE INTEGER);
        CREATE TABLE ZADDITIONALASSETATTRIBUTES (Z_PK INTEGER PRIMARY KEY, ZASSET INTEGER, ZTIMEZONEOFFSET INTEGER);
        CREATE TABLE ZGENERICALBUM (Z_PK INTEGER PRIMARY KEY, ZTITLE TEXT, ZKIND INTEGER, ZTRASHEDSTATE INTEGER);
        CREATE TABLE Z_28ASSETS (Z_28ALBUMS INTEGER, Z_3ASSETS INTEGER, Z_FOK_3ASSETS INTEGER);
    """)
    taken = datetime(2019, 3, 4, 4, 50, 30, tzinfo=timezone.utc).timestamp() - iosbackup.APPLE_EPOCH
    conn.executemany("INSERT INTO ZASSET VALUES (?,?,?,?,?,?,?)", [
        (1, "DCIM/100APPLE", "IMG_0001.HEIC", taken, 1, 0, 0),
        (2, "DCIM/100APPLE", "IMG_0002.JPG", taken, 0, 1, 0),
        (3, "DCIM/100APPLE", "IMG_0003.JPG", taken, 0, 0, 1)])
    conn.executemany("INSERT INTO ZADDITIONALASSETATTRIBUTES VALUES (?,?,?)", [(1, 1, 19800), (2, 2, 19800)])
    conn.executemany("INSERT INTO ZGENERICALBUM VALUES (?,?,?,?)", [(1, "Trip", 2, 0), (2, "Recents", 1505, 0)])
    conn.executemany("INSERT INTO Z_28ASSETS VALUES (?,?,?)", [(1, 1, 1), (2, 1, 1), (2, 2, 2)])
    conn.commit()
    conn.close()
    return path.read_bytes()


def test_library_import_keeps_iphone_favourites_albums_dates_and_skips_recently_deleted(tmp_path):
    files = {("CameraRollDomain", "Media/DCIM/100APPLE/IMG_0001.HEIC"): b"heic-photo" * 1000,
             ("CameraRollDomain", "Media/DCIM/100APPLE/IMG_0001.MOV"): b"live-video" * 3000,
             ("CameraRollDomain", "Media/DCIM/100APPLE/IMG_0002.JPG"): b"hidden-photo" * 100,
             ("CameraRollDomain", "Media/DCIM/100APPLE/IMG_0003.JPG"): b"deleted-photo" * 100,
             ("CameraRollDomain", iosbackup.PHOTOS_DB): _photos_db(tmp_path)}
    backup = iosbackup.read_backup(make_backup(tmp_path / "Backups", files))
    before = snapshot(backup.path)
    lib_root = tmp_path / "Library"
    lib_root.mkdir()
    (lib_root / "old copy.heic").write_bytes(b"heic-photo" * 1000)
    lib = Library(lib_root)
    try:
        scanner.scan(lib)
        entries = iosbackup.list_files(backup)
        photos = iosbackup.read_photos_library(backup, entries)
        assert snapshot(backup.path) == before                    # read from a temporary copy
        kept = [e for e in entries if not ((i := iosbackup.photo_info(e, photos)) and i.trashed)]
        dest = iosbackup.default_library_folder(lib, backup)
        result = iosbackup.extract(backup, dest, ["camera_roll"], media_only=True, library=lib, entries=kept)
        assert sorted(p.name for p in dest.rglob("*") if p.is_file() and ".memoria" not in p.parts) == \
            ["IMG_0001.MOV", "IMG_0002.JPG"]                        # HEIC already held; deleted one left out
        scanner.scan(lib)
        summary = iosbackup.apply_photos_details(lib, dest, kept, result, photos)
        assert summary == {"favourites": 2, "albums": 2, "dates": 3}

        def row(rel):
            return lib.file_by_rel(rel)

        def albums_of(rel):
            return sorted(r[0] for r in lib.db.execute(
                "SELECT a.name FROM albums a JOIN album_items i ON i.album_id=a.id WHERE i.file_id=?",
                (row(rel)["id"],)))
        live = lib.rel(dest / "Camera Roll" / "100APPLE" / "IMG_0001.MOV")
        hidden = lib.rel(dest / "Camera Roll" / "100APPLE" / "IMG_0002.JPG")
        assert albums_of("old copy.heic") == albums_of(live) == ["Trip"]   # smart albums are not copied
        assert albums_of(hidden) == [iosbackup.HIDDEN_ALBUM]
        fav = {r[0] for r in lib.db.execute("SELECT file_id FROM file_metadata WHERE favorite=1")}
        assert fav == {row("old copy.heic")["id"], row(live)["id"]}
        assert (row(hidden)["taken_at"], row(hidden)["date_source"]) == ("2019-03-04 10:20:30", "iphone")
        scanner.analyze(lib)                                          # re-analysis keeps the Photos date
        assert (row(hidden)["taken_at"], row(hidden)["date_source"]) == ("2019-03-04 10:20:30", "iphone")
        iosbackup.apply_photos_details(lib, dest, kept, result, photos)   # repeating adds no albums
        assert lib.db.execute("SELECT COUNT(*) FROM albums").fetchone()[0] == 2
    finally:
        lib.close()
