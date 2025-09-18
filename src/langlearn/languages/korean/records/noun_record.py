"""Korean noun record with particle patterns and counter support."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from langlearn.core.records.base_record import BaseRecord, RecordType


@dataclass
class KoreanNounRecord(BaseRecord):
    """Korean noun record with essential particle patterns and counter information.

    Based on Korean language pedagogy research, this record focuses on the most
    critical features for English speakers learning Korean nouns:
    1. Particle attachment patterns (은/는, 이/가, 을/를)
    2. Counter classification system
    3. Proper Hangul and pronunciation support
    """

    # Required fields (no defaults)
    hangul: str
    romanization: str
    english: str
    primary_counter: str

    # Optional fields (with defaults)
    topic_particle: str = ""
    subject_particle: str = ""
    object_particle: str = ""
    possessive_form: str = ""
    counter_example: str = ""
    honorific_form: str | None = None
    semantic_category: str = "object"
    usage_notes: str | None = None
    example: str = ""
    example_english: str = ""

    def __post_init__(self) -> None:
        """Post-initialization to generate particle forms and validate data."""
        self._generate_particle_forms()
        self._validate_counter()
        self._validate_category()

    def _generate_particle_forms(self) -> None:
        """Auto-generate particle forms based on phonological rules."""
        if not self.topic_particle:
            self.topic_particle = self._generate_topic_particle()
        if not self.subject_particle:
            self.subject_particle = self._generate_subject_particle()
        if not self.object_particle:
            self.object_particle = self._generate_object_particle()
        if not self.possessive_form:
            self.possessive_form = f"{self.hangul}의"

    def _generate_topic_particle(self) -> str:
        """Generate topic particle (은/는) based on final sound."""
        return f"{self.hangul}{'은' if self._has_final_consonant() else '는'}"

    def _generate_subject_particle(self) -> str:
        """Generate subject particle (이/가) based on final sound."""
        return f"{self.hangul}{'이' if self._has_final_consonant() else '가'}"

    def _generate_object_particle(self) -> str:
        """Generate object particle (을/를) based on final sound."""
        return f"{self.hangul}{'을' if self._has_final_consonant() else '를'}"

    def _has_final_consonant(self) -> bool:
        """Check if the Hangul word ends with a consonant."""
        if not self.hangul:
            return False

        # Get the last character's Unicode code point
        last_char = self.hangul[-1]
        char_code = ord(last_char)

        # Check if it's in the Hangul syllables range
        if 0xAC00 <= char_code <= 0xD7A3:
            # Calculate the final consonant (jongseong)
            # Korean syllable structure: (char_code - 0xAC00) =
            #   (initial * 21 + medial) * 28 + final
            final_consonant = (char_code - 0xAC00) % 28
            return final_consonant != 0  # 0 means no final consonant

        return False

    def _validate_counter(self) -> None:
        """Validate that counter is one of the common Korean counters."""
        common_counters = {
            "개": "general objects",
            "명": "people (neutral)",
            "분": "people (honorific)",
            "마리": "animals",
            "장": "flat objects",
            "권": "books",
            "대": "vehicles/machines",
            "병": "bottles",
            "잔": "cups/glasses",
            "그루": "trees",
        }

        if self.primary_counter not in common_counters:
            # Allow the counter but could warn in logs
            pass

    def _validate_category(self) -> None:
        """Validate semantic category."""
        valid_categories = {"person", "object", "place", "abstract", "animal", "food"}
        if self.semantic_category not in valid_categories:
            raise ValueError(
                f"Invalid semantic category: {self.semantic_category}. "
                f"Must be one of {valid_categories}"
            )

    @classmethod
    def get_record_type(cls) -> RecordType:
        """Return the record type for this Korean noun."""
        return RecordType.KOREAN_NOUN

    @classmethod
    def from_csv_fields(cls, fields: list[str]) -> KoreanNounRecord:
        """Create KoreanNounRecord from CSV fields.

        Expected CSV format:
        [hangul, romanization, english, primary_counter, semantic_category,
         example, example_english, honorific_form, usage_notes]
        """
        if len(fields) != cls.get_expected_field_count():
            expected = cls.get_expected_field_count()
            raise ValueError(
                f"KoreanNounRecord expects {expected} fields, got {len(fields)}"
            )

        # Clean whitespace from all fields
        fields = [field.strip() for field in fields]

        return cls(
            hangul=fields[0],
            romanization=fields[1],
            english=fields[2],
            primary_counter=fields[3],
            semantic_category=fields[4],
            example=fields[5] if len(fields) > 5 else "",
            example_english=fields[6] if len(fields) > 6 else "",
            honorific_form=fields[7] if len(fields) > 7 and fields[7] else None,
            usage_notes=fields[8] if len(fields) > 8 and fields[8] else None,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert record to dictionary format."""
        return {
            "hangul": self.hangul,
            "romanization": self.romanization,
            "english": self.english,
            "topic_particle": self.topic_particle,
            "subject_particle": self.subject_particle,
            "object_particle": self.object_particle,
            "possessive_form": self.possessive_form,
            "primary_counter": self.primary_counter,
            "counter_example": self.counter_example,
            "honorific_form": self.honorific_form,
            "semantic_category": self.semantic_category,
            "example": self.example,
            "example_english": self.example_english,
            "usage_notes": self.usage_notes,
        }

    @classmethod
    def get_expected_field_count(cls) -> int:
        """Expected number of CSV fields for Korean nouns."""
        return 9

    @classmethod
    def get_field_names(cls) -> list[str]:
        """Field names for Korean noun CSV."""
        return [
            "hangul",
            "romanization",
            "english",
            "primary_counter",
            "semantic_category",
            "example",
            "example_english",
            "honorific_form",
            "usage_notes",
        ]
