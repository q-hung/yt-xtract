"""Fetch and parse YouTube caption tracks into readable text."""

from __future__ import annotations

import html
import xml.etree.ElementTree as ET
from dataclasses import dataclass

import httpx

from yt_xtract.extractor import (
    CaptionTrack,
    ExtractionError,
    VideoInfo,
    _HEADERS,
    fetch_video_info,
)


@dataclass
class TranscriptSegment:
    text: str
    start: float
    duration: float

    def format_timestamp(self) -> str:
        minutes, seconds = divmod(int(self.start), 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"


def _select_track(tracks: list[CaptionTrack], lang: str) -> CaptionTrack:
    """Pick the best matching caption track for the requested language."""
    for track in tracks:
        if track.language_code == lang:
            return track
    for track in tracks:
        if track.language_code.startswith(lang.split("-")[0]):
            return track
    if tracks:
        return tracks[0]
    raise ExtractionError("No caption tracks available for this video.")


def _parse_caption_xml(xml_text: str) -> list[TranscriptSegment]:
    """Parse YouTube's timedtext XML into transcript segments."""
    root = ET.fromstring(xml_text)
    segments: list[TranscriptSegment] = []
    for elem in root.iter("text"):
        text = elem.text or ""
        text = html.unescape(text).replace("\n", " ").strip()
        if not text:
            continue
        start = float(elem.get("start", "0"))
        dur = float(elem.get("dur", "0"))
        segments.append(TranscriptSegment(text=text, start=start, duration=dur))
    return segments


def fetch_transcript(
    url_or_id: str,
    *,
    lang: str = "en",
    client: httpx.Client | None = None,
) -> tuple[VideoInfo, list[TranscriptSegment]]:
    """Fetch the transcript for a YouTube video.

    Returns the VideoInfo and a list of TranscriptSegments.
    """
    should_close = client is None
    client = client or httpx.Client(headers=_HEADERS, follow_redirects=True)
    try:
        info = fetch_video_info(url_or_id, client=client)
        track = _select_track(info.caption_tracks, lang)

        resp = client.get(track.url)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise ExtractionError(f"Failed to fetch caption track: {exc}") from exc
    finally:
        if should_close:
            client.close()

    if not resp.text.strip():
        raise ExtractionError(
            "Caption track returned empty content. "
            "The video may have restricted captions."
        )

    segments = _parse_caption_xml(resp.text)
    return info, segments


def format_transcript(
    segments: list[TranscriptSegment],
    *,
    timestamps: bool = False,
) -> str:
    """Format transcript segments into readable text."""
    lines: list[str] = []
    for seg in segments:
        if timestamps:
            lines.append(f"[{seg.format_timestamp()}] {seg.text}")
        else:
            lines.append(seg.text)
    return "\n".join(lines)
