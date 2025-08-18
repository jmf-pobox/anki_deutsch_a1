"""Tests for Noun domain model behavior."""

import pytest

from langlearn.models.noun import Noun


class TestNounDomainBehavior:
    """Test Noun domain model rich behavior and German language logic."""

    def test_get_combined_audio_text_with_article_in_singular(self) -> None:
        """Test combined audio includes article + singular + plural."""
        noun = Noun(
            noun="Katze",
            article="die",
            english="cat",
            plural="Katzen",
            example="Die Katze schläft.",
            word_audio="",
            example_audio="",
            image_path="",
        )

        result = noun.get_combined_audio_text()
        assert result == "die Katze, die Katzen"

    def test_get_combined_audio_text_with_article_in_plural(self) -> None:
        """Test combined audio when plural already includes article."""
        noun = Noun(
            noun="Stuhl",
            article="der",
            english="chair",
            plural="die Stühle",  # Already includes article
            example="Der Stuhl ist bequem.",
            word_audio="",
            example_audio="",
            image_path="",
        )

        result = noun.get_combined_audio_text()
        assert result == "der Stuhl, die Stühle"

    def test_is_concrete_vs_abstract_nouns(self) -> None:
        """Test concrete noun detection using German language patterns."""
        # Concrete nouns
        concrete = Noun(
            noun="Katze",
            article="die",
            english="cat",
            plural="Katzen",
            example="",
            word_audio="",
            example_audio="",
            image_path="",
        )
        assert concrete.is_concrete() is True

        # Abstract nouns by suffix
        abstract_suffix = Noun(
            noun="Freiheit",
            article="die",
            english="freedom",
            plural="",
            example="",
            word_audio="",
            example_audio="",
            image_path="",
        )
        assert abstract_suffix.is_concrete() is False

        # Abstract nouns by word list
        abstract_word = Noun(
            noun="Liebe",
            article="die",
            english="love",
            plural="",
            example="",
            word_audio="",
            example_audio="",
            image_path="",
        )
        assert abstract_word.is_concrete() is False

    def test_is_concrete_with_german_suffixes(self) -> None:
        """Test abstract noun detection using German suffixes."""
        test_cases = [
            # Abstract suffixes
            ("Schönheit", False),  # -heit suffix
            ("Fröhlichkeit", False),  # -keit suffix
            ("Bildung", False),  # -ung suffix
            ("Information", False),  # -ion suffix
            ("Freundschaft", False),  # -schaft suffix
            # Concrete indicators
            ("Kätzchen", True),  # -chen diminutive
            ("Häuschen", True),  # -chen diminutive
            ("Werkzeug", True),  # -zeug indicator
        ]

        for noun_text, expected in test_cases:
            noun = Noun(
                noun=noun_text,
                article="die",
                english="test",
                plural="",
                example="",
                word_audio="",
                example_audio="",
                image_path="",
            )
            assert noun.is_concrete() == expected, (
                f"{noun_text} should be {'concrete' if expected else 'abstract'}"
            )

    def test_get_image_search_terms_concrete(self) -> None:
        """Test image search terms for concrete nouns use direct translation."""
        noun = Noun(
            noun="Katze",
            article="die",
            english="cat",
            plural="Katzen",
            example="",
            word_audio="",
            example_audio="",
            image_path="",
        )
        assert noun.get_image_search_terms() == "cat"

    def test_get_image_search_terms_abstract(self) -> None:
        """Test enhanced search terms for abstract concepts."""
        # Test specific concept mappings
        love_noun = Noun(
            noun="Liebe",
            article="die",
            english="love",
            plural="",
            example="",
            word_audio="",
            example_audio="",
            image_path="",
        )
        result = love_noun.get_image_search_terms()
        assert "heart symbol" in result and "family together" in result

        freedom_noun = Noun(
            noun="Freiheit",
            article="die",
            english="freedom",
            plural="",
            example="",
            word_audio="",
            example_audio="",
            image_path="",
        )
        result = freedom_noun.get_image_search_terms()
        assert "person celebrating independence" in result

        # Test fallback for unmapped abstract concepts
        abstract_noun = Noun(
            noun="Weisheit",
            article="die",
            english="wisdom",
            plural="",
            example="",
            word_audio="",
            example_audio="",
            image_path="",
        )
        result = abstract_noun.get_image_search_terms()
        assert result == "wisdom concept symbol"

    def test_domain_methods_integration(self) -> None:
        """Test that domain methods work together correctly."""
        # Test a concrete noun
        concrete_noun = Noun(
            noun="Hund",
            article="der",
            english="dog",
            plural="Hunde",
            example="Der Hund bellt laut.",
            word_audio="",
            example_audio="",
            image_path="",
        )

        # All methods should work
        assert concrete_noun.is_concrete() is True
        assert concrete_noun.get_combined_audio_text() == "der Hund, die Hunde"
        assert concrete_noun.get_image_search_terms() == "dog"

        # Test an abstract noun
        abstract_noun = Noun(
            noun="Hoffnung",
            article="die",
            english="hope",
            plural="",
            example="Die Hoffnung stirbt zuletzt.",
            word_audio="",
            example_audio="",
            image_path="",
        )

        assert abstract_noun.is_concrete() is False
        assert abstract_noun.get_combined_audio_text() == "die Hoffnung, die "
        assert "sunrise bright future" in abstract_noun.get_image_search_terms()

    @pytest.mark.parametrize(
        "noun,article,english,plural,expected_audio",
        [
            ("Katze", "die", "cat", "Katzen", "die Katze, die Katzen"),
            ("Hund", "der", "dog", "die Hunde", "der Hund, die Hunde"),
            ("Buch", "das", "book", "Bücher", "das Buch, die Bücher"),
            ("Auto", "das", "car", "die Autos", "das Auto, die Autos"),
        ],
    )
    def test_combined_audio_patterns(
        self, noun: str, article: str, english: str, plural: str, expected_audio: str
    ) -> None:
        """Test various German noun audio generation patterns."""
        noun_obj = Noun(
            noun=noun,
            article=article,
            english=english,
            plural=plural,
            example="",
            word_audio="",
            example_audio="",
            image_path="",
        )
        assert noun_obj.get_combined_audio_text() == expected_audio

    def test_empty_noun_handling(self) -> None:
        """Test edge cases with empty or invalid data."""
        # Empty noun should be considered concrete by default heuristic
        empty_noun = Noun(
            noun="",
            article="der",
            english="",
            plural="",
            example="",
            word_audio="",
            example_audio="",
            image_path="",
        )
        assert empty_noun.is_concrete() is False  # Empty noun is not concrete

        # But other methods should handle gracefully
        assert empty_noun.get_combined_audio_text() == "der , die "
        assert empty_noun.get_image_search_terms() == ""  # Direct English translation
