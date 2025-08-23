"""Tests for AnkiRenderSimulator - comprehensive simulation of Anki card rendering."""

import tempfile
from pathlib import Path
from typing import Dict

import pytest

from langlearn.testing.anki_simulator import AnkiRenderSimulator


class TestAnkiRenderSimulator:
    """Test suite for AnkiRenderSimulator functionality."""

    def test_apply_field_substitution_basic(self) -> None:
        """Test basic field substitution."""
        template = "{{Word}} means {{Meaning}} in English"
        fields = {"Word": "Haus", "Meaning": "house"}
        
        result = AnkiRenderSimulator.apply_field_substitution(template, fields)
        
        assert result == "Haus means house in English"

    def test_apply_field_substitution_empty_field(self) -> None:
        """Test field substitution with empty field value."""
        template = "{{Word}} means {{Meaning}}"
        fields = {"Word": "Haus", "Meaning": ""}
        
        result = AnkiRenderSimulator.apply_field_substitution(template, fields)
        
        assert result == "Haus means "

    def test_apply_field_substitution_missing_field(self) -> None:
        """Test field substitution with missing field."""
        template = "{{Word}} means {{Meaning}}"
        fields = {"Word": "Haus"}  # Missing Meaning field
        
        result = AnkiRenderSimulator.apply_field_substitution(template, fields)
        
        assert result == "Haus means {{Meaning}}"  # Unreplaced field remains

    def test_render_cloze_deletion_show_answer(self) -> None:
        """Test cloze deletion rendering with answer shown."""
        content = "{{c1::Der}} Mann ist hier"
        
        result = AnkiRenderSimulator.render_cloze_deletion(content, show_answer=True)
        
        assert result == "Der Mann ist hier"

    def test_render_cloze_deletion_hide_answer(self) -> None:
        """Test cloze deletion rendering with answer hidden."""
        content = "{{c1::Der}} Mann ist hier"
        
        result = AnkiRenderSimulator.render_cloze_deletion(content, show_answer=False)
        
        assert result == "[...] Mann ist hier"

    def test_render_cloze_deletion_multiple_clozes(self) -> None:
        """Test cloze deletion rendering with multiple clozes."""
        content = "{{c1::Der}} {{c2::Mann}} ist hier"
        
        result_front = AnkiRenderSimulator.render_cloze_deletion(content, show_answer=False)
        result_back = AnkiRenderSimulator.render_cloze_deletion(content, show_answer=True)
        
        assert result_front == "[...] [...] ist hier"
        assert result_back == "Der Mann ist hier"

    def test_simulate_card_display_basic_cloze(self) -> None:
        """Test basic card display simulation with cloze deletion."""
        note_data = {"Word": "Haus", "Meaning": "house"}
        template = "The German word {{c1::{{Word}}}} means {{Meaning}}"
        
        result = AnkiRenderSimulator.simulate_card_display(note_data, template)
        
        assert "front" in result and "back" in result
        assert result["front"] == "The German word [...] means house"
        assert result["back"] == "The German word Haus means house"
        assert result["rendered"] == "The German word {{c1::Haus}} means house"

    def test_simulate_card_display_no_cloze(self) -> None:
        """Test card display simulation without cloze deletions."""
        note_data = {"Word": "Haus", "Meaning": "house"}
        template = "{{Word}} means {{Meaning}}"
        
        result = AnkiRenderSimulator.simulate_card_display(note_data, template)
        
        assert result["front"] == "Haus means house"
        assert result["back"] == "Haus means house"

    def test_simulate_cloze_card_states_single_cloze(self) -> None:
        """Test cloze card state simulation with single cloze."""
        content = "{{c1::Der}} Mann ist hier"
        fields: Dict[str, str] = {}
        
        states = AnkiRenderSimulator.simulate_cloze_card_states(content, fields)
        
        assert 1 in states
        assert states[1]["front"] == "[...] Mann ist hier"
        assert states[1]["back"] == "Der Mann ist hier"

    def test_simulate_cloze_card_states_multiple_clozes(self) -> None:
        """Test cloze card state simulation with multiple clozes."""
        content = "{{c1::Der}} {{c2::Mann}} ist hier"
        fields: Dict[str, str] = {}
        
        states = AnkiRenderSimulator.simulate_cloze_card_states(content, fields)
        
        assert 1 in states and 2 in states
        # For cloze 1: hide c1, show c2
        assert states[1]["front"] == "[...] Mann ist hier"
        assert states[1]["back"] == "Der Mann ist hier"
        # For cloze 2: show c1, hide c2  
        assert states[2]["front"] == "Der [...] ist hier"
        assert states[2]["back"] == "Der Mann ist hier"

    def test_simulate_cloze_card_states_with_fields(self) -> None:
        """Test cloze card state simulation with field substitution."""
        content = "{{c1::{{Word}}}} means {{Meaning}}"
        fields = {"Word": "Haus", "Meaning": "house"}
        
        states = AnkiRenderSimulator.simulate_cloze_card_states(content, fields)
        
        assert 1 in states
        assert states[1]["front"] == "[...] means house"
        assert states[1]["back"] == "Haus means house"

    def test_detect_rendering_issues_unreplaced_field(self) -> None:
        """Test detection of unreplaced field references."""
        rendered = "Haus means {{UnknownField}}"
        
        issues = AnkiRenderSimulator.detect_rendering_issues(rendered)
        
        assert len(issues) > 0
        assert any("Unreplaced field reference" in issue for issue in issues)
        assert any("UnknownField" in issue for issue in issues)

    def test_detect_rendering_issues_blank_content(self) -> None:
        """Test detection of blank content."""
        rendered = ""
        
        issues = AnkiRenderSimulator.detect_rendering_issues(rendered)
        
        assert len(issues) > 0
        assert any("completely blank" in issue for issue in issues)

    def test_detect_rendering_issues_too_short(self) -> None:
        """Test detection of too short content."""
        rendered = "Hi"
        
        issues = AnkiRenderSimulator.detect_rendering_issues(rendered)
        
        assert len(issues) > 0
        assert any("too short" in issue for issue in issues)

    def test_detect_rendering_issues_malformed_cloze(self) -> None:
        """Test detection of malformed cloze deletions."""
        rendered = "{{c1:: incomplete cloze"
        
        issues = AnkiRenderSimulator.detect_rendering_issues(rendered)
        
        assert len(issues) > 0
        assert any("Malformed cloze deletion" in issue for issue in issues)

    def test_detect_rendering_issues_valid_content(self) -> None:
        """Test that valid content has no rendering issues."""
        rendered = "The German word {{c1::Haus}} means house"
        
        issues = AnkiRenderSimulator.detect_rendering_issues(rendered)
        
        # Should detect no issues with valid cloze content
        major_issues = [issue for issue in issues if "blank" in issue or "short" in issue]
        assert len(major_issues) == 0

    def test_validate_card_rendering_valid_card(self) -> None:
        """Test comprehensive rendering validation of valid card."""
        content = "The German word {{c1::{{Word}}}} means {{Meaning}}"
        fields = {"Word": "Haus", "Meaning": "house"}
        
        valid, issues = AnkiRenderSimulator.validate_card_rendering(content, fields)
        
        assert valid is True
        assert len(issues) == 0

    def test_validate_card_rendering_missing_field(self) -> None:
        """Test comprehensive rendering validation with missing field."""
        content = "{{c1::{{Word}}}} means {{MissingField}}"
        fields = {"Word": "Haus"}
        
        valid, issues = AnkiRenderSimulator.validate_card_rendering(content, fields)
        
        assert valid is False
        assert "rendering" in issues
        assert any("MissingField" in str(issues["rendering"]) for _ in [True])

    def test_validate_card_rendering_identical_front_back(self) -> None:
        """Test detection of identical front and back views."""
        content = "{{Word}} means {{Meaning}}"  # No cloze deletion
        fields = {"Word": "Haus", "Meaning": "house"}
        
        valid, issues = AnkiRenderSimulator.validate_card_rendering(content, fields)
        
        assert valid is False
        assert "cloze_processing" in issues
        assert any("identical" in issue for issue in issues["cloze_processing"])

    def test_validate_card_rendering_blank_card(self) -> None:
        """Test detection of blank cards."""
        content = "{{c1::{{Word}}}}"
        fields = {"Word": ""}  # Empty field leads to blank card
        
        valid, issues = AnkiRenderSimulator.validate_card_rendering(content, fields)
        
        assert valid is False
        # Should detect blank or rendering issues
        assert any(category in issues for category in ["blank_cards", "rendering"])

    def test_real_world_german_gender_cloze(self) -> None:
        """Test with real German gender cloze card from the project."""
        content = "{{c1::Der}} Mann arbeitet hier"
        fields = {"Explanation": "Maskulin - Geschlecht erkennen"}
        
        # Test card display simulation
        result = AnkiRenderSimulator.simulate_card_display(fields, content)
        
        assert result["front"] == "[...] Mann arbeitet hier"
        assert result["back"] == "Der Mann arbeitet hier"

    def test_real_world_german_case_cloze(self) -> None:
        """Test with real German case cloze card from the project."""
        content = "Ich sehe {{c1::das}} Haus"
        fields = {"Explanation": "das - Neutrum Akkusativ (wen/was? direktes Objekt)"}
        
        # Test cloze state simulation
        states = AnkiRenderSimulator.simulate_cloze_card_states(content, fields)
        
        assert 1 in states
        assert states[1]["front"] == "Ich sehe [...] Haus"
        assert states[1]["back"] == "Ich sehe das Haus"

    def test_field_substitution_with_nested_cloze(self) -> None:
        """Test field substitution within cloze deletions."""
        template = "{{c1::{{Word}}}} means {{Meaning}}"
        fields = {"Word": "Haus", "Meaning": "house"}
        
        # First apply field substitution
        after_fields = AnkiRenderSimulator.apply_field_substitution(template, fields)
        assert after_fields == "{{c1::Haus}} means house"
        
        # Then test cloze rendering
        front = AnkiRenderSimulator.render_cloze_deletion(after_fields, show_answer=False)
        back = AnkiRenderSimulator.render_cloze_deletion(after_fields, show_answer=True)
        
        assert front == "[...] means house"
        assert back == "Haus means house"

    def test_complex_multi_cloze_with_fields(self) -> None:
        """Test complex scenario with multiple clozes and field substitution."""
        content = "{{c1::{{Article}}}} {{c2::{{Noun}}}} ist {{c3::groß}}"
        fields = {"Article": "Das", "Noun": "Haus"}
        
        states = AnkiRenderSimulator.simulate_cloze_card_states(content, fields)
        
        assert len(states) == 3
        
        # Test each cloze state
        assert states[1]["front"] == "[...] Haus ist groß"  # Hide article
        assert states[1]["back"] == "Das Haus ist groß"
        
        assert states[2]["front"] == "Das [...] ist groß"   # Hide noun  
        assert states[2]["back"] == "Das Haus ist groß"
        
        assert states[3]["front"] == "Das Haus ist [...]"  # Hide adjective
        assert states[3]["back"] == "Das Haus ist groß"

    @pytest.mark.parametrize("content,fields,should_be_valid", [
        # Valid cases
        ("{{c1::Der}} Mann", {}, True),
        ("{{c1::{{Word}}}} means {{Meaning}}", {"Word": "Haus", "Meaning": "house"}, True),
        ("{{c1::Das}} {{c2::Haus}} ist groß", {}, True),
        
        # Invalid cases - blank cards
        ("{{c1::{{Word}}}}", {"Word": ""}, False),
        ("{{MissingField}}", {}, False),
        ("", {}, False),
        
        # Invalid cases - no learning value
        ("{{Word}} means {{Meaning}}", {"Word": "Haus", "Meaning": "house"}, False),
    ])
    def test_rendering_validation_patterns(
        self, content: str, fields: Dict[str, str], should_be_valid: bool
    ) -> None:
        """Test various rendering validation patterns."""
        valid, _ = AnkiRenderSimulator.validate_card_rendering(content, fields)
        assert valid == should_be_valid

    def test_html_content_processing(self) -> None:
        """Test that HTML content is handled appropriately."""
        content = '<div class="german">{{c1::Der}} Mann</div>'
        fields: Dict[str, str] = {}
        
        result = AnkiRenderSimulator.simulate_card_display(fields, content)
        
        assert result["front"] == '<div class="german">[...] Mann</div>'
        assert result["back"] == '<div class="german">Der Mann</div>'

    def test_edge_case_empty_cloze_content(self) -> None:
        """Test edge case with empty cloze content."""
        content = "{{c1::}} ist leer"
        fields: Dict[str, str] = {}
        
        issues = AnkiRenderSimulator.detect_rendering_issues(content)
        
        # Should not crash but may have issues
        assert isinstance(issues, list)
        
        # Test rendering still works
        front = AnkiRenderSimulator.render_cloze_deletion(content, show_answer=False)
        back = AnkiRenderSimulator.render_cloze_deletion(content, show_answer=True)
        
        assert front == "[...] ist leer"
        assert back == " ist leer"  # Empty cloze content becomes just space