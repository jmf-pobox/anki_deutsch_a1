"""Live tests for the audio service."""

import os

import pytest
from botocore.exceptions import (  # type: ignore[import-untyped]  # External dependency boundary - no stubs available
    NoCredentialsError,
)

from langlearn.services import AudioService


def has_aws_credentials() -> bool:
    """Check if AWS credentials are configured."""
    try:
        service = AudioService()
        # Try a simple describe voices call to verify credentials
        service.client.describe_voices()
        return True
    except NoCredentialsError:
        return False


pytestmark = pytest.mark.skipif(
    not has_aws_credentials(),
    reason="AWS credentials not configured",
)


def test_live_audio_generation() -> None:
    """Test audio generation with real AWS Polly service."""
    service = AudioService()
    result = service.generate_audio("Hallo, wie geht es dir?")

    assert result is not None
    assert os.path.exists(result)
    assert result.endswith(".mp3")

    # Clean up
    os.remove(result)


def test_live_audio_custom_config() -> None:
    """Test audio generation with custom configuration."""
    service = AudioService(
        output_dir="custom_audio",
        voice_id="Vicki",
        language_code="en-GB",
        speech_rate=90,
    )
    result = service.generate_audio("Hello, how are you?")

    assert result is not None
    assert os.path.exists(result)
    assert result.endswith(".mp3")
    assert "custom_audio" in result

    # Clean up
    os.remove(result)
    if os.path.exists("custom_audio"):
        os.rmdir("custom_audio")
