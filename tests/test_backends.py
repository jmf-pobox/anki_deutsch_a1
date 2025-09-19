"""Tests for deck backend abstraction layer."""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from langlearn.infrastructure.backends import AnkiBackend, CardTemplate, NoteType
from langlearn.languages.german.language import GermanLanguage


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

    def test_anki_backend_basic_functionality(
        self, sample_note_type: NoteType, mock_media_service: Mock
    ) -> None:
        """Test basic functionality of the official Anki backend."""
        backend = AnkiBackend(
            "Test Deck", mock_media_service, GermanLanguage(), "Test Description"
        )

        # Test note type creation
        note_type_id = backend.create_note_type(sample_note_type)
        assert note_type_id is not None
        assert isinstance(note_type_id, str)

        # Test adding notes - should raise DataProcessingError for insufficient fields
        from langlearn.exceptions import DataProcessingError

        with pytest.raises(
            DataProcessingError, match="AdjectiveRecord requires at least 4 fields"
        ):
            backend.add_note(note_type_id, ["gut", "good", "Das Wetter ist gut."])

        # Test statistics after creating note type (no notes due to validation)
        stats = backend.get_stats()
        assert stats["deck_name"] == "Test Deck"
        assert stats["note_types_count"] == 1
        assert (
            stats["notes_count"] == 0
        )  # No notes were successfully added due to validation error
        assert stats["media_files_count"] == 0

    def test_media_file_handling(
        self, temp_audio_file: str, mock_media_service: Mock
    ) -> None:
        """Test media file handling with Anki backend."""
        # Test with Anki backend
        anki_backend = AnkiBackend("Media Test", mock_media_service, GermanLanguage())
        media_file = anki_backend.add_media_file(temp_audio_file)
        # AnkiBackend wraps audio files in [sound:] format for Anki compatibility
        expected_reference = f"[sound:{os.path.basename(temp_audio_file)}]"
        assert media_file.reference == expected_reference
        assert len(anki_backend.get_media_files()) == 1

        # Cleanup
        os.unlink(temp_audio_file)

    def test_export_functionality(
        self, sample_note_type: NoteType, tmp_path: Path, mock_media_service: Mock
    ) -> None:
        """Test export functionality for Anki backend."""
        # Test Anki backend export (Phase 2: .apkg files)
        anki_backend = AnkiBackend("Export Test", mock_media_service, GermanLanguage())
        note_type_id = anki_backend.create_note_type(sample_note_type)
        # Should raise DataProcessingError for insufficient fields
        from langlearn.exceptions import DataProcessingError

        with pytest.raises(
            DataProcessingError, match="AdjectiveRecord requires at least 4 fields"
        ):
            anki_backend.add_note(note_type_id, ["test", "test", "Test sentence"])

        anki_output = tmp_path / "anki_test.apkg"
        anki_backend.export_deck(str(anki_output))

        # Check .apkg file was created (Phase 2: real Anki export)
        assert anki_output.exists()
        assert anki_output.stat().st_size > 0

        # Verify file is substantial (indicating real deck export)
        assert anki_output.stat().st_size > 1000  # >1KB

    def test_error_handling(self, mock_media_service: Mock) -> None:
        """Test error handling in Anki backend."""
        backend = AnkiBackend("Error Test", mock_media_service, GermanLanguage())

        # Test adding note with invalid note type ID
        with pytest.raises(ValueError, match="Note type ID"):
            backend.add_note("invalid_id", ["test", "test"])

        # Test adding non-existent media file
        with pytest.raises(FileNotFoundError):
            backend.add_media_file("/path/to/nonexistent/file.mp3")

    def test_backend_interface_compatibility(
        self, sample_note_type: NoteType, mock_media_service: Mock
    ) -> None:
        """Test that Anki backend implements the interface correctly."""
        backend = AnkiBackend("Interface Test", mock_media_service, GermanLanguage())

        # Test interface methods exist and work
        assert hasattr(backend, "create_note_type")
        assert hasattr(backend, "add_note")
        assert hasattr(backend, "add_media_file")
        assert hasattr(backend, "export_deck")
        assert hasattr(backend, "get_media_files")

        # Test basic workflow
        note_type_id = backend.create_note_type(sample_note_type)
        # Should raise DataProcessingError for insufficient fields
        from langlearn.exceptions import DataProcessingError

        with pytest.raises(
            DataProcessingError, match="AdjectiveRecord requires at least 4 fields"
        ):
            backend.add_note(note_type_id, ["word", "translation", "example"])
        media_files = backend.get_media_files()
        assert len(media_files) == 0  # No media files added yet
