#!/usr/bin/env python3
"""Main application entry point for multi-language deck generation.

This provides the modern implementation for deck generation
supporting multiple languages and decks per language.
"""

import argparse
import logging
import sys
from pathlib import Path

from langlearn.deck_builder import DeckBuilder

# Set up logging
logging.basicConfig(
    level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate language learning Anki decks"
    )
    parser.add_argument(
        "--language",
        default="german",
        help="Language to generate deck for (default: german)",
    )
    parser.add_argument(
        "--deck",
        default="default",
        help="Deck name within the language (default: default)",
    )
    parser.add_argument(
        "--output", help="Output file path (auto-generated if not specified)"
    )
    return parser.parse_args()


def main() -> None:
    """Main application entry point."""
    args = parse_args()

    print(f"=== {args.language.title()} Deck Generator ===")
    print(f"Creating {args.deck} deck with automatic audio and image generation...")

    # Configuration based on CLI parameters
    deck_name = f"{args.language.title()} {args.deck.title()} Vocabulary"
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / "data" / args.language / args.deck
    output_dir = project_root / "output"

    print(f"📂 Data directory: {data_dir}")
    print(f"💾 Output directory: {output_dir}")

    if not data_dir.exists():
        print(f"❌ Error: Data directory not found: {data_dir}")
        print("Available languages/decks:")
        data_root = project_root / "data"
        if data_root.exists():
            for lang_dir in data_root.iterdir():
                if lang_dir.is_dir() and not lang_dir.name.startswith("."):
                    print(f"  Language: {lang_dir.name}")
                    for deck_dir in lang_dir.iterdir():
                        if deck_dir.is_dir() and not deck_dir.name.startswith("."):
                            print(f"    Deck: {deck_dir.name}")
        sys.exit(1)

    try:
        # Create the deck using DeckBuilder with language/deck configuration
        with DeckBuilder(
            deck_name=deck_name,
            backend_type="anki",  # Use AnkiBackend for production
            language=args.language,
            deck_type=args.deck,
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

            # Export deck
            if args.output:
                output_file = Path(args.output)
            else:
                filename = f"{args.language}_{args.deck}.apkg"
                output_file = output_dir / filename
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
