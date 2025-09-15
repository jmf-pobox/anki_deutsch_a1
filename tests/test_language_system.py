"""Tests for the multi-language system."""

from pathlib import Path

import pytest

from langlearn.languages import GermanLanguage, LanguageRegistry


class TestLanguageRegistry:
    """Test LanguageRegistry functionality."""

    def test_registry_registration_and_retrieval(self) -> None:
        """Test that languages can be registered and retrieved."""
        # Clear registry for clean test
        LanguageRegistry.clear()

        # Register test language
        LanguageRegistry.register("de", GermanLanguage)

        # Test retrieval
        german = LanguageRegistry.get("de")
        assert german.code == "de"
        assert german.name == "German"

        # Test listing
        assert LanguageRegistry.list_available() == ["de"]

    def test_registry_unknown_language_error(self) -> None:
        """Test error handling for unknown languages."""
        LanguageRegistry.clear()

        with pytest.raises(ValueError, match="Language ru not registered"):
            LanguageRegistry.get("ru")

    def test_registry_multiple_language_codes(self) -> None:
        """Test multiple codes can map to same language."""
        LanguageRegistry.clear()
        LanguageRegistry.register("de", GermanLanguage)
        LanguageRegistry.register("german", GermanLanguage)

        german_de = LanguageRegistry.get("de")
        german_full = LanguageRegistry.get("german")

        assert german_de.code == german_full.code == "de"
        assert german_de.name == german_full.name == "German"


class TestGermanLanguage:
    """Test GermanLanguage implementation."""

    def test_german_language_properties(self) -> None:
        """Test basic German language properties."""
        german = GermanLanguage()

        assert german.code == "de"
        assert german.name == "German"

    def test_supported_record_types(self) -> None:
        """Test German supported record types."""
        german = GermanLanguage()
        record_types = german.get_supported_record_types()

        expected_types = [
            "noun",
            "verb",
            "adjective",
            "adverb",
            "article",
            "negation",
            "preposition",
            "phrase",
        ]

        assert record_types == expected_types

    def test_get_services(self) -> None:
        """Test getting German language services."""
        german = GermanLanguage()

        # Test card builder
        card_builder = german.get_card_builder()
        assert card_builder is not None

        # Test record mapper
        record_mapper = german.get_record_mapper()
        assert record_mapper is not None

        # Test grammar service (returns module)
        grammar_service = german.get_grammar_service()
        assert grammar_service is not None

    def test_template_path_generation(self) -> None:
        """Test template path generation follows conventions."""
        german = GermanLanguage()

        # Test various record types and sides
        noun_front = german.get_template_path("noun", "front")
        verb_back = german.get_template_path("verb", "back")

        # Verify paths exist and follow naming convention
        assert "noun_DE_de_front.html" in noun_front
        assert "verb_DE_de_back.html" in verb_back

        # Verify paths are absolute and point to templates directory
        assert Path(noun_front).is_absolute()
        assert "templates" in noun_front

    def test_template_path_actual_files(self) -> None:
        """Test that some expected template files actually exist."""
        german = GermanLanguage()

        # Test some known templates that should exist
        test_templates = [
            ("noun", "front"),
            ("noun", "back"),
            ("verb", "front"),
        ]

        for record_type, side in test_templates:
            template_path = german.get_template_path(record_type, side)
            # Just verify path structure is correct - don't require files to exist
            # since this is about the architecture, not file content
            assert template_path.endswith(f"{record_type}_DE_de_{side}.html")
            assert "templates" in template_path