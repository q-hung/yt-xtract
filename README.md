# yt-xtract

A command-line tool to fetch transcripts and thumbnails from YouTube.

No third-party YouTube libraries are used -- all data is extracted via direct HTTP
requests to public YouTube endpoints.

## Installation

Requires Python 3.10+.

```bash
# Install with uv (recommended)
uv pip install .

# Or install in development mode
uv pip install -e .
```

## Usage

### Fetch a transcript

```bash
# Print transcript to stdout
yt-xtract transcript "https://www.youtube.com/watch?v=VIDEO_ID"

# With timestamps
yt-xtract transcript -t "https://youtu.be/VIDEO_ID"

# Specify language
yt-xtract transcript -l es "https://www.youtube.com/watch?v=VIDEO_ID"

# Pipe-friendly: redirect to a file
yt-xtract transcript "VIDEO_ID" > transcript.txt
```

### Download a thumbnail

```bash
# Download best available quality
yt-xtract thumbnail "https://www.youtube.com/watch?v=VIDEO_ID"

# Specify output path
yt-xtract thumbnail -o cover.jpg "VIDEO_ID"

# Request a specific quality
yt-xtract thumbnail -q hqdefault "VIDEO_ID"
```

Thumbnail quality options: `maxresdefault`, `sddefault`, `hqdefault`, `mqdefault`, `default`.

## Development

```bash
# Clone and set up
cd yt-xtract
uv sync

# Run directly
uv run yt-xtract --help

# Or via python -m
uv run python -m yt_xtract --help
```
