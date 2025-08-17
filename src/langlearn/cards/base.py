"""Base class for Anki card generators."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from ..backends.base import CardTemplate, DeckBackend, NoteType
from ..services.template_service import TemplateService

# Generic type for the data model
T = TypeVar("T")


class BaseCardGenerator(ABC, Generic[T]):
    """Abstract base class for all Anki card generators.

    Uses generics to provide type safety for the data model being processed.
    Works with any backend implementation through the BackendProtocol.
    """

    def __init__(
        self,
        backend: DeckBackend,
        template_service: TemplateService,
        card_type: str,
    ) -> None:
        """Initialize the base card generator.

        Args:
            backend: Backend implementation for deck operations
            template_service: Service for loading card templates
            card_type: Type of card (adjective, noun, etc.)
        """
        self._backend = backend
        self._template_service = template_service
        self._card_type = card_type
        self._note_type_id: str | None = None

    @property
    def note_type_id(self) -> str:
        """Get or create the note type for this card generator.

        Returns:
            Note type ID for this card type

        Raises:
            RuntimeError: If note type creation fails
        """
        if self._note_type_id is None:
            note_type = self._create_note_type()
            self._note_type_id = self._backend.create_note_type(note_type)
            if self._note_type_id is None:
                raise RuntimeError(f"Failed to create note type for {self._card_type}")
        return self._note_type_id

    def add_card(self, data: T) -> None:
        """Add a card to the deck using the backend.

        Args:
            data: The data model to create the card from
        """
        fields = self._extract_fields(data)
        self._backend.add_note(self.note_type_id, fields)

    def _create_note_type(self) -> NoteType:
        """Create a note type for this card generator.

        Returns:
            NoteType configured for this card type
        """
        template = self._template_service.get_template(self._card_type)
        return NoteType(
            name=template.name,
            fields=self._get_field_names(),
            templates=[template],
        )

    @abstractmethod
    def _get_field_names(self) -> list[str]:
        """Get the list of field names for this card type.

        Returns:
            List of field names in the correct order
        """
        raise NotImplementedError

    @abstractmethod
    def _extract_fields(self, data: T) -> list[str]:
        """Extract field values from the data model.

        Args:
            data: The data model to extract fields from

        Returns:
            List of field values in the correct order
        """
        raise NotImplementedError
