"""Tests for DebugDeckGenerator - user issue reproduction functionality."""

from pathlib import Path

import pytest

from langlearn.debug.debug_deck_generator import DebugDeckGenerator


class TestDebugDeckGenerator:
    """Test suite for DebugDeckGenerator functionality."""

    def test_create_debug_deck_blank_cards(self) -> None:
        """Test creation of blank cards debug deck."""
        result_path = DebugDeckGenerator.create_debug_deck("blank_cards")

        assert isinstance(result_path, Path)
        assert result_path.name == "debug_blank_cards.apkg"

    def test_create_debug_deck_duplicate_detection(self) -> None:
        """Test creation of duplicate detection debug deck."""
        result_path = DebugDeckGenerator.create_debug_deck("duplicate_detection")

        assert isinstance(result_path, Path)
        assert result_path.name == "debug_duplicate_detection.apkg"

    def test_create_debug_deck_template_syntax(self) -> None:
        """Test creation of template syntax debug deck."""
        result_path = DebugDeckGenerator.create_debug_deck("template_syntax")

        assert isinstance(result_path, Path)
        assert result_path.name == "debug_template_syntax.apkg"

    def test_create_debug_deck_case_sensitivity(self) -> None:
        """Test creation of case sensitivity debug deck."""
        result_path = DebugDeckGenerator.create_debug_deck("case_sensitivity")

        assert isinstance(result_path, Path)
        assert result_path.name == "debug_case_sensitivity.apkg"

    def test_create_debug_deck_field_substitution(self) -> None:
        """Test creation of field substitution debug deck."""
        result_path = DebugDeckGenerator.create_debug_deck("field_substitution")

        assert isinstance(result_path, Path)
        assert result_path.name == "debug_field_substitution.apkg"

    def test_create_debug_deck_multi_cloze(self) -> None:
        """Test creation of multi-cloze debug deck."""
        result_path = DebugDeckGenerator.create_debug_deck("multi_cloze")

        assert isinstance(result_path, Path)
        assert result_path.name == "debug_multi_cloze.apkg"

    def test_create_debug_deck_invalid_issue_type(self) -> None:
        """Test error handling for invalid issue type."""
        with pytest.raises(ValueError, match="Unknown issue type 'invalid_type'"):
            DebugDeckGenerator.create_debug_deck("invalid_type")

    def test_generate_test_cards_gender_cloze(self) -> None:
        """Test generation of gender cloze test cards."""
        cards = DebugDeckGenerator.generate_test_cards("gender_cloze", count=3)

        assert len(cards) == 3
        assert all("c1::" in card["Text"] for card in cards)
        assert all("card_type" in card for card in cards)
        assert all(card["card_type"] == "gender_cloze" for card in cards)

    def test_generate_test_cards_case_cloze(self) -> None:
        """Test generation of case cloze test cards."""
        cards = DebugDeckGenerator.generate_test_cards("case_cloze", count=4)

        assert len(cards) == 4
        assert all("c1::" in card["Text"] for card in cards)
        assert all("card_type" in card for card in cards)
        assert all(card["card_type"] == "case_cloze" for card in cards)

    def test_generate_test_cards_field_substitution(self) -> None:
        """Test generation of field substitution test cards."""
        cards = DebugDeckGenerator.generate_test_cards("field_substitution", count=2)

        assert len(cards) == 2
        assert all("{{Word}}" in card["Text"] for card in cards)
        assert all("Word" in card for card in cards)
        assert all("Meaning" in card for card in cards)

    def test_generate_test_cards_multi_cloze(self) -> None:
        """Test generation of multi-cloze test cards."""
        cards = DebugDeckGenerator.generate_test_cards("multi_cloze", count=2)

        assert len(cards) == 2
        assert all("c1::" in card["Text"] and "c2::" in card["Text"] for card in cards)
        assert all("card_type" in card for card in cards)

    def test_generate_test_cards_invalid_pattern(self) -> None:
        """Test error handling for invalid pattern type."""
        with pytest.raises(ValueError, match="Unknown pattern 'invalid_pattern'"):
            DebugDeckGenerator.generate_test_cards("invalid_pattern")

    def test_add_diagnostic_fields(self) -> None:
        """Test addition of diagnostic fields to card data."""
        original_card = {
            "Text": "{{c1::Der}} Mann",
            "Explanation": "Test card",
            "debug_issue_type": "test_issue",
            "expected_behavior": "Should work correctly",
            "test_notes": "Test notes",
        }

        enhanced_card = DebugDeckGenerator.add_diagnostic_fields(original_card)

        # Check original fields are preserved
        assert enhanced_card["Text"] == original_card["Text"]
        assert enhanced_card["Explanation"] == original_card["Explanation"]

        # Check diagnostic fields are added
        assert "Debug_Issue_Type" in enhanced_card
        assert "Debug_Expected_Behavior" in enhanced_card
        assert "Debug_Test_Notes" in enhanced_card
        assert "Debug_Generated_At" in enhanced_card

        assert enhanced_card["Debug_Issue_Type"] == "test_issue"
        assert enhanced_card["Debug_Expected_Behavior"] == "Should work correctly"
        assert enhanced_card["Debug_Test_Notes"] == "Test notes"

    def test_add_diagnostic_fields_defaults(self) -> None:
        """Test diagnostic fields with default values."""
        original_card = {"Text": "{{c1::Der}} Mann", "Explanation": "Test card"}

        enhanced_card = DebugDeckGenerator.add_diagnostic_fields(original_card)

        assert enhanced_card["Debug_Issue_Type"] == "unknown"
        assert enhanced_card["Debug_Expected_Behavior"] == "See notes"
        assert enhanced_card["Debug_Test_Notes"] == "Generated for debugging"

    def test_blank_card_test_generation(self) -> None:
        """Test specific blank card test generation."""
        cards = DebugDeckGenerator._generate_blank_card_test()

        assert len(cards) == 3

        # Check first card (empty field)
        assert cards[0]["Word"] == ""
        assert "{{Word}}" in cards[0]["Text"]
        assert cards[0]["debug_issue_type"] == "blank_cards"

        # Check second card (empty cloze)
        assert "{{c1::}}" in cards[1]["Text"]

        # Check third card (missing field)
        assert "{{MissingField}}" in cards[2]["Text"]

    def test_duplicate_test_generation(self) -> None:
        """Test specific duplicate detection test generation."""
        cards = DebugDeckGenerator._generate_duplicate_test()

        assert len(cards) == 4

        # Check that some cards have identical content
        texts = [card["Text"] for card in cards]
        assert texts.count(texts[0]) >= 2  # At least 2 cards with same text

    def test_template_syntax_test_generation(self) -> None:
        """Test specific template syntax test generation."""
        cards = DebugDeckGenerator._generate_template_syntax_test()

        assert len(cards) == 3

        # Check for various syntax issues
        issues = [card["Text"] for card in cards]
        assert any("UndefinedField" in issue for issue in issues)
        assert any("{{c2::" in issue and "{{c1::" not in issue for issue in issues)
        assert any("nested" in issue for issue in issues)

    def test_case_sensitivity_test_generation(self) -> None:
        """Test specific case sensitivity test generation."""
        cards = DebugDeckGenerator._generate_case_sensitivity_test()

        assert len(cards) == 3

        # Check for various case patterns
        texts = [card["Text"] for card in cards]
        assert any("{{c1::der}}" in text for text in texts)  # lowercase
        assert any("{{c1::Der}}" in text for text in texts)  # capitalized
        assert any("DIE" in text for text in texts)  # uppercase

    def test_field_substitution_test_generation(self) -> None:
        """Test specific field substitution test generation."""
        cards = DebugDeckGenerator._generate_field_substitution_test()

        assert len(cards) == 3

        # Check field substitution patterns
        assert any("{{Word}}" in card["Text"] for card in cards)
        assert any(card.get("EmptyField") == "" for card in cards)  # Empty field test
        assert any("{{c2::" in card["Text"] for card in cards)  # Multiple cloze

    def test_multi_cloze_test_generation(self) -> None:
        """Test specific multi-cloze test generation."""
        cards = DebugDeckGenerator._generate_multi_cloze_test()

        assert len(cards) == 2

        # Check multi-cloze patterns
        for card in cards:
            text = card["Text"]
            assert "{{c1::" in text
            assert "{{c2::" in text
            assert "{{c3::" in text

    def test_gender_cloze_pattern_generation(self) -> None:
        """Test gender cloze pattern generation."""
        for i in range(1, 7):  # Test cycling through patterns
            card = DebugDeckGenerator._create_gender_cloze_pattern(i)

            assert "{{c1::" in card["Text"]
            assert card["card_type"] == "gender_cloze"
            assert "Geschlecht erkennen" in card["Explanation"]

    def test_case_cloze_pattern_generation(self) -> None:
        """Test case cloze pattern generation."""
        for i in range(1, 9):  # Test cycling through patterns
            card = DebugDeckGenerator._create_case_cloze_pattern(i)

            assert "{{c1::" in card["Text"]
            assert card["card_type"] == "case_cloze"
            assert any(
                case in card["Explanation"]
                for case in ["Akkusativ", "Dativ", "Genitiv"]
            )

    def test_field_substitution_pattern_generation(self) -> None:
        """Test field substitution pattern generation."""
        for i in range(1, 6):  # Test cycling through patterns
            card = DebugDeckGenerator._create_field_substitution_pattern(i)

            assert "{{Word}}" in card["Text"]
            assert "Word" in card
            assert "Meaning" in card
            assert card["card_type"] == "field_substitution"

    def test_multi_cloze_pattern_generation(self) -> None:
        """Test multi-cloze pattern generation."""
        for i in range(1, 5):  # Test cycling through patterns
            card = DebugDeckGenerator._create_multi_cloze_pattern(i)

            text = card["Text"]
            assert "{{c1::" in text
            assert "{{c2::" in text
            assert "{{c3::" in text
            assert card["card_type"] == "multi_cloze"

    def test_issue_type_coverage(self) -> None:
        """Test that all documented issue types are supported."""
        documented_types = [
            "blank_cards",
            "duplicate_detection",
            "template_syntax",
            "case_sensitivity",
            "field_substitution",
            "multi_cloze",
        ]

        # Should not raise exceptions for any documented type
        for issue_type in documented_types:
            result = DebugDeckGenerator.create_debug_deck(issue_type)
            assert isinstance(result, Path)

    def test_pattern_type_coverage(self) -> None:
        """Test that all documented pattern types are supported."""
        documented_patterns = [
            "gender_cloze",
            "case_cloze",
            "field_substitution",
            "multi_cloze",
        ]

        # Should not raise exceptions for any documented pattern
        for pattern in documented_patterns:
            cards = DebugDeckGenerator.generate_test_cards(pattern, count=1)
            assert len(cards) == 1
            assert isinstance(cards[0], dict)
