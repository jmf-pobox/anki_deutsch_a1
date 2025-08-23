#!/usr/bin/env python3
"""Anki Validation Script - validates generated cards will work correctly in Anki.

This script addresses the critical verification gap that caused $566 in wasted costs
from false "fix" claims by validating content will actually work in Anki application.
"""

import sys
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from langlearn.validators.anki_validator import AnkiValidator


def validate_test_cards() -> tuple[bool, int, int]:
    """Validate test German cloze cards for Anki compatibility.

    Returns:
        Tuple of (all_valid, total_cards_tested, issues_found)
    """
    test_cards = [
        # Valid German gender cloze cards
        {
            "content": "{{c1::Der}} Mann arbeitet hier",
            "fields": {"Explanation": "Maskulin - Geschlecht erkennen"},
            "description": "German gender recognition (masculine)",
        },
        {
            "content": "{{c1::Die}} Frau ist schön",
            "fields": {"Explanation": "Feminin - Geschlecht erkennen"},
            "description": "German gender recognition (feminine)",
        },
        {
            "content": "{{c1::Das}} Haus ist groß",
            "fields": {"Explanation": "Neutrum - Geschlecht erkennen"},
            "description": "German gender recognition (neuter)",
        },
        # Valid German case cloze cards
        {
            "content": "Ich sehe {{c1::den}} Mann",
            "fields": {
                "Explanation": "den - Maskulin Akkusativ (wen/was? direktes Objekt)"
            },
            "description": "German case usage (accusative masculine)",
        },
        {
            "content": "Mit {{c1::dem}} Auto fahre ich",
            "fields": {"Explanation": "dem - Maskulin Dativ (wem? mit Präposition)"},
            "description": "German case usage (dative masculine)",
        },
        # Test cards with field substitution
        {
            "content": "{{c1::{{Word}}}} means {{Meaning}}",
            "fields": {
                "Word": "Haus",
                "Meaning": "house",
                "Explanation": "Noun meaning",
            },
            "description": "Field substitution within cloze deletion",
        },
        # Edge case: multiple cloze deletions
        {
            "content": "{{c1::Der}} {{c2::Mann}} arbeitet {{c3::hier}}",
            "fields": {"Explanation": "Multiple cloze deletions"},
            "description": "Multiple cloze deletions in one card",
        },
    ]

    print("🔍 ANKI VALIDATION - Testing card compatibility...")
    print("=" * 60)

    all_valid = True
    total_issues = 0

    for i, card in enumerate(test_cards, 1):
        content = card["content"]
        fields = card["fields"]
        description = card["description"]

        print(f"\n📋 Test {i}: {description}")
        print(f"   Content: {content}")

        # Run comprehensive validation
        is_valid, issues = AnkiValidator.validate_card_complete(content, fields)

        if is_valid:
            print("   ✅ VALID - Card will work correctly in Anki")
        else:
            print("   ❌ INVALID - Issues found:")
            all_valid = False
            for category, category_issues in issues.items():
                total_issues += len(category_issues)
                for issue in category_issues:
                    print(f"      • {category}: {issue}")

    return all_valid, len(test_cards), total_issues


def validate_problematic_cases() -> tuple[bool, int, int]:
    """Validate known problematic cases that caused user issues.

    Returns:
        Tuple of (all_valid, total_cases_tested, issues_found)
    """
    problematic_cases = [
        # Case that caused blank cards in user feedback
        {
            "content": "{{c1::{{Word}}}} Mann ist hier",
            "fields": {"Word": ""},  # Empty field causes blank card
            "description": "Empty field in cloze deletion (user reported issue)",
            "should_be_valid": False,  # This SHOULD be detected as invalid
        },
        # Missing field reference
        {
            "content": "{{c1::Der}} {{UndefinedField}} ist hier",
            "fields": {"Explanation": "Test"},
            "description": "Missing field reference",
            "should_be_valid": False,
        },
        # Invalid cloze numbering
        {
            "content": "{{c2::Mann}} without c1",
            "fields": {},
            "description": "Invalid cloze numbering (starts with c2)",
            "should_be_valid": False,
        },
        # Empty cloze deletion
        {
            "content": "{{c1::}} empty cloze",
            "fields": {},
            "description": "Empty cloze deletion",
            "should_be_valid": False,
        },
    ]

    print("\n\n🚨 PROBLEMATIC CASES - Testing known issue patterns...")
    print("=" * 60)

    all_correct = True
    total_issues = 0

    for i, case in enumerate(problematic_cases, 1):
        content = case["content"]
        fields = case["fields"]
        description = case["description"]
        should_be_valid = case["should_be_valid"]

        print(f"\n🔬 Problem Test {i}: {description}")
        print(f"   Content: {content}")

        # Run validation
        is_valid, issues = AnkiValidator.validate_card_complete(content, fields)

        # Check if validation result matches expectation
        if is_valid == should_be_valid:
            if should_be_valid:
                print("   ✅ CORRECT - Card correctly identified as valid")
            else:
                print("   ✅ CORRECT - Problem correctly detected as invalid")
                total_issue_count = sum(
                    len(category_issues) for category_issues in issues.values()
                )
                print(f"      Issues found: {total_issue_count}")
        else:
            print(
                f"   ❌ INCORRECT - Expected valid={should_be_valid}, "
                f"got valid={is_valid}"
            )
            all_correct = False
            if not is_valid:
                total_issues += sum(
                    len(category_issues) for category_issues in issues.values()
                )
                for category, category_issues in issues.items():
                    for issue in category_issues:
                        print(f"      • {category}: {issue}")

    return all_correct, len(problematic_cases), total_issues


def main() -> int:
    """Run complete Anki validation suite.

    Returns:
        Exit code (0 for success, 1 for validation failures)
    """
    print("🛡️  ANKI VALIDATION SYSTEM")
    print("Preventing $566+ costs from false 'fix' claims")
    print("Validating content will work correctly in Anki application")

    try:
        # Test 1: Validate normal test cards
        cards_valid, cards_tested, card_issues = validate_test_cards()

        # Test 2: Validate problematic cases are detected
        problems_correct, problems_tested, problem_issues = validate_problematic_cases()

        # Summary
        print("\n" + "=" * 60)
        print("📊 VALIDATION SUMMARY")
        print(f"✅ Test Cards: {cards_tested} tested")
        print(f"🚨 Problem Cases: {problems_tested} tested")
        print(f"🔍 Total Issues Found: {card_issues + problem_issues}")

        if cards_valid and problems_correct:
            print("\n🎉 SUCCESS: All validations passed!")
            print("   • Valid cards correctly identified as valid")
            print("   • Problem cases correctly identified as invalid")
            print("   • AnkiValidator is working correctly")
            return 0
        else:
            print("\n❌ FAILURE: Validation issues detected!")
            if not cards_valid:
                print(f"   • {card_issues} issues found in test cards")
            if not problems_correct:
                print("   • Problem detection logic needs improvement")
            print("   • Review validation logic before claiming fixes work")
            return 1

    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: Validation system failed: {e}")
        print("   • Cannot validate Anki compatibility")
        print("   • DO NOT claim fixes work without manual verification")
        return 1


if __name__ == "__main__":
    exit(main())
