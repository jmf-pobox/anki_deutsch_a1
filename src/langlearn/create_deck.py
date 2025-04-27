#!/usr/bin/env python3
"""
Script to create Anki German A1 deck from CSV files.
"""

import os
from pathlib import Path

from langlearn.generator import AnkiDeckGenerator


def main() -> None:
    """Create an Anki deck from the CSV files in the data directory."""
    # Get the path to the data directory
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent.parent  # Changed to go up two levels to reach project root
    data_dir = project_dir / "data"
    output_dir = project_dir / "output"

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Create deck
    generator = AnkiDeckGenerator("German A1 Adjectives")

    # Load adjectives
    adjectives_file = data_dir / "adjectives.csv"
    if adjectives_file.exists():
        print(f"Loading adjectives from {adjectives_file}")
        generator.load_from_csv(str(adjectives_file), "adjective")
    else:
        print(f"Warning: {adjectives_file} not found")

    # Temporarily comment out other word types
    """
    # Load nouns
    nouns_file = data_dir / "nouns.csv"
    if nouns_file.exists():
        print(f"Loading nouns from {nouns_file}")
        generator.load_from_csv(str(nouns_file), "noun")
    else:
        print(f"Warning: {nouns_file} not found")

    # Load verbs
    verbs_file = data_dir / "verbs.csv"
    if verbs_file.exists():
        print(f"Loading verbs from {verbs_file}")
        generator.load_from_csv(str(verbs_file), "verb")
    else:
        print(f"Warning: {verbs_file} not found")

    # Load prepositions
    prepositions_file = data_dir / "prepositions.csv"
    if prepositions_file.exists():
        print(f"Loading prepositions from {prepositions_file}")
        generator.load_from_csv(str(prepositions_file), "preposition")
    else:
        print(f"Warning: {prepositions_file} not found")

    # Load phrases
    phrases_file = data_dir / "phrases.csv"
    if phrases_file.exists():
        print(f"Loading phrases from {phrases_file}")
        generator.load_from_csv(str(phrases_file), "phrase")
    else:
        print(f"Warning: {phrases_file} not found")
    """

    # Save the deck
    output_file = output_dir / "German_A1_Adjectives.apkg"
    generator.save_deck(str(output_file))
    print(f"Deck saved to {output_file}")


if __name__ == "__main__":
    main()
