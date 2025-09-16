"""Test utilities for mocking external services."""

import contextlib
from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from langlearn.core.backends.anki_backend import AnkiBackend
from langlearn.deck_builder import DeckBuilder


# Rate limit detection utilities
def is_rate_limited_error(e: Exception) -> bool:
    """Check if an exception indicates Pexels API rate limiting.

    Detects rate limiting from:
    - HTTP 429 status codes
    - "Too Many Requests" messages
    - Quota exceeded errors
    - Rate limit keywords in error messages
    """
    error_str = str(e).lower()
    rate_limit_indicators = [
        "429",
        "too many requests",
        "rate limit",
        "quota exceeded",
        "requests per hour exceeded",
        "api limit",
    ]
    return any(indicator in error_str for indicator in rate_limit_indicators)


def skip_if_rate_limited(e: Exception, test_name: str = "test") -> None:
    """Skip test if exception indicates rate limiting."""
    if is_rate_limited_error(e):
        pytest.skip(f"Pexels API rate limited during {test_name} - skipping for CI")


def check_rate_limit_in_logs(caplog: pytest.LogCaptureFixture) -> bool:
    """Check if rate limiting was detected in test logs."""
    log_text = caplog.text.lower()
    return is_rate_limited_error(Exception(log_text))


# Common test utilities
@contextlib.contextmanager
def mock_env(var_name: str, value: str | None) -> Generator[None]:
    """Context manager for temporarily setting environment variables."""
    import os

    original = os.environ.get(var_name)
    if value is None:
        if var_name in os.environ:
            del os.environ[var_name]
    else:
        os.environ[var_name] = value
    try:
        yield
    finally:
        # Restore original state
        if original is None:
            os.environ.pop(var_name, None)
        else:
            os.environ[var_name] = original


# Common test fixtures and helpers
@pytest.fixture
def mock_environment_variable() -> Any:
    """Context manager for temporarily setting environment variables."""
    return mock_env


@pytest.fixture
def mock_requests_and_sleep() -> Any:
    """Common fixture for mocking requests.get and time.sleep together."""
    from unittest.mock import Mock, patch

    @contextlib.contextmanager
    def _mock_requests_sleep(**kwargs: Any) -> Generator[tuple[Mock, Mock]]:
        """Context manager that mocks both requests.get and time.sleep.

        Args:
            **kwargs: Arguments to configure the mock response
                - response: Mock response object
                - side_effect: Side effect for requests.get
                - status_code: HTTP status code
                - content: Response content
        """
        mock_response = Mock()
        if "response" in kwargs:
            mock_response = kwargs["response"]
        elif "status_code" in kwargs:
            mock_response.status_code = kwargs["status_code"]
        if "content" in kwargs:
            mock_response.content = kwargs["content"]
        mock_response.raise_for_status.return_value = None

        with patch("requests.get") as mock_get, patch("time.sleep") as mock_sleep:
            if "side_effect" in kwargs:
                mock_get.side_effect = kwargs["side_effect"]
            else:
                mock_get.return_value = mock_response
            yield mock_get, mock_sleep

    return _mock_requests_sleep


@contextlib.contextmanager
def temp_directory_with_nested_path(
    nested_path: str = "nested/path",
) -> Generator[tuple[str, Any]]:
    """Create a temporary directory and yield a nested path within it."""
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as temp_dir:
        nested_dir = Path(temp_dir) / nested_path
        yield temp_dir, nested_dir


@pytest.fixture
def mock_aws_services() -> Any:
    """Mock AWS services to avoid requiring credentials in unit tests."""
    with patch("langlearn.core.services.audio_service.boto3.client") as mock_boto3:
        mock_polly = MagicMock()
        mock_boto3.return_value = mock_polly
        yield mock_polly


@pytest.fixture
def mock_external_services() -> Any:
    """Mock all external services for unit testing."""
    with (
        patch("langlearn.core.services.audio_service.boto3.client") as mock_boto3,
        patch("langlearn.core.services.image_service.PexelsService") as mock_pexels,
        patch("langlearn.core.services.ai_service.AnthropicService") as mock_anthropic,
    ):
        # Configure mock boto3 client
        mock_polly = MagicMock()
        mock_boto3.return_value = mock_polly

        yield {
            "polly": mock_polly,
            "pexels": mock_pexels,
            "anthropic": mock_anthropic,
        }


@pytest.fixture
def mock_audio_service() -> MagicMock:
    """Create a mock AudioService for dependency injection."""
    mock_service = MagicMock()
    mock_service.generate_audio.return_value = "test_audio.mp3"
    mock_service.get_existing_audio.return_value = None
    return mock_service


@pytest.fixture
def mock_pexels_service() -> MagicMock:
    """Create a mock PexelsService for dependency injection."""
    mock_service = MagicMock()
    mock_service.search_photos.return_value = [{"src": {"medium": "test_image.jpg"}}]
    mock_service.download_photo.return_value = "test_image.jpg"
    return mock_service


@pytest.fixture
def mock_media_service(mock_audio_service: Any, mock_pexels_service: Any) -> MagicMock:
    """Create a mock MediaService for dependency injection."""
    mock_service = MagicMock()
    mock_service.generate_or_get_audio.return_value = "[sound:test_audio.mp3]"
    mock_service.generate_or_get_image.return_value = "test_image.jpg"
    mock_service._audio_service = mock_audio_service
    mock_service._pexels_service = mock_pexels_service
    return mock_service


@pytest.fixture
def anki_backend_with_mocks(
    mock_media_service: Any,
) -> Generator[AnkiBackend]:
    """Create an AnkiBackend instance with mocked services via dependency injection."""
    backend = AnkiBackend("Test Deck", mock_media_service, "Test description")
    yield backend
    # Cleanup if needed - removed as AnkiBackend doesn't have cleanup method
    pass


@pytest.fixture
def deck_builder_with_mocks(
    mock_audio_service: Any, mock_pexels_service: Any, mock_media_service: Any
) -> Generator[DeckBuilder]:
    """Create a DeckBuilder instance with mocked services via dependency injection."""
    builder = DeckBuilder(
        "Test Deck",
        audio_service=mock_audio_service,
        pexels_service=mock_pexels_service,
    )
    yield builder


@pytest.fixture
def anki_backend_no_aws(
    mock_external_services: Any,
    mock_media_service: Any,
) -> Generator[AnkiBackend]:
    """Create an AnkiBackend instance with mocked external services."""
    backend = AnkiBackend("Test Deck", mock_media_service, "Test description")
    yield backend
    # Cleanup if needed - removed as AnkiBackend doesn't have cleanup method
    pass
