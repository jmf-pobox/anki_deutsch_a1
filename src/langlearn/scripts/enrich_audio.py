#!/usr/bin/env python3
"""Script to enrich CSV files with audio files."""

import logging
from pathlib import Path

from langlearn.utils.audio_enricher import AudioEnricher

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run the audio enrichment process."""
    try:
        # Initialize the audio enricher
        enricher = AudioEnricher()

        # Path to the adjectives CSV file
        csv_file = Path("data/adjectives.csv")

        # Enrich the adjectives with audio
        logger.info("Starting audio enrichment for adjectives")
        enricher.enrich_adjectives(csv_file)
        logger.info("Audio enrichment completed successfully")

    except Exception as e:
        logger.error("Error during audio enrichment: %s", str(e))
        raise


if __name__ == "__main__":
    main()
