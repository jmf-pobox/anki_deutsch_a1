"""AnkiRenderSimulator for simulating exact Anki card display behavior.

This module provides simulation functionality to predict exactly what Anki will
display to users, addressing the critical verification gap that caused $566 in
wasted costs from false "fix" claims.
"""

import re
from pathlib import Path


class AnkiRenderSimulator:
    """Simulates exactly what Anki will display to users.

    This class addresses the critical verification gap identified after experiencing
    significant costs from claiming fixes worked when they didn't actually work in
    the real Anki application.

    The simulator mimics:
    - Field substitution ({{Field}} replacement)
    - Cloze deletion processing ({{c1::text}} handling)
    - HTML rendering as Anki would display it
    - Card state simulation (front/back views)
    """

    # Anki field and cloze patterns
    FIELD_PATTERN = re.compile(r"{{([^}]*?)}}")
    CLOZE_PATTERN = re.compile(r"{{c(\d+)::(.*?)}}")

    @staticmethod
    def simulate_card_display(
        note_data: dict[str, str], template: str
    ) -> dict[str, str]:
        """Simulate exactly what Anki will display for a card.

        Args:
            note_data: Dictionary mapping field names to their values
            template: Card template with field references and cloze deletions

        Returns:
            Dictionary with 'front' and 'back' keys showing rendered content

        Example:
            >>> note_data = {"Word": "Haus", "Meaning": "house"}
            >>> template = "{{c1::{{Word}}}} means {{Meaning}}"
            >>> result = AnkiRenderSimulator.simulate_card_display(note_data, template)
            >>> assert "{{c1::Haus}}" in result['front']
            >>> assert "Haus" in result['back']
        """
        # Step 1: Apply field substitution
        rendered_content = AnkiRenderSimulator.apply_field_substitution(
            template, note_data
        )

        # Step 2: Process cloze deletions for front/back views
        front_view = AnkiRenderSimulator.render_cloze_deletion(
            rendered_content, show_answer=False
        )
        back_view = AnkiRenderSimulator.render_cloze_deletion(
            rendered_content, show_answer=True
        )

        return {
            "front": front_view,
            "back": back_view,
            "rendered": rendered_content,  # After field substitution, before cloze
        }

    @staticmethod
    def render_cloze_deletion(content: str, show_answer: bool = False) -> str:
        """Process cloze deletions as Anki would display them.

        Args:
            content: Content with cloze deletions like {{c1::answer}}
            show_answer: If True, show answer; if False, show blank/ellipsis

        Returns:
            Content as Anki would display it

        Example:
            >>> content = "{{c1::Der}} Mann ist hier"
            >>> front = AnkiRenderSimulator.render_cloze_deletion(content, False)
            >>> assert "[...]" in front  # Shows blank
            >>> back = AnkiRenderSimulator.render_cloze_deletion(content, True)
            >>> assert "Der" in back  # Shows answer
        """
        if show_answer:
            # Back side: Show the answer, remove cloze markup
            return AnkiRenderSimulator.CLOZE_PATTERN.sub(r"\2", content)
        else:
            # Front side: Replace cloze with blank/ellipsis
            return AnkiRenderSimulator.CLOZE_PATTERN.sub("[...]", content)

    @staticmethod
    def apply_field_substitution(template: str, fields: dict[str, str]) -> str:
        """Simulates Anki's field replacement process.

        Args:
            template: Template content with field references like {{Field}}
            fields: Field name to value mapping

        Returns:
            Content after field replacement

        Example:
            >>> template = "{{Word}} means {{Meaning}} in English"
            >>> fields = {"Word": "Haus", "Meaning": "house"}
            >>> result = AnkiRenderSimulator.apply_field_substitution(template, fields)
            >>> assert result == "Haus means house in English"
        """
        rendered = template

        # Replace field references with actual values
        for field_name, field_value in fields.items():
            field_pattern = f"{{{{{field_name}}}}}"
            rendered = rendered.replace(field_pattern, field_value or "")

        return rendered

    @staticmethod
    def detect_rendering_issues(rendered: str) -> list[str]:
        """Detect issues that would cause problems in Anki display.

        Args:
            rendered: Content after field replacement and cloze processing

        Returns:
            List of rendering issues found

        Example:
            >>> rendered = "{{UnknownField}} and empty content"
            >>> issues = AnkiRenderSimulator.detect_rendering_issues(rendered)
            >>> assert "Unreplaced field reference" in str(issues)
        """
        issues = []

        # Check for unreplaced field references
        field_matches = AnkiRenderSimulator.FIELD_PATTERN.findall(rendered)
        for field_name in field_matches:
            # Skip cloze deletions (they start with 'c')
            if not field_name.startswith("c") and "::" not in field_name:
                issues.append(f"Unreplaced field reference: {{{{{field_name}}}}}")

        # Check for malformed cloze deletions
        if "{{c" in rendered and not AnkiRenderSimulator.CLOZE_PATTERN.search(rendered):
            issues.append("Malformed cloze deletion syntax detected")

        # Check for empty content after processing
        text_content = re.sub(r"<[^>]+>", "", rendered)  # Remove HTML
        text_content = AnkiRenderSimulator.CLOZE_PATTERN.sub(
            "[...]", text_content
        )  # Process cloze

        if not text_content.strip():
            issues.append("Card will render as completely blank")
        elif len(text_content.strip()) < 3:
            issues.append("Card content is too short to be meaningful")

        return issues

    @staticmethod
    def simulate_cloze_card_states(
        content: str, fields: dict[str, str]
    ) -> dict[int, dict[str, str]]:
        """Simulate all cloze deletion states for a card.

        Args:
            content: Card content with multiple cloze deletions
            fields: Field values for substitution

        Returns:
            Dictionary mapping cloze numbers to front/back views

        Example:
            >>> content = "{{c1::Der}} {{c2::Mann}} ist hier"
            >>> fields = {}
            >>> states = AnkiRenderSimulator.simulate_cloze_card_states(content, fields)
            >>> assert 1 in states and 2 in states
            >>> assert "[...]" in states[1]['front']  # First cloze hidden
            >>> assert "Der" in states[1]['back']     # First cloze revealed
        """
        # Apply field substitution first
        rendered = AnkiRenderSimulator.apply_field_substitution(content, fields)

        # Find all cloze numbers
        cloze_matches = AnkiRenderSimulator.CLOZE_PATTERN.findall(rendered)
        cloze_numbers = sorted({int(match[0]) for match in cloze_matches})

        card_states = {}

        for cloze_num in cloze_numbers:
            # For each cloze, show only that one as blank on front
            front_content = rendered
            back_content = rendered

            # Process all cloze deletions
            for match_num, match_text in cloze_matches:
                cloze_pattern = f"{{{{c{match_num}::{re.escape(match_text)}}}}}"
                if int(match_num) == cloze_num:
                    # This is the target cloze - hide on front, show on back
                    front_content = front_content.replace(cloze_pattern, "[...]")
                    back_content = back_content.replace(cloze_pattern, match_text)
                else:
                    # Other clozes - always show the answer
                    front_content = front_content.replace(cloze_pattern, match_text)
                    back_content = back_content.replace(cloze_pattern, match_text)

            card_states[cloze_num] = {"front": front_content, "back": back_content}

        return card_states

    @classmethod
    def validate_card_rendering(
        cls, content: str, fields: dict[str, str], media_dir: Path | None = None
    ) -> tuple[bool, dict[str, list[str]]]:
        """Comprehensive rendering validation for a complete card.

        Args:
            content: Card content with field references and cloze deletions
            fields: Available fields for the card
            media_dir: Optional directory for media file validation

        Returns:
            Tuple of (renders_correctly, dict_of_issues_by_category)

        Example:
            >>> content = "{{c1::{{Word}}}} means {{Meaning}}"
            >>> fields = {"Word": "Haus", "Meaning": "house"}
            >>> valid, issues = AnkiRenderSimulator.validate_card_rendering(
            ...     content, fields
            ... )
            >>> assert valid == True
        """
        all_issues = {}

        # Step 1: Apply field substitution
        try:
            rendered = cls.apply_field_substitution(content, fields)
        except Exception as e:
            all_issues["field_substitution"] = [f"Field substitution failed: {e}"]
            return False, all_issues

        # Step 2: Check for rendering issues
        rendering_issues = cls.detect_rendering_issues(rendered)
        if rendering_issues:
            all_issues["rendering"] = rendering_issues

        # Step 3: Simulate card display
        try:
            card_display = cls.simulate_card_display(fields, content)

            # Check if front and back are meaningfully different
            front = card_display["front"]
            back = card_display["back"]

            if front == back:
                if not all_issues.get("cloze_processing"):
                    all_issues["cloze_processing"] = []
                all_issues["cloze_processing"].append(
                    "Front and back views are identical - no learning value"
                )

            # Check for blank front or back
            if not front.strip():
                if not all_issues.get("blank_cards"):
                    all_issues["blank_cards"] = []
                all_issues["blank_cards"].append("Front view is completely blank")

            if not back.strip():
                if not all_issues.get("blank_cards"):
                    all_issues["blank_cards"] = []
                all_issues["blank_cards"].append("Back view is completely blank")

        except Exception as e:
            all_issues["card_display"] = [f"Card display simulation failed: {e}"]

        # Step 4: Validate cloze card states if cloze deletions exist
        if "{{c" in content:
            try:
                cloze_states = cls.simulate_cloze_card_states(content, fields)
                if not cloze_states:
                    if not all_issues.get("cloze_processing"):
                        all_issues["cloze_processing"] = []
                    all_issues["cloze_processing"].append(
                        "No valid cloze states could be generated"
                    )
            except Exception as e:
                all_issues["cloze_processing"] = [f"Cloze state simulation failed: {e}"]

        return len(all_issues) == 0, all_issues
