"""Media file registrar service for Clean Pipeline Architecture.

This service handles media file registration with the backend for APKG export.
It maintains clean separation between card formatting and infrastructure concerns.
"""

import logging
import re
from pathlib import Path
from typing import Any

from langlearn.backends.base import DeckBackend

logger = logging.getLogger(__name__)


class MediaFileRegistrar:
    """Registers media files with the backend for APKG export.

    This service extracts media references from generated cards and
    registers the corresponding files with the backend. It maintains
    clean separation between card formatting and infrastructure concerns.

    Part of Clean Pipeline Architecture:
    CardBuilder → MediaFileRegistrar → Backend
    """

    def __init__(
        self,
        audio_base_path: Path = Path("data/audio"),
        image_base_path: Path = Path("data/images"),
    ) -> None:
        """Initialize MediaFileRegistrar.

        Args:
            audio_base_path: Base directory for audio files
            image_base_path: Base directory for image files
        """
        self._audio_base_path = audio_base_path
        self._image_base_path = image_base_path
        self._registered_files: set[str] = set()  # Track to avoid duplicates

        logger.debug(
            f"MediaFileRegistrar initialized with audio_path={audio_base_path}, "
            f"image_path={image_base_path}"
        )

    def register_card_media(self, field_values: list[str], backend: DeckBackend) -> int:
        """Extract and register all media files referenced in card fields.

        Args:
            field_values: List of card field values to scan for media references
            backend: Backend to register media files with

        Returns:
            Number of media files successfully registered
        """
        registered_count = 0

        for field_value in field_values:
            if not field_value:
                continue

            # Extract audio references: [sound:filename.mp3]
            audio_refs = self._extract_audio_references(field_value)
            for audio_ref in audio_refs:
                if self._register_audio_file(audio_ref, backend):
                    registered_count += 1

            # Extract image references: <img src="filename.jpg">
            image_refs = self._extract_image_references(field_value)
            for image_ref in image_refs:
                if self._register_image_file(image_ref, backend):
                    registered_count += 1

        return registered_count

    def register_all_card_media(
        self, all_field_values: list[list[str]], backend: DeckBackend
    ) -> int:
        """Register media files from multiple cards in batch.

        Args:
            all_field_values: List of card field value lists
            backend: Backend to register media files with

        Returns:
            Total number of media files successfully registered
        """
        total_registered = 0

        for field_values in all_field_values:
            total_registered += self.register_card_media(field_values, backend)

        logger.info(
            f"MediaFileRegistrar registered {total_registered} media files "
            f"from {len(all_field_values)} cards"
        )
        return total_registered

    def _extract_audio_references(self, content: str) -> list[str]:
        """Extract audio file references from content.

        Args:
            content: String content to search for audio references

        Returns:
            List of audio filenames found in [sound:filename] format
        """
        # Match [sound:filename.mp3] pattern (exclude empty filenames)
        audio_pattern = r"\[sound:([^]\s]+)\]"
        matches = re.findall(audio_pattern, content)
        return [
            match
            for match in matches
            if match.strip() and self._is_safe_filename(match.strip())
        ]

    def _is_safe_filename(self, filename: str) -> bool:
        """Validate that filename is safe and doesn't contain path traversal sequences.

        Args:
            filename: Filename to validate

        Returns:
            True if filename is safe, False otherwise
        """
        # Check for path traversal attempts
        if "../" in filename or "..\\" in filename:
            return False

        # Check for absolute paths
        if filename.startswith("/") or filename.startswith("\\"):
            return False

        # Use regex pattern for comprehensive filename validation
        # Disallow consecutive dots, filenames starting/ending with dots
        # Only allow alphanumerics, single dots, dashes, underscores
        import re

        safe_pattern = r"^[A-Za-z0-9](?!.*\.\.)[A-Za-z0-9._-]*[A-Za-z0-9_-]$"
        return re.match(safe_pattern, filename) is not None

    def _extract_image_references(self, content: str) -> list[str]:
        """Extract image file references from content.

        Args:
            content: String content to search for image references

        Returns:
            List of image filenames found in <img src="filename"> format
        """
        # Match <img src="filename.jpg"> pattern (various formats)
        img_pattern = r'<img[^>]+src=[\'"]([^>\'"]+)[\'"][^>]*>'
        matches = re.findall(img_pattern, content)
        return [match for match in matches if self._is_safe_filename(match)]

    def _register_audio_file(self, filename: str, backend: DeckBackend) -> bool:
        """Register an audio file with the backend.

        Args:
            filename: Audio filename to register
            backend: Backend to register with

        Returns:
            True if file was successfully registered, False otherwise
        """
        if filename in self._registered_files:
            return False  # Already registered

        file_path = self._audio_base_path / filename

        if not file_path.exists():
            logger.warning(f"Audio file not found: {file_path}")
            return False

        try:
            backend.add_media_file(str(file_path), media_type="audio")
            self._registered_files.add(filename)
            logger.debug(f"Registered audio file: {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to register audio file {filename}: {e}")
            return False

    def _register_image_file(self, filename: str, backend: DeckBackend) -> bool:
        """Register an image file with the backend.

        Args:
            filename: Image filename to register
            backend: Backend to register with

        Returns:
            True if file was successfully registered, False otherwise
        """
        if filename in self._registered_files:
            return False  # Already registered

        file_path = self._image_base_path / filename

        if not file_path.exists():
            logger.warning(f"Image file not found: {file_path}")
            return False

        try:
            backend.add_media_file(str(file_path), media_type="image")
            self._registered_files.add(filename)
            logger.debug(f"Registered image file: {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to register image file {filename}: {e}")
            return False

    def get_registration_stats(self) -> dict[str, Any]:
        """Get statistics about media file registration.

        Returns:
            Dictionary with registration statistics
        """
        return {
            "total_files_registered": len(self._registered_files),
            "registered_files": sorted(self._registered_files),
        }

    def reset_registration_tracking(self) -> None:
        """Reset the internal tracking of registered files.

        Useful for starting a fresh registration session.
        """
        self._registered_files.clear()
        logger.debug("MediaFileRegistrar registration tracking reset")
