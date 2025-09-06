"""Media enrichment service using domain models exclusively.

This service provides audio and image generation for German language learning
cards by leveraging domain model expertise through the MediaGenerationCapable protocol.
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from langlearn.protocols.media_generation_protocol import MediaGenerationCapable
from langlearn.services.anthropic_service import AnthropicService
from langlearn.services.pexels_service import PexelsService

if TYPE_CHECKING:
    from langlearn.services.audio_service import AudioService
else:
    # Runtime import to avoid circular dependency
    try:
        from langlearn.services.audio_service import AudioService
    except ImportError:
        AudioService = None  # type: ignore[misc,assignment]

logger = logging.getLogger(__name__)


class MediaEnricher:
    """Abstract base class for media enrichment."""

    def enrich_with_media(
        self, domain_model: MediaGenerationCapable
    ) -> dict[str, Any]:
        """Enrich domain model with media using its domain expertise.

        Args:
            domain_model: Domain model implementing MediaGenerationCapable protocol

        Returns:
            Dictionary with media fields (image, audio references)
        """
        raise NotImplementedError


class StandardMediaEnricher(MediaEnricher):
    """Standard implementation of media enrichment using domain models."""

    def __init__(
        self,
        audio_service: "AudioService",
        pexels_service: PexelsService,
        anthropic_service: AnthropicService,
        audio_base_path: Path,
        image_base_path: Path,
    ) -> None:
        """Initialize media enricher with required services.

        Args:
            audio_service: Service for generating audio files
            pexels_service: Service for downloading images
            anthropic_service: Service for AI-powered content generation
            audio_base_path: Base directory for audio files
            image_base_path: Base directory for image files
        """
        self._audio_service = audio_service
        self._pexels_service = pexels_service
        self._anthropic_service = anthropic_service
        self._audio_base_path = audio_base_path
        self._image_base_path = image_base_path

        # Ensure directories exist
        self._audio_base_path.mkdir(parents=True, exist_ok=True)
        self._image_base_path.mkdir(parents=True, exist_ok=True)

    def enrich_with_media(
        self, domain_model: MediaGenerationCapable
    ) -> dict[str, Any]:
        """Enrich domain model with media using its domain expertise.

        Args:
            domain_model: Domain model implementing MediaGenerationCapable protocol

        Returns:
            Dictionary with media fields (image, word_audio, example_audio, etc.)
        """
        model_name = type(domain_model).__name__
        logger.debug(f"Enriching {model_name} with media using domain expertise")

        media_data: dict[str, Any] = {}

        # Generate audio using domain model's audio strategy
        try:
            audio_text = domain_model.get_combined_audio_text()
            if audio_text:
                audio_hash = self._generate_content_hash(audio_text)
                audio_filename = f"{audio_hash}.mp3"
                audio_path = self._audio_base_path / audio_filename

                if not audio_path.exists():
                    logger.debug(f"Generating audio: {audio_text[:50]}...")
                    self._audio_service.generate_audio(audio_text, audio_path)
                    logger.info(f"Generated audio: {audio_path}")
                else:
                    logger.debug(f"Audio exists: {audio_path}")

                media_data["word_audio"] = audio_filename
        except Exception as e:
            logger.warning(f"Audio generation failed for {model_name}: {e}")

        # Generate image using domain model's image strategy  
        try:
            # First check if image already exists before calling expensive Anthropic API
            model_word = self._extract_primary_word(domain_model)
            image_filename = f"{model_word.lower()}.jpg"
            image_path = self._image_base_path / image_filename

            if image_path.exists():
                logger.debug(f"Image exists: {image_path}")
                media_data["image"] = image_filename
            else:
                # Image doesn't exist - now use domain model's image strategy
                image_strategy = domain_model.get_image_search_strategy(
                    self._anthropic_service
                )
                if image_strategy is not None:
                    search_query = image_strategy()
                    if search_query:
                        logger.debug(f"Generating image for query: {search_query}")
                        success = self._pexels_service.download_image(
                            search_query, str(image_path)
                        )
                        if success:
                            logger.info(f"Generated image: {image_path}")
                            media_data["image"] = image_filename
                        else:
                            logger.warning(f"Image generation failed: {search_query}")
                    else:
                        logger.debug(f"No search query generated for {model_name}")
                else:
                    logger.debug(f"No image strategy available for {model_name}")
        except Exception as e:
            logger.warning(f"Image generation failed for {model_name}: {e}")

        return media_data

    def enrich_records(
        self, records: list[dict[str, Any]], domain_models: list[MediaGenerationCapable]
    ) -> list[dict[str, Any]]:
        """Batch enrich records with domain models.

        Args:
            records: List of record dictionaries
            domain_models: List of corresponding domain models

        Returns:
            List of enriched record dictionaries
        """
        if len(records) != len(domain_models):
            raise ValueError(
                f"Records and domain models count mismatch: "
                f"{len(records)} records vs {len(domain_models)} models"
            )

        enriched_records = []
        for record, domain_model in zip(records, domain_models, strict=False):
            try:
                # Get media data from domain model
                media_data = self.enrich_with_media(domain_model)

                # Merge media data into record
                enriched_record = record.copy()
                enriched_record.update(media_data)
                enriched_records.append(enriched_record)

            except Exception as e:
                model_name = type(domain_model).__name__
                logger.error(f"Failed to enrich record with {model_name}: {e}")
                enriched_records.append(record.copy())

        return enriched_records

    def _generate_content_hash(self, content: str) -> str:
        """Generate hash for content to create deterministic filenames."""
        return hashlib.md5(content.encode("utf-8")).hexdigest()

    def _extract_primary_word(self, domain_model: MediaGenerationCapable) -> str:
        """Extract the primary word from domain model for filename generation."""
        # Use domain model's primary identifier for filename
        if hasattr(domain_model, "noun"):
            return cast(str, domain_model.noun)
        elif hasattr(domain_model, "word"):
            return cast(str, domain_model.word)
        elif hasattr(domain_model, "phrase"):
            # Use first word of phrase for filename
            phrase = cast(str, domain_model.phrase)
            return phrase.split()[0] if phrase else "phrase"
        elif hasattr(domain_model, "verb"):
            return cast(str, domain_model.verb)
        elif hasattr(domain_model, "preposition"):
            return cast(str, domain_model.preposition)
        else:
            # Fallback to class name
            return type(domain_model).__name__.lower()