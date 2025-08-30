"""Tests for Verb field processing functionality."""

from langlearn.models.verb import Verb
from langlearn.services.domain_media_generator import MockDomainMediaGenerator


class TestVerbFieldProcessing:
    """Test verb-specific field processing functionality."""

    def test_verb_implements_field_processor_interface(self) -> None:
        """Test that Verb correctly implements FieldProcessor interface."""
        verb = Verb(
            verb="gehen",
            english="to go",
            present_ich="gehe",
            present_du="gehst",
            present_er="geht",
            perfect="ist gegangen",
            example="Ich gehe zur Schule.",
            word_audio="",
            example_audio="",
            image_path="",
        )

        # Should implement required methods
        assert hasattr(verb, "process_fields_for_media_generation")
        assert hasattr(verb, "get_expected_field_count")
        assert hasattr(verb, "validate_field_structure")

        # Should have correct field count
        assert verb.get_expected_field_count() == 8

    def test_verb_field_validation_sufficient_fields(self) -> None:
        """Test verb field validation with sufficient fields."""
        verb = Verb(
            verb="spielen",
            english="to play",
            present_ich="spiele",
            present_du="spielst",
            present_er="spielt",
            perfect="hat gespielt",
            example="Wir spielen Fußball.",
            word_audio="",
            example_audio="",
            image_path="",
        )

        fields = [
            "spielen",
            "to play",
            "spiele",
            "spielst",
            "spielt",
            "hat gespielt",
            "Wir spielen Fußball.",
            "",  # ExampleAudio
        ]

        assert verb.validate_field_structure(fields) is True

    def test_verb_field_validation_insufficient_fields(self) -> None:
        """Test verb field validation with insufficient fields."""
        verb = Verb(
            verb="sein",
            english="to be",
            present_ich="bin",
            present_du="bist",
            present_er="ist",
            perfect="ist gewesen",
            example="Ich bin hier.",
            word_audio="",
            example_audio="",
            image_path="",
        )

        # Only 5 fields instead of required 8
        fields = ["sein", "to be", "bin", "bist", "ist"]

        assert verb.validate_field_structure(fields) is False

    def test_process_fields_complete_verb_generation(self) -> None:
        """Test complete verb field processing with media generation."""
        media_generator = MockDomainMediaGenerator()
        media_generator.set_responses(audio="/fake/audio.mp3")

        verb = Verb(
            verb="lernen",
            english="to learn",
            present_ich="lerne",
            present_du="lernst",
            present_er="lernt",
            perfect="hat gelernt",
            example="Ich lerne Deutsch.",
            word_audio="",
            example_audio="",
            image_path="",
        )

        fields = [
            "lernen",
            "to learn",
            "lerne",
            "lernst",
            "lernt",
            "hat gelernt",
            "Ich lerne Deutsch.",
            "",  # ExampleAudio - empty, should be filled
        ]

        result = verb.process_fields_for_media_generation(fields, media_generator)

        # Should generate example audio
        assert result[7] == "[sound:audio.mp3]"
        assert len(media_generator.audio_calls) == 1
        assert media_generator.audio_calls[0] == "Ich lerne Deutsch."

    def test_process_fields_existing_audio_preserved(self) -> None:
        """Test that existing audio in fields is preserved."""
        media_generator = MockDomainMediaGenerator()

        verb = Verb(
            verb="haben",
            english="to have",
            present_ich="habe",
            present_du="hast",
            present_er="hat",
            perfect="hat gehabt",
            example="Ich habe Zeit.",
            word_audio="",
            example_audio="",
            image_path="",
        )

        fields = [
            "haben",
            "to have",
            "habe",
            "hast",
            "hat",
            "hat gehabt",
            "Ich habe Zeit.",
            "[sound:existing_audio.mp3]",  # ExampleAudio - already has audio
        ]

        result = verb.process_fields_for_media_generation(fields, media_generator)

        # Should preserve existing audio
        assert result[7] == "[sound:existing_audio.mp3]"
        # Should not call media generator
        assert len(media_generator.audio_calls) == 0

    def test_process_fields_empty_example_no_audio(self) -> None:
        """Test verb processing when example sentence is empty."""
        media_generator = MockDomainMediaGenerator()

        verb = Verb(
            verb="kommen",
            english="to come",
            present_ich="komme",
            present_du="kommst",
            present_er="kommt",
            perfect="ist gekommen",
            example="",  # Empty example
            word_audio="",
            example_audio="",
            image_path="",
        )

        fields = [
            "kommen",
            "to come",
            "komme",
            "kommst",
            "kommt",
            "ist gekommen",
            "",  # Empty example
            "",  # ExampleAudio
        ]

        result = verb.process_fields_for_media_generation(fields, media_generator)

        # Should not generate audio for empty example
        assert result[7] == ""
        assert len(media_generator.audio_calls) == 0

    def test_process_fields_insufficient_fields_returns_original(self) -> None:
        """Test processing with insufficient fields returns original."""
        media_generator = MockDomainMediaGenerator()

        verb = Verb(
            verb="machen",
            english="to do",
            present_ich="mache",
            present_du="machst",
            present_er="macht",
            perfect="hat gemacht",
            example="Ich mache das.",
            word_audio="",
            example_audio="",
            image_path="",
        )

        # Only 5 fields instead of required 8
        fields = ["machen", "to do", "mache", "machst", "macht"]

        result = verb.process_fields_for_media_generation(fields, media_generator)

        # Should return original fields unchanged
        assert result == fields
        assert len(media_generator.audio_calls) == 0

    def test_process_fields_media_generation_failure(self) -> None:
        """Test verb processing when media generation fails."""
        media_generator = MockDomainMediaGenerator()
        media_generator.set_responses(audio=None)  # Simulate failure

        verb = Verb(
            verb="wohnen",
            english="to live",
            present_ich="wohne",
            present_du="wohnst",
            present_er="wohnt",
            perfect="hat gewohnt",
            example="Wir wohnen hier.",
            word_audio="",
            example_audio="",
            image_path="",
        )

        fields = [
            "wohnen",
            "to live",
            "wohne",
            "wohnst",
            "wohnt",
            "hat gewohnt",
            "Wir wohnen hier.",
            "",  # ExampleAudio
        ]

        result = verb.process_fields_for_media_generation(fields, media_generator)

        # Should leave audio field empty when generation fails
        assert result[7] == ""
        assert len(media_generator.audio_calls) == 1

    def test_get_combined_audio_text_complete_conjugation(self) -> None:
        """Test combined audio text generation with all conjugations."""
        verb = Verb(
            verb="arbeiten",
            english="to work",
            present_ich="arbeite",
            present_du="arbeitest",
            present_er="arbeitet",
            perfect="hat gearbeitet",
            example="Ich arbeite hier.",
            word_audio="",
            example_audio="",
            image_path="",
        )

        combined_text = verb.get_combined_audio_text()
        expected = (
            "arbeiten, <break strength='strong'/>Präsens, ich arbeite, "
            "du arbeitest, er sie es arbeitet, <break strength='strong'/>"
            "Perfekt, er sie es hat gearbeitet"
        )

        assert combined_text == expected

    def test_get_combined_audio_text_partial_conjugation(self) -> None:
        """Test combined audio text with missing conjugations."""
        verb = Verb(
            verb="sein",
            english="to be",
            present_ich="bin",
            present_du="",  # Missing du form
            present_er="ist",
            perfect="ist gewesen",
            example="Ich bin da.",
            word_audio="",
            example_audio="",
            image_path="",
        )

        combined_text = verb.get_combined_audio_text()
        expected = (
            "sein, <break strength='strong'/>Präsens, ich bin, er sie es ist, "
            "<break strength='strong'/>Perfekt, er sie es ist gewesen"
        )

        assert combined_text == expected

    def test_get_combined_audio_text_only_infinitive(self) -> None:
        """Test combined audio text with only infinitive."""
        verb = Verb(
            verb="verstehen",
            english="to understand",
            present_ich="",  # All conjugations empty
            present_du="",
            present_er="",
            perfect="hat verstanden",
            example="Ich verstehe das.",
            word_audio="",
            example_audio="",
            image_path="",
        )

        combined_text = verb.get_combined_audio_text()
        expected = (
            "verstehen, <break strength='strong'/>Perfekt, er sie es hat verstanden"
        )

        assert combined_text == expected

    def test_verb_field_processing_integration(self) -> None:
        """Test integration of verb field processing with realistic data."""
        media_generator = MockDomainMediaGenerator()
        media_generator.set_responses(audio="/fake/verb_audio.mp3")

        verb = Verb(
            verb="sprechen",
            english="to speak",
            present_ich="spreche",
            present_du="sprichst",
            present_er="spricht",
            perfect="hat gesprochen",
            example="Ich spreche Deutsch.",
            word_audio="",
            example_audio="",
            image_path="",
        )

        # Realistic verb fields from CSV data
        fields = [
            "sprechen",  # Verb
            "to speak",  # English
            "spreche",  # ich form
            "sprichst",  # du form
            "spricht",  # er form
            "hat gesprochen",  # perfect
            "Ich spreche Deutsch.",  # Example
            "",  # ExampleAudio (empty, to be filled)
        ]

        result = verb.process_fields_for_media_generation(fields, media_generator)

        # Verify all original fields preserved
        assert result[0] == "sprechen"
        assert result[1] == "to speak"
        assert result[2] == "spreche"
        assert result[3] == "sprichst"
        assert result[4] == "spricht"
        assert result[5] == "hat gesprochen"
        assert result[6] == "Ich spreche Deutsch."

        # Verify audio was generated for example
        assert result[7] == "[sound:verb_audio.mp3]"
        assert len(media_generator.audio_calls) == 1
        assert "Ich spreche Deutsch." in media_generator.audio_calls
