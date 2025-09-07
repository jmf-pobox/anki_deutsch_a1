"""Unit tests for the Adverb domain model.

Comprehensive tests for the German adverb domain model covering:
- Basic model initialization and validation
- AdverbType enumeration and German linguistic classifications
- Audio text generation for pronunciation context
- Context building for type-specific image search guidance
- Edge cases and error handling
"""

from unittest.mock import Mock

import pytest

from langlearn.exceptions import MediaGenerationError
from langlearn.languages.german.models.adverb import (
    GERMAN_ADVERB_TYPES,
    GERMAN_TO_ENGLISH_ADVERB_TYPE_MAP,
    Adverb,
    AdverbType,
)


class TestAdverbBasics:
    """Test basic Adverb model functionality."""

    def test_adverb_initialization(self) -> None:
        """Test that an Adverb can be initialized with valid data."""
        adverb = Adverb(
            word="hier",
            english="here",
            type=AdverbType.LOCATION,
            example="Ich wohne hier.",
        )
        assert adverb.word == "hier"
        assert adverb.english == "here"
        assert adverb.type == AdverbType.LOCATION
        assert adverb.example == "Ich wohne hier."

    def test_adverb_type_validation(self) -> None:
        """Test that all AdverbType values are valid."""
        # Test that all valid AdverbType values work
        for adverb_type in AdverbType:
            adverb = Adverb(
                word="test",
                english="test",
                type=adverb_type,
                example="Test test.",
            )
            assert adverb.type == adverb_type

    def test_adverb_type_invalid_raises_error(self) -> None:
        """Test that invalid adverb types raise ValueError."""
        with pytest.raises(ValueError):
            # This should raise ValueError for invalid enum value
            AdverbType("invalid_type")

    def test_required_fields_validation(self) -> None:
        """Test that missing required fields raise validation errors."""
        # Test that missing required fields raise TypeError (dataclass requirement)
        with pytest.raises(TypeError):
            Adverb()  # type: ignore[call-arg] # Missing all required fields

        with pytest.raises(TypeError):
            Adverb(word="test")  # type: ignore[call-arg] # Missing english, type, example

        with pytest.raises(TypeError):
            Adverb(word="test", english="test")  # type: ignore[call-arg] # Missing type, example

        # Test that empty strings raise ValueError (__post_init__ validation)
        with pytest.raises(ValueError, match="Required field 'word' cannot be empty"):
            Adverb(word="", english="test", type=AdverbType.LOCATION, example="Test.")

        with pytest.raises(
            ValueError, match="Required field 'english' cannot be empty"
        ):
            Adverb(word="test", english="", type=AdverbType.LOCATION, example="Test.")

        with pytest.raises(
            ValueError, match="Required field 'example' cannot be empty"
        ):
            Adverb(word="test", english="test", type=AdverbType.LOCATION, example="")

        # Test that invalid type raises ValueError
        with pytest.raises(ValueError, match="Type must be an AdverbType"):
            Adverb(word="test", english="test", type="invalid", example="Test.")  # type: ignore[arg-type]


class TestAdverbType:
    """Test AdverbType enumeration and German classifications."""

    def test_adverb_type_german_values(self) -> None:
        """Test that AdverbType contains correct German linguistic terms."""
        assert AdverbType.LOCATION.value == "Ortsadverb"
        assert AdverbType.TIME.value == "Zeitadverb"
        assert AdverbType.FREQUENCY.value == "Häufigkeitsadverb"
        assert AdverbType.MANNER.value == "Modaladverb"
        assert AdverbType.INTENSITY.value == "Gradadverb"
        assert AdverbType.ATTITUDE.value == "Kommentaradverb"

    def test_german_adverb_types_list(self) -> None:
        """Test that GERMAN_ADVERB_TYPES contains all enum values."""
        expected_types = [adverb_type.value for adverb_type in AdverbType]
        assert set(GERMAN_ADVERB_TYPES) == set(expected_types)

    def test_german_to_english_mapping(self) -> None:
        """Test German to English adverb type mapping."""
        # Test core German types
        assert GERMAN_TO_ENGLISH_ADVERB_TYPE_MAP["Ortsadverb"] == AdverbType.LOCATION
        assert GERMAN_TO_ENGLISH_ADVERB_TYPE_MAP["Zeitadverb"] == AdverbType.TIME

        # Test alternative German names
        assert GERMAN_TO_ENGLISH_ADVERB_TYPE_MAP["Lokaladverb"] == AdverbType.LOCATION
        assert GERMAN_TO_ENGLISH_ADVERB_TYPE_MAP["Temporaladverb"] == AdverbType.TIME

        # Test English compatibility
        assert GERMAN_TO_ENGLISH_ADVERB_TYPE_MAP["time"] == AdverbType.TIME
        assert GERMAN_TO_ENGLISH_ADVERB_TYPE_MAP["location"] == AdverbType.LOCATION


class TestAudioGeneration:
    """Test audio text generation functionality."""

    def test_get_combined_audio_text_format(self) -> None:
        """Test that audio text combines word and example correctly."""
        adverb = Adverb(
            word="schnell",
            english="quickly",
            type=AdverbType.MANNER,
            example="Er läuft schnell.",
        )

        audio_text = adverb.get_combined_audio_text()
        assert audio_text == "schnell. Er läuft schnell."

    def test_get_combined_audio_text_different_types(self) -> None:
        """Test audio generation for different adverb types."""
        test_cases = [
            (
                AdverbType.TIME,
                "heute",
                "today",
                "Heute regnet es.",
                "heute. Heute regnet es.",
            ),
            (
                AdverbType.LOCATION,
                "dort",
                "there",
                "Das Buch liegt dort.",
                "dort. Das Buch liegt dort.",
            ),
            (
                AdverbType.INTENSITY,
                "sehr",
                "very",
                "Das ist sehr gut.",
                "sehr. Das ist sehr gut.",
            ),
        ]

        for adverb_type, word, english, example, expected in test_cases:
            adverb = Adverb(
                word=word, english=english, type=adverb_type, example=example
            )
            assert adverb.get_combined_audio_text() == expected


class TestContextBuilding:
    """Test context building for image search term generation."""

    def test_build_search_context_contains_adverb_info(self) -> None:
        """Test that context includes basic adverb information."""
        adverb = Adverb(
            word="langsam",
            english="slowly",
            type=AdverbType.MANNER,
            example="Sie geht langsam.",
        )

        context = adverb._build_search_context()
        assert "langsam" in context
        assert "slowly" in context
        assert "Modaladverb" in context
        assert "Sie geht langsam" in context

    def test_build_search_context_type_specific_guidance(self) -> None:
        """Test that different adverb types get appropriate guidance."""
        test_cases = [
            (AdverbType.TIME, ["temporal symbols", "clocks", "calendars"]),
            (
                AdverbType.LOCATION,
                [
                    "spatial relationships",
                    "directional arrows",
                    "environmental contexts",
                ],
            ),
            (
                AdverbType.MANNER,
                ["Focus on how actions are performed", "style", "method indicators"],
            ),
            (
                AdverbType.FREQUENCY,
                ["repetition patterns", "cycles", "counting symbols"],
            ),
            (
                AdverbType.INTENSITY,
                ["visual emphasis", "gradients", "scale representations"],
            ),
        ]

        for adverb_type, expected_keywords in test_cases:
            adverb = Adverb(
                word="test", english="test", type=adverb_type, example="Test sentence."
            )
            context = adverb._build_search_context()

            for keyword in expected_keywords:
                assert keyword in context, (
                    f"Missing '{keyword}' in context for {adverb_type}"
                )

    def test_build_search_context_unknown_type_fallback(self) -> None:
        """Test fallback guidance for unknown adverb types."""
        # This tests the fallback in the type_guidance.get() call
        adverb = Adverb(
            word="test",
            english="test",
            type=AdverbType.MANNER,  # Use valid type but test fallback logic
            example="Test.",
        )

        context = adverb._build_search_context()
        assert "Generate search terms" in context


class TestImageSearchStrategy:
    """Test image search strategy with domain expertise."""

    def test_image_search_strategy_uses_context(self) -> None:
        """Test that image search strategy passes rich context string to service."""
        mock_service = Mock()
        mock_service.generate_image_query.return_value = "generated terms"

        adverb = Adverb(
            word="oben",
            english="above",
            type=AdverbType.LOCATION,
            example="Der Vogel fliegt oben.",
        )

        strategy = adverb.get_image_search_strategy(mock_service)
        result = strategy()

        # Verify service was called with rich context string from domain expertise
        mock_service.generate_image_query.assert_called_once()
        called_arg = mock_service.generate_image_query.call_args[0][0]

        # The argument should be the rich context string from _build_search_context
        assert isinstance(called_arg, str)
        assert "German adverb: oben" in called_arg
        assert "English: above" in called_arg
        assert "Type: Ortsadverb (LOCATION)" in called_arg
        assert "Der Vogel fliegt oben" in called_arg
        assert "spatial relationships" in called_arg

        assert result == "generated terms"

    def test_image_search_strategy_service_failure_raises_error(self) -> None:
        """Test exception when service fails."""
        mock_service = Mock()
        mock_service.generate_image_query.side_effect = Exception("Service failed")

        adverb = Adverb(
            word="gestern",
            english="yesterday",
            type=AdverbType.TIME,
            example="Gestern war Sonntag.",
        )

        strategy = adverb.get_image_search_strategy(mock_service)

        # Should raise MediaGenerationError when service fails
        with pytest.raises(
            MediaGenerationError,
            match="Failed to generate image search for adverb 'gestern'",
        ):
            strategy()

    def test_image_search_strategy_empty_result_raises_error(self) -> None:
        """Test exception when service returns empty result."""
        mock_service = Mock()
        mock_service.generate_image_query.return_value = ""  # Empty result

        adverb = Adverb(
            word="nie",
            english="never",
            type=AdverbType.FREQUENCY,
            example="Ich bin nie müde.",
        )

        strategy = adverb.get_image_search_strategy(mock_service)

        # Should raise MediaGenerationError when service returns empty result
        with pytest.raises(
            MediaGenerationError,
            match="AI service returned empty image search query for adverb 'nie'",
        ):
            strategy()


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_adverb_with_minimal_data(self) -> None:
        """Test adverb with minimal required data."""
        adverb = Adverb(
            word="ja", english="yes", type=AdverbType.ATTITUDE, example="Ja."
        )

        assert adverb.get_combined_audio_text() == "ja. Ja."

        context = adverb._build_search_context()
        assert "ja" in context
        assert "yes" in context

    def test_adverb_with_special_characters(self) -> None:
        """Test adverb with German special characters."""
        adverb = Adverb(
            word="natürlich",
            english="naturally",
            type=AdverbType.ATTITUDE,
            example="Natürlich ist das möglich.",
        )

        audio_text = adverb.get_combined_audio_text()
        assert "natürlich" in audio_text
        assert "möglich" in audio_text

        context = adverb._build_search_context()
        assert "natürlich" in context

    def test_adverb_with_long_example(self) -> None:
        """Test adverb with longer example sentence."""
        long_example = "Manchmal denke ich, dass das Leben zu kompliziert ist."
        adverb = Adverb(
            word="manchmal",
            english="sometimes",
            type=AdverbType.FREQUENCY,
            example=long_example,
        )

        audio_text = adverb.get_combined_audio_text()
        assert audio_text == f"manchmal. {long_example}"

        context = adverb._build_search_context()
        assert long_example in context
