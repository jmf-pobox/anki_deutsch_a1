# Clean Pipeline Architecture Migration TODO

Last updated: 2025-08-21 07:45

## Current status (honest snapshot)

Short version: The Clean Pipeline components are largely built, but the main application flow is not fully using them yet. Media assets are not being embedded into the .apkg because the Clean Pipeline path does not enrich records with audio/image references.

What works now:
- RecordMapper supports 9 record types (noun, adjective, adverb, negation, verb, phrase, preposition, verb_conjugation, verb_imperative).
- CardBuilder builds notes for all 9 types and maps fields to templates.
- MediaFileRegistrar correctly scans card fields for [sound:...] and <img ...> and registers real files with the backend for APKG export.
- DeckBuilder loads CSVs into Records and builds notes via CardBuilder; legacy MVP paths remain for nouns/adjectives/adverbs/negations.

What’s not wired end-to-end yet (root causes):
1) Missing media enrichment in Clean Pipeline
   - DeckBuilder.generate_all_cards currently sets enriched_data_list = [{}] * len(records) and never invokes MediaEnricher. Result: cards lack audio/image references, so MediaFileRegistrar has nothing to register into the apkg.
2) Partial type coverage in MediaEnricher
   - StandardMediaEnricher implements noun/adjective/adverb/negation enrichment, but not verb, preposition, phrase (and no special handling for verb_conjugation/verb_imperative).
3) Legacy-domain backfill limited to 4 types
   - DeckBuilder reconstructs legacy domain models (noun/adjective/adverb/negation) for backward compatibility only. MediaEnricher expects domain-model behavior (e.g., get_image_search_strategy), so we either need domain-model shims for additional types or teach MediaEnricher to operate on record dicts for those types.
4) Templates must be verified for new types
   - CardBuilder has field mappings for all 9 types; ensure TemplateService serves templates for verb, phrase, preposition, verb_conjugation, verb_imperative.

Impact:
- Media files don’t get embedded in exported .apkg on the Clean Pipeline path because media references are never added to the card fields.

## Plan to fix (incremental, minimal-risk)

A) Wire MediaEnricher into DeckBuilder.generate_all_cards (MVP)
- For each record in each type-group, build or reconstruct an appropriate domain model and call media_enricher.enrich_record(rec.to_dict(), domain_model).
- Merge only media-related fields into enriched_data_list (image, word_audio, example_audio, plus phrase/verb specific fields as applicable).
- Keep try/except per-record to avoid stopping the run.

B) Extend MediaEnricher to cover missing types (basic support first)
- verb: at least word_audio for infinitive and example_audio; optional image.
- phrase: phrase_audio and optional image.
- preposition: word_audio and example1/2 audio; optional image.
- verb_conjugation: word_audio for infinitive/tense context and example_audio.
- verb_imperative: word_audio for infinitive; du/ihr/sie example audios (du_audio, ihr_audio, sie_audio).
- If domain-model helpers are missing, operate directly on record dicts (best-effort) to avoid blocking.

C) Verify TemplateService mappings and assets
- Ensure templates exist and are resolvable for verb, phrase, preposition, verb_conjugation, verb_imperative.
- Confirm CardBuilder fields line up with template field names.

D) Validate media registration end-to-end
- Run DeckBuilder with generate_media=True and sample CSVs.
- Confirm generated cards include [sound:...] and <img ...> so MediaFileRegistrar registers files.
- Export .apkg and verify media present in Anki’s media manager.

E) Tests and safety
- Add or adjust unit tests to cover the enrichment call and minimal new-type enrichment branches.
- Keep existing tests green; avoid broad refactors.

Success criteria
- Clean Pipeline path produces cards with media references for at least the 4 legacy-covered types immediately; others gain basic audio support shortly after.
- Exported .apkg contains corresponding media files (verified by MediaFileRegistrar counts and Anki import).
- No regressions in existing tests; any new tests pass.

## Concrete next steps (execution order)

1) DeckBuilder.generate_all_cards: replace enrichment placeholder with real calls
   - Introduce a helper _record_to_domain_model(rec) returning existing domain models where available, else fallback to rec.
   - Build enriched_data_list using StandardMediaEnricher for each record when generate_media=True.
2) Minimal MediaEnricher extensions for verb/phrase/preposition
   - Implement straightforward audio generation using record dicts; add fields CardBuilder expects (e.g., phrase_audio, example1_audio, example2_audio).
3) Verify templates exist and are mapped in TemplateService for all types
   - Especially verb/phrase/preposition and verb_conjugation/verb_imperative templates.
4) Manual e2e check
   - Load small CSVs, generate cards with media, export deck, confirm media embedded.
5) Add targeted tests (optional but recommended if time allows)
   - A unit test asserting that generate_all_cards invokes MediaFileRegistrar with non-empty media for a noun once media exists.

Notes
- MediaService paths: by default use project_root/data/audio and data/images; MediaFileRegistrar defaults to data/audio and data/images relative to CWD. Running from repo root keeps paths aligned.
- Performance: StandardMediaEnricher checks for existing files before computing search terms; API calls are avoided when assets already exist.

---

Reference pointers (for implementers)
- DeckBuilder.generate_all_cards: media enrichment placeholder is at lines ~527–536 (enriched_data_list = [{}] * len(records)).
- StandardMediaEnricher currently supports noun/adjective/adverb/negation methods; extend for other types.
- MediaFileRegistrar already plugged in after backend.add_note; no change needed there.

This document reflects the current, practical status and the exact steps to “flip the switch” safely. Once Step 1 is merged, media will start flowing into the apkg for the covered types, addressing the immediate blocker. 