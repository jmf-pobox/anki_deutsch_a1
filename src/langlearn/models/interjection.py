import re

from pydantic import BaseModel, Field, ValidationInfo, field_validator


class Interjection(BaseModel):
    """A model representing a German interjection with its translation and usage.

    Attributes:
        word: The German interjection word
        translation: The English translation
        usage: Description of when/how to use the interjection
        example: An example sentence using the interjection
    """

    word: str = Field(..., min_length=1, description="The German interjection word")
    translation: str = Field(..., min_length=1, description="The English translation")
    usage: str = Field(
        ..., min_length=1, description="Description of when/how to use the interjection"
    )
    example: str = Field(
        ..., min_length=1, description="An example sentence using the interjection"
    )

    @field_validator("word")
    @classmethod
    def validate_word(cls, v: str) -> str:
        """Validate the interjection word."""
        if not v:
            raise ValueError("Interjection word cannot be empty")

        # Check for valid characters (letters, umlauts, and common punctuation)
        if not re.match(r"^[a-zA-ZäöüßÄÖÜ!?.,\s]+$", v):
            raise ValueError("Interjection word contains invalid characters")
        return v

    @field_validator("example")
    @classmethod
    def validate_example(cls, v: str, info: ValidationInfo) -> str:
        """Validate the example sentence."""
        if not v:
            raise ValueError("Example sentence cannot be empty")

        word = info.data.get("word", "")
        if word and word not in v:
            raise ValueError("Example sentence must contain the interjection word")

        if not v.endswith((".", "!", "?")):
            raise ValueError("Example sentence must end with proper punctuation")
        return v

    def __str__(self) -> str:
        """Return a string representation of the interjection."""
        return f"{self.word} - {self.translation} ({self.usage})"
