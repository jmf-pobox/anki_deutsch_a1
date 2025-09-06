"""Tests for MediaGenerationCapable protocol."""

from typing import TYPE_CHECKING

from langlearn.protocols.image_query_generation_protocol import (
    ImageQueryGenerationProtocol,
)
from langlearn.protocols.media_generation_protocol import MediaGenerationCapable

if TYPE_CHECKING:
    from collections.abc import Callable


class MockMediaGenerationCapable:
    """Mock implementation of MediaGenerationCapable for testing."""

    def get_image_search_strategy(
        self, anthropic_service: ImageQueryGenerationProtocol
    ) -> "Callable[[], str]":
        """Return a mock strategy that generates test search terms."""

        def strategy() -> str:
            return "context-aware search terms"

        return strategy

    def get_combined_audio_text(self) -> str:
        """Return mock audio text."""
        return "test audio text"

    def get_audio_segments(self) -> dict[str, str]:
        """Return mock audio segments."""
        return {
            "word_audio": "test audio text",
            "example_audio": "test example audio",
        }


class TestMediaGenerationCapable:
    """Test MediaGenerationCapable protocol compliance."""

    def test_protocol_compliance(self) -> None:
        """Test that mock class satisfies the protocol."""
        mock = MockMediaGenerationCapable()

        # This should not raise any type errors
        assert isinstance(mock, MediaGenerationCapable)

    def test_get_image_search_strategy_returns_callable(self) -> None:
        """Test that get_image_search_strategy returns a callable."""
        from unittest.mock import Mock

        mock = MockMediaGenerationCapable()
        mock_service = Mock(spec=ImageQueryGenerationProtocol)
        strategy = mock.get_image_search_strategy(mock_service)

        assert callable(strategy)
        assert strategy() == "context-aware search terms"

    def test_get_combined_audio_text_returns_string(self) -> None:
        """Test that get_combined_audio_text returns a string."""
        mock = MockMediaGenerationCapable()
        result = mock.get_combined_audio_text()

        assert isinstance(result, str)
        assert result == "test audio text"

    def test_protocol_with_domain_model_interface(self) -> None:
        """Test protocol works with domain model interface."""
        from unittest.mock import Mock

        def use_media_capable(
            obj: MediaGenerationCapable, service: ImageQueryGenerationProtocol
        ) -> tuple[str, str]:
            """Function that uses MediaGenerationCapable protocol."""
            strategy = obj.get_image_search_strategy(service)
            audio_text = obj.get_combined_audio_text()
            return strategy(), audio_text

        mock = MockMediaGenerationCapable()
        mock_service = Mock(spec=ImageQueryGenerationProtocol)
        result = use_media_capable(mock, mock_service)

        assert result == ("context-aware search terms", "test audio text")
