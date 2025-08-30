"""Unit tests for the IrregularVerb model."""

from langlearn.models.irregular_verb import IrregularVerb


def test_irregular_verb_creation() -> None:
    """Test creating an irregular verb with valid data."""
    verb = IrregularVerb(
        verb="sein",
        english="to be",
        present_ich="bin",
        present_du="bist",
        present_er="ist",
        perfect="ist gewesen",
        example="Ich bin müde.",
        notes="Highly irregular, no pattern",
    )

    assert verb.verb == "sein"
    assert verb.english == "to be"
    assert verb.present_ich == "bin"
    assert verb.present_du == "bist"
    assert verb.present_er == "ist"
    assert verb.perfect == "ist gewesen"
    assert verb.example == "Ich bin müde."
    assert verb.notes == "Highly irregular, no pattern"


def test_irregular_verb_validation() -> None:
    """Test validation of irregular verb conjugation patterns."""
    # Verb with vowel changes
    vowel_change_verb = IrregularVerb(
        verb="sehen",
        english="to see",
        present_ich="sehe",
        present_du="siehst",
        present_er="sieht",
        perfect="hat gesehen",
        example="Sie sieht einen Film.",
        notes="Vowel change in present tense",
    )
    assert vowel_change_verb.validate_irregular_conjugation() is True

    # Verb with 'sein' in perfect tense
    sein_verb = IrregularVerb(
        verb="gehen",
        english="to go",
        present_ich="gehe",
        present_du="gehst",
        present_er="geht",
        perfect="ist gegangen",
        example="Sie geht zur Schule.",
        notes="Irregular perfect with 'ist'",
    )
    assert sein_verb.validate_irregular_conjugation() is True

    # Verb with irregular perfect tense
    irregular_perfect_verb = IrregularVerb(
        verb="haben",
        english="to have",
        present_ich="habe",
        present_du="hast",
        present_er="hat",
        perfect="hat gehabt",
        example="Er hat ein Auto.",
        notes="Irregular in perfect tense",
    )
    assert irregular_perfect_verb.validate_irregular_conjugation() is True

    # Invalid irregular verb (regular conjugation)
    invalid_verb = IrregularVerb(
        verb="lernen",
        english="to learn",
        present_ich="lerne",
        present_du="lernst",
        present_er="lernt",
        perfect="hat gelernt",
        example="Ich lerne Deutsch.",
        notes="This is actually a regular verb",
    )
    assert invalid_verb.validate_irregular_conjugation() is False


def test_irregular_verb_from_csv() -> None:
    """Test creating an irregular verb from CSV data."""
    csv_data = {
        "verb": "kommen",
        "english": "to come",
        "classification": "unregelmäßig",
        "present_ich": "komme",
        "present_du": "kommst",
        "present_er": "kommt",
        "präteritum": "kam",
        "auxiliary": "sein",
        "perfect": "ist gekommen",
        "example": "Woher kommst du?",
        "notes": "Irregular perfect with 'ist'",
    }

    verb = IrregularVerb(
        verb=csv_data["verb"],
        english=csv_data["english"],
        classification=csv_data["classification"],
        present_ich=csv_data["present_ich"],
        present_du=csv_data["present_du"],
        present_er=csv_data["present_er"],
        präteritum=csv_data["präteritum"],
        auxiliary=csv_data["auxiliary"],
        perfect=csv_data["perfect"],
        example=csv_data["example"],
        notes=csv_data["notes"],
    )
    assert verb.verb == "kommen"
    assert verb.notes == "Irregular perfect with 'ist'"
    assert verb.validate_irregular_conjugation() is True
