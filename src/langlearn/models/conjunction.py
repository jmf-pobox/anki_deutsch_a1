"""Model for German conjunctions."""

from enum import Enum

from pydantic import BaseModel, Field


class ConjunctionType(str, Enum):
    """Types of German conjunctions."""

    COORDINATING = "coordinating"  # und, oder, aber, denn, sondern
    SUBORDINATING = "subordinating"  # weil, dass, wenn, obwohl
    CORRELATIVE = "correlative"  # entweder...oder, sowohl...als auch
    ADVERBIAL = "adverbial"  # deshalb, trotzdem, daher


class Conjunction(BaseModel):
    """Model representing a German conjunction with its properties.

    German conjunctions are words that connect clauses, phrases, or words.
    They can be coordinating (connecting equal elements) or subordinating
    (introducing dependent clauses).
    """

    word: str = Field(..., description="The German conjunction")
    english: str = Field(..., description="English translation")
    type: ConjunctionType = Field(..., description="Type of conjunction")
    example: str = Field(..., description="Example sentence using the conjunction")

    def validate_example(self) -> bool:
        """Validate that the example contains the conjunction and follows basic rules.

        Returns:
            bool: True if the example is valid
        """
        # Example must contain the conjunction (case-insensitive)
        if self.word.lower() not in self.example.lower():
            print(f"Conjunction {self.word} not found in example")
            return False

        # Example must be a complete sentence
        if not any(self.example.endswith(p) for p in ".!?"):
            print("Example missing end punctuation")
            return False

        # Example must start with a capital letter
        if not self.example[0].isupper():
            print("Example does not start with capital letter")
            return False

        # Check conjunction position and usage
        return self.validate_position()

    def validate_position(self) -> bool:
        """Validate that the conjunction is in a valid position in the example sentence.

        Returns:
            bool: True if the conjunction position is valid
        """
        # Split the example into words
        words = self.example.rstrip(".!?").split()
        print(f"Validating position for {self.word} (type: {self.type})")
        print(f"Words in example: {words}")

        # Convert words to lowercase for case-insensitive comparison
        words_lower = [w.lower() for w in words]
        word_lower = self.word.lower()

        # Find the position of the conjunction
        try:
            conj_pos = words_lower.index(word_lower)
            print(f"Found {self.word} at position {conj_pos}")
        except ValueError:
            print(f"Could not find {self.word} in {words}")
            return False

        # Coordinating conjunctions typically come between clauses
        if self.type == ConjunctionType.COORDINATING:
            print("Checking coordinating conjunction position")
            # Should not be at the start or end of the sentence
            if 0 < conj_pos < len(words) - 1:
                print("Coordinating conjunction in valid position")
                return True
            print("Coordinating conjunction in invalid position")

        # Subordinating conjunctions typically start the dependent clause
        if self.type == ConjunctionType.SUBORDINATING:
            print("Checking subordinating conjunction position")
            # Should be at the start of the dependent clause
            # This is a simplified check - in reality, we'd need to parse the sentence structure
            if conj_pos > 0:  # Not at the start of the main clause
                print("Subordinating conjunction in valid position")
                return True
            print("Subordinating conjunction in invalid position")

        # Correlative conjunctions come in pairs
        if self.type == ConjunctionType.CORRELATIVE:
            print("Checking correlative conjunction position")
            # This is a simplified check - in reality, we'd need to check for both parts
            if conj_pos == 0:  # Should be at the start
                print("Correlative conjunction in valid position")
                return True
            print("Correlative conjunction in invalid position")

        # Adverbial conjunctions can be at the start or in the middle
        if self.type == ConjunctionType.ADVERBIAL:
            print("Checking adverbial conjunction position")
            # Should be after the main clause but not at the end
            if 0 < conj_pos < len(words) - 1:  # Not at start or end
                print("Adverbial conjunction in valid position")
                return True
            print("Adverbial conjunction in invalid position")

        print("No valid position found")
        return False
