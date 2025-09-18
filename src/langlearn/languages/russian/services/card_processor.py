"""Russian-specific card processing logic."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from langlearn.core.backends.base import NoteType
    from langlearn.core.records import BaseRecord


class RussianCardProcessor:
    """Russian language card processor.

    Handles Russian-specific card generation logic.
    """

    def get_record_to_model_factory(self) -> Any:
        """Get the RecordToModelFactory for Russian language."""
        from langlearn.languages.russian.services.record_to_model_factory import (
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
        """Process Russian records into cards using Russian-specific logic."""
        # Russian currently uses standard single-card generation for all record types
        # Future: Add Russian-specific handling for cases, verb aspects, etc.
        return card_builder.build_cards_from_records(records, enriched_data_list)  # type: ignore[no-any-return]
