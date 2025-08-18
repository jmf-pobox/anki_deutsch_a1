"""Media file management and coordination functionality.

The MediaManager handles media file lifecycle, deduplication, caching strategies,
and provides statistics tracking. It coordinates between media generation services
and deck backends while maintaining separation of concerns.
"""

import hashlib
import logging
from pathlib import Path
from typing import Any, NamedTuple

from langlearn.backends.base import DeckBackend, MediaFile
from langlearn.services.media_service import MediaService

logger = logging.getLogger(__name__)


class MediaStats(NamedTuple):
    """Media management statistics."""

    files_added: int
    duplicates_skipped: int
    total_size_bytes: int
    unique_files: int


class MediaManager:
    """Manages media file lifecycle and deduplication across deck generation.

    The MediaManager provides a coordinated interface for handling media files
    including deduplication, caching, and statistics tracking. It composes
    with MediaService for generation and DeckBackend for storage.
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

        # Track added files to prevent duplicates
        self._added_files: set[str] = set()  # Set of file hashes
        self._file_paths: dict[str, str] = {}  # hash -> original file path

        # Statistics
        self._stats = {
            "files_added": 0,
            "duplicates_skipped": 0,
            "total_size_bytes": 0,
        }

    def add_media_file(
        self, file_path: str, allow_duplicates: bool = False
    ) -> MediaFile | None:
        """Add a media file to the deck with deduplication.

        Args:
            file_path: Path to the media file
            allow_duplicates: If True, skip deduplication check

        Returns:
            MediaFile object if added, None if skipped as duplicate
        """
        if not Path(file_path).exists():
            logger.warning(f"Media file does not exist: {file_path}")
            return None

        # Calculate file hash for deduplication
        file_hash = self._calculate_file_hash(file_path)

        # Check for duplicates unless explicitly allowed
        if not allow_duplicates and file_hash in self._added_files:
            logger.debug(f"Skipping duplicate media file: {file_path}")
            self._stats["duplicates_skipped"] += 1
            return None

        try:
            # Add to backend
            media_file = self._backend.add_media_file(file_path)

            # Track the file
            self._added_files.add(file_hash)
            self._file_paths[file_hash] = file_path

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
                return self.add_media_file(audio_path)
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
                return self.add_media_file(image_path)
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
            duplicates_skipped=self._stats["duplicates_skipped"],
            total_size_bytes=self._stats["total_size_bytes"],
            unique_files=len(self._added_files),
        )

    def get_added_files(self) -> list[str]:
        """Get list of all added file paths.

        Returns:
            List of file paths that have been added to the deck
        """
        return list(self._file_paths.values())

    def is_file_added(self, file_path: str) -> bool:
        """Check if a file has already been added.

        Args:
            file_path: Path to check

        Returns:
            True if file has been added, False otherwise
        """
        file_hash = self._calculate_file_hash(file_path)
        return file_hash in self._added_files

    def clear_cache(self) -> None:
        """Clear the internal deduplication cache.

        This allows previously added files to be added again.
        Use with caution as it may result in duplicate files.
        """
        self._added_files.clear()
        self._file_paths.clear()
        logger.info("Media manager cache cleared")

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

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of a file for deduplication.

        Args:
            file_path: Path to the file

        Returns:
            Hexadecimal hash string
        """
        try:
            hasher = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.warning(f"Could not hash file {file_path}: {e}")
            # Fallback to path-based hash for basic deduplication
            return hashlib.sha256(file_path.encode()).hexdigest()
