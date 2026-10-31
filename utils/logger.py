"""Logging configuration for local runs and GitHub Actions."""

import logging


logger = logging.getLogger("bible_auto_poster")


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("poster.log", encoding="utf-8"),
        ],
    )
