"""Media coordination service for audio and image generation."""

import hashlib
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

from .audio import AudioService
from .pexels_service import PexelsService, PhotoSize

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class MediaGenerationConfig:
    """Configuration for media generation behavior."""

    audio_sample_rate: int = 16000
    image_size: PhotoSize = "medium"
    audio_dir: str = "data/audio"
    images_dir: str = "data/images"


class MediaAssets(NamedTuple):
    """Generated media assets for a word."""

    audio_path: str | None
    image_path: str | None


class MediaGenerationStats(NamedTuple):
    """Statistics for media generation operations."""

    audio_generated: int
    audio_reused: int
    images_downloaded: int
    images_reused: int
    generation_errors: int


class MediaService:
    """Coordinates audio and image generation with deduplication and caching.

    This service orchestrates the existing AudioService and PexelsService,
    providing a clean interface for media generation with proper caching,
    deduplication, and error handling.
    """

    def __init__(
        self,
        audio_service: AudioService,
        pexels_service: PexelsService,
        config: MediaGenerationConfig,
        project_root: Path,
    ) -> None:
        """Initialize MediaService with dependency injection.

        Args:
            audio_service: Injected audio generation service
            pexels_service: Injected image search/download service
            config: Media generation configuration
            project_root: Project root path for resolving media directories
        """
        self._audio_service = audio_service
        self._pexels_service = pexels_service
        self._config = config
        self._project_root = project_root

        # Setup media directories
        self._audio_dir = project_root / config.audio_dir
        self._images_dir = project_root / config.images_dir
        self._audio_dir.mkdir(parents=True, exist_ok=True)
        self._images_dir.mkdir(parents=True, exist_ok=True)

        # Statistics tracking
        self._stats = {
            "audio_generated": 0,
            "audio_reused": 0,
            "images_downloaded": 0,
            "images_reused": 0,
            "generation_errors": 0,
        }

    def generate_audio(self, text: str) -> str | None:
        """Generate audio for text with MD5-based deduplication.

        Uses the same MD5 hash naming convention as the original AudioService
        for consistent file naming and deduplication.

        Args:
            text: Text to generate audio for

        Returns:
            Path to audio file or None if generation failed
        """
        try:
            # Generate MD5 hash for consistent filename
            # (matches AudioService._save_audio_file)
            filename = f"{hashlib.md5(text.encode()).hexdigest()}.mp3"
            audio_path = self._audio_dir / filename

            # Check if audio already exists (deduplication)
            if audio_path.exists():
                self._stats["audio_reused"] += 1
                logger.debug(f"Reusing existing audio: {audio_path}")
                return str(audio_path)

            # Generate new audio using injected service
            generated_path = self._audio_service.generate_audio(text)
            if generated_path:
                self._stats["audio_generated"] += 1
                logger.info(f"Generated new audio: {generated_path}")
                return generated_path
            else:
                self._stats["generation_errors"] += 1
                logger.error(f"Failed to generate audio for: {text}")
                return None

        except Exception as e:
            logger.error(f"Error generating audio for '{text}': {e}")
            self._stats["generation_errors"] += 1
            return None

    def generate_or_get_audio(self, text: str) -> str | None:
        """Generate audio for text or return existing audio file path.

        Alias for generate_audio to maintain backward compatibility.

        Args:
            text: Text to generate audio for

        Returns:
            Path to audio file or None if generation failed
        """
        return self.generate_audio(text)

    def generate_image(
        self,
        word: str,
        search_query: str | None = None,
        example_sentence: str | None = None,
    ) -> str | None:
        """Generate/download image with intelligent search query enhancement.

        Args:
            word: German word for image generation
            search_query: Optional specific search query
            example_sentence: Optional sentence context for query enhancement

        Returns:
            Path to image file or None if generation failed
        """
        try:
            # Generate descriptive filename using German word
            # Always use German word for filename to match CSV expectations
            safe_filename = "".join(
                c for c in word if c.isalnum() or c in (" ", "-", "_")
            ).rstrip()
            safe_filename = safe_filename.replace(" ", "_").lower()
            image_path = self._images_dir / f"{safe_filename}.jpg"

            # Check if image already exists (deduplication)
            if image_path.exists():
                self._stats["images_reused"] += 1
                logger.debug(f"Reusing existing image: {image_path}")
                return str(image_path)

            # Determine search query (will be enhanced by caller with German
            # context if needed)
            query = search_query or word

            # Download image using injected service
            if self._pexels_service.download_image(
                query, str(image_path), self._config.image_size
            ):
                self._stats["images_downloaded"] += 1
                logger.info(f"Downloaded new image: {image_path}")
                return str(image_path)
            else:
                self._stats["generation_errors"] += 1
                logger.error(f"Failed to download image for query: {query}")
                return None

        except Exception as e:
            logger.error(f"Error generating image for '{word}': {e}")
            self._stats["generation_errors"] += 1
            return None

    def generate_or_get_image(
        self, word: str, search_query: str | None = None, example_sentence: str = ""
    ) -> str | None:
        """Generate/download image for word or return existing image file path.

        Alias for generate_image to maintain backward compatibility.

        Args:
            word: German word to get image for
            search_query: Optional search query
            example_sentence: Example sentence for context

        Returns:
            Path to image file or None if generation failed
        """
        return self.generate_image(word, search_query, example_sentence)

    def generate_media_for_word(
        self,
        word: str,
        audio_text: str | None = None,
        search_query: str | None = None,
        example_sentence: str | None = None,
    ) -> MediaAssets:
        """Generate both audio and image for a word.

        Args:
            word: German word
            audio_text: Text for audio generation (defaults to word)
            search_query: Search query for image (defaults to word)
            example_sentence: Example sentence for context enhancement

        Returns:
            MediaAssets with paths to generated files
        """
        # Generate audio
        audio_path = self.generate_audio(audio_text or word)

        # Generate image
        image_path = self.generate_image(word, search_query, example_sentence)

        return MediaAssets(audio_path=audio_path, image_path=image_path)

    def get_stats(self) -> MediaGenerationStats:
        """Get current media generation statistics.

        Returns:
            MediaGenerationStats with current counts
        """
        return MediaGenerationStats(
            audio_generated=self._stats["audio_generated"],
            audio_reused=self._stats["audio_reused"],
            images_downloaded=self._stats["images_downloaded"],
            images_reused=self._stats["images_reused"],
            generation_errors=self._stats["generation_errors"],
        )

    def reset_stats(self) -> None:
        """Reset statistics counters."""
        for key in self._stats:
            self._stats[key] = 0
