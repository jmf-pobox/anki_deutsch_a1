"""Global pytest configuration and fixtures for test suite.

This module provides centralized mocking for external services to ensure
unit tests run reliably in CI/CD environments without keyring backends.
"""

import os
from collections.abc import Generator
from typing import Any
from unittest.mock import Mock, patch

import pytest


@pytest.fixture(autouse=True)
def mock_external_services(
    request: pytest.FixtureRequest,
) -> Generator[dict[str, Any] | None, None, None]:
    """Automatically mock external services for unit tests only.

    This fixture runs before every test to ensure that:
    1. Environment variables are set for services that check them first
    2. Keyring calls are mocked as fallback
    3. AWS boto3 clients are mocked
    4. HTTP requests are mocked

    Integration tests (in tests/integration/) are excluded from
    mocking so they can make real API calls for end-to-end testing.

    This prevents keyring errors in CI environments while maintaining
    proper test isolation for unit tests.
    """
    # Skip mocking for integration tests that need real API calls
    if "integration" in str(request.path):
        yield None
        return
    # Store original environment
    original_env = {}
    test_env_vars = {
        "PEXELS_API_KEY": "mock-pexels-key",
        "ANTHROPIC_API_KEY": "mock-anthropic-key",
        "AWS_DEFAULT_REGION": "us-east-1",
        "AWS_ACCESS_KEY_ID": "mock-aws-key",
        "AWS_SECRET_ACCESS_KEY": "mock-aws-secret",
    }

    # Set test environment variables
    for key, value in test_env_vars.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value

    # Mock external service calls
    with (
        patch("langlearn.services.audio.boto3.client") as mock_boto_client,
        patch("langlearn.services.pexels_service.requests.get") as mock_requests,
        patch("keyring.get_password") as mock_keyring,
    ):
        # Configure mocks
        mock_boto_client.return_value = Mock()
        mock_requests.return_value = Mock()
        mock_keyring.return_value = "mock-api-key"  # Fallback for keyring calls

        try:
            yield {
                "boto_client": mock_boto_client,
                "requests": mock_requests,
                "keyring": mock_keyring,
            }
        finally:
            # Restore original environment
            for key, original_value in original_env.items():
                if original_value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = original_value
