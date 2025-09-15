"""VerbConjugationRecord for German verb conjugation data from CSV."""

from typing import Any

from pydantic import Field, field_validator, model_validator

from langlearn.core.records import BaseRecord, RecordType


class VerbConjugationRecord(BaseRecord):
    """Record for German verb conjugation data from CSV.

    Handles standard conjugation patterns with 6 person forms:
    ich, du, er/sie/es, wir, ihr, sie/Sie
    """

    infinitive: str = Field(..., description="German infinitive verb")
    english: str = Field(..., description="English meaning")
    classification: str = Field(
        ..., description="Verb type (regelmäßig/unregelmäßig/gemischt)"
    )
    separable: bool = Field(..., description="Whether verb is separable")
    auxiliary: str = Field(..., description="Auxiliary verb (haben/sein)")
    tense: str = Field(..., description="Tense (present/preterite/perfect/future)")

    # Six conjugation forms (optional for imperative/perfect tenses)
    ich: str = Field(default="", description="First person singular form")
    du: str = Field(default="", description="Second person singular form")
    er: str = Field(default="", description="Third person singular form (er/sie/es)")
    wir: str = Field(default="", description="First person plural form")
    ihr: str = Field(default="", description="Second person plural form")
    sie: str = Field(
        default="", description="Third person plural/formal form (sie/Sie)"
    )

    example: str = Field(..., description="Example sentence using this tense")

    # Media fields (populated during enrichment)
    word_audio: str | None = Field(
        default=None, description="Infinitive audio reference"
    )
    example_audio: str | None = Field(
        default=None, description="Example audio reference"
    )
    image: str | None = Field(default=None, description="Image reference")

    @classmethod
    def get_record_type(cls) -> RecordType:
        """Return the record type for verb conjugations."""
        return RecordType.VERB_CONJUGATION

    @field_validator("classification")
    @classmethod
    def validate_classification(cls, v: str) -> str:
        """Validate verb classification."""
        valid_classifications = {"regelmäßig", "unregelmäßig", "gemischt", "modal"}
        if v not in valid_classifications:
            raise ValueError(
                f"Invalid classification: {v}. Must be one of {valid_classifications}"
            )
        return v

    @field_validator("auxiliary")
    @classmethod
    def validate_auxiliary(cls, v: str) -> str:
        """Validate auxiliary verb."""
        valid_auxiliaries = {"haben", "sein"}
        if v not in valid_auxiliaries:
            raise ValueError(
                f"Invalid auxiliary: {v}. Must be one of {valid_auxiliaries}"
            )
        return v

    @field_validator("tense")
    @classmethod
    def validate_tense(cls, v: str) -> str:
        """Validate tense name."""
        valid_tenses = {
            "present",
            "preterite",
            "perfect",
            "future",
            "subjunctive",
            "imperative",
        }
        if v not in valid_tenses:
            raise ValueError(f"Invalid tense: {v}. Must be one of {valid_tenses}")
        return v

    @field_validator("ich", "du", "er", "wir", "ihr", "sie")
    @classmethod
    def validate_conjugation_forms(cls, v: str) -> str:
        """Validate conjugation forms, allowing empty for specific tenses."""
        # Allow empty/None values for imperative and perfect tenses
        # These will be validated in model_validator for completeness
        if v is None or v == "":
            return ""
        return v.strip()

    @model_validator(mode="after")
    def validate_tense_completeness(self) -> "VerbConjugationRecord":
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

        return self

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
