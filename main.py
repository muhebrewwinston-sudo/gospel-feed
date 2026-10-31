"""Daily Bible verse poster entry point."""

from __future__ import annotations

import argparse
from datetime import datetime
from zoneinfo import ZoneInfo

from config import Settings, load_settings
from facebook.poster import FacebookPostError, post_to_facebook
from sources import get_verse_of_the_day
from sources.bible_gateway_rss import VerseSourceError
from utils.formatter import format_post
from utils.history import (
    HistoryError,
    load_history,
    make_verse_key,
    save_history,
)
from utils.logger import configure_logging, logger


def run(
    settings: Settings,
    *,
    source_override: str | None = None,
    dry_run: bool = False,
    now: datetime | None = None,
) -> int:
    source = source_override or settings.bible_source
    is_dry_run = dry_run or settings.dry_run
    timezone = ZoneInfo(settings.timezone)

    if now is None:
        current_time = datetime.now(timezone)
    elif now.tzinfo is None:
        current_time = now.replace(tzinfo=timezone)
    else:
        current_time = now.astimezone(timezone)

    if not is_dry_run and (
        not settings.facebook_page_id or not settings.facebook_access_token
    ):
        logger.error(
            "Live posting needs FACEBOOK_PAGE_ID and FACEBOOK_ACCESS_TOKEN. "
            "Add them to .env or use --dry-run."
        )
        return 2

    try:
        history = load_history(settings.history_file)
        verse = get_verse_of_the_day(source, current_time.date())
        message = format_post(
            verse["text"],
            verse["reference"],
            settings.post_hashtags,
            settings.max_post_length,
        )
    except (HistoryError, VerseSourceError, ValueError, KeyError) as exc:
        logger.error("Could not prepare the daily post: %s", exc)
        return 1

    verse_key = make_verse_key(current_time.date(), source, verse["reference"])
    logger.info("Prepared post for %s:\n%s", verse["reference"], message)

    if verse_key in history and not is_dry_run:
        logger.info("This verse was already posted today. Skipping.")
        return 0

    if is_dry_run:
        logger.info("Dry run complete. Nothing was published or added to history.")
        return 0

    try:
        post_id = post_to_facebook(
            message=message,
            page_id=settings.facebook_page_id,
            access_token=settings.facebook_access_token,
            graph_version=settings.graph_api_version,
            timeout=settings.request_timeout,
        )
    except FacebookPostError as exc:
        logger.error("Failed to publish: %s", exc)
        return 1

    history[verse_key] = {
        "reference": verse["reference"],
        "source": source,
        "post_id": post_id,
        "posted_at": current_time.isoformat(),
    }

    try:
        save_history(settings.history_file, history)
    except HistoryError as exc:
        logger.error(
            "Post %s was published, but its history could not be saved: %s. "
            "Record it manually before rerunning to avoid a duplicate.",
            post_id,
            exc,
        )
        return 1

    logger.info("Successfully posted to Facebook. Post ID: %s", post_id)
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        choices=("rss", "kjv"),
        help="Override BIBLE_SOURCE for this run",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the post without publishing or changing history",
    )
    return parser.parse_args()


def main() -> int:
    configure_logging()
    args = _parse_args()
    try:
        settings = load_settings()
    except ValueError as exc:
        logger.error("Invalid configuration: %s", exc)
        return 2

    return run(
        settings,
        source_override=args.source,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    raise SystemExit(main())
