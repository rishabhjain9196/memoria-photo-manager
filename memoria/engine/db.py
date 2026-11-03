"""SQLite catalogue for one library. One connection per thread (WAL mode)."""
from __future__ import annotations

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

THUMB_SCHEMA = "CREATE TABLE IF NOT EXISTS thumbs (file_id INTEGER PRIMARY KEY, data BLOB NOT NULL);"

# Columns derived from file content; cleared whenever a file's size or mtime changes.
DERIVED = ("qhash", "chash", "analyzed", "error", "width", "height", "taken_at", "date_source",
           "camera", "lat", "lon", "duration", "dhash", "sharpness", "brightness", "contrast",
           "clipped", "faces")


def _connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path), timeout=30, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA temp_store=MEMORY")
    conn.execute("PRAGMA cache_size=-32000")
    return conn


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
        self.db.executescript(SCHEMA)
        self.thumbs_db.executescript(THUMB_SCHEMA)

    # connections -----------------------------------------------------------------------
    @property
    def db(self) -> sqlite3.Connection:
        conn = getattr(self._local, "db", None)
        if conn is None:
            conn = self._local.db = _connect(self.db_path)
        return conn

    @property
    def thumbs_db(self) -> sqlite3.Connection:
        conn = getattr(self._local, "thumbs", None)
        if conn is None:
            conn = self._local.thumbs = _connect(self.thumbs_path)
        return conn

    def close(self) -> None:
        for name in ("db", "thumbs"):
            conn = getattr(self._local, name, None)
            if conn is not None:
                conn.close()
                setattr(self._local, name, None)

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
                   SUM(kind!='other' AND analyzed=0) AS pending,
                   SUM(error IS NOT NULL) AS errors,
                   MIN(CASE WHEN kind!='other' AND error IS NULL THEN taken_at END) AS first,
                   MAX(CASE WHEN kind!='other' AND error IS NULL THEN taken_at END) AS last
            FROM files""").fetchone()
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
