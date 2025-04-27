"""Tests for the audio service."""

import io
import logging
import os
import shutil
from collections.abc import Generator
from typing import TypedDict
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError, NoCredentialsError

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
def mock_polly() -> Generator[MagicMock, None, None]:
    """Mock AWS Polly client."""
    with patch("boto3.client") as mock_client:
        mock_polly = MagicMock()
        # Create a file-like object for the audio stream
        audio_stream = io.BytesIO(b"mock_audio_data")
        mock_polly.synthesize_speech.return_value = {
            "AudioStream": audio_stream,
            "ContentType": "audio/mpeg",
        }
        mock_client.return_value = mock_polly
        yield mock_polly


@pytest.fixture
def cleanup_audio_dir() -> Generator[None, None, None]:
    """Clean up audio directories after tests."""
    yield
    # Clean up any leftover audio directories
    if os.path.exists("audio"):
        shutil.rmtree("audio")
    if os.path.exists("custom_audio"):
        shutil.rmtree("custom_audio")


def test_generate_audio_success(
    mock_polly: MagicMock, cleanup_audio_dir: None, caplog: pytest.LogCaptureFixture
) -> None:
    """Test successful audio generation."""
    with caplog.at_level(logging.DEBUG):
        service = AudioService()
        result = service.generate_audio("Hallo, wie geht es dir?")

        assert result is not None
        assert result.endswith(".mp3")
        assert os.path.exists(result)
        mock_polly.synthesize_speech.assert_called_once()

        # Verify logs
        assert "Generating audio for text: Hallo, wie geht es dir?" in caplog.text
        assert "Successfully saved audio file to:" in caplog.text

        # Clean up
        os.remove(result)


def test_generate_audio_no_credentials(caplog: pytest.LogCaptureFixture) -> None:
    """Test audio generation with missing AWS credentials."""
    with caplog.at_level(logging.ERROR):
        with patch("boto3.client", side_effect=NoCredentialsError()):
            with pytest.raises(NoCredentialsError) as exc_info:
                AudioService()
            assert str(exc_info.value) == "Unable to locate credentials"


def test_generate_audio_client_error(
    mock_polly: MagicMock, cleanup_audio_dir: None, caplog: pytest.LogCaptureFixture
) -> None:
    """Test audio generation with AWS client error."""
    error_response: ErrorResponse = {
        "Error": {
            "Code": "ValidationException",
            "Message": "This voice does not support the selected engine: standard",
            "Type": "Sender",
            "RequestId": "test-request-id",
        },
        "ResponseMetadata": {
            "RequestId": "test-request-id",
            "HTTPStatusCode": 400,
            "HTTPHeaders": {},
            "RetryAttempts": 0,
        },
        "Status": "Failed",
        "StatusReason": "Validation Error",
    }
    mock_polly.synthesize_speech.side_effect = ClientError(
        error_response,
        "synthesize_speech",
    )

    with caplog.at_level(logging.DEBUG):
        service = AudioService()
        with pytest.raises(ClientError):
            service.generate_audio("Guten Morgen!")

        # Verify logs
        assert "Error generating audio" in caplog.text
        assert "Error details:" in caplog.text
        assert "Failed SSML:" in caplog.text


def test_generate_audio_custom_config(
    cleanup_audio_dir: None, caplog: pytest.LogCaptureFixture
) -> None:
    """Test audio generation with custom configuration."""
    with caplog.at_level(logging.DEBUG):
        with patch("boto3.client") as mock_client:
            mock_polly = MagicMock()
            audio_stream = io.BytesIO(b"mock_audio_data")
            mock_polly.synthesize_speech.return_value = {
                "AudioStream": audio_stream,
                "ContentType": "audio/mpeg",
            }
            mock_client.return_value = mock_polly

            service = AudioService(
                output_dir="custom_audio",
                voice_id="Daniel",
                language_code="de-DE",
                speech_rate=90,
            )
            result = service.generate_audio("Ich lerne Deutsch.")

            assert result is not None
            assert "custom_audio" in result
            assert os.path.exists(result)

            # Verify logs
            assert "AudioService initialized with voice_id=Daniel" in caplog.text
            assert "Generating audio for text: Ich lerne Deutsch." in caplog.text
            assert "Successfully saved audio file to:" in caplog.text

            # Clean up
            os.remove(result)
            os.rmdir("custom_audio")
