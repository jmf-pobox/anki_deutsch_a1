"""NegationRecord for German negation data from CSV."""

from typing import Any

from pydantic import Field

from .base import BaseRecord, RecordType


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
    def get_record_type(cls) -> RecordType:
        """Return the record type for negations."""
        return RecordType.NEGATION

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
