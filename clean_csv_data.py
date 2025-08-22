#!/usr/bin/env python3
"""Clean CSV files by removing English parenthetical content from German text."""

import csv
import re
import shutil
from pathlib import Path


def clean_german_text(text: str) -> str:
    """Remove English parenthetical content from German text.

    Examples:
    - "Fahr ab! (To depart!)" -> "Fahr ab!"
    - "die Wohnung (apartment), das Zimmer (room)" -> "die Wohnung, das Zimmer"
    """
    if not text:
        return text

    # Remove parenthetical content
    cleaned = re.sub(r"\s*\([^)]*\)", "", text)

    # Clean up extra whitespace and punctuation
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    # Clean up trailing commas or other punctuation artifacts
    cleaned = re.sub(r",\s*$", "", cleaned)
    cleaned = re.sub(r",\s*,", ",", cleaned)  # Remove double commas

    return cleaned


def clean_csv_file(file_path: Path, fields_to_clean: list[str]) -> int:
    """Clean a CSV file by removing English parenthetical content from specified fields.

    Args:
        file_path: Path to CSV file
        fields_to_clean: List of field names to clean

    Returns:
        Number of entries cleaned
    """
    print(f"\n🧹 Cleaning {file_path.name}...")

    # Create backup
    backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
    shutil.copy2(file_path, backup_path)
    print(f"   📋 Backup created: {backup_path.name}")

    cleaned_count = 0
    rows = []

    # Read and clean the file
    with open(file_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        for row in reader:
            row.copy()

            # Clean specified fields
            for field in fields_to_clean:
                if row.get(field):
                    original_text = row[field]
                    cleaned_text = clean_german_text(original_text)

                    if cleaned_text != original_text:
                        row[field] = cleaned_text
                        cleaned_count += 1
                        print(
                            f"   🔧 Row {len(rows) + 1}, {field}: '{original_text}' -> '{cleaned_text}'"
                        )

            rows.append(row)

    # Write cleaned data back
    with open(file_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"   ✅ Cleaned {cleaned_count} entries in {len(rows)} total rows")
    return cleaned_count


def main():
    """Clean all CSV files that have English parenthetical content."""
    print("🧽 Cleaning CSV files by removing English parenthetical content...")

    # Define which fields need cleaning in each file
    files_to_clean = {
        "data/verbs_unified.csv": ["example"],
        "data/nouns.csv": ["related"],
        "data/phrases.csv": [
            "phrase",
            "context",
        ],  # Check if these have parenthetical content
        "data/prepositions.csv": ["example1", "example2"],
        "data/other_pronouns.csv": ["example"],
        "data/personal_pronouns.csv": ["example"],
        "data/verbs.csv": ["example"],
    }

    total_cleaned = 0

    for file_path_str, fields in files_to_clean.items():
        file_path = Path(file_path_str)

        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue

        cleaned = clean_csv_file(file_path, fields)
        total_cleaned += cleaned

    print(f"\n🎉 Cleaning complete! Total entries cleaned: {total_cleaned}")
    print("\n📋 Backup files created with .backup extension")
    print("   You can restore from backups if needed")


if __name__ == "__main__":
    main()
