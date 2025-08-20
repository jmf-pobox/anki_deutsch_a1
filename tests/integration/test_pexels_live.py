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


def is_rate_limited_error(e: Exception) -> bool:
    """Check if an exception indicates Pexels API rate limiting.

    Detects rate limiting from:
    - HTTP 429 status codes
    - "Too Many Requests" messages
    - Quota exceeded errors
    - Rate limit keywords in error messages
    """
    error_str = str(e).lower()
    rate_limit_indicators = [
        "429",
        "too many requests",
        "rate limit",
        "quota exceeded",
        "requests per hour exceeded",
        "api limit",
    ]
    return any(indicator in error_str for indicator in rate_limit_indicators)


def skip_if_rate_limited(e: Exception, test_name: str = "test") -> None:
    """Skip test if exception indicates rate limiting."""
    if is_rate_limited_error(e):
        pytest.skip(f"Pexels API rate limited during {test_name} - skipping for CI")


@pytest.mark.live
def test_api_direct() -> None:
    """Test Pexels API directly."""
    # Use environment variables first, then fall back to keyring
    import os

    api_key = os.environ.get("PEXELS_API_KEY")
    if not api_key:
        try:
            api_key = keyring.get_password("PEXELS_API_KEY", "PEXELS_API_KEY")
        except Exception:
            pytest.skip("PEXELS_API_KEY not available in environment or keyring")

    if not api_key:
        pytest.skip("PEXELS_API_KEY not available in environment or keyring")

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
        skip_if_rate_limited(e, "test_api_direct")
        raise


@pytest.mark.live
def test_live_image_url() -> None:
    """Test getting real image URL from Pexels."""
    # Use service constructor which checks environment variables first, then keyring
    try:
        service = PexelsService()
    except ValueError as e:
        if "not found in environment variables or keyring" in str(e):
            pytest.skip("PEXELS_API_KEY not available in environment or keyring")
        raise

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
            if is_rate_limited_error(e):
                rate_limited = True
                logger.warning("Rate limited by Pexels API")
            continue

    if rate_limited and url is None:
        pytest.skip("Rate limited by Pexels API during URL retrieval")

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
            if is_rate_limited_error(e):
                rate_limited = True
                logger.warning("Rate limited by Pexels API")
            continue

    if rate_limited:
        pytest.skip("Rate limited by Pexels API during size testing")


@pytest.mark.live
def test_live_download_image(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Test downloading a real image."""
    # Use service constructor which checks environment variables first, then keyring
    try:
        service = PexelsService()
    except ValueError as e:
        if "not found in environment variables or keyring" in str(e):
            pytest.skip("PEXELS_API_KEY not available in environment or keyring")
        raise
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
            if is_rate_limited_error(e):
                rate_limited = True
                logger.warning("Rate limited by Pexels API")
            continue

    if rate_limited:
        pytest.skip("Rate limited by Pexels API during download attempts")

    if not success:
        # Check if we got rate limit errors in the nested calls
        log_text = caplog.text.lower()
        if is_rate_limited_error(Exception(log_text)):
            pytest.skip("Rate limited by Pexels API (detected in logs)")

    assert success, "Failed to download image after trying multiple queries"
    assert output_path.exists()
    assert output_path.stat().st_size > 0
