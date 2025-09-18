"""PhraseRecord for German phrase data from CSV."""

from dataclasses import dataclass
from typing import Any

from langlearn.core.records import BaseRecord, RecordType


@dataclass
class PhraseRecord(BaseRecord):
    """Record for German phrase data from CSV.

    Simple record processing migration for current phrases.csv structure.
    Matches existing phrases.csv format:
    phrase,english,context,related
    """

    phrase: str
    english: str
    context: str
    related: str = ""

    # Media fields (populated during enrichment)
    phrase_audio: str | None = None
    image: str | None = None

    @classmethod
    def get_record_type(cls) -> RecordType:
        """Return the record type for phrases."""
        return RecordType.PHRASE

    @classmethod
    def from_csv_fields(cls, fields: list[str]) -> "PhraseRecord":
        """Create PhraseRecord from CSV field array.

        Args:
            fields: Array of CSV field values in order:
                [phrase, english, context, related]

        Returns:
            PhraseRecord instance

        Raises:
            ValueError: If fields length doesn't match expected count
        """
        if len(fields) != cls.get_expected_field_count():
            expected = cls.get_expected_field_count()
            raise ValueError(
                f"PhraseRecord expects {expected} fields, got {len(fields)}"
            )

        return cls(
            phrase=fields[0].strip(),
            english=fields[1].strip(),
            context=fields[2].strip(),
            related=fields[3].strip(),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for media enrichment."""
        return {
            "phrase": self.phrase,
            "english": self.english,
            "context": self.context,
            "related": self.related,
            "phrase_audio": self.phrase_audio,
            "image": self.image,
        }

    @classmethod
    def get_expected_field_count(cls) -> int:
        """Expected number of CSV fields for phrases."""
        return 4

    @classmethod
    def get_field_names(cls) -> list[str]:
        """Field names for phrase CSV."""
        return ["phrase", "english", "context", "related"]
