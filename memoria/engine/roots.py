"""Stable catalogue keys for media folders; source identities are checked before disk work."""
from __future__ import annotations

import json
import os
import re
import uuid
from pathlib import Path
from typing import TYPE_CHECKING

from . import config

if TYPE_CHECKING:
    from .db import Library

_KEY = re.compile(r"@root:(\d+)(?:\\(.*))?$")
MARKER = "source.json"


def split_key(key: str) -> tuple[int, str]:
    if key.startswith("@root:"):
        match = _KEY.fullmatch(key)
        if match is None:
            raise ValueError(f"Invalid catalogue path: {key}")
        source, relative = int(match[1]), match[2] or ""
    else:
        source, relative = 1, key
    path = Path(relative)
    if source < 1 or path.is_absolute() or path.drive or ".." in path.parts:
        raise ValueError("A catalogue path must stay inside its registered folder.")
    return source, relative


def key_for(source: int, relative: str = "") -> str:
    relative = relative.replace("/", "\\")
    key = relative if source == 1 else f"@root:{source}" + (f"\\{relative}" if relative else "")
    split_key(key)
    return key


def marker(path: Path) -> dict:
    with (config.app_dir(path) / MARKER).open(encoding="utf-8") as stream:
        data = json.load(stream)
    if not isinstance(data, dict) or not all(isinstance(data.get(k), str) and data[k] for k in ("catalogue", "source")):
        raise ValueError("The media-folder identity is invalid. The folder was not modified.")
    return data


def _write_marker(path: Path, catalogue: str, source: str) -> None:
    config.ensure_app_dir(path)
    with (config.app_dir(path) / MARKER).open("x", encoding="utf-8") as stream:
        json.dump({"catalogue": catalogue, "source": source}, stream)
        stream.flush()
        os.fsync(stream.fileno())


def check_home(path: Path) -> None:
    if (config.app_dir(path) / MARKER).exists():
        data = marker(path)
        if data["catalogue"] != data["source"]:
            raise ValueError("This is an added media folder. Open its owning library's catalogue home instead.")


def initialize(lib: Library) -> None:
    row = lib.db.execute("SELECT * FROM library_roots WHERE id=1").fetchone()
    if row is None:
        identity = marker(lib.root) if (config.app_dir(lib.root) / MARKER).exists() else None
        token = identity["source"] if identity else uuid.uuid4().hex
        lib.db.execute("INSERT INTO library_roots(id,path,label,token,online) VALUES (1,?,?,?,1)",
                       (str(lib.root), lib.root.name or str(lib.root), token))
    else:
        token = row["token"]
    if not (config.app_dir(lib.root) / MARKER).exists():
        _write_marker(lib.root, token, token)
    if marker(lib.root) != {"catalogue": token, "source": token}:
        raise ValueError("The catalogue home has a different source identity. Nothing was changed.")
    lib._catalogue_token = token
    old_home = Path(row["path"]) if row else lib.root
    if row is None or not row["keys_migrated"]:
        with lib.transaction() as db:
            for op in db.execute("SELECT id,src,dst FROM operations WHERE src_key IS NULL AND dst_key IS NULL").fetchall():
                keys = []
                for value in (op["src"], op["dst"]):
                    try:
                        keys.append(str(Path(value).relative_to(old_home)) if value else None)
                    except ValueError:
                        keys.append(None)
                if any(value is not None for value in keys):
                    db.execute("UPDATE operations SET src_key=?,dst_key=? WHERE id=?", (*keys, op["id"]))
            db.execute("UPDATE library_roots SET keys_migrated=1 WHERE id=1")
    lib.db.execute("UPDATE library_roots SET path=?,online=1,error=NULL WHERE id=1", (str(lib.root),))
    lib._reload_roots()


def _nonoverlapping(lib: Library, path: Path, skip: int | None = None) -> None:
    for source in lib.roots():
        if source["id"] == skip:
            continue
        existing = Path(source["path"])
        if path == existing or path in existing.parents or existing in path.parents:
            raise ValueError("Media folders must not overlap. This folder is already covered by another library root.")


def add(lib: Library, path: str | Path, label: str = "") -> int:
    path = Path(path).resolve()
    if not path.is_dir():
        raise NotADirectoryError(str(path))
    _nonoverlapping(lib, path)
    if (config.app_dir(path) / config.DB_NAME).exists():
        raise ValueError("This folder already contains a separate Memoria catalogue. "
                         "Add its media subfolders instead; catalogues are not merged automatically.")
    if (config.app_dir(path) / MARKER).exists():
        data = marker(path)
        if data["catalogue"] != lib._catalogue_token:
            raise ValueError("This media folder belongs to a different catalogue.")
        if lib.db.execute("SELECT 1 FROM library_roots WHERE token=?", (data["source"],)).fetchone():
            raise ValueError("This media folder is already registered. Use Reconnect to update its location.")
        token = data["source"]
    else:
        token = uuid.uuid4().hex
        _write_marker(path, lib._catalogue_token, token)
    from .db import _acquire_lock
    lock = _acquire_lock(config.app_dir(path) / "lock")
    try:
        with lib.transaction() as db:
            source = db.execute("INSERT INTO library_roots(path,label,token,online) VALUES (?,?,?,1)",
                                (str(path), label.strip() or path.name or str(path), token)).lastrowid
    except BaseException:
        from .db import _release_lock
        _release_lock(lock)
        raise
    lib._source_locks[source] = lock
    lib._reload_roots()
    return source


def reconnect(lib: Library, source: int, path: str | Path) -> None:
    if source == 1:
        raise ValueError("Open the catalogue from its new home to reconnect the primary folder.")
    row = next((r for r in lib.roots() if r["id"] == source), None)
    if row is None:
        raise ValueError("Unknown media folder.")
    path = Path(path).resolve()
    _nonoverlapping(lib, path, source)
    if marker(path) != {"catalogue": lib._catalogue_token, "source": row["token"]}:
        raise ValueError("This is not the registered media folder. Its identity does not match; nothing was changed.")
    from .db import _acquire_lock, _release_lock
    lock = _acquire_lock(config.app_dir(path) / "lock")
    try:
        lib.db.execute("UPDATE library_roots SET path=?,online=1,error=NULL WHERE id=?", (str(path), source))
    except BaseException:
        _release_lock(lock)
        raise
    previous = lib._source_locks.pop(source, None)
    if previous:
        _release_lock(previous)
    lib._source_locks[source] = lock
    lib._reload_roots()


def check(lib: Library, source: int) -> None:
    from .db import LibraryUnavailable, _acquire_lock, _release_lock
    row = next((r for r in lib.roots() if r["id"] == source), None)
    if row is None:
        raise ValueError("Unknown media folder.")
    path = Path(row["path"])
    try:
        if marker(path) != {"catalogue": lib._catalogue_token, "source": row["token"]}:
            raise ValueError("A different folder or drive is at the registered location.")
        if source != 1 and source not in lib._source_locks:
            lib._source_locks[source] = _acquire_lock(config.app_dir(path) / "lock")
    except (OSError, ValueError, RuntimeError) as error:
        lock = lib._source_locks.pop(source, None)
        if lock is not None:
            _release_lock(lock)
        lib.db.execute("UPDATE library_roots SET online=0,error=? WHERE id=?", (str(error)[:300], source))
        raise LibraryUnavailable(f"Reconnect '{row['label']}' before accessing its files: {error}") from error
    if not row["online"] or row["error"] is not None:
        lib.db.execute("UPDATE library_roots SET online=1,error=NULL WHERE id=?", (source,))
