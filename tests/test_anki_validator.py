"""
Tests for AnkiValidator - comprehensive validation of Anki application
compatibility.
"""

import tempfile
from pathlib import Path

import pytest

from langlearn.validators.anki_validator import AnkiValidator


class TestAnkiValidator:
    """Test suite for AnkiValidator functionality."""

    def test_validate_cloze_card_valid_basic(self) -> None:
        """Test validation of a basic valid cloze card."""
        content = "The word {{c1::{{Word}}}} means {{Meaning}}"
        fields = {"Word": "Haus", "Meaning": "house"}

        valid, issues = AnkiValidator.validate_cloze_card(content, fields)

        assert valid is True
        assert len(issues) == 0

    def test_validate_cloze_card_missing_cloze(self) -> None:
        """Test detection of missing cloze deletions."""
        content = "The word {{Word}} means {{Meaning}}"  # No cloze deletion
        fields = {"Word": "Haus", "Meaning": "house"}

        valid, issues = AnkiValidator.validate_cloze_card(content, fields)

        assert valid is False
        assert "No valid cloze deletions found" in str(issues)

    def test_validate_cloze_card_missing_field(self) -> None:
        """Test detection of missing field references."""
        content = "The word {{c1::{{Word}}}} means {{NonExistentField}}"
        fields = {"Word": "Haus"}  # Missing NonExistentField

        valid, issues = AnkiValidator.validate_cloze_card(content, fields)

        assert valid is False
        assert "Missing field reference: {{ NonExistentField }}" in str(issues)

    def test_validate_cloze_card_blank_after_rendering(self) -> None:
        """Test detection of cards that will appear blank."""
        content = "{{c1::{{Word}}}}"  # Only cloze deletion, no context
        fields = {"Word": ""}  # Empty field

        valid, issues = AnkiValidator.validate_cloze_card(content, fields)

        assert valid is False
        assert "blank" in str(issues).lower()

    def test_validate_cloze_card_multiple_clozes(self) -> None:
        """Test validation of multiple cloze deletions."""
        content = "{{c1::Der}} {{c2::Mann}} ist hier"
        fields: dict[str, str] = {}

        valid, issues = AnkiValidator.validate_cloze_card(content, fields)

        assert valid is True
        assert len(issues) == 0

    def test_validate_cloze_card_invalid_numbering(self) -> None:
        """Test detection of invalid cloze numbering."""
        content = "{{c2::Word}} without c1"  # Starts with c2 instead of c1
        fields: dict[str, str] = {}

        valid, issues = AnkiValidator.validate_cloze_card(content, fields)

        assert valid is False
        assert "must start with c1" in str(issues)

    def test_validate_field_references_valid(self) -> None:
        """Test validation of valid field references."""
        template = "<div>{{Word}}</div><div>{{Meaning}}</div>"
        fields = {"Word": "Haus", "Meaning": "house"}

        valid, issues = AnkiValidator.validate_field_references(template, fields)

        assert valid is True
        assert len(issues) == 0

    def test_validate_field_references_undefined_field(self) -> None:
        """Test detection of undefined field references."""
        template = "<div>{{Word}}</div><div>{{UndefinedField}}</div>"
        fields = {"Word": "Haus"}

        valid, issues = AnkiValidator.validate_field_references(template, fields)

        assert valid is False
        assert "UndefinedField" in str(issues)

    def test_validate_field_references_empty_critical_field(self) -> None:
        """Test detection of empty critical fields."""
        template = "<div>{{Text}}</div>"
        fields = {"Text": ""}  # Empty critical field

        valid, issues = AnkiValidator.validate_field_references(template, fields)

        assert valid is False
        assert "Text" in str(issues) and "empty" in str(issues).lower()

    def test_validate_media_paths_valid_sound(self) -> None:
        """Test validation of valid sound file references."""
        with tempfile.TemporaryDirectory() as temp_dir:
            media_dir = Path(temp_dir)
            sound_file = media_dir / "test.mp3"
            sound_file.touch()  # Create empty file

            content = "Word: [sound:test.mp3]"

            valid, issues = AnkiValidator.validate_media_paths(content, media_dir)

            assert valid is True
            assert len(issues) == 0

    def test_validate_media_paths_missing_sound(self) -> None:
        """Test detection of missing sound files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            media_dir = Path(temp_dir)
            content = "Word: [sound:missing.mp3]"

            valid, issues = AnkiValidator.validate_media_paths(content, media_dir)

            assert valid is False
            assert "missing.mp3" in str(issues)

    def test_validate_media_paths_empty_sound_reference(self) -> None:
        """Test detection of empty sound references."""
        content = "Word: [sound:]"

        valid, issues = AnkiValidator.validate_media_paths(content)

        assert valid is False
        assert "Empty sound file reference" in str(issues)

    def test_validate_media_paths_valid_image(self) -> None:
        """Test validation of valid image file references."""
        with tempfile.TemporaryDirectory() as temp_dir:
            media_dir = Path(temp_dir)
            image_file = media_dir / "test.jpg"
            image_file.touch()

            content = '<img src="test.jpg" alt="test">'

            valid, issues = AnkiValidator.validate_media_paths(content, media_dir)

            assert valid is True
            assert len(issues) == 0

    def test_validate_media_paths_missing_image(self) -> None:
        """Test detection of missing image files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            media_dir = Path(temp_dir)
            content = '<img src="missing.jpg" alt="test">'

            valid, issues = AnkiValidator.validate_media_paths(content, media_dir)

            assert valid is False
            assert "missing.jpg" in str(issues)

    def test_detect_blank_cards_empty_content(self) -> None:
        """Test detection of completely empty cards."""
        rendered_content = ""

        has_blanks, issues = AnkiValidator.detect_blank_cards(rendered_content)

        assert has_blanks is True
        assert "completely empty" in str(issues)

    def test_detect_blank_cards_only_cloze(self) -> None:
        """Test detection of cards with only cloze deletions."""
        rendered_content = "{{c1::word}}"

        has_blanks, issues = AnkiValidator.detect_blank_cards(rendered_content)

        assert has_blanks is True
        assert "only cloze deletion" in str(issues).lower()

    def test_detect_blank_cards_valid_content(self) -> None:
        """Test that valid content is not flagged as blank."""
        rendered_content = "The word {{c1::Haus}} means house"

        has_blanks, issues = AnkiValidator.detect_blank_cards(rendered_content)

        assert has_blanks is False
        assert len(issues) == 0

    def test_validate_cloze_syntax_valid(self) -> None:
        """Test validation of correct cloze syntax."""
        content = "{{c1::word}} and {{c2::another}}"

        valid, issues = AnkiValidator.validate_cloze_syntax(content)

        assert valid is True
        assert len(issues) == 0

    def test_validate_cloze_syntax_empty_cloze(self) -> None:
        """Test detection of empty cloze deletions."""
        content = "{{c1::}} empty cloze"

        valid, issues = AnkiValidator.validate_cloze_syntax(content)

        assert valid is False
        assert "Empty cloze deletion" in str(issues)

    def test_validate_cloze_syntax_nested_cloze(self) -> None:
        """Test detection of nested cloze deletions."""
        content = "{{c1::outer {{c2::inner}} text}}"

        valid, issues = AnkiValidator.validate_cloze_syntax(content)

        assert valid is False
        assert "Nested cloze deletions" in str(issues)

    def test_validate_cloze_syntax_zero_numbering(self) -> None:
        """Test detection of zero-based cloze numbering."""
        content = "{{c0::word}} should start from 1"

        valid, issues = AnkiValidator.validate_cloze_syntax(content)

        assert valid is False
        assert "must start from 1" in str(issues)

    def test_simulate_field_replacement(self) -> None:
        """Test field replacement simulation."""
        content = "{{Word}} means {{Meaning}} in English"
        fields = {"Word": "Haus", "Meaning": "house"}

        result = AnkiValidator._simulate_field_replacement(content, fields)

        assert result == "Haus means house in English"

    def test_is_blank_after_rendering_blank(self) -> None:
        """Test blank detection after rendering."""
        rendered_content = "{{c1::}}"  # Empty cloze

        is_blank = AnkiValidator._is_blank_after_rendering(rendered_content)

        assert is_blank is True

    def test_is_blank_after_rendering_valid(self) -> None:
        """Test valid content is not considered blank."""
        rendered_content = "The word {{c1::Haus}} is German"

        is_blank = AnkiValidator._is_blank_after_rendering(rendered_content)

        assert is_blank is False

    def test_validate_card_complete_valid(self) -> None:
        """Test comprehensive validation of a valid card."""
        content = "The German word {{c1::{{Word}}}} means {{Meaning}}"
        fields = {"Word": "Haus", "Meaning": "house"}

        valid, issues = AnkiValidator.validate_card_complete(content, fields)

        assert valid is True
        assert len(issues) == 0

    def test_validate_card_complete_multiple_issues(self) -> None:
        """Test comprehensive validation with multiple issue types."""
        content = "{{UndefinedField}} {{c0::{{Word}}}}"  # Missing field + invalid cloze
        fields = {"Word": ""}  # Empty field that will cause blank card

        valid, issues = AnkiValidator.validate_card_complete(content, fields)

        assert valid is False
        assert len(issues) > 1  # Multiple categories of issues
        assert "field_references" in issues
        assert "cloze_syntax" in issues

    def test_real_world_cloze_card_german_gender(self) -> None:
        """Test validation of real German gender cloze card from the project."""
        content = "{{c1::Der}} Mann ist hier"
        fields = {"Explanation": "Maskulin - Geschlecht erkennen"}

        valid, issues = AnkiValidator.validate_cloze_card(content, fields)

        assert valid is True
        assert len(issues) == 0

    def test_real_world_cloze_card_german_case(self) -> None:
        """Test validation of real German case cloze card from the project."""
        content = "das Auto {{c1::des}} Mannes"
        fields = {"Explanation": "des - Maskulin Genitiv"}

        valid, issues = AnkiValidator.validate_cloze_card(content, fields)

        assert valid is True
        assert len(issues) == 0

    def test_problematic_case_empty_field_in_cloze(self) -> None:
        """Test the specific case that caused blank cards in the user's report."""
        # This represents the case where {{c1::{{Field}}}} had an empty Field value
        content = "{{c1::{{Word}}}} Mann ist hier"
        fields = {"Word": ""}  # Empty field that caused blank cards

        valid, issues = AnkiValidator.validate_cloze_card(content, fields)

        assert valid is False
        assert "blank" in str(issues).lower()

    @pytest.mark.parametrize(
        "cloze_content,expected_valid",
        [
            ("{{c1::Der}} Mann", True),
            ("{{c1::}} empty", False),
            ("{{c1::Der}} {{c2::Mann}}", True),
            ("{{c1::outer {{c2::inner}}}}", False),
            ("{{c0::zero}}", False),
        ],
    )
    def test_cloze_syntax_patterns(
        self, cloze_content: str, expected_valid: bool
    ) -> None:
        """Test various cloze syntax patterns."""
        valid, _ = AnkiValidator.validate_cloze_syntax(cloze_content)
        assert valid == expected_valid

    def test_cloze_numbering_validation(self) -> None:
        """Test cloze numbering validation separately."""
        # This should fail because it doesn't start with c1
        content = "{{c2::Mann}} without c1"
        fields: dict[str, str] = {}

        valid, issues = AnkiValidator.validate_cloze_card(content, fields)

        assert valid is False
        assert "must start with c1" in str(issues)
