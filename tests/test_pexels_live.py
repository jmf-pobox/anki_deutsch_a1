"""Live integration tests for Pexels image service."""

import sys
from pathlib import Path

import keyring
import pytest
import requests

from langlearn.services import PexelsService


@pytest.mark.live
def test_api_direct() -> None:
    """Test Pexels API directly."""
    api_key = keyring.get_password("PEXELS_API_KEY", "PEXELS_API_KEY")
    if not api_key:
        pytest.skip("PEXELS_API_KEY not found in keyring")

    headers = {"Authorization": api_key}
    response = requests.get(
        "https://api.pexels.com/v1/search",
        headers=headers,
        params={"query": "test", "per_page": 1},
    )
    print(f"Status code: {response.status_code}", file=sys.stderr)
    print(f"Response: {response.text}", file=sys.stderr)
    print(f"Headers: {response.headers}", file=sys.stderr)
    assert response.status_code == 200
    assert "photos" in response.json()


@pytest.mark.live
def test_live_image_url() -> None:
    """Test getting real image URL from Pexels."""
    service = PexelsService()  # Will use API key from keyring
    url = service.get_image_url("test query")
    assert url is not None
    assert url.startswith("https://")

    # Test different sizes
    small_url = service.get_image_url("test query", "small")
    assert small_url is not None
    assert small_url.startswith("https://")

    large_url = service.get_image_url("test query", "large")
    assert large_url is not None
    assert large_url.startswith("https://")

    original_url = service.get_image_url("test query", "original")
    assert original_url is not None
    assert original_url.startswith("https://")


@pytest.mark.live
def test_live_download_image(tmp_path: Path) -> None:
    """Test downloading a real image."""
    service = PexelsService()  # Will use API key from keyring
    output_path = tmp_path / "test.jpg"
    assert service.download_image("test query", str(output_path))
    assert output_path.exists()
    assert output_path.stat().st_size > 0  # Verify file is not empty
