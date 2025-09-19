"""Card processing protocol for language-specific card generation logic."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from langlearn.core.records import BaseRecord
    from langlearn.infrastructure.backends.base import NoteType


class LanguageCardProcessor(Protocol):
    """Protocol for language-specific card processing and generation.

    This protocol encapsulates all language-specific logic for converting
    records to cards, including special record type handling, media enrichment
    coordination, and card building.
    """

    def get_record_to_model_factory(self) -> Any:
        """Get the RecordToModelFactory for this language.

        Returns:
            Factory class for creating domain models from records
        """

    def process_records_for_cards(
        self,
        records: list[BaseRecord],
        record_type: str,
        enriched_data_list: list[dict[str, Any]],
        card_builder: Any,
    ) -> list[tuple[list[str], NoteType]]:
        """Process records into cards using language-specific logic.

        Args:
            records: List of records to process
            record_type: Type of records being processed
            enriched_data_list: Media enrichment data for each record
            card_builder: Language-specific card builder

        Returns:
            List of (field_values, note_type) tuples ready for Anki backend
        """
