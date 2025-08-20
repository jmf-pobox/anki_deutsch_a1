"""Enhanced pytest configuration for better test isolation.

This configuration file provides:
- Automatic AWS service mocking for unit tests
- Proper separation between unit and integration tests
- Centralized fixtures for service mocking
- Environment variable management for CI/CD
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest


# Environment setup for tests
def pytest_configure(config):
    """Configure pytest environment before tests run."""
    # Set default test environment variables if not present
    # This prevents service initialization errors in CI/CD
    if "AWS_DEFAULT_REGION" not in os.environ:
        os.environ["AWS_DEFAULT_REGION"] = "eu-central-1"

    # Add test markers
    config.addinivalue_line("markers", "live: marks tests that require live API access")
    config.addinivalue_line(
        "markers", "unit: marks unit tests that use mocked services"
    )
    config.addinivalue_line(
        "markers", "integration: marks integration tests that use real services"
    )


@pytest.fixture(autouse=True)
def auto_mock_external_services(request):
    """Automatically mock external services for unit tests.

    This fixture:
    - Runs automatically for all tests
    - Skips mocking for tests marked with @pytest.mark.live
    - Provides mock AWS credentials for service initialization
    - Mocks boto3 client creation to prevent real API calls
    """
    # Check if this is an integration test
    if "live" in request.keywords or "integration" in request.keywords:
        # Don't mock for integration tests
        yield
        return

    # Set mock credentials if not present (for service initialization)
    original_env = {}
    mock_env_vars = {
        "AWS_ACCESS_KEY_ID": os.environ.get("AWS_ACCESS_KEY_ID", "mock-access-key"),
        "AWS_SECRET_ACCESS_KEY": os.environ.get("AWS_SECRET_ACCESS_KEY", "mock-secret"),
        "AWS_DEFAULT_REGION": os.environ.get("AWS_DEFAULT_REGION", "eu-central-1"),
        "PEXELS_API_KEY": os.environ.get("PEXELS_API_KEY", "mock-pexels-key"),
    }

    # Store original values and set mock values
    for key, value in mock_env_vars.items():
        if key not in os.environ:
            original_env[key] = None
            os.environ[key] = value

    # Mock boto3 client creation to prevent real AWS calls
    with patch("boto3.client") as mock_boto_client:
        # Create mock Polly client
        mock_polly = Mock()
        mock_polly.synthesize_speech.return_value = {
            "AudioStream": Mock(read=lambda: b"mock audio data"),
            "ContentType": "audio/mpeg",
            "RequestCharacters": 100,
        }

        # Return appropriate mock based on service name
        def get_mock_client(service_name, **kwargs):
            if service_name == "polly":
                return mock_polly
            return Mock()

        mock_boto_client.side_effect = get_mock_client

        try:
            yield mock_polly
        finally:
            # Restore original environment
            for key, value in original_env.items():
                if value is None and key in os.environ:
                    del os.environ[key]


@pytest.fixture
def mock_audio_service():
    """Provide a fully mocked AudioService for tests.

    Returns:
        Mock: A mock AudioService with common methods stubbed
    """
    from langlearn.services.audio import AudioService

    service = Mock(spec=AudioService)
    service.output_dir = Path("/tmp/test_audio")
    service.voice_id = "Daniel"
    service.language_code = "de-DE"
    service.speech_rate = 75

    # Mock the generate_audio method
    def mock_generate_audio(text, filename=None):
        if filename is None:
            filename = "mock_audio"
        return Path(f"/tmp/test_audio/{filename}.mp3")

    service.generate_audio.side_effect = mock_generate_audio
    service.generate_audio_with_retry.side_effect = mock_generate_audio

    return service


@pytest.fixture
def mock_pexels_service():
    """Provide a fully mocked PexelsService for tests.

    Returns:
        Mock: A mock PexelsService with common methods stubbed
    """
    from langlearn.services.pexels_service import PexelsService

    service = Mock(spec=PexelsService)

    # Mock the search_and_download method
    def mock_search_and_download(query, output_dir, filename=None):
        if filename is None:
            filename = query.replace(" ", "_")
        return Path(f"{output_dir}/{filename}.jpg")

    service.search_and_download.side_effect = mock_search_and_download
    service.download_image.return_value = Path("/tmp/test_image.jpg")

    return service


@pytest.fixture
def mock_media_service(mock_audio_service, mock_pexels_service):
    """Provide a fully mocked MediaService for tests.

    Args:
        mock_audio_service: Mocked AudioService fixture
        mock_pexels_service: Mocked PexelsService fixture

    Returns:
        Mock: A mock MediaService with all dependencies mocked
    """
    from langlearn.protocols import MediaServiceProtocol

    service = Mock(spec=MediaServiceProtocol)

    # Wire up the mock services
    service._audio_service = mock_audio_service
    service._pexels_service = mock_pexels_service

    # Mock the main methods
    service.generate_audio.side_effect = mock_audio_service.generate_audio
    service.fetch_image.side_effect = mock_pexels_service.search_and_download

    return service


@pytest.fixture
def temp_test_dir():
    """Create a temporary directory for test files.

    Yields:
        Path: Path to temporary directory that's cleaned up after test
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_anki_backend(mock_media_service):
    """Provide a properly initialized AnkiBackend with mocked services.

    Args:
        mock_media_service: Mocked MediaService fixture

    Returns:
        AnkiBackend: Backend instance with mocked external services
    """
    from langlearn.backends.anki_backend import AnkiBackend

    # Create backend with mocked media service
    backend = AnkiBackend(
        deck_name="Test Deck",
        description="Test Description",
        media_service=mock_media_service,
    )

    return backend


@pytest.fixture
def sample_csv_data():
    """Provide sample CSV data for testing.

    Returns:
        dict: Dictionary of CSV data by word type
    """
    return {
        "noun": [
            {
                "word": "Haus",
                "article": "das",
                "plural": "Häuser",
                "translation": "house",
                "example": "Das Haus ist groß.",
            },
            {
                "word": "Katze",
                "article": "die",
                "plural": "Katzen",
                "translation": "cat",
                "example": "Die Katze schläft.",
            },
        ],
        "adjective": [
            {
                "word": "schön",
                "translation": "beautiful",
                "example": "Das ist schön.",
                "comparative": "schöner",
                "superlative": "am schönsten",
            },
            {
                "word": "groß",
                "translation": "big",
                "example": "Der Baum ist groß.",
                "comparative": "größer",
                "superlative": "am größten",
            },
        ],
        "verb": [
            {
                "word": "gehen",
                "translation": "to go",
                "present_ich": "gehe",
                "present_du": "gehst",
                "present_er": "geht",
                "perfect": "ist gegangen",
            },
        ],
    }


@pytest.fixture
def integration_test_guard(request):
    """Guard fixture to ensure integration tests have required credentials.

    This fixture:
    - Only runs for tests marked with @pytest.mark.live
    - Checks for required environment variables
    - Skips test if credentials are missing
    """
    if "live" not in request.keywords:
        return

    required_vars = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "PEXELS_API_KEY"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        pytest.skip(
            f"Integration test requires environment variables: {', '.join(missing_vars)}"
        )


# Test environment validation
def test_environment_setup():
    """Verify test environment is properly configured."""
    assert "AWS_DEFAULT_REGION" in os.environ
    assert os.environ["AWS_DEFAULT_REGION"] in ["eu-central-1", "us-east-1"]
