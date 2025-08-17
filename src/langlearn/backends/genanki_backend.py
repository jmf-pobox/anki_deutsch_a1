"""Genanki backend implementation for deck generation."""

import os
import random
import shutil
import tempfile
from typing import TYPE_CHECKING

import genanki  # type: ignore

from .base import CardTemplate, DeckBackend, MediaFile, NoteType

if TYPE_CHECKING:
    from genanki import Deck, Model


class GenankiBackend(DeckBackend):
    """Deck backend using the genanki library."""

    def __init__(self, deck_name: str, description: str = "") -> None:
        """Initialize the genanki backend.

        Args:
            deck_name: Name of the deck to create
            description: Optional description for the deck
        """
        super().__init__(deck_name, description)

        # Create unique deck ID
        self._deck_id = random.randrange(1 << 30, 1 << 31)

        # Create the deck
        self._deck: "Deck" = genanki.Deck(self._deck_id, deck_name, description)

        # Track note types and their genanki models
        self._note_types: dict[str, "Model"] = {}

        # Create temporary directory for media files
        self._media_dir = tempfile.mkdtemp()

    def __del__(self) -> None:
        """Clean up temporary directory."""
        if hasattr(self, "_media_dir"):
            shutil.rmtree(self._media_dir, ignore_errors=True)

    def create_note_type(self, note_type: NoteType) -> str:
        """Create a genanki note type and return its ID.

        Args:
            note_type: The note type to create

        Returns:
            String ID of the created note type
        """
        # Generate unique model ID
        model_id = random.randrange(1 << 30, 1 << 31)

        # Convert fields to genanki format
        genanki_fields = [{"name": field} for field in note_type.fields]

        # Convert templates to genanki format
        genanki_templates = []
        for template in note_type.templates:
            genanki_templates.append(
                {
                    "name": template.name,
                    "qfmt": template.front_html,
                    "afmt": template.back_html,
                }
            )

        # Create genanki model
        model = genanki.Model(
            model_id,
            note_type.name,
            fields=genanki_fields,
            templates=genanki_templates,
            css=note_type.templates[0].css if note_type.templates else "",
        )

        # Store the model
        note_type_id = str(model_id)
        self._note_types[note_type_id] = model

        return note_type_id

    def add_note(
        self,
        note_type_id: str,
        fields: list[str],
        tags: list[str] | None = None,
    ) -> None:
        """Add a note to the deck.

        Args:
            note_type_id: ID of the note type to use
            fields: List of field values for the note
            tags: Optional list of tags for the note (not used in genanki)
        """
        if note_type_id not in self._note_types:
            raise ValueError(f"Note type ID {note_type_id} not found")

        model = self._note_types[note_type_id]
        note = genanki.Note(model=model, fields=fields)

        self._deck.add_note(note)

    def add_media_file(self, file_path: str) -> MediaFile:
        """Add a media file to the deck.

        Args:
            file_path: Path to the media file

        Returns:
            MediaFile object with reference information
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Media file not found: {file_path}")

        # Get filename for reference
        filename = os.path.basename(file_path)

        # Copy file to media directory
        dest_path = os.path.join(self._media_dir, filename)
        shutil.copy2(file_path, dest_path)

        # Create MediaFile object
        media_file = MediaFile(path=dest_path, reference=filename)
        self._media_files.append(media_file)

        return media_file

    def export_deck(self, output_path: str) -> None:
        """Export the deck to an .apkg file.

        Args:
            output_path: Path where the deck should be saved
        """
        # Create genanki package
        package = genanki.Package(self._deck)

        # Add media files
        media_file_paths = [media.path for media in self._media_files]
        package.media_files = media_file_paths

        # Export the package
        package.write_to_file(output_path)
