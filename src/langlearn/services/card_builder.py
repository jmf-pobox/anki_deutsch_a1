"""Card builder service for Clean Pipeline Architecture.

This service handles the final assembly step in the Clean Pipeline Architecture:
Enriched Records → Cards with applied templates and formatting.
"""

import logging
from pathlib import Path
from typing import Any

from langlearn.backends.base import CardTemplate, NoteType
from langlearn.models.records import BaseRecord, VerbConjugationRecord
from langlearn.services.template_service import TemplateService

logger = logging.getLogger(__name__)


class CardBuilder:
    """Builds formatted cards from enriched records using templates.

    This service represents the final assembly step in Clean Pipeline Architecture:
    CSV → Records → Domain Models → MediaEnricher → Enriched Records → CardBuilder
    """

    def __init__(
        self,
        template_service: TemplateService | None = None,
        project_root: Path | None = None,
    ) -> None:
        """Initialize CardBuilder.

        Args:
            template_service: Service for loading card templates
            project_root: Root path of the project for default template location
        """
        self._project_root = project_root or Path.cwd()

        if template_service is None:
            template_dir = self._project_root / "src" / "langlearn" / "templates"
            template_service = TemplateService(template_dir)

        self._template_service = template_service
        logger.debug(
            "CardBuilder initialized with project root: %s", self._project_root
        )

    def build_card_from_record(
        self, record: BaseRecord, enriched_data: dict[str, Any] | None = None
    ) -> tuple[list[str], NoteType]:
        """Build a formatted card from a record and optional enriched data.

        Args:
            record: The base record (noun, adjective, adverb, negation)
            enriched_data: Optional enriched data with media (merged with record data)

        Returns:
            Tuple of (field_values, note_type) ready for backend.add_note()
        """
        # Get record type from class name
        record_type = self._get_record_type_from_instance(record)
        logger.debug("Building card from %s record", record_type)

        # Merge record data with enriched data
        card_data = record.to_dict()
        if enriched_data:
            card_data.update(enriched_data)

        # Load template for this record type
        template = self._template_service.get_template(record_type)

        # Create note type
        note_type = self._create_note_type_for_record(record_type, template)

        # Extract and format field values
        field_values = self._extract_field_values(record_type, card_data, note_type)

        logger.debug("Built card with %d fields for %s", len(field_values), record_type)
        return field_values, note_type

    def build_cards_from_records(
        self,
        records: list[BaseRecord],
        enriched_data_list: list[dict[str, Any]] | None = None,
    ) -> list[tuple[list[str], NoteType]]:
        """Build multiple cards from records and enriched data.

        Args:
            records: List of base records
            enriched_data_list: Optional list of enriched data dicts
                (same order as records)

        Returns:
            List of (field_values, note_type) tuples ready for backend
        """
        logger.debug("Building cards from %d records", len(records))

        cards = []
        for i, record in enumerate(records):
            enriched_data = (
                enriched_data_list[i]
                if enriched_data_list and i < len(enriched_data_list)
                else None
            )

            try:
                card = self.build_card_from_record(record, enriched_data)
                cards.append(card)
            except Exception as e:
                logger.error("Failed to build card from record %d: %s", i, e)
                continue

        logger.debug("Successfully built %d/%d cards", len(cards), len(records))
        return cards

    def _create_note_type_for_record(
        self, record_type: str, template: CardTemplate
    ) -> NoteType:
        """Create a NoteType for the given record type using template.

        Args:
            record_type: Type of record (noun, adjective, adverb, negation)
            template: Card template to use

        Returns:
            NoteType configured for this record type
        """
        field_names = self._get_field_names_for_record_type(record_type)

        return NoteType(
            name=template.name,
            fields=field_names,
            templates=[template],
        )

    def _get_field_names_for_record_type(self, record_type: str) -> list[str]:
        """Get the field names for a record type.

        Args:
            record_type: Type of record (noun, adjective, adverb, negation)

        Returns:
            List of field names in the correct order
        """
        # Define field mappings for each record type
        # These match the expected Anki card field structure
        field_mappings = {
            "noun": [
                "Noun",
                "Article",
                "English",
                "Plural",
                "Example",
                "Related",
                "Image",
                "WordAudio",
                "ExampleAudio",
            ],
            "adjective": [
                "Word",
                "English",
                "Example",
                "Comparative",
                "Superlative",
                "Image",
                "WordAudio",
                "ExampleAudio",
            ],
            "adverb": [
                "Word",
                "English",
                "Type",
                "Example",
                "Image",
                "WordAudio",
                "ExampleAudio",
            ],
            "negation": [
                "Word",
                "English",
                "Type",
                "Example",
                "Image",
                "WordAudio",
                "ExampleAudio",
            ],
            "verb": [
                "Verb",
                "English",
                "PresentIch",
                "PresentDu",
                "PresentEr",
                "Perfect",
                "Example",
                "Image",
                "WordAudio",
                "ExampleAudio",
            ],
            "phrase": [
                "Phrase",
                "English",
                "Context",
                "Related",
                "Image",
                "PhraseAudio",
            ],
            "preposition": [
                "Preposition",
                "English",
                "Case",
                "Example1",
                "Example2",
                "Image",
                "WordAudio",
                "Example1Audio",
                "Example2Audio",
            ],
            "verb_conjugation": [
                "Infinitive",
                "English",
                "Classification",
                "Separable",
                "Auxiliary",
                "Tense",
                "Ich",
                "Du",
                "Er",
                "Wir",
                "Ihr",
                "Sie",
                "Example",
                "Image",
                "WordAudio",
                "ExampleAudio",
            ],
            "verb_imperative": [
                "Infinitive",
                "English",
                "Meaning",
                "Classification",
                "Separable",
                "DuForm",
                "IhrForm",
                "SieForm",
                "WirForm",
                "ExampleDu",
                "ExampleIhr",
                "ExampleSie",
                "Image",
                "WordAudio",
                "DuAudio",
                "IhrAudio",
                "SieAudio",
                "WirAudio",
            ],
        }

        return field_mappings.get(record_type, [])

    def _extract_field_values(
        self, record_type: str, card_data: dict[str, Any], note_type: NoteType
    ) -> list[str]:
        """Extract field values from card data in the correct order.

        Args:
            record_type: Type of record (noun, adjective, adverb, negation)
            card_data: Merged record and enriched data
            note_type: Note type with field definitions

        Returns:
            List of field values in the order defined by note_type.fields
        """
        field_values = []

        for field_name in note_type.fields:
            # Map Anki field names to record field names
            record_field = self._map_anki_field_to_record_field(field_name, record_type)

            # Get value from card data
            value = card_data.get(record_field, "")

            # Format value if needed
            formatted_value = self._format_field_value(field_name, value)
            field_values.append(formatted_value)

        return field_values

    def _map_anki_field_to_record_field(self, anki_field: str, record_type: str) -> str:
        """Map Anki field names to record field names.

        Args:
            anki_field: Anki field name (e.g., "WordAudio")
            record_type: Type of record (noun, adjective, adverb, negation)

        Returns:
            Corresponding record field name (e.g., "word_audio")
        """
        # Common mappings across all record types
        common_mappings = {
            "Image": "image",
            "WordAudio": "word_audio",
            "ExampleAudio": "example_audio",
            "English": "english",
            "Example": "example",
        }

        # Type-specific mappings
        type_mappings = {
            "noun": {
                "Noun": "noun",
                "Article": "article",
                "Plural": "plural",
                "Related": "related",
            },
            "adjective": {
                "Word": "word",
                "Comparative": "comparative",
                "Superlative": "superlative",
            },
            "adverb": {
                "Word": "word",
                "Type": "type",
            },
            "negation": {
                "Word": "word",
                "Type": "type",
            },
            "verb": {
                "Verb": "verb",
                "PresentIch": "present_ich",
                "PresentDu": "present_du",
                "PresentEr": "present_er",
                "Perfect": "perfect",
            },
            "phrase": {
                "Phrase": "phrase",
                "Context": "context",
                "Related": "related",
                "PhraseAudio": "phrase_audio",
            },
            "preposition": {
                "Preposition": "preposition",
                "Case": "case",
                "Example1": "example1",
                "Example2": "example2",
                "Example1Audio": "example1_audio",
                "Example2Audio": "example2_audio",
            },
            "verb_conjugation": {
                "Infinitive": "infinitive",
                "English": "english",
                "Meaning": "english",
                "Classification": "classification",
                "Separable": "separable",
                "Auxiliary": "auxiliary",
                "Tense": "tense",
                "Ich": "ich",
                "Du": "du",
                "Er": "er",
                "Wir": "wir",
                "Ihr": "ihr",
                "Sie": "sie",
            },
            "verb_imperative": {
                "Infinitive": "infinitive",
                "English": "english",
                "Meaning": "english",
                "Classification": "classification",
                "Separable": "separable",
                "DuForm": "du_form",
                "IhrForm": "ihr_form",
                "SieForm": "sie_form",
                "WirForm": "wir_form",
                "ExampleDu": "example_du",
                "ExampleIhr": "example_ihr",
                "ExampleSie": "example_sie",
                "DuAudio": "du_audio",
                "IhrAudio": "ihr_audio",
                "SieAudio": "sie_audio",
                "WirAudio": "wir_audio",
            },
        }

        # Try type-specific mappings first (they override common mappings)
        if record_type in type_mappings and anki_field in type_mappings[record_type]:
            return type_mappings[record_type][anki_field]

        # Try common mappings second
        if anki_field in common_mappings:
            return common_mappings[anki_field]

        # Fallback: convert to lowercase
        return anki_field.lower()

    def _format_field_value(self, field_name: str, value: Any) -> str:
        """Format field value for Anki card display.

        Args:
            field_name: Name of the field
            value: Raw field value

        Returns:
            Formatted field value as string
        """
        if value is None:
            return ""

        # Handle boolean values (e.g., Separable field)
        if isinstance(value, bool):
            return "Yes" if value else ""

        # Convert to string
        str_value = str(value)

        # Apply field-specific formatting
        if (
            field_name
            in [
                "WordAudio",
                "ExampleAudio",
                "Example1Audio",
                "Example2Audio",
                "PhraseAudio",
                "DuAudio",
                "IhrAudio",
                "SieAudio",
            ]
            and str_value
        ):
            # Ensure audio fields have proper Anki format
            if not str_value.startswith("[sound:") and not str_value.endswith("]"):
                str_value = f"[sound:{str_value}]"

        elif (
            field_name == "Image"
            and str_value
            and not (str_value.startswith("<img") and str_value.endswith(">"))
        ):
            str_value = f'<img src="{str_value}" />'

        return str_value

    def get_supported_record_types(self) -> list[str]:
        """Get list of supported record types.

        Returns:
            List of supported record type names
        """
        return [
            "noun",
            "adjective",
            "adverb",
            "negation",
            "verb",
            "phrase",
            "preposition",
            "verb_conjugation",
            "verb_imperative",
        ]

    def validate_record_for_card_building(self, record: BaseRecord) -> bool:
        """Validate that a record can be used for card building.

        Args:
            record: Record to validate

        Returns:
            True if record is valid for card building
        """
        record_type = self._get_record_type_from_instance(record)

        if record_type not in self.get_supported_record_types():
            logger.warning("Unsupported record type for card building: %s", record_type)
            return False

        # Check that record has required fields
        record_data = record.to_dict()
        required_fields = self._get_required_fields_for_record_type(record_type)

        for field in required_fields:
            if not record_data.get(field):
                logger.warning(
                    "Missing required field '%s' for %s record", field, record_type
                )
                return False

        return True

    def _get_required_fields_for_record_type(self, record_type: str) -> list[str]:
        """Get required fields for card building for a record type.

        Args:
            record_type: Type of record

        Returns:
            List of required field names
        """
        required_fields = {
            "noun": ["noun", "article", "english"],
            "adjective": ["word", "english"],
            "adverb": ["word", "english", "type"],
            "negation": ["word", "english", "type"],
            "verb": ["verb", "english", "present_ich", "present_du", "present_er"],
            "phrase": ["phrase", "english", "context"],
            "preposition": ["preposition", "english", "case", "example1", "example2"],
            "verb_conjugation": ["infinitive", "english", "tense", "ich", "du", "er"],
            "verb_imperative": [
                "infinitive",
                "english",
                "du_form",
                "ihr_form",
                "sie_form",
            ],
        }

        return required_fields.get(record_type, [])

    def _get_record_type_from_instance(self, record: BaseRecord) -> str:
        """Get record type from record instance.

        Args:
            record: Record instance

        Returns:
            Record type string (noun, adjective, adverb, negation)
        """
        class_name = record.__class__.__name__

        # Map class names to record type strings
        class_to_type = {
            "NounRecord": "noun",
            "AdjectiveRecord": "adjective",
            "AdverbRecord": "adverb",
            "NegationRecord": "negation",
            "VerbRecord": "verb",
            "PhraseRecord": "phrase",
            "PrepositionRecord": "preposition",
            "VerbConjugationRecord": "verb_conjugation",
            "VerbImperativeRecord": "verb_imperative",
        }

        return class_to_type.get(class_name, class_name.lower())

    def build_verb_conjugation_cards(
        self,
        records: list[VerbConjugationRecord],
        enriched_data_list: list[dict[str, Any]] | None = None,
    ) -> list[tuple[list[str], NoteType]]:
        """Build multiple tense-specific cards from verb conjugation records.

        This method implements the verb card generation modernization,
        creating 3-4 cards per verb instead of 1 card per verb.

        Args:
            records: List of VerbConjugationRecord instances
            enriched_data_list: Optional enriched data for each record

        Returns:
            List of (field_values, note_type) tuples for multiple cards per verb
        """
        logger.info("Building verb conjugation cards from %d records", len(records))

        # Import here to avoid circular dependency
        from langlearn.services.verb_conjugation_processor import (
            VerbConjugationProcessor,
        )

        # Create processor and delegate to it
        processor = VerbConjugationProcessor(self)
        return processor.process_verb_records(records, enriched_data_list)
