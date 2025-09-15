"""VerbImperativeRecord for German verb imperative data from CSV."""

from typing import Any

from pydantic import Field, field_validator

from langlearn.core.records import BaseRecord, RecordType


class VerbImperativeRecord(BaseRecord):
    """Record for German verb imperative data from CSV.

    Aligned with PM-CARD-SPEC.md specification.
    Handles imperative forms: du, ihr, Sie, wir
    """

    infinitive: str = Field(..., description="German infinitive verb")
    english: str = Field(..., description="English meaning")

    # Four imperative forms as per specification
    du: str = Field(..., description="Imperative for du (informal singular)")
    ihr: str = Field(..., description="Imperative for ihr (informal plural)")
    sie: str = Field(..., description="Imperative for Sie (formal)")
    wir: str = Field(..., description="Imperative for wir (let's...)")

    # Examples for three forms (no example_wir per spec)
    example_du: str = Field(..., description="Example sentence with du-form")
    example_ihr: str = Field(..., description="Example sentence with ihr-form")
    example_sie: str = Field(..., description="Example sentence with Sie-form")

    # Media fields (populated during enrichment)
    word_audio: str | None = Field(
        default=None, description="Combined imperative audio reference"
    )
    image: str | None = Field(default=None, description="Image reference")

    @field_validator("du", "ihr", "sie", "wir")
    @classmethod
    def validate_imperative_forms(cls, v: str) -> str:
        """Ensure imperative forms are not empty."""
        if not v or v.strip() == "":
            raise ValueError("Imperative forms cannot be empty")
        return v.strip()

    @classmethod
    def get_record_type(cls) -> RecordType:
        """Return the record type for type-safe dispatch."""
        return RecordType.VERB_IMPERATIVE

    @classmethod
    def from_csv_fields(cls, fields: list[str]) -> "VerbImperativeRecord":
        """Create VerbImperativeRecord from CSV fields."""
        if len(fields) < 7:
            raise ValueError(
                f"VerbImperativeRecord requires at least 7 fields, got {len(fields)}"
            )

        return cls(
            infinitive=fields[0].strip(),
            english=fields[1].strip(),
            du=fields[2].strip(),
            ihr=fields[3].strip(),
            sie=fields[4].strip(),
            wir=fields[5].strip(),
            example_du=fields[6].strip() if len(fields) > 6 else "",
            example_ihr=fields[7].strip() if len(fields) > 7 else "",
            example_sie=fields[8].strip() if len(fields) > 8 else "",
            word_audio=(
                fields[9].strip() if len(fields) > 9 and fields[9].strip() else None
            ),
            image=(
                fields[10].strip() if len(fields) > 10 and fields[10].strip() else None
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for MediaEnricher."""
        return {
            "infinitive": self.infinitive,
            "english": self.english,
            "du": self.du,
            "ihr": self.ihr,
            "sie": self.sie,
            "wir": self.wir,
            "example_du": self.example_du,
            "example_ihr": self.example_ihr,
            "example_sie": self.example_sie,
            "word_audio": self.word_audio,
            "image": self.image,
        }

    @classmethod
    def get_expected_field_count(cls) -> int:
        """Expected CSV field count for verb imperatives."""
        return 9

    @classmethod
    def get_field_names(cls) -> list[str]:
        """Field names for verb imperative CSV."""
        return [
            "infinitive",
            "english",
            "du",
            "ihr",
            "sie",
            "wir",
            "example_du",
            "example_ihr",
            "example_sie",
        ]
