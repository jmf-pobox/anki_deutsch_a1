"""AdjectiveRecord for German adjective data from CSV."""

from dataclasses import dataclass
from typing import Any

from langlearn.core.records import BaseRecord, RecordType


@dataclass
class AdjectiveRecord(BaseRecord):
    """Record for German adjective data from CSV."""

    word: str
    english: str
    example: str
    comparative: str
    superlative: str = ""

    # Media fields (populated during enrichment)
    image: str | None = None
    word_audio: str | None = None
    example_audio: str | None = None

    @classmethod
    def get_record_type(cls) -> RecordType:
        """Return the record type for adjectives."""
        return RecordType.ADJECTIVE

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
