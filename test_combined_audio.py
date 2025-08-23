#!/usr/bin/env python3
"""Test combined audio generation for verb cards."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from langlearn.models.records import VerbConjugationRecord
from langlearn.services.media_enricher import StandardMediaEnricher


def test_combined_audio():
    """Test combined audio text generation for different verb tenses."""
    print("🧪 Testing combined audio text generation...")

    # Create test records for different tenses
    test_records = [
        # Present tense
        VerbConjugationRecord(
            infinitive="sprechen",
            english="to speak",
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
            example="Ich spreche Deutsch.",
        ),
        # Imperative
        VerbConjugationRecord(
            infinitive="sprechen",
            english="to speak",
            classification="unregelmäßig",
            separable=False,
            auxiliary="haben",
            tense="imperative",
            du="sprich",
            ihr="sprecht",
            sie="sprechen Sie",
            wir="sprechen wir",
            example="Sprich lauter!",
        ),
    ]

    # Create enricher (dummy - we just need the method)
    class TestEnricher(StandardMediaEnricher):
        def __init__(self):
            # Skip initialization for testing
            pass

    enricher = TestEnricher()

    for record in test_records:
        record_dict = record.to_dict()
        combined_text = enricher._get_verb_combined_audio_text(record_dict)

        print(f"\n📢 {record.tense.upper()} tense:")
        print(f'   Combined audio: "{combined_text}"')
        print(f"   Length: {len(combined_text)} characters")

        # Verify no English in the combined text
        english_words = ["to", "speak", "the", "and", "of", "in"]
        english_found = [
            word for word in english_words if word.lower() in combined_text.lower()
        ]
        if english_found:
            print(f"   ⚠️  English words detected: {english_found}")
        else:
            print("   ✅ No English words detected")


if __name__ == "__main__":
    test_combined_audio()
