"""Tests for environment utility functions."""

import os
import sys
from unittest.mock import patch

from langlearn.infrastructure.utils.environment import (
    is_ci_environment,
    is_github_actions,
    is_test_environment,
)


class TestEnvironmentUtils:
    """Test environment detection utilities."""

    def test_is_test_environment_no_api_key(self) -> None:
        """Test is_test_environment without API key."""
        # Should return True since pytest is in sys.modules
        assert is_test_environment() is True

    def test_is_test_environment_with_api_key_ci(self) -> None:
        """Test is_test_environment with API key in CI outside test context."""
        env_patch = {"CI": "true", "PYTEST_CURRENT_TEST": ""}
        with (
            patch.dict(os.environ, env_patch, clear=True),
            patch.object(sys, "argv", ["myapp"]),
            patch.dict(sys.modules, {}, clear=True),
        ):
            # Simulate CI environment without pytest context
            assert is_test_environment("test-key") is False

    def test_is_test_environment_with_api_key_integration_env(self) -> None:
        """Test is_test_environment with API key and integration test marker."""
        with patch.dict(os.environ, {"PYTEST_CURRENT_TEST": "integration_test"}):
            assert is_test_environment("test-key") is False

    def test_is_test_environment_with_api_key_live_env(self) -> None:
        """Test is_test_environment with API key and live test marker."""
        with patch.dict(os.environ, {"PYTEST_CURRENT_TEST": "test_live_api"}):
            assert is_test_environment("test-key") is False

    def test_is_test_environment_with_api_key_integration_argv(self) -> None:
        """Test is_test_environment with API key and integration in argv."""
        with patch.object(sys, "argv", ["pytest", "tests/integration/"]):
            assert is_test_environment("test-key") is False

    def test_is_test_environment_unit_test_context(self) -> None:
        """Test is_test_environment detects unit test context."""
        # Test without API key (pytest modules detected)
        assert is_test_environment() is True

        # Test with test in argv
        with patch.object(sys, "argv", ["python", "-m", "pytest", "test_something.py"]):
            assert is_test_environment("test-key") is True

    def test_is_test_environment_pytest_current_test_env(self) -> None:
        """Test is_test_environment with PYTEST_CURRENT_TEST environment variable."""
        with patch.dict(
            os.environ, {"PYTEST_CURRENT_TEST": "test_unit.py::test_something"}
        ):
            # Without API key, should still be True (unit test)
            assert is_test_environment() is True

    def test_is_ci_environment_ci_true(self) -> None:
        """Test is_ci_environment when CI=true."""
        with patch.dict(os.environ, {"CI": "true"}):
            assert is_ci_environment() is True

    def test_is_ci_environment_gh_actions_true(self) -> None:
        """Test is_ci_environment when GH_ACTIONS=true."""
        with patch.dict(os.environ, {"GH_ACTIONS": "true"}):
            assert is_ci_environment() is True

    def test_is_ci_environment_false(self) -> None:
        """Test is_ci_environment when not in CI."""
        with patch.dict(os.environ, {}, clear=True):
            assert is_ci_environment() is False

    def test_is_ci_environment_ci_false(self) -> None:
        """Test is_ci_environment when CI=false."""
        with patch.dict(os.environ, {"CI": "false"}):
            assert is_ci_environment() is False

    def test_is_github_actions_github_actions_true(self) -> None:
        """Test is_github_actions when GITHUB_ACTIONS=true."""
        with patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}):
            assert is_github_actions() is True

    def test_is_github_actions_gh_actions_true(self) -> None:
        """Test is_github_actions when GH_ACTIONS=true."""
        with patch.dict(os.environ, {"GH_ACTIONS": "true"}):
            assert is_github_actions() is True

    def test_is_github_actions_false(self) -> None:
        """Test is_github_actions when not in GitHub Actions."""
        with patch.dict(os.environ, {}, clear=True):
            assert is_github_actions() is False

    def test_is_github_actions_github_actions_false(self) -> None:
        """Test is_github_actions when GITHUB_ACTIONS=false."""
        with patch.dict(os.environ, {"GITHUB_ACTIONS": "false"}):
            assert is_github_actions() is False

    def test_edge_cases_empty_strings(self) -> None:
        """Test edge cases with empty strings."""
        with patch.dict(
            os.environ, {"CI": "", "GITHUB_ACTIONS": "", "PYTEST_CURRENT_TEST": ""}
        ):
            assert is_ci_environment() is False
            assert is_github_actions() is False
            # Empty PYTEST_CURRENT_TEST should still be detected as test environment
            assert is_test_environment() is True

    def test_comprehensive_integration_scenarios(self) -> None:
        """Test comprehensive scenarios to maximize coverage."""
        # Test PYTEST_CURRENT_TEST without API key
        with patch.dict(
            os.environ,
            {"PYTEST_CURRENT_TEST": "test_unit_something.py::TestClass::test_method"},
        ):
            assert is_test_environment() is True

        # Test integration test detection via sys.argv (covers line 37)
        with patch.object(sys, "argv", ["python", "tests/integration/test_something.py"]):
            assert is_test_environment() is False  # Should detect integration test

        # Test multiple CI environment variable combinations
        with patch.dict(
            os.environ, {"CI": "true", "GH_ACTIONS": "true", "GITHUB_ACTIONS": "true"}
        ):
            assert is_ci_environment() is True
            assert is_github_actions() is True
            assert (
                is_test_environment("api-key") is False
            )  # CI with API key allows real calls
