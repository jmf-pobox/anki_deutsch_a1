"""High-level orchestrator for Anki deck generation.

The DeckBuilder provides a comprehensive, easy-to-use interface for creating
language learning Anki decks. It orchestrates all services, managers, and
backends while maintaining clean separation of concerns and following dependency
injection principles.
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar

from langlearn.core.backends.anki_backend import AnkiBackend
from langlearn.core.services import get_anthropic_service
from langlearn.core.services.audio_service import AudioService
from langlearn.core.services.image_service import PexelsService
from langlearn.core.services.media_enricher import StandardMediaEnricher
from langlearn.core.services.media_file_registrar import MediaFileRegistrar
from langlearn.core.services.media_service import MediaGenerationConfig, MediaService
from langlearn.core.services.template_service import TemplateService
from langlearn.languages.registry import LanguageRegistry
from langlearn.managers.deck_manager import DeckManager
from langlearn.managers.media_manager import MediaManager

if TYPE_CHECKING:
    from langlearn.core.records import BaseRecord

logger = logging.getLogger(__name__)


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
        builder.load_nouns_from_csv("languages/nouns.csv")
        builder.load_adjectives_from_csv("languages/adjectives.csv")

        # Generate with media
        builder.generate_all_media()

        # Export deck
        builder.export_deck("output/german_a1.apkg")
        ```
    """

    def __init__(
        self,
        deck_name: str,
        language: str = "german",
        deck_type: str = "default",
        audio_service: AudioService | None = None,
        pexels_service: PexelsService | None = None,
    ) -> None:
        """Initialize the deck builder.

        Args:
            deck_name: Name of the Anki deck to create
            language: Language for the deck (e.g., "german", "russian")
            deck_type: Deck type within the language (e.g., "default", "business")
            audio_service: Optional AudioService for dependency injection
            pexels_service: Optional PexelsService for dependency injection
        """
        self.deck_name = deck_name
        self.language = language
        self.deck_type = deck_type

        # Get language implementation via LanguageRegistry
        self._language_impl = LanguageRegistry.get(language)

        # Initialize language-specific services via LanguageRegistry
        record_mapper_class = self._language_impl.get_record_mapper()
        self._record_mapper = record_mapper_class()

        # Initialize template service with language-specific resolver
        template_dir = self._language_impl.get_template_directory()
        template_resolver = self._language_impl.get_template_filename
        self._template_service = TemplateService(template_dir, template_resolver)

        # Initialize CardBuilder service via LanguageRegistry
        card_builder_class = self._language_impl.get_card_builder()
        self._card_builder = card_builder_class(template_service=self._template_service)

        # Initialize ArticleApplicationService via language implementation
        grammar_module = self._language_impl.get_grammar_service()
        self._article_service = grammar_module.ArticleApplicationService(
            self._card_builder
        )

        # Initialize StandardMediaEnricher (type annotation)
        self._media_enricher: Any = None  # Will be properly initialized later

        # Initialize dependencies for media service with language/deck specific paths
        project_root = Path(__file__).parent.parent.parent  # Go up to project root
        language_deck_data_dir = project_root / "languages" / language / deck_type

        # Use provided services or create defaults with language/deck specific paths
        # Get TTS configuration from language implementation
        if audio_service is not None:
            actual_audio_service = audio_service
        else:
            tts_config = self._language_impl.get_tts_config()
            actual_audio_service = AudioService(
                output_dir=str(language_deck_data_dir / "audio"),
                voice_id=tts_config.voice_id,
                language_code=tts_config.language_code,
                engine=tts_config.engine,
            )
        actual_pexels_service = pexels_service or PexelsService()
        media_config = MediaGenerationConfig(
            audio_dir=str(language_deck_data_dir / "audio"),
            images_dir=str(language_deck_data_dir / "images"),
        )

        # Create media service
        self._media_service = MediaService(
            audio_service=actual_audio_service,
            pexels_service=actual_pexels_service,
            config=media_config,
            project_root=project_root,
        )

        # Initialize backend
        self._backend = AnkiBackend(
            deck_name=deck_name,
            media_service=self._media_service,
            language=self._language_impl,
        )

        # Initialize managers with dependency injection
        self._deck_manager = DeckManager(self._backend)
        self._media_manager = MediaManager(self._backend, self._media_service)

        # Initialize MediaFileRegistrar with language/deck paths
        self._media_file_registrar = MediaFileRegistrar(
            audio_base_path=language_deck_data_dir / "audio",
            image_base_path=language_deck_data_dir / "images",
        )

        # Initialize StandardMediaEnricher
        if self._media_service:
            # Get anthropic service for AI-powered search term generation
            anthropic_service = get_anthropic_service()

            self._media_enricher = StandardMediaEnricher(
                audio_service=actual_audio_service,
                pexels_service=actual_pexels_service,
                anthropic_service=anthropic_service,
                audio_base_path=language_deck_data_dir / "audio",
                image_base_path=language_deck_data_dir / "images",
            )
        else:
            self._media_enricher = None

        # Records from CSV data
        self._loaded_records: list[BaseRecord] = []

        logger.info(f"Initialized DeckBuilder for {language} language")

    # Data Loading Methods

    def load_data_from_directory(self, data_dir: str | Path) -> None:
        """Load all available data files from a directory.

        Args:
            data_dir: Directory containing CSV data files
        """
        data_dir = Path(data_dir)
        logger.info(f"Loading data from directory: {data_dir}")

        # Map CSV files directly to record types
        csv_to_record_type = {
            "nouns.csv": "noun",
            "adjectives.csv": "adjective",
            "adverbs.csv": "adverb",
            "negations.csv": "negation",
            "prepositions.csv": "preposition",
            "phrases.csv": "phrase",
            "articles_unified.csv": "unified_article",
            "verbs.csv": "verb",
            "verbs_unified.csv": "verb_conjugation",
        }

        for filename, record_type in csv_to_record_type.items():
            file_path = data_dir / filename
            if file_path.exists():
                logger.info(f"Loading {record_type} data from {file_path}")
                records = self._record_mapper.load_records_from_csv(file_path)
                self._loaded_records.extend(records)
                logger.info(f"Loaded {len(records)} {record_type} records")
            else:
                logger.debug(f"Data file not found: {file_path}")

        total_records = len(self._loaded_records)
        logger.info(f"Total records loaded: {total_records}")

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

    def generate_all_cards(self, generate_media: bool = True) -> dict[str, int]:
        """Generate all cards from loaded records.

        Args:
            generate_media: Whether to generate audio/image media

        Returns:
            Dictionary with counts of cards generated by type
        """
        if not self._loaded_records:
            logger.warning("No records loaded - call load_data_from_directory() first")
            return {}

        logger.info(f"Generating cards for {len(self._loaded_records)} records")

        # **PIPELINE FLOW**: Records → MediaEnricher → CardBuilder → AnkiBackend

        # Step 1: Group records by type for processing
        records_by_type: dict[str, list[BaseRecord]] = {}
        for record in self._loaded_records:
            # Use the record's get_record_type() method for consistent naming
            record_type = record.get_record_type().value

            if record_type not in records_by_type:
                records_by_type[record_type] = []
            records_by_type[record_type].append(record)

        results: dict[str, int] = {}

        for record_type, records in records_by_type.items():
            logger.info(f"Processing {len(records)} {record_type} records")

            # Step 1.5: Create subdeck for this word type
            # Use the record class's get_subdeck_name() method for consistent naming
            if records:  # Use the first record to get the subdeck name
                subdeck_name = records[0].__class__.get_subdeck_name()
            else:
                # Fallback if no records (shouldn't happen)
                subdeck_name = record_type.replace("_", " ").title() + "s"
            self.create_subdeck(subdeck_name)
            logger.info(f"Created subdeck: {subdeck_name}")

            # Step 2: Media enrichment (if enabled) - batch processing
            enriched_data_list: list[dict[str, Any]] = []
            if generate_media and self._media_enricher:
                logger.info(f"Generating media for {record_type} records...")

                # Convert Records to Domain Models for media enrichment
                # Use language-specific RecordToModelFactory via card processor
                card_processor = self._language_impl.get_card_processor()
                record_to_model_factory = card_processor.get_record_to_model_factory()

                record_dicts = []
                domain_models = []
                skipped_indices = []

                for i, rec in enumerate(records):
                    try:
                        domain_model = record_to_model_factory.create_domain_model(rec)
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

            # Step 3: Card building via language-specific card processor
            logger.info(f"Building cards for {record_type} records...")

            # Delegate all language-specific card building logic to card processor
            card_processor = self._language_impl.get_card_processor()
            cards = card_processor.process_records_for_cards(
                records, record_type, enriched_data_list, self._card_builder
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
            # Use the record class's get_result_key() method for consistent naming
            if records:  # Use the first record to get the result key
                result_key = records[0].__class__.get_result_key()
            else:
                # Fallback if no records (shouldn't happen)
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
        logger.info(f"🎉 Generated {total} total cards: {results}")

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
        # Count loaded records by type
        clean_pipeline_stats = {}
        for record in self._loaded_records:
            record_type = record.__class__.__name__.replace("Record", "").lower()
            if record_type not in clean_pipeline_stats:
                clean_pipeline_stats[record_type] = 0
            clean_pipeline_stats[record_type] += 1

        stats = {
            "deck_info": {
                "name": self.deck_name,
                "media_enabled": True,
            },
            "loaded_data": {
                # Loaded data
                **clean_pipeline_stats,
                # Total loaded records
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
        # Clear loaded data
        self._loaded_records.clear()
        logger.info("Cleared all loaded data")

    # Context Manager Support

    def __enter__(self) -> "DeckBuilder":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit with cleanup."""
        # Cleanup is handled by individual services
        pass
