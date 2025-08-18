"""Genanki backend implementation for deck generation."""

import logging
import os
import random
import shutil
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any

import genanki  # type: ignore

from langlearn.models.model_factory import ModelFactory
from langlearn.services.audio import AudioService
from langlearn.services.domain_media_generator import DomainMediaGenerator
from langlearn.services.german_language_service import GermanLanguageService
from langlearn.services.media_service import MediaGenerationConfig, MediaService
from langlearn.services.pexels_service import PexelsService

from .base import DeckBackend, MediaFile, NoteType

if TYPE_CHECKING:
    from genanki import Deck, Model

logger = logging.getLogger(__name__)


class GenankiBackend(DeckBackend):
    """Deck backend using the genanki library."""

    def __init__(
        self,
        deck_name: str,
        description: str = "",
        media_service: MediaService | None = None,
        german_service: GermanLanguageService | None = None,
        enable_field_processing: bool = False,
    ) -> None:
        """Initialize the genanki backend.

        Args:
            deck_name: Name of the deck to create
            description: Optional description for the deck
            media_service: Optional MediaService for media generation
            german_service: Optional GermanLanguageService for German processing
            enable_field_processing: Whether to enable field processing (default: False)
        """
        super().__init__(deck_name, description)

        # Create unique deck ID
        self._deck_id = random.randrange(1 << 30, 1 << 31)

        # Create the deck
        self._deck: Deck = genanki.Deck(self._deck_id, deck_name, description)

        # Track note types and their genanki models
        self._note_types: dict[str, Model] = {}

        # Create temporary directory for media files
        self._media_dir = tempfile.mkdtemp()

        # Optional field processing setup
        self._enable_field_processing = enable_field_processing
        self._domain_media_generator = None

        if enable_field_processing:
            # Project root for media directories
            self._project_root = Path(
                os.path.abspath(
                    os.path.join(os.path.dirname(__file__), "..", "..", "..")
                )
            )

            # Initialize services with dependency injection
            if media_service is None:
                audio_service = AudioService(output_dir="data/audio")
                pexels_service = PexelsService()
                config = MediaGenerationConfig()
                media_service = MediaService(
                    audio_service, pexels_service, config, self._project_root
                )

            if german_service is None:
                german_service = GermanLanguageService()

            # Create domain media generator for field processing delegation
            self._domain_media_generator = DomainMediaGenerator(
                media_service, german_service
            )

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
    ) -> int:
        """Add a note to the deck.

        Args:
            note_type_id: ID of the note type to use
            fields: List of field values for the note
            tags: Optional list of tags for the note (not used in genanki)

        Returns:
            The note ID (generated)
        """
        if note_type_id not in self._note_types:
            raise ValueError(f"Note type ID {note_type_id} not found")

        model = self._note_types[note_type_id]

        # Process fields if field processing is enabled
        processed_fields = fields
        if self._enable_field_processing and self._domain_media_generator:
            processed_fields = self._process_fields_with_media(note_type_id, fields)

        note = genanki.Note(model=model, fields=processed_fields)
        self._deck.add_note(note)

        # Generate a simple note ID for genanki compatibility
        return len(self._deck.notes)

    def _process_fields_with_media(
        self, note_type_id: str, fields: list[str]
    ) -> list[str]:
        """Process fields using domain model delegation.

        This method provides the same field processing capabilities as AnkiBackend
        to ensure consistent behavior between backends.

        Args:
            note_type_id: ID of the note type to process
            fields: Original field values

        Returns:
            Processed field values with media
        """
        try:
            # For GenanKiBackend, note_type_id is typically the note type name
            # Try to create domain model using factory
            field_processor = ModelFactory.create_field_processor(note_type_id)
            if field_processor is None:
                # No domain model available - return fields unchanged
                logger.debug(f"No domain model available for: {note_type_id}")
                return fields

            # Use domain model for field processing
            logger.debug(f"Using domain model for: {note_type_id}")
            # Type assertion: we know _domain_media_generator is not None here
            # because _enable_field_processing is True and we initialize it
            assert self._domain_media_generator is not None
            return field_processor.process_fields_for_media_generation(
                fields, self._domain_media_generator
            )

        except Exception as e:
            logger.error(f"Error processing media for {note_type_id}: {e}")
            return fields

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

        # Create MediaFile object with proper reference format
        reference = filename
        if filename.endswith((".mp3", ".wav", ".ogg")):
            reference = f"[sound:{filename}]"

        media_file = MediaFile(path=dest_path, reference=reference)
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

    def get_stats(self) -> dict[str, Any]:
        """Get deck statistics.

        Returns:
            Dictionary containing deck statistics
        """
        return {
            "deck_name": self.deck_name,
            "note_types_count": len(self._note_types),
            "notes_count": len(self._deck.notes),
            "media_files_count": len(self._media_files),
        }
