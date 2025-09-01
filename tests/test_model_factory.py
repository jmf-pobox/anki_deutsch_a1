"""
Tests for ModelFactory implementation.

This module tests the factory that creates appropriate FieldProcessor instances
based on note type detection patterns. The factory now supports Clean Pipeline
Architecture where certain word types (noun, adjective, adverb, negation, verb, phrase)
return
None and are handled by the Records system instead.
"""

import pytest

from langlearn.models.field_processor import FieldProcessor
from langlearn.models.model_factory import ModelFactory
from langlearn.models.preposition import Preposition


class TestModelFactory:
    """Test ModelFactory note type detection and instance creation."""

    def test_adjective_detection_patterns(self) -> None:
        """Test adjective note type name patterns (Clean Pipeline - returns None)."""
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
            # Clean Pipeline Architecture: adjectives return None (handled by Records)
            assert processor is None, (
                f"Expected None for Clean Pipeline type: {note_type}"
            )

    def test_noun_detection_patterns(self) -> None:
        """Test noun note type name patterns (Clean Pipeline - returns None)."""
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
            # Clean Pipeline Architecture: nouns return None (handled by Records)
            assert processor is None, (
                f"Expected None for Clean Pipeline type: {note_type}"
            )

    def test_adverb_detection_patterns(self) -> None:
        """Test adverb note type name patterns (Clean Pipeline - returns None)."""
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
            # Clean Pipeline Architecture: adverbs return None (handled by Records)
            assert processor is None, (
                f"Expected None for Clean Pipeline type: {note_type}"
            )

    def test_negation_detection_patterns(self) -> None:
        """Test negation note type name patterns (Clean Pipeline - returns None)."""
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
            # Clean Pipeline Architecture: negations return None (handled by Records)
            assert processor is None, (
                f"Expected None for Clean Pipeline type: {note_type}"
            )

    def test_create_verb_processor(self) -> None:
        """Test that verb returns None (handled by Clean Pipeline)."""
        processor = ModelFactory.create_field_processor("German Verb")

        assert processor is None, (
            "Verb types should return None - handled by Clean Pipeline Architecture"
        )

    def test_verb_detection_patterns(self) -> None:
        """Test various verb note type name patterns return None (Clean Pipeline)."""
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
            assert processor is None, (
                f"Verb type '{note_type}' should return None - Clean Pipeline handles"
            )

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
        """Test that phrase returns None (handled by Clean Pipeline)."""
        processor = ModelFactory.create_field_processor("German Phrase")

        assert processor is None, (
            "Phrase types should return None - handled by Clean Pipeline Architecture"
        )

    def test_phrase_detection_patterns(self) -> None:
        """Test various phrase note type name patterns return None (Clean Pipeline)."""
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
            assert processor is None, (
                f"Phrase type '{note_type}' should return None - Clean Pipeline handles"
            )

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
        """Test case insensitive detection (Clean Pipeline - returns None)."""
        variants = [
            "adjective",
            "Adjective",
            "ADJECTIVE",
            "AdJeCtIvE",
        ]

        for variant in variants:
            processor = ModelFactory.create_field_processor(variant)
            # Clean Pipeline Architecture: adjectives return None (handled by Records)
            assert processor is None

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
