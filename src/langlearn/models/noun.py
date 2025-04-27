"""Model for German nouns."""

from pydantic import BaseModel, Field


class Noun(BaseModel):
    """Model representing a German noun with its properties."""

    noun: str = Field(..., description="The German noun")
    article: str = Field(..., description="The definite article (der/die/das)")
    english: str = Field(..., description="English translation")
    plural: str = Field(..., description="Plural form of the noun")
    example: str = Field(..., description="Example sentence using the noun")
    related: str = Field(default="", description="Related words or phrases")
