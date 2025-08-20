"""Environment detection utilities for services."""

import os
import sys


def is_test_environment(api_key: str | None = None) -> bool:
    """Check if we're running in a test environment that should be mocked.

    Args:
        api_key: Optional API key to check. If provided and we're in CI,
                will return False to allow integration tests with real APIs.

    Returns:
        True for unit tests that should be mocked, False for integration
        tests that need real API clients even in CI environments.
    """
    # If we're in CI but have real API credentials, we're running integration tests
    if os.environ.get("CI") == "true" and api_key:
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
