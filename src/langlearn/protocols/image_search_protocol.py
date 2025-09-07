from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

"""Protocol for searching and downloading images from external APIs."""


@runtime_checkable
class ImageSearchProtocol(Protocol):
    """Protocol for image search and download services.

    This protocol defines the interface for services that can search for
    and download images from external APIs like Pexels, Unsplash, etc.
    """

    def search_photos(self, query: str, per_page: int = 5) -> list[Any]:
        """Search for photos using a text query.

        Args:
            query: Search query text (e.g., "domestic cat sleeping")
            per_page: Number of results to return (default: 5)

        Returns:
            List of photo objects/dictionaries with image metadata

        Example:
            >>> service = PexelsService()
            >>> results = service.search_photos("domestic cat", per_page=5)
            >>> print(len(results))  # 5
        """
        ...

    def download_image(
        self, query: str, output_path: str, size: Any = "medium"
    ) -> bool:
        """Search for and download an image directly by query.

        Args:
            query: Search query text (e.g., "domestic cat sleeping")
            output_path: Local file path where image should be saved
            size: Image size to download (default: "medium")

        Returns:
            True if image was successfully downloaded, False otherwise

        Example:
            >>> service = PexelsService()
            >>> success = service.download_image("domestic cat", "/images/cat.jpg")
            >>> print(success)  # True
        """
        ...
