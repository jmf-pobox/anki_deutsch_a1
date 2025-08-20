"""Pexels service protocol for dependency injection."""

from typing import Any, Protocol


class PexelsServiceProtocol(Protocol):
    """Protocol defining the Pexels service interface."""

    def search_photos(self, query: str, per_page: int = 10) -> list[dict[str, Any]]:
        """Search for photos on Pexels."""
        ...

    def download_photo(self, photo_url: str, filename: str) -> str:
        """Download a photo and return the local file path."""
        ...
