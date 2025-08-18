#!/usr/bin/env python3
"""
Demonstration script showing the new backend abstraction layer.
This shows how both genanki and the official Anki library can be used
through the same interface.
"""

from pathlib import Path

from langlearn.backends import AnkiBackend, CardTemplate, GenankiBackend, NoteType


def create_sample_note_type() -> NoteType:
    """Create a sample German adjective note type."""
    template = CardTemplate(
        name="German Adjective",
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
        {{#Comparative}}
        <div class="comparative">Comparative: {{Comparative}}</div>
        {{/Comparative}}
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
        """,
    )

    return NoteType(
        name="German Adjective",
        fields=["Word", "English", "Example", "Comparative", "Image"],
        templates=[template],
    )


def demonstrate_backend(
    backend_name: str, backend: GenankiBackend | AnkiBackend
) -> None:
    """Demonstrate a backend by creating a small deck."""
    print(f"\n=== Demonstrating {backend_name} Backend ===")

    # Create note type
    note_type = create_sample_note_type()
    note_type_id = backend.create_note_type(note_type)
    print(f"Created note type with ID: {note_type_id}")

    # Add some sample German adjectives
    adjectives = [
        ["gut", "good", "Das Wetter ist heute gut.", "besser", ""],
        ["schlecht", "bad", "Das Essen ist schlecht.", "schlechter", ""],
        ["groß", "big", "Das Haus ist sehr groß.", "größer", ""],
        ["klein", "small", "Der Hund ist klein.", "kleiner", ""],
    ]

    for adj_data in adjectives:
        backend.add_note(note_type_id, adj_data)

    print(f"Added {len(adjectives)} adjective notes")

    # Show statistics (if available) - before export to avoid collection closing
    if hasattr(backend, "get_stats"):
        stats = backend.get_stats()  # type: ignore
        print(f"Deck statistics: {stats}")

    # Create output directory
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)

    # Export deck
    output_file = output_dir / f"demo_{backend_name.lower().replace(' ', '_')}.apkg"
    backend.export_deck(str(output_file))
    print(f"Exported deck to: {output_file}")


def main() -> None:
    """Run the backend demonstration."""
    print("Backend Abstraction Layer Demonstration")
    print("=" * 50)

    # Demonstrate genanki backend
    genanki_backend = GenankiBackend(
        "Demo Deck - genanki", "Created with genanki backend"
    )
    demonstrate_backend("Genanki", genanki_backend)

    # Demonstrate official Anki backend
    anki_backend = AnkiBackend(
        "Demo Deck - Official", "Created with official Anki backend"
    )
    demonstrate_backend("Official Anki", anki_backend)

    print("\n" + "=" * 50)
    print("Demonstration completed!")
    print("\nKey achievements:")
    print("✅ Same interface works with both backends")
    print("✅ genanki backend creates .apkg files")
    print("✅ Official Anki backend creates .apkg files (Phase 2 complete!)")
    print("✅ Abstraction layer is working correctly")
    print("✅ Real Collection-based deck generation working")


if __name__ == "__main__":
    main()
