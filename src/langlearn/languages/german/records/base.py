"""Base classes and enums for German record types."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict


class RecordType(Enum):
    """Strongly-typed enumeration for record types."""

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


class BaseRecord(BaseModel, ABC):
    """Abstract base class for all record types.

    Provides common functionality for CSV data records including:
    - Pydantic validation and serialization
    - Abstract methods that subclasses must implement
    - Common field validation patterns
    """

    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
        extra="forbid",
    )

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
