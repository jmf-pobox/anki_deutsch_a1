#!/usr/bin/env python3
"""Debug exactly where article media data is lost."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "src"))

from langlearn.models.records import UnifiedArticleRecord
from langlearn.services import get_anthropic_service
from langlearn.services.audio import AudioService
from langlearn.services.media_enricher import StandardMediaEnricher
from langlearn.services.pexels_service import PexelsService
from langlearn.services.record_to_model_factory import RecordToModelFactory


def debug_media_pipeline():
    print("🔍 DEBUGGING ARTICLE MEDIA PIPELINE")
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

    # Step 2: Convert to domain model
    print("\n2️⃣ Converting to Article domain model...")
    domain_model = RecordToModelFactory.create_domain_model(record)
    print(f"✅ Domain model: {type(domain_model).__name__}")

    # Step 3: Check domain model audio generation
    print("\n3️⃣ Testing domain model audio generation...")
    audio_segments = domain_model.get_audio_segments()
    print(f"✅ Audio segments generated: {len(audio_segments)}")
    for key, text in audio_segments.items():
        print(f"   - {key}: '{text[:40]}...'")

    # Step 4: Test MediaEnricher (the critical step)
    print("\n4️⃣ Testing MediaEnricher...")
    try:
        audio_service = AudioService(output_dir="data/audio")
        pexels_service = PexelsService()
        anthropic_service = get_anthropic_service()

        if not anthropic_service:
            print("❌ No Anthropic service - media enrichment will fail")
            return

        enricher = StandardMediaEnricher(
            audio_service=audio_service,
            pexels_service=pexels_service,
            anthropic_service=anthropic_service,
            audio_base_path=Path("data/audio"),
            image_base_path=Path("data/images"),
        )

        # This is the critical call - does it actually generate media?
        print("   Calling enricher.enrich_with_media()...")
        media_data = enricher.enrich_with_media(domain_model)

        print(f"✅ MediaEnricher returned: {len(media_data)} fields")
        for key, value in media_data.items():
            print(f"   - {key}: {value}")

        # Check if audio files were actually created
        print("\n   Checking if audio files exist...")
        audio_dir = Path("data/audio")
        if audio_dir.exists():
            audio_files = list(audio_dir.glob("*.mp3"))
            print(f"   Audio files in data/audio: {len(audio_files)}")
            for f in audio_files[-3:]:  # Show last 3
                print(f"     - {f.name}")
        else:
            print("   ❌ data/audio directory doesn't exist")

    except Exception as e:
        print(f"❌ MediaEnricher failed: {e}")
        import traceback

        traceback.print_exc()

    # Step 5: Test the filtering that was supposedly fixed
    print("\n5️⃣ Testing media_keys filtering...")
    media_keys = {
        "image",
        "word_audio",
        "example_audio",
        "phrase_audio",
        "example1_audio",
        "example2_audio",
        "du_audio",
        "ihr_audio",
        "sie_audio",
        "wir_audio",
        # Article-specific (recently added)
        "pattern_audio",
        "example_nom_audio",
        "example_akk_audio",
        "example_dat_audio",
        "example_gen_audio",
    }

    filtered_data = {k: v for k, v in media_data.items() if k in media_keys}
    print(f"✅ After filtering: {len(filtered_data)} fields remain")
    for key, value in filtered_data.items():
        print(f"   - {key}: {value}")

    if len(filtered_data) < len(audio_segments):
        missing = set(audio_segments.keys()) - set(filtered_data.keys())
        print(f"❌ LOST FIELDS: {missing}")
    else:
        print("✅ No fields lost in filtering")


if __name__ == "__main__":
    debug_media_pipeline()
