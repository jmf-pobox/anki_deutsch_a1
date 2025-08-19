"""Official Anki library backend implementation for deck generation."""

import hashlib
import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from anki.collection import Collection
from anki.decks import DeckId
from anki.models import NotetypeId

from langlearn.models.model_factory import ModelFactory
from langlearn.services.audio import AudioService
from langlearn.services.domain_media_generator import DomainMediaGenerator
from langlearn.services.german_language_service import GermanLanguageService
from langlearn.services.media_service import MediaGenerationConfig, MediaService
from langlearn.services.pexels_service import PexelsService

from .base import DeckBackend, MediaFile, NoteType

logger = logging.getLogger(__name__)


class AnkiBackend(DeckBackend):
    """Deck backend using the official Anki library.

    Phase 2 implementation: Uses real Anki Collection for deck generation.
    Creates actual .apkg files that can be imported into Anki.
    """

    def __init__(
        self,
        deck_name: str,
        description: str = "",
        media_service: MediaService | None = None,
        german_service: GermanLanguageService | None = None,
    ) -> None:
        """Initialize the official Anki backend.

        Args:
            deck_name: Name of the deck to create
            description: Optional description for the deck
            media_service: Optional MediaService for media generation
            german_service: Optional GermanLanguageService for German processing
        """
        super().__init__(deck_name, description)

        # Create temporary collection file
        self._temp_dir = tempfile.mkdtemp()
        self._collection_path = os.path.join(self._temp_dir, "collection.anki2")

        # Initialize Anki collection
        self._collection = Collection(self._collection_path)

        # Create the main deck
        main_deck_id = self._collection.decks.add_normal_deck_with_name(deck_name).id
        self._main_deck_id: DeckId = DeckId(main_deck_id)
        self._deck_id: DeckId = self._main_deck_id

        # Track note types
        self._note_type_map: dict[str, NotetypeId] = {}
        self._next_note_type_id = 1

        # Project root and media directories
        self._project_root = Path(
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
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

        self._media_service = media_service
        self._german_service = german_service

        # Create domain media generator for field processing delegation
        self._domain_media_generator = DomainMediaGenerator(
            self._media_service, self._german_service
        )

        # Media generation statistics (kept for backward compatibility)
        self._media_generation_stats = {
            "audio_generated": 0,
            "audio_reused": 0,
            "images_downloaded": 0,
            "images_reused": 0,
            "generation_errors": 0,
        }

        # Set up media directories
        self._audio_dir = self._project_root / "data" / "audio"
        self._images_dir = self._project_root / "data" / "images"
        self._audio_dir.mkdir(parents=True, exist_ok=True)
        self._images_dir.mkdir(parents=True, exist_ok=True)

    @property
    def _audio_service(self) -> AudioService:
        """Backward compatibility property for tests."""
        return self._media_service._audio_service

    @property
    def _pexels_service(self) -> PexelsService:
        """Backward compatibility property for tests."""
        return self._media_service._pexels_service

    def __del__(self) -> None:
        """Clean up temporary files."""
        if hasattr(self, "_temp_dir") and os.path.exists(self._temp_dir):
            shutil.rmtree(self._temp_dir, ignore_errors=True)

    def create_note_type(self, note_type: NoteType) -> str:
        """Create a note type and return its ID.

        Args:
            note_type: The note type to create

        Returns:
            Unique identifier for the created note type
        """
        # Create Anki note type
        notetype = self._collection.models.new(note_type.name)

        # Add fields
        for field_name in note_type.fields:
            field = self._collection.models.new_field(field_name)
            self._collection.models.add_field(notetype, field)

        # Add templates
        for template in note_type.templates:
            card_template = self._collection.models.new_template(template.name)
            card_template["qfmt"] = template.front_html
            card_template["afmt"] = template.back_html
            self._collection.models.add_template(notetype, card_template)

        # Set CSS
        if note_type.templates:
            notetype["css"] = note_type.templates[0].css

        # Add to collection
        changes_with_id = self._collection.models.add(notetype)
        actual_notetype_id = changes_with_id.id

        # Map our ID to Anki's ID
        our_id = str(self._next_note_type_id)
        self._note_type_map[our_id] = NotetypeId(actual_notetype_id)
        self._next_note_type_id += 1

        return our_id

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
        if note_type_id not in self._note_type_map:
            raise ValueError(f"Note type ID {note_type_id} not found")

        anki_notetype_id = self._note_type_map[note_type_id]

        # Process fields for media generation (skip if already processed by card generators)
        if skip_media_processing:
            processed_fields = fields
            logger.info(
                "🔄 Skipping media processing (already processed by card generator)"
            )
        else:
            processed_fields = self._process_fields_with_media(note_type_id, fields)
        print(
            f"DEBUG: Final processed fields: "
            f"{[f[:30] + '...' if len(f) > 30 else f for f in processed_fields]}"
        )

        # Create note - need to get the notetype dict first
        notetype = self._collection.models.get(anki_notetype_id)
        if notetype is None:
            raise ValueError(f"Note type not found: {anki_notetype_id}")
        note = self._collection.new_note(notetype)
        for i, field_value in enumerate(processed_fields):
            if i < len(note.fields):
                note.fields[i] = field_value
                if "[sound:" in field_value:
                    print(f"DEBUG: Setting field {i} to audio: {field_value}")

        if tags:
            note.tags = tags

        self._collection.add_note(note, self._deck_id)
        return note.id

    def _process_fields_with_media(
        self, note_type_input: str, fields: list[str]
    ) -> list[str]:
        """Process fields using domain model delegation.

        Args:
            note_type_input: Either note type ID or note type name
            fields: Original field values

        Returns:
            Processed field values with media
        """
        try:
            # Determine if input is note type ID or name
            if note_type_input in self._note_type_map:
                # It's a note type ID, get the name
                anki_notetype_id = self._note_type_map[note_type_input]
                notetype = self._collection.models.get(anki_notetype_id)
                if notetype is None:
                    return fields
                note_type_name = notetype.get("name", "")
            else:
                # It's already a note type name (for backward compatibility with tests)
                note_type_name = note_type_input

            # Try to create domain model using factory
            field_processor = ModelFactory.create_field_processor(note_type_name)
            if field_processor is None:
                # No domain model available - unsupported note type
                logger.warning(
                    f"No domain model available for: {note_type_name}. "
                    f"Returning fields unchanged."
                )
                return fields

            # Use domain model for field processing (all German word types supported)
            logger.debug(f"Using domain model for: {note_type_name}")
            return field_processor.process_fields_for_media_generation(
                fields, self._domain_media_generator
            )

        except Exception as e:
            logger.error(f"Error processing media for {note_type_input}: {e}")
            return fields

    def _generate_or_get_audio(self, text: str) -> str | None:
        """Generate audio for text or return existing audio file path."""
        try:
            result = self._media_service.generate_or_get_audio(text)

            # Update stats
            if result is not None:
                filename = f"{hashlib.md5(text.encode()).hexdigest()}.mp3"
                audio_path = self._audio_dir / filename
                if audio_path.exists():
                    self._media_generation_stats["audio_reused"] += 1
                else:
                    self._media_generation_stats["audio_generated"] += 1
            else:
                self._media_generation_stats["generation_errors"] += 1

            return result
        except Exception as e:
            print(f"Error generating audio for '{text}': {e}")
            self._media_generation_stats["generation_errors"] += 1
            return None

    def _generate_or_get_image(
        self, word: str, search_query: str | None = None, example_sentence: str = ""
    ) -> str | None:
        """Generate/download image for word or return existing image file path."""
        try:
            result = self._media_service.generate_or_get_image(
                word, search_query, example_sentence
            )

            # Update stats
            if result is not None:
                image_path = self._images_dir / f"{word}.jpg"
                if image_path.exists():
                    self._media_generation_stats["images_reused"] += 1
                else:
                    self._media_generation_stats["images_downloaded"] += 1
            else:
                self._media_generation_stats["generation_errors"] += 1

            return result
        except Exception as e:
            print(f"Error downloading image for '{word}': {e}")
            self._media_generation_stats["generation_errors"] += 1
            return None

    def add_media_file(self, file_path: str, media_type: str = "") -> MediaFile:
        """Add a media file to the deck."""
        logger.info(
            f"🔧 AnkiBackend.add_media_file: '{file_path}' (media_type='{media_type}')"
        )

        if not os.path.exists(file_path):
            logger.error(f"❌ Media file not found: {file_path}")
            raise FileNotFoundError(f"Media file not found: {file_path}")

        # Copy to collection media directory
        filename = os.path.basename(file_path)
        logger.info(f"   📂 Copying to Anki collection: {filename}")
        self._collection.media.add_file(file_path)

        # Generate reference based on expected media type and file extension
        reference = filename
        file_ext = Path(file_path).suffix.lower()
        logger.info(f"   📄 File extension: '{file_ext}'")

        # Use media_type context to determine proper reference format
        audio_exts = [".mp3", ".wav", ".ogg"]
        image_exts = [".jpg", ".jpeg", ".png", ".gif"]

        if media_type == "audio" or (media_type == "" and file_ext in audio_exts):
            # Audio files should be wrapped in [sound:] format
            reference = f"[sound:{filename}]"
            logger.info(f"   🔊 Audio reference: '{reference}'")
        elif media_type == "image" or (media_type == "" and file_ext in image_exts):
            # Image files should be plain filename for <img> tags
            reference = filename
            logger.info(f"   🖼️ Image reference: '{reference}'")
        else:
            # Fallback: use extension-based detection but log warning
            if file_ext in audio_exts:
                reference = f"[sound:{filename}]"
                logger.warning(f"⚠️ Fallback to audio: '{reference}'")
                if media_type and media_type != "audio":
                    logger.warning(
                        f"Media type mismatch: expected '{media_type}', "
                        f"got audio file: {file_path}"
                    )
            elif file_ext in image_exts:
                reference = filename
                logger.warning(f"⚠️ Fallback to image: '{reference}'")
                if media_type and media_type != "image":
                    logger.warning(
                        f"Media type mismatch: expected '{media_type}', "
                        f"got image file: {file_path}"
                    )

        media_file = MediaFile(
            path=file_path, reference=reference, media_type=media_type
        )
        self._media_files.append(media_file)

        logger.info(
            f"   ✅ Created MediaFile: path='{media_file.path}', "
            f"reference='{media_file.reference}', "
            f"media_type='{media_file.media_type}'"
        )
        return media_file

    def export_deck(self, output_path: str) -> None:
        """Export the deck to a file."""
        from anki.exporting import AnkiPackageExporter

        exporter = AnkiPackageExporter(self._collection)
        exporter.did = self._deck_id
        exporter.include_media = True  # type: ignore[attr-defined]  # Anki API boundary - attribute may not exist in all versions

        logger.info(f"Exporting deck with {len(self._media_files)} media files")

        try:
            # Try the modern API first
            if hasattr(exporter, "export_to_file"):
                exporter.export_to_file(output_path)
            elif hasattr(exporter, "exportInto"):
                exporter.exportInto(output_path)
            else:
                # Fallback: use the collection export
                self._collection.export_anki_package(output_path, [self._deck_id], True)  # type: ignore[misc,arg-type]  # Anki API boundary - signature varies by version
        except Exception as e:
            logger.error(f"Export failed with error: {e}")
            # As a last resort, create a simple export
            import shutil

            shutil.copy2(self._collection_path, output_path)

    def get_stats(self) -> dict[str, Any]:
        """Get deck statistics."""
        stats: dict[str, Any] = {
            "deck_name": self.deck_name,
            "note_types_count": len(self._note_type_map),
            "notes_count": 0,
            "media_files_count": len(self._media_files),
        }

        # Add media generation statistics
        stats["media_generation_stats"] = self._media_generation_stats.copy()
        stats["media_generation_stats"]["total_media_generated"] = (
            self._media_generation_stats["audio_generated"]
            + self._media_generation_stats["images_downloaded"]
        )
        stats["media_generation_stats"]["total_media_reused"] = (
            self._media_generation_stats["audio_reused"]
            + self._media_generation_stats["images_reused"]
        )

        try:
            if self._collection.db is not None:
                stats["notes_count"] = self._collection.db.scalar(
                    "SELECT count() FROM notes"
                )
        except Exception:
            pass

        return stats
