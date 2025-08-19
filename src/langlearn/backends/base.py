"""Abstract base classes for deck generation backends.

This module defines the minimal interface for deck backends, following the
principle of keeping interfaces small and focused. The DeckBackend interface
handles only core deck operations:

- Note type creation and management
- Note addition with fields and tags
- Media file handling
- Deck export to file format
- Statistics reporting

Higher-level functionality like media processing, German language features,
and template management is handled by service classes that compose with
deck backends rather than extending them.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, TypeVar

T = TypeVar("T")


@dataclass
class MediaFile:
    """Represents a media file for inclusion in an Anki deck."""

    path: str
    """Path to the media file on disk."""

    reference: str
    """Reference string to use in card content (e.g., 'audio.mp3')."""

    media_type: str = ""
    """Type of media: 'audio', 'image', or '' for automatic detection."""


@dataclass
class CardTemplate:
    """Represents a card template with front/back HTML and CSS."""

    name: str
    """Name of the card template."""

    front_html: str
    """HTML template for the front of the card."""

    back_html: str
    """HTML template for the back of the card."""

    css: str = ""
    """CSS styling for the card."""


@dataclass
class NoteType:
    """Represents a note type (model) with fields and templates."""

    name: str
    """Name of the note type."""

    fields: list[str]
    """List of field names for this note type."""

    templates: list[CardTemplate]
    """List of card templates for this note type."""


class DeckBackend(ABC):
    """Abstract base class for deck generation backends."""

    def __init__(self, deck_name: str, description: str = "") -> None:
        """Initialize the deck backend.

        Args:
            deck_name: Name of the deck to create
            description: Optional description for the deck
        """
        self.deck_name = deck_name
        self.description = description
        self._media_files: list[MediaFile] = []

    @abstractmethod
    def create_note_type(self, note_type: NoteType) -> str:
        """Create a note type and return its ID.

        Args:
            note_type: The note type to create

        Returns:
            Unique identifier for the created note type
        """

    @abstractmethod
    def add_note(
        self,
        note_type_id: str,
        fields: list[str],
        tags: list[str] | None = None,
        skip_media_processing: bool = False,
    ) -> int:
        """Add a note to the deck.

        Args:
            note_type_id: ID of the note type to use
            fields: List of field values for the note
            tags: Optional list of tags for the note
            skip_media_processing: Skip media processing if fields are already processed

        Returns:
            The note ID
        """

    @abstractmethod
    def add_media_file(self, file_path: str, media_type: str = "") -> MediaFile:
        """Add a media file to the deck.

        Args:
            file_path: Path to the media file
            media_type: Expected media type ('audio', 'image', or '' for auto-detect)

        Returns:
            MediaFile object with reference information
        """

    @abstractmethod
    def export_deck(self, output_path: str) -> None:
        """Export the deck to a file.

        Args:
            output_path: Path where the deck should be saved
        """

    @abstractmethod
    def get_stats(self) -> dict[str, Any]:
        """Get deck statistics.

        Returns:
            Dictionary containing deck statistics like note counts, media files, etc.
        """

    def get_media_files(self) -> list[MediaFile]:
        """Get all media files added to the deck.

        Returns:
            List of MediaFile objects
        """
        return self._media_files.copy()
