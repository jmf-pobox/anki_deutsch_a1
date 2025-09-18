"""Korean noun domain model with particle patterns and counter system."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from langlearn.core.protocols.domain_model_protocol import LanguageDomainModel
from langlearn.core.protocols.media_generation_protocol import MediaGenerationCapable

if TYPE_CHECKING:
    from collections.abc import Callable

    from langlearn.core.protocols.image_query_generation_protocol import (
        ImageQueryGenerationProtocol,
    )


@dataclass
class KoreanNoun(LanguageDomainModel, MediaGenerationCapable):
    """Korean noun domain model with particle patterns and media generation.

    Focuses on pedagogically critical features for English speakers:
    - Automatic particle generation based on phonological rules
    - Counter classification system
    - Honorific forms when applicable
    - Proper pronunciation support
    """

    # Core identification
    hangul: str
    romanization: str
    english: str

    # Auto-generated particle patterns
    topic_particle: str = ""
    subject_particle: str = ""
    object_particle: str = ""
    possessive_form: str = ""

    # Counter system (pedagogically critical)
    primary_counter: str = "개"  # Default to general counter
    counter_example: str = ""

    # Honorific system
    honorific_form: str | None = None
    semantic_category: str = "object"

    # Example sentences
    example: str = ""
    example_english: str = ""
    usage_notes: str | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields after dataclass creation."""
        # Auto-generate particle forms if not provided
        if not self.topic_particle:
            self.topic_particle = self._generate_topic_particle()
        if not self.subject_particle:
            self.subject_particle = self._generate_subject_particle()
        if not self.object_particle:
            self.object_particle = self._generate_object_particle()
        if not self.possessive_form:
            self.possessive_form = f"{self.hangul}의"

        # Generate counter example if not provided
        if not self.counter_example and self.primary_counter:
            number = "세" if self.semantic_category == "object" else "다섯"
            self.counter_example = f"{self.hangul} {number} {self.primary_counter}"

    def _has_final_consonant(self) -> bool:
        """Check if the Hangul word ends with a consonant (jongseong)."""
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

    def _generate_topic_particle(self) -> str:
        """Generate topic particle (은/는) based on final sound."""
        return f"{self.hangul}{'은' if self._has_final_consonant() else '는'}"

    def _generate_subject_particle(self) -> str:
        """Generate subject particle (이/가) based on final sound."""
        return f"{self.hangul}{'이' if self._has_final_consonant() else '가'}"

    def _generate_object_particle(self) -> str:
        """Generate object particle (을/를) based on final sound."""
        return f"{self.hangul}{'을' if self._has_final_consonant() else '를'}"

    def get_combined_audio_text(self) -> str:
        """Get text for audio generation with particle patterns."""
        # Include particle patterns for pronunciation learning
        particle_text = (
            f"{self.topic_particle}, {self.subject_particle}, {self.object_particle}"
        )

        if self.example:
            return f"{self.hangul}. {particle_text}. {self.example}"
        else:
            return f"{self.hangul}. {particle_text}"

    def get_image_search_strategy(
        self, anthropic_service: ImageQueryGenerationProtocol
    ) -> Callable[[], str]:
        """Get a strategy for generating image search terms."""

        def strategy() -> str:
            # For Korean nouns, use English translation for better image results
            # Include semantic context to improve search accuracy
            context = f"Korean noun: {self.hangul} ({self.english})"
            if self.semantic_category != "object":
                context += f", Category: {self.semantic_category}"
            if self.usage_notes:
                context += f", Usage: {self.usage_notes}"

            return anthropic_service.generate_image_query(context)

        return strategy

    def get_audio_segments(self) -> dict[str, str]:
        """Get all audio segments needed for Korean noun cards."""
        segments = {
            "word_audio": self.hangul,
        }

        # Add particle pronunciation examples
        segments["particles_audio"] = (
            f"{self.topic_particle}, {self.subject_particle}, {self.object_particle}"
        )

        # Add counter example audio
        if self.counter_example:
            segments["counter_audio"] = self.counter_example

        # Add example sentence audio if available
        if self.example:
            segments["example_audio"] = self.example

        return segments

    def get_primary_word(self) -> str:
        """Get the primary word for filename generation and identification."""
        return self.hangul

    def get_particle_pattern_text(self) -> str:
        """Get particle pattern text for display in flashcards."""
        topic = f"은/는: {self.topic_particle}"
        subject = f"이/가: {self.subject_particle}"
        obj = f"을/를: {self.object_particle}"
        return f"{topic} | {subject} | {obj}"

    def get_counter_information(self) -> str:
        """Get counter information for display."""
        counter_info = f"Counter: {self.primary_counter}"
        if self.counter_example:
            counter_info += f" (ex: {self.counter_example})"
        return counter_info

    def get_grammatical_info(self) -> dict[str, Any]:
        """Get grammatical information about this Korean noun."""
        return {
            "semantic_category": self.semantic_category,
            "primary_counter": self.primary_counter,
            "has_honorific": self.honorific_form is not None,
            "particle_patterns": {
                "topic": self.topic_particle,
                "subject": self.subject_particle,
                "object": self.object_particle,
                "possessive": self.possessive_form,
            },
            "phonological_info": {
                "has_final_consonant": self._has_final_consonant(),
                "romanization": self.romanization,
            },
        }

    def get_display_forms(self) -> dict[str, str]:
        """Get all forms for display in flashcards."""
        forms = {
            "Hangul": self.hangul,
            "Romanization": self.romanization,
            "English": self.english,
            "Topic": self.topic_particle,
            "Subject": self.subject_particle,
            "Object": self.object_particle,
            "Counter": f"{self.primary_counter} ({self.counter_example})"
            if self.counter_example
            else self.primary_counter,
        }

        # Add honorific form if available
        if self.honorific_form:
            forms["Honorific"] = self.honorific_form

        # Add example if available
        if self.example:
            forms["Example"] = self.example
            if self.example_english:
                forms["Example (EN)"] = self.example_english

        return forms

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
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
