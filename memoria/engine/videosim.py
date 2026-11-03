"""Similar videos: re-encoded, compressed, resized or slightly trimmed copies of the same clip
(e.g. a phone original and the copy WhatsApp sent back).

Signature: 8 frames taken at evenly spaced positions (5 %…95 % of the duration), each reduced to a
64-bit difference hash. All frames of a video are read by ONE ffmpeg call (short clips are decoded
straight through, longer ones fast-seek to each position, so long videos cost little more than short
ones). Flat frames (black/white screens) are ignored. Signatures are cached in the ``video_sigs``
table and recomputed only when a file's size or modification time changes.

Two videos match when their durations are within max(1 s, 4 %) and the median Hamming distance
between corresponding frames is at most ``FRAME_THRESHOLD`` (alignment offsets of ±1 frame are
tried as well, to tolerate trimmed copies). Matches are joined into groups; byte-identical copies
are collapsed to one member because those belong to the Duplicates tool.

Results are ``similar.SimilarGroup`` objects (best first), so the photo review widgets can be reused.
To act on a selection use :func:`plan_recycle` (re-exported from ``similar``).
"""
from __future__ import annotations

import json
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import cmp_to_key
from typing import Optional

import numpy as np
from PIL import Image

from . import config, ffmpeg, media
from .db import Library
from .duplicates import keeper_score
from .progress import Progress
from .similar import SimilarGroup, _collapse_identical, _DSU, plan_recycle

__all__ = ["find_similar_videos", "plan_recycle", "signature", "frame_distance", "N_FRAMES",
           "FRAME_THRESHOLD"]

N_FRAMES = 8
FRAME_THRESHOLD = 12          # max median Hamming distance (of 64 bits) between matching frames
DURATION_ABS = 1.0            # seconds
DURATION_REL = 0.04           # fraction of the longer duration
OFFSETS = (0, -1, 1)
SEQUENTIAL_MAX = 20.0         # seconds; shorter clips are decoded straight through instead of seeking
FLAT_STD = 2.0                # frames with less gray-level spread than this carry no usable hash
_FW, _FH = 36, 32             # tiny gray frame; an exact multiple of the 9×8 dHash grid
_FRAME_BYTES = _FW * _FH
_MASK = (1 << 64) - 1
_VF = f"scale={_FW}:{_FH}:flags=area,format=gray"

SIG_SCHEMA = """CREATE TABLE IF NOT EXISTS video_sigs (
    file_id INTEGER PRIMARY KEY, size INTEGER, mtime REAL, duration REAL, sig TEXT)"""

Sig = list[Optional[int]]


# --------------------------------------------------------------------------- signatures
def positions(duration: float, n: int = N_FRAMES) -> list[float]:
    return [duration * (0.05 + 0.9 * i / (n - 1)) for i in range(n)]


def _hash_frame(raw: bytes) -> Optional[int]:
    """dHash of one tiny gray frame; ``None`` for flat frames (black/white screens), whose hash is
    just noise or all zeros and would make unrelated videos look alike."""
    if np.frombuffer(raw, dtype=np.uint8).std() < FLAT_STD:
        return None
    return media.dhash(Image.frombytes("L", (_FW, _FH), raw))


def _hashes(raw: bytes) -> Sig:
    return [_hash_frame(raw[k:k + _FRAME_BYTES]) for k in range(0, len(raw) - _FRAME_BYTES + 1, _FRAME_BYTES)]


def _grab_all(path: str, times: list[float], duration: float = 0.0) -> Optional[bytes]:
    """One ffmpeg process, one tiny gray frame per position, raw bytes out.

    Short clips are decoded straight through (cheaper than seeking: most of a short clip is a single
    keyframe interval anyway); longer ones fast-seek to every position."""
    if 0 < duration <= SEQUENTIAL_MAX:
        expr = "+".join(f"gte(t,{t:.3f})*lt(prev_t,{t:.3f})" for t in times)
        proc = ffmpeg.run_ffmpeg(["-loglevel", "error", "-an", "-sn", "-dn", "-i", path, "-map", "0:v:0",
                                  "-vf", f"setpts=PTS-STARTPTS,select='{expr}',{_VF}",
                                  "-fps_mode", "passthrough", "-f", "rawvideo", "-pix_fmt", "gray", "pipe:1"],
                                 timeout=120)
        if proc.returncode == 0 and len(proc.stdout) == _FRAME_BYTES * len(times):
            return proc.stdout
    args: list[str] = []
    chains = []
    for k, t in enumerate(times):
        args += ["-ss", f"{t:.3f}", "-t", "2", "-i", path]
        chains.append(f"[{k}:v:0]{_VF},trim=end_frame=1,setpts=PTS-STARTPTS[v{k}]")
    graph = ";".join(chains) + ";" + "".join(f"[v{k}]" for k in range(len(times))) + \
        f"concat=n={len(times)}:v=1:a=0[out]"
    proc = ffmpeg.run_ffmpeg(["-loglevel", "error", *args, "-filter_complex", graph, "-map", "[out]",
                              "-fps_mode", "passthrough", "-f", "rawvideo", "-pix_fmt", "gray", "pipe:1"],
                             timeout=120)
    if proc.returncode != 0 or len(proc.stdout) != _FRAME_BYTES * len(times):
        return None
    return proc.stdout


def _grab_one(path: str, t: float) -> Optional[bytes]:
    proc = ffmpeg.run_ffmpeg(["-loglevel", "error", "-ss", f"{max(0.0, t):.3f}", "-i", path, "-an", "-sn",
                              "-frames:v", "1", "-vf", _VF, "-f", "rawvideo", "-pix_fmt", "gray", "pipe:1"],
                             timeout=60)
    if proc.returncode != 0 or len(proc.stdout) < _FRAME_BYTES:
        return None
    return proc.stdout[:_FRAME_BYTES]


def signature(path, duration: float) -> Sig:
    """Per-frame dHashes at :func:`positions`; ``None`` for frames that could not be read."""
    path = str(path)
    times = positions(duration)
    raw = _grab_all(path, times, duration)
    if raw is not None:
        return _hashes(raw)
    out: Sig = []                      # slow, tolerant fallback: one process per frame
    for t in times:
        one = _grab_one(path, t)
        out.append(_hashes(one)[0] if one else None)
    return out


def _ensure_table(lib: Library) -> None:
    lib.db.execute(SIG_SCHEMA)


def _signatures(lib: Library, rows: list[dict], progress: Progress) -> dict[int, tuple[float, Sig]]:
    _ensure_table(lib)
    db = lib.db
    # Rows of removed files are kept on purpose: an undo restores the same file id, size and mtime.
    cached = {r["file_id"]: r for r in db.execute("SELECT * FROM video_sigs")}
    out: dict[int, tuple[float, Sig]] = {}
    todo = []
    for r in rows:
        c = cached.get(r["id"])
        if c is not None and c["size"] == r["size"] and c["mtime"] == r["mtime"] and c["sig"] is not None:
            out[r["id"]] = (c["duration"], json.loads(c["sig"]))
        else:
            todo.append(r)
    if not todo:
        return out

    def work(r):
        if progress.cancelled:
            return r, None
        try:
            return r, signature(lib.abspath(r["rel_path"]), r["duration"])
        except Exception:
            return r, [None] * N_FRAMES

    pending: list[tuple] = []

    def flush():
        if pending:
            with lib.transaction() as conn:
                conn.executemany("INSERT OR REPLACE INTO video_sigs (file_id, size, mtime, duration, sig) "
                                 "VALUES (?, ?, ?, ?, ?)", pending)
            pending.clear()

    n = len(todo)
    progress.update(0, n, f"Reading videos… 0 of {n:,}", force=True)
    pool = ThreadPoolExecutor(max_workers=max(1, config.WORKERS // 2))
    try:
        futures = [pool.submit(work, r) for r in todo]
        for i, fut in enumerate(as_completed(futures), 1):
            r, sig = fut.result()
            if sig is not None:
                out[r["id"]] = (r["duration"], sig)
                pending.append((r["id"], r["size"], r["mtime"], r["duration"], json.dumps(sig)))
                if len(pending) >= 16:
                    flush()
            progress.update(i, n, f"Reading videos… {i:,} of {n:,}")
    finally:
        pool.shutdown(wait=True, cancel_futures=True)
        flush()                        # keep finished work even when cancelled
    return out


# --------------------------------------------------------------------------- matching
def frame_distance(a: Sig, b: Sig, offsets=OFFSETS) -> Optional[float]:
    """Best (lowest) median Hamming distance between aligned frames over the alignment offsets."""
    best = None
    for off in offsets:
        d = [((x ^ y) & _MASK).bit_count()
             for i, x in enumerate(a) if 0 <= i + off < len(b)
             for y in (b[i + off],) if x is not None and y is not None]
        if len(d) >= max(3, len(a) // 2):
            m = statistics.median(d)
            best = m if best is None else min(best, m)
    return best


def durations_close(d1: float, d2: float) -> bool:
    return abs(d1 - d2) <= max(DURATION_ABS, DURATION_REL * max(d1, d2))


def _pairs(items: list[tuple[float, Sig]], progress: Progress, threshold: int):
    order = sorted(range(len(items)), key=lambda i: items[i][0])
    n = len(order)
    for a in range(n):
        i = order[a]
        for b in range(a + 1, n):
            j = order[b]
            if not durations_close(items[i][0], items[j][0]):
                break
            d = frame_distance(items[i][1], items[j][1])
            if d is not None and d <= threshold:
                yield i, j
        progress.update(a + 1, n, f"Comparing videos… {a + 1:,} of {n:,}")


# --------------------------------------------------------------------------- ranking
def _px(r) -> int:
    return (r["width"] or 0) * (r["height"] or 0)


def _rate(r) -> float:
    """Average bitrate in bits per second (whole file, so it includes audio)."""
    return r["size"] * 8 / r["duration"] if r["duration"] else 0.0


def _cmp(a, b) -> int:
    pa, pb = _px(a), _px(b)
    if max(pa, pb) and abs(pa - pb) > 0.05 * max(pa, pb):
        return -1 if pa > pb else 1
    ra, rb = _rate(a), _rate(b)
    if max(ra, rb) and abs(ra - rb) > 0.15 * max(ra, rb):
        return -1 if ra > rb else 1
    da, db = a["duration"] or 0, b["duration"] or 0
    if abs(da - db) > 0.25:
        return -1 if da > db else 1
    ka, kb = keeper_score(a), keeper_score(b)
    return -1 if ka < kb else 1 if ka > kb else 0


def _mbps(r) -> str:
    return f"{_rate(r) / 1e6:.1f} Mb/s"


def _res(r) -> str:
    return f"{r['width']}×{r['height']}"


def rank_group(members: list[dict]) -> SimilarGroup:
    """Order a group best first and explain the choice in plain words."""
    ordered = sorted(members, key=cmp_to_key(_cmp))
    best = ordered[0]
    max_px = max(_px(m) for m in members) or 1
    max_rate = max(_rate(m) for m in members) or 1.0
    max_dur = max(m["duration"] or 0 for m in members) or 1.0
    scores = {m["id"]: round(0.6 * _px(m) / max_px + 0.3 * _rate(m) / max_rate
                             + 0.1 * (m["duration"] or 0) / max_dur, 4) for m in members}
    g = SimilarGroup(files=ordered, best_id=best["id"], scores=scores, burst=False)

    bits = []
    if len({_px(m) for m in members}) > 1 and _px(best) >= max_px:
        bits.append(f"highest resolution ({_res(best)})")
    if _rate(best) >= max_rate * 0.999 and min(_rate(m) for m in members) < max_rate * 0.85:
        bits.append(f"highest quality ({_mbps(best)})")
    if (best["duration"] or 0) >= max_dur - 1e-6 and min(m["duration"] or 0 for m in members) < max_dur - 0.25:
        bits.append(f"longest ({best['duration']:.1f} s)")
    if not bits:
        bits.append("best name and location")
    g.reasons[best["id"]] = "Best pick: " + ", ".join(bits)

    for m in ordered[1:]:
        weak = []
        if _px(m) < _px(best) * 0.95:
            weak.append(f"smaller ({_res(m)})")
        if _rate(m) < _rate(best) * 0.85:
            weak.append(f"lower quality ({_mbps(m)})")
        if (m["duration"] or 0) < (best["duration"] or 0) - 0.25:
            weak.append(f"shorter ({m['duration']:.1f} s vs {best['duration']:.1f} s)")
        g.reasons[m["id"]] = ("Weaker: " + ", ".join(weak)) if weak else "Very similar to the best pick"
    return g


# --------------------------------------------------------------------------- public API
def find_similar_videos(lib: Library, progress: Optional[Progress] = None,
                        threshold: int = FRAME_THRESHOLD) -> list[SimilarGroup]:
    """Groups of visually similar videos, best first within each group. Changes no files."""
    progress = progress or Progress()
    rows = [dict(r) for r in lib.files("kind='video' AND error IS NULL AND duration > 0")]
    if len(rows) < 2:
        progress.update(1, 1, "Found 0 groups of similar videos", force=True)
        return []
    sigs = _signatures(lib, rows, progress)
    rows = [r for r in rows if r["id"] in sigs and any(h is not None for h in sigs[r["id"]][1])]
    items = [sigs[r["id"]] for r in rows]
    dsu = _DSU(len(rows))
    for i, j in _pairs(items, progress, threshold):
        dsu.union(i, j)
    clusters: dict[int, list[int]] = {}
    for i in range(len(rows)):
        clusters.setdefault(dsu.find(i), []).append(i)
    groups_idx = [m for m in clusters.values() if len(m) > 1]
    groups_idx = _collapse_identical(lib, rows, groups_idx, progress)
    groups = [rank_group([rows[i] for i in m]) for m in groups_idx]
    groups.sort(key=lambda g: (-len(g.files), -g.reclaimable, g.files[0]["rel_path"]))
    progress.update(1, 1, f"Found {len(groups):,} group{'s' if len(groups) != 1 else ''} of similar videos",
                    force=True)
    return groups
