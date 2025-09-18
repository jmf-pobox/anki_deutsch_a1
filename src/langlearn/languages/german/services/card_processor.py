"""German-specific card processing logic."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from langlearn.core.backends.base import NoteType
    from langlearn.core.records import BaseRecord

logger = logging.getLogger(__name__)


class GermanCardProcessor:
    """German language card processor handling German-specific card generation logic."""

    def get_record_to_model_factory(self) -> Any:
        """Get the RecordToModelFactory for German language."""
        from langlearn.languages.german.services.record_to_model_factory import (
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
        """Process German records into cards using German-specific logic."""
        # Special handling for verb conjugation records - use multi-card generation
        if record_type == "verbconjugation":
            from langlearn.languages.german.records.factory import (
                VerbConjugationRecord,
            )

            # Cast records to the proper type for verb conjugation processing
            verb_records = [r for r in records if isinstance(r, VerbConjugationRecord)]
            logger.info(
                f"Using verb conjugation multi-card generation for "
                f"{len(verb_records)} records"
            )

            return card_builder.build_verb_conjugation_cards(  # type: ignore[no-any-return]
                verb_records, enriched_data_list
            )

        # Special handling for unified articles (MediaEnricher + specialized cards)
        elif record_type == "unified_article":
            from langlearn.languages.german.records.factory import (
                ArticleRecord,
                IndefiniteArticleRecord,
                NegativeArticleRecord,
                UnifiedArticleRecord,
            )

            # Filter unified article records (supporting all article types)
            article_records = [
                r
                for r in records
                if isinstance(
                    r,
                    ArticleRecord
                    | IndefiniteArticleRecord
                    | NegativeArticleRecord
                    | UnifiedArticleRecord,
                )
            ]

            # Use specialized article card building WITH enriched media data
            return card_builder.build_article_pattern_cards(  # type: ignore[no-any-return]
                article_records, enriched_data_list
            )
        else:
            # Standard single-card generation for other record types
            return card_builder.build_cards_from_records(records, enriched_data_list)  # type: ignore[no-any-return]
