"""Tests for GermanExplanationFactory.

This module provides comprehensive test coverage for the German explanation factory,
which generates German-language grammatical explanations for article cloze cards.

Test coverage includes:
- Case explanation generation (gender + case combinations)
- Article type explanations (bestimmt, unbestimmt, verneinend)
- Gender recognition explanations
- German case name conversion
- Edge cases and error handling
"""

import pytest

from langlearn.services.german_explanation_factory import GermanExplanationFactory


class TestGermanExplanationFactory:
    """Test GermanExplanationFactory functionality."""

    @pytest.fixture
    def factory(self) -> GermanExplanationFactory:
        """Create GermanExplanationFactory instance for testing."""
        return GermanExplanationFactory()

    def test_initialization(self, factory: GermanExplanationFactory) -> None:
        """Test factory initialization."""
        assert factory is not None
        # Verify internal dictionaries are populated
        assert len(factory._case_explanations) == 4
        assert len(factory._gender_names) == 3
        assert len(factory._article_type_names) == 3

    def test_create_case_explanation_masculine_nominative(
        self, factory: GermanExplanationFactory
    ) -> None:
        """Test masculine nominative case explanation."""
        result = factory.create_case_explanation("masculine", "nominative", "der")
        expected = "der - Maskulin Nominativ (wer/was? - Subjekt des Satzes)"
        assert result == expected

    def test_create_case_explanation_masculine_accusative(
        self, factory: GermanExplanationFactory
    ) -> None:
        """Test masculine accusative case explanation."""
        result = factory.create_case_explanation("masculine", "accusative", "den")
        expected = "den - Maskulin Akkusativ (wen/was? - direktes Objekt)"
        assert result == expected

    def test_create_case_explanation_masculine_dative(
        self, factory: GermanExplanationFactory
    ) -> None:
        """Test masculine dative case explanation."""
        result = factory.create_case_explanation("masculine", "dative", "dem")
        expected = "dem - Maskulin Dativ (wem? - indirektes Objekt)"
        assert result == expected

    def test_create_case_explanation_masculine_genitive(
        self, factory: GermanExplanationFactory
    ) -> None:
        """Test masculine genitive case explanation."""
        result = factory.create_case_explanation("masculine", "genitive", "des")
        expected = (
            "des - Maskulin Genitiv (wessen? - Besitz und bestimmte Präpositionen)"
        )
        assert result == expected

    def test_create_case_explanation_feminine_cases(
        self, factory: GermanExplanationFactory
    ) -> None:
        """Test feminine case explanations."""
        test_cases = [
            (
                "nominative",
                "die",
                "die - Feminin Nominativ (wer/was? - Subjekt des Satzes)",
            ),
            (
                "accusative",
                "die",
                "die - Feminin Akkusativ (wen/was? - direktes Objekt)",
            ),
            ("dative", "der", "der - Feminin Dativ (wem? - indirektes Objekt)"),
            (
                "genitive",
                "der",
                "der - Feminin Genitiv (wessen? - Besitz und bestimmte Präpositionen)",
            ),
        ]

        for case, article, expected in test_cases:
            result = factory.create_case_explanation("feminine", case, article)
            assert result == expected

    def test_create_case_explanation_neuter_cases(
        self, factory: GermanExplanationFactory
    ) -> None:
        """Test neuter case explanations."""
        test_cases = [
            (
                "nominative",
                "das",
                "das - Neutrum Nominativ (wer/was? - Subjekt des Satzes)",
            ),
            (
                "accusative",
                "das",
                "das - Neutrum Akkusativ (wen/was? - direktes Objekt)",
            ),
            ("dative", "dem", "dem - Neutrum Dativ (wem? - indirektes Objekt)"),
            (
                "genitive",
                "des",
                "des - Neutrum Genitiv (wessen? - Besitz und bestimmte Präpositionen)",
            ),
        ]

        for case, article, expected in test_cases:
            result = factory.create_case_explanation("neuter", case, article)
            assert result == expected

    def test_create_case_explanation_unknown_gender(
        self, factory: GermanExplanationFactory
    ) -> None:
        """Test case explanation with unknown gender."""
        result = factory.create_case_explanation("unknown", "nominative", "x")
        expected = "x - Unknown Nominativ (wer/was? - Subjekt des Satzes)"
        assert result == expected

    def test_create_case_explanation_unknown_case(
        self, factory: GermanExplanationFactory
    ) -> None:
        """Test case explanation with unknown case."""
        result = factory.create_case_explanation("masculine", "instrumental", "xyz")
        expected = "xyz - Maskulin Instrumental (instrumental)"
        assert result == expected

    def test_create_article_type_explanation_bestimmt(
        self, factory: GermanExplanationFactory
    ) -> None:
        """Test definite article type explanation."""
        result = factory.create_article_type_explanation("bestimmt")
        expected = "bestimmter Artikel"
        assert result == expected

    def test_create_article_type_explanation_unbestimmt(
        self, factory: GermanExplanationFactory
    ) -> None:
        """Test indefinite article type explanation."""
        result = factory.create_article_type_explanation("unbestimmt")
        expected = "unbestimmter Artikel"
        assert result == expected

    def test_create_article_type_explanation_verneinend(
        self, factory: GermanExplanationFactory
    ) -> None:
        """Test negative article type explanation."""
        result = factory.create_article_type_explanation("verneinend")
        expected = "verneinender Artikel"
        assert result == expected

    def test_create_article_type_explanation_unknown(
        self, factory: GermanExplanationFactory
    ) -> None:
        """Test unknown article type explanation."""
        result = factory.create_article_type_explanation("unknown")
        expected = "unknown"
        assert result == expected

    def test_create_gender_recognition_explanation_masculine(
        self, factory: GermanExplanationFactory
    ) -> None:
        """Test masculine gender recognition explanation."""
        result = factory.create_gender_recognition_explanation("masculine")
        expected = "Maskulin - Geschlecht erkennen"
        assert result == expected

    def test_create_gender_recognition_explanation_feminine(
        self, factory: GermanExplanationFactory
    ) -> None:
        """Test feminine gender recognition explanation."""
        result = factory.create_gender_recognition_explanation("feminine")
        expected = "Feminin - Geschlecht erkennen"
        assert result == expected

    def test_create_gender_recognition_explanation_neuter(
        self, factory: GermanExplanationFactory
    ) -> None:
        """Test neuter gender recognition explanation."""
        result = factory.create_gender_recognition_explanation("neuter")
        expected = "Neutrum - Geschlecht erkennen"
        assert result == expected

    def test_create_gender_recognition_explanation_unknown(
        self, factory: GermanExplanationFactory
    ) -> None:
        """Test unknown gender recognition explanation."""
        result = factory.create_gender_recognition_explanation("unknown")
        expected = "Unknown - Geschlecht erkennen"
        assert result == expected

    def test_get_german_case_name_all_cases(
        self, factory: GermanExplanationFactory
    ) -> None:
        """Test German case name conversion for all standard cases."""
        test_cases = [
            ("nominative", "Nominativ"),
            ("accusative", "Akkusativ"),
            ("dative", "Dativ"),
            ("genitive", "Genitiv"),
        ]

        for english_case, german_case in test_cases:
            result = factory._get_german_case_name(english_case)
            assert result == german_case

    def test_get_german_case_name_unknown_case(
        self, factory: GermanExplanationFactory
    ) -> None:
        """Test German case name conversion for unknown case."""
        result = factory._get_german_case_name("instrumental")
        expected = "Instrumental"  # Title case fallback
        assert result == expected

    def test_get_german_case_name_empty_string(
        self, factory: GermanExplanationFactory
    ) -> None:
        """Test German case name conversion for empty string."""
        result = factory._get_german_case_name("")
        expected = ""  # Title case of empty string is empty
        assert result == expected

    def test_case_explanations_content(self, factory: GermanExplanationFactory) -> None:
        """Test that case explanations contain expected German content."""
        explanations = factory._case_explanations

        # Verify German question words
        assert "wer/was?" in explanations["nominative"]
        assert "wen/was?" in explanations["accusative"]
        assert "wem?" in explanations["dative"]
        assert "wessen?" in explanations["genitive"]

        # Verify German descriptions
        assert "Subjekt" in explanations["nominative"]
        assert "direktes Objekt" in explanations["accusative"]
        assert "indirektes Objekt" in explanations["dative"]
        assert "Besitz" in explanations["genitive"]

    def test_gender_names_content(self, factory: GermanExplanationFactory) -> None:
        """Test that gender names are properly translated to German."""
        genders = factory._gender_names

        assert genders["masculine"] == "Maskulin"
        assert genders["feminine"] == "Feminin"
        assert genders["neuter"] == "Neutrum"

    def test_article_type_names_content(
        self, factory: GermanExplanationFactory
    ) -> None:
        """Test that article type names are in German."""
        article_types = factory._article_type_names

        assert article_types["bestimmt"] == "bestimmter Artikel"
        assert article_types["unbestimmt"] == "unbestimmter Artikel"
        assert article_types["verneinend"] == "verneinender Artikel"

    def test_edge_case_empty_values(self, factory: GermanExplanationFactory) -> None:
        """Test handling of empty string inputs."""
        # Empty gender should still work
        result = factory.create_case_explanation("", "nominative", "x")
        expected = "x -  Nominativ (wer/was? - Subjekt des Satzes)"
        assert result == expected

        # Empty article should still work
        result = factory.create_case_explanation("masculine", "accusative", "")
        expected = " - Maskulin Akkusativ (wen/was? - direktes Objekt)"
        assert result == expected

    def test_comprehensive_integration_example(
        self, factory: GermanExplanationFactory
    ) -> None:
        """Test comprehensive example matching expected usage."""
        # This should match the format expected in article cloze cards
        result = factory.create_case_explanation("masculine", "accusative", "den")

        # Verify format: "article - Gender Case (question - function)"
        assert result.startswith("den - ")
        assert "Maskulin Akkusativ" in result
        assert "wen/was?" in result
        assert "direktes Objekt" in result

        # Full expected format
        expected = "den - Maskulin Akkusativ (wen/was? - direktes Objekt)"
        assert result == expected
