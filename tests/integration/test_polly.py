"""Tests for the audio service."""

import logging
import os
import shutil
from collections.abc import Generator
from typing import TypedDict

import pytest

from langlearn.services import AudioService


class ErrorDict(TypedDict, total=False):
    """Type for AWS error response."""

    Code: str
    Message: str
    Type: str
    RequestId: str


class ResponseMetadataDict(TypedDict, total=False):
    """Type for AWS response metadata."""

    RequestId: str
    HTTPStatusCode: int
    HTTPHeaders: dict[str, str]
    RetryAttempts: int


class ErrorResponse(TypedDict, total=False):
    """Type for complete AWS error response."""

    Error: ErrorDict
    ResponseMetadata: ResponseMetadataDict
    Status: str
    StatusReason: str


@pytest.fixture
def cleanup_audio_dir() -> Generator[None, None, None]:
    """Clean up test audio directories after tests."""
    yield
    # Clean up any leftover test audio directories
    if os.path.exists("test_audio"):
        shutil.rmtree("test_audio")
    if os.path.exists("test_custom_audio"):
        shutil.rmtree("test_custom_audio")


@pytest.mark.live
def test_generate_audio_success(
    cleanup_audio_dir: None, caplog: pytest.LogCaptureFixture
) -> None:
    """Test successful audio generation."""
    with caplog.at_level(logging.DEBUG):
        service = AudioService(output_dir="test_audio")
        result = service.generate_audio("Hallo, wie geht es dir?")

        assert result is not None
        assert result.endswith(".mp3")
        assert os.path.exists(result)

        # Verify logs
        assert "Generating audio for text: Hallo, wie geht es dir?" in caplog.text
        assert "Successfully saved audio file to:" in caplog.text

        # Clean up
        os.remove(result)


@pytest.mark.live
def test_generate_audio_custom_config(
    cleanup_audio_dir: None, caplog: pytest.LogCaptureFixture
) -> None:
    """Test audio generation with custom configuration."""
    with caplog.at_level(logging.DEBUG):
        service = AudioService(
            output_dir="test_custom_audio",
            voice_id="Daniel",
            language_code="de-DE",
            speech_rate=90,
        )
        result = service.generate_audio("Ich lerne Deutsch.")

        assert result is not None
        assert "test_custom_audio" in result
        assert os.path.exists(result)

        # Verify logs
        assert "AudioService initialized with voice_id=Daniel" in caplog.text
        assert "Generating audio for text: Ich lerne Deutsch." in caplog.text
        assert "Successfully saved audio file to:" in caplog.text

        # Clean up
        os.remove(result)
        os.rmdir("test_custom_audio")
