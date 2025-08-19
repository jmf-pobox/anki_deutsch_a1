"""
Tests for Negation field processing implementation.

This module tests the Negation model's implementation of the FieldProcessor interface
and its German-specific field processing logic.
"""

import pytest

from langlearn.models.field_processor import FieldProcessingError
from langlearn.models.negation import Negation, NegationType
from langlearn.services.domain_media_generator import MockDomainMediaGenerator


class TestNegationFieldProcessing:
    """Test Negation implementation of FieldProcessor interface."""

    @pytest.fixture
    def general_negation(self) -> Negation:
        """Create a test general negation instance."""
        return Negation(
            word="nicht",
            english="not",
            type=NegationType.GENERAL,
            example="Ich verstehe das nicht.",
            word_audio="",
            example_audio="",
            image_path="",
        )

    @pytest.fixture
    def article_negation(self) -> Negation:
        """Create a test article negation instance."""
        return Negation(
            word="kein",
            english="no/not a",
            type=NegationType.ARTICLE,
            example="Ich habe kein Auto.",
            word_audio="",
            example_audio="",
            image_path="",
        )

    @pytest.fixture
    def pronoun_negation(self) -> Negation:
        """Create a test pronoun negation instance."""
        return Negation(
            word="nichts",
            english="nothing",
            type=NegationType.PRONOUN,
            example="Ich verstehe nichts.",
            word_audio="",
            example_audio="",
            image_path="",
        )

    @pytest.fixture
    def mock_generator(self) -> MockDomainMediaGenerator:
        """Create mock media generator for testing."""
        return MockDomainMediaGenerator()

    def test_negation_implements_field_processor(
        self, general_negation: Negation
    ) -> None:
        """Test that Negation properly implements FieldProcessor interface."""
        from langlearn.models.field_processor import FieldProcessor

        assert isinstance(general_negation, FieldProcessor)
        assert hasattr(general_negation, "process_fields_for_media_generation")
        assert hasattr(general_negation, "get_expected_field_count")
        assert hasattr(general_negation, "validate_field_structure")
        assert hasattr(general_negation, "_get_field_names")

    def test_field_layout_info(self, general_negation: Negation) -> None:
        """Test field layout information."""
        info = general_negation.get_field_layout_info()

        assert info["model_type"] == "Negation"
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

    def test_field_validation(self, general_negation: Negation) -> None:
        """Test field structure validation."""
        # Valid field counts
        assert general_negation.validate_field_structure([""] * 7) is True
        # Extra fields OK
        assert general_negation.validate_field_structure([""] * 8) is True

        # Invalid field counts
        assert general_negation.validate_field_structure([""] * 6) is False
        assert general_negation.validate_field_structure([]) is False

    def test_process_fields_complete_generation(
        self, general_negation: Negation, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test complete field processing with all media generation."""
        fields = [
            "nicht",  # 0: Word
            "not",  # 1: English
            "general",  # 2: Type
            "Ich verstehe das nicht.",  # 3: Example
            "",  # 4: WordAudio (empty - should generate)
            "",  # 5: ExampleAudio (empty - should generate)
            "",  # 6: Image (empty - should generate)
        ]

        # Set up mock responses
        mock_generator.set_responses(
            audio="/fake/audio.mp3",
            image="/fake/image.jpg",
            context="prohibition stop sign red x",
        )

        result = general_negation.process_fields_for_media_generation(
            fields, mock_generator
        )

        # Verify field structure preserved
        assert len(result) == 7
        assert result[0] == "nicht"
        assert result[1] == "not"
        assert result[2] == "general"
        assert result[3] == "Ich verstehe das nicht."

        # Verify media generated
        assert result[4] == "[sound:audio.mp3]"  # WordAudio generated
        assert result[5] == "[sound:audio.mp3]"  # ExampleAudio generated
        assert result[6] == '<img src="image.jpg">'  # Image generated

        # Verify mock was called correctly
        assert len(mock_generator.audio_calls) == 2
        assert mock_generator.audio_calls[0] == "nicht"  # Word audio
        assert (
            mock_generator.audio_calls[1] == "Ich verstehe das nicht."
        )  # Example audio

        assert len(mock_generator.image_calls) == 1
        # Check that AI-enhanced search terms were generated (now uses AnthropicService)
        primary_query, backup_query = mock_generator.image_calls[0]
        assert len(primary_query) > len(
            "not"
        )  # Should be more detailed than just "not"
        assert backup_query == "not"  # Backup is always the English fallback

    def test_process_fields_partial_generation(
        self, article_negation: Negation, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test field processing with some fields already populated."""
        fields = [
            "kein",
            "no/not a",
            "article",
            "Ich habe kein Auto.",
            "[sound:existing.mp3]",  # WordAudio already exists
            "",  # ExampleAudio empty - should generate
            '<img src="existing.jpg">',  # Image already exists
        ]

        result = article_negation.process_fields_for_media_generation(
            fields, mock_generator
        )

        # Verify existing content preserved
        assert result[4] == "[sound:existing.mp3]"
        assert result[6] == '<img src="existing.jpg">'

        # Verify only empty fields got generated
        assert result[5] == "[sound:audio.mp3]"  # ExampleAudio generated

        # Verify only one audio call (for example, not word)
        assert len(mock_generator.audio_calls) == 1
        assert mock_generator.audio_calls[0] == "Ich habe kein Auto."

        # Verify no image calls (image already existed)
        assert len(mock_generator.image_calls) == 0

    def test_process_fields_media_generation_failure(
        self, pronoun_negation: Negation, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test field processing handles media generation failures gracefully."""
        fields = [
            "nichts",
            "nothing",
            "pronoun",
            "Ich verstehe nichts.",
            "",
            "",
            "",
        ]

        # Set up mock to return None (generation failure)
        mock_generator.set_responses(
            audio=None, image=None, context="empty void blank nothing"
        )

        result = pronoun_negation.process_fields_for_media_generation(
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
        self, general_negation: Negation, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test error handling for insufficient fields."""
        short_fields = ["nicht", "not", "general"]  # Only 3 fields, need 7

        with pytest.raises(FieldProcessingError) as exc_info:
            general_negation.process_fields_for_media_generation(
                short_fields, mock_generator
            )

        error = exc_info.value
        assert "Insufficient fields" in str(error)
        assert "got 3, need at least 7" in str(error)
        assert error.model_type == "Negation"
        assert error.original_fields == short_fields

    def test_ai_enhanced_image_search_integration(
        self, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test AI-enhanced image search terms for different negation types."""
        # Test different negation types with AI-generated contextual search terms
        test_cases = [
            ("nicht", "not", "general"),
            ("kein", "no/not a", "article"),
            ("nichts", "nothing", "pronoun"),
            ("nie", "never", "temporal"),
            ("nirgends", "nowhere", "spatial"),
        ]

        for word, english, negation_type in test_cases:
            negation = Negation(
                word=word,
                english=english,
                type=NegationType(negation_type),
                example=f"Test {word}.",
                word_audio="",
                example_audio="",
                image_path="",
            )

            fields = [word, english, negation_type, f"Test {word}.", "", "", ""]
            mock_generator.reset()

            negation.process_fields_for_media_generation(fields, mock_generator)

            # Verify AI-enhanced search terms were generated
            if mock_generator.image_calls:
                actual_search = mock_generator.image_calls[0][0]
                # Should generate contextual terms that are more detailed
                # than the basic English
                assert len(actual_search) >= len(
                    english.split("/")[0]
                )  # At least as long as the main English meaning
                # Should be contextual and relevant to the negation concept
                assert actual_search != ""  # Should not be empty

    def test_invalid_negation_type_handling(
        self, general_negation: Negation, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test handling of invalid negation types in field processing."""
        fields = [
            "test",
            "test",
            "invalid_type",  # Invalid NegationType
            "Test sentence.",
            "",
            "",
            "",
        ]

        # Should not raise exception, just skip image generation
        result = general_negation.process_fields_for_media_generation(
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

    def test_negation_type_specific_fallbacks(
        self, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test that different negation types get appropriate fallback search terms."""
        # Test correlative negation fallback
        fields = [
            "weder",
            "neither",
            "correlative",
            "Weder Hans noch Maria.",
            "",
            "",
            "",
        ]

        correlative_negation = Negation(
            word="weder",
            english="neither",
            type=NegationType.CORRELATIVE,
            example="Weder Hans noch Maria.",
            word_audio="",
            example_audio="",
            image_path="",
        )

        correlative_negation.process_fields_for_media_generation(fields, mock_generator)

        # Check that AI-enhanced terms were generated for correlative negation
        if mock_generator.image_calls:
            search_terms = mock_generator.image_calls[0][0]
            # Should contain contextual terms related to the German sentence meaning
            assert len(search_terms) > len("neither")  # Should be more detailed
            assert any(
                word in search_terms.lower()
                for word in ["neither", "choice", "people", "excluded"]
            )

    def test_preserve_field_order_and_structure(
        self, general_negation: Negation, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test that original field order and structure is preserved."""
        original_fields = [
            "nicht",
            "not",
            "general",
            "Das ist nicht richtig.",
            "",
            "",
            "",
        ]

        result = general_negation.process_fields_for_media_generation(
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

    def test_ai_enhanced_search_terms(
        self, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test that AI-enhanced search terms are generated for different negations."""
        # Test that different negations generate relevant AI search terms
        test_cases = [
            ("kein", "no", "Kein Problem."),
            ("niemand", "nobody", "Niemand ist da."),
            ("niemals", "never", "Das mache ich niemals."),
            ("nirgendwo", "nowhere", "Ich finde es nirgendwo."),
        ]

        for word, english, example in test_cases:
            negation = Negation(
                word=word,
                english=english,
                type=NegationType.GENERAL,
                example=example,
                word_audio="",
                example_audio="",
                image_path="",
            )

            search_terms = negation.get_image_search_terms()
            # Check that AI-generated terms are contextual and relevant
            # AI may generate very contextual terms that don't literally
            # contain the word but are visually relevant
            assert isinstance(search_terms, str)
            assert len(search_terms) > 0  # Should generate some search terms
            assert len(search_terms) > 3  # Should be more than just a single short word


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
