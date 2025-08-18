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
from .backends.genanki_backend import GenankiBackend
from .managers.deck_manager import DeckManager
from .managers.media_manager import MediaManager
from .models.adjective import Adjective
from .models.adverb import Adverb
from .models.negation import Negation
from .models.noun import Noun
from .services.csv_service import CSVService
from .services.german_language_service import GermanLanguageService
from .services.media_service import MediaService
from .services.template_service import TemplateService

logger = logging.getLogger(__name__)

T = TypeVar("T")


class GermanDeckBuilder:
    """High-level orchestrator for German Anki deck generation.

    This class provides the main interface for creating German language learning
    Anki decks. It orchestrates all necessary services, manages dependencies,
    and provides a clean API for deck generation workflows.

    The builder supports both genanki and official Anki library backends,
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
            backend_type: Backend to use ("anki" or "genanki")
            enable_media_generation: Whether to enable media generation services
        """
        self.deck_name = deck_name
        self.backend_type = backend_type
        self.enable_media_generation = enable_media_generation

        # Initialize services
        self._csv_service = CSVService()
        self._german_service = GermanLanguageService()

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
            audio_service = AudioService(output_dir="data/audio")
            pexels_service = PexelsService()
            media_config = MediaGenerationConfig()
            project_root = Path(__file__).parent.parent.parent  # Go up to project root

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
                german_service=self._german_service,
            )
        elif backend_type == "genanki":
            return GenankiBackend(
                deck_name=deck_name,
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
        """Generate Anki cards for loaded nouns.

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

        # Get or create noun note type
        noun_note_type = self._template_service.get_noun_note_type()
        note_type_id = self._deck_manager.create_note_type(noun_note_type)
        print(
            f"DEBUG: Using noun note type ID: {note_type_id} for {noun_note_type.name}"
        )

        cards_created = 0

        for noun in self._loaded_nouns:
            # Use existing media paths from CSV or generate new media
            audio_ref = ""
            image_html = ""
            example_audio_ref = ""

            # Check for existing word audio
            if noun.word_audio and Path(noun.word_audio).exists():
                audio_file = self._media_manager.add_media_file(noun.word_audio)
                if audio_file:
                    audio_ref = audio_file.reference
            elif generate_media and self._media_service:
                # Generate audio for combined noun forms only if no existing audio
                audio_text = self._german_service.get_combined_noun_audio_text(noun)
                audio_file = self._media_manager.generate_and_add_audio(audio_text)
                if audio_file:
                    audio_ref = audio_file.reference

            # Check for existing example audio
            if noun.example_audio and Path(noun.example_audio).exists():
                example_audio_file = self._media_manager.add_media_file(
                    noun.example_audio
                )
                if example_audio_file:
                    example_audio_ref = example_audio_file.reference
            elif generate_media and self._media_service:
                # Generate example sentence audio if no existing audio
                example_audio_file = self._media_manager.generate_and_add_audio(
                    noun.example
                )
                if example_audio_file:
                    example_audio_ref = example_audio_file.reference

            # Check for existing image - first check CSV path,
            # then check expected filename
            image_found = False
            if noun.image_path and Path(noun.image_path).exists():
                image_file = self._media_manager.add_media_file(noun.image_path)
                if image_file:
                    filename = image_file.reference
                    image_html = f'<img src="{filename}">'
                    image_found = True
            else:
                # Check for existing image by expected filename pattern
                safe_filename = (
                    "".join(c for c in noun.noun if c.isalnum() or c in (" ", "-", "_"))
                    .rstrip()
                    .replace(" ", "_")
                    .lower()
                )
                expected_image_path = Path("data/images") / f"{safe_filename}.jpg"
                if expected_image_path.exists():
                    image_file = self._media_manager.add_media_file(
                        str(expected_image_path)
                    )
                    if image_file:
                        filename = image_file.reference
                        image_html = f'<img src="{filename}">'
                        image_found = True

            if not image_found and generate_media and self._media_service:
                # Generate image only if no existing image found
                image_file = self._media_manager.generate_and_add_image(
                    noun.noun,
                    search_query=noun.english,
                    example_sentence=noun.example,
                )
                if image_file:
                    filename = image_file.reference
                    image_html = f'<img src="{filename}">'

            # Prepare fields for the card (matching noun note type field order)
            fields = [
                noun.noun,
                noun.article,
                noun.english,
                noun.plural,
                noun.example,
                noun.related,
                image_html,
                audio_ref,
                example_audio_ref,
            ]

            # Add note to deck
            self._deck_manager.add_note(note_type_id, fields, ["noun"])
            cards_created += 1

        self.reset_to_main_deck()
        logger.info(f"Generated {cards_created} noun cards")
        return cards_created

    def generate_adjective_cards(self, generate_media: bool = True) -> int:
        """Generate Anki cards for loaded adjectives.

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

        # Get or create adjective note type
        adjective_note_type = self._template_service.get_adjective_note_type()
        note_type_id = self._deck_manager.create_note_type(adjective_note_type)
        print(
            f"DEBUG: Using adjective note type ID: {note_type_id} "
            f"for {adjective_note_type.name}"
        )

        cards_created = 0

        for adjective in self._loaded_adjectives:
            # Use existing media paths from CSV or generate new media
            audio_ref = ""
            image_html = ""
            example_audio_ref = ""

            # Check for existing word audio
            if adjective.word_audio and Path(adjective.word_audio).exists():
                audio_file = self._media_manager.add_media_file(adjective.word_audio)
                if audio_file:
                    audio_ref = audio_file.reference
            elif generate_media and self._media_service:
                # Generate audio for combined adjective forms only if no existing audio
                audio_text = self._german_service.get_combined_adjective_audio_text(
                    adjective
                )
                audio_file = self._media_manager.generate_and_add_audio(audio_text)
                if audio_file:
                    audio_ref = audio_file.reference

            # Check for existing example audio
            if adjective.example_audio and Path(adjective.example_audio).exists():
                example_audio_file = self._media_manager.add_media_file(
                    adjective.example_audio
                )
                if example_audio_file:
                    example_audio_ref = example_audio_file.reference
            elif generate_media and self._media_service:
                # Generate example sentence audio if no existing audio
                example_audio_file = self._media_manager.generate_and_add_audio(
                    adjective.example
                )
                if example_audio_file:
                    example_audio_ref = example_audio_file.reference

            # Check for existing image
            if adjective.image_path and Path(adjective.image_path).exists():
                image_file = self._media_manager.add_media_file(adjective.image_path)
                if image_file:
                    filename = image_file.reference
                    image_html = f'<img src="{filename}">'
            elif generate_media and self._media_service:
                # Generate image only if no existing image
                image_file = self._media_manager.generate_and_add_image(
                    adjective.word,
                    search_query=adjective.english,
                    example_sentence=adjective.example,
                )
                if image_file:
                    filename = image_file.reference
                    image_html = f'<img src="{filename}">'

            # Prepare fields for the card
            fields = [
                adjective.word,
                adjective.english,
                adjective.example,
                adjective.comparative,
                adjective.superlative,
                image_html,
                audio_ref,
                example_audio_ref,
            ]

            # Add note to deck
            self._deck_manager.add_note(note_type_id, fields, ["adjective"])
            cards_created += 1

        self.reset_to_main_deck()
        logger.info(f"Generated {cards_created} adjective cards")
        return cards_created

    def generate_adverb_cards(self, generate_media: bool = True) -> int:
        """Generate Anki cards for loaded adverbs.

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

        # Get or create adverb note type
        adverb_note_type = self._template_service.get_adverb_note_type()
        note_type_id = self._deck_manager.create_note_type(adverb_note_type)
        print(
            f"DEBUG: Using adverb note type ID: {note_type_id} "
            f"for {adverb_note_type.name}"
        )

        cards_created = 0

        for adverb in self._loaded_adverbs:
            # Use existing media paths from CSV or generate new media
            audio_ref = ""
            image_html = ""
            example_audio_ref = ""

            # Check for existing word audio
            if adverb.word_audio and Path(adverb.word_audio).exists():
                audio_file = self._media_manager.add_media_file(adverb.word_audio)
                if audio_file:
                    audio_ref = audio_file.reference
            elif generate_media and self._media_service:
                # Generate audio for adverb only if no existing audio
                audio_file = self._media_manager.generate_and_add_audio(adverb.word)
                if audio_file:
                    audio_ref = audio_file.reference

            # Check for existing example audio
            if adverb.example_audio and Path(adverb.example_audio).exists():
                example_audio_file = self._media_manager.add_media_file(
                    adverb.example_audio
                )
                if example_audio_file:
                    example_audio_ref = example_audio_file.reference
            elif generate_media and self._media_service:
                # Generate example sentence audio if no existing audio
                example_audio_file = self._media_manager.generate_and_add_audio(
                    adverb.example
                )
                if example_audio_file:
                    example_audio_ref = example_audio_file.reference

            # Check for existing image - first check CSV path,
            # then check expected filename
            image_found = False
            if adverb.image_path and Path(adverb.image_path).exists():
                image_file = self._media_manager.add_media_file(adverb.image_path)
                if image_file:
                    filename = image_file.reference
                    image_html = f'<img src="{filename}">'
                    image_found = True
            else:
                # Check for existing image by expected filename pattern
                safe_filename = (
                    "".join(
                        c for c in adverb.word if c.isalnum() or c in (" ", "-", "_")
                    )
                    .rstrip()
                    .replace(" ", "_")
                    .lower()
                )
                expected_image_path = Path("data/images") / f"{safe_filename}.jpg"
                if expected_image_path.exists():
                    image_file = self._media_manager.add_media_file(
                        str(expected_image_path)
                    )
                    if image_file:
                        filename = image_file.reference
                        image_html = f'<img src="{filename}">'
                        image_found = True

            if not image_found and generate_media and self._media_service:
                # Generate image only if no existing image found
                image_file = self._media_manager.generate_and_add_image(
                    adverb.word,
                    search_query=adverb.english,
                    example_sentence=adverb.example,
                )
                if image_file:
                    filename = image_file.reference
                    image_html = f'<img src="{filename}">'

            # Prepare fields for the card
            fields = [
                adverb.word,
                adverb.english,
                adverb.type.value,
                adverb.example,
                image_html,
                audio_ref,
                example_audio_ref,
            ]

            # Add note to deck
            self._deck_manager.add_note(note_type_id, fields, ["adverb"])
            cards_created += 1

        self.reset_to_main_deck()
        logger.info(f"Generated {cards_created} adverb cards")
        return cards_created

    def generate_negation_cards(self, generate_media: bool = True) -> int:
        """Generate Anki cards for loaded negations.

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

        # Get or create negation note type
        negation_note_type = self._template_service.get_negation_note_type()
        note_type_id = self._deck_manager.create_note_type(negation_note_type)

        cards_created = 0

        for negation in self._loaded_negations:
            # Use existing media paths from CSV or generate new media
            audio_ref = ""
            image_html = ""
            example_audio_ref = ""

            # Check for existing word audio
            if negation.word_audio and Path(negation.word_audio).exists():
                audio_file = self._media_manager.add_media_file(negation.word_audio)
                if audio_file:
                    audio_ref = audio_file.reference
            elif generate_media and self._media_service:
                # Generate audio for negation only if no existing audio
                audio_file = self._media_manager.generate_and_add_audio(negation.word)
                if audio_file:
                    audio_ref = audio_file.reference

            # Check for existing example audio
            if negation.example_audio and Path(negation.example_audio).exists():
                example_audio_file = self._media_manager.add_media_file(
                    negation.example_audio
                )
                if example_audio_file:
                    example_audio_ref = example_audio_file.reference
            elif generate_media and self._media_service:
                # Generate example sentence audio if no existing audio
                example_audio_file = self._media_manager.generate_and_add_audio(
                    negation.example
                )
                if example_audio_file:
                    example_audio_ref = example_audio_file.reference

            # Check for existing image - first check CSV path,
            # then check expected filename
            image_found = False
            if negation.image_path and Path(negation.image_path).exists():
                image_file = self._media_manager.add_media_file(negation.image_path)
                if image_file:
                    filename = image_file.reference
                    image_html = f'<img src="{filename}">'
                    image_found = True
            else:
                # Check for existing image by expected filename pattern
                safe_filename = (
                    "".join(
                        c for c in negation.word if c.isalnum() or c in (" ", "-", "_")
                    )
                    .rstrip()
                    .replace(" ", "_")
                    .lower()
                )
                expected_image_path = Path("data/images") / f"{safe_filename}.jpg"
                if expected_image_path.exists():
                    image_file = self._media_manager.add_media_file(
                        str(expected_image_path)
                    )
                    if image_file:
                        filename = image_file.reference
                        image_html = f'<img src="{filename}">'
                        image_found = True

            if not image_found and generate_media and self._media_service:
                # Generate image only if no existing image found
                image_file = self._media_manager.generate_and_add_image(
                    negation.word,
                    search_query=negation.english,
                    example_sentence=negation.example,
                )
                if image_file:
                    filename = image_file.reference
                    image_html = f'<img src="{filename}">'

            # Prepare fields for the card
            fields = [
                negation.word,
                negation.english,
                negation.type.value,
                negation.example,
                image_html,
                audio_ref,
                example_audio_ref,
            ]

            # Add note to deck
            self._deck_manager.add_note(note_type_id, fields, ["negation"])
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

    def clear_media_cache(self) -> None:
        """Clear media generation cache."""
        if self._media_manager:
            self._media_manager.clear_cache()
            logger.info("Cleared media cache")

    # Context Manager Support

    def __enter__(self) -> "GermanDeckBuilder":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit with cleanup."""
        # Cleanup is handled by individual services
        pass
