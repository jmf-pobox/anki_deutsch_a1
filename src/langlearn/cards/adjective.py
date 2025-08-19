"""Card generator for adjectives."""

from langlearn.backends.base import DeckBackend
from langlearn.cards.base import BaseCardGenerator
from langlearn.managers.media_manager import MediaManager
from langlearn.models.adjective import Adjective
from langlearn.services.template_service import TemplateService


class AdjectiveCardGenerator(BaseCardGenerator[Adjective]):
    """Generator for adjective cards in Anki with type safety."""

    def __init__(
        self,
        backend: DeckBackend,
        template_service: TemplateService,
        media_manager: MediaManager | None = None,
    ) -> None:
        """Initialize the adjective card generator.

        Args:
            backend: Backend implementation for deck operations
            template_service: Service for loading card templates
            media_manager: Optional media manager for audio/image generation
        """
        super().__init__(backend, template_service, "adjective", media_manager)

    def _get_field_names(self) -> list[str]:
        """Get the list of field names for adjective cards.

        Returns:
            List of field names in the correct order
        """
        return [
            "Word",
            "English",
            "Example",
            "Comparative",
            "Superlative",
            "Image",
            "WordAudio",
            "ExampleAudio",
        ]

    def _extract_fields(self, data: Adjective) -> list[str]:
        """Extract field values from an Adjective model.

        Args:
            data: The Adjective model to extract fields from

        Returns:
            List of field values in the correct order
        """
        return [
            data.word,
            data.english,
            data.example,
            data.comparative,
            data.superlative,
            "",  # Image field (to be filled by media enhancement)
            "",  # WordAudio field (to be filled by media enhancement)
            "",  # ExampleAudio field (to be filled by media enhancement)
        ]

    def _enhance_fields_with_media(
        self, adjective: Adjective, fields: list[str]
    ) -> list[str]:
        """Enhance adjective fields with generated media (audio/images).

        Args:
            adjective: The Adjective model being processed
            fields: The base field values

        Returns:
            Enhanced field values with media references
        """
        if not self._media_manager:
            return fields

        enhanced_fields = fields.copy()

        # Handle word audio (index 6: WordAudio)
        audio_ref = self._get_or_generate_word_audio(adjective)
        if audio_ref:
            enhanced_fields[6] = audio_ref

        # Handle example audio (index 7: ExampleAudio)
        example_audio_ref = self._get_or_generate_example_audio(adjective)
        if example_audio_ref:
            enhanced_fields[7] = example_audio_ref

        # Handle image (index 5: Image)
        image_html = self._get_or_generate_image(adjective)
        if image_html:
            enhanced_fields[5] = image_html

        return enhanced_fields

    def _get_or_generate_word_audio(self, adjective: Adjective) -> str:
        """Get existing or generate word audio for adjective.

        Returns:
            Audio reference string or empty string if none available
        """
        if not self._media_manager:
            return ""

        # Check for existing word audio (field no longer exists on model)
        # Audio generation now handled by field processor during CSV processing

        # Generate audio for combined adjective forms using domain model
        audio_text = adjective.get_combined_audio_text()
        audio_file = self._media_manager.generate_and_add_audio(audio_text)
        if audio_file:
            return audio_file.reference

        return ""

    def _get_or_generate_example_audio(self, adjective: Adjective) -> str:
        """Get existing or generate example audio for adjective.

        Returns:
            Audio reference string or empty string if none available
        """
        if not self._media_manager:
            return ""

        # Check for existing example audio (field no longer exists on model)
        # Audio generation now handled by field processor during CSV processing

        # Generate example sentence audio
        example_audio_file = self._media_manager.generate_and_add_audio(
            adjective.example
        )
        if example_audio_file:
            return example_audio_file.reference

        return ""

    def _get_or_generate_image(self, adjective: Adjective) -> str:
        """Get existing or generate image for adjective.

        Returns:
            Image HTML string or empty string if none available
        """
        if not self._media_manager:
            return ""

        # Check for existing image (field no longer exists on model)
        # Image generation now handled by field processor during CSV processing

        # Generate image using domain model's enhanced search terms
        enhanced_search_query = adjective.get_image_search_terms()
        image_file = self._media_manager.generate_and_add_image(
            adjective.word,
            search_query=enhanced_search_query,
            example_sentence=adjective.example,
        )
        if image_file:
            return f'<img src="{image_file.reference}">'

        return ""
