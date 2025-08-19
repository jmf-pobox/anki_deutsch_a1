"""
Tests for MediaEnricher service.

This module tests the Clean Pipeline Architecture's MediaEnricher service
that centralizes all media existence checks and generation logic.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from langlearn.models.adjective import Adjective
from langlearn.models.adverb import Adverb, AdverbType
from langlearn.models.negation import Negation, NegationType
from langlearn.models.noun import Noun
from langlearn.services.media_enricher import MediaEnricher, StandardMediaEnricher


class TestMediaEnricher:
    """Test MediaEnricher abstract interface."""

    def test_media_enricher_is_abstract(self):
        """Test that MediaEnricher cannot be instantiated directly."""
        with pytest.raises(TypeError):
            MediaEnricher()  # Should raise TypeError for abstract class


class TestStandardMediaEnricher:
    """Test StandardMediaEnricher implementation."""

    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            audio_dir = temp_path / "audio"
            image_dir = temp_path / "images"
            audio_dir.mkdir()
            image_dir.mkdir()
            yield audio_dir, image_dir

    @pytest.fixture
    def mock_media_service(self):
        """Create mock media service."""
        service = Mock()
        service.generate_audio.return_value = "/fake/audio.mp3"
        service.generate_image.return_value = "/fake/image.jpg"
        return service

    @pytest.fixture
    def media_enricher(self, mock_media_service, temp_dirs):
        """Create StandardMediaEnricher with mock service and temp directories."""
        audio_dir, image_dir = temp_dirs
        return StandardMediaEnricher(
            media_service=mock_media_service,
            audio_base_path=audio_dir,
            image_base_path=image_dir,
        )

    @pytest.fixture
    def sample_noun(self):
        """Create sample noun for testing."""
        return Noun(
            noun="Katze",
            article="die",
            english="cat",
            plural="Katzen",
            example="Die Katze ist süß.",
            related="Tier",
        )

    @pytest.fixture
    def sample_adjective(self):
        """Create sample adjective for testing."""
        return Adjective(
            word="schön",
            english="beautiful",
            example="Das ist schön.",
            comparative="schöner",
            superlative="am schönsten",
        )

    @pytest.fixture
    def sample_adverb(self):
        """Create sample adverb for testing."""
        return Adverb(
            word="hier",
            english="here",
            type=AdverbType.LOCATION,
            example="Ich bin hier.",
        )

    @pytest.fixture
    def sample_negation(self):
        """Create sample negation for testing."""
        return Negation(
            word="nicht",
            english="not",
            type=NegationType.GENERAL,
            example="Das ist nicht gut.",
        )

    def test_initialization(self, mock_media_service, temp_dirs):
        """Test StandardMediaEnricher initialization."""
        audio_dir, image_dir = temp_dirs
        enricher = StandardMediaEnricher(
            media_service=mock_media_service,
            audio_base_path=audio_dir,
            image_base_path=image_dir,
        )

        assert enricher._media_service == mock_media_service
        assert enricher._audio_base_path == audio_dir
        assert enricher._image_base_path == image_dir
        assert audio_dir.exists()
        assert image_dir.exists()

    def test_directories_created_if_not_exist(self, mock_media_service):
        """Test that directories are created if they don't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            audio_dir = temp_path / "new_audio"
            image_dir = temp_path / "new_images"

            # Directories don't exist yet
            assert not audio_dir.exists()
            assert not image_dir.exists()

            # Create enricher - should create directories
            StandardMediaEnricher(
                media_service=mock_media_service,
                audio_base_path=audio_dir,
                image_base_path=image_dir,
            )

            # Directories should now exist
            assert audio_dir.exists()
            assert image_dir.exists()

    def test_audio_exists_true(self, media_enricher, temp_dirs):
        """Test audio_exists returns True when file exists."""
        audio_dir, _ = temp_dirs

        # Create fake audio file
        test_audio = audio_dir / "audio_12345678.mp3"
        test_audio.write_text("fake audio")

        # Mock the filename generation
        with patch.object(
            media_enricher, "_get_audio_filename", return_value="audio_12345678.mp3"
        ):
            assert media_enricher.audio_exists("test text") is True

    def test_audio_exists_false(self, media_enricher):
        """Test audio_exists returns False when file doesn't exist."""
        assert media_enricher.audio_exists("nonexistent text") is False

    def test_audio_exists_empty_text(self, media_enricher):
        """Test audio_exists returns False for empty text."""
        assert media_enricher.audio_exists("") is False
        assert media_enricher.audio_exists(None) is False

    def test_image_exists_true(self, media_enricher, temp_dirs):
        """Test image_exists returns True when file exists."""
        _, image_dir = temp_dirs

        # Create fake image file
        test_image = image_dir / "katze.jpg"
        test_image.write_text("fake image")

        assert media_enricher.image_exists("Katze") is True

    def test_image_exists_false(self, media_enricher):
        """Test image_exists returns False when file doesn't exist."""
        assert media_enricher.image_exists("nonexistent") is False

    def test_image_exists_empty_word(self, media_enricher):
        """Test image_exists returns False for empty word."""
        assert media_enricher.image_exists("") is False
        assert media_enricher.image_exists(None) is False

    def test_generate_audio_success(self, media_enricher, mock_media_service):
        """Test successful audio generation."""
        result = media_enricher.generate_audio("test text")

        assert result == "/fake/audio.mp3"
        mock_media_service.generate_audio.assert_called_once_with("test text")

    def test_generate_audio_failure(self, media_enricher, mock_media_service):
        """Test audio generation failure handling."""
        mock_media_service.generate_audio.side_effect = Exception("Generation failed")

        result = media_enricher.generate_audio("test text")

        assert result is None

    def test_generate_image_success(self, media_enricher, mock_media_service):
        """Test successful image generation."""
        result = media_enricher.generate_image("search terms", "fallback")

        assert result == "/fake/image.jpg"
        mock_media_service.generate_image.assert_called_once_with(
            "search terms", "fallback"
        )

    def test_generate_image_failure(self, media_enricher, mock_media_service):
        """Test image generation failure handling."""
        mock_media_service.generate_image.side_effect = Exception("Generation failed")

        result = media_enricher.generate_image("search terms", "fallback")

        assert result is None

    @patch("langlearn.services.service_container.get_anthropic_service")
    def test_enrich_noun_record_complete(
        self, mock_anthropic_service, media_enricher, sample_noun, mock_media_service
    ):
        """Test complete noun record enrichment."""
        # Mock anthropic service to return None for fallback behavior
        mock_anthropic_service.return_value = None

        record = {
            "noun": "Katze",
            "article": "die",
            "english": "cat",
            "plural": "Katzen",
            "example": "Die Katze ist süß.",
            "related": "Tier",
        }

        result = media_enricher.enrich_record(record, sample_noun)

        # Should have added media fields
        assert "word_audio" in result
        assert "example_audio" in result
        assert "image" in result
        assert result["word_audio"] == "[sound:audio.mp3]"
        assert result["example_audio"] == "[sound:audio.mp3]"
        assert result["image"] == '<img src="image.jpg">'

    def test_enrich_noun_record_existing_media(self, media_enricher, sample_noun):
        """Test noun record enrichment with existing media."""
        record = {
            "noun": "Katze",
            "article": "die",
            "english": "cat",
            "plural": "Katzen",
            "example": "Die Katze ist süß.",
            "related": "Tier",
            "word_audio": "[sound:existing.mp3]",
            "example_audio": "[sound:existing2.mp3]",
            "image": '<img src="existing.jpg">',
        }

        result = media_enricher.enrich_record(record, sample_noun)

        # Should preserve existing media
        assert result["word_audio"] == "[sound:existing.mp3]"
        assert result["example_audio"] == "[sound:existing2.mp3]"
        assert result["image"] == '<img src="existing.jpg">'

    @patch("langlearn.services.service_container.get_anthropic_service")
    def test_enrich_adjective_record(
        self, mock_anthropic_service, media_enricher, sample_adjective
    ):
        """Test adjective record enrichment."""
        # Mock anthropic service to return None for fallback behavior
        mock_anthropic_service.return_value = None

        record = {
            "word": "schön",
            "english": "beautiful",
            "example": "Das ist schön.",
            "comparative": "schöner",
            "superlative": "am schönsten",
        }

        result = media_enricher.enrich_record(record, sample_adjective)

        assert "word_audio" in result
        assert "example_audio" in result
        assert "image" in result

    @patch("langlearn.services.service_container.get_anthropic_service")
    def test_enrich_adverb_record(
        self, mock_anthropic_service, media_enricher, sample_adverb
    ):
        """Test adverb record enrichment."""
        # Mock anthropic service to return None for fallback behavior
        mock_anthropic_service.return_value = None

        record = {
            "word": "hier",
            "english": "here",
            "type": "location",
            "example": "Ich bin hier.",
        }

        result = media_enricher.enrich_record(record, sample_adverb)

        assert "word_audio" in result
        assert "example_audio" in result
        assert "image" in result

    @patch("langlearn.services.service_container.get_anthropic_service")
    def test_enrich_negation_record(
        self, mock_anthropic_service, media_enricher, sample_negation
    ):
        """Test negation record enrichment."""
        # Mock anthropic service to return None for fallback behavior
        mock_anthropic_service.return_value = None

        record = {
            "word": "nicht",
            "english": "not",
            "type": "general",
            "example": "Das ist nicht gut.",
        }

        result = media_enricher.enrich_record(record, sample_negation)

        assert "word_audio" in result
        assert "example_audio" in result
        assert "image" in result

    def test_enrich_unknown_model_type(self, media_enricher):
        """Test enrichment with unknown model type."""

        class UnknownModel:
            pass

        record = {"word": "test"}
        unknown_model = UnknownModel()

        result = media_enricher.enrich_record(record, unknown_model)

        # Should return unchanged record
        assert result == record

    def test_get_audio_filename(self, media_enricher):
        """Test audio filename generation."""
        filename = media_enricher._get_audio_filename("test text")

        assert filename.startswith("audio_")
        assert filename.endswith(".mp3")
        assert len(filename) == len("audio_") + 8 + len(".mp3")  # 8-char hash

    def test_get_image_filename(self, media_enricher):
        """Test image filename generation."""
        filename = media_enricher._get_image_filename("Test-Word_123")

        assert filename == "test-word_123.jpg"

    def test_get_image_filename_special_chars(self, media_enricher):
        """Test image filename generation with special characters."""
        filename = media_enricher._get_image_filename("Schön@#$%^&*()")

        assert filename == "schön.jpg"  # Special chars removed, German chars preserved

    def test_get_or_generate_audio_existing(self, media_enricher, temp_dirs):
        """Test _get_or_generate_audio with existing file."""
        audio_dir, _ = temp_dirs

        # Create fake existing audio file
        test_audio = audio_dir / "audio_12345678.mp3"
        test_audio.write_text("fake audio")

        with patch.object(
            media_enricher, "_get_audio_filename", return_value="audio_12345678.mp3"
        ):
            result = media_enricher._get_or_generate_audio("test text")

            # Should return path to existing file
            assert result == str(audio_dir / "audio_12345678.mp3")

    def test_get_or_generate_audio_generate_new(
        self, media_enricher, mock_media_service
    ):
        """Test _get_or_generate_audio with new generation."""
        result = media_enricher._get_or_generate_audio("new text")

        # Should generate new audio
        assert result == "/fake/audio.mp3"
        mock_media_service.generate_audio.assert_called_once_with("new text")

    def test_get_or_generate_image_existing(self, media_enricher, temp_dirs):
        """Test _get_or_generate_image with existing file."""
        _, image_dir = temp_dirs

        # Create fake existing image file
        test_image = image_dir / "test.jpg"
        test_image.write_text("fake image")

        result = media_enricher._get_or_generate_image(
            "test", "search terms", "fallback"
        )

        # Should return path to existing file
        assert result == str(image_dir / "test.jpg")

    def test_get_or_generate_image_generate_new(
        self, media_enricher, mock_media_service
    ):
        """Test _get_or_generate_image with new generation."""
        result = media_enricher._get_or_generate_image(
            "newword", "search terms", "fallback"
        )

        # Should generate new image
        assert result == "/fake/image.jpg"
        mock_media_service.generate_image.assert_called_once_with(
            "search terms", "fallback"
        )

    def test_abstract_noun_no_image_generation(self, media_enricher, temp_dirs):
        """Test that abstract nouns don't get image generation."""
        # Create abstract noun
        abstract_noun = Noun(
            noun="Glück",  # Abstract concept
            article="das",
            english="happiness",
            plural="",
            example="Glück ist wichtig.",
            related="Gefühl",
        )

        record = {
            "noun": "Glück",
            "article": "das",
            "english": "happiness",
            "plural": "",
            "example": "Glück ist wichtig.",
            "related": "Gefühl",
        }

        result = media_enricher.enrich_record(record, abstract_noun)

        # Should have audio but no image
        assert "word_audio" in result
        assert "example_audio" in result
        assert result.get("image") is None or result.get("image") == ""
