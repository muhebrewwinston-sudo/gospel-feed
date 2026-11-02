"""Post rotating KJV verse cards and prewritten reflections every five hours."""

from __future__ import annotations

import json
import tempfile
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from config import Settings, load_settings
from facebook.poster import FacebookPostError, post_photo_to_facebook
from sources.kjv_local import VERSES
from utils.card_generator import generate_verse_card
from utils.formatter import format_post
from utils.history import HistoryError, load_history, make_verse_key, save_history
from utils.logger import configure_logging, logger

FIRST_POST_HOUR = 3
HOURS_BETWEEN_POSTS = 5
POSTS_PER_DAY = 5
SLOT_KEY_PREFIX = "five-hour-slot-"
ORIGINAL_COLLECTION_SIZE = 16
ROOT = Path(__file__).resolve().parent
REFLECTIONS = json.loads((ROOT / "data" / "reflections.json").read_text(encoding="utf-8"))


def slot_for_time(now: datetime) -> int:
    """Return the zero-based five-hour slot for the local time."""
    return ((now.hour - FIRST_POST_HOUR) % 24) // HOURS_BETWEEN_POSTS


def next_rotation_index(history: dict) -> int:
    """Continue after the last recorded passage instead of restarting by date."""
    indices = [
        record["rotation_index"]
        for record in history.values()
        if isinstance(record, dict) and isinstance(record.get("rotation_index"), int)
    ]
    if indices:
        return max(indices) + 1
    # History created before persistent indices used the original 16 passages.
    # Start with new material rather than immediately repeating those passages.
    return ORIGINAL_COLLECTION_SIZE if history else 0


def _slot_already_posted(history: dict, posted_date: date, slot: int) -> bool:
    prefix = f"{posted_date.isoformat()}|"
    suffix = f"|{SLOT_KEY_PREFIX}{slot}"
    return any(key.startswith(prefix) and key.endswith(suffix) for key in history)


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

    try:
        history = load_history(settings.history_file)
    except HistoryError as exc:
        logger.error("Could not read posting history: %s", exc)
        return 1

    slot = slot_for_time(current_time)
    if _slot_already_posted(history, current_time.date(), slot) and not is_dry_run:
        logger.info("This slot was already posted. Skipping.")
        return 0

    verse_index = next_rotation_index(history)
    verse_text, reference = VERSES[verse_index % len(VERSES)]
    try:
        message, theme = _caption(settings, verse_text, reference)
    except (ValueError, KeyError) as exc:
        logger.error("Could not prepare the post: %s", exc)
        return 1

    base_key = make_verse_key(current_time.date(), "kjv", reference)
    verse_key = f"{base_key}|{SLOT_KEY_PREFIX}{slot}"
    logger.info(
        "Prepared photo post for slot %s (rotation %s): %s\n%s",
        slot + 1,
        verse_index,
        reference,
        message,
    )

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
        "schedule": "five-hour",
        "rotation_index": verse_index,
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
