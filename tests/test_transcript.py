"""Tests for transcript helpers and CLI save behaviour."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from yt_xtract.transcript import slugify_title, transcript_filename


class TestSlugifyTitle:
    @pytest.mark.parametrize(
        "title, expected",
        [
            ("Hello World", "hello_world"),
            ("My Video - Part 1 (HD)", "my_video_part_1_hd"),
            ("ALLCAPS", "allcaps"),
            ("  spaces  ", "spaces"),
            ("special!@#chars$%^", "special_chars"),
            ("already_snake_case", "already_snake_case"),
            ("multiple   spaces", "multiple_spaces"),
            ("trailing---dashes---", "trailing_dashes"),
            ("", "video"),
            ("   ", "video"),
            ("!!!!", "video"),
        ],
    )
    def test_slugify(self, title: str, expected: str) -> None:
        assert slugify_title(title) == expected


class TestTranscriptFilename:
    def test_normal_title(self) -> None:
        assert transcript_filename("My Video", "dQw4w9WgXcQ") == "my_video_dQw4w9WgXcQ.txt"

    def test_empty_title_fallback(self) -> None:
        assert transcript_filename("", "dQw4w9WgXcQ") == "video_dQw4w9WgXcQ.txt"

    def test_special_chars_in_title(self) -> None:
        result = transcript_filename("What's Up? (2024)", "abc12345678")
        assert result == "what_s_up_2024_abc12345678.txt"


class TestTranscriptCLISave:
    """Smoke tests for the transcript CLI --save flag using mocked fetch."""

    def test_save_creates_file(self, tmp_path, monkeypatch) -> None:
        from yt_xtract import cli
        from yt_xtract.extractor import VideoInfo
        from yt_xtract.transcript import TranscriptSegment

        dummy_info = VideoInfo(video_id="dQw4w9WgXcQ", title="Test Video")
        dummy_segments = [
            TranscriptSegment(text="Hello world", start=0.0, duration=2.0),
            TranscriptSegment(text="Second line", start=2.0, duration=3.0),
        ]

        monkeypatch.setattr(
            "yt_xtract.cli.fetch_transcript",
            lambda *a, **kw: (dummy_info, dummy_segments),
        )

        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli.main, ["transcript", "-s", "dQw4w9WgXcQ"])
            assert result.exit_code == 0, result.output

            from pathlib import Path

            expected = Path("test_video_dQw4w9WgXcQ.txt")
            assert expected.exists()
            content = expected.read_text()
            assert "Hello world" in content
            assert "Second line" in content

    def test_save_with_output_path(self, tmp_path, monkeypatch) -> None:
        from yt_xtract import cli
        from yt_xtract.extractor import VideoInfo
        from yt_xtract.transcript import TranscriptSegment

        dummy_info = VideoInfo(video_id="dQw4w9WgXcQ", title="Test Video")
        dummy_segments = [
            TranscriptSegment(text="Hello", start=0.0, duration=1.0),
        ]

        monkeypatch.setattr(
            "yt_xtract.cli.fetch_transcript",
            lambda *a, **kw: (dummy_info, dummy_segments),
        )

        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(
                cli.main, ["transcript", "-o", "custom.txt", "dQw4w9WgXcQ"]
            )
            assert result.exit_code == 0, result.output

            from pathlib import Path

            assert Path("custom.txt").exists()
            assert "Hello" in Path("custom.txt").read_text()

    def test_save_with_timestamps(self, tmp_path, monkeypatch) -> None:
        from yt_xtract import cli
        from yt_xtract.extractor import VideoInfo
        from yt_xtract.transcript import TranscriptSegment

        dummy_info = VideoInfo(video_id="dQw4w9WgXcQ", title="Test Video")
        dummy_segments = [
            TranscriptSegment(text="Hello", start=65.0, duration=2.0),
        ]

        monkeypatch.setattr(
            "yt_xtract.cli.fetch_transcript",
            lambda *a, **kw: (dummy_info, dummy_segments),
        )

        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(
                cli.main, ["transcript", "-s", "-t", "dQw4w9WgXcQ"]
            )
            assert result.exit_code == 0, result.output

            from pathlib import Path

            path = Path("test_video_dQw4w9WgXcQ.txt")
            assert path.exists()
            content = path.read_text()
            assert "[01:05]" in content

    def test_stdout_mode_unchanged(self, monkeypatch) -> None:
        """Without --save, transcript should print to stdout, not create a file."""
        from yt_xtract import cli
        from yt_xtract.extractor import VideoInfo
        from yt_xtract.transcript import TranscriptSegment

        dummy_info = VideoInfo(video_id="dQw4w9WgXcQ", title="Test Video")
        dummy_segments = [
            TranscriptSegment(text="Hello", start=0.0, duration=1.0),
        ]

        monkeypatch.setattr(
            "yt_xtract.cli.fetch_transcript",
            lambda *a, **kw: (dummy_info, dummy_segments),
        )

        runner = CliRunner()
        result = runner.invoke(cli.main, ["transcript", "dQw4w9WgXcQ"])
        assert result.exit_code == 0
        assert "Hello" in result.output
