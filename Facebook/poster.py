"""Publish posts to a Facebook Page through the official Graph API."""

from __future__ import annotations

import requests


class FacebookPostError(RuntimeError):
    """Raised when Facebook rejects or cannot complete a post request."""


def post_to_facebook(
    message: str,
    page_id: str,
    access_token: str,
    graph_version: str = "v24.0",
    timeout: int = 30,
) -> str:
    """Publish a message and return its Facebook post ID."""
    if not page_id or not access_token:
        raise FacebookPostError(
            "FACEBOOK_PAGE_ID and FACEBOOK_ACCESS_TOKEN are required for live posting"
        )

    url = f"https://graph.facebook.com/{graph_version}/{page_id}/feed"
    payload = {"message": message, "access_token": access_token}

    try:
        response = requests.post(url, data=payload, timeout=timeout)
    except requests.RequestException as exc:
        raise FacebookPostError(f"Could not reach the Facebook Graph API: {exc}") from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise FacebookPostError(
            f"Facebook returned a non-JSON response (HTTP {response.status_code})"
        ) from exc

    if response.ok and isinstance(data, dict) and data.get("id"):
        return str(data["id"])

    error = data.get("error", {}) if isinstance(data, dict) else {}
    error_message = error.get("message", "Unknown Facebook API error")
    error_code = error.get("code", "unknown")
    error_type = error.get("type", "unknown")
    raise FacebookPostError(
        f"Facebook API error (HTTP {response.status_code}, "
        f"code {error_code}, type {error_type}): {error_message}"
    )
