"""Dataclass-based base classes for language-agnostic record types.

This module provides a dataclass replacement for the Pydantic BaseRecord,
eliminating metaclass conflicts while preserving the exact same interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, ClassVar, Protocol


class RecordType(Enum):
    """Strongly-typed enumeration for record types."""

    # FIXME: This needs to be revisited given multi-language support

    NOUN = "noun"
    ADJECTIVE = "adjective"
    ADVERB = "adverb"
    NEGATION = "negation"
    PHRASE = "phrase"
    VERB_CONJUGATION = "verb_conjugation"
    UNIFIED_ARTICLE = "unified_article"
    PREPOSITION = "preposition"
    VERB = "verb"
    VERB_IMPERATIVE = "verb_imperative"
    ARTICLE = "article"
    INDEFINITE_ARTICLE = "indefinite_article"
    NEGATIVE_ARTICLE = "negative_article"

    # Language-specific record types
    KOREAN_NOUN = "korean_noun"


class RecordClassProtocol(Protocol):
    """Protocol defining the interface that all record classes must implement."""

    @classmethod
    def get_field_names(cls) -> list[str]:
        """Get the list of field names for this record type."""
        ...

    @classmethod
    def get_expected_field_count(cls) -> int:
        """Get the expected number of fields for this record type."""
        ...


@dataclass
class BaseRecord(ABC):
    """Abstract base class for all record types.

    Provides common functionality for CSV data records including:
    - Dataclass-based initialization and field management
    - Abstract methods that subclasses must implement
    - Common field validation patterns
    - Strict field checking (no extra fields allowed by dataclasses)
    """

    # Class-level configuration
    _allow_extra: ClassVar[bool] = False  # Equivalent to Pydantic's extra="forbid"

    def __post_init__(self) -> None:
        """Post-initialization validation hook.

        Subclasses can override validate() to add custom validation logic.
        This replaces Pydantic's field and model validators.
        """
        # Call subclass validation if it exists
        self.validate()

    def validate(self) -> None:
        """Override in subclasses to add custom validation logic.

        This method is called automatically after initialization.
        Raise ValueError for validation errors.

        Example:
            def validate(self) -> None:
                if self.value < 0:
                    raise ValueError("Value must be non-negative")
        """
        # Default implementation does nothing
        # Subclasses override this to add validation
        return

    @classmethod
    @abstractmethod
    def get_record_type(cls) -> RecordType:
        """Return the RecordType for this record class.

        Returns:
            RecordType: The enum value identifying this record type
        """

    @classmethod
    @abstractmethod
    def from_csv_fields(cls, fields: list[str]) -> "BaseRecord":
        """Create a record instance from CSV field values.

        Args:
            fields: List of string values from CSV row

        Returns:
            BaseRecord: Instance of the appropriate record subclass

        Raises:
            ValueError: If fields are invalid or insufficient
        """

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Convert record to dictionary format for processing.

        Returns:
            dict: Dictionary representation suitable for MediaEnricher
        """

    @classmethod
    @abstractmethod
    def get_expected_field_count(cls) -> int:
        """Get the expected number of CSV fields for this record type.

        Returns:
            int: Expected field count
        """

    @classmethod
    @abstractmethod
    def get_field_names(cls) -> list[str]:
        """Get ordered list of field names for CSV headers.

        Returns:
            list[str]: Field names in CSV order
        """

    @classmethod
    def get_subdeck_name(cls) -> str:
        """Get the subdeck name for this record type.

        Returns:
            str: Subdeck name for Anki (e.g., "Nouns", "Verbs")
        """
        record_type = cls.get_record_type()

        # Map record types to subdeck names
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

        return subdeck_mapping.get(record_type, f"{record_type.value.title()}s")

    @classmethod
    def get_result_key(cls) -> str:
        """Get the result key for card statistics.

        Returns:
            str: Result key for statistics (e.g., "nouns", "verbs")
        """
        record_type = cls.get_record_type()

        # Map record types to result keys
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

        return result_mapping.get(record_type, f"{record_type.value}s")

    @classmethod
    def get_display_name(cls) -> str:
        """Get the display name for this record type.

        Returns:
            str: Display name for UI (e.g., "Noun", "Verb")
        """
        record_type = cls.get_record_type()

        # Map record types to display names
        display_mapping = {
            RecordType.NOUN: "Noun",
            RecordType.VERB: "Verb",
            RecordType.VERB_CONJUGATION: "Verb Conjugation",
            RecordType.VERB_IMPERATIVE: "Verb Imperative",
            RecordType.ADJECTIVE: "Adjective",
            RecordType.ADVERB: "Adverb",
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

        default = record_type.value.replace("_", " ").title()
        return display_mapping.get(record_type, default)
