"""Live integration tests for Pexels image service."""

import logging
import sys
import time
from pathlib import Path
from typing import Literal

import keyring
import pytest
import requests

from langlearn.services import PexelsService

logger = logging.getLogger(__name__)


def is_rate_limited(e: Exception) -> bool:
    """Check if an exception is due to rate limiting."""
    return "429" in str(e) or "Too Many Requests" in str(e)


def is_rate_limit_error(e: Exception) -> bool:
    """Check if an error is due to rate limiting, including nested errors."""
    if is_rate_limited(e):
        return True
    # Check if the error message contains a nested rate limit error
    error_str = str(e).lower()
    return "429" in error_str or "too many requests" in error_str


@pytest.mark.live
def test_api_direct() -> None:
    """Test Pexels API directly."""
    api_key = keyring.get_password("PEXELS_API_KEY", "PEXELS_API_KEY")
    if not api_key:
        pytest.skip("PEXELS_API_KEY not found in keyring")

    try:
        headers = {"Authorization": api_key}
        params: dict[str, str | int] = {"query": "test", "per_page": 1}
        response = requests.get(
            "https://api.pexels.com/v1/search",
            headers=headers,
            params=params,
        )
        print(f"Status code: {response.status_code}", file=sys.stderr)
        print(f"Response: {response.text}", file=sys.stderr)
        print(f"Headers: {response.headers}", file=sys.stderr)
        assert response.status_code == 200
        assert "photos" in response.json()
    except Exception as e:
        if is_rate_limit_error(e):
            pytest.skip("Rate limited by Pexels API")
        raise


@pytest.mark.live
def test_live_image_url() -> None:
    """Test getting real image URL from Pexels."""
    service = PexelsService()  # Will use API key from keyring

    # Try a few different queries to increase chances of success
    queries = ["nature", "city", "people"]
    url = None
    rate_limited = False

    for i, query in enumerate(queries):
        if i > 0:  # Add delay between attempts
            time.sleep(5)  # Wait 5 seconds between queries
        try:
            url = service.get_image_url(query)
            if url is not None:
                break
        except Exception as e:
            if is_rate_limit_error(e):
                rate_limited = True
                logger.warning("Rate limited by Pexels API")
            continue

    if rate_limited and url is None:
        pytest.skip("Rate limited by Pexels API")

    assert url is not None, "Failed to get image URL after trying multiple queries"
    assert url.startswith("https://")

    # Test different sizes with delay between requests
    rate_limited = False
    sizes: list[Literal["small", "large", "original"]] = ["small", "large", "original"]
    for i, size in enumerate(sizes):
        if i > 0:  # Add delay between attempts
            time.sleep(5)  # Wait 5 seconds between queries
        try:
            size_url = service.get_image_url(queries[0], size)
            if size_url is not None:
                assert size_url.startswith("https://")
                break
        except Exception as e:
            if is_rate_limit_error(e):
                rate_limited = True
                logger.warning("Rate limited by Pexels API")
            continue

    if rate_limited:
        pytest.skip("Rate limited by Pexels API")


@pytest.mark.live
def test_live_download_image(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Test downloading a real image."""
    service = PexelsService()  # Will use API key from keyring
    output_path = tmp_path / "test.jpg"

    # Try a few different queries to increase chances of success
    queries = ["nature", "city", "people"]
    success = False
    rate_limited = False

    for i, query in enumerate(queries):
        if i > 0:  # Add delay between attempts
            time.sleep(5)  # Wait 5 seconds between queries
        try:
            if service.download_image(query, str(output_path)):
                success = True
                break
        except Exception as e:
            if is_rate_limit_error(e):
                rate_limited = True
                logger.warning("Rate limited by Pexels API")
            continue

    if rate_limited:
        pytest.skip("Rate limited by Pexels API")

    if not success:
        # If we're not rate limited but still failed, check the logs
        # to see if we got any rate limit errors in the nested calls
        log_text = caplog.text.lower()
        if "429" in log_text or "too many requests" in log_text:
            pytest.skip("Rate limited by Pexels API (detected in logs)")

    assert success, "Failed to download image after trying multiple queries"
    assert output_path.exists()
    assert output_path.stat().st_size > 0
