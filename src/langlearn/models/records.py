"""
Record types for the Clean Pipeline Architecture.

These are pure data containers that represent structured CSV data without
business logic. They serve as the intermediate representation between raw CSV
fields and domain models.
"""

from abc import ABC, abstractmethod
from typing import Any, Literal, overload

from pydantic import BaseModel, Field, field_validator


class BaseRecord(BaseModel, ABC):
    """Abstract base class for all record types.

    Records are pure data containers that represent structured CSV data.
    They contain no business logic - that belongs in domain models.
    """

    @classmethod
    @abstractmethod
    def from_csv_fields(cls, fields: list[str]) -> "BaseRecord":
        """Create record from CSV field array.

        Args:
            fields: Array of CSV field values

        Returns:
            Record instance
        """
        pass

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Convert record to dictionary for media enrichment.

        Returns:
            Dictionary representation suitable for MediaEnricher
        """
        pass

    @classmethod
    @abstractmethod
    def get_expected_field_count(cls) -> int:
        """Get expected number of CSV fields for this record type.

        Returns:
            Expected field count
        """
        pass

    @classmethod
    @abstractmethod
    def get_field_names(cls) -> list[str]:
        """Get human-readable field names.

        Returns:
            List of field names in CSV order
        """
        pass


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


class AdjectiveRecord(BaseRecord):
    """Record for German adjective data from CSV."""

    word: str = Field(..., description="German adjective")
    english: str = Field(..., description="English translation")
    example: str = Field(..., description="Example sentence")
    comparative: str = Field(..., description="Comparative form")
    superlative: str = Field(default="", description="Superlative form")

    # Media fields (populated during enrichment)
    image: str | None = Field(default=None, description="Image reference")
    word_audio: str | None = Field(default=None, description="Word audio reference")
    example_audio: str | None = Field(
        default=None, description="Example audio reference"
    )

    @classmethod
    def from_csv_fields(cls, fields: list[str]) -> "AdjectiveRecord":
        """Create AdjectiveRecord from CSV fields."""
        if len(fields) < 4:
            raise ValueError(
                f"AdjectiveRecord requires at least 4 fields, got {len(fields)}"
            )

        return cls(
            word=fields[0].strip(),
            english=fields[1].strip(),
            example=fields[2].strip(),
            comparative=fields[3].strip(),
            superlative=fields[4].strip() if len(fields) > 4 else "",
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for MediaEnricher."""
        return {
            "word": self.word,
            "english": self.english,
            "example": self.example,
            "comparative": self.comparative,
            "superlative": self.superlative,
            "image": self.image,
            "word_audio": self.word_audio,
            "example_audio": self.example_audio,
        }

    @classmethod
    def get_expected_field_count(cls) -> int:
        """Expected CSV field count for adjectives."""
        return 5

    @classmethod
    def get_field_names(cls) -> list[str]:
        """Field names for adjective CSV."""
        return ["word", "english", "example", "comparative", "superlative"]


class AdverbRecord(BaseRecord):
    """Record for German adverb data from CSV."""

    word: str = Field(..., description="German adverb")
    english: str = Field(..., description="English translation")
    type: str = Field(..., description="Adverb type (location, time, etc.)")
    example: str = Field(..., description="Example sentence")

    # Media fields (populated during enrichment)
    image: str | None = Field(default=None, description="Image reference")
    word_audio: str | None = Field(default=None, description="Word audio reference")
    example_audio: str | None = Field(
        default=None, description="Example audio reference"
    )

    @classmethod
    def from_csv_fields(cls, fields: list[str]) -> "AdverbRecord":
        """Create AdverbRecord from CSV fields."""
        if len(fields) < 4:
            raise ValueError(
                f"AdverbRecord requires at least 4 fields, got {len(fields)}"
            )

        return cls(
            word=fields[0].strip(),
            english=fields[1].strip(),
            type=fields[2].strip(),
            example=fields[3].strip(),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for MediaEnricher."""
        return {
            "word": self.word,
            "english": self.english,
            "type": self.type,
            "example": self.example,
            "image": self.image,
            "word_audio": self.word_audio,
            "example_audio": self.example_audio,
        }

    @classmethod
    def get_expected_field_count(cls) -> int:
        """Expected CSV field count for adverbs."""
        return 4

    @classmethod
    def get_field_names(cls) -> list[str]:
        """Field names for adverb CSV."""
        return ["word", "english", "type", "example"]


class NegationRecord(BaseRecord):
    """Record for German negation data from CSV."""

    word: str = Field(..., description="German negation word")
    english: str = Field(..., description="English translation")
    type: str = Field(..., description="Negation type (general, article, etc.)")
    example: str = Field(..., description="Example sentence")

    # Media fields (populated during enrichment)
    image: str | None = Field(default=None, description="Image reference")
    word_audio: str | None = Field(default=None, description="Word audio reference")
    example_audio: str | None = Field(
        default=None, description="Example audio reference"
    )

    @classmethod
    def from_csv_fields(cls, fields: list[str]) -> "NegationRecord":
        """Create NegationRecord from CSV fields."""
        if len(fields) < 4:
            raise ValueError(
                f"NegationRecord requires at least 4 fields, got {len(fields)}"
            )

        return cls(
            word=fields[0].strip(),
            english=fields[1].strip(),
            type=fields[2].strip(),
            example=fields[3].strip(),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for MediaEnricher."""
        return {
            "word": self.word,
            "english": self.english,
            "type": self.type,
            "example": self.example,
            "image": self.image,
            "word_audio": self.word_audio,
            "example_audio": self.example_audio,
        }

    @classmethod
    def get_expected_field_count(cls) -> int:
        """Expected CSV field count for negations."""
        return 4

    @classmethod
    def get_field_names(cls) -> list[str]:
        """Field names for negation CSV."""
        return ["word", "english", "type", "example"]


class VerbRecord(BaseRecord):
    """Record for German verb data from CSV.

    Simple Clean Pipeline migration for current verb CSV structure.
    Matches existing verbs.csv format:
    verb,english,present_ich,present_du,present_er,perfect,example
    """

    verb: str = Field(..., description="German verb in infinitive form")
    english: str = Field(..., description="English translation")
    present_ich: str = Field(..., description="First person singular present")
    present_du: str = Field(..., description="Second person singular present")
    present_er: str = Field(..., description="Third person singular present")
    perfect: str = Field(..., description="Perfect tense form")
    example: str = Field(..., description="Example sentence")

    # Media fields (populated during enrichment)
    word_audio: str | None = Field(
        default=None, description="Verb pronunciation audio reference"
    )
    example_audio: str | None = Field(
        default=None, description="Example sentence audio reference"
    )
    image: str | None = Field(default=None, description="Image reference")

    @classmethod
    def from_csv_fields(cls, fields: list[str]) -> "VerbRecord":
        """Create VerbRecord from CSV field array.

        Args:
            fields: Array of CSV field values in order:
                [verb, english, present_ich, present_du, present_er,
                 perfect, example]

        Returns:
            VerbRecord instance

        Raises:
            ValueError: If fields length doesn't match expected count
        """
        if len(fields) != cls.get_expected_field_count():
            expected = cls.get_expected_field_count()
            raise ValueError(f"VerbRecord expects {expected} fields, got {len(fields)}")

        return cls(
            verb=fields[0],
            english=fields[1],
            present_ich=fields[2],
            present_du=fields[3],
            present_er=fields[4],
            perfect=fields[5],
            example=fields[6],
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for media enrichment."""
        return {
            "verb": self.verb,
            "english": self.english,
            "present_ich": self.present_ich,
            "present_du": self.present_du,
            "present_er": self.present_er,
            "perfect": self.perfect,
            "example": self.example,
            "word_audio": self.word_audio,
            "example_audio": self.example_audio,
            "image": self.image,
        }

    @classmethod
    def get_expected_field_count(cls) -> int:
        """Expected number of CSV fields for verbs."""
        return 7

    @classmethod
    def get_field_names(cls) -> list[str]:
        """Field names for verb CSV."""
        return [
            "verb",
            "english",
            "present_ich",
            "present_du",
            "present_er",
            "perfect",
            "example",
        ]


class VerbConjugationRecord(BaseRecord):
    """Record for German verb conjugation data from CSV.

    Handles standard conjugation patterns with 6 person forms:
    ich, du, er/sie/es, wir, ihr, sie/Sie
    """

    infinitive: str = Field(..., description="German infinitive verb")
    meaning: str = Field(..., description="English meaning")
    classification: str = Field(
        ..., description="Verb type (regelmäßig/unregelmäßig/gemischt)"
    )
    separable: bool = Field(..., description="Whether verb is separable")
    auxiliary: str = Field(..., description="Auxiliary verb (haben/sein)")
    tense: str = Field(..., description="Tense (present/preterite/perfect/future)")

    # Six conjugation forms
    ich: str = Field(..., description="First person singular form")
    du: str = Field(..., description="Second person singular form")
    er: str = Field(..., description="Third person singular form (er/sie/es)")
    wir: str = Field(..., description="First person plural form")
    ihr: str = Field(..., description="Second person plural form")
    sie: str = Field(..., description="Third person plural/formal form (sie/Sie)")

    example: str = Field(..., description="Example sentence using this tense")

    # Media fields (populated during enrichment)
    word_audio: str | None = Field(
        default=None, description="Infinitive audio reference"
    )
    example_audio: str | None = Field(
        default=None, description="Example audio reference"
    )
    image: str | None = Field(default=None, description="Image reference")

    @field_validator("classification")
    @classmethod
    def validate_classification(cls, v: str) -> str:
        """Validate verb classification."""
        valid_classifications = {"regelmäßig", "unregelmäßig", "gemischt"}
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
        valid_tenses = {"present", "preterite", "perfect", "future", "subjunctive"}
        if v not in valid_tenses:
            raise ValueError(f"Invalid tense: {v}. Must be one of {valid_tenses}")
        return v

    @field_validator("ich", "du", "er", "wir", "ihr", "sie")
    @classmethod
    def validate_conjugation_not_empty(cls, v: str) -> str:
        """Ensure conjugation forms are not empty."""
        if not v or v.strip() == "":
            raise ValueError("Conjugation forms cannot be empty")
        return v.strip()

    @classmethod
    def from_csv_fields(cls, fields: list[str]) -> "VerbConjugationRecord":
        """Create VerbConjugationRecord from CSV fields."""
        if len(fields) < 12:
            raise ValueError(
                f"VerbConjugationRecord requires at least 12 fields, got {len(fields)}"
            )

        return cls(
            infinitive=fields[0].strip(),
            meaning=fields[1].strip(),
            classification=fields[2].strip(),
            separable=fields[3].strip().lower() in ("true", "1", "yes"),
            auxiliary=fields[4].strip(),
            tense=fields[5].strip(),
            ich=fields[6].strip(),
            du=fields[7].strip(),
            er=fields[8].strip(),
            wir=fields[9].strip(),
            ihr=fields[10].strip(),
            sie=fields[11].strip(),
            example=fields[12].strip() if len(fields) > 12 else "",
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for MediaEnricher."""
        return {
            "infinitive": self.infinitive,
            "meaning": self.meaning,
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
            "meaning",
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


class VerbImperativeRecord(BaseRecord):
    """Record for German verb imperative data from CSV.

    Handles imperative forms with 3 person forms:
    du-form, ihr-form, Sie-form (formal)
    """

    infinitive: str = Field(..., description="German infinitive verb")
    meaning: str = Field(..., description="English meaning")
    classification: str = Field(
        ..., description="Verb type (regelmäßig/unregelmäßig/gemischt)"
    )
    separable: bool = Field(..., description="Whether verb is separable")

    # Three imperative forms
    du_form: str = Field(..., description="Imperative for du (informal singular)")
    ihr_form: str = Field(..., description="Imperative for ihr (informal plural)")
    sie_form: str = Field(..., description="Imperative for Sie (formal)")

    # Examples for each form
    example_du: str = Field(..., description="Example sentence with du-form")
    example_ihr: str = Field(default="", description="Example sentence with ihr-form")
    example_sie: str = Field(default="", description="Example sentence with Sie-form")

    # Media fields (populated during enrichment)
    word_audio: str | None = Field(
        default=None, description="Infinitive audio reference"
    )
    du_audio: str | None = Field(default=None, description="Du-form audio reference")
    ihr_audio: str | None = Field(default=None, description="Ihr-form audio reference")
    sie_audio: str | None = Field(default=None, description="Sie-form audio reference")
    image: str | None = Field(default=None, description="Image reference")

    @field_validator("classification")
    @classmethod
    def validate_classification(cls, v: str) -> str:
        """Validate verb classification."""
        valid_classifications = {"regelmäßig", "unregelmäßig", "gemischt"}
        if v not in valid_classifications:
            raise ValueError(
                f"Invalid classification: {v}. Must be one of {valid_classifications}"
            )
        return v

    @field_validator("du_form", "ihr_form", "sie_form")
    @classmethod
    def validate_imperative_forms(cls, v: str) -> str:
        """Ensure imperative forms are not empty."""
        if not v or v.strip() == "":
            raise ValueError("Imperative forms cannot be empty")
        return v.strip()

    @classmethod
    def from_csv_fields(cls, fields: list[str]) -> "VerbImperativeRecord":
        """Create VerbImperativeRecord from CSV fields."""
        if len(fields) < 7:
            raise ValueError(
                f"VerbImperativeRecord requires at least 7 fields, got {len(fields)}"
            )

        return cls(
            infinitive=fields[0].strip(),
            meaning=fields[1].strip(),
            classification=fields[2].strip(),
            separable=fields[3].strip().lower() in ("true", "1", "yes"),
            du_form=fields[4].strip(),
            ihr_form=fields[5].strip(),
            sie_form=fields[6].strip(),
            example_du=fields[7].strip() if len(fields) > 7 else "",
            example_ihr=fields[8].strip() if len(fields) > 8 else "",
            example_sie=fields[9].strip() if len(fields) > 9 else "",
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for MediaEnricher."""
        return {
            "infinitive": self.infinitive,
            "meaning": self.meaning,
            "classification": self.classification,
            "separable": self.separable,
            "du_form": self.du_form,
            "ihr_form": self.ihr_form,
            "sie_form": self.sie_form,
            "example_du": self.example_du,
            "example_ihr": self.example_ihr,
            "example_sie": self.example_sie,
            "word_audio": self.word_audio,
            "du_audio": self.du_audio,
            "ihr_audio": self.ihr_audio,
            "sie_audio": self.sie_audio,
            "image": self.image,
        }

    @classmethod
    def get_expected_field_count(cls) -> int:
        """Expected CSV field count for verb imperatives."""
        return 10

    @classmethod
    def get_field_names(cls) -> list[str]:
        """Field names for verb imperative CSV."""
        return [
            "infinitive",
            "meaning",
            "classification",
            "separable",
            "du_form",
            "ihr_form",
            "sie_form",
            "example_du",
            "example_ihr",
            "example_sie",
        ]


# Registry for mapping model types to record types
RECORD_TYPE_REGISTRY = {
    "noun": NounRecord,
    "adjective": AdjectiveRecord,
    "adverb": AdverbRecord,
    "negation": NegationRecord,
    "verb": VerbRecord,
    "verb_conjugation": VerbConjugationRecord,
    "verb_imperative": VerbImperativeRecord,
}


@overload
def create_record(model_type: Literal["noun"], fields: list[str]) -> NounRecord: ...


@overload
def create_record(
    model_type: Literal["adjective"], fields: list[str]
) -> AdjectiveRecord: ...


@overload
def create_record(model_type: Literal["adverb"], fields: list[str]) -> AdverbRecord: ...


@overload
def create_record(
    model_type: Literal["negation"], fields: list[str]
) -> NegationRecord: ...


@overload
def create_record(model_type: Literal["verb"], fields: list[str]) -> VerbRecord: ...


@overload
def create_record(
    model_type: Literal["verb_conjugation"], fields: list[str]
) -> VerbConjugationRecord: ...


@overload
def create_record(
    model_type: Literal["verb_imperative"], fields: list[str]
) -> VerbImperativeRecord: ...


@overload
def create_record(model_type: str, fields: list[str]) -> BaseRecord: ...


def create_record(model_type: str, fields: list[str]) -> BaseRecord:
    """Factory function to create records from model type and CSV fields.

    Args:
        model_type: Type of model (noun, adjective, adverb, negation,
                   verb_conjugation, verb_imperative)
        fields: CSV field values

    Returns:
        Record instance of the appropriate type

    Raises:
        ValueError: If model_type is unknown or fields are invalid
    """
    if model_type not in RECORD_TYPE_REGISTRY:
        raise ValueError(
            f"Unknown model type: {model_type}. "
            f"Available: {list(RECORD_TYPE_REGISTRY.keys())}"
        )

    record_class = RECORD_TYPE_REGISTRY[model_type]
    # Type ignore needed because mypy can't infer the exact return type from registry
    return record_class.from_csv_fields(fields)  # type: ignore[no-any-return, attr-defined]
