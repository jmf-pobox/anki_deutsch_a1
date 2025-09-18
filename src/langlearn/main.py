#!/usr/bin/env python3
"""Main application entry point for multi-language deck generation.

This provides the modern implementation for deck generation
supporting multiple languages and decks per language.
"""

import argparse
import logging
import sys
from pathlib import Path

from langlearn.core.deck import DeckBuilderAPI

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
        help="Language to generate deck for (case-insensitive, default: german)",
    )
    parser.add_argument(
        "--deck",
        default="default",
        help="Deck name within the language (case-insensitive, default: default)",
    )
    parser.add_argument(
        "--output", help="Output file path (auto-generated if not specified)"
    )
    args = parser.parse_args()

    # Normalize language and deck to lowercase for consistent filesystem paths
    args.language = args.language.lower()
    args.deck = args.deck.lower()

    return args


def main() -> None:
    """Main application entry point."""
    args = parse_args()

    print(f"=== {args.language.title()} Deck Generator ===")
    print(f"Creating {args.deck} deck with automatic audio and image generation...")

    # Configuration based on CLI parameters
    deck_name = f"{args.language.title()} {args.deck.title()} Vocabulary"
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / "languages" / args.language / args.deck
    output_dir = project_root / "output"

    print(f"📂 Data directory: {data_dir}")
    print(f"💾 Output directory: {output_dir}")

    if not data_dir.exists():
        print(f"❌ Error: Data directory not found: {data_dir}")
        print("Available languages/decks:")
        data_root = project_root / "languages"
        if data_root.exists():
            for lang_dir in data_root.iterdir():
                if lang_dir.is_dir() and not lang_dir.name.startswith("."):
                    print(f"  Language: {lang_dir.name}")
                    for deck_dir in lang_dir.iterdir():
                        if deck_dir.is_dir() and not deck_dir.name.startswith("."):
                            print(f"    Deck: {deck_dir.name}")
        sys.exit(1)

    try:
        # Create the deck using DeckBuilderAPI with language/deck configuration
        with DeckBuilderAPI(
            deck_name=deck_name,
            language=args.language,
            deck_type=args.deck,
        ) as builder:
            print("🚀 Initialized AnkiBackend")

            # Load data from directory
            print(f"\n📚 Loading vocabulary data from {data_dir}...")
            loaded_data = builder.load_data(data_dir)

            # Show what was loaded
            total_words = loaded_data.total_records
            if total_words == 0:
                print("❌ No vocabulary data found in data directory")
                sys.exit(1)

            print(f"✅ Loaded {total_words} words:")
            # Import NamingService for consistent naming
            from langlearn.core.services import NamingService

            for word_type, records in loaded_data.records_by_type.items():
                count = len(records)
                if count > 0:
                    # Use NamingService for consistent display names
                    display_name = NamingService.get_display_name(word_type)
                    print(f"   📖 {display_name}: {count}")

            # Generate cards with media
            print("\n🎴 Generating Anki cards with media...")

            # Enrich with media
            print("   🖼️  Enriching records with media...")
            for progress in builder.enrich_media():
                print(
                    f"      Processing {progress.record_type}: "
                    f"{progress.processed}/{progress.total}"
                )

            # Build cards
            print("   🔨 Building Anki cards...")
            built_cards = builder.build_cards()

            total_cards = len(built_cards.cards)
            print(f"✅ Generated {total_cards} cards:")
            for card_type, cards in built_cards.cards_by_type.items():
                count = len(cards)
                print(f"   🎴 {card_type.title()}: {count}")

            # Show final statistics
            pipeline_summary = builder.get_pipeline_summary()
            print("\n📊 Final Statistics:")
            print(f"   📋 Total records loaded: {pipeline_summary.loaded}")
            print(f"   🖼️  Records enriched with media: {pipeline_summary.enriched}")
            print(f"   🎴 Cards built: {pipeline_summary.built}")
            print(f"   📊 Current phase: {pipeline_summary.phase.value}")

            # Export deck
            if args.output:
                output_file = Path(args.output)
            else:
                filename = f"LangLearn_{args.language.capitalize()}_{args.deck}.apkg"
                output_file = output_dir / filename
            print(f"\n💾 Exporting deck to {output_file}...")

            export_result = builder.export_deck(output_file)

            # Show export results
            print("✅ Deck exported successfully!")
            print(f"   📁 File: {export_result.output_path}")
            print(f"   📊 Size: {export_result.file_size:,} bytes")
            print(f"   🎴 Cards exported: {export_result.cards_exported}")
            print("\n🎉 Import this file into Anki to start learning!")

    except KeyboardInterrupt:
        print("\n⏹️  Cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Application failed: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
