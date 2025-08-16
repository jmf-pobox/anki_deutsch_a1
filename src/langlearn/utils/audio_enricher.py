"""Audio enrichment service for generating and managing audio assets."""

import logging
import shutil
from datetime import datetime
from pathlib import Path

import pandas as pd  # type: ignore
from pandas import DataFrame  # type: ignore

from langlearn.services.audio import AudioService
from langlearn.services.csv_service import CSVService

logger = logging.getLogger(__name__)


class AudioEnricher:
    """Service for enriching data with audio assets."""

    def __init__(self, audio_dir: str = "data/audio") -> None:
        """Initialize the AudioEnricher.

        Args:
            audio_dir: Directory to store audio files
        """
        self.audio_dir = Path(audio_dir)
        self.audio_service = AudioService(output_dir=str(self.audio_dir))
        self.csv_service = CSVService()
        self._setup_directories()

    def _setup_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        self.audio_dir.mkdir(parents=True, exist_ok=True)

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

    def enrich_adjectives(self, csv_file: Path) -> None:
        """Enrich adjectives with audio files.

        Args:
            csv_file: Path to the adjectives CSV file
        """
        logger.info("Starting audio enrichment for adjectives")

        try:
            # Create backup before processing
            self._backup_csv(csv_file)

            # Read the CSV file
            df: DataFrame = pd.read_csv(csv_file)

            # Add new columns if they don't exist
            if "word_audio" not in df.columns:
                df["word_audio"] = ""
            if "example_audio" not in df.columns:
                df["example_audio"] = ""

            # Process each adjective
            for index, row in df.iterrows():
                try:
                    # Skip rows with empty values
                    if pd.isna(row["word"]) or pd.isna(row["example"]):
                        logger.error("Error enriching adjective: empty word or example")
                        continue

                    # Check if word audio exists
                    word_audio_path_str = (
                        str(row["word_audio"]) if pd.notna(row["word_audio"]) else ""  # type: ignore
                    )
                    word_audio_path = (
                        Path(word_audio_path_str) if word_audio_path_str else None
                    )
                    if not word_audio_path or not word_audio_path.exists():
                        word_audio_path = self.audio_service.generate_audio(
                            str(row["word"])  # type: ignore
                        )
                        df.at[index, "word_audio"] = str(word_audio_path)
                        logger.debug(
                            "Generated new word audio for: %s",
                            str(row["word"]),  # type: ignore
                        )
                    else:
                        logger.debug(
                            "Using existing word audio for: %s",
                            str(row["word"]),  # type: ignore
                        )

                    # Check if example audio exists
                    example_audio_path_str = (
                        str(row["example_audio"])  # type: ignore
                        if pd.notna(row["example_audio"])  # type: ignore
                        else ""
                    )
                    example_audio_path = (
                        Path(example_audio_path_str) if example_audio_path_str else None
                    )
                    if not example_audio_path or not example_audio_path.exists():
                        example_audio_path = self.audio_service.generate_audio(
                            str(row["example"])  # type: ignore
                        )
                        df.at[index, "example_audio"] = str(example_audio_path)
                        logger.debug(
                            "Generated new example audio for: %s",
                            str(row["word"]),  # type: ignore
                        )
                    else:
                        logger.debug(
                            "Using existing example audio for: %s",
                            str(row["word"]),  # type: ignore
                        )

                except Exception as e:
                    logger.error(
                        "Error enriching adjective %s: %s",
                        str(row["word"]),
                        str(e),  # type: ignore
                    )

            # Save the updated CSV
            df.to_csv(csv_file, index=False)  # type: ignore
            logger.info("Successfully enriched adjectives CSV with audio files")

        except Exception as e:
            logger.error("Error during adjective enrichment: %s", str(e))
            raise
