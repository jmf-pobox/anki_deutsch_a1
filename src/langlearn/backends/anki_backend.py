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
from langlearn.models.records import create_record
from langlearn.protocols import MediaServiceProtocol
from langlearn.services.audio import AudioService
from langlearn.services.domain_media_generator import DomainMediaGenerator
from langlearn.services.media_enricher import StandardMediaEnricher
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
        media_service: MediaServiceProtocol | None = None,
    ) -> None:
        """Initialize the official Anki backend.

        Args:
            deck_name: Name of the deck to create
            description: Optional description for the deck
            media_service: Optional MediaServiceProtocol for media generation
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

        # Initialize services with dependency injection
        if media_service is None:
            from typing import cast

            audio_service = AudioService(
                output_dir=str(self._project_root / "data" / "audio")
            )
            pexels_service = PexelsService()
            config = MediaGenerationConfig()
            media_service = cast(
                "MediaServiceProtocol",
                MediaService(audio_service, pexels_service, config, self._project_root),
            )

        self._media_service = media_service

        # Create domain media generator for field processing delegation
        # Only create if we have a concrete MediaService (not just protocol)
        self._domain_media_generator: DomainMediaGenerator | None = None
        if isinstance(self._media_service, MediaService):
            self._domain_media_generator = DomainMediaGenerator(self._media_service)

        # Create MediaEnricher for Clean Pipeline Architecture
        self._media_enricher = StandardMediaEnricher(
            self._media_service,
            audio_base_path=self._project_root / "data" / "audio",
            image_base_path=self._project_root / "data" / "images",
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
        if not isinstance(self._media_service, MediaService):
            raise ValueError("MediaService must be available for audio operations")
        return self._media_service._audio_service

    @property
    def _pexels_service(self) -> PexelsService:
        """Backward compatibility property for tests."""
        if not isinstance(self._media_service, MediaService):
            raise ValueError("MediaService must be available for image operations")
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

            # Map note type name to record type for Clean Pipeline Architecture
            note_type_to_record_type = {
                "German Noun": "noun",
                "German Noun with Media": "noun",
                "German Adjective": "adjective",
                "German Adjective with Media": "adjective",
                "German Adverb": "adverb",
                "German Adverb with Media": "adverb",
                "German Negation": "negation",
                "German Negation with Media": "negation",
                "German Verb": "verb",
                "German Verb with Media": "verb",
            }

            # Check if we support this note type with new architecture
            record_type = None
            for note_pattern, rec_type in note_type_to_record_type.items():
                if note_pattern.lower() in note_type_name.lower():
                    record_type = rec_type
                    break

            if record_type is not None:
                # Use Clean Pipeline Architecture
                logger.debug(f"Using Clean Pipeline Architecture for: {note_type_name}")
                try:
                    # Create record from fields
                    record = create_record(record_type, fields)

                    # Create domain model for business logic validation
                    domain_model = self._create_domain_model_from_record(
                        record, record_type
                    )

                    # Enrich record using MediaEnricher
                    enriched_record_dict = self._media_enricher.enrich_record(
                        record.to_dict(), domain_model
                    )

                    # Convert back to field list format for backward compatibility
                    # The specific field order depends on the record type
                    if record_type == "noun":
                        return [
                            enriched_record_dict["noun"],
                            enriched_record_dict["article"],
                            enriched_record_dict["english"],
                            enriched_record_dict["plural"],
                            enriched_record_dict["example"],
                            enriched_record_dict["related"],
                            enriched_record_dict.get("image", ""),
                            enriched_record_dict.get("word_audio", ""),
                            enriched_record_dict.get("example_audio", ""),
                        ]
                    elif record_type == "adjective":
                        return [
                            enriched_record_dict["word"],
                            enriched_record_dict["english"],
                            enriched_record_dict["example"],
                            enriched_record_dict["comparative"],
                            enriched_record_dict["superlative"],
                            enriched_record_dict.get("image", ""),
                            enriched_record_dict.get("word_audio", ""),
                            enriched_record_dict.get("example_audio", ""),
                        ]
                    elif record_type in ["adverb", "negation"]:
                        return [
                            enriched_record_dict["word"],
                            enriched_record_dict["english"],
                            enriched_record_dict["type"],
                            enriched_record_dict["example"],
                            enriched_record_dict.get("image", ""),
                            enriched_record_dict.get("word_audio", ""),
                            enriched_record_dict.get("example_audio", ""),
                        ]

                except Exception as record_error:
                    logger.warning(
                        f"Clean Pipeline Architecture failed for {note_type_name}: "
                        f"{record_error}"
                    )
                    # Fall back to old approach for backward compatibility

            # Fall back to old FieldProcessor approach for unsupported types or failures
            field_processor = ModelFactory.create_field_processor(note_type_name)
            if field_processor is not None and hasattr(
                field_processor, "process_fields_for_media_generation"
            ):
                logger.debug(f"Using legacy FieldProcessor for: {note_type_name}")
                if self._domain_media_generator is None:
                    logger.warning(
                        "No domain media generator available for FieldProcessor"
                    )
                    return fields
                return field_processor.process_fields_for_media_generation(
                    fields, self._domain_media_generator
                )
            else:
                # No processing available - unsupported note type
                logger.warning(
                    f"No processing available for: {note_type_name}. "
                    f"Returning fields unchanged."
                )
                return fields

        except Exception as e:
            logger.error(f"Error processing media for {note_type_input}: {e}")
            return fields

    def _create_domain_model_from_record(self, record: Any, record_type: str) -> Any:
        """Create domain model instance from record data."""
        from langlearn.models.adjective import Adjective
        from langlearn.models.adverb import Adverb, AdverbType
        from langlearn.models.negation import Negation, NegationType
        from langlearn.models.noun import Noun
        from langlearn.models.verb import Verb

        if record_type == "noun":
            return Noun(
                noun=record.noun,
                article=record.article,
                english=record.english,
                plural=record.plural,
                example=record.example,
                related=record.related,
            )
        elif record_type == "adjective":
            return Adjective(
                word=record.word,
                english=record.english,
                example=record.example,
                comparative=record.comparative,
                superlative=record.superlative,
            )
        elif record_type == "adverb":
            return Adverb(
                word=record.word,
                english=record.english,
                type=AdverbType(record.type),
                example=record.example,
            )
        elif record_type == "negation":
            return Negation(
                word=record.word,
                english=record.english,
                type=NegationType(record.type),
                example=record.example,
            )
        elif record_type == "verb":
            return Verb(
                verb=record.verb,
                english=record.english,
                present_ich=record.present_ich,
                present_du=record.present_du,
                present_er=record.present_er,
                perfect=record.perfect,
                example=record.example,
            )
        else:
            raise ValueError(f"Unsupported record type: {record_type}")

    def _generate_or_get_audio(self, text: str) -> str | None:
        """Generate audio for text or return existing audio file path."""
        try:
            # Check if media service is available - using getattr to avoid
            # flow analysis issues
            media_service: MediaServiceProtocol | None = getattr(
                self, "_media_service", None
            )
            if media_service is None:
                return None
            result = media_service.generate_or_get_audio(text)

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
            # Check if media service is available - using getattr to avoid
            # flow analysis issues
            media_service: MediaServiceProtocol | None = getattr(
                self, "_media_service", None
            )
            if media_service is None:
                return None
            result = media_service.generate_or_get_image(
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
