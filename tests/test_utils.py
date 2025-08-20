"""Test utilities for mocking external services."""

from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from langlearn.backends.anki_backend import AnkiBackend
from langlearn.deck_builder import DeckBuilder


@pytest.fixture
def mock_aws_services() -> Any:
    """Mock AWS services to avoid requiring credentials in unit tests."""
    with patch("langlearn.services.audio.boto3.client") as mock_boto3:
        mock_polly = MagicMock()
        mock_boto3.return_value = mock_polly
        yield mock_polly


@pytest.fixture
def mock_external_services() -> Any:
    """Mock all external services for unit testing."""
    with (
        patch("langlearn.services.audio.boto3.client") as mock_boto3,
        patch("langlearn.services.pexels_service.PexelsService") as mock_pexels,
        patch(
            "langlearn.services.anthropic_service.AnthropicService"
        ) as mock_anthropic,
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
) -> Generator[AnkiBackend, None, None]:
    """Create an AnkiBackend instance with mocked services via dependency injection."""
    backend = AnkiBackend(
        "Test Deck", "Test description", media_service=mock_media_service
    )
    yield backend
    # Cleanup if needed - removed as AnkiBackend doesn't have cleanup method
    pass


@pytest.fixture
def deck_builder_with_mocks(
    mock_audio_service: Any, mock_pexels_service: Any, mock_media_service: Any
) -> Generator[DeckBuilder, None, None]:
    """Create a DeckBuilder instance with mocked services via dependency injection."""
    builder = DeckBuilder(
        "Test Deck",
        enable_media_generation=True,
        audio_service=mock_audio_service,
        pexels_service=mock_pexels_service,
        media_service=mock_media_service,
    )
    yield builder


@pytest.fixture
def anki_backend_no_aws(
    mock_external_services: Any,
) -> Generator[AnkiBackend, None, None]:
    """Create an AnkiBackend instance with mocked external services."""
    backend = AnkiBackend("Test Deck", "Test description")
    yield backend
    # Cleanup if needed - removed as AnkiBackend doesn't have cleanup method
    pass
