"""Korean card builder service for record-based architecture."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from langlearn.core.records.base_record import BaseRecord
from langlearn.infrastructure.backends.base import CardTemplate, NoteType
from langlearn.infrastructure.services.template_service import TemplateService
from langlearn.languages.korean.records.noun_record import KoreanNounRecord

logger = logging.getLogger(__name__)


class KoreanCardBuilder:
    """Builds formatted Korean cards from enriched records using templates."""

    def __init__(
        self,
        template_service: TemplateService | None = None,
        project_root: Path | None = None,
    ) -> None:
        """Initialize Korean CardBuilder."""
        self._project_root = project_root or Path.cwd()

        if template_service is None:
            # Use Korean template directory
            korean_template_dir = (
                self._project_root
                / "src"
                / "langlearn"
                / "languages"
                / "korean"
                / "templates"
            )
            template_service = TemplateService(korean_template_dir)

        self._template_service = template_service

    def build_card_from_record(
        self, record: BaseRecord, media_data: dict[str, str]
    ) -> tuple[list[str], NoteType]:
        """Build Korean card from enriched record."""
        if isinstance(record, KoreanNounRecord):
            return self._build_korean_noun_card(record, media_data)
        else:
            raise ValueError(f"Unsupported Korean record type: {type(record)}")

    def _build_korean_noun_card(
        self, record: KoreanNounRecord, media_data: dict[str, str]
    ) -> tuple[list[str], NoteType]:
        """Build Korean noun card with particle patterns and counter information."""
        # Get templates using TemplateService
        try:
            card_template = self._template_service.get_template("korean_noun")
            logger.info("Successfully loaded Korean noun template")

            # Debug template content
            logger.info("Template front HTML length: %d", len(card_template.front_html))
            if "{{" in card_template.front_html:
                logger.info("Front template contains field references - good!")
            else:
                logger.error("Front template does NOT contain field references!")
                logger.error(
                    "Front template content: %s", card_template.front_html[:200]
                )

        except Exception as e:
            logger.error(f"Failed to load template for Korean noun: {e}")
            # Fail fast - don't use fallback templates
            raise RuntimeError(
                f"Failed to load Korean noun templates from template service: {e}. "
                f"Check that template files exist and are properly configured."
            ) from e

        # Create note type
        note_type = self._create_note_type_for_record("korean_noun", card_template)

        # Prepare field values to match the NoteType field order exactly
        # Format counter info for better display
        counter_info = record.primary_counter
        if record.counter_example:
            counter_info += f" (예: {record.counter_example})"

        # Raw field values
        raw_field_values = [
            record.hangul,  # Hangul
            record.romanization,  # Romanization
            record.english,  # English
            record.topic_particle,  # TopicParticle
            record.subject_particle,  # SubjectParticle
            record.object_particle,  # ObjectParticle
            counter_info,  # Counter
            record.example,  # Example
            media_data.get("image", ""),  # Image
            media_data.get("word_audio", ""),  # WordAudio
            media_data.get("example_audio", ""),  # ExampleAudio
        ]

        # Format field values for Anki display
        field_names = [
            "Hangul",
            "Romanization",
            "English",
            "TopicParticle",
            "SubjectParticle",
            "ObjectParticle",
            "Counter",
            "Example",
            "Image",
            "WordAudio",
            "ExampleAudio",
        ]

        field_values = []
        for field_name, raw_value in zip(field_names, raw_field_values, strict=False):
            formatted_value = self._format_field_value(field_name, raw_value)
            field_values.append(formatted_value)

        # Debug logging
        logger.info("Korean card field values: %s", field_values[:4])  # First 4 fields
        logger.info("Korean note type name: %s", note_type.name)
        logger.info(
            "Korean field count: %d fields, %d values",
            len(note_type.fields),
            len(field_values),
        )

        return field_values, note_type

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

        # Convert to string
        str_value = str(value)

        # Apply field-specific formatting for media file detection
        if (
            field_name in ["WordAudio", "ExampleAudio"]
            and str_value
            and not str_value.startswith("[sound:")
        ):
            # Format audio for MediaFileRegistrar detection
            str_value = f"[sound:{str_value}]"
            logger.debug(f"Formatted Korean audio field {field_name}: {str_value}")

        elif field_name == "Image" and str_value and not str_value.startswith("<img"):
            # Format image for MediaFileRegistrar detection
            str_value = f'<img src="{str_value}" />'

        return str_value

    def _create_note_type_for_record(
        self, record_type: str, template: CardTemplate
    ) -> NoteType:
        """Create NoteType for Korean record.

        Field names must match the template field references exactly.
        """
        field_names = [
            "Hangul",  # {{Hangul}} in templates
            "Romanization",  # {{Romanization}} in templates
            "English",  # {{English}} in templates
            "TopicParticle",  # {{TopicParticle}} in templates
            "SubjectParticle",  # {{SubjectParticle}} in templates
            "ObjectParticle",  # {{ObjectParticle}} in templates
            "Counter",  # {{Counter}} in front template - matches template field
            "Example",  # {{Example}} in templates
            "Image",  # {{Image}} in templates
            "WordAudio",  # {{WordAudio}} in templates
            "ExampleAudio",  # {{ExampleAudio}} in templates
        ]

        return NoteType(
            name=f"Korean {record_type.title()}",
            fields=field_names,
            templates=[template],
        )

    def build_cards_from_records(
        self,
        records: list[BaseRecord],
        enriched_data_list: list[dict[str, str]] | None = None,
    ) -> list[tuple[list[str], NoteType]]:
        """Build multiple Korean cards from records and enriched data.

        Args:
            records: List of Korean base records
            enriched_data_list: Optional list of enriched data dicts
                (same order as records)

        Returns:
            List of (field_values, note_type) tuples ready for backend

        Raises:
            RuntimeError: If any card building fails
        """
        logger.debug("Building Korean cards from %d records", len(records))
        cards = []

        for i, record in enumerate(records):
            enriched_data = (
                enriched_data_list[i]
                if enriched_data_list and i < len(enriched_data_list)
                else {}
            )
            try:
                card = self.build_card_from_record(record, enriched_data)
                cards.append(card)
            except Exception as e:
                logger.error("Failed to build Korean card from record %d: %s", i, e)
                # Fail fast - don't continue with broken cards
                raise RuntimeError(
                    f"Failed to build Korean card from record {i}: {e}"
                ) from e

        logger.info("Successfully built %d Korean cards", len(cards))
        return cards
