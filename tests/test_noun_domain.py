"""Tests for Noun domain model behavior."""

import pytest

from langlearn.exceptions import MediaGenerationError
from langlearn.languages.german.models.noun import Noun


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
            related="",
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
            related="",
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
            example="Die Katze schläft.",
            related="",
        )
        assert concrete.is_concrete() is True

        # Abstract nouns by suffix
        abstract_suffix = Noun(
            noun="Freiheit",
            article="die",
            english="freedom",
            plural="",
            example="Die Freiheit ist wichtig.",
            related="",
        )
        assert abstract_suffix.is_concrete() is False

        # Abstract nouns by word list
        abstract_word = Noun(
            noun="Liebe",
            article="die",
            english="love",
            plural="",
            example="Die Liebe ist schön.",
            related="",
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
                example="Das ist ein Test.",
                related="",
            )
            assert noun.is_concrete() == expected, (
                f"{noun_text} should be {'concrete' if expected else 'abstract'}"
            )

    def test_fallback_search_terms_concrete(self) -> None:
        """Test fallback search terms for concrete nouns use direct translation."""
        from unittest.mock import Mock

        noun = Noun(
            noun="Katze",
            article="die",
            english="cat",
            plural="Katzen",
            example="Die Katze schläft.",
            related="",
        )
        # Test strategy fails fast when AI service fails
        mock_service = Mock()
        mock_service.generate_image_query.side_effect = Exception("AI failed")
        strategy = noun.get_image_search_strategy(mock_service)

        with pytest.raises(
            MediaGenerationError,
            match="Failed to generate image search for noun 'Katze'.*AI failed",
        ):
            strategy()

    def test_fallback_search_terms_abstract(self) -> None:
        """Test fallback search terms for abstract concepts use direct translation."""
        from unittest.mock import Mock

        # Test abstract noun fallback when AI service fails
        love_noun = Noun(
            noun="Liebe",
            article="die",
            english="love",
            plural="",
            example="Die Liebe ist schön.",
            related="",
        )
        mock_service = Mock()
        mock_service.generate_image_query.side_effect = Exception("AI failed")
        strategy = love_noun.get_image_search_strategy(mock_service)

        with pytest.raises(
            MediaGenerationError,
            match="Failed to generate image search for noun 'Liebe'.*AI failed",
        ):
            strategy()

        freedom_noun = Noun(
            noun="Freiheit",
            article="die",
            english="freedom",
            plural="",
            example="Die Freiheit ist wichtig.",
            related="",
        )
        strategy = freedom_noun.get_image_search_strategy(mock_service)

        with pytest.raises(
            MediaGenerationError,
            match="Failed to generate image search for noun 'Freiheit'.*AI failed",
        ):
            strategy()

        # Test fail-fast for any abstract concept
        abstract_noun = Noun(
            noun="Weisheit",
            article="die",
            english="wisdom",
            plural="",
            example="Die Weisheit kommt mit dem Alter.",
            related="",
        )
        strategy = abstract_noun.get_image_search_strategy(mock_service)

        with pytest.raises(
            MediaGenerationError,
            match="Failed to generate image search for noun 'Weisheit'.*AI failed",
        ):
            strategy()

    def test_domain_methods_integration(self) -> None:
        """Test that domain methods work together correctly."""
        # Test a concrete noun
        concrete_noun = Noun(
            noun="Hund",
            article="der",
            english="dog",
            plural="Hunde",
            example="Der Hund bellt laut.",
            related="",
        )

        # All methods should work
        assert concrete_noun.is_concrete() is True
        assert concrete_noun.get_combined_audio_text() == "der Hund, die Hunde"
        # Test fail-fast behavior when AI service fails
        from unittest.mock import Mock

        mock_service = Mock()
        mock_service.generate_image_query.side_effect = Exception("AI failed")
        strategy = concrete_noun.get_image_search_strategy(mock_service)

        with pytest.raises(
            MediaGenerationError,
            match="Failed to generate image search for noun 'Hund'.*AI failed",
        ):
            strategy()

        # Test an abstract noun
        abstract_noun = Noun(
            noun="Hoffnung",
            article="die",
            english="hope",
            plural="",
            example="Die Hoffnung stirbt zuletzt.",
            related="",
        )

        assert abstract_noun.is_concrete() is False
        assert abstract_noun.get_combined_audio_text() == "die Hoffnung, die "
        # Test abstract noun also fails fast
        strategy = abstract_noun.get_image_search_strategy(mock_service)

        with pytest.raises(
            MediaGenerationError,
            match=r"Failed to generate image search for noun 'Hoffnung'.*AI failed",
        ):
            strategy()

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
            example=f"{article.capitalize()} {noun} ist gut.",
            related="",
        )
        assert noun_obj.get_combined_audio_text() == expected_audio

    def test_empty_noun_handling(self) -> None:
        """Test edge cases with empty or invalid data."""
        # Empty required fields should raise validation error
        with pytest.raises(ValueError, match="Required field 'noun' cannot be empty"):
            Noun(
                noun="",
                article="der",
                english="test",
                plural="",
                example="Test example",
                related="",
            )

        with pytest.raises(
            ValueError, match="Required field 'example' cannot be empty"
        ):
            Noun(
                noun="Test",
                article="der",
                english="test",
                plural="",
                example="",
                related="",
            )

        # But plural and related can be empty (valid for collective nouns)
        valid_noun = Noun(
            noun="Wasser",
            article="das",
            english="water",
            plural="",  # Collective noun - no plural
            example="Das Wasser ist kalt.",
            related="",  # Optional field
        )
        assert valid_noun.is_concrete() is True
        assert valid_noun.get_combined_audio_text() == "das Wasser, die "
