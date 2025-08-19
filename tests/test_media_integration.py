"""Tests for media integration in AnkiBackend."""

import hashlib
import os
import tempfile
from collections.abc import Generator
from pathlib import Path
from unittest.mock import patch

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
            back_html=(
                "{{Word}} {{#Image}}{{Image}}{{/Image}}<hr>{{English}}<br>"
                "{{Example}}<br>{{Comparative}}, {{Superlative}}"
            ),
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
    def temp_audio_file(self) -> Generator[str, None, None]:
        """Create a temporary audio file for testing."""
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(b"fake mp3 content")
            temp_path = f.name
        yield temp_path
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    @pytest.fixture
    def temp_image_file(self) -> Generator[str, None, None]:
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

    # Legacy adjective test removed - replaced by test_backend_integration.py
    # The old test_process_fields_with_media_adjective tested infrastructure
    # directly calling _generate_or_get_audio, but now we delegate to domain models

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

        fake_audio_path = "/fake/katze.mp3"

        # Mock the MediaService that DomainMediaGenerator uses
        with (
            patch.object(
                backend._domain_media_generator._media_service,
                "generate_audio",
                side_effect=[fake_audio_path, fake_audio_path],
            ),
            patch.object(
                backend._domain_media_generator._media_service,
                "generate_image",
                return_value=None,
            ),
        ):
            result = backend._process_fields_with_media(note_type_name, fields)

            # Should add combined noun audio to WordAudio field (index 7)
            assert result[7] == "[sound:katze.mp3]"

            # Should add example audio to ExampleAudio field (index 8)
            assert result[8] == "[sound:katze.mp3]"

            # Verify that audio generation was called with the right parameters
            media_service = backend._domain_media_generator._media_service
            media_service.generate_audio.assert_any_call("die Katze, die Katzen")  # type: ignore[attr-defined]
            media_service.generate_audio.assert_any_call("Die Katze schläft.")  # type: ignore[attr-defined]

    def test_process_fields_with_media_error_handling(
        self, backend: AnkiBackend
    ) -> None:
        """Test _process_fields_with_media handles errors gracefully."""
        note_type_name = "German Adjective with Media"
        fields = ["test", "test", "test", "test", ""]

        # Mock both audio and image generation to raise exceptions
        with (
            patch.object(
                backend, "_generate_or_get_audio", side_effect=Exception("Test error")
            ),
            patch.object(
                backend, "_generate_or_get_image", side_effect=Exception("Test error")
            ),
        ):
            result = backend._process_fields_with_media(note_type_name, fields)

            # Should extend fields but fail gracefully on media generation
            # The extended fields may not match original since fields get extended
            assert len(result) >= 8  # Fields get extended to minimum required length
            assert result[0] == "test"  # Original field values preserved
            assert result[1] == "test"
            assert result[2] == "test"
            assert result[3] == "test"
            assert result[4] == ""  # Original empty field

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
            # Verify _process_fields_with_media was called with correct note type ID
            backend._process_fields_with_media.assert_called_once_with(  # type: ignore[attr-defined]  # Mock boundary
                note_type_id, fields
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
        """Test _process_fields_with_media with insufficient fields extends them."""
        note_type_name = "German Adjective with Media"
        fields = [
            "word",
            "english",
            "example",
            "comparative",
            "superlative",
        ]  # Only 5 fields, will be extended to 8+

        result = backend._process_fields_with_media(note_type_name, fields)

        # Should extend fields and process media
        assert len(result) >= 8  # Should be extended
        assert result[0] == "word"  # Original fields preserved
        assert result[1] == "english"
        assert result[2] == "example"
        assert result[3] == "comparative"
        assert result[4] == "superlative"
        # Fields 5+ may have media content

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

    # Legacy adjective tests removed - replaced by comprehensive test coverage in:
    # - test_adjective_field_processing.py: Domain model field processing tests
    # - test_backend_integration.py: Backend delegation tests
    # - test_field_processor_interface.py: Interface and protocol tests
    #
    # The old tests were testing infrastructure directly calling _generate_or_get_audio
    # but the new architecture delegates to domain models via FieldProcessor interface
