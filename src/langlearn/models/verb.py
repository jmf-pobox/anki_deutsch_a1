"""Model for German verbs with field processing capabilities."""

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


class Verb(BaseModel, FieldProcessor):
    """Model representing a German verb with its conjugations.

    Implements FieldProcessor interface to handle its own field processing
    for media generation, following Domain-Driven Design principles.
    Enhanced to match VerbRecord structure with all tenses.
    """

    verb: str = Field(..., description="The German verb in infinitive form")
    english: str = Field(..., description="English translation")
    classification: str = Field(default="", description="Verb classification (regelmäßig, unregelmäßig, gemischt)")
    present_ich: str = Field(..., description="First person singular present tense")
    present_du: str = Field(..., description="Second person singular present tense")
    present_er: str = Field(..., description="Third person singular present tense")
    präteritum: str = Field(default="", description="Präteritum 3rd person singular form")
    auxiliary: str = Field(default="", description="Auxiliary verb (haben or sein)")
    perfect: str = Field(..., description="Perfect tense form")
    example: str = Field(..., description="Example sentence using the verb")
    separable: bool = Field(default=False, description="Whether the verb is separable")

    # Media fields (not from CSV but added during processing)
    word_audio: str = Field(
        default="", description="Audio file path for conjugated verb"
    )
    example_audio: str = Field(
        default="", description="Audio file path for example sentence"
    )
    image_path: str = Field(
        default="", description="Image file path for verb visualization"
    )

    def process_fields_for_media_generation(
        self, fields: list[str], media_generator: "MediaGenerator"
    ) -> list[str]:
        """Process verb fields for media generation.

        Field layout:
            [Verb, English, ich_form, du_form, er_form, perfect, Example, ExampleAudio]

        Args:
            fields: List of field values from the note
            media_generator: Interface for generating media files

        Returns:
            Updated fields list with media references
        """
        try:
            validate_minimum_fields(fields, self.get_expected_field_count(), "Verb")
        except FieldProcessingError:
            return fields

        # Create working copy
        processed_fields = fields.copy()

        # Extract field values for processing
        if len(fields) < 8:
            return processed_fields

        example = fields[6] if len(fields) > 6 else ""

        # Generate example audio if ExampleAudio field (index 7) is empty
        if len(processed_fields) > 7 and not processed_fields[7] and example:
            audio_path = media_generator.generate_audio(example)
            if audio_path:
                processed_fields[7] = format_media_reference(audio_path, "audio")

        return processed_fields

    def get_expected_field_count(self) -> int:
        """Return expected number of fields for verb notes.

        Returns:
            8 fields: (Verb, English, ich_form, du_form, er_form, perfect,
                     Example, ExampleAudio)
        """
        return 8

    def validate_field_structure(self, fields: list[str]) -> bool:
        """Validate that fields match expected verb structure.

        Args:
            fields: Field values to validate

        Returns:
            True if fields have valid verb structure
        """
        return len(fields) >= self.get_expected_field_count()

    def _get_field_names(self) -> list[str]:
        """Return the field names for verb cards.

        Returns:
            List of field names corresponding to field positions
        """
        return [
            "Verb",  # 0
            "English",  # 1
            "ich_form",  # 2
            "du_form",  # 3
            "er_form",  # 4
            "perfect",  # 5
            "Example",  # 6
            "ExampleAudio",  # 7
        ]

    def get_combined_audio_text(self) -> str:
        """Get combined text for verb conjugation audio with German tense labels.

        Returns:
            Combined text with German tense labels and all conjugations:
            "arbeiten, Präsens ich arbeite, du arbeitest, er sie es arbeitet, Präteritum er sie es arbeitete, Perfekt er sie es hat gearbeitet"
        """
        parts = [self.verb]
        
        # Präsens (Present tense) with German label
        if self.present_ich or self.present_du or self.present_er:
            parts.append("Präsens")
            if self.present_ich:
                parts.append(f"ich {self.present_ich}")
            if self.present_du:
                parts.append(f"du {self.present_du}")
            if self.present_er:
                parts.append(f"er sie es {self.present_er}")
        
        # Präteritum with German label
        if self.präteritum:
            parts.extend(["Präteritum", f"er sie es {self.präteritum}"])
        
        # Perfekt with German label
        if self.perfect:
            # The perfect form typically already includes the auxiliary verb
            parts.extend(["Perfekt", f"er sie es {self.perfect}"])
        
        return ", ".join(parts)
