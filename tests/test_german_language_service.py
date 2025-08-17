"""Unit tests for GermanLanguageService."""

import pytest

from langlearn.models.adjective import Adjective
from langlearn.models.noun import Noun
from langlearn.services.german_language_service import GermanLanguageService


class TestGermanLanguageService:
    """Test GermanLanguageService functionality."""

    @pytest.fixture
    def service(self) -> GermanLanguageService:
        """GermanLanguageService instance for testing."""
        return GermanLanguageService()

    @pytest.fixture
    def sample_adjective(self) -> Adjective:
        """Sample adjective for testing."""
        return Adjective(
            word="schön",
            english="beautiful",
            example="Das Haus ist sehr schön.",
            comparative="schöner",
            superlative="am schönsten",
        )

    @pytest.fixture
    def sample_noun(self) -> Noun:
        """Sample noun for testing."""
        return Noun(
            noun="Haus",
            article="das",
            english="house",
            plural="Häuser",
            example="Das Haus ist groß.",
        )

    def test_extract_context_basic(self, service: GermanLanguageService) -> None:
        """Test basic context extraction."""
        result = service.extract_context_from_sentence(
            sentence="Das Haus ist sehr groß.", word="groß", english_word="big"
        )

        # Should enhance with person context for "sehr groß"
        assert "big" in result or "tall" in result

    def test_extract_context_person(self, service: GermanLanguageService) -> None:
        """Test person context extraction."""
        result = service.extract_context_from_sentence(
            sentence="Er ist sehr groß.", word="groß", english_word="tall"
        )

        # Should detect person context and enhance accordingly
        assert "person" in result or "tall" in result

    def test_extract_context_activity(self, service: GermanLanguageService) -> None:
        """Test activity context extraction."""
        result = service.extract_context_from_sentence(
            sentence="Das Kind spielt im Park.", word="Kind", english_word="child"
        )

        # Should detect activity context - the logic detects person first, then activity
        assert "child" in result

    def test_extract_context_empty_sentence(
        self, service: GermanLanguageService
    ) -> None:
        """Test handling of empty sentence."""
        result = service.extract_context_from_sentence(
            sentence="", word="test", english_word="test"
        )

        assert result == "test"

    def test_get_combined_adjective_audio_text(
        self, service: GermanLanguageService, sample_adjective: Adjective
    ) -> None:
        """Test combined adjective audio text generation."""
        result = service.get_combined_adjective_audio_text(sample_adjective)

        expected = "schön, schöner, am schönsten"
        assert result == expected

    def test_get_combined_noun_audio_text(
        self, service: GermanLanguageService, sample_noun: Noun
    ) -> None:
        """Test combined noun audio text generation."""
        result = service.get_combined_noun_audio_text(sample_noun)

        expected = "das Haus, die Häuser"
        assert result == expected

    def test_get_conceptual_image_search_adverb(
        self, service: GermanLanguageService
    ) -> None:
        """Test conceptual image search for adverbs."""
        result = service.get_conceptual_image_search_terms(
            word_type="adverb", word="heute", english="today"
        )

        # Should return calendar-related search terms
        assert "calendar" in result
        assert "today" in result

    def test_get_conceptual_image_search_negation(
        self, service: GermanLanguageService
    ) -> None:
        """Test conceptual image search for negations."""
        result = service.get_conceptual_image_search_terms(
            word_type="negation", word="nicht", english="not"
        )

        # Should return prohibition-related search terms
        assert "stop" in result or "prohibition" in result

    def test_enhance_person_context_tall(self, service: GermanLanguageService) -> None:
        """Test person context enhancement for tall."""
        result = service._enhance_person_context("groß", "tall", "")
        assert result == "tall person man"

    def test_enhance_person_context_young(self, service: GermanLanguageService) -> None:
        """Test person context enhancement for young."""
        result = service._enhance_person_context("jung", "young", "")
        assert result == "young person"

    def test_enhance_activity_context_child_playing(
        self, service: GermanLanguageService
    ) -> None:
        """Test activity context for child playing."""
        result = service._enhance_activity_context("Kind", "child", "spielt")
        assert result == "child playing playground"

    def test_enhance_location_context_house_small(
        self, service: GermanLanguageService
    ) -> None:
        """Test location context for small house."""
        result = service._enhance_location_context("Haus", "house", "klein")
        assert result == "small house home"
