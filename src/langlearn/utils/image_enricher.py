"""Image enrichment service for generating and managing image assets."""

import logging
import shutil
import time
from datetime import datetime
from pathlib import Path

import pandas as pd  # type: ignore

from langlearn.models.adjective import Adjective
from langlearn.services.anthropic_service import AnthropicService
from langlearn.services.pexels_service import PexelsService

logger = logging.getLogger(__name__)


class ImageEnricher:
    """Service for enriching data with image assets."""

    def __init__(
        self, images_dir: str = "data/images", rate_limit_ms: int = 500
    ) -> None:
        """Initialize the ImageEnricher.

        Args:
            images_dir: Directory to store image files
            rate_limit_ms: Delay in milliseconds between API calls
        """
        self.images_dir = Path(images_dir).absolute()
        self.anthropic_service = AnthropicService()
        self.pexels_service = PexelsService()
        self.rate_limit_ms = rate_limit_ms
        self._setup_directories()

    def _setup_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        self.images_dir.mkdir(parents=True, exist_ok=True)

    def _backup_csv(self, csv_file: Path) -> Path:
        """Create a backup of the CSV file before processing.

        Args:
            csv_file: Path to the CSV file to backup

        Returns:
            Path to the backup file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = csv_file.parent / "backups"
        backup_dir.mkdir(exist_ok=True)

        backup_file = backup_dir / f"{csv_file.stem}_{timestamp}{csv_file.suffix}"
        shutil.copy2(csv_file, backup_file)
        logger.info("Created backup of CSV file at: %s", backup_file)
        return backup_file

    def _rate_limit(self) -> None:
        """Sleep for the configured rate limit duration."""
        time.sleep(self.rate_limit_ms / 1000.0)

    def enrich_adjectives(self, csv_file: Path) -> None:
        """Enrich adjectives with image files.

        Args:
            csv_file: Path to the adjectives CSV file
        """
        logger.info("Starting image enrichment for adjectives")

        try:
            # Create backup before processing
            self._backup_csv(csv_file)

            # Read the CSV file
            df = pd.read_csv(csv_file)  # type: ignore

            # Add image_path column if it doesn't exist
            if "image_path" not in df.columns:
                df["image_path"] = ""

            # Process each adjective
            for index, row in df.iterrows():
                try:
                    # Create a model instance for the Anthropic service
                    model = Adjective(
                        word=row["word"],  # type: ignore
                        english=row["english"],  # type: ignore
                        example=row["example"],  # type: ignore
                        comparative=row["comparative"],  # type: ignore
                        superlative=row.get("superlative", None),  # type: ignore
                    )

                    # Generate image filename
                    image_filename = f"{row['word']}.jpg"
                    image_path = self.images_dir / image_filename

                    # Only download if image doesn't exist
                    if not image_path.exists():
                        # Generate search query using the example text
                        search_query = self.anthropic_service.generate_pexels_query(
                            model
                        )
                        logger.debug("Generated search query: %s", search_query)
                        self._rate_limit()  # Rate limit between API calls

                        # Download the image
                        if self.pexels_service.download_image(
                            search_query, str(image_path)
                        ):
                            # Use absolute path when storing in CSV
                            df.at[index, "image_path"] = str(image_path.absolute())
                            logger.debug(
                                "Successfully enriched adjective: %s with image",
                                row["word"],  # type: ignore
                            )
                        else:
                            logger.error(
                                "Failed to download image for adjective: %s",
                                row["word"],  # type: ignore
                            )
                        self._rate_limit()  # Rate limit between API calls
                    else:
                        logger.debug(
                            "Image already exists for adjective: %s",
                            row["word"],  # type: ignore
                        )

                except Exception as e:
                    logger.error(
                        "Error enriching adjective %s: %s",
                        row["word"],  # type: ignore
                        str(e),
                    )

            # Save the updated CSV
            df.to_csv(csv_file, index=False)  # type: ignore
            logger.info("Successfully enriched adjectives CSV with images")

        except Exception as e:
            logger.error("Error during adjective enrichment: %s", str(e))
            raise
