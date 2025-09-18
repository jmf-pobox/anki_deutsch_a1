"""Korean-specific card processing logic."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from langlearn.core.backends.base import NoteType
    from langlearn.core.records import BaseRecord


class KoreanCardProcessor:
    """Korean language card processor handling Korean-specific card generation logic."""

    def get_record_to_model_factory(self) -> Any:
        """Get the RecordToModelFactory for Korean language."""
        from langlearn.languages.korean.services.record_to_model_factory import (
            RecordToModelFactory,
        )

        return RecordToModelFactory

    def process_records_for_cards(
        self,
        records: list[BaseRecord],
        record_type: str,
        enriched_data_list: list[dict[str, Any]],
        card_builder: Any,
    ) -> list[tuple[list[str], NoteType]]:
        """Process Korean records into cards using Korean-specific logic."""
        # Korean currently uses standard single-card generation for all record types
        # Future: Add Korean-specific handling for honorifics, particles, etc.
        return card_builder.build_cards_from_records(records, enriched_data_list)  # type: ignore[no-any-return]
