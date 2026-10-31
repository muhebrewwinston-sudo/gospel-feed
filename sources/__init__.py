"""Supported Bible verse sources."""

from __future__ import annotations

from datetime import date


def get_verse_of_the_day(source: str, day: date) -> dict[str, str]:
    if source == "rss":
        from sources.bible_gateway_rss import get_verse_of_the_day as get_rss_verse

        return get_rss_verse()

    if source == "kjv":
        from sources.kjv_local import get_verse_of_the_day as get_kjv_verse

        return get_kjv_verse(day)

    raise ValueError(f"Unsupported Bible source: {source}")
