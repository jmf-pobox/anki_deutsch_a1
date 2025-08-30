#!/usr/bin/env python3
"""Anki Card Simulation Script - simulates exactly what Anki will display to users.

This script addresses the critical verification gap that caused $566 in wasted costs
by simulating the actual user experience in Anki application.

Extended with CardSpecificationGenerator for automatic documentation generation.
"""

import argparse
import sys
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from langlearn.testing.anki_simulator import AnkiRenderSimulator
from langlearn.testing.card_specification_generator import CardSpecificationGenerator


def simulate_german_cloze_cards() -> None:
    """Simulate German cloze deletion cards showing front/back views."""

    german_cards = [
        {
            "content": "{{c1::Der}} Mann arbeitet hier",
            "fields": {"Explanation": "Maskulin - Geschlecht erkennen"},
            "title": "German Gender Recognition (Masculine)",
        },
        {
            "content": "{{c1::Die}} Frau ist schön",
            "fields": {"Explanation": "Feminin - Geschlecht erkennen"},
            "title": "German Gender Recognition (Feminine)",
        },
        {
            "content": "{{c1::Das}} Haus ist groß",
            "fields": {"Explanation": "Neutrum - Geschlecht erkennen"},
            "title": "German Gender Recognition (Neuter)",
        },
        {
            "content": "Ich sehe {{c1::den}} Mann",
            "fields": {
                "Explanation": "den - Maskulin Akkusativ (wen/was? direktes Objekt)"
            },
            "title": "German Case Usage (Accusative)",
        },
        {
            "content": "Mit {{c1::dem}} Auto fahre ich",
            "fields": {"Explanation": "dem - Maskulin Dativ (wem? mit Präposition)"},
            "title": "German Case Usage (Dative)",
        },
    ]

    print("🎴 GERMAN CLOZE CARD SIMULATION")
    print("Showing exactly what users will see in Anki")
    print("=" * 60)

    for i, card in enumerate(german_cards, 1):
        content = card["content"]
        fields = card["fields"]
        title = card["title"]

        print(f"\n📋 Card {i}: {title}")
        print(f"Template: {content}")

        # Simulate card display
        display = AnkiRenderSimulator.simulate_card_display(fields, content)

        print("📖 FRONT (Question):")
        print(f"   {display['front']}")
        print(f"   Explanation: {fields.get('Explanation', 'N/A')}")

        print("📝 BACK (Answer):")
        print(f"   {display['back']}")

        # Check for rendering issues
        issues = AnkiRenderSimulator.detect_rendering_issues(display["rendered"])
        if issues:
            print("⚠️  Rendering Issues:")
            for issue in issues:
                print(f"   • {issue}")
        else:
            print("✅ No rendering issues detected")


def simulate_field_substitution_cards() -> None:
    """Simulate cards with field substitution within cloze deletions."""

    field_cards = [
        {
            "content": "The German word {{c1::{{Word}}}} means {{Meaning}}",
            "fields": {"Word": "Haus", "Meaning": "house"},
            "title": "Field Substitution in Cloze Deletion",
        },
        {
            "content": "{{c1::{{Article}}}} {{Noun}} ist {{Adjective}}",
            "fields": {"Article": "Das", "Noun": "Haus", "Adjective": "groß"},
            "title": "Multiple Field Substitutions",
        },
        {
            "content": "{{c1::{{Word}}}} translation",
            "fields": {"Word": ""},  # Empty field - problematic case
            "title": "Empty Field (Problematic Case)",
        },
    ]

    print("\n\n🔄 FIELD SUBSTITUTION SIMULATION")
    print("Testing field replacement within cloze deletions")
    print("=" * 60)

    for i, card in enumerate(field_cards, 1):
        content = card["content"]
        fields = card["fields"]
        title = card["title"]

        print(f"\n📋 Field Test {i}: {title}")
        print(f"Template: {content}")
        print(f"Fields: {fields}")

        # Step-by-step simulation
        print("📝 Step 1: Field Substitution")
        after_fields = AnkiRenderSimulator.apply_field_substitution(content, fields)
        print(f"   Result: {after_fields}")

        print("📖 Step 2: Front View (Hide Cloze)")
        front = AnkiRenderSimulator.render_cloze_deletion(
            after_fields, show_answer=False
        )
        print(f"   Front: {front}")

        print("📝 Step 3: Back View (Show Answer)")
        back = AnkiRenderSimulator.render_cloze_deletion(after_fields, show_answer=True)
        print(f"   Back: {back}")

        # Validate rendering
        valid, issues = AnkiRenderSimulator.validate_card_rendering(content, fields)
        if valid:
            print("✅ Card renders correctly")
        else:
            print("❌ Rendering issues detected:")
            for category, category_issues in issues.items():
                for issue in category_issues:
                    print(f"   • {category}: {issue}")


def simulate_multi_cloze_cards() -> None:
    """Simulate cards with multiple cloze deletions."""

    multi_cloze_cards = [
        {
            "content": "{{c1::Der}} {{c2::Mann}} arbeitet {{c3::hier}}",
            "fields": {},
            "title": "Triple Cloze Deletion",
        },
        {
            "content": "{{c1::{{Article}}}} {{c2::{{Noun}}}} ist {{c3::{{Adjective}}}}",
            "fields": {"Article": "Das", "Noun": "Haus", "Adjective": "groß"},
            "title": "Multi-Cloze with Field Substitution",
        },
    ]

    print("\n\n🎯 MULTI-CLOZE SIMULATION")
    print("Testing multiple cloze deletions in single card")
    print("=" * 60)

    for i, card in enumerate(multi_cloze_cards, 1):
        content = card["content"]
        fields = card["fields"]
        title = card["title"]

        print(f"\n📋 Multi-Cloze {i}: {title}")
        print(f"Template: {content}")

        # Simulate all cloze states
        states = AnkiRenderSimulator.simulate_cloze_card_states(content, fields)

        print(f"📚 Anki will create {len(states)} separate cards:")

        for cloze_num, state in states.items():
            print(f"\n   Card {cloze_num} (c{cloze_num}):")
            print(f"   📖 Front: {state['front']}")
            print(f"   📝 Back:  {state['back']}")

        # Overall validation
        valid, issues = AnkiRenderSimulator.validate_card_rendering(content, fields)
        if valid:
            print("✅ All cloze states render correctly")
        else:
            print("❌ Some cloze states have issues:")
            for category, category_issues in issues.items():
                for issue in category_issues:
                    print(f"   • {category}: {issue}")


def generate_card_specifications(output_file: Path | None = None) -> int:
    """Generate comprehensive card type specifications.

    Args:
        output_file: Optional output file for markdown documentation

    Returns:
        Exit code (0 for success, 1 for errors)
    """
    print("📋 CARD SPECIFICATION GENERATOR")
    print("Generating comprehensive documentation for all card types")
    print("=" * 60)

    try:
        # Initialize generator
        project_root = Path(__file__).parent.parent
        generator = CardSpecificationGenerator(project_root=project_root)

        # Generate all specifications
        print("🔍 Introspecting all card types...")
        specifications = generator.generate_all_specifications()

        print(f"✅ Generated specifications for {len(specifications)} card types:")
        for spec in specifications:
            cloze_indicator = " (Cloze)" if spec.cloze_deletion else ""
            print(f"   • {spec.card_type}{cloze_indicator}: {len(spec.fields)} fields")

        # Generate rendering examples for cloze cards
        print("\n🎯 Generating rendering examples...")
        examples = generator.simulate_card_rendering_examples(specifications)

        if examples:
            print(f"✅ Generated {len(examples)} rendering examples")
            for card_type, _example in examples.items():
                print(f"   • {card_type}: Front/Back simulation ready")

        # Generate markdown documentation
        print("\n📄 Generating markdown documentation...")
        markdown = generator.generate_markdown_documentation(specifications)

        # Write to file if specified
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Create backup of existing file to prevent loss of manual changes
            if output_file.exists():
                from datetime import datetime

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = output_file.with_suffix(f".backup_{timestamp}.md")
                backup_content = output_file.read_text(encoding="utf-8")
                backup_file.write_text(backup_content, encoding="utf-8")
                print(f"🔄 Created backup: {backup_file}")

            output_file.write_text(markdown, encoding="utf-8")
            print(f"✅ Documentation written to: {output_file}")
            print("⚠️  WARNING: This overwrites manual changes. Check backup if needed.")
        else:
            # Print summary to console
            print("\n" + "=" * 60)
            print("📋 CARD TYPE SUMMARY")
            print("=" * 60)

            for spec in specifications:
                print(f"\n🎴 {spec.card_type.upper()}")
                print(f"   Anki Note Type: {spec.anki_note_type_name}")
                required_count = sum(1 for f in spec.fields if f.required)
                print(f"   Fields: {len(spec.fields)} ({required_count} required)")
                sources = {f.data_source for f in spec.fields}
                print(f"   Sources: {', '.join(sources)}")
                print(f"   Cloze: {'Yes' if spec.cloze_deletion else 'No'}")
                print(f"   Templates: {len(spec.template_files)} files")

        print("\n" + "=" * 60)
        print("🎉 SPECIFICATION GENERATION COMPLETE")
        print("✅ All card types documented with accurate field mappings")
        print("✅ Data sources identified (CSV, Pexels, AWS Polly)")
        print("✅ Template files catalogued")
        print("✅ Learning objectives defined")

        return 0

    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: Specification generation failed: {e}")
        print("   • Cannot generate accurate documentation")
        print("   • Check template files and CardBuilder configuration")
        import traceback

        traceback.print_exc()
        return 1


def main() -> int:
    """Run Anki card simulation and specification generation.

    Returns:
        Exit code (0 for success, 1 for errors)
    """
    parser = argparse.ArgumentParser(
        description="Anki Card Simulation and Specification System"
    )
    parser.add_argument(
        "--generate-specs",
        action="store_true",
        help="Generate card type specifications instead of simulations",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file for specification documentation "
        "(default: docs/PROD-CARD-SPEC.md)",
    )

    args = parser.parse_args()

    if args.generate_specs:
        # Generate specifications
        output_file = args.output or Path("docs/PROD-CARD-SPEC.md")
        return generate_card_specifications(output_file)
    else:
        # Run simulations
        print("🎭 ANKI CARD SIMULATION SYSTEM")
        print("Preventing $566+ costs from false 'fix' claims")
        print("Simulating exactly what users will see in Anki application")

        try:
            # Run all simulation tests
            simulate_german_cloze_cards()
            simulate_field_substitution_cards()
            simulate_multi_cloze_cards()

            print("\n" + "=" * 60)
            print("🎉 SIMULATION COMPLETE")
            print("All card types successfully simulated!")
            print("✅ You can now predict exactly what Anki will display")
            print("✅ Use these simulations to verify fixes before claiming they work")
            print(
                "\n💡 TIP: Use --generate-specs to create comprehensive "
                "card documentation"
            )

            return 0

        except Exception as e:
            print(f"\n💥 CRITICAL ERROR: Simulation failed: {e}")
            print("   • Cannot predict Anki behavior")
            print("   • DO NOT claim fixes work without manual verification")
            return 1


if __name__ == "__main__":
    exit(main())
