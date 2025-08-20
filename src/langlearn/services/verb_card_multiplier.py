"""VerbCardMultiplier service for German verb flashcard generation.

This service handles the 1-to-N card generation for German verbs, creating
multiple cards per verb based on CEFR level and verb type (conjugation vs imperative).
"""

import logging
from dataclasses import dataclass
from typing import Any

from langlearn.models.records import (
    BaseRecord,
    VerbConjugationRecord,
    VerbImperativeRecord,
)

logger = logging.getLogger(__name__)


@dataclass
class VerbCardConfig:
    """Configuration for verb card generation based on CEFR level."""

    cefr_level: str = "A1"  # A1, A2, B1
    include_conjugations: bool = True
    include_imperatives: bool = True
    max_tenses_per_verb: int = 3  # A1: 3, A2: 5, B1: 7

    @classmethod
    def for_cefr_level(cls, level: str) -> "VerbCardConfig":
        """Create config appropriate for CEFR level.

        Args:
            level: CEFR level (A1, A2, B1)

        Returns:
            VerbCardConfig with appropriate settings
        """
        if level == "A1":
            return cls(
                cefr_level="A1",
                include_conjugations=True,
                include_imperatives=True,
                max_tenses_per_verb=3,  # present, preterite, perfect
            )
        elif level == "A2":
            return cls(
                cefr_level="A2",
                include_conjugations=True,
                include_imperatives=True,
                max_tenses_per_verb=5,  # present, preterite, perfect, future,
                # subjunctive
            )
        elif level == "B1":
            return cls(
                cefr_level="B1",
                include_conjugations=True,
                include_imperatives=True,
                max_tenses_per_verb=7,  # all tenses
            )
        else:
            logger.warning("Unknown CEFR level %s, defaulting to A1", level)
            return cls.for_cefr_level("A1")


class VerbCardMultiplier:
    """Service for generating multiple cards from verb records.

    Implements the two-tier German verb flashcard system:
    - One core verb card per verb (basic meaning and classification)
    - Multiple conjugation/imperative cards per tense based on CEFR level

    This service takes verb records and expands them into multiple card records
    suitable for CardBuilder processing.
    """

    def __init__(self, config: VerbCardConfig | None = None) -> None:
        """Initialize VerbCardMultiplier.

        Args:
            config: Configuration for card generation (defaults to A1)
        """
        self._config = config or VerbCardConfig.for_cefr_level("A1")
        logger.debug(
            "VerbCardMultiplier initialized for CEFR level: %s", self._config.cefr_level
        )

    def multiply_verb_records(
        self,
        verb_records: list[BaseRecord],
        enriched_data_list: list[dict[str, Any]] | None = None,
    ) -> list[BaseRecord]:
        """Generate multiple cards from verb records.

        This is the main entry point that takes raw verb records and produces
        the expanded list of records for CardBuilder.

        Args:
            verb_records: List of verb records (VerbConjugationRecord,
                         VerbImperativeRecord)
            enriched_data_list: Optional enriched media data

        Returns:
            Expanded list of verb records ready for CardBuilder

        Raises:
            ValueError: If unsupported record type is provided
        """
        logger.debug(
            "Multiplying %d verb records for CEFR level %s",
            len(verb_records),
            self._config.cefr_level,
        )

        expanded_records: list[BaseRecord] = []

        for i, record in enumerate(verb_records):
            enriched_data = (
                enriched_data_list[i]
                if enriched_data_list and i < len(enriched_data_list)
                else None
            )

            try:
                # Generate cards based on record type
                if isinstance(record, VerbConjugationRecord):
                    cards: list[BaseRecord] = self._multiply_conjugation_record(
                        record, enriched_data
                    )
                elif isinstance(record, VerbImperativeRecord):
                    cards = self._multiply_imperative_record(record, enriched_data)
                else:
                    logger.warning(
                        "Unsupported record type for multiplication: %s",
                        type(record).__name__,
                    )
                    # Pass through non-verb records unchanged
                    cards = [record]

                expanded_records.extend(cards)

            except Exception as e:
                logger.error(
                    "Failed to multiply verb record %d (%s): %s",
                    i,
                    getattr(record, "infinitive", "unknown"),
                    e,
                )
                # Include original record on error to avoid data loss
                expanded_records.append(record)

        logger.info(
            "Expanded %d verb records into %d cards (%dx multiplier)",
            len(verb_records),
            len(expanded_records),
            len(expanded_records) / len(verb_records) if verb_records else 0,
        )

        return expanded_records

    def _multiply_conjugation_record(
        self, record: VerbConjugationRecord, enriched_data: dict[str, Any] | None = None
    ) -> list[BaseRecord]:
        """Generate multiple cards from a single conjugation record.

        For conjugation records, we maintain the original structure but may
        filter based on CEFR level tense requirements.

        Args:
            record: Verb conjugation record
            enriched_data: Optional enriched media data
                          (ignored - handled by MediaEnricher)

        Returns:
            List of conjugation records (typically just the original)
        """
        logger.debug(
            "Processing conjugation record for %s (%s tense)",
            record.infinitive,
            record.tense,
        )

        # Check if this tense is appropriate for the CEFR level
        if not self._is_tense_appropriate_for_level(record.tense):
            logger.debug(
                "Skipping %s tense for %s (not appropriate for %s level)",
                record.tense,
                record.infinitive,
                self._config.cefr_level,
            )
            return []

        # For conjugation records, we return the original record unchanged
        # The 1-to-N expansion happens at the CSV level (one row per tense)
        # MediaEnricher will handle media field population later in the pipeline

        return [record]

    def _multiply_imperative_record(
        self, record: VerbImperativeRecord, enriched_data: dict[str, Any] | None = None
    ) -> list[BaseRecord]:
        """Generate multiple cards from a single imperative record.

        For imperative records, we typically return just the original since
        imperatives don't have tense variations like conjugations.

        Args:
            record: Verb imperative record
            enriched_data: Optional enriched media data
                          (ignored - handled by MediaEnricher)

        Returns:
            List of imperative records (typically just the original)
        """
        logger.debug("Processing imperative record for %s", record.infinitive)

        # Imperatives are simpler - they don't have tense variations
        # We include them at all CEFR levels since they're fundamental
        # MediaEnricher will handle media field population later in the pipeline

        return [record]

    def _is_tense_appropriate_for_level(self, tense: str) -> bool:
        """Check if a tense is appropriate for the current CEFR level.

        Args:
            tense: Tense name (present, preterite, perfect, future, subjunctive)

        Returns:
            True if tense should be included at this level
        """
        # Define tense progression by CEFR level
        level_tenses = {
            "A1": {"present", "preterite", "perfect"},
            "A2": {"present", "preterite", "perfect", "future"},
            "B1": {"present", "preterite", "perfect", "future", "subjunctive"},
        }

        allowed_tenses = level_tenses.get(self._config.cefr_level, set())
        return tense.lower() in allowed_tenses

    def get_expected_card_count(self, verb_records: list[BaseRecord]) -> int:
        """Calculate expected number of cards after multiplication.

        Args:
            verb_records: List of input verb records

        Returns:
            Expected number of output cards
        """
        count = 0

        for record in verb_records:
            if isinstance(record, VerbConjugationRecord):
                # Check if tense is appropriate for CEFR level
                if self._is_tense_appropriate_for_level(record.tense):
                    count += 1
            elif isinstance(record, VerbImperativeRecord):
                # Imperatives are included at all levels
                count += 1
            else:
                # Non-verb records pass through unchanged
                count += 1

        return count

    def get_config(self) -> VerbCardConfig:
        """Get current configuration.

        Returns:
            Current VerbCardConfig
        """
        return self._config

    def update_config(self, config: VerbCardConfig) -> None:
        """Update configuration.

        Args:
            config: New configuration to use
        """
        self._config = config
        logger.debug(
            "VerbCardMultiplier configuration updated to CEFR level: %s",
            config.cefr_level,
        )
