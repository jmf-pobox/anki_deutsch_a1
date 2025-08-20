"""Tests for DeckBackend interface compliance and consistency."""

import os
import tempfile
from unittest.mock import Mock, patch

import pytest

from langlearn.backends import AnkiBackend
from langlearn.backends.base import CardTemplate, DeckBackend, NoteType


class TestDeckBackendInterface:
    """Test that AnkiBackend implements the DeckBackend interface correctly."""

    @pytest.fixture
    def backend(self) -> DeckBackend:
        """Create a backend instance for testing."""
        # Mock external services for unit testing
        with (
            patch("langlearn.services.audio.boto3.client") as mock_boto_client,
            patch("langlearn.services.pexels_service.requests.get") as mock_requests,
            patch("keyring.get_password") as mock_keyring,
        ):
            mock_boto_client.return_value = Mock()
            mock_requests.return_value = Mock()
            mock_keyring.return_value = "mock-api-key"  # Fallback for keyring calls

            # Set environment variables for services that check them first
            original_env = {}
            test_env_vars = {
                "PEXELS_API_KEY": "mock-pexels-key",
                "ANTHROPIC_API_KEY": "mock-anthropic-key",
                "AWS_DEFAULT_REGION": "us-east-1",
                "AWS_ACCESS_KEY_ID": "mock-aws-key",
                "AWS_SECRET_ACCESS_KEY": "mock-aws-secret",
            }

            # Store original values and set test values
            for key, value in test_env_vars.items():
                original_env[key] = os.environ.get(key)
                os.environ[key] = value

            try:
                return AnkiBackend("Test Deck", "Test description")
            finally:
                # Restore original environment
                for key, original_value in original_env.items():
                    if original_value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = original_value

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
        """Test that AnkiBackend tracks statistics correctly."""
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

    def test_interface_operations(self) -> None:
        """Test that AnkiBackend supports all interface operations."""
        # Mock AWS services to avoid region configuration issues in CI
        with (
            patch("langlearn.services.audio.boto3.client") as mock_boto_client,
            patch("langlearn.services.pexels_service.requests.get") as mock_requests,
        ):
            mock_boto_client.return_value = Mock()
            mock_requests.return_value = Mock()
            backend = AnkiBackend("Interface Test")

            template = CardTemplate(
                name="Test Template", front_html="{{Field1}}", back_html="{{Field2}}"
            )
            note_type = NoteType(
                name="Test Note Type", fields=["Field1", "Field2"], templates=[template]
            )

            # Backend should support all operations
            note_type_id = backend.create_note_type(note_type)
            note_id = backend.add_note(note_type_id, ["Value1", "Value2"])
            stats = backend.get_stats()

            assert isinstance(note_type_id, str)
            assert isinstance(note_id, int)
            assert isinstance(stats, dict)
            assert stats["note_types_count"] == 1
            assert stats["notes_count"] == 1

    def test_error_handling(self, backend: DeckBackend) -> None:
        """Test that AnkiBackend handles errors correctly."""
        # Test adding note with invalid note type ID
        with pytest.raises(ValueError, match="Note type ID .* not found"):
            backend.add_note("nonexistent_id", ["field1", "field2"])

        # Test adding media file that doesn't exist
        with pytest.raises(FileNotFoundError, match="Media file not found"):
            backend.add_media_file("/nonexistent/file.mp3")
