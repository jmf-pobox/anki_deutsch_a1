"""
Model factory for creating appropriate FieldProcessor instances.

This factory implements the detection logic for determining which domain model
should handle field processing based on note type names or field patterns.
"""

from .field_processor import FieldProcessor
from .preposition import Preposition


class ModelFactory:
    """Factory for creating FieldProcessor instances based on note type detection."""

    @classmethod
    def create_field_processor(cls, note_type_name: str) -> FieldProcessor | None:
        """Create appropriate FieldProcessor for the given note type.

        Note: Only returns FieldProcessor instances for legacy types
        (verb, preposition, phrase). Clean Pipeline Architecture types
        (noun, adjective, adverb, negation) return None since they are
        handled by the Clean Pipeline Architecture.

        Args:
            note_type_name: Name of the Anki note type to process

        Returns:
            FieldProcessor instance for legacy note types, or None if Clean Pipeline
        """
        note_type_lower = note_type_name.lower()

        # Clean Pipeline Architecture types - return None (handled by Clean Pipeline)
        clean_pipeline_types = [
            "adjective",
            "noun",
            "adverb",
            "negation",
            "verb",
            "phrase",
        ]
        if any(word_type in note_type_lower for word_type in clean_pipeline_types):
            return None

        # Preposition detection
        if "preposition" in note_type_lower:
            return Preposition(
                preposition="",
                english="",
                case="",
                example1="",
                example2="",
                audio1="",
                audio2="",
                image_path="",
            )

        return None

    @classmethod
    def get_supported_note_types(cls) -> list[str]:
        """Get list of note types that have FieldProcessor implementations.

        Returns:
            List of supported note type names (lowercase)
        """
        return [
            "adjective",
            "noun",
            "adverb",
            "negation",
            "verb",
            "preposition",
            "phrase",
        ]

    @classmethod
    def is_supported_note_type(cls, note_type_name: str) -> bool:
        """Check if a note type is supported by the factory.

        Args:
            note_type_name: Name of the note type to check

        Returns:
            True if the note type is supported
        """
        note_type_lower = note_type_name.lower()
        return any(
            supported_type in note_type_lower
            for supported_type in cls.get_supported_note_types()
        )
