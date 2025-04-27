import re
from enum import Enum

from pydantic import BaseModel, Field, ValidationInfo, field_validator


class Case(Enum):
    """Enum representing German grammatical cases."""

    NOMINATIVE = "nominative"
    ACCUSATIVE = "accusative"
    DATIVE = "dative"
    GENITIVE = "genitive"


class PersonalPronoun(BaseModel):
    """A model representing a German personal pronoun with its various case forms.

    Attributes:
        pronoun: The base form of the pronoun
        english: The English translation
        case: The grammatical case of this form
        form: The specific form of the pronoun for the given case
        example: An example sentence using the pronoun
    """

    pronoun: str = Field(..., min_length=1, description="The base form of the pronoun")
    english: str = Field(..., min_length=1, description="The English translation")
    case: Case = Field(..., description="The grammatical case of this form")
    form: str = Field(
        ...,
        min_length=1,
        description="The specific form of the pronoun for the given case",
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
        if form and form.lower() not in v.lower():
            raise ValueError("Example sentence must contain the pronoun form")

        if not v.endswith((".", "!", "?")):
            raise ValueError("Example sentence must end with proper punctuation")
        return v

    def __str__(self) -> str:
        """Return a string representation of the personal pronoun."""
        return f"{self.pronoun} ({self.english}) - {self.case.value}: {self.form}"
