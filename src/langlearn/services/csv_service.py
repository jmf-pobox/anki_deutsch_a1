"""Generic CSV data provider service for German language learning."""

import csv
import logging
import logging.handlers
from pathlib import Path
from typing import TypeVar

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Add file handler for csv.log
file_handler = logging.handlers.RotatingFileHandler(
    log_dir / "csv.log", maxBytes=1024 * 1024, backupCount=5  # 1MB
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(file_handler)

# Add console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logger.addHandler(console_handler)

T = TypeVar("T")


class CSVService:
    """Generic CSV service for reading data files."""

    def read_csv(self, file_path: Path, model_class: type[T]) -> list[T]:
        """Read data from a CSV file and convert to specified model type.

        Args:
            file_path: Path to the CSV file
            model_class: Pydantic model class to convert rows to

        Returns:
            List of model instances parsed from the CSV file

        Raises:
            FileNotFoundError: If the CSV file doesn't exist
            csv.Error: If there's an error parsing the CSV file
            ValidationError: If the CSV data doesn't match the model schema
        """
        logger.info("Reading data from %s", file_path)
        items: list[T] = []
        try:
            with open(file_path, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert empty strings to None for optional fields
                    cleaned_row = {k: v if v != "" else None for k, v in row.items()}
                    item = model_class(**cleaned_row)
                    items.append(item)
            logger.info("Successfully read %d items from %s", len(items), file_path)
            return items
        except FileNotFoundError:
            logger.error("CSV file not found: %s", file_path)
            raise
        except csv.Error as e:
            logger.error("Error reading CSV file %s: %s", file_path, e)
            raise
        except Exception as e:
            logger.error("Unexpected error reading data from %s: %s", file_path, e)
            raise
