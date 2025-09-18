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
    # First, check if we're running integration tests (always use real APIs)
    current_test = os.environ.get("PYTEST_CURRENT_TEST", "")
    if any(marker in current_test for marker in ["integration", "live"]):
        return False

    if any("integration" in arg for arg in sys.argv):
        return False

    # Then check if we're in a unit test context (always use mocks)
    is_unit_test = (
        "pytest" in sys.modules
        or bool(os.environ.get("PYTEST_CURRENT_TEST", "").strip())
        or any("test" in arg for arg in sys.argv)
    )

    if is_unit_test:
        return True

    # If we have API key and we're in CI (but not in test context), use real APIs
    if api_key and os.environ.get("CI") == "true":
        return False

    # Default to mocking if no clear context
    return True


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
