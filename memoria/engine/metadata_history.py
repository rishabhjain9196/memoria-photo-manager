"""Undoable organisation merges attached to completed duplicate-removal operations.

These are catalogue-only operations: callers must exclude them from file/byte
result counts and undo the physical source operation before undoing its merge.
"""
from __future__ import annotations

import json
from contextlib import contextmanager
from typing import Optional

from . import organisation
from .db import Library


@contextmanager
def _transaction(lib: Library):
    if not lib.db.in_transaction:
        with lib.transaction() as db:
            yield db
        return
    lib.db.execute("SAVEPOINT metadata_history")
    try:
        yield lib.db
        lib.db.execute("RELEASE metadata_history")
    except BaseException:
        lib.db.execute("ROLLBACK TO metadata_history")
        lib.db.execute("RELEASE metadata_history")
        raise


def _operation(lib: Library, op_id: int):
    organisation._id(op_id)
    row = lib.db.execute("SELECT * FROM operations WHERE id=?", (op_id,)).fetchone()
    if row is None:
        raise ValueError("That operation no longer exists.")
    return row


def _file_key(lib: Library, file_id: int) -> str:
    organisation.require_file(lib, file_id)
    row = lib.db.execute("SELECT rel_path FROM files WHERE id=?", (file_id,)).fetchone()
    if row is not None:
        return row["rel_path"]
    row = lib.db.execute(
        "SELECT data FROM parked_files WHERE file_id=? UNION ALL "
        "SELECT data FROM missing_files WHERE file_id=? LIMIT 1", (file_id, file_id)).fetchone()
    try:
        value = json.loads(row["data"])
        if value["id"] != file_id or not isinstance(value["rel_path"], str):
            raise ValueError("Invalid retained file identity.")
        return value["rel_path"]
    except (TypeError, KeyError, json.JSONDecodeError) as error:
        raise ValueError("The retained file identity is unavailable.") from error


def _check_source(lib: Library, source, source_file_id: int) -> None:
    row = lib.db.execute("SELECT file_id FROM parked_files WHERE op_id=?", (source["id"],)).fetchone()
    if row is not None:
        if row["file_id"] != source_file_id:
            raise ValueError("The source file does not belong to this operation.")
        organisation.require_file(lib, source_file_id)
        return
    key = _file_key(lib, source_file_id)
    expected = [source["src_key"] if source["src_key"] is not None else lib.rel(source["src"])]
    if source["op"] == "move" and source["dst_key"] is not None:
        expected.append(source["dst_key"])
    if key.casefold() not in {value.casefold() for value in expected}:
        raise ValueError("The source file does not belong to this operation.")


def _snapshot(lib: Library, value) -> dict:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError as error:
            raise ValueError("The organisation snapshot is unreadable; no choices were restored.") from error
    return organisation._validated(lib, value)


def apply_merge(lib: Library, source_op_id: int, source_file_id: int, keeper_id: int,
                seq: int) -> Optional[int]:
    """Apply once and return the metadata operation ID (None for a completed no-op).

    An existing merge is never replayed, even after resets supersede its snapshot.
    Supports an enclosing transaction; otherwise takes an immediate write transaction.
    """
    organisation._id(source_file_id)
    organisation._id(keeper_id)
    if source_file_id == keeper_id:
        raise ValueError("The source and keeper must be different files.")
    if type(seq) is not int or not -(2**63) <= seq < 2**63:
        raise ValueError("Choose a valid operation sequence.")
    with _transaction(lib) as db:
        source = _operation(lib, source_op_id)
        if source["status"] != "done" or source["op"] not in ("recycle", "move"):
            raise ValueError("Organisation can merge only after the source removal has completed.")
        if source["merge_target"] is not None and source["merge_target"] != keeper_id:
            raise ValueError("This operation has a different recorded keeper.")
        _check_source(lib, source, source_file_id)
        existing = db.execute("SELECT op_id,file_id FROM metadata_journal WHERE source_op=?",
                              (source_op_id,)).fetchone()
        if existing is not None:
            if existing["file_id"] != keeper_id:
                raise ValueError("This operation already merged into a different keeper.")
            if not source["merge_complete"]:
                db.execute("UPDATE operations SET merge_complete=1 WHERE id=?", (source_op_id,))
            return existing["op_id"]
        if source["merge_complete"]:
            return None

        keeper_key = _file_key(lib, keeper_id)
        keeper_path = str(lib.abspath(keeper_key))
        before, after = organisation.merged_state(lib, source_file_id, keeper_id)
        before, after = _snapshot(lib, before), _snapshot(lib, after)
        op_id = None
        if before != after:
            op_id = db.execute(
                "INSERT INTO operations(batch_id,seq,op,src,src_key,size,reason,status) "
                "VALUES (?,?,'metadata',?,?,0,'Preserve duplicate organisation','pending')",
                (source["batch_id"], seq, keeper_path, keeper_key)).lastrowid
            db.execute(
                "INSERT INTO metadata_journal(op_id,file_id,before_json,after_json,source_op) VALUES (?,?,?,?,?)",
                (op_id, keeper_id, json.dumps(before, sort_keys=True), json.dumps(after, sort_keys=True), source_op_id))
            organisation.set_state(lib, keeper_id, after)
            db.execute("UPDATE operations SET status='done' WHERE id=?", (op_id,))
        db.execute("UPDATE operations SET merge_complete=1 WHERE id=?", (source_op_id,))
        return op_id


def undo_merge(lib: Library, metadata_op_id: int) -> None:
    """Compare-and-restore only after the source is restored; never overwrite later edits.

    Already undone/superseded operations are harmless no-ops. Reset-sanitized
    snapshots are used as stored, without reconstructing the original values.
    """
    with _transaction(lib) as db:
        op = _operation(lib, metadata_op_id)
        if op["op"] != "metadata":
            raise ValueError("That operation is not an organisation merge.")
        if op["status"] in ("undone", "superseded"):
            return
        if op["status"] != "done":
            raise ValueError("That organisation merge is not complete.")
        journal = db.execute("SELECT * FROM metadata_journal WHERE op_id=?", (metadata_op_id,)).fetchone()
        if journal is None or journal["source_op"] is None:
            raise ValueError("The organisation snapshot has no source operation; no choices were restored.")
        source = _operation(lib, journal["source_op"])
        if source["status"] != "undone" or db.execute(
                "SELECT 1 FROM parked_files WHERE op_id=?", (source["id"],)).fetchone():
            raise ValueError("Restore the source from Recovery first. A purged or unrestored source cannot undo this merge.")
        before = _snapshot(lib, journal["before_json"])
        after = _snapshot(lib, journal["after_json"])
        current = _snapshot(lib, organisation.state(lib, journal["file_id"]))
        if current != after:
            raise ValueError("Keeper organisation changed after the merge; current choices were left unchanged.")
        organisation.set_state(lib, journal["file_id"], before)
        db.execute("UPDATE operations SET status='undone',error=NULL WHERE id=?", (metadata_op_id,))
