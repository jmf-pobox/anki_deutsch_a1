"""VerbImperativeRecord for German verb imperative data from CSV."""

from dataclasses import dataclass
from typing import Any

from langlearn.core.records import BaseRecord, RecordType


@dataclass
class VerbImperativeRecord(BaseRecord):
    """Record for German verb imperative data from CSV.

    Aligned with PM-CARD-SPEC.md specification.
    Handles imperative forms: du, ihr, Sie, wir
    """

    infinitive: str
    english: str

    # Four imperative forms as per specification
    du: str
    ihr: str
    sie: str
    wir: str

    # Examples for three forms (no example_wir per spec)
    example_du: str
    example_ihr: str
    example_sie: str

    # Media fields (populated during enrichment)
    word_audio: str | None = None
    image: str | None = None

    def __post_init__(self) -> None:
        """Post-init validation for dataclass."""
        self.validate()

    def validate(self) -> None:
        """Validate the record after initialization."""
        # Validate imperative forms are not empty
        imperative_forms = [self.du, self.ihr, self.sie, self.wir]
        form_names = ["du", "ihr", "sie", "wir"]

        for form, name in zip(imperative_forms, form_names, strict=False):
            if not form or form.strip() == "":
                raise ValueError(f"Imperative form '{name}' cannot be empty")

        # Clean the forms
        self.du = self.du.strip()
        self.ihr = self.ihr.strip()
        self.sie = self.sie.strip()
        self.wir = self.wir.strip()

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
