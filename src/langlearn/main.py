#!/usr/bin/env python3
"""Main application entry point using GermanDeckBuilder.

This replaces the legacy create_deck.py with a modern implementation
using the GermanDeckBuilder orchestrator.
"""

import logging
import sys
from pathlib import Path

from langlearn.german_deck_builder import GermanDeckBuilder

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Main application entry point."""
    print("=== German A1 Deck Generator ===")
    print("Creating deck with automatic audio and image generation...")

    # Configuration
    deck_name = "German A1 Vocabulary"
    data_dir = Path(__file__).parent.parent.parent / "data"
    output_dir = Path(__file__).parent.parent.parent / "output"

    print(f"📂 Data directory: {data_dir}")
    print(f"💾 Output directory: {output_dir}")

    if not data_dir.exists():
        print(f"❌ Error: Data directory not found: {data_dir}")
        sys.exit(1)

    try:
        # Create the deck using GermanDeckBuilder
        with GermanDeckBuilder(
            deck_name=deck_name,
            backend_type="anki",  # Use AnkiBackend for production
            enable_media_generation=True,  # Enable media generation
        ) as builder:
            print(f"🚀 Initialized {builder.backend_type} backend")

            # Load data from directory
            print(f"\n📚 Loading vocabulary data from {data_dir}...")
            builder.load_data_from_directory(data_dir)

            # Show what was loaded
            stats = builder.get_statistics()
            loaded_data = stats["loaded_data"]

            total_words = sum(loaded_data.values())
            if total_words == 0:
                print("❌ No vocabulary data found in data directory")
                sys.exit(1)

            print(f"✅ Loaded {total_words} words:")
            for word_type, count in loaded_data.items():
                if count > 0:
                    print(f"   📖 {word_type.title()}: {count}")

            # Generate cards with media
            print("\n🎴 Generating Anki cards with media...")
            results = builder.generate_all_cards(generate_media=True)

            total_cards = sum(results.values())
            print(f"✅ Generated {total_cards} cards:")
            for card_type, count in results.items():
                print(f"   🎴 {card_type.title()}: {count}")

            # Show final statistics
            final_stats = builder.get_statistics()
            print("\n📊 Final Statistics:")
            print(f"   📋 Total notes: {final_stats['deck_stats']['notes_count']}")

            # Show subdeck information
            subdeck_info = builder.get_subdeck_info()
            if subdeck_info["subdeck_names"]:
                print(f"   🗂️  Subdecks: {len(subdeck_info['subdeck_names'])}")
                for name in subdeck_info["subdeck_names"]:
                    print(f"      - {name}")

            # Show media statistics if available
            if "media_stats" in final_stats:
                media_stats = final_stats["media_stats"]
                print(f"   🎵 Media files: {media_stats['files_added']}")
                print(f"   💾 Total size: {media_stats['total_size_bytes']:,} bytes")

            # Export deck
            output_file = output_dir / f"{deck_name.replace(' ', '_').lower()}.apkg"
            print(f"\n💾 Exporting deck to {output_file}...")

            builder.export_deck(output_file)

            # Show export results
            if output_file.exists():
                file_size = output_file.stat().st_size
                print("✅ Deck exported successfully!")
                print(f"   📁 File: {output_file}")
                print(f"   📊 Size: {file_size:,} bytes")
                print("\n🎉 Import this file into Anki to start learning!")
            else:
                print("❌ Export failed - file not created")
                sys.exit(1)

    except KeyboardInterrupt:
        print("\n⏹️  Cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Application failed: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
