import pytest
from pydantic import ValidationError

from langlearn.models.other_pronoun import Case, Gender, OtherPronoun, PronounType


def test_other_pronoun_initialization():
    """Test that a pronoun can be initialized with valid data."""
    pronoun = OtherPronoun(
        pronoun="mein",
        english="my",
        type=PronounType.POSSESSIVE,
        gender=Gender.MASCULINE,
        case=Case.NOMINATIVE,
        form="mein",
        example="Das ist mein Bruder.",
    )
    assert pronoun.pronoun == "mein"
    assert pronoun.english == "my"
    assert pronoun.type == PronounType.POSSESSIVE
    assert pronoun.gender == Gender.MASCULINE
    assert pronoun.case == Case.NOMINATIVE
    assert pronoun.form == "mein"
    assert pronoun.example == "Das ist mein Bruder."


def test_other_pronoun_validation_empty_pronoun():
    """Test that an empty pronoun raises a ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        OtherPronoun(
            pronoun="",
            english="my",
            type=PronounType.POSSESSIVE,
            gender=Gender.MASCULINE,
            case=Case.NOMINATIVE,
            form="mein",
            example="Das ist mein Bruder.",
        )
    assert "String should have at least 1 character" in str(exc_info.value)


def test_other_pronoun_validation_invalid_characters():
    """Test that invalid characters in the pronoun raise a ValueError."""
    with pytest.raises(ValueError, match="Pronoun contains invalid characters"):
        OtherPronoun(
            pronoun="mein@",
            english="my",
            type=PronounType.POSSESSIVE,
            gender=Gender.MASCULINE,
            case=Case.NOMINATIVE,
            form="mein",
            example="Das ist mein Bruder.",
        )


def test_other_pronoun_validation_empty_form():
    """Test that an empty form raises a ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        OtherPronoun(
            pronoun="mein",
            english="my",
            type=PronounType.POSSESSIVE,
            gender=Gender.MASCULINE,
            case=Case.NOMINATIVE,
            form="",
            example="Das ist mein Bruder.",
        )
    assert "String should have at least 1 character" in str(exc_info.value)


def test_other_pronoun_validation_invalid_form_characters():
    """Test that invalid characters in the form raise a ValueError."""
    with pytest.raises(ValueError, match="Pronoun form contains invalid characters"):
        OtherPronoun(
            pronoun="mein",
            english="my",
            type=PronounType.POSSESSIVE,
            gender=Gender.MASCULINE,
            case=Case.NOMINATIVE,
            form="mein@",
            example="Das ist mein Bruder.",
        )


def test_other_pronoun_validation_empty_example():
    """Test that an empty example raises a ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        OtherPronoun(
            pronoun="mein",
            english="my",
            type=PronounType.POSSESSIVE,
            gender=Gender.MASCULINE,
            case=Case.NOMINATIVE,
            form="mein",
            example="",
        )
    assert "String should have at least 1 character" in str(exc_info.value)


def test_other_pronoun_validation_missing_form_in_example():
    """Test that an example without the pronoun form raises a ValueError."""
    with pytest.raises(
        ValueError, match="Example sentence must contain the pronoun form"
    ):
        OtherPronoun(
            pronoun="mein",
            english="my",
            type=PronounType.POSSESSIVE,
            gender=Gender.MASCULINE,
            case=Case.NOMINATIVE,
            form="mein",
            example="Das ist der Bruder.",
        )


def test_other_pronoun_validation_missing_punctuation():
    """Test that an example without proper punctuation raises a ValueError."""
    with pytest.raises(
        ValueError, match="Example sentence must end with proper punctuation"
    ):
        OtherPronoun(
            pronoun="mein",
            english="my",
            type=PronounType.POSSESSIVE,
            gender=Gender.MASCULINE,
            case=Case.NOMINATIVE,
            form="mein",
            example="Das ist mein Bruder",
        )


def test_other_pronoun_string_representation():
    """Test the string representation of a pronoun."""
    pronoun = OtherPronoun(
        pronoun="mein",
        english="my",
        type=PronounType.POSSESSIVE,
        gender=Gender.MASCULINE,
        case=Case.NOMINATIVE,
        form="mein",
        example="Das ist mein Bruder.",
    )
    assert str(pronoun) == "mein (my) - possessive/Masculine/nominative: mein"


def test_other_pronoun_with_umlauts():
    """Test that pronouns with umlauts are valid."""
    pronoun = OtherPronoun(
        pronoun="für",
        english="for",
        type=PronounType.POSSESSIVE,
        gender=Gender.MASCULINE,
        case=Case.NOMINATIVE,
        form="für",
        example="Das ist für den Bruder.",
    )
    assert pronoun.pronoun == "für"
    assert pronoun.form == "für"


def test_other_pronoun_all_cases_and_genders():
    """Test that all cases and genders are valid for possessive and demonstrative pronouns."""
    cases = [Case.NOMINATIVE, Case.ACCUSATIVE, Case.DATIVE, Case.GENITIVE]
    genders = [Gender.MASCULINE, Gender.FEMININE, Gender.NEUTRAL, Gender.PLURAL]
    types = [PronounType.POSSESSIVE, PronounType.DEMONSTRATIVE]

    for pronoun_type in types:
        for case in cases:
            for gender in genders:
                pronoun = OtherPronoun(
                    pronoun="mein",
                    english="my",
                    type=pronoun_type,
                    gender=gender,
                    case=case,
                    form="mein",
                    example="Das ist mein Bruder.",
                )
                assert pronoun.case == case
                assert pronoun.gender == gender


def test_reflexive_pronoun_first_person():
    """Test first person reflexive pronouns."""
    # Accusative
    pronoun = OtherPronoun(
        pronoun="mich",
        english="myself",
        type=PronounType.REFLEXIVE,
        gender=Gender.MASCULINE,
        case=Case.ACCUSATIVE,
        form="mich",
        example="Ich wasche mich.",
    )
    assert pronoun.type == PronounType.REFLEXIVE
    assert pronoun.case == Case.ACCUSATIVE
    assert pronoun.form == "mich"

    # Dative
    pronoun = OtherPronoun(
        pronoun="mir",
        english="myself",
        type=PronounType.REFLEXIVE,
        gender=Gender.MASCULINE,
        case=Case.DATIVE,
        form="mir",
        example="Ich kaufe mir ein Buch.",
    )
    assert pronoun.type == PronounType.REFLEXIVE
    assert pronoun.case == Case.DATIVE
    assert pronoun.form == "mir"


def test_reflexive_pronoun_third_person():
    """Test third person reflexive pronouns."""
    # Test all genders with 'sich'
    genders = [
        (Gender.MASCULINE, "himself", "Er"),
        (Gender.FEMININE, "herself", "Sie"),
        (Gender.NEUTRAL, "itself", "Es"),
    ]

    for gender, english, subject in genders:
        # Accusative
        pronoun = OtherPronoun(
            pronoun="sich",
            english=english,
            type=PronounType.REFLEXIVE,
            gender=gender,
            case=Case.ACCUSATIVE,
            form="sich",
            example=f"{subject} wäscht sich.",
        )
        assert pronoun.type == PronounType.REFLEXIVE
        assert pronoun.case == Case.ACCUSATIVE
        assert pronoun.gender == gender

        # Dative
        pronoun = OtherPronoun(
            pronoun="sich",
            english=english,
            type=PronounType.REFLEXIVE,
            gender=gender,
            case=Case.DATIVE,
            form="sich",
            example=f"{subject} kauft sich ein Buch.",
        )
        assert pronoun.type == PronounType.REFLEXIVE
        assert pronoun.case == Case.DATIVE
        assert pronoun.gender == gender


def test_reflexive_pronoun_formal():
    """Test formal reflexive pronouns."""
    # Accusative
    pronoun = OtherPronoun(
        pronoun="Sich",
        english="yourself (formal)",
        type=PronounType.REFLEXIVE,
        gender=Gender.MASCULINE,
        case=Case.ACCUSATIVE,
        form="Sich",
        example="Sie waschen Sich.",
    )
    assert pronoun.type == PronounType.REFLEXIVE
    assert pronoun.case == Case.ACCUSATIVE
    assert pronoun.form == "Sich"

    # Dative
    pronoun = OtherPronoun(
        pronoun="Sich",
        english="yourself (formal)",
        type=PronounType.REFLEXIVE,
        gender=Gender.MASCULINE,
        case=Case.DATIVE,
        form="Sich",
        example="Sie kaufen Sich ein Buch.",
    )
    assert pronoun.type == PronounType.REFLEXIVE
    assert pronoun.case == Case.DATIVE
    assert pronoun.form == "Sich"


def test_demonstrative_pronoun_dieser():
    """Test 'dieser' demonstrative pronouns."""
    test_cases = [
        (Gender.MASCULINE, Case.NOMINATIVE, "dieser", "Dieser Mann ist groß."),
        (Gender.MASCULINE, Case.ACCUSATIVE, "diesen", "Ich sehe diesen Mann."),
        (Gender.FEMININE, Case.NOMINATIVE, "diese", "Diese Frau ist groß."),
        (Gender.NEUTRAL, Case.DATIVE, "diesem", "Ich gebe diesem Kind das Buch."),
        (Gender.PLURAL, Case.GENITIVE, "dieser", "Das ist das Haus dieser Leute."),
    ]

    for gender, case, form, example in test_cases:
        pronoun = OtherPronoun(
            pronoun="dieser",
            english="this",
            type=PronounType.DEMONSTRATIVE,
            gender=gender,
            case=case,
            form=form,
            example=example,
        )
        assert pronoun.type == PronounType.DEMONSTRATIVE
        assert pronoun.gender == gender
        assert pronoun.case == case
        assert pronoun.form == form


def test_demonstrative_pronoun_der():
    """Test 'der' demonstrative pronouns."""
    test_cases = [
        (Gender.MASCULINE, Case.NOMINATIVE, "der", "Der Mann ist groß."),
        (Gender.MASCULINE, Case.ACCUSATIVE, "den", "Ich sehe den Mann."),
        (Gender.FEMININE, Case.NOMINATIVE, "die", "Die Frau ist groß."),
        (Gender.NEUTRAL, Case.DATIVE, "dem", "Ich gebe dem Kind das Buch."),
        (Gender.PLURAL, Case.GENITIVE, "deren", "Das ist das Haus deren Leute."),
    ]

    for gender, case, form, example in test_cases:
        pronoun = OtherPronoun(
            pronoun="der",
            english="that",
            type=PronounType.DEMONSTRATIVE,
            gender=gender,
            case=case,
            form=form,
            example=example,
        )
        assert pronoun.type == PronounType.DEMONSTRATIVE
        assert pronoun.gender == gender
        assert pronoun.case == case
        assert pronoun.form == form


def test_demonstrative_pronoun_solcher():
    """Test 'solcher' demonstrative pronouns."""
    test_cases = [
        (Gender.MASCULINE, Case.NOMINATIVE, "solcher", "Solcher Mann ist selten."),
        (Gender.MASCULINE, Case.ACCUSATIVE, "solchen", "Ich sehe solchen Mann."),
        (Gender.FEMININE, Case.NOMINATIVE, "solche", "Solche Frau ist selten."),
        (Gender.NEUTRAL, Case.DATIVE, "solchem", "Ich gebe solchem Kind das Buch."),
        (Gender.PLURAL, Case.GENITIVE, "solcher", "Das ist das Haus solcher Leute."),
    ]

    for gender, case, form, example in test_cases:
        pronoun = OtherPronoun(
            pronoun="solcher",
            english="such",
            type=PronounType.DEMONSTRATIVE,
            gender=gender,
            case=case,
            form=form,
            example=example,
        )
        assert pronoun.type == PronounType.DEMONSTRATIVE
        assert pronoun.gender == gender
        assert pronoun.case == case
        assert pronoun.form == form


def test_demonstrative_pronoun_invalid_case():
    """Test that demonstrative pronouns accept all cases."""
    for case in Case:
        pronoun = OtherPronoun(
            pronoun="dieser",
            english="this",
            type=PronounType.DEMONSTRATIVE,
            gender=Gender.MASCULINE,
            case=case,
            form="dieser",
            example="Dieser Mann ist groß.",
        )
        assert pronoun.case == case


def test_reflexive_pronoun_invalid_case():
    """Test that reflexive pronouns only accept accusative and dative cases."""
    invalid_cases = [Case.NOMINATIVE, Case.GENITIVE]
    for case in invalid_cases:
        with pytest.raises(
            ValueError,
            match="Reflexive pronouns can only be in accusative or dative case",
        ):
            OtherPronoun(
                pronoun="sich",
                english="himself",
                type=PronounType.REFLEXIVE,
                gender=Gender.MASCULINE,
                case=case,
                form="sich",
                example="Er wäscht sich.",
            )


def test_reflexive_pronoun_invalid_example():
    """Test that reflexive pronouns require reflexive verbs in examples."""
    with pytest.raises(
        ValueError, match="Example for reflexive pronoun must contain a reflexive verb"
    ):
        OtherPronoun(
            pronoun="sich",
            english="himself",
            type=PronounType.REFLEXIVE,
            gender=Gender.MASCULINE,
            case=Case.ACCUSATIVE,
            form="sich",
            example="Er liest ein Buch.",
        )


def test_other_pronoun_from_csv():
    """Test creating a pronoun from actual CSV data."""
    pronoun = OtherPronoun(
        pronoun="mein",
        english="my",
        type=PronounType.POSSESSIVE,
        gender=Gender.MASCULINE,
        case=Case.ACCUSATIVE,
        form="meinen",
        example="Ich sehe meinen Bruder.",
    )
    assert pronoun.pronoun == "mein"
    assert pronoun.english == "my"
    assert pronoun.type == PronounType.POSSESSIVE
    assert pronoun.gender == Gender.MASCULINE
    assert pronoun.case == Case.ACCUSATIVE
    assert pronoun.form == "meinen"
    assert pronoun.example == "Ich sehe meinen Bruder."
