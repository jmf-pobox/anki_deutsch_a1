"""Model for German adverbs."""

from enum import Enum

from pydantic import BaseModel, Field


class AdverbType(str, Enum):
    """Types of German adverbs."""

    LOCATION = "location"  # hier, dort, oben, unten
    TIME = "time"  # heute, morgen, jetzt
    FREQUENCY = "frequency"  # immer, oft, manchmal
    MANNER = "manner"  # gern, langsam, schnell
    INTENSITY = "intensity"  # sehr, zu, besonders
    ADDITION = "addition"  # auch
    LIMITATION = "limitation"  # nur
    ATTITUDE = "attitude"  # leider, natürlich
    PROBABILITY = "probability"  # vielleicht, wahrscheinlich


class Adverb(BaseModel):
    """Model representing a German adverb with its properties.

    German adverbs are words that modify verbs, adjectives, or other adverbs.
    They provide information about time, place, manner, degree, etc.
    Unlike adjectives, they do not change their form.
    """

    word: str = Field(..., description="The German adverb")
    english: str = Field(..., description="English translation")
    type: AdverbType = Field(..., description="Type of adverb")
    example: str = Field(..., description="Example sentence using the adverb")

    def validate_position(self) -> bool:
        """Validate that the adverb is in a valid position in the example sentence.

        Returns:
            bool: True if the adverb position is valid
        """
        # Split the example into words
        words = self.example.rstrip(".!?").split()
        print(f"Words: {words}")

        # Convert words to lowercase for case-insensitive comparison
        words_lower = [w.lower() for w in words]
        word_lower = self.word.lower()

        # Find the position of the adverb
        try:
            adverb_pos = words_lower.index(word_lower)
            print(f"Found {self.word} at position {adverb_pos}")
        except ValueError:
            print(f"Could not find {self.word} in {words}")
            return False

        # Time adverbs can be at the start, after the verb, or at the end
        if self.type == AdverbType.TIME:
            print(f"Checking time adverb position: {adverb_pos}")
            # Can be at the start of the sentence
            if adverb_pos == 0:
                print("Time adverb at start - valid")
                return True
            # Can be after the verb or at the end
            if adverb_pos > 0:
                print("Time adverb after start - valid")
                return True

        # Manner and frequency adverbs typically come after the verb
        if self.type in [AdverbType.MANNER, AdverbType.FREQUENCY]:
            # Can be after the verb
            if adverb_pos > 0:
                return True

        # Location adverbs typically come at the end
        if self.type == AdverbType.LOCATION:
            # Should be towards the end of the sentence
            if adverb_pos > 0:
                return True

        # Intensity adverbs come before what they modify
        if self.type == AdverbType.INTENSITY:
            # Should not be at the end
            if adverb_pos < len(words) - 1:
                return True

        # Modal adverbs (attitude, probability) often come in second position
        if self.type in [AdverbType.ATTITUDE, AdverbType.PROBABILITY]:
            # Can be at start or in second position
            if adverb_pos <= 1:
                return True

        # Addition and limitation adverbs are more flexible
        if self.type in [AdverbType.ADDITION, AdverbType.LIMITATION]:
            return True

        print("No valid position found")
        return False

    def validate_example(self) -> bool:
        """Validate that the example contains the adverb and follows basic rules.

        Returns:
            bool: True if the example is valid
        """
        # Example must contain the adverb (case-insensitive)
        if self.word.lower() not in self.example.lower():
            print(f"Adverb {self.word} not found in example")
            return False

        # Example must be a complete sentence
        if not any(self.example.endswith(p) for p in ".!?"):
            print("Example missing end punctuation")
            return False

        # Example must start with a capital letter
        if not self.example[0].isupper():
            print("Example does not start with capital letter")
            return False

        # Check adverb position
        return self.validate_position()
