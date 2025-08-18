"""
Model factory for creating appropriate FieldProcessor instances.

This factory implements the detection logic for determining which domain model
should handle field processing based on note type names or field patterns.
"""

from .adjective import Adjective
from .adverb import Adverb
from .field_processor import FieldProcessor
from .negation import Negation
from .noun import Noun
from .phrase import Phrase
from .preposition import Preposition
from .verb import Verb


class ModelFactory:
    """Factory for creating FieldProcessor instances based on note type detection."""

    @classmethod
    def create_field_processor(cls, note_type_name: str) -> FieldProcessor | None:
        """Create appropriate FieldProcessor for the given note type.

        Args:
            note_type_name: Name of the Anki note type to process

        Returns:
            FieldProcessor instance for the note type, or None if unsupported
        """
        note_type_lower = note_type_name.lower()

        # Adjective detection
        if "adjective" in note_type_lower:
            return Adjective(
                word="",
                english="",
                example="",
                comparative="",
                superlative="",
                word_audio="",
                example_audio="",
                image_path="",
            )

        # Noun detection
        if "noun" in note_type_lower:
            return Noun(
                noun="",
                article="",
                english="",
                plural="",
                example="",
                related="",
                word_audio="",
                example_audio="",
                image_path="",
            )

        # Adverb detection
        if "adverb" in note_type_lower:
            from .adverb import AdverbType

            return Adverb(
                word="",
                english="",
                type=AdverbType.MANNER,  # Default type
                example="",
                word_audio="",
                example_audio="",
                image_path="",
            )

        # Negation detection
        if "negation" in note_type_lower:
            from .negation import NegationType

            return Negation(
                word="",
                english="",
                type=NegationType.GENERAL,  # Default type
                example="",
                word_audio="",
                example_audio="",
                image_path="",
            )

        # Verb detection
        if "verb" in note_type_lower:
            return Verb(
                verb="",
                english="",
                present_ich="",
                present_du="",
                present_er="",
                perfect="",
                example="",
                word_audio="",
                example_audio="",
                image_path="",
            )

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

        # Phrase detection
        if "phrase" in note_type_lower:
            return Phrase(
                phrase="",
                english="",
                context="",
                related="",
                phrase_audio="",
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
