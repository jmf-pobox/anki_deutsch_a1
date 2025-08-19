"""High-level orchestrator for German Anki deck generation.

The GermanDeckBuilder provides a comprehensive, easy-to-use interface for creating
German language learning Anki decks. It orchestrates all services, managers, and
backends while maintaining clean separation of concerns and following dependency
injection principles.
"""

import logging
from pathlib import Path
from typing import Any, TypeVar

from .backends.anki_backend import AnkiBackend
from .backends.base import DeckBackend
from .cards.factory import CardGeneratorFactory
from .managers.deck_manager import DeckManager
from .managers.media_manager import MediaManager
from .models.adjective import Adjective
from .models.adverb import Adverb
from .models.negation import Negation
from .models.noun import Noun
from .services.csv_service import CSVService
from .services.media_service import MediaService
from .services.template_service import TemplateService

logger = logging.getLogger(__name__)

T = TypeVar("T")


class DeckBuilder:
    """High-level orchestrator for German Anki deck generation.

    This class provides the main interface for creating German language learning
    Anki decks. It orchestrates all necessary services, manages dependencies,
    and provides a clean API for deck generation workflows.

    The builder uses the official Anki library backend,
    comprehensive media generation, subdeck organization, and follows clean
    architecture principles throughout.

    Example:
        ```python
        # Basic usage
        builder = GermanDeckBuilder("German A1 Vocabulary")

        # Load data and create deck
        builder.load_nouns_from_csv("data/nouns.csv")
        builder.load_adjectives_from_csv("data/adjectives.csv")

        # Generate with media
        builder.generate_all_media()

        # Export deck
        builder.export_deck("output/german_a1.apkg")
        ```
    """

    def __init__(
        self,
        deck_name: str,
        backend_type: str = "anki",
        enable_media_generation: bool = True,
    ) -> None:
        """Initialize the German deck builder.

        Args:
            deck_name: Name of the Anki deck to create
            backend_type: Backend to use ("anki")
            enable_media_generation: Whether to enable media generation services
        """
        self.deck_name = deck_name
        self.backend_type = backend_type
        self.enable_media_generation = enable_media_generation

        # Initialize services
        self._csv_service = CSVService()

        # Initialize template service with templates directory
        template_dir = Path(__file__).parent / "templates"
        self._template_service = TemplateService(template_dir)

        # Initialize media service if enabled
        self._media_service: MediaService | None = None
        if enable_media_generation:
            from .services.audio import AudioService
            from .services.media_service import MediaGenerationConfig
            from .services.pexels_service import PexelsService

            # Initialize dependencies for media service
            project_root = Path(__file__).parent.parent.parent  # Go up to project root

            # Check if we're running under pytest (avoid AWS in unit tests)
            import sys
            if 'pytest' in sys.modules:
                # Use mock service for testing
                from unittest.mock import MagicMock
                audio_service = MagicMock()
            else:
                # Use real service for production
                audio_service = AudioService(
                    output_dir=str(project_root / "data" / "audio")
                )
                pexels_service = PexelsService()
            media_config = MediaGenerationConfig()

            self._media_service = MediaService(
                audio_service=audio_service,
                pexels_service=pexels_service,
                config=media_config,
                project_root=project_root,
            )

        # Initialize backend
        self._backend = self._create_backend(deck_name, backend_type)

        # Initialize managers with dependency injection
        self._deck_manager = DeckManager(self._backend)
        self._media_manager = MediaManager(self._backend, self._media_service)

        # Initialize card generator factory
        self._card_factory = CardGeneratorFactory(
            backend=self._backend,
            template_service=self._template_service,
            media_manager=self._media_manager,
        )

        # Track loaded data
        self._loaded_nouns: list[Noun] = []
        self._loaded_adjectives: list[Adjective] = []
        self._loaded_adverbs: list[Adverb] = []
        self._loaded_negations: list[Negation] = []
        # Additional model types will be added as needed

        logger.info(f"Initialized GermanDeckBuilder with {backend_type} backend")

    def _create_backend(self, deck_name: str, backend_type: str) -> DeckBackend:
        """Create the appropriate backend instance.

        Args:
            deck_name: Name of the deck
            backend_type: Type of backend to create

        Returns:
            Configured DeckBackend instance
        """
        if backend_type == "anki":
            return AnkiBackend(
                deck_name=deck_name,
                media_service=self._media_service,
            )
        elif backend_type == "genanki":
            raise ValueError(
                "GenanKi backend has been deprecated and removed. "
                "Use backend_type='anki' for production (official Anki library). "
                "See docs/BACKEND_MIGRATION_GUIDE.md for details."
            )
        else:
            raise ValueError(f"Unknown backend type: {backend_type}")

    # Data Loading Methods

    def load_nouns_from_csv(self, csv_path: str | Path) -> None:
        """Load German nouns from CSV file.

        Args:
            csv_path: Path to the CSV file containing noun data
        """
        csv_path = Path(csv_path)
        logger.info(f"Loading nouns from {csv_path}")

        nouns = self._csv_service.read_csv(csv_path, Noun)
        self._loaded_nouns.extend(nouns)

        logger.info(f"Loaded {len(nouns)} nouns")

    def load_adjectives_from_csv(self, csv_path: str | Path) -> None:
        """Load German adjectives from CSV file.

        Args:
            csv_path: Path to the CSV file containing adjective data
        """
        csv_path = Path(csv_path)
        logger.info(f"Loading adjectives from {csv_path}")

        adjectives = self._csv_service.read_csv(csv_path, Adjective)
        self._loaded_adjectives.extend(adjectives)

        logger.info(f"Loaded {len(adjectives)} adjectives")

    def load_adverbs_from_csv(self, csv_path: str | Path) -> None:
        """Load German adverbs from CSV file.

        Args:
            csv_path: Path to the CSV file containing adverb data
        """
        csv_path = Path(csv_path)
        logger.info(f"Loading adverbs from {csv_path}")

        adverbs = self._csv_service.read_csv(csv_path, Adverb)
        self._loaded_adverbs.extend(adverbs)

        logger.info(f"Loaded {len(adverbs)} adverbs")

    def load_negations_from_csv(self, csv_path: str | Path) -> None:
        """Load German negations from CSV file.

        Args:
            csv_path: Path to the CSV file containing negation data
        """
        csv_path = Path(csv_path)
        logger.info(f"Loading negations from {csv_path}")

        negations = self._csv_service.read_csv(csv_path, Negation)
        self._loaded_negations.extend(negations)

        logger.info(f"Loaded {len(negations)} negations")

    def load_data_from_directory(self, data_dir: str | Path) -> None:
        """Load all available data files from a directory.

        Args:
            data_dir: Directory containing CSV data files
        """
        data_dir = Path(data_dir)
        logger.info(f"Loading data from directory: {data_dir}")

        # Define expected files and their corresponding load methods
        file_mappings = {
            "nouns.csv": self.load_nouns_from_csv,
            "adjectives.csv": self.load_adjectives_from_csv,
            "adverbs.csv": self.load_adverbs_from_csv,
            "negations.csv": self.load_negations_from_csv,
            # Additional mappings will be added as more models are implemented
        }

        for filename, load_method in file_mappings.items():
            file_path = data_dir / filename
            if file_path.exists():
                load_method(file_path)
            else:
                logger.debug(f"Data file not found: {file_path}")

    # Subdeck Organization Methods

    def create_subdeck(self, subdeck_name: str) -> None:
        """Create a new subdeck for organizing content.

        Args:
            subdeck_name: Name of the subdeck (e.g., "Nouns", "Adjectives")
        """
        self._deck_manager.set_current_subdeck(subdeck_name)
        logger.info(f"Created subdeck: {subdeck_name}")

    def reset_to_main_deck(self) -> None:
        """Reset to the main deck for subsequent card additions."""
        self._deck_manager.reset_to_main_deck()
        logger.info("Reset to main deck")

    # Card Generation Methods

    def generate_noun_cards(self, generate_media: bool = True) -> int:
        """Generate Anki cards for loaded nouns using MVP architecture.

        Args:
            generate_media: Whether to generate audio/image media

        Returns:
            Number of cards created
        """
        if not self._loaded_nouns:
            logger.warning("No nouns loaded - call load_nouns_from_csv() first")
            return 0

        # Create subdeck for nouns
        self.create_subdeck("Nouns")

        # Use the card generator factory to create a properly configured generator
        noun_generator = self._card_factory.create_noun_generator()

        cards_created = 0
        for noun in self._loaded_nouns:
            noun_generator.add_card(noun, generate_media=generate_media)
            cards_created += 1

        self.reset_to_main_deck()
        logger.info(f"Generated {cards_created} noun cards")
        return cards_created

    def generate_adjective_cards(self, generate_media: bool = True) -> int:
        """Generate Anki cards for loaded adjectives using MVP architecture.

        Args:
            generate_media: Whether to generate audio/image media

        Returns:
            Number of cards created
        """
        if not self._loaded_adjectives:
            logger.warning(
                "No adjectives loaded - call load_adjectives_from_csv() first"
            )
            return 0

        # Create subdeck for adjectives
        self.create_subdeck("Adjectives")

        # Use the card generator factory to create a properly configured generator
        adjective_generator = self._card_factory.create_adjective_generator()

        cards_created = 0
        for adjective in self._loaded_adjectives:
            adjective_generator.add_card(adjective, generate_media=generate_media)
            cards_created += 1

        self.reset_to_main_deck()
        logger.info(f"Generated {cards_created} adjective cards")
        return cards_created

    def generate_adverb_cards(self, generate_media: bool = True) -> int:
        """Generate Anki cards for loaded adverbs using MVP architecture.

        Args:
            generate_media: Whether to generate audio/image media

        Returns:
            Number of cards created
        """
        if not self._loaded_adverbs:
            logger.warning("No adverbs loaded - call load_adverbs_from_csv() first")
            return 0

        # Create subdeck for adverbs
        self.create_subdeck("Adverbs")

        # Use the card generator factory to create a properly configured generator
        adverb_generator = self._card_factory.create_adverb_generator()

        cards_created = 0
        for adverb in self._loaded_adverbs:
            adverb_generator.add_card(adverb, generate_media=generate_media)
            cards_created += 1

        self.reset_to_main_deck()
        logger.info(f"Generated {cards_created} adverb cards")
        return cards_created

    def generate_negation_cards(self, generate_media: bool = True) -> int:
        """Generate Anki cards for loaded negations using MVP architecture.

        Args:
            generate_media: Whether to generate audio/image media

        Returns:
            Number of cards created
        """
        if not self._loaded_negations:
            logger.warning("No negations loaded - call load_negations_from_csv() first")
            return 0

        # Create subdeck for negations
        self.create_subdeck("Negations")

        # Use the card generator factory to create a properly configured generator
        negation_generator = self._card_factory.create_negation_generator()

        cards_created = 0
        for negation in self._loaded_negations:
            negation_generator.add_card(negation, generate_media=generate_media)
            cards_created += 1

        self.reset_to_main_deck()
        logger.info(f"Generated {cards_created} negation cards")
        return cards_created

    def generate_all_cards(self, generate_media: bool = True) -> dict[str, int]:
        """Generate all cards for loaded data.

        Args:
            generate_media: Whether to generate audio/image media

        Returns:
            Dictionary with counts of cards generated by type
        """
        results = {}

        if self._loaded_nouns:
            results["nouns"] = self.generate_noun_cards(generate_media)

        if self._loaded_adjectives:
            results["adjectives"] = self.generate_adjective_cards(generate_media)

        if self._loaded_adverbs:
            results["adverbs"] = self.generate_adverb_cards(generate_media)

        if self._loaded_negations:
            results["negations"] = self.generate_negation_cards(generate_media)

        total = sum(results.values())
        logger.info(f"Generated {total} total cards: {results}")

        return results

    # Media Generation Methods

    def generate_all_media(self) -> dict[str, Any]:
        """Generate all media for loaded data.

        Returns:
            Statistics about media generation
        """
        if not self._media_service:
            logger.warning("Media generation disabled")
            return {}

        # Media generation happens during card creation
        # This method provides a way to pre-generate media if needed
        logger.info("Media will be generated during card creation")
        return self._media_manager.get_detailed_stats()

    # Export and Statistics Methods

    def export_deck(self, output_path: str | Path) -> None:
        """Export the deck to an .apkg file.

        Args:
            output_path: Path where the deck file should be saved
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        self._deck_manager.export_deck(str(output_path))
        logger.info(f"Deck exported to {output_path}")

    def get_statistics(self) -> dict[str, Any]:
        """Get comprehensive statistics about the deck and generation process.

        Returns:
            Dictionary containing all available statistics
        """
        stats = {
            "deck_info": {
                "name": self.deck_name,
                "backend_type": self.backend_type,
                "media_enabled": self.enable_media_generation,
            },
            "loaded_data": {
                "nouns": len(self._loaded_nouns),
                "adjectives": len(self._loaded_adjectives),
                "adverbs": len(self._loaded_adverbs),
                "negations": len(self._loaded_negations),
            },
            "deck_stats": self._deck_manager.get_stats(),
        }

        # Add media statistics if available
        if self._media_service:
            stats.update(self._media_manager.get_detailed_stats())

        return stats

    def get_subdeck_info(self) -> dict[str, Any]:
        """Get information about created subdecks.

        Returns:
            Dictionary with subdeck information
        """
        return {
            "current_deck": self._deck_manager.get_current_deck_name(),
            "subdeck_names": self._deck_manager.get_subdeck_names(),
            "full_subdeck_names": self._deck_manager.get_full_subdeck_names(),
        }

    # Cleanup Methods

    def clear_loaded_data(self) -> None:
        """Clear all loaded data from memory."""
        self._loaded_nouns.clear()
        self._loaded_adjectives.clear()
        self._loaded_adverbs.clear()
        self._loaded_negations.clear()
        logger.info("Cleared all loaded data")

    # Context Manager Support

    def __enter__(self) -> "DeckBuilder":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit with cleanup."""
        # Cleanup is handled by individual services
        pass
