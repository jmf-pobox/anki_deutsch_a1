"""Unit tests for the Negation model."""

import pytest

from langlearn.models.negation import Negation, NegationType


def test_negation_initialization() -> None:
    """Test that a Negation can be initialized with valid data."""
    negation = Negation(
        word="nicht",
        english="not",
        type=NegationType.GENERAL,
        example="Ich verstehe das nicht.",
    )
    assert negation.word == "nicht"
    assert negation.english == "not"
    assert negation.type == NegationType.GENERAL
    assert negation.example == "Ich verstehe das nicht."


def test_negation_validation() -> None:
    """Test that validation works correctly for valid negations."""
    valid_negations = [
        Negation(
            word="nicht",
            english="not",
            type=NegationType.GENERAL,
            example="Ich verstehe das nicht.",
        ),
        Negation(
            word="kein",
            english="no/not a",
            type=NegationType.ARTICLE,
            example="Ich habe kein Auto.",
        ),
        Negation(
            word="niemand",
            english="nobody",
            type=NegationType.PRONOUN,
            example="Niemand ist hier.",
        ),
        Negation(
            word="nie",
            english="never",
            type=NegationType.TEMPORAL,
            example="Ich war noch nie in Berlin.",
        ),
        Negation(
            word="nirgends",
            english="nowhere",
            type=NegationType.SPATIAL,
            example="Das Buch ist nirgends zu finden.",
        ),
        Negation(
            word="weder",
            english="neither",
            type=NegationType.CORRELATIVE,
            example="Ich spreche weder Französisch noch Spanisch.",
        ),
        Negation(
            word="gar nicht",
            english="not at all",
            type=NegationType.INTENSIFIER,
            example="Das gefällt mir gar nicht.",
        ),
    ]

    for negation in valid_negations:
        assert negation.validate_example() is True
        assert negation.validate_position() is True


def test_invalid_example_sentences() -> None:
    """Test that invalid example sentences are caught."""
    invalid_examples = [
        Negation(
            word="nicht",
            english="not",
            type=NegationType.GENERAL,
            example="nicht verstehe das.",  # No capital letter
        ),
        Negation(
            word="kein",
            english="no/not a",
            type=NegationType.ARTICLE,
            example="Ich habe kein Auto",  # No period
        ),
        Negation(
            word="niemand",
            english="nobody",
            type=NegationType.PRONOUN,
            example="Jemand ist hier.",  # Missing negation
        ),
    ]

    for negation in invalid_examples:
        assert negation.validate_example() is False


def test_negation_position_validation() -> None:
    """Test position validation for different negation types."""
    # Test general negation (at end or before adjective)
    general_end = Negation(
        word="nicht",
        english="not",
        type=NegationType.GENERAL,
        example="Ich verstehe das nicht.",
    )
    assert general_end.validate_position() is True

    general_before_adj = Negation(
        word="nicht",
        english="not",
        type=NegationType.GENERAL,
        example="Das ist nicht gut.",
    )
    assert general_before_adj.validate_position() is True

    # Test article negation (before noun)
    article = Negation(
        word="kein",
        english="no/not a",
        type=NegationType.ARTICLE,
        example="Ich habe kein Auto.",
    )
    assert article.validate_position() is True

    # Test pronoun negation (as subject)
    pronoun_subject = Negation(
        word="niemand",
        english="nobody",
        type=NegationType.PRONOUN,
        example="Niemand ist hier.",
    )
    assert pronoun_subject.validate_position() is True

    # Test temporal negation (not at end)
    temporal = Negation(
        word="nie",
        english="never",
        type=NegationType.TEMPORAL,
        example="Ich war noch nie in Berlin.",
    )
    assert temporal.validate_position() is True

    # Test spatial negation (middle/end)
    spatial = Negation(
        word="nirgends",
        english="nowhere",
        type=NegationType.SPATIAL,
        example="Das Buch ist nirgends zu finden.",
    )
    assert spatial.validate_position() is True

    # Test correlative negation (with pair)
    correlative = Negation(
        word="weder",
        english="neither",
        type=NegationType.CORRELATIVE,
        example="Ich spreche weder Französisch noch Spanisch.",
    )
    assert correlative.validate_position() is True

    # Test intensifier negation
    intensifier = Negation(
        word="gar nicht",
        english="not at all",
        type=NegationType.INTENSIFIER,
        example="Das gefällt mir gar nicht.",
    )
    assert intensifier.validate_position() is True


def test_invalid_negation_positions() -> None:
    """Test that invalid negation positions are caught."""
    invalid_positions = [
        Negation(
            word="nicht",
            english="not",
            type=NegationType.GENERAL,
            example="Nicht ich verstehe das.",  # General negation at start
        ),
        Negation(
            word="kein",
            english="no/not a",
            type=NegationType.ARTICLE,
            example="Das Auto kein.",  # Article negation at end
        ),
        Negation(
            word="nie",
            english="never",
            type=NegationType.TEMPORAL,
            example="Ich war in Berlin nie.",  # Temporal negation at end
        ),
        Negation(
            word="weder",
            english="neither",
            type=NegationType.CORRELATIVE,
            example="Ich spreche weder.",  # Correlative without pair
        ),
    ]

    for negation in invalid_positions:
        assert negation.validate_position() is False


def test_negation_type_validation() -> None:
    """Test that invalid negation types are caught."""
    # Test that all valid NegationType values work
    for negation_type in NegationType:
        Negation(word="test", english="test", type=negation_type, example="Test test.")

    # Test that trying to use an invalid type raises ValueError
    with pytest.raises(ValueError):
        # Create an invalid NegationType value
        invalid_type = "invalid_type"
        # Try to use it in a Negation
        Negation(
            word="test",
            english="test",
            type=NegationType(invalid_type),  # This should raise ValueError
            example="Test test.",
        )
