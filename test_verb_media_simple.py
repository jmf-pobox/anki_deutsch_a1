#!/usr/bin/env python3
"""Simple test script to check verb conjugation media enrichment."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from langlearn.models.records import VerbConjugationRecord


def test_verb_media_enrichment():
    """Test verb conjugation media enrichment directly."""
    print("🧪 Testing verb conjugation media enrichment...")

    # Create a sample VerbConjugationRecord
    test_record = VerbConjugationRecord(
        infinitive="sprechen",
        meaning="to speak",
        classification="unregelmäßig",
        separable=False,
        auxiliary="haben",
        tense="present",
        ich="spreche",
        du="sprichst",
        er="spricht",
        wir="sprechen",
        ihr="sprecht",
        sie="sprechen",
        example="Ich spreche Deutsch mit meinen Freunden.",
    )

    print(f"✅ Created test record: {test_record.infinitive} ({test_record.tense})")

    # Create media enricher using DeckBuilder
    print("\n🔧 Setting up media enricher...")
    try:
        from langlearn.deck_builder import DeckBuilder

        # Create deck builder which initializes the media enricher
        builder = DeckBuilder("Test", enable_media_generation=True)
        enricher = builder._media_enricher

        if not enricher:
            print("❌ Media enricher not initialized in DeckBuilder")
            return

        print("✅ Media enricher created successfully")

    except Exception as e:
        print(f"❌ Failed to create media enricher: {e}")
        import traceback

        traceback.print_exc()
        return

    # Test enrichment
    print(f"\n🔍 Testing enrichment for: {test_record.infinitive}")
    record_dict = test_record.to_dict()

    print(f"   Record type: {type(test_record).__name__}")
    print(f"   Record fields: {list(record_dict.keys())}")
    print(f"   Has infinitive: {record_dict.get('infinitive')}")
    print(f"   Has example: {record_dict.get('example')}")

    try:
        # Test with VerbConjugationRecord as domain model
        enriched = enricher.enrich_record(record_dict, test_record)
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

            # Check if media files exist
            print("\n📁 Checking media files...")
            if media_fields.get("word_audio"):
                audio_file = Path("data/audio") / media_fields["word_audio"].replace(
                    "[sound:", ""
                ).replace("]", "")
                print(f"   - Audio file exists: {audio_file.exists()} ({audio_file})")

            if media_fields.get("image"):
                img_src = (
                    media_fields["image"].split('src="')[1].split('"')[0]
                    if 'src="' in media_fields["image"]
                    else ""
                )
                if img_src:
                    image_file = Path("data/images") / img_src
                    print(
                        f"   - Image file exists: {image_file.exists()} ({image_file})"
                    )

        else:
            print("❌ No media fields generated")
            print(f"   Available keys: {list(enriched.keys())}")

    except Exception as e:
        print(f"❌ Enrichment failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_verb_media_enrichment()
