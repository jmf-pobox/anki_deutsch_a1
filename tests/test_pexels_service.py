"""Unit tests for PexelsService."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from requests.exceptions import ConnectionError, HTTPError, Timeout

from langlearn.services.pexels_service import PexelsService, Photo, PhotoSize


class TestPexelsService:
    """Test PexelsService functionality."""

    @pytest.fixture
    def sample_photo(self) -> Photo:
        """Create a sample photo for testing."""
        return {
            "id": 123,
            "width": 800,
            "height": 600,
            "url": "https://www.pexels.com/photo/123",
            "photographer": "Test Photographer",
            "photographer_url": "https://www.pexels.com/@photographer",
            "photographer_id": 456,
            "avg_color": "#5A5A5A",
            "src": {
                "original": "https://images.pexels.com/photos/123/original.jpg",
                "large2x": "https://images.pexels.com/photos/123/large2x.jpg",
                "large": "https://images.pexels.com/photos/123/large.jpg",
                "medium": "https://images.pexels.com/photos/123/medium.jpg",
                "small": "https://images.pexels.com/photos/123/small.jpg",
                "portrait": "https://images.pexels.com/photos/123/portrait.jpg",
                "landscape": "https://images.pexels.com/photos/123/landscape.jpg",
                "tiny": "https://images.pexels.com/photos/123/tiny.jpg",
            },
            "liked": False,
            "alt": "A beautiful test photo",
        }

    @pytest.fixture
    def service(self) -> PexelsService:
        """Create PexelsService instance with mocked API key."""
        import os

        # Mock environment variable first (our new behavior)
        original_env = os.environ.get("PEXELS_API_KEY")
        os.environ["PEXELS_API_KEY"] = "test_api_key"

        try:
            return PexelsService()
        finally:
            # Restore original environment
            if original_env is None:
                os.environ.pop("PEXELS_API_KEY", None)
            else:
                os.environ["PEXELS_API_KEY"] = original_env

    def test_init_success(self) -> None:
        """Test successful initialization with API key."""
        import os

        # Test environment variable path (new behavior)
        original_env = os.environ.get("PEXELS_API_KEY")
        os.environ["PEXELS_API_KEY"] = "test_api_key"

        try:
            service = PexelsService()

            assert service.api_key == "test_api_key"
            assert service.base_url == "https://api.pexels.com/v1"
            assert service.max_retries == 5
            assert service.base_delay == 2
            assert service.max_delay == 60
            assert service.request_delay == 1.0
        finally:
            # Restore original environment
            if original_env is None:
                os.environ.pop("PEXELS_API_KEY", None)
            else:
                os.environ["PEXELS_API_KEY"] = original_env

    def test_init_no_api_key(self) -> None:
        """Test initialization failure when API key not found.

        This tests that the service properly raises an error when no
        credentials are available in a production (non-test) environment.
        """
        import os

        # Ensure no environment variable set
        original_env = os.environ.get("PEXELS_API_KEY")
        if "PEXELS_API_KEY" in os.environ:
            del os.environ["PEXELS_API_KEY"]

        try:
            with (
                patch("keyring.get_password") as mock_keyring,
                patch(
                    "langlearn.utils.environment.is_test_environment",
                    return_value=False,
                ),
            ):
                mock_keyring.return_value = None

                with pytest.raises(
                    ValueError,
                    match=(
                        "Pexels API key not found in environment variables or keyring"
                    ),
                ):
                    PexelsService()
        finally:
            # Restore original environment
            if original_env is not None:
                os.environ["PEXELS_API_KEY"] = original_env

    def test_get_headers(self, service: PexelsService) -> None:
        """Test header generation."""
        headers = service._get_headers()
        assert headers == {"Authorization": "test_api_key"}

    def test_calculate_backoff_delay_basic(self, service: PexelsService) -> None:
        """Test basic exponential backoff calculation."""
        # Mock random to get consistent results
        with patch("random.random", return_value=0.5):
            # Attempt 0: base_delay * 2^0 = 2 seconds
            delay = service._calculate_backoff_delay(0)
            assert delay >= 1  # At least minimum 1 second

            # Attempt 1: base_delay * 2^1 = 4 seconds
            delay = service._calculate_backoff_delay(1)
            assert delay >= 1

    def test_calculate_backoff_delay_with_retry_after(
        self, service: PexelsService
    ) -> None:
        """Test backoff calculation with server-suggested retry delay."""
        with patch("random.random", return_value=0.5):
            # Server suggests 10 seconds
            delay = service._calculate_backoff_delay(0, retry_after=10)
            # Should use max(10, base_delay=2) = 10 as base
            assert delay >= 1

    def test_calculate_backoff_delay_max_cap(self, service: PexelsService) -> None:
        """Test that backoff delay is capped at max_delay."""
        with patch("random.random", return_value=0.5):
            # Large attempt should be capped
            delay = service._calculate_backoff_delay(10)
            assert delay <= service.max_delay

    def test_calculate_backoff_delay_minimum(self, service: PexelsService) -> None:
        """Test that backoff delay has minimum of 1 second."""
        with patch("random.random", return_value=0.5):
            delay = service._calculate_backoff_delay(0)
            assert delay >= 1

    def test_make_request_success(self, service: PexelsService) -> None:
        """Test successful API request."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None

        with (
            patch("requests.get", return_value=mock_response) as mock_get,
            patch("time.sleep") as mock_sleep,
        ):
            result = service._make_request("https://test.com", {"query": "test"})

            assert result == mock_response
            mock_get.assert_called_once_with(
                "https://test.com",
                headers={"Authorization": "test_api_key"},
                params={"query": "test"},
                timeout=15,
            )
            # Should sleep after successful first attempt
            mock_sleep.assert_called_once_with(1.0)

    def test_make_request_rate_limit_with_retry_after(
        self, service: PexelsService
    ) -> None:
        """Test handling rate limit with Retry-After header."""
        # First call fails with 429, second succeeds
        mock_error_response = Mock()
        mock_error_response.status_code = 429
        mock_error_response.headers = {"Retry-After": "30"}

        mock_success_response = Mock()
        mock_success_response.raise_for_status.return_value = None

        http_error = HTTPError()
        http_error.response = mock_error_response

        with patch("requests.get") as mock_get, patch("time.sleep") as mock_sleep:
            mock_get.side_effect = [http_error, mock_success_response]

            result = service._make_request("https://test.com", {"query": "test"})

            assert result == mock_success_response
            assert mock_get.call_count == 2
            # Should have slept during retry
            mock_sleep.assert_called()

    def test_make_request_rate_limit_invalid_retry_after(
        self, service: PexelsService
    ) -> None:
        """Test handling rate limit with invalid Retry-After header."""
        mock_error_response = Mock()
        mock_error_response.status_code = 429
        mock_error_response.headers = {"Retry-After": "invalid"}

        mock_success_response = Mock()
        mock_success_response.raise_for_status.return_value = None

        http_error = HTTPError()
        http_error.response = mock_error_response

        with patch("requests.get") as mock_get, patch("time.sleep") as mock_sleep:
            mock_get.side_effect = [http_error, mock_success_response]

            result = service._make_request("https://test.com", {"query": "test"})

            assert result == mock_success_response
            # Should have slept during retry
            mock_sleep.assert_called()

    def test_make_request_rate_limit_exhausted(self, service: PexelsService) -> None:
        """Test rate limit exhaustion after all retries."""
        mock_error_response = Mock()
        mock_error_response.status_code = 429
        mock_error_response.headers = {}

        http_error = HTTPError()
        http_error.response = mock_error_response

        with (
            patch("requests.get", side_effect=http_error) as mock_get,
            patch("time.sleep"),
        ):
            with pytest.raises(HTTPError):
                service._make_request("https://test.com", {"query": "test"})

            # Should have tried max_retries times
            assert mock_get.call_count == service.max_retries

    def test_make_request_other_http_error(self, service: PexelsService) -> None:
        """Test handling of non-429 HTTP errors."""
        mock_error_response = Mock()
        mock_error_response.status_code = 404

        http_error = HTTPError()
        http_error.response = mock_error_response

        with (
            patch("requests.get", side_effect=http_error),
            pytest.raises(HTTPError),
        ):
            service._make_request("https://test.com", {"query": "test"})

    def test_make_request_generic_exception_with_retries(
        self, service: PexelsService
    ) -> None:
        """Test handling of generic exceptions with retries."""
        # First few calls fail, last one succeeds
        mock_success_response = Mock()
        mock_success_response.raise_for_status.return_value = None

        with patch("requests.get") as mock_get, patch("time.sleep") as mock_sleep:
            mock_get.side_effect = [
                ConnectionError("Network error"),
                Timeout("Request timeout"),
                mock_success_response,
            ]

            result = service._make_request("https://test.com", {"query": "test"})

            assert result == mock_success_response
            assert mock_get.call_count == 3
            # Should have slept during retries
            assert mock_sleep.call_count >= 2

    def test_make_request_generic_exception_exhausted(
        self, service: PexelsService
    ) -> None:
        """Test generic exception exhaustion after all retries."""
        with (
            patch(
                "requests.get", side_effect=ConnectionError("Network error")
            ) as mock_get,
            patch("time.sleep"),
        ):
            with pytest.raises(ConnectionError):
                service._make_request("https://test.com", {"query": "test"})

            # Should have tried max_retries times
            assert mock_get.call_count == service.max_retries

    def test_make_request_fails_after_all_retries(self, service: PexelsService) -> None:
        """Test that original exception is raised when all retries are exhausted."""
        # Simulate max_retries attempts, all failing with same exception
        with (
            patch("requests.get", side_effect=ConnectionError("Network error")),
            patch("time.sleep"),
            pytest.raises(ConnectionError, match="Network error"),
        ):
            service._make_request("https://test.com", {"query": "test"})

    def test_search_photos_success(
        self, service: PexelsService, sample_photo: Photo
    ) -> None:
        """Test successful photo search."""
        mock_response = Mock()
        mock_response.json.return_value = {"photos": [sample_photo]}

        with patch.object(service, "_make_request", return_value=mock_response):
            photos = service.search_photos("test query", per_page=10)

            assert len(photos) == 1
            assert photos[0] == sample_photo

    def test_search_photos_exception(self, service: PexelsService) -> None:
        """Test search_photos exception handling."""
        with patch.object(service, "_make_request", side_effect=Exception("API Error")):
            photos = service.search_photos("test query")

            # Should return empty list on exception
            assert photos == []

    def test_download_image_success(
        self, service: PexelsService, sample_photo: Photo
    ) -> None:
        """Test successful image download."""
        mock_search_response = Mock()
        mock_search_response.json.return_value = {"photos": [sample_photo]}

        mock_download_response = Mock()
        mock_download_response.content = b"fake image data"
        mock_download_response.raise_for_status.return_value = None

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test.jpg"

            with (
                patch.object(
                    service, "_make_request", return_value=mock_search_response
                ),
                patch("requests.get", return_value=mock_download_response),
                patch("random.choice", return_value=sample_photo),
            ):
                result = service.download_image(
                    "test query", str(output_path), "medium"
                )

                assert result is True
                assert output_path.exists()
                assert output_path.read_bytes() == b"fake image data"

    def test_download_image_no_photos_found(self, service: PexelsService) -> None:
        """Test download_image when no photos are found."""
        with patch.object(service, "search_photos", return_value=[]):
            result = service.download_image("nonexistent query", "test.jpg")

            assert result is False

    def test_download_image_exception(
        self, service: PexelsService, sample_photo: Photo
    ) -> None:
        """Test download_image exception handling."""
        with patch.object(
            service, "search_photos", side_effect=Exception("Search error")
        ):
            result = service.download_image("test query", "test.jpg")

            assert result is False

    def test_download_image_download_exception(
        self, service: PexelsService, sample_photo: Photo
    ) -> None:
        """Test download_image when image download fails."""
        with (
            patch.object(service, "search_photos", return_value=[sample_photo]),
            patch("requests.get", side_effect=HTTPError("Download failed")),
            patch("random.choice", return_value=sample_photo),
        ):
            result = service.download_image("test query", "test.jpg")

            assert result is False

    def test_download_image_file_write_exception(
        self, service: PexelsService, sample_photo: Photo
    ) -> None:
        """Test download_image when file writing fails."""
        mock_download_response = Mock()
        mock_download_response.content = b"fake image data"
        mock_download_response.raise_for_status.return_value = None

        with (
            patch.object(service, "search_photos", return_value=[sample_photo]),
            patch("requests.get", return_value=mock_download_response),
            patch("random.choice", return_value=sample_photo),
            patch("builtins.open", side_effect=OSError("Permission denied")),
        ):
            result = service.download_image("test query", "test.jpg")

            assert result is False

    def test_get_image_url_success(
        self, service: PexelsService, sample_photo: Photo
    ) -> None:
        """Test successful image URL retrieval."""
        with patch.object(service, "search_photos", return_value=[sample_photo]):
            url = service.get_image_url("test query", "large")

            assert url == sample_photo["src"]["large"]

    def test_get_image_url_no_photos_found(self, service: PexelsService) -> None:
        """Test get_image_url when no photos are found."""
        with patch.object(service, "search_photos", return_value=[]):
            url = service.get_image_url("nonexistent query")

            assert url is None

    def test_get_image_url_exception(self, service: PexelsService) -> None:
        """Test get_image_url exception handling."""
        with patch.object(
            service, "search_photos", side_effect=Exception("Search error")
        ):
            url = service.get_image_url("test query")

            assert url is None

    def test_get_image_url_different_sizes(
        self, service: PexelsService, sample_photo: Photo
    ) -> None:
        """Test get_image_url with different size parameters."""
        with patch.object(service, "search_photos", return_value=[sample_photo]):
            # Test all available sizes
            sizes: list[PhotoSize] = [
                "original",
                "large2x",
                "large",
                "medium",
                "small",
                "portrait",
                "landscape",
                "tiny",
            ]

            for size in sizes:
                url = service.get_image_url("test query", size)
                assert url == sample_photo["src"][size]

    def test_download_image_different_sizes(
        self, service: PexelsService, sample_photo: Photo
    ) -> None:
        """Test download_image with different size parameters."""
        mock_download_response = Mock()
        mock_download_response.content = b"fake image data"
        mock_download_response.raise_for_status.return_value = None

        with (
            tempfile.TemporaryDirectory() as temp_dir,
            patch.object(service, "search_photos", return_value=[sample_photo]),
            patch("requests.get", return_value=mock_download_response),
            patch("random.choice", return_value=sample_photo),
        ):
            sizes: list[PhotoSize] = [
                "original",
                "large2x",
                "large",
                "medium",
                "small",
                "portrait",
                "landscape",
                "tiny",
            ]

            for size in sizes:
                output_path = Path(temp_dir) / f"test_{size}.jpg"
                result = service.download_image("test query", str(output_path), size)

                assert result is True
                assert output_path.exists()

    def test_download_image_creates_parent_directories(
        self, service: PexelsService, sample_photo: Photo
    ) -> None:
        """Test that download_image creates parent directories."""
        mock_download_response = Mock()
        mock_download_response.content = b"fake image data"
        mock_download_response.raise_for_status.return_value = None

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create nested path that doesn't exist
            output_path = Path(temp_dir) / "nested" / "path" / "test.jpg"

            with (
                patch.object(service, "search_photos", return_value=[sample_photo]),
                patch("requests.get", return_value=mock_download_response),
                patch("random.choice", return_value=sample_photo),
            ):
                result = service.download_image("test query", str(output_path))

                assert result is True
                assert output_path.exists()
                assert output_path.parent.exists()

    def test_search_photos_default_per_page(
        self, service: PexelsService, sample_photo: Photo
    ) -> None:
        """Test search_photos uses default per_page value."""
        mock_response = Mock()
        mock_response.json.return_value = {"photos": [sample_photo]}

        with patch.object(
            service, "_make_request", return_value=mock_response
        ) as mock_request:
            service.search_photos("test query")

            # Check that default per_page=5 was used
            mock_request.assert_called_once_with(
                f"{service.base_url}/search", {"query": "test query", "per_page": 5}
            )

    def test_get_image_url_default_size(
        self, service: PexelsService, sample_photo: Photo
    ) -> None:
        """Test get_image_url uses default medium size."""
        with patch.object(service, "search_photos", return_value=[sample_photo]):
            url = service.get_image_url("test query")

            assert url == sample_photo["src"]["medium"]

    def test_make_request_loop_completion_fallback(
        self, service: PexelsService
    ) -> None:
        """Test the unreachable fallback HTTPError (defensive programming)."""
        # This tests the defensive HTTPError at the end of _make_request
        # While it's technically unreachable given current logic, it's good
        # defensive programming

        # We'll mock the range function to return an empty range, simulating
        # loop completion
        with (
            patch("builtins.range", return_value=[]),
            patch("requests.get"),  # Should never be called
            pytest.raises(HTTPError, match="Failed to make request after all retries"),
        ):
            service._make_request("https://test.com", {"query": "test"})
