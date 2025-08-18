"""Card generator for adjectives."""

from langlearn.backends.base import DeckBackend
from langlearn.cards.base import BaseCardGenerator
from langlearn.models.adjective import Adjective
from langlearn.services.template_service import TemplateService


class AdjectiveCardGenerator(BaseCardGenerator[Adjective]):
    """Generator for adjective cards in Anki with type safety."""

    def __init__(
        self,
        backend: DeckBackend,
        template_service: TemplateService,
    ) -> None:
        """Initialize the adjective card generator.

        Args:
            backend: Backend implementation for deck operations
            template_service: Service for loading card templates
        """
        super().__init__(backend, template_service, "adjective")

    def _get_field_names(self) -> list[str]:
        """Get the list of field names for adjective cards.

        Returns:
            List of field names in the correct order
        """
        return [
            "Word",
            "English",
            "Example",
            "Comparative",
            "Superlative",
            "Image",
            "WordAudio",
            "ExampleAudio",
        ]

    def _extract_fields(self, data: Adjective) -> list[str]:
        """Extract field values from an Adjective model.

        Args:
            data: The Adjective model to extract fields from

        Returns:
            List of field values in the correct order
        """
        return [
            data.word,
            data.english,
            data.example,
            data.comparative,
            data.superlative,
            "",  # Image field (to be filled by backend media processing)
            "",  # WordAudio field (to be filled by backend media processing)
            "",  # ExampleAudio field (to be filled by backend media processing)
        ]
