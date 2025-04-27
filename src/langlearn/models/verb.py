"""Model for German verbs."""

from pydantic import BaseModel, Field


class Verb(BaseModel):
    """Model representing a German verb with its conjugations."""

    verb: str = Field(..., description="The German verb in infinitive form")
    english: str = Field(..., description="English translation")
    present_ich: str = Field(..., description="First person singular present tense")
    present_du: str = Field(..., description="Second person singular present tense")
    present_er: str = Field(..., description="Third person singular present tense")
    perfect: str = Field(..., description="Perfect tense form")
    example: str = Field(..., description="Example sentence using the verb")
