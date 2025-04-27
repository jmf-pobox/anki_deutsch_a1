"""Base class for Anki card generators."""

from abc import ABC, abstractmethod
from typing import Any

import genanki  # type: ignore


class BaseCardGenerator(ABC):
    """Abstract base class for all Anki card generators.

    Attributes:
        model_id: Unique ID for the card model
        model_name: Name of the card model
        fields: List of field names for the card
        templates: List of card templates
        css: CSS styling for the card
    """

    def __init__(
        self,
        model_id: int,
        model_name: str,
        fields: list[str],
        templates: list[dict[str, str]],
        css: str = "",
    ) -> None:
        """Initialize the base card generator.

        Args:
            model_id: Unique ID for the card model
            model_name: Name of the card model
            fields: List of field names for the card
            templates: List of card templates
            css: CSS styling for the card
        """
        self.model_id = model_id
        self.model_name = model_name
        self.fields = fields
        self.templates = templates
        self.css = css
        self._model: genanki.Model | None = None

    @property
    def model(self) -> genanki.Model:
        """Get the genanki model for this card type.

        Returns:
            The genanki model
        """
        if self._model is None:
            self._model = genanki.Model(
                self.model_id,
                self.model_name,
                fields=[{"name": field} for field in self.fields],
                templates=self.templates,
                css=self.css,
            )
        return self._model

    @abstractmethod
    def create_note(self, data: Any) -> genanki.Note:
        """Create an Anki note from the given data.

        Args:
            data: The data to create the note from

        Returns:
            The created Anki note
        """
        raise NotImplementedError
