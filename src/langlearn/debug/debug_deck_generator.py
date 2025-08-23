"""Debug Deck Generator for reproducing user-reported issues.

This module generates minimal test decks to reproduce specific problems,
enabling precise debugging and verification of fixes.
"""

import tempfile
from pathlib import Path
from typing import Dict, List, Any

from langlearn.deck_builder import DeckBuilder


class DebugDeckGenerator:
    """Generates minimal decks for reproducing specific user issues.
    
    This class creates focused test decks that isolate specific problems,
    making it easier to debug issues and verify that fixes actually work
    in the real Anki application.
    """
    
    @staticmethod
    def create_debug_deck(issue_type: str) -> Path:
        """Create a debug deck for a specific issue type.
        
        Args:
            issue_type: Type of issue to reproduce (see available types below)
            
        Returns:
            Path to generated debug deck file (.apkg)
            
        Available issue types:
        - "blank_cards": Cards that appear blank due to empty cloze deletions
        - "duplicate_detection": Multiple cards with same content
        - "template_syntax": Template field mismatch issues
        - "case_sensitivity": Article case sensitivity problems
        - "field_substitution": Field replacement failures
        - "multi_cloze": Multiple cloze deletion issues
        """
        issue_generators = {
            "blank_cards": DebugDeckGenerator._generate_blank_card_test,
            "duplicate_detection": DebugDeckGenerator._generate_duplicate_test,
            "template_syntax": DebugDeckGenerator._generate_template_syntax_test,
            "case_sensitivity": DebugDeckGenerator._generate_case_sensitivity_test,
            "field_substitution": DebugDeckGenerator._generate_field_substitution_test,
            "multi_cloze": DebugDeckGenerator._generate_multi_cloze_test,
        }
        
        if issue_type not in issue_generators:
            available_types = ", ".join(issue_generators.keys())
            raise ValueError(f"Unknown issue type '{issue_type}'. Available: {available_types}")
        
        # Generate test cards for the specific issue
        test_cards = issue_generators[issue_type]()
        
        # Create debug deck
        output_file = Path(tempfile.gettempdir()) / f"debug_{issue_type}.apkg"
        
        # For now, return the test card data for manual inspection
        # Future: Integration with DeckBuilder when needed
        debug_info = {
            "issue_type": issue_type,
            "test_cards": test_cards,
            "card_count": len(test_cards),
            "output_path": output_file
        }
        
        # Write debug info to file for inspection
        debug_file = Path(tempfile.gettempdir()) / f"debug_{issue_type}_info.txt"
        with open(debug_file, "w", encoding="utf-8") as f:
            f.write(f"Debug Deck: {issue_type.replace('_', ' ').title()}\n")
            f.write(f"Generated {len(test_cards)} test cards\n\n")
            
            for i, card in enumerate(test_cards, 1):
                f.write(f"Card {i}:\n")
                for key, value in card.items():
                    f.write(f"  {key}: {value}\n")
                f.write("\n")
        
        print(f"Debug info written to: {debug_file}")
        print(f"Use this data to create test cases for '{issue_type}' issues")
        
        return output_file
    
    @staticmethod
    def generate_test_cards(pattern: str, count: int = 5) -> List[Dict[str, Any]]:
        """Generate test cards following a specific pattern.
        
        Args:
            pattern: Pattern type ("gender_cloze", "case_cloze", "field_substitution")
            count: Number of cards to generate
            
        Returns:
            List of card data dictionaries
        """
        patterns = {
            "gender_cloze": DebugDeckGenerator._create_gender_cloze_pattern,
            "case_cloze": DebugDeckGenerator._create_case_cloze_pattern, 
            "field_substitution": DebugDeckGenerator._create_field_substitution_pattern,
            "multi_cloze": DebugDeckGenerator._create_multi_cloze_pattern,
        }
        
        if pattern not in patterns:
            available_patterns = ", ".join(patterns.keys())
            raise ValueError(f"Unknown pattern '{pattern}'. Available: {available_patterns}")
        
        cards = []
        pattern_generator = patterns[pattern]
        
        for i in range(count):
            card_data = pattern_generator(i + 1)
            cards.append(card_data)
        
        return cards
    
    @staticmethod
    def add_diagnostic_fields(card_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add diagnostic fields to help with debugging.
        
        Args:
            card_data: Original card data
            
        Returns:
            Card data with additional diagnostic fields
        """
        # Create a copy to avoid modifying original
        enhanced_data = card_data.copy()
        
        # Add diagnostic fields
        enhanced_data["Debug_Issue_Type"] = card_data.get("debug_issue_type", "unknown")
        enhanced_data["Debug_Expected_Behavior"] = card_data.get("expected_behavior", "See notes")
        enhanced_data["Debug_Test_Notes"] = card_data.get("test_notes", "Generated for debugging")
        enhanced_data["Debug_Generated_At"] = str(Path.cwd())
        
        return enhanced_data
    
    # Issue-specific test generators
    
    @staticmethod
    def _generate_blank_card_test() -> List[Dict[str, Any]]:
        """Generate test cards that reproduce blank card issues."""
        return [
            {
                "Text": "{{c1::{{Word}}}} Mann ist hier",
                "Word": "",  # Empty field causes blank card
                "Explanation": "Empty Word field test",
                "debug_issue_type": "blank_cards",
                "expected_behavior": "Should show blank cloze deletion",
                "test_notes": "Reproduces user-reported blank card issue"
            },
            {
                "Text": "{{c1::}} ist leer", 
                "Explanation": "Empty cloze deletion test",
                "debug_issue_type": "blank_cards",
                "expected_behavior": "Should show empty cloze",
                "test_notes": "Tests empty cloze deletion handling"
            },
            {
                "Text": "{{c1::{{MissingField}}}} reference",
                "Explanation": "Missing field test",
                "debug_issue_type": "blank_cards", 
                "expected_behavior": "Should show unreplaced field reference",
                "test_notes": "Tests missing field handling"
            }
        ]
    
    @staticmethod
    def _generate_duplicate_test() -> List[Dict[str, Any]]:
        """Generate test cards to test duplicate detection."""
        # Create intentionally similar cards
        base_card = {
            "Text": "{{c1::Der}} Mann arbeitet hier",
            "Explanation": "Maskulin - Geschlecht erkennen",
            "debug_issue_type": "duplicate_detection"
        }
        
        return [
            {**base_card, "test_notes": "Original card"},
            {**base_card, "test_notes": "Exact duplicate"},
            {
                **base_card,
                "Text": "{{c1::Der}} Mann arbeitet hier",  # Same content
                "Explanation": "Different explanation",  # Different field
                "test_notes": "Same content, different explanation"
            },
            {
                **base_card,
                "Text": "{{c1::Die}} Frau arbeitet hier",  # Different article
                "test_notes": "Similar structure, different article"
            }
        ]
    
    @staticmethod
    def _generate_template_syntax_test() -> List[Dict[str, Any]]:
        """Generate test cards with template syntax issues."""
        return [
            {
                "Text": "{{c1::Der}} {{UndefinedField}} ist hier",
                "Explanation": "Test explanation",
                "debug_issue_type": "template_syntax",
                "expected_behavior": "Should detect undefined field",
                "test_notes": "Tests undefined field detection"
            },
            {
                "Text": "{{c2::Mann}} without c1",
                "Explanation": "Invalid cloze numbering",
                "debug_issue_type": "template_syntax",
                "expected_behavior": "Should detect invalid cloze numbering",
                "test_notes": "Tests cloze numbering validation"
            },
            {
                "Text": "{{c1::outer {{c2::nested}} deletion}}",
                "Explanation": "Nested cloze test",
                "debug_issue_type": "template_syntax",
                "expected_behavior": "Should detect nested cloze deletions",
                "test_notes": "Tests nested cloze detection"
            }
        ]
    
    @staticmethod
    def _generate_case_sensitivity_test() -> List[Dict[str, Any]]:
        """Generate test cards for case sensitivity issues."""
        return [
            {
                "Text": "{{c1::der}} Mann arbeitet hier",  # lowercase in data
                "Article": "der",
                "Explanation": "Lowercase article test",
                "debug_issue_type": "case_sensitivity",
                "expected_behavior": "Should handle lowercase 'der' correctly",
                "test_notes": "Tests case-sensitive replacement (user issue)"
            },
            {
                "Text": "{{c1::Der}} Mann arbeitet hier",  # capitalized in sentence
                "Article": "der",  # lowercase in field
                "Explanation": "Mixed case article test", 
                "debug_issue_type": "case_sensitivity",
                "expected_behavior": "Should preserve capitalization",
                "test_notes": "Tests capitalization preservation"
            },
            {
                "Text": "{{c1::DIE}} FRAU IST SCHÖN",  # all caps
                "Article": "die",
                "Explanation": "All caps test",
                "debug_issue_type": "case_sensitivity", 
                "expected_behavior": "Should handle unusual capitalization",
                "test_notes": "Tests extreme case variations"
            }
        ]
    
    @staticmethod
    def _generate_field_substitution_test() -> List[Dict[str, Any]]:
        """Generate test cards for field substitution issues."""
        return [
            {
                "Text": "{{c1::{{Word}}}} means {{Meaning}}",
                "Word": "Haus",
                "Meaning": "house",
                "Explanation": "Field substitution test",
                "debug_issue_type": "field_substitution",
                "expected_behavior": "Should substitute fields within cloze",
                "test_notes": "Tests nested field substitution"
            },
            {
                "Text": "{{c1::{{EmptyField}}}} test",
                "EmptyField": "",
                "Explanation": "Empty field test",
                "debug_issue_type": "field_substitution",
                "expected_behavior": "Should handle empty field substitution",
                "test_notes": "Tests empty field handling"
            },
            {
                "Text": "{{c1::{{Word}}}} {{c2::{{Meaning}}}} double substitution",
                "Word": "Haus", 
                "Meaning": "house",
                "Explanation": "Multiple field substitution",
                "debug_issue_type": "field_substitution",
                "expected_behavior": "Should substitute multiple fields correctly",
                "test_notes": "Tests multiple field substitutions"
            }
        ]
    
    @staticmethod
    def _generate_multi_cloze_test() -> List[Dict[str, Any]]:
        """Generate test cards for multi-cloze deletion issues."""
        return [
            {
                "Text": "{{c1::Der}} {{c2::Mann}} arbeitet {{c3::hier}}",
                "Explanation": "Triple cloze test",
                "debug_issue_type": "multi_cloze",
                "expected_behavior": "Should create 3 separate cards",
                "test_notes": "Tests multiple cloze deletions"
            },
            {
                "Text": "{{c1::{{Article}}}} {{c2::{{Noun}}}} ist {{c3::{{Adjective}}}}",
                "Article": "Das",
                "Noun": "Haus", 
                "Adjective": "groß",
                "Explanation": "Multi-cloze with field substitution",
                "debug_issue_type": "multi_cloze",
                "expected_behavior": "Should substitute fields and create multiple cards",
                "test_notes": "Tests multi-cloze with field substitution"
            }
        ]
    
    # Pattern generators for test cards
    
    @staticmethod
    def _create_gender_cloze_pattern(index: int) -> Dict[str, Any]:
        """Create gender cloze pattern card."""
        articles = ["Der", "Die", "Das"]
        nouns = ["Mann", "Frau", "Haus"]
        genders = ["Maskulin", "Feminin", "Neutrum"]
        
        i = (index - 1) % 3
        
        return {
            "Text": f"{{{{c1::{articles[i]}}}}} {nouns[i]} ist hier",
            "Explanation": f"{genders[i]} - Geschlecht erkennen",
            "card_type": "gender_cloze",
            "test_notes": f"Generated gender cloze pattern #{index}"
        }
    
    @staticmethod
    def _create_case_cloze_pattern(index: int) -> Dict[str, Any]:
        """Create case cloze pattern card."""
        cases = [
            ("den", "Maskulin Akkusativ (wen/was? direktes Objekt)"),
            ("dem", "Maskulin Dativ (wem? mit Präposition)"), 
            ("des", "Maskulin Genitiv (wessen? Besitz)"),
            ("der", "Feminin Dativ/Genitiv (wem/wessen?)")
        ]
        
        sentences = [
            "Ich sehe {{c1::den}} Mann",
            "Mit {{c1::dem}} Auto fahre ich",
            "Das Auto {{c1::des}} Mannes ist rot",
            "Ich gebe {{c1::der}} Frau das Buch"
        ]
        
        i = (index - 1) % 4
        article, explanation = cases[i]
        
        return {
            "Text": sentences[i],
            "Explanation": f"{article} - {explanation}",
            "card_type": "case_cloze",
            "test_notes": f"Generated case cloze pattern #{index}"
        }
    
    @staticmethod
    def _create_field_substitution_pattern(index: int) -> Dict[str, Any]:
        """Create field substitution pattern card."""
        words = ["Haus", "Auto", "Frau", "Mann", "Kind"]
        meanings = ["house", "car", "woman", "man", "child"]
        
        i = (index - 1) % len(words)
        
        return {
            "Text": f"{{{{c1::{{{{Word}}}}}}}} means {{{{Meaning}}}}",
            "Word": words[i],
            "Meaning": meanings[i],
            "Explanation": f"Field substitution test for {words[i]}",
            "card_type": "field_substitution", 
            "test_notes": f"Generated field substitution pattern #{index}"
        }
    
    @staticmethod  
    def _create_multi_cloze_pattern(index: int) -> Dict[str, Any]:
        """Create multi-cloze pattern card."""
        patterns = [
            ("{{c1::Der}} {{c2::Mann}} arbeitet {{c3::hier}}", "Triple cloze deletion"),
            ("{{c1::Die}} {{c2::Frau}} ist {{c3::schön}}", "Triple cloze with feminine"),
            ("{{c1::Das}} {{c2::Haus}} ist {{c3::groß}}", "Triple cloze with neuter"),
            ("{{c1::Ich}} sehe {{c2::den}} {{c3::Mann}}", "Subject-verb-object cloze")
        ]
        
        i = (index - 1) % len(patterns)
        text, description = patterns[i]
        
        return {
            "Text": text,
            "Explanation": f"{description} - test #{index}",
            "card_type": "multi_cloze",
            "test_notes": f"Generated multi-cloze pattern #{index}"
        }