#! /usr/bin/env python


import contextlib

import anthropic
import keyring
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


def main() -> None:
    """Test environment setup for API key configuration."""
    print("🔑 Testing API key environment setup...")
    print()

    # Create a credential manager for your application
    key: str = "ANTHROPIC_API_KEY"
    cred_manager = CredentialManager(key)

    # Retrieve the key
    print(f"📋 Checking keyring for {key}...")
    stored_key = cred_manager.get_password(key)

    if stored_key is None:
        print("❌ FAILED: API key not found in system keyring")
        print()
        print("🛠️  Setup Instructions:")
        print(
            "   Run: python scripts/api_keyring.py add ANTHROPIC_API_KEY your_key_here"
        )
        print("   Or set environment variable: export ANTHROPIC_API_KEY=your_key_here")
        return

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
        print("✅ API connection successful!")
        print(f"   Response: {response_text}")
        print()
        print("🎉 Environment setup complete! Your API keys are working correctly.")

    except Exception as e:
        print("❌ FAILED: API connection error")
        print(f"   Error: {e!s}")
        print()
        print("🛠️  Troubleshooting:")
        print("   1. Verify your API key is valid at https://console.anthropic.com")
        print("   2. Check your internet connection")
        print("   3. Ensure you have sufficient API credits")


if __name__ == "__main__":
    main()
