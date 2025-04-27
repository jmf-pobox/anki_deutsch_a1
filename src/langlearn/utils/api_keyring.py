#!/usr/bin/env python

import argparse
import contextlib
import sys
from typing import NoReturn

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


def test_anthropic_key(key: str) -> None:
    """Test if an Anthropic API key is valid.

    Args:
        key: The API key to test

    Raises:
        ValueError: If the key is invalid or the API call fails
    """
    client = anthropic.Anthropic(api_key=key)
    try:
        client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1,
            messages=[{"role": "user", "content": "Test"}],
        )
        print("✅ API key is valid")
    except Exception as e:
        raise ValueError(f"Invalid API key or API error: {str(e)}")


def main() -> NoReturn:
    """Main entry point for the API keyring utility."""
    parser = argparse.ArgumentParser(
        description="Manage API keys in the system keyring"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new API key")
    add_parser.add_argument("key_name", help="Name of the API key")
    add_parser.add_argument("key_value", help="Value of the API key")

    # View command
    view_parser = subparsers.add_parser("view", help="View an API key")
    view_parser.add_argument("key_name", help="Name of the API key to view")

    args = parser.parse_args()

    if args.command == "add":
        cred_manager = CredentialManager(args.key_name)
        cred_manager.save_credentials(args.key_name, args.key_value)
        print(f"✅ API key '{args.key_name}' saved successfully")
        
        # Test the key if it's an Anthropic key
        if args.key_name == "ANTHROPIC_API_KEY":
            try:
                test_anthropic_key(args.key_value)
            except ValueError as e:
                print(f"⚠️ Warning: {str(e)}")
                sys.exit(1)

    elif args.command == "view":
        cred_manager = CredentialManager(args.key_name)
        key_value = cred_manager.get_password(args.key_name)
        if key_value is None:
            print(f"❌ API key '{args.key_name}' not found")
            sys.exit(1)
        print(key_value)

    sys.exit(0)


if __name__ == "__main__":
    main() 