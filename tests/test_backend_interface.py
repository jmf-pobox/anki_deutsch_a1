"""Tests for DeckBackend interface compliance and consistency."""

import os
import tempfile

import pytest

from langlearn.backends import AnkiBackend, GenankiBackend
from langlearn.backends.base import CardTemplate, DeckBackend, NoteType


class TestDeckBackendInterface:
    """Test that both backends implement the DeckBackend interface consistently."""

    @pytest.fixture(params=[AnkiBackend, GenankiBackend])
    def backend_class(self, request: pytest.FixtureRequest) -> type[DeckBackend]:
        """Parametrized fixture to test both backend implementations."""
        return request.param  # type: ignore

    @pytest.fixture
    def backend(self, backend_class: type[DeckBackend]) -> DeckBackend:
        """Create a backend instance for testing."""
        return backend_class("Test Deck", "Test description")

    @pytest.fixture
    def sample_note_type(self) -> NoteType:
        """Create a sample note type for testing."""
        template = CardTemplate(
            name="Basic Card",
            front_html="{{Front}}",
            back_html="{{Back}}",
            css=".card { font-family: Arial; }",
        )
        return NoteType(
            name="Basic Note Type", fields=["Front", "Back"], templates=[template]
        )

    def test_interface_methods_exist(self, backend: DeckBackend) -> None:
        """Test that all required interface methods exist."""
        # Abstract methods that must be implemented
        assert hasattr(backend, "create_note_type")
        assert callable(backend.create_note_type)

        assert hasattr(backend, "add_note")
        assert callable(backend.add_note)

        assert hasattr(backend, "add_media_file")
        assert callable(backend.add_media_file)

        assert hasattr(backend, "export_deck")
        assert callable(backend.export_deck)

        assert hasattr(backend, "get_stats")
        assert callable(backend.get_stats)

        # Non-abstract methods
        assert hasattr(backend, "get_media_files")
        assert callable(backend.get_media_files)

    def test_create_note_type_returns_string(
        self, backend: DeckBackend, sample_note_type: NoteType
    ) -> None:
        """Test that create_note_type returns a string ID."""
        note_type_id = backend.create_note_type(sample_note_type)
        assert isinstance(note_type_id, str)
        assert len(note_type_id) > 0

    def test_add_note_returns_int(
        self, backend: DeckBackend, sample_note_type: NoteType
    ) -> None:
        """Test that add_note returns an integer note ID."""
        note_type_id = backend.create_note_type(sample_note_type)
        note_id = backend.add_note(note_type_id, ["Front content", "Back content"])
        assert isinstance(note_id, int)
        assert note_id > 0

    def test_get_stats_returns_dict(self, backend: DeckBackend) -> None:
        """Test that get_stats returns a dictionary with expected keys."""
        stats = backend.get_stats()
        assert isinstance(stats, dict)

        # All backends should provide these basic statistics
        assert "deck_name" in stats
        assert "note_types_count" in stats
        assert "notes_count" in stats
        assert "media_files_count" in stats

        assert stats["deck_name"] == "Test Deck"
        assert isinstance(stats["note_types_count"], int)
        assert isinstance(stats["notes_count"], int)
        assert isinstance(stats["media_files_count"], int)

    def test_get_media_files_returns_list(self, backend: DeckBackend) -> None:
        """Test that get_media_files returns a list."""
        media_files = backend.get_media_files()
        assert isinstance(media_files, list)
        # Initially should be empty
        assert len(media_files) == 0

    def test_export_deck_creates_file(self, backend: DeckBackend) -> None:
        """Test that export_deck creates a file."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".apkg") as temp_file:
            output_path = temp_file.name

        try:
            backend.export_deck(output_path)
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_consistent_stats_tracking(
        self, backend: DeckBackend, sample_note_type: NoteType
    ) -> None:
        """Test that both backends track statistics consistently."""
        # Initial state
        initial_stats = backend.get_stats()
        assert initial_stats["note_types_count"] == 0
        assert initial_stats["notes_count"] == 0

        # Add note type
        note_type_id = backend.create_note_type(sample_note_type)
        stats_after_note_type = backend.get_stats()
        assert stats_after_note_type["note_types_count"] == 1
        assert stats_after_note_type["notes_count"] == 0

        # Add note
        backend.add_note(note_type_id, ["Test front", "Test back"])
        stats_after_note = backend.get_stats()
        assert stats_after_note["note_types_count"] == 1
        assert stats_after_note["notes_count"] == 1

    def test_interface_polymorphism(self) -> None:
        """Test that both backends can be used polymorphically."""
        backends: list[DeckBackend] = [
            AnkiBackend("Poly Test 1"),
            GenankiBackend("Poly Test 2"),
        ]

        template = CardTemplate(
            name="Test Template", front_html="{{Field1}}", back_html="{{Field2}}"
        )
        note_type = NoteType(
            name="Test Note Type", fields=["Field1", "Field2"], templates=[template]
        )

        for backend in backends:
            # All backends should support the same operations
            note_type_id = backend.create_note_type(note_type)
            note_id = backend.add_note(note_type_id, ["Value1", "Value2"])
            stats = backend.get_stats()

            assert isinstance(note_type_id, str)
            assert isinstance(note_id, int)
            assert isinstance(stats, dict)
            assert stats["note_types_count"] == 1
            assert stats["notes_count"] == 1

    def test_error_consistency(self, backend: DeckBackend) -> None:
        """Test that both backends handle errors consistently."""
        # Test adding note with invalid note type ID
        with pytest.raises(ValueError, match="Note type ID .* not found"):
            backend.add_note("nonexistent_id", ["field1", "field2"])

        # Test adding media file that doesn't exist
        with pytest.raises(FileNotFoundError, match="Media file not found"):
            backend.add_media_file("/nonexistent/file.mp3")
