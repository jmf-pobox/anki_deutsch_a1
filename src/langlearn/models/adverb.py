"""Model for German adverbs."""

from enum import Enum
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from collections.abc import Callable

# Removed field_processor import - now pure domain model


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
    """Model representing a German adverb with its properties and business logic.

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
        if self.type in [AdverbType.MANNER, AdverbType.FREQUENCY] and adverb_pos > 0:
            return True

        # Location adverbs typically come at the end
        if self.type == AdverbType.LOCATION and adverb_pos > 0:
            return True

        # Intensity adverbs come before what they modify
        if self.type == AdverbType.INTENSITY and adverb_pos < len(words) - 1:
            return True

        # Modal adverbs (attitude, probability) often come in second position
        if (
            self.type in [AdverbType.ATTITUDE, AdverbType.PROBABILITY]
            and adverb_pos <= 1
        ):
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

    def get_image_search_strategy(self) -> "Callable[[], str]":
        """Get a strategy for generating search terms without executing it immediately.
        
        This lazy evaluation approach prevents unnecessary Anthropic API calls
        when images already exist or aren't needed.

        Returns:
            A callable that when invoked will generate context-aware search terms,
            with fallback to adverb concept mappings
        """
        def generate_search_terms() -> str:
            """Execute the search term generation strategy."""
            if not self.english.strip():
                return ""

            # Try to use Anthropic service for context-aware query generation
            try:
                from langlearn.services.service_container import get_anthropic_service

                service = get_anthropic_service()
                if service:
                    context_query = service.generate_pexels_query(self)
                    if context_query and context_query.strip():
                        return context_query.strip()
            except Exception:
                # Fall back to concept mappings if Anthropic service fails
                pass
            
            # Return fallback search terms
            return self._get_fallback_search_terms()
        
        return generate_search_terms
    
    def get_image_search_terms(self) -> str:
        """Legacy method for backward compatibility - executes strategy immediately.
        
        Note: This method maintains compatibility but should be replaced with
        get_image_search_strategy() for better performance.
        """
        strategy = self.get_image_search_strategy()
        return strategy()
    
    def _get_fallback_search_terms(self) -> str:
        """Get fallback search terms using adverb concept mappings."""

        # Most adverbs are abstract concepts, so use enhanced search terms
        concept_mappings = {
            "here": "location place here",
            "there": "location place there",
            "today": "calendar today current day",
            "tomorrow": "calendar future tomorrow",
            "yesterday": "calendar past yesterday",
            "always": "infinity symbol always",
            "never": "prohibition never symbol",
            "often": "frequency often regular",
            "sometimes": "occasionally sometimes",
            "slowly": "slow motion turtle snail",
            "quickly": "speed fast motion",
            "very": "intensity emphasis very",
            "too": "excessive too much",
            "inside": "interior indoor inside",
            "outside": "exterior outdoor outside",
            "above": "up arrow above over",
            "below": "down arrow below under",
            "front": "forward direction front",
            "behind": "backward direction behind",
        }

        english_lower = self.english.lower()
        for key, enhanced_terms in concept_mappings.items():
            if key in english_lower:
                return enhanced_terms

        # For location adverbs, add "location" context
        if self.type == AdverbType.LOCATION:
            return f"{self.english} location place"

        # For time adverbs, add "time" context
        if self.type == AdverbType.TIME:
            return f"{self.english} time clock calendar"

        # For manner adverbs, add "way" context
        if self.type == AdverbType.MANNER:
            return f"{self.english} way method manner"

        # Default to the English translation with concept indicator
        return f"{self.english} concept symbol"


# Removed field processing methods - now pure domain model with only business logic
