"""Performance benchmark.

    python tools/benchmark.py [WORK_DIR] [--photos N]

Generates N distinct ~6 MP JPEGs with EXIF (plus some exact copies), then times each engine
stage, and stress-tests similarity grouping with 100,000 synthetic hashes.
"""
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from memoria.engine import duplicates, health, scanner, similar  # noqa: E402
from memoria.engine.db import Library  # noqa: E402
from memoria.samplelib import exif_bytes, scene  # noqa: E402


def make_photos(root: Path, n: int) -> int:
    bases = [np.asarray(scene(s, 3100, 2100)) for s in range(24)]
    t0 = datetime(2018, 1, 1, 9)

    def one(i):
        b = bases[i % len(bases)]
        ox, oy = (i * 7) % 100, (i * 3) % 100
        arr = b[oy:oy + 2000, ox:ox + 3000].astype(np.int16)
        arr = np.clip(arr + np.random.default_rng(i).integers(-6, 7, arr.shape, dtype=np.int16), 0, 255).astype(np.uint8)
        dt = t0 + timedelta(hours=7 * i)
        p = root / f"{dt:%Y}" / f"Event {i // 50:03d}" / f"IMG_{i:05d}.JPG"
        p.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(arr).save(p, "JPEG", quality=88, exif=exif_bytes(dt, i % 3, None))
        return p.stat().st_size

    with ThreadPoolExecutor() as pool:
        total = sum(pool.map(one, range(n)))
    for i in range(0, n, 20):  # 5% exact copies in a backup folder
        src = next((root).rglob(f"IMG_{i:05d}.JPG"))
        dst = root / "Backup" / src.name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        total += src.stat().st_size
    return total


RESULTS: list[dict] = []


def timed(label, fn, note_fn=None):
    t = time.perf_counter()
    out = fn()
    dt = time.perf_counter() - t
    print(f"  {label:<38} {dt:7.2f} s")
    RESULTS.append({"stage": label, "seconds": round(dt, 3), "note": ""})
    return out, dt


def note(text: str) -> None:
    print(f"    → {text}")
    RESULTS[-1]["note"] = text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("work", nargs="?", default=str(Path(tempfile.gettempdir()) / "memoria-bench"))
    ap.add_argument("--photos", type=int, default=1000)
    ap.add_argument("--json", help="also write results to this JSON file")
    a = ap.parse_args()
    root = Path(a.work) / "library"
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    print(f"Generating {a.photos} photos in {root} …")
    total, gen = timed("generate test photos", lambda: make_photos(root, a.photos))
    n_files = sum(1 for _ in root.rglob("*.JPG"))
    note(f"{n_files:,} files, {total / 1e9:.2f} GB")

    lib = Library(root)
    print("Engine stages (cold OS cache not guaranteed):")
    timed("scan (walk + catalogue)", lambda: scanner.scan(lib))
    _, t_an = timed("analyse (EXIF, thumbs, hashes, quality)", lambda: scanner.analyze(lib))
    note(f"{n_files / t_an:,.0f} photos/s, {total / 1e6 / t_an:,.0f} MB/s of photos")
    timed("rescan, nothing changed", lambda: (scanner.scan(lib), scanner.analyze(lib)))
    g, _ = timed("find duplicates (first run)", lambda: duplicates.find_duplicates(lib))
    note(f"{len(g)} groups")
    timed("find duplicates (cached)", lambda: duplicates.find_duplicates(lib))
    sg, _ = timed("find similar (+faces for group members)", lambda: similar.find_similar(lib))
    note(f"{len(sg)} groups")
    _, t_h = timed("health check (full read)", lambda: health.run_health(lib))
    note(f"{total / 1e6 / t_h:,.0f} MB/s")

    print("Similarity stress test, 100,000 random hashes:")
    rng = np.random.default_rng(1)
    hashes = rng.integers(-(2**63), 2**63 - 1, 100_000, dtype=np.int64)
    times = np.full(100_000, np.nan)
    timed("similarity pairs, 100,000 hashes", lambda: sum(1 for _ in similar.similar_pairs(hashes, times, 10, 3, 16)))
    note("5×10⁹ pair comparisons")
    lib.close()
    shutil.rmtree(root, ignore_errors=True)
    if a.json:
        import json
        import os
        import platform
        info = {"photos": a.photos, "files": n_files, "bytes": total, "cpu_count": os.cpu_count(),
                "machine": platform.machine(), "python": platform.python_version(),
                "os": f"{platform.system()} {platform.release()}", "stages": RESULTS}
        Path(a.json).write_text(json.dumps(info, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
