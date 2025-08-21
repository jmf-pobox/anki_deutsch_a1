#!/usr/bin/env python3
"""Test script to debug verb processing issue."""

import logging
from pathlib import Path

from src.langlearn.services.card_builder import CardBuilder
from src.langlearn.services.record_mapper import RecordMapper
from src.langlearn.services.template_service import TemplateService

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG, format="%(name)s - %(levelname)s: %(message)s")

# Step 1: Load verb records
print("=== STEP 1: Loading Verb Records ===")
mapper = RecordMapper()
verb_records = mapper.load_records_from_csv("data/verbs.csv")
print(f"Loaded {len(verb_records)} verb records")
print(f"First record type: {type(verb_records[0]).__name__}")
print(f"First record data: {verb_records[0].to_dict()}")

# Step 2: Test card building
print("\n=== STEP 2: Building Card from Verb Record ===")
template_dir = Path("src/langlearn/templates")
template_service = TemplateService(template_dir)
card_builder = CardBuilder(template_service=template_service)

# Check if verb is supported
supported = card_builder.get_supported_record_types()
print(f"Supported types: {supported}")
print(f"Verb supported: {'verb' in supported}")

# Validate first verb record
is_valid = card_builder.validate_record_for_card_building(verb_records[0])
print(f"First verb record valid for card building: {is_valid}")

# Try to build a card from the first verb
try:
    field_values, note_type = card_builder.build_card_from_record(verb_records[0])
    print("Successfully built card!")
    print(f"Note type: {note_type.name}")
    print(f"Fields: {note_type.fields}")
    print(f"Field values: {field_values}")
except Exception as e:
    print(f"ERROR building card: {e}")
    import traceback

    traceback.print_exc()

# Step 3: Check template loading
print("\n=== STEP 3: Template Check ===")
try:
    verb_template = template_service.get_template("verb")
    print("Verb template loaded successfully")
    print(f"Template front: {verb_template.front[:100]}...")
    print(f"Template back: {verb_template.back[:100]}...")
except Exception as e:
    print(f"ERROR loading verb template: {e}")
