"""Utility for inspecting Anki deck contents in tests."""

from __future__ import annotations

import sqlite3
import tempfile
import zipfile
from pathlib import Path
from typing import Any


class DeckInspector:
    """Utility for inspecting the contents of Anki deck files."""

    def __init__(self, deck_path: str | Path) -> None:
        """Initialize with path to deck file."""
        self.deck_path = Path(deck_path)
        if not self.deck_path.exists():
            raise FileNotFoundError(f"Deck file not found: {deck_path}")

    def extract_and_inspect(self) -> dict[str, Any]:
        """Extract deck and return inspection results."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Extract the .apkg file
            with zipfile.ZipFile(self.deck_path, "r") as zip_ref:
                zip_ref.extractall(temp_path)

            extracted_files = list(temp_path.iterdir())
            db_path = temp_path / "collection.anki2"

            results = {
                "extracted_files": [f.name for f in extracted_files],
                "media_files": [],
                "notes": [],
                "note_count": 0,
            }

            # Find media files
            results["media_files"] = [
                f.name
                for f in extracted_files
                if f.suffix.lower() in {".jpg", ".jpeg", ".png", ".mp3", ".wav"}
            ]

            # Inspect database if it exists
            if db_path.exists():
                results.update(self._inspect_database(db_path))

            return results

    def _inspect_database(self, db_path: Path) -> dict[str, Any]:
        """Inspect the SQLite database inside the Anki deck."""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            # Get table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [table[0] for table in cursor.fetchall()]

            # Count notes
            cursor.execute("SELECT COUNT(*) FROM notes;")
            note_count = cursor.fetchone()[0]

            # Get all notes with field contents
            cursor.execute("SELECT id, mid, flds FROM notes;")
            notes_data = cursor.fetchall()

            notes = []
            for note_id, model_id, fields_blob in notes_data:
                # Fields are stored as \x1f separated values in Anki
                field_values = fields_blob.split("\x1f")
                notes.append(
                    {"id": note_id, "model_id": model_id, "field_values": field_values}
                )

            return {
                "tables": tables,
                "note_count": note_count,
                "notes": notes,
            }

        except Exception as e:
            return {"tables": [], "note_count": 0, "notes": [], "db_error": str(e)}
        finally:
            conn.close()

    def get_media_file_count(self) -> int:
        """Get count of media files in the deck."""
        results = self.extract_and_inspect()
        return len(results["media_files"])

    def get_note_field_values(self) -> list[list[str]]:
        """Get field values for all notes."""
        results = self.extract_and_inspect()
        return [note["field_values"] for note in results["notes"]]

    def has_media_in_fields(self) -> bool:
        """Check if any note fields contain media references."""
        field_values = self.get_note_field_values()
        for note_fields in field_values:
            for field in note_fields:
                if any(
                    media_tag in field
                    for media_tag in ["<img", "[sound:", ".jpg", ".mp3"]
                ):
                    return True
        return False

    def validate_deck_structure(self) -> dict[str, bool]:
        """Validate expected deck structure."""
        results = self.extract_and_inspect()

        return {
            "has_database": "collection.anki2" in results["extracted_files"],
            "has_media_files": len(results["media_files"]) > 0,
            "has_notes": results["note_count"] > 0,
            "has_media_references": self.has_media_in_fields(),
        }
