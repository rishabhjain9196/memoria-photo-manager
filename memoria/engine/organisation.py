"""User-authored organisation, separate from derived analysis and original media."""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterable

from .db import Library

REVIEWS = ("unreviewed", "pick", "reject")
FIELDS = {"rating", "favorite", "review", "tags", "albums"}


@contextmanager
def _transaction(lib):
    # Snapshots are also applied inside the operation journal's transaction.
    lib.db.execute("SAVEPOINT organisation_edit")
    try:
        yield lib.db
        lib.db.execute("RELEASE organisation_edit")
    except BaseException:
        lib.db.execute("ROLLBACK TO organisation_edit")
        lib.db.execute("RELEASE organisation_edit")
        raise


def _id(value):
    if type(value) is not int or not 0 < value < 2**63:
        raise ValueError("Choose a valid catalogue ID.")
    return value


def require_file(lib: Library, file_id: int, *, live: bool = False) -> None:
    _id(file_id)
    sql = "SELECT id FROM files WHERE id=?"
    params = [file_id]
    if not live:
        sql += " UNION ALL SELECT file_id FROM parked_files WHERE file_id=?"
        sql += " UNION ALL SELECT file_id FROM missing_files WHERE file_id=?"
        params += [file_id, file_id]
    if not lib.db.execute(sql, params).fetchone():
        raise ValueError("That file is no longer in the catalogue.")


def tag_names(values: Iterable[str]) -> list[str]:
    if not isinstance(values, (list, tuple, set)):
        raise ValueError("Tags must be a list of names.")
    result = {}
    for value in values:
        if not isinstance(value, str) or any(ord(c) < 32 for c in value):
            raise ValueError("Tags must be text without control characters.")
        name = " ".join(value.split())
        if not name or len(name) > 128:
            raise ValueError("Each tag needs 1–128 characters.")
        result.setdefault(name.lower(), name)
    if len(result) > 200:
        raise ValueError("Choose at most 200 tags per file.")
    return sorted(result.values(), key=str.lower)


def _validated(lib, value):
    if not isinstance(value, dict) or set(value) != FIELDS:
        raise ValueError("Organisation state must contain rating, favorite, review, tags and albums.")
    rating, favorite, review = value["rating"], value["favorite"], value["review"]
    if type(rating) is not int or not 0 <= rating <= 5:
        raise ValueError("Rating must be an integer from 0 to 5 (0 means unrated).")
    if type(favorite) not in (int, bool) or favorite not in (0, 1):
        raise ValueError("Favourite must be true or false.")
    if review not in REVIEWS:
        raise ValueError("Review must be unreviewed, pick or reject.")
    if not isinstance(value["albums"], (list, tuple, set)):
        raise ValueError("Albums must be a list of static album IDs.")
    ids = sorted({_id(aid) for aid in value["albums"]})
    for aid in ids:
        if not lib.db.execute("SELECT 1 FROM albums WHERE id=? AND rule_json IS NULL", (aid,)).fetchone():
            raise ValueError("Choose an existing static album; smart albums are query results.")
    return {"rating": rating, "favorite": bool(favorite), "review": review,
            "tags": tag_names(value["tags"]), "albums": ids}


def state(lib: Library, file_id: int) -> dict:
    """JSON-compatible snapshot for live, missing or parked IDs. No biometric/health data."""
    require_file(lib, file_id)
    row = lib.db.execute("SELECT rating,favorite,review FROM file_metadata WHERE file_id=?", (file_id,)).fetchone()
    value = dict(row) if row else {"rating": 0, "favorite": False, "review": "unreviewed"}
    value["favorite"] = bool(value["favorite"])
    value["tags"] = [r[0] for r in lib.db.execute(
        "SELECT t.name FROM tags t JOIN file_tags x ON x.tag_id=t.id WHERE x.file_id=? "
        "ORDER BY t.name COLLATE NOCASE", (file_id,))]
    value["albums"] = [r[0] for r in lib.db.execute(
        "SELECT a.id FROM albums a JOIN album_items i ON i.album_id=a.id "
        "WHERE i.file_id=? AND a.rule_json IS NULL ORDER BY a.id", (file_id,))]
    return value


def merged_state(lib: Library, source_id: int, keeper_id: int) -> tuple[dict, dict]:
    """Pure merge: keeper's explicit choices win; unset values and memberships are filled."""
    source, before = state(lib, source_id), state(lib, keeper_id)
    after = {**before, "rating": before["rating"] or source["rating"],
             "favorite": before["favorite"] or source["favorite"],
             "review": source["review"] if before["review"] == "unreviewed" else before["review"],
             "tags": tag_names(before["tags"] + source["tags"]),
             "albums": sorted(set(before["albums"]) | set(source["albums"]))}
    return before, after


def _write(lib, file_id, value):
    db = lib.db
    db.execute("INSERT INTO file_metadata(file_id,rating,favorite,review) VALUES (?,?,?,?) "
               "ON CONFLICT(file_id) DO UPDATE SET rating=excluded.rating,favorite=excluded.favorite,"
               "review=excluded.review", (file_id, value["rating"], int(value["favorite"]), value["review"]))
    db.execute("DELETE FROM file_tags WHERE file_id=?", (file_id,))
    for name in value["tags"]:
        db.execute("INSERT OR IGNORE INTO tags(name) VALUES (?)", (name,))
        db.execute("INSERT INTO file_tags(file_id,tag_id) SELECT ?,id FROM tags WHERE name=? COLLATE NOCASE",
                   (file_id, name))
    current = {r[0] for r in db.execute("SELECT album_id FROM album_items WHERE file_id=?", (file_id,))}
    desired = set(value["albums"])
    db.executemany("DELETE FROM album_items WHERE file_id=? AND album_id=?",
                   [(file_id, aid) for aid in current - desired])
    db.executemany("UPDATE albums SET cover_id=NULL WHERE id=? AND cover_id=?",
                   [(aid, file_id) for aid in current - desired])
    for aid in desired - current:
        db.execute("INSERT INTO album_items(album_id,file_id,pos) "
                   "SELECT ?,?,COALESCE(MAX(pos),-1)+1 FROM album_items WHERE album_id=?", (aid, file_id, aid))


def set_state(lib: Library, file_id: int, value: dict) -> None:
    """Atomically replace only organisation fields; retained missing/parked IDs are valid."""
    with _transaction(lib):
        require_file(lib, file_id)
        _write(lib, file_id, _validated(lib, value))


def edit(lib: Library, file_ids: Iterable[int], *, rating=None, favorite=None, review=None,
         add_tags=(), remove_tags=()) -> int:
    """Atomic selection-scoped edit of live catalogue rows. None leaves a field unchanged."""
    ids = list(dict.fromkeys(file_ids))
    additions, removals = tag_names(add_tags), {t.lower() for t in tag_names(remove_tags)}
    with _transaction(lib):
        for file_id in ids:
            require_file(lib, file_id, live=True)
            value = state(lib, file_id)
            for key, update in (("rating", rating), ("favorite", favorite), ("review", review)):
                if update is not None:
                    value[key] = update
            value["tags"] = [t for t in value["tags"] if t.lower() not in removals] + additions
            _write(lib, file_id, _validated(lib, value))
    return len(ids)


def cleanup(lib: Library) -> None:
    """Forget links only when an ID is absent from both live and retained records."""
    with _transaction(lib):
        for table in ("file_tags", "file_metadata", "album_items"):
            lib.db.execute(f"DELETE FROM {table} WHERE file_id NOT IN "
                           "(SELECT id FROM files UNION SELECT file_id FROM parked_files "
                           "UNION SELECT file_id FROM missing_files)")
