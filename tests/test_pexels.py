"""Mock tests for Pexels image service."""

from pathlib import Path
from typing import TypedDict, cast
from unittest.mock import patch

import pytest

from langlearn.services import PexelsService


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


class PexelsResponse(TypedDict):
    """Type definition for Pexels API response."""

    photos: list[Photo]


@pytest.fixture
def mock_photo() -> Photo:
    """Create a mock Pexels photo."""
    return cast(
        Photo,
        {
            "id": 1,
            "width": 100,
            "height": 100,
            "url": "https://example.com/photo",
            "photographer": "Test Photographer",
            "photographer_url": "https://example.com/photographer",
            "photographer_id": 1,
            "avg_color": "#000000",
            "src": {
                "original": "https://example.com/original.jpg",
                "large2x": "https://example.com/large2x.jpg",
                "large": "https://example.com/large.jpg",
                "medium": "https://example.com/medium.jpg",
                "small": "https://example.com/small.jpg",
                "portrait": "https://example.com/portrait.jpg",
                "landscape": "https://example.com/landscape.jpg",
                "tiny": "https://example.com/tiny.jpg",
            },
            "liked": False,
            "alt": "Test photo",
        },
    )


@pytest.fixture
def mock_response(mock_photo: Photo) -> PexelsResponse:
    """Create a mock Pexels API response."""
    return {"photos": [mock_photo]}


def test_get_image_url_success(mock_response: PexelsResponse) -> None:
    """Test successful image URL retrieval."""
    with (
        patch("requests.get") as mock_get,
        patch("keyring.get_password") as mock_get_password,
    ):
        mock_get_password.return_value = "test_key"
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status.return_value = None

        service = PexelsService()

        # Test different sizes
        assert service.get_image_url("house", "small") == "https://example.com/small.jpg"
        assert service.get_image_url("house", "medium") == "https://example.com/medium.jpg"
        assert service.get_image_url("house", "large") == "https://example.com/large.jpg"
        assert service.get_image_url("house", "original") == "https://example.com/original.jpg"


def test_download_image_success(mock_response: PexelsResponse, tmp_path: Path) -> None:
    """Test successful image download."""
    with (
        patch("requests.get") as mock_get,
        patch("keyring.get_password") as mock_get_password,
    ):
        mock_get_password.return_value = "test_key"
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status.return_value = None
        mock_get.return_value.content = b"fake image data"

        service = PexelsService()
        output_path = tmp_path / "test.jpg"

        assert service.download_image("dog", str(output_path))
        assert output_path.exists()
        assert output_path.read_bytes() == b"fake image data"


@pytest.mark.live
def test_live_get_image_url() -> None:
    """Test image URL retrieval with real API key."""
    service = PexelsService()  # Uses real API key from keyring
    url = service.get_image_url("house", "medium")
    assert url is not None
    assert url.startswith("https://images.pexels.com/photos/")


@pytest.mark.live
def test_live_download_image(tmp_path: Path) -> None:
    """Test image download with real API key."""
    service = PexelsService()  # Uses real API key from keyring
    output_path = tmp_path / "test.jpg"
    assert service.download_image("house", str(output_path))
    assert output_path.exists()
    assert output_path.stat().st_size > 0
