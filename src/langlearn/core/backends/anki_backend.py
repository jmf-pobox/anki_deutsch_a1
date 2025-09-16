"""Official Anki library backend implementation for deck generation."""

import hashlib
import logging
import os
import re
import shutil
import tempfile
import unicodedata
from pathlib import Path
from typing import Any

from anki.collection import Collection
from anki.decks import DeckId
from anki.models import NotetypeId

from langlearn.core.services.audio_service import AudioService
from langlearn.core.services.domain_media_generator import DomainMediaGenerator
from langlearn.core.services.image_service import PexelsService
from langlearn.core.services.media_service import MediaService
from langlearn.exceptions import (
    CardGenerationError,
    DataProcessingError,
    MediaGenerationError,
)
from langlearn.protocols.language_protocol import Language

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
        media_service: MediaService,
        language: Language,
        description: str = "",
    ) -> None:
        """Initialize the official Anki backend.

        Args:
            deck_name: Name of the deck to create
            media_service: Required MediaService for media generation
            language: Language implementation for domain model creation
            description: Optional description for the deck
        """
        super().__init__(deck_name, description)
        self._language = language

        # Create temporary collection file
        self._temp_dir = tempfile.mkdtemp()
        self._collection_path = os.path.join(self._temp_dir, "collection.anki2")

        # Initialize Anki collection
        self._collection = Collection(self._collection_path)

        # Create the main deck
        main_deck_id = self._collection.decks.add_normal_deck_with_name(deck_name).id
        self._main_deck_id: DeckId = DeckId(main_deck_id)
        self._deck_id: DeckId = self._main_deck_id

        # Track subdecks and current deck
        self._subdeck_map: dict[str, DeckId] = {}  # full_deck_name -> DeckId
        self._current_subdeck_name: str | None = None

        # Track note types
        self._note_type_map: dict[str, NotetypeId] = {}
        self._next_note_type_id = 1

        # Project root and media directories
        self._project_root = Path(
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        )

        # Store required media service
        self._media_service = media_service

        # Use MediaService's directories instead of legacy data/ paths
        self._audio_dir: Path = media_service._audio_dir
        self._images_dir: Path = media_service._images_dir

        # Create domain media generator for field processing delegation
        self._domain_media_generator = DomainMediaGenerator(self._media_service)

        # Create MediaEnricher for Clean Pipeline Architecture
        from langlearn.core.services import get_anthropic_service

        anthropic_service = get_anthropic_service()

        self._media_enricher = self._language.create_media_enricher(
            audio_service=self._media_service._audio_service,
            pexels_service=self._media_service._pexels_service,
            anthropic_service=anthropic_service,
            audio_base_path=self._audio_dir,
            image_base_path=self._images_dir,
        )

        # Media generation statistics (kept for backward compatibility)
        self._media_generation_stats = {
            "audio_generated": 0,
            "audio_reused": 0,
            "images_downloaded": 0,
            "images_reused": 0,
            "generation_errors": 0,
        }

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
        # FIXME: is this a typo?
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

    def create_subdeck(self, full_deck_name: str) -> DeckId:
        """Create a subdeck and return its ID.

        Args:
            full_deck_name: Full deck name with "::" separator (e.g., "Main::Nouns")

        Returns:
            DeckId of the created subdeck
        """
        if full_deck_name not in self._subdeck_map:
            subdeck_id = self._collection.decks.add_normal_deck_with_name(
                full_deck_name
            ).id
            self._subdeck_map[full_deck_name] = DeckId(subdeck_id)
            logger.info(f"Created subdeck: {full_deck_name}")

        return self._subdeck_map[full_deck_name]

    def set_current_subdeck(self, full_deck_name: str | None) -> None:
        """Set the current subdeck for note additions.

        Args:
            full_deck_name: Full deck name, or None for main deck
        """
        if full_deck_name is None:
            # Reset to main deck
            self._deck_id = self._main_deck_id
            self._current_subdeck_name = None
        else:
            # Create subdeck if it doesn't exist and switch to it
            subdeck_id = self.create_subdeck(full_deck_name)
            self._deck_id = subdeck_id
            self._current_subdeck_name = full_deck_name

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

        # Process fields for media generation
        # (skip if already processed by card generators)
        if skip_media_processing:
            processed_fields = fields
            logger.info(
                "🔄 Skipping media processing (already processed by card generator)"
            )
        else:
            processed_fields = self._process_fields_with_media(note_type_id, fields)

        # Create note - need to get the notetype dict first
        notetype = self._collection.models.get(anki_notetype_id)
        if notetype is None:
            raise ValueError(f"Note type not found: {anki_notetype_id}")
        note = self._collection.new_note(notetype)

        for i, field_value in enumerate(processed_fields):
            if i < len(note.fields):
                # Extract and add media files (only if not already processed)
                if not skip_media_processing:
                    processed_field_value = self._extract_and_add_media_from_html(
                        field_value
                    )
                else:
                    processed_field_value = field_value
                note.fields[i] = processed_field_value

                # LOG EXACT FIELD ASSIGNMENT FOR MEDIA FIELDS
                if any(
                    media_key in field_value
                    for media_key in ["<img", "[sound:", "audio", "image"]
                ):
                    logger.debug(f"Field[{i}] BEFORE processing: {field_value}")
                    logger.debug(
                        f"Field[{i}] AFTER processing: {processed_field_value}"
                    )
                    logger.debug(f"Field[{i}] ASSIGNED to note: {note.fields[i]}")

                if "[sound:" in field_value:
                    logger.debug(f"Setting field {i} to audio: {field_value}")

        if tags:
            note.tags = tags

        self._collection.add_note(note, self._deck_id)

        return int(note.id)

    def _process_fields_with_media(
        self, note_type_input: str, fields: list[str]
    ) -> list[str]:
        """Process fields using language-specific delegation.

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

            # Delegate all field processing to language-specific implementation
            return self._language.process_fields_for_anki(
                note_type_name, fields, self._media_enricher
            )

        except DataProcessingError:
            # Re-raise DataProcessingError without modification
            raise
        except Exception as e:
            logger.error(f"Error processing media for {note_type_input}: {e}")
            raise DataProcessingError(
                f"Media processing failed for note type {note_type_input}: {e}"
            ) from e

    def _generate_or_get_audio(self, text: str) -> str:
        """Generate audio for text or return existing audio file path."""
        try:
            result = self._media_service.generate_or_get_audio(text)

            # Update stats and validate result
            if result is not None:
                filename = f"{hashlib.md5(text.encode()).hexdigest()}.mp3"
                audio_path = self._audio_dir / filename
                if audio_path.exists():
                    self._media_generation_stats["audio_reused"] += 1
                else:
                    self._media_generation_stats["audio_generated"] += 1
                return result
            else:
                self._media_generation_stats["generation_errors"] += 1
                raise MediaGenerationError(f"Audio generation failed for '{text}'")
        except MediaGenerationError:
            # Re-raise MediaGenerationError without double-counting stats
            raise
        except Exception as e:
            logger.error(f"Error generating audio for '{text}': {e}")
            self._media_generation_stats["generation_errors"] += 1
            raise MediaGenerationError(
                f"Failed to generate audio for '{text}': {e}"
            ) from e

    def _generate_or_get_image(
        self, word: str, search_query: str | None = None, example_sentence: str = ""
    ) -> str:
        """Generate/download image for word or return existing image file path."""
        try:
            result = self._media_service.generate_or_get_image(
                word, search_query, example_sentence
            )

            # Update stats and validate result
            if result is not None:
                image_path = self._images_dir / f"{word}.jpg"
                if image_path.exists():
                    self._media_generation_stats["images_reused"] += 1
                else:
                    self._media_generation_stats["images_downloaded"] += 1
                return result
            else:
                self._media_generation_stats["generation_errors"] += 1
                raise MediaGenerationError(f"Image generation failed for '{word}'")
        except MediaGenerationError:
            # Re-raise MediaGenerationError without double-counting stats
            raise
        except Exception as e:
            logger.error(f"Error downloading image for '{word}': {e}")
            self._media_generation_stats["generation_errors"] += 1
            raise MediaGenerationError(
                f"Failed to generate image for '{word}': {e}"
            ) from e

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
        # Normalize filename to NFC form for consistent Unicode handling
        normalized_filename = unicodedata.normalize("NFC", filename)
        logger.info(f"   📂 Copying to Anki collection: {normalized_filename}")
        self._collection.media.add_file(file_path)

        # Generate reference based on media type
        if media_type == "audio":
            # Audio files (always .mp3) should be wrapped in [sound:] format
            reference = f"[sound:{filename}]"
            logger.info(f"   🔊 Audio reference: '{reference}'")
        elif media_type == "image":
            # Image files (always .png/.jpg) should be plain filename for <img> tags
            reference = filename
            logger.info(f"   🖼️ Image reference: '{reference}'")
        elif media_type == "":
            # Legacy support: infer from file extension
            file_ext = Path(file_path).suffix.lower()
            if file_ext == ".mp3":
                reference = f"[sound:{filename}]"
                logger.info(f"   🔊 Audio reference (inferred): '{reference}'")
            elif file_ext in [".jpg", ".jpeg", ".png"]:
                reference = filename
                logger.info(f"   🖼️ Image reference (inferred): '{reference}'")
            else:
                raise ValueError(
                    f"Cannot infer media type from extension: {file_ext} "
                    f"for file: {file_path}"
                )
        else:
            raise ValueError(
                f"Unknown media type: '{media_type}' for file: {file_path}"
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

    def _extract_and_add_media_from_html(self, html_content: str) -> str:
        """Extract media references from HTML and add files to collection.

        Args:
            html_content: HTML content that may contain <img> or [sound:] references

        Returns:
            Updated HTML content with verified media references
        """
        if not html_content:
            return html_content

        # Extract image references from <img src="filename">
        img_pattern = r'<img\s+src="([^"]+)"[^>]*>'
        img_matches = re.findall(img_pattern, html_content, re.IGNORECASE)

        for img_filename in img_matches:
            # Try to find the image file in the images directory
            image_path = Path("data/images") / img_filename
            if image_path.exists():
                try:
                    logger.info(f"   🖼️ Adding image from HTML: {img_filename}")
                    self.add_media_file(str(image_path), "image")
                except Exception as e:
                    logger.warning(f"   ⚠️ Failed to add image {img_filename}: {e}")
            else:
                logger.warning(f"   ⚠️ Image file not found: {image_path}")

        # Extract audio references from [sound:filename]
        sound_pattern = r"\[sound:([^\]]+)\]"
        sound_matches = re.findall(sound_pattern, html_content)

        for audio_filename in sound_matches:
            # Try to find the audio file in the audio directory
            audio_path = Path("data/audio") / audio_filename
            if audio_path.exists():
                try:
                    logger.info(f"   🔊 Adding audio from HTML: {audio_filename}")
                    self.add_media_file(str(audio_path), "audio")
                except Exception as e:
                    logger.warning(f"   ⚠️ Failed to add audio {audio_filename}: {e}")
            else:
                logger.warning(f"   ⚠️ Audio file not found: {audio_path}")

        return html_content

    def export_deck(self, output_path: str) -> None:
        """Export the deck to a file."""
        from anki.exporting import AnkiPackageExporter

        exporter = AnkiPackageExporter(self._collection)
        exporter.did = self._deck_id
        # Set include_media if the attribute exists (varies by Anki version)
        if hasattr(exporter, "include_media"):
            exporter.include_media = True

        logger.info(f"Exporting deck with {len(self._media_files)} media files")

        try:
            # Try the modern API first
            if hasattr(exporter, "export_to_file"):
                exporter.export_to_file(output_path)
            elif hasattr(exporter, "exportInto"):
                exporter.exportInto(output_path)
            else:
                # No supported export method found
                raise CardGenerationError(
                    "No supported export method found on AnkiPackageExporter"
                )
        except CardGenerationError:
            # Re-raise CardGenerationError
            raise
        except Exception as e:
            logger.error(f"Export failed with error: {e}")
            raise CardGenerationError(f"Failed to export deck: {e}") from e

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
        except OSError as e:
            logger.warning(f"Database file access error when counting notes: {e}")
            stats["notes_count"] = 0
        except Exception as e:
            logger.error(f"Database query failed when counting notes: {e}")
            # Don't raise here - stats collection is non-critical
            stats["notes_count"] = 0

        return stats
