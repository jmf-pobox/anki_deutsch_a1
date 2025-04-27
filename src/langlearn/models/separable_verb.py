"""Model for German separable verbs."""

from pydantic import Field

from .verb import Verb


class SeparableVerb(Verb):
    """Model representing a German separable verb with its conjugations.

    Separable verbs in German have a prefix that separates from the main verb
    in certain tenses and positions. This model extends the base Verb class
    with additional validation specific to separable verbs.
    """

    prefix: str = Field(..., description="The separable prefix of the verb")

    def validate_separable_conjugation(self) -> bool:
        """Validate that the verb follows separable verb conjugation patterns.

        Returns:
            bool: True if the verb follows separable verb conjugation patterns
        """
        # Separable verbs in German typically:
        # 1. Have a prefix that separates in present tense
        # 2. Have the prefix at the end of the sentence in present tense
        # 3. Have the prefix before the main verb in perfect tense

        # Check that the prefix is present in the verb
        if not self.verb.startswith(self.prefix):
            return False

        # Check that present tense forms have the prefix at the end
        if not (
            self.present_ich.endswith(f" {self.prefix}")
            and self.present_du.endswith(f" {self.prefix}")
            and self.present_er.endswith(f" {self.prefix}")
        ):
            return False

        # Check that perfect tense has the prefix before the main verb
        if not self.perfect.startswith(
            f"hat {self.prefix}"
        ) and not self.perfect.startswith(f"ist {self.prefix}"):
            return False

        # Check that the example sentence has the prefix at the end
        return self.example.endswith(f" {self.prefix}.")

    def is_valid_example(self) -> bool:
        """Check if the example sentence is valid for a separable verb."""
        # Check that the example sentence has the prefix at the end
        return self.example.endswith(f" {self.prefix}.")
