"""
Tests for Adverb field processing implementation.

This module tests the Adverb model's implementation of the FieldProcessor interface
and its German-specific field processing logic.
"""

import pytest

from langlearn.models.adverb import Adverb, AdverbType
from langlearn.models.field_processor import FieldProcessingError
from langlearn.services.domain_media_generator import MockDomainMediaGenerator


class TestAdverbFieldProcessing:
    """Test Adverb implementation of FieldProcessor interface."""

    @pytest.fixture
    def location_adverb(self) -> Adverb:
        """Create a test location adverb instance."""
        return Adverb(
            word="hier",
            english="here",
            type=AdverbType.LOCATION,
            example="Ich wohne hier.",
            word_audio="",
            example_audio="",
            image_path="",
        )

    @pytest.fixture
    def time_adverb(self) -> Adverb:
        """Create a test time adverb instance."""
        return Adverb(
            word="heute",
            english="today",
            type=AdverbType.TIME,
            example="Heute ist es sonnig.",
            word_audio="",
            example_audio="",
            image_path="",
        )

    @pytest.fixture
    def mock_generator(self) -> MockDomainMediaGenerator:
        """Create mock media generator for testing."""
        return MockDomainMediaGenerator()

    def test_adverb_implements_field_processor(self, location_adverb: Adverb) -> None:
        """Test that Adverb properly implements FieldProcessor interface."""
        from langlearn.models.field_processor import FieldProcessor

        assert isinstance(location_adverb, FieldProcessor)
        assert hasattr(location_adverb, "process_fields_for_media_generation")
        assert hasattr(location_adverb, "get_expected_field_count")
        assert hasattr(location_adverb, "validate_field_structure")
        assert hasattr(location_adverb, "_get_field_names")

    def test_field_layout_info(self, location_adverb: Adverb) -> None:
        """Test field layout information."""
        info = location_adverb.get_field_layout_info()

        assert info["model_type"] == "Adverb"
        assert info["expected_field_count"] == 7
        assert info["field_names"] == [
            "Word",
            "English",
            "Type",
            "Example",
            "WordAudio",
            "ExampleAudio",
            "Image",
        ]

    def test_field_validation(self, location_adverb: Adverb) -> None:
        """Test field structure validation."""
        # Valid field counts
        assert location_adverb.validate_field_structure([""] * 7) is True
        # Extra fields OK
        assert location_adverb.validate_field_structure([""] * 8) is True

        # Invalid field counts
        assert location_adverb.validate_field_structure([""] * 6) is False
        assert location_adverb.validate_field_structure([]) is False

    def test_process_fields_complete_generation(
        self, location_adverb: Adverb, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test complete field processing with all media generation."""
        fields = [
            "hier",  # 0: Word
            "here",  # 1: English
            "location",  # 2: Type
            "Ich wohne hier.",  # 3: Example
            "",  # 4: WordAudio (empty - should generate)
            "",  # 5: ExampleAudio (empty - should generate)
            "",  # 6: Image (empty - should generate)
        ]

        # Set up mock responses
        mock_generator.set_responses(
            audio="/fake/audio.mp3",
            image="/fake/image.jpg",
            context="location place here",
        )

        result = location_adverb.process_fields_for_media_generation(
            fields, mock_generator
        )

        # Verify field structure preserved
        assert len(result) == 7
        assert result[0] == "hier"
        assert result[1] == "here"
        assert result[2] == "location"
        assert result[3] == "Ich wohne hier."

        # Verify media generated
        assert result[4] == "[sound:audio.mp3]"  # WordAudio generated
        assert result[5] == "[sound:audio.mp3]"  # ExampleAudio generated
        assert result[6] == '<img src="image.jpg">'  # Image generated

        # Verify mock was called correctly
        assert len(mock_generator.audio_calls) == 2
        assert mock_generator.audio_calls[0] == "hier"  # Word audio
        assert mock_generator.audio_calls[1] == "Ich wohne hier."  # Example audio

        assert len(mock_generator.image_calls) == 1
        # Check that AI-enhanced search terms were generated (now uses AnthropicService)
        primary_query, backup_query = mock_generator.image_calls[0]
        assert len(primary_query) > len(
            "here"
        )  # Should be more detailed than just "here"
        assert backup_query == "here"  # Backup is always the English fallback

    def test_process_fields_partial_generation(
        self, time_adverb: Adverb, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test field processing with some fields already populated."""
        fields = [
            "heute",
            "today",
            "time",
            "Heute ist es sonnig.",
            "[sound:existing.mp3]",  # WordAudio already exists
            "",  # ExampleAudio empty - should generate
            '<img src="existing.jpg">',  # Image already exists
        ]

        result = time_adverb.process_fields_for_media_generation(fields, mock_generator)

        # Verify existing content preserved
        assert result[4] == "[sound:existing.mp3]"
        assert result[6] == '<img src="existing.jpg">'

        # Verify only empty fields got generated
        assert result[5] == "[sound:audio.mp3]"  # ExampleAudio generated

        # Verify only one audio call (for example, not word)
        assert len(mock_generator.audio_calls) == 1
        assert mock_generator.audio_calls[0] == "Heute ist es sonnig."

        # Verify no image calls (image already existed)
        assert len(mock_generator.image_calls) == 0

    def test_process_fields_media_generation_failure(
        self, location_adverb: Adverb, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test field processing handles media generation failures gracefully."""
        fields = [
            "dort",
            "there",
            "location",
            "Das Buch liegt dort.",
            "",
            "",
            "",
        ]

        # Set up mock to return None (generation failure)
        mock_generator.set_responses(
            audio=None, image=None, context="location place there"
        )

        result = location_adverb.process_fields_for_media_generation(
            fields, mock_generator
        )

        # Verify fields remain empty when generation fails
        assert result[4] == ""  # WordAudio field still empty
        assert result[5] == ""  # ExampleAudio field still empty
        assert result[6] == ""  # Image field still empty

        # Verify mock was still called (attempts were made)
        assert len(mock_generator.audio_calls) == 2
        assert len(mock_generator.image_calls) == 1

    def test_process_fields_insufficient_fields_error(
        self, location_adverb: Adverb, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test error handling for insufficient fields."""
        short_fields = ["hier", "here", "location"]  # Only 3 fields, need 7

        with pytest.raises(FieldProcessingError) as exc_info:
            location_adverb.process_fields_for_media_generation(
                short_fields, mock_generator
            )

        error = exc_info.value
        assert "Insufficient fields" in str(error)
        assert "got 3, need at least 7" in str(error)
        assert error.model_type == "Adverb"
        assert error.original_fields == short_fields

    def test_ai_enhanced_search_terms_integration(
        self, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test AI-enhanced search terms for different adverb types."""
        # Test different adverb types with AI-generated contextual search terms
        test_cases = [
            ("hier", "here", "location"),
            ("heute", "today", "time"),
            ("langsam", "slowly", "manner"),
            ("sehr", "very", "intensity"),
        ]

        for word, english, adverb_type in test_cases:
            adverb = Adverb(
                word=word,
                english=english,
                type=AdverbType(adverb_type),
                example=f"Test {word}.",
                word_audio="",
                example_audio="",
                image_path="",
            )

            fields = [word, english, adverb_type, f"Test {word}.", "", "", ""]
            mock_generator.reset()

            adverb.process_fields_for_media_generation(fields, mock_generator)

            # Verify AI-enhanced search terms were generated
            if mock_generator.image_calls:
                actual_search = mock_generator.image_calls[0][0]
                # Should contain the English meaning or be contextually relevant
                assert len(actual_search) > len(
                    english
                )  # More detailed than just the English word
                assert (
                    english in actual_search
                    or word in actual_search
                    or any(
                        term in actual_search.lower() for term in ["test", adverb_type]
                    )
                )

    def test_invalid_adverb_type_handling(
        self, location_adverb: Adverb, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test handling of invalid adverb types in field processing."""
        fields = [
            "test",
            "test",
            "invalid_type",  # Invalid AdverbType
            "Test sentence.",
            "",
            "",
            "",
        ]

        # Should not raise exception, just skip image generation
        result = location_adverb.process_fields_for_media_generation(
            fields, mock_generator
        )

        # Audio should still be generated
        assert result[4] == "[sound:audio.mp3]"  # WordAudio
        assert result[5] == "[sound:audio.mp3]"  # ExampleAudio

        # Image should remain empty due to invalid type
        assert result[6] == ""

        # Audio calls made, but no image calls
        assert len(mock_generator.audio_calls) == 2
        assert len(mock_generator.image_calls) == 0

    def test_adverb_type_specific_search_terms(
        self, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test that different adverb types get appropriate search terms."""
        # Test location adverb fallback
        fields = ["oben", "above", "location", "Die Katze ist oben.", "", "", ""]

        location_adverb = Adverb(
            word="oben",
            english="above",
            type=AdverbType.LOCATION,
            example="Die Katze ist oben.",
            word_audio="",
            example_audio="",
            image_path="",
        )

        location_adverb.process_fields_for_media_generation(fields, mock_generator)

        # Check that AI-enhanced contextual search terms were generated
        if mock_generator.image_calls:
            search_terms = mock_generator.image_calls[0][0]
            # Should generate contextual terms based on the German sentence
            assert len(search_terms) > len("above")  # More detailed than just "above"
            assert any(
                word in search_terms.lower()
                for word in ["above", "cat", "high", "up", "over"]
            )

    def test_preserve_field_order_and_structure(
        self, location_adverb: Adverb, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test that original field order and structure is preserved."""
        original_fields = [
            "unten",
            "below",
            "location",
            "Das Auto steht unten.",
            "",
            "",
            "",
        ]

        result = location_adverb.process_fields_for_media_generation(
            original_fields, mock_generator
        )

        # Core content should be unchanged
        assert result[:4] == original_fields[:4]

        # Only media fields should be modified
        assert result[4] != ""  # WordAudio added
        assert result[5] != ""  # ExampleAudio added
        assert result[6] != ""  # Image added

        # But original list should be unmodified (working copy)
        assert original_fields[4] == ""
        assert original_fields[5] == ""
        assert original_fields[6] == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
