#!/usr/bin/env python3
"""Test script to check verb conjugation media enrichment."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from langlearn.deck_builder import DeckBuilder
from langlearn.services.csv_service import CSVService
from langlearn.services.record_mapper import RecordMapper


def test_verb_media_enrichment():
    """Test verb conjugation media enrichment."""
    print("🧪 Testing verb conjugation media enrichment...")

    # Load just a few verb records
    csv_service = CSVService()
    record_mapper = RecordMapper()

    # Read and convert verb data
    print("📄 Loading verb data...")
    csv_data = csv_service.read_csv_as_records(
        Path("data/verbs_unified.csv"), "verb_conjugation"
    )[:3]
    records, errors = record_mapper.records_from_csv_data(csv_data, "verb_conjugation")

    if errors:
        print(f"❌ Errors during conversion: {errors}")
        return

    print(f"✅ Loaded {len(records)} verb conjugation records:")
    for record in records:
        print(f"   - {record.infinitive} ({record.tense})")

    # Create deck builder with media enabled
    print("\n🔧 Testing media enrichment...")
    builder = DeckBuilder("Test Verb Media", enable_media_generation=True)

    # Test media enricher directly
    if not builder._media_enricher:
        print("❌ Media enricher not initialized!")
        return

    # Test enrichment on first record
    test_record = records[0]
    record_dict = test_record.to_dict()
    domain_model = test_record  # Use record itself as domain model

    print(f"\n🔍 Testing enrichment for: {test_record.infinitive}")
    print(f"   Record type: {type(test_record).__name__}")
    print(f"   Record fields: {list(record_dict.keys())}")

    # Test enrichment
    try:
        enriched = builder._media_enricher.enrich_record(record_dict, domain_model)
        print("\n✅ Enrichment completed!")

        # Check media fields
        media_fields = {}
        for key in ["image", "word_audio", "example_audio"]:
            if enriched.get(key):
                media_fields[key] = enriched[key]

        if media_fields:
            print("📸 Media fields generated:")
            for field, value in media_fields.items():
                print(f"   - {field}: {value}")
        else:
            print("❌ No media fields generated")
            print(f"   Available keys: {list(enriched.keys())}")

    except Exception as e:
        print(f"❌ Enrichment failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_verb_media_enrichment()
