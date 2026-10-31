"""Application settings loaded from environment variables or a local .env file."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from dotenv import load_dotenv

load_dotenv()

DEFAULT_HASHTAGS = "#BibleVerse #DailyVerse #Gospel #Faith #Jesus"


def env_bool(name: str, default: bool = False) -> bool:
    """Read a boolean environment variable with a useful validation error."""
    value = os.getenv(name)
    if value is None or not value.strip():
        return default

    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} must be true or false, not {value!r}")


def _positive_int(name: str, default: int) -> int:
    value = int(os.getenv(name, str(default)))
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero")
    return value


@dataclass(frozen=True)
class Settings:
    facebook_page_id: str
    facebook_access_token: str
    graph_api_version: str
    bible_source: str
    post_hashtags: str
    max_post_length: int
    request_timeout: int
    timezone: str
    history_file: Path
    dry_run: bool


def load_settings() -> Settings:
    source = os.getenv("BIBLE_SOURCE", "rss").strip().lower()
    if source not in {"rss", "kjv"}:
        raise ValueError("BIBLE_SOURCE must be either 'rss' or 'kjv'")

    timezone = os.getenv("POST_TIMEZONE", "Africa/Blantyre").strip()
    try:
        ZoneInfo(timezone)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"Unknown POST_TIMEZONE: {timezone}") from exc

    graph_version = os.getenv("FACEBOOK_GRAPH_VERSION", "v24.0").strip()
    if not graph_version.startswith("v"):
        graph_version = f"v{graph_version}"

    return Settings(
        facebook_page_id=os.getenv("FACEBOOK_PAGE_ID", "").strip(),
        facebook_access_token=os.getenv("FACEBOOK_ACCESS_TOKEN", "").strip(),
        graph_api_version=graph_version,
        bible_source=source,
        post_hashtags=os.getenv("POST_HASHTAGS", DEFAULT_HASHTAGS).strip(),
        max_post_length=_positive_int("MAX_POST_LENGTH", 2000),
        request_timeout=_positive_int("REQUEST_TIMEOUT", 30),
        timezone=timezone,
        history_file=Path(
            os.getenv("POSTED_VERSES_FILE", "data/posted_verses.json")
        ),
        dry_run=env_bool("POSTER_DRY_RUN", False),
    )
