"""Deck organization and management functionality.

The DeckManager handles higher-level deck organization patterns including
subdeck creation, deck naming conventions, and deck hierarchy management.
It composes with DeckBackend instances to provide orchestration without
coupling to specific backend implementations.
"""

from typing import Any

from ..backends.base import DeckBackend, NoteType


class DeckManager:
    """Manages deck organization including subdeck creation and naming patterns.

    The DeckManager provides a higher-level interface for organizing decks
    while delegating core deck operations to the underlying DeckBackend.
    It handles Anki-specific subdeck naming (using "::" separators) and
    maintains the current context for card additions.
    """

    def __init__(self, backend: DeckBackend) -> None:
        """Initialize DeckManager with a backend.

        Args:
            backend: The DeckBackend instance to use for deck operations
        """
        self._backend = backend
        self._current_subdeck: str | None = None
        self._subdecks: dict[str, str] = {}  # subdeck_name -> full_deck_name

    @property
    def backend(self) -> DeckBackend:
        """Get the underlying deck backend."""
        return self._backend

    @property
    def deck_name(self) -> str:
        """Get the base deck name."""
        return self._backend.deck_name

    def set_current_subdeck(self, subdeck_name: str) -> None:
        """Set the current subdeck for subsequent card additions.

        Uses Anki's "::" naming convention for subdeck hierarchy.
        For example, if the main deck is "German A1" and subdeck is "Adjectives",
        the full name becomes "German A1::Adjectives".

        Args:
            subdeck_name: Name of the subdeck (e.g., "Adjectives")
        """
        self._current_subdeck = subdeck_name
        full_deck_name = f"{self._backend.deck_name}::{subdeck_name}"
        self._subdecks[subdeck_name] = full_deck_name

    def get_current_deck_name(self) -> str:
        """Get the current active deck name (including subdeck if set).

        Returns:
            Full deck name including subdeck hierarchy
        """
        if self._current_subdeck:
            return self._subdecks[self._current_subdeck]
        return self._backend.deck_name

    def get_subdeck_names(self) -> list[str]:
        """Get list of all created subdeck names.

        Returns:
            List of subdeck names (not including full paths)
        """
        return list(self._subdecks.keys())

    def get_full_subdeck_names(self) -> list[str]:
        """Get list of all full subdeck names with hierarchy.

        Returns:
            List of full deck names including "::" separators
        """
        return list(self._subdecks.values())

    def reset_to_main_deck(self) -> None:
        """Reset the current context to the main deck (no subdeck)."""
        self._current_subdeck = None

    # Delegate core deck operations to backend

    def create_note_type(self, note_type: NoteType) -> str:
        """Create a note type using the backend.

        Args:
            note_type: The note type to create

        Returns:
            Unique identifier for the created note type
        """
        return self._backend.create_note_type(note_type)

    def add_note(
        self,
        note_type_id: str,
        fields: list[str],
        tags: list[str] | None = None,
    ) -> int:
        """Add a note to the current deck/subdeck.

        Args:
            note_type_id: ID of the note type to use
            fields: List of field values for the note
            tags: Optional list of tags for the note

        Returns:
            The note ID
        """
        # Add current subdeck as a tag if we're in a subdeck
        note_tags = tags or []
        if self._current_subdeck:
            note_tags = note_tags + [f"subdeck:{self._current_subdeck}"]

        return self._backend.add_note(note_type_id, fields, note_tags)

    def export_deck(self, output_path: str) -> None:
        """Export the deck to a file.

        Args:
            output_path: Path where the deck should be saved
        """
        self._backend.export_deck(output_path)

    def get_stats(self) -> dict[str, Any]:
        """Get deck statistics including subdeck information.

        Returns:
            Dictionary containing deck statistics
        """
        stats = self._backend.get_stats()

        # Add subdeck information
        stats["subdecks"] = {
            "count": len(self._subdecks),
            "names": self.get_subdeck_names(),
            "full_names": self.get_full_subdeck_names(),
            "current": self._current_subdeck,
        }

        return stats
