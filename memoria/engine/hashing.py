"""Content hashing.

- ``full_hash`` reads the whole file (xxh3-128). It is the only hash used to decide that
  two files are identical or that a file is unchanged.
- ``quick_hash`` reads a few small samples. It is only a cheap pre-filter: different quick
  hashes prove files differ; equal quick hashes must be confirmed with ``full_hash``.
"""
from __future__ import annotations

import os
from typing import Optional

import xxhash

from .config import SAMPLE_BYTES, SAMPLE_POINTS

CHUNK = 1024 * 1024


def full_hash(path: str | os.PathLike) -> Optional[str]:
    h = xxhash.xxh3_128()
    try:
        with open(path, "rb", buffering=0) as f:
            buf = bytearray(CHUNK)
            view = memoryview(buf)
            while True:
                n = f.readinto(buf)
                if not n:
                    break
                h.update(view[:n])
    except OSError:
        return None
    return h.hexdigest()


def quick_hash(path: str | os.PathLike, size: int) -> Optional[str]:
    if size <= SAMPLE_BYTES * SAMPLE_POINTS:
        return full_hash(path)
    h = xxhash.xxh3_128()
    last = size - SAMPLE_BYTES
    try:
        with open(path, "rb", buffering=0) as f:
            for i in range(SAMPLE_POINTS):
                f.seek(last * i // (SAMPLE_POINTS - 1))
                h.update(f.read(SAMPLE_BYTES))
    except OSError:
        return None
    h.update(size.to_bytes(8, "little"))
    return h.hexdigest()
