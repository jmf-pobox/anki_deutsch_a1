"""Tests for the Anthropic service."""

import os
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from anthropic.types import Message
from pydantic import BaseModel

from langlearn.services.anthropic_service import AnthropicService


class MockModel(BaseModel):
    """Generic test model for testing the Anthropic service."""

    word: str
    english: str
    example: str


@pytest.fixture
def mock_anthropic() -> Generator[MagicMock, None, None]:
    """Fixture for mocking the Anthropic client."""
    with patch("anthropic.Anthropic") as mock:
        yield mock


@pytest.fixture
def mock_keyring() -> Generator[MagicMock, None, None]:
    """Fixture for mocking the keyring."""
    with patch("keyring.get_password") as mock:
        mock.return_value = None
        yield mock


@pytest.fixture
def anthropic_service() -> AnthropicService:
    """Fixture for creating an AnthropicService instance."""
    return AnthropicService()


def test_anthropic_service_initialization(mock_keyring: MagicMock) -> None:
    """Test that the service raises ValueError when API key is not set."""
    # Store original value
    original_env = os.environ.get("ANTHROPIC_API_KEY")

    # Remove environment variable to force keyring fallback
    if "ANTHROPIC_API_KEY" in os.environ:
        del os.environ["ANTHROPIC_API_KEY"]

    try:
        # Mock keyring to return None (simulating missing credentials)
        mock_keyring.return_value = None

        # Should only fail if we're not in a test environment
        # In CI, this test should be skipped since credentials should be available
        if os.environ.get("CI") == "true":
            pytest.skip("Skipping credential validation test in CI environment")

        with pytest.raises(
            ValueError,
            match="Key ANTHROPIC_API_KEY not found in environment or keyring",
        ):
            AnthropicService()
    finally:
        # Restore original environment
        if original_env is not None:
            os.environ["ANTHROPIC_API_KEY"] = original_env


def test_generate_pexels_query(anthropic_service: AnthropicService) -> None:
    """Test generating a Pexels query from a model."""
    # Create test model
    test_model = MockModel(
        word="groß",
        english="big",
        example="Das Haus ist groß.",
    )

    # Generate query
    query = anthropic_service.generate_pexels_query(test_model)

    # Verify results
    assert isinstance(query, str)
    assert len(query) > 0
    # Query should be semantically related to the input
    assert any(
        word.lower() in query.lower()
        for word in [
            "big",
            "large",
            "huge",
            "tall",
            "house",
            "building",
            "size",
            "groß",
        ]
    ), f"Query '{query}' does not contain any expected semantic terms"


def test_prompt_creation(anthropic_service: AnthropicService) -> None:
    """Test prompt creation through the public interface."""
    test_model = MockModel(
        word="groß",
        english="big",
        example="Das Haus ist groß.",
    )

    # Setup mock response
    mock_content = {"text": "test query"}
    mock_response = MagicMock(spec=Message)
    mock_response.content = [mock_content]
    mock_messages = MagicMock()
    mock_messages.create.return_value = mock_response
    mock_client = MagicMock()
    mock_client.messages = mock_messages
    anthropic_service.client = mock_client

    # Generate query to test prompt creation
    anthropic_service.generate_pexels_query(test_model)

    # Verify the prompt was created correctly
    call_args = mock_messages.create.call_args
    assert call_args is not None
    prompt = call_args[1]["messages"][0]["content"]
    assert "groß" in prompt
    assert "big" in prompt
    assert "concrete, visual" in prompt


@pytest.mark.live
def test_live_generate_pexels_query() -> None:
    """Live test for generating a Pexels query."""
    # Use service constructor which checks environment variables first, then keyring
    try:
        service = AnthropicService()
    except ValueError as e:
        if "not found in environment or keyring" in str(e):
            pytest.skip("ANTHROPIC_API_KEY not available in environment or keyring")
        raise
    test_model = MockModel(
        word="groß",
        english="big",
        example="Das Haus ist groß.",
    )

    query = service.generate_pexels_query(test_model)

    assert isinstance(query, str)
    assert len(query) > 0
    # Query should be semantically related to the input
    assert any(
        word.lower() in query.lower()
        for word in [
            "big",
            "large",
            "huge",
            "tall",
            "house",
            "building",
            "size",
            "groß",
        ]
    ), f"Query '{query}' does not contain any expected semantic terms"
