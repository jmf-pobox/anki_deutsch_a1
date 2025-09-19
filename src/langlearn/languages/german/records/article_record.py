"""ArticleRecord for German definite articles from CSV."""

from dataclasses import dataclass
from typing import Any

from langlearn.core.records import BaseRecord, RecordType


@dataclass
class ArticleRecord(BaseRecord):
    """Record for German definite articles from CSV - declension grid format."""

    gender: str
    nominative: str
    accusative: str
    dative: str
    genitive: str
    example_nom: str
    example_acc: str
    example_dat: str
    example_gen: str

    # Media fields (populated during enrichment)
    article_audio: str | None = None
    example_audio: str | None = None

    def __post_init__(self) -> None:
        """Post-init validation for dataclass."""
        self.validate()

    def validate(self) -> None:
        """Validate the record after initialization."""
        # Validate gender
        valid_genders = {"masculine", "feminine", "neuter", "plural"}
        if self.gender not in valid_genders:
            raise ValueError(
                f"Invalid gender: {self.gender}. Must be one of {valid_genders}"
            )

    @classmethod
    def get_record_type(cls) -> RecordType:
        """Return the record type for type-safe dispatch."""
        return RecordType.ARTICLE

    @classmethod
    def from_csv_fields(cls, fields: list[str]) -> "ArticleRecord":
        """Create ArticleRecord from CSV fields."""
        if len(fields) != cls.get_expected_field_count():
            expected = cls.get_expected_field_count()
            raise ValueError(
                f"ArticleRecord expects {expected} fields, got {len(fields)}"
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
        """Expected CSV field count for articles."""
        return 9

    @classmethod
    def get_field_names(cls) -> list[str]:
        """Field names for article CSV."""
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
