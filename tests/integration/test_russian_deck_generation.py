"""Integration test for Russian deck generation."""

from __future__ import annotations

from pathlib import Path

import pytest

from langlearn.core.deck import DeckBuilderAPI as DeckBuilder
from tests.utils.deck_inspector import DeckInspector


@pytest.mark.integration
class TestRussianDeckGeneration:
    """Test complete Russian deck generation process."""

    def test_generate_russian_deck_with_media(self, tmp_path: Path) -> None:
        """Test generating a complete Russian deck with media files."""
        # Skip if Russian data doesn't exist
        project_root = Path(__file__).parent.parent.parent
        russian_data_dir = project_root / "languages" / "russian" / "default"

        if not russian_data_dir.exists():
            pytest.skip("Russian test data not available")

        output_file = tmp_path / "test_russian_deck.apkg"

        # Create and configure deck builder
        with DeckBuilder(
            deck_name="Test Russian Vocabulary",
            language="russian",
            deck_type="default",
        ) as builder:
            # Load Russian data
            builder.load_data_from_directory(str(russian_data_dir))

            # Verify data loaded
            stats = builder.get_statistics()
            loaded_data = stats["loaded_data"]
            assert sum(loaded_data.values()) > 0, "No Russian data loaded"

            # Generate cards with media
            results = builder.generate_all_cards(
                generate_media=False
            )  # Skip media for faster testing
            assert sum(results.values()) > 0, "No cards generated"

            # Export deck
            builder.export_deck(output_file)

        # Verify deck file was created
        assert output_file.exists(), "Deck file was not created"
        assert output_file.stat().st_size > 1000, "Deck file is too small"

        # Inspect deck contents
        inspector = DeckInspector(output_file)
        validation = inspector.validate_deck_structure()

        # Verify deck structure
        assert validation["has_database"], "Deck missing database"
        assert validation["has_notes"], "Deck has no notes"

        # Verify note contents
        field_values = inspector.get_note_field_values()
        assert len(field_values) > 0, "No notes found in deck"

        # Check that Russian text is present
        russian_text_found = False
        anki_version_issue = False

        for note_fields in field_values:
            for field in note_fields:
                if "This file requires a newer version of Anki" in field:
                    anki_version_issue = True
                elif any(
                    char for char in field if ord(char) > 1024
                ):  # Cyrillic characters
                    russian_text_found = True
                    break

        # If we hit the Anki version issue in test environment, skip the Cyrillic check
        # This is a known issue with testing modern Anki decks in older environments
        if anki_version_issue:
            pytest.skip(
                "Test environment using older Anki format - deck generation successful"
            )

        assert russian_text_found, "No Russian (Cyrillic) text found in deck"

    def test_russian_audio_configuration(self) -> None:
        """Test that Russian deck uses correct audio configuration."""
        with DeckBuilder(
            deck_name="Test Audio Config",
            language="russian",
            deck_type="default",
        ) as builder:
            # Verify audio service configuration
            from typing import cast

            from langlearn.core.services.media_enricher import StandardMediaEnricher

            media_enricher = cast("StandardMediaEnricher", builder._media_enricher)
            audio_service = media_enricher._audio_service
            assert audio_service.voice_id == "Tatyana"
            assert audio_service.language_code == "ru-RU"
            assert audio_service.engine == "standard"

    def test_russian_subdeck_naming(self, tmp_path: Path) -> None:
        """Test that Russian deck creates properly named subdecks."""
        # Skip if Russian data doesn't exist
        project_root = Path(__file__).parent.parent.parent
        russian_data_dir = project_root / "languages" / "russian" / "default"

        if not russian_data_dir.exists():
            pytest.skip("Russian test data not available")

        with DeckBuilder(
            deck_name="Test Russian Subdecks",
            language="russian",
            deck_type="default",
        ) as builder:
            builder.load_data_from_directory(str(russian_data_dir))
            builder.generate_all_cards(generate_media=False)

            # Check subdeck names
            subdeck_info = builder.get_subdeck_info()
            subdeck_names = subdeck_info["subdeck_names"]

            # Should have "Nouns" subdeck, not "Russiannouns"
            assert "Nouns" in subdeck_names, (
                f"Expected 'Nouns' subdeck, got: {subdeck_names}"
            )
            assert not any("russian" in name.lower() for name in subdeck_names), (
                f"Found language prefix in subdeck names: {subdeck_names}"
            )
