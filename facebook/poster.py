"""Publish posts to a Facebook Page through the official Graph API."""

from __future__ import annotations

from pathlib import Path

import requests


class FacebookPostError(RuntimeError):
    """Raised when Facebook rejects or cannot complete a post request."""


def _response_json(response: requests.Response) -> dict:
    try:
        return response.json()
    except ValueError as exc:
        raise FacebookPostError(
            f"Facebook returned a non-JSON response (HTTP {response.status_code})"
        ) from exc


def _raise_api_error(response: requests.Response, data: dict) -> None:
    error = data.get("error", {}) if isinstance(data, dict) else {}
    error_message = error.get("message", "Unknown Facebook API error")
    error_code = error.get("code", "unknown")
    error_type = error.get("type", "unknown")
    raise FacebookPostError(
        f"Facebook API error (HTTP {response.status_code}, "
        f"code {error_code}, type {error_type}): {error_message}"
    )


def post_to_facebook(
    message: str,
    page_id: str,
    access_token: str,
    graph_version: str = "v24.0",
    timeout: int = 30,
) -> str:
    """Publish a text message and return its Facebook post ID."""
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

    data = _response_json(response)
    if response.ok and isinstance(data, dict) and data.get("id"):
        return str(data["id"])
    _raise_api_error(response, data)
    raise FacebookPostError("Unknown Facebook API error")


def post_photo_to_facebook(
    message: str,
    image_path: str | Path,
    page_id: str,
    access_token: str,
    graph_version: str = "v24.0",
    timeout: int = 60,
) -> str:
    """Upload a photo and caption to a Page and return the resulting post ID."""
    if not page_id or not access_token:
        raise FacebookPostError(
            "FACEBOOK_PAGE_ID and FACEBOOK_ACCESS_TOKEN are required for live posting"
        )

    image_path = Path(image_path)
    url = f"https://graph.facebook.com/{graph_version}/{page_id}/photos"
    try:
        with image_path.open("rb") as image:
            response = requests.post(
                url,
                data={"caption": message, "access_token": access_token},
                files={"source": (image_path.name, image, "image/png")},
                timeout=timeout,
            )
    except OSError as exc:
        raise FacebookPostError(f"Could not read verse-card image: {exc}") from exc
    except requests.RequestException as exc:
        raise FacebookPostError(f"Could not reach the Facebook Graph API: {exc}") from exc

    data = _response_json(response)
    if response.ok and isinstance(data, dict) and (data.get("post_id") or data.get("id")):
        return str(data.get("post_id") or data["id"])
    _raise_api_error(response, data)
    raise FacebookPostError("Unknown Facebook API error")
