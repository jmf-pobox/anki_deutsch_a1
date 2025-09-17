"""Global pytest configuration and fixtures for test suite.

This module provides centralized mocking for external services to ensure
unit tests run reliably in CI/CD environments without keyring backends.
"""

import os
from collections.abc import Generator
from typing import Any
from unittest.mock import Mock, patch

import pytest

# Import to ensure language registration happens at test session start
import langlearn.languages  # noqa: F401


@pytest.fixture(autouse=True)
def mock_external_services(
    request: pytest.FixtureRequest,
) -> Generator[dict[str, Any] | None]:
    """Automatically mock external services for unit tests only.

    This fixture runs before every test to ensure that:
    1. Environment variables are set for services that check them first
    2. Keyring calls are mocked as fallback
    3. AWS boto3 clients are mocked
    4. HTTP requests are mocked

    Integration tests (in tests/integration/) are excluded from
    mocking so they can make real API calls for end-to-end testing.

    This prevents keyring errors in CI environments while maintaining
    proper test isolation for unit tests.
    """
    # Skip mocking for live integration tests that need real API calls
    if request.node.get_closest_marker("live") or "integration" in str(
        request.node.fspath
    ):
        yield None
        return
    # Store original environment
    original_env = {}
    test_env_vars = {
        "PEXELS_API_KEY": "mock-pexels-key",
        "ANTHROPIC_API_KEY": "mock-anthropic-key",
        "AWS_DEFAULT_REGION": "us-east-1",
        "AWS_ACCESS_KEY_ID": "mock-aws-key",
        "AWS_SECRET_ACCESS_KEY": "mock-aws-secret",
    }

    # Set test environment variables
    for key, value in test_env_vars.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value

    # Mock external service calls
    with (
        patch("langlearn.core.services.audio_service.boto3.client") as mock_boto_client,
        patch("langlearn.core.services.image_service.requests.get") as mock_requests,
        patch("keyring.get_password") as mock_keyring,
    ):
        # Configure mocks
        mock_boto_client.return_value = Mock()
        mock_requests.return_value = Mock()
        mock_keyring.return_value = "mock-api-key"  # Fallback for keyring calls

        try:
            yield {
                "boto_client": mock_boto_client,
                "requests": mock_requests,
                "keyring": mock_keyring,
            }
        finally:
            # Restore original environment
            for key, original_value in original_env.items():
                if original_value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = original_value


# Shared media service mock for tests that need a simple stub
@pytest.fixture
def mock_media_service() -> Mock:
    """Provide a basic mock media service with predictable outputs.

    Some tests (e.g., translation integration in MediaEnricher tests) expect a
    fixture named `mock_media_service` to be available at module scope.
    """
    service = Mock()
    service.generate_audio.return_value = "/fake/audio.mp3"
    service.generate_image.return_value = "/fake/image.jpg"
    service.generate_or_get_audio.return_value = "/fake/audio.mp3"
    service.generate_or_get_image.return_value = "/fake/image.jpg"

    # Add Path attributes needed by AnkiBackend
    import tempfile
    from pathlib import Path

    temp_dir = Path(tempfile.mkdtemp())
    service._audio_dir = temp_dir / "audio"
    service._images_dir = temp_dir / "images"

    return service
