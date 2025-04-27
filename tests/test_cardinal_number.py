import pytest

from langlearn.models.cardinal_number import CardinalNumber


def test_cardinal_number_initialization():
    """Test that a CardinalNumber can be initialized with valid data."""
    cardinal = CardinalNumber(
        number="42",
        word="zweiundvierzig",
        english="forty-two",
        example="Es sind zweiundvierzig Schüler in der Klasse.",
    )
    assert cardinal.number == "42"
    assert cardinal.word == "zweiundvierzig"
    assert cardinal.english == "forty-two"
    assert cardinal.example == "Es sind zweiundvierzig Schüler in der Klasse."


def test_cardinal_number_validation_empty_number():
    """Test that an empty number raises a ValidationError."""
    with pytest.raises(ValueError, match="Number cannot be empty"):
        CardinalNumber(
            number="",
            word="zweiundvierzig",
            english="forty-two",
            example="Es sind zweiundvierzig Schüler in der Klasse.",
        )


def test_cardinal_number_validation_invalid_number():
    """Test that an invalid number format raises a ValidationError."""
    with pytest.raises(ValueError, match="Number must be a valid integer"):
        CardinalNumber(
            number="42.5",
            word="zweiundvierzig",
            english="forty-two",
            example="Es sind zweiundvierzig Schüler in der Klasse.",
        )


def test_cardinal_number_validation_number_too_small():
    """Test that a number less than 2 raises a ValidationError."""
    with pytest.raises(ValueError, match="Number must be 2 or greater"):
        CardinalNumber(
            number="1", word="eins", english="one", example="Es ist eins Uhr."
        )


def test_cardinal_number_validation_number_too_large():
    """Test that a number greater than 1,000,000 raises a ValidationError."""
    with pytest.raises(ValueError, match="Number must not exceed 1,000,000"):
        CardinalNumber(
            number="1000001",
            word="eine Million eins",
            english="one million and one",
            example="Das Projekt kostet eine Million eins Euro.",
        )


def test_cardinal_number_validation_empty_word():
    """Test that an empty word raises a ValidationError."""
    with pytest.raises(ValueError, match="Word cannot be empty"):
        CardinalNumber(
            number="42",
            word="",
            english="forty-two",
            example="Es sind zweiundvierzig Schüler in der Klasse.",
        )


def test_cardinal_number_validation_invalid_word_characters():
    """Test that a word with invalid characters raises a ValidationError."""
    with pytest.raises(
        ValueError, match="Word must contain only letters, spaces, and umlauts"
    ):
        CardinalNumber(
            number="42",
            word="zweiundvierzig2",
            english="forty-two",
            example="Es sind zweiundvierzig Schüler in der Klasse.",
        )


def test_cardinal_number_validation_word_with_umlauts():
    """Test that a word with umlauts is valid."""
    cardinal = CardinalNumber(
        number="5",
        word="fünf",
        english="five",
        example="Es sind fünf Äpfel auf dem Tisch.",
    )
    assert cardinal.word == "fünf"


def test_cardinal_number_validation_empty_english():
    """Test that an empty English translation raises a ValidationError."""
    with pytest.raises(ValueError, match="English translation cannot be empty"):
        CardinalNumber(
            number="42",
            word="zweiundvierzig",
            english="",
            example="Es sind zweiundvierzig Schüler in der Klasse.",
        )


def test_cardinal_number_validation_invalid_english_characters():
    """Test that an English translation with invalid characters raises a ValidationError."""
    with pytest.raises(
        ValueError,
        match="English translation must contain only letters, spaces, hyphens, and commas",
    ):
        CardinalNumber(
            number="42",
            word="zweiundvierzig",
            english="forty-two!",
            example="Es sind zweiundvierzig Schüler in der Klasse.",
        )


def test_cardinal_number_validation_empty_example():
    """Test that an empty example raises a ValidationError."""
    with pytest.raises(ValueError, match="Example cannot be empty"):
        CardinalNumber(
            number="42", word="zweiundvierzig", english="forty-two", example=""
        )


def test_cardinal_number_validation_missing_word_in_example():
    """Test that an example without the word raises a ValidationError."""
    with pytest.raises(ValueError, match="Example must contain the German word"):
        CardinalNumber(
            number="42",
            word="zweiundvierzig",
            english="forty-two",
            example="Es sind viele Schüler in der Klasse.",
        )


def test_cardinal_number_validation_missing_punctuation():
    """Test that an example without proper punctuation raises a ValidationError."""
    with pytest.raises(ValueError, match="Example must end with proper punctuation"):
        CardinalNumber(
            number="42",
            word="zweiundvierzig",
            english="forty-two",
            example="Es sind zweiundvierzig Schüler in der Klasse",
        )


def test_cardinal_number_string_representation():
    """Test the string representation of a CardinalNumber."""
    cardinal = CardinalNumber(
        number="42",
        word="zweiundvierzig",
        english="forty-two",
        example="Es sind zweiundvierzig Schüler in der Klasse.",
    )
    assert str(cardinal) == "42 (zweiundvierzig) - forty-two"


def test_cardinal_number_from_csv():
    """Test creating a CardinalNumber from CSV data."""
    cardinal = CardinalNumber(
        number="2153",
        word="zweitausendeinhundertdreiundfünfzig",
        english="two thousand one hundred and fifty-three",
        example="Die Bibliothek hat zweitausendeinhundertdreiundfünfzig Bücher.",
    )
    assert cardinal.number == "2153"
    assert cardinal.word == "zweitausendeinhundertdreiundfünfzig"
    assert cardinal.english == "two thousand one hundred and fifty-three"
    assert (
        cardinal.example
        == "Die Bibliothek hat zweitausendeinhundertdreiundfünfzig Bücher."
    )
