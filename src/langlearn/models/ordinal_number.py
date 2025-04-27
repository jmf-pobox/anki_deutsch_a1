from enum import Enum

from pydantic import BaseModel, Field, ValidationInfo, field_validator


class Case(str, Enum):
    """Grammatical cases in German."""

    NOMINATIV = "Nominativ"
    AKKUSATIV = "Akkusativ"
    DATIV = "Dativ"
    GENITIV = "Genitiv"


class Gender(str, Enum):
    """Grammatical genders in German."""

    MASCULINE = "masculine"
    FEMININE = "feminine"
    NEUTER = "neuter"


class OrdinalNumber(BaseModel):
    """Model for German ordinal numbers."""

    number: str = Field(
        ..., description="The ordinal number in digits (e.g., '1st', '2nd')"
    )
    word: str = Field(..., description="The German word for the ordinal number")
    english: str = Field(..., description="The English translation")
    case: Case = Field(..., description="The grammatical case")
    gender: Gender = Field(..., description="The grammatical gender")
    example: str = Field(
        ..., description="An example sentence using the ordinal number"
    )

    @field_validator("number")
    @classmethod
    def validate_number(cls, v: str) -> str:
        """Validate the number format."""
        if not v:
            raise ValueError("Number cannot be empty")
        if not v.endswith(("st", "nd", "rd", "th")):
            raise ValueError("Number must end with 'st', 'nd', 'rd', or 'th'")
        return v

    @field_validator("word")
    @classmethod
    def validate_word(cls, v: str) -> str:
        """Validate the German word."""
        if not v:
            raise ValueError("Word cannot be empty")
        if not v.isalpha():
            raise ValueError("Word must contain only letters")
        return v

    @field_validator("english")
    @classmethod
    def validate_english(cls, v: str) -> str:
        """Validate the English translation."""
        if not v:
            raise ValueError("English translation cannot be empty")
        return v

    @field_validator("example")
    @classmethod
    def validate_example(cls, v: str, info: ValidationInfo) -> str:
        """Validate the example sentence."""
        if not v:
            raise ValueError("Example cannot be empty")
        if "word" in info.data and info.data["word"] not in v:
            raise ValueError("Example must contain the German word")
        if not v.endswith((".", "!", "?")):
            raise ValueError("Example must end with proper punctuation")
        return v

    def __str__(self) -> str:
        """Return a string representation of the ordinal number."""
        return f"{self.number} ({self.word}) - {self.case.value} {self.gender.value}"
