"""
Tests for backend integration with ModelFactory delegation.

This module tests the Phase 3 implementation where both AnkiBackend and
GenanKiBackend use ModelFactory to delegate field processing to domain models.
"""

from unittest.mock import Mock, patch

import pytest

from langlearn.backends.anki_backend import AnkiBackend
from langlearn.backends.genanki_backend import GenankiBackend
from langlearn.services.domain_media_generator import MockDomainMediaGenerator


class TestBackendIntegration:
    """Test backend integration with domain model delegation."""

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

    def test_genanki_backend_delegation_when_enabled(self) -> None:
        """Test GenanKiBackend uses delegation when field processing is enabled."""
        backend = GenankiBackend(
            "Test Deck", "Test Description", enable_field_processing=True
        )

        # Mock the DomainMediaGenerator
        mock_generator = Mock()
        backend._domain_media_generator = mock_generator

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

    def test_genanki_backend_no_processing_when_disabled(self) -> None:
        """Test GenanKiBackend skips processing when field processing is disabled."""
        backend = GenankiBackend("Test Deck", "Test Description")  # Default: disabled

        # Should not have domain media generator
        assert backend._domain_media_generator is None
        assert backend._enable_field_processing is False

        # Processing should return fields unchanged
        fields = ["field1", "field2"]
        result = backend._process_fields_with_media("German Adjective", fields)
        assert result == fields

    def test_adjective_processing_consistency(self) -> None:
        """Test that both backends process adjectives identically."""
        # Set up identical adjective fields
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

        # Create backends
        anki_backend = AnkiBackend("Test Deck")
        genanki_backend = GenankiBackend(
            "Test Deck",
            enable_field_processing=True,
            media_service=anki_backend._media_service,  # Use same media service
            german_service=anki_backend._german_service,  # Use same German service
        )

        # Mock media generation consistently
        mock_media_generator = MockDomainMediaGenerator()
        mock_media_generator.set_responses(
            audio="/fake/audio.mp3", image="/fake/image.jpg", context="beautiful scene"
        )

        # Replace domain media generators with identical mocks
        anki_backend._domain_media_generator = mock_media_generator  # type: ignore[assignment]
        genanki_backend._domain_media_generator = mock_media_generator  # type: ignore[assignment]

        # Process fields with both backends
        anki_result = anki_backend._process_fields_with_media(
            "German Adjective", fields.copy()
        )
        genanki_result = genanki_backend._process_fields_with_media(
            "German Adjective", fields.copy()
        )

        # Results should be identical
        assert anki_result == genanki_result

        # Verify expected structure
        assert len(anki_result) == 8
        assert anki_result[0] == "schön"  # Word unchanged
        assert anki_result[1] == "beautiful"  # English unchanged
        assert anki_result[2] == "Das ist schön."  # Example unchanged
        assert anki_result[5] == '<img src="image.jpg">'  # Image generated
        assert anki_result[6] == "[sound:audio.mp3]"  # WordAudio generated
        assert anki_result[7] == "[sound:audio.mp3]"  # ExampleAudio generated

    def test_error_handling_consistency(self) -> None:
        """Test that both backends handle processing errors identically."""
        fields = ["schön", "beautiful", "Das ist schön."]

        anki_backend = AnkiBackend("Test Deck")
        genanki_backend = GenankiBackend("Test Deck", enable_field_processing=True)

        # Mock field processor to raise an exception
        factory_path = "langlearn.models.model_factory.ModelFactory"
        with patch(f"{factory_path}.create_field_processor") as mock_factory:
            mock_processor = Mock()
            error_msg = "Test error"
            mock_processor.process_fields_for_media_generation.side_effect = Exception(
                error_msg
            )
            mock_factory.return_value = mock_processor

            # Both backends should handle errors gracefully and return original fields
            anki_result = anki_backend._process_fields_with_media(
                "German Adjective", fields
            )
            genanki_result = genanki_backend._process_fields_with_media(
                "German Adjective", fields
            )

            # Both should return original fields on error
            assert anki_result == fields
            assert genanki_result == fields

    def test_unsupported_note_type_handling(self) -> None:
        """Test handling of note types not supported by ModelFactory."""
        fields = ["word", "meaning", "example"]

        anki_backend = AnkiBackend("Test Deck")
        genanki_backend = GenankiBackend("Test Deck", enable_field_processing=True)

        # Both backends should handle unsupported types gracefully
        anki_result = anki_backend._process_fields_with_media("Unknown Type", fields)
        genanki_result = genanki_backend._process_fields_with_media(
            "Unknown Type", fields
        )

        # AnkiBackend falls back to legacy (which returns fields unchanged for
        # unknown types)
        # GenanKiBackend returns fields unchanged
        assert anki_result == fields
        assert genanki_result == fields


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
