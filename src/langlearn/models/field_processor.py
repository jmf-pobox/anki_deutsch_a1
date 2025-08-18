"""
Abstract base classes and protocols for domain field processing.

This module provides the interface that domain models must implement to handle
their own field processing logic, separating German grammar rules from
infrastructure concerns.
"""

import os
from abc import ABC, abstractmethod
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class MediaGenerator(Protocol):
    """Protocol for media generation services.

    This interface allows domain models to request media generation
    without depending on specific infrastructure implementations.
    """

    def generate_audio(self, text: str) -> str | None:
        """Generate audio file for the given text.

        Args:
            text: Text to convert to speech

        Returns:
            Path to generated audio file, or None if generation failed
        """
        ...

    def generate_image(self, query: str, backup_query: str | None = None) -> str | None:
        """Generate/download image for the given search query.

        Args:
            query: Primary image search query
            backup_query: Fallback query if primary fails

        Returns:
            Path to generated/downloaded image, or None if generation failed
        """
        ...

    def get_context_enhanced_query(self, word: str, english: str, example: str) -> str:
        """Get context-enhanced search query from German sentence analysis.

        Args:
            word: German word
            english: English translation
            example: German example sentence

        Returns:
            Enhanced search query with contextual information
        """
        ...

    def get_conceptual_search_terms(
        self, word_type: str, word: str, english: str
    ) -> str:
        """Get conceptual search terms for abstract words.

        Args:
            word_type: Type of word (adverb, negation, etc.)
            word: German word
            english: English translation

        Returns:
            Search terms for conceptual imagery
        """
        ...


class FieldProcessor(ABC):
    """Abstract base class for domain models that process their own fields.

    This class establishes the contract that all German vocabulary domain models
    must follow to handle their field processing logic. This separates German
    grammar rules from infrastructure concerns like Anki API integration.
    """

    @abstractmethod
    def process_fields_for_media_generation(
        self, fields: list[str], media_generator: MediaGenerator
    ) -> list[str]:
        """Process model-specific field layout with media generation.

        This method contains the German grammar and vocabulary-specific logic
        for processing field layouts, determining which fields need media,
        and coordinating media generation through the MediaGenerator interface.

        Args:
            fields: List of field values in the expected order for this model type
            media_generator: Interface for generating audio/image media

        Returns:
            Processed field list with media references added where appropriate

        Raises:
            ValueError: If fields don't match expected structure
        """

    @abstractmethod
    def get_expected_field_count(self) -> int:
        """Return expected number of fields for this model type.

        Returns:
            Number of fields expected in the field processing method
        """

    @abstractmethod
    def validate_field_structure(self, fields: list[str]) -> bool:
        """Validate that fields match expected structure for this model.

        Args:
            fields: Field list to validate

        Returns:
            True if field structure is valid for this model type
        """

    def get_field_layout_info(self) -> dict[str, Any]:
        """Get information about this model's field layout.

        This method provides metadata about the field structure for
        debugging and documentation purposes.

        Returns:
            Dictionary containing field layout information
        """
        return {
            "model_type": self.__class__.__name__,
            "expected_field_count": self.get_expected_field_count(),
            "field_names": self._get_field_names(),
        }

    @abstractmethod
    def _get_field_names(self) -> list[str]:
        """Get human-readable names for each field position.

        Returns:
            List of field names corresponding to field positions
        """


class FieldProcessingError(Exception):
    """Exception raised when field processing encounters an error.

    This exception preserves the original field data and provides context
    about what went wrong during processing.
    """

    def __init__(self, message: str, original_fields: list[str], model_type: str):
        """Initialize field processing error.

        Args:
            message: Error description
            original_fields: The field data that caused the error
            model_type: Type of model that encountered the error
        """
        super().__init__(message)
        self.original_fields = original_fields
        self.model_type = model_type
        self.message = message

    def __str__(self) -> str:
        return (
            f"{self.message} "
            f"(Model: {self.model_type}, Fields: {len(self.original_fields)})"
        )


def format_media_reference(media_path: str | None, media_type: str) -> str:
    """Format media path as appropriate reference for Anki cards.

    Args:
        media_path: Path to media file, or None if generation failed
        media_type: Type of media ('audio' or 'image')

    Returns:
        Formatted media reference, or empty string if media_path is None
    """
    if not media_path:
        return ""

    filename = os.path.basename(media_path)

    if media_type == "audio":
        return f"[sound:{filename}]"
    elif media_type == "image":
        return f'<img src="{filename}">'
    else:
        raise ValueError(f"Unknown media type: {media_type}")


def validate_minimum_fields(
    fields: list[str], minimum_count: int, model_type: str
) -> None:
    """Validate that field list meets minimum length requirement.

    Args:
        fields: Field list to validate
        minimum_count: Minimum number of fields required
        model_type: Type of model for error reporting

    Raises:
        FieldProcessingError: If fields list is too short
    """
    if len(fields) < minimum_count:
        raise FieldProcessingError(
            f"Insufficient fields: got {len(fields)}, need at least {minimum_count}",
            fields,
            model_type,
        )
