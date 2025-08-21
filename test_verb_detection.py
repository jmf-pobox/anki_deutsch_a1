#!/usr/bin/env python3
"""Quick test to verify verb CSV detection and loading."""

from pathlib import Path

from langlearn.services.record_mapper import RecordMapper


def test_verb_csv_detection():
    """Test that verb CSV files are detected correctly."""
    mapper = RecordMapper()

    csv_files = [
        "data/verbs.csv",
        "data/regular_verbs.csv",
        "data/irregular_verbs.csv",
        "data/separable_verbs.csv",
    ]

    for csv_file in csv_files:
        path = Path(csv_file)
        if path.exists():
            try:
                detected_type = mapper.detect_csv_record_type(path)
                print(f"{csv_file}: detected as '{detected_type}'")

                # Try to load records
                records = mapper.load_records_from_csv(path)
                print(f"  → Loaded {len(records)} records")
                if records:
                    print(f"  → First record type: {type(records[0]).__name__}")
            except Exception as e:
                print(f"{csv_file}: ERROR - {e}")
        else:
            print(f"{csv_file}: File not found")


if __name__ == "__main__":
    test_verb_csv_detection()
