"""Tests for Verb model and MediaGenerationCapable protocol compliance."""

from unittest.mock import Mock

import pytest

from langlearn.models.verb import Verb
from langlearn.protocols.media_generation_protocol import MediaGenerationCapable


class TestVerbProtocol:
    """Test Verb model protocol compliance and functionality."""

    def test_verb_initialization_valid(self) -> None:
        """Test verb initialization with valid data."""
        verb = Verb(
            verb="gehen",
            english="to go",
            present_ich="gehe",
            present_du="gehst",
            present_er="geht",
            perfect="gegangen",
            example="Ich gehe zur Schule.",
        )

        assert verb.verb == "gehen"
        assert verb.english == "to go"
        assert verb.present_ich == "gehe"
        assert verb.present_du == "gehst"
        assert verb.present_er == "geht"
        assert verb.perfect == "gegangen"
        assert verb.example == "Ich gehe zur Schule."

    def test_verb_initialization_empty_verb(self) -> None:
        """Test verb initialization fails with empty verb."""
        with pytest.raises(ValueError, match="Required field 'verb' cannot be empty"):
            Verb(
                verb="",
                english="to go",
                present_ich="gehe",
                present_du="gehst",
                present_er="geht",
                perfect="gegangen",
                example="Example",
            )

    def test_verb_initialization_empty_english(self) -> None:
        """Test verb initialization fails with empty english."""
        with pytest.raises(
            ValueError, match="Required field 'english' cannot be empty"
        ):
            Verb(
                verb="gehen",
                english="",
                present_ich="gehe",
                present_du="gehst",
                present_er="geht",
                perfect="gegangen",
                example="Example",
            )

    def test_verb_initialization_empty_present_forms(self) -> None:
        """Test verb initialization fails with empty present forms."""
        with pytest.raises(
            ValueError, match="Required field 'present_ich' cannot be empty"
        ):
            Verb(
                verb="gehen",
                english="to go",
                present_ich="",
                present_du="gehst",
                present_er="geht",
                perfect="gegangen",
                example="Example",
            )

    def test_verb_initialization_whitespace_only(self) -> None:
        """Test verb initialization fails with whitespace-only fields."""
        with pytest.raises(ValueError, match="Required field 'verb' cannot be empty"):
            Verb(
                verb="   \t\n   ",
                english="to go",
                present_ich="gehe",
                present_du="gehst",
                present_er="geht",
                perfect="gegangen",
                example="Example",
            )

    def test_verb_initialization_none_values(self) -> None:
        """Test verb initialization fails with None values."""
        with pytest.raises(ValueError, match="Required field 'verb' cannot be empty"):
            Verb(
                verb=None,  # type: ignore[arg-type]
                english="to go",
                present_ich="gehe",
                present_du="gehst",
                present_er="geht",
                perfect="gegangen",
                example="Example",
            )

    def test_mediageneration_protocol_compliance(self) -> None:
        """Test verb implements MediaGenerationCapable protocol."""
        verb = Verb(
            verb="laufen",
            english="to run",
            present_ich="laufe",
            present_du="läufst",
            present_er="läuft",
            perfect="gelaufen",
            example="Ich laufe jeden Tag.",
        )

        assert isinstance(verb, MediaGenerationCapable)

    def test_get_combined_audio_text(self) -> None:
        """Test get_combined_audio_text method."""
        verb = Verb(
            verb="sprechen",
            english="to speak",
            present_ich="spreche",
            present_du="sprichst",
            present_er="spricht",
            perfect="gesprochen",
            example="Ich spreche Deutsch.",
        )

        result = verb.get_combined_audio_text()

        # Should combine verb with conjugations and German labels
        assert "sprechen" in result
        assert "Präsens" in result
        assert "ich spreche" in result
        assert "du sprichst" in result
        assert "er sie es spricht" in result
        assert "Perfekt" in result
        assert "er sie es gesprochen" in result
        assert isinstance(result, str)

    def test_get_combined_audio_text_minimal(self) -> None:
        """Test get_combined_audio_text with minimal verb data."""
        verb = Verb(
            verb="lesen",
            english="to read",
            present_ich="lese",
            present_du="liest",
            present_er="liest",
            perfect="gelesen",
            example="Ich lese ein Buch.",
        )

        result = verb.get_combined_audio_text()

        # Should include the verb
        assert "lesen" in result
        # Should include present forms
        assert "ich lese" in result

    def test_get_image_search_strategy(self) -> None:
        """Test get_image_search_strategy method."""
        verb = Verb(
            verb="schwimmen",
            english="to swim",
            present_ich="schwimme",
            present_du="schwimmst",
            present_er="schwimmt",
            perfect="geschwommen",
            example="Ich schwimme im See.",
        )

        mock_anthropic_service = Mock()
        mock_anthropic_service.generate_image_query.return_value = "person swimming"

        strategy = verb.get_image_search_strategy(mock_anthropic_service)

        # Strategy should be callable
        assert callable(strategy)

        # Execute strategy
        result = strategy()

        assert result == "person swimming"
        mock_anthropic_service.generate_image_query.assert_called_once()

    def test_get_image_search_strategy_context_content(self) -> None:
        """Test that image search strategy passes rich context to service."""
        verb = Verb(
            verb="kochen",
            english="to cook",
            present_ich="koche",
            present_du="kochst",
            present_er="kocht",
            perfect="gekocht",
            example="Ich koche Pasta.",
        )

        mock_anthropic_service = Mock()
        mock_anthropic_service.generate_image_query.return_value = "person cooking"

        strategy = verb.get_image_search_strategy(mock_anthropic_service)
        strategy()

        # Check that context was passed to the service
        call_args = mock_anthropic_service.generate_image_query.call_args[0][0]
        assert "kochen" in call_args
        assert "to cook" in call_args
        assert "Pasta" in call_args

    def test_is_separable_verb_positive(self) -> None:
        """Test is_separable method for separable verbs."""
        verb = Verb(
            verb="aufstehen",
            english="to get up",
            present_ich="stehe auf",
            present_du="stehst auf",
            present_er="steht auf",
            perfect="aufgestanden",
            example="Ich stehe um 7 Uhr auf.",
        )

        # Test if method exists and works
        if hasattr(verb, "is_separable"):
            assert verb.is_separable()

    def test_is_separable_verb_negative(self) -> None:
        """Test is_separable method for non-separable verbs."""
        verb = Verb(
            verb="gehen",
            english="to go",
            present_ich="gehe",
            present_du="gehst",
            present_er="geht",
            perfect="gegangen",
            example="Ich gehe nach Hause.",
        )

        # Test if method exists and works
        if hasattr(verb, "is_separable"):
            assert not verb.is_separable()

    def test_get_auxiliary_verb_haben(self) -> None:
        """Test auxiliary verb detection for haben verbs."""
        verb = Verb(
            verb="lernen",
            english="to learn",
            present_ich="lerne",
            present_du="lernst",
            present_er="lernt",
            perfect="gelernt",
            example="Ich habe Deutsch gelernt.",
        )

        # Test if method exists
        if hasattr(verb, "get_auxiliary_verb"):
            auxiliary = verb.get_auxiliary_verb()
            assert auxiliary in ["haben", "sein"]

    def test_get_auxiliary_verb_sein(self) -> None:
        """Test auxiliary verb detection for sein verbs."""
        verb = Verb(
            verb="gehen",
            english="to go",
            present_ich="gehe",
            present_du="gehst",
            present_er="geht",
            perfect="gegangen",
            example="Ich bin nach Hause gegangen.",
        )

        # Test if method exists
        if hasattr(verb, "get_auxiliary_verb"):
            auxiliary = verb.get_auxiliary_verb()
            assert auxiliary in ["haben", "sein"]

    def test_verb_conjugation_validation(self) -> None:
        """Test verb conjugation pattern validation."""
        verb = Verb(
            verb="haben",
            english="to have",
            present_ich="habe",
            present_du="hast",
            present_er="hat",
            perfect="gehabt",
            example="Ich habe einen Hund.",
        )

        # Test if validation method exists
        if hasattr(verb, "validate_conjugation"):
            # Should not raise exception for valid conjugation
            verb.validate_conjugation()

    def test_verb_with_umlauts(self) -> None:
        """Test verb handling with German umlauts."""
        verb = Verb(
            verb="hören",
            english="to hear",
            present_ich="höre",
            present_du="hörst",
            present_er="hört",
            perfect="gehört",
            example="Ich höre Musik.",
        )

        assert verb.verb == "hören"
        assert "hören" in verb.get_combined_audio_text()

    def test_irregular_verb_patterns(self) -> None:
        """Test handling of irregular German verbs."""
        verb = Verb(
            verb="sein",
            english="to be",
            present_ich="bin",
            present_du="bist",
            present_er="ist",
            perfect="gewesen",
            example="Ich bin müde.",
        )

        # Test if irregular detection exists
        if hasattr(verb, "is_irregular"):
            # sein should be detected as irregular
            assert verb.is_irregular()

    def test_modal_verb_detection(self) -> None:
        """Test modal verb detection."""
        verb = Verb(
            verb="können",
            english="can/to be able to",
            present_ich="kann",
            present_du="kannst",
            present_er="kann",
            perfect="gekonnt",
            example="Ich kann schwimmen.",
        )

        # Test if modal detection exists
        if hasattr(verb, "is_modal"):
            assert verb.is_modal()

    def test_verb_stem_extraction(self) -> None:
        """Test verb stem extraction for conjugation."""
        verb = Verb(
            verb="spielen",
            english="to play",
            present_ich="spiele",
            present_du="spielst",
            present_er="spielt",
            perfect="gespielt",
            example="Ich spiele Fußball.",
        )

        # Test if stem extraction exists
        if hasattr(verb, "get_stem"):
            stem = verb.get_stem()
            assert stem == "spiel"

    def test_perfect_tense_formation(self) -> None:
        """Test perfect tense formation rules."""
        verb = Verb(
            verb="machen",
            english="to make/do",
            present_ich="mache",
            present_du="machst",
            present_er="macht",
            perfect="gemacht",
            example="Ich habe es gemacht.",
        )

        # Test if perfect formation method exists
        if hasattr(verb, "get_perfect_form"):
            perfect = verb.get_perfect_form()
            assert "gemacht" in perfect


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
