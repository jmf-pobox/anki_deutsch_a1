"""Tests for GermanDeckBuilder orchestrator functionality."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from langlearn.core.backends.base import DeckBackend, MediaFile
from langlearn.deck_builder import DeckBuilder
from langlearn.languages.german.models.adjective import Adjective
from langlearn.languages.german.models.adverb import Adverb, AdverbType
from langlearn.languages.german.models.negation import Negation, NegationType
from langlearn.languages.german.models.noun import Noun


class TestGermanDeckBuilder:
    """Test GermanDeckBuilder orchestration functionality."""

    @pytest.fixture
    def mock_backend(self) -> Mock:
        """Create a mock backend for testing."""
        backend = Mock(spec=DeckBackend)
        backend.deck_name = "Test German Deck"
        backend.create_note_type.return_value = "note_type_1"
        backend.add_note.return_value = 42
        backend.add_media_file.return_value = MediaFile(
            path="/fake/audio.mp3", reference="[sound:audio.mp3]"
        )
        backend.get_stats.return_value = {
            "deck_name": "Test German Deck",
            "note_types_count": 2,
            "notes_count": 10,
            "media_files_count": 5,
        }
        return backend

    @pytest.fixture
    def sample_noun_data(self) -> list[Noun]:
        """Create sample noun data for testing."""
        return [
            Noun(
                noun="Katze",
                article="die",
                english="cat",
                plural="Katzen",
                example="Die Katze schläft.",
                related="Haustier",
            ),
            Noun(
                noun="Hund",
                article="der",
                english="dog",
                plural="Hunde",
                example="Der Hund bellt.",
                related="Haustier",
            ),
        ]

    @pytest.fixture
    def sample_adjective_data(self) -> list[Adjective]:
        """Create sample adjective data for testing."""
        return [
            Adjective(
                word="schön",
                english="beautiful",
                example="Das Haus ist schön.",
                comparative="schöner",
                superlative="am schönsten",
            ),
            Adjective(
                word="groß",
                english="big",
                example="Der Baum ist groß.",
                comparative="größer",
                superlative="am größten",
            ),
        ]

    @pytest.fixture
    def sample_adverb_data(self) -> list[Adverb]:
        """Create sample adverb data for testing."""
        return [
            Adverb(
                word="schnell",
                english="fast",
                type=AdverbType.MANNER,
                example="Er läuft schnell.",
            ),
            Adverb(
                word="sehr",
                english="very",
                type=AdverbType.INTENSITY,
                example="Das ist sehr gut.",
            ),
        ]

    @pytest.fixture
    def sample_negation_data(self) -> list[Negation]:
        """Create sample negation data for testing."""
        return [
            Negation(
                word="nicht",
                english="not",
                type=NegationType.GENERAL,
                example="Ich gehe nicht.",
            ),
            Negation(
                word="kein",
                english="no/none",
                type=NegationType.ARTICLE,
                example="Ich habe kein Geld.",
            ),
        ]

    def test_initialization_genanki_backend_deprecated(self) -> None:
        """Test GermanDeckBuilder properly rejects deprecated genanki backend."""
        with pytest.raises(ValueError, match="GenanKi backend has been deprecated"):
            DeckBuilder("Test Deck", backend_type="genanki")

    def test_initialization_anki_backend(self) -> None:
        """Test GermanDeckBuilder initialization with official Anki backend."""
        with patch("langlearn.deck_builder.AnkiBackend") as mock_anki:
            mock_backend = Mock(spec=DeckBackend)
            mock_anki.return_value = mock_backend

            builder = DeckBuilder("Test Deck", backend_type="anki")

            assert builder.backend_type == "anki"
            mock_anki.assert_called_once()

    def test_initialization_invalid_backend(self) -> None:
        """Test GermanDeckBuilder initialization with invalid backend."""
        with pytest.raises(ValueError, match="Unknown backend type: invalid"):
            DeckBuilder("Test Deck", backend_type="invalid")

    def test_initialization_media_disabled(self) -> None:
        """Test GermanDeckBuilder initialization with media generation disabled."""
        with patch("langlearn.deck_builder.AnkiBackend") as mock_anki:
            mock_backend = Mock(spec=DeckBackend)
            mock_anki.return_value = mock_backend

            builder = DeckBuilder("Test Deck", backend_type="anki")

            assert builder._media_service is not None

    # Legacy CSV loading tests removed - use load_data_from_directory

    @patch("langlearn.deck_builder.AnkiBackend")
    def test_load_data_from_directory(
        self, mock_anki: Mock, sample_noun_data: list[Noun]
    ) -> None:
        """Test loading data from directory with multiple files using Clean Pipeline."""
        mock_backend = Mock(spec=DeckBackend)
        mock_anki.return_value = mock_backend

        builder = DeckBuilder("Test Deck", backend_type="anki")

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create fake CSV files
            temp_path = Path(temp_dir)
            (temp_path / "nouns.csv").touch()

            # Mock record mapper - testing directory logic, not CSV parsing
            with patch.object(
                builder._record_mapper, "load_records_from_csv"
            ) as mock_load:
                from langlearn.languages.german.records.factory import NounRecord

                # Return mock records when CSV loading is called
                mock_load.return_value = [
                    NounRecord(
                        noun="Katze",
                        article="die",
                        english="cat",
                        plural="Katzen",
                        example="Test",
                        related="",
                    )
                ]

                builder.load_data_from_directory(temp_dir)

                # Should call load_records_from_csv once since nouns.csv exists
                mock_load.assert_called_once()
                # Should have loaded records
                assert len(builder._loaded_records) == 1

    @patch("langlearn.deck_builder.AnkiBackend")
    def test_create_subdeck(self, mock_anki: Mock) -> None:
        """Test creating subdecks."""
        mock_backend = Mock(spec=DeckBackend)
        mock_anki.return_value = mock_backend

        builder = DeckBuilder("Test Deck", backend_type="anki")

        with patch.object(builder._deck_manager, "set_current_subdeck") as mock_set:
            builder.create_subdeck("Nouns")
            mock_set.assert_called_once_with("Nouns")

    @patch("langlearn.deck_builder.AnkiBackend")
    def test_reset_to_main_deck(self, mock_anki: Mock) -> None:
        """Test resetting to main deck."""
        mock_backend = Mock(spec=DeckBackend)
        mock_anki.return_value = mock_backend

        builder = DeckBuilder("Test Deck", backend_type="anki")

        with patch.object(builder._deck_manager, "reset_to_main_deck") as mock_reset:
            builder.reset_to_main_deck()
            mock_reset.assert_called_once()

    # Legacy noun card generation tests removed - use generate_all_cards

    # Legacy test removed: test_generate_noun_cards_with_media
    # - tested functionality removed from DeckBuilder

    # Legacy test removed: test_generate_adjective_cards_with_data
    # - tested functionality removed from DeckBuilder

    # Legacy test removed: test_generate_all_cards
    # - tested functionality removed from DeckBuilder

    @patch("langlearn.deck_builder.AnkiBackend")
    def test_export_deck(self, mock_anki: Mock) -> None:
        """Test exporting deck to file."""
        mock_backend = Mock(spec=DeckBackend)
        mock_anki.return_value = mock_backend

        builder = DeckBuilder("Test Deck", backend_type="anki")

        with patch.object(builder._deck_manager, "export_deck") as mock_export:
            builder.export_deck("output/test.apkg")
            mock_export.assert_called_once_with("output/test.apkg")

    # Legacy test removed: test_get_statistics
    # - tested functionality removed from DeckBuilder

    @patch("langlearn.deck_builder.AnkiBackend")
    def test_get_subdeck_info(self, mock_anki: Mock) -> None:
        """Test getting subdeck information."""
        mock_backend = Mock(spec=DeckBackend)
        mock_anki.return_value = mock_backend

        builder = DeckBuilder("Test Deck", backend_type="anki")

        with patch.object(
            builder._deck_manager, "get_current_deck_name"
        ) as mock_current:
            mock_current.return_value = "Test Deck::Nouns"

            with patch.object(builder._deck_manager, "get_subdeck_names") as mock_names:
                mock_names.return_value = ["Nouns", "Adjectives"]

                with patch.object(
                    builder._deck_manager, "get_full_subdeck_names"
                ) as mock_full:
                    mock_full.return_value = [
                        "Test Deck::Nouns",
                        "Test Deck::Adjectives",
                    ]

                    info = builder.get_subdeck_info()

                    assert info["current_deck"] == "Test Deck::Nouns"
                    assert info["subdeck_names"] == ["Nouns", "Adjectives"]
                    assert len(info["full_subdeck_names"]) == 2

    # Legacy test removed: test_clear_loaded_data
    # - tested functionality removed from DeckBuilder

    @patch("langlearn.deck_builder.AnkiBackend")
    def test_context_manager_support(self, mock_anki: Mock) -> None:
        """Test context manager support."""
        mock_backend = Mock(spec=DeckBackend)
        mock_anki.return_value = mock_backend

        with DeckBuilder("Test Deck", backend_type="anki") as builder:
            assert isinstance(builder, DeckBuilder)
            assert builder.deck_name == "Test Deck"

    @patch("langlearn.deck_builder.AnkiBackend")
    def test_load_data_from_directory_all_files(self, mock_anki: Mock) -> None:
        """Test loading data from directory with all file types using Clean Pipeline."""
        mock_backend = Mock(spec=DeckBackend)
        mock_anki.return_value = mock_backend

        builder = DeckBuilder("Test Deck", backend_type="anki")

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create all CSV files
            temp_path = Path(temp_dir)
            (temp_path / "nouns.csv").touch()
            (temp_path / "adjectives.csv").touch()
            (temp_path / "adverbs.csv").touch()
            (temp_path / "negations.csv").touch()

            # Mock record mapper - testing directory logic, not CSV parsing
            with patch.object(
                builder._record_mapper, "load_records_from_csv"
            ) as mock_load:
                from langlearn.languages.german.records.factory import (
                    AdjectiveRecord,
                    AdverbRecord,
                    NegationRecord,
                    NounRecord,
                )

                # Return different record types based on call
                mock_load.side_effect = [
                    [
                        NounRecord(
                            noun="Katze",
                            article="die",
                            english="cat",
                            plural="Katzen",
                            example="Test",
                            related="",
                        )
                    ],
                    [
                        AdjectiveRecord(
                            word="schön",
                            english="beautiful",
                            example="Test",
                            comparative="schöner",
                            superlative="am schönsten",
                        )
                    ],
                    [
                        AdverbRecord(
                            word="hier", english="here", type="location", example="Test"
                        )
                    ],
                    [
                        NegationRecord(
                            word="nicht", english="not", type="general", example="Test"
                        )
                    ],
                ]

                builder.load_data_from_directory(temp_dir)

                # Should call load_records_from_csv 4 times (once for each CSV file)
                assert mock_load.call_count == 4
                # Should have loaded records from all files
                assert len(builder._loaded_records) == 4


# Legacy test removed: test_generate_all_cards_with_all_types
# - tested functionality removed from DeckBuilder

# Legacy test removed: test_get_statistics_comprehensive
# - tested functionality removed from DeckBuilder

# Legacy test removed: test_clear_loaded_data_comprehensive
# - tested functionality removed from DeckBuilder
