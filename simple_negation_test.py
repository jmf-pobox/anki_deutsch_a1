#!/usr/bin/env python3
"""Simple test to isolate the negation field logic."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from langlearn.models.negation import Negation, NegationType


def test_simple_field_logic():
    """Test basic field logic without complex dependencies."""

    # Create test negation
    nie = Negation(
        word="nie",
        english="never",
        type=NegationType.TEMPORAL,
        example="Ich war noch nie in Berlin.",
        word_audio="",
        example_audio="",
        image_path="",
    )

    print(f"=== SIMPLE FIELD LOGIC TEST FOR '{nie.word}' ===")

    # Simulate the field names from NegationCardGenerator
    field_names = [
        "Word",  # 0
        "English",  # 1
        "Type",  # 2
        "Example",  # 3
        "Image",  # 4
        "WordAudio",  # 5
        "ExampleAudio",  # 6
    ]

    # Simulate _extract_fields
    base_fields = [
        nie.word,  # 0: Word
        nie.english,  # 1: English
        nie.type.value,  # 2: Type
        nie.example,  # 3: Example
        "",  # 4: Image (empty initially)
        "",  # 5: WordAudio (empty initially)
        "",  # 6: ExampleAudio (empty initially)
    ]

    print("\nField mapping:")
    for i, (name, value) in enumerate(zip(field_names, base_fields, strict=False)):
        print(f"  [{i}] {name}: '{value}'")

    # Simulate what SHOULD happen in media enhancement
    enhanced_fields = base_fields.copy()

    # Simulate audio generation results (what the screenshot shows is wrong)
    # The bug must be that these are being assigned to wrong indices
    mock_word_audio_ref = "[sound:9c64c1526cabc7558ad604b71592b5ec.mp3]"
    mock_example_audio_ref = (
        "[sound:different_hash_for_example.mp3]"  # Should be different!
    )
    mock_image_html = '<img src="nie.jpg">'

    # CORRECT assignment should be:
    enhanced_fields[4] = mock_image_html  # Image at index 4
    enhanced_fields[5] = mock_word_audio_ref  # WordAudio at index 5
    enhanced_fields[6] = mock_example_audio_ref  # ExampleAudio at index 6

    print("\n=== CORRECT ENHANCED FIELDS ===")
    for i, (name, value) in enumerate(zip(field_names, enhanced_fields, strict=False)):
        print(f"  [{i}] {name}: '{value}'")

    # Show what the bug looks like (from screenshot)
    print("\n=== BUG SYMPTOMS (from screenshot) ===")
    buggy_fields = base_fields.copy()
    buggy_fields[4] = (
        "[sound:do6d8e4fa443e49f41597ef14b65a548.mp3]"  # Audio in Image field!
    )
    buggy_fields[5] = "[sound:9c64c1526cabc7558ad604b71592b5ec.mp3]"  # WordAudio
    buggy_fields[6] = (
        "[sound:9c64c1526cabc7558ad604b71592b5ec.mp3]"  # Same audio in ExampleAudio!
    )

    for i, (name, value) in enumerate(zip(field_names, buggy_fields, strict=False)):
        print(f"  [{i}] {name}: '{value}'")

    print("\n=== ANALYSIS ===")
    print("The bug shows:")
    print("1. Image field (index 4) has audio instead of image HTML")
    print("2. WordAudio and ExampleAudio have the same audio file")
    print(
        "3. This suggests wrong field indices or same text being used for both audio generations"
    )


if __name__ == "__main__":
    test_simple_field_logic()
