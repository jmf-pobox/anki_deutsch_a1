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
