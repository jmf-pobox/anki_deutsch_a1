"""Tests for Adjective domain model behavior."""

import pytest

from langlearn.models.adjective import Adjective


class TestAdjectiveDomainBehavior:
    """Test Adjective domain model rich behavior and German grammar logic."""

    def test_get_combined_audio_text_all_forms(self) -> None:
        """Test combined audio includes base, comparative, and superlative."""
        adjective = Adjective(
            word="schön",
            english="beautiful",
            example="Das Haus ist schön.",
            comparative="schöner",
            superlative="am schönsten",
        )

        result = adjective.get_combined_audio_text()
        assert result == "schön, schöner, am schönsten"

    def test_get_combined_audio_text_partial_forms(self) -> None:
        """Test combined audio with missing superlative."""
        adjective = Adjective(
            word="schnell",
            english="fast",
            example="Er läuft schnell.",
            comparative="schneller",
            superlative="",  # Empty superlative
        )

        result = adjective.get_combined_audio_text()
        assert result == "schnell, schneller"

    def test_get_combined_audio_text_only_base(self) -> None:
        """Test combined audio with only base form."""
        adjective = Adjective(
            word="gut",
            english="good",
            example="Das ist gut.",
            comparative="",  # Empty comparative
            superlative="",  # Empty superlative
        )

        result = adjective.get_combined_audio_text()
        assert result == "gut"

    def test_existing_validation_methods_still_work(self) -> None:
        """Test that existing validation methods are not broken."""
        # Test regular comparative validation
        regular = Adjective(
            word="schön",
            english="beautiful",
            example="Das Haus ist schön.",
            comparative="schöner",
            superlative="am schönsten",
        )
        assert regular.validate_comparative() is True
        assert regular.validate_superlative() is True

        # Test irregular comparative validation
        irregular = Adjective(
            word="gut",
            english="good",
            example="Das Essen ist gut.",
            comparative="besser",
            superlative="am besten",
        )
        assert irregular.validate_comparative() is True
        assert irregular.validate_superlative() is True

        # Test umlaut changes
        umlaut = Adjective(
            word="alt",
            english="old",
            example="Der Mann ist alt.",
            comparative="älter",
            superlative="am ältesten",
        )
        assert umlaut.validate_comparative() is True
        assert umlaut.validate_superlative() is True

    def test_domain_methods_with_real_adjectives(self) -> None:
        """Test domain methods with real German adjectives."""
        test_adjectives = [
            {
                "word": "klein",
                "comparative": "kleiner",
                "superlative": "am kleinsten",
                "expected_audio": "klein, kleiner, am kleinsten",
            },
            {
                "word": "schön",
                "comparative": "schöner",
                "superlative": "am schönsten",
                "expected_audio": "schön, schöner, am schönsten",
            },
            {
                "word": "jung",
                "comparative": "jünger",
                "superlative": "am jüngsten",
                "expected_audio": "jung, jünger, am jüngsten",
            },
        ]

        for adj_data in test_adjectives:
            adjective = Adjective(
                word=adj_data["word"],
                english="test",
                example="Test sentence.",
                comparative=adj_data["comparative"],
                superlative=adj_data["superlative"],
            )

            # Test rich domain behavior
            assert adjective.get_combined_audio_text() == adj_data["expected_audio"]

            # Test validation still works
            assert adjective.validate_comparative() is True
            assert adjective.validate_superlative() is True

    @pytest.mark.parametrize(
        "word,comparative,superlative,expected_audio",
        [
            ("schön", "schöner", "am schönsten", "schön, schöner, am schönsten"),
            ("gut", "besser", "am besten", "gut, besser, am besten"),
            ("viel", "mehr", "am meisten", "viel, mehr, am meisten"),
            ("hoch", "höher", "am höchsten", "hoch, höher, am höchsten"),
            ("nah", "näher", "am nächsten", "nah, näher, am nächsten"),
            ("schnell", "schneller", "", "schnell, schneller"),  # No superlative
            ("laut", "", "", "laut"),  # Only base form
        ],
    )
    def test_audio_generation_patterns(
        self, word: str, comparative: str, superlative: str, expected_audio: str
    ) -> None:
        """Test various German adjective audio generation patterns."""
        adjective = Adjective(
            word=word,
            english="test",
            example="Test sentence.",
            comparative=comparative,
            superlative=superlative,
        )
        assert adjective.get_combined_audio_text() == expected_audio

    def test_integration_with_validation(self) -> None:
        """Test that rich domain behavior integrates well with validation."""
        # Create a valid adjective
        valid_adj = Adjective(
            word="schön",
            english="beautiful",
            example="Das Haus ist sehr schön.",
            comparative="schöner",
            superlative="am schönsten",
        )

        # Both validation and rich behavior should work
        assert valid_adj.validate_comparative() is True
        assert valid_adj.validate_superlative() is True
        assert valid_adj.get_combined_audio_text() == "schön, schöner, am schönsten"

        # Create an invalid adjective (for testing validation)
        invalid_adj = Adjective(
            word="gut",
            english="good",
            example="Das Essen ist gut.",
            comparative="guter",  # Invalid - should be "besser"
            superlative="am besten",
        )

        # Validation should fail, but audio generation should still work
        assert invalid_adj.validate_comparative() is False
        assert invalid_adj.validate_superlative() is True  # Superlative is correct
        assert invalid_adj.get_combined_audio_text() == "gut, guter, am besten"
