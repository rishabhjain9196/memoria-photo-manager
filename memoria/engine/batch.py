"""Batch operations on a hand-picked selection of library files (from Photos & videos)."""
from __future__ import annotations

from pathlib import Path

from . import config
from .actions import Action
from .db import Library


def plan_recycle(lib: Library, rows: list[dict]) -> list[Action]:
    return [Action(op="recycle", src=str(lib.abspath(r["rel_path"])), size=r["size"], mtime=r["mtime"],
                   reason="Moved to Recovery from Photos & videos", file_id=r["id"]) for r in rows]


def plan_copy_to(lib: Library, rows: list[dict], dest: str | Path) -> list[Action]:
    """Verified copies into ``dest`` (flat). Existing names get a number; nothing is overwritten."""
    dest = Path(dest).resolve()
    if config.APP_DIR_NAME in dest.parts:
        raise ValueError("Choose a folder outside Memoria's own .memoria folder.")
    return [Action(op="copy", src=str(lib.abspath(r["rel_path"])), dst=str(dest / r["name"]), size=r["size"],
                   hash=r.get("chash"), reason=f"Copied to {dest}") for r in rows]


def plan_move_within(lib: Library, rows: list[dict], dest: str | Path) -> list[Action]:
    """Move files to another folder inside the same library (catalogue rows follow them)."""
    dest = Path(dest).resolve()
    try:
        rel = dest.relative_to(lib.root)
    except ValueError:
        raise ValueError("Choose a folder inside this library. To put files somewhere else, use Copy to folder.")
    if config.APP_DIR_NAME in rel.parts:
        raise ValueError("Choose a folder outside Memoria's own .memoria folder.")
    out = []
    for r in rows:
        if Path(r["folder"]) == rel:
            continue
        out.append(Action(op="move", src=str(lib.abspath(r["rel_path"])), dst=str(dest / r["name"]),
                          size=r["size"], mtime=r["mtime"], file_id=r["id"], reason=f"Moved to {rel or 'library root'}"))
    return out
