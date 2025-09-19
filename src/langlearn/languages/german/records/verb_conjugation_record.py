"""VerbConjugationRecord for German verb conjugation data from CSV."""

from dataclasses import dataclass
from typing import Any

from langlearn.core.records import BaseRecord, RecordType


@dataclass
class VerbConjugationRecord(BaseRecord):
    """Record for German verb conjugation data from CSV.

    Handles standard conjugation patterns with 6 person forms:
    ich, du, er/sie/es, wir, ihr, sie/Sie
    """

    infinitive: str
    english: str
    classification: str
    separable: bool
    auxiliary: str
    tense: str

    # Six conjugation forms (optional for imperative/perfect tenses)
    ich: str = ""
    du: str = ""
    er: str = ""
    wir: str = ""
    ihr: str = ""
    sie: str = ""

    example: str = ""

    # Media fields (populated during enrichment)
    word_audio: str | None = None
    example_audio: str | None = None
    image: str | None = None

    def __post_init__(self) -> None:
        """Post-init validation for dataclass."""
        self.validate()

    def validate(self) -> None:
        """Validate the record after initialization."""
        # Validate classification
        valid_classifications = {"regelmäßig", "unregelmäßig", "gemischt", "modal"}
        if self.classification not in valid_classifications:
            raise ValueError(
                f"Invalid classification: {self.classification}. "
                f"Must be one of {valid_classifications}"
            )

        # Validate auxiliary
        valid_auxiliaries = {"haben", "sein"}
        if self.auxiliary not in valid_auxiliaries:
            raise ValueError(
                f"Invalid auxiliary: {self.auxiliary}. "
                f"Must be one of {valid_auxiliaries}"
            )

        # Validate tense
        valid_tenses = {
            "present",
            "preterite",
            "perfect",
            "future",
            "subjunctive",
            "imperative",
        }
        if self.tense not in valid_tenses:
            raise ValueError(
                f"Invalid tense: {self.tense}. Must be one of {valid_tenses}"
            )

        # Clean conjugation forms
        self.ich = self.ich.strip() if self.ich else ""
        self.du = self.du.strip() if self.du else ""
        self.er = self.er.strip() if self.er else ""
        self.wir = self.wir.strip() if self.wir else ""
        self.ihr = self.ihr.strip() if self.ihr else ""
        self.sie = self.sie.strip() if self.sie else ""

        # Validate tense completeness
        self._validate_tense_completeness()

    def _validate_tense_completeness(self) -> None:
        """Validate that required conjugation forms are present for each tense."""
        tense = self.tense.lower()

        # Impersonal verbs (weather verbs) only need 3rd person singular
        impersonal_verbs = {"regnen", "schneien", "hageln", "donnern", "blitzen"}
        is_impersonal = self.infinitive in impersonal_verbs

        if tense in {"present", "preterite", "subjunctive"}:
            if is_impersonal:
                # Impersonal verbs only need 3rd person singular (sie field)
                if not self.sie or self.sie.strip() == "":
                    raise ValueError(
                        f"Impersonal verb {self.infinitive} requires 'sie' form"
                    )
            else:
                # Regular verbs require all 6 persons
                required_forms = [
                    self.ich,
                    self.du,
                    self.er,
                    self.wir,
                    self.ihr,
                    self.sie,
                ]
                empty_forms = [
                    i
                    for i, form in enumerate(required_forms)
                    if not form or form.strip() == ""
                ]
                if empty_forms:
                    person_names = ["ich", "du", "er", "wir", "ihr", "sie"]
                    missing = [person_names[i] for i in empty_forms]
                    raise ValueError(
                        f"{tense} tense requires all persons: "
                        f"missing {', '.join(missing)}"
                    )

        elif tense == "imperative":
            # Imperative requires only du and ihr forms (sie/Sie can be optional)
            if not self.du or self.du.strip() == "":
                raise ValueError("Imperative tense requires 'du' form")
            if not self.ihr or self.ihr.strip() == "":
                raise ValueError("Imperative tense requires 'ihr' form")
            # ich, er, wir can be empty for imperatives

        elif tense == "perfect" and (not self.sie or self.sie.strip() == ""):
            # Perfect tense uses auxiliary form in sie field (legacy compatibility)
            raise ValueError("Perfect tense requires auxiliary form in 'sie' field")
            # Other persons can be empty for perfect tense

    @classmethod
    def get_record_type(cls) -> RecordType:
        """Return the record type for verb conjugations."""
        return RecordType.VERB_CONJUGATION

    @classmethod
    def from_csv_fields(cls, fields: list[str]) -> "VerbConjugationRecord":
        """Create VerbConjugationRecord from CSV fields."""
        if len(fields) < 12:
            raise ValueError(
                f"VerbConjugationRecord requires at least 12 fields, got {len(fields)}"
            )

        # Helper function to safely strip string or return empty string
        def safe_strip(field: str | None) -> str:
            if field is None:
                return ""
            return field.strip() if isinstance(field, str) else ""

        return cls(
            infinitive=safe_strip(fields[0]),
            english=safe_strip(fields[1]),
            classification=safe_strip(fields[2]),
            separable=safe_strip(fields[3]).lower() in ("true", "1", "yes"),
            auxiliary=safe_strip(fields[4]),
            tense=safe_strip(fields[5]),
            ich=safe_strip(fields[6]),
            du=safe_strip(fields[7]),
            er=safe_strip(fields[8]),
            wir=safe_strip(fields[9]),
            ihr=safe_strip(fields[10]),
            sie=safe_strip(fields[11]),
            example=safe_strip(fields[12]) if len(fields) > 12 else "",
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for MediaEnricher."""
        return {
            "infinitive": self.infinitive,
            "english": self.english,
            "classification": self.classification,
            "separable": self.separable,
            "auxiliary": self.auxiliary,
            "tense": self.tense,
            "ich": self.ich,
            "du": self.du,
            "er": self.er,
            "wir": self.wir,
            "ihr": self.ihr,
            "sie": self.sie,
            "example": self.example,
            "word_audio": self.word_audio,
            "example_audio": self.example_audio,
            "image": self.image,
        }

    @classmethod
    def get_expected_field_count(cls) -> int:
        """Expected CSV field count for verb conjugations."""
        return 13

    @classmethod
    def get_field_names(cls) -> list[str]:
        """Field names for verb conjugation CSV."""
        return [
            "infinitive",
            "english",
            "classification",
            "separable",
            "auxiliary",
            "tense",
            "ich",
            "du",
            "er",
            "wir",
            "ihr",
            "sie",
            "example",
        ]
