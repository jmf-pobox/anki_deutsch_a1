#!/usr/bin/env python3
"""Test verb loading in the deck builder."""

import logging
from pathlib import Path

from langlearn.deck_builder import DeckBuilder

logging.basicConfig(level=logging.INFO)


def test_verb_loading():
    """Test that verbs are loaded correctly by DeckBuilder."""

    # Create builder with media disabled for speed
    builder = DeckBuilder("Test Verb Deck", enable_media_generation=False)

    # Load data from directory
    data_dir = Path("data")
    builder.load_data_from_directory(data_dir)

    # Get stats
    stats = builder.get_stats()
    print("\n=== Loaded Data Stats ===")
    for key, value in stats["loaded_data"].items():
        if value > 0:
            print(f"{key}: {value}")

    # Check loaded records
    print(f"\nTotal Clean Pipeline records: {len(builder._loaded_records)}")

    # Group records by type
    records_by_type = {}
    for record in builder._loaded_records:
        record_type = type(record).__name__
        if record_type not in records_by_type:
            records_by_type[record_type] = 0
        records_by_type[record_type] += 1

    print("\n=== Records by Type ===")
    for record_type, count in records_by_type.items():
        print(f"{record_type}: {count}")

    # Try to generate cards without media
    print("\n=== Generating Cards ===")
    results = builder.generate_all_cards(generate_media=False)

    print("\n=== Card Generation Results ===")
    for card_type, count in results.items():
        print(f"{card_type}: {count} cards")

    return results


if __name__ == "__main__":
    results = test_verb_loading()
    if results.get("verbs", 0) == 0:
        print("\n⚠️  WARNING: No verb cards were generated!")
    else:
        print(f"\n✅ Successfully generated {results['verbs']} verb cards")
