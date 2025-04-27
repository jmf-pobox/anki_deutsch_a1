"""Service for interacting with the Pexels API."""

import logging
import logging.handlers
import random
from pathlib import Path
from typing import TypedDict

import requests

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Add file handler for pexels.log
file_handler = logging.handlers.RotatingFileHandler(
    log_dir / "pexels.log", maxBytes=1024 * 1024, backupCount=5  # 1MB
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(file_handler)

# Add console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logger.addHandler(console_handler)


class PhotoSource(TypedDict):
    """Type definition for Pexels photo source URLs."""

    original: str
    large2x: str
    large: str
    medium: str
    small: str
    portrait: str
    landscape: str
    tiny: str


class Photo(TypedDict):
    """Type definition for Pexels photo object."""

    id: int
    width: int
    height: int
    url: str
    photographer: str
    photographer_url: str
    photographer_id: int
    avg_color: str
    src: PhotoSource
    liked: bool
    alt: str


class PexelsService:
    """Service for interacting with the Pexels API."""

    def __init__(self) -> None:
        """Initialize the PexelsService."""
        import keyring

        self.api_key = keyring.get_password("PEXELS_API_KEY", "PEXELS_API_KEY")
        if not self.api_key:
            raise ValueError("Pexels API key not found in keyring")
        self.base_url = "https://api.pexels.com/v1"

    def _get_headers(self) -> dict[str, str]:
        """Get headers for Pexels API requests.

        Returns:
            dict: Headers for API requests
        """
        return {"Authorization": self.api_key}

    def search_photos(self, query: str, per_page: int = 5) -> list[Photo]:
        """Search for photos on Pexels.

        Args:
            query: Search query
            per_page: Number of results to return

        Returns:
            List of photo results
        """
        try:
            response = requests.get(
                f"{self.base_url}/search",
                headers=self._get_headers(),
                params={"query": query, "per_page": per_page},
                timeout=10,
            )
            response.raise_for_status()
            return response.json()["photos"]
        except Exception as e:
            logger.error("Error searching Pexels: %s", str(e))
            return []

    def download_image(self, query: str, output_path: str) -> bool:
        """Download an image from Pexels.

        Args:
            query: Search query
            output_path: Path to save the image

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Search for photos
            photos = self.search_photos(query)
            if not photos:
                logger.error("No photos found for query: %s", query)
                return False

            # Randomly select one of the top results
            selected_photo = random.choice(photos)
            image_url = selected_photo["src"]["original"]

            # Download the image
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()

            # Save the image
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(response.content)

            logger.debug(
                "Successfully downloaded image from %s to %s", image_url, output_path
            )
            return True

        except Exception as e:
            logger.error("Error downloading image: %s", str(e))
            return False

    def get_image_url(self, query: str, size: str = "medium") -> str | None:
        """Get the URL of an image from Pexels.

        Args:
            query: Search query
            size: Desired image size (small, medium, large, original)

        Returns:
            str: URL of the image, or None if not found
        """
        try:
            photos = self.search_photos(query, per_page=1)
            if not photos:
                logger.error("No photos found for query: %s", query)
                return None

            photo = photos[0]
            return photo["src"][size]
        except Exception as e:
            logger.error("Error getting image URL: %s", str(e))
            return None
