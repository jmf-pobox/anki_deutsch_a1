"""Korean RecordToModelFactory for creating domain models from records."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from langlearn.core.records.base_record import BaseRecord

logger = logging.getLogger(__name__)


class KoreanNounDomainModel:
    """Korean noun domain model for media generation and card display."""

    def __init__(self, record: BaseRecord) -> None:
        """Initialize Korean noun domain model."""
        # Type guard to ensure we have the right record type
        if not hasattr(record, "hangul") or not hasattr(record, "english"):
            raise ValueError(
                "Record must be a Korean noun record with required attributes"
            )

        self.hangul = str(getattr(record, "hangul", ""))
        self.romanization = str(getattr(record, "romanization", ""))
        self.english = str(getattr(record, "english", ""))
        self.topic_particle = str(getattr(record, "topic_particle", ""))
        self.subject_particle = str(getattr(record, "subject_particle", ""))
        self.object_particle = str(getattr(record, "object_particle", ""))
        self.possessive_form = str(getattr(record, "possessive_form", ""))
        self.primary_counter = str(getattr(record, "primary_counter", ""))
        self.counter_example = str(getattr(record, "counter_example", ""))
        self.honorific_form = str(getattr(record, "honorific_form", ""))
        self.semantic_category = str(getattr(record, "semantic_category", ""))
        self.example = str(getattr(record, "example", ""))
        self.example_english = str(getattr(record, "example_english", ""))
        self.usage_notes = str(getattr(record, "usage_notes", ""))

    def get_combined_audio_text(self) -> str:
        """Get combined text for Korean audio generation."""
        return f"{self.hangul}. {self.example}" if self.example else self.hangul

    def get_primary_word(self) -> str:
        """Get the primary word for image generation (required by MediaService)."""
        return self.hangul

    def get_audio_segments(self) -> dict[str, str]:
        """Get audio segments for Korean noun."""
        segments = {}

        # Word audio (Hangul pronunciation)
        if self.hangul:
            segments["word_audio"] = self.hangul

        # Example audio (Korean sentence)
        if self.example:
            segments["example_audio"] = self.example

        return segments

    def get_image_search_strategy(self, ai_service: Any) -> Callable[[], str]:
        """Get image search strategy with AI service dependency injection."""

        def search_strategy() -> str:
            return self.english  # Return English translation for image search

        return search_strategy


class RecordToModelFactory:
    """Factory for creating Korean domain models from records."""

    @staticmethod
    def create_domain_model(record: BaseRecord) -> Any:
        """Create Korean domain model from record."""
        record_type = record.get_record_type().value

        if record_type == "korean_noun":
            return KoreanNounDomainModel(record)
        else:
            raise ValueError(f"Unsupported Korean record type: {record_type}")
