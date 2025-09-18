"""Korean language implementation for multi-language architecture."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from langlearn.core.protocols.tts_protocol import TTSConfig

if TYPE_CHECKING:
    from langlearn.core.protocols.card_processor_protocol import LanguageCardProcessor
    from langlearn.core.records import BaseRecord
    from langlearn.protocols.domain_model_protocol import LanguageDomainModel
    from langlearn.protocols.media_enricher_protocol import MediaEnricherProtocol


class KoreanLanguage:
    """Korean language implementation with Hangul support and particle patterns."""

    @property
    def code(self) -> str:
        """ISO language code."""
        return "ko"

    @property
    def name(self) -> str:
        """Human-readable language name."""
        return "Korean"

    def get_supported_record_types(self) -> list[str]:
        """Get record types this language supports."""
        return [
            "korean_noun",
            # Future: "korean_verb", "korean_adjective", etc.
        ]

    def get_card_builder(self) -> Any:
        """Get the card builder for this language."""
        from .services.card_builder import KoreanCardBuilder

        return KoreanCardBuilder

    def get_grammar_service(self) -> Any:
        """Get language-specific grammar service."""
        from .services import grammar_service

        return grammar_service

    def get_record_mapper(self) -> Any:
        """Get language-specific record mapper."""
        from .services.record_mapper import KoreanRecordMapper

        return KoreanRecordMapper

    def get_template_path(self, record_type: str, side: str) -> str:
        """Get template path for record type and side (front/back)."""
        current_dir = Path(__file__).parent
        templates_dir = current_dir / "templates"

        # Korean template naming convention
        template_name = f"{record_type}_KO_ko_{side}.html"
        template_path = templates_dir / template_name

        return str(template_path)

    def get_template_filename(self, card_type: str, side: str) -> str:
        """Get template filename for card type and side."""
        if side == "css":
            return f"{card_type}_KO_ko.css"
        else:
            return f"{card_type}_KO_ko_{side}.html"

    def get_template_directory(self) -> Path:
        """Get the templates directory for Korean language."""
        current_dir = Path(__file__).parent
        return current_dir / "templates"

    def get_tts_config(self) -> TTSConfig:
        """Get TTS configuration for Korean language."""
        return TTSConfig(
            voice_id="Seoyeon",
            language_code="ko-KR",
            engine="standard",
        )

    def get_card_processor(self) -> LanguageCardProcessor:
        """Get card processor for Korean language."""
        from .services.card_processor import KoreanCardProcessor

        return KoreanCardProcessor()

    def create_domain_model(
        self, record_type: str, record: BaseRecord
    ) -> LanguageDomainModel:
        """Create Korean domain model from record using proper type narrowing."""
        if record_type == "korean_noun":
            from .models.noun import KoreanNoun
            from .records.noun_record import KoreanNounRecord

            if isinstance(record, KoreanNounRecord):
                return KoreanNoun(
                    hangul=record.hangul,
                    romanization=record.romanization,
                    english=record.english,
                    topic_particle=record.topic_particle,
                    subject_particle=record.subject_particle,
                    object_particle=record.object_particle,
                    possessive_form=record.possessive_form,
                    primary_counter=record.primary_counter,
                    counter_example=record.counter_example,
                    honorific_form=record.honorific_form,
                    semantic_category=record.semantic_category,
                    example=record.example,
                    example_english=record.example_english,
                    usage_notes=record.usage_notes,
                )

        supported_types = self.get_supported_record_types()
        raise ValueError(
            f"Unsupported record type '{record_type}' for Korean language "
            f"or incorrect record instance type. Supported types: {supported_types}"
        )

    def create_record_from_csv(self, record_type: str, fields: list[str]) -> BaseRecord:
        """Create Korean record from CSV fields."""
        if record_type == "korean_noun":
            from .records.noun_record import KoreanNounRecord

            # Korean noun CSV format:
            # [hangul, romanization, english, primary_counter, semantic_category,
            #  example, example_english, honorific_form, usage_notes]
            if len(fields) < 5:
                raise ValueError(
                    f"Korean noun requires at least 5 fields: hangul, romanization, "
                    f"primary_counter, semantic_category. "
                    f"Got {len(fields)} fields: {fields}"
                )

            return KoreanNounRecord.from_csv_fields(fields)

        supported_types = self.get_supported_record_types()
        raise ValueError(
            f"Unsupported record type '{record_type}' for Korean language. "
            f"Supported types: {supported_types}"
        )

    def get_media_enricher(self) -> MediaEnricherProtocol:
        """Get Korean-specific media enricher configured with services."""
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
        """Create Korean-specific media enricher with injected services."""
        # Use the core StandardMediaEnricher (language-agnostic)
        # In the future, this could be KoreanMediaEnricher with Hangul-specific logic
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
        """Get Korean-specific Anki note type name mappings."""
        return {
            "Korean Noun": "korean_noun",
            "Korean Noun with Media": "korean_noun",
            # Future mappings:
            # "Korean Verb": "korean_verb",
            # "Korean Adjective": "korean_adjective",
        }

    def process_fields_for_anki(
        self,
        note_type_name: str,
        fields: list[str],
        media_enricher: Any,
    ) -> list[str]:
        """Process fields for Anki note creation with Korean-specific logic."""
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
                f"No processing available for Korean note type: {note_type_name}. "
                f"Returning fields unchanged."
            )
            return fields

        except DataProcessingError:
            # Re-raise DataProcessingError without modification
            raise
        except Exception as e:
            logger.error(f"Error processing media for Korean {note_type_name}: {e}")
            raise DataProcessingError(
                f"Media processing failed for Korean note type {note_type_name}: {e}"
            ) from e

    def _process_standard_record_fields(
        self, record_type: str, fields: list[str], media_enricher: Any
    ) -> list[str]:
        """Process standard record type fields with Korean-specific formatting."""
        import logging

        from langlearn.exceptions import DataProcessingError

        logger = logging.getLogger(__name__)

        logger.debug(f"Using record-based architecture for Korean: {record_type}")
        try:
            # Create record from fields using Korean record factory
            record = self.create_record_from_csv(record_type, fields)

            # Import locally to avoid circular imports
            from .records.noun_record import KoreanNounRecord

            # Type narrowing for MyPy
            if not isinstance(record, KoreanNounRecord):
                raise ValueError(f"Expected KoreanNounRecord, got {type(record)}")

            # Create domain model using Korean factory
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
            if record_type == "korean_noun":
                return self._format_korean_noun_fields(enriched_record_dict)
            else:
                # For other record types, return available fields
                return self._format_generic_fields(enriched_record_dict)

        except Exception as record_error:
            logger.error(
                f"record-based architecture failed for Korean {record_type}: "
                f"{record_error}"
            )
            raise DataProcessingError(
                f"record-based architecture failed for Korean {record_type}: "
                f"{record_error}"
            ) from record_error

    def _format_korean_noun_fields(
        self, enriched_record_dict: dict[str, Any]
    ) -> list[str]:
        """Format Korean noun fields for Anki cards."""
        # Korean Noun field order:
        # [hangul, romanization, english, topic_particle, subject_particle,
        #  object_particle, counter_info, example, image, word_audio, example_audio]
        counter = enriched_record_dict.get("primary_counter", "")
        counter_ex = enriched_record_dict.get("counter_example", "")
        counter_info = f"{counter} ({counter_ex})"

        return [
            enriched_record_dict["hangul"],
            enriched_record_dict["romanization"],
            enriched_record_dict["english"],
            enriched_record_dict["topic_particle"],
            enriched_record_dict["subject_particle"],
            enriched_record_dict["object_particle"],
            counter_info,
            enriched_record_dict.get("example", ""),
            enriched_record_dict.get("image", ""),
            enriched_record_dict.get("word_audio", ""),
            enriched_record_dict.get("example_audio", ""),
        ]

    def _format_generic_fields(self, enriched_record_dict: dict[str, Any]) -> list[str]:
        """Format generic fields for unsupported record types."""
        # Extract common fields that most record types should have
        formatted_fields = []

        # Core word field
        for field_name in ["hangul", "word", "noun", "verb", "adjective"]:
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
