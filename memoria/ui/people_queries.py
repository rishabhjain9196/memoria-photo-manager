"""Bounded catalogue pages for the People UI; no original files are read."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage

from ..engine import faces

GROUP_PAGE = 60
PHOTO_PAGE = 200
FACE_PAGE = 80


def _where(key):
    if key.startswith("p"):
        return "f.person_id=?", (int(key[1:]),)
    return "f.person_id IS NULL AND f.ignored=0 AND f.cluster=?", (int(key[1:]),)


def _thumb(lib, face_id):
    data = faces.face_thumb(lib, face_id) if face_id else None
    return QImage.fromData(data).scaled(72, 72, Qt.AspectRatioMode.KeepAspectRatio,
                                        Qt.TransformationMode.SmoothTransformation) if data else QImage()


def group_page(lib, minimum, search, offset):
    query = """
        WITH groups AS (
            SELECT 'p' || p.id AS key, p.name, COUNT(f.id) AS faces,
                   COUNT(DISTINCT files.id) AS photos, MAX(f.id) AS cover, 0 AS unnamed
            FROM people p LEFT JOIN faces f ON f.person_id=p.id AND f.file_id IN (SELECT id FROM files)
            LEFT JOIN files ON files.id=f.file_id
            GROUP BY p.id
            UNION ALL
            SELECT 'c' || f.cluster, NULL, COUNT(*), COUNT(DISTINCT f.file_id), MAX(f.id), 1
            FROM faces f JOIN files ON files.id=f.file_id
            WHERE f.person_id IS NULL AND f.ignored=0 AND f.cluster IS NOT NULL
            GROUP BY f.cluster HAVING COUNT(DISTINCT f.file_id)>=?
        ) """
    condition = "WHERE instr(lower(COALESCE(name, 'Unnamed person')), lower(?))>0"
    args = (minimum, search.strip())
    total = lib.db.execute(query + "SELECT COUNT(*) FROM groups " + condition, args).fetchone()[0]
    offset = min(offset, max(0, ((total - 1) // GROUP_PAGE) * GROUP_PAGE))
    rows = lib.db.execute(query + "SELECT * FROM groups " + condition +
                          " ORDER BY unnamed, photos DESC, name, key LIMIT ? OFFSET ?",
                          (*args, GROUP_PAGE, offset)).fetchall()
    groups = [faces.Group(row["key"], row["name"], row["faces"], row["photos"], row["cover"] or 0)
              for row in rows]
    return {"groups": groups, "covers": {g.cover: _thumb(lib, g.cover) for g in groups},
            "total": total, "offset": offset, "status": faces.status(lib)}


def group_contents(lib, key, photo_offset, face_offset):
    where, args = _where(key)
    photos = [dict(row) for row in lib.db.execute(
        f"SELECT DISTINCT files.* FROM files JOIN faces f ON files.id=f.file_id WHERE {where} "
        "ORDER BY COALESCE(files.taken_at,''), files.rel_path LIMIT ? OFFSET ?",
        (*args, PHOTO_PAGE, photo_offset))]
    selected_faces = [dict(row) for row in lib.db.execute(
        f"SELECT f.id AS face_id, files.rel_path FROM faces f JOIN files ON files.id=f.file_id WHERE {where} "
        "ORDER BY COALESCE(files.taken_at,''), files.rel_path, f.id LIMIT ? OFFSET ?",
        (*args, FACE_PAGE, face_offset))]
    return {"photos": photos, "faces": selected_faces,
            "thumbs": {row["face_id"]: _thumb(lib, row["face_id"]) for row in selected_faces}}


def group_ids(lib, key):
    where, args = _where(key)
    return [row[0] for row in lib.db.execute(
        f"SELECT DISTINCT f.file_id FROM faces f JOIN files ON files.id=f.file_id WHERE {where}", args)]


def similar_page(lib, face_id, limit=2000):
    """Keep only the best bounded set while streaming embeddings in small batches."""
    import heapq
    import numpy as np

    source = lib.db.execute("SELECT emb FROM faces WHERE id=?", (face_id,)).fetchone()
    if source is None:
        return []
    query = np.frombuffer(source[0], np.float32)
    best = {}
    cursor = lib.db.execute("SELECT f.file_id,f.id,f.emb FROM faces f JOIN files ON files.id=f.file_id")
    while batch := cursor.fetchmany(512):
        for row in batch:
            similarity = float(np.frombuffer(row["emb"], np.float32) @ query)
            if similarity >= faces.SAME_PERSON and similarity > best.get(row["file_id"], (-1, 0))[0]:
                best[row["file_id"]] = (similarity, row["id"])
        if len(best) > limit:
            best = dict(heapq.nlargest(limit, best.items(), key=lambda item: item[1][0]))
    return [{**dict(lib.file(file_id)), "similarity": score, "face_id": face}
            for file_id, (score, face) in sorted(best.items(), key=lambda item: -item[1][0])[:limit]]
