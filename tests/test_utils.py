"""Test utilities for mocking external services."""

from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest

from langlearn.backends.anki_backend import AnkiBackend


@pytest.fixture
def mock_aws_services():
    """Mock AWS services to avoid requiring credentials in unit tests."""
    with patch('langlearn.services.audio.boto3.client') as mock_boto3:
        mock_polly = MagicMock()
        mock_boto3.return_value = mock_polly
        yield mock_polly


@pytest.fixture
def mock_external_services():
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
def anki_backend_no_aws(mock_external_services) -> Generator[AnkiBackend, None, None]:
    """Create an AnkiBackend instance with mocked external services."""
    backend = AnkiBackend("Test Deck", "Test description")
    yield backend
    # Cleanup if needed
    backend.cleanup()
