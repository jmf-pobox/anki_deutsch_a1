#!/usr/bin/env python3
"""Test script to reproduce negation field assignment issue."""

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from langlearn.backends.genanki_backend import GenkiBackend
from langlearn.cards.negation import NegationCardGenerator
from langlearn.models.negation import Negation, NegationType
from langlearn.services.template_service import TemplateService


def test_negation_field_assignment():
    """Test negation field assignment to identify the bug."""

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

    print(f"=== TESTING NEGATION CARD GENERATION FOR '{nie.word}' ===")

    # Create minimal setup for card generation (without actual media generation)
    backend = GenkiBackend()
    template_service = TemplateService(Path("src/langlearn/templates"))

    # Create card generator WITHOUT MediaManager to avoid actual file generation
    generator = NegationCardGenerator(backend, template_service, media_manager=None)

    # Test field extraction
    field_names = generator._get_field_names()
    base_fields = generator._extract_fields(nie)

    print(f"\nField names: {field_names}")
    print("\nBase fields after _extract_fields:")
    for i, (name, value) in enumerate(zip(field_names, base_fields, strict=False)):
        print(f"  [{i}] {name}: '{value}'")

    # Test media enhancement WITHOUT actual media manager
    enhanced_fields = generator._enhance_fields_with_media(nie, base_fields)

    print("\nEnhanced fields after _enhance_fields_with_media (no MediaManager):")
    for i, (name, value) in enumerate(zip(field_names, enhanced_fields, strict=False)):
        print(f"  [{i}] {name}: '{value}'")

    # Verify the field indices are correct
    print("\n=== FIELD INDEX VERIFICATION ===")
    for i, name in enumerate(field_names):
        print(f"Index {i}: {name}")


if __name__ == "__main__":
    test_negation_field_assignment()
