#!/usr/bin/env python

import os
import sys
import unittest

# Add the src directory to the Python path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
)

from langlearn.utils.api_keyring import CredentialManager


class TestApiKeyring(unittest.TestCase):
    """Integration tests for the API keyring utility."""

    def setUp(self) -> None:
        """Set up test environment."""
        # Skip all keyring tests in CI environment
        if os.environ.get("CI") == "true":
            self.skipTest("Keyring functionality not available in CI environment")

        self.test_app_name = "test_app"
        self.test_username = "test_user"
        self.test_password = "test_password"

        try:
            self.cred_manager = CredentialManager(self.test_app_name)
        except Exception as e:
            if "keyring" in str(e).lower() or "backend" in str(e).lower():
                self.skipTest("Keyring backend not available")
            raise

    def tearDown(self) -> None:
        """Clean up test environment."""
        # Clean up any test credentials
        self.cred_manager.delete_credentials(self.test_username)

    def test_save_and_retrieve_credentials(self) -> None:
        """Test saving and retrieving credentials."""
        # Save credentials
        self.cred_manager.save_credentials(self.test_username, self.test_password)

        # Retrieve credentials
        retrieved_password = self.cred_manager.get_password(self.test_username)

        # Verify
        self.assertEqual(retrieved_password, self.test_password)

    def test_delete_credentials(self) -> None:
        """Test deleting credentials."""
        # Save credentials first
        self.cred_manager.save_credentials(self.test_username, self.test_password)

        # Delete credentials
        self.cred_manager.delete_credentials(self.test_username)

        # Verify deletion
        retrieved_password = self.cred_manager.get_password(self.test_username)
        self.assertIsNone(retrieved_password)

    def test_nonexistent_credentials(self) -> None:
        """Test retrieving nonexistent credentials."""
        retrieved_password = self.cred_manager.get_password("nonexistent_user")
        self.assertIsNone(retrieved_password)

    def test_update_credentials(self) -> None:
        """Test updating existing credentials."""
        # Save initial credentials
        self.cred_manager.save_credentials(self.test_username, self.test_password)

        # Update credentials
        new_password = "new_test_password"
        self.cred_manager.save_credentials(self.test_username, new_password)

        # Verify update
        retrieved_password = self.cred_manager.get_password(self.test_username)
        self.assertEqual(retrieved_password, new_password)

    def test_multiple_apps(self) -> None:
        """Test managing credentials for multiple apps."""
        # Create another app's credential manager
        other_app_name = "other_test_app"
        other_cred_manager = CredentialManager(other_app_name)

        # Save credentials for both apps
        self.cred_manager.save_credentials(self.test_username, self.test_password)
        other_password = "other_test_password"
        other_cred_manager.save_credentials(self.test_username, other_password)

        # Verify credentials are stored separately
        self.assertEqual(
            self.cred_manager.get_password(self.test_username), self.test_password
        )
        self.assertEqual(
            other_cred_manager.get_password(self.test_username), other_password
        )

        # Clean up
        other_cred_manager.delete_credentials(self.test_username)


if __name__ == "__main__":
    unittest.main()
