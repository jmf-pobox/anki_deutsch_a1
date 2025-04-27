import pytest
from pydantic import ValidationError

from langlearn.models.interjection import Interjection


def test_interjection_initialization():
    """Test that an interjection can be initialized with valid data."""
    interjection = Interjection(
        word="Ach",
        translation="oh",
        usage="expression of surprise or realization",
        example="Ach, jetzt verstehe ich!",
    )
    assert interjection.word == "Ach"
    assert interjection.translation == "oh"
    assert interjection.usage == "expression of surprise or realization"
    assert interjection.example == "Ach, jetzt verstehe ich!"


def test_interjection_validation_empty_word():
    """Test that an empty word raises a ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        Interjection(
            word="",
            translation="oh",
            usage="expression of surprise",
            example="Ach, das ist toll!",
        )
    assert "String should have at least 1 character" in str(exc_info.value)


def test_interjection_validation_invalid_characters():
    """Test that invalid characters in the word raise a ValueError."""
    with pytest.raises(
        ValueError, match="Interjection word contains invalid characters"
    ):
        Interjection(
            word="Ach@",
            translation="oh",
            usage="expression of surprise",
            example="Ach, das ist toll!",
        )


def test_interjection_validation_empty_example():
    """Test that an empty example raises a ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        Interjection(
            word="Ach", translation="oh", usage="expression of surprise", example=""
        )
    assert "String should have at least 1 character" in str(exc_info.value)


def test_interjection_validation_missing_word_in_example():
    """Test that an example without the interjection word raises a ValueError."""
    with pytest.raises(
        ValueError, match="Example sentence must contain the interjection word"
    ):
        Interjection(
            word="Ach",
            translation="oh",
            usage="expression of surprise",
            example="Das ist toll!",
        )


def test_interjection_validation_missing_punctuation():
    """Test that an example without proper punctuation raises a ValueError."""
    with pytest.raises(
        ValueError, match="Example sentence must end with proper punctuation"
    ):
        Interjection(
            word="Ach",
            translation="oh",
            usage="expression of surprise",
            example="Ach das ist toll",
        )


def test_interjection_string_representation():
    """Test the string representation of an interjection."""
    interjection = Interjection(
        word="Ach",
        translation="oh",
        usage="expression of surprise",
        example="Ach, das ist toll!",
    )
    assert str(interjection) == "Ach - oh (expression of surprise)"


def test_interjection_with_umlauts():
    """Test that interjections with umlauts are valid."""
    interjection = Interjection(
        word="Ähm",
        translation="um",
        usage="expression of hesitation",
        example="Ähm, ich weiß nicht...",
    )
    assert interjection.word == "Ähm"
    assert interjection.translation == "um"


def test_interjection_with_punctuation():
    """Test that interjections with punctuation are valid."""
    interjection = Interjection(
        word="Hoppla!",
        translation="oops",
        usage="expression of mistake",
        example="Hoppla! Das war nicht beabsichtigt!",
    )
    assert interjection.word == "Hoppla!"
    assert interjection.translation == "oops"
