"""Media service protocol for dependency injection."""

from typing import Protocol


class MediaServiceProtocol(Protocol):
    """Protocol defining the media service interface."""

    def generate_or_get_audio(self, text: str) -> str | None:
        """Generate or get existing audio for text."""
        ...

    def generate_or_get_image(
        self, word: str, search_query: str | None = None, example_sentence: str = ""
    ) -> str | None:
        """Generate or get existing image for word."""
        ...
