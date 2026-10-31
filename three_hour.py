"""Post rotating KJV verse cards and prewritten reflections every three hours."""

from __future__ import annotations

import json
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from config import Settings, load_settings
from facebook.poster import FacebookPostError, post_photo_to_facebook
from sources.kjv_local import VERSES
from utils.card_generator import generate_verse_card
from utils.formatter import format_post
from utils.history import HistoryError, load_history, make_verse_key, save_history
from utils.logger import configure_logging, logger

FIRST_POST_HOUR = 0
HOURS_BETWEEN_POSTS = 3
POSTS_PER_DAY = 8
ROOT = Path(__file__).resolve().parent
REFLECTIONS = json.loads((ROOT / "data" / "reflections.json").read_text(encoding="utf-8"))


def rotation_for_time(now: datetime) -> tuple[int, int]:
    """Return the daily slot and its position in the continuous KJV rotation."""
    slot = ((now.hour - FIRST_POST_HOUR) % 24) // HOURS_BETWEEN_POSTS
    index = (now.date().toordinal() * POSTS_PER_DAY + slot) % len(VERSES)
    return slot, index


def _caption(settings: Settings, verse_text: str, reference: str) -> tuple[str, str]:
    entry = REFLECTIONS[reference]
    base = format_post(verse_text, reference, "", settings.max_post_length)
    caption = (
        f"{base}\n\n💭 Reflection\n{entry['reflection']}\n\n{settings.post_hashtags}"
    ).strip()
    if len(caption) > settings.max_post_length:
        raise ValueError("Caption and reflection exceed the configured post-length limit")
    return caption, entry["theme"]


def run(settings: Settings, now: datetime | None = None) -> int:
    timezone = ZoneInfo(settings.timezone)
    if now is None:
        current_time = datetime.now(timezone)
    elif now.tzinfo is None:
        current_time = now.replace(tzinfo=timezone)
    else:
        current_time = now.astimezone(timezone)

    is_dry_run = settings.dry_run
    if not is_dry_run and (
        not settings.facebook_page_id or not settings.facebook_access_token
    ):
        logger.error("Live posting needs the two Facebook credentials.")
        return 2

    slot, verse_index = rotation_for_time(current_time)
    verse_text, reference = VERSES[verse_index]

    try:
        history = load_history(settings.history_file)
        message, theme = _caption(settings, verse_text, reference)
    except (HistoryError, ValueError, KeyError) as exc:
        logger.error("Could not prepare the post: %s", exc)
        return 1

    base_key = make_verse_key(current_time.date(), "kjv", reference)
    verse_key = f"{base_key}|slot-{slot}"
    logger.info("Prepared photo post for slot %s: %s\n%s", slot + 1, reference, message)

    if verse_key in history and not is_dry_run:
        logger.info("This slot was already posted. Skipping.")
        return 0

    with tempfile.TemporaryDirectory(prefix="gospel-card-") as directory:
        try:
            card_path = generate_verse_card(
                verse_text,
                reference,
                Path(directory) / "verse-card.png",
                theme,
            )
        except (OSError, ValueError) as exc:
            logger.error("Could not create the verse card: %s", exc)
            return 1

        if is_dry_run:
            logger.info("Dry run complete. Verse card created; nothing was published or recorded.")
            return 0

        try:
            post_id = post_photo_to_facebook(
                message=message,
                image_path=card_path,
                page_id=settings.facebook_page_id,
                access_token=settings.facebook_access_token,
                graph_version=settings.graph_api_version,
                timeout=max(settings.request_timeout, 60),
            )
        except FacebookPostError as exc:
            logger.error("Failed to publish: %s", exc)
            return 1

    history[verse_key] = {
        "reference": reference,
        "source": "kjv",
        "slot": slot,
        "media": "photo",
        "theme": theme,
        "post_id": post_id,
        "posted_at": current_time.isoformat(),
    }
    try:
        save_history(settings.history_file, history)
    except HistoryError as exc:
        logger.error(
            "Post %s was published, but history was not saved: %s. "
            "Record it before rerunning.",
            post_id,
            exc,
        )
        return 1

    logger.info("Successfully posted verse card to Facebook. Post ID: %s", post_id)
    return 0


def main() -> int:
    configure_logging()
    try:
        settings = load_settings()
    except ValueError as exc:
        logger.error("Invalid configuration: %s", exc)
        return 2
    return run(settings)


if __name__ == "__main__":
    raise SystemExit(main())
