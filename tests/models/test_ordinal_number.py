import pytest

from langlearn.models.ordinal_number import Case, Gender, OrdinalNumber


def test_ordinal_number_initialization():
    """Test that an OrdinalNumber can be initialized with valid data."""
    ordinal = OrdinalNumber(
        number="1st",
        word="erste",
        english="first",
        case=Case.NOMINATIV,
        gender=Gender.MASCULINE,
        example="Das ist der erste Tag in Deutschland.",
    )
    assert ordinal.number == "1st"
    assert ordinal.word == "erste"
    assert ordinal.english == "first"
    assert ordinal.case == Case.NOMINATIV
    assert ordinal.gender == Gender.MASCULINE
    assert ordinal.example == "Das ist der erste Tag in Deutschland."


def test_ordinal_number_validation_empty_number():
    """Test that an empty number raises a ValidationError."""
    with pytest.raises(ValueError, match="Number cannot be empty"):
        OrdinalNumber(
            number="",
            word="erste",
            english="first",
            case=Case.NOMINATIV,
            gender=Gender.MASCULINE,
            example="Das ist der erste Tag in Deutschland.",
        )


def test_ordinal_number_validation_invalid_number_format():
    """Test that an invalid number format raises a ValidationError."""
    with pytest.raises(
        ValueError, match="Number must end with 'st', 'nd', 'rd', or 'th'"
    ):
        OrdinalNumber(
            number="1",
            word="erste",
            english="first",
            case=Case.NOMINATIV,
            gender=Gender.MASCULINE,
            example="Das ist der erste Tag in Deutschland.",
        )


def test_ordinal_number_validation_empty_word():
    """Test that an empty word raises a ValidationError."""
    with pytest.raises(ValueError, match="Word cannot be empty"):
        OrdinalNumber(
            number="1st",
            word="",
            english="first",
            case=Case.NOMINATIV,
            gender=Gender.MASCULINE,
            example="Das ist der erste Tag in Deutschland.",
        )


def test_ordinal_number_validation_invalid_word_characters():
    """Test that a word with invalid characters raises a ValidationError."""
    with pytest.raises(ValueError, match="Word must contain only letters"):
        OrdinalNumber(
            number="1st",
            word="erste1",
            english="first",
            case=Case.NOMINATIV,
            gender=Gender.MASCULINE,
            example="Das ist der erste Tag in Deutschland.",
        )


def test_ordinal_number_validation_empty_english():
    """Test that an empty English translation raises a ValidationError."""
    with pytest.raises(ValueError, match="English translation cannot be empty"):
        OrdinalNumber(
            number="1st",
            word="erste",
            english="",
            case=Case.NOMINATIV,
            gender=Gender.MASCULINE,
            example="Das ist der erste Tag in Deutschland.",
        )


def test_ordinal_number_validation_empty_example():
    """Test that an empty example raises a ValidationError."""
    with pytest.raises(ValueError, match="Example cannot be empty"):
        OrdinalNumber(
            number="1st",
            word="erste",
            english="first",
            case=Case.NOMINATIV,
            gender=Gender.MASCULINE,
            example="",
        )


def test_ordinal_number_validation_missing_word_in_example():
    """Test that an example without the word raises a ValidationError."""
    with pytest.raises(ValueError, match="Example must contain the German word"):
        OrdinalNumber(
            number="1st",
            word="erste",
            english="first",
            case=Case.NOMINATIV,
            gender=Gender.MASCULINE,
            example="Das ist ein Tag in Deutschland.",
        )


def test_ordinal_number_validation_missing_punctuation():
    """Test that an example without proper punctuation raises a ValidationError."""
    with pytest.raises(ValueError, match="Example must end with proper punctuation"):
        OrdinalNumber(
            number="1st",
            word="erste",
            english="first",
            case=Case.NOMINATIV,
            gender=Gender.MASCULINE,
            example="Das ist der erste Tag in Deutschland",
        )


def test_ordinal_number_string_representation():
    """Test the string representation of an OrdinalNumber."""
    ordinal = OrdinalNumber(
        number="1st",
        word="erste",
        english="first",
        case=Case.NOMINATIV,
        gender=Gender.MASCULINE,
        example="Das ist der erste Tag in Deutschland.",
    )
    assert str(ordinal) == "1st (erste) - Nominativ masculine"


def test_ordinal_number_all_cases():
    """Test that all cases are valid."""
    for case in Case:
        ordinal = OrdinalNumber(
            number="1st",
            word="erste",
            english="first",
            case=case,
            gender=Gender.MASCULINE,
            example="Das ist der erste Tag in Deutschland.",
        )
        assert ordinal.case == case


def test_ordinal_number_all_genders():
    """Test that all genders are valid."""
    for gender in Gender:
        ordinal = OrdinalNumber(
            number="1st",
            word="erste",
            english="first",
            case=Case.NOMINATIV,
            gender=gender,
            example="Das ist der erste Tag in Deutschland.",
        )
        assert ordinal.gender == gender


def test_ordinal_number_from_csv():
    """Test creating an OrdinalNumber from CSV data."""
    ordinal = OrdinalNumber(
        number="1st",
        word="erste",
        english="first",
        case=Case.NOMINATIV,
        gender=Gender.MASCULINE,
        example="Das ist der erste Tag in Deutschland.",
    )
    assert ordinal.number == "1st"
    assert ordinal.word == "erste"
    assert ordinal.english == "first"
    assert ordinal.case == Case.NOMINATIV
    assert ordinal.gender == Gender.MASCULINE
    assert ordinal.example == "Das ist der erste Tag in Deutschland."
