#!/usr/bin/env python3
"""Debug media file registration flow."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "src"))

from langlearn.services.media_file_registrar import MediaFileRegistrar


def test_media_registration():
    print("🔍 TESTING MEDIA REGISTRATION FLOW")
    print("=" * 60)

    # Simulate article card field values (the actual output from debug)
    test_field_values = [
        "{{c1::Der}} Mann ist hier",
        "Maskulin - Geschlecht erkennen",
        "maskulin_bestimmt.jpg",  # Image field
        "00e7fb4c7d71e4aa5513daceab4ceef2.mp3",  # Audio field
    ]

    print(f"Test field values: {test_field_values}")

    # Create MediaFileRegistrar
    registrar = MediaFileRegistrar(
        audio_base_path=Path("data/audio"), image_base_path=Path("data/images")
    )

    # Test the registration process (simulate what register_card_media does)
    total_detected = 0

    for field_value in test_field_values:
        if not field_value:
            continue

        print(f"\n🔍 Processing field: '{field_value}'")

        # Extract audio references
        audio_refs = registrar._extract_audio_references(field_value)
        print(f"   Audio detected: {audio_refs}")
        total_detected += len(audio_refs)

        # Extract image references
        image_refs = registrar._extract_image_references(field_value)
        print(f"   Images detected: {image_refs}")
        total_detected += len(image_refs)

    print(f"\n✅ Total media files detected: {total_detected}")

    if total_detected == 0:
        print("❌ No media files detected - this explains why deck is small!")
    else:
        print("✅ Media files detected - issue might be elsewhere")


if __name__ == "__main__":
    test_media_registration()
