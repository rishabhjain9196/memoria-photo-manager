"""Similar photos, burst groups, best-shot selection and blur detection.

Similarity uses the 64-bit difference hash computed during indexing. Pairwise Hamming distances
are computed in vectorised blocks (``numpy.bitwise_count``), so tens of thousands of photos take
seconds. Nothing here changes files; results are suggestions for the user to review.
"""
from __future__ import annotations

import math
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import numpy as np

from . import activity, config, dates, disk_speed, media
from .actions import Action
from .db import Library
from .progress import Progress

BLOCK = 512
COL_BLOCK = 8192


@dataclass
class SimilarGroup:
    files: list[dict]                 # best first
    best_id: int
    scores: dict[int, float] = field(default_factory=dict)
    reasons: dict[int, str] = field(default_factory=dict)
    burst: bool = False

    @property
    def reclaimable(self) -> int:
        return sum(f["size"] for f in self.files if f["id"] != self.best_id)


class _DSU:
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[max(ra, rb)] = min(ra, rb)


def _epoch(row) -> float:
    """Capture time from camera/video metadata only; file names and mtimes are too coarse for bursts."""
    if row["taken_at"] and row["date_source"] in dates.PRECISE:
        try:
            return datetime.fromisoformat(row["taken_at"]).timestamp()
        except ValueError:
            pass
    return math.nan


def similar_pairs(hashes: np.ndarray, times: np.ndarray, threshold: int, burst_seconds: float,
                  burst_threshold: int, progress: Optional[Progress] = None):
    """Yield (i, j, is_burst) for i<j that are similar by hash, or close in time and loosely similar.

    Hash comparisons run as vectorised blocks across threads (numpy releases the GIL); bursts are
    found with a sliding window over capture times, so they cost O(n) rather than O(n²).
    """
    h = hashes.view(np.uint64)
    n = len(h)

    def block(start: int):
        blk = h[start:start + BLOCK]
        out_i, out_j = [], []
        for cstart in range(start, n, COL_BLOCK):
            hit = np.bitwise_count(blk[:, None] ^ h[None, cstart:cstart + COL_BLOCK]) <= threshold
            if cstart == start:
                hit = np.triu(hit, k=1)
            ii, jj = np.nonzero(hit)
            if len(ii):
                out_i.append(ii + start)
                out_j.append(jj + cstart)
        return out_i, out_j

    starts = list(range(0, n, BLOCK))
    with activity.pool("Comparing", config.WORKERS), ThreadPoolExecutor(max_workers=config.WORKERS) as pool:
        for k, (out_i, out_j) in enumerate(pool.map(block, starts), 1):
            if progress:
                progress.update(k, len(starts), f"Comparing photos… {min(k * BLOCK, n):,} of {n:,}")
            for ii, jj in zip(out_i, out_j):
                for i, j in zip(ii.tolist(), jj.tolist()):
                    yield i, j, False

    finite = np.nonzero(~np.isnan(times))[0]
    order = finite[np.argsort(times[finite], kind="stable")]
    ts = times[order]
    for a in range(len(order)):
        b = a + 1
        while b < len(order) and ts[b] - ts[a] <= burst_seconds:
            i, j = sorted((int(order[a]), int(order[b])))
            distance = int(np.bitwise_count(h[i] ^ h[j]))
            if threshold < distance <= burst_threshold:
                yield i, j, True
            b += 1


def find_similar(lib: Library, threshold: int = 10, burst_seconds: float = 3.0,
                 burst_threshold: int = 16, progress: Optional[Progress] = None,
                 detect_faces: bool = True) -> list[SimilarGroup]:
    """Groups of visually similar photos. Byte-identical copies are collapsed to one member
    (those belong to the Duplicates tool)."""
    progress = progress or Progress()
    rows = [dict(r) for r in lib.files("kind='image' AND dhash IS NOT NULL AND error IS NULL")]
    if len(rows) < 2:
        return []
    hashes = np.array([r["dhash"] for r in rows], dtype=np.int64)
    times = np.array([_epoch(r) for r in rows], dtype=np.float64)
    dsu = _DSU(len(rows))
    for i, j, _ in similar_pairs(hashes, times, threshold, burst_seconds, burst_threshold, progress):
        dsu.union(i, j)
    clusters: dict[int, list[int]] = {}
    for i in range(len(rows)):
        clusters.setdefault(dsu.find(i), []).append(i)
    groups_idx = [m for m in clusters.values() if len(m) > 1]
    groups_idx = _collapse_identical(lib, rows, groups_idx, progress)
    if detect_faces:
        _ensure_faces(lib, [rows[i] for m in groups_idx for i in m], progress)
    groups = []
    for m in groups_idx:
        members = [rows[i] for i in m]
        g = rank_group(members)
        ts = [times[i] for i in m]
        g.burst = all(not math.isnan(t) for t in ts) and len(m) >= 3 and max(ts) - min(ts) <= burst_seconds * len(m)
        groups.append(g)
    groups.sort(key=lambda g: (-len(g.files), g.files[0]["taken_at"] or ""))
    progress.update(1, 1, f"Found {len(groups):,} groups of similar photos", force=True)
    return groups


def _collapse_identical(lib: Library, rows: list[dict], groups_idx: list[list[int]],
                        progress: Progress) -> list[list[int]]:
    from .duplicates import confirm_identical, keeper_score
    members = [rows[i] for m in groups_idx for i in m]
    identical = confirm_identical(lib, members, progress, "Checking for exact copies")
    drop: set[int] = set()
    for same in identical.values():
        ordered = sorted(same, key=keeper_score)
        drop.update(r["id"] for r in ordered[1:])
    out = []
    for m in groups_idx:
        kept = [i for i in m if rows[i]["id"] not in drop]
        if len(kept) > 1:
            out.append(kept)
    return out


def _ensure_faces(lib: Library, rows: list[dict], progress: Progress) -> None:
    todo = [r for r in rows if r.get("faces") is None]
    if not todo:
        return

    def work(r, gate):
        path = lib.abspath(r["rel_path"])
        try:
            data = disk_speed.read_original(path, gate)
        except OSError:
            data = None
        return r["id"], media.count_faces(path, data)

    updates = []
    for i, (fid, n) in enumerate(disk_speed.paced_map(work, todo, lambda r: lib.abspath(r["rel_path"]),
                                                      "Face counting", hold_gate=False), 1):
        progress.update(i, len(todo), f"Looking for faces… {i:,} of {len(todo):,}")
        updates.append((n if n is not None else -1, fid))
    with lib.transaction() as db:
        db.executemany("UPDATE files SET faces=? WHERE id=?", updates)
    faces = {fid: n for n, fid in updates}
    for r in rows:
        if r["id"] in faces:
            r["faces"] = faces[r["id"]]


def _exposure(r) -> float:
    clipped = r["clipped"] or 0.0
    bright = r["brightness"] if r["brightness"] is not None else 118
    return max(0.0, 1.0 - min(1.0, clipped * 2.5 + abs(bright - 118) / 118 * 0.6))


def rank_group(members: list[dict]) -> SimilarGroup:
    """Score photos in a group and explain the choice in plain words."""
    max_sharp = max((m["sharpness"] or 0) for m in members) or 1.0
    max_px = max((m["width"] or 0) * (m["height"] or 0) for m in members) or 1
    max_faces = max(max(m.get("faces") or 0, 0) for m in members)
    scores = {}
    for m in members:
        sharp = math.log1p(m["sharpness"] or 0) / math.log1p(max_sharp)
        px = ((m["width"] or 0) * (m["height"] or 0)) / max_px
        s = 0.55 * sharp + 0.25 * _exposure(m) + 0.08 * px
        if max_faces > 0:
            s += 0.12 * (max(m.get("faces") or 0, 0) / max_faces)
        scores[m["id"]] = round(s, 4)
    ordered = sorted(members, key=lambda m: (-scores[m["id"]], m["rel_path"]))
    best = ordered[0]
    g = SimilarGroup(files=ordered, best_id=best["id"], scores=scores)
    g.reasons[best["id"]] = _best_reason(best, ordered)
    for m in ordered[1:]:
        g.reasons[m["id"]] = _other_reason(m, best)
    return g


def _best_reason(best, members) -> str:
    bits = []
    sharp = [m["sharpness"] or 0 for m in members]
    if (best["sharpness"] or 0) >= max(sharp):
        lo = min(sharp) or 1
        ratio = (best["sharpness"] or 0) / lo
        bits.append(f"sharpest ({ratio:.1f}× the softest)" if ratio >= 1.3 else "sharpest")
    if _exposure(best) >= max(_exposure(m) for m in members) - 1e-6:
        bits.append("best exposure")
    if (best.get("faces") or 0) > 0 and (best.get("faces") or 0) >= max((m.get("faces") or 0) for m in members):
        bits.append(f"{best['faces']} face{'s' if best['faces'] != 1 else ''} detected")
    px = (best["width"] or 0) * (best["height"] or 0)
    if px >= max((m["width"] or 0) * (m["height"] or 0) for m in members) and len({(m["width"], m["height"]) for m in members}) > 1:
        bits.append("highest resolution")
    return "Best pick: " + (", ".join(bits) if bits else "highest overall score")


def _other_reason(m, best) -> str:
    bits = []
    bs, ms = best["sharpness"] or 0, m["sharpness"] or 0
    if bs > 0 and ms < bs * 0.75:
        bits.append(f"blurrier ({ms / bs:.0%} of best sharpness)")
    if _exposure(m) < _exposure(best) - 0.08:
        bri = m["brightness"] or 0
        bits.append("too dark" if bri < 90 else "too bright" if bri > 160 else "clipped highlights/shadows")
    if (m["width"] or 0) * (m["height"] or 0) < (best["width"] or 0) * (best["height"] or 0) * 0.8:
        bits.append(f"smaller ({m['width']}×{m['height']})")
    if (m.get("faces") or 0) < (best.get("faces") or 0):
        bits.append("fewer faces visible")
    return ("Weaker: " + ", ".join(bits)) if bits else "Very similar to the best pick"


BLUR_PRESETS = {"strict": 8.0, "normal": 20.0, "lenient": 45.0}


def find_blurry(lib: Library, threshold: float = BLUR_PRESETS["normal"]) -> list[dict]:
    """Photos whose sharpness score is below ``threshold`` (variance of Laplacian at 512 px)."""
    return [dict(r) for r in lib.files("kind='image' AND sharpness IS NOT NULL AND sharpness < ? "
                                       "AND error IS NULL", (threshold,), order="sharpness")]


def plan_recycle(lib: Library, rows: list[dict], reason: str) -> list[Action]:
    return [Action(op="recycle", src=str(lib.abspath(r["rel_path"])), size=r["size"], mtime=r["mtime"],
                   reason=reason, file_id=r["id"]) for r in rows]
