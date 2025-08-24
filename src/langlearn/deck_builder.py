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
from .models.records import BaseRecord
from .protocols import AudioServiceProtocol, MediaServiceProtocol, PexelsServiceProtocol
from .services.article_application_service import ArticleApplicationService
from .services.card_builder import CardBuilder
from .services.csv_service import CSVService
from .services.media_file_registrar import MediaFileRegistrar
from .services.media_service import MediaService
from .services.record_mapper import RecordMapper
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
        audio_service: AudioServiceProtocol | None = None,
        pexels_service: PexelsServiceProtocol | None = None,
        media_service: MediaServiceProtocol | None = None,
    ) -> None:
        """Initialize the German deck builder.

        Args:
            deck_name: Name of the Anki deck to create
            backend_type: Backend to use ("anki")
            enable_media_generation: Whether to enable media generation services
            audio_service: Optional AudioServiceProtocol for dependency injection
            pexels_service: Optional PexelsServiceProtocol for dependency injection
            media_service: Optional MediaServiceProtocol for dependency injection
        """
        self.deck_name = deck_name
        self.backend_type = backend_type
        self.enable_media_generation = enable_media_generation

        # Initialize services
        self._csv_service = CSVService()

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

        # Initialize media service with dependency injection
        self._media_service: MediaServiceProtocol | None = None
        if media_service is not None:
            # Use provided media service (for dependency injection)
            self._media_service = media_service
        elif enable_media_generation:
            from .services.audio import AudioService
            from .services.media_service import MediaGenerationConfig
            from .services.pexels_service import PexelsService

            # Initialize dependencies for media service with dependency injection
            project_root = Path(__file__).parent.parent.parent  # Go up to project root

            # Use provided services or create defaults
            actual_audio_service = audio_service or AudioService(
                output_dir=str(project_root / "data" / "audio")
            )
            actual_pexels_service = pexels_service or PexelsService()
            media_config = MediaGenerationConfig()

            # Cast to concrete types since MediaService requires concrete types
            from typing import cast

            self._media_service = cast(
                "MediaServiceProtocol",
                MediaService(
                    audio_service=cast("AudioService", actual_audio_service),
                    pexels_service=cast("PexelsService", actual_pexels_service),
                    config=media_config,
                    project_root=project_root,
                ),
            )

        # Initialize backend
        self._backend = self._create_backend(deck_name, backend_type)

        # Initialize managers with dependency injection
        self._deck_manager = DeckManager(self._backend)
        # Cast MediaServiceProtocol to MediaService for MediaManager
        media_service_for_manager = (
            cast("MediaService", self._media_service) if self._media_service else None
        )
        self._media_manager = MediaManager(self._backend, media_service_for_manager)

        # Initialize MediaFileRegistrar for Clean Pipeline
        self._media_file_registrar = MediaFileRegistrar()

        # Initialize StandardMediaEnricher for Clean Pipeline
        if self._media_service:
            from .services import get_translation_service
            from .services.media_enricher import StandardMediaEnricher

            # Get translation service for improved image search
            translation_service = get_translation_service()

            self._media_enricher = StandardMediaEnricher(
                media_service=self._media_service,
                translation_service=translation_service,
            )
        else:
            self._media_enricher = None

        # Initialize card generator factory (legacy compatibility)
        self._card_factory = CardGeneratorFactory(
            backend=self._backend,
            template_service=self._template_service,
            media_manager=self._media_manager,
        )

        # Track loaded data - DUAL STORAGE for compatibility
        # Legacy domain models (for backward compatibility)
        self._loaded_nouns: list[Noun] = []
        self._loaded_adjectives: list[Adjective] = []
        self._loaded_adverbs: list[Adverb] = []
        self._loaded_negations: list[Negation] = []

        # Clean Pipeline records (new architecture)
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
            # Unified Article system for German case learning
            "articles_unified.csv": "unified_article",
            # Re-enabled basic verb cards (Issue #26) - processed first
            "verbs.csv": "verb",
            # Modern multi-tense verb system - same subdeck as basic verbs
            "verbs_unified.csv": "verb_conjugation",  # Multi-tense verb system
            # "regular_verbs.csv": "verb",
            # "irregular_verbs.csv": "verb",
            # "separable_verbs.csv": "verb",
        }

        for filename, record_type in csv_to_record_type.items():
            file_path = data_dir / filename
            if file_path.exists():
                logger.info(f"Loading {record_type} data from {file_path}")
                # Use Clean Pipeline: CSV → Records
                records = self._record_mapper.load_records_from_csv(file_path)
                self._loaded_records.extend(records)
                logger.info(f"Loaded {len(records)} {record_type} records")

                # Legacy compatibility: load into old domain models too
                self._load_legacy_models_from_records(records, record_type)
            else:
                logger.debug(f"Data file not found: {file_path}")

        total_records = len(self._loaded_records)
        logger.info(f"Total records loaded via Clean Pipeline: {total_records}")

    def _load_legacy_models_from_records(
        self, records: list[BaseRecord], record_type: str
    ) -> None:
        """Load legacy domain models from records for backward compatibility.

        Args:
            records: Records to convert to legacy models
            record_type: Type of record being converted
        """
        from .models.records import (
            AdjectiveRecord,
            AdverbRecord,
            NegationRecord,
            NounRecord,
        )

        # Convert records back to legacy domain models for compatibility
        for record in records:
            if record_type == "noun" and isinstance(record, NounRecord):
                noun = Noun(
                    noun=record.noun,
                    article=record.article,
                    english=record.english,
                    plural=record.plural,
                    example=record.example,
                    related=record.related,
                )
                self._loaded_nouns.append(noun)
            elif record_type == "adjective" and isinstance(record, AdjectiveRecord):
                adjective = Adjective(
                    word=record.word,
                    english=record.english,
                    example=record.example,
                    comparative=record.comparative,
                    superlative=record.superlative,
                )
                self._loaded_adjectives.append(adjective)
            elif record_type == "adverb" and isinstance(record, AdverbRecord):
                from .models.adverb import AdverbType

                adverb_type = (
                    AdverbType(record.type) if record.type else AdverbType.TIME
                )
                adverb = Adverb(
                    word=record.word,
                    english=record.english,
                    type=adverb_type,
                    example=record.example,
                )
                self._loaded_adverbs.append(adverb)
            elif record_type == "negation" and isinstance(record, NegationRecord):
                from .models.negation import NegationType

                negation_type = (
                    NegationType(record.type) if record.type else NegationType.GENERAL
                )
                negation = Negation(
                    word=record.word,
                    english=record.english,
                    type=negation_type,
                    example=record.example,
                )
                self._loaded_negations.append(negation)

    def _record_to_domain_model(self, rec: BaseRecord) -> Any:
        """Convert a record into a legacy domain model where available.

        Provides domain behavior (e.g., get_image_search_strategy,
        get_combined_audio_text) expected by StandardMediaEnricher.
        For unsupported types, returns the record itself.
        """
        try:
            from .models.records import (
                AdjectiveRecord,
                AdverbRecord,
                NegationRecord,
                NounRecord,
                VerbRecord,
            )

            if isinstance(rec, NounRecord):
                return Noun(
                    noun=rec.noun,
                    article=rec.article,
                    english=rec.english,
                    plural=rec.plural,
                    example=rec.example,
                    related=rec.related,
                )
            if isinstance(rec, AdjectiveRecord):
                return Adjective(
                    word=rec.word,
                    english=rec.english,
                    example=rec.example,
                    comparative=rec.comparative,
                    superlative=rec.superlative,
                )
            if isinstance(rec, AdverbRecord):
                from .models.adverb import Adverb as AdvModel
                from .models.adverb import AdverbType

                adv_type = AdverbType(rec.type) if rec.type else AdverbType.TIME
                return AdvModel(
                    word=rec.word,
                    english=rec.english,
                    type=adv_type,
                    example=rec.example,
                )
            if isinstance(rec, NegationRecord):
                from .models.negation import Negation as NegModel
                from .models.negation import NegationType

                neg_type = NegationType(rec.type) if rec.type else NegationType.GENERAL
                return NegModel(
                    word=rec.word,
                    english=rec.english,
                    type=neg_type,
                    example=rec.example,
                )
            if isinstance(rec, VerbRecord):
                from .models.verb import Verb

                return Verb(
                    verb=rec.verb,
                    english=rec.english,
                    present_ich=rec.present_ich,
                    present_du=rec.present_du,
                    present_er=rec.present_er,
                    perfect=rec.perfect,
                    example=rec.example,
                )
        except Exception as e:
            # If anything goes wrong, just fall back to the record itself
            logger.debug(
                f"Domain model conversion failed for {type(rec).__name__}: {e}"
            )

        # For other record types (verb, phrase, preposition, etc.),
        # StandardMediaEnricher should be extended to operate on record dicts directly.
        return rec

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
        """Generate all cards using Clean Pipeline.

        Args:
            generate_media: Whether to generate audio/image media

        Returns:
            Dictionary with counts of cards generated by type
        """
        if not self._loaded_records:
            logger.warning("No records loaded - using legacy fallback")
            return self._generate_all_cards_legacy(generate_media)

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

                # Collect all records and domain models for batch enrichment
                record_dicts = []
                domain_models = []
                for rec in records:
                    try:
                        domain_model = self._record_to_domain_model(rec)
                        record_dicts.append(rec.to_dict())
                        domain_models.append(domain_model)
                    except Exception as e:
                        logger.warning(f"Failed to map record to domain model: {e}")
                        record_dicts.append(rec.to_dict())
                        domain_models.append(None)

                # Batch enrich all records
                try:
                    enriched_list = self._media_enricher.enrich_records(
                        record_dicts, domain_models
                    )
                except Exception as e:
                    logger.error(f"Batch enrichment failed for {record_type}: {e}")
                    enriched_list = [{} for _ in records]

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
                }
                for enriched in enriched_list:
                    if isinstance(enriched, dict):
                        enriched_data_list.append(
                            {k: v for k, v in enriched.items() if k in media_keys and v}
                        )
                    else:
                        enriched_data_list.append({})
            else:
                # No media generation - create empty enrichment data
                enriched_data_list = [{}] * len(records)

            # Step 3: Card building via CardBuilder service
            logger.info(f"Building cards for {record_type} records...")

            # Special handling for verb conjugation records - use multi-card generation
            if record_type == "verbconjugation":
                from .models.records import VerbConjugationRecord

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

            # Special handling for unified article records with noun integration
            elif record_type == "unified_article":
                from .models.records import (
                    ArticleRecord,
                    IndefiniteArticleRecord,
                    NegativeArticleRecord,
                    NounRecord,
                    UnifiedArticleRecord,
                )

                # Filter unified article records
                unified_article_records = [
                    r for r in records if isinstance(r, UnifiedArticleRecord)
                ]
                logger.info(
                    f"Processing unified article system with "
                    f"{len(unified_article_records)} article pattern records"
                )

                # Generate article pattern cards (same as before)
                from typing import cast

                article_records_for_pattern = cast(
                    "list[ArticleRecord | IndefiniteArticleRecord | "
                    "NegativeArticleRecord | UnifiedArticleRecord]",
                    unified_article_records,
                )
                pattern_cards = self._card_builder.build_article_pattern_cards(
                    article_records_for_pattern, enriched_data_list
                )

                # Get noun records for noun-article practice cards
                noun_records = [
                    r
                    for r_type, record_list in records_by_type.items()
                    if r_type == "noun"
                    for r in record_list
                    if isinstance(r, NounRecord)
                ]

                if noun_records:
                    logger.info(
                        f"Skipping noun-article practice cards for "
                        f"{len(noun_records)} noun records "
                        f"(temporarily disabled for cloze testing)"
                    )
                    # TEMPORARY: Disable noun-article cards to focus on testing
                    # cloze deletion system
                    # TODO: Update ArticleApplicationService to use cloze deletion
                    # instead of templates
                    # noun_enriched_data: list[dict[str, Any]] = [{}] * len(
                    #     noun_records
                    # )
                    # noun_article_cards = (
                    #     self._article_service.generate_noun_article_cards(
                    #         noun_records, noun_enriched_data
                    #     )
                    # )
                    # For now, only use pattern cards (cloze deletion)
                    cards = pattern_cards
                else:
                    logger.info("No noun records found for noun-article integration")
                    cards = pattern_cards
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

    def _generate_all_cards_legacy(self, generate_media: bool = True) -> dict[str, int]:
        """Legacy fallback for card generation using old architecture.

        Args:
            generate_media: Whether to generate audio/image media

        Returns:
            Dictionary with counts of cards generated by type
        """
        logger.info("Using legacy card generation architecture")
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
        logger.info(f"Legacy architecture generated {total} total cards: {results}")

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
                "media_enabled": self.enable_media_generation,
            },
            "loaded_data": {
                # Legacy data (backward compatibility)
                "nouns": len(self._loaded_nouns),
                "adjectives": len(self._loaded_adjectives),
                "adverbs": len(self._loaded_adverbs),
                "negations": len(self._loaded_negations),
                # Clean Pipeline data
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
        # Clear legacy data
        self._loaded_nouns.clear()
        self._loaded_adjectives.clear()
        self._loaded_adverbs.clear()
        self._loaded_negations.clear()
        # Clear Clean Pipeline data
        self._loaded_records.clear()
        logger.info("Cleared all loaded data (legacy + Clean Pipeline records)")

    # Context Manager Support

    def __enter__(self) -> "DeckBuilder":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit with cleanup."""
        # Cleanup is handled by individual services
        pass
