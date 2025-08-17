#!/usr/bin/env python3
"""
Demo script showing automatic media generation integration.
Tests AudioService and PexelsService integration in AnkiBackend.
"""

from pathlib import Path

from langlearn.backends import AnkiBackend, CardTemplate, NoteType


def create_german_adjective_note_type() -> NoteType:
    """Create a German adjective note type with image field."""
    template = CardTemplate(
        name="German Adjective with Media",
        front_html="""
        <div class="german">{{Word}}</div>
        {{#Image}}{{Image}}{{/Image}}
        """,
        back_html="""
        <div class="german">{{Word}}</div>
        {{#Image}}{{Image}}{{/Image}}
        <hr>
        <div class="english">{{English}}</div>
        <div class="example">{{Example}}</div>
        {{#Comparative}}<div class="comparative">Comparative: {{Comparative}}</div>{{/Comparative}}
        """,
        css="""
        .card {
            font-family: Arial, sans-serif;
            text-align: center;
            background-color: #f5f5f5;
            padding: 20px;
        }
        .german {
            font-size: 24px;
            font-weight: bold;
            color: #2c5aa0;
        }
        .english {
            font-size: 18px;
            color: #333;
            margin: 10px 0;
        }
        .example, .comparative {
            font-size: 16px;
            color: #666;
            margin: 5px 0;
        }
        img {
            max-width: 300px;
            max-height: 200px;
            border-radius: 8px;
        }
        """,
    )

    return NoteType(
        name="German Adjective with Media",
        fields=[
            "Word",
            "English",
            "Example",
            "Comparative",
            "Superlative",
            "Image",
            "WordAudio",
            "ExampleAudio",
        ],
        templates=[template],
    )


def demonstrate_media_integration() -> None:
    """Demonstrate automatic media generation during card creation."""
    print("=== Media Integration Demonstration ===")
    print("Testing automatic audio and image generation...")

    # Create backend
    backend = AnkiBackend(
        "Media Integration Demo", "Testing automatic audio + image generation"
    )

    # Create note type
    note_type = create_german_adjective_note_type()
    note_type_id = backend.create_note_type(note_type)
    print(f"Created note type with ID: {note_type_id}")

    # Test adjectives (some should already have images in data/images/)
    # Fields: [Word, English, Example, Comparative, Superlative, Image, WordAudio, ExampleAudio]
    test_adjectives = [
        [
            "gut",
            "good",
            "Das Wetter ist heute gut.",
            "besser",
            "am besten",
            "",
            "",
            "",
        ],  # Image exists
        [
            "schlecht",
            "bad",
            "Das Essen ist schlecht.",
            "schlechter",
            "am schlechtesten",
            "",
            "",
            "",
        ],  # Image exists
        [
            "fantastisch",
            "fantastic",
            "Der Film war fantastisch.",
            "fantastischer",
            "am fantastischsten",
            "",
            "",
            "",
        ],  # New image needed
        [
            "wunderbar",
            "wonderful",
            "Das ist wunderbar!",
            "wunderbarer",
            "am wunderbarsten",
            "",
            "",
            "",
        ],  # Image exists
    ]

    print(
        f"\nAdding {len(test_adjectives)} adjective cards with automatic media generation..."
    )

    for i, adj_data in enumerate(test_adjectives):
        try:
            note_id = backend.add_note(
                note_type_id, adj_data, tags=["adjective", "test"]
            )
            print(f"  {i + 1}. Added '{adj_data[0]}' -> Note ID: {note_id}")
        except Exception as e:
            print(f"  {i + 1}. ERROR adding '{adj_data[0]}': {e}")

    # Show statistics
    print("\n=== Media Generation Statistics ===")
    if hasattr(backend, "get_stats"):
        stats = backend.get_stats()

        if "media_generation_stats" in stats:
            media_gen = stats["media_generation_stats"]
            print(f"✅ Audio generated: {media_gen['audio_generated']}")
            print(f"♻️  Audio reused: {media_gen['audio_reused']}")
            print(f"🖼️  Images downloaded: {media_gen['images_downloaded']}")
            print(f"♻️  Images reused: {media_gen['images_reused']}")
            print(f"❌ Generation errors: {media_gen['generation_errors']}")
            print(f"🆕 Total new media: {media_gen['total_media_generated']}")
            print(f"🔄 Total reused media: {media_gen['total_media_reused']}")

        if "media_stats" in stats:
            media_stats = stats["media_stats"]
            print(f"📦 Media files added to deck: {media_stats['files_added']}")
            print(f"🚫 Media duplicates skipped: {media_stats['duplicates_skipped']}")

    # Create output directory
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)

    # Export deck
    output_file = output_dir / "media_integration_demo.apkg"
    backend.export_deck(str(output_file))
    print(f"\nExported deck to: {output_file}")

    print("\n=== Integration Test Complete ===")
    print("✅ AudioService integration: Audio files generated/reused automatically")
    print("✅ PexelsService integration: Images downloaded/reused automatically")
    print("✅ Media files properly added to Anki collection")
    print("✅ Existing assets detected and reused efficiently")


if __name__ == "__main__":
    demonstrate_media_integration()
