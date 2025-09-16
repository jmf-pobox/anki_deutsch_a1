"""Tests for LanguageDomainModel protocol."""

from collections.abc import Callable
from unittest.mock import Mock

from langlearn.protocols.domain_model_protocol import LanguageDomainModel
from langlearn.protocols.image_query_generation_protocol import (
    ImageQueryGenerationProtocol,
)


class MockDomainModel:
    """Mock implementation of LanguageDomainModel for testing."""

    def __init__(
        self,
        combined_audio_text: str = "test audio text",
        audio_segments: dict[str, str] | None = None,
        primary_word: str = "test_word",
        search_strategy: Callable[[], str] | None = None,
    ):
        self._combined_audio_text = combined_audio_text
        self._audio_segments = audio_segments or {
            "word": "test",
            "example": "test sentence",
        }
        self._primary_word = primary_word
        self._search_strategy = search_strategy or (lambda: "test search query")

    def get_combined_audio_text(self) -> str:
        return self._combined_audio_text

    def get_audio_segments(self) -> dict[str, str]:
        return self._audio_segments

    def get_primary_word(self) -> str:
        return self._primary_word

    def get_image_search_strategy(
        self, ai_service: ImageQueryGenerationProtocol
    ) -> Callable[[], str]:
        return self._search_strategy


class TestLanguageDomainModelProtocol:
    """Test LanguageDomainModel protocol compliance and functionality."""

    def test_protocol_compliance(self) -> None:
        """Test that MockDomainModel implements the protocol correctly."""
        mock_model = MockDomainModel()

        # Should be recognized as implementing the protocol
        assert isinstance(mock_model, LanguageDomainModel)

    def test_get_combined_audio_text(self) -> None:
        """Test get_combined_audio_text method."""
        test_audio_text = "Hund. Der Hund ist groß."
        model = MockDomainModel(combined_audio_text=test_audio_text)

        result = model.get_combined_audio_text()

        assert result == test_audio_text
        assert isinstance(result, str)

    def test_get_audio_segments(self) -> None:
        """Test get_audio_segments method returns correct format."""
        test_segments = {
            "word": "Hund",
            "example": "Der Hund ist groß",
            "article": "der",
        }
        model = MockDomainModel(audio_segments=test_segments)

        result = model.get_audio_segments()

        assert result == test_segments
        assert isinstance(result, dict)
        # All values should be strings
        for key, value in result.items():
            assert isinstance(key, str)
            assert isinstance(value, str)

    def test_get_primary_word(self) -> None:
        """Test get_primary_word method."""
        test_word = "Haus"
        model = MockDomainModel(primary_word=test_word)

        result = model.get_primary_word()

        assert result == test_word
        assert isinstance(result, str)

    def test_get_image_search_strategy(self) -> None:
        """Test get_image_search_strategy returns callable."""

        def test_strategy() -> str:
            return "house home building"

        model = MockDomainModel(search_strategy=test_strategy)
        mock_ai_service = Mock(spec=ImageQueryGenerationProtocol)

        strategy = model.get_image_search_strategy(mock_ai_service)

        assert callable(strategy)
        assert strategy() == "house home building"

    def test_image_search_strategy_with_ai_service(self) -> None:
        """Test that image search strategy can use AI service."""
        mock_ai_service = Mock(spec=ImageQueryGenerationProtocol)
        mock_ai_service.generate_image_query.return_value = "enhanced ai terms"

        def ai_enhanced_strategy() -> str:
            # This would use the ai_service in a real implementation
            return str(mock_ai_service.generate_image_query.return_value)

        model = MockDomainModel(search_strategy=ai_enhanced_strategy)

        strategy = model.get_image_search_strategy(mock_ai_service)
        result = strategy()

        assert result == "enhanced ai terms"


class TestProtocolStructuralTyping:
    """Test that protocol works with structural typing (duck typing)."""

    def test_structural_typing_compliance(self) -> None:
        """Test that any object with required methods implements the protocol."""

        class DuckTypedModel:
            """Class that implements protocol methods without explicit inheritance."""

            def get_combined_audio_text(self) -> str:
                return "duck typed audio"

            def get_audio_segments(self) -> dict[str, str]:
                return {"word": "duck"}

            def get_primary_word(self) -> str:
                return "duck"

            def get_image_search_strategy(
                self, ai_service: ImageQueryGenerationProtocol
            ) -> Callable[[], str]:
                return lambda: "duck search terms"

        duck_model = DuckTypedModel()

        # Should be recognized as implementing the protocol via structural typing
        assert isinstance(duck_model, LanguageDomainModel)

    def test_protocol_method_signatures(self) -> None:
        """Test that protocol enforces correct method signatures."""
        mock_model = MockDomainModel()

        # Test method signatures match protocol requirements
        audio_text = mock_model.get_combined_audio_text()
        assert isinstance(audio_text, str)

        audio_segments = mock_model.get_audio_segments()
        assert isinstance(audio_segments, dict)

        primary_word = mock_model.get_primary_word()
        assert isinstance(primary_word, str)

        mock_ai_service = Mock(spec=ImageQueryGenerationProtocol)
        strategy = mock_model.get_image_search_strategy(mock_ai_service)
        assert callable(strategy)

        search_result = strategy()
        assert isinstance(search_result, str)
