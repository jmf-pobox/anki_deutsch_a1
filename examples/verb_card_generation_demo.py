"""Demo script for multi-card verb generation.

This script demonstrates the new verb card generation modernization,
showing how we transform from 1 card per verb to 3-4 tense-specific cards.
"""

import logging
from pathlib import Path

from langlearn.models.records import VerbConjugationRecord
from langlearn.services.card_builder import CardBuilder
from langlearn.services.record_mapper import RecordMapper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sample_verb_data() -> list[VerbConjugationRecord]:
    """Create sample VerbConjugationRecord instances for testing."""

    sample_data = [
        # Present tense "gehen" (irregular, motion verb)
        VerbConjugationRecord(
            infinitive="gehen",
            meaning="to go",
            classification="unregelmäßig",
            separable=False,
            auxiliary="sein",
            tense="present",
            ich="gehe",
            du="gehst",
            er="geht",
            wir="gehen",
            ihr="geht",
            sie="gehen",
            example="Ich gehe nach Hause.",
        ),
        # Perfect tense "gehen"
        VerbConjugationRecord(
            infinitive="gehen",
            meaning="to go",
            classification="unregelmäßig",
            separable=False,
            auxiliary="sein",
            tense="perfect",
            ich="",
            du="",
            er="",
            wir="",
            ihr="",
            sie="gegangen",  # Perfect tense stored in sie field
            example="Ich bin nach Hause gegangen.",
        ),
        # Imperative "gehen"
        VerbConjugationRecord(
            infinitive="gehen",
            meaning="to go",
            classification="unregelmäßig",
            separable=False,
            auxiliary="sein",
            tense="imperative",
            ich="",
            du="geh",  # du-form imperative
            er="",
            wir="gehen wir",  # wir-form imperative
            ihr="geht",  # ihr-form imperative
            sie="gehen Sie",  # Sie-form imperative
            example="Geh nach Hause!",
        ),
        # Present tense "machen" (regular verb)
        VerbConjugationRecord(
            infinitive="machen",
            meaning="to make/do",
            classification="regelmäßig",
            separable=False,
            auxiliary="haben",
            tense="present",
            ich="mache",
            du="machst",
            er="macht",
            wir="machen",
            ihr="macht",
            sie="machen",
            example="Ich mache Hausaufgaben.",
        ),
        # Perfect tense "machen"
        VerbConjugationRecord(
            infinitive="machen",
            meaning="to make/do",
            classification="regelmäßig",
            separable=False,
            auxiliary="haben",
            tense="perfect",
            ich="",
            du="",
            er="",
            wir="",
            ihr="",
            sie="gemacht",  # Perfect participle
            example="Ich habe Hausaufgaben gemacht.",
        ),
        # Imperative "machen"
        VerbConjugationRecord(
            infinitive="machen",
            meaning="to make/do",
            classification="regelmäßig",
            separable=False,
            auxiliary="haben",
            tense="imperative",
            ich="",
            du="mach",
            er="",
            wir="machen wir",
            ihr="macht",
            sie="machen Sie",
            example="Mach deine Hausaufgaben!",
        ),
    ]

    return sample_data


def demo_verb_card_generation():
    """Demonstrate multi-card generation from verb records."""

    logger.info("🚀 Starting Verb Card Generation Demo")

    # Create sample verb data
    verb_records = create_sample_verb_data()
    logger.info(f"Created {len(verb_records)} verb records")

    # Group by verb to show the transformation
    verbs = {}
    for record in verb_records:
        if record.infinitive not in verbs:
            verbs[record.infinitive] = []
        verbs[record.infinitive].append(record)

    logger.info("📊 Data Summary:")
    for verb, records in verbs.items():
        tenses = [r.tense for r in records]
        logger.info(f"  • {verb}: {len(records)} tenses ({', '.join(tenses)})")

    # Initialize CardBuilder with correct template path
    project_root = Path(__file__).parent.parent
    card_builder = CardBuilder(project_root=project_root)

    # Generate multi-tense cards
    logger.info("\n🎴 Generating Multi-Tense Cards...")
    cards = card_builder.build_verb_conjugation_cards(verb_records)

    logger.info(f"✅ Generated {len(cards)} cards from {len(verbs)} verbs")

    # Analyze card generation results
    logger.info("\n📈 Card Generation Results:")
    for i, (field_values, note_type) in enumerate(cards, 1):
        # Extract key information from card
        infinitive = field_values[0] if field_values else "Unknown"
        tense = "Unknown"

        # Determine tense from note type or field content
        if "imperative" in note_type.name.lower():
            tense = "Imperative"
        elif len(field_values) > 5 and field_values[5]:  # Tense field in conjugation
            tense = field_values[5].title()

        logger.info(f"  Card {i}: {infinitive} ({tense}) - {len(field_values)} fields")
        logger.info(f"    Template: {note_type.name}")
        logger.info(f"    Fields: {len(field_values)} values")

        # Show first few field values for verification
        if field_values:
            preview = field_values[:3]
            logger.info(f"    Preview: {preview}")

    # Demonstrate the transformation
    logger.info("\n🎯 Transformation Summary:")
    logger.info(
        f"  📝 Old System: {len(verbs)} verbs → {len(verbs)} cards (1 per verb)"
    )
    logger.info(
        f"  ✨ New System: {len(verbs)} verbs → {len(cards)} cards "
        f"({len(cards) / len(verbs):.1f} per verb)"
    )
    logger.info(
        f"  🚀 Improvement: {((len(cards) / len(verbs)) - 1) * 100:.0f}% "
        f"more learning content!"
    )

    return cards


def demo_record_mapper_integration():
    """Demonstrate RecordMapper integration with verb CSV data."""

    logger.info("\n🔗 Testing RecordMapper Integration...")

    # Check if verbs_unified.csv exists
    project_root = Path(__file__).parent.parent
    csv_path = project_root / "data" / "verbs_unified.csv"

    if not csv_path.exists():
        logger.warning(f"⚠️ CSV file not found: {csv_path}")
        logger.info("Skipping RecordMapper integration demo")
        return []

    # Initialize RecordMapper
    record_mapper = RecordMapper(project_root)

    try:
        # Load verb records from CSV
        logger.info(f"📂 Loading verb records from: {csv_path}")
        verb_records = record_mapper.load_records_from_csv(csv_path)

        logger.info(f"✅ Loaded {len(verb_records)} records from CSV")

        # Analyze loaded data
        if verb_records:
            tense_counts = {}
            verb_counts = {}

            for record in verb_records:
                if hasattr(record, "tense"):
                    tense_counts[record.tense] = tense_counts.get(record.tense, 0) + 1
                if hasattr(record, "infinitive"):
                    verb_counts[record.infinitive] = (
                        verb_counts.get(record.infinitive, 0) + 1
                    )

            logger.info("📊 Tense Distribution:")
            for tense, count in sorted(tense_counts.items()):
                logger.info(f"  • {tense}: {count} records")

            logger.info("📊 Verb Distribution:")
            unique_verbs = len(verb_counts)
            avg_tenses = len(verb_records) / unique_verbs if unique_verbs > 0 else 0
            logger.info(f"  • {unique_verbs} unique verbs")
            logger.info(f"  • {avg_tenses:.1f} average tenses per verb")

            # Test card generation with real data
            logger.info("\n🎴 Testing card generation with real CSV data...")
            card_builder = CardBuilder(project_root=project_root)

            # Use only the first few records for demo
            sample_records = verb_records[:12]  # 3-4 verbs worth
            cards = card_builder.build_verb_conjugation_cards(sample_records)

            logger.info(
                f"✅ Generated {len(cards)} cards from "
                f"{len(sample_records)} CSV records"
            )

            return cards

    except Exception as e:
        logger.error(f"❌ Error during RecordMapper integration: {e}")
        return []


if __name__ == "__main__":
    """Run the verb card generation demonstration."""

    print("=" * 60)
    print("🎓 German Verb Card Generation Modernization Demo")
    print("=" * 60)

    try:
        # Demo 1: Sample data generation
        sample_cards = demo_verb_card_generation()

        # Demo 2: Real CSV integration
        csv_cards = demo_record_mapper_integration()

        print("\n" + "=" * 60)
        print("✅ Demo Complete!")
        print(f"📊 Sample Cards Generated: {len(sample_cards)}")
        print(f"📊 CSV Cards Generated: {len(csv_cards)}")
        print("🚀 Verb card generation modernization is working!")
        print("=" * 60)

    except Exception as e:
        logger.error(f"❌ Demo failed with error: {e}")
        raise
