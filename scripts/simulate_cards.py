#!/usr/bin/env python3
"""Anki Card Simulation Script - simulates exactly what Anki will display to users.

This script addresses the critical verification gap that caused $566 in wasted costs
by simulating the actual user experience in Anki application.
"""

import sys
from pathlib import Path
from typing import Dict, List

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from langlearn.testing.anki_simulator import AnkiRenderSimulator


def simulate_german_cloze_cards() -> None:
    """Simulate German cloze deletion cards showing front/back views."""
    
    german_cards = [
        {
            "content": "{{c1::Der}} Mann arbeitet hier",
            "fields": {"Explanation": "Maskulin - Geschlecht erkennen"},
            "title": "German Gender Recognition (Masculine)"
        },
        {
            "content": "{{c1::Die}} Frau ist schön",
            "fields": {"Explanation": "Feminin - Geschlecht erkennen"},  
            "title": "German Gender Recognition (Feminine)"
        },
        {
            "content": "{{c1::Das}} Haus ist groß",
            "fields": {"Explanation": "Neutrum - Geschlecht erkennen"},
            "title": "German Gender Recognition (Neuter)"
        },
        {
            "content": "Ich sehe {{c1::den}} Mann",
            "fields": {"Explanation": "den - Maskulin Akkusativ (wen/was? direktes Objekt)"},
            "title": "German Case Usage (Accusative)"
        },
        {
            "content": "Mit {{c1::dem}} Auto fahre ich",
            "fields": {"Explanation": "dem - Maskulin Dativ (wem? mit Präposition)"},
            "title": "German Case Usage (Dative)"
        }
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
        
        print(f"📖 FRONT (Question):")
        print(f"   {display['front']}")
        print(f"   Explanation: {fields.get('Explanation', 'N/A')}")
        
        print(f"📝 BACK (Answer):")
        print(f"   {display['back']}")
        
        # Check for rendering issues
        issues = AnkiRenderSimulator.detect_rendering_issues(display['rendered'])
        if issues:
            print(f"⚠️  Rendering Issues:")
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
            "title": "Field Substitution in Cloze Deletion"
        },
        {
            "content": "{{c1::{{Article}}}} {{Noun}} ist {{Adjective}}",
            "fields": {"Article": "Das", "Noun": "Haus", "Adjective": "groß"},
            "title": "Multiple Field Substitutions"
        },
        {
            "content": "{{c1::{{Word}}}} translation",
            "fields": {"Word": ""},  # Empty field - problematic case
            "title": "Empty Field (Problematic Case)"
        }
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
        print(f"📝 Step 1: Field Substitution")
        after_fields = AnkiRenderSimulator.apply_field_substitution(content, fields)
        print(f"   Result: {after_fields}")
        
        print(f"📖 Step 2: Front View (Hide Cloze)")
        front = AnkiRenderSimulator.render_cloze_deletion(after_fields, show_answer=False)
        print(f"   Front: {front}")
        
        print(f"📝 Step 3: Back View (Show Answer)")
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
            "title": "Triple Cloze Deletion"
        },
        {
            "content": "{{c1::{{Article}}}} {{c2::{{Noun}}}} ist {{c3::{{Adjective}}}}",
            "fields": {"Article": "Das", "Noun": "Haus", "Adjective": "groß"},
            "title": "Multi-Cloze with Field Substitution"
        }
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


def main() -> int:
    """Run complete Anki card simulation.
    
    Returns:
        Exit code (0 for success, 1 for simulation errors)
    """
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
        
        return 0
        
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: Simulation failed: {e}")
        print("   • Cannot predict Anki behavior")
        print("   • DO NOT claim fixes work without manual verification")
        return 1


if __name__ == "__main__":
    exit(main())