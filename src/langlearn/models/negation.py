"""Model for German negation words."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from .field_processor import (
    FieldProcessor,
    MediaGenerator,
    format_media_reference,
    validate_minimum_fields,
)


class NegationType(str, Enum):
    """Types of German negation words."""

    GENERAL = "general"  # nicht
    ARTICLE = "article"  # kein, keine
    PRONOUN = "pronoun"  # nichts, niemand
    TEMPORAL = "temporal"  # nie, niemals
    SPATIAL = "spatial"  # nirgends, nirgendwo
    CORRELATIVE = "correlative"  # weder...noch
    INTENSIFIER = "intensifier"  # gar nicht, überhaupt nicht


class Negation(BaseModel, FieldProcessor):
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
    word_audio: str = Field("", description="Path to audio file for the negation")
    example_audio: str = Field("", description="Path to audio file for the example")
    image_path: str = Field("", description="Path to image file for the negation")

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
                            f"Multi-word negation parts not in sequence at "
                            f"position {neg_pos + i}"
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

    def get_image_search_terms(self) -> str:
        """Generate contextual image search terms for this negation.

        Returns:
            Search terms optimized for finding relevant images
        """
        if not self.english.strip():
            return ""

        # Negation words are abstract concepts, so use enhanced search terms
        # Check for exact matches first, then partial matches (longer first)
        concept_mappings = [
            ("nobody", "empty person silhouette nobody"),
            ("nothing", "empty void blank nothing"),
            ("nowhere", "empty space void location"),
            ("neither", "choice rejection either"),
            ("never", "infinity crossed out never"),
            (
                "no/not a",
                "crossed out circle prohibition stop sign",
            ),  # Better search terms
            ("not", "prohibition stop sign red x"),
            ("no", "negative denial no symbol"),
        ]

        english_lower = self.english.lower()
        for key, enhanced_terms in concept_mappings:
            if key in english_lower:
                return enhanced_terms

        # For different negation types, add context
        type_mappings = {
            NegationType.GENERAL: f"{self.english} prohibition stop sign",
            NegationType.ARTICLE: f"{self.english} denial rejection symbol",
            NegationType.PRONOUN: f"{self.english} empty void absence",
            NegationType.TEMPORAL: f"{self.english} time crossed out never",
            NegationType.SPATIAL: f"{self.english} location empty void",
            NegationType.CORRELATIVE: f"{self.english} choice rejection neither",
            NegationType.INTENSIFIER: f"{self.english} emphasis prohibition strong",
        }
        return type_mappings.get(
            self.type, f"{self.english} negation prohibition symbol"
        )

    # FieldProcessor interface implementation
    def process_fields_for_media_generation(
        self, fields: list[str], media_generator: MediaGenerator
    ) -> list[str]:
        """Process negation fields with German-specific logic.

        Field Layout: [Word, English, Type, Example, WordAudio, ExampleAudio, Image]

        Args:
            fields: Original field values
            media_generator: Interface for generating media

        Returns:
            Processed field values with media
        """
        validate_minimum_fields(fields, 7, "Negation")

        # Extract field values
        word = fields[0]
        english = fields[1]
        # type_field = fields[2]  # NegationType as string
        example = fields[3]

        # Create a copy to modify
        processed = fields.copy()

        # Only generate word audio if WordAudio field (index 4) is empty
        if not processed[4]:  # WordAudio field
            audio_path = media_generator.generate_audio(word)
            if audio_path:
                processed[4] = format_media_reference(audio_path, "audio")

        # Only generate example audio if ExampleAudio field (index 5) is empty
        if not processed[5]:  # ExampleAudio field
            audio_path = media_generator.generate_audio(example)
            if audio_path:
                processed[5] = format_media_reference(audio_path, "audio")

        # Only generate image if Image field (index 6) is empty
        if not processed[6]:  # Image field
            # Create temporary negation instance to get search terms
            try:
                negation_type = NegationType(
                    fields[2]
                )  # Convert string to NegationType
                temp_negation = Negation(
                    word=word,
                    english=english,
                    type=negation_type,
                    example=example,
                    word_audio="",
                    example_audio="",
                    image_path="",
                )
                search_terms = temp_negation.get_image_search_terms()
                image_path = media_generator.generate_image(search_terms, english)
                if image_path:
                    processed[6] = format_media_reference(image_path, "image")
            except ValueError:
                # If negation type is invalid, skip image generation
                pass

        return processed

    def get_expected_field_count(self) -> int:
        """Return expected number of fields for negation cards."""
        return 7

    def validate_field_structure(self, fields: list[str]) -> bool:
        """Validate that fields match expected negation structure."""
        return len(fields) >= 7

    def get_field_layout_info(self) -> dict[str, Any]:
        """Return information about the negation field layout."""
        return {
            "model_type": "Negation",
            "expected_field_count": 7,
            "field_names": self._get_field_names(),
            "description": "German negation with type classification and examples",
        }

    def _get_field_names(self) -> list[str]:
        """Return the field names for negation cards."""
        return [
            "Word",  # 0
            "English",  # 1
            "Type",  # 2
            "Example",  # 3
            "WordAudio",  # 4
            "ExampleAudio",  # 5
            "Image",  # 6
        ]
