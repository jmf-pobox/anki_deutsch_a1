"""Tests for Noun model MediaGenerationCapable protocol compliance."""

from unittest.mock import Mock

import pytest

from langlearn.exceptions import MediaGenerationError
from langlearn.languages.german.models.noun import Noun
from langlearn.protocols import MediaGenerationCapable
from langlearn.protocols.image_query_generation_protocol import (
    ImageQueryGenerationProtocol,
)


class TestNounProtocolCompliance:
    """Test that Noun implements MediaGenerationCapable protocol."""

    def test_noun_satisfies_protocol(self) -> None:
        """Test that Noun instance satisfies MediaGenerationCapable protocol."""
        noun = Noun(
            noun="Katze",
            article="die",
            english="cat",
            plural="Katzen",
            example="Die Katze schläft auf dem Sofa.",
        )

        # This should pass with @runtime_checkable protocol
        assert isinstance(noun, MediaGenerationCapable)

    def test_protocol_method_implementation(self) -> None:
        """Test that Noun implements required protocol methods."""
        noun = Noun(
            noun="Hund",
            article="der",
            english="dog",
            plural="Hunde",
            example="Der Hund bellt laut.",
        )

        # Test get_image_search_strategy returns callable with mock service
        mock_service = Mock()
        mock_service.generate_image_query.return_value = "mock search terms"

        strategy = noun.get_image_search_strategy(mock_service)
        assert callable(strategy)

        # Test get_combined_audio_text returns string
        audio_text = noun.get_combined_audio_text()
        assert isinstance(audio_text, str)
        assert audio_text == "der Hund, die Hunde"

    def test_protocol_with_dependency_injection(self) -> None:
        """Test protocol works with dependency injection pattern."""

        def use_media_capable(
            obj: MediaGenerationCapable, service: ImageQueryGenerationProtocol
        ) -> tuple[str, str]:
            """Function that uses MediaGenerationCapable protocol."""
            strategy = obj.get_image_search_strategy(service)
            audio_text = obj.get_combined_audio_text()
            return strategy(), audio_text

        noun = Noun(
            noun="Haus",
            article="das",
            english="house",
            plural="Häuser",
            example="Das Haus ist sehr schön.",
        )

        # Test audio text works independently
        audio_text = noun.get_combined_audio_text()
        assert audio_text == "das Haus, die Häuser"

        # Create mock service that fails
        mock_service = Mock()
        mock_service.generate_image_query.side_effect = Exception("Service failed")

        # Should raise MediaGenerationError when service fails (no more fallbacks)
        with pytest.raises(
            MediaGenerationError,
            match="Failed to generate image search for noun 'Haus'",
        ):
            use_media_capable(noun, mock_service)

    def test_protocol_with_mock_anthropic_service(self) -> None:
        """Test protocol works with mock Anthropic service injection."""
        mock_service = Mock()
        mock_service.generate_image_query.return_value = "mocked search terms"

        noun = Noun(
            noun="Auto",
            article="das",
            english="car",
            plural="Autos",
            example="Das Auto fährt schnell.",
        )

        strategy = noun.get_image_search_strategy(mock_service)
        result = strategy()

        assert result == "mocked search terms"
        mock_service.generate_image_query.assert_called_once()

    def test_context_building_for_concrete_noun(self) -> None:
        """Test that concrete nouns build appropriate context."""
        noun = Noun(
            noun="Katze",
            article="die",
            english="cat",
            plural="Katzen",
            example="Die Katze schläft gerne.",
        )

        context = noun._build_search_context()

        # Check that context contains noun information
        assert "Katze" in context
        assert "cat" in context
        assert "die - feminine" in context
        assert "Katzen" in context
        assert "Die Katze schläft gerne" in context

        # Check concrete noun strategy
        assert "Focus on the physical object" in context
        assert "direct visual representation" in context
        assert "Concrete" in context

    def test_context_building_for_abstract_noun(self) -> None:
        """Test that abstract nouns build appropriate context."""
        noun = Noun(
            noun="Freiheit",
            article="die",
            english="freedom",
            plural="",
            example="Freiheit ist wichtig.",
        )

        context = noun._build_search_context()

        # Check that context contains noun information
        assert "Freiheit" in context
        assert "freedom" in context
        assert "die - feminine" in context

        # Check abstract noun strategy
        assert "symbolic imagery" in context
        assert "metaphorical representations" in context
        assert "Abstract" in context

    def test_service_failure_raises_exception_for_concrete_noun(self) -> None:
        """Test exception behavior for concrete nouns when service fails."""
        mock_service = Mock()
        mock_service.generate_image_query.side_effect = Exception("Service failed")

        noun = Noun(
            noun="Hund",
            article="der",
            english="dog",
            plural="Hunde",
            example="Der Hund ist treu.",
        )

        strategy = noun.get_image_search_strategy(mock_service)

        # Should raise MediaGenerationError when AI service fails (no fallbacks)
        with pytest.raises(
            MediaGenerationError,
            match="Failed to generate image search for noun 'Hund'",
        ):
            strategy()

    def test_service_failure_raises_exception_for_abstract_noun(self) -> None:
        """Test exception behavior for abstract nouns when service fails."""
        mock_service = Mock()
        mock_service.generate_image_query.side_effect = Exception("Service failed")

        noun = Noun(
            noun="Liebe",
            article="die",
            english="love",
            plural="",
            example="Liebe ist schön.",
        )

        strategy = noun.get_image_search_strategy(mock_service)

        # Should raise MediaGenerationError when AI service fails (no fallbacks)
        with pytest.raises(
            MediaGenerationError,
            match="Failed to generate image search for noun 'Liebe'",
        ):
            strategy()

    def test_gender_context_in_search_terms(self) -> None:
        """Test that gender context is included in search context."""
        test_cases = [
            ("der", "Hund", "masculine"),
            ("die", "Katze", "feminine"),
            ("das", "Haus", "neuter"),
        ]

        for article, noun_word, expected_gender in test_cases:
            noun = Noun(
                noun=noun_word,
                article=article,
                english="test",
                plural="test",
                example="Test sentence.",
            )

            context = noun._build_search_context()
            assert f"{article} - {expected_gender}" in context
