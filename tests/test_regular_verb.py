"""Unit tests for the RegularVerb model."""

from langlearn.models.regular_verb import RegularVerb


def test_regular_verb_creation() -> None:
    """Test creating a regular verb with valid data."""
    verb = RegularVerb(
        verb="lernen",
        english="to learn",
        present_ich="lerne",
        present_du="lernst",
        present_er="lernt",
        perfect="hat gelernt",
        example="Ich lerne Deutsch.",
    )

    assert verb.verb == "lernen"
    assert verb.english == "to learn"
    assert verb.present_ich == "lerne"
    assert verb.present_du == "lernst"
    assert verb.present_er == "lernt"
    assert verb.perfect == "hat gelernt"
    assert verb.example == "Ich lerne Deutsch."


def test_regular_verb_validation() -> None:
    """Test validation of regular verb conjugation patterns."""
    # Valid regular verb
    valid_verb = RegularVerb(
        verb="machen",
        english="to do",
        present_ich="mache",
        present_du="machst",
        present_er="macht",
        perfect="hat gemacht",
        example="Ich mache Hausaufgaben.",
    )
    assert valid_verb.validate_regular_conjugation() is True

    # Invalid regular verb (wrong endings)
    invalid_verb = RegularVerb(
        verb="machen",
        english="to do",
        present_ich="mache",
        present_du="macht",  # Wrong ending
        present_er="machst",  # Wrong ending
        perfect="hat gemacht",
        example="Ich mache Hausaufgaben.",
    )
    assert invalid_verb.validate_regular_conjugation() is False

    # Invalid regular verb (wrong perfect tense)
    invalid_verb2 = RegularVerb(
        verb="machen",
        english="to do",
        present_ich="mache",
        present_du="machst",
        present_er="macht",
        perfect="ist gemacht",  # Wrong auxiliary verb
        example="Ich mache Hausaufgaben.",
    )
    assert invalid_verb2.validate_regular_conjugation() is False


def test_regular_verb_from_csv() -> None:
    """Test creating a regular verb from CSV data."""
    csv_data = {
        "verb": "spielen",
        "english": "to play",
        "classification": "regelmäßig",
        "present_ich": "spiele",
        "present_du": "spielst",
        "present_er": "spielt",
        "präteritum": "spielte",
        "auxiliary": "haben",
        "perfect": "hat gespielt",
        "example": "Die Kinder spielen im Park.",
    }

    verb = RegularVerb(
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
    )
    assert verb.verb == "spielen"
    assert verb.validate_regular_conjugation() is True
