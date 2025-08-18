"""Tests for GermanDeckBuilder orchestrator functionality."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from langlearn.backends.base import DeckBackend, MediaFile, NoteType
from langlearn.german_deck_builder import GermanDeckBuilder
from langlearn.models.adjective import Adjective
from langlearn.models.adverb import Adverb, AdverbType
from langlearn.models.negation import Negation, NegationType
from langlearn.models.noun import Noun


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
                word_audio="",
                example_audio="",
                image_path="",
            ),
            Noun(
                noun="Hund",
                article="der",
                english="dog",
                plural="Hunde",
                example="Der Hund bellt.",
                related="Haustier",
                word_audio="",
                example_audio="",
                image_path="",
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
                word_audio="",
                example_audio="",
                image_path="",
            ),
            Adjective(
                word="groß",
                english="big",
                example="Der Baum ist groß.",
                comparative="größer",
                superlative="am größten",
                word_audio="",
                example_audio="",
                image_path="",
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
                word_audio="",
                example_audio="",
                image_path="",
            ),
            Adverb(
                word="sehr",
                english="very",
                type=AdverbType.INTENSITY,
                example="Das ist sehr gut.",
                word_audio="",
                example_audio="",
                image_path="",
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
                word_audio="",
                example_audio="",
                image_path="",
            ),
            Negation(
                word="kein",
                english="no/none",
                type=NegationType.ARTICLE,
                example="Ich habe kein Geld.",
                word_audio="",
                example_audio="",
                image_path="",
            ),
        ]

    def test_initialization_genanki_backend(self) -> None:
        """Test GermanDeckBuilder initialization with genanki backend."""
        with patch("langlearn.german_deck_builder.GenankiBackend") as mock_genanki:
            mock_backend = Mock(spec=DeckBackend)
            mock_genanki.return_value = mock_backend

            builder = GermanDeckBuilder("Test Deck", backend_type="genanki")

            assert builder.deck_name == "Test Deck"
            assert builder.backend_type == "genanki"
            assert builder.enable_media_generation is True

            # Check that services were initialized
            assert builder._csv_service is not None
            assert builder._german_service is not None
            assert builder._template_service is not None
            assert builder._media_service is not None

            # Check that managers were initialized
            assert builder._deck_manager is not None
            assert builder._media_manager is not None

    def test_initialization_anki_backend(self) -> None:
        """Test GermanDeckBuilder initialization with official Anki backend."""
        with patch("langlearn.german_deck_builder.AnkiBackend") as mock_anki:
            mock_backend = Mock(spec=DeckBackend)
            mock_anki.return_value = mock_backend

            builder = GermanDeckBuilder("Test Deck", backend_type="anki")

            assert builder.backend_type == "anki"
            mock_anki.assert_called_once()

    def test_initialization_invalid_backend(self) -> None:
        """Test GermanDeckBuilder initialization with invalid backend."""
        with pytest.raises(ValueError, match="Unknown backend type: invalid"):
            GermanDeckBuilder("Test Deck", backend_type="invalid")

    def test_initialization_media_disabled(self) -> None:
        """Test GermanDeckBuilder initialization with media generation disabled."""
        with patch("langlearn.german_deck_builder.GenankiBackend") as mock_genanki:
            mock_backend = Mock(spec=DeckBackend)
            mock_genanki.return_value = mock_backend

            builder = GermanDeckBuilder(
                "Test Deck", backend_type="genanki", enable_media_generation=False
            )

            assert builder._media_service is None
            assert builder.enable_media_generation is False

    @patch("langlearn.german_deck_builder.GenankiBackend")
    def test_load_nouns_from_csv(
        self, mock_genanki: Mock, sample_noun_data: list[Noun]
    ) -> None:
        """Test loading nouns from CSV file."""
        mock_backend = Mock(spec=DeckBackend)
        mock_genanki.return_value = mock_backend

        builder = GermanDeckBuilder("Test Deck", backend_type="genanki")

        with patch.object(builder._csv_service, "read_csv") as mock_read:
            mock_read.return_value = sample_noun_data

            builder.load_nouns_from_csv("fake_nouns.csv")

            assert len(builder._loaded_nouns) == 2
            assert builder._loaded_nouns[0].noun == "Katze"
            mock_read.assert_called_once()

    @patch("langlearn.german_deck_builder.GenankiBackend")
    def test_load_adjectives_from_csv(
        self, mock_genanki: Mock, sample_adjective_data: list[Adjective]
    ) -> None:
        """Test loading adjectives from CSV file."""
        mock_backend = Mock(spec=DeckBackend)
        mock_genanki.return_value = mock_backend

        builder = GermanDeckBuilder("Test Deck", backend_type="genanki")

        with patch.object(builder._csv_service, "read_csv") as mock_read:
            mock_read.return_value = sample_adjective_data

            builder.load_adjectives_from_csv("fake_adjectives.csv")

            assert len(builder._loaded_adjectives) == 2
            assert builder._loaded_adjectives[0].word == "schön"
            mock_read.assert_called_once()

    @patch("langlearn.german_deck_builder.GenankiBackend")
    def test_load_data_from_directory(
        self, mock_genanki: Mock, sample_noun_data: list[Noun]
    ) -> None:
        """Test loading data from directory with multiple files."""
        mock_backend = Mock(spec=DeckBackend)
        mock_genanki.return_value = mock_backend

        builder = GermanDeckBuilder("Test Deck", backend_type="genanki")

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create fake CSV files
            temp_path = Path(temp_dir)
            (temp_path / "nouns.csv").touch()

            with (
                patch.object(builder, "load_nouns_from_csv") as mock_load_nouns,
                patch.object(builder, "load_adjectives_from_csv") as mock_load_adj,
            ):
                builder.load_data_from_directory(temp_dir)

                # Should call load_nouns_from_csv since nouns.csv exists
                mock_load_nouns.assert_called_once()
                # Should not call load_adjectives_from_csv since file doesn't exist
                mock_load_adj.assert_not_called()

    @patch("langlearn.german_deck_builder.GenankiBackend")
    def test_create_subdeck(self, mock_genanki: Mock) -> None:
        """Test creating subdecks."""
        mock_backend = Mock(spec=DeckBackend)
        mock_genanki.return_value = mock_backend

        builder = GermanDeckBuilder("Test Deck", backend_type="genanki")

        with patch.object(builder._deck_manager, "set_current_subdeck") as mock_set:
            builder.create_subdeck("Nouns")
            mock_set.assert_called_once_with("Nouns")

    @patch("langlearn.german_deck_builder.GenankiBackend")
    def test_reset_to_main_deck(self, mock_genanki: Mock) -> None:
        """Test resetting to main deck."""
        mock_backend = Mock(spec=DeckBackend)
        mock_genanki.return_value = mock_backend

        builder = GermanDeckBuilder("Test Deck", backend_type="genanki")

        with patch.object(builder._deck_manager, "reset_to_main_deck") as mock_reset:
            builder.reset_to_main_deck()
            mock_reset.assert_called_once()

    @patch("langlearn.german_deck_builder.GenankiBackend")
    def test_generate_noun_cards_no_data(self, mock_genanki: Mock) -> None:
        """Test generating noun cards when no data is loaded."""
        mock_backend = Mock(spec=DeckBackend)
        mock_genanki.return_value = mock_backend

        builder = GermanDeckBuilder("Test Deck", backend_type="genanki")

        result = builder.generate_noun_cards()
        assert result == 0

    @patch("langlearn.german_deck_builder.GenankiBackend")
    def test_generate_noun_cards_with_data(
        self, mock_genanki: Mock, sample_noun_data: list[Noun]
    ) -> None:
        """Test generating noun cards with loaded data."""
        mock_backend = Mock(spec=DeckBackend)
        mock_backend.deck_name = "Test Deck"
        mock_genanki.return_value = mock_backend

        builder = GermanDeckBuilder("Test Deck", backend_type="genanki")
        builder._loaded_nouns = sample_noun_data

        # Mock the template service
        mock_note_type = Mock(spec=NoteType)
        mock_note_type.name = "Test Noun Note Type"
        with patch.object(
            builder._template_service, "get_noun_note_type"
        ) as mock_get_template:
            mock_get_template.return_value = mock_note_type

            with patch.object(
                builder._deck_manager, "create_note_type"
            ) as mock_create_type:
                mock_create_type.return_value = "note_type_1"

                with patch.object(builder._deck_manager, "add_note") as mock_add_note:
                    result = builder.generate_noun_cards(generate_media=False)

                    assert result == 2
                    assert mock_add_note.call_count == 2

    @patch("langlearn.german_deck_builder.GenankiBackend")
    def test_generate_noun_cards_with_media(
        self, mock_genanki: Mock, sample_noun_data: list[Noun]
    ) -> None:
        """Test generating noun cards with media generation."""
        mock_backend = Mock(spec=DeckBackend)
        mock_backend.deck_name = "Test Deck"
        mock_genanki.return_value = mock_backend

        builder = GermanDeckBuilder("Test Deck", backend_type="genanki")
        builder._loaded_nouns = sample_noun_data[:1]  # Just one noun for simplicity

        # Mock services and managers
        mock_note_type = Mock(spec=NoteType)
        mock_note_type.name = "Test Noun Note Type"
        mock_media_file = MediaFile(
            path="/fake/audio.mp3", reference="[sound:audio.mp3]"
        )

        with patch.object(
            builder._template_service, "get_noun_note_type"
        ) as mock_get_template:
            mock_get_template.return_value = mock_note_type

            with patch.object(
                builder._deck_manager, "create_note_type"
            ) as mock_create_type:
                mock_create_type.return_value = "note_type_1"

                with patch.object(
                    builder._media_manager, "generate_and_add_audio"
                ) as mock_gen_audio:
                    mock_gen_audio.return_value = mock_media_file

                    with patch.object(
                        builder._media_manager, "generate_and_add_image"
                    ) as mock_gen_image:
                        mock_gen_image.return_value = mock_media_file

                        with patch.object(
                            builder._deck_manager, "add_note"
                        ) as mock_add_note:
                            result = builder.generate_noun_cards(generate_media=True)

                            assert result == 1
                            # Should call audio generation twice: noun forms + example
                            assert mock_gen_audio.call_count == 2
                            mock_gen_audio.assert_any_call("die Katze, die Katzen")
                            mock_gen_audio.assert_any_call("Die Katze schläft.")

                            # Check that the audio reference was included in the fields
                            call_args = mock_add_note.call_args[0]
                            fields = call_args[1]
                            assert "[sound:audio.mp3]" in fields

    @patch("langlearn.german_deck_builder.GenankiBackend")
    def test_generate_adjective_cards_with_data(
        self, mock_genanki: Mock, sample_adjective_data: list[Adjective]
    ) -> None:
        """Test generating adjective cards with loaded data."""
        mock_backend = Mock(spec=DeckBackend)
        mock_backend.deck_name = "Test Deck"
        mock_genanki.return_value = mock_backend

        builder = GermanDeckBuilder("Test Deck", backend_type="genanki")
        builder._loaded_adjectives = sample_adjective_data

        # Mock the template service
        mock_note_type = Mock(spec=NoteType)
        mock_note_type.name = "Test Adjective Note Type"
        with patch.object(
            builder._template_service, "get_adjective_note_type"
        ) as mock_get_template:
            mock_get_template.return_value = mock_note_type

            with patch.object(
                builder._deck_manager, "create_note_type"
            ) as mock_create_type:
                mock_create_type.return_value = "note_type_1"

                with patch.object(builder._deck_manager, "add_note") as mock_add_note:
                    result = builder.generate_adjective_cards(generate_media=False)

                    assert result == 2
                    assert mock_add_note.call_count == 2

    @patch("langlearn.german_deck_builder.GenankiBackend")
    def test_generate_all_cards(
        self,
        mock_genanki: Mock,
        sample_noun_data: list[Noun],
        sample_adjective_data: list[Adjective],
    ) -> None:
        """Test generating all cards for loaded data."""
        mock_backend = Mock(spec=DeckBackend)
        mock_genanki.return_value = mock_backend

        builder = GermanDeckBuilder("Test Deck", backend_type="genanki")
        builder._loaded_nouns = sample_noun_data
        builder._loaded_adjectives = sample_adjective_data

        with patch.object(builder, "generate_noun_cards") as mock_noun_cards:
            mock_noun_cards.return_value = 2

            with patch.object(builder, "generate_adjective_cards") as mock_adj_cards:
                mock_adj_cards.return_value = 2

                result = builder.generate_all_cards(generate_media=False)

                assert result == {"nouns": 2, "adjectives": 2}
                mock_noun_cards.assert_called_once_with(False)
                mock_adj_cards.assert_called_once_with(False)

    @patch("langlearn.german_deck_builder.GenankiBackend")
    def test_export_deck(self, mock_genanki: Mock) -> None:
        """Test exporting deck to file."""
        mock_backend = Mock(spec=DeckBackend)
        mock_genanki.return_value = mock_backend

        builder = GermanDeckBuilder("Test Deck", backend_type="genanki")

        with patch.object(builder._deck_manager, "export_deck") as mock_export:
            builder.export_deck("output/test.apkg")
            mock_export.assert_called_once_with("output/test.apkg")

    @patch("langlearn.german_deck_builder.GenankiBackend")
    def test_get_statistics(self, mock_genanki: Mock) -> None:
        """Test getting comprehensive statistics."""
        mock_backend = Mock(spec=DeckBackend)
        mock_genanki.return_value = mock_backend

        builder = GermanDeckBuilder("Test Deck", backend_type="genanki")
        builder._loaded_nouns = [Mock()]
        builder._loaded_adjectives = [Mock(), Mock()]

        mock_deck_stats = {"notes_count": 10}
        mock_media_stats = {"files_added": 5}

        with patch.object(builder._deck_manager, "get_stats") as mock_get_deck_stats:
            mock_get_deck_stats.return_value = mock_deck_stats

            with patch.object(
                builder._media_manager, "get_detailed_stats"
            ) as mock_get_media_stats:
                mock_get_media_stats.return_value = mock_media_stats

                stats = builder.get_statistics()

                assert stats["deck_info"]["name"] == "Test Deck"
                assert stats["loaded_data"]["nouns"] == 1
                assert stats["loaded_data"]["adjectives"] == 2
                assert stats["deck_stats"] == mock_deck_stats
                assert stats["files_added"] == 5

    @patch("langlearn.german_deck_builder.GenankiBackend")
    def test_get_subdeck_info(self, mock_genanki: Mock) -> None:
        """Test getting subdeck information."""
        mock_backend = Mock(spec=DeckBackend)
        mock_genanki.return_value = mock_backend

        builder = GermanDeckBuilder("Test Deck", backend_type="genanki")

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

    @patch("langlearn.german_deck_builder.GenankiBackend")
    def test_clear_loaded_data(self, mock_genanki: Mock) -> None:
        """Test clearing loaded data."""
        mock_backend = Mock(spec=DeckBackend)
        mock_genanki.return_value = mock_backend

        builder = GermanDeckBuilder("Test Deck", backend_type="genanki")
        builder._loaded_nouns = [Mock()]
        builder._loaded_adjectives = [Mock()]

        builder.clear_loaded_data()

        assert len(builder._loaded_nouns) == 0
        assert len(builder._loaded_adjectives) == 0

    @patch("langlearn.german_deck_builder.GenankiBackend")
    def test_clear_media_cache(self, mock_genanki: Mock) -> None:
        """Test clearing media cache."""
        mock_backend = Mock(spec=DeckBackend)
        mock_genanki.return_value = mock_backend

        builder = GermanDeckBuilder("Test Deck", backend_type="genanki")

        with patch.object(builder._media_manager, "clear_cache") as mock_clear:
            builder.clear_media_cache()
            mock_clear.assert_called_once()

    @patch("langlearn.german_deck_builder.GenankiBackend")
    def test_context_manager_support(self, mock_genanki: Mock) -> None:
        """Test context manager support."""
        mock_backend = Mock(spec=DeckBackend)
        mock_genanki.return_value = mock_backend

        with GermanDeckBuilder("Test Deck", backend_type="genanki") as builder:
            assert isinstance(builder, GermanDeckBuilder)
            assert builder.deck_name == "Test Deck"

    @patch("langlearn.german_deck_builder.GenankiBackend")
    def test_generate_all_media_no_service(self, mock_genanki: Mock) -> None:
        """Test generate_all_media when media service is disabled."""
        mock_backend = Mock(spec=DeckBackend)
        mock_genanki.return_value = mock_backend

        builder = GermanDeckBuilder(
            "Test Deck", backend_type="genanki", enable_media_generation=False
        )

        result = builder.generate_all_media()
        assert result == {}

    @patch("langlearn.german_deck_builder.GenankiBackend")
    def test_generate_all_media_with_service(self, mock_genanki: Mock) -> None:
        """Test generate_all_media when media service is enabled."""
        mock_backend = Mock(spec=DeckBackend)
        mock_genanki.return_value = mock_backend

        builder = GermanDeckBuilder("Test Deck", backend_type="genanki")

        mock_stats = {"files_added": 10}
        with patch.object(
            builder._media_manager, "get_detailed_stats"
        ) as mock_get_stats:
            mock_get_stats.return_value = mock_stats

            result = builder.generate_all_media()
            assert result == mock_stats

    @patch("langlearn.german_deck_builder.GenankiBackend")
    def test_load_adverbs_from_csv(
        self, mock_genanki: Mock, sample_adverb_data: list[Adverb]
    ) -> None:
        """Test loading adverbs from CSV file."""
        mock_backend = Mock(spec=DeckBackend)
        mock_genanki.return_value = mock_backend

        builder = GermanDeckBuilder("Test Deck", backend_type="genanki")

        with patch.object(builder._csv_service, "read_csv") as mock_read:
            mock_read.return_value = sample_adverb_data

            builder.load_adverbs_from_csv("fake_adverbs.csv")

            assert len(builder._loaded_adverbs) == 2
            assert builder._loaded_adverbs[0].word == "schnell"
            mock_read.assert_called_once()

    @patch("langlearn.german_deck_builder.GenankiBackend")
    def test_load_negations_from_csv(
        self, mock_genanki: Mock, sample_negation_data: list[Negation]
    ) -> None:
        """Test loading negations from CSV file."""
        mock_backend = Mock(spec=DeckBackend)
        mock_genanki.return_value = mock_backend

        builder = GermanDeckBuilder("Test Deck", backend_type="genanki")

        with patch.object(builder._csv_service, "read_csv") as mock_read:
            mock_read.return_value = sample_negation_data

            builder.load_negations_from_csv("fake_negations.csv")

            assert len(builder._loaded_negations) == 2
            assert builder._loaded_negations[0].word == "nicht"
            mock_read.assert_called_once()

    @patch("langlearn.german_deck_builder.GenankiBackend")
    def test_generate_adverb_cards_no_data(self, mock_genanki: Mock) -> None:
        """Test generating adverb cards when no data is loaded."""
        mock_backend = Mock(spec=DeckBackend)
        mock_genanki.return_value = mock_backend

        builder = GermanDeckBuilder("Test Deck", backend_type="genanki")

        result = builder.generate_adverb_cards()
        assert result == 0

    @patch("langlearn.german_deck_builder.GenankiBackend")
    def test_generate_adverb_cards_with_data(
        self, mock_genanki: Mock, sample_adverb_data: list[Adverb]
    ) -> None:
        """Test generating adverb cards with loaded data."""
        mock_backend = Mock(spec=DeckBackend)
        mock_backend.deck_name = "Test Deck"
        mock_genanki.return_value = mock_backend

        builder = GermanDeckBuilder("Test Deck", backend_type="genanki")
        builder._loaded_adverbs = sample_adverb_data

        # Mock the template service
        mock_note_type = Mock(spec=NoteType)
        mock_note_type.name = "Test Adverb Note Type"
        with patch.object(
            builder._template_service, "get_adverb_note_type"
        ) as mock_get_template:
            mock_get_template.return_value = mock_note_type

            with patch.object(
                builder._deck_manager, "create_note_type"
            ) as mock_create_type:
                mock_create_type.return_value = "note_type_1"

                with patch.object(builder._deck_manager, "add_note") as mock_add_note:
                    result = builder.generate_adverb_cards(generate_media=False)

                    assert result == 2
                    assert mock_add_note.call_count == 2

    @patch("langlearn.german_deck_builder.GenankiBackend")
    def test_generate_negation_cards_no_data(self, mock_genanki: Mock) -> None:
        """Test generating negation cards when no data is loaded."""
        mock_backend = Mock(spec=DeckBackend)
        mock_genanki.return_value = mock_backend

        builder = GermanDeckBuilder("Test Deck", backend_type="genanki")

        result = builder.generate_negation_cards()
        assert result == 0

    @patch("langlearn.german_deck_builder.GenankiBackend")
    def test_generate_negation_cards_with_data(
        self, mock_genanki: Mock, sample_negation_data: list[Negation]
    ) -> None:
        """Test generating negation cards with loaded data."""
        mock_backend = Mock(spec=DeckBackend)
        mock_backend.deck_name = "Test Deck"
        mock_genanki.return_value = mock_backend

        builder = GermanDeckBuilder("Test Deck", backend_type="genanki")
        builder._loaded_negations = sample_negation_data

        # Mock the template service
        mock_note_type = Mock(spec=NoteType)
        mock_note_type.name = "Test Negation Note Type"
        with patch.object(
            builder._template_service, "get_negation_note_type"
        ) as mock_get_template:
            mock_get_template.return_value = mock_note_type

            with patch.object(
                builder._deck_manager, "create_note_type"
            ) as mock_create_type:
                mock_create_type.return_value = "note_type_1"

                with patch.object(builder._deck_manager, "add_note") as mock_add_note:
                    result = builder.generate_negation_cards(generate_media=False)

                    assert result == 2
                    assert mock_add_note.call_count == 2

    @patch("langlearn.german_deck_builder.GenankiBackend")
    def test_generate_adverb_cards_with_existing_media(
        self, mock_genanki: Mock, sample_adverb_data: list[Adverb]
    ) -> None:
        """Test generating adverb cards with existing media files."""
        mock_backend = Mock(spec=DeckBackend)
        mock_backend.deck_name = "Test Deck"
        mock_genanki.return_value = mock_backend

        builder = GermanDeckBuilder("Test Deck", backend_type="genanki")
        # Modify adverb data to have existing media paths
        adverb_with_media = sample_adverb_data[0]
        adverb_with_media.word_audio = "/fake/existing_audio.mp3"
        adverb_with_media.image_path = "/fake/existing_image.jpg"
        builder._loaded_adverbs = [adverb_with_media]

        mock_note_type = Mock(spec=NoteType)
        mock_note_type.name = "Test Adverb Note Type"
        mock_media_file = MediaFile(
            path="/fake/audio.mp3", reference="[sound:audio.mp3]"
        )

        with (
            patch.object(Path, "exists", return_value=True),
            patch.object(
                builder._template_service, "get_adverb_note_type"
            ) as mock_get_template,
            patch.object(builder._deck_manager, "create_note_type") as mock_create_type,
            patch.object(builder._media_manager, "add_media_file") as mock_add_media,
            patch.object(builder._deck_manager, "add_note"),
        ):
            mock_get_template.return_value = mock_note_type
            mock_create_type.return_value = "note_type_1"
            mock_add_media.return_value = mock_media_file

            result = builder.generate_adverb_cards(generate_media=True)

            assert result == 1
            # Should call add_media_file for existing audio and image
            assert mock_add_media.call_count >= 1

    @patch("langlearn.german_deck_builder.GenankiBackend")
    def test_generate_negation_cards_with_media_generation(
        self, mock_genanki: Mock, sample_negation_data: list[Negation]
    ) -> None:
        """Test generating negation cards with media generation."""
        mock_backend = Mock(spec=DeckBackend)
        mock_backend.deck_name = "Test Deck"
        mock_genanki.return_value = mock_backend

        builder = GermanDeckBuilder("Test Deck", backend_type="genanki")
        builder._loaded_negations = sample_negation_data[:1]  # Just one for simplicity

        mock_note_type = Mock(spec=NoteType)
        mock_note_type.name = "Test Negation Note Type"
        mock_media_file = MediaFile(
            path="/fake/audio.mp3", reference="[sound:audio.mp3]"
        )

        with patch.object(
            builder._template_service, "get_negation_note_type"
        ) as mock_get_template:
            mock_get_template.return_value = mock_note_type

            with patch.object(
                builder._deck_manager, "create_note_type"
            ) as mock_create_type:
                mock_create_type.return_value = "note_type_1"

                with patch.object(
                    builder._media_manager, "generate_and_add_audio"
                ) as mock_gen_audio:
                    mock_gen_audio.return_value = mock_media_file

                    with patch.object(
                        builder._media_manager, "generate_and_add_image"
                    ) as mock_gen_image:
                        mock_gen_image.return_value = mock_media_file

                        with patch.object(builder._deck_manager, "add_note"):
                            result = builder.generate_negation_cards(
                                generate_media=True
                            )

                            assert result == 1
                            # Should generate audio for the negation word and example
                            assert mock_gen_audio.call_count >= 1

    @patch("langlearn.german_deck_builder.GenankiBackend")
    def test_load_data_from_directory_all_files(self, mock_genanki: Mock) -> None:
        """Test loading data from directory with all file types."""
        mock_backend = Mock(spec=DeckBackend)
        mock_genanki.return_value = mock_backend

        builder = GermanDeckBuilder("Test Deck", backend_type="genanki")

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create all CSV files
            temp_path = Path(temp_dir)
            (temp_path / "nouns.csv").touch()
            (temp_path / "adjectives.csv").touch()
            (temp_path / "adverbs.csv").touch()
            (temp_path / "negations.csv").touch()

            with (
                patch.object(builder, "load_nouns_from_csv") as mock_load_nouns,
                patch.object(builder, "load_adjectives_from_csv") as mock_load_adj,
                patch.object(builder, "load_adverbs_from_csv") as mock_load_adv,
                patch.object(builder, "load_negations_from_csv") as mock_load_neg,
            ):
                builder.load_data_from_directory(temp_dir)

                # Should call all loaders
                mock_load_nouns.assert_called_once()
                mock_load_adj.assert_called_once()
                mock_load_adv.assert_called_once()
                mock_load_neg.assert_called_once()

    @patch("langlearn.german_deck_builder.GenankiBackend")
    def test_generate_all_cards_with_all_types(
        self,
        mock_genanki: Mock,
        sample_noun_data: list[Noun],
        sample_adjective_data: list[Adjective],
        sample_adverb_data: list[Adverb],
        sample_negation_data: list[Negation],
    ) -> None:
        """Test generating all cards for all loaded data types."""
        mock_backend = Mock(spec=DeckBackend)
        mock_genanki.return_value = mock_backend

        builder = GermanDeckBuilder("Test Deck", backend_type="genanki")
        builder._loaded_nouns = sample_noun_data
        builder._loaded_adjectives = sample_adjective_data
        builder._loaded_adverbs = sample_adverb_data
        builder._loaded_negations = sample_negation_data

        with (
            patch.object(builder, "generate_noun_cards") as mock_noun_cards,
            patch.object(builder, "generate_adjective_cards") as mock_adj_cards,
            patch.object(builder, "generate_adverb_cards") as mock_adv_cards,
            patch.object(builder, "generate_negation_cards") as mock_neg_cards,
        ):
            mock_noun_cards.return_value = 2
            mock_adj_cards.return_value = 2
            mock_adv_cards.return_value = 2
            mock_neg_cards.return_value = 2

            result = builder.generate_all_cards(generate_media=False)

            expected = {
                "nouns": 2,
                "adjectives": 2,
                "adverbs": 2,
                "negations": 2,
            }
            assert result == expected
            mock_noun_cards.assert_called_once_with(False)
            mock_adj_cards.assert_called_once_with(False)
            mock_adv_cards.assert_called_once_with(False)
            mock_neg_cards.assert_called_once_with(False)

    @patch("langlearn.german_deck_builder.GenankiBackend")
    def test_get_statistics_comprehensive(
        self,
        mock_genanki: Mock,
        sample_noun_data: list[Noun],
        sample_adjective_data: list[Adjective],
        sample_adverb_data: list[Adverb],
        sample_negation_data: list[Negation],
    ) -> None:
        """Test getting comprehensive statistics with all data types."""
        mock_backend = Mock(spec=DeckBackend)
        mock_genanki.return_value = mock_backend

        builder = GermanDeckBuilder("Test Deck", backend_type="genanki")
        builder._loaded_nouns = sample_noun_data
        builder._loaded_adjectives = sample_adjective_data
        builder._loaded_adverbs = sample_adverb_data
        builder._loaded_negations = sample_negation_data

        mock_deck_stats = {"notes_count": 20}
        mock_media_stats = {"files_added": 15}

        with patch.object(builder._deck_manager, "get_stats") as mock_get_deck_stats:
            mock_get_deck_stats.return_value = mock_deck_stats

            with patch.object(
                builder._media_manager, "get_detailed_stats"
            ) as mock_get_media_stats:
                mock_get_media_stats.return_value = mock_media_stats

                stats = builder.get_statistics()

                assert stats["deck_info"]["name"] == "Test Deck"
                assert stats["loaded_data"]["nouns"] == 2
                assert stats["loaded_data"]["adjectives"] == 2
                assert stats["loaded_data"]["adverbs"] == 2
                assert stats["loaded_data"]["negations"] == 2
                assert stats["deck_stats"] == mock_deck_stats
                assert stats["files_added"] == 15

    @patch("langlearn.german_deck_builder.GenankiBackend")
    def test_clear_loaded_data_comprehensive(
        self,
        mock_genanki: Mock,
        sample_noun_data: list[Noun],
        sample_adjective_data: list[Adjective],
        sample_adverb_data: list[Adverb],
        sample_negation_data: list[Negation],
    ) -> None:
        """Test clearing all loaded data types."""
        mock_backend = Mock(spec=DeckBackend)
        mock_genanki.return_value = mock_backend

        builder = GermanDeckBuilder("Test Deck", backend_type="genanki")
        builder._loaded_nouns = sample_noun_data
        builder._loaded_adjectives = sample_adjective_data
        builder._loaded_adverbs = sample_adverb_data
        builder._loaded_negations = sample_negation_data

        builder.clear_loaded_data()

        assert len(builder._loaded_nouns) == 0
        assert len(builder._loaded_adjectives) == 0
        assert len(builder._loaded_adverbs) == 0
        assert len(builder._loaded_negations) == 0
