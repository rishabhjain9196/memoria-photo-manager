"""Check everything: one read-only pass that runs every finder and summarises the results."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from . import duplicates, organize, scanner, similar, tidy
from .db import Library
from .progress import Progress


@dataclass
class Checkup:
    results: dict[str, Any] = field(default_factory=dict)
    summary: dict[str, str] = field(default_factory=dict)
    counts: dict[str, int] = field(default_factory=dict)


def run(lib: Library, progress: Optional[Progress] = None, include_videos: bool = True) -> Checkup:
    """Index, then find duplicates, similar photos (and videos), blurry photos, tidy-up items and the
    organise plan. Reads only — nothing in the library is changed."""
    progress = progress or Progress()
    try:
        from . import videosim
    except ImportError:  # pragma: no cover - optional module
        videosim = None
    steps = ["Reading the library", "Finding exact duplicates", "Finding similar photos"]
    if include_videos and videosim is not None:
        steps.append("Finding similar videos")
    steps += ["Checking for leftovers", "Planning date folders"]
    c = Checkup()
    i = 0

    def step():
        nonlocal i
        p = progress.step(i, len(steps), steps[i])
        i += 1
        return p

    scanner.index(lib, step())
    dups = duplicates.find_duplicates(lib, step())
    c.results["duplicates"] = dups
    c.counts["duplicates"] = sum(len(g.files) - 1 for g in dups)
    c.summary["duplicates"] = f"{c.counts['duplicates']:,} extra copies in {len(dups):,} groups"
    sim = similar.find_similar(lib, progress=step())
    c.results["similar"] = sim
    c.counts["similar"] = sum(len(g.files) - 1 for g in sim)
    c.summary["similar"] = f"{len(sim):,} groups of similar photos"
    if include_videos and videosim is not None:
        vids = videosim.find_similar_videos(lib, step())
        c.results["similar_videos"] = vids
        c.counts["similar_videos"] = sum(len(g.files) - 1 for g in vids)
        c.summary["similar_videos"] = f"{len(vids):,} groups of similar videos"
    blurry = similar.find_blurry(lib)
    c.results["blurry"] = blurry
    c.counts["blurry"] = len(blurry)
    rep = tidy.find_tidy(lib, step())
    c.results["tidy"] = rep
    c.counts["tidy"] = rep.count("junk") + rep.count("empty") + rep.count("folders")
    plan = organize.plan_organize(lib, progress=step())
    c.results["organize"] = plan
    c.counts["organize"] = len(plan.items)
    progress.update(1000, 1000, "Check-up complete", force=True)
    return c
