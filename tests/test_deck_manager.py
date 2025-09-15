"""Tests for DeckManager functionality."""

from unittest.mock import Mock

import pytest

from langlearn.core.backends.base import CardTemplate, DeckBackend, NoteType
from langlearn.managers.deck_manager import DeckManager


class TestDeckManager:
    """Test DeckManager orchestration functionality."""

    @pytest.fixture
    def mock_backend(self) -> Mock:
        """Create a mock backend for testing."""
        backend = Mock(spec=DeckBackend)
        backend.deck_name = "Test Deck"
        backend.create_note_type.return_value = "note_type_1"
        backend.add_note.return_value = 42
        backend.get_stats.return_value = {
            "deck_name": "Test Deck",
            "note_types_count": 1,
            "notes_count": 5,
            "media_files_count": 3,
        }
        return backend

    @pytest.fixture
    def deck_manager(self, mock_backend: Mock) -> DeckManager:
        """Create a DeckManager instance for testing."""
        return DeckManager(mock_backend)

    @pytest.fixture
    def sample_note_type(self) -> NoteType:
        """Create a sample note type for testing."""
        template = CardTemplate(
            name="Test Template",
            front_html="{{Front}}",
            back_html="{{Back}}",
        )
        return NoteType(
            name="Test Note Type",
            fields=["Front", "Back"],
            templates=[template],
        )

    def test_initialization(self, mock_backend: Mock) -> None:
        """Test DeckManager initialization."""
        manager = DeckManager(mock_backend)

        assert manager.backend is mock_backend
        assert manager.deck_name == "Test Deck"
        assert manager.get_subdeck_names() == []
        assert manager.get_current_deck_name() == "Test Deck"

    def test_subdeck_management(self, deck_manager: DeckManager) -> None:
        """Test subdeck creation and management."""
        # Initially no subdecks
        assert deck_manager.get_subdeck_names() == []
        assert deck_manager.get_full_subdeck_names() == []
        assert deck_manager.get_current_deck_name() == "Test Deck"

        # Set first subdeck
        deck_manager.set_current_subdeck("Adjectives")
        assert deck_manager.get_current_deck_name() == "Test Deck::Adjectives"
        assert deck_manager.get_subdeck_names() == ["Adjectives"]
        assert deck_manager.get_full_subdeck_names() == ["Test Deck::Adjectives"]

        # Set second subdeck
        deck_manager.set_current_subdeck("Nouns")
        assert deck_manager.get_current_deck_name() == "Test Deck::Nouns"
        assert set(deck_manager.get_subdeck_names()) == {"Adjectives", "Nouns"}
        assert set(deck_manager.get_full_subdeck_names()) == {
            "Test Deck::Adjectives",
            "Test Deck::Nouns",
        }

        # Reset to main deck
        deck_manager.reset_to_main_deck()
        assert deck_manager.get_current_deck_name() == "Test Deck"
        # Subdecks should still be tracked
        assert len(deck_manager.get_subdeck_names()) == 2

    def test_create_note_type_delegation(
        self, deck_manager: DeckManager, mock_backend: Mock, sample_note_type: NoteType
    ) -> None:
        """Test that create_note_type is properly delegated."""
        note_type_id = deck_manager.create_note_type(sample_note_type)

        assert note_type_id == "note_type_1"
        mock_backend.create_note_type.assert_called_once_with(sample_note_type)

    def test_add_note_without_subdeck(
        self, deck_manager: DeckManager, mock_backend: Mock
    ) -> None:
        """Test adding note without subdeck context."""
        note_id = deck_manager.add_note("note_type_1", ["Front", "Back"], ["tag1"])

        assert note_id == 42
        mock_backend.add_note.assert_called_once_with(
            "note_type_1", ["Front", "Back"], ["tag1"]
        )

    def test_add_note_with_subdeck(
        self, deck_manager: DeckManager, mock_backend: Mock
    ) -> None:
        """Test adding note with subdeck context."""
        deck_manager.set_current_subdeck("Adjectives")
        note_id = deck_manager.add_note("note_type_1", ["Front", "Back"], ["tag1"])

        assert note_id == 42
        # Should add subdeck tag
        mock_backend.add_note.assert_called_once_with(
            "note_type_1", ["Front", "Back"], ["tag1", "subdeck:Adjectives"]
        )

    def test_add_note_with_subdeck_no_existing_tags(
        self, deck_manager: DeckManager, mock_backend: Mock
    ) -> None:
        """Test adding note with subdeck when no existing tags."""
        deck_manager.set_current_subdeck("Nouns")
        note_id = deck_manager.add_note("note_type_1", ["Front", "Back"])

        assert note_id == 42
        # Should create tags list with subdeck tag
        mock_backend.add_note.assert_called_once_with(
            "note_type_1", ["Front", "Back"], ["subdeck:Nouns"]
        )

    def test_export_deck_delegation(
        self, deck_manager: DeckManager, mock_backend: Mock
    ) -> None:
        """Test that export_deck is properly delegated."""
        deck_manager.export_deck("/path/to/output.apkg")

        mock_backend.export_deck.assert_called_once_with("/path/to/output.apkg")

    def test_get_stats_with_subdeck_info(
        self, deck_manager: DeckManager, mock_backend: Mock
    ) -> None:
        """Test that get_stats includes subdeck information."""
        # Add some subdecks
        deck_manager.set_current_subdeck("Adjectives")
        deck_manager.set_current_subdeck("Nouns")

        stats = deck_manager.get_stats()

        # Should include original backend stats
        assert stats["deck_name"] == "Test Deck"
        assert stats["note_types_count"] == 1
        assert stats["notes_count"] == 5
        assert stats["media_files_count"] == 3

        # Should include subdeck information
        assert "subdecks" in stats
        subdeck_stats = stats["subdecks"]
        assert subdeck_stats["count"] == 2
        assert set(subdeck_stats["names"]) == {"Adjectives", "Nouns"}
        assert set(subdeck_stats["full_names"]) == {
            "Test Deck::Adjectives",
            "Test Deck::Nouns",
        }
        assert subdeck_stats["current"] == "Nouns"

    def test_get_stats_no_subdecks(
        self, deck_manager: DeckManager, mock_backend: Mock
    ) -> None:
        """Test get_stats when no subdecks are created."""
        stats = deck_manager.get_stats()

        subdeck_stats = stats["subdecks"]
        assert subdeck_stats["count"] == 0
        assert subdeck_stats["names"] == []
        assert subdeck_stats["full_names"] == []
        assert subdeck_stats["current"] is None
