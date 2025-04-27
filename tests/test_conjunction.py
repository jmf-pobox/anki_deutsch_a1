"""Unit tests for the Conjunction model."""

import pytest

from langlearn.models.conjunction import Conjunction, ConjunctionType


def test_conjunction_initialization():
    """Test that a Conjunction can be initialized with valid data."""
    conjunction = Conjunction(
        word="und",
        english="and",
        type=ConjunctionType.COORDINATING,
        example="Ich lese ein Buch und sie schaut fern.",
    )
    assert conjunction.word == "und"
    assert conjunction.english == "and"
    assert conjunction.type == ConjunctionType.COORDINATING
    assert conjunction.example == "Ich lese ein Buch und sie schaut fern."


def test_conjunction_validation():
    """Test that validation works correctly for valid conjunctions."""
    valid_conjunctions = [
        Conjunction(
            word="und",
            english="and",
            type=ConjunctionType.COORDINATING,
            example="Ich lese ein Buch und sie schaut fern.",
        ),
        Conjunction(
            word="weil",
            english="because",
            type=ConjunctionType.SUBORDINATING,
            example="Ich bleibe zu Hause, weil ich krank bin.",
        ),
        Conjunction(
            word="entweder",
            english="either",
            type=ConjunctionType.CORRELATIVE,
            example="Entweder kommst du mit oder du bleibst hier.",
        ),
        Conjunction(
            word="deshalb",
            english="therefore",
            type=ConjunctionType.ADVERBIAL,
            example="Es regnet, deshalb bleibe ich zu Hause.",
        ),
    ]

    for conjunction in valid_conjunctions:
        assert conjunction.validate_example() is True
        assert conjunction.validate_position() is True


def test_invalid_example_sentences():
    """Test that invalid example sentences are caught."""
    invalid_examples = [
        Conjunction(
            word="und",
            english="and",
            type=ConjunctionType.COORDINATING,
            example="und ich lese ein Buch",  # No capital letter
        ),
        Conjunction(
            word="weil",
            english="because",
            type=ConjunctionType.SUBORDINATING,
            example="Ich bleibe zu Hause, weil ich krank bin",  # No period
        ),
        Conjunction(
            word="deshalb",
            english="therefore",
            type=ConjunctionType.ADVERBIAL,
            example="Es regnet, ich bleibe zu Hause.",  # Missing conjunction
        ),
    ]

    for conjunction in invalid_examples:
        assert conjunction.validate_example() is False


def test_conjunction_position_validation():
    """Test position validation for different conjunction types."""
    # Test coordinating conjunctions (should be between clauses)
    coordinating = Conjunction(
        word="und",
        english="and",
        type=ConjunctionType.COORDINATING,
        example="Ich lese ein Buch und sie schaut fern.",
    )
    assert coordinating.validate_position() is True

    # Test subordinating conjunctions (should start dependent clause)
    subordinating = Conjunction(
        word="weil",
        english="because",
        type=ConjunctionType.SUBORDINATING,
        example="Ich bleibe zu Hause, weil ich krank bin.",
    )
    assert subordinating.validate_position() is True

    # Test correlative conjunctions (should be in pairs)
    correlative = Conjunction(
        word="entweder",
        english="either",
        type=ConjunctionType.CORRELATIVE,
        example="Entweder kommst du mit oder du bleibst hier.",
    )
    assert correlative.validate_position() is True

    # Test adverbial conjunctions (can be at start or middle)
    adverbial = Conjunction(
        word="deshalb",
        english="therefore",
        type=ConjunctionType.ADVERBIAL,
        example="Es regnet, deshalb bleibe ich zu Hause.",
    )
    assert adverbial.validate_position() is True


def test_invalid_conjunction_positions():
    """Test that invalid conjunction positions are caught."""
    invalid_positions = [
        Conjunction(
            word="und",
            english="and",
            type=ConjunctionType.COORDINATING,
            example="Und ich lese ein Buch.",  # Coordinating at start
        ),
        Conjunction(
            word="weil",
            english="because",
            type=ConjunctionType.SUBORDINATING,
            example="Weil ich krank bin, bleibe ich zu Hause.",  # Subordinating at start
        ),
        Conjunction(
            word="deshalb",
            english="therefore",
            type=ConjunctionType.ADVERBIAL,
            example="Ich bleibe zu Hause deshalb.",  # Adverbial at end
        ),
    ]

    for conjunction in invalid_positions:
        assert conjunction.validate_position() is False


def test_conjunction_type_validation():
    """Test that invalid conjunction types are caught."""
    # Test that all valid ConjunctionType values work
    for conjunction_type in ConjunctionType:
        Conjunction(
            word="test", english="test", type=conjunction_type, example="Test test."
        )

    # Test that trying to use an invalid type raises ValueError
    with pytest.raises(ValueError):
        # Create an invalid ConjunctionType value
        invalid_type = "invalid_type"
        # Try to use it in a Conjunction
        Conjunction(
            word="test",
            english="test",
            type=ConjunctionType(invalid_type),  # This should raise ValueError
            example="Test test.",
        )
