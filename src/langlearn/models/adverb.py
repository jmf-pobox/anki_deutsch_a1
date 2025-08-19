"""Model for German adverbs."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from .field_processor import (
    FieldProcessor,
    MediaGenerator,
    format_media_reference,
    validate_minimum_fields,
)


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


class Adverb(BaseModel, FieldProcessor):
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

    def get_image_search_terms(self) -> str:
        """Generate contextual image search terms prioritizing sentence context.

        Returns:
            Context-aware search terms generated from the example sentence,
            with fallback to adverb concept mappings
        """
        if not self.english.strip():
            return ""

        # Try to use Anthropic service for context-aware query generation
        try:
            from langlearn.services.anthropic_service import AnthropicService

            service = AnthropicService()
            context_query = service.generate_pexels_query(self)
            if context_query and context_query.strip():
                return context_query.strip()
        except Exception:
            # Fall back to concept mappings if Anthropic service fails
            pass

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

    # FieldProcessor interface implementation
    def process_fields_for_media_generation(
        self, fields: list[str], media_generator: MediaGenerator
    ) -> list[str]:
        """Process adverb fields with German-specific logic.

        Field Layout: [Word, English, Type, Example]

        Args:
            fields: Original field values
            media_generator: Interface for generating media

        Returns:
            Processed field values with media fields appended
        """
        validate_minimum_fields(fields, 4, "Adverb")

        # Extract field values
        word = fields[0]
        english = fields[1]
        # type_field = fields[2]  # AdverbType as string
        example = fields[3]

        # Create a copy and extend with media fields
        processed = fields.copy()

        # Ensure we have exactly 7 fields (4 original + 3 media)
        while len(processed) < 7:
            processed.append("")

        # Generate word audio if not present
        if not processed[4]:  # WordAudio field
            audio_path = media_generator.generate_audio(word)
            if audio_path:
                processed[4] = format_media_reference(audio_path, "audio")

        # Generate example audio if not present
        if not processed[5]:  # ExampleAudio field
            audio_path = media_generator.generate_audio(example)
            if audio_path:
                processed[5] = format_media_reference(audio_path, "audio")

        # Generate image if not present
        if not processed[6]:  # Image field
            # Create temporary adverb instance to get search terms
            try:
                adverb_type = AdverbType(fields[2])  # Convert string to AdverbType
                temp_adverb = Adverb(
                    word=word,
                    english=english,
                    type=adverb_type,
                    example=example,
                )
                search_terms = temp_adverb.get_image_search_terms()
                image_path = media_generator.generate_image(search_terms, english)
                if image_path:
                    processed[6] = format_media_reference(image_path, "image")
            except ValueError:
                # If adverb type is invalid, skip image generation
                pass

        return processed

    def get_expected_field_count(self) -> int:
        """Return expected number of fields for adverb cards."""
        return 4

    def validate_field_structure(self, fields: list[str]) -> bool:
        """Validate that fields match expected adverb structure."""
        return len(fields) >= 4

    def get_field_layout_info(self) -> dict[str, Any]:
        """Return information about the adverb field layout."""
        return {
            "model_type": "Adverb",
            "expected_field_count": 4,
            "field_names": self._get_field_names(),
            "description": "German adverb with type classification and examples",
        }

    def _get_field_names(self) -> list[str]:
        """Return the field names for adverb cards."""
        return [
            "Word",  # 0
            "English",  # 1
            "Type",  # 2
            "Example",  # 3
        ]
