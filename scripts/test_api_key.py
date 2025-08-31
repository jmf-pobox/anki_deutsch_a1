#! /usr/bin/env python


import contextlib
import os

import anthropic
import keyring
import requests
from keyring.errors import PasswordDeleteError


class CredentialManager:
    """Manages application credentials using the system keyring."""

    __slots__ = ("_app_name",)

    _app_name: str

    def __new__(cls, app_name: str) -> "CredentialManager":
        """Create a new credential manager for the given application.

        Args:
            app_name: The name of the application to store credentials for

        Returns:
            A new CredentialManager instance
        """
        instance = super().__new__(cls)
        instance._app_name = app_name
        return instance

    def save_credentials(self, username: str, password: str) -> None:
        """Save credentials to the system keyring.

        Args:
            username: The username to store
            password: The password to store securely
        """
        keyring.set_password(self._app_name, username, password)

    def get_password(self, username: str) -> str | None:
        """Retrieve a password from the system keyring.

        Args:
            username: The username to retrieve the password for

        Returns:
            The stored password or None if not found
        """
        return keyring.get_password(self._app_name, username)

    def delete_credentials(self, username: str) -> None:
        """Delete credentials from the system keyring.

        Args:
            username: The username whose credentials should be deleted
        """
        with contextlib.suppress(PasswordDeleteError):
            keyring.delete_password(self._app_name, username)


def verify_pexels_api(api_key: str) -> bool:
    """Test Pexels API connectivity.

    Args:
        api_key: The Pexels API key to test

    Returns:
        True if API test successful, False otherwise
    """
    try:
        # Test with a minimal search query
        response = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": api_key},
            params={"query": "test", "per_page": 1},
            timeout=10,
        )
        response.raise_for_status()

        data = response.json()
        if "photos" in data and isinstance(data["photos"], list):
            print("✅ Pexels API connection successful!")
            print(f"   Found {data.get('total_results', 0)} available photos")
            return True
        else:
            print("❌ Pexels API returned unexpected format")
            return False

    except requests.exceptions.RequestException as e:
        print("❌ FAILED: Pexels API connection error")
        print(f"   Error: {e!s}")
        return False
    except Exception as e:
        print("❌ FAILED: Pexels API unexpected error")
        print(f"   Error: {e!s}")
        return False


def main() -> None:
    """Test environment setup for API key configuration."""
    print("🔑 Testing API key environment setup...")
    print()

    tests_passed = 0
    total_tests = 2

    # Test 1: Anthropic API
    print("=== Anthropic API Test ===")
    anthropic_key = "ANTHROPIC_API_KEY"
    cred_manager = CredentialManager(anthropic_key)

    # Retrieve the key
    print(f"📋 Checking keyring for {anthropic_key}...")
    stored_key = cred_manager.get_password(anthropic_key)

    if stored_key is None:
        print("❌ FAILED: Anthropic API key not found in system keyring")
        print()
        print("🛠️  Setup Instructions:")
        print(
            "   Run: python scripts/api_keyring.py add ANTHROPIC_API_KEY your_key_here"
        )
        print("   Or set environment variable: export ANTHROPIC_API_KEY=your_key_here")
    else:
        print("✅ API key found in keyring")
        print(f"   Key starts with: {stored_key[:20]}...")
        print()

        # Test API connectivity
        print("🌐 Testing Anthropic API connection...")
        try:
            client = anthropic.Anthropic(api_key=stored_key)
            message = client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=50,
                messages=[
                    {
                        "role": "user",
                        "content": "Say 'API test successful' in exactly those words.",
                    }
                ],
            )

            response_text = message.content[0].text if message.content else ""
            print("✅ Anthropic API connection successful!")
            print(f"   Response: {response_text}")
            tests_passed += 1

        except Exception as e:
            print("❌ FAILED: Anthropic API connection error")
            print(f"   Error: {e!s}")

    print()

    # Test 2: Pexels API
    print("=== Pexels API Test ===")
    pexels_key = "PEXELS_API_KEY"
    pexels_cred_manager = CredentialManager(pexels_key)

    print(f"📋 Checking keyring for {pexels_key}...")
    # First try keyring, then environment variable
    pexels_api_key = pexels_cred_manager.get_password(pexels_key)
    if not pexels_api_key:
        pexels_api_key = os.environ.get("PEXELS_API_KEY")

    if not pexels_api_key:
        print("❌ FAILED: Pexels API key not found in keyring or environment")
        print()
        print("🛠️  Setup Instructions:")
        print("   Run: python scripts/api_keyring.py add PEXELS_API_KEY your_key_here")
        print("   Or set environment variable: export PEXELS_API_KEY=your_key_here")
    else:
        print("✅ API key found")
        print(f"   Key starts with: {pexels_api_key[:15]}...")
        print()

        # Test API connectivity
        print("🌐 Testing Pexels API connection...")
        if verify_pexels_api(pexels_api_key):
            tests_passed += 1

    print()
    print("=" * 50)

    # Final summary
    if tests_passed == total_tests:
        print("🎉 All API tests passed! Your environment is fully configured.")
    elif tests_passed > 0:
        print(f"⚠️  Partial success: {tests_passed}/{total_tests} API tests passed.")
        print("   Some functionality may be limited until all APIs are configured.")
    else:
        print("❌ No API tests passed. Please configure your API keys.")

    print()
    print("🛠️  General Troubleshooting:")
    print("   1. Verify your API keys are valid")
    print("   2. Check your internet connection")
    print("   3. Ensure you have sufficient API credits")
    print("   4. Review the setup instructions in README.md")


if __name__ == "__main__":
    main()
