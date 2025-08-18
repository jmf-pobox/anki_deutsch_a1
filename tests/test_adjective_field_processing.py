"""
Tests for Adjective field processing implementation.

This module tests the Phase 2 implementation where the Adjective model
implements the FieldProcessor interface and handles its own field processing.
"""

import pytest

from langlearn.models.adjective import Adjective
from langlearn.models.field_processor import FieldProcessingError
from langlearn.services.domain_media_generator import MockDomainMediaGenerator


class TestAdjectiveFieldProcessing:
    """Test Adjective implementation of FieldProcessor interface."""

    @pytest.fixture
    def adjective(self) -> Adjective:
        """Create a test adjective instance."""
        return Adjective(
            word="schön",
            english="beautiful",
            example="Das ist schön.",
            comparative="schöner",
            superlative="am schönsten",
            word_audio="",
            example_audio="",
            image_path="",
        )

    @pytest.fixture
    def mock_generator(self) -> MockDomainMediaGenerator:
        """Create mock media generator for testing."""
        return MockDomainMediaGenerator()

    def test_adjective_implements_field_processor(self, adjective: Adjective) -> None:
        """Test that Adjective properly implements FieldProcessor interface."""
        from langlearn.models.field_processor import FieldProcessor

        assert isinstance(adjective, FieldProcessor)
        assert hasattr(adjective, "process_fields_for_media_generation")
        assert hasattr(adjective, "get_expected_field_count")
        assert hasattr(adjective, "validate_field_structure")
        assert hasattr(adjective, "_get_field_names")

    def test_field_layout_info(self, adjective: Adjective) -> None:
        """Test field layout information."""
        info = adjective.get_field_layout_info()

        assert info["model_type"] == "Adjective"
        assert info["expected_field_count"] == 8
        assert info["field_names"] == [
            "Word",
            "English",
            "Example",
            "Comparative",
            "Superlative",
            "Image",
            "WordAudio",
            "ExampleAudio",
        ]

    def test_field_validation(self, adjective: Adjective) -> None:
        """Test field structure validation."""
        # Valid field counts
        assert adjective.validate_field_structure([""] * 8) is True
        assert adjective.validate_field_structure([""] * 9) is True  # Extra fields OK

        # Invalid field counts
        assert adjective.validate_field_structure([""] * 7) is False
        assert adjective.validate_field_structure([]) is False

    def test_process_fields_complete_generation(
        self, adjective: Adjective, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test complete field processing with all media generation."""
        fields = [
            "schön",  # 0: Word
            "beautiful",  # 1: English
            "Das ist schön.",  # 2: Example
            "schöner",  # 3: Comparative
            "am schönsten",  # 4: Superlative
            "",  # 5: Image (empty - should generate)
            "",  # 6: WordAudio (empty - should generate)
            "",  # 7: ExampleAudio (empty - should generate)
        ]

        # Set up mock responses
        mock_generator.set_responses(
            audio="/fake/audio.mp3",
            image="/fake/image.jpg",
            context="beautiful sunset scene",
        )

        result = adjective.process_fields_for_media_generation(fields, mock_generator)

        # Verify field structure preserved
        assert len(result) == 8
        assert result[0] == "schön"
        assert result[1] == "beautiful"
        assert result[2] == "Das ist schön."
        assert result[3] == "schöner"
        assert result[4] == "am schönsten"

        # Verify media generated
        assert result[5] == '<img src="image.jpg">'
        assert result[6] == "[sound:audio.mp3]"
        assert result[7] == "[sound:audio.mp3]"

        # Verify mock was called correctly
        assert len(mock_generator.audio_calls) == 2
        assert (
            mock_generator.audio_calls[0] == "schön, schöner, am schönsten"
        )  # Combined audio
        assert mock_generator.audio_calls[1] == "Das ist schön."  # Example audio

        assert len(mock_generator.image_calls) == 1
        assert mock_generator.image_calls[0] == (
            "beautiful",
            "beautiful",
        )  # Enhanced search terms from domain model

        # Context calls are no longer used - we now use domain-specific search terms
        assert len(mock_generator.context_calls) == 0

    def test_process_fields_partial_generation(
        self, adjective: Adjective, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test field processing with some fields already populated."""
        fields = [
            "gut",
            "good",
            "Das ist gut.",
            "besser",
            "am besten",
            '<img src="existing.jpg">',  # Image already exists
            "",  # WordAudio empty - should generate
            "[sound:existing.mp3]",  # ExampleAudio already exists
        ]

        result = adjective.process_fields_for_media_generation(fields, mock_generator)

        # Verify existing content preserved
        assert result[5] == '<img src="existing.jpg">'
        assert result[7] == "[sound:existing.mp3]"

        # Verify only empty fields got generated
        assert result[6] == "[sound:audio.mp3]"  # WordAudio generated

        # Verify only one audio call (for word, not example)
        assert len(mock_generator.audio_calls) == 1
        assert mock_generator.audio_calls[0] == "gut, besser, am besten"

        # Verify no image or context calls (image already existed)
        assert len(mock_generator.image_calls) == 0
        assert len(mock_generator.context_calls) == 0

    def test_process_fields_media_generation_failure(
        self, adjective: Adjective, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test field processing handles media generation failures gracefully."""
        fields = [
            "schön",
            "beautiful",
            "Das ist schön.",
            "schöner",
            "am schönsten",
            "",
            "",
            "",
        ]

        # Set up mock to return None (generation failure)
        mock_generator.set_responses(audio=None, image=None, context="enhanced")

        result = adjective.process_fields_for_media_generation(fields, mock_generator)

        # Verify fields remain empty when generation fails
        assert result[5] == ""  # Image field still empty
        assert result[6] == ""  # WordAudio field still empty
        assert result[7] == ""  # ExampleAudio field still empty

        # Verify mock was still called (attempts were made)
        assert len(mock_generator.audio_calls) == 2
        assert len(mock_generator.image_calls) == 1

    def test_process_fields_insufficient_fields_error(
        self, adjective: Adjective, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test error handling for insufficient fields."""
        short_fields = ["schön", "beautiful"]  # Only 2 fields, need 8

        with pytest.raises(FieldProcessingError) as exc_info:
            adjective.process_fields_for_media_generation(short_fields, mock_generator)

        error = exc_info.value
        assert "Insufficient fields" in str(error)
        assert "got 2, need at least 8" in str(error)
        assert error.model_type == "Adjective"
        assert error.original_fields == short_fields

    def test_combined_audio_text_integration(
        self, adjective: Adjective, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test that domain-specific combined audio text logic is used."""
        fields = [
            "hoch",  # Irregular adjective
            "high",
            "Der Berg ist hoch.",
            "höher",  # Irregular comparative
            "am höchsten",  # Irregular superlative
            "",
            "",  # WordAudio - should use combined text
            "",
        ]

        adjective.process_fields_for_media_generation(fields, mock_generator)

        # Verify the combined audio text includes all forms
        assert len(mock_generator.audio_calls) >= 1
        combined_call = mock_generator.audio_calls[0]
        assert "hoch" in combined_call
        assert "höher" in combined_call
        assert "höchsten" in combined_call
        assert combined_call == "hoch, höher, am höchsten"

    def test_empty_optional_fields_handling(
        self, adjective: Adjective, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test handling of empty optional fields like superlative."""
        fields = [
            "schnell",
            "fast",
            "Das Auto ist schnell.",
            "schneller",
            "",  # Empty superlative (optional)
            "",
            "",
            "",
        ]

        result = adjective.process_fields_for_media_generation(fields, mock_generator)

        # Should still work with empty superlative
        assert len(result) == 8

        # Combined audio should only include non-empty forms
        combined_call = mock_generator.audio_calls[0]
        assert combined_call == "schnell, schneller"  # No superlative

    def test_preserve_field_order_and_structure(
        self, adjective: Adjective, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test that original field order and structure is preserved."""
        original_fields = [
            "alt",
            "old",
            "Das Haus ist alt.",
            "älter",
            "am ältesten",
            "",
            "",
            "",
        ]

        result = adjective.process_fields_for_media_generation(
            original_fields, mock_generator
        )

        # Core content should be unchanged
        assert result[:5] == original_fields[:5]

        # Only media fields should be modified
        assert result[5] != ""  # Image added
        assert result[6] != ""  # WordAudio added
        assert result[7] != ""  # ExampleAudio added

        # But original list should be unmodified (working copy)
        assert original_fields[5] == ""
        assert original_fields[6] == ""
        assert original_fields[7] == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
