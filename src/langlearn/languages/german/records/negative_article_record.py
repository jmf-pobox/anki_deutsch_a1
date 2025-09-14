"""NegativeArticleRecord for German negative articles from CSV."""

from typing import Any

from pydantic import Field, field_validator

from .base import BaseRecord, RecordType


class NegativeArticleRecord(BaseRecord):
    """Record for German negative articles from CSV - declension grid format."""

    gender: str = Field(..., description="Gender (masculine, feminine, neuter, plural)")
    nominative: str = Field(..., description="Nominative case form")
    accusative: str = Field(..., description="Accusative case form")
    dative: str = Field(..., description="Dative case form")
    genitive: str = Field(..., description="Genitive case form")
    example_nom: str = Field(..., description="Example sentence in nominative")
    example_acc: str = Field(..., description="Example sentence in accusative")
    example_dat: str = Field(..., description="Example sentence in dative")
    example_gen: str = Field(..., description="Example sentence in genitive")

    # Media fields (populated during enrichment)
    article_audio: str | None = Field(
        default=None, description="Article audio reference"
    )
    example_audio: str | None = Field(
        default=None, description="Example audio reference"
    )

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        """Validate gender values."""
        valid_genders = {"masculine", "feminine", "neuter", "plural"}
        if v not in valid_genders:
            raise ValueError(f"Invalid gender: {v}. Must be one of {valid_genders}")
        return v

    @classmethod
    def get_record_type(cls) -> RecordType:
        """Return the record type for type-safe dispatch."""
        return RecordType.ARTICLE

    @classmethod
    def from_csv_fields(cls, fields: list[str]) -> "NegativeArticleRecord":
        """Create NegativeArticleRecord from CSV fields."""
        if len(fields) != cls.get_expected_field_count():
            expected = cls.get_expected_field_count()
            raise ValueError(
                f"NegativeArticleRecord expects {expected} fields, got {len(fields)}"
            )

        return cls(
            gender=fields[0].strip(),
            nominative=fields[1].strip(),
            accusative=fields[2].strip(),
            dative=fields[3].strip(),
            genitive=fields[4].strip(),
            example_nom=fields[5].strip(),
            example_acc=fields[6].strip(),
            example_dat=fields[7].strip(),
            example_gen=fields[8].strip(),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for media enrichment."""
        return {
            "gender": self.gender,
            "nominative": self.nominative,
            "accusative": self.accusative,
            "dative": self.dative,
            "genitive": self.genitive,
            "example_nom": self.example_nom,
            "example_acc": self.example_acc,
            "example_dat": self.example_dat,
            "example_gen": self.example_gen,
            "article_audio": self.article_audio,
            "example_audio": self.example_audio,
        }

    @classmethod
    def get_expected_field_count(cls) -> int:
        """Expected CSV field count for negative articles."""
        return 9

    @classmethod
    def get_field_names(cls) -> list[str]:
        """Field names for negative article CSV."""
        return [
            "gender",
            "nominative",
            "accusative",
            "dative",
            "genitive",
            "example_nom",
            "example_acc",
            "example_dat",
            "example_gen",
        ]
