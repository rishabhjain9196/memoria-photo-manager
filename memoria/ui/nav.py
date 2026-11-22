"""Sidebar structure: sections, pages, icons and the colour each section uses for visual cues."""
from __future__ import annotations

from typing import Optional

from . import theme

NAV = [
    ("LIBRARY", [("overview", "Overview", "\uE80F"), ("photos", "Photos & videos", "\uE91B"),
                 ("people", "People", "\uE716"), ("insights", "Library insights", "\uE9D9")]),
    ("CLEAN UP", [("duplicates", "Duplicates", "\uE8C8"), ("similar", "Similar & best shots", "\uE734"),
                  ("tidy", "Tidy up", "\uE74D")]),
    ("ORGANISE", [("organize", "Organise by date", "\uE8B7"), ("albums", "Albums", "\uE7AA")]),
    ("CREATE", [("editor", "Editor", "\uE70F"), ("story", "Story maker", "\uE786"),
                ("video", "Video compressor", "\uE714")]),
    ("PROTECT", [("health", "Health check", "\uEA18"), ("compare", "Compare & sync", "\uE895"),
                 ("history", "History & recovery", "\uE81C")]),
]
NAV_KEYS = [k for _, items in NAV for k, _, _ in items]


def identity(key_or_title: str) -> Optional[tuple[str, str, str]]:
    """(key, glyph, section heading) for a page key or title, or None."""
    for heading, items in NAV:
        for key, title, glyph in items:
            if key_or_title in (key, title):
                return key, glyph, heading
    return None


def color(key_or_title: str) -> str:
    """The section colour for a page (the accent colour if unknown)."""
    found = identity(key_or_title)
    return theme.section_color(found[2]) if found else theme.ACCENT
