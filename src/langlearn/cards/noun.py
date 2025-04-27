"""Card generator for nouns."""

import genanki  # type: ignore

from langlearn.cards.base import BaseCardGenerator
from langlearn.models.noun import Noun


class NounCardGenerator(BaseCardGenerator):
    """Generator for noun cards in Anki."""

    def __init__(self, model_id: int) -> None:
        """Initialize the noun card generator.

        Args:
            model_id: Unique ID for the card model
        """
        fields = [
            "Noun",
            "Article",
            "English",
            "Plural",
            "Example",
            "Related",
            "Audio",
        ]

        templates = [
            {
                "name": "Card 1",
                "qfmt": "{{Noun}}<br>{{Article}}",
                "afmt": "{{FrontSide}}<hr id=answer>{{English}}<br>Plural: {{Plural}}<br>Example: {{Example}}<br>Related: {{Related}}",
            }
        ]

        super().__init__(
            model_id=model_id,
            model_name="German Noun",
            fields=fields,
            templates=templates,
        )

    def create_note(self, data: Noun) -> genanki.Note:
        """Create an Anki note from a Noun model.

        Args:
            data: The Noun model to create the note from

        Returns:
            The created Anki note
        """
        return genanki.Note(
            model=self.model,
            fields=[
                data.noun,
                data.article,
                data.english,
                data.plural,
                data.example,
                data.related,
                "",  # Audio field (to be implemented later)
            ],
        )
