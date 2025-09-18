"""PrepositionRecord for German preposition data from CSV."""

from dataclasses import dataclass
from typing import Any

from langlearn.core.records import BaseRecord, RecordType


@dataclass
class PrepositionRecord(BaseRecord):
    """Record for German preposition data from CSV.

    Simple record processing migration for current prepositions.csv structure.
    Matches existing prepositions.csv format:
    preposition,english,case,example1,example2
    """

    preposition: str
    english: str
    case: str
    example1: str
    example2: str

    # Media fields (populated during enrichment)
    word_audio: str | None = None
    example1_audio: str | None = None
    example2_audio: str | None = None
    image: str | None = None

    @classmethod
    def get_record_type(cls) -> RecordType:
        """Return the record type for prepositions."""
        return RecordType.PREPOSITION

    @classmethod
    def from_csv_fields(cls, fields: list[str]) -> "PrepositionRecord":
        """Create PrepositionRecord from CSV field array.

        Args:
            fields: Array of CSV field values in order:
                [preposition, english, case, example1, example2]

        Returns:
            PrepositionRecord instance

        Raises:
            ValueError: If fields length doesn't match expected count
        """
        if len(fields) != cls.get_expected_field_count():
            expected = cls.get_expected_field_count()
            raise ValueError(
                f"PrepositionRecord expects {expected} fields, got {len(fields)}"
            )

        return cls(
            preposition=fields[0].strip(),
            english=fields[1].strip(),
            case=fields[2].strip(),
            example1=fields[3].strip(),
            example2=fields[4].strip(),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for media enrichment."""
        return {
            "preposition": self.preposition,
            "english": self.english,
            "case": self.case,
            "example1": self.example1,
            "example2": self.example2,
            "word_audio": self.word_audio,
            "example1_audio": self.example1_audio,
            "example2_audio": self.example2_audio,
            "image": self.image,
        }

    @classmethod
    def get_expected_field_count(cls) -> int:
        """Expected number of CSV fields for prepositions."""
        return 5

    @classmethod
    def get_field_names(cls) -> list[str]:
        """Field names for preposition CSV."""
        return ["preposition", "english", "case", "example1", "example2"]
