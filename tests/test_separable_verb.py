"""Unit tests for the SeparableVerb model."""

from langlearn.models.separable_verb import SeparableVerb


def test_separable_verb_creation() -> None:
    """Test creating a separable verb with valid data."""
    verb = SeparableVerb(
        verb="aufstehen",
        english="to get up",
        present_ich="stehe auf",
        present_du="stehst auf",
        present_er="steht auf",
        perfect="ist aufgestanden",
        example="Ich stehe um 7 Uhr auf.",
        prefix="auf",
    )

    assert verb.verb == "aufstehen"
    assert verb.english == "to get up"
    assert verb.present_ich == "stehe auf"
    assert verb.present_du == "stehst auf"
    assert verb.present_er == "steht auf"
    assert verb.perfect == "ist aufgestanden"
    assert verb.example == "Ich stehe um 7 Uhr auf."
    assert verb.prefix == "auf"


def test_separable_verb_validation() -> None:
    """Test validation of separable verb conjugation patterns."""
    # Valid separable verb
    valid_verb = SeparableVerb(
        verb="anrufen",
        english="to call",
        present_ich="rufe an",
        present_du="rufst an",
        present_er="ruft an",
        perfect="hat angerufen",
        example="Er ruft seine Mutter an.",
        prefix="an",
    )
    assert valid_verb.validate_separable_conjugation() is True

    # Invalid separable verb (wrong prefix position)
    invalid_verb = SeparableVerb(
        verb="anrufen",
        english="to call",
        present_ich="anrufe",  # Wrong: prefix should be at the end
        present_du="anrufst",  # Wrong: prefix should be at the end
        present_er="anruft",  # Wrong: prefix should be at the end
        perfect="hat angerufen",
        example="Er ruft seine Mutter an.",
        prefix="an",
    )
    assert invalid_verb.validate_separable_conjugation() is False

    # Invalid separable verb (wrong perfect tense)
    invalid_verb2 = SeparableVerb(
        verb="anrufen",
        english="to call",
        present_ich="rufe an",
        present_du="rufst an",
        present_er="ruft an",
        perfect="hat rufen an",  # Wrong: prefix should be before the main verb
        example="Er ruft seine Mutter an.",
        prefix="an",
    )
    assert invalid_verb2.validate_separable_conjugation() is False


def test_separable_verb_from_csv() -> None:
    """Test creating a separable verb from CSV data."""
    csv_data = {
        "verb": "ausgehen",
        "english": "to go out",
        "classification": "unregelmäßig",
        "present_ich": "gehe aus",
        "present_du": "gehst aus",
        "present_er": "geht aus",
        "präteritum": "ging aus",
        "auxiliary": "sein",
        "perfect": "ist ausgegangen",
        "example": "Wir gehen heute Abend aus.",
        "prefix": "aus",
    }

    verb = SeparableVerb(
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
        prefix=csv_data["prefix"],
    )
    assert verb.verb == "ausgehen"
    assert verb.prefix == "aus"
    assert verb.validate_separable_conjugation() is True
