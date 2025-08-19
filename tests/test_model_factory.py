"""
Tests for ModelFactory implementation.

This module tests the factory that creates appropriate FieldProcessor instances
based on note type detection patterns.
"""

import pytest

from langlearn.models.adjective import Adjective
from langlearn.models.adverb import Adverb
from langlearn.models.field_processor import FieldProcessor
from langlearn.models.model_factory import ModelFactory
from langlearn.models.negation import Negation
from langlearn.models.noun import Noun
from langlearn.models.phrase import Phrase
from langlearn.models.preposition import Preposition
from langlearn.models.verb import Verb


class TestModelFactory:
    """Test ModelFactory note type detection and instance creation."""

    @pytest.mark.skip(reason="FieldProcessor interface deprecated")
    def test_create_adjective_processor(self) -> None:
        """Test creating adjective field processor."""
        processor = ModelFactory.create_field_processor("German Adjective")

        assert processor is not None
        assert isinstance(processor, Adjective)
        assert isinstance(processor, FieldProcessor)

    @pytest.mark.skip(reason="FieldProcessor interface deprecated")
    def test_create_noun_processor(self) -> None:
        """Test creating noun field processor."""
        processor = ModelFactory.create_field_processor("German Noun")

        assert processor is not None
        assert isinstance(processor, Noun)
        assert isinstance(processor, FieldProcessor)

    def test_adjective_detection_patterns(self) -> None:
        """Test various adjective note type name patterns."""
        test_cases = [
            "German Adjective",
            "adjective",
            "Adjective with Media",
            "German Adjective Cards",
            "ADJECTIVE",
            "Basic Adjective",
        ]

        for note_type in test_cases:
            processor = ModelFactory.create_field_processor(note_type)
            assert processor is not None, f"Failed to detect adjective in: {note_type}"
            assert isinstance(processor, Adjective)

    def test_noun_detection_patterns(self) -> None:
        """Test various noun note type name patterns."""
        test_cases = [
            "German Noun",
            "noun",
            "Noun with Media",
            "German Noun Cards",
            "NOUN",
            "Basic Noun",
        ]

        for note_type in test_cases:
            processor = ModelFactory.create_field_processor(note_type)
            assert processor is not None, f"Failed to detect noun in: {note_type}"
            assert isinstance(processor, Noun)

    @pytest.mark.skip(reason="FieldProcessor interface deprecated")
    def test_create_adverb_processor(self) -> None:
        """Test creating adverb field processor."""
        processor = ModelFactory.create_field_processor("German Adverb")

        assert processor is not None
        assert isinstance(processor, Adverb)
        assert isinstance(processor, FieldProcessor)

    def test_adverb_detection_patterns(self) -> None:
        """Test various adverb note type name patterns."""
        test_cases = [
            "German Adverb",
            "adverb",
            "Adverb with Media",
            "German Adverb Cards",
            "ADVERB",
            "Basic Adverb",
        ]

        for note_type in test_cases:
            processor = ModelFactory.create_field_processor(note_type)
            assert processor is not None, f"Failed to detect adverb in: {note_type}"
            assert isinstance(processor, Adverb)

    @pytest.mark.skip(reason="FieldProcessor interface deprecated")
    def test_create_negation_processor(self) -> None:
        """Test creating negation field processor."""
        processor = ModelFactory.create_field_processor("German Negation")

        assert processor is not None
        assert isinstance(processor, Negation)
        assert isinstance(processor, FieldProcessor)

    def test_negation_detection_patterns(self) -> None:
        """Test various negation note type name patterns."""
        test_cases = [
            "German Negation",
            "negation",
            "Negation with Media",
            "German Negation Cards",
            "NEGATION",
            "Basic Negation",
        ]

        for note_type in test_cases:
            processor = ModelFactory.create_field_processor(note_type)
            assert processor is not None, f"Failed to detect negation in: {note_type}"
            assert isinstance(processor, Negation)

    def test_create_verb_processor(self) -> None:
        """Test creating verb field processor."""
        processor = ModelFactory.create_field_processor("German Verb")

        assert processor is not None
        assert isinstance(processor, Verb)
        assert isinstance(processor, FieldProcessor)

    def test_verb_detection_patterns(self) -> None:
        """Test various verb note type name patterns."""
        test_cases = [
            "German Verb",
            "verb",
            "Verb with Media",
            "German Verb Cards",
            "VERB",
            "Basic Verb",
        ]

        for note_type in test_cases:
            processor = ModelFactory.create_field_processor(note_type)
            assert processor is not None, f"Failed to detect verb in: {note_type}"
            assert isinstance(processor, Verb)

    def test_create_preposition_processor(self) -> None:
        """Test creating preposition field processor."""
        processor = ModelFactory.create_field_processor("German Preposition")

        assert processor is not None
        assert isinstance(processor, Preposition)
        assert isinstance(processor, FieldProcessor)

    def test_preposition_detection_patterns(self) -> None:
        """Test various preposition note type name patterns."""
        test_cases = [
            "German Preposition",
            "preposition",
            "Preposition with Media",
            "German Preposition Cards",
            "PREPOSITION",
            "Basic Preposition",
        ]

        for note_type in test_cases:
            processor = ModelFactory.create_field_processor(note_type)
            assert processor is not None, (
                f"Failed to detect preposition in: {note_type}"
            )
            assert isinstance(processor, Preposition)

    def test_create_phrase_processor(self) -> None:
        """Test creating phrase field processor."""
        processor = ModelFactory.create_field_processor("German Phrase")

        assert processor is not None
        assert isinstance(processor, Phrase)
        assert isinstance(processor, FieldProcessor)

    def test_phrase_detection_patterns(self) -> None:
        """Test various phrase note type name patterns."""
        test_cases = [
            "German Phrase",
            "phrase",
            "Phrase with Media",
            "German Phrase Cards",
            "PHRASE",
            "Basic Phrase",
        ]

        for note_type in test_cases:
            processor = ModelFactory.create_field_processor(note_type)
            assert processor is not None, f"Failed to detect phrase in: {note_type}"
            assert isinstance(processor, Phrase)

    def test_unsupported_note_types(self) -> None:
        """Test that unsupported note types return None."""
        unsupported_types = [
            "German Article",  # Not implemented
            "German Conjunction",  # Not implemented
            "Random Card Type",
            "Basic",
            "",
            "Some Other Type",
        ]

        for note_type in unsupported_types:
            processor = ModelFactory.create_field_processor(note_type)
            assert processor is None, f"Unexpectedly supported: {note_type}"

    def test_case_insensitive_detection(self) -> None:
        """Test that note type detection is case insensitive."""
        variants = [
            "adjective",
            "Adjective",
            "ADJECTIVE",
            "AdJeCtIvE",
        ]

        for variant in variants:
            processor = ModelFactory.create_field_processor(variant)
            assert processor is not None
            assert isinstance(processor, Adjective)

    def test_get_supported_note_types(self) -> None:
        """Test getting list of supported note types."""
        supported = ModelFactory.get_supported_note_types()

        assert isinstance(supported, list)
        assert "adjective" in supported
        assert len(supported) >= 1

        # All should be lowercase
        for note_type in supported:
            assert note_type.islower()

    def test_is_supported_note_type(self) -> None:
        """Test checking if note types are supported."""
        # Supported types
        assert ModelFactory.is_supported_note_type("German Adjective") is True
        assert ModelFactory.is_supported_note_type("adjective") is True
        assert ModelFactory.is_supported_note_type("ADJECTIVE CARD") is True
        assert ModelFactory.is_supported_note_type("German Noun") is True
        assert ModelFactory.is_supported_note_type("noun") is True
        assert ModelFactory.is_supported_note_type("NOUN CARD") is True
        assert ModelFactory.is_supported_note_type("German Adverb") is True
        assert ModelFactory.is_supported_note_type("adverb") is True
        assert ModelFactory.is_supported_note_type("ADVERB CARD") is True
        assert ModelFactory.is_supported_note_type("German Negation") is True
        assert ModelFactory.is_supported_note_type("negation") is True
        assert ModelFactory.is_supported_note_type("NEGATION CARD") is True
        assert ModelFactory.is_supported_note_type("German Verb") is True
        assert ModelFactory.is_supported_note_type("verb") is True
        assert ModelFactory.is_supported_note_type("VERB CARD") is True
        assert ModelFactory.is_supported_note_type("German Preposition") is True
        assert ModelFactory.is_supported_note_type("preposition") is True
        assert ModelFactory.is_supported_note_type("PREPOSITION CARD") is True
        assert ModelFactory.is_supported_note_type("German Phrase") is True
        assert ModelFactory.is_supported_note_type("phrase") is True
        assert ModelFactory.is_supported_note_type("PHRASE CARD") is True

        # Unsupported types
        assert ModelFactory.is_supported_note_type("Random Type") is False
        assert ModelFactory.is_supported_note_type("") is False

    @pytest.mark.skip(reason="FieldProcessor interface deprecated")
    def test_created_processor_field_layout(self) -> None:
        """Test that created processors have correct field layout."""
        processor = ModelFactory.create_field_processor("German Adjective")

        assert processor is not None
        assert processor.get_expected_field_count() == 8

        field_names = processor._get_field_names()
        expected_names = [
            "Word",
            "English",
            "Example",
            "Comparative",
            "Superlative",
            "Image",
            "WordAudio",
            "ExampleAudio",
        ]
        assert field_names == expected_names

    @pytest.mark.skip(reason="FieldProcessor interface deprecated")
    def test_created_processor_functionality(self) -> None:
        """Test that created processors are fully functional."""
        from langlearn.services.domain_media_generator import MockDomainMediaGenerator

        processor = ModelFactory.create_field_processor("German Adjective")
        mock_generator = MockDomainMediaGenerator()

        fields = [
            "schön",
            "beautiful",
            "Das ist schön.",
            "schöner",
            "am schönsten",
            "",
            "",
            "",
        ]

        assert processor is not None  # Type guard
        result = processor.process_fields_for_media_generation(fields, mock_generator)

        assert len(result) == 8
        assert result[0] == "schön"
        assert len(mock_generator.audio_calls) > 0

    def test_factory_expansion_readiness(self) -> None:
        """Test that factory structure supports future model additions."""
        # This test ensures the factory pattern supports easy expansion
        # when other models implement FieldProcessor

        # Current state
        assert ModelFactory.is_supported_note_type("adjective") is True

        # Current supported types
        assert ModelFactory.is_supported_note_type("noun") is True  # Now implemented

        # Current supported types
        assert ModelFactory.is_supported_note_type("adverb") is True  # Now implemented

        # Current supported types
        assert (
            ModelFactory.is_supported_note_type("negation") is True
        )  # Now implemented

        # All main models are now implemented
        assert ModelFactory.is_supported_note_type("verb") is True
        assert ModelFactory.is_supported_note_type("preposition") is True
        assert ModelFactory.is_supported_note_type("phrase") is True

        # These should be False now but will be True when implemented
        future_types = ["article", "conjunction"]
        for future_type in future_types:
            assert ModelFactory.is_supported_note_type(future_type) is False

        # Factory should handle None returns gracefully for unsupported types
        processor = ModelFactory.create_field_processor(
            "article"
        )  # Not yet implemented
        assert processor is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
