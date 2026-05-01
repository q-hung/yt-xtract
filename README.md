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
# Print transcript to stdout (video ID or full URL)
yt-xtract transcript VIDEO_ID
yt-xtract transcript "https://www.youtube.com/watch?v=VIDEO_ID"

# With timestamps
yt-xtract transcript -t VIDEO_ID

# Specify language
yt-xtract transcript -l es VIDEO_ID

# Save to a text file (auto-named <title>_<video_id>.txt)
yt-xtract transcript -s VIDEO_ID

# Save with timestamps to a custom path
yt-xtract transcript -s -t -o notes.txt VIDEO_ID

# Pipe-friendly: redirect to a file
yt-xtract transcript VIDEO_ID > transcript.txt
```

### Download a thumbnail

```bash
# Download best available quality (video ID or full URL)
yt-xtract thumbnail VIDEO_ID
yt-xtract thumbnail "https://www.youtube.com/watch?v=VIDEO_ID"

# Specify output path
yt-xtract thumbnail -o cover.jpg VIDEO_ID

# Request a specific quality
yt-xtract thumbnail -q hqdefault VIDEO_ID
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

# Run tests
make test
```
