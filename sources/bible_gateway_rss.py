"""Read Bible Gateway's official Verse of the Day Atom feed."""

from __future__ import annotations

import html
import re

import feedparser
import requests

RSS_URL = "https://www.biblegateway.com/votd/get/?format=atom"


class VerseSourceError(RuntimeError):
    """Raised when a verse cannot be retrieved or parsed."""


def _clean_html(value: str) -> str:
    """Convert feed HTML to compact plain text without scraping web pages."""
    if not value:
        return ""

    text = html.unescape(str(value))
    text = re.sub(r"(?is)<(script|style)\b[^>]*>.*?</\1>", "", text)
    text = re.sub(r"(?is)<sup\b[^>]*>.*?</sup>", "", text)
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?s)<[^>]+>", "", text)
    text = html.unescape(text)
    return " ".join(text.split()).strip()


def get_verse_of_the_day(timeout: int = 30) -> dict[str, str]:
    """Return the first official feed entry as text and reference."""
    try:
        response = requests.get(
            RSS_URL,
            timeout=timeout,
            headers={"User-Agent": "gospel-feed/1.0 (official RSS reader)"},
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise VerseSourceError(f"Could not fetch the Bible Gateway RSS feed: {exc}") from exc

    try:
        feed = feedparser.parse(response.content)
    except Exception as exc:  # feedparser can expose parser-specific exceptions
        raise VerseSourceError(f"Could not parse the Bible Gateway RSS feed: {exc}") from exc

    if not feed.entries:
        detail = f": {feed.bozo_exception}" if getattr(feed, "bozo", False) else ""
        raise VerseSourceError(f"No entries were found in the Bible Gateway RSS feed{detail}")

    entry = feed.entries[0]
    reference = _clean_html(entry.get("title", ""))

    content = ""
    if entry.get("content"):
        content = entry.content[0].get("value", "")
    if not content:
        content = entry.get("summary", "")

    text = _clean_html(content)
    if not text or not reference:
        raise VerseSourceError("The RSS entry did not contain both verse text and a reference")

    return {"text": text, "reference": reference}
