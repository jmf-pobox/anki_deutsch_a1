"""NounRecord for German noun data from CSV."""

from typing import Any

from pydantic import Field

from langlearn.core.records import BaseRecord, RecordType


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
    def get_record_type(cls) -> RecordType:
        """Return the record type for nouns."""
        return RecordType.NOUN

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
