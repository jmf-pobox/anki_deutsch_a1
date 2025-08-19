"""Factory for creating card generators with proper dependency injection."""

from langlearn.backends.base import DeckBackend
from langlearn.cards.adjective import AdjectiveCardGenerator
from langlearn.cards.adverb import AdverbCardGenerator
from langlearn.cards.negation import NegationCardGenerator
from langlearn.cards.noun import NounCardGenerator
from langlearn.managers.media_manager import MediaManager
from langlearn.services.template_service import TemplateService


class CardGeneratorFactory:
    """Factory for creating card generators with proper dependencies.

    This factory encapsulates the dependency injection logic for creating
    card generators, ensuring they have the proper backend, template service,
    media manager, and German language service dependencies.
    """

    def __init__(
        self,
        backend: DeckBackend,
        template_service: TemplateService,
        media_manager: MediaManager | None = None,
    ) -> None:
        """Initialize the card generator factory.

        Args:
            backend: Backend implementation for deck operations
            template_service: Service for loading card templates
            media_manager: Optional media manager for audio/image generation
        """
        self._backend = backend
        self._template_service = template_service
        self._media_manager = media_manager

    def create_noun_generator(self) -> NounCardGenerator:
        """Create a noun card generator with all dependencies.

        Returns:
            Configured NounCardGenerator instance
        """
        return NounCardGenerator(
            backend=self._backend,
            template_service=self._template_service,
            media_manager=self._media_manager,
        )

    def create_adjective_generator(self) -> AdjectiveCardGenerator:
        """Create an adjective card generator with all dependencies.

        Returns:
            Configured AdjectiveCardGenerator instance
        """
        return AdjectiveCardGenerator(
            backend=self._backend,
            template_service=self._template_service,
            media_manager=self._media_manager,
        )

    def create_adverb_generator(self) -> AdverbCardGenerator:
        """Create an adverb card generator with all dependencies.

        Returns:
            Configured AdverbCardGenerator instance
        """
        return AdverbCardGenerator(
            backend=self._backend,
            template_service=self._template_service,
            media_manager=self._media_manager,
        )

    def create_negation_generator(self) -> NegationCardGenerator:
        """Create a negation card generator with all dependencies.

        Returns:
            Configured NegationCardGenerator instance
        """
        return NegationCardGenerator(
            backend=self._backend,
            template_service=self._template_service,
            media_manager=self._media_manager,
        )
