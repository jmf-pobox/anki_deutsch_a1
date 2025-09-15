"""Service for interacting with the Pexels API."""

import contextlib
import logging
import logging.handlers
import random
import time
from pathlib import Path
from typing import Any, Literal, TypedDict, cast

import requests
from requests.exceptions import HTTPError

from langlearn.protocols.image_search_protocol import ImageSearchProtocol

# Set up logging
logger = logging.getLogger(__name__)

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Add file handler for pexels.log
file_handler = logging.handlers.RotatingFileHandler(
    log_dir / "pexels.log",
    maxBytes=1024 * 1024,
    backupCount=5,  # 1MB
)
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


# Define valid size options as a type
PhotoSize = Literal[
    "original",
    "large2x",
    "large",
    "medium",
    "small",
    "portrait",
    "landscape",
    "tiny",
]


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


class PexelsService(ImageSearchProtocol):
    """Service for interacting with the Pexels API."""

    def __init__(self) -> None:
        """Initialize the PexelsService."""
        import os

        # First check environment variables (for CI/CD), then fall back to keyring
        self.api_key = os.environ.get("PEXELS_API_KEY")
        if self.api_key is None:  # Environment variable not set at all
            import keyring

            self.api_key = keyring.get_password("PEXELS_API_KEY", "PEXELS_API_KEY")

        # Allow empty API key in test environments (will be mocked)
        from langlearn.utils.environment import is_test_environment

        if not self.api_key and not is_test_environment(self.api_key):
            raise ValueError(
                "Pexels API key not found in environment variables or keyring"
            )
        self.base_url = "https://api.pexels.com/v1"
        self.max_retries = 5  # Increased for bulk operations
        self.base_delay = 2  # Base delay in seconds for exponential backoff
        self.max_delay = 60  # Maximum delay cap
        self.request_delay = 1.0  # Minimum delay between requests to be API-friendly

    def _get_headers(self) -> dict[str, str]:
        """Get headers for Pexels API requests.

        Returns:
            dict: Headers for API requests
        """
        return {"Authorization": str(self.api_key)}

    def _calculate_backoff_delay(
        self, attempt: int, retry_after: int | None = None
    ) -> int:
        """Calculate exponential backoff delay with jitter.

        Args:
            attempt: Current attempt number (0-based)
            retry_after: Server-suggested retry delay (if any)

        Returns:
            Delay in seconds
        """
        if retry_after is not None:
            # Use server-suggested delay, but apply exponential backoff on top
            base_delay = max(retry_after, self.base_delay)
        else:
            base_delay = self.base_delay

        # Exponential backoff: base_delay * 2^attempt
        delay = base_delay * (2**attempt)

        # Cap the delay
        delay = min(delay, self.max_delay)

        # Add jitter to prevent thundering herd (±20%)
        jitter = delay * 0.2 * (random.random() - 0.5)  # -10% to +10%
        delay_with_jitter = int(delay + jitter)

        return max(delay_with_jitter, 1)  # Minimum 1 second

    def _make_request(self, url: str, params: dict[str, Any]) -> requests.Response:
        """Make a request to the Pexels API with exponential backoff retry logic.

        Args:
            url: API endpoint URL
            params: Query parameters

        Returns:
            Response from the API

        Raises:
            HTTPError: If the request fails after all retries
        """
        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    url,
                    headers=self._get_headers(),
                    params=params,
                    timeout=15,  # Increased timeout for stability
                )
                response.raise_for_status()

                # Add small delay after successful request to be API-friendly
                if attempt == 0:  # Only delay on first successful attempt, not retries
                    time.sleep(self.request_delay)

                return response
            except HTTPError as e:
                # Rate limit check
                if e.response.status_code == 429 and attempt < self.max_retries - 1:
                    # Get server-suggested retry delay
                    retry_after = None
                    if "Retry-After" in e.response.headers:
                        with contextlib.suppress(ValueError):
                            retry_after = int(e.response.headers["Retry-After"])

                    # Calculate exponential backoff delay
                    delay = self._calculate_backoff_delay(attempt, retry_after)

                    logger.warning(
                        "Rate limited. Using exponential backoff: waiting %d seconds "
                        "(attempt %d/%d, base_delay=%ds)",
                        delay,
                        attempt + 1,
                        self.max_retries,
                        retry_after or self.base_delay,
                    )
                    time.sleep(delay)
                    continue
                raise
            except Exception as e:
                if attempt < self.max_retries - 1:
                    # Apply exponential backoff for other errors too
                    delay = self._calculate_backoff_delay(attempt)
                    logger.warning(
                        "Request failed (%s). Retrying in %d seconds (attempt %d/%d)",
                        str(e),
                        delay,
                        attempt + 1,
                        self.max_retries,
                    )
                    time.sleep(delay)
                    continue
                logger.error("Error making request to Pexels: %s", str(e))
                raise
        raise HTTPError("Failed to make request after all retries")

    def search_photos(self, query: str, per_page: int = 5) -> list[Photo]:
        """Search for photos on Pexels.

        Args:
            query: Search query
            per_page: Number of results to return

        Returns:
            List of photo results

        Raises:
            MediaGenerationError: If the search request fails
        """
        try:
            response = self._make_request(
                f"{self.base_url}/search",
                {"query": query, "per_page": per_page},
            )
            return cast("list[Photo]", response.json()["photos"])
        except Exception as e:
            logger.error("Error searching Pexels: %s", str(e))
            # Re-raise with appropriate specific exception type
            from langlearn.exceptions import MediaGenerationError

            raise MediaGenerationError(
                f"Failed to search Pexels for '{query}': {e}"
            ) from e

    def download_image(
        self, query: str, output_path: str, size: PhotoSize = "medium"
    ) -> bool:
        """Download an image from Pexels.

        Args:
            query: Search query
            output_path: Path to save the image
            size: Image size to download (default: "medium" for good
                quality/size balance)

        Returns:
            bool: True if successful

        Raises:
            MediaGenerationError: If the download fails or no photos are found
        """
        try:
            # Search for photos
            photos = self.search_photos(query)
            if not photos:
                logger.error("No photos found for query: %s", query)
                from langlearn.exceptions import MediaGenerationError

                raise MediaGenerationError(f"No photos found for query: '{query}'")

            # Randomly select one of the top results
            selected_photo = random.choice(photos)
            image_url = selected_photo["src"][size]

            # Download the image
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()

            # Save the image
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "wb") as f:
                f.write(response.content)

            logger.debug(
                "Successfully downloaded image (%s size) from %s to %s",
                size,
                image_url,
                output_path,
            )
            return True

        except Exception as e:
            logger.error("Error downloading image: %s", str(e))
            # Re-raise with appropriate specific exception type
            from langlearn.exceptions import MediaGenerationError

            raise MediaGenerationError(
                f"Failed to download image for '{query}': {e}"
            ) from e

    def get_image_url(self, query: str, size: PhotoSize = "medium") -> str | None:
        """Get the URL of an image from Pexels.

        Args:
            query: Search query
            size: Desired image size (small, medium, large, original)

        Returns:
            str: URL of the image

        Raises:
            MediaGenerationError: If the request fails or no photos are found
        """
        try:
            photos: list[Photo] = self.search_photos(query, per_page=1)
            if not photos:
                logger.error("No photos found for query: %s", query)
                from langlearn.exceptions import MediaGenerationError

                raise MediaGenerationError(f"No photos found for query: '{query}'")

            photo: Photo = photos[0]
            url: str = photo["src"][size]
            return url
        except Exception as e:
            logger.error("Error getting image URL: %s", str(e))
            # Re-raise with appropriate specific exception type
            from langlearn.exceptions import MediaGenerationError

            raise MediaGenerationError(
                f"Failed to get image URL for '{query}': {e}"
            ) from e
