"""Verb conjugation processor for multi-tense card generation.

This service processes VerbConjugationRecord instances to generate multiple
tense-specific cards, transforming from 1 card per verb to 3-4 cards per verb.
"""

import logging
from collections import defaultdict

# Use TYPE_CHECKING to avoid circular imports
from typing import TYPE_CHECKING, Any

from langlearn.backends.base import NoteType
from langlearn.languages.german.records.records import VerbConjugationRecord

if TYPE_CHECKING:
    from langlearn.services.card_builder import CardBuilder

logger = logging.getLogger(__name__)


class VerbConjugationProcessor:
    """Processes VerbConjugationRecord into multiple tense-specific cards.

    This service implements the core logic for the verb card generation
    modernization, creating separate cards for each tense type rather than
    combining all tenses into a single overwhelming card.
    """

    def __init__(self, card_builder: "CardBuilder") -> None:
        """Initialize the processor with a CardBuilder instance.

        Args:
            card_builder: CardBuilder service for creating formatted cards
        """
        self._card_builder = card_builder
        logger.debug("VerbConjugationProcessor initialized")

    def process_verb_records(
        self,
        records: list[VerbConjugationRecord],
        enriched_data_list: list[dict[str, Any]] | None = None,
    ) -> list[tuple[list[str], NoteType]]:
        """Generate multiple tense-specific cards from verb records.

        Transforms the approach from 1 card per verb to 3-4 cards per verb:
        - Present tense card (6-person conjugation table)
        - Perfect tense card (auxiliary + participle focus)
        - Imperative card (4 imperative forms)
        - Optional preterite card (irregular verbs only)

        Args:
            records: List of VerbConjugationRecord instances
            enriched_data_list: Optional enriched data (media) for each record

        Returns:
            List of (field_values, note_type) tuples ready for Anki backend

        Raises:
            MediaGenerationError: If verb card generation fails
        """
        logger.info(
            "Processing %d verb records for multi-card generation", len(records)
        )

        # Group records by infinitive (each verb has multiple tense records)
        verb_groups = self._group_records_by_infinitive(records)
        logger.debug("Grouped into %d unique verbs", len(verb_groups))

        all_cards = []
        enriched_data_dict = self._create_enriched_data_dict(
            records, enriched_data_list
        )

        for infinitive, verb_records in verb_groups.items():
            try:
                verb_cards = self._create_cards_for_verb(
                    infinitive, verb_records, enriched_data_dict
                )
                all_cards.extend(verb_cards)
                logger.debug(
                    "Created %d cards for verb '%s'", len(verb_cards), infinitive
                )
            except Exception as e:
                logger.error("Failed to create cards for verb '%s': %s", infinitive, e)
                from langlearn.exceptions import MediaGenerationError

                raise MediaGenerationError(
                    f"Failed to create cards for verb '{infinitive}': {e}"
                ) from e

        logger.info(
            "Successfully generated %d total cards from %d verbs",
            len(all_cards),
            len(verb_groups),
        )
        return all_cards

    def _group_records_by_infinitive(
        self, records: list[VerbConjugationRecord]
    ) -> dict[str, list[VerbConjugationRecord]]:
        """Group VerbConjugationRecord instances by infinitive.

        Args:
            records: List of verb conjugation records

        Returns:
            Dictionary mapping infinitive -> list of tense records for that verb
        """
        groups: dict[str, list[VerbConjugationRecord]] = defaultdict(list)

        for record in records:
            groups[record.infinitive].append(record)

        # Sort each group's records by tense priority for consistent ordering
        for infinitive, verb_records in groups.items():
            groups[infinitive] = self._sort_records_by_tense_priority(verb_records)

        return dict(groups)

    def _sort_records_by_tense_priority(
        self, records: list[VerbConjugationRecord]
    ) -> list[VerbConjugationRecord]:
        """Sort records by pedagogical tense priority for A1 learners.

        Priority order: present -> perfect -> imperative -> preterite

        Args:
            records: List of records for a single verb

        Returns:
            Records sorted by tense priority
        """
        tense_priority = {"present": 1, "perfect": 2, "imperative": 3, "preterite": 4}

        return sorted(records, key=lambda r: tense_priority.get(r.tense, 5))

    def _create_enriched_data_dict(
        self,
        records: list[VerbConjugationRecord],
        enriched_data_list: list[dict[str, Any]] | None,
    ) -> dict[str, dict[str, Any]]:
        """Create lookup dictionary for enriched data by record key.

        Args:
            records: List of verb conjugation records
            enriched_data_list: Optional enriched data list

        Returns:
            Dictionary mapping record key -> enriched data
        """
        if not enriched_data_list:
            return {}

        enriched_dict = {}
        for i, record in enumerate(records):
            if i < len(enriched_data_list):
                # Create unique key for each tense of each verb
                key = f"{record.infinitive}_{record.tense}"
                enriched_dict[key] = enriched_data_list[i]

        return enriched_dict

    def _create_cards_for_verb(
        self,
        infinitive: str,
        verb_records: list[VerbConjugationRecord],
        enriched_data_dict: dict[str, dict[str, Any]],
    ) -> list[tuple[list[str], NoteType]]:
        """Create tense-specific cards for a single verb.

        Args:
            infinitive: The verb infinitive (e.g., "gehen")
            verb_records: All tense records for this verb
            enriched_data_dict: Enriched data lookup dictionary

        Returns:
            List of cards for this verb (one per available tense)
            Cards are ordered: imperative, present, perfect, preterite
        """
        cards = []

        # Sort records: imperative first, then present, perfect, preterite
        def tense_sort_key(record: VerbConjugationRecord) -> int:
            if record.tense == "imperative":
                return 1  # First
            elif record.tense == "present":
                return 2  # Second
            elif record.tense == "perfect":
                return 3  # Third
            elif record.tense == "preterite":
                return 4  # Fourth
            else:
                return 5  # Any other tenses last

        sorted_records = sorted(verb_records, key=tense_sort_key)

        for record in sorted_records:
            try:
                # Skip tenses that shouldn't generate cards
                if not self._should_create_card_for_tense(record):
                    continue

                # Get enriched data for this specific tense
                record_key = f"{record.infinitive}_{record.tense}"
                enriched_data = enriched_data_dict.get(record_key)

                # Create tense-specific card
                card = self._create_tense_specific_card(record, enriched_data)
                if card:
                    cards.append(card)

            except Exception as e:
                logger.error(
                    "Failed to create %s card for %s: %s", record.tense, infinitive, e
                )
                from langlearn.exceptions import MediaGenerationError

                raise MediaGenerationError(
                    f"Failed to create {record.tense} card for {infinitive}: {e}"
                ) from e

        return cards

    def _should_create_card_for_tense(self, record: VerbConjugationRecord) -> bool:
        """Determine if a card should be created for this tense.

        Args:
            record: Verb conjugation record

        Returns:
            True if card should be created
        """
        # Always create cards for core A1 tenses
        if record.tense in {"present", "perfect", "imperative"}:
            return True

        # Only create preterite cards for irregular high-frequency verbs
        if record.tense == "preterite":
            high_frequency_irregulars = {
                "sein",
                "haben",
                "werden",
                "gehen",
                "kommen",
                "sehen",
                "wissen",
                "geben",
                "nehmen",
                "können",
                "müssen",
                "wollen",
            }
            return (
                record.infinitive in high_frequency_irregulars
                and record.classification == "unregelmäßig"
            )

        return False

    def _create_tense_specific_card(
        self, record: VerbConjugationRecord, enriched_data: dict[str, Any] | None
    ) -> tuple[list[str], NoteType] | None:
        """Create a card for a specific tense using appropriate template.

        Args:
            record: Verb conjugation record for specific tense
            enriched_data: Optional enriched data (audio, images)

        Returns:
            Formatted card tuple or None if creation failed

        Raises:
            MediaGenerationError: If card creation fails
        """
        # Map tense to specific record type for template selection
        tense_to_record_type = {
            "present": "verb_conjugation",
            "perfect": "verb_conjugation",
            "preterite": "verb_conjugation",
            "imperative": "verb_imperative",
        }

        record_type = tense_to_record_type.get(record.tense)
        if not record_type:
            logger.warning("Unknown tense type: %s", record.tense)
            return None

        try:
            # For imperative cards, create special imperative record format
            if record.tense == "imperative":
                return self._create_imperative_card(record, enriched_data)
            else:
                # For conjugation cards (present, perfect, preterite)
                return self._create_conjugation_card(record, enriched_data)

        except Exception as e:
            logger.error(
                "Failed to create %s card for %s: %s",
                record.tense,
                record.infinitive,
                e,
            )
            from langlearn.exceptions import MediaGenerationError

            raise MediaGenerationError(
                f"Failed to create {record.tense} card for {record.infinitive}: {e}"
            ) from e

    def _create_conjugation_card(
        self, record: VerbConjugationRecord, enriched_data: dict[str, Any] | None
    ) -> tuple[list[str], NoteType]:
        """Create a conjugation table card (present/perfect/preterite).

        Args:
            record: Verb conjugation record
            enriched_data: Optional enriched data

        Returns:
            Formatted conjugation card
        """
        # Use CardBuilder's existing verb_conjugation support
        return self._card_builder.build_card_from_record(record, enriched_data)

    def _create_imperative_card(
        self, record: VerbConjugationRecord, enriched_data: dict[str, Any] | None
    ) -> tuple[list[str], NoteType]:
        """Create an imperative-specific card with all 4 forms.

        Args:
            record: Imperative verb conjugation record
            enriched_data: Optional enriched data

        Returns:
            Formatted imperative card
        """
        # Transform conjugation record data to imperative card format
        imperative_data = {
            "infinitive": record.infinitive,
            "english": record.english,
            "classification": record.classification,
            "separable": record.separable,
            # Map conjugation fields to imperative forms (use expected keys)
            "du": record.du,  # du form
            "ihr": record.ihr,  # ihr form
            "sie": record.sie,  # Sie form (formal)
            "wir": record.wir,  # wir form (let's...)
            # Single example used for all example fields per mapping
            "example": record.example,
        }

        # Add enriched data if available
        if enriched_data:
            imperative_data.update(enriched_data)

        # Use CardBuilder's direct field mapping approach for imperative cards
        return self._create_imperative_card_direct(imperative_data)

    def _create_imperative_card_direct(
        self, imperative_data: dict[str, Any]
    ) -> tuple[list[str], NoteType]:
        """Create imperative card using direct field mapping.

        Args:
            imperative_data: Imperative card data dictionary

        Returns:
            Formatted imperative card tuple
        """
        # Get field names for verb_imperative type
        field_names = self._card_builder._get_field_names_for_record_type(
            "verb_imperative"
        )

        # Load template for imperative cards
        template = self._card_builder._template_service.get_template("verb_imperative")

        # Create note type
        note_type = NoteType(
            name=template.name,
            fields=field_names,
            templates=[template],
        )

        # Map data to field values in correct order
        field_values = []
        for field_name in field_names:
            # Map Anki field names to data keys
            data_key = self._map_imperative_field_to_data_key(field_name)
            value = imperative_data.get(data_key, "")

            # Format the value
            formatted_value = self._card_builder._format_field_value(field_name, value)
            field_values.append(formatted_value)

        return field_values, note_type

    def _map_imperative_field_to_data_key(self, field_name: str) -> str:
        """Map Anki imperative field names to data dictionary keys.

        Args:
            field_name: Anki field name

        Returns:
            Corresponding data dictionary key
        """
        # Mapping from CardBuilder field names to our data keys
        mapping = {
            "Infinitive": "infinitive",
            "English": "english",
            "Du": "du",
            "Ihr": "ihr",
            "Sie": "sie",
            "Wir": "wir",
            "Example": "example",
            "ExampleDu": "example",
            "ExampleIhr": "example",
            "ExampleSie": "example",
            "Image": "image",
            "WordAudio": "word_audio",
        }

        return mapping.get(field_name, field_name.lower())

    def get_expected_card_count(self, records: list[VerbConjugationRecord]) -> int:
        """Calculate expected number of cards from given records.

        Args:
            records: List of verb conjugation records

        Returns:
            Expected number of cards to be generated
        """
        verb_groups = self._group_records_by_infinitive(records)
        total_cards = 0

        for verb_records in verb_groups.values():
            for record in verb_records:
                if self._should_create_card_for_tense(record):
                    total_cards += 1

        return total_cards

    def get_supported_tenses(self) -> list[str]:
        """Get list of tenses supported for card generation.

        Returns:
            List of supported tense names
        """
        return ["present", "perfect", "imperative", "preterite"]

    def validate_records_for_processing(
        self, records: list[VerbConjugationRecord]
    ) -> list[str]:
        """Validate records and return list of any validation errors.

        Args:
            records: List of records to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        if not records:
            errors.append("No records provided for processing")
            return errors

        # Check for required fields in each record
        for i, record in enumerate(records):
            if not record.infinitive:
                errors.append(f"Record {i}: Missing infinitive")
            if not record.english:
                errors.append(f"Record {i}: Missing english")
            if not record.tense:
                errors.append(f"Record {i}: Missing tense")

        # Check for reasonable data distribution
        verb_groups = self._group_records_by_infinitive(records)
        if len(verb_groups) < 10:
            errors.append(f"Very few verbs ({len(verb_groups)}) - expected at least 10")

        return errors
