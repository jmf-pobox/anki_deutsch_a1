"""Tests for media integration in AnkiBackend."""

import hashlib
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from langlearn.backends import AnkiBackend, CardTemplate, NoteType


class TestMediaIntegration:
    """Test media integration functionality in AnkiBackend."""

    @pytest.fixture
    def backend(self) -> AnkiBackend:
        """Create an AnkiBackend instance for testing."""
        return AnkiBackend("Media Test Deck", "Testing media integration")

    @pytest.fixture
    def adjective_note_type(self) -> NoteType:
        """Create a German adjective note type for testing."""
        template = CardTemplate(
            name="German Adjective with Media",
            front_html="{{Word}} {{#Image}}{{Image}}{{/Image}}",
            back_html="{{Word}} {{#Image}}{{Image}}{{/Image}}<hr>{{English}}<br>{{Example}}<br>{{Comparative}}, {{Superlative}}",
            css=".card { font-family: Arial; }",
        )

        return NoteType(
            name="German Adjective with Media",
            fields=[
                "Word",
                "English",
                "Example",
                "Comparative",
                "Superlative",
                "Image",
                "WordAudio",
                "ExampleAudio",
            ],
            templates=[template],
        )

    @pytest.fixture
    def temp_audio_file(self) -> str:
        """Create a temporary audio file for testing."""
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(b"fake mp3 content")
            temp_path = f.name
        yield temp_path
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    @pytest.fixture
    def temp_image_file(self) -> str:
        """Create a temporary image file for testing."""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(b"fake jpeg content")
            temp_path = f.name
        yield temp_path
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_generate_or_get_audio_existing_file(self, backend: AnkiBackend) -> None:
        """Test _generate_or_get_audio returns existing file path when file exists."""
        text = "test"
        expected_filename = f"{hashlib.md5(text.encode()).hexdigest()}.mp3"

        # Mock file exists
        with patch.object(Path, "exists", return_value=True):
            result = backend._generate_or_get_audio(text)

            assert result is not None
            assert result.endswith(expected_filename)
            assert backend._media_generation_stats["audio_reused"] == 1
            assert backend._media_generation_stats["audio_generated"] == 0

    def test_generate_or_get_audio_new_file(self, backend: AnkiBackend) -> None:
        """Test _generate_or_get_audio generates new audio when file doesn't exist."""
        text = "neues_wort"
        fake_generated_path = "/fake/path/audio.mp3"

        # Mock file doesn't exist and audio service generates new file
        with (
            patch.object(Path, "exists", return_value=False),
            patch.object(
                backend._audio_service,
                "generate_audio",
                return_value=fake_generated_path,
            ),
        ):
            result = backend._generate_or_get_audio(text)

            assert result == fake_generated_path
            assert backend._media_generation_stats["audio_generated"] == 1
            assert backend._media_generation_stats["audio_reused"] == 0

    def test_generate_or_get_audio_generation_failure(
        self, backend: AnkiBackend
    ) -> None:
        """Test _generate_or_get_audio handles generation failure gracefully."""
        text = "test"

        # Mock file doesn't exist and audio service fails
        with (
            patch.object(Path, "exists", return_value=False),
            patch.object(backend._audio_service, "generate_audio", return_value=None),
        ):
            result = backend._generate_or_get_audio(text)

            assert result is None
            assert backend._media_generation_stats["generation_errors"] == 1

    def test_generate_or_get_image_existing_file(self, backend: AnkiBackend) -> None:
        """Test _generate_or_get_image returns existing file path when file exists."""
        word = "gut"

        # Mock file exists
        with patch.object(Path, "exists", return_value=True):
            result = backend._generate_or_get_image(word)

            assert result is not None
            assert result.endswith("gut.jpg")
            assert backend._media_generation_stats["images_reused"] == 1
            assert backend._media_generation_stats["images_downloaded"] == 0

    def test_generate_or_get_image_new_download(self, backend: AnkiBackend) -> None:
        """Test _generate_or_get_image downloads new image when file doesn't exist."""
        word = "fantastisch"

        # Mock file doesn't exist and pexels service downloads successfully
        with (
            patch.object(Path, "exists", return_value=False),
            patch.object(backend._pexels_service, "download_image", return_value=True),
        ):
            result = backend._generate_or_get_image(word)

            assert result is not None
            assert result.endswith("fantastisch.jpg")
            assert backend._media_generation_stats["images_downloaded"] == 1
            assert backend._media_generation_stats["images_reused"] == 0

    def test_generate_or_get_image_download_failure(self, backend: AnkiBackend) -> None:
        """Test _generate_or_get_image handles download failure gracefully."""
        word = "test"

        # Mock file doesn't exist and pexels service fails
        with (
            patch.object(Path, "exists", return_value=False),
            patch.object(backend._pexels_service, "download_image", return_value=False),
        ):
            result = backend._generate_or_get_image(word)

            assert result is None
            assert backend._media_generation_stats["generation_errors"] == 1

    def test_is_concrete_noun_concrete_words(self, backend: AnkiBackend) -> None:
        """Test _is_concrete_noun correctly identifies concrete nouns."""
        concrete_nouns = ["Hund", "Haus", "Auto", "Tisch", "Baum"]

        for noun in concrete_nouns:
            assert backend._is_concrete_noun(noun) is True

    def test_is_concrete_noun_abstract_words(self, backend: AnkiBackend) -> None:
        """Test _is_concrete_noun correctly identifies abstract nouns."""
        abstract_nouns = [
            "Freiheit",  # -heit
            "Schnelligkeit",  # -keit
            "Bildung",  # -ung
            "Diskussion",  # -ion
            "Rhythmus",  # -mus
            "Universität",  # -tät
        ]

        for noun in abstract_nouns:
            assert backend._is_concrete_noun(noun) is False

    def test_process_fields_with_media_adjective(self, backend: AnkiBackend) -> None:
        """Test _process_fields_with_media processes adjective cards correctly."""
        note_type_name = "German Adjective with Media"
        fields = [
            "schön",
            "beautiful",
            "Das Haus ist schön.",
            "schöner",
            "am schönsten",
            "",
            "",
            "",
        ]

        # Mock media generation - AnkiBackend now generates combined audio for adjective forms
        fake_combined_audio_path = "/fake/combined_audio.mp3"
        fake_example_audio_path = "/fake/example_audio.mp3"
        fake_image_path = "/fake/image.jpg"

        fake_media_file_combined = Mock()
        fake_media_file_combined.reference = "[sound:combined_audio.mp3]"
        fake_media_file_example = Mock()
        fake_media_file_example.reference = "[sound:example_audio.mp3]"
        fake_media_file_image = Mock()
        fake_media_file_image.reference = "image.jpg"

        with (
            patch.object(
                backend,
                "_generate_or_get_audio",
                side_effect=[fake_combined_audio_path, fake_example_audio_path],
            ),
            patch.object(
                backend, "_generate_or_get_image", return_value=fake_image_path
            ),
            patch.object(
                backend,
                "add_media_file",
                side_effect=[
                    fake_media_file_combined,
                    fake_media_file_example,
                    fake_media_file_image,
                ],
            ),
        ):
            result = backend._process_fields_with_media(note_type_name, fields)

            # Should add combined audio to WordAudio field (index 6)
            word_audio = result[6]
            assert word_audio == "[sound:combined_audio.mp3]"

            # Should add example audio to ExampleAudio field (index 7)
            assert result[7] == "[sound:example_audio.mp3]"

            # Should add image to Image field (index 5)
            assert '<img src="image.jpg"' in result[5]

            # Verify that audio generation was called with the right parameters
            backend._generate_or_get_audio.assert_any_call("schön, schöner, am schönsten")
            backend._generate_or_get_audio.assert_any_call("Das Haus ist schön.")

    def test_process_fields_with_media_noun(self, backend: AnkiBackend) -> None:
        """Test _process_fields_with_media processes noun cards correctly."""
        note_type_name = "German Noun"  # Must match exact note type in AnkiBackend
        fields = [
            "Katze",
            "die",
            "cat",
            "die Katzen",
            "Die Katze schläft.",
            "Tier",
            "",
            "",
            "",
        ]  # Added fields for Image, WordAudio, ExampleAudio

        fake_audio_path = "/fake/audio.mp3"
        fake_media_file = Mock()
        fake_media_file.reference = "[sound:katze.mp3]"

        with (
            patch.object(
                backend, "_generate_or_get_audio", side_effect=[fake_audio_path, fake_audio_path]
            ),
            patch.object(backend, "_generate_or_get_image", return_value=None),
            patch.object(backend, "add_media_file", side_effect=[fake_media_file, fake_media_file]),
        ):
            result = backend._process_fields_with_media(note_type_name, fields)

            # Should add combined noun audio to WordAudio field (index 7)
            assert result[7] == "[sound:katze.mp3]"

            # Should add example audio to ExampleAudio field (index 8)
            assert result[8] == "[sound:katze.mp3]"

            # Verify that audio generation was called with the right parameters
            backend._generate_or_get_audio.assert_any_call("die Katze, die Katzen")
            backend._generate_or_get_audio.assert_any_call("Die Katze schläft.")

    def test_process_fields_with_media_verb(self, backend: AnkiBackend) -> None:
        """Test _process_fields_with_media processes verb cards correctly."""
        note_type_name = "German Verb"
        fields = [
            "laufen",
            "to run",
            "ich laufe",
            "du läufst",
            "er läuft",
            "ist gelaufen",
            "Ich laufe schnell.",
            "",
        ]

        fake_audio_path = "/fake/example_audio.mp3"
        fake_media_file = Mock()
        fake_media_file.reference = "[sound:example.mp3]"

        with (
            patch.object(
                backend, "_generate_or_get_audio", return_value=fake_audio_path
            ),
            patch.object(backend, "add_media_file", return_value=fake_media_file),
        ):
            result = backend._process_fields_with_media(note_type_name, fields)

            # Should add audio to example audio field (index 7)
            assert result[7] == "[sound:example.mp3]"

    def test_process_fields_with_media_preposition(self, backend: AnkiBackend) -> None:
        """Test _process_fields_with_media processes preposition cards correctly."""
        note_type_name = "German Preposition"
        fields = [
            "mit",
            "Dativ",
            "with",
            "Ich gehe mit dir.",
            "Er kommt mit uns.",
            "",
            "",
        ]

        fake_audio_path = "/fake/audio.mp3"
        fake_media_file = Mock()
        fake_media_file.reference = "[sound:example.mp3]"

        with (
            patch.object(
                backend, "_generate_or_get_audio", return_value=fake_audio_path
            ),
            patch.object(backend, "add_media_file", return_value=fake_media_file),
        ):
            result = backend._process_fields_with_media(note_type_name, fields)

            # Should add audio to both example audio fields (indices 5 and 6)
            assert result[5] == "[sound:example.mp3]"
            assert result[6] == "[sound:example.mp3]"

    def test_process_fields_with_media_phrase(self, backend: AnkiBackend) -> None:
        """Test _process_fields_with_media processes phrase cards correctly."""
        note_type_name = "German Phrase"
        fields = [
            "Wie geht's?",
            "How are you?",
            "Informal greeting",
            "Hallo, Tschüss",
            "",
        ]

        fake_audio_path = "/fake/phrase_audio.mp3"
        fake_media_file = Mock()
        fake_media_file.reference = "[sound:phrase.mp3]"

        with (
            patch.object(
                backend, "_generate_or_get_audio", return_value=fake_audio_path
            ),
            patch.object(backend, "add_media_file", return_value=fake_media_file),
        ):
            result = backend._process_fields_with_media(note_type_name, fields)

            # Should add audio to phrase audio field (index 4)
            assert result[4] == "[sound:phrase.mp3]"

    def test_process_fields_with_media_error_handling(
        self, backend: AnkiBackend
    ) -> None:
        """Test _process_fields_with_media handles errors gracefully."""
        note_type_name = "German Adjective with Media"
        fields = ["test", "test", "test", "test", ""]

        # Mock media generation to raise exception
        with patch.object(
            backend, "_generate_or_get_audio", side_effect=Exception("Test error")
        ):
            result = backend._process_fields_with_media(note_type_name, fields)

            # Should return original fields when processing fails
            assert result == fields

    def test_add_note_with_media_integration(
        self, backend: AnkiBackend, adjective_note_type: NoteType
    ) -> None:
        """Test that add_note integrates with media processing."""
        note_type_id = backend.create_note_type(adjective_note_type)
        fields = ["wunderbar", "wonderful", "Das ist wunderbar!", "wunderbarer", ""]

        # Mock media processing to return modified fields
        expected_processed_fields = fields.copy()
        expected_processed_fields[2] = (
            "Das ist wunderbar! [sound:audio.mp3]"  # Modified example
        )
        expected_processed_fields[4] = '<img src="image.jpg">'  # Modified image field

        with patch.object(
            backend,
            "_process_fields_with_media",
            return_value=expected_processed_fields,
        ):
            note_id = backend.add_note(note_type_id, fields)

            assert note_id is not None
            # Verify _process_fields_with_media was called with correct note type name
            backend._process_fields_with_media.assert_called_once_with(
                "German Adjective with Media", fields
            )

    def test_media_generation_statistics_tracking(self, backend: AnkiBackend) -> None:
        """Test that media generation statistics are tracked correctly."""
        initial_stats = backend._media_generation_stats.copy()

        # Test audio generation tracking
        with (
            patch.object(Path, "exists", return_value=False),
            patch.object(
                backend._audio_service, "generate_audio", return_value="/fake/path.mp3"
            ),
        ):
            backend._generate_or_get_audio("test")

        assert (
            backend._media_generation_stats["audio_generated"]
            == initial_stats["audio_generated"] + 1
        )

        # Test audio reuse tracking
        with patch.object(Path, "exists", return_value=True):
            backend._generate_or_get_audio("test2")

        assert (
            backend._media_generation_stats["audio_reused"]
            == initial_stats["audio_reused"] + 1
        )

        # Test image download tracking
        with (
            patch.object(Path, "exists", return_value=False),
            patch.object(backend._pexels_service, "download_image", return_value=True),
        ):
            backend._generate_or_get_image("test")

        assert (
            backend._media_generation_stats["images_downloaded"]
            == initial_stats["images_downloaded"] + 1
        )

        # Test error tracking
        with (
            patch.object(Path, "exists", return_value=False),
            patch.object(backend._audio_service, "generate_audio", return_value=None),
        ):
            backend._generate_or_get_audio("test3")

        assert (
            backend._media_generation_stats["generation_errors"]
            == initial_stats["generation_errors"] + 1
        )

    def test_media_statistics_in_get_stats(self, backend: AnkiBackend) -> None:
        """Test that media generation statistics appear in get_stats output."""
        # Simulate some media generation
        backend._media_generation_stats["audio_generated"] = 2
        backend._media_generation_stats["images_downloaded"] = 1
        backend._media_generation_stats["audio_reused"] = 3
        backend._media_generation_stats["images_reused"] = 2

        stats = backend.get_stats()

        assert "media_generation_stats" in stats
        media_gen_stats = stats["media_generation_stats"]

        assert media_gen_stats["audio_generated"] == 2
        assert media_gen_stats["images_downloaded"] == 1
        assert media_gen_stats["audio_reused"] == 3
        assert media_gen_stats["images_reused"] == 2
        assert media_gen_stats["total_media_generated"] == 3  # 2 + 1
        assert media_gen_stats["total_media_reused"] == 5  # 3 + 2

    def test_field_processing_unknown_note_type(self, backend: AnkiBackend) -> None:
        """Test _process_fields_with_media with unknown note type does nothing."""
        note_type_name = "Unknown Note Type"
        fields = ["field1", "field2", "field3"]

        result = backend._process_fields_with_media(note_type_name, fields)

        # Should return unchanged fields
        assert result == fields

    def test_field_processing_insufficient_fields(self, backend: AnkiBackend) -> None:
        """Test _process_fields_with_media with insufficient fields does nothing."""
        note_type_name = "German Adjective with Media"
        fields = [
            "word",
            "english",
            "example",
            "comparative",
            "superlative",
        ]  # Only 5 fields, need 8+

        result = backend._process_fields_with_media(note_type_name, fields)

        # Should return unchanged fields
        assert result == fields

    def test_media_path_construction(self, backend: AnkiBackend) -> None:
        """Test that media paths are constructed correctly."""
        # Test audio path construction
        text = "Hund"
        expected_hash = hashlib.md5(text.encode()).hexdigest()

        with patch.object(Path, "exists", return_value=True):
            result = backend._generate_or_get_audio(text)

        assert result is not None
        assert expected_hash in result
        assert result.endswith(".mp3")

        # Test image path construction
        word = "schön"
        with patch.object(Path, "exists", return_value=True):
            result = backend._generate_or_get_image(word)

        assert result is not None
        assert "schön.jpg" in result

    def test_enhanced_adjective_audio_generation(self, backend: AnkiBackend) -> None:
        """Test that all three adjective forms (base, comparative, superlative) generate audio."""
        note_type_name = "German Adjective with Media"
        fields = [
            "gut",
            "good",
            "Das Wetter ist gut.",
            "besser",
            "am besten",
            "",
            "",
            "",
        ]

        # Mock successful audio generation for combined forms and example
        fake_combined_path = "/fake/combined.mp3"
        fake_example_path = "/fake/example.mp3"
        
        fake_combined_media = Mock()
        fake_combined_media.reference = "[sound:combined.mp3]"
        fake_example_media = Mock()
        fake_example_media.reference = "[sound:example.mp3]"

        # Mock image generation
        fake_image_file = Mock()
        fake_image_file.reference = "gut.jpg"

        with (
            patch.object(backend, "_generate_or_get_audio", side_effect=[fake_combined_path, fake_example_path]),
            patch.object(
                backend, "_generate_or_get_image", return_value="/fake/gut.jpg"
            ),
            patch.object(
                backend,
                "add_media_file",
                side_effect=[fake_combined_media, fake_example_media, fake_image_file],
            ),
        ):
            result = backend._process_fields_with_media(note_type_name, fields)

            # Verify combined adjective audio and example audio were processed
            backend._generate_or_get_audio.assert_any_call(
                "gut, besser, am besten"
            )  # Combined forms
            backend._generate_or_get_audio.assert_any_call(
                "Das Wetter ist gut."
            )  # Example

            # Verify WordAudio field contains combined audio reference
            word_audio = result[6]
            assert word_audio == "[sound:combined.mp3]"  # Combined audio

            # Verify ExampleAudio field has example audio
            assert result[7] == "[sound:example.mp3]"

            # Verify that audio generation was called 2 times (combined forms, example)
            assert backend._generate_or_get_audio.call_count == 2

    def test_adjective_with_missing_forms(self, backend: AnkiBackend) -> None:
        """Test adjective processing when comparative or superlative are missing."""
        note_type_name = "German Adjective with Media"
        # Missing superlative form
        fields = [
            "schnell",
            "fast",
            "Das Auto ist schnell.",
            "schneller",
            "",
            "",
            "",
            "",
        ]

        fake_combined_path = "/fake/combined.mp3"
        fake_example_path = "/fake/example.mp3"
        
        fake_combined_media = Mock()
        fake_combined_media.reference = "[sound:combined.mp3]"
        fake_example_media = Mock()
        fake_example_media.reference = "[sound:example.mp3]"

        with (
            patch.object(backend, "_generate_or_get_audio", side_effect=[fake_combined_path, fake_example_path]),
            patch.object(backend, "_generate_or_get_image", return_value=None),
            patch.object(backend, "add_media_file", side_effect=[fake_combined_media, fake_example_media]),
        ):
            result = backend._process_fields_with_media(note_type_name, fields)

            # Should call audio generation for combined forms and example (2 calls total)
            assert backend._generate_or_get_audio.call_count == 2
            backend._generate_or_get_audio.assert_any_call(
                "schnell, schneller"
            )  # Combined available forms
            backend._generate_or_get_audio.assert_any_call(
                "Das Auto ist schnell."
            )  # Example

            # WordAudio should have combined audio
            word_audio = result[6]
            assert word_audio == "[sound:combined.mp3]"  # Combined audio
