"""Official Anki library backend implementation for deck generation."""

import hashlib
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from anki.collection import Collection
from anki.decks import DeckId
from anki.models import NotetypeId

from ..models.adjective import Adjective
from ..models.noun import Noun
from ..services.audio import AudioService
from ..services.german_language_service import GermanLanguageService
from ..services.media_service import MediaGenerationConfig, MediaService
from ..services.pexels_service import PexelsService
from .base import DeckBackend, MediaFile, NoteType


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
    ) -> int:
        """Add a note to the deck.

        Args:
            note_type_id: ID of the note type to use
            fields: List of field values for the note
            tags: Optional list of tags for the note

        Returns:
            The note ID
        """
        if note_type_id not in self._note_type_map:
            raise ValueError(f"Note type ID {note_type_id} not found")

        anki_notetype_id = self._note_type_map[note_type_id]

        # Process fields for media generation
        processed_fields = self._process_fields_with_media(note_type_id, fields)

        # Create note
        note = self._collection.new_note(anki_notetype_id)
        for i, field_value in enumerate(processed_fields):
            if i < len(note.fields):
                note.fields[i] = field_value

        if tags:
            note.tags = tags

        self._collection.add_note(note, self._deck_id)
        return note.id

    def _process_fields_with_media(
        self, note_type_input: str, fields: list[str]
    ) -> list[str]:
        """Process fields to add media generation.

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
                note_type_name = notetype.get("name", "")
            else:
                # It's already a note type name (for backward compatibility with tests)
                note_type_name = note_type_input

            # Create a copy to modify
            processed_fields = fields.copy()

            # Process based on note type
            if "adjective" in note_type_name.lower() and len(fields) >= 8:
                processed_fields = self._process_adjective_fields(processed_fields)
            elif "noun" in note_type_name.lower() and len(fields) >= 9:
                processed_fields = self._process_noun_fields(processed_fields)
            elif "verb" in note_type_name.lower() and len(fields) >= 8:
                processed_fields = self._process_verb_fields(processed_fields)
            elif "preposition" in note_type_name.lower() and len(fields) >= 7:
                processed_fields = self._process_preposition_fields(processed_fields)
            elif "phrase" in note_type_name.lower() and len(fields) >= 5:
                processed_fields = self._process_phrase_fields(processed_fields)

            return processed_fields

        except Exception as e:
            print(f"Error processing media: {e}")
            return fields

    def _process_adjective_fields(self, fields: list[str]) -> list[str]:
        """Process adjective fields with combined audio and image generation."""
        try:
            # Fields: [Word, English, Example, Comparative, Superlative, Image, WordAudio, ExampleAudio]
            word = fields[0]
            english = fields[1]
            example = fields[2]
            comparative = fields[3]
            superlative = fields[4]

            # Generate combined audio for adjective forms
            adjective = Adjective(
                word=word,
                english=english,
                example=example,
                comparative=comparative,
                superlative=superlative,
            )
            combined_text = self._german_service.get_combined_adjective_audio_text(
                adjective
            )

            combined_audio_path = self._generate_or_get_audio(combined_text)
            if combined_audio_path:
                fields[6] = f"[sound:{os.path.basename(combined_audio_path)}]"

            # Generate example audio
            example_audio_path = self._generate_or_get_audio(example)
            if example_audio_path:
                fields[7] = f"[sound:{os.path.basename(example_audio_path)}]"

            # Generate image
            context_query = self._german_service.extract_context_from_sentence(
                example, word, english
            )
            image_path = self._generate_or_get_image(word, context_query, example)
            if image_path:
                fields[5] = f'<img src="{os.path.basename(image_path)}">'

            return fields
        except Exception as e:
            print(f"Error processing adjective fields: {e}")
            return fields

    def _process_noun_fields(self, fields: list[str]) -> list[str]:
        """Process noun fields with combined audio generation."""
        try:
            # Fields: [Noun, Article, English, Plural, Example, Related, Image, WordAudio, ExampleAudio]
            noun = fields[0]
            article = fields[1]
            plural = fields[3]
            example = fields[4]

            # Generate combined audio for noun
            noun_obj = Noun(
                noun=noun,
                article=article,
                english=fields[2],
                plural=plural,
                example=example,
                related=fields[5] if len(fields) > 5 else "",
            )
            combined_text = self._german_service.get_combined_noun_audio_text(noun_obj)

            combined_audio_path = self._generate_or_get_audio(combined_text)
            if combined_audio_path:
                fields[7] = f"[sound:{os.path.basename(combined_audio_path)}]"

            # Generate example audio
            example_audio_path = self._generate_or_get_audio(example)
            if example_audio_path:
                fields[8] = f"[sound:{os.path.basename(example_audio_path)}]"

            return fields
        except Exception as e:
            print(f"Error processing noun fields: {e}")
            return fields

    def _process_verb_fields(self, fields: list[str]) -> list[str]:
        """Process verb fields with audio generation."""
        try:
            # Fields: [Verb, English, ich_form, du_form, er_form, perfect, Example, ExampleAudio]
            example = fields[6] if len(fields) > 6 else ""

            # Generate example audio
            if example:
                example_audio_path = self._generate_or_get_audio(example)
                if example_audio_path and len(fields) > 7:
                    fields[7] = f"[sound:{os.path.basename(example_audio_path)}]"

            return fields
        except Exception as e:
            print(f"Error processing verb fields: {e}")
            return fields

    def _process_preposition_fields(self, fields: list[str]) -> list[str]:
        """Process preposition fields with audio generation."""
        try:
            # Fields: [Preposition, Case, English, Example1, Example2, Audio1, Audio2]
            example1 = fields[3] if len(fields) > 3 else ""
            example2 = fields[4] if len(fields) > 4 else ""

            # Generate audio for both examples
            if example1:
                audio1_path = self._generate_or_get_audio(example1)
                if audio1_path and len(fields) > 5:
                    fields[5] = f"[sound:{os.path.basename(audio1_path)}]"

            if example2:
                audio2_path = self._generate_or_get_audio(example2)
                if audio2_path and len(fields) > 6:
                    fields[6] = f"[sound:{os.path.basename(audio2_path)}]"

            return fields
        except Exception as e:
            print(f"Error processing preposition fields: {e}")
            return fields

    def _process_phrase_fields(self, fields: list[str]) -> list[str]:
        """Process phrase fields with audio generation."""
        try:
            # Fields: [Phrase, English, Context, Related, PhraseAudio]
            phrase = fields[0] if len(fields) > 0 else ""

            # Generate phrase audio
            if phrase:
                phrase_audio_path = self._generate_or_get_audio(phrase)
                if phrase_audio_path and len(fields) > 4:
                    fields[4] = f"[sound:{os.path.basename(phrase_audio_path)}]"

            return fields
        except Exception as e:
            print(f"Error processing phrase fields: {e}")
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

    def _is_concrete_noun(self, noun: str) -> bool:
        """Basic heuristic to determine if a noun represents a concrete object.

        Delegates to GermanLanguageService.

        Args:
            noun: German noun to evaluate

        Returns:
            True if likely concrete, False otherwise
        """
        return self._german_service.is_concrete_noun(noun)

    def add_media_file(self, file_path: str) -> MediaFile:
        """Add a media file to the deck."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Media file not found: {file_path}")

        # Copy to collection media directory
        filename = os.path.basename(file_path)
        self._collection.media.add_file(file_path)

        # For Anki backend, wrap audio files in [sound:] format
        reference = filename
        if filename.endswith((".mp3", ".wav", ".ogg")):
            reference = f"[sound:{filename}]"

        media_file = MediaFile(path=file_path, reference=reference)
        self._media_files.append(media_file)
        return media_file

    def export_deck(self, output_path: str) -> None:
        """Export the deck to a file."""
        from anki.exporting import AnkiPackageExporter

        exporter = AnkiPackageExporter(self._collection)
        exporter.did = self._deck_id

        # The correct method name might be different, let's try the common patterns
        if hasattr(exporter, "export_to_file"):
            exporter.export_to_file(output_path)
        elif hasattr(exporter, "exportInto"):
            exporter.exportInto(output_path)
        else:
            # Create a simple export by copying the collection
            import shutil

            shutil.copy2(self._collection_path, output_path)

    def get_stats(self) -> dict[str, Any]:
        """Get deck statistics."""
        stats = {
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
            stats["notes_count"] = self._collection.db.scalar(
                "SELECT count() FROM notes"
            )
        except Exception:
            pass

        return stats
