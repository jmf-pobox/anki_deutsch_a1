"""Tests for the audio enrichment process."""

import logging
import os
import shutil
from collections.abc import Generator
from pathlib import Path
from typing import cast

import pandas as pd  # type: ignore
import pytest

from langlearn.utils.audio_enricher import AudioEnricher


@pytest.fixture
def cleanup_audio_dir() -> Generator[None, None, None]:
    """Clean up test audio directories after tests."""
    yield
    if os.path.exists("data/test_audio"):
        shutil.rmtree("data/test_audio")


@pytest.fixture(autouse=True)
def setup_logging() -> None:
    """Set up logging for tests."""
    logging.getLogger("langlearn.utils.audio_enricher").setLevel(logging.INFO)


def test_enrich_adjectives_success(
    cleanup_audio_dir: None,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test successful enrichment of adjectives with audio."""
    caplog.set_level(logging.INFO)

    # Create a temporary CSV file
    csv_content = """word,english,example,comparative,superlative
groß,big/tall,Er ist sehr groß.,größer,am größten
klein,small,Meine Wohnung ist klein.,kleiner,am kleinsten"""

    csv_file = tmp_path / "test_adjectives.csv"
    csv_file.write_text(csv_content)

    # Create enricher and process
    enricher = AudioEnricher(audio_dir="data/test_audio")
    enricher.enrich_adjectives(csv_file)

    # Verify results
    assert os.path.exists("data/test_audio")

    # Read the updated CSV
    with open(csv_file) as f:
        content = f.read()
        assert "word_audio" in content
        assert "example_audio" in content
        assert ".mp3" in content  # Audio files should be generated with .mp3 extension

    # Check that audio files exist for both words and examples
    df = pd.read_csv(csv_file)
    for _, row in df.iterrows():
        word_audio = cast("str", row["word_audio"])
        example_audio = cast("str", row["example_audio"])
        assert os.path.exists(word_audio)
        assert os.path.exists(example_audio)

    # Verify logs
    assert "Starting audio enrichment for adjectives" in caplog.text
    assert "Successfully enriched adjectives CSV with audio files" in caplog.text


def test_enrich_adjectives_error_handling(
    cleanup_audio_dir: None,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test error handling during enrichment with invalid input."""
    caplog.set_level(logging.INFO)

    # Create a temporary CSV file with invalid content that should trigger
    # error handling
    csv_file = tmp_path / "test_adjectives.csv"
    csv_file.write_text(
        "word,english,example\n,,"
    )  # Empty values should trigger error handling

    # Create enricher and process
    enricher = AudioEnricher()
    enricher.enrich_adjectives(csv_file)

    # Verify error handling
    assert "Error enriching adjective" in caplog.text
