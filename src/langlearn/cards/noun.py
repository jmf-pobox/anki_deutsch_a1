"""Card generator for nouns."""

from pathlib import Path

from langlearn.backends.base import DeckBackend
from langlearn.cards.base import BaseCardGenerator
from langlearn.managers.media_manager import MediaManager
from langlearn.models.noun import Noun
from langlearn.services.template_service import TemplateService


class NounCardGenerator(BaseCardGenerator[Noun]):
    """Generator for noun cards in Anki with type safety."""

    def __init__(
        self,
        backend: DeckBackend,
        template_service: TemplateService,
        media_manager: MediaManager | None = None,
    ) -> None:
        """Initialize the noun card generator.

        Args:
            backend: Backend implementation for deck operations
            template_service: Service for loading card templates
            media_manager: Optional media manager for audio/image generation
        """
        super().__init__(backend, template_service, "noun", media_manager)

    def _get_field_names(self) -> list[str]:
        """Get the list of field names for noun cards.

        Returns:
            List of field names in the correct order
        """
        return [
            "Noun",
            "Article",
            "English",
            "Plural",
            "Example",
            "Related",
            "Image",
            "WordAudio",
            "ExampleAudio",
        ]

    def _extract_fields(self, data: Noun) -> list[str]:
        """Extract field values from a Noun model.

        Args:
            data: The Noun model to extract fields from

        Returns:
            List of field values in the correct order
        """
        return [
            data.noun,
            data.article,
            data.english,
            data.plural,
            data.example,
            data.related,
            "",  # Image field (to be filled by media enhancement)
            "",  # WordAudio field (to be filled by media enhancement)
            "",  # ExampleAudio field (to be filled by media enhancement)
        ]

    def _enhance_fields_with_media(self, noun: Noun, fields: list[str]) -> list[str]:
        """Enhance noun fields with generated media (audio/images).

        Args:
            noun: The Noun model being processed
            fields: The base field values

        Returns:
            Enhanced field values with media references
        """
        if not self._media_manager:
            return fields

        enhanced_fields = fields.copy()

        # Handle word audio (index 7: WordAudio)
        audio_ref = self._get_or_generate_word_audio(noun)
        if audio_ref:
            enhanced_fields[7] = audio_ref

        # Handle example audio (index 8: ExampleAudio)
        example_audio_ref = self._get_or_generate_example_audio(noun)
        if example_audio_ref:
            enhanced_fields[8] = example_audio_ref

        # Handle image (index 6: Image)
        image_html = self._get_or_generate_image(noun)
        if image_html:
            enhanced_fields[6] = image_html

        return enhanced_fields

    def _get_or_generate_word_audio(self, noun: Noun) -> str:
        """Get existing or generate word audio for noun.

        Returns:
            Audio reference string or empty string if none available
        """
        if not self._media_manager:
            return ""

        # Check for existing word audio
        if noun.word_audio and Path(noun.word_audio).exists():
            audio_file = self._media_manager.add_media_file(noun.word_audio)
            if audio_file:
                return audio_file.reference

        # Generate audio for combined noun forms using domain model
        audio_text = noun.get_combined_audio_text()
        audio_file = self._media_manager.generate_and_add_audio(audio_text)
        if audio_file:
            return audio_file.reference

        return ""

    def _get_or_generate_example_audio(self, noun: Noun) -> str:
        """Get existing or generate example audio for noun.

        Returns:
            Audio reference string or empty string if none available
        """
        if not self._media_manager:
            return ""

        # Check for existing example audio
        if noun.example_audio and Path(noun.example_audio).exists():
            example_audio_file = self._media_manager.add_media_file(noun.example_audio)
            if example_audio_file:
                return example_audio_file.reference

        # Generate example sentence audio
        example_audio_file = self._media_manager.generate_and_add_audio(noun.example)
        if example_audio_file:
            return example_audio_file.reference

        return ""

    def _get_or_generate_image(self, noun: Noun) -> str:
        """Get existing or generate image for noun.

        Returns:
            Image HTML string or empty string if none available
        """
        if not self._media_manager:
            return ""

        # Check for existing image from CSV path
        if noun.image_path and Path(noun.image_path).exists():
            image_file = self._media_manager.add_media_file(noun.image_path)
            if image_file:
                return f'<img src="{image_file.reference}">'

        # Check for existing image by expected filename pattern
        safe_filename = (
            "".join(c for c in noun.noun if c.isalnum() or c in (" ", "-", "_"))
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
        enhanced_search_query = noun.get_image_search_terms()
        image_file = self._media_manager.generate_and_add_image(
            noun.noun,
            search_query=enhanced_search_query,
            example_sentence=noun.example,
        )
        if image_file:
            return f'<img src="{image_file.reference}">'

        return ""
