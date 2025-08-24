"""Tests for article card media enrichment functionality."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from langlearn.services.media_enricher import LocalMediaEnricher


class TestArticleCardEnrichment:
    """Test article card media enrichment methods."""

    @pytest.fixture
    def mock_enricher(self):
        """Create a mock MediaEnricher for testing."""
        enricher = LocalMediaEnricher(
            audio_base_path=Path("/tmp/audio"),
            image_base_path=Path("/tmp/images"),
            pexels_service=Mock(),
            audio_service=Mock(),
            translation_service=Mock(),
        )
        return enricher

    def test_enrich_artikel_context_record(self, mock_enricher):
        """Test artikel_context record enrichment."""
        # Arrange
        record = {
            "nominative": "der",
            "example_nom": "Der Mann arbeitet hier",
            "noun_only": "Mann",
            "noun_english": "man",
        }

        # Mock methods
        mock_enricher._get_or_generate_audio = Mock(return_value="audio_test.mp3")
        mock_enricher.image_exists = Mock(return_value=False)
        mock_enricher._translate_for_search = Mock(return_value="The man works here")
        mock_enricher._get_or_generate_image = Mock(return_value="mann_001.jpg")

        # Act
        result = mock_enricher._enrich_artikel_context_record(record)

        # Assert
        assert "article_audio" in result
        assert result["article_audio"] == "[sound:audio_test.mp3]"
        assert "example_audio" in result
        assert result["example_audio"] == "[sound:audio_test.mp3]"
        assert "image" in result
        assert result["image"] == '<img src="mann_001.jpg">'

        # Verify translation was called
        mock_enricher._translate_for_search.assert_called_with("Der Mann arbeitet hier")

    def test_enrich_artikel_gender_record(self, mock_enricher):
        """Test artikel_gender record enrichment."""
        # Arrange
        record = {
            "nominative": "das",
            "example_nom": "Das Haus ist groß",
            "noun_only": "Haus",
            "noun_english": "house",
        }

        # Mock methods
        mock_enricher._get_or_generate_audio = Mock(return_value="audio_test.mp3")
        mock_enricher.image_exists = Mock(return_value=False)
        mock_enricher._translate_for_search = Mock(return_value="The house is big")
        mock_enricher._get_or_generate_image = Mock(return_value="haus_001.jpg")

        # Act
        result = mock_enricher._enrich_artikel_gender_record(record)

        # Assert
        assert "article_audio" in result
        assert result["article_audio"] == "[sound:audio_test.mp3]"
        assert "example_audio" in result
        assert result["example_audio"] == "[sound:audio_test.mp3]"
        assert "image" in result
        assert result["image"] == '<img src="haus_001.jpg">'

        # Verify translation was called
        mock_enricher._translate_for_search.assert_called_with("Das Haus ist groß")

    def test_enrich_noun_article_recognition_record(self, mock_enricher):
        """Test noun_article_recognition record enrichment."""
        # Arrange
        record = {
            "noun_only": "Katze",
            "example": "Die Katze schläft",
            "english_meaning": "cat",
        }

        # Mock methods
        mock_enricher._get_or_generate_audio = Mock(return_value="audio_test.mp3")
        mock_enricher.image_exists = Mock(return_value=False)
        mock_enricher._translate_for_search = Mock(return_value="The cat sleeps")
        mock_enricher._get_or_generate_image = Mock(return_value="katze_001.jpg")

        # Act
        result = mock_enricher._enrich_noun_article_recognition_record(record)

        # Assert
        assert "word_audio" in result
        assert result["word_audio"] == "[sound:audio_test.mp3]"
        assert "image" in result
        assert result["image"] == '<img src="katze_001.jpg">'

        # Verify translation was called
        mock_enricher._translate_for_search.assert_called_with("Die Katze schläft")

    def test_enrich_noun_case_context_record(self, mock_enricher):
        """Test noun_case_context record enrichment."""
        # Arrange
        record = {"noun": "Hund", "example": "Ich sehe den Hund", "english": "dog"}

        # Mock methods
        mock_enricher._get_or_generate_audio = Mock(return_value="audio_test.mp3")
        mock_enricher.image_exists = Mock(return_value=False)
        mock_enricher._translate_for_search = Mock(return_value="I see the dog")
        mock_enricher._get_or_generate_image = Mock(return_value="hund_001.jpg")

        # Act
        result = mock_enricher._enrich_noun_case_context_record(record)

        # Assert
        assert "word_audio" in result
        assert result["word_audio"] == "[sound:audio_test.mp3]"
        assert "example_audio" in result
        assert result["example_audio"] == "[sound:audio_test.mp3]"
        assert "image" in result
        assert result["image"] == '<img src="hund_001.jpg">'

        # Verify translation was called
        mock_enricher._translate_for_search.assert_called_with("Ich sehe den Hund")

    def test_enrich_artikel_cloze_record(self, mock_enricher):
        """Test artikel cloze record enrichment."""
        # Arrange
        record = {
            "text": "{{c1::Der}} Mann arbeitet hier",
            "explanation": "Nominativ case explanation",
        }

        # Mock methods
        mock_enricher._get_or_generate_audio = Mock(return_value="audio_test.mp3")
        mock_enricher.image_exists = Mock(return_value=False)
        mock_enricher._translate_for_search = Mock(return_value="The man works here")
        mock_enricher._get_or_generate_image = Mock(return_value="mann_001.jpg")

        # Act
        result = mock_enricher._enrich_artikel_cloze_record(record)

        # Assert
        assert "audio" in result
        assert result["audio"] == "[sound:audio_test.mp3]"
        assert "image" in result
        assert result["image"] == '<img src="mann_001.jpg">'

        # Verify translation was called with clean text (no cloze markers)
        mock_enricher._translate_for_search.assert_called_with("Der Mann arbeitet hier")

    def test_enrich_artikel_cloze_record_existing_image(self, mock_enricher):
        """Test artikel cloze record with existing image."""
        # Arrange
        record = {
            "text": "{{c1::Das}} Haus ist groß",
            "explanation": "Nominativ case explanation",
        }

        # Mock methods
        mock_enricher._get_or_generate_audio = Mock(return_value="audio_test.mp3")
        mock_enricher.image_exists = Mock(return_value=True)
        mock_enricher._get_image_filename = Mock(return_value="haus_existing.jpg")

        # Act
        result = mock_enricher._enrich_artikel_cloze_record(record)

        # Assert
        assert "audio" in result
        assert result["audio"] == "[sound:audio_test.mp3]"
        assert "image" in result
        assert result["image"] == '<img src="haus_existing.jpg">'

        # Verify existing image was used
        mock_enricher._get_image_filename.assert_called_with("Haus")

    def test_fallback_enrichment_detection(self, mock_enricher):
        """Test that article cards are detected in fallback enrichment."""
        # Test artikel_context detection
        artikel_context_record = {
            "front_text": "Test",
            "gender": "masculine",
            "case": "nominativ",
        }

        with patch.object(
            mock_enricher, "_enrich_artikel_context_record"
        ) as mock_context:
            mock_enricher.enrich_record(artikel_context_record, None)
            mock_context.assert_called_once()

        # Test artikel_gender detection
        artikel_gender_record = {"front_text": "Test", "gender": "feminine"}

        with patch.object(
            mock_enricher, "_enrich_artikel_gender_record"
        ) as mock_gender:
            mock_enricher.enrich_record(artikel_gender_record, None)
            mock_gender.assert_called_once()

        # Test noun_article_recognition detection
        noun_article_record = {"card_type": "noun_article_recognition"}

        with patch.object(
            mock_enricher, "_enrich_noun_article_recognition_record"
        ) as mock_noun_article:
            mock_enricher.enrich_record(noun_article_record, None)
            mock_noun_article.assert_called_once()

        # Test artikel cloze detection
        cloze_record = {"text": "{{c1::Der}} Mann", "explanation": "Test explanation"}

        with patch.object(mock_enricher, "_enrich_artikel_cloze_record") as mock_cloze:
            mock_enricher.enrich_record(cloze_record, None)
            mock_cloze.assert_called_once()
