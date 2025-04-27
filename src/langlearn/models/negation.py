"""Model for German negation words."""

from enum import Enum

from pydantic import BaseModel, Field


class NegationType(str, Enum):
    """Types of German negation words."""

    GENERAL = "general"  # nicht
    ARTICLE = "article"  # kein, keine
    PRONOUN = "pronoun"  # nichts, niemand
    TEMPORAL = "temporal"  # nie, niemals
    SPATIAL = "spatial"  # nirgends, nirgendwo
    CORRELATIVE = "correlative"  # weder...noch
    INTENSIFIER = "intensifier"  # gar nicht, überhaupt nicht


class Negation(BaseModel):
    """Model representing a German negation word with its properties.

    German negation words follow specific rules for their position and usage:
    - 'nicht' typically comes at the end of the clause or before adjectives/adverbs
    - 'kein/keine' replace indefinite articles
    - Pronouns like 'nichts' and 'niemand' can be subjects or objects
    - Temporal and spatial negations follow time/place position rules
    """

    word: str = Field(..., description="The German negation word")
    english: str = Field(..., description="English translation")
    type: NegationType = Field(..., description="Type of negation")
    example: str = Field(..., description="Example sentence using the negation")

    def validate_example(self) -> bool:
        """Validate that the example contains the negation and follows basic rules.

        Returns:
            bool: True if the example is valid
        """
        # Example must contain the negation (case-insensitive)
        if not any(part.lower() in self.example.lower() for part in self.word.split()):
            print(f"Negation {self.word} not found in example")
            return False

        # Example must be a complete sentence
        if not any(self.example.endswith(p) for p in ".!?"):
            print("Example missing end punctuation")
            return False

        # Example must start with a capital letter
        if not self.example[0].isupper():
            print("Example does not start with capital letter")
            return False

        # Check negation position and usage
        return self.validate_position()

    def validate_position(self) -> bool:
        """Validate that the negation is in a valid position in the example sentence.

        Returns:
            bool: True if the negation position is valid
        """
        # Split the example into words
        words = self.example.rstrip(".!?").split()
        print(f"Validating position for {self.word} (type: {self.type})")
        print(f"Words in example: {words}")

        # Convert words to lowercase for case-insensitive comparison
        words_lower = [w.lower() for w in words]

        # For multi-word negations, find the position of the first word
        word_parts = self.word.lower().split()
        try:
            # Find position of first part
            neg_pos = words_lower.index(word_parts[0])
            print(f"Found {word_parts[0]} at position {neg_pos}")

            # For multi-word negations, verify all parts are present in sequence
            if len(word_parts) > 1:
                for i, part in enumerate(word_parts[1:], 1):
                    if (
                        neg_pos + i >= len(words_lower)
                        or words_lower[neg_pos + i] != part
                    ):
                        print(
                            f"Multi-word negation parts not in sequence at position {neg_pos + i}"
                        )
                        return False
        except ValueError:
            print(f"Could not find {self.word} in {words}")
            return False

        # General negation (nicht) typically comes at the end or before adjectives
        if self.type == NegationType.GENERAL:
            print("Checking general negation position")
            # Should not be at the start
            if neg_pos == 0:
                print("General negation at start - invalid")
                return False
            # Should be at the end or before an adjective/adverb
            if neg_pos == len(words) - 1:  # At end
                print("General negation at end - valid")
                return True
            if neg_pos < len(words) - 1:  # Before adjective/adverb
                print("General negation before next word - valid")
                return True

        # Article negations (kein/keine) come where articles would
        if self.type == NegationType.ARTICLE:
            print("Checking article negation position")
            # Should be followed by a noun (simplified check)
            if neg_pos < len(words) - 1:
                print("Article negation before noun - valid")
                return True

        # Pronouns can be subjects (start) or objects (middle/end)
        if self.type == NegationType.PRONOUN:
            print("Checking pronoun negation position")
            # Can be at start or in sentence
            if neg_pos == 0 or neg_pos > 0:
                print("Pronoun negation in valid position")
                return True

        # Temporal negations follow time expression rules
        if self.type == NegationType.TEMPORAL:
            print("Checking temporal negation position")
            # Should not be at the very end
            if neg_pos < len(words) - 1:
                print("Temporal negation in valid position")
                return True

        # Spatial negations follow place expression rules
        if self.type == NegationType.SPATIAL:
            print("Checking spatial negation position")
            # Should be in the middle or end of clause
            if neg_pos > 0:
                print("Spatial negation in valid position")
                return True

        # Correlative negations need their pair (simplified check)
        if self.type == NegationType.CORRELATIVE:
            print("Checking correlative negation position")
            # Should be followed by more words (for the 'noch' part)
            if neg_pos < len(words) - 2:
                print("Correlative negation with space for pair - valid")
                return True

        # Intensifiers modify other negations or come at clause end
        if self.type == NegationType.INTENSIFIER:
            print("Checking intensifier negation position")
            # Account for multi-word intensifiers
            total_words = len(word_parts)
            # Should be at end or before what they modify
            if neg_pos + total_words == len(words):  # At end
                print("Intensifier negation at end - valid")
                return True
            if neg_pos + total_words < len(words):  # Before what they modify
                print("Intensifier negation before modified word - valid")
                return True

        print("No valid position found")
        return False
