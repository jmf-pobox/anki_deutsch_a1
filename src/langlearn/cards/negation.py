"""Card generator for negations."""

import logging
from pathlib import Path

from langlearn.backends.base import DeckBackend
from langlearn.cards.base import BaseCardGenerator
from langlearn.managers.media_manager import MediaManager
from langlearn.models.negation import Negation
from langlearn.services.template_service import TemplateService

logger = logging.getLogger(__name__)


class NegationCardGenerator(BaseCardGenerator[Negation]):
    """Generator for negation cards in Anki with type safety."""

    def __init__(
        self,
        backend: DeckBackend,
        template_service: TemplateService,
        media_manager: MediaManager | None = None,
    ) -> None:
        """Initialize the negation card generator.

        Args:
            backend: Backend implementation for deck operations
            template_service: Service for loading card templates
            media_manager: Optional media manager for audio/image generation
        """
        super().__init__(backend, template_service, "negation", media_manager)

    def _get_field_names(self) -> list[str]:
        """Get the list of field names for negation cards.

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

    def _extract_fields(self, data: Negation) -> list[str]:
        """Extract field values from a Negation model.

        Args:
            data: The Negation model to extract fields from

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
        self, negation: Negation, fields: list[str]
    ) -> list[str]:
        """Enhance negation fields with generated media (audio/images).

        Args:
            negation: The Negation model being processed
            fields: The base field values

        Returns:
            Enhanced field values with media references
        """
        logger.info(f"🎯 MEDIA ENHANCEMENT START: negation='{negation.word}'")
        logger.info(f"   Field names: {self._get_field_names()}")
        logger.info(
            f"   Base fields: {[f[:50] + '...' if len(f) > 50 else f for f in fields]}"
        )

        if not self._media_manager:
            logger.warning(f"   No MediaManager available for {negation.word}")
            return fields

        enhanced_fields = fields.copy()

        # Handle word audio (index 5: WordAudio)
        logger.info(f"   🔊 Generating word audio for '{negation.word}'...")
        audio_ref = self._get_or_generate_word_audio(negation)
        if audio_ref:
            logger.info(f"   ✅ WordAudio generated: '{audio_ref}'")
            logger.info(f"   📝 Setting field[5] (WordAudio) = '{audio_ref}'")
            enhanced_fields[5] = audio_ref
        else:
            logger.warning(f"   ❌ No word audio generated for '{negation.word}'")

        # Handle example audio (index 6: ExampleAudio)
        logger.info(f"   🔊 Generating example audio for '{negation.example}'...")
        example_audio_ref = self._get_or_generate_example_audio(negation)
        if example_audio_ref:
            logger.info(f"   ✅ ExampleAudio generated: '{example_audio_ref}'")
            logger.info(
                f"   📝 Setting field[6] (ExampleAudio) = '{example_audio_ref}'"
            )
            enhanced_fields[6] = example_audio_ref
        else:
            logger.warning(f"   ❌ No example audio generated for '{negation.example}'")

        # Handle image (index 4: Image) - Process LAST to avoid field contamination
        logger.info(f"   🖼️ Generating image for '{negation.word}'...")
        image_html = self._get_or_generate_image(negation)
        if image_html:
            logger.info(f"   ✅ Image generated: '{image_html[:100]}...'")
            logger.info(f"   📝 Setting field[4] (Image) = '{image_html[:50]}...'")
            enhanced_fields[4] = image_html
        else:
            logger.warning(f"   ❌ No image generated for '{negation.word}'")

        logger.info(f"🎯 MEDIA ENHANCEMENT COMPLETE: negation='{negation.word}'")
        logger.info(
            f"   Final fields: "
            f"{[f[:50] + '...' if len(f) > 50 else f for f in enhanced_fields]}"
        )

        return enhanced_fields

    def _get_or_generate_word_audio(self, negation: Negation) -> str:
        """Get existing or generate word audio for negation.

        Returns:
            Audio reference string or empty string if none available
        """
        if not self._media_manager:
            return ""

        # Check for existing word audio
        if negation.word_audio and Path(negation.word_audio).exists():
            audio_file = self._media_manager.add_media_file(
                negation.word_audio, media_type="audio"
            )
            if audio_file:
                return audio_file.reference

        # Generate audio for negation word only (no special forms like nouns/adjectives)
        # Add debug logging for problematic words
        audio_text = negation.word
        if negation.word in ["nie", "niemals"]:
            logger.debug(
                f"Generating word audio for '{negation.word}' with text: '{audio_text}'"
            )

        audio_file = self._media_manager.generate_and_add_audio(audio_text)
        if audio_file:
            ref = audio_file.reference
            if negation.word in ["nie", "niemals"]:
                logger.debug(f"Generated word audio reference: {ref}")
            return ref

        return ""

    def _get_or_generate_example_audio(self, negation: Negation) -> str:
        """Get existing or generate example audio for negation.

        Returns:
            Audio reference string or empty string if none available
        """
        if not self._media_manager:
            return ""

        # Check for existing example audio
        if negation.example_audio and Path(negation.example_audio).exists():
            example_audio_file = self._media_manager.add_media_file(
                negation.example_audio, media_type="audio"
            )
            if example_audio_file:
                return example_audio_file.reference

        # Generate example sentence audio
        # Add debug logging for problematic words
        example_text = negation.example
        if negation.word in ["nie", "niemals"]:
            logger.debug(
                f"Generating example audio for '{negation.word}' with text: "
                f"'{example_text}'"
            )

        example_audio_file = self._media_manager.generate_and_add_audio(example_text)
        if example_audio_file:
            ref = example_audio_file.reference
            if negation.word in ["nie", "niemals"]:
                logger.debug(f"Generated example audio reference: {ref}")
            return ref

        return ""

    def _get_or_generate_image(self, negation: Negation) -> str:
        """Get existing or generate image for negation.

        Returns:
            Image HTML string or empty string if none available
        """
        if not self._media_manager:
            return ""

        # Check for existing image from CSV path
        if negation.image_path and Path(negation.image_path).exists():
            image_file = self._media_manager.add_media_file(
                negation.image_path, media_type="image"
            )
            if image_file:
                return f'<img src="{image_file.reference}">'

        # Check for existing image by expected filename pattern
        safe_filename = (
            "".join(c for c in negation.word if c.isalnum() or c in (" ", "-", "_"))
            .rstrip()
            .replace(" ", "_")
            .lower()
        )
        expected_image_path = Path("data/images") / f"{safe_filename}.jpg"
        if expected_image_path.exists():
            # Validate the file is actually an image before adding
            if expected_image_path.suffix.lower() in [".jpg", ".jpeg", ".png", ".gif"]:
                image_file = self._media_manager.add_media_file(
                    str(expected_image_path), media_type="image"
                )
                if image_file:
                    # Ensure the reference is valid and doesn't contain audio markers
                    ref = image_file.reference
                    if not ref.startswith("[sound:") and not ref.endswith(".mp3]"):
                        return f'<img src="{ref}">'
                    else:
                        logger.warning(
                            f"MediaManager returned audio reference for image: {ref}"
                        )
            else:
                logger.warning(
                    f"Expected image file is not an image: {expected_image_path}"
                )

        # Generate image using domain model's enhanced search terms
        enhanced_search_query = negation.get_image_search_terms()
        image_file = self._media_manager.generate_and_add_image(
            negation.word,
            search_query=enhanced_search_query,
            example_sentence=negation.example,
        )
        if image_file:
            return f'<img src="{image_file.reference}">'

        return ""
