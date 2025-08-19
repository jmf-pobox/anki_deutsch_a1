#!/usr/bin/env python3
"""Test script to verify duplicate image fix for nie/niemals."""

import logging
from pathlib import Path

from langlearn.backends.anki_backend import AnkiBackend
from langlearn.cards.negation import NegationCardGenerator
from langlearn.managers.media_manager import MediaManager
from langlearn.models.negation import Negation
from langlearn.services.csv_service import CSVService
from langlearn.services.media_service import MediaService

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)


def test_duplicate_fix():
    """Test duplicate image handling for nie/niemals cards."""

    # Load only nie and niemals entries for focused testing
    csv_service = CSVService()
    negations = csv_service.read_csv(Path("data/negations.csv"), Negation)

    # Filter for nie and niemals only
    test_negations = [n for n in negations if n.word in ("nie", "niemals")]
    logger.info(
        f"Testing with {len(test_negations)} negations: {[n.word for n in test_negations]}"
    )

    if len(test_negations) != 2:
        logger.error(f"Expected 2 negations (nie, niemals), got {len(test_negations)}")
        return

    # Setup components
    backend = AnkiBackend("Duplicate Fix Test")
    media_service = MediaService()
    media_manager = MediaManager(backend, media_service)
    card_generator = NegationCardGenerator(backend, media_manager)

    logger.info("🧪 Starting duplicate image fix test...")

    # Generate cards for both nie and niemals
    for negation in test_negations:
        logger.info(f"\n🔄 Processing: {negation.word}")
        try:
            card_generator.generate_card(negation, generate_media=True)
            logger.info(f"✅ Successfully generated card for: {negation.word}")
        except Exception as e:
            logger.error(f"❌ Failed to generate card for {negation.word}: {e}")

    # Get media statistics
    stats = media_manager.get_media_stats()
    logger.info("\n📊 Media Statistics:")
    logger.info(f"   Files added: {stats.files_added}")
    logger.info(f"   Duplicates handled: {stats.duplicates_skipped}")
    logger.info(f"   Unique files: {stats.unique_files}")

    # Save test deck
    output_path = "duplicate_fix_test.apkg"
    backend.save_deck(output_path)
    logger.info(f"\n💾 Test deck saved as: {output_path}")

    # Verify file existence and sizes
    logger.info("\n🔍 File Analysis:")
    nie_path = Path("data/images/nie.jpg")
    niemals_path = Path("data/images/niemals.jpg")

    if nie_path.exists() and niemals_path.exists():
        nie_size = nie_path.stat().st_size
        niemals_size = niemals_path.stat().st_size
        logger.info(f"   nie.jpg size: {nie_size} bytes")
        logger.info(f"   niemals.jpg size: {niemals_size} bytes")
        logger.info(f"   Files identical: {nie_size == niemals_size}")

        # Calculate hashes to confirm
        import hashlib

        def get_file_hash(path):
            with open(path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()

        nie_hash = get_file_hash(nie_path)
        niemals_hash = get_file_hash(niemals_path)
        logger.info(f"   nie.jpg hash: {nie_hash[:16]}...")
        logger.info(f"   niemals.jpg hash: {niemals_hash[:16]}...")
        logger.info(f"   Hashes identical: {nie_hash == niemals_hash}")

    logger.info("\n✅ Duplicate fix test completed!")


if __name__ == "__main__":
    test_duplicate_fix()
