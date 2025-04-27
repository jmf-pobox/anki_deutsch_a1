#!/usr/bin/env python3
"""Script to enrich CSV files with image files."""

import logging
from pathlib import Path

from langlearn.utils.image_enricher import ImageEnricher

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run the image enrichment process."""
    try:
        # Initialize the image enricher
        enricher = ImageEnricher()

        # Path to the adjectives CSV file
        csv_file = Path("data/adjectives.csv")

        # Enrich the adjectives with images
        logger.info("Starting image enrichment for adjectives")
        enricher.enrich_adjectives(csv_file)
        logger.info("Image enrichment completed successfully")

    except Exception as e:
        logger.error("Error during image enrichment: %s", str(e))
        raise


if __name__ == "__main__":
    main()
