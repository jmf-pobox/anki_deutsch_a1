#!/usr/bin/env python

import argparse
import contextlib
import sys
from typing import NoReturn

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


def main() -> NoReturn:
    """Main entry point for the API keyring utility."""
    parser = argparse.ArgumentParser(
        description="Manage API keys in the system keyring"
    )
    subparsers = parser.add_subparsers(dest="command")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new API key")
    add_parser.add_argument("key_name", help="Name of the API key")
    add_parser.add_argument("key_value", help="Value of the API key")

    # View command
    view_parser = subparsers.add_parser("view", help="View an API key")
    view_parser.add_argument("key_name", help="Name of the API key to view")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete an API key")
    delete_parser.add_argument("key_name", help="Name of the API key to delete")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "add":
        cred_manager = CredentialManager(args.key_name)
        cred_manager.save_credentials(args.key_name, args.key_value)
        print(f"✅ API key '{args.key_name}' saved successfully")

    elif args.command == "view":
        cred_manager = CredentialManager(args.key_name)
        key_value = cred_manager.get_password(args.key_name)
        if key_value is None:
            print(f"❌ API key '{args.key_name}' not found")
            sys.exit(1)
        print(key_value)

    elif args.command == "delete":
        cred_manager = CredentialManager(args.key_name)
        key_value = cred_manager.get_password(args.key_name)
        if key_value is None:
            print(f"❌ API key '{args.key_name}' not found")
            sys.exit(1)

        cred_manager = CredentialManager(args.key_name)
        cred_manager.delete_credentials(args.key_name)
        print(f"✅ API key '{args.key_name}' deleted successfully")

    sys.exit(0)


if __name__ == "__main__":
    main()
