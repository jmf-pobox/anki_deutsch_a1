"""Model for German prepositions with field processing capabilities."""

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


class Preposition(BaseModel, FieldProcessor):
    """Model representing a German preposition with its properties.

    Implements FieldProcessor interface to handle its own field processing
    for media generation, following Domain-Driven Design principles.
    """

    preposition: str = Field(..., description="The German preposition")
    english: str = Field(..., description="English translation")
    case: str = Field(
        ...,
        description="The case(s) the preposition takes (Accusative/Dative/Genitive)",
    )
    example1: str = Field(..., description="First example sentence")
    example2: str = Field(..., description="Second example sentence")

    # Media fields (not from CSV but added during processing)
    audio1: str = Field(default="", description="Audio file path for first example")
    audio2: str = Field(default="", description="Audio file path for second example")
    image_path: str = Field(
        default="", description="Image file path for preposition visualization"
    )

    def process_fields_for_media_generation(
        self, fields: list[str], media_generator: "MediaGenerator"
    ) -> list[str]:
        """Process preposition fields for media generation.

        Field layout:
            [Preposition, English, Case, Example1, Example2, Audio1, Audio2]

        Args:
            fields: List of field values from the note
            media_generator: Interface for generating media files

        Returns:
            Updated fields list with media references
        """
        try:
            validate_minimum_fields(
                fields, self.get_expected_field_count(), "Preposition"
            )
        except FieldProcessingError:
            return fields

        # Create working copy
        processed_fields = fields.copy()

        # Extract field values for processing
        if len(fields) < 7:
            return processed_fields

        example1 = fields[3] if len(fields) > 3 else ""
        example2 = fields[4] if len(fields) > 4 else ""

        # Generate audio for first example if Audio1 field (index 5) is empty
        if len(processed_fields) > 5 and not processed_fields[5] and example1:
            audio_path = media_generator.generate_audio(example1)
            if audio_path:
                processed_fields[5] = format_media_reference(audio_path, "audio")

        # Generate audio for second example if Audio2 field (index 6) is empty
        if len(processed_fields) > 6 and not processed_fields[6] and example2:
            audio_path = media_generator.generate_audio(example2)
            if audio_path:
                processed_fields[6] = format_media_reference(audio_path, "audio")

        return processed_fields

    def get_expected_field_count(self) -> int:
        """Return expected number of fields for preposition notes.

        Returns:
            7 fields: (Preposition, English, Case, Example1, Example2, Audio1, Audio2)
        """
        return 7

    def validate_field_structure(self, fields: list[str]) -> bool:
        """Validate that fields match expected preposition structure.

        Args:
            fields: Field values to validate

        Returns:
            True if fields have valid preposition structure
        """
        return len(fields) >= self.get_expected_field_count()

    def _get_field_names(self) -> list[str]:
        """Return the field names for preposition cards.

        Returns:
            List of field names corresponding to field positions
        """
        return [
            "Preposition",  # 0
            "English",  # 1
            "Case",  # 2
            "Example1",  # 3
            "Example2",  # 4
            "Audio1",  # 5
            "Audio2",  # 6
        ]

    def get_case_description(self) -> str:
        """Get human-readable description of the grammatical case(s).

        Returns:
            Formatted description of case usage
        """
        case_descriptions = {
            "accusative": "takes accusative case (direct object)",
            "dative": "takes dative case (indirect object)",
            "genitive": "takes genitive case (possession)",
            "accusative/dative": "takes accusative (motion) or dative (location)",
        }

        case_lower = self.case.lower()
        return case_descriptions.get(case_lower, f"takes {self.case} case")

    def is_two_way_preposition(self) -> bool:
        """Check if this preposition can take both accusative and dative cases.

        Returns:
            True if preposition takes both accusative and dative
        """
        return (
            "/" in self.case.lower()
            and "accusative" in self.case.lower()
            and "dative" in self.case.lower()
        )
