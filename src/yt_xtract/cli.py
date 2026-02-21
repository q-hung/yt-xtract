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
@click.argument("video_url")
@click.option("-l", "--lang", default="en", show_default=True, help="Language code for the transcript.")
@click.option("-t", "--timestamps", is_flag=True, help="Include timestamps in the output.")
def transcript(video_url: str, lang: str, timestamps: bool) -> None:
    """Fetch and print the transcript for a YouTube video."""
    try:
        info, segments = fetch_transcript(video_url, lang=lang)
    except ExtractionError as exc:
        click.secho(f"Error: {exc}", fg="red", err=True)
        sys.exit(1)

    if not segments:
        click.secho("No transcript segments found.", fg="yellow", err=True)
        sys.exit(1)

    click.echo(f"# {info.title}\n", err=True)
    click.echo(format_transcript(segments, timestamps=timestamps))


@main.command()
@click.argument("video_url")
@click.option("-o", "--output", default=None, help="Output file path (default: <video_id>_<quality>.jpg).")
@click.option(
    "-q",
    "--quality",
    default=None,
    type=click.Choice(QUALITY_OPTIONS, case_sensitive=False),
    help="Preferred thumbnail quality.",
)
def thumbnail(video_url: str, output: str | None, quality: str | None) -> None:
    """Download the thumbnail for a YouTube video."""
    try:
        path = download_thumbnail(video_url, output=output, quality=quality)
    except ExtractionError as exc:
        click.secho(f"Error: {exc}", fg="red", err=True)
        sys.exit(1)

    click.secho(f"Saved thumbnail to {path}", fg="green", err=True)
