#!/usr/bin/env python


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
        try:
            keyring.delete_password(self._app_name, username)
        except PasswordDeleteError:
            # Password didn't exist or couldn't be deleted
            pass


# Usage example
def main() -> None:
    # Load environment variables from .env file
    # load_dotenv()
    # key: str = "PEXELS_API_KEY"
    # key_value: str | None = os.environ.get(key)
    # if key_value is None:
    #     raise ValueError(f"Key {key} not found in environment variables")

    # Get the key from the environment variables
    key: str = "PEXELS_API_KEY"
    key_value: str = "Egjgpz6iR3C1hoktNXzTS4Tuy6HJU16sHNAR212eM6hnoYjIy5aKmIoY"

    # Create a credential manager for your application
    cred_manager = CredentialManager(key)
    # Store the value of the key
    cred_manager.save_credentials(key, key_value)

    # Retrieve the key
    stored_key = cred_manager.get_password(key)
    print(f"Retrieved key: {stored_key}")

    # When no longer needed, delete the credentials
    # cred_manager.delete_credentials(key)


if __name__ == "__main__":
    main()
