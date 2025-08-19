"""
Record types for the Clean Pipeline Architecture.

These are pure data containers that represent structured CSV data without
business logic. They serve as the intermediate representation between raw CSV
fields and domain models.
"""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class BaseRecord(BaseModel, ABC):
    """Abstract base class for all record types.

    Records are pure data containers that represent structured CSV data.
    They contain no business logic - that belongs in domain models.
    """

    @classmethod
    @abstractmethod
    def from_csv_fields(cls, fields: list[str]) -> "BaseRecord":
        """Create record from CSV field array.

        Args:
            fields: Array of CSV field values

        Returns:
            Record instance
        """
        pass

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Convert record to dictionary for media enrichment.

        Returns:
            Dictionary representation suitable for MediaEnricher
        """
        pass

    @classmethod
    @abstractmethod
    def get_expected_field_count(cls) -> int:
        """Get expected number of CSV fields for this record type.

        Returns:
            Expected field count
        """
        pass

    @classmethod
    @abstractmethod
    def get_field_names(cls) -> list[str]:
        """Get human-readable field names.

        Returns:
            List of field names in CSV order
        """
        pass


class NounRecord(BaseRecord):
    """Record for German noun data from CSV."""

    noun: str = Field(..., description="German noun")
    article: str = Field(..., description="Definite article (der/die/das)")
    english: str = Field(..., description="English translation")
    plural: str = Field(..., description="Plural form")
    example: str = Field(..., description="Example sentence")
    related: str = Field(default="", description="Related words/phrases")

    # Media fields (populated during enrichment)
    image: str | None = Field(default=None, description="Image reference")
    word_audio: str | None = Field(default=None, description="Word audio reference")
    example_audio: str | None = Field(
        default=None, description="Example audio reference"
    )

    @classmethod
    def from_csv_fields(cls, fields: list[str]) -> "NounRecord":
        """Create NounRecord from CSV fields."""
        if len(fields) < 6:
            raise ValueError(
                f"NounRecord requires at least 6 fields, got {len(fields)}"
            )

        return cls(
            noun=fields[0].strip(),
            article=fields[1].strip(),
            english=fields[2].strip(),
            plural=fields[3].strip(),
            example=fields[4].strip(),
            related=fields[5].strip() if len(fields) > 5 else "",
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for MediaEnricher."""
        return {
            "noun": self.noun,
            "article": self.article,
            "english": self.english,
            "plural": self.plural,
            "example": self.example,
            "related": self.related,
            "image": self.image,
            "word_audio": self.word_audio,
            "example_audio": self.example_audio,
        }

    @classmethod
    def get_expected_field_count(cls) -> int:
        """Expected CSV field count for nouns."""
        return 6

    @classmethod
    def get_field_names(cls) -> list[str]:
        """Field names for noun CSV."""
        return ["noun", "article", "english", "plural", "example", "related"]


class AdjectiveRecord(BaseRecord):
    """Record for German adjective data from CSV."""

    word: str = Field(..., description="German adjective")
    english: str = Field(..., description="English translation")
    example: str = Field(..., description="Example sentence")
    comparative: str = Field(..., description="Comparative form")
    superlative: str = Field(default="", description="Superlative form")

    # Media fields (populated during enrichment)
    image: str | None = Field(default=None, description="Image reference")
    word_audio: str | None = Field(default=None, description="Word audio reference")
    example_audio: str | None = Field(
        default=None, description="Example audio reference"
    )

    @classmethod
    def from_csv_fields(cls, fields: list[str]) -> "AdjectiveRecord":
        """Create AdjectiveRecord from CSV fields."""
        if len(fields) < 4:
            raise ValueError(
                f"AdjectiveRecord requires at least 4 fields, got {len(fields)}"
            )

        return cls(
            word=fields[0].strip(),
            english=fields[1].strip(),
            example=fields[2].strip(),
            comparative=fields[3].strip(),
            superlative=fields[4].strip() if len(fields) > 4 else "",
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for MediaEnricher."""
        return {
            "word": self.word,
            "english": self.english,
            "example": self.example,
            "comparative": self.comparative,
            "superlative": self.superlative,
            "image": self.image,
            "word_audio": self.word_audio,
            "example_audio": self.example_audio,
        }

    @classmethod
    def get_expected_field_count(cls) -> int:
        """Expected CSV field count for adjectives."""
        return 5

    @classmethod
    def get_field_names(cls) -> list[str]:
        """Field names for adjective CSV."""
        return ["word", "english", "example", "comparative", "superlative"]


class AdverbRecord(BaseRecord):
    """Record for German adverb data from CSV."""

    word: str = Field(..., description="German adverb")
    english: str = Field(..., description="English translation")
    type: str = Field(..., description="Adverb type (location, time, etc.)")
    example: str = Field(..., description="Example sentence")

    # Media fields (populated during enrichment)
    image: str | None = Field(default=None, description="Image reference")
    word_audio: str | None = Field(default=None, description="Word audio reference")
    example_audio: str | None = Field(
        default=None, description="Example audio reference"
    )

    @classmethod
    def from_csv_fields(cls, fields: list[str]) -> "AdverbRecord":
        """Create AdverbRecord from CSV fields."""
        if len(fields) < 4:
            raise ValueError(
                f"AdverbRecord requires at least 4 fields, got {len(fields)}"
            )

        return cls(
            word=fields[0].strip(),
            english=fields[1].strip(),
            type=fields[2].strip(),
            example=fields[3].strip(),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for MediaEnricher."""
        return {
            "word": self.word,
            "english": self.english,
            "type": self.type,
            "example": self.example,
            "image": self.image,
            "word_audio": self.word_audio,
            "example_audio": self.example_audio,
        }

    @classmethod
    def get_expected_field_count(cls) -> int:
        """Expected CSV field count for adverbs."""
        return 4

    @classmethod
    def get_field_names(cls) -> list[str]:
        """Field names for adverb CSV."""
        return ["word", "english", "type", "example"]


class NegationRecord(BaseRecord):
    """Record for German negation data from CSV."""

    word: str = Field(..., description="German negation word")
    english: str = Field(..., description="English translation")
    type: str = Field(..., description="Negation type (general, article, etc.)")
    example: str = Field(..., description="Example sentence")

    # Media fields (populated during enrichment)
    image: str | None = Field(default=None, description="Image reference")
    word_audio: str | None = Field(default=None, description="Word audio reference")
    example_audio: str | None = Field(
        default=None, description="Example audio reference"
    )

    @classmethod
    def from_csv_fields(cls, fields: list[str]) -> "NegationRecord":
        """Create NegationRecord from CSV fields."""
        if len(fields) < 4:
            raise ValueError(
                f"NegationRecord requires at least 4 fields, got {len(fields)}"
            )

        return cls(
            word=fields[0].strip(),
            english=fields[1].strip(),
            type=fields[2].strip(),
            example=fields[3].strip(),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for MediaEnricher."""
        return {
            "word": self.word,
            "english": self.english,
            "type": self.type,
            "example": self.example,
            "image": self.image,
            "word_audio": self.word_audio,
            "example_audio": self.example_audio,
        }

    @classmethod
    def get_expected_field_count(cls) -> int:
        """Expected CSV field count for negations."""
        return 4

    @classmethod
    def get_field_names(cls) -> list[str]:
        """Field names for negation CSV."""
        return ["word", "english", "type", "example"]


# Registry for mapping model types to record types
RECORD_TYPE_REGISTRY = {
    "noun": NounRecord,
    "adjective": AdjectiveRecord,
    "adverb": AdverbRecord,
    "negation": NegationRecord,
}


def create_record(model_type: str, fields: list[str]) -> BaseRecord:
    """Factory function to create records from model type and CSV fields.

    Args:
        model_type: Type of model (noun, adjective, adverb, negation)
        fields: CSV field values

    Returns:
        Record instance of the appropriate type

    Raises:
        ValueError: If model_type is unknown or fields are invalid
    """
    if model_type not in RECORD_TYPE_REGISTRY:
        raise ValueError(
            f"Unknown model type: {model_type}. "
            f"Available: {list(RECORD_TYPE_REGISTRY.keys())}"
        )

    record_class = RECORD_TYPE_REGISTRY[model_type]
    return record_class.from_csv_fields(fields)
