"""Model for German regular verbs."""

from .verb import Verb


class RegularVerb(Verb):
    """Model representing a German regular verb with its conjugations.

    Regular verbs follow a consistent conjugation pattern in German.
    This model extends the base Verb class with additional validation
    specific to regular verbs.
    """

    def validate_regular_conjugation(self) -> bool:
        """Validate that the verb follows regular conjugation patterns.

        Returns:
            bool: True if the verb follows regular conjugation patterns
        """
        # Regular verbs in German typically:
        # 1. End with -en in infinitive
        # 2. Have -e, -st, -t endings in present tense
        # 3. Form perfect tense with ge- prefix and -t suffix

        # Check infinitive ends with -en
        if not self.verb.endswith("en"):
            return False

        # Check present tense endings
        if not (
            self.present_ich.endswith("e")
            and self.present_du.endswith("st")
            and self.present_er.endswith("t")
        ):
            return False

        # Check perfect tense formation
        if not (self.perfect.startswith("hat ") and self.perfect.endswith("t")):
            return False

        return True
