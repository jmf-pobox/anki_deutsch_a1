"""Audio service protocol for dependency injection."""

from typing import Protocol


class AudioServiceProtocol(Protocol):
    """Protocol defining the audio service interface."""

    def generate_audio(self, text: str, voice: str = "Marlene") -> str:
        """Generate audio file for given text and return filename."""
        ...

    def get_existing_audio(self, text: str, voice: str = "Marlene") -> str | None:
        """Get existing audio file path if it exists."""
        ...
