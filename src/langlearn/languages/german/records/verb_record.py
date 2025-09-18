"""VerbRecord for German verb data from CSV."""

from dataclasses import dataclass
from typing import Any

from langlearn.core.records import BaseRecord, RecordType


@dataclass
class VerbRecord(BaseRecord):
    """Record for German verb data from CSV.

    Enhanced record processing for complete verb CSV structure.
    Matches enhanced verbs.csv format:
    verb,english,classification,present_ich,present_du,present_er,präteritum,auxiliary,perfect,example,separable
    """

    verb: str
    english: str
    classification: str
    present_ich: str
    present_du: str
    present_er: str
    präteritum: str
    auxiliary: str
    perfect: str
    example: str
    separable: bool

    # Media fields (populated during enrichment)
    word_audio: str | None = None
    example_audio: str | None = None
    image: str | None = None

    @classmethod
    def get_record_type(cls) -> RecordType:
        """Return the record type for verbs."""
        return RecordType.VERB

    @classmethod
    def from_csv_fields(cls, fields: list[str]) -> "VerbRecord":
        """Create VerbRecord from CSV field array.

        Args:
            fields: Array of CSV field values in order:
                [verb, english, classification, present_ich, present_du, present_er,
                 präteritum, auxiliary, perfect, example, separable]

        Returns:
            VerbRecord instance

        Raises:
            ValueError: If fields length doesn't match expected count
        """
        if len(fields) != cls.get_expected_field_count():
            expected = cls.get_expected_field_count()
            raise ValueError(f"VerbRecord expects {expected} fields, got {len(fields)}")

        # Convert separable from string to boolean
        separable_bool = fields[10].strip().lower() == "true"

        return cls(
            verb=fields[0].strip(),
            english=fields[1].strip(),
            classification=fields[2].strip(),
            present_ich=fields[3].strip(),
            present_du=fields[4].strip(),
            present_er=fields[5].strip(),
            präteritum=fields[6].strip(),
            auxiliary=fields[7].strip(),
            perfect=fields[8].strip(),
            example=fields[9].strip(),
            separable=separable_bool,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for media enrichment."""
        return {
            "verb": self.verb,
            "english": self.english,
            "classification": self.classification,
            "present_ich": self.present_ich,
            "present_du": self.present_du,
            "present_er": self.present_er,
            "präteritum": self.präteritum,
            "auxiliary": self.auxiliary,
            "perfect": self.perfect,
            "example": self.example,
            "separable": self.separable,
            "word_audio": self.word_audio,
            "example_audio": self.example_audio,
            "image": self.image,
        }

    @classmethod
    def get_expected_field_count(cls) -> int:
        """Expected number of CSV fields for verbs."""
        return 11

    @classmethod
    def get_field_names(cls) -> list[str]:
        """Field names for verb CSV."""
        return [
            "verb",
            "english",
            "classification",
            "present_ich",
            "present_du",
            "present_er",
            "präteritum",
            "auxiliary",
            "perfect",
            "example",
            "separable",
        ]
