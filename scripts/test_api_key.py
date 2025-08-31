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
    # Create a credential manager for your application
    key: str = "ANTHROPIC_API_KEY"
    cred_manager = CredentialManager(key)

    # Retrieve the key
    stored_key = cred_manager.get_password(key)
    print(stored_key)
    if stored_key is None:
        raise ValueError(f"Key {key} not found in system keyring")

    client = anthropic.Anthropic(
        api_key=stored_key,
    )
    message = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=1024,
        messages=[{"role": "user", "content": "Hello, Claude"}],
    )
    print(message.content)


if __name__ == "__main__":
    main()
