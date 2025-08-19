"""
Tests for backend integration with ModelFactory delegation.

This module tests the implementation where AnkiBackend uses ModelFactory
to delegate field processing to domain models.
"""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from langlearn.backends.anki_backend import AnkiBackend


class TestBackendIntegration:
    """Test backend integration with domain model delegation."""

    @pytest.fixture
    def temp_hide_images(self):
        """Temporarily move existing image files so tests can check generation paths."""
        # List of image files that conflict with tests
        image_files = ["schön.jpg"]
        moved_files = []

        # Create temporary directory
        temp_dir = Path(tempfile.mkdtemp())

        try:
            # Move existing image files temporarily
            for filename in image_files:
                source = Path(f"data/images/{filename}")
                if source.exists():
                    dest = temp_dir / filename
                    shutil.move(str(source), str(dest))
                    moved_files.append((str(source), str(dest)))

            yield

        finally:
            # Restore moved files
            for source, temp_path in moved_files:
                if Path(temp_path).exists():
                    shutil.move(temp_path, source)

            # Clean up temp directory
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_anki_backend_uses_domain_delegation(self) -> None:
        """Test that AnkiBackend delegates to domain models when available."""
        backend = AnkiBackend("Test Deck", "Test Description")

        # Mock the DomainMediaGenerator to verify delegation
        mock_generator = Mock()
        backend._domain_media_generator = mock_generator

        # Mock the field processor creation and processing
        factory_path = "langlearn.models.model_factory.ModelFactory"
        with patch(f"{factory_path}.create_field_processor") as mock_factory:
            mock_processor = Mock()
            mock_processor.process_fields_for_media_generation.return_value = [
                "processed_field_1",
                "processed_field_2",
            ]
            mock_factory.return_value = mock_processor

            fields = ["original_field_1", "original_field_2"]
            result = backend._process_fields_with_media("German Adjective", fields)

            # Verify delegation occurred
            mock_factory.assert_called_once_with("German Adjective")
            mock_processor.process_fields_for_media_generation.assert_called_once_with(
                fields, mock_generator
            )
            assert result == ["processed_field_1", "processed_field_2"]

    def test_anki_backend_handles_unsupported_types(self) -> None:
        """Test AnkiBackend returns unchanged fields for unsupported note types."""
        backend = AnkiBackend("Test Deck", "Test Description")

        factory_path = "langlearn.models.model_factory.ModelFactory"
        with patch(f"{factory_path}.create_field_processor") as mock_factory:
            # Return None to simulate unsupported note type
            mock_factory.return_value = None

            fields = ["field1", "field2"]
            result = backend._process_fields_with_media("Unsupported Type", fields)

            # Verify original fields returned unchanged (no legacy processing)
            mock_factory.assert_called_once_with("Unsupported Type")
            assert result == fields

    def test_adjective_processing(self, temp_hide_images) -> None:
        """Test that AnkiBackend processes adjectives correctly."""
        # Set up adjective fields
        fields = [
            "schön",  # 0: Word
            "beautiful",  # 1: English
            "Das ist schön.",  # 2: Example
            "schöner",  # 3: Comparative
            "am schönsten",  # 4: Superlative
            "",  # 5: Image (empty)
            "",  # 6: WordAudio (empty)
            "",  # 7: ExampleAudio (empty)
        ]

        # Create backend
        anki_backend = AnkiBackend("Test Deck")

        # Mock the new MediaEnricher for Clean Pipeline Architecture
        class MockMediaEnricher:
            def enrich_record(self, record_dict, domain_model):
                # Return predictable mock responses
                enriched = record_dict.copy()
                enriched["image"] = '<img src="image.jpg">'
                enriched["word_audio"] = "[sound:audio.mp3]"
                enriched["example_audio"] = "[sound:audio.mp3]"
                return enriched

        # Replace MediaEnricher with mock
        anki_backend._media_enricher = MockMediaEnricher()  # type: ignore[assignment]

        # Process fields
        result = anki_backend._process_fields_with_media(
            "German Adjective", fields.copy()
        )

        # Verify expected structure
        assert len(result) == 8
        assert result[0] == "schön"  # Word unchanged
        assert result[1] == "beautiful"  # English unchanged
        assert result[2] == "Das ist schön."  # Example unchanged
        assert result[5] == '<img src="image.jpg">'  # Image generated
        assert result[6] == "[sound:audio.mp3]"  # WordAudio generated
        assert result[7] == "[sound:audio.mp3]"  # ExampleAudio generated

    def test_error_handling(self) -> None:
        """Test that AnkiBackend handles processing errors gracefully."""
        fields = ["schön", "beautiful", "Das ist schön."]

        anki_backend = AnkiBackend("Test Deck")

        # Mock field processor to raise an exception
        factory_path = "langlearn.models.model_factory.ModelFactory"
        with patch(f"{factory_path}.create_field_processor") as mock_factory:
            mock_processor = Mock()
            error_msg = "Test error"
            mock_processor.process_fields_for_media_generation.side_effect = Exception(
                error_msg
            )
            mock_factory.return_value = mock_processor

            # Backend should handle errors gracefully and return original fields
            anki_result = anki_backend._process_fields_with_media(
                "German Adjective", fields
            )

            # Should return original fields on error
            assert anki_result == fields

    def test_unsupported_note_type_handling(self) -> None:
        """Test handling of note types not supported by ModelFactory."""
        fields = ["word", "meaning", "example"]

        anki_backend = AnkiBackend("Test Deck")

        # Backend should handle unsupported types gracefully
        anki_result = anki_backend._process_fields_with_media("Unknown Type", fields)

        # AnkiBackend returns fields unchanged for unknown types
        assert anki_result == fields


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
