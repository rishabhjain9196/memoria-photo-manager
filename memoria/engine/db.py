"""SQLite catalogue for one library. One connection per thread (WAL mode)."""
from __future__ import annotations

import json
import os
import sqlite3
import threading
from pathlib import Path
from typing import Iterable, Optional

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS files (
    id            INTEGER PRIMARY KEY,
    rel_path      TEXT NOT NULL UNIQUE COLLATE NOCASE,
    folder        TEXT NOT NULL,
    name          TEXT NOT NULL,
    ext           TEXT NOT NULL,
    kind          TEXT NOT NULL,
    size          INTEGER NOT NULL,
    mtime         REAL NOT NULL,
    qhash         TEXT,
    chash         TEXT,
    analyzed      INTEGER NOT NULL DEFAULT 0,
    error         TEXT,
    width         INTEGER,
    height        INTEGER,
    taken_at      TEXT,
    date_source   TEXT,
    camera        TEXT,
    lat           REAL,
    lon           REAL,
    duration      REAL,
    dhash         INTEGER,
    sharpness     REAL,
    brightness    REAL,
    contrast      REAL,
    clipped       REAL,
    faces         INTEGER,
    baseline_hash TEXT,
    baseline_size INTEGER,
    baseline_mtime REAL,
    checked_at    TEXT
);
CREATE INDEX IF NOT EXISTS ix_files_size ON files(size);
CREATE INDEX IF NOT EXISTS ix_files_taken ON files(taken_at);
CREATE INDEX IF NOT EXISTS ix_files_kind ON files(kind);

CREATE TABLE IF NOT EXISTS batches (
    id          TEXT PRIMARY KEY,
    created_at  TEXT NOT NULL,
    kind        TEXT NOT NULL,
    title       TEXT NOT NULL,
    status      TEXT NOT NULL,
    files       INTEGER NOT NULL DEFAULT 0,
    bytes       INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS operations (
    id        INTEGER PRIMARY KEY,
    batch_id  TEXT NOT NULL REFERENCES batches(id),
    seq       INTEGER NOT NULL,
    op        TEXT NOT NULL,
    src       TEXT NOT NULL,
    dst       TEXT,
    size      INTEGER,
    hash      TEXT,
    reason    TEXT,
    status    TEXT NOT NULL,
    error     TEXT
);
CREATE INDEX IF NOT EXISTS ix_ops_batch ON operations(batch_id, seq);
"""

# Numbered schema upgrades applied after the frozen v1 schema above. Never edit a released step;
# append a new one. ``PRAGMA user_version`` records the last step applied.
MIGRATIONS: dict[int, list[str]] = {
    2: [
        # Catalogue rows of files moved to Recovery, kept so Undo restores fingerprints/analysis.
        "CREATE TABLE IF NOT EXISTS parked_files (op_id INTEGER PRIMARY KEY, file_id INTEGER NOT NULL, "
        "data TEXT NOT NULL)",
    ],
    3: [
        # People: faces found in photos (position, 128-number signature), named people and the user's
        # corrections. Albums: named sets of library files. Neither changes any file.
        "CREATE TABLE IF NOT EXISTS people (id INTEGER PRIMARY KEY, name TEXT NOT NULL, created_at TEXT NOT NULL)",
        "CREATE TABLE IF NOT EXISTS faces (id INTEGER PRIMARY KEY, file_id INTEGER NOT NULL, x REAL NOT NULL, "
        "y REAL NOT NULL, w REAL NOT NULL, h REAL NOT NULL, score REAL NOT NULL, emb BLOB NOT NULL, person_id INTEGER, "
        "confirmed INTEGER NOT NULL DEFAULT 0, cluster INTEGER, ignored INTEGER NOT NULL DEFAULT 0)",
        "CREATE INDEX IF NOT EXISTS ix_faces_file ON faces(file_id)",
        "CREATE INDEX IF NOT EXISTS ix_faces_person ON faces(person_id)",
        "CREATE TABLE IF NOT EXISTS face_scans (file_id INTEGER PRIMARY KEY, size INTEGER NOT NULL, "
        "mtime REAL NOT NULL, faces INTEGER NOT NULL)",
        "CREATE TABLE IF NOT EXISTS face_rejects (face_id INTEGER NOT NULL, person_id INTEGER NOT NULL, "
        "PRIMARY KEY (face_id, person_id))",
        "CREATE TABLE IF NOT EXISTS albums (id INTEGER PRIMARY KEY, name TEXT NOT NULL, kind TEXT NOT NULL, "
        "created_at TEXT NOT NULL, cover_id INTEGER)",
        "CREATE TABLE IF NOT EXISTS album_items (album_id INTEGER NOT NULL, file_id INTEGER NOT NULL, "
        "pos INTEGER NOT NULL, PRIMARY KEY (album_id, file_id))",
    ],
    4: [
        # Rebuild from the frozen schema, retaining every column and existing identity.
        SCHEMA.split("CREATE INDEX", 1)[0].replace("IF NOT EXISTS files", "files_v4").replace(
            "INTEGER PRIMARY KEY,", "INTEGER PRIMARY KEY AUTOINCREMENT,", 1),
        "INSERT INTO files_v4 SELECT * FROM files",
        "DROP TABLE files",
        "ALTER TABLE files_v4 RENAME TO files",
        "CREATE INDEX ix_files_size ON files(size)",
        "CREATE INDEX ix_files_taken ON files(taken_at)",
        "CREATE INDEX ix_files_kind ON files(kind)",
        "UPDATE sqlite_sequence SET seq=MAX(seq, COALESCE((SELECT MAX(file_id) FROM "
        "(SELECT file_id FROM parked_files UNION ALL SELECT file_id FROM album_items "
        "UNION ALL SELECT file_id FROM faces UNION ALL SELECT file_id FROM face_scans)),0)) WHERE name='files'",
        "CREATE TABLE IF NOT EXISTS missing_files (file_id INTEGER PRIMARY KEY, rel_path TEXT NOT NULL UNIQUE COLLATE NOCASE, "
        "data TEXT NOT NULL)",
    ],
    5: [
        "CREATE TABLE IF NOT EXISTS storage_reset (id INTEGER PRIMARY KEY CHECK(id=1), "
        "options TEXT NOT NULL, phase TEXT NOT NULL, forgotten TEXT NOT NULL)",
    ],
    6: [
        "ALTER TABLE files ADD COLUMN metadata_version INTEGER DEFAULT 0",
        "ALTER TABLE files ADD COLUMN fps REAL",
        "ALTER TABLE files ADD COLUMN video_codec TEXT",
        "ALTER TABLE files ADD COLUMN audio_codec TEXT",
        "ALTER TABLE files ADD COLUMN iso INTEGER",
        "ALTER TABLE files ADD COLUMN aperture REAL",
        "ALTER TABLE files ADD COLUMN exposure_seconds REAL",
        "ALTER TABLE files ADD COLUMN focal_length_mm REAL",
        "ALTER TABLE files ADD COLUMN lens TEXT",
    ],
}
SCHEMA_VERSION = max(MIGRATIONS)
METADATA_VERSION = 1

THUMB_SCHEMA = """CREATE TABLE IF NOT EXISTS thumbs (file_id INTEGER PRIMARY KEY, data BLOB NOT NULL);
CREATE TABLE IF NOT EXISTS face_thumbs (face_id INTEGER PRIMARY KEY, data BLOB NOT NULL);"""

# Columns derived from file content; cleared whenever a file's size or mtime changes.
DERIVED = ("qhash", "chash", "analyzed", "error", "width", "height", "taken_at", "date_source",
           "camera", "lat", "lon", "duration", "dhash", "sharpness", "brightness", "contrast",
           "clipped", "faces", "metadata_version", "fps", "video_codec", "audio_codec",
           "iso", "aperture", "exposure_seconds", "focal_length_mm", "lens")


def _connect(path: Path, durable: bool = False) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path), timeout=30, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=FULL" if durable else "PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA temp_store=MEMORY")
    conn.execute("PRAGMA cache_size=-32000")
    return conn


class LibraryInUse(RuntimeError):
    """Another Memoria window or process already has this library open."""


class LibraryUnavailable(RuntimeError):
    """The library folder can't be read right now (drive unplugged, network down…)."""


class LibraryTooNew(RuntimeError):
    """The catalogue was created by a newer version of Memoria."""


_LOCKS: dict[str, list] = {}
_LOCKS_GUARD = threading.Lock()


def _acquire_lock(path: Path) -> str:
    """Exclusive cross-process lock (re-entrant within this process)."""
    key = str(path).lower()
    with _LOCKS_GUARD:
        if key in _LOCKS:
            _LOCKS[key][1] += 1
            return key
        fd = os.open(str(path), os.O_RDWR | os.O_CREAT)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            else:  # pragma: no cover
                import fcntl
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            os.close(fd)
            raise LibraryInUse("This library is already open in another Memoria window.")
        _LOCKS[key] = [fd, 1]
        return key


def _release_lock(key: str) -> None:
    with _LOCKS_GUARD:
        entry = _LOCKS.get(key)
        if not entry:
            return
        entry[1] -= 1
        if entry[1] > 0:
            return
        fd = entry[0]
        try:
            if os.name == "nt":
                import msvcrt
                os.lseek(fd, 0, 0)
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        except OSError:
            pass
        os.close(fd)
        del _LOCKS[key]


class Library:
    """A folder of photos plus its ``.memoria`` catalogue."""

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        if not self.root.is_dir():
            raise NotADirectoryError(str(self.root))
        config.ensure_app_dir(self.root)
        self.db_path = config.app_dir(self.root) / config.DB_NAME
        self.thumbs_path = config.app_dir(self.root) / config.THUMBS_DB_NAME
        self._local = threading.local()
        self._lock_key: Optional[str] = _acquire_lock(config.app_dir(self.root) / "lock")
        try:
            self._migrate()
            self.thumbs_db.executescript(THUMB_SCHEMA)
        except BaseException:
            self.close()
            raise

    def _migrate(self) -> None:
        db = self.db
        version = db.execute("PRAGMA user_version").fetchone()[0]
        if version > SCHEMA_VERSION:
            raise LibraryTooNew("This library was last used by a newer version of Memoria. Please update Memoria.")
        if version < 1:
            db.executescript(SCHEMA)
            version = 1
        for step in range(version + 1, SCHEMA_VERSION + 1):
            db.execute("BEGIN IMMEDIATE")
            try:
                for sql in MIGRATIONS[step]:
                    db.execute(sql)
                db.execute(f"PRAGMA user_version={step}")
                db.execute("COMMIT")
            except BaseException:
                db.execute("ROLLBACK")
                raise

    # connections -----------------------------------------------------------------------
    @property
    def db(self) -> sqlite3.Connection:
        conn = getattr(self._local, "db", None)
        if conn is None:
            conn = self._local.db = _connect(self.db_path, durable=True)
        return conn

    @property
    def thumbs_db(self) -> sqlite3.Connection:
        conn = getattr(self._local, "thumbs", None)
        if conn is None:
            conn = self._local.thumbs = _connect(self.thumbs_path)
        return conn

    def close_thread(self) -> None:
        """Close the calling thread's connections only (the library stays open and locked)."""
        for name in ("db", "thumbs"):
            conn = getattr(self._local, name, None)
            if conn is not None:
                conn.close()
                setattr(self._local, name, None)

    def close(self) -> None:
        """Close this thread's connections and release the library lock."""
        self.close_thread()
        if self._lock_key is not None:
            _release_lock(self._lock_key)
            self._lock_key = None

    # paths -----------------------------------------------------------------------------
    def abspath(self, rel_path: str) -> Path:
        return self.root / rel_path

    def rel(self, path: str | Path) -> str:
        return str(Path(path).resolve().relative_to(self.root))

    @property
    def recovery(self) -> Path:
        return config.recovery_dir(self.root)

    # queries ---------------------------------------------------------------------------
    def files(self, where: str = "1", params: Iterable = (), order: str = "rel_path") -> list[sqlite3.Row]:
        return self.db.execute(f"SELECT * FROM files WHERE {where} ORDER BY {order}", tuple(params)).fetchall()

    def file(self, file_id: int) -> Optional[sqlite3.Row]:
        return self.db.execute("SELECT * FROM files WHERE id=?", (file_id,)).fetchone()

    def file_by_rel(self, rel_path: str) -> Optional[sqlite3.Row]:
        return self.db.execute("SELECT * FROM files WHERE rel_path=?", (rel_path,)).fetchone()

    def set_hashes(self, updates: list[tuple[int, Optional[str], Optional[str]]]) -> None:
        """updates: (file_id, qhash, chash); None values leave the column unchanged."""
        with self.transaction():
            self.db.executemany(
                "UPDATE files SET qhash=COALESCE(?, qhash), chash=COALESCE(?, chash) WHERE id=?",
                [(q, c, i) for i, q, c in updates])

    def thumbnail(self, file_id: int) -> Optional[bytes]:
        row = self.thumbs_db.execute("SELECT data FROM thumbs WHERE file_id=?", (file_id,)).fetchone()
        return row[0] if row else None

    def stats(self) -> dict:
        r = self.db.execute("""
            SELECT COUNT(*) AS files,
                   COALESCE(SUM(size),0) AS bytes,
                   SUM(kind='image') AS images,
                   SUM(kind='video') AS videos,
                   SUM(kind='other') AS others,
                   SUM(kind!='other' AND (analyzed=0 OR COALESCE(metadata_version,0)<?)) AS pending,
                   SUM(error IS NOT NULL) AS errors,
                   MIN(CASE WHEN kind!='other' AND error IS NULL THEN taken_at END) AS first,
                   MAX(CASE WHEN kind!='other' AND error IS NULL THEN taken_at END) AS last
            FROM files""", (METADATA_VERSION,)).fetchone()
        return {k: (r[k] or 0) if k not in ("first", "last") else r[k] for k in r.keys()}

    def remove_rows(self, file_ids: list[int]) -> None:
        if not file_ids:
            return
        with self.transaction():
            self.db.executemany("DELETE FROM files WHERE id=?", [(i,) for i in file_ids])
        tdb = self.thumbs_db
        tdb.execute("BEGIN")
        tdb.executemany("DELETE FROM thumbs WHERE file_id=?", [(i,) for i in file_ids])
        tdb.execute("COMMIT")

    def mark_missing(self, file_ids: list[int]) -> None:
        """Retain identities and fingerprints of files absent from a successful scan."""
        with self.transaction() as db:
            for fid in file_ids:
                row = db.execute("SELECT * FROM files WHERE id=?", (fid,)).fetchone()
                if row is not None:
                    db.execute("INSERT OR REPLACE INTO missing_files VALUES (?,?,?)",
                               (fid, row["rel_path"], json.dumps(dict(row))))
                    db.execute("DELETE FROM files WHERE id=?", (fid,))

    def missing(self) -> list[dict]:
        return [json.loads(r[0]) for r in self.db.execute("SELECT data FROM missing_files ORDER BY rel_path")]

    # parking: rows of files in Recovery ------------------------------------------------
    def park_rows(self, pairs: list[tuple[int, int]]) -> None:
        """Move catalogue rows (op_id, file_id) out of ``files`` but keep them (and thumbnails)."""
        if not pairs:
            return
        with self.transaction() as db:
            for op_id, fid in pairs:
                row = db.execute("SELECT * FROM files WHERE id=?", (fid,)).fetchone()
                if row is None:
                    continue
                db.execute("INSERT OR REPLACE INTO parked_files (op_id, file_id, data) VALUES (?,?,?)",
                           (op_id, fid, json.dumps(dict(row))))
                db.execute("DELETE FROM files WHERE id=?", (fid,))

    def restore_parked(self, op_id: int, rel_path: str) -> bool:
        """Put a parked row back at ``rel_path``. Returns False if there is nothing to restore."""
        db = self.db
        rec = db.execute("SELECT * FROM parked_files WHERE op_id=?", (op_id,)).fetchone()
        if rec is None:
            return False
        data = json.loads(rec["data"])
        folder, name = os.path.split(rel_path)
        data.update(rel_path=rel_path, folder=folder, name=name)
        with self.transaction() as tx:
            if tx.execute("SELECT 1 FROM files WHERE rel_path=?", (rel_path,)).fetchone():
                tx.execute("DELETE FROM parked_files WHERE op_id=?", (op_id,))
                return False
            old_id = data["id"]
            if tx.execute("SELECT 1 FROM files WHERE id=?", (old_id,)).fetchone():
                data.pop("id")
            cols_known = {r[1] for r in tx.execute("PRAGMA table_info(files)")}
            cols = [c for c in data if c in cols_known]
            cur = tx.execute(f"INSERT INTO files ({', '.join(cols)}) VALUES ({', '.join('?' * len(cols))})",
                             [data[c] for c in cols])
            new_id = cur.lastrowid if "id" not in data else old_id
            tx.execute("DELETE FROM parked_files WHERE op_id=?", (op_id,))
        if new_id != old_id:
            t = self.thumbs_db
            t.execute("UPDATE OR REPLACE thumbs SET file_id=? WHERE file_id=?", (new_id, old_id))
        return True

    def drop_parked(self, op_ids: list[int]) -> None:
        """Forget parked rows for good (their files were permanently deleted)."""
        if not op_ids:
            return
        ids = []
        with self.transaction() as db:
            for op_id in op_ids:
                r = db.execute("SELECT file_id FROM parked_files WHERE op_id=?", (op_id,)).fetchone()
                if r:
                    ids.append(r[0])
                db.execute("DELETE FROM parked_files WHERE op_id=?", (op_id,))
            live = {r[0] for r in db.execute(f"SELECT id FROM files WHERE id IN ({','.join('?' * len(ids))})", ids)} if ids else set()
        orphan = [i for i in ids if i not in live]
        if orphan:
            t = self.thumbs_db
            t.execute("BEGIN")
            t.executemany("DELETE FROM thumbs WHERE file_id=?", [(i,) for i in orphan])
            t.execute("COMMIT")

    # transactions ----------------------------------------------------------------------
    def transaction(self):
        return _Tx(self.db)


class _Tx:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def __enter__(self):
        self.conn.execute("BEGIN IMMEDIATE")
        return self.conn

    def __exit__(self, exc_type, exc, tb):
        self.conn.execute("ROLLBACK" if exc_type else "COMMIT")
        return False
