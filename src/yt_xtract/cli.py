"""CLI entry point for yt-xtract."""

from __future__ import annotations

import sys

import click

from yt_xtract.extractor import ExtractionError
from yt_xtract.thumbnail import QUALITY_OPTIONS, download_thumbnail
from yt_xtract.transcript import fetch_transcript, format_transcript


@click.group()
@click.version_option(package_name="yt-xtract")
def main() -> None:
    """Fetch transcripts and thumbnails from YouTube."""


@main.command()
@click.argument("video")
@click.option(
    "-l",
    "--lang",
    default="en",
    show_default=True,
    help="Language code for the transcript.",
)
@click.option(
    "-t", "--timestamps", is_flag=True, help="Include timestamps in the output."
)
@click.option(
    "-s",
    "--save",
    is_flag=True,
    help="Save transcript to a text file (<title>_<id>.txt).",
)
@click.option("-o", "--output", default=None, help="Output file path (implies --save).")
def transcript(
    video: str, lang: str, timestamps: bool, save: bool, output: str | None
) -> None:
    """Fetch and print the transcript for a YouTube video.

    VIDEO is a YouTube video ID (e.g. dQw4w9WgXcQ) or full URL.
    """
    try:
        info, segments = fetch_transcript(video, lang=lang)
    except ExtractionError as exc:
        click.secho(f"Error: {exc}", fg="red", err=True)
        sys.exit(1)

    if not segments:
        click.secho("No transcript segments found.", fg="yellow", err=True)
        sys.exit(1)

    text = format_transcript(segments, timestamps=timestamps)

    if output:
        save = True

    if save:
        from pathlib import Path

        from yt_xtract.transcript import transcript_filename

        path = (
            Path(output)
            if output
            else Path(transcript_filename(info.title, info.video_id))
        )
        path.write_text(text, encoding="utf-8")
        click.secho(f"Saved transcript to {path}", fg="green", err=True)
    else:
        click.echo(f"# {info.title}\n", err=True)
        click.echo(text)


@main.command()
@click.argument("video")
@click.option(
    "-o",
    "--output",
    default=None,
    help="Output file path (default: <video_id>_<quality>.jpg).",
)
@click.option(
    "-q",
    "--quality",
    default=None,
    type=click.Choice(QUALITY_OPTIONS, case_sensitive=False),
    help="Preferred thumbnail quality.",
)
def thumbnail(video: str, output: str | None, quality: str | None) -> None:
    """Download the thumbnail for a YouTube video.

    VIDEO is a YouTube video ID (e.g. dQw4w9WgXcQ) or full URL.
    """
    try:
        path = download_thumbnail(video, output=output, quality=quality)
    except ExtractionError as exc:
        click.secho(f"Error: {exc}", fg="red", err=True)
        sys.exit(1)

    click.secho(f"Saved thumbnail to {path}", fg="green", err=True)
