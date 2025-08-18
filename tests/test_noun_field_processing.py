"""
Tests for Noun field processing implementation.

This module tests the Noun model's implementation of the FieldProcessor interface
and its German-specific field processing logic.
"""

import pytest

from langlearn.models.field_processor import FieldProcessingError
from langlearn.models.noun import Noun
from langlearn.services.domain_media_generator import MockDomainMediaGenerator


class TestNounFieldProcessing:
    """Test Noun implementation of FieldProcessor interface."""

    @pytest.fixture
    def concrete_noun(self) -> Noun:
        """Create a test concrete noun instance."""
        return Noun(
            noun="Katze",
            article="die",
            english="cat",
            plural="Katzen",
            example="Die Katze ist sehr süß.",
            related="Tier, Haustier",
            word_audio="",
            example_audio="",
            image_path="",
        )

    @pytest.fixture
    def abstract_noun(self) -> Noun:
        """Create a test abstract noun instance."""
        return Noun(
            noun="Freiheit",
            article="die",
            english="freedom",
            plural="Freiheiten",
            example="Freiheit ist wichtig.",
            related="Recht, Demokratie",
            word_audio="",
            example_audio="",
            image_path="",
        )

    @pytest.fixture
    def mock_generator(self) -> MockDomainMediaGenerator:
        """Create mock media generator for testing."""
        return MockDomainMediaGenerator()

    def test_noun_implements_field_processor(self, concrete_noun: Noun) -> None:
        """Test that Noun properly implements FieldProcessor interface."""
        from langlearn.models.field_processor import FieldProcessor

        assert isinstance(concrete_noun, FieldProcessor)
        assert hasattr(concrete_noun, "process_fields_for_media_generation")
        assert hasattr(concrete_noun, "get_expected_field_count")
        assert hasattr(concrete_noun, "validate_field_structure")
        assert hasattr(concrete_noun, "_get_field_names")

    def test_field_layout_info(self, concrete_noun: Noun) -> None:
        """Test field layout information."""
        info = concrete_noun.get_field_layout_info()

        assert info["model_type"] == "Noun"
        assert info["expected_field_count"] == 9
        assert info["field_names"] == [
            "Noun",
            "Article",
            "English",
            "Plural",
            "Example",
            "Related",
            "Image",
            "WordAudio",
            "ExampleAudio",
        ]

    def test_field_validation(self, concrete_noun: Noun) -> None:
        """Test field structure validation."""
        # Valid field counts
        assert concrete_noun.validate_field_structure([""] * 9) is True
        assert (
            concrete_noun.validate_field_structure([""] * 10) is True
        )  # Extra fields OK

        # Invalid field counts
        assert concrete_noun.validate_field_structure([""] * 8) is False
        assert concrete_noun.validate_field_structure([]) is False

    def test_process_fields_complete_generation_concrete(
        self, concrete_noun: Noun, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test complete field processing with all media generation for concrete."""
        fields = [
            "Katze",  # 0: Noun
            "die",  # 1: Article
            "cat",  # 2: English
            "Katzen",  # 3: Plural
            "Die Katze ist sehr süß.",  # 4: Example
            "Tier, Haustier",  # 5: Related
            "",  # 6: Image (empty - should generate for concrete)
            "",  # 7: WordAudio (empty - should generate)
            "",  # 8: ExampleAudio (empty - should generate)
        ]

        # Set up mock responses
        mock_generator.set_responses(
            audio="/fake/audio.mp3", image="/fake/image.jpg", context="cat animal pet"
        )

        result = concrete_noun.process_fields_for_media_generation(
            fields, mock_generator
        )

        # Verify field structure preserved
        assert len(result) == 9
        assert result[0] == "Katze"
        assert result[1] == "die"
        assert result[2] == "cat"
        assert result[3] == "Katzen"
        assert result[4] == "Die Katze ist sehr süß."
        assert result[5] == "Tier, Haustier"

        # Verify media generated
        assert result[6] == '<img src="image.jpg">'  # Image generated for concrete noun
        assert result[7] == "[sound:audio.mp3]"  # WordAudio generated
        assert result[8] == "[sound:audio.mp3]"  # ExampleAudio generated

        # Verify mock was called correctly
        assert len(mock_generator.audio_calls) == 2
        assert (
            mock_generator.audio_calls[0] == "die Katze, die Katzen"
        )  # Combined audio
        assert (
            mock_generator.audio_calls[1] == "Die Katze ist sehr süß."
        )  # Example audio

        assert len(mock_generator.image_calls) == 1
        assert mock_generator.image_calls[0] == ("cat", "cat")  # Search terms, backup

    def test_process_fields_complete_generation_abstract(
        self, abstract_noun: Noun, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test complete field processing for abstract noun (no image generation)."""
        fields = [
            "Freiheit",  # 0: Noun
            "die",  # 1: Article
            "freedom",  # 2: English
            "Freiheiten",  # 3: Plural
            "Freiheit ist wichtig.",  # 4: Example
            "Recht, Demokratie",  # 5: Related
            "",  # 6: Image (empty - should NOT generate for abstract)
            "",  # 7: WordAudio (empty - should generate)
            "",  # 8: ExampleAudio (empty - should generate)
        ]

        # Set up mock responses
        mock_generator.set_responses(
            audio="/fake/audio.mp3",
            image="/fake/image.jpg",
            context="person celebrating independence",
        )

        result = abstract_noun.process_fields_for_media_generation(
            fields, mock_generator
        )

        # Verify field structure preserved
        assert len(result) == 9
        assert result[0] == "Freiheit"
        assert result[6] == ""  # Image field still empty for abstract noun

        # Verify audio generated but not image
        assert result[7] == "[sound:audio.mp3]"  # WordAudio generated
        assert result[8] == "[sound:audio.mp3]"  # ExampleAudio generated

        # Verify mock was called correctly - no image generation for abstract nouns
        assert len(mock_generator.audio_calls) == 2
        assert mock_generator.audio_calls[0] == "die Freiheit, die Freiheiten"
        assert len(mock_generator.image_calls) == 0  # No image calls for abstract noun

    def test_process_fields_partial_generation(
        self, concrete_noun: Noun, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test field processing with some fields already populated."""
        fields = [
            "Hund",
            "der",
            "dog",
            "Hunde",
            "Der Hund bellt.",
            "Tier",
            '<img src="existing.jpg">',  # Image already exists
            "",  # WordAudio empty - should generate
            "[sound:existing.mp3]",  # ExampleAudio already exists
        ]

        result = concrete_noun.process_fields_for_media_generation(
            fields, mock_generator
        )

        # Verify existing content preserved
        assert result[6] == '<img src="existing.jpg">'
        assert result[8] == "[sound:existing.mp3]"

        # Verify only empty fields got generated
        assert result[7] == "[sound:audio.mp3]"  # WordAudio generated

        # Verify only one audio call (for word, not example)
        assert len(mock_generator.audio_calls) == 1
        assert mock_generator.audio_calls[0] == "der Hund, die Hunde"

        # Verify no image calls (image already existed)
        assert len(mock_generator.image_calls) == 0

    def test_process_fields_media_generation_failure(
        self, concrete_noun: Noun, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test field processing handles media generation failures gracefully."""
        fields = [
            "Baum",
            "der",
            "tree",
            "Bäume",
            "Der Baum ist groß.",
            "Pflanze",
            "",
            "",
            "",
        ]

        # Set up mock to return None (generation failure)
        mock_generator.set_responses(audio=None, image=None, context="tree plant")

        result = concrete_noun.process_fields_for_media_generation(
            fields, mock_generator
        )

        # Verify fields remain empty when generation fails
        assert result[6] == ""  # Image field still empty
        assert result[7] == ""  # WordAudio field still empty
        assert result[8] == ""  # ExampleAudio field still empty

        # Verify mock was still called (attempts were made)
        assert len(mock_generator.audio_calls) == 2
        assert len(mock_generator.image_calls) == 1

    def test_process_fields_insufficient_fields_error(
        self, concrete_noun: Noun, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test error handling for insufficient fields."""
        short_fields = ["Katze", "die", "cat"]  # Only 3 fields, need 9

        with pytest.raises(FieldProcessingError) as exc_info:
            concrete_noun.process_fields_for_media_generation(
                short_fields, mock_generator
            )

        error = exc_info.value
        assert "Insufficient fields" in str(error)
        assert "got 3, need at least 9" in str(error)
        assert error.model_type == "Noun"
        assert error.original_fields == short_fields

    def test_combined_audio_text_integration(
        self, concrete_noun: Noun, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test that domain-specific combined audio text logic is used."""
        fields = [
            "Auto",
            "das",
            "car",
            "Autos",
            "Das Auto ist schnell.",
            "Fahrzeug",
            "",
            "",  # WordAudio - should use combined text
            "",
        ]

        concrete_noun.process_fields_for_media_generation(fields, mock_generator)

        # Verify the combined audio text includes article + noun + plural forms
        assert len(mock_generator.audio_calls) >= 1
        combined_call = mock_generator.audio_calls[0]
        assert "Auto" in combined_call
        assert "das" in combined_call
        assert "Autos" in combined_call
        assert combined_call == "das Auto, die Autos"

    def test_concrete_vs_abstract_noun_detection(
        self, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test that concrete and abstract noun detection affects image generation."""
        # Concrete noun
        concrete = Noun(
            noun="Tisch",
            article="der",
            english="table",
            plural="Tische",
            example="Der Tisch ist braun.",
            related="Möbel",
            word_audio="",
            example_audio="",
            image_path="",
        )

        # Abstract noun (unused - field processing uses field data, not instances)
        # Note: We don't need to instantiate this since we're testing field processing

        # Concrete noun field data (processor uses field data, not instance data)
        concrete_fields = [
            "Tisch",  # 0: Noun
            "der",  # 1: Article
            "table",  # 2: English
            "Tische",  # 3: Plural
            "Der Tisch ist braun.",  # 4: Example
            "Möbel",  # 5: Related
            "",  # 6: Image (empty - should generate for concrete)
            "",  # 7: WordAudio
            "",  # 8: ExampleAudio
        ]

        # Abstract noun field data
        abstract_fields = [
            "Glück",  # 0: Noun
            "das",  # 1: Article
            "happiness",  # 2: English
            "",  # 3: Plural
            "Glück ist wichtig.",  # 4: Example
            "Gefühl",  # 5: Related
            "",  # 6: Image (empty - should NOT generate for abstract)
            "",  # 7: WordAudio
            "",  # 8: ExampleAudio
        ]

        # Process both (any noun instance can be used as processor)
        concrete.process_fields_for_media_generation(
            concrete_fields.copy(), mock_generator
        )
        concrete_image_calls = len(mock_generator.image_calls)

        mock_generator.reset()  # Reset for second test
        concrete.process_fields_for_media_generation(
            abstract_fields.copy(), mock_generator
        )
        abstract_image_calls = len(mock_generator.image_calls)

        # Concrete noun should generate image, abstract should not
        assert concrete_image_calls > 0
        assert abstract_image_calls == 0

    def test_preserve_field_order_and_structure(
        self, concrete_noun: Noun, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test that original field order and structure is preserved."""
        original_fields = [
            "Buch",
            "das",
            "book",
            "Bücher",
            "Das Buch ist interessant.",
            "Literatur",
            "",
            "",
            "",
        ]

        result = concrete_noun.process_fields_for_media_generation(
            original_fields, mock_generator
        )

        # Core content should be unchanged
        assert result[:6] == original_fields[:6]

        # Only media fields should be modified
        assert result[6] != ""  # Image added
        assert result[7] != ""  # WordAudio added
        assert result[8] != ""  # ExampleAudio added

        # But original list should be unmodified (working copy)
        assert original_fields[6] == ""
        assert original_fields[7] == ""
        assert original_fields[8] == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
