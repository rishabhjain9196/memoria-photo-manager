"""People: find faces in photos, group them into people, name them, and find every photo of someone.

Runs entirely on this computer with two small open models from the OpenCV model zoo: YuNet finds
faces (MIT licence) and SFace turns each face into 128 numbers (Apache 2.0) — two photos of the
same person give similar numbers. Face positions, those numbers and names are stored only in this
library's catalogue, and :func:`forget_all` removes them. No photo is ever changed.
"""
from __future__ import annotations

import io
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image

from . import activity, config, media
from .db import Library
from .progress import Progress

DATA = Path(__file__).with_name("data")
DETECTOR = DATA / "face_detection_yunet_2023mar.onnx"
RECOGNIZER = DATA / "face_recognition_sface_2021dec.onnx"
MIN_SCORE = 0.8          # detector confidence needed to keep a face
MIN_FACE = 20            # px, in the (≤ LOAD_SIZE) image the detector sees
SAME_PERSON = 0.42       # cosine similarity at which two faces are taken to be the same person
LOAD_SIZE = 1600
THUMB = 128
DIM = 128
_local = threading.local()
_buffers: dict[str, np.ndarray] = {}
_buf_lock = threading.Lock()


@dataclass
class Face:
    box: tuple[float, float, float, float]   # x, y, w, h as fractions of the upright photo
    score: float
    emb: np.ndarray                          # 128 float32, unit length
    thumb: bytes                             # small JPEG of the face


@dataclass
class Group:
    """A named person, or an unnamed group of faces that look alike."""
    key: str                 # "p<person id>" or "c<cluster number>"
    name: Optional[str]
    faces: int
    photos: int
    cover: int               # face id used as the picture

    @property
    def named(self) -> bool:
        return self.key.startswith("p")

    @property
    def id(self) -> int:
        return int(self.key[1:])


@dataclass
class ScanResult:
    photos: int = 0
    checked: int = 0
    faces: int = 0


def available() -> bool:
    try:
        import cv2
    except ImportError:  # pragma: no cover
        return False
    return hasattr(cv2, "FaceDetectorYN") and DETECTOR.exists() and RECOGNIZER.exists()


def _buffer(path: Path) -> np.ndarray:
    """Model bytes, read once (by Python, so any install path works)."""
    with _buf_lock:
        if path.name not in _buffers:
            _buffers[path.name] = np.frombuffer(path.read_bytes(), np.uint8)
        return _buffers[path.name]


def _models():
    m = getattr(_local, "models", None)
    if m is None:
        import cv2
        empty = np.empty(0, np.uint8)
        det = cv2.FaceDetectorYN.create("onnx", _buffer(DETECTOR), empty, (320, 320), 0.6, 0.3, 5000)
        rec = cv2.FaceRecognizerSF.create("onnx", _buffer(RECOGNIZER), empty)
        m = _local.models = (det, rec)
    return m


# ----------------------------------------------------------------------------- detection
def _detect_at(det, bgr: np.ndarray, long_side: int) -> list[np.ndarray]:
    import cv2
    h, w = bgr.shape[:2]
    s = min(1.0, long_side / max(h, w))
    img = cv2.resize(bgr, (max(1, round(w * s)), max(1, round(h * s))), interpolation=cv2.INTER_AREA) if s < 1 else bgr
    det.setInputSize((img.shape[1], img.shape[0]))
    _, found = det.detect(img)
    if found is None:
        return []
    found = found.copy()
    found[:, :14] /= s
    return list(found)


def _nms(faces: list[np.ndarray]) -> list[np.ndarray]:
    keep: list[np.ndarray] = []
    for f in sorted(faces, key=lambda f: -float(f[14])):
        x, y, w, h = f[:4]
        if all(max(0, min(x + w, k[0] + k[2]) - max(x, k[0])) * max(0, min(y + h, k[1] + k[3]) - max(y, k[1]))
               <= 0.4 * min(w * h, k[2] * k[3]) for k in keep):
            keep.append(f)
    return keep


def _thumb(img: Image.Image, x: float, y: float, w: float, h: float) -> bytes:
    side = max(w, h) * 1.6
    cx, cy = x + w / 2, y + h / 2.2
    box = (max(0, round(cx - side / 2)), max(0, round(cy - side / 2)),
           min(img.width, round(cx + side / 2)), min(img.height, round(cy + side / 2)))
    crop = img.crop(box)
    crop.thumbnail((THUMB, THUMB), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    crop.save(buf, "JPEG", quality=85)
    return buf.getvalue()


def detect(path) -> list[Face]:
    """Faces in one photo: the photo is looked at twice (small faces need more pixels, large faces
    fewer), overlapping detections are merged, and each face gets its 128-number signature."""
    det, rec = _models()
    img, _, _ = media.open_oriented(path, LOAD_SIZE)
    if max(img.size) > LOAD_SIZE:
        img.thumbnail((LOAD_SIZE, LOAD_SIZE), Image.Resampling.LANCZOS)
    img = img.convert("RGB")
    bgr = np.ascontiguousarray(np.asarray(img)[:, :, ::-1])
    H, W = bgr.shape[:2]
    found = _detect_at(det, bgr, 640)
    if max(H, W) > 800:
        found += _detect_at(det, bgr, max(H, W))
    out = []
    for f in _nms(found):
        if float(f[14]) < MIN_SCORE or min(f[2], f[3]) < MIN_FACE:
            continue
        e = rec.feature(rec.alignCrop(bgr, f)).flatten().astype(np.float32)
        n = float(np.linalg.norm(e))
        if not n:
            continue
        x, y, w, h = (float(v) for v in f[:4])
        out.append(Face((max(0.0, x / W), max(0.0, y / H), w / W, h / H), float(f[14]), e / n, _thumb(img, x, y, w, h)))
    return out


# ----------------------------------------------------------------------------- scanning
def _live_ids(lib: Library) -> str:
    return "(SELECT id FROM files UNION SELECT file_id FROM parked_files UNION SELECT file_id FROM missing_files)"


def _cleanup(lib: Library) -> None:
    """Forget faces of files that are gone for good (files in Recovery keep theirs, for Undo)."""
    db = lib.db
    gone = [r[0] for r in db.execute(f"SELECT id FROM faces WHERE file_id NOT IN {_live_ids(lib)}")]
    with lib.transaction() as tx:
        tx.execute(f"DELETE FROM face_scans WHERE file_id NOT IN {_live_ids(lib)}")
        if gone:
            _delete_faces(lib, tx, gone)


def _delete_faces(lib: Library, tx, face_ids: list[int]) -> None:
    tx.executemany("DELETE FROM faces WHERE id=?", [(i,) for i in face_ids])
    tx.executemany("DELETE FROM face_rejects WHERE face_id=?", [(i,) for i in face_ids])
    t = lib.thumbs_db
    t.execute("BEGIN")
    t.executemany("DELETE FROM face_thumbs WHERE face_id=?", [(i,) for i in face_ids])
    t.execute("COMMIT")


def _store(lib: Library, batch: list[tuple[dict, list[Face]]]) -> None:
    thumbs = []
    with lib.transaction() as tx:
        for r, faces in batch:
            old = [x[0] for x in tx.execute("SELECT id FROM faces WHERE file_id=?", (r["id"],))]
            if old:
                _delete_faces(lib, tx, old)
            for f in faces:
                cur = tx.execute("INSERT INTO faces (file_id, x, y, w, h, score, emb) VALUES (?,?,?,?,?,?,?)",
                                 (r["id"], *f.box, f.score, f.emb.astype(np.float32).tobytes()))
                thumbs.append((cur.lastrowid, f.thumb))
            tx.execute("INSERT OR REPLACE INTO face_scans (file_id, size, mtime, faces) VALUES (?,?,?,?)",
                       (r["id"], r["size"], r["mtime"], len(faces)))
    if thumbs:
        t = lib.thumbs_db
        t.execute("BEGIN")
        t.executemany("INSERT OR REPLACE INTO face_thumbs (face_id, data) VALUES (?,?)", thumbs)
        t.execute("COMMIT")


def pending(lib: Library) -> int:
    """Photos not yet looked at (new or changed since the last scan)."""
    return lib.db.execute(
        "SELECT COUNT(*) FROM files f LEFT JOIN face_scans s ON s.file_id=f.id WHERE f.kind='image' AND "
        "f.error IS NULL AND f.size>0 AND (s.file_id IS NULL OR s.size!=f.size OR s.mtime!=f.mtime)").fetchone()[0]


def scan(lib: Library, progress: Optional[Progress] = None, chunk: int = 48) -> ScanResult:
    """Look for faces in every photo that is new or changed since the last scan, then group them."""
    import cv2
    progress = progress or Progress()
    _cleanup(lib)
    rows = [dict(r) for r in lib.readable_files("kind='image' AND error IS NULL AND size>0")]
    seen = {r[0]: (r[1], r[2]) for r in lib.db.execute("SELECT file_id, size, mtime FROM face_scans")}
    todo = [r for r in rows if seen.get(r["id"]) != (r["size"], r["mtime"])]
    res = ScanResult(photos=len(rows))

    def work(r):
        progress.check()
        lib.check_path(lib.abspath(r["rel_path"]))
        try:
            return r, detect(lib.abspath(r["rel_path"]))
        except Exception:
            return r, []          # unreadable: recorded as "no faces" until the file changes

    prev = cv2.getNumThreads()
    cv2.setNumThreads(1)          # parallel across photos instead of inside each model
    try:
        with activity.pool("Face detection", config.WORKERS), ThreadPoolExecutor(max_workers=config.WORKERS) as pool:
            for start in range(0, len(todo), chunk):
                part = list(pool.map(work, todo[start:start + chunk]))
                _store(lib, part)
                res.checked += len(part)
                res.faces += sum(len(f) for _, f in part)
                progress.update(res.checked, len(todo), f"Looking for faces… {res.checked:,} of {len(todo):,} photos")
    finally:
        cv2.setNumThreads(prev)
    progress.update(len(todo), len(todo), "Grouping faces into people…", force=True)
    cluster(lib)
    return res


# ----------------------------------------------------------------------------- grouping
def _unit(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.where(n == 0, 1, n)


def _blocked_best(E: np.ndarray, C: np.ndarray, block: int = 4096) -> tuple[np.ndarray, np.ndarray]:
    best = np.empty(len(E), np.int64)
    sim = np.empty(len(E), np.float32)
    for s in range(0, len(E), block):
        S = E[s:s + block] @ C.T
        best[s:s + block] = S.argmax(1)
        sim[s:s + block] = S[np.arange(len(S)), best[s:s + block]]
    return best, sim


def group_faces(E: np.ndarray, threshold: float = SAME_PERSON) -> np.ndarray:
    """Cluster unit vectors: leader pass (each face joins the closest group centre if similar enough),
    then centre-to-centre merging, then a reassignment pass. Returns labels 0..k-1, biggest group first."""
    n = len(E)
    if n == 0:
        return np.zeros(0, np.int64)
    sums = np.zeros((n, E.shape[1]), np.float32)
    cents = np.zeros((n, E.shape[1]), np.float32)
    labels = np.empty(n, np.int64)
    m = 0
    for i in range(n):
        if m:
            s = cents[:m] @ E[i]
            j = int(s.argmax())
            if s[j] >= threshold:
                sums[j] += E[i]
                cents[j] = _unit(sums[j])
                labels[i] = j
                continue
        sums[m] = cents[m] = E[i]
        labels[i] = m
        m += 1
    sums, cents = sums[:m], cents[:m]
    alive = np.ones(m, bool)
    while True:                                   # merge rounds: best pairs first, each group once per round
        idx = np.flatnonzero(alive)
        if len(idx) < 2:
            break
        S = cents[idx] @ cents[idx].T
        np.fill_diagonal(S, -1)
        a, b = np.nonzero(np.triu(S >= threshold, 1))
        if not len(a):
            break
        used = set()
        for k in np.argsort(-S[a, b]):
            x, y = int(idx[a[k]]), int(idx[b[k]])
            if x in used or y in used:
                continue
            used.update((x, y))
            sums[x] += sums[y]
            cents[x] = _unit(sums[x])
            alive[y] = False
            labels[labels == y] = x
    idx = np.flatnonzero(alive)
    best, sim = _blocked_best(E, cents[idx])
    new = np.where(sim >= threshold, idx[best], labels)
    uniq, inv, counts = np.unique(new, return_inverse=True, return_counts=True)
    order = np.argsort(-counts, kind="stable")
    rank = np.empty_like(order)
    rank[order] = np.arange(len(order))
    return rank[inv]


def cluster(lib: Library) -> None:
    """Assign faces to named people (unless the user said "not this person"), and group the rest."""
    rows = lib.db.execute("SELECT f.id, f.emb, f.person_id, f.confirmed, f.ignored FROM faces f "
                          "JOIN files ON files.id=f.file_id ORDER BY f.score DESC, f.id").fetchall()
    if not rows:
        return
    ids = np.array([r["id"] for r in rows])
    E = np.frombuffer(b"".join(r["emb"] for r in rows), np.float32).reshape(-1, DIM)
    person = np.array([r["person_id"] or 0 for r in rows])
    confirmed = np.array([bool(r["confirmed"]) for r in rows])
    ignored = np.array([bool(r["ignored"]) for r in rows])
    person[(person > 0) & ~confirmed] = 0                     # automatic matches are re-decided each time
    pids = np.unique(person[confirmed & (person > 0)])
    if len(pids):
        C = _unit(np.stack([E[confirmed & (person == p)].mean(0) for p in pids]))
        rejects = {(a, b) for a, b in lib.db.execute("SELECT face_id, person_id FROM face_rejects")}
        free = np.flatnonzero((person == 0) & ~ignored)
        for s in range(0, len(free), 4096):
            part = free[s:s + 4096]
            S = E[part] @ C.T
            for row, i in enumerate(part):
                for k in np.argsort(-S[row]):
                    if S[row, k] < SAME_PERSON:
                        break
                    if (int(ids[i]), int(pids[k])) not in rejects:
                        person[i] = pids[k]
                        break
    rest = np.flatnonzero((person == 0) & ~ignored)
    cl = np.zeros(len(ids), np.int64)
    cl[rest] = group_faces(E[rest]) + 1
    with lib.transaction() as tx:
        tx.executemany("UPDATE faces SET person_id=?, cluster=? WHERE id=?",
                       [(int(p) or None, int(c) or None, int(i)) for p, c, i in zip(person, cl, ids)])


# ----------------------------------------------------------------------------- browsing
def groups(lib: Library, min_photos: int = 2) -> list[Group]:
    """Named people (most photos first), then unnamed groups seen in at least ``min_photos`` photos."""
    db = lib.db
    out = [Group(f"p{r['id']}", r["name"], r["faces"] or 0, r["photos"] or 0, r["cover"] or 0) for r in db.execute(
        "SELECT p.id, p.name, COUNT(f.id) AS faces, COUNT(DISTINCT f.file_id) AS photos, "
        "(SELECT f2.id FROM faces f2 JOIN files ON files.id=f2.file_id WHERE f2.person_id=p.id "
        " ORDER BY f2.confirmed DESC, f2.score * f2.w DESC LIMIT 1) AS cover "
        "FROM people p LEFT JOIN faces f ON f.person_id=p.id AND f.file_id IN (SELECT id FROM files) "
        "GROUP BY p.id ORDER BY photos DESC, p.name")]
    for r in db.execute(
            "SELECT f.cluster, COUNT(*) AS faces, COUNT(DISTINCT f.file_id) AS photos, MAX(f.score * f.w) AS q, f.id "
            "FROM faces f JOIN files ON files.id=f.file_id WHERE f.person_id IS NULL AND f.ignored=0 AND "
            "f.cluster IS NOT NULL GROUP BY f.cluster HAVING photos >= ? ORDER BY photos DESC, f.cluster",
            (min_photos,)):
        out.append(Group(f"c{r['cluster']}", None, r["faces"], r["photos"], r["id"]))
    return out


def _where(key: str) -> tuple[str, tuple]:
    if key.startswith("p"):
        return "f.person_id=?", (int(key[1:]),)
    return "f.person_id IS NULL AND f.ignored=0 AND f.cluster=?", (int(key[1:]),)


def faces_of(lib: Library, key: str) -> list[dict]:
    w, p = _where(key)
    return [dict(r) for r in lib.db.execute(
        f"SELECT f.id AS face_id, f.x, f.y, f.w, f.h, f.score, f.confirmed, files.* FROM faces f "
        f"JOIN files ON files.id=f.file_id WHERE {w} ORDER BY COALESCE(files.taken_at, ''), files.rel_path", p)]


def photos_of(lib: Library, key: str) -> list[dict]:
    """Every photo the person (or group) appears in, oldest first."""
    seen, out = set(), []
    for r in faces_of(lib, key):
        if r["id"] not in seen:
            seen.add(r["id"])
            out.append(r)
    return out


def faces_in(lib: Library, file_id: int) -> list[dict]:
    return [dict(r) for r in lib.db.execute(
        "SELECT f.id AS face_id, f.x, f.y, f.w, f.h, f.score, f.person_id, f.cluster, p.name FROM faces f "
        "LEFT JOIN people p ON p.id=f.person_id WHERE f.file_id=? ORDER BY f.x", (file_id,))]


def face_thumb(lib: Library, face_id: int) -> Optional[bytes]:
    r = lib.thumbs_db.execute("SELECT data FROM face_thumbs WHERE face_id=?", (face_id,)).fetchone()
    return r[0] if r else None


def similar(lib: Library, face_id: int, threshold: float = SAME_PERSON, limit: int = 2000) -> list[dict]:
    """Photos with a face like this one, most alike first (each photo once, with its best match)."""
    me = lib.db.execute("SELECT emb FROM faces WHERE id=?", (face_id,)).fetchone()
    if me is None:
        return []
    q = np.frombuffer(me[0], np.float32)
    rows = lib.db.execute("SELECT f.id, f.file_id, f.emb FROM faces f JOIN files ON files.id=f.file_id").fetchall()
    if not rows:
        return []
    E = np.frombuffer(b"".join(r["emb"] for r in rows), np.float32).reshape(-1, DIM)
    sims = E @ q
    best: dict[int, tuple[float, int]] = {}
    for r, s in zip(rows, sims):
        if s >= threshold and s > best.get(r["file_id"], (-1.0, 0))[0]:
            best[r["file_id"]] = (float(s), r["id"])
    out = []
    for fid, (s, face) in sorted(best.items(), key=lambda kv: -kv[1][0])[:limit]:
        row = lib.file(fid)
        if row is not None:
            out.append({**dict(row), "similarity": s, "face_id": face})
    return out


def names_by_file(lib: Library) -> dict[int, list[str]]:
    out: dict[int, list[str]] = {}
    for fid, name in lib.db.execute("SELECT DISTINCT f.file_id, p.name FROM faces f JOIN people p ON p.id=f.person_id"):
        out.setdefault(fid, []).append(name)
    return out


def status(lib: Library) -> dict:
    db = lib.db
    return {"photos": db.execute("SELECT COUNT(*) FROM files WHERE kind='image' AND error IS NULL AND size>0").fetchone()[0],
            "pending": pending(lib),
            "faces": db.execute("SELECT COUNT(*) FROM faces WHERE file_id IN (SELECT id FROM files)").fetchone()[0],
            "people": db.execute("SELECT COUNT(*) FROM people").fetchone()[0]}


# ----------------------------------------------------------------------------- the user's corrections
def name(lib: Library, key: str, new_name: str) -> int:
    """Name a group (or rename a person). Using an existing person's name joins the two."""
    new_name = " ".join(new_name.split())
    if not new_name:
        raise ValueError("Type a name.")
    db = lib.db
    other = db.execute("SELECT id FROM people WHERE lower(name)=lower(?)", (new_name,)).fetchone()
    if key.startswith("p"):
        pid = int(key[1:])
        if other and other[0] != pid:
            merge(lib, key, other[0])
            return other[0]
        db.execute("UPDATE people SET name=? WHERE id=?", (new_name, pid))
        return pid
    with lib.transaction() as tx:
        pid = other[0] if other else tx.execute("INSERT INTO people (name, created_at) VALUES (?,?)",
                                                (new_name, datetime.now().isoformat(sep=" ", timespec="seconds"))).lastrowid
        tx.execute("UPDATE faces SET person_id=?, confirmed=1, cluster=NULL WHERE person_id IS NULL AND ignored=0 "
                   "AND cluster=?", (pid, int(key[1:])))
    return pid


def merge(lib: Library, key: str, person_id: int) -> None:
    """Move every face of ``key`` (person or group) to ``person_id``."""
    w, p = _where(key)
    with lib.transaction() as tx:
        tx.execute(f"UPDATE faces SET person_id=?, confirmed=1, cluster=NULL WHERE id IN "
                   f"(SELECT f.id FROM faces f WHERE {w})", (person_id, *p))
        if key.startswith("p") and int(key[1:]) != person_id:
            tx.execute("DELETE FROM face_rejects WHERE person_id=?", (int(key[1:]),))
            tx.execute("DELETE FROM people WHERE id=?", (int(key[1:]),))


def assign(lib: Library, face_ids: list[int], person_id: int) -> None:
    with lib.transaction() as tx:
        for f in face_ids:
            tx.execute("UPDATE faces SET person_id=?, confirmed=1, cluster=NULL, ignored=0 WHERE id=?", (person_id, f))
            tx.execute("DELETE FROM face_rejects WHERE face_id=? AND person_id=?", (f, person_id))


def not_this_person(lib: Library, face_ids: list[int]) -> None:
    """Take faces out of their person or group; they are never matched to that person again."""
    with lib.transaction() as tx:
        for f in face_ids:
            r = tx.execute("SELECT person_id FROM faces WHERE id=?", (f,)).fetchone()
            if r and r[0]:
                tx.execute("INSERT OR IGNORE INTO face_rejects (face_id, person_id) VALUES (?,?)", (f, r[0]))
            tx.execute("UPDATE faces SET person_id=NULL, confirmed=0, cluster=NULL WHERE id=?", (f,))


def hide(lib: Library, key: str) -> None:
    """Hide an unnamed group (strangers in the background, statues…)."""
    w, p = _where(key)
    lib.db.execute(f"UPDATE faces SET ignored=1, cluster=NULL WHERE id IN (SELECT f.id FROM faces f WHERE {w})", p)


def unhide_all(lib: Library) -> int:
    return lib.db.execute("UPDATE faces SET ignored=0 WHERE ignored=1").rowcount


def forget_person(lib: Library, person_id: int) -> None:
    """Remove a name; the faces become an unnamed group again at the next grouping."""
    with lib.transaction() as tx:
        tx.execute("UPDATE faces SET person_id=NULL, confirmed=0 WHERE person_id=?", (person_id,))
        tx.execute("DELETE FROM face_rejects WHERE person_id=?", (person_id,))
        tx.execute("DELETE FROM people WHERE id=?", (person_id,))


def forget_all(lib: Library) -> None:
    """Delete every face, signature, name and correction from this library's catalogue."""
    with lib.transaction() as tx:
        for t in ("faces", "face_scans", "face_rejects", "people"):
            tx.execute(f"DELETE FROM {t}")
    t = lib.thumbs_db
    t.execute("DELETE FROM face_thumbs")
