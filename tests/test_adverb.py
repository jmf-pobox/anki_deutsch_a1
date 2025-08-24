"""Unit tests for the Adverb model."""

import pytest

from langlearn.models.adverb import Adverb, AdverbType


def test_adverb_initialization() -> None:
    """Test that an Adverb can be initialized with valid data."""
    adverb = Adverb(
        word="hier",
        english="here",
        type=AdverbType.LOCATION,
        example="Ich wohne hier.",
    )
    assert adverb.word == "hier"
    assert adverb.english == "here"
    assert adverb.type == AdverbType.LOCATION
    assert adverb.example == "Ich wohne hier."


def test_adverb_validation() -> None:
    """Test that validation works correctly for valid adverbs."""
    valid_adverbs = [
        Adverb(
            word="hier",
            english="here",
            type=AdverbType.LOCATION,
            example="Ich wohne hier.",
        ),
        Adverb(
            word="heute",
            english="today",
            type=AdverbType.TIME,
            example="Heute ist es sonnig.",
        ),
        Adverb(
            word="immer",
            english="always",
            type=AdverbType.FREQUENCY,
            example="Er kommt immer pünktlich.",
        ),
    ]

    for adverb in valid_adverbs:
        assert adverb.validate_example() is True
        assert adverb.validate_position() is True


def test_invalid_example_sentences() -> None:
    """Test that invalid example sentences are caught."""
    invalid_examples = [
        Adverb(
            word="hier",
            english="here",
            type=AdverbType.LOCATION,
            example="hier wohne ich.",  # No capital letter
        ),
        Adverb(
            word="heute",
            english="today",
            type=AdverbType.TIME,
            example="Heute ist es sonnig",  # No period
        ),
        Adverb(
            word="immer",
            english="always",
            type=AdverbType.FREQUENCY,
            example="Er kommt pünktlich.",  # Missing adverb
        ),
    ]

    for adverb in invalid_examples:
        assert adverb.validate_example() is False


def test_adverb_position_validation() -> None:
    """Test position validation for different adverb types."""
    # Test location adverbs (should be at end)
    location_adverb = Adverb(
        word="hier",
        english="here",
        type=AdverbType.LOCATION,
        example="Ich wohne hier.",
    )
    assert location_adverb.validate_position() is True

    # Test time adverbs (can be at start or after verb)
    time_adverb_start = Adverb(
        word="heute",
        english="today",
        type=AdverbType.TIME,
        example="Heute ist es sonnig.",
    )
    assert time_adverb_start.validate_position() is True

    time_adverb_middle = Adverb(
        word="heute",
        english="today",
        type=AdverbType.TIME,
        example="Ich gehe heute einkaufen.",
    )
    assert time_adverb_middle.validate_position() is True

    # Test manner adverbs (should be after verb)
    manner_adverb = Adverb(
        word="langsam",
        english="slowly",
        type=AdverbType.MANNER,
        example="Er spricht langsam Deutsch.",
    )
    assert manner_adverb.validate_position() is True

    # Test intensity adverbs (should be before what they modify)
    intensity_adverb = Adverb(
        word="sehr",
        english="very",
        type=AdverbType.INTENSITY,
        example="Das Buch ist sehr interessant.",
    )
    assert intensity_adverb.validate_position() is True


def test_invalid_adverb_positions() -> None:
    """Test that invalid adverb positions are caught."""
    invalid_positions = [
        Adverb(
            word="hier",
            english="here",
            type=AdverbType.LOCATION,
            example="Hier wohne ich.",  # Location adverb at start
        ),
        Adverb(
            word="sehr",
            english="very",
            type=AdverbType.INTENSITY,
            example="Das Buch ist interessant sehr.",  # Intensity adverb at end
        ),
    ]

    for adverb in invalid_positions:
        assert adverb.validate_position() is False


def test_adverb_type_validation() -> None:
    """Test that invalid adverb types are caught."""
    # Test that all valid AdverbType values work
    for adverb_type in AdverbType:
        Adverb(
            word="test",
            english="test",
            type=adverb_type,
            example="Test test.",
        )

    # Test that trying to use an invalid type raises ValueError
    with pytest.raises(ValueError):
        # Create an invalid AdverbType value
        invalid_type = "invalid_type"
        # Try to use it in an Adverb
        Adverb(
            word="test",
            english="test",
            type=AdverbType(invalid_type),  # This should raise ValueError
            example="Test test.",
        )
