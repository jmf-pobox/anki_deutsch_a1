"""AnkiValidator for validating content will work correctly in Anki application.

This module provides validation functionality to catch issues before they reach
the Anki application, preventing the verification gap that caused $566 in wasted
costs from false "fix" claims.
"""

import re
from pathlib import Path


class AnkiValidator:
    """Validates content for Anki application compatibility.

    This class addresses the critical verification gap identified after experiencing
    significant costs from claiming fixes worked when they didn't actually work in
    the real Anki application.

    The validator checks:
    - Cloze deletion syntax correctness
    - Field reference validity
    - Media path accessibility
    - Blank card detection through rendering simulation
    """

    # Anki cloze deletion patterns
    CLOZE_PATTERN = re.compile(r"{{c(\d+)::(.*?)}}")
    FIELD_PATTERN = re.compile(r"{{([^c][^}]*?)}}")
    SOUND_PATTERN = re.compile(r"\[sound:([^\]]+)\]")
    IMAGE_PATTERN = re.compile(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>')

    @staticmethod
    def validate_cloze_card(
        content: str, fields: dict[str, str]
    ) -> tuple[bool, list[str]]:
        """Validates cloze deletion cards for Anki compatibility.

        Args:
            content: The card content with cloze deletions and field references
            fields: Dictionary mapping field names to their values

        Returns:
            Tuple of (is_valid, list_of_issues)

        Example:
            >>> content = "{{c1::{{Word}}}} means {{Meaning}}"
            >>> fields = {"Word": "Haus", "Meaning": "house"}
            >>> valid, issues = AnkiValidator.validate_cloze_card(content, fields)
            >>> assert valid == True
        """
        issues = []

        # Check for valid cloze syntax
        cloze_matches = AnkiValidator.CLOZE_PATTERN.findall(content)
        if not cloze_matches:
            issues.append(
                "No valid cloze deletions found (expected {{c1::text}} format)"
            )
        else:
            # Validate cloze numbering
            cloze_numbers = [int(match[0]) for match in cloze_matches]
            unique_numbers = set(cloze_numbers)

            # Check if starts with c1
            if min(unique_numbers) != 1:
                issues.append("Cloze numbering must start with c1")

            # Check for gaps in numbering (but only if more than one unique number)
            if (
                len(unique_numbers) > 1
                and max(unique_numbers) - min(unique_numbers) + 1 != len(unique_numbers)
            ):
                issues.append("Cloze numbering has gaps (e.g., c1, c3 without c2)")

        # Check field references exist
        field_matches = AnkiValidator.FIELD_PATTERN.findall(content)
        for field_name in field_matches:
            if field_name not in fields:
                issues.append(f"Missing field reference: {{{{ {field_name} }}}}")

        # Simulate rendering to detect blank cards
        try:
            rendered = AnkiValidator._simulate_field_replacement(content, fields)
            if AnkiValidator._is_blank_after_rendering(rendered):
                issues.append("Card will appear blank after field replacement")
        except Exception as e:
            issues.append(f"Field replacement simulation failed: {e}")

        return (len(issues) == 0, issues)

    @staticmethod
    def validate_field_references(
        template: str, fields: dict[str, str]
    ) -> tuple[bool, list[str]]:
        """Validates all field references in a template exist in the provided fields.

        Args:
            template: HTML template with field references like {{Field}}
            fields: Dictionary of available field names and values

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        # Find all field references (excluding cloze deletions)
        field_matches = AnkiValidator.FIELD_PATTERN.findall(template)

        for field_name in field_matches:
            if field_name not in fields:
                issues.append(
                    f"Template references undefined field: {{{{ {field_name} }}}}"
                )

        # Check for empty required fields that would cause blank content
        critical_fields = [
            "Text",
            "Word",
            "German",
            "English",
        ]  # Common critical fields
        for field_name in critical_fields:
            if (
                field_name in fields
                and not fields[field_name].strip()
                and f"{{{{{field_name}}}}}" in template
            ):
                issues.append(
                    f"Critical field '{field_name}' is empty but referenced "
                    f"in template"
                )

        return (len(issues) == 0, issues)

    @staticmethod
    def validate_media_paths(
        card_content: str, media_dir: Path | None = None
    ) -> tuple[bool, list[str]]:
        """Validates media file references are accessible.

        Args:
            card_content: Content with media references like [sound:file.mp3] or
                <img src="...">
            media_dir: Optional directory to check for file existence

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        # Check sound file references
        sound_matches = AnkiValidator.SOUND_PATTERN.findall(card_content)

        # Also check for empty sound references [sound:]
        if "[sound:]" in card_content:
            issues.append("Empty sound file reference: [sound:]")

        for sound_file in sound_matches:
            if not sound_file.strip():
                issues.append("Empty sound file reference: [sound:]")
            elif media_dir and not (media_dir / sound_file).exists():
                issues.append(f"Sound file not found: {sound_file}")

        # Check image file references
        image_matches = AnkiValidator.IMAGE_PATTERN.findall(card_content)
        for image_file in image_matches:
            if not image_file.strip():
                issues.append("Empty image file reference in <img src=''>")
            elif media_dir and not (media_dir / image_file).exists():
                issues.append(f"Image file not found: {image_file}")

        return (len(issues) == 0, issues)

    @staticmethod
    def detect_blank_cards(rendered_content: str) -> tuple[bool, list[str]]:
        """Detects if a card will appear blank to the user after rendering.

        Args:
            rendered_content: Content after field replacement and cloze processing

        Returns:
            Tuple of (has_blank_cards, list_of_issues)
        """
        issues = []

        # Remove HTML tags for text analysis
        text_content = re.sub(r"<[^>]+>", "", rendered_content)

        # Remove cloze deletions for blank detection
        text_without_cloze = AnkiValidator.CLOZE_PATTERN.sub("___", text_content)

        # Check if card is essentially blank
        if not text_without_cloze.strip():
            issues.append("Card content is completely empty")
        elif text_without_cloze.strip() == "___":
            issues.append("Card contains only cloze deletion with no context")
        elif len(text_without_cloze.strip()) < 3:
            issues.append("Card content is too short to be meaningful")

        # Check for common blank card patterns
        blank_patterns = [
            (r"^\s*___\s*$", "Card is only a cloze deletion"),
            (r"^\s*\{\{[^}]+\}\}\s*$", "Card is only an unreplaced field reference"),
            (r"^\s*\[sound:[^\]]*\]\s*$", "Card contains only audio with no text"),
        ]

        for pattern, message in blank_patterns:
            if re.match(pattern, text_content.strip()):
                issues.append(message)

        return (len(issues) > 0, issues)

    @staticmethod
    def validate_cloze_syntax(content: str) -> tuple[bool, list[str]]:
        """Validates cloze deletion syntax matches Anki's requirements.

        Args:
            content: Content containing cloze deletions

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        # Check for malformed cloze deletions
        malformed_patterns = [
            (r"\{\{c\d+::\}\}", "Empty cloze deletion: {{c1::}}"),
            (r"\{\{c\d+::[^}]*\{\{c\d+::", "Nested cloze deletions are not allowed"),
            (r"\{\{c[^0-9]", "Cloze must have number: {{c1::text}}"),
            (r"\{\{c0::", "Cloze numbering must start from 1, not 0"),
        ]

        for pattern, message in malformed_patterns:
            if re.search(pattern, content):
                issues.append(message)

        # Check for valid cloze pattern
        valid_clozes = AnkiValidator.CLOZE_PATTERN.findall(content)
        if not valid_clozes and "{{c" in content:
            issues.append(
                "Found cloze-like patterns but none match valid {{c1::text}} format"
            )

        return (len(issues) == 0, issues)

    @staticmethod
    def _simulate_field_replacement(content: str, fields: dict[str, str]) -> str:
        """Simulates Anki's field replacement process.

        Args:
            content: Template content with field references
            fields: Field name to value mapping

        Returns:
            Content after field replacement
        """
        rendered = content

        # Replace field references with actual values
        for field_name, field_value in fields.items():
            field_pattern = f"{{{{{field_name}}}}}"
            rendered = rendered.replace(field_pattern, field_value)

        return rendered

    @staticmethod
    def _is_blank_after_rendering(rendered_content: str) -> bool:
        """Checks if content will appear blank after rendering.

        Args:
            rendered_content: Content after field replacement

        Returns:
            True if content will appear blank to user
        """
        # Remove HTML tags
        text_only = re.sub(r"<[^>]+>", "", rendered_content)

        # Check for empty cloze deletions like {{c1::}}
        if re.search(r"\{\{c\d+::\}\}", text_only):
            return True

        # Remove cloze deletions for analysis
        text_without_cloze = AnkiValidator.CLOZE_PATTERN.sub("___", text_only)

        # Check if meaningful content remains
        meaningful_text = text_without_cloze.strip()
        return len(meaningful_text) < 3 or meaningful_text == "___"

    @classmethod
    def validate_card_complete(
        cls, content: str, fields: dict[str, str], media_dir: Path | None = None
    ) -> tuple[bool, dict[str, list[str]]]:
        """Comprehensive validation of a complete card.

        Args:
            content: Card content with cloze deletions and field references
            fields: Available fields for the card
            media_dir: Optional directory for media file validation

        Returns:
            Tuple of (is_completely_valid, dict_of_issues_by_category)
        """
        all_issues = {}

        # Validate cloze deletions
        cloze_valid, cloze_issues = cls.validate_cloze_card(content, fields)
        if cloze_issues:
            all_issues["cloze_deletions"] = cloze_issues

        # Validate field references
        field_valid, field_issues = cls.validate_field_references(content, fields)
        if field_issues:
            all_issues["field_references"] = field_issues

        # Validate media paths
        media_valid, media_issues = cls.validate_media_paths(content, media_dir)
        if media_issues:
            all_issues["media_paths"] = media_issues

        # Validate cloze syntax
        syntax_valid, syntax_issues = cls.validate_cloze_syntax(content)
        if syntax_issues:
            all_issues["cloze_syntax"] = syntax_issues

        # Check for blank cards
        rendered = cls._simulate_field_replacement(content, fields)
        has_blanks, blank_issues = cls.detect_blank_cards(rendered)
        if has_blanks:
            all_issues["blank_cards"] = blank_issues

        return (len(all_issues) == 0, all_issues)
