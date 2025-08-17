"""Tests for deck backend abstraction layer."""

import os
import tempfile
from pathlib import Path

import pytest

from langlearn.backends import AnkiBackend, CardTemplate, GenankiBackend, NoteType


class TestBackendAbstraction:
    """Test the backend abstraction layer with both implementations."""

    @pytest.fixture
    def sample_note_type(self) -> NoteType:
        """Create a sample note type for testing."""
        template = CardTemplate(
            name="Basic",
            front_html="{{Word}}",
            back_html="{{Word}}<hr>{{English}}",
            css=".card { font-family: Arial; }",
        )

        return NoteType(
            name="German Adjective",
            fields=["Word", "English", "Example"],
            templates=[template],
        )

    @pytest.fixture
    def temp_audio_file(self) -> str:
        """Create a temporary audio file for testing."""
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(b"fake audio content")
            return f.name

    def test_genanki_backend_basic_functionality(
        self, sample_note_type: NoteType
    ) -> None:
        """Test basic functionality of the genanki backend."""
        backend = GenankiBackend("Test Deck", "Test Description")

        # Test note type creation
        note_type_id = backend.create_note_type(sample_note_type)
        assert note_type_id is not None
        assert isinstance(note_type_id, str)

        # Test adding notes
        backend.add_note(note_type_id, ["gut", "good", "Das Wetter ist gut."])
        backend.add_note(note_type_id, ["schlecht", "bad", "Das Wetter ist schlecht."])

        # Test deck has correct name
        assert backend.deck_name == "Test Deck"
        assert backend.description == "Test Description"

    def test_anki_backend_basic_functionality(self, sample_note_type: NoteType) -> None:
        """Test basic functionality of the official Anki backend."""
        backend = AnkiBackend("Test Deck", "Test Description")

        # Test note type creation
        note_type_id = backend.create_note_type(sample_note_type)
        assert note_type_id is not None
        assert isinstance(note_type_id, str)

        # Test adding notes
        backend.add_note(note_type_id, ["gut", "good", "Das Wetter ist gut."])
        backend.add_note(note_type_id, ["schlecht", "bad", "Das Wetter ist schlecht."])

        # Test statistics
        stats = backend.get_stats()
        assert stats["deck_name"] == "Test Deck"
        assert stats["note_types_count"] == 1
        assert stats["notes_count"] == 2
        # Media files count is 0 because the note type has insufficient fields (3) for media generation
        # which requires at least 5 fields for adjective cards
        assert stats["media_files_count"] == 0

    def test_media_file_handling(self, temp_audio_file: str) -> None:
        """Test media file handling in both backends."""
        # Test with genanki backend
        genanki_backend = GenankiBackend("Media Test")
        media_file = genanki_backend.add_media_file(temp_audio_file)
        assert media_file.reference == os.path.basename(temp_audio_file)
        assert len(genanki_backend.get_media_files()) == 1

        # Test with Anki backend
        anki_backend = AnkiBackend("Media Test")
        media_file = anki_backend.add_media_file(temp_audio_file)
        # AnkiBackend wraps audio files in [sound:] format for Anki compatibility
        expected_reference = f"[sound:{os.path.basename(temp_audio_file)}]"
        assert media_file.reference == expected_reference
        assert len(anki_backend.get_media_files()) == 1

        # Cleanup
        os.unlink(temp_audio_file)

    def test_export_functionality(
        self, sample_note_type: NoteType, tmp_path: Path
    ) -> None:
        """Test export functionality for both backends."""
        # Test genanki backend export
        genanki_backend = GenankiBackend("Export Test")
        note_type_id = genanki_backend.create_note_type(sample_note_type)
        genanki_backend.add_note(note_type_id, ["test", "test", "Test sentence"])

        genanki_output = tmp_path / "genanki_test.apkg"
        genanki_backend.export_deck(str(genanki_output))
        assert genanki_output.exists()

        # Test Anki backend export (Phase 2: .apkg files)
        anki_backend = AnkiBackend("Export Test")
        note_type_id = anki_backend.create_note_type(sample_note_type)
        anki_backend.add_note(note_type_id, ["test", "test", "Test sentence"])

        anki_output = tmp_path / "anki_test.apkg"
        anki_backend.export_deck(str(anki_output))

        # Check .apkg file was created (Phase 2: real Anki export)
        assert anki_output.exists()
        assert anki_output.stat().st_size > 0

        # Verify both files are substantial (indicating real deck exports)
        assert genanki_output.stat().st_size > 1000  # >1KB
        assert anki_output.stat().st_size > 1000  # >1KB

    def test_error_handling(self) -> None:
        """Test error handling in both backends."""
        backend = GenankiBackend("Error Test")

        # Test adding note with invalid note type ID
        with pytest.raises(ValueError, match="Note type ID"):
            backend.add_note("invalid_id", ["test", "test"])

        # Test adding non-existent media file
        with pytest.raises(FileNotFoundError):
            backend.add_media_file("/path/to/nonexistent/file.mp3")

    def test_backend_interface_compatibility(self, sample_note_type: NoteType) -> None:
        """Test that both backends implement the same interface correctly."""
        backends = [
            GenankiBackend("Interface Test"),
            AnkiBackend("Interface Test"),
        ]

        for backend in backends:
            # Test interface methods exist and work
            assert hasattr(backend, "create_note_type")
            assert hasattr(backend, "add_note")
            assert hasattr(backend, "add_media_file")
            assert hasattr(backend, "export_deck")
            assert hasattr(backend, "get_media_files")

            # Test basic workflow
            note_type_id = backend.create_note_type(sample_note_type)
            backend.add_note(note_type_id, ["word", "translation", "example"])
            media_files = backend.get_media_files()
            assert len(media_files) == 0  # No media files added yet
