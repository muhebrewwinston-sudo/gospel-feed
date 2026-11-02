"""Keep the KJV photo bot running continuously on Wispbyte."""

from __future__ import annotations

import os
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from config import load_settings
from five_hour import run
from utils.logger import configure_logging, logger

SLOT_HOURS = (3, 8, 13, 18, 23)


def next_slot(now: datetime) -> datetime:
    """Return the next strict five-hour slot after the supplied aware datetime."""
    for hour in SLOT_HOURS:
        candidate = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        if candidate > now:
            return candidate
    return (now + timedelta(days=1)).replace(hour=SLOT_HOURS[0], minute=0, second=0, microsecond=0)


def _sleep_until(target: datetime, timezone: ZoneInfo) -> None:
    while True:
        remaining = (target - datetime.now(timezone)).total_seconds()
        if remaining <= 0:
            return
        time.sleep(min(remaining, 300))


def _startup_run_requested() -> bool:
    return os.getenv("POSTER_RUN_ON_STARTUP", "false").strip().lower() in {"1", "true", "yes", "on"}


def _post(settings) -> None:
    try:
        result = run(settings, datetime.now(ZoneInfo(settings.timezone)))
        if result != 0:
            logger.error("Posting run exited with code %s; the scheduler will continue.", result)
    except Exception:
        logger.exception("Unexpected posting error; the scheduler will continue.")


def main() -> int:
    configure_logging()
    try:
        settings = load_settings()
    except ValueError as exc:
        logger.error("Invalid configuration: %s", exc)
        return 2
    if not settings.dry_run and (
        not settings.facebook_page_id or not settings.facebook_access_token
    ):
        logger.error("Set FACEBOOK_PAGE_ID and FACEBOOK_ACCESS_TOKEN in Startup → Environment Variables.")
        return 2

    timezone = ZoneInfo(settings.timezone)
    logger.info(
        "Wispbyte scheduler started. Posting every five hours; dry_run=%s.",
        settings.dry_run,
    )
    if _startup_run_requested():
        logger.info("Startup run requested; duplicate protection remains active.")
        _post(settings)

    while True:
        target = next_slot(datetime.now(timezone))
        logger.info("Next scheduled post: %s", target.isoformat())
        _sleep_until(target, timezone)
        _post(settings)


if __name__ == "__main__":
    raise SystemExit(main())
