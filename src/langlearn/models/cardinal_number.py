from pydantic import BaseModel, Field, ValidationInfo, field_validator


class CardinalNumber(BaseModel):
    """Model for German cardinal numbers."""

    number: str = Field(
        ..., description="The number in digits (e.g., '2', '42', '1000000')"
    )
    word: str = Field(..., description="The German word for the number")
    english: str = Field(..., description="The English translation")
    example: str = Field(..., description="An example sentence using the number")

    @field_validator("number")
    @classmethod
    def validate_number(cls, v: str) -> str:
        """Validate the number format."""
        if not v:
            raise ValueError("Number cannot be empty")
        try:
            num = int(v)
            if num < 2:  # We start from 2 as specified
                raise ValueError("Number must be 2 or greater")
            if num > 1000000:  # Upper limit as specified
                raise ValueError("Number must not exceed 1,000,000")
        except ValueError as e:
            if str(e).startswith("Number must"):
                raise e
            raise ValueError("Number must be a valid integer")
        return v

    @field_validator("word")
    @classmethod
    def validate_word(cls, v: str) -> str:
        """Validate the German word."""
        if not v:
            raise ValueError("Word cannot be empty")
        # Allow letters, spaces, and umlauts
        valid_chars = set("abcdefghijklmnopqrstuvwxyzäöüß ")
        if not all(char.lower() in valid_chars for char in v):
            raise ValueError("Word must contain only letters, spaces, and umlauts")
        return v

    @field_validator("english")
    @classmethod
    def validate_english(cls, v: str) -> str:
        """Validate the English translation."""
        if not v:
            raise ValueError("English translation cannot be empty")
        # Allow letters, spaces, hyphens, and commas for numbers like "one hundred"
        valid_chars = set("abcdefghijklmnopqrstuvwxyz ,.-")
        if not all(char.lower() in valid_chars for char in v):
            raise ValueError(
                "English translation must contain only letters, spaces, hyphens, and commas"
            )
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
        """Return a string representation of the cardinal number."""
        return f"{self.number} ({self.word}) - {self.english}"
