#!/usr/bin/env python3
"""Simple test script to create a basic Anki deck with media for compatibility testing."""

import logging
import sys
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from langlearn.backends.anki_backend import AnkiBackend
from langlearn.backends.base import CardTemplate, NoteType


def create_simple_test_deck():
    """Create a very simple deck with basic media to test Anki 25.x compatibility."""

    deck_name = "Simple Media Test"
    output_path = Path(__file__).parent / "output" / "simple_media_test.apkg"

    print(f"Creating simple test deck: {deck_name}")
    print(f"Output: {output_path}")

    # Ensure output directory exists
    output_path.parent.mkdir(exist_ok=True)

    try:
        backend = AnkiBackend(deck_name)

        # Create a very basic note type
        note_type = NoteType(
            name="Simple Test",
            fields=["German", "English", "Audio", "Image"],
            templates=[
                CardTemplate(
                    name="Simple Test Card",
                    front_html="<div style='font-size: 24px;'>{{German}}</div><br>{{Image}}<br>{{Audio}}",
                    back_html="<div style='font-size: 24px;'>{{German}}</div><br>{{Image}}<br>{{Audio}}<hr><div style='font-size: 20px;'>{{English}}</div>",
                    css=".card { font-family: Arial; text-align: center; }",
                )
            ],
        )

        note_type_id = backend.create_note_type(note_type)
        print(f"Created note type: {note_type_id}")

        # Add media files manually
        print("Adding media files...")

        # Add an existing audio file
        audio_path = "data/audio/d8bd8e4fa443e49f41597ef14b65a548.mp3"  # nie audio
        if Path(audio_path).exists():
            audio_media = backend.add_media_file(audio_path, media_type="audio")
            print(f"Added audio: {audio_media.reference}")
        else:
            audio_media = None
            print("Audio file not found")

        # Add an existing image file
        image_path = "data/images/nie.jpg"
        if Path(image_path).exists():
            image_media = backend.add_media_file(image_path, media_type="image")
            print(f"Added image: {image_media.reference}")
        else:
            image_media = None
            print("Image file not found")

        # Create a simple note with direct media references
        fields = [
            "nie",  # German
            "never",  # English
            audio_media.reference if audio_media else "",  # Audio
            f"<img src='{image_media.reference}'>" if image_media else "",  # Image
        ]

        print(f"Adding note with fields: {fields}")
        note_id = backend.add_note(note_type_id, fields, skip_media_processing=True)
        print(f"Created note: {note_id}")

        # Export deck
        print("Exporting deck...")
        backend.export_deck(str(output_path))
        print(f"✅ Simple test deck exported to: {output_path}")

        # Show stats
        stats = backend.get_stats()
        print(f"📊 Stats: {stats}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    create_simple_test_deck()
