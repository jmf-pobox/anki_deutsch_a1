"""Model for German phrases with field processing capabilities."""

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from .field_processor import (
    FieldProcessingError,
    FieldProcessor,
    format_media_reference,
    validate_minimum_fields,
)

if TYPE_CHECKING:
    from .field_processor import MediaGenerator


class Phrase(BaseModel, FieldProcessor):
    """Model representing a German phrase with its properties.

    Implements FieldProcessor interface to handle its own field processing
    for media generation, following Domain-Driven Design principles.
    """

    phrase: str = Field(..., description="The German phrase")
    english: str = Field(..., description="English translation")
    context: str = Field(..., description="Context or usage description")
    related: str = Field(..., description="Related phrases")

    # Media fields (not from CSV but added during processing)
    phrase_audio: str = Field(
        default="", description="Audio file path for phrase pronunciation"
    )
    image_path: str = Field(
        default="", description="Image file path for phrase visualization"
    )

    def process_fields_for_media_generation(
        self, fields: list[str], media_generator: "MediaGenerator"
    ) -> list[str]:
        """Process phrase fields for media generation.

        Field layout:
            [Phrase, English, Context, Related, PhraseAudio]

        Args:
            fields: List of field values from the note
            media_generator: Interface for generating media files

        Returns:
            Updated fields list with media references
        """
        try:
            validate_minimum_fields(fields, self.get_expected_field_count(), "Phrase")
        except FieldProcessingError:
            return fields

        # Create working copy
        processed_fields = fields.copy()

        # Extract field values for processing
        if len(fields) < 5:
            return processed_fields

        phrase = fields[0] if len(fields) > 0 else ""

        # Generate phrase audio if PhraseAudio field (index 4) is empty
        if len(processed_fields) > 4 and not processed_fields[4] and phrase:
            audio_path = media_generator.generate_audio(phrase)
            if audio_path:
                processed_fields[4] = format_media_reference(audio_path, "audio")

        return processed_fields

    def get_expected_field_count(self) -> int:
        """Return expected number of fields for phrase notes.

        Returns:
            5 fields: (Phrase, English, Context, Related, PhraseAudio)
        """
        return 5

    def validate_field_structure(self, fields: list[str]) -> bool:
        """Validate that fields match expected phrase structure.

        Args:
            fields: Field values to validate

        Returns:
            True if fields have valid phrase structure
        """
        return len(fields) >= self.get_expected_field_count()

    def _get_field_names(self) -> list[str]:
        """Return the field names for phrase cards.

        Returns:
            List of field names corresponding to field positions
        """
        return [
            "Phrase",  # 0
            "English",  # 1
            "Context",  # 2
            "Related",  # 3
            "PhraseAudio",  # 4
        ]

    def is_greeting(self) -> bool:
        """Check if this phrase is a greeting.

        Returns:
            True if phrase appears to be a greeting
        """
        greeting_indicators = ["guten", "hallo", "hi", "greeting"]
        phrase_lower = self.phrase.lower()
        context_lower = self.context.lower()

        return any(
            indicator in phrase_lower or indicator in context_lower
            for indicator in greeting_indicators
        )

    def is_farewell(self) -> bool:
        """Check if this phrase is a farewell expression.

        Returns:
            True if phrase appears to be a farewell
        """
        farewell_indicators = ["auf wiedersehen", "tschüss", "bis", "goodbye", "bye"]
        phrase_lower = self.phrase.lower()
        context_lower = self.context.lower()

        return any(
            indicator in phrase_lower or indicator in context_lower
            for indicator in farewell_indicators
        )

    def get_phrase_category(self) -> str:
        """Categorize the phrase based on its content and context.

        Returns:
            Category name for the phrase
        """
        if self.is_greeting():
            return "greeting"
        elif self.is_farewell():
            return "farewell"
        elif any(word in self.context.lower() for word in ["polite", "formal"]):
            return "formal"
        elif any(word in self.context.lower() for word in ["informal", "casual"]):
            return "informal"
        else:
            return "general"
