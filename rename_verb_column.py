#!/usr/bin/env python3
"""Rename 'meaning' column to 'english' in verbs_unified.csv."""

import csv
import shutil
from pathlib import Path


def rename_column():
    """Rename meaning column to english in verbs_unified.csv."""
    file_path = Path("data/verbs_unified.csv")

    print(f"🔧 Renaming 'meaning' column to 'english' in {file_path.name}...")

    # Create backup
    backup_path = file_path.with_suffix(f"{file_path.suffix}.column_rename_backup")
    shutil.copy2(file_path, backup_path)
    print(f"   📋 Backup created: {backup_path.name}")

    # Read and update the file
    rows = []
    with open(file_path, encoding="utf-8") as f:
        reader = csv.reader(f)

        # Update header
        header = next(reader)
        if "meaning" in header:
            header_index = header.index("meaning")
            header[header_index] = "english"
            print(f"   ✅ Updated header: {','.join(header)}")
        else:
            print("   ⚠️  'meaning' column not found in header")
            return

        rows.append(header)

        # Copy all data rows
        for row in reader:
            rows.append(row)

    # Write back to file
    with open(file_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print(f"   ✅ Column renamed successfully in {len(rows) - 1} total rows")
    print(f"   📋 Backup available at: {backup_path}")


if __name__ == "__main__":
    rename_column()
