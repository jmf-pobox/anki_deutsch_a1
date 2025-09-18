"""Russian language implementation for multi-language architecture."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from langlearn.core.records import BaseRecord
    from langlearn.protocols.domain_model_protocol import LanguageDomainModel
    from langlearn.protocols.media_enricher_protocol import MediaEnricherProtocol


class RussianLanguage:
    """Russian language implementation supporting Cyrillic script and case system."""

    @property
    def code(self) -> str:
        """ISO language code."""
        return "ru"

    @property
    def name(self) -> str:
        """Human-readable language name."""
        return "Russian"

    def get_supported_record_types(self) -> list[str]:
        """Get record types this language supports."""
        return [
            "noun",
            # Future: "verb", "adjective", "adverb", etc.
        ]

    def get_card_builder(self) -> Any:
        """Get the card builder for this language."""
        from .services.card_builder import RussianCardBuilder

        return RussianCardBuilder

    def get_grammar_service(self) -> Any:
        """Get language-specific grammar service."""
        from .services import grammar_service

        return grammar_service

    def get_record_mapper(self) -> Any:
        """Get language-specific record mapper."""
        from .services.record_mapper import RussianRecordMapper

        return RussianRecordMapper

    def get_template_path(self, record_type: str, side: str) -> str:
        """Get template path for record type and side (front/back)."""
        current_dir = Path(__file__).parent
        templates_dir = current_dir / "templates"

        # Russian template naming convention
        template_name = f"{record_type}_RU_ru_{side}.html"
        template_path = templates_dir / template_name

        return str(template_path)

    def get_template_filename(self, card_type: str, side: str) -> str:
        """Get template filename for card type and side."""
        if side == "css":
            return f"{card_type}_RU_ru.css"
        else:
            return f"{card_type}_RU_ru_{side}.html"

    def get_template_directory(self) -> Path:
        """Get the templates directory for Russian language."""
        current_dir = Path(__file__).parent
        return current_dir / "templates"

    def create_domain_model(
        self, record_type: str, record: BaseRecord
    ) -> LanguageDomainModel:
        """Create Russian domain model from record using proper type narrowing."""
        if record_type == "noun":
            from .models.noun import RussianNoun
            from .records.noun_record import RussianNounRecord

            if isinstance(record, RussianNounRecord):
                return RussianNoun(
                    noun=record.noun,
                    english=record.english,
                    example=record.example,
                    related=record.related,
                    gender=record.gender,
                    animacy=record.animacy,
                    nominative=record.nominative,
                    genitive=record.genitive,
                    accusative=record.accusative,
                    instrumental=record.instrumental,
                    prepositional=record.prepositional,
                    dative=record.dative,
                    plural_nominative=record.plural_nominative,
                    plural_genitive=record.plural_genitive,
                )

        supported_types = self.get_supported_record_types()
        raise ValueError(
            f"Unsupported record type '{record_type}' for Russian language "
            f"or incorrect record instance type. Supported types: {supported_types}"
        )

    def create_record_from_csv(self, record_type: str, fields: list[str]) -> BaseRecord:
        """Create Russian record from CSV fields."""
        if record_type == "noun":
            from .records.noun_record import RussianNounRecord

            # Russian noun CSV format:
            # [noun, english, gender, genitive, example, related, animacy, ...]
            if len(fields) < 3:
                raise ValueError(
                    f"Russian noun requires at least 3 fields: noun, english, gender. "
                    f"Got {len(fields)} fields: {fields}"
                )

            # Use the from_csv_fields class method for proper type handling
            return RussianNounRecord.from_csv_fields(fields)

        supported_types = self.get_supported_record_types()
        raise ValueError(
            f"Unsupported record type '{record_type}' for Russian language. "
            f"Supported types: {supported_types}"
        )

    def get_media_enricher(self) -> MediaEnricherProtocol:
        """Get Russian-specific media enricher configured with services."""
        raise NotImplementedError(
            "get_media_enricher() should be called from AnkiBackend with proper "
            "service injection"
        )

    def create_media_enricher(
        self,
        audio_service: Any,
        pexels_service: Any,
        anthropic_service: Any,
        audio_base_path: Any,
        image_base_path: Any,
    ) -> MediaEnricherProtocol:
        """Create Russian-specific media enricher with injected services."""
        # Use the core StandardMediaEnricher (language-agnostic)
        # In the future, this could be RussianMediaEnricher with Cyrillic-specific logic
        from langlearn.core.services.media_enricher import (
            StandardMediaEnricher,
        )

        return StandardMediaEnricher(
            audio_service=audio_service,
            pexels_service=pexels_service,
            anthropic_service=anthropic_service,
            audio_base_path=audio_base_path,
            image_base_path=image_base_path,
        )

    def get_note_type_mappings(self) -> dict[str, str]:
        """Get Russian-specific Anki note type name mappings."""
        return {
            "Russian Noun": "noun",
            "Russian Noun with Media": "noun",
            # Future mappings:
            # "Russian Verb": "verb",
            # "Russian Adjective": "adjective",
        }

    def process_fields_for_anki(
        self,
        note_type_name: str,
        fields: list[str],
        media_enricher: Any,
    ) -> list[str]:
        """Process fields for Anki note creation with Russian-specific logic."""
        import logging

        from langlearn.exceptions import DataProcessingError

        logger = logging.getLogger(__name__)

        try:
            # Get note type to record type mappings
            note_type_to_record_type = self.get_note_type_mappings()

            # Check if we support this note type
            record_type = None
            for note_pattern, rec_type in note_type_to_record_type.items():
                if note_pattern.lower() in note_type_name.lower():
                    record_type = rec_type
                    break

            if record_type is not None:
                # Use record-based architecture for standard record types
                return self._process_standard_record_fields(
                    record_type, fields, media_enricher
                )

            # No processing available - unsupported note type
            logger.warning(
                f"No processing available for Russian note type: {note_type_name}. "
                f"Returning fields unchanged."
            )
            return fields

        except DataProcessingError:
            # Re-raise DataProcessingError without modification
            raise
        except Exception as e:
            logger.error(f"Error processing media for Russian {note_type_name}: {e}")
            raise DataProcessingError(
                f"Media processing failed for Russian note type {note_type_name}: {e}"
            ) from e

    def _process_standard_record_fields(
        self, record_type: str, fields: list[str], media_enricher: Any
    ) -> list[str]:
        """Process standard record type fields with Russian-specific formatting."""
        import logging

        from langlearn.exceptions import DataProcessingError

        logger = logging.getLogger(__name__)

        logger.debug(f"Using record-based architecture for Russian: {record_type}")
        try:
            # Create record from fields using Russian record factory
            record = self.create_record_from_csv(record_type, fields)

            # Import locally to avoid circular imports
            from .records.noun_record import RussianNounRecord

            # Type narrowing for MyPy
            if not isinstance(record, RussianNounRecord):
                raise ValueError(f"Expected RussianNounRecord, got {type(record)}")

            # Create domain model using Russian factory
            domain_model = self.create_domain_model(record_type, record)

            # Type narrowing for MyPy
            if not hasattr(domain_model, "get_audio_segments"):
                raise ValueError(
                    f"Domain model does not implement MediaGenerationCapable: "
                    f"{type(domain_model)}"
                )

            # Enrich record using MediaEnricher with domain model
            media_data = media_enricher.enrich_with_media(domain_model)
            enriched_record_dict = record.to_dict()
            enriched_record_dict.update(media_data)

            # Convert back to field list format for Anki
            if record_type == "noun":
                return self._format_russian_noun_fields(enriched_record_dict)
            else:
                # For other record types, return available fields
                return self._format_generic_fields(enriched_record_dict)

        except Exception as record_error:
            logger.error(
                f"record-based architecture failed for Russian {record_type}: "
                f"{record_error}"
            )
            raise DataProcessingError(
                f"record-based architecture failed for Russian {record_type}: "
                f"{record_error}"
            ) from record_error

    def _format_russian_noun_fields(
        self, enriched_record_dict: dict[str, Any]
    ) -> list[str]:
        """Format Russian noun fields for Anki cards."""
        # Russian Noun field order:
        # [noun, english, gender, genitive, example, related, image,
        #  word_audio, example_audio]
        return [
            enriched_record_dict["noun"],
            enriched_record_dict["english"],
            enriched_record_dict["gender"],
            enriched_record_dict.get("genitive", ""),
            enriched_record_dict.get("example", ""),
            enriched_record_dict.get("related", ""),
            enriched_record_dict.get("image", ""),
            enriched_record_dict.get("word_audio", ""),
            enriched_record_dict.get("example_audio", ""),
        ]

    def _format_generic_fields(self, enriched_record_dict: dict[str, Any]) -> list[str]:
        """Format generic fields for unsupported record types."""
        # Extract common fields that most record types should have
        formatted_fields = []

        # Core word field
        for field_name in ["noun", "word", "verb", "adjective"]:
            if field_name in enriched_record_dict:
                formatted_fields.append(enriched_record_dict[field_name])
                break

        # English translation
        if "english" in enriched_record_dict:
            formatted_fields.append(enriched_record_dict["english"])

        # Example
        if "example" in enriched_record_dict:
            formatted_fields.append(enriched_record_dict["example"])

        # Media fields
        formatted_fields.extend(
            [
                enriched_record_dict.get("image", ""),
                enriched_record_dict.get("word_audio", ""),
                enriched_record_dict.get("example_audio", ""),
            ]
        )

        return formatted_fields
