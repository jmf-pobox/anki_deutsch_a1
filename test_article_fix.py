#!/usr/bin/env python3
"""Test the ArticlePatternProcessor audio fix."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "src"))

from langlearn.models.records import UnifiedArticleRecord
from langlearn.services import get_anthropic_service
from langlearn.services.article_pattern_processor import ArticlePatternProcessor
from langlearn.services.audio import AudioService
from langlearn.services.card_builder import CardBuilder
from langlearn.services.media_enricher import StandardMediaEnricher
from langlearn.services.pexels_service import PexelsService
from langlearn.services.record_to_model_factory import RecordToModelFactory


def test_article_audio_fix():
    print("🔍 TESTING ARTICLE AUDIO FIX")
    print("=" * 60)

    # Step 1: Create test article record
    print("\n1️⃣ Creating UnifiedArticleRecord...")
    article_data = {
        "artikel_typ": "bestimmt",
        "geschlecht": "maskulin",
        "nominativ": "der",
        "akkusativ": "den",
        "dativ": "dem",
        "genitiv": "des",
        "beispiel_nom": "Der Mann ist hier",
        "beispiel_akk": "Ich sehe den Mann",
        "beispiel_dat": "mit dem Mann",
        "beispiel_gen": "das Auto des Mannes",
    }

    record = UnifiedArticleRecord(**article_data)
    print(f"✅ Record created: {record.artikel_typ} {record.geschlecht}")

    # Step 2: Convert to domain model and generate media
    print("\n2️⃣ Testing MediaEnricher...")
    domain_model = RecordToModelFactory.create_domain_model(record)

    audio_service = AudioService(output_dir="data/audio")
    pexels_service = PexelsService()
    anthropic_service = get_anthropic_service()

    if not anthropic_service:
        print("❌ No Anthropic service - cannot test")
        return

    enricher = StandardMediaEnricher(
        audio_service=audio_service,
        pexels_service=pexels_service,
        anthropic_service=anthropic_service,
        audio_base_path=Path("data/audio"),
        image_base_path=Path("data/images"),
    )

    media_data = enricher.enrich_with_media(domain_model)
    print(f"✅ MediaEnricher generated: {len(media_data)} fields")
    for key in media_data:
        print(f"   - {key}: {media_data[key]}")

    # Step 3: Test ArticlePatternProcessor with enriched data
    print("\n3️⃣ Testing ArticlePatternProcessor...")

    # Create a minimal CardBuilder for the processor
    from langlearn.services.template_service import TemplateService

    template_service = TemplateService(template_dir=Path("src/langlearn/templates"))
    card_builder = CardBuilder(template_service)

    processor = ArticlePatternProcessor(card_builder)

    # Test with enriched data
    cards = processor.process_article_records([record], [media_data])
    print(f"✅ Generated {len(cards)} cards")

    # Check if audio fields are populated in cards
    print("\n4️⃣ Checking audio fields in cards...")
    for i, (field_values, note_type) in enumerate(cards):
        print(f"\nCard {i + 1}:")
        print(f"  Note type: {note_type.name}")

        # Find Audio field
        audio_field_index = None
        for j, field_name in enumerate(note_type.field_names):
            if field_name.lower() == "audio":
                audio_field_index = j
                break

        if audio_field_index is not None:
            audio_value = field_values[audio_field_index]
            print(f"  Audio field: '{audio_value}'")
            if audio_value:
                print("  ✅ Audio present!")
            else:
                print("  ❌ Audio missing!")
        else:
            print("  ⚠️  No Audio field found")


if __name__ == "__main__":
    test_article_audio_fix()
