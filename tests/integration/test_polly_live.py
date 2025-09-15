"""Live tests for the audio service."""

import os

import pytest
from botocore.exceptions import (
    NoCredentialsError,
)

from langlearn.services import AudioService


def has_aws_credentials() -> bool:
    """Check if AWS credentials are configured."""
    try:
        import tempfile

        service = AudioService(output_dir=tempfile.mkdtemp())
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
    import tempfile

    service = AudioService(output_dir=tempfile.mkdtemp())
    result = service.generate_audio("Hallo, wie geht es dir?")

    assert result is not None
    assert os.path.exists(result)
    assert result.endswith(".mp3")

    # Clean up
    os.remove(result)


def test_live_audio_custom_config() -> None:
    """Test audio generation with custom configuration."""
    import tempfile

    service = AudioService(
        output_dir=tempfile.mkdtemp(),
        voice_id="Vicki",
        language_code="en-GB",
        speech_rate=90,
    )
    result = service.generate_audio("Hello, how are you?")

    assert result is not None
    assert os.path.exists(result)
    assert result.endswith(".mp3")
    # Result should be in a temporary directory, not project directory

    # Clean up
    os.remove(result)
