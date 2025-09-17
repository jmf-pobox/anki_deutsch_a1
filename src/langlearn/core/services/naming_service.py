"""Centralized naming service for consistent display formatting."""

from __future__ import annotations

from langlearn.core.records.base_record import BaseRecord, RecordType


class NamingService:
    """Service for consistent naming and formatting across the application.

    This service provides a single source of truth for all naming conventions,
    ensuring consistency in:
    - Subdeck names (e.g., "Nouns", "Verbs")
    - Result keys (e.g., "nouns", "verbs")
    - Display names (e.g., "Noun", "Verb")

    The service works with both RecordType enums and BaseRecord instances,
    providing flexibility while maintaining consistency.
    """

    @staticmethod
    def get_subdeck_name(record_or_type: BaseRecord | RecordType | str) -> str:
        """Get the subdeck name for a record or record type.

        Args:
            record_or_type: Can be a BaseRecord instance, RecordType enum, or string

        Returns:
            str: Subdeck name for Anki (e.g., "Nouns", "Verbs")
        """
        if isinstance(record_or_type, BaseRecord):
            return record_or_type.__class__.get_subdeck_name()
        elif isinstance(record_or_type, RecordType):
            # For RecordType enum, use the same mapping as BaseRecord
            subdeck_mapping = {
                RecordType.NOUN: "Nouns",
                RecordType.VERB: "Verbs",
                RecordType.VERB_CONJUGATION: "Verbs",
                RecordType.VERB_IMPERATIVE: "Verbs",
                RecordType.ADJECTIVE: "Adjectives",
                RecordType.ADVERB: "Adverbs",
                RecordType.PREPOSITION: "Prepositions",
                RecordType.PHRASE: "Phrases",
                RecordType.NEGATION: "Negations",
                RecordType.UNIFIED_ARTICLE: "Articles",
                RecordType.ARTICLE: "Articles",
                RecordType.INDEFINITE_ARTICLE: "Articles",
                RecordType.NEGATIVE_ARTICLE: "Articles",
                # Language-specific types
                RecordType.KOREAN_NOUN: "Nouns",
            }
            return subdeck_mapping.get(
                record_or_type, f"{record_or_type.value.title()}s"
            )
        else:
            # String fallback (for legacy code)
            record_type_str = str(record_or_type)
            return record_type_str.replace("_", " ").title() + (
                "s" if not record_type_str.endswith("s") else ""
            )

    @staticmethod
    def get_result_key(record_or_type: BaseRecord | RecordType | str) -> str:
        """Get the result key for card statistics.

        Args:
            record_or_type: Can be a BaseRecord instance, RecordType enum, or string

        Returns:
            str: Result key for statistics (e.g., "nouns", "verbs")
        """
        if isinstance(record_or_type, BaseRecord):
            return record_or_type.__class__.get_result_key()
        elif isinstance(record_or_type, RecordType):
            # For RecordType enum, use the same mapping as BaseRecord
            result_mapping = {
                RecordType.NOUN: "nouns",
                RecordType.VERB: "verbs",
                RecordType.VERB_CONJUGATION: "verbs",
                RecordType.VERB_IMPERATIVE: "verbs",
                RecordType.ADJECTIVE: "adjectives",
                RecordType.ADVERB: "adverbs",
                RecordType.PREPOSITION: "prepositions",
                RecordType.PHRASE: "phrases",
                RecordType.NEGATION: "negations",
                RecordType.UNIFIED_ARTICLE: "articles",
                RecordType.ARTICLE: "articles",
                RecordType.INDEFINITE_ARTICLE: "articles",
                RecordType.NEGATIVE_ARTICLE: "articles",
                # Language-specific types
                RecordType.KOREAN_NOUN: "nouns",
            }
            return result_mapping.get(record_or_type, f"{record_or_type.value}s")
        else:
            # String fallback (for legacy code)
            record_type_str = str(record_or_type)
            return record_type_str.replace("_", "") + "s"

    @staticmethod
    def get_display_name(record_or_type: BaseRecord | RecordType | str) -> str:
        """Get the display name for a record or record type.

        Args:
            record_or_type: Can be a BaseRecord instance, RecordType enum, or string

        Returns:
            str: Display name for UI (e.g., "Noun", "Verb")
        """
        if isinstance(record_or_type, BaseRecord):
            return record_or_type.__class__.get_display_name()
        elif isinstance(record_or_type, RecordType):
            # For RecordType enum, use the same mapping as BaseRecord
            display_mapping = {
                RecordType.NOUN: "Noun",
                RecordType.VERB: "Verb",
                RecordType.VERB_CONJUGATION: "Verb Conjugation",
                RecordType.VERB_IMPERATIVE: "Verb Imperative",
                RecordType.ADJECTIVE: "Adjective",
                RecordType.ADVERB: "Adverbs",
                RecordType.PREPOSITION: "Preposition",
                RecordType.PHRASE: "Phrase",
                RecordType.NEGATION: "Negation",
                RecordType.UNIFIED_ARTICLE: "Unified Article",
                RecordType.ARTICLE: "Article",
                RecordType.INDEFINITE_ARTICLE: "Indefinite Article",
                RecordType.NEGATIVE_ARTICLE: "Negative Article",
                # Language-specific types
                RecordType.KOREAN_NOUN: "Noun",
            }
            return display_mapping.get(
                record_or_type, record_or_type.value.replace("_", " ").title()
            )
        else:
            # String fallback (for legacy code)
            record_type_str = str(record_or_type)
            return record_type_str.replace("_", " ").title()

    @staticmethod
    def get_record_type_from_string(type_string: str) -> RecordType | None:
        """Convert a string representation to a RecordType enum.

        Args:
            type_string: String representation of a record type

        Returns:
            RecordType enum value or None if not found
        """
        # Try direct match first
        for record_type in RecordType:
            if record_type.value == type_string:
                return record_type

        # Try normalized match (lowercase, underscores)
        normalized = type_string.lower().replace("-", "_").replace(" ", "_")
        for record_type in RecordType:
            if record_type.value == normalized:
                return record_type

        return None
