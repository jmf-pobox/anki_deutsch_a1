"""AdverbRecord for German adverb data from CSV."""

from dataclasses import dataclass
from typing import Any

from langlearn.core.records import BaseRecord, RecordType


@dataclass
class AdverbRecord(BaseRecord):
    """Record for German adverb data from CSV."""

    word: str
    english: str
    type: str
    example: str

    # Media fields (populated during enrichment)
    image: str | None = None
    word_audio: str | None = None
    example_audio: str | None = None

    @classmethod
    def get_record_type(cls) -> RecordType:
        """Return the record type for adverbs."""
        return RecordType.ADVERB

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
