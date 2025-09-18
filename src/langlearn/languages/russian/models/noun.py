"""Russian noun domain model with business logic."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

from langlearn.core.protocols.media_generation_protocol import MediaGenerationCapable

if TYPE_CHECKING:
    from collections.abc import Callable

    from langlearn.core.protocols.image_query_generation_protocol import (
        ImageQueryGenerationProtocol,
    )


@dataclass
class RussianNoun(MediaGenerationCapable):
    """Russian noun domain model with grammatical knowledge and media generation."""

    # Core noun data
    noun: str
    english: str
    example: str = ""
    related: str = ""

    # Russian grammatical features
    gender: Literal["masculine", "feminine", "neuter"] = "masculine"
    animacy: Literal["animate", "inanimate"] = "inanimate"

    # Case declensions
    nominative: str = ""
    genitive: str = ""
    accusative: str = ""
    instrumental: str = ""
    prepositional: str = ""
    dative: str = ""

    # Plural forms
    plural_nominative: str = ""
    plural_genitive: str = ""

    def __post_init__(self) -> None:
        """Initialize derived fields after dataclass creation."""
        if not self.nominative:
            self.nominative = self.noun

        # Russian-specific accusative logic
        if not self.accusative:
            if self.animacy == "animate":
                self.accusative = self.genitive if self.genitive else self.noun
            else:
                self.accusative = self.nominative

    def get_combined_audio_text(self) -> str:
        """Get text for audio generation using Russian pronunciation patterns."""
        # For Russian, we want the base form pronounced clearly
        return self.noun

    def get_image_search_strategy(
        self, anthropic_service: ImageQueryGenerationProtocol
    ) -> Callable[[], str]:
        """Get a strategy for generating image search terms."""

        def strategy() -> str:
            # For Russian nouns, use the English translation for image search
            # This ensures better image matching in international databases
            context = (
                f"Russian noun: {self.noun} ({self.english}), Gender: {self.gender}"
            )
            return anthropic_service.generate_image_query(context)

        return strategy

    def get_audio_segments(self) -> dict[str, str]:
        """Get all audio segments needed for Russian noun cards."""
        segments = {
            "word_audio": self.noun,
        }

        # Add example audio if available
        if self.example:
            segments["example_audio"] = self.example

        # Add case pattern audio for pronunciation learning
        case_text = self.get_case_pattern_text()
        if case_text != self.noun:  # Only if we have case forms
            segments["cases_audio"] = case_text

        return segments

    def get_primary_word(self) -> str:
        """Get the primary word for filename generation and identification."""
        return self.noun

    def get_case_pattern_text(self) -> str:
        """Get text showing case pattern for audio generation."""
        # Create a pattern showing key case forms
        cases = []
        if self.nominative:
            cases.append(f"именительный {self.nominative}")
        if self.genitive:
            cases.append(f"родительный {self.genitive}")
        if self.accusative and self.accusative != self.nominative:
            cases.append(f"винительный {self.accusative}")

        return ", ".join(cases) if cases else self.noun

    def get_grammatical_info(self) -> dict[str, Any]:
        """Get grammatical information about this noun."""
        return {
            "gender": self.gender,
            "animacy": self.animacy,
            "base_form": self.noun,
            "primary_cases": {
                "nominative": self.nominative,
                "genitive": self.genitive,
                "accusative": self.accusative,
            },
        }

    def get_display_forms(self) -> dict[str, str]:
        """Get all forms for display in flashcards."""
        forms = {"Base": self.noun, "English": self.english}

        # Add case forms
        if self.genitive:
            forms["Genitive"] = self.genitive
        if self.accusative and self.accusative != self.nominative:
            forms["Accusative"] = self.accusative
        if self.instrumental:
            forms["Instrumental"] = self.instrumental
        if self.prepositional:
            forms["Prepositional"] = self.prepositional
        if self.dative:
            forms["Dative"] = self.dative

        # Add plural forms
        if self.plural_nominative:
            forms["Plural"] = self.plural_nominative

        return forms

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
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
