"""Model for German irregular verbs."""

from pydantic import Field

from .verb import Verb


class IrregularVerb(Verb):
    """Model representing a German irregular verb with its conjugations.

    Irregular verbs in German have unique conjugation patterns that don't follow
    the regular rules. This model extends the base Verb class with additional
    validation specific to irregular verbs.
    """

    notes: str | None = Field(
        None, description="Notes about the irregular patterns of this verb"
    )

    def validate_irregular_conjugation(self) -> bool:
        """Validate that the verb follows irregular verb conjugation patterns.

        Returns:
            bool: True if the verb follows irregular verb conjugation patterns
        """
        # Irregular verbs in German typically:
        # 1. Have vowel changes in present tense
        # 2. Have irregular perfect tense forms
        # 3. May use 'sein' instead of 'haben' in perfect tense
        # 4. Have irregular present tense forms

        # Check for vowel changes in present tense
        if self._has_vowel_changes():
            return True

        # Check for irregular perfect tense
        if self._has_irregular_perfect():
            return True

        # Check for 'sein' in perfect tense
        if self.perfect.startswith("ist "):
            return True

        # Check for irregular present tense forms
        if self._has_irregular_present():
            return True

        return False

    def _has_vowel_changes(self) -> bool:
        """Check if the verb has vowel changes in present tense.

        Returns:
            bool: True if the verb has vowel changes
        """
        # Common vowel changes in German irregular verbs
        vowel_changes = {"e": ["i", "ie"], "a": ["ä"], "o": ["ö"], "u": ["ü"]}

        # Get the stem of the verb (remove -en ending)
        stem = self.verb[:-2]

        # Check each present tense form for vowel changes
        for form in [self.present_ich, self.present_du, self.present_er]:
            form_stem = form[:-1]  # Remove ending
            for original, changes in vowel_changes.items():
                if original in stem and any(change in form_stem for change in changes):
                    return True

        return False

    def _has_irregular_perfect(self) -> bool:
        """Check if the verb has an irregular perfect tense form.

        Returns:
            bool: True if the verb has an irregular perfect tense
        """
        # Check for irregular perfect tense patterns
        if self.perfect.startswith("hat ") or self.perfect.startswith("ist "):
            # Get the past participle (remove auxiliary verb)
            past_participle = self.perfect.split(" ", 1)[1]

            # Check for irregular patterns
            if not past_participle.startswith("ge"):
                return True
            if not past_participle.endswith("t"):
                return True
            # Check for irregular past participles
            if past_participle in ["gehabt", "gewesen", "gegangen", "gekommen"]:
                return True

        return False

    def _has_irregular_present(self) -> bool:
        """Check if the verb has irregular present tense forms.

        Returns:
            bool: True if the verb has irregular present tense forms
        """
        # List of highly irregular verbs
        irregular_verbs = {
            "sein": ["bin", "bist", "ist"],
            "haben": ["habe", "hast", "hat"],
            "werden": ["werde", "wirst", "wird"],
            "wissen": ["weiß", "weißt", "weiß"],
            "tun": ["tue", "tust", "tut"],
        }

        if self.verb in irregular_verbs:
            expected_forms = irregular_verbs[self.verb]
            actual_forms = [self.present_ich, self.present_du, self.present_er]
            return actual_forms == expected_forms

        return False

    def has_irregular_forms(self) -> bool:
        """Check if the verb has any irregular forms."""
        # Check for irregular present tense forms
        return bool(self._has_irregular_present())
