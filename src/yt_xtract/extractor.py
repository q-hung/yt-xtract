"""Extract video metadata from YouTube using the InnerTube API."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

import httpx

_VIDEO_ID_PATTERNS = [
    re.compile(r"(?:v=|/v/|youtu\.be/|/embed/|/shorts/)([a-zA-Z0-9_-]{11})"),
    re.compile(r"^([a-zA-Z0-9_-]{11})$"),
]

_INNERTUBE_API_KEY_RE = re.compile(r'"INNERTUBE_API_KEY":"([^"]+)"')

_INNERTUBE_PLAYER_URL = "https://www.youtube.com/youtubei/v1/player"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# Android client context yields caption URLs that actually return content,
# unlike the WEB client whose timedtext URLs return empty responses.
_INNERTUBE_CONTEXT = {
    "client": {
        "clientName": "ANDROID",
        "clientVersion": "20.10.38",
    }
}


class ExtractionError(Exception):
    """Raised when extraction of YouTube data fails."""


@dataclass
class CaptionTrack:
    url: str
    language_code: str
    name: str
    is_translatable: bool = False


@dataclass
class VideoInfo:
    video_id: str
    title: str
    caption_tracks: list[CaptionTrack] = field(default_factory=list)
    thumbnail_url: str | None = None


def extract_video_id(url_or_id: str) -> str:
    """Parse a YouTube URL or bare video ID and return the 11-char video ID."""
    url_or_id = url_or_id.strip()
    for pattern in _VIDEO_ID_PATTERNS:
        match = pattern.search(url_or_id)
        if match:
            return match.group(1)
    raise ExtractionError(
        f"Could not extract video ID from: {url_or_id!r}. "
        "Provide an 11-character video ID (e.g. dQw4w9WgXcQ) or a YouTube URL."
    )


def _get_api_key(client: httpx.Client, video_id: str) -> str:
    """Fetch the YouTube watch page and extract the InnerTube API key."""
    try:
        resp = client.get(f"https://www.youtube.com/watch?v={video_id}")
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise ExtractionError(f"Failed to fetch YouTube page: {exc}") from exc

    match = _INNERTUBE_API_KEY_RE.search(resp.text)
    if not match:
        raise ExtractionError("Could not find INNERTUBE_API_KEY in page HTML.")
    return match.group(1)


def _fetch_player_response(
    client: httpx.Client, video_id: str, api_key: str
) -> dict:
    """Call the InnerTube /player endpoint with Android client context."""
    body = {
        "context": _INNERTUBE_CONTEXT,
        "videoId": video_id,
    }
    try:
        resp = client.post(
            _INNERTUBE_PLAYER_URL,
            params={"key": api_key},
            json=body,
        )
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise ExtractionError(f"InnerTube player request failed: {exc}") from exc

    try:
        return resp.json()
    except json.JSONDecodeError as exc:
        raise ExtractionError(f"Failed to parse player response JSON: {exc}") from exc


def _parse_caption_tracks(player_response: dict) -> list[CaptionTrack]:
    """Extract caption track metadata from the player response."""
    captions = (
        player_response
        .get("captions", {})
        .get("playerCaptionsTracklistRenderer", {})
        .get("captionTracks", [])
    )
    tracks = []
    for track in captions:
        url = re.sub(r"&fmt=\w+", "", track["baseUrl"])
        tracks.append(
            CaptionTrack(
                url=url,
                language_code=track.get("languageCode", "unknown"),
                name=track.get("name", {}).get("simpleText", ""),
                is_translatable=track.get("isTranslatable", False),
            )
        )
    return tracks


def fetch_video_info(url_or_id: str, *, client: httpx.Client | None = None) -> VideoInfo:
    """Fetch and parse video info from YouTube for a given URL or video ID."""
    video_id = extract_video_id(url_or_id)

    should_close = client is None
    client = client or httpx.Client(headers=_HEADERS, follow_redirects=True)
    try:
        api_key = _get_api_key(client, video_id)
        player_response = _fetch_player_response(client, video_id, api_key)
    finally:
        if should_close:
            client.close()

    video_details = player_response.get("videoDetails", {})
    title = video_details.get("title", "")
    thumbnail_url = (
        video_details.get("thumbnail", {}).get("thumbnails", [{}])[-1].get("url")
    )
    caption_tracks = _parse_caption_tracks(player_response)

    return VideoInfo(
        video_id=video_id,
        title=title,
        caption_tracks=caption_tracks,
        thumbnail_url=thumbnail_url,
    )
