#!/usr/bin/env python3
"""Demonstration of the GermanDeckBuilder orchestrator.

This script shows how to use the GermanDeckBuilder to create German language
learning Anki decks with the official Anki library backend.
"""

import sys
from pathlib import Path

# Add src to path to import langlearn modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from langlearn.deck_builder import DeckBuilder
from langlearn.models.adjective import Adjective
from langlearn.models.noun import Noun


def demo_german_deck_builder() -> None:
    """Demonstrate GermanDeckBuilder usage with sample data."""
    print("🚀 GermanDeckBuilder Demo")
    print("=" * 50)

    # Create builder with AnkiBackend (production default)
    print("\n📦 Creating GermanDeckBuilder with AnkiBackend...")
    with DeckBuilder(
        deck_name="Demo German A1 Vocabulary",
        backend_type="anki",  # Use production AnkiBackend
        enable_media_generation=False,  # Disable to avoid API dependencies
    ) as builder:
        print(f"✅ Builder initialized: {builder.deck_name}")
        print(f"   Backend: {builder.backend_type}")
        print(f"   Media enabled: {builder.enable_media_generation}")

        # Create sample data instead of loading from CSV
        print("\n📚 Adding sample vocabulary data...")

        # Sample nouns
        sample_nouns = [
            Noun(
                noun="Katze",
                article="die",
                english="cat",
                plural="Katzen",
                example="Die Katze schläft auf dem Sofa.",
                related="Haustier, Tier",
            ),
            Noun(
                noun="Hund",
                article="der",
                english="dog",
                plural="Hunde",
                example="Der Hund bellt laut.",
                related="Haustier, Tier",
            ),
            Noun(
                noun="Auto",
                article="das",
                english="car",
                plural="Autos",
                example="Das Auto ist rot.",
                related="Verkehr, Fahrzeug",
            ),
        ]

        # Sample adjectives
        sample_adjectives = [
            Adjective(
                word="schön",
                english="beautiful",
                example="Das Haus ist sehr schön.",
                comparative="schöner",
                superlative="am schönsten",
            ),
            Adjective(
                word="groß",
                english="big",
                example="Der Baum ist groß.",
                comparative="größer",
                superlative="am größten",
            ),
        ]

        # Load the sample data directly into the builder
        builder._loaded_nouns = sample_nouns
        builder._loaded_adjectives = sample_adjectives

        print(f"   Loaded {len(sample_nouns)} nouns")
        print(f"   Loaded {len(sample_adjectives)} adjectives")

        # Show subdeck management
        print("\n🗂️  Managing subdecks...")
        builder.create_subdeck("Test Nouns")
        print(f"   Created subdeck: {builder.get_subdeck_info()['current_deck']}")

        builder.reset_to_main_deck()
        print(f"   Reset to main deck: {builder.get_subdeck_info()['current_deck']}")

        # Generate cards (without media to avoid API dependencies)
        print("\n🎴 Generating Anki cards...")
        results = builder.generate_all_cards(generate_media=False)

        for card_type, count in results.items():
            print(f"   {card_type.title()}: {count} cards generated")

        print(f"   Total cards: {sum(results.values())}")

        # Show statistics
        print("\n📊 Deck Statistics:")
        stats = builder.get_statistics()

        print(f"   Deck name: {stats['deck_info']['name']}")
        print(f"   Backend: {stats['deck_info']['backend_type']}")
        print(f"   Loaded nouns: {stats['loaded_data']['nouns']}")
        print(f"   Loaded adjectives: {stats['loaded_data']['adjectives']}")
        print(f"   Total notes: {stats['deck_stats']['notes_count']}")

        # Show subdeck information
        subdeck_info = builder.get_subdeck_info()
        if subdeck_info["subdeck_names"]:
            print(f"   Subdecks created: {len(subdeck_info['subdeck_names'])}")
            for name in subdeck_info["subdeck_names"]:
                print(f"     - {name}")

        # Export deck
        output_path = Path("output/demo_german_deck.apkg")
        print(f"\n💾 Exporting deck to {output_path}...")

        try:
            builder.export_deck(output_path)
            print("✅ Deck exported successfully!")
            print(f"   File size: {output_path.stat().st_size:,} bytes")
        except Exception as e:
            print(f"❌ Export failed: {e}")

    print("\n🎉 Demo completed!")


def demo_with_csv_loading() -> None:
    """Demonstrate CSV loading (requires actual CSV files)."""
    print("\n📂 CSV Loading Demo")
    print("=" * 30)

    data_dir = Path(__file__).parent.parent / "data"
    if not data_dir.exists():
        print("❌ Data directory not found, skipping CSV demo")
        return

    with DeckBuilder(
        deck_name="CSV Demo Deck",
        backend_type="anki",  # Use production AnkiBackend
        enable_media_generation=False,
    ) as builder:
        print(f"📂 Loading data from {data_dir}...")

        try:
            # Try to load all data from directory
            builder.load_data_from_directory(data_dir)

            # Show what was loaded
            stats = builder.get_statistics()
            print(f"   Loaded {stats['loaded_data']['nouns']} nouns")
            print(f"   Loaded {stats['loaded_data']['adjectives']} adjectives")

            if sum(stats["loaded_data"].values()) > 0:
                print("✅ CSV data loaded successfully")
            else:
                print("i No CSV data found")

        except Exception as e:
            print(f"❌ CSV loading failed: {e}")


if __name__ == "__main__":
    # Run the main demo
    demo_german_deck_builder()

    # Optionally try CSV loading demo
    demo_with_csv_loading()

    print("\n📝 Note: To use media generation, enable it and set up API keys:")
    print("   - AWS credentials for audio generation (Polly)")
    print("   - Pexels API key for image generation")
    print("   - Use builder with enable_media_generation=True")
