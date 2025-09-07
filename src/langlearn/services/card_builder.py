"""Card builder service for Clean Pipeline Architecture.

This service handles the final assembly step in the Clean Pipeline Architecture:
Enriched Records → Cards with applied templates and formatting.
"""

import logging
from pathlib import Path
from typing import Any

from langlearn.backends.base import CardTemplate, NoteType
from langlearn.models.records import (
    ArticleRecord,
    BaseRecord,
    IndefiniteArticleRecord,
    NegativeArticleRecord,
    NounRecord,
    UnifiedArticleRecord,
    VerbConjugationRecord,
)
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

        # Initialize article application service for noun-article cards
        from langlearn.services.article_application_service import (
            ArticleApplicationService,
        )

        self._article_application_service = ArticleApplicationService(self)

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
        else:
            logger.debug(f"No enriched_data provided for {record_type} record")

        # Load template for this record type
        template = self._template_service.get_template(record_type)

        # Create note type
        note_type = self._create_note_type_for_record(record_type, template)

        # Extract and format field values
        field_values = self._extract_field_values(record_type, card_data, note_type)

        field_summary = ", ".join(
            [
                f"({i}) {v[:20]}..." if len(v) > 20 else f"({i}) {v}"
                for i, v in enumerate(field_values)
            ]
        )
        logger.info(
            f"[FIELD ORDER] Final field_values for {record_type}: [{field_summary}]"
        )

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

        Raises:
            MediaGenerationError: If any card building fails
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
                from langlearn.exceptions import MediaGenerationError

                raise MediaGenerationError(
                    f"Failed to build card from record {i}: {e}"
                ) from e

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

        logger.info(
            f"[FIELD ORDER] NoteType field names for {record_type}: {field_names}"
        )

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
                "Classification",
                "PresentIch",
                "PresentDu",
                "PresentEr",
                "Präteritum",
                "Auxiliary",
                "Perfect",
                "Example",
                "Separable",
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
                "Infinitive",  # Sort Field - primary identifier
                "English",
                "Du",
                "Ihr",
                "Sie",
                "Wir",
                "ExampleDu",
                "ExampleIhr",
                "ExampleSie",
                "Image",
                "WordAudio",
            ],
            "artikel_gender_cloze": [
                "Text",
                "Explanation",
                "Image",
                "Audio",
            ],
            "artikel_context_cloze": [
                "Text",
                "Explanation",
                "Image",
                "Audio",
            ],
            "artikel_gender": [
                "FrontText",
                "BackText",
                "Gender",
                "Nominative",
                "Accusative",
                "Dative",
                "Genitive",
                "ExampleNom",
                "Image",
                "ArticleAudio",
                "ExampleAudio",
                "ArtikelTypBestimmt",
                "ArtikelTypUnbestimmt",
                "ArtikelTypVerneinend",
                "NounOnly",
                "NounEnglish",
            ],
            "artikel_context": [
                "FrontText",
                "BackText",
                "Gender",
                "Case",
                "CaseRule",
                "ArticleForm",
                "CaseUsage",
                "Nominative",
                "Accusative",
                "Dative",
                "Genitive",
                "CaseNominative",
                "CaseAccusative",
                "CaseDative",
                "CaseGenitive",
                "Image",
                "ExampleAudio",
                "ArtikelTypBestimmt",
                "ArtikelTypUnbestimmt",
                "ArtikelTypVerneinend",
                "NounOnly",
                "NounEnglish",
            ],
            "noun_article_recognition": [
                "FrontText",
                "BackText",
                "Noun",
                "Article",
                "English",
                "Plural",
                "Example",
                "Related",
                "Image",
                "WordAudio",
                "NounOnly",
                "NounEnglishWithArticle",
            ],
            "noun_case_context": [
                "FrontText",
                "BackText",
                "Noun",
                "Article",
                "Case",
                "CaseRule",
                "ArticleForm",
                "CaseUsage",
                "English",
                "Plural",
                "CaseNominativ",
                "CaseAkkusativ",
                "CaseDativ",
                "CaseGenitiv",
                "Image",
                "WordAudio",
                "ExampleAudio",
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

            # DIAGNOSTIC: Log media field mapping
            if field_name in ["Image", "WordAudio", "ExampleAudio"]:
                logger.info(
                    f"[MEDIA TRACE] Mapping {field_name} -> {record_field} = "
                    f"{value or 'EMPTY'}"
                )

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
                "Classification": "classification",
                "PresentIch": "present_ich",
                "PresentDu": "present_du",
                "PresentEr": "present_er",
                "Präteritum": "präteritum",
                "Auxiliary": "auxiliary",
                "Perfect": "perfect",
                "Separable": "separable",
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
                "Du": "du",
                "Ihr": "ihr",
                "Sie": "sie",
                "Wir": "wir",
                "ExampleDu": "example_du",
                "ExampleIhr": "example_ihr",
                "ExampleSie": "example_sie",
            },
            # Article cloze deletion cards
            "artikel_gender_cloze": {
                "Text": "Text",
                "Explanation": "Explanation",
                "Image": "Image",
                "Audio": "Audio",
            },
            "artikel_context_cloze": {
                "Text": "Text",
                "Explanation": "Explanation",
                "Image": "Image",
                "Audio": "Audio",
            },
            # Article pattern cards - gender recognition and case context
            "artikel_gender": {
                "FrontText": "front_text",
                "BackText": "back_text",
                "Gender": "gender",
                "Nominative": "nominative",
                "Accusative": "accusative",
                "Dative": "dative",
                "Genitive": "genitive",
                "ExampleNom": "example_nom",
                "ArticleAudio": "article_audio",
                "NounOnly": "NounOnly",
                "NounEnglish": "NounEnglish",
            },
            "artikel_context": {
                "FrontText": "front_text",
                "BackText": "back_text",
                "Gender": "gender",
                "Case": "case",
                "CaseRule": "case_rule",
                "ArticleForm": "article_form",
                "CaseUsage": "case_usage",
                "Nominative": "nominative",
                "Accusative": "accusative",
                "Dative": "dative",
                "Genitive": "genitive",
                # Conditional case highlighting fields
                "CaseNominative": "case_nominative",
                "CaseAccusative": "case_accusative",
                "CaseDative": "case_dative",
                "CaseGenitive": "case_genitive",
                "NounOnly": "NounOnly",
                "NounEnglish": "NounEnglish",
            },
            "noun_article_recognition": {
                "FrontText": "front_text",
                "BackText": "back_text",
                "English": "english_meaning",
            },
            "noun_case_context": {
                "FrontText": "front_text",
                "BackText": "back_text",
                "Case": "case",
                "CaseRule": "case_rule",
                "ArticleForm": "article_form",
                "CaseUsage": "case_usage",
                "CaseNominativ": "case_nominativ",
                "CaseAkkusativ": "case_akkusativ",
                "CaseDativ": "case_dativ",
                "CaseGenitiv": "case_genitiv",
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

        # Apply field-specific formatting for media file detection
        if (
            field_name
            in [
                "Audio",
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
            and not str_value.startswith("[sound:")
        ):
            # Format audio for MediaFileRegistrar detection
            str_value = f"[sound:{str_value}]"

        elif field_name == "Image" and str_value and not str_value.startswith("<img"):
            # Format image for MediaFileRegistrar detection
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
            # Check for field existence and non-empty values
            # Note: Use 'in' for existence to handle boolean False values correctly
            if field not in record_data or record_data[field] in (None, ""):
                logger.warning(
                    "Missing required field '%s' for %s record", field, record_type
                )
                return False

        return True

    def _get_required_fields_for_record_type(self, record_type: str) -> list[str]:
        """Get required fields for card building for a record type.

        CardBuilder runs AFTER MediaEnricher in the Clean Pipeline Architecture:
        CSV → RecordMapper → Records → MediaEnricher → CardBuilder → AnkiBackend

        Therefore, all fields marked as Required ✅ in PROD-CARD-SPEC.md must be
        present, including media fields generated by MediaEnricher.

        Args:
            record_type: Type of record

        Returns:
            List of required field names (including media fields)
        """
        required_fields = {
            # All fields marked as Required ✅ in PROD-CARD-SPEC.md
            # MediaEnricher runs BEFORE CardBuilder, so media fields must be present
            "noun": [
                "noun",
                "article",
                "english",
                "plural",
                "example",
                "related",
                "image",
                "word_audio",
                "example_audio",
            ],
            "adjective": [
                "word",
                "english",
                "example",
                "comparative",
                "superlative",
                "image",
                "word_audio",
                "example_audio",
            ],
            "adverb": [
                "word",
                "english",
                "type",
                "example",
                "image",
                "word_audio",
                "example_audio",
            ],
            "negation": [
                "word",
                "english",
                "type",
                "example",
                "image",
                "word_audio",
                "example_audio",
            ],
            "verb": [
                "verb",
                "english",
                "classification",
                "present_ich",
                "present_du",
                "present_er",
                "präteritum",
                "auxiliary",
                "perfect",
                "example",
                "separable",
                "image",
                "word_audio",
                "example_audio",
            ],
            "phrase": ["phrase", "english", "context", "image", "phrase_audio"],
            "preposition": [
                "preposition",
                "english",
                "case",
                "example1",
                "example1_audio",
                "image",
                "word_audio",
            ],
            "verb_conjugation": [
                "infinitive",
                "english",
                "tense",
                "ich",
                "du",
                "er",
                "wir",
                "ihr",
                "sie",
                "classification",
                "separable",
                "auxiliary",
                "example",
                "image",
                "word_audio",
                "example_audio",
            ],
            "verb_imperative": [
                "english",
                "infinitive",
                "du",
                "ihr",
                "sie",
                "wir",
                "example_du",
                "example_ihr",
                "example_sie",
                "image",
                "word_audio",
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

    def build_article_pattern_cards(
        self,
        records: list[
            ArticleRecord
            | IndefiniteArticleRecord
            | NegativeArticleRecord
            | UnifiedArticleRecord
        ],
        enriched_data_list: list[dict[str, Any]] | None = None,
    ) -> list[tuple[list[str], NoteType]]:
        """Build multiple case-specific cards from article pattern records.

        This method implements the article card generation system from PM-ARTICLES.md,
        creating 5 cards per article record instead of 1 card per record:
        - 1 Gender Recognition card
        - 4 Case Context cards (Nominative, Accusative, Dative, Genitive)

        Args:
            records: List of article record instances (ArticleRecord,
                     IndefiniteArticleRecord, or NegativeArticleRecord)
            enriched_data_list: Optional enriched data for each record

        Returns:
            List of (field_values, note_type) tuples for multiple cards per record
        """
        logger.info("Building article pattern cards from %d records", len(records))

        # Import here to avoid circular dependency
        from langlearn.services.article_pattern_processor import (
            ArticlePatternProcessor,
        )

        # Create processor and delegate to it
        processor = ArticlePatternProcessor(self)
        return processor.process_article_records(records, enriched_data_list)

    def build_noun_article_cards(
        self,
        noun_records: list[NounRecord],
        enriched_data_list: list[dict[str, Any]] | None = None,
    ) -> list[tuple[list[str], NoteType]]:
        """Generate noun-article practice cards from noun records.

        Creates cards that help students learn which article (der/die/das) goes
        with each noun, addressing the core use case of German article learning.

        Args:
            noun_records: List of NounRecord instances with article information
            enriched_data_list: Optional enriched data for each record

        Returns:
            List of (field_values, note_type) tuples for noun-article practice cards
        """
        logger.info(
            "Building noun-article cards from %d noun records", len(noun_records)
        )

        # Use the pre-initialized article application service
        return self._article_application_service.generate_noun_article_cards(
            noun_records, enriched_data_list
        )
