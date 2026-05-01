"""Download YouTube video thumbnails at the best available quality."""

from __future__ import annotations

from contextlib import nullcontext
from pathlib import Path

import httpx

from yt_xtract.extractor import ExtractionError, extract_video_id, make_client

QUALITY_OPTIONS = ("maxresdefault", "sddefault", "hqdefault", "mqdefault", "default")

_THUMBNAIL_URL = "https://img.youtube.com/vi/{video_id}/{quality}.jpg"

# YouTube returns a small grey placeholder (~1KB) for non-existent qualities
_MIN_THUMBNAIL_BYTES = 5_000


def _try_download(client: httpx.Client, video_id: str, quality: str) -> bytes | None:
    """Attempt to download a thumbnail at the given quality. Returns bytes or None."""
    url = _THUMBNAIL_URL.format(video_id=video_id, quality=quality)
    try:
        resp = client.get(url)
        if resp.status_code == 200 and len(resp.content) > _MIN_THUMBNAIL_BYTES:
            return resp.content
    except httpx.HTTPError:
        pass
    return None


def download_thumbnail(
    url_or_id: str,
    *,
    output: str | Path | None = None,
    quality: str | None = None,
    client: httpx.Client | None = None,
) -> Path:
    """Download the thumbnail for a YouTube video.

    Tries the requested quality first, then falls back through lower qualities.
    Returns the path to the saved file.
    """
    video_id = extract_video_id(url_or_id)

    client_context = nullcontext(client) if client is not None else make_client()
    with client_context as active_client:
        qualities = list(QUALITY_OPTIONS)
        if quality:
            if quality not in qualities:
                raise ExtractionError(
                    f"Unknown quality '{quality}'. "
                    f"Options: {', '.join(QUALITY_OPTIONS)}"
                )
            idx = qualities.index(quality)
            qualities = qualities[idx:]

        data: bytes | None = None
        used_quality = qualities[0]
        for q in qualities:
            data = _try_download(active_client, video_id, q)
            if data is not None:
                used_quality = q
                break

        if data is None:
            raise ExtractionError(
                f"No thumbnail found for video {video_id} at any quality."
            )

    out_path = Path(output) if output else Path(f"{video_id}_{used_quality}.jpg")
    out_path.write_bytes(data)
    return out_path
