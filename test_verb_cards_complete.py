#!/usr/bin/env python3
"""Test complete verb card generation with media."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_verb_card_generation():
    """Test complete verb card generation."""
    print("🧪 Testing complete verb card generation...")

    try:
        from langlearn.deck_builder import DeckBuilder

        # Create deck builder
        builder = DeckBuilder("Test Verb Cards", enable_media_generation=True)
        print("✅ DeckBuilder initialized")

        # Load verb records directly using the record mapper
        print("\n📄 Loading verb records...")
        verb_records = builder._record_mapper.load_records_from_csv(
            Path("data/verbs_unified.csv")
        )

        # Limit to first 6 records (2 verbs x 3 tenses each for testing)
        test_records = verb_records[:6]
        builder._loaded_records = test_records

        print(f"✅ Limited to {len(test_records)} verb records for testing:")
        for record in test_records:
            print(f"   - {record.infinitive} ({record.tense})")

        # Generate cards with media
        print("\n🔧 Generating cards with media...")
        results = builder.generate_all_cards(generate_media=True)

        print(f"✅ Generated cards: {results}")

        # Create a small test deck file
        print("\n💾 Creating test deck file...")
        output_path = "output/test_verb_cards.apkg"
        builder.export_deck(output_path)

        if Path(output_path).exists():
            print(f"✅ Test deck created: {output_path}")
            file_size = Path(output_path).stat().st_size
            print(f"   File size: {file_size:,} bytes")
        else:
            print("❌ Test deck not created")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_verb_card_generation()
