"""Tests for video ID extraction."""

from __future__ import annotations

import pytest

from yt_xtract.extractor import ExtractionError, extract_video_id


class TestExtractVideoId:
    @pytest.mark.parametrize(
        "input_val, expected",
        [
            ("dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("  dQw4w9WgXcQ  ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/v/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=120", "dQw4w9WgXcQ"),
        ],
    )
    def test_accepts_id_and_url_formats(self, input_val: str, expected: str) -> None:
        assert extract_video_id(input_val) == expected

    @pytest.mark.parametrize(
        "bad_input",
        [
            "",
            "short",
            "https://www.example.com/watch?v=abc",
            "not-a-valid-id-at-all!!",
        ],
    )
    def test_rejects_invalid_input(self, bad_input: str) -> None:
        with pytest.raises(ExtractionError, match="Provide an 11-character video ID"):
            extract_video_id(bad_input)
