"""Russian noun record for validation and data transport."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from langlearn.core.records.base_record import BaseRecord, RecordType


@dataclass
class RussianNounRecord(BaseRecord):
    """Russian noun record with case declensions and grammatical features."""

    # Required fields (no defaults)
    noun: str  # Base form (nominative singular)
    english: str  # English translation
    gender: Literal["masculine", "feminine", "neuter"]
    nominative: str  # Base form (same as noun)
    genitive: str  # Родительный падеж

    # Optional fields (with defaults)
    example: str = ""  # Example sentence in Russian
    related: str = ""  # Related words or topic
    animacy: Literal["animate", "inanimate"] = "inanimate"
    accusative: str = ""  # Винительный падеж (often same as nom/gen based on animacy)
    instrumental: str = ""  # Творительный падеж
    prepositional: str = ""  # Предложный падеж
    dative: str = ""  # Дательный падеж
    plural_nominative: str = ""  # Именительный падеж множественного числа
    plural_genitive: str = ""  # Родительный падеж множественного числа

    def __post_init__(self) -> None:
        """Post-initialization validation for Russian noun data."""
        # Basic validation
        if not self.noun or not self.english:
            raise ValueError("Russian noun requires both 'noun' and 'english' fields")

        if not self.gender:
            raise ValueError("Russian noun requires 'gender' field")

        # Set nominative to base form if not provided
        if not self.nominative:
            self.nominative = self.noun

        # For animate nouns, accusative typically equals genitive
        # For inanimate nouns, accusative typically equals nominative
        if not self.accusative:
            if self.animacy == "animate":
                self.accusative = self.genitive if self.genitive else self.noun
            else:
                self.accusative = self.nominative

    @classmethod
    def get_record_type(cls) -> RecordType:
        """Return the RecordType for this record class."""
        return RecordType.NOUN

    @classmethod
    def from_csv_fields(cls, fields: list[str]) -> RussianNounRecord:
        """Create a Russian noun record from CSV fields."""
        if len(fields) < 3:
            raise ValueError(
                f"Russian noun requires at least 3 fields: noun, english, gender. "
                f"Got {len(fields)} fields: {fields}"
            )

        # Validate gender field
        gender_value: Literal["masculine", "feminine", "neuter"] = "masculine"
        if len(fields) > 2 and fields[2] in ["masculine", "feminine", "neuter"]:
            gender_value = fields[2]  # type: ignore[assignment]

        # Validate animacy field
        animacy_value: Literal["animate", "inanimate"] = "inanimate"
        if len(fields) > 6 and fields[6] in ["animate", "inanimate"]:
            animacy_value = fields[6]  # type: ignore[assignment]

        return cls(
            noun=fields[0],
            english=fields[1],
            gender=gender_value,
            genitive=fields[3] if len(fields) > 3 else "",
            example=fields[4] if len(fields) > 4 else "",
            related=fields[5] if len(fields) > 5 else "",
            animacy=animacy_value,
            nominative=fields[0],  # Same as noun field
            instrumental=fields[7] if len(fields) > 7 else "",
            prepositional=fields[8] if len(fields) > 8 else "",
            dative=fields[9] if len(fields) > 9 else "",
            plural_nominative=fields[10] if len(fields) > 10 else "",
            plural_genitive=fields[11] if len(fields) > 11 else "",
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert record to dictionary format for processing."""
        return {
            "noun": self.noun,
            "english": self.english,
            "example": self.example,
            "related": self.related,
            "gender": self.gender,
            "animacy": self.animacy,
            "nominative": self.nominative,
            "genitive": self.genitive,
            "accusative": self.accusative,
            "instrumental": self.instrumental,
            "prepositional": self.prepositional,
            "dative": self.dative,
            "plural_nominative": self.plural_nominative,
            "plural_genitive": self.plural_genitive,
        }

    @classmethod
    def get_expected_field_count(cls) -> int:
        """Get the expected number of CSV fields for this record type."""
        return 12  # noun, english, gender, genitive, example, related, animacy,
        # instrumental, prepositional, dative, plural_nom, plural_gen

    @classmethod
    def get_field_names(cls) -> list[str]:
        """Get ordered list of field names for CSV headers."""
        return [
            "noun",
            "english",
            "gender",
            "genitive",
            "example",
            "related",
            "animacy",
            "instrumental",
            "prepositional",
            "dative",
            "plural_nominative",
            "plural_genitive",
        ]

    def get_display_cases(self) -> dict[str, str]:
        """Get case forms for display purposes."""
        return {
            "Nominative": self.nominative,
            "Genitive": self.genitive,
            "Accusative": self.accusative,
            "Instrumental": self.instrumental,
            "Prepositional": self.prepositional,
            "Dative": self.dative,
        }

    def get_plural_forms(self) -> dict[str, str]:
        """Get plural forms for display purposes."""
        forms = {}
        if self.plural_nominative:
            forms["Plural Nominative"] = self.plural_nominative
        if self.plural_genitive:
            forms["Plural Genitive"] = self.plural_genitive
        return forms
