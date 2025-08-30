"""German explanation factory for article cloze cards.

This factory generates German-language grammatical explanations for article
cloze deletion cards, supporting immersive German language learning.
"""


class GermanExplanationFactory:
    """Factory for generating German grammatical explanations for article cards.

    Provides consistent, pedagogically sound German explanations for:
    - Gender and case combinations
    - Article types (bestimmt, unbestimmt, verneinend)
    - Case usage descriptions

    All explanations are in German to support immersive learning.
    """

    def __init__(self) -> None:
        """Initialize the German explanation factory."""
        # Case explanations with German question words
        self._case_explanations: dict[str, str] = {
            "nominative": "wer/was? - Subjekt des Satzes",
            "accusative": "wen/was? - direktes Objekt",
            "dative": "wem? - indirektes Objekt",
            "genitive": "wessen? - Besitz und bestimmte Präpositionen",
        }

        # German gender names
        self._gender_names: dict[str, str] = {
            "masculine": "Maskulin",
            "feminine": "Feminin",
            "neuter": "Neutrum",
        }

        # Article type descriptions
        self._article_type_names: dict[str, str] = {
            "bestimmt": "bestimmter Artikel",
            "unbestimmt": "unbestimmter Artikel",
            "verneinend": "verneinender Artikel",
        }

    def create_case_explanation(self, gender: str, case: str, article: str) -> str:
        """Generate German explanation for gender + case combination.

        Args:
            gender: Gender in English (masculine, feminine, neuter)
            case: Case in English (nominative, accusative, dative, genitive)
            article: The actual article form (der, den, dem, des, etc.)

        Returns:
            German explanation like "der - Maskulin Nominativ (wer/was? Subjekt)"

        Example:
            >>> factory.create_case_explanation("masculine", "accusative", "den")
            "den - Maskulin Akkusativ (wen/was? direktes Objekt)"
        """
        gender_de = self._gender_names.get(gender, gender.title())
        case_de = self._get_german_case_name(case)
        case_explanation = self._case_explanations.get(case, case)

        return f"{article} - {gender_de} {case_de} ({case_explanation})"

    def create_article_type_explanation(self, artikel_typ: str) -> str:
        """Generate German explanation for article type.

        Args:
            artikel_typ: Article type (bestimmt, unbestimmt, verneinend)

        Returns:
            German explanation like "bestimmter Artikel"

        Example:
            >>> factory.create_article_type_explanation("unbestimmt")
            "unbestimmter Artikel"
        """
        return self._article_type_names.get(artikel_typ, artikel_typ)

    def create_gender_recognition_explanation(self, gender: str) -> str:
        """Generate German explanation for gender recognition cards.

        Args:
            gender: Gender in English (masculine, feminine, neuter)

        Returns:
            German explanation like "Maskulin - Geschlecht erkennen"

        Example:
            >>> factory.create_gender_recognition_explanation("feminine")
            "Feminin - Geschlecht erkennen"
        """
        gender_de = self._gender_names.get(gender, gender.title())
        return f"{gender_de} - Geschlecht erkennen"

    def _get_german_case_name(self, case: str) -> str:
        """Convert English case name to German.

        Args:
            case: English case name (nominative, accusative, dative, genitive)

        Returns:
            German case name (Nominativ, Akkusativ, Dativ, Genitiv)
        """
        case_names = {
            "nominative": "Nominativ",
            "accusative": "Akkusativ",
            "dative": "Dativ",
            "genitive": "Genitiv",
        }
        return case_names.get(case, case.title())
