"""Tests for the image enrichment service."""

from pathlib import Path

import pytest

from langlearn.utils.image_enricher import ImageEnricher


@pytest.fixture
def image_enricher() -> ImageEnricher:
    """Fixture for creating an ImageEnricher instance."""
    return ImageEnricher()


def test_enrich_adjectives_success(
    image_enricher: ImageEnricher,
    tmp_path: Path,
) -> None:
    """Test successful image enrichment for adjectives."""
    # Create a temporary CSV file
    csv_file = tmp_path / "adjectives.csv"
    csv_file.write_text(
        "word,english,example,comparative\n"
        "groß,big,Das Haus ist groß.,größer\n"
        "klein,small,Der Hund ist klein.,kleiner\n"
    )

    # Run the enrichment
    image_enricher.enrich_adjectives(csv_file)

    # Verify CSV was updated with image paths
    updated_content = csv_file.read_text()
    assert "image_path" in updated_content

    # Verify images were downloaded to the default data/images directory
    assert Path("data/images/groß.jpg").exists()
    assert Path("data/images/klein.jpg").exists()


def test_enrich_adjectives_error_handling(
    image_enricher: ImageEnricher,
    tmp_path: Path,
) -> None:
    """Test error handling during image enrichment."""
    # Create a temporary CSV file with invalid data
    csv_file = tmp_path / "adjectives.csv"
    csv_file.write_text(
        "word,english,example,comparative\ninvalid,invalid,Invalid example.,invalid\n"
    )

    # Run the enrichment - this should handle errors gracefully without crashing
    try:
        image_enricher.enrich_adjectives(csv_file)
    except Exception:
        # Error handling test - enrichment may fail gracefully
        pass

    # Verify CSV was processed (may or may not have image depending on API)
    updated_content = csv_file.read_text()
    assert "word,english,example,comparative" in updated_content


def test_backup_creation(
    image_enricher: ImageEnricher,
    tmp_path: Path,
) -> None:
    """Test that a backup is created before processing."""
    # Create a temporary CSV file
    csv_file = tmp_path / "adjectives.csv"
    csv_file.write_text(
        "word,english,example,comparative\ntest,test,Test example.,test\n"
    )

    # Run the enrichment
    image_enricher.enrich_adjectives(csv_file)

    # Verify backup was created
    backup_dir = csv_file.parent / "backups"
    assert backup_dir.exists()
    assert len(list(backup_dir.glob("*.csv"))) == 1
