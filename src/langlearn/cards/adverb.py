"""Card generator for adverbs."""

from pathlib import Path

from langlearn.backends.base import DeckBackend
from langlearn.cards.base import BaseCardGenerator
from langlearn.managers.media_manager import MediaManager
from langlearn.models.adverb import Adverb
from langlearn.services.german_language_service import GermanLanguageService
from langlearn.services.template_service import TemplateService


class AdverbCardGenerator(BaseCardGenerator[Adverb]):
    """Generator for adverb cards in Anki with type safety."""

    def __init__(
        self,
        backend: DeckBackend,
        template_service: TemplateService,
        media_manager: MediaManager | None = None,
        german_service: GermanLanguageService | None = None,
    ) -> None:
        """Initialize the adverb card generator.

        Args:
            backend: Backend implementation for deck operations
            template_service: Service for loading card templates
            media_manager: Optional media manager for audio/image generation
            german_service: Optional German language service for audio text generation
        """
        super().__init__(backend, template_service, "adverb", media_manager)
        self._german_service = german_service

    def _get_field_names(self) -> list[str]:
        """Get the list of field names for adverb cards.

        Returns:
            List of field names in the correct order
        """
        return [
            "Word",
            "English",
            "Type",
            "Example",
            "Image",
            "WordAudio",
            "ExampleAudio",
        ]

    def _extract_fields(self, data: Adverb) -> list[str]:
        """Extract field values from an Adverb model.

        Args:
            data: The Adverb model to extract fields from

        Returns:
            List of field values in the correct order
        """
        return [
            data.word,
            data.english,
            data.type.value,
            data.example,
            "",  # Image field (to be filled by media enhancement)
            "",  # WordAudio field (to be filled by media enhancement)
            "",  # ExampleAudio field (to be filled by media enhancement)
        ]

    def _enhance_fields_with_media(
        self, adverb: Adverb, fields: list[str]
    ) -> list[str]:
        """Enhance adverb fields with generated media (audio/images).

        Args:
            adverb: The Adverb model being processed
            fields: The base field values

        Returns:
            Enhanced field values with media references
        """
        if not self._media_manager:
            return fields

        enhanced_fields = fields.copy()

        # Handle word audio (index 5: WordAudio)
        audio_ref = self._get_or_generate_word_audio(adverb)
        if audio_ref:
            enhanced_fields[5] = audio_ref

        # Handle example audio (index 6: ExampleAudio)
        example_audio_ref = self._get_or_generate_example_audio(adverb)
        if example_audio_ref:
            enhanced_fields[6] = example_audio_ref

        # Handle image (index 4: Image)
        image_html = self._get_or_generate_image(adverb)
        if image_html:
            enhanced_fields[4] = image_html

        return enhanced_fields

    def _get_or_generate_word_audio(self, adverb: Adverb) -> str:
        """Get existing or generate word audio for adverb.

        Returns:
            Audio reference string or empty string if none available
        """
        if not self._media_manager:
            return ""

        # Check for existing word audio
        if adverb.word_audio and Path(adverb.word_audio).exists():
            audio_file = self._media_manager.add_media_file(adverb.word_audio)
            if audio_file:
                return audio_file.reference

        # Generate audio for adverb word only (no special forms like nouns/adjectives)
        audio_file = self._media_manager.generate_and_add_audio(adverb.word)
        if audio_file:
            return audio_file.reference

        return ""

    def _get_or_generate_example_audio(self, adverb: Adverb) -> str:
        """Get existing or generate example audio for adverb.

        Returns:
            Audio reference string or empty string if none available
        """
        if not self._media_manager:
            return ""

        # Check for existing example audio
        if adverb.example_audio and Path(adverb.example_audio).exists():
            example_audio_file = self._media_manager.add_media_file(
                adverb.example_audio
            )
            if example_audio_file:
                return example_audio_file.reference

        # Generate example sentence audio
        example_audio_file = self._media_manager.generate_and_add_audio(adverb.example)
        if example_audio_file:
            return example_audio_file.reference

        return ""

    def _get_or_generate_image(self, adverb: Adverb) -> str:
        """Get existing or generate image for adverb.

        Returns:
            Image HTML string or empty string if none available
        """
        if not self._media_manager:
            return ""

        # Check for existing image from CSV path
        if adverb.image_path and Path(adverb.image_path).exists():
            image_file = self._media_manager.add_media_file(adverb.image_path)
            if image_file:
                return f'<img src="{image_file.reference}">'

        # Check for existing image by expected filename pattern
        safe_filename = (
            "".join(c for c in adverb.word if c.isalnum() or c in (" ", "-", "_"))
            .rstrip()
            .replace(" ", "_")
            .lower()
        )
        expected_image_path = Path("data/images") / f"{safe_filename}.jpg"
        if expected_image_path.exists():
            image_file = self._media_manager.add_media_file(str(expected_image_path))
            if image_file:
                return f'<img src="{image_file.reference}">'

        # Generate image using domain model's enhanced search terms
        enhanced_search_query = adverb.get_image_search_terms()
        image_file = self._media_manager.generate_and_add_image(
            adverb.word,
            search_query=enhanced_search_query,
            example_sentence=adverb.example,
        )
        if image_file:
            return f'<img src="{image_file.reference}">'

        return ""
