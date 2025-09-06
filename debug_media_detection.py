#!/usr/bin/env python3
"""Debug media file detection in MediaFileRegistrar."""

import re
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "src"))


def test_media_detection():
    print("🔍 TESTING MEDIA FILE DETECTION")
    print("=" * 50)

    # Test image detection
    test_image_values = [
        "maskulin_bestimmt.jpg",
        '<img src="maskulin_bestimmt.jpg" />',
        "feminin_unbestimmt.jpg",
        "some random text",
    ]

    # Test audio detection
    test_audio_values = [
        "00e7fb4c7d71e4aa5513daceab4ceef2.mp3",
        "[sound:00e7fb4c7d71e4aa5513daceab4ceef2.mp3]",
        "3ccda87822037f97c1bf3b948bc09eb9.mp3",
        "some random text",
    ]

    print("\n📷 Testing Image Detection:")
    for value in test_image_values:
        image_refs = extract_image_references(value)
        print(f"   Input: '{value}' -> Detected: {image_refs}")

    print("\n🔊 Testing Audio Detection:")
    for value in test_audio_values:
        audio_refs = extract_audio_references(value)
        print(f"   Input: '{value}' -> Detected: {audio_refs}")


def is_safe_filename(filename: str) -> bool:
    """Copy of MediaFileRegistrar._is_safe_filename for testing."""
    if not filename or len(filename) > 255:
        return False
    safe_pattern = r"^[A-Za-z0-9](?!.*\.\.)[A-Za-z0-9._-]*[A-Za-z0-9_-]$"
    return re.match(safe_pattern, filename) is not None


def extract_audio_references(content: str) -> list[str]:
    """Copy of MediaFileRegistrar._extract_audio_references for testing."""
    audio_refs = []

    # Match [sound:filename.mp3] pattern (exclude empty filenames)
    audio_pattern = r"\[sound:([^]\s]+)\]"
    matches = re.findall(audio_pattern, content)
    audio_refs.extend(
        [
            match
            for match in matches
            if match.strip() and is_safe_filename(match.strip())
        ]
    )

    # Also detect raw audio filenames (for template compatibility)
    # Look for strings that are pure audio filenames
    content_stripped = content.strip()
    if (
        content_stripped.endswith((".mp3", ".wav", ".m4a", ".ogg"))
        and is_safe_filename(content_stripped)
        and "/" not in content_stripped
        and "\\" not in content_stripped
    ):
        audio_refs.append(content_stripped)

    return audio_refs


def extract_image_references(content: str) -> list[str]:
    """Copy of MediaFileRegistrar._extract_image_references for testing."""
    image_refs = []

    # Match <img src="filename.jpg"> pattern (various formats)
    img_pattern = r'<img[^>]+src=[\'"]([^>\'"]+)[\'"][^>]*>'
    matches = re.findall(img_pattern, content)
    image_refs.extend([match for match in matches if is_safe_filename(match)])

    # Also detect raw image filenames (for template compatibility)
    # Look for strings that are pure image filenames
    content_stripped = content.strip()
    if (
        content_stripped.endswith((".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"))
        and is_safe_filename(content_stripped)
        and "/" not in content_stripped
        and "\\" not in content_stripped
    ):
        image_refs.append(content_stripped)

    return image_refs


if __name__ == "__main__":
    test_media_detection()
