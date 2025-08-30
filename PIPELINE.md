# Pipeline Migration Plan

This document outlines a practical, incremental plan to migrate from the current DeckBuilder-centric orchestration to an explicit, composable pipeline using the mini pipeline framework in `src/langlearn/pipeline/pipeline.py`.

The goal is to:
- Make the end-to-end deck build flow explicit, testable, and modular via `Pipeline`, `PipelineTask`, and `PipelineObject`.
- Preserve existing behavior, keep public APIs (e.g., `DeckBuilder`) stable, and enable gradual adoption.
- Improve observability, type-safety, and reuse of the core steps.


## 0) Current State Summary

Primary flow (implemented inside `DeckBuilder`):
1. Data loading: `load_data_from_directory()` maps CSVs → Clean Pipeline `Record` objects, and also populates legacy models for compatibility.
2. Group & orchestrate: `generate_all_cards()` groups records by type and for each type:
   - Choose subdeck name
   - Optional batch media enrichment via `StandardMediaEnricher`
   - Build cards via `CardBuilder` (normal, verb conjugations, unified articles)
   - Create note types and add notes via `AnkiBackend`
   - Register media
3. Export: `export_deck()` via `DeckManager`/backend.

Mini pipeline framework available in `pipeline.py`:
- `PipelineObject[T]`: mutable holder for the value moving through the pipeline
- `PipelineTask[InT, OutT]`: units of work with lifecycle, validation, and logging
- `Pipeline[T]`: orchestrates a typed sequence of tasks


## 1) Target Architecture Overview

We will express the deck generation lifecycle as a chain of `PipelineTask` instances operating on typed carriers. The high-level end-to-end pipeline:

Input: `BuildContext` (configuration) + `ProjectData` (paths)

1. LoadDataTask: File system → `RecordSet`
2. GroupRecordsTask: `RecordSet` → `GroupedRecords`
3. CreateSubdeckTask: `GroupedRecords` → `GroupedRecords` (idempotent, side-effect: deck manager)
4. MediaEnrichmentTask: `GroupedRecords` → `EnrichedGroupedRecords`
5. CardBuildTask: `EnrichedGroupedRecords` → `BuiltCards` (list[(fields, note_type)])
6. WriteNotesTask: `BuiltCards` → `WriteResult` (counts, ids)
7. ExportDeckTask (optional): `WriteResult` → `ExportResult`

Output: `PipelineReport` containing totals, per-type counts, subdeck info, and media stats.

The end-user API can remain `DeckBuilder.generate_all_cards(...)` and `export_deck(...)`, but internally it will construct and run a `Pipeline` when the feature flag is enabled.


## 2) Data Types (lightweight containers)

Define simple typed containers to pass between tasks. These are plain dataclasses (or TypedDicts) to avoid mutability pitfalls and ease testing.

- BuildContext
  - deck_name: str
  - media_enabled: bool
  - backend_type: Literal["anki"]
  - project_root: Path

- ProjectData
  - data_dir: Path

- RecordSet
  - records: list[BaseRecord]
  - legacy_models: dict[str, list[Any]]  # optional compatibility payload

- GroupedRecords
  - by_type: dict[str, list[BaseRecord]]

- EnrichedGroupedRecords
  - by_type: dict[str, list[tuple[BaseRecord, dict]]]

- BuiltCards
  - items: list[tuple[dict[str, Any], NoteType]]
  - counts_by_type: dict[str, int]

- WriteResult
  - created_note_types: set[str]
  - counts_by_type: dict[str, int]
  - total_cards: int

- ExportResult
  - output_path: Path
  - file_size: int | None

- PipelineReport
  - aggregated stats including deck/subdecks/media if available

Note: Many of these are already implicitly represented inside `DeckBuilder`. We will keep them minimal and focused on pipeline step IO.


## 3) Proposed PipelineTasks

Each task is a thin wrapper around existing `DeckBuilder` capabilities and services. All tasks subclass `PipelineTask[InT, OutT]` from `pipeline.py`.

1) LoadDataTask[BuildContext, RecordSet]
- Uses `RecordMapper.load_records_from_csv` for each configured CSV in `data_dir`.
- Optionally populates `legacy_models` by reusing `_load_legacy_models_from_records`.
- Mirrors `DeckBuilder.load_data_from_directory` logic.

2) GroupRecordsTask[RecordSet, GroupedRecords]
- Groups by simplified record type, applying existing special cases (`unified_article` etc.).
- Mirrors grouping logic at the start of `generate_all_cards`.

3) CreateSubdeckTask[GroupedRecords, GroupedRecords]
- Iterates group keys in deterministic order; calls `DeckManager.set_current_subdeck(...)` using existing naming rules (verbs grouped together, etc.).
- Stateless w.r.t. output value (passes through); purpose is side-effect consistency and centralizing naming rules.
- After each type is processed in downstream tasks, we will call a complementary ResetDeckBoundaryTask if needed, or make WriteNotesTask responsible for resetting.

4) MediaEnrichmentTask[GroupedRecords, EnrichedGroupedRecords]
- If media disabled or `self._media_enricher` is None, pass-through with empty dicts.
- Otherwise reuses `_record_to_domain_model` and batch `StandardMediaEnricher.enrich_records`.
- Preserves the filtering to media keys.

5) CardBuildTask[EnrichedGroupedRecords, BuiltCards]
- For each type:
  - `verbconjugation`: use `CardBuilder.build_verb_conjugation_cards`
  - `unified_article`: use `CardBuilder.build_article_pattern_cards` and retain current behavior regarding noun-article practice (currently disabled) 
  - otherwise: `CardBuilder.build_cards_from_records`
- Accumulate `(field_values, note_type)` and per-type counts.

6) WriteNotesTask[BuiltCards, WriteResult]
- For each card:
  - Create or reuse note type via `AnkiBackend.create_note_type` (cache)
  - Add note via `AnkiBackend.add_note(..., skip_media_processing=True)`
  - Register media via `MediaFileRegistrar` where present
- Maintain per-type counts and totals (respect the consolidated keys: verbs → "verbs", unified_article → "articles", etc.).
- Reset deck back to main via `DeckManager.reset_to_main_deck()` after finishing each type block. Alternatively, we can keep deck resets as a standalone task that runs after this step.

7) ExportDeckTask[WriteResult, ExportResult] (optional)
- Calls through to `DeckManager.export_deck` into a configured output path.

8) BuildReportTask[ExportResult | WriteResult, PipelineReport]
- Produce the final stats format to match `DeckBuilder.get_statistics()`/CLI output expectations.

Note: To keep the pipeline linear, we can model type-scoped loops inside tasks (e.g., MediaEnrichmentTask processes all groups internally). Alternate approach is a per-type nested Pipeline constructed dynamically, but the first iteration keeps the surface simpler and closer to today’s flow.


## 4) Integration Strategy (Incremental)

Phase A: Documentation + Interfaces
- Add this plan (PIPELINE.md) and declare minimal dataclasses and type aliases in a new module `src/langlearn/pipeline/types.py` (optional, future PR).

Phase B: Task Shims (Non-invasive)
- Implement the proposed tasks under `src/langlearn/pipeline/tasks/` as thin wrappers that call existing `DeckBuilder` collaborators (`RecordMapper`, `StandardMediaEnricher`, `CardBuilder`, `DeckManager`, `AnkiBackend`).
- Each task receives required collaborators via constructor dependency injection. No global state.

Phase C: Opt-in Pipeline in DeckBuilder
- Add a feature flag (e.g., `use_pipeline: bool=False`) to `DeckBuilder.__init__`.
- In `generate_all_cards()`, if `use_pipeline` is True and `_loaded_records` is empty, build and run a `Pipeline` that:
  - Starts with `PipelineObject[BuildContext]` pre-populated from `DeckBuilder`’s properties and data_dir (if known), or use the current in-memory `_loaded_records` as the `RecordSet` input if already loaded by callers.
  - Appends the tasks described in section 3.
  - Returns results and keeps current public return type/format.
- Keep the legacy path untouched when `use_pipeline` is False.

Phase D: CLI/Entry integration
- In `src/langlearn/main.py`, optionally expose an environment variable or CLI flag to toggle the pipeline path. Default off for now.

Phase E: Full Migration
- Make the pipeline path the default after adequate test coverage.
- Deprecate legacy orchestration code, but keep key helpers (e.g., domain model mapping, card building) since they are used by tasks.


## 5) Error Handling, Logging, Validation

- Use `PipelineTask.is_valid()` defaults and enrich tasks with domain validations (e.g., ensure non-empty `records` when required, check data_dir existence).
- Keep existing logging fidelity: tasks log key steps and counts. Leverage `PipelineTaskState.start/complete` messages automatically.
- Wrap batch operations with try/except at the task level; convert to partial failures with warnings where feasible.
- Surface meaningful `ValueError` from tasks to fail-fast when misconfigured (e.g., unknown backend_type).


## 6) Configuration and DI

- Tasks accept collaborators via constructor parameters pulled from `DeckBuilder`:
  - RecordMapper, MediaService (optional), StandardMediaEnricher, CardBuilder, MediaFileRegistrar, DeckManager, AnkiBackend.
- BuildContext carries runtime flags (media on/off). ProjectData identifies data directories.
- This preserves the current dependency injection strategy and makes tasks independently testable.


## 7) Testing Plan

- Unit tests per task:
  - LoadDataTask: Given a temp directory with CSVs, produces proper `RecordSet`.
  - GroupRecordsTask: Correct grouping rules and naming edge cases.
  - MediaEnrichmentTask: With and without media service; filters only allowed media keys.
  - CardBuildTask: Respect special cases (verbs, unified_article). Deterministic counts.
  - WriteNotesTask: Creates note types once; counts per type; registers media.
- Pipeline integration test:
  - Construct a small end-to-end Pipeline using synthetic records and validate final counts match legacy `generate_all_cards` for the same input.
- Maintain existing tests. Add a small compatibility test that toggles `use_pipeline=True` and asserts identical outputs where possible.


## 8) Backwards Compatibility & Rollout

- Public `DeckBuilder` API remains stable.
- Generated deck contents and statistics should remain unchanged for existing datasets. Minor logging differences are acceptable.
- A feature flag allows fall-back to legacy orchestration until parity is verified.
- After stability, flip default to `use_pipeline=True` and document deprecation timeline for the legacy path.


## 9) Example Sketch (pseudo-code)

```python
# Inside DeckBuilder.generate_all_cards(generate_media=True)
if self.use_pipeline:
    ctx = BuildContext(
        deck_name=self.deck_name,
        media_enabled=generate_media and self.enable_media_generation,
        backend_type=self.backend_type,
        project_root=Path(__file__).parent.parent.parent,
    )

    holder: PipelineObject[BuildContext] = PipelineObject()
    holder.input = ctx
    pipe: Pipeline[BuildContext] = Pipeline(holder)

    pipe = (
        pipe
        .add_task(LoadDataTask(record_mapper=self._record_mapper, data_dir=data_dir,
                               legacy_loader=self._load_legacy_models_from_records))
        .add_task(GroupRecordsTask())
        .add_task(CreateSubdeckTask(deck_manager=self._deck_manager))
        .add_task(MediaEnrichmentTask(media_enricher=self._media_enricher,
                                     record_to_domain=self._record_to_domain_model))
        .add_task(CardBuildTask(card_builder=self._card_builder))
        .add_task(WriteNotesTask(backend=self._backend,
                                 registrar=self._media_file_registrar,
                                 deck_manager=self._deck_manager))
        # optionally
        # .add_task(ExportDeckTask(deck_manager=self._deck_manager, output_path=...))
    )

    result = pipe.run()
    return result.counts_by_type
else:
    return self._generate_all_cards_legacy(generate_media)
```


## 10) Work Breakdown (Actionable Items)

1. Create pipeline data types (light-weight dataclasses) in `pipeline/types.py`.
2. Implement tasks (thin shims) in `pipeline/tasks/`:
   - LoadDataTask, GroupRecordsTask, CreateSubdeckTask,
     MediaEnrichmentTask, CardBuildTask, WriteNotesTask, ExportDeckTask, BuildReportTask.
3. Add `use_pipeline: bool = False` flag to `DeckBuilder` and a code path to construct and execute the pipeline using existing collaborators.
4. Add unit tests for tasks and a small end-to-end pipeline test mirroring a subset of `generate_all_cards`.
5. Add CLI flag or env var to toggle pipeline usage in `main.py` (default off initially).
6. Validate parity on a sample dataset; fix discrepancies; iterate.
7. Make pipeline path default, keep legacy as fallback for one release; then deprecate.


## 11) Risks and Mitigations

- Parity drift: Keep tasks as thin wrappers around existing logic; share helper methods.
- Type evolution: Keep containers minimal; don’t over-constrain types initially.
- Media side-effects: Ensure idempotent behavior and reuse current registrar; add tests around file registration.
- Performance: Batch enrichment retained; logging kept at info/debug as today.


## 12) Conclusion

This plan transitions the current implicit orchestration into a clear, typed pipeline without disrupting the public interface. It emphasizes incremental adoption, high test coverage, and reuse of existing, well-understood components to minimize risk while improving maintainability and extensibility.