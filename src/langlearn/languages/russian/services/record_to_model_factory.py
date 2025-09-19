"""Russian RecordToModelFactory for creating domain models from records."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from langlearn.core.records.base_record import BaseRecord

logger = logging.getLogger(__name__)


class RussianNounDomainModel:
    """Simple Russian noun domain model for media generation."""

    def __init__(self, record: BaseRecord) -> None:
        """Initialize Russian noun domain model."""
        # Type guard to ensure we have the right record type
        if not hasattr(record, "noun") or not hasattr(record, "english"):
            raise ValueError(
                "Record must be a Russian noun record with required attributes"
            )

        self.noun = str(record.noun)
        self.english = str(record.english)
        self.gender = str(getattr(record, "gender", ""))
        self.genitive = str(getattr(record, "genitive", ""))
        self.example = str(getattr(record, "example", ""))
        self.related = str(getattr(record, "related", ""))
        self.animacy = str(getattr(record, "animacy", ""))
        self.instrumental = str(getattr(record, "instrumental", ""))
        self.prepositional = str(getattr(record, "prepositional", ""))
        self.dative = str(getattr(record, "dative", ""))
        self.plural_nominative = str(getattr(record, "plural_nominative", ""))
        self.plural_genitive = str(getattr(record, "plural_genitive", ""))

    def get_combined_audio_text(self) -> str:
        """Get combined text for audio generation."""
        return f"{self.noun}. {self.example}" if self.example else self.noun

    def get_image_search_text(self) -> str:
        """Get text for image search."""
        return self.english

    def get_word_audio_text(self) -> str:
        """Get word audio text."""
        return self.noun

    def get_example_audio_text(self) -> str:
        """Get example audio text."""
        return self.example if self.example else ""

    def get_primary_word(self) -> str:
        """Get primary word for filename generation and identification."""
        return self.noun

    def get_audio_segments(self) -> dict[str, str]:
        """Get audio segments for media generation."""
        segments = {}

        # Word audio
        if self.noun:
            segments["word_audio"] = self.noun

        # Example audio
        if self.example:
            segments["example_audio"] = self.example

        return segments

    def get_image_search_strategy(self, ai_service: Any) -> Callable[[], str]:
        """Get image search strategy with AI service dependency injection."""

        def search_strategy() -> str:
            return self.english  # Return English translation for image search

        return search_strategy


class RecordToModelFactory:
    """Factory for creating Russian domain models from records."""

    @staticmethod
    def create_domain_model(record: BaseRecord) -> Any:
        """Create Russian domain model from record."""
        record_type = record.get_record_type().value

        if record_type == "noun":
            return RussianNounDomainModel(record)
        else:
            raise ValueError(f"Unsupported Russian record type: {record_type}")
