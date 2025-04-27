import re
from enum import Enum

from pydantic import BaseModel, Field, ValidationInfo, field_validator


class Gender(Enum):
    """Enum representing German grammatical genders."""

    MASCULINE = "Masculine"
    FEMININE = "Feminine"
    NEUTRAL = "Neutral"
    PLURAL = "Plural"


class Case(Enum):
    """Enum representing German grammatical cases."""

    NOMINATIVE = "nominative"
    ACCUSATIVE = "accusative"
    DATIVE = "dative"
    GENITIVE = "genitive"


class PronounType(Enum):
    """Enum representing different types of German pronouns."""

    POSSESSIVE = "possessive"
    REFLEXIVE = "reflexive"
    DEMONSTRATIVE = "demonstrative"


class OtherPronoun(BaseModel):
    """A model representing various types of German pronouns with their forms.

    Attributes:
        pronoun: The base form of the pronoun
        english: The English translation
        type: The type of pronoun (possessive, reflexive, or demonstrative)
        gender: The grammatical gender this form is used with
        case: The grammatical case of this form
        form: The specific form of the pronoun for the given gender and case
        example: An example sentence using the pronoun
    """

    pronoun: str = Field(..., min_length=1, description="The base form of the pronoun")
    english: str = Field(..., min_length=1, description="The English translation")
    type: PronounType = Field(..., description="The type of pronoun")
    gender: Gender = Field(
        ..., description="The grammatical gender this form is used with"
    )
    case: Case = Field(..., description="The grammatical case of this form")
    form: str = Field(
        ...,
        min_length=1,
        description="The specific form of the pronoun for the given gender and case",
    )
    example: str = Field(
        ..., min_length=1, description="An example sentence using the pronoun"
    )

    @field_validator("pronoun")
    @classmethod
    def validate_pronoun(cls, v: str) -> str:
        """Validate the pronoun base form."""
        if not v:
            raise ValueError("Pronoun cannot be empty")

        # Check for valid characters (letters and umlauts)
        if not re.match(r"^[a-zA-ZäöüßÄÖÜ]+$", v):
            raise ValueError("Pronoun contains invalid characters")
        return v

    @field_validator("form")
    @classmethod
    def validate_form(cls, v: str, info: ValidationInfo) -> str:
        """Validate the pronoun form."""
        if not v:
            raise ValueError("Pronoun form cannot be empty")

        # Check for valid characters (letters and umlauts)
        if not re.match(r"^[a-zA-ZäöüßÄÖÜ]+$", v):
            raise ValueError("Pronoun form contains invalid characters")
        return v

    @field_validator("example")
    @classmethod
    def validate_example(cls, v: str, info: ValidationInfo) -> str:
        """Validate the example sentence."""
        if not v:
            raise ValueError("Example sentence cannot be empty")

        form = info.data.get("form", "")
        pronoun_type = info.data.get("type")

        if not v.endswith((".", "!", "?")):
            raise ValueError("Example sentence must end with proper punctuation")

        # Additional validation for reflexive pronouns
        if pronoun_type == PronounType.REFLEXIVE:
            # Check if the example contains a reflexive verb pattern
            reflexive_patterns = [
                "sich",
                "mich",
                "dich",
                "uns",
                "euch",  # Basic reflexive pronouns
                "mir",
                "dir",  # Dative reflexive pronouns
                "waschen",
                "freuen",
                "ärgern",
                "bewegen",  # Common reflexive verbs
                "kaufen.*mir",
                "kaufen.*dir",
                "kaufen.*sich",  # Dative reflexive patterns
                "Sich",  # Formal reflexive
            ]
            if not any(pattern.lower() in v.lower() for pattern in reflexive_patterns):
                raise ValueError(
                    "Example for reflexive pronoun must contain a reflexive verb"
                )

        if form and form.lower() not in v.lower():
            raise ValueError("Example sentence must contain the pronoun form")

        return v

    @field_validator("case")
    @classmethod
    def validate_case(cls, v: Case, info: ValidationInfo) -> Case:
        """Validate the case based on pronoun type."""
        pronoun_type = info.data.get("type")

        if pronoun_type == PronounType.REFLEXIVE and v not in [
            Case.ACCUSATIVE,
            Case.DATIVE,
        ]:
            raise ValueError(
                "Reflexive pronouns can only be in accusative or dative case"
            )

        return v

    def __str__(self) -> str:
        """Return a string representation of the pronoun."""
        return (
            f"{self.pronoun} ({self.english}) - {self.type.value}/"
            f"{self.gender.value}/{self.case.value}: {self.form}"
        )
