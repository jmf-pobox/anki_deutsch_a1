"""Card generator for nouns."""

from ..backends.base import DeckBackend
from ..cards.base import BaseCardGenerator
from ..models.noun import Noun
from ..services.template_service import TemplateService


class NounCardGenerator(BaseCardGenerator[Noun]):
    """Generator for noun cards in Anki with type safety."""

    def __init__(
        self,
        backend: DeckBackend,
        template_service: TemplateService,
    ) -> None:
        """Initialize the noun card generator.

        Args:
            backend: Backend implementation for deck operations
            template_service: Service for loading card templates
        """
        super().__init__(backend, template_service, "noun")

    def _get_field_names(self) -> list[str]:
        """Get the list of field names for noun cards.

        Returns:
            List of field names in the correct order
        """
        return [
            "Noun",
            "Article",
            "English",
            "Plural",
            "Example",
            "Related",
            "Image",
            "WordAudio",
            "ExampleAudio",
        ]

    def _extract_fields(self, data: Noun) -> list[str]:
        """Extract field values from a Noun model.

        Args:
            data: The Noun model to extract fields from

        Returns:
            List of field values in the correct order
        """
        return [
            data.noun,
            data.article,
            data.english,
            data.plural,
            data.example,
            data.related,
            "",  # Image field (to be filled by backend media processing)
            "",  # WordAudio field (to be filled by backend media processing)
            "",  # ExampleAudio field (to be filled by backend media processing)
        ]
