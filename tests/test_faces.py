"""People: face detection and recognition against public-domain portraits with known identities."""
import os
import shutil

import numpy as np
import pytest
from PIL import Image, ImageOps

from memoria.engine import actions, batch, faces, scanner

pytestmark = pytest.mark.skipif(not faces.available(), reason="face models not available")


def _groups_by_files(lib):
    return {g.key: {r["rel_path"] for r in faces.photos_of(lib, g.key)} for g in faces.groups(lib, min_photos=1)}


def _files_snapshot(root):
    return {p: (p.stat().st_size, p.stat().st_mtime) for p in root.rglob("*") if p.is_file() and ".memoria" not in p.parts}


def test_group_faces_separates_clusters():
    rng = np.random.default_rng(7)
    centres = faces._unit(rng.normal(size=(3, 128)).astype(np.float32))
    E = faces._unit(np.concatenate([c + rng.normal(scale=0.06, size=(20, 128)) for c in centres]).astype(np.float32))
    labels = faces.group_faces(E)
    assert len(set(labels)) == 3
    for k in range(3):
        assert len(set(labels[k * 20:(k + 1) * 20])) == 1


def test_scan_finds_the_people_and_nothing_else(library, expected):
    before = _files_snapshot(library.root)
    res = faces.scan(library)
    assert res.checked == res.photos > 0
    groups = _groups_by_files(library)
    everyone = {f for files in expected["people"].values() for f in files}
    for person, files in expected["people"].items():
        g = next(k for k, got in groups.items() if set(files) <= got)          # all of a person's photos together…
        assert not (groups[g] - set(files) - set(expected["faces_hard"]))      # …with nobody else in the group
        assert not (groups[g] & (everyone - set(files)))
    found = {r["rel_path"] for r in library.files("id IN (SELECT file_id FROM faces)")}
    assert found <= everyone | set(expected["faces_hard"])                    # no faces in landscapes and screenshots
    assert not found & set(expected["no_face"])
    assert _files_snapshot(library.root) == before                            # photos are never changed
    assert faces.scan(library).checked == 0                                   # second run: nothing new to look at


def test_changed_and_deleted_photos_are_rescanned_and_forgotten(library, expected):
    faces.scan(library)
    target = library.abspath(expected["people"]["Abraham Lincoln"][0])
    old = {r["face_id"] for r in faces.faces_in(library, library.file_by_rel(expected["people"]["Abraham Lincoln"][0])["id"])}
    ImageOps.mirror(Image.open(target)).save(target, quality=90)
    gone = library.abspath(expected["people"]["Mark Twain"][0])
    os.remove(gone)
    scanner.index(library)
    res = faces.scan(library)
    assert res.checked == 1
    fid = library.file_by_rel(expected["people"]["Abraham Lincoln"][0])["id"]
    new = {r["face_id"] for r in faces.faces_in(library, fid)}
    assert new and not new & old
    assert library.db.execute("SELECT COUNT(*) FROM faces WHERE file_id NOT IN (SELECT id FROM files)").fetchone()[0] == 0
    lincoln = next(k for k, got in _groups_by_files(library).items()
                   if set(expected["people"]["Abraham Lincoln"]) <= got)
    assert lincoln                                                            # the mirrored photo is still Lincoln


def test_naming_merging_and_corrections_stick(library, expected):
    faces.scan(library)
    groups = _groups_by_files(library)
    lin = next(k for k, got in groups.items() if set(expected["people"]["Abraham Lincoln"]) <= got)
    twa = next(k for k, got in groups.items() if set(expected["people"]["Mark Twain"]) <= got)
    pid = faces.name(library, lin, "  Abe   Lincoln ")
    assert library.db.execute("SELECT name FROM people").fetchone()[0] == "Abe Lincoln"
    faces.name(library, f"p{pid}", "Abraham Lincoln")
    faces.cluster(library)                                                    # names survive regrouping
    assert {r["rel_path"] for r in faces.photos_of(library, f"p{pid}")} == set(expected["people"]["Abraham Lincoln"])
    tw = faces.name(library, twa, "Mark Twain")
    assert {g.name for g in faces.groups(library) if g.named} == {"Abraham Lincoln", "Mark Twain"}
    # A wrong face: taken out, it is never matched to that person again — even after regrouping.
    one = faces.faces_of(library, f"p{tw}")[0]["face_id"]
    faces.not_this_person(library, [one])
    faces.cluster(library)
    assert one not in {r["face_id"] for r in faces.faces_of(library, f"p{tw}")}
    faces.assign(library, [one], tw)
    faces.cluster(library)
    assert one in {r["face_id"] for r in faces.faces_of(library, f"p{tw}")}
    # Using an existing name joins the two people.
    faces.name(library, f"p{tw}", "abraham lincoln")
    assert library.db.execute("SELECT COUNT(*) FROM people").fetchone()[0] == 1
    # Photos search: names by file
    names = faces.names_by_file(library)
    assert all("Abraham Lincoln" in names[library.file_by_rel(r)["id"]] for r in expected["people"]["Abraham Lincoln"])


def test_look_alike_search_ranks_the_same_person_first(library, expected):
    faces.scan(library)
    lincoln = set(expected["people"]["Abraham Lincoln"])
    fid = library.file_by_rel(sorted(lincoln)[0])["id"]
    face = faces.faces_in(library, fid)[0]["face_id"]
    hits = faces.similar(library, face)
    got = [h["rel_path"] for h in hits]
    assert set(got) == lincoln and hits[0]["similarity"] > 0.99
    assert all(a["similarity"] >= b["similarity"] for a, b in zip(hits, hits[1:]))


def test_recycled_photo_keeps_its_faces_for_undo(library, expected):
    faces.scan(library)
    groups = _groups_by_files(library)
    pid = faces.name(library, next(k for k, got in groups.items() if set(expected["people"]["Mark Twain"]) <= got),
                     "Mark Twain")
    row = dict(library.file_by_rel(expected["people"]["Mark Twain"][0]))
    res = actions.apply(library, "batch", "Recycle", batch.plan_recycle(library, [row]))
    faces.scan(library)
    assert row["rel_path"] not in {r["rel_path"] for r in faces.photos_of(library, f"p{pid}")}
    actions.undo(library, res.batch_id)
    faces.scan(library)
    assert row["rel_path"] in {r["rel_path"] for r in faces.photos_of(library, f"p{pid}")}


def test_hide_and_forget_all(library):
    before = _files_snapshot(library.root)
    faces.scan(library)
    g = next(g for g in faces.groups(library) if not g.named)
    faces.hide(library, g.key)
    assert g.key not in {x.key for x in faces.groups(library)}
    assert faces.unhide_all(library) > 0
    faces.name(library, faces.groups(library)[0].key, "Someone")
    faces.forget_all(library)
    for t in ("faces", "face_scans", "people", "face_rejects"):
        assert library.db.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] == 0
    assert library.thumbs_db.execute("SELECT COUNT(*) FROM face_thumbs").fetchone()[0] == 0
    assert _files_snapshot(library.root) == before


def test_models_load_from_any_path(tmp_path, monkeypatch, expected, pristine_library):
    """Models are read by Python and handed to OpenCV as bytes, so non-ASCII install paths work."""
    odd = tmp_path / "Ünïcödé models"
    shutil.copytree(faces.DATA, odd)
    monkeypatch.setattr(faces, "DETECTOR", odd / faces.DETECTOR.name)
    monkeypatch.setattr(faces, "RECOGNIZER", odd / faces.RECOGNIZER.name)
    monkeypatch.setattr(faces, "_buffers", {})
    monkeypatch.setattr(faces, "_local", type(faces._local)())
    found = faces.detect(pristine_library / expected["people"]["Abraham Lincoln"][0])
    assert len(found) == 1 and found[0].emb.shape == (128,) and found[0].thumb[:2] == b"\xff\xd8"
