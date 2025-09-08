"""High-level orchestrator for Anki deck generation.

The DeckBuilder provides a comprehensive, easy-to-use interface for creating
language learning Anki decks. It orchestrates all services, managers, and
backends while maintaining clean separation of concerns and following dependency
injection principles.
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar

from .backends.anki_backend import AnkiBackend
from .backends.base import DeckBackend

# CardGeneratorFactory import removed - using Clean Pipeline CardBuilder
from .managers.deck_manager import DeckManager
from .managers.media_manager import MediaManager

# Legacy domain model imports removed - using Clean Pipeline Records
# Removed unused protocol imports - services are used directly
from .services.article_application_service import ArticleApplicationService
from .services.audio import AudioService
from .services.card_builder import CardBuilder
from .services.media_file_registrar import MediaFileRegistrar
from .services.media_service import MediaGenerationConfig, MediaService
from .services.pexels_service import PexelsService
from .services.record_mapper import RecordMapper
from .services.service_container import (
    get_translation_service as _get_translation_service,
)
from .services.template_service import TemplateService

if TYPE_CHECKING:
    from langlearn.languages.german.records.records import BaseRecord

logger = logging.getLogger(__name__)

# Re-export factory for tests that patch DeckBuilder-level symbol
# Some tests expect to patch langlearn.deck_builder.get_translation_service
# Provide a module-level alias to satisfy those patches.
get_translation_service = _get_translation_service

T = TypeVar("T")


class DeckBuilder:
    """High-level orchestrator for Anki deck generation.

    This class provides the main interface for creating language learning
    Anki decks. It orchestrates all necessary services, manages dependencies,
    and provides a clean API for deck generation workflows.

    The builder uses the official Anki library backend,
    comprehensive media generation, subdeck organization, and follows clean
    architecture principles throughout.

    Example:
        ```python
        # Basic usage
        builder = DeckBuilder("A1 German Vocabulary")

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
        audio_service: AudioService | None = None,
        pexels_service: PexelsService | None = None,
    ) -> None:
        """Initialize the deck builder.

        Args:
            deck_name: Name of the Anki deck to create
            backend_type: Backend to use ("anki")
            audio_service: Optional AudioService for dependency injection
            pexels_service: Optional PexelsService for dependency injection
        """
        self.deck_name = deck_name
        self.backend_type = backend_type

        # Initialize Clean Pipeline services
        self._record_mapper = RecordMapper()

        # Initialize template service with templates directory
        template_dir = Path(__file__).parent / "templates"
        self._template_service = TemplateService(template_dir)

        # Initialize CardBuilder service for Clean Pipeline
        self._card_builder = CardBuilder(template_service=self._template_service)

        # Initialize ArticleApplicationService for unified article system
        self._article_service = ArticleApplicationService(self._card_builder)

        # Initialize StandardMediaEnricher (type annotation)
        self._media_enricher: Any = None  # Will be properly initialized later

        # Initialize dependencies for media service
        project_root = Path(__file__).parent.parent.parent  # Go up to project root

        # Use provided services or create defaults
        actual_audio_service = audio_service or AudioService(
            output_dir=str(project_root / "data" / "audio")
        )
        actual_pexels_service = pexels_service or PexelsService()
        media_config = MediaGenerationConfig()

        # Always create media service - no optional media
        self._media_service = MediaService(
            audio_service=actual_audio_service,
            pexels_service=actual_pexels_service,
            config=media_config,
            project_root=project_root,
        )

        # Initialize backend
        self._backend = self._create_backend(deck_name, backend_type)

        # Initialize managers with dependency injection
        self._deck_manager = DeckManager(self._backend)
        self._media_manager = MediaManager(self._backend, self._media_service)

        # Initialize MediaFileRegistrar for Clean Pipeline
        self._media_file_registrar = MediaFileRegistrar()

        # Initialize StandardMediaEnricher for Clean Pipeline
        if self._media_service:
            from .services import get_anthropic_service
            from .services.media_enricher import StandardMediaEnricher

            # Translation service not needed for domain-model MediaEnricher
            # Get anthropic service for AI-powered search term generation
            anthropic_service = get_anthropic_service()
            if anthropic_service is None:
                raise ValueError("AnthropicService is required for media enrichment")

            self._media_enricher = StandardMediaEnricher(
                audio_service=actual_audio_service,
                pexels_service=actual_pexels_service,
                anthropic_service=anthropic_service,
                audio_base_path=project_root / "data" / "audio",
                image_base_path=project_root / "data" / "images",
            )
        else:
            self._media_enricher = None

        # Card generator factory removed - using CardBuilder service in Clean Pipeline

        # Clean Pipeline records (unified architecture)
        self._loaded_records: list[BaseRecord] = []

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

    # Data Loading Methods (Clean Pipeline only)

    def load_data_from_directory(self, data_dir: str | Path) -> None:
        """Load all available data files from a directory using Clean Pipeline.

        Args:
            data_dir: Directory containing CSV data files
        """
        data_dir = Path(data_dir)
        logger.info(f"Loading data from directory: {data_dir}")

        # Clean Pipeline approach: Map CSV files directly to record types
        csv_to_record_type = {
            "nouns.csv": "noun",
            "adjectives.csv": "adjective",
            "adverbs.csv": "adverb",
            "negations.csv": "negation",
            "prepositions.csv": "preposition",
            "phrases.csv": "phrase",
            # Unified Article system for case learning
            "articles_unified.csv": "unified_article",
            # Re-enabled basic verb cards (Issue #26) - processed first
            "verbs.csv": "verb",
            # Modern multi-tense verb system - same subdeck as basic verbs
            "verbs_unified.csv": "verb_conjugation",  # Multi-tense verb system
        }

        for filename, record_type in csv_to_record_type.items():
            file_path = data_dir / filename
            if file_path.exists():
                logger.info(f"Loading {record_type} data from {file_path}")
                # Use Clean Pipeline: CSV → Records
                records = self._record_mapper.load_records_from_csv(file_path)
                self._loaded_records.extend(records)
                logger.info(f"Loaded {len(records)} {record_type} records")

            # Legacy compatibility removed - using Clean Pipeline only
            else:
                logger.debug(f"Data file not found: {file_path}")

        total_records = len(self._loaded_records)
        logger.info(f"Total records loaded via Clean Pipeline: {total_records}")

    # Legacy model conversion methods removed - Clean Pipeline uses records directly

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

    # Card Generation Methods (Clean Pipeline only)

    def generate_all_cards(self, generate_media: bool = True) -> dict[str, int]:
        """Generate all cards using Clean Pipeline.

        Args:
            generate_media: Whether to generate audio/image media

        Returns:
            Dictionary with counts of cards generated by type
        """
        if not self._loaded_records:
            logger.warning("No records loaded - call load_data_from_directory() first")
            return {}

        logger.info(f"Generating cards for {len(self._loaded_records)} records")

        # **CLEAN PIPELINE FLOW**: Records → MediaEnricher → CardBuilder → AnkiBackend

        # Step 1: Group records by type for processing
        records_by_type: dict[str, list[BaseRecord]] = {}
        for record in self._loaded_records:
            record_type = record.__class__.__name__.replace("Record", "").lower()

            # Handle special naming for unified article records
            if record_type == "unifiedarticle":
                record_type = "unified_article"

            if record_type not in records_by_type:
                records_by_type[record_type] = []
            records_by_type[record_type].append(record)

        results: dict[str, int] = {}

        for record_type, records in records_by_type.items():
            logger.info(f"Processing {len(records)} {record_type} records")

            # Step 1.5: Create subdeck for this word type
            # Special case: all verb-related cards go to "Verbs" subdeck
            if record_type in ["verb", "verbconjugation", "verbimperative"]:
                subdeck_name = "Verbs"
            elif record_type == "unified_article":
                subdeck_name = "Articles"
            else:
                subdeck_name = record_type.capitalize() + (
                    "s" if not record_type.endswith("s") else ""
                )
            self.create_subdeck(subdeck_name)
            logger.info(f"Created subdeck: {subdeck_name}")

            # Step 2: Media enrichment (if enabled) - Clean Pipeline batch processing
            enriched_data_list: list[dict[str, Any]] = []
            if generate_media and self._media_enricher:
                logger.info(f"Generating media for {record_type} records...")

                # Convert Records to Domain Models for media enrichment
                from langlearn.services.record_to_model_factory import (
                    RecordToModelFactory,
                )

                record_dicts = []
                domain_models = []
                skipped_indices = []

                for i, rec in enumerate(records):
                    try:
                        domain_model = RecordToModelFactory.create_domain_model(rec)
                        record_dicts.append(rec.to_dict())
                        domain_models.append(domain_model)
                    except ValueError as e:
                        logger.warning(f"No domain model for {type(rec).__name__}: {e}")
                        logger.warning(
                            "CRITICAL: This record will have NO MEDIA generated!"
                        )
                        # Track records without domain models
                        skipped_indices.append(i)
                        continue

                # Batch enrich records that have domain models
                enriched_list = []
                if record_dicts and domain_models:
                    try:
                        enriched_list = self._media_enricher.enrich_records(
                            record_dicts, domain_models
                        )
                    except Exception as e:
                        logger.error(f"Batch enrichment failed for {record_type}: {e}")
                        enriched_list = [{} for _ in record_dicts]

                # Reconstruct enriched data for all records, including skipped ones
                all_enriched: list[dict[str, Any]] = []
                enriched_idx = 0
                for i in range(len(records)):
                    if i in skipped_indices:
                        # No domain model - use empty media data
                        all_enriched.append({})
                    else:
                        # Has domain model - use enriched media data
                        if enriched_idx < len(enriched_list):
                            all_enriched.append(enriched_list[enriched_idx])
                        else:
                            all_enriched.append({})
                        enriched_idx += 1

                enriched_list = all_enriched

                # Keep only media-related fields to merge into cards
                media_keys = {
                    "image",
                    "word_audio",
                    "example_audio",
                    "phrase_audio",
                    "example1_audio",
                    "example2_audio",
                    "du_audio",
                    "ihr_audio",
                    "sie_audio",
                    "wir_audio",
                    # Article-specific audio fields (CRITICAL FIX)
                    "pattern_audio",
                    "example_nom_audio",
                    "example_akk_audio",
                    "example_dat_audio",
                    "example_gen_audio",
                }
                for enriched in enriched_list:
                    # CRITICAL FIX: Don't filter out empty values - let
                    # CardBuilder handle them
                    # The `and v` condition was causing data loss when MediaEnricher
                    # couldn't generate media (e.g., API failures, missing files)
                    enriched_data_list.append(
                        {k: v for k, v in enriched.items() if k in media_keys}
                    )
            else:
                # No media generation - create empty enrichment data
                enriched_data_list = [{}] * len(records)

            # Step 3: Card building via CardBuilder service
            logger.info(f"Building cards for {record_type} records...")

            # Special handling for verb conjugation records - use multi-card generation
            if record_type == "verbconjugation":
                from langlearn.languages.german.records.records import (
                    VerbConjugationRecord,
                )

                # Cast records to the proper type for verb conjugation processing
                verb_records = [
                    r for r in records if isinstance(r, VerbConjugationRecord)
                ]
                logger.info(
                    f"Using verb conjugation multi-card generation for "
                    f"{len(verb_records)} records"
                )

                cards = self._card_builder.build_verb_conjugation_cards(
                    verb_records, enriched_data_list
                )

            # Special handling for unified articles (MediaEnricher + specialized cards)
            elif record_type == "unified_article":
                from langlearn.languages.german.records.records import (
                    ArticleRecord,
                    IndefiniteArticleRecord,
                    NegativeArticleRecord,
                    UnifiedArticleRecord,
                )

                # Filter unified article records (supporting all article types)
                article_records = [
                    r
                    for r in records
                    if isinstance(
                        r,
                        ArticleRecord
                        | IndefiniteArticleRecord
                        | NegativeArticleRecord
                        | UnifiedArticleRecord,
                    )
                ]

                # Use specialized article card building WITH enriched media data
                cards = self._card_builder.build_article_pattern_cards(
                    article_records, enriched_data_list
                )
            else:
                # Standard single-card generation for other record types
                cards = self._card_builder.build_cards_from_records(
                    records, enriched_data_list
                )

            # Step 4: Create note types and add cards to backend via AnkiBackend
            cards_created = 0
            created_note_types = {}  # Cache note type IDs to avoid duplicates

            for field_values, note_type in cards:
                try:
                    # Create note type if not already created
                    if note_type.name not in created_note_types:
                        note_type_id = self._backend.create_note_type(note_type)
                        created_note_types[note_type.name] = note_type_id
                        logger.debug(
                            f"Created note type: {note_type.name} -> {note_type_id}"
                        )
                    else:
                        note_type_id = created_note_types[note_type.name]

                    # Skip media processing since CardBuilder already processed fields
                    self._backend.add_note(
                        note_type_id, field_values, skip_media_processing=True
                    )

                    # Register media files referenced in this card
                    if self._media_file_registrar:
                        self._media_file_registrar.register_card_media(
                            field_values, self._backend
                        )

                    cards_created += 1
                except Exception as e:
                    logger.error(f"Failed to add {record_type} card: {e}")

            # Format result key to match expected output format
            # Special case: consolidate all verb-related cards under "verbs" key
            if record_type in ["verb", "verbconjugation", "verbimperative"]:
                result_key = "verbs"
            elif record_type == "unified_article":
                result_key = "articles"
            else:
                # (remove underscores, add 's')
                result_key = record_type.replace("_", "") + "s"

            # Accumulate cards for consolidated result keys
            if result_key in results:
                results[result_key] += cards_created
            else:
                results[result_key] = cards_created
            logger.info(f"Created {cards_created} {record_type} cards")

            # Step 5: Reset to main deck after processing this word type
            self.reset_to_main_deck()

        total = sum(results.values())
        logger.info(f"🎉 Clean Pipeline generated {total} total cards: {results}")

        return results

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
        # Count Clean Pipeline records by type
        clean_pipeline_stats = {}
        for record in self._loaded_records:
            record_type = record.__class__.__name__.replace("Record", "").lower()
            if record_type not in clean_pipeline_stats:
                clean_pipeline_stats[record_type] = 0
            clean_pipeline_stats[record_type] += 1

        stats = {
            "deck_info": {
                "name": self.deck_name,
                "backend_type": self.backend_type,
                "media_enabled": True,
            },
            "loaded_data": {
                # Clean Pipeline data (unified architecture)
                **clean_pipeline_stats,
                # Total records via Clean Pipeline
                "total_clean_pipeline_records": len(self._loaded_records),
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
        # Clear Clean Pipeline data (unified architecture)
        self._loaded_records.clear()
        logger.info("Cleared all loaded data (Clean Pipeline records)")

    # Context Manager Support

    def __enter__(self) -> "DeckBuilder":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit with cleanup."""
        # Cleanup is handled by individual services
        pass
