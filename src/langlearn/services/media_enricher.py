"""
Media enrichment service for the Clean Pipeline Architecture.

This service centralizes all media existence checks and generation logic,
removing infrastructure concerns from domain models.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class MediaEnricher(ABC):
    """Abstract base class for media enrichment services.

    This service handles all media-related operations including:
    - Checking for existing media files
    - Generating missing media (audio, images)
    - Managing media file paths and references
    """

    @abstractmethod
    def enrich_record(
        self, record: dict[str, Any], domain_model: Any
    ) -> dict[str, Any]:
        """Enrich a record with media files based on domain model business rules.

        Args:
            record: Base record data from CSV
            domain_model: Domain model instance for business logic

        Returns:
            Enriched record with media references added
        """
        pass

    @abstractmethod
    def audio_exists(self, text: str) -> bool:
        """Check if audio file exists for given text.

        Args:
            text: Text to check audio for

        Returns:
            True if audio file exists
        """
        pass

    @abstractmethod
    def image_exists(self, word: str) -> bool:
        """Check if image file exists for given word.

        Args:
            word: Word to check image for

        Returns:
            True if image file exists
        """
        pass

    @abstractmethod
    def generate_audio(self, text: str) -> str | None:
        """Generate audio file for text if not exists.

        Args:
            text: Text to generate audio for

        Returns:
            Path to audio file or None if generation failed
        """
        pass

    @abstractmethod
    def generate_image(self, search_terms: str, fallback: str) -> str | None:
        """Generate image file for search terms if not exists.

        Args:
            search_terms: Primary search terms for image
            fallback: Fallback search terms

        Returns:
            Path to image file or None if generation failed
        """
        pass


class StandardMediaEnricher(MediaEnricher):
    """Standard implementation of MediaEnricher using existing services."""

    def __init__(
        self,
        media_service: Any,  # MediaService - avoiding import for now
        audio_base_path: Path = Path("data/audio"),
        image_base_path: Path = Path("data/images"),
    ) -> None:
        """Initialize media enricher with existing services.

        Args:
            media_service: Existing MediaService instance
            audio_base_path: Base directory for audio files
            image_base_path: Base directory for image files
        """
        self._media_service = media_service
        self._audio_base_path = audio_base_path
        self._image_base_path = image_base_path

        # Ensure directories exist
        self._audio_base_path.mkdir(parents=True, exist_ok=True)
        self._image_base_path.mkdir(parents=True, exist_ok=True)

    def enrich_record(
        self, record: dict[str, Any], domain_model: Any
    ) -> dict[str, Any]:
        """Enrich record with media based on domain model type and business rules."""
        enriched = record.copy()

        # Determine model type for type-specific enrichment
        model_type = type(domain_model).__name__.lower()

        if model_type == "noun":
            return self._enrich_noun_record(enriched, domain_model)
        elif model_type == "adjective":
            return self._enrich_adjective_record(enriched, domain_model)
        elif model_type == "adverb":
            return self._enrich_adverb_record(enriched, domain_model)
        elif model_type == "negation":
            return self._enrich_negation_record(enriched, domain_model)
        else:
            logger.warning(f"Unknown model type: {model_type}")
            return enriched

    def _enrich_noun_record(self, record: dict[str, Any], noun: Any) -> dict[str, Any]:
        """Enrich noun record with media."""
        # Generate word audio (combined article + noun + plural)
        if not record.get("word_audio"):
            combined_text = noun.get_combined_audio_text()
            audio_path = self._get_or_generate_audio(combined_text)
            if audio_path:
                record["word_audio"] = f"[sound:{Path(audio_path).name}]"

        # Generate example audio
        if not record.get("example_audio") and record.get("example"):
            audio_path = self._get_or_generate_audio(record["example"])
            if audio_path:
                record["example_audio"] = f"[sound:{Path(audio_path).name}]"

        # Generate image (only for concrete nouns)
        if not record.get("image") and noun.is_concrete():
            search_terms = noun.get_image_search_terms()
            image_path = self._get_or_generate_image(
                record["noun"], search_terms, record["english"]
            )
            if image_path:
                record["image"] = f'<img src="{Path(image_path).name}">'

        return record

    def _enrich_adjective_record(
        self, record: dict[str, Any], adjective: Any
    ) -> dict[str, Any]:
        """Enrich adjective record with media."""
        # Generate word audio (combined forms)
        if not record.get("word_audio"):
            combined_text = adjective.get_combined_audio_text()
            audio_path = self._get_or_generate_audio(combined_text)
            if audio_path:
                record["word_audio"] = f"[sound:{Path(audio_path).name}]"

        # Generate example audio
        if not record.get("example_audio") and record.get("example"):
            audio_path = self._get_or_generate_audio(record["example"])
            if audio_path:
                record["example_audio"] = f"[sound:{Path(audio_path).name}]"

        # Generate image
        if not record.get("image"):
            search_terms = adjective.get_image_search_terms()
            image_path = self._get_or_generate_image(
                record["word"], search_terms, record["english"]
            )
            if image_path:
                record["image"] = f'<img src="{Path(image_path).name}">'

        return record

    def _enrich_adverb_record(
        self, record: dict[str, Any], adverb: Any
    ) -> dict[str, Any]:
        """Enrich adverb record with media."""
        # Generate word audio
        if not record.get("word_audio") and record.get("word"):
            audio_path = self._get_or_generate_audio(record["word"])
            if audio_path:
                record["word_audio"] = f"[sound:{Path(audio_path).name}]"

        # Generate example audio
        if not record.get("example_audio") and record.get("example"):
            audio_path = self._get_or_generate_audio(record["example"])
            if audio_path:
                record["example_audio"] = f"[sound:{Path(audio_path).name}]"

        # Generate image
        if not record.get("image"):
            search_terms = adverb.get_image_search_terms()
            image_path = self._get_or_generate_image(
                record["word"], search_terms, record["english"]
            )
            if image_path:
                record["image"] = f'<img src="{Path(image_path).name}">'

        return record

    def _enrich_negation_record(
        self, record: dict[str, Any], negation: Any
    ) -> dict[str, Any]:
        """Enrich negation record with media."""
        # Generate word audio
        if not record.get("word_audio") and record.get("word"):
            audio_path = self._get_or_generate_audio(record["word"])
            if audio_path:
                record["word_audio"] = f"[sound:{Path(audio_path).name}]"

        # Generate example audio
        if not record.get("example_audio") and record.get("example"):
            audio_path = self._get_or_generate_audio(record["example"])
            if audio_path:
                record["example_audio"] = f"[sound:{Path(audio_path).name}]"

        # Generate image
        if not record.get("image"):
            search_terms = negation.get_image_search_terms()
            image_path = self._get_or_generate_image(
                record["word"], search_terms, record["english"]
            )
            if image_path:
                record["image"] = f'<img src="{Path(image_path).name}">'

        return record

    def _get_or_generate_audio(self, text: str) -> str | None:
        """Get existing audio or generate if not exists."""
        if not text or not text.strip():
            return None

        # Check if audio already exists
        if self.audio_exists(text):
            # Return existing audio path
            audio_filename = self._get_audio_filename(text)
            return str(self._audio_base_path / audio_filename)

        # Generate new audio
        return self.generate_audio(text)

    def _get_or_generate_image(
        self, word: str, search_terms: str, fallback: str
    ) -> str | None:
        """Get existing image or generate if not exists."""
        if not word:
            return None

        # Check if image already exists
        if self.image_exists(word):
            # Return existing image path
            image_filename = self._get_image_filename(word)
            return str(self._image_base_path / image_filename)

        # Generate new image
        return self.generate_image(search_terms, fallback)

    def audio_exists(self, text: str) -> bool:
        """Check if audio file exists for given text."""
        if not text:
            return False

        audio_filename = self._get_audio_filename(text)
        return (self._audio_base_path / audio_filename).exists()

    def image_exists(self, word: str) -> bool:
        """Check if image file exists for given word."""
        if not word:
            return False

        image_filename = self._get_image_filename(word)
        return (self._image_base_path / image_filename).exists()

    def generate_audio(self, text: str) -> str | None:
        """Generate audio file for text."""
        try:
            return self._media_service.generate_audio(text)  # type: ignore[no-any-return]
        except Exception as e:
            logger.warning(f"Audio generation failed for '{text[:50]}...': {e}")
            return None

    def generate_image(self, search_terms: str, fallback: str) -> str | None:
        """Generate image file for search terms."""
        try:
            return self._media_service.generate_image(search_terms, fallback)  # type: ignore[no-any-return]
        except Exception as e:
            logger.warning(f"Image generation failed for '{search_terms}': {e}")
            return None

    def _get_audio_filename(self, text: str) -> str:
        """Get standardized audio filename for text."""
        # This should match the existing MediaService logic
        # For now, using a simple hash-based approach
        import hashlib

        text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        return f"audio_{text_hash}.mp3"

    def _get_image_filename(self, word: str) -> str:
        """Get standardized image filename for word."""
        # Clean word for filename (match existing logic)
        safe_word = (
            "".join(c for c in word.lower() if c.isalnum() or c in (" ", "-", "_"))
            .rstrip()
            .replace(" ", "_")
        )
        return f"{safe_word}.jpg"
