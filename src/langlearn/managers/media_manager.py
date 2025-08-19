"""Media file management and coordination functionality.

The MediaManager handles media file lifecycle, caching strategies,
and provides statistics tracking. It coordinates between media generation services
and deck backends while maintaining separation of concerns.
"""

import logging
from pathlib import Path
from typing import Any, NamedTuple

from langlearn.backends.base import DeckBackend, MediaFile
from langlearn.services.media_service import MediaService

logger = logging.getLogger(__name__)


class MediaStats(NamedTuple):
    """Media management statistics."""

    files_added: int
    total_size_bytes: int


class MediaManager:
    """Manages media file lifecycle across deck generation.

    The MediaManager provides a coordinated interface for handling media files
    including statistics tracking. It composes with MediaService for generation
    and DeckBackend for storage.
    """

    def __init__(
        self, backend: DeckBackend, media_service: MediaService | None = None
    ) -> None:
        """Initialize MediaManager.

        Args:
            backend: DeckBackend for adding media files to the deck
            media_service: Optional MediaService for media generation
        """
        self._backend = backend
        self._media_service = media_service

        # Statistics
        self._stats = {
            "files_added": 0,
            "total_size_bytes": 0,
        }

    def add_media_file(self, file_path: str, media_type: str = "") -> MediaFile | None:
        """Add a media file to the deck.

        Args:
            file_path: Path to the media file
            media_type: Expected media type ('audio', 'image', or '' for auto-detect)

        Returns:
            MediaFile object if added successfully, None if failed
        """
        logger.info(
            f"📁 MediaManager.add_media_file: '{file_path}' (type='{media_type}')"
        )

        if not Path(file_path).exists():
            logger.warning(f"❌ Media file does not exist: {file_path}")
            return None

        try:
            # Add to backend with media type context
            logger.info(
                f"   🔧 Calling backend.add_media_file('{file_path}', "
                f"media_type='{media_type}')"
            )
            media_file = self._backend.add_media_file(file_path, media_type=media_type)
            logger.info(
                f"   ✅ Backend returned MediaFile: path='{media_file.path}', "
                f"reference='{media_file.reference}', "
                f"media_type='{media_file.media_type}'"
            )

            # Update statistics
            self._stats["files_added"] += 1
            try:
                file_size = Path(file_path).stat().st_size
                self._stats["total_size_bytes"] += file_size
            except OSError:
                logger.warning(f"Could not get size for file: {file_path}")

            logger.debug(f"Added media file: {file_path}")
            return media_file

        except Exception as e:
            logger.error(f"Failed to add media file {file_path}: {e}")
            return None

    def generate_and_add_audio(self, text: str) -> MediaFile | None:
        """Generate audio and add it to the deck.

        Args:
            text: Text to generate audio for

        Returns:
            MediaFile object if successful, None otherwise
        """
        if not self._media_service:
            logger.warning("No MediaService available for audio generation")
            return None

        try:
            audio_path = self._media_service.generate_audio(text)
            if audio_path:
                return self.add_media_file(audio_path, media_type="audio")
            return None
        except Exception as e:
            logger.error(f"Failed to generate audio for '{text}': {e}")
            return None

    def generate_and_add_image(
        self,
        word: str,
        search_query: str | None = None,
        example_sentence: str | None = None,
    ) -> MediaFile | None:
        """Generate image and add it to the deck.

        Args:
            word: German word for image generation
            search_query: Optional specific search query
            example_sentence: Optional sentence context

        Returns:
            MediaFile object if successful, None otherwise
        """
        if not self._media_service:
            logger.warning("No MediaService available for image generation")
            return None

        try:
            image_path = self._media_service.generate_image(
                word, search_query, example_sentence
            )
            if image_path:
                return self.add_media_file(image_path, media_type="image")
            return None
        except Exception as e:
            logger.error(f"Failed to generate image for '{word}': {e}")
            return None

    def get_media_stats(self) -> MediaStats:
        """Get media management statistics.

        Returns:
            MediaStats with current counts and metrics
        """
        return MediaStats(
            files_added=self._stats["files_added"],
            total_size_bytes=self._stats["total_size_bytes"],
        )

    def get_detailed_stats(self) -> dict[str, Any]:
        """Get detailed media statistics including service stats.

        Returns:
            Dictionary with comprehensive media statistics
        """
        stats = {
            "media_stats": self.get_media_stats()._asdict(),
        }

        # Include MediaService statistics if available
        if self._media_service:
            service_stats = self._media_service.get_stats()
            stats["media_generation_stats"] = service_stats._asdict()

            # Add computed totals
            stats["media_generation_stats"]["total_media_generated"] = (
                service_stats.audio_generated + service_stats.images_downloaded
            )
            stats["media_generation_stats"]["total_media_reused"] = (
                service_stats.audio_reused + service_stats.images_reused
            )

        return stats
