"""Environment detection utilities for services."""

import os
import sys


def is_test_environment(api_key: str | None = None) -> bool:
    """Check if we're running in a test environment that should be mocked.

    Args:
        api_key: Optional API key to check. If provided and we're in CI or
                integration tests, will return False to allow real API calls.

    Returns:
        True for unit tests that should be mocked, False for integration
        tests that need real API clients in any environment.
    """
    # If we have real API credentials, check if we're running integration tests
    if api_key:
        # Always allow real API calls in CI with credentials
        if os.environ.get("CI") == "true":
            return False

        # Allow real API calls for integration tests locally
        # Integration tests marked with @pytest.mark.live or run via test-integration
        current_test = os.environ.get("PYTEST_CURRENT_TEST", "")
        if any(marker in current_test for marker in ["integration", "live"]):
            return False

        # Check if we're explicitly running integration tests
        if any("integration" in arg for arg in sys.argv):
            return False

    # Check for pytest unit test environment (should be mocked)
    return (
        "pytest" in sys.modules
        or "PYTEST_CURRENT_TEST" in os.environ
        or any("test" in arg for arg in sys.argv)
    )


def is_ci_environment() -> bool:
    """Check if we're running in a CI environment.

    Returns:
        True if running in CI, False otherwise.
    """
    return os.environ.get("CI") == "true" or os.environ.get("GH_ACTIONS") == "true"


def is_github_actions() -> bool:
    """Check if we're running in GitHub Actions specifically.

    Returns:
        True if running in GitHub Actions, False otherwise.
    """
    return (
        os.environ.get("GITHUB_ACTIONS") == "true"
        or os.environ.get("GH_ACTIONS") == "true"
    )
