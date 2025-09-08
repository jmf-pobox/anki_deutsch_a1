"""
Record types for the Clean Pipeline Architecture.

These are pure data containers that represent structured CSV data without
business logic. They serve as the intermediate representation between raw CSV
fields and domain models.
"""

from typing import Any, Literal, overload

from pydantic import Field, field_validator, model_validator

from .adjective_record import AdjectiveRecord
from .adverb_record import AdverbRecord
from .base import BaseRecord, RecordClassProtocol, RecordType
from .negation_record import NegationRecord
from .noun_record import NounRecord
from .phrase_record import PhraseRecord
from .preposition_record import PrepositionRecord

# Export all record types and base classes for external imports
__all__ = [
    "AdjectiveRecord",
    "AdverbRecord",
    "ArticleRecord",
    "BaseRecord",
    "IndefiniteArticleRecord",
    "NegationRecord",
    "NegativeArticleRecord",
    "NounRecord",
    "PhraseRecord",
    "PrepositionRecord",
    "RecordClassProtocol",
    "RecordType",
    "UnifiedArticleRecord",
    "VerbConjugationRecord",
    "VerbImperativeRecord",
    "VerbRecord",
]


class VerbRecord(BaseRecord):
    """Record for German verb data from CSV.

    Enhanced Clean Pipeline for complete verb CSV structure.
    Matches enhanced verbs.csv format:
    verb,english,classification,present_ich,present_du,present_er,präteritum,auxiliary,perfect,example,separable
    """

    verb: str = Field(..., description="German verb in infinitive form")
    english: str = Field(..., description="English translation")
    classification: str = Field(
        ..., description="Verb classification (regelmäßig, unregelmäßig, gemischt)"
    )
    present_ich: str = Field(..., description="First person singular present")
    present_du: str = Field(..., description="Second person singular present")
    present_er: str = Field(..., description="Third person singular present")
    präteritum: str = Field(..., description="Präteritum 3rd person singular form")
    auxiliary: str = Field(..., description="Auxiliary verb (haben or sein)")
    perfect: str = Field(..., description="Perfect tense form")
    example: str = Field(..., description="Example sentence")
    separable: bool = Field(..., description="Whether the verb is separable")

    # Media fields (populated during enrichment)
    word_audio: str | None = Field(
        default=None, description="Verb pronunciation audio reference"
    )
    example_audio: str | None = Field(
        default=None, description="Example sentence audio reference"
    )
    image: str | None = Field(default=None, description="Image reference")

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


class VerbImperativeRecord(BaseRecord):
    """Record for German verb imperative data from CSV.

    Aligned with PROD-CARD-SPEC.md specification.
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


class ArticleRecord(BaseRecord):
    """Record for German definite articles from CSV - declension grid format."""

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


class IndefiniteArticleRecord(BaseRecord):
    """Record for German indefinite articles from CSV - declension grid format."""

    gender: str = Field(..., description="Gender (masculine, feminine, neuter)")
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
        valid_genders = {"masculine", "feminine", "neuter"}
        if v not in valid_genders:
            raise ValueError(f"Invalid gender: {v}. Must be one of {valid_genders}")
        return v

    @classmethod
    def get_record_type(cls) -> RecordType:
        """Return the record type for type-safe dispatch."""
        return RecordType.ARTICLE

    @classmethod
    def from_csv_fields(cls, fields: list[str]) -> "IndefiniteArticleRecord":
        """Create IndefiniteArticleRecord from CSV fields."""
        if len(fields) != cls.get_expected_field_count():
            expected = cls.get_expected_field_count()
            raise ValueError(
                f"IndefiniteArticleRecord expects {expected} fields, got {len(fields)}"
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
        """Expected CSV field count for indefinite articles."""
        return 9

    @classmethod
    def get_field_names(cls) -> list[str]:
        """Field names for indefinite article CSV."""
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


class UnifiedArticleRecord(BaseRecord):
    """Record for unified German articles from CSV with German terminology."""

    artikel_typ: str = Field(
        ..., description="Article type (bestimmt, unbestimmt, verneinend)"
    )
    geschlecht: str = Field(
        ..., description="Gender (maskulin, feminin, neutral, plural)"
    )
    nominativ: str = Field(..., description="Nominative case form")
    akkusativ: str = Field(..., description="Accusative case form")
    dativ: str = Field(..., description="Dative case form")
    genitiv: str = Field(..., description="Genitive case form")
    beispiel_nom: str = Field(..., description="Example sentence in nominative")
    beispiel_akk: str = Field(..., description="Example sentence in accusative")
    beispiel_dat: str = Field(..., description="Example sentence in dative")
    beispiel_gen: str = Field(..., description="Example sentence in genitive")

    # Media fields (populated during enrichment)
    article_audio: str | None = Field(
        default=None, description="Article audio reference"
    )
    example_audio: str | None = Field(
        default=None, description="Example audio reference"
    )
    image: str | None = Field(default=None, description="Image reference")

    @classmethod
    def get_record_type(cls) -> RecordType:
        """Return the record type for unified articles."""
        return RecordType.UNIFIED_ARTICLE

    @field_validator("artikel_typ")
    @classmethod
    def validate_artikel_typ(cls, v: str) -> str:
        """Validate article type."""
        valid_types = {"bestimmt", "unbestimmt", "verneinend"}
        if v not in valid_types:
            raise ValueError(f"Invalid artikel_typ: {v}. Must be one of {valid_types}")
        return v

    @field_validator("geschlecht")
    @classmethod
    def validate_geschlecht(cls, v: str) -> str:
        """Validate gender."""
        valid_genders = {"maskulin", "feminin", "neutral", "plural"}
        if v not in valid_genders:
            raise ValueError(f"Invalid geschlecht: {v}. Must be one of {valid_genders}")
        return v

    @classmethod
    def get_expected_field_count(cls) -> int:
        """Number of fields expected from CSV."""
        return 10

    @classmethod
    def from_csv_fields(cls, fields: list[str]) -> "UnifiedArticleRecord":
        """Create UnifiedArticleRecord from CSV fields."""
        if len(fields) != cls.get_expected_field_count():
            expected = cls.get_expected_field_count()
            raise ValueError(
                f"UnifiedArticleRecord expects {expected} fields, got {len(fields)}"
            )

        return cls(
            artikel_typ=fields[0].strip(),
            geschlecht=fields[1].strip(),
            nominativ=fields[2].strip(),
            akkusativ=fields[3].strip(),
            dativ=fields[4].strip(),
            genitiv=fields[5].strip(),
            beispiel_nom=fields[6].strip(),
            beispiel_akk=fields[7].strip(),
            beispiel_dat=fields[8].strip(),
            beispiel_gen=fields[9].strip(),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for media enrichment."""
        return {
            "artikel_typ": self.artikel_typ,
            "geschlecht": self.geschlecht,
            "nominativ": self.nominativ,
            "akkusativ": self.akkusativ,
            "dativ": self.dativ,
            "genitiv": self.genitiv,
            "beispiel_nom": self.beispiel_nom,
            "beispiel_akk": self.beispiel_akk,
            "beispiel_dat": self.beispiel_dat,
            "beispiel_gen": self.beispiel_gen,
            "article_audio": self.article_audio,
            "example_audio": self.example_audio,
            "image": self.image,
        }

    @classmethod
    def get_field_names(cls) -> list[str]:
        """Field names for unified article CSV."""
        return [
            "artikel_typ",
            "geschlecht",
            "nominativ",
            "akkusativ",
            "dativ",
            "genitiv",
            "beispiel_nom",
            "beispiel_akk",
            "beispiel_dat",
            "beispiel_gen",
        ]

    # Compatibility properties for legacy ArticlePatternProcessor
    @property
    def gender(self) -> str:
        """Legacy compatibility: geschlecht -> gender."""
        return self.geschlecht

    @property
    def nominative(self) -> str:
        """Legacy compatibility: nominativ -> nominative."""
        return self.nominativ

    @property
    def accusative(self) -> str:
        """Legacy compatibility: akkusativ -> accusative."""
        return self.akkusativ

    @property
    def dative(self) -> str:
        """Legacy compatibility: dativ -> dative."""
        return self.dativ

    @property
    def genitive(self) -> str:
        """Legacy compatibility: genitiv -> genitive."""
        return self.genitiv

    @property
    def example_nom(self) -> str:
        """Legacy compatibility: beispiel_nom -> example_nom."""
        return self.beispiel_nom

    @property
    def example_acc(self) -> str:
        """Legacy compatibility: beispiel_akk -> example_acc."""
        return self.beispiel_akk

    @property
    def example_dat(self) -> str:
        """Legacy compatibility: beispiel_dat -> example_dat."""
        return self.beispiel_dat

    @property
    def example_gen(self) -> str:
        """Legacy compatibility: beispiel_gen -> example_gen."""
        return self.beispiel_gen

    def get_image_search_strategy(self) -> str:
        """Get image search strategy for media generation.

        Returns the most representative example for image searches.
        Uses nominative example as it's typically the clearest form.
        """
        return self.beispiel_nom

    def get_combined_audio_text(self) -> str:
        """Get combined text for audio generation.

        Returns the nominative example as the primary audio content
        since it represents the most basic article usage.
        """
        return self.beispiel_nom


# Registry for mapping model types to record types
RECORD_TYPE_REGISTRY: dict[str, type[RecordClassProtocol]] = {
    "noun": NounRecord,
    "adjective": AdjectiveRecord,
    "adverb": AdverbRecord,
    "negation": NegationRecord,
    "verb": VerbRecord,
    "phrase": PhraseRecord,
    "preposition": PrepositionRecord,
    "verb_conjugation": VerbConjugationRecord,
    "verb_imperative": VerbImperativeRecord,
    "article": ArticleRecord,
    "indefinite_article": IndefiniteArticleRecord,
    "negative_article": NegativeArticleRecord,
    "unified_article": UnifiedArticleRecord,
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
def create_record(model_type: Literal["phrase"], fields: list[str]) -> PhraseRecord: ...


@overload
def create_record(
    model_type: Literal["preposition"], fields: list[str]
) -> PrepositionRecord: ...


@overload
def create_record(
    model_type: Literal["verb_conjugation"], fields: list[str]
) -> VerbConjugationRecord: ...


@overload
def create_record(
    model_type: Literal["verb_imperative"], fields: list[str]
) -> VerbImperativeRecord: ...


@overload
def create_record(
    model_type: Literal["article"], fields: list[str]
) -> ArticleRecord: ...


@overload
def create_record(
    model_type: Literal["indefinite_article"], fields: list[str]
) -> IndefiniteArticleRecord: ...


@overload
def create_record(
    model_type: Literal["negative_article"], fields: list[str]
) -> NegativeArticleRecord: ...


@overload
def create_record(model_type: str, fields: list[str]) -> BaseRecord: ...


def create_record(model_type: str, fields: list[str]) -> BaseRecord:
    """Factory function to create records from model type and CSV fields.

    Args:
        model_type: Type of model (noun, adjective, adverb, negation,
                   verb, phrase, preposition, verb_conjugation, verb_imperative,
                   article, indefinite_article, negative_article)
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
    return record_class.from_csv_fields(fields)  # type: ignore
