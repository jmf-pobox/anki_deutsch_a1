#!/usr/bin/env python3
"""
Test new media generation for words without existing assets.
"""

from langlearn.backends import AnkiBackend, CardTemplate, NoteType


def test_new_media_generation() -> None:
    """Test generation of new media for words without existing assets."""
    print("=== Testing New Media Generation ===")

    backend = AnkiBackend("New Media Test", "Testing new asset generation")

    # Create simple adjective note type
    template = CardTemplate(
        name="Test Adjective",
        front_html="{{Word}}",
        back_html="{{Word}}<hr>{{English}}<br>{{Example}}<br>{{Image}}",
        css=".card { font-family: Arial; font-size: 18px; }",
    )

    note_type = NoteType(
        name="German Adjective with Media",
        fields=["Word", "English", "Example", "Comparative", "Image"],
        templates=[template],
    )

    note_type_id = backend.create_note_type(note_type)

    # Test with words that likely don't have existing assets
    test_words = [
        ["grandios", "grandiose", "Das war grandios!", "grandioser", ""],
        [
            "spektakulär",
            "spectacular",
            "Ein spektakulärer Erfolg.",
            "spektakulärer",
            "",
        ],
    ]

    print(f"Adding {len(test_words)} cards to test new media generation...")

    for word_data in test_words:
        backend.add_note(note_type_id, word_data, tags=["test", "new-media"])
        print(f"  Added '{word_data[0]}'")

    # Show statistics
    stats = backend.get_stats()
    if "media_generation_stats" in stats:
        media_gen = stats["media_generation_stats"]
        print("\nNew generation results:")
        print(f"  Audio generated: {media_gen['audio_generated']}")
        print(f"  Images downloaded: {media_gen['images_downloaded']}")
        print(f"  Errors: {media_gen['generation_errors']}")

        if media_gen["total_media_generated"] > 0:
            print("✅ New media generation working!")
        else:
            print("i No new media generated (files may already exist)")


if __name__ == "__main__":
    test_new_media_generation()
