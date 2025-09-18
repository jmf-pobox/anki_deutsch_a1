"""Observable phase-based deck builder for Anki language learning decks."""

import logging
import logging.handlers
from collections.abc import Iterator
from pathlib import Path
from typing import Any, TypeVar

from langlearn.core.backends.anki_backend import AnkiBackend
from langlearn.core.records import BaseRecord
from langlearn.core.services import get_anthropic_service
from langlearn.core.services.audio_service import AudioService
from langlearn.core.services.image_service import PexelsService
from langlearn.core.services.media_file_registrar import MediaFileRegistrar
from langlearn.core.services.media_service import MediaGenerationConfig, MediaService
from langlearn.core.services.template_service import TemplateService
from langlearn.languages.registry import LanguageRegistry
from langlearn.managers.deck_manager import DeckManager
from langlearn.managers.media_manager import MediaManager

from .data_types import (
    BuiltCards,
    Card,
    CardPreview,
    EnrichedData,
    EnrichmentError,
    ExportResult,
    LoadedData,
    MediaFile,
    PipelineSummary,
    ValidationError,
)
from .phases import InvalidPhaseError, Phase
from .progress import EnrichmentProgress

# Set up logging
logger = logging.getLogger(__name__)

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Add file handler for deck_builder.log
file_handler = logging.handlers.RotatingFileHandler(
    log_dir / "deck_builder.log",
    maxBytes=1024 * 1024,
    backupCount=5,  # 1MB
)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)  # Ensure INFO messages are captured
logger.propagate = False  # Don't propagate to root logger (prevents console output)


T = TypeVar("T")


class DeckBuilderAPI:
    """Observable phase-based deck builder for language learning.

    This class provides a comprehensive interface for creating language learning
    Anki decks with clear phases, read access to intermediate work, and
    observable progress tracking.

    Pipeline: INITIALIZED → DATA_LOADED → MEDIA_ENRICHED → CARDS_BUILT → DECK_EXPORTED

    Example:
        ```python
        builder = DeckBuilderAPI("German A1", "german")

        # Load with inspection
        loaded = builder.load_data(data_dir)
        print(f"Loaded {loaded.total_records} records")

        # Enrich with progress
        for progress in builder.enrich_media():
            print(
                f"Enriching {progress.record_type}: "
                f"{progress.processed}/{progress.total}"
            )

        # Preview before committing
        cards = builder.build_cards(preview_only=True)
        preview = builder.preview_card(0)
        print(f"Card preview: {preview.front[:50]}...")

        # Export when satisfied
        result = builder.export_deck("output/deck.apkg")
        print(f"Exported {result.cards_exported} cards")
        ```
    """

    def __init__(
        self,
        deck_name: str,
        language: str,
        deck_type: str = "default",
        audio_service: AudioService | None = None,
        pexels_service: PexelsService | None = None,
    ):
        """Initialize the deck builder API.

        Args:
            deck_name: Name of the Anki deck to create
            language: Language for the deck (e.g., "german", "russian")
            deck_type: Deck type within the language (e.g., "default", "business")
            audio_service: Optional AudioService for dependency injection
            pexels_service: Optional PexelsService for dependency injection
        """
        self._deck_name = deck_name
        self._language = language
        self._deck_type = deck_type
        self._phase = Phase.INITIALIZED

        # Phase-specific data
        self._loaded_data: LoadedData | None = None
        self._enriched_data: dict[str, EnrichedData] = {}
        self._built_cards: BuiltCards | None = None
        self._export_result: ExportResult | None = None

        # Initialize services - same logic as old DeckBuilder but cleaner
        self._language_impl = LanguageRegistry.get(language)

        # Initialize language-specific services
        record_mapper_class = self._language_impl.get_record_mapper()
        self._record_mapper = record_mapper_class()

        # Initialize template service
        template_dir = self._language_impl.get_template_directory()
        template_resolver = self._language_impl.get_template_filename
        self._template_service = TemplateService(template_dir, template_resolver)

        # Initialize CardBuilder service
        card_builder_class = self._language_impl.get_card_builder()
        self._card_builder = card_builder_class(template_service=self._template_service)

        # Initialize dependencies for media service
        project_root = Path(__file__).parent.parent.parent.parent.parent
        language_deck_data_dir = project_root / "languages" / language / deck_type

        # Use provided services or create defaults
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

        # Initialize managers
        self._deck_manager = DeckManager(self._backend)
        self._media_manager = MediaManager(self._backend, self._media_service)

        # Initialize MediaFileRegistrar
        self._media_file_registrar = MediaFileRegistrar(
            audio_base_path=language_deck_data_dir / "audio",
            image_base_path=language_deck_data_dir / "images",
        )

        # Initialize language-specific MediaEnricher
        if self._media_service:
            anthropic_service = get_anthropic_service()
            self._media_enricher = self._language_impl.create_media_enricher(
                audio_service=actual_audio_service,
                pexels_service=actual_pexels_service,
                anthropic_service=anthropic_service,
                audio_base_path=language_deck_data_dir / "audio",
                image_base_path=language_deck_data_dir / "images",
            )
        else:
            self._media_enricher = None  # type: ignore[assignment]

        # Records storage
        self._loaded_records: list[BaseRecord] = []

        logger.info(
            f"Initialized DeckBuilderAPI for {language} language in "
            f"{self._phase.value} phase"
        )

    # --- Phase Management ---

    def _require_phase(self, required_phase: Phase) -> None:
        """Ensure we're in the required phase."""
        if self._phase.value != required_phase.value:
            raise InvalidPhaseError(
                f"Operation requires {required_phase.value} phase, "
                f"currently in {self._phase.value}"
            )

    def _batch_records(
        self, records: list[BaseRecord], batch_size: int
    ) -> Iterator[list[BaseRecord]]:
        """Split records into batches for processing."""
        for i in range(0, len(records), batch_size):
            yield records[i:i + batch_size]

    # --- Data Loading Phase ---

    def load_data(self, data_dir: str | Path) -> LoadedData:
        """Load and validate vocabulary data with full observability.

        Args:
            data_dir: Directory containing CSV data files

        Returns:
            LoadedData with records grouped by type, validation errors, etc.

        Raises:
            InvalidPhaseError: If not in INITIALIZED phase
        """
        self._require_phase(Phase.INITIALIZED)
        data_dir = Path(data_dir)
        logger.info(f"Loading data from directory: {data_dir}")

        # Load data using language-specific mapping
        csv_to_record_type = self._language_impl.get_csv_to_record_type_mapping()

        for filename, record_type in csv_to_record_type.items():
            file_path = data_dir / filename
            if file_path.exists():
                logger.info(f"Loading {record_type} data from {file_path}")
                records = self._record_mapper.load_records_from_csv(
                    file_path, record_type
                )
                self._loaded_records.extend(records)
                logger.info(f"Loaded {len(records)} {record_type} records")
            else:
                logger.debug(f"Data file not found: {file_path}")

        # Group records by type for observability
        records_by_type: dict[str, list[BaseRecord]] = {}
        validation_errors: list[ValidationError] = []

        for record in self._loaded_records:
            record_type = record.get_record_type().value
            if record_type not in records_by_type:
                records_by_type[record_type] = []
            records_by_type[record_type].append(record)

        # Create LoadedData result
        self._loaded_data = LoadedData(
            records_by_type=records_by_type,
            total_records=len(self._loaded_records),
            source_paths=[data_dir],
            validation_errors=validation_errors,
        )

        self._phase = Phase.DATA_LOADED
        logger.info(
            f"Loaded {self._loaded_data.total_records} records across "
            f"{len(records_by_type)} types"
        )
        return self._loaded_data

    def get_loaded_data(self) -> LoadedData | None:
        """Read API: Access loaded data."""
        return self._loaded_data

    def get_records_by_type(self, record_type: str) -> list[BaseRecord]:
        """Read API: Get specific record type for inspection.

        Args:
            record_type: Type of records to retrieve

        Returns:
            List of records for the specified type

        Raises:
            InvalidPhaseError: If no data has been loaded
        """
        if not self._loaded_data:
            raise InvalidPhaseError(f"No data loaded. Current phase: {self._phase}")
        return self._loaded_data.records_by_type.get(record_type, [])

    # --- Media Enrichment Phase ---

    def enrich_media(
        self,
        record_types: list[str] | None = None,
        batch_size: int = 10,
    ) -> Iterator[EnrichmentProgress]:
        """Enrich records with media, yielding progress.

        Args:
            record_types: Specific record types to enrich, or None for all
            batch_size: Number of records to process in each batch

        Yields:
            EnrichmentProgress for each batch processed

        Raises:
            InvalidPhaseError: If not in DATA_LOADED phase
        """
        self._require_phase(Phase.DATA_LOADED)

        if not self._loaded_data:
            return

        record_types_to_process = record_types or list(
            self._loaded_data.records_by_type.keys()
        )
        logger.info(f"Enriching media for record types: {record_types_to_process}")

        for record_type in record_types_to_process:
            records = self._loaded_data.records_by_type.get(record_type, [])
            if not records:
                continue

            logger.info(
                f"Processing {len(records)} {record_type} records for "
                f"media enrichment"
            )

            # Process records using media enricher if available
            enriched_records = []
            media_data_list = []
            media_files: list[MediaFile] = []
            errors: list[EnrichmentError] = []

            if self._media_enricher:
                # Convert Records to Domain Models for media enrichment
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
                        skipped_indices.append(i)
                        continue

                # Batch enrich records that have domain models
                enriched_list = []
                if record_dicts and domain_models:
                    try:
                        # Use the media enricher to enrich records
                        for i, domain_model in enumerate(domain_models):
                            try:
                                media_data = (
                                    self._media_enricher.enrich_with_media(
                                        domain_model
                                    )
                                )
                                record_dicts[i].update(media_data)
                            except Exception as e:
                                logger.error(f"Failed to enrich record {i}: {e}")
                        enriched_list = record_dicts
                    except Exception as e:
                        logger.error(f"Batch enrichment failed for {record_type}: {e}")
                        enriched_list = [{} for _ in record_dicts]

                # Reconstruct media data for all records
                all_media_data: list[dict[str, Any]] = []
                enriched_idx = 0
                for i in range(len(records)):
                    if i in skipped_indices:
                        all_media_data.append({})
                    else:
                        if enriched_idx < len(enriched_list):
                            all_media_data.append(enriched_list[enriched_idx])
                        else:
                            all_media_data.append({})
                        enriched_idx += 1

                media_data_list = all_media_data
                enriched_records = records
            else:
                # No media enrichment available
                media_data_list = [{}] * len(records)
                enriched_records = records

            # Process in batches for progress reporting
            for batch_index, _batch in enumerate(
                self._batch_records(enriched_records, batch_size)
            ):
                processed_count = (batch_index + 1) * batch_size
                processed_count = min(processed_count, len(records))

                yield EnrichmentProgress(
                    record_type=record_type,
                    processed=processed_count,
                    total=len(records),
                    media_created=len(media_files),
                )

            # Store enriched data for this record type
            self._enriched_data[record_type] = EnrichedData(
                records=enriched_records,
                media_data=media_data_list,
                media_files_created=media_files,
                enrichment_errors=errors,
            )

        self._phase = Phase.MEDIA_ENRICHED
        total_enriched = sum(
            len(data.records) for data in self._enriched_data.values()
        )
        logger.info(
            f"Media enrichment complete. Enriched {total_enriched} records "
            f"across {len(self._enriched_data)} types"
        )

    def get_enriched_data(
        self, record_type: str | None = None
    ) -> dict[str, EnrichedData]:
        """Read API: Access enriched data by type.

        Args:
            record_type: Specific record type, or None for all types

        Returns:
            Dictionary mapping record types to their enriched data
        """
        if record_type:
            enriched = self._enriched_data.get(record_type)
            return {record_type: enriched} if enriched else {}
        return self._enriched_data.copy()

    def get_media_files(self) -> list[MediaFile]:
        """Read API: Get all created media files."""
        files = []
        for enriched in self._enriched_data.values():
            files.extend(enriched.media_files_created)
        return files

    # --- Card Building Phase ---

    def build_cards(
        self,
        record_types: list[str] | None = None,
        preview_only: bool = False,
    ) -> BuiltCards:
        """Build Anki cards from enriched data.

        Args:
            record_types: Specific record types to build cards for, or None for all
            preview_only: If True, don't advance to CARDS_BUILT phase

        Returns:
            BuiltCards containing all built card data

        Raises:
            InvalidPhaseError: If not in MEDIA_ENRICHED phase
        """
        self._require_phase(Phase.MEDIA_ENRICHED)

        record_types_to_process = record_types or list(self._enriched_data.keys())
        logger.info(f"Building cards for record types: {record_types_to_process}")

        all_cards = []
        cards_by_type: dict[str, list[Card]] = {}
        template_usage: dict[str, int] = {}
        build_errors = []

        for record_type in record_types_to_process:
            enriched = self._enriched_data.get(record_type)
            if not enriched:
                continue

            logger.info(
                f"Building cards for {len(enriched.records)} {record_type} records"
            )

            try:
                # Create subdeck for this word type
                if enriched.records:
                    subdeck_name = enriched.records[0].__class__.get_subdeck_name()
                else:
                    subdeck_name = record_type.replace("_", " ").title() + "s"

                self._deck_manager.set_current_subdeck(subdeck_name)

                # Use language-specific card processor
                card_processor = self._language_impl.get_card_processor()
                cards = card_processor.process_records_for_cards(
                    enriched.records,
                    record_type,
                    enriched.media_data,
                    self._card_builder,
                )

                # Process cards and add to backend
                created_note_types = {}
                cards_created = 0

                for field_values, note_type in cards:
                    try:
                        # Create note type if not already created
                        if note_type.name not in created_note_types:
                            note_type_id = self._backend.create_note_type(note_type)
                            created_note_types[note_type.name] = note_type_id
                        else:
                            note_type_id = created_note_types[note_type.name]

                        # Add note to backend
                        self._backend.add_note(
                            note_type_id, field_values, skip_media_processing=True
                        )

                        # Register media files
                        if self._media_file_registrar:
                            self._media_file_registrar.register_card_media(
                                field_values, self._backend
                            )

                        # Create Card object for tracking
                        # Convert field_values list to dict for Card object
                        # Use note type field names if available
                        field_names = getattr(note_type, 'field_names', [])
                        if len(field_names) >= len(field_values):
                            fields_dict = dict(
                                zip(field_names, field_values, strict=False)
                            )
                        else:
                            # Fallback to indexed keys
                            fields_dict = {
                                f"Field{i}": val
                                for i, val in enumerate(field_values)
                            }

                        card = Card(
                            fields=fields_dict,
                            note_type_name=note_type.name,
                            template_name="Basic",
                        )

                        all_cards.append((field_values, note_type))

                        if record_type not in cards_by_type:
                            cards_by_type[record_type] = []
                        cards_by_type[record_type].append(card)

                        # Track template usage
                        template_usage[note_type.name] = (
                            template_usage.get(note_type.name, 0) + 1
                        )

                        cards_created += 1
                    except Exception as e:
                        from .data_types import BuildError
                        error = BuildError(
                            record_index=cards_created,
                            record_type=record_type,
                            message=str(e),
                        )
                        build_errors.append(error)
                        logger.error(f"Failed to add {record_type} card: {e}")

                logger.info(f"Created {cards_created} {record_type} cards")

                # Reset to main deck
                self._deck_manager.reset_to_main_deck()

            except Exception as e:
                from .data_types import BuildError
                error = BuildError(
                    record_index=0,
                    record_type=record_type,
                    message=str(e),
                )
                build_errors.append(error)
                logger.error(f"Card building error for {record_type}: {e}")

        self._built_cards = BuiltCards(
            cards=all_cards,
            cards_by_type=cards_by_type,
            template_usage=template_usage,
            build_errors=build_errors,
        )

        if not preview_only:
            self._phase = Phase.CARDS_BUILT

        logger.info(f"Built {len(all_cards)} cards across {len(cards_by_type)} types")
        return self._built_cards

    def get_built_cards(self) -> BuiltCards | None:
        """Read API: Access built cards."""
        return self._built_cards

    def preview_card(self, index: int) -> CardPreview:
        """Read API: Preview a specific card.

        Args:
            index: Index of the card to preview

        Returns:
            CardPreview with rendered front/back content

        Raises:
            InvalidPhaseError: If no cards have been built
            IndexError: If index is out of range
        """
        if not self._built_cards:
            raise InvalidPhaseError("No cards built")

        if index >= len(self._built_cards.cards):
            raise IndexError(
                f"Card index {index} out of range "
                f"(have {len(self._built_cards.cards)} cards)"
            )

        field_values, note_type = self._built_cards.cards[index]

        # Convert field_values list to dict for preview
        field_names = getattr(note_type, 'field_names', [])
        if len(field_names) >= len(field_values):
            fields = dict(zip(field_names, field_values, strict=False))
        else:
            fields = {f"Field{i}": val for i, val in enumerate(field_values)}

        # Simple preview rendering
        word = fields.get("Word", field_values[0] if field_values else "N/A")
        english = fields.get(
            "English", field_values[1] if len(field_values) > 1 else "N/A"
        )
        front = f"Word: {word}"
        back = f"English: {english}"

        # Handle example field
        has_example = (
            fields.get("Example")
            or (len(field_values) > 2 and field_values[2])
        )
        if has_example:
            example = fields.get(
                "Example", field_values[2] if len(field_values) > 2 else ""
            )
            if example:
                back += f"\nExample: {example}"

        return CardPreview(
            front=front,
            back=back,
            fields=fields,
            note_type=str(note_type),
        )

    # --- Export Phase ---

    def export_deck(self, output_path: str | Path) -> ExportResult:
        """Export built cards to .apkg file.

        Args:
            output_path: Path where the deck file should be saved

        Returns:
            ExportResult with export statistics

        Raises:
            InvalidPhaseError: If not in CARDS_BUILT phase
        """
        self._require_phase(Phase.CARDS_BUILT)
        output_path = Path(output_path)

        if not self._built_cards:
            raise InvalidPhaseError("No cards built despite being in CARDS_BUILT phase")

        logger.info(f"Exporting {len(self._built_cards.cards)} cards to {output_path}")

        # Export using deck manager
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self._deck_manager.export_deck(str(output_path))

        # Create export result
        file_size = output_path.stat().st_size if output_path.exists() else 0

        self._export_result = ExportResult(
            output_path=output_path,
            file_size=file_size,
            cards_exported=len(self._built_cards.cards),
        )

        self._phase = Phase.DECK_EXPORTED
        logger.info(
            f"Export complete: {self._export_result.cards_exported} cards, "
            f"{file_size} bytes"
        )
        return self._export_result

    # --- Query APIs ---

    def get_current_phase(self) -> Phase:
        """Get the current pipeline phase."""
        return self._phase

    def get_pipeline_summary(self) -> PipelineSummary:
        """Get comprehensive summary of all phases."""
        loaded = self._loaded_data.total_records if self._loaded_data else 0
        enriched = sum(
            len(data.records) for data in self._enriched_data.values()
        )
        built = len(self._built_cards.cards) if self._built_cards else 0
        exported = self._export_result is not None

        return PipelineSummary(
            phase=self._phase,
            loaded=loaded,
            enriched=enriched,
            built=built,
            exported=exported,
        )

    def get_errors(self) -> dict[str, list[Any]]:
        """Get all errors from all phases."""
        errors: dict[str, list[Any]] = {
            "loading": [],
            "enrichment": [],
            "building": [],
        }

        if self._loaded_data:
            errors["loading"].extend(self._loaded_data.validation_errors)

        for enriched in self._enriched_data.values():
            errors["enrichment"].extend(enriched.enrichment_errors)

        if self._built_cards:
            errors["building"].extend(self._built_cards.build_errors)

        return errors

    # --- Backward Compatibility Methods ---

    def load_data_from_directory(self, data_dir: str | Path) -> None:
        """Load data from directory (backward compatibility)."""
        self.load_data(data_dir)

    def create_subdeck(self, subdeck_name: str) -> None:
        """Create a new subdeck for organizing content."""
        self._deck_manager.set_current_subdeck(subdeck_name)
        logger.info(f"Created subdeck: {subdeck_name}")

    def reset_to_main_deck(self) -> None:
        """Reset to the main deck for subsequent card additions."""
        self._deck_manager.reset_to_main_deck()
        logger.info("Reset to main deck")

    def get_statistics(self) -> dict[str, Any]:
        """Get comprehensive statistics about the deck and generation process."""
        # Count loaded records by type
        clean_pipeline_stats = {}
        if self._loaded_data:
            for record_type, records in self._loaded_data.records_by_type.items():
                record_key = record_type.replace("_", "").lower()
                clean_pipeline_stats[record_key] = len(records)

        stats = {
            "deck_info": {
                "name": self._deck_name,
                "media_enabled": True,
            },
            "loaded_data": {
                **clean_pipeline_stats,
                "total_clean_pipeline_records": (
                    self._loaded_data.total_records if self._loaded_data else 0
                ),
            },
            "deck_stats": self._deck_manager.get_stats(),
        }

        if self._media_service:
            stats.update(self._media_manager.get_detailed_stats())

        return stats

    def generate_all_cards(self, generate_media: bool = True) -> dict[str, int]:
        """Generate all cards from loaded records (backward compatibility)."""
        # Enrich media if requested
        if generate_media:
            for _ in self.enrich_media():
                pass  # Consume the iterator
        else:
            self._phase = Phase.MEDIA_ENRICHED
            # Create empty enriched data
            if self._loaded_data:
                for record_type, records in self._loaded_data.records_by_type.items():
                    self._enriched_data[record_type] = EnrichedData(
                        records=records,
                        media_data=[{}] * len(records),
                        media_files_created=[],
                        enrichment_errors=[],
                    )

        # Build cards
        built_cards = self.build_cards()

        # Format results like old DeckBuilder
        results: dict[str, int] = {}
        for record_type, cards in built_cards.cards_by_type.items():
            # Use record class to get result key
            if self._loaded_data and record_type in self._loaded_data.records_by_type:
                records = self._loaded_data.records_by_type[record_type]
                if records:
                    result_key = records[0].__class__.get_result_key()
                else:
                    result_key = record_type.replace("_", "") + "s"
            else:
                result_key = record_type.replace("_", "") + "s"

            if result_key in results:
                results[result_key] += len(cards)
            else:
                results[result_key] = len(cards)

        return results

    def get_subdeck_info(self) -> dict[str, Any]:
        """Get information about created subdecks."""
        return {
            "current_deck": self._deck_manager.get_current_deck_name(),
            "subdeck_names": self._deck_manager.get_subdeck_names(),
            "full_subdeck_names": self._deck_manager.get_full_subdeck_names(),
        }

    @property
    def deck_name(self) -> str:
        """Get the deck name."""
        return self._deck_name

    # --- Context Manager Support ---

    def __enter__(self) -> "DeckBuilderAPI":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit with cleanup."""
        # Cleanup is handled by individual services
        pass
