"""Model for German adjectives."""

from pydantic import BaseModel, Field


class Adjective(BaseModel):
    """Model representing a German adjective with its properties.

    German adjectives have comparative and superlative forms, and follow
    specific patterns for their formation.
    """

    word: str = Field(..., description="The German adjective")
    english: str = Field(..., description="English translation")
    example: str = Field(..., description="Example sentence using the adjective")
    comparative: str = Field(..., description="Comparative form of the adjective")
    superlative: str = Field(..., description="Superlative form of the adjective")

    def validate_comparative(self) -> bool:
        """Validate that the comparative form follows German grammar rules.

        Returns:
            bool: True if the comparative form is valid
        """
        # Most German comparatives add -er to the base form
        # Some have umlaut changes (e.g., alt -> älter)
        # A few are irregular (e.g., gut -> besser)

        irregular_comparatives = {
            "gut": "besser",
            "viel": "mehr",
            "gern": "lieber",
            "hoch": "höher",
            "nah": "näher",
        }

        # Check for irregular comparatives
        if self.word in irregular_comparatives:
            return self.comparative == irregular_comparatives[self.word]

        # Check for regular pattern (-er ending)
        if not self.comparative.endswith("er"):
            return False

        # Check that the comparative starts with the base adjective
        # (allowing for possible umlaut changes)
        base = self.word.rstrip("e")  # Remove trailing 'e' if present
        comp_base = self.comparative[:-2]  # Remove 'er' ending

        # Check if bases match, accounting for umlaut changes
        umlaut_pairs = [("a", "ä"), ("o", "ö"), ("u", "ü")]
        if base == comp_base:
            return True

        # Check for umlaut changes
        for normal, umlaut in umlaut_pairs:
            if base.replace(normal, umlaut) == comp_base:
                return True

        return False

    def validate_superlative(self) -> bool:
        """Validate that the superlative form follows German grammar rules.

        Returns:
            bool: True if the superlative form is valid
        """
        if not self.superlative:
            return True  # Optional field

        # Most German superlatives are formed with "am" + adjective + "sten"
        # Some add -esten instead of -sten
        # Some have umlaut changes
        # Some are irregular (e.g., gut -> am besten)

        irregular_superlatives = {
            "gut": "am besten",
            "viel": "am meisten",
            "gern": "am liebsten",
            "hoch": "am höchsten",
            "nah": "am nächsten",
        }

        # Check for irregular superlatives
        if self.word in irregular_superlatives:
            return self.superlative == irregular_superlatives[self.word]

        # Check for regular pattern
        if not self.superlative.startswith("am "):
            return False

        # Check for -sten or -esten ending
        if not (self.superlative.endswith("sten")):
            return False

        # Get the base form from the superlative, handling both -sten and -esten cases
        superlative_base = self.superlative[3:-4]  # Remove "am " and "sten"
        if superlative_base.endswith("e"):  # Handle -esten case
            superlative_base = superlative_base[:-1]

        base = self.word.rstrip("e")  # Remove trailing 'e' if present

        # Check if bases match, accounting for umlaut changes
        umlaut_pairs = [("a", "ä"), ("o", "ö"), ("u", "ü")]
        if base == superlative_base:
            return True

        # Check for umlaut changes
        for normal, umlaut in umlaut_pairs:
            if base.replace(normal, umlaut) == superlative_base:
                return True

        return False
