"""Russian Card builder service for record-based architecture."""

from __future__ import annotations

import logging
from pathlib import Path

from langlearn.core.records.base_record import BaseRecord
from langlearn.infrastructure.backends.base import CardTemplate, NoteType
from langlearn.infrastructure.services.template_service import TemplateService

logger = logging.getLogger(__name__)


class RussianCardBuilder:
    """Builds formatted Russian cards from enriched records using templates."""

    def __init__(
        self,
        template_service: TemplateService | None = None,
        project_root: Path | None = None,
    ) -> None:
        """Initialize Russian CardBuilder."""
        self._project_root = project_root or Path.cwd()

        if template_service is None:
            # Use Russian template directory
            russian_template_dir = (
                self._project_root
                / "src"
                / "langlearn"
                / "languages"
                / "russian"
                / "templates"
            )
            template_service = TemplateService(russian_template_dir)

        self._template_service = template_service
        logger.debug("Russian CardBuilder initialized with template service")

    def build_cards_from_records(
        self, records: list[BaseRecord], enriched_records: list[dict[str, str]]
    ) -> list[tuple[list[str], NoteType]]:
        """Build cards from Russian records and enriched data.

        Args:
            records: List of Russian record objects
            enriched_records: List of enriched data dictionaries

        Returns:
            List of tuples containing (field_values, note_type) for Anki backend
        """
        logger.info(f"Building cards for {len(records)} Russian records")

        all_cards = []
        for record, enriched_data in zip(records, enriched_records, strict=False):
            field_values, note_type = self.build_card_from_record(record, enriched_data)
            all_cards.append((field_values, note_type))

        logger.info(f"Built {len(all_cards)} cards total")
        return all_cards

    def build_card_from_record(
        self, record: BaseRecord, enriched_data: dict[str, str]
    ) -> tuple[list[str], NoteType]:
        """Build Russian card from enriched record data.

        Returns:
            Tuple of (field_values, note_type)
        """

        if record.get_record_type().value == "noun":
            return self._build_noun_card(record, enriched_data)
        else:
            raise ValueError(
                f"Unsupported Russian record type: {record.get_record_type()}"
            )

    def _build_noun_card(
        self, record: BaseRecord, enriched_data: dict[str, str]
    ) -> tuple[list[str], NoteType]:
        """Build Russian noun card."""

        # Create note type for Russian noun
        note_type = self.create_note_type("noun")

        # Merge record data with enriched data (following German CardBuilder pattern)
        card_data = record.to_dict()
        if enriched_data:
            card_data.update(enriched_data)

        logger.debug(
            f"Building Russian noun card with data keys: {list(card_data.keys())}"
        )

        # Field names in order as defined in note type

        # Create field values in same order, with proper media formatting
        field_values = [
            card_data.get("noun", ""),
            card_data.get("english", ""),
            card_data.get("gender", ""),
            card_data.get("genitive", ""),
            card_data.get("example", ""),
            card_data.get("related", ""),
            self._format_field_value("Image", card_data.get("image", "")),
            self._format_field_value("WordAudio", card_data.get("word_audio", "")),
            self._format_field_value(
                "ExampleAudio", card_data.get("example_audio", "")
            ),
        ]

        return field_values, note_type

    def _format_field_value(self, field_name: str, value: str | None) -> str:
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
            field_name
            in [
                "WordAudio",
                "ExampleAudio",
            ]
            and str_value
            and not str_value.startswith("[sound:")
        ):
            # Format audio for Anki
            str_value = f"[sound:{str_value}]"

        elif field_name == "Image" and str_value and not str_value.startswith("<img"):
            # Format image for Anki
            str_value = f'<img src="{str_value}" />'

        return str_value

    def create_note_type(
        self,
        record_type: str,
        project_root: Path | None = None,
    ) -> NoteType:
        """Create Russian note type with templates."""

        if record_type != "noun":
            raise ValueError(f"Unsupported Russian record type: {record_type}")

        # Load Russian templates
        russian_template_dir = Path(__file__).parent.parent / "templates"

        front_template = (russian_template_dir / "noun_RU_ru_front.html").read_text(
            encoding="utf-8"
        )
        back_template = (russian_template_dir / "noun_RU_ru_back.html").read_text(
            encoding="utf-8"
        )
        css_content = (russian_template_dir / "noun_RU_ru.css").read_text(
            encoding="utf-8"
        )

        return NoteType(
            name="Russian Noun",
            fields=[
                "Noun",
                "English",
                "Gender",
                "Genitive",
                "Example",
                "Related",
                "Image",
                "WordAudio",
                "ExampleAudio",
            ],
            templates=[
                CardTemplate(
                    name="Recognition",
                    front_html=front_template,
                    back_html=back_template,
                    css=css_content,
                )
            ],
        )
