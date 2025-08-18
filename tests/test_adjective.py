"""Unit tests for the Adjective model."""

from langlearn.models.adjective import Adjective


def test_adjective_creation() -> None:
    """Test creating an adjective with valid data."""
    adj = Adjective(
        word="groß",
        english="big/tall",
        example="Er ist sehr groß.",
        comparative="größer",
        superlative="am größten",
        word_audio="",
        example_audio="",
        image_path="",
    )

    assert adj.word == "groß"
    assert adj.english == "big/tall"
    assert adj.example == "Er ist sehr groß."
    assert adj.comparative == "größer"
    assert adj.superlative == "am größten"


def test_comparative_validation() -> None:
    """Test validation of comparative forms."""
    # Regular comparative
    regular = Adjective(
        word="klein",
        english="small",
        example="Meine Wohnung ist klein.",
        comparative="kleiner",
        superlative="am kleinsten",
        word_audio="",
        example_audio="",
        image_path="",
    )
    assert regular.validate_comparative() is True

    # Comparative with umlaut
    umlaut = Adjective(
        word="alt",
        english="old",
        example="Das ist ein altes Haus.",
        comparative="älter",
        superlative="am ältesten",
        word_audio="",
        example_audio="",
        image_path="",
    )
    assert umlaut.validate_comparative() is True

    # Irregular comparative
    irregular = Adjective(
        word="gut",
        english="good",
        example="Das Essen schmeckt gut.",
        comparative="besser",
        superlative="am besten",
        word_audio="",
        example_audio="",
        image_path="",
    )
    assert irregular.validate_comparative() is True

    # Invalid comparative (wrong ending)
    invalid = Adjective(
        word="schön",
        english="beautiful",
        example="Das ist eine schöne Blume.",
        comparative="schöne",  # Missing -er ending
        superlative="am schönsten",
        word_audio="",
        example_audio="",
        image_path="",
    )
    assert invalid.validate_comparative() is False


def test_superlative_validation() -> None:
    """Test validation of superlative forms."""
    # Regular superlative
    regular = Adjective(
        word="klein",
        english="small",
        example="Meine Wohnung ist klein.",
        comparative="kleiner",
        superlative="am kleinsten",
        word_audio="",
        example_audio="",
        image_path="",
    )
    assert regular.validate_superlative() is True

    # Superlative with umlaut
    umlaut = Adjective(
        word="alt",
        english="old",
        example="Das ist ein altes Haus.",
        comparative="älter",
        superlative="am ältesten",
        word_audio="",
        example_audio="",
        image_path="",
    )
    assert umlaut.validate_superlative() is True

    # Irregular superlative
    irregular = Adjective(
        word="gut",
        english="good",
        example="Das Essen schmeckt gut.",
        comparative="besser",
        superlative="am besten",
        word_audio="",
        example_audio="",
        image_path="",
    )
    assert irregular.validate_superlative() is True

    # Invalid superlative (wrong pattern)
    invalid = Adjective(
        word="schön",
        english="beautiful",
        example="Das ist eine schöne Blume.",
        comparative="schöner",
        superlative="der schönste",  # Wrong pattern, should be "am schönsten"
        word_audio="",
        example_audio="",
        image_path="",
    )
    assert invalid.validate_superlative() is False

    # Test case removed - all German adjectives should have superlative forms


def test_adjective_from_csv() -> None:
    """Test creating an adjective from CSV data."""
    csv_data = {
        "word": "jung",
        "english": "young",
        "example": "Sie ist sehr jung.",
        "comparative": "jünger",
        "superlative": "am jüngsten",
    }

    adj = Adjective(word_audio="", example_audio="", image_path="", **csv_data)
    assert adj.word == "jung"
    assert adj.validate_comparative() is True
    assert adj.validate_superlative() is True
