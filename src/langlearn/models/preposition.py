"""Model for German prepositions."""

from pydantic import BaseModel, Field


class Preposition(BaseModel):
    """Model representing a German preposition with its properties."""

    preposition: str = Field(..., description="The German preposition")
    english: str = Field(..., description="English translation")
    case: str = Field(
        ...,
        description="The case(s) the preposition takes (Accusative/Dative/Genitive)",
    )
    example1: str = Field(..., description="First example sentence")
    example2: str = Field(..., description="Second example sentence")
