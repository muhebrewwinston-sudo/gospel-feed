"""Persistent posting history used to prevent duplicate publications."""

from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path
from typing import Any


class HistoryError(RuntimeError):
    """Raised when posting history cannot be read or written safely."""


def load_history(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}

    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise HistoryError(f"Could not read posting history at {path}: {exc}") from exc

    # Migrate the simple list format used by early versions of the project.
    if isinstance(data, list):
        return {str(key): {} for key in data}

    if data == {}:
        return {}

    if not isinstance(data, dict) or not isinstance(data.get("posted_verses"), dict):
        raise HistoryError(
            f"Posting history at {path} has an invalid format; "
            "fix it before running the poster again"
        )

    return dict(data["posted_verses"])


def save_history(path: Path, history: dict[str, dict[str, Any]]) -> None:
    """Write history atomically so an interrupted run does not corrupt it."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = path.with_name(f"{path.name}.tmp")
        with temporary_path.open("w", encoding="utf-8") as handle:
            json.dump(
                {"posted_verses": history},
                handle,
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
            )
            handle.write("\n")
        os.replace(temporary_path, path)
    except OSError as exc:
        raise HistoryError(f"Could not save posting history at {path}: {exc}") from exc


def make_verse_key(day: date, source: str, reference: str) -> str:
    normalized_reference = " ".join(reference.split()).casefold()
    return f"{day.isoformat()}|{source}|{normalized_reference}"
