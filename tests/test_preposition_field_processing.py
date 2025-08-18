"""Tests for Preposition field processing functionality."""

from langlearn.models.preposition import Preposition
from langlearn.services.domain_media_generator import MockDomainMediaGenerator


class TestPrepositionFieldProcessing:
    """Test preposition-specific field processing functionality."""

    def test_preposition_implements_field_processor_interface(self) -> None:
        """Test that Preposition correctly implements FieldProcessor interface."""
        preposition = Preposition(
            preposition="in",
            english="in",
            case="Accusative/Dative",
            example1="Ich gehe in die Schule.",
            example2="Ich bin in der Schule.",
            audio1="",
            audio2="",
            image_path="",
        )

        # Should implement required methods
        assert hasattr(preposition, "process_fields_for_media_generation")
        assert hasattr(preposition, "get_expected_field_count")
        assert hasattr(preposition, "validate_field_structure")

        # Should have correct field count
        assert preposition.get_expected_field_count() == 7

    def test_preposition_field_validation_sufficient_fields(self) -> None:
        """Test preposition field validation with sufficient fields."""
        preposition = Preposition(
            preposition="auf",
            english="on",
            case="Accusative/Dative",
            example1="Ich lege das Buch auf den Tisch.",
            example2="Das Buch liegt auf dem Tisch.",
            audio1="",
            audio2="",
            image_path="",
        )

        fields = [
            "auf",
            "on",
            "Accusative/Dative",
            "Ich lege das Buch auf den Tisch.",
            "Das Buch liegt auf dem Tisch.",
            "",  # Audio1
            "",  # Audio2
        ]

        assert preposition.validate_field_structure(fields) is True

    def test_preposition_field_validation_insufficient_fields(self) -> None:
        """Test preposition field validation with insufficient fields."""
        preposition = Preposition(
            preposition="mit",
            english="with",
            case="Dative",
            example1="Ich gehe mit dir.",
            example2="",
            audio1="",
            audio2="",
            image_path="",
        )

        # Only 4 fields instead of required 7
        fields = ["mit", "with", "Dative", "Ich gehe mit dir."]

        assert preposition.validate_field_structure(fields) is False

    def test_process_fields_complete_preposition_generation(self) -> None:
        """Test complete preposition field processing with media generation."""
        media_generator = MockDomainMediaGenerator()
        media_generator.set_responses(audio="/fake/audio.mp3")

        preposition = Preposition(
            preposition="unter",
            english="under",
            case="Accusative/Dative",
            example1="Ich stelle die Schuhe unter den Tisch.",
            example2="Die Schuhe stehen unter dem Tisch.",
            audio1="",
            audio2="",
            image_path="",
        )

        fields = [
            "unter",
            "under",
            "Accusative/Dative",
            "Ich stelle die Schuhe unter den Tisch.",
            "Die Schuhe stehen unter dem Tisch.",
            "",  # Audio1 - empty, should be filled
            "",  # Audio2 - empty, should be filled
        ]

        result = preposition.process_fields_for_media_generation(
            fields, media_generator
        )

        # Should generate audio for both examples
        assert result[5] == "[sound:audio.mp3]"
        assert result[6] == "[sound:audio.mp3]"
        assert len(media_generator.audio_calls) == 2
        assert "Ich stelle die Schuhe unter den Tisch." in media_generator.audio_calls
        assert "Die Schuhe stehen unter dem Tisch." in media_generator.audio_calls

    def test_process_fields_existing_audio_preserved(self) -> None:
        """Test that existing audio in fields is preserved."""
        media_generator = MockDomainMediaGenerator()

        preposition = Preposition(
            preposition="vor",
            english="in front of",
            case="Accusative/Dative",
            example1="Ich stelle den Stuhl vor das Fenster.",
            example2="Der Stuhl steht vor dem Fenster.",
            audio1="",
            audio2="",
            image_path="",
        )

        fields = [
            "vor",
            "in front of",
            "Accusative/Dative",
            "Ich stelle den Stuhl vor das Fenster.",
            "Der Stuhl steht vor dem Fenster.",
            "[sound:existing_audio1.mp3]",  # Audio1 - already has audio
            "[sound:existing_audio2.mp3]",  # Audio2 - already has audio
        ]

        result = preposition.process_fields_for_media_generation(
            fields, media_generator
        )

        # Should preserve existing audio
        assert result[5] == "[sound:existing_audio1.mp3]"
        assert result[6] == "[sound:existing_audio2.mp3]"
        # Should not call media generator
        assert len(media_generator.audio_calls) == 0

    def test_process_fields_empty_examples_no_audio(self) -> None:
        """Test preposition processing when examples are empty."""
        media_generator = MockDomainMediaGenerator()

        preposition = Preposition(
            preposition="über",
            english="over/above",
            case="Accusative/Dative",
            example1="",  # Empty example1
            example2="",  # Empty example2
            audio1="",
            audio2="",
            image_path="",
        )

        fields = [
            "über",
            "over/above",
            "Accusative/Dative",
            "",  # Empty example1
            "",  # Empty example2
            "",  # Audio1
            "",  # Audio2
        ]

        result = preposition.process_fields_for_media_generation(
            fields, media_generator
        )

        # Should not generate audio for empty examples
        assert result[5] == ""
        assert result[6] == ""
        assert len(media_generator.audio_calls) == 0

    def test_process_fields_insufficient_fields_returns_original(self) -> None:
        """Test processing with insufficient fields returns original."""
        media_generator = MockDomainMediaGenerator()

        preposition = Preposition(
            preposition="hinter",
            english="behind",
            case="Accusative/Dative",
            example1="Ich stelle das Regal hinter die Tür.",
            example2="Das Regal steht hinter der Tür.",
            audio1="",
            audio2="",
            image_path="",
        )

        # Only 4 fields instead of required 7
        fields = [
            "hinter",
            "behind",
            "Accusative/Dative",
            "Ich stelle das Regal hinter die Tür.",
        ]

        result = preposition.process_fields_for_media_generation(
            fields, media_generator
        )

        # Should return original fields unchanged
        assert result == fields
        assert len(media_generator.audio_calls) == 0

    def test_process_fields_media_generation_failure(self) -> None:
        """Test preposition processing when media generation fails."""
        media_generator = MockDomainMediaGenerator()
        media_generator.set_responses(audio=None)  # Simulate failure

        preposition = Preposition(
            preposition="neben",
            english="next to",
            case="Accusative/Dative",
            example1="Ich setze mich neben den Mann.",
            example2="Ich sitze neben dem Mann.",
            audio1="",
            audio2="",
            image_path="",
        )

        fields = [
            "neben",
            "next to",
            "Accusative/Dative",
            "Ich setze mich neben den Mann.",
            "Ich sitze neben dem Mann.",
            "",  # Audio1
            "",  # Audio2
        ]

        result = preposition.process_fields_for_media_generation(
            fields, media_generator
        )

        # Should leave audio fields empty when generation fails
        assert result[5] == ""
        assert result[6] == ""
        assert len(media_generator.audio_calls) == 2

    def test_get_case_description_simple_cases(self) -> None:
        """Test case description generation for simple cases."""
        accusative_prep = Preposition(
            preposition="durch",
            english="through",
            case="Accusative",
            example1="Ich gehe durch den Park.",
            example2="",
            audio1="",
            audio2="",
            image_path="",
        )

        assert "accusative case" in accusative_prep.get_case_description()

        dative_prep = Preposition(
            preposition="mit",
            english="with",
            case="Dative",
            example1="Ich gehe mit dir.",
            example2="",
            audio1="",
            audio2="",
            image_path="",
        )

        assert "dative case" in dative_prep.get_case_description()

    def test_get_case_description_two_way_preposition(self) -> None:
        """Test case description for two-way prepositions."""
        preposition = Preposition(
            preposition="in",
            english="in",
            case="Accusative/Dative",
            example1="Ich gehe in die Schule.",
            example2="Ich bin in der Schule.",
            audio1="",
            audio2="",
            image_path="",
        )

        description = preposition.get_case_description()
        assert "accusative" in description
        assert "dative" in description

    def test_is_two_way_preposition(self) -> None:
        """Test two-way preposition detection."""
        two_way_prep = Preposition(
            preposition="auf",
            english="on",
            case="Accusative/Dative",
            example1="Ich lege das Buch auf den Tisch.",
            example2="Das Buch liegt auf dem Tisch.",
            audio1="",
            audio2="",
            image_path="",
        )

        assert two_way_prep.is_two_way_preposition() is True

        one_way_prep = Preposition(
            preposition="mit",
            english="with",
            case="Dative",
            example1="Ich gehe mit dir.",
            example2="",
            audio1="",
            audio2="",
            image_path="",
        )

        assert one_way_prep.is_two_way_preposition() is False

    def test_preposition_field_processing_integration(self) -> None:
        """Test integration of preposition field processing with realistic data."""
        media_generator = MockDomainMediaGenerator()
        media_generator.set_responses(audio="/fake/prep_audio.mp3")

        preposition = Preposition(
            preposition="zwischen",
            english="between",
            case="Accusative/Dative",
            example1="Ich setze mich zwischen die Kinder.",
            example2="Ich sitze zwischen den Kindern.",
            audio1="",
            audio2="",
            image_path="",
        )

        # Realistic preposition fields from CSV data
        fields = [
            "zwischen",  # Preposition
            "between",  # English
            "Accusative/Dative",  # Case
            "Ich setze mich zwischen die Kinder.",  # Example1
            "Ich sitze zwischen den Kindern.",  # Example2
            "",  # Audio1 (empty, to be filled)
            "",  # Audio2 (empty, to be filled)
        ]

        result = preposition.process_fields_for_media_generation(
            fields, media_generator
        )

        # Verify all original fields preserved
        assert result[0] == "zwischen"
        assert result[1] == "between"
        assert result[2] == "Accusative/Dative"
        assert result[3] == "Ich setze mich zwischen die Kinder."
        assert result[4] == "Ich sitze zwischen den Kindern."

        # Verify audio was generated for both examples
        assert result[5] == "[sound:prep_audio.mp3]"
        assert result[6] == "[sound:prep_audio.mp3]"
        assert len(media_generator.audio_calls) == 2
        assert "Ich setze mich zwischen die Kinder." in media_generator.audio_calls
        assert "Ich sitze zwischen den Kindern." in media_generator.audio_calls
