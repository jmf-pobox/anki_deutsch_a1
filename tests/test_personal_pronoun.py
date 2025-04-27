import pytest
from pydantic import ValidationError

from langlearn.models.personal_pronoun import Case, PersonalPronoun


def test_personal_pronoun_initialization() -> None:
    """Test that a personal pronoun can be initialized with valid data."""
    pronoun = PersonalPronoun(
        pronoun="ich",
        english="I",
        case=Case.NOMINATIVE,
        form="ich",
        example="Ich gehe nach Hause.",
    )
    assert pronoun.pronoun == "ich"
    assert pronoun.english == "I"
    assert pronoun.case == Case.NOMINATIVE
    assert pronoun.form == "ich"
    assert pronoun.example == "Ich gehe nach Hause."


def test_personal_pronoun_validation_empty_pronoun() -> None:
    """Test that an empty pronoun raises a ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        PersonalPronoun(
            pronoun="",
            english="I",
            case=Case.NOMINATIVE,
            form="ich",
            example="Ich gehe nach Hause.",
        )
    assert "String should have at least 1 character" in str(exc_info.value)


def test_personal_pronoun_validation_invalid_characters() -> None:
    """Test that invalid characters in the pronoun raise a ValueError."""
    with pytest.raises(ValueError, match="Pronoun contains invalid characters"):
        PersonalPronoun(
            pronoun="ich@",
            english="I",
            case=Case.NOMINATIVE,
            form="ich",
            example="Ich gehe nach Hause.",
        )


def test_personal_pronoun_validation_empty_form() -> None:
    """Test that an empty form raises a ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        PersonalPronoun(
            pronoun="ich",
            english="I",
            case=Case.NOMINATIVE,
            form="",
            example="Ich gehe nach Hause.",
        )
    assert "String should have at least 1 character" in str(exc_info.value)


def test_personal_pronoun_validation_invalid_form_characters() -> None:
    """Test that invalid characters in the form raise a ValueError."""
    with pytest.raises(ValueError, match="Pronoun form contains invalid characters"):
        PersonalPronoun(
            pronoun="ich",
            english="I",
            case=Case.NOMINATIVE,
            form="ich@",
            example="Ich gehe nach Hause.",
        )


def test_personal_pronoun_validation_empty_example() -> None:
    """Test that an empty example raises a ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        PersonalPronoun(
            pronoun="ich", english="I", case=Case.NOMINATIVE, form="ich", example=""
        )
    assert "String should have at least 1 character" in str(exc_info.value)


def test_personal_pronoun_validation_missing_form_in_example() -> None:
    """Test that an example without the pronoun form raises a ValueError."""
    with pytest.raises(
        ValueError, match="Example sentence must contain the pronoun form"
    ):
        PersonalPronoun(
            pronoun="ich",
            english="I",
            case=Case.NOMINATIVE,
            form="ich",
            example="Er geht nach Hause.",
        )


def test_personal_pronoun_validation_missing_punctuation() -> None:
    """Test that an example without proper punctuation raises a ValueError."""
    with pytest.raises(
        ValueError, match="Example sentence must end with proper punctuation"
    ):
        PersonalPronoun(
            pronoun="ich",
            english="I",
            case=Case.NOMINATIVE,
            form="ich",
            example="Ich gehe nach Hause",
        )


def test_personal_pronoun_string_representation() -> None:
    """Test the string representation of a personal pronoun."""
    pronoun = PersonalPronoun(
        pronoun="ich",
        english="I",
        case=Case.NOMINATIVE,
        form="ich",
        example="Ich gehe nach Hause.",
    )
    assert str(pronoun) == "ich (I) - nominative: ich"


def test_personal_pronoun_with_umlauts() -> None:
    """Test that personal pronouns with umlauts are valid."""
    pronoun = PersonalPronoun(
        pronoun="für",
        english="for",
        case=Case.DATIVE,
        form="für",
        example="Das ist für dich.",
    )
    assert pronoun.pronoun == "für"
    assert pronoun.form == "für"


def test_personal_pronoun_all_cases() -> None:
    """Test that all cases are valid."""
    cases = [Case.NOMINATIVE, Case.ACCUSATIVE, Case.DATIVE, Case.GENITIVE]
    for case in cases:
        pronoun = PersonalPronoun(
            pronoun="ich",
            english="I",
            case=case,
            form="ich",
            example="Ich gehe nach Hause.",
        )
        assert pronoun.case == case


def test_personal_pronoun_from_csv() -> None:
    """Test creating a personal pronoun from actual CSV data."""
    pronoun = PersonalPronoun(
        pronoun="ich",
        english="I",
        case=Case.ACCUSATIVE,
        form="mich",
        example="Er sieht mich.",
    )
    assert pronoun.pronoun == "ich"
    assert pronoun.english == "I"
    assert pronoun.case == Case.ACCUSATIVE
    assert pronoun.form == "mich"
    assert pronoun.example == "Er sieht mich."
