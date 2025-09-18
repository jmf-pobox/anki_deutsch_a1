"""Test Russian card field assignment end-to-end."""

from __future__ import annotations

from pathlib import Path

import pytest

from langlearn.core.backends.base import NoteType
from langlearn.core.deck import DeckBuilderAPI as DeckBuilder


class TestRussianFieldAssignment:
    """Test Russian card field assignment process."""

    def test_russian_note_field_assignment(self, tmp_path: Path) -> None:
        """Test end-to-end Russian field assignment from records to Anki backend."""
        # Skip if Russian language is not registered
        from langlearn.languages import LanguageRegistry

        try:
            LanguageRegistry.get("russian")
        except ValueError:
            pytest.skip("Russian language not registered")

        # Create DeckBuilder with Russian language
        deck_builder = DeckBuilder(
            deck_name="Test Russian Field Assignment",
            language="russian",
            deck_type="default",
        )

        # Load Russian data
        project_root = Path(__file__).parent.parent
        russian_data_dir = project_root / "languages" / "russian" / "default"

        # Skip if Russian data doesn't exist (for CI environments)
        if not russian_data_dir.exists():
            pytest.skip("Russian test data not available")

        deck_builder.load_data_from_directory(str(russian_data_dir))

        # Get first Russian record
        russian_records = [
            r
            for r in deck_builder._loaded_records
            if r.__class__.__name__.startswith("Russian")
        ]

        if not russian_records:
            pytest.skip("No Russian records loaded")

        record = russian_records[0]

        # Verify record data
        record_data = record.to_dict()
        assert "noun" in record_data
        assert "english" in record_data
        assert "gender" in record_data

        # Test card building process
        from langlearn.languages.russian.services.card_builder import RussianCardBuilder

        card_builder = RussianCardBuilder()
        field_values, note_type = card_builder.build_card_from_record(record, {})

        # Verify note type structure
        assert isinstance(note_type, NoteType)
        assert note_type.name == "Russian Noun"
        assert len(note_type.fields) == 9

        expected_fields = [
            "Noun",
            "English",
            "Gender",
            "Genitive",
            "Example",
            "Related",
            "Image",
            "WordAudio",
            "ExampleAudio",
        ]
        assert note_type.fields == expected_fields

        # Verify field values
        assert len(field_values) == len(note_type.fields)
        assert field_values[0] == record_data["noun"]  # Noun field
        assert field_values[1] == record_data["english"]  # English field
        assert field_values[2] == record_data["gender"]  # Gender field

        # Test AnkiBackend integration
        note_type_id = deck_builder._backend.create_note_type(note_type)
        assert note_type_id is not None

        note_id = deck_builder._backend.add_note(
            note_type_id, field_values, skip_media_processing=True
        )
        assert note_id is not None

    def test_russian_audio_service_configuration(self) -> None:
        """Test that Russian audio service uses correct voice and language."""
        # Skip if Russian language is not registered
        from langlearn.languages import LanguageRegistry

        try:
            LanguageRegistry.get("russian")
        except ValueError:
            pytest.skip("Russian language not registered")

        deck_builder = DeckBuilder(
            deck_name="Test Russian Audio Config",
            language="russian",
            deck_type="default",
        )

        # Verify Russian-specific audio configuration
        from typing import cast

        from langlearn.core.services.media_enricher import StandardMediaEnricher

        media_enricher = cast("StandardMediaEnricher", deck_builder._media_enricher)
        audio_service = media_enricher._audio_service
        assert audio_service.voice_id == "Tatyana"
        assert audio_service.language_code == "ru-RU"
        assert audio_service.engine == "standard"
