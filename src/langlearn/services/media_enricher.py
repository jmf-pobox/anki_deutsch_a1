"""
Media enrichment service for the Clean Pipeline Architecture.

This service centralizes all media existence checks and generation logic,
removing infrastructure concerns from domain models.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class MediaEnricher(ABC):
    """Abstract base class for media enrichment services.

    This service handles all media-related operations including:
    - Checking for existing media files
    - Generating missing media (audio, images)
    - Managing media file paths and references
    """

    @abstractmethod
    def enrich_record(
        self, record: dict[str, Any], domain_model: Any
    ) -> dict[str, Any]:
        """Enrich a record with media files based on domain model business rules.

        Args:
            record: Base record data from CSV
            domain_model: Domain model instance for business logic

        Returns:
            Enriched record with media references added
        """
        pass

    @abstractmethod
    def audio_exists(self, text: str) -> bool:
        """Check if audio file exists for given text.

        Args:
            text: Text to check audio for

        Returns:
            True if audio file exists
        """
        pass

    @abstractmethod
    def image_exists(self, word: str) -> bool:
        """Check if image file exists for given word.

        Args:
            word: Word to check image for

        Returns:
            True if image file exists
        """
        pass

    @abstractmethod
    def generate_audio(self, text: str) -> str | None:
        """Generate audio file for text if not exists.

        Args:
            text: Text to generate audio for

        Returns:
            Path to audio file or None if generation failed
        """
        pass

    @abstractmethod
    def generate_image(self, search_terms: str, fallback: str) -> str | None:
        """Generate image file for search terms if not exists.

        Args:
            search_terms: Primary search terms for image
            fallback: Fallback search terms

        Returns:
            Path to image file or None if generation failed
        """
        pass


class StandardMediaEnricher(MediaEnricher):
    """Standard implementation of MediaEnricher using existing services."""

    def __init__(
        self,
        media_service: Any,  # MediaService - avoiding import for now
        audio_base_path: Path = Path("data/audio"),
        image_base_path: Path = Path("data/images"),
    ) -> None:
        """Initialize media enricher with existing services.

        Args:
            media_service: Existing MediaService instance
            audio_base_path: Base directory for audio files
            image_base_path: Base directory for image files
        """
        self._media_service = media_service
        self._audio_base_path = audio_base_path
        self._image_base_path = image_base_path

        # Ensure directories exist
        self._audio_base_path.mkdir(parents=True, exist_ok=True)
        self._image_base_path.mkdir(parents=True, exist_ok=True)

    def enrich_record(
        self, record: dict[str, Any], domain_model: Any
    ) -> dict[str, Any]:
        """Enrich record with media based on domain model type and business rules."""
        enriched = record.copy()

        # Determine model type for type-specific enrichment
        model_type = type(domain_model).__name__.lower()

        if model_type == "noun":
            return self._enrich_noun_record(enriched, domain_model)
        elif model_type == "adjective":
            return self._enrich_adjective_record(enriched, domain_model)
        elif model_type == "adverb":
            return self._enrich_adverb_record(enriched, domain_model)
        elif model_type == "negation":
            return self._enrich_negation_record(enriched, domain_model)
        elif model_type == "verbconjugationrecord":
            return self._enrich_verb_conjugation_record(enriched, domain_model)
        else:
            # Fallback enrichment for record types without legacy
            # domain models (key-based detection)
            try:
                if "preposition" in enriched:
                    return self._enrich_preposition_record(enriched)
                if "phrase" in enriched:
                    return self._enrich_phrase_record(enriched)
                if "verb" in enriched:
                    return self._enrich_verb_record(enriched)
                if "infinitive" in enriched:
                    # Handle VerbConjugationRecord that falls through
                    return self._enrich_verb_conjugation_record_fallback(enriched)
            except Exception as e:
                logger.warning(f"Fallback enrichment failed for {model_type}: {e}")
            logger.warning(f"Unknown model type: {model_type}")
            return enriched

    def _enrich_noun_record(self, record: dict[str, Any], noun: Any) -> dict[str, Any]:
        """Enrich noun record with media."""
        # Generate word audio (combined article + noun + plural)
        if not record.get("word_audio"):
            combined_text = noun.get_combined_audio_text()
            audio_path = self._get_or_generate_audio(combined_text)
            if audio_path:
                record["word_audio"] = f"[sound:{Path(audio_path).name}]"

        # Generate example audio
        if not record.get("example_audio") and record.get("example"):
            audio_path = self._get_or_generate_audio(record["example"])
            if audio_path:
                record["example_audio"] = f"[sound:{Path(audio_path).name}]"

        # Generate image (only for concrete nouns)
        if not record.get("image") and noun.is_concrete():
            # Check if image already exists before generating search terms
            word = record["noun"]
            if not self.image_exists(word):
                # Generate search terms (API calls) only if image missing
                search_strategy = noun.get_image_search_strategy()
                search_terms = (
                    search_strategy()
                )  # Anthropic API call happens here, only when needed
                image_path = self._get_or_generate_image(
                    word, search_terms, record["english"]
                )
                if image_path:
                    record["image"] = f'<img src="{Path(image_path).name}">'
            else:
                # Use existing image without any API calls
                image_filename = self._get_image_filename(word)
                record["image"] = f'<img src="{image_filename}">'

        return record

    def _enrich_adjective_record(
        self, record: dict[str, Any], adjective: Any
    ) -> dict[str, Any]:
        """Enrich adjective record with media."""
        # Generate word audio (combined forms)
        if not record.get("word_audio"):
            combined_text = adjective.get_combined_audio_text()
            audio_path = self._get_or_generate_audio(combined_text)
            if audio_path:
                record["word_audio"] = f"[sound:{Path(audio_path).name}]"

        # Generate example audio
        if not record.get("example_audio") and record.get("example"):
            audio_path = self._get_or_generate_audio(record["example"])
            if audio_path:
                record["example_audio"] = f"[sound:{Path(audio_path).name}]"

        # Generate image
        if not record.get("image"):
            # Check if image already exists before generating search terms
            word = record["word"]
            if not self.image_exists(word):
                # Generate search terms (API calls) only if image missing
                search_strategy = adjective.get_image_search_strategy()
                search_terms = (
                    search_strategy()
                )  # Anthropic API call happens here, only when needed
                image_path = self._get_or_generate_image(
                    word, search_terms, record["english"]
                )
                if image_path:
                    record["image"] = f'<img src="{Path(image_path).name}">'
            else:
                # Use existing image without any API calls
                image_filename = self._get_image_filename(word)
                record["image"] = f'<img src="{image_filename}">'

        return record

    def _enrich_adverb_record(
        self, record: dict[str, Any], adverb: Any
    ) -> dict[str, Any]:
        """Enrich adverb record with media."""
        # Generate word audio
        if not record.get("word_audio") and record.get("word"):
            audio_path = self._get_or_generate_audio(record["word"])
            if audio_path:
                record["word_audio"] = f"[sound:{Path(audio_path).name}]"

        # Generate example audio
        if not record.get("example_audio") and record.get("example"):
            audio_path = self._get_or_generate_audio(record["example"])
            if audio_path:
                record["example_audio"] = f"[sound:{Path(audio_path).name}]"

        # Generate image
        if not record.get("image"):
            # Check if image already exists before generating search terms
            word = record["word"]
            if not self.image_exists(word):
                # Generate search terms (API calls) only if image missing
                search_strategy = adverb.get_image_search_strategy()
                search_terms = (
                    search_strategy()
                )  # Anthropic API call happens here, only when needed
                image_path = self._get_or_generate_image(
                    word, search_terms, record["english"]
                )
                if image_path:
                    record["image"] = f'<img src="{Path(image_path).name}">'
            else:
                # Use existing image without any API calls
                image_filename = self._get_image_filename(word)
                record["image"] = f'<img src="{image_filename}">'

        return record

    def _enrich_negation_record(
        self, record: dict[str, Any], negation: Any
    ) -> dict[str, Any]:
        """Enrich negation record with media."""
        # Generate word audio
        if not record.get("word_audio") and record.get("word"):
            audio_path = self._get_or_generate_audio(record["word"])
            if audio_path:
                record["word_audio"] = f"[sound:{Path(audio_path).name}]"

        # Generate example audio
        if not record.get("example_audio") and record.get("example"):
            audio_path = self._get_or_generate_audio(record["example"])
            if audio_path:
                record["example_audio"] = f"[sound:{Path(audio_path).name}]"

        # Generate image
        if not record.get("image"):
            # Check if image already exists before generating search terms
            word = record["word"]
            if not self.image_exists(word):
                # Generate search terms (API calls) only if image missing
                search_strategy = negation.get_image_search_strategy()
                search_terms = (
                    search_strategy()
                )  # Anthropic API call happens here, only when needed
                image_path = self._get_or_generate_image(
                    word, search_terms, record["english"]
                )
                if image_path:
                    record["image"] = f'<img src="{Path(image_path).name}">'
            else:
                # Use existing image without any API calls
                image_filename = self._get_image_filename(word)
                record["image"] = f'<img src="{image_filename}">'

        return record

    def _enrich_verb_conjugation_record(
        self, record: dict[str, Any], verb_record: Any
    ) -> dict[str, Any]:
        """Enrich verb conjugation record with media.

        Args:
            record: Record dictionary with verb conjugation data
            verb_record: VerbConjugationRecord instance with media fields

        Returns:
            Enriched record with media references
        """
        # Generate word audio (combined infinitive + conjugated forms with pronouns)
        if not record.get("word_audio") and record.get("infinitive"):
            combined_audio_text = self._get_verb_combined_audio_text(record)
            audio_path = self._get_or_generate_audio(combined_audio_text)
            if audio_path:
                record["word_audio"] = f"[sound:{Path(audio_path).name}]"

        # Generate example audio
        if not record.get("example_audio") and record.get("example"):
            audio_path = self._get_or_generate_audio(record["example"])
            if audio_path:
                record["example_audio"] = f"[sound:{Path(audio_path).name}]"

        # Generate image based on example sentence (representing the action)
        if (
            not record.get("image")
            and record.get("infinitive")
            and record.get("example")
        ):
            infinitive = record["infinitive"]
            if not self.image_exists(infinitive):
                # Use example sentence as search terms for better verb visualization
                search_terms = record["example"]
                fallback = record.get("english", infinitive)
                image_path = self._get_or_generate_image(
                    infinitive, search_terms, fallback
                )
                if image_path:
                    record["image"] = f'<img src="{Path(image_path).name}">'
            else:
                # Use existing image without any API calls
                image_filename = self._get_image_filename(infinitive)
                record["image"] = f'<img src="{image_filename}">'

        return record

    def _enrich_verb_conjugation_record_fallback(
        self, record: dict[str, Any]
    ) -> dict[str, Any]:
        """Fallback enrichment for VerbConjugationRecord when domain model is None."""
        # This is essentially the same logic but without domain model dependency
        return self._enrich_verb_conjugation_record(record, None)

    def _get_verb_combined_audio_text(self, record: dict[str, Any]) -> str:
        """Generate combined audio text for verb conjugations.

        Creates audio text that includes the infinitive plus all conjugated forms
        with their pronouns, similar to how adjectives work.

        For present/perfect/preterite: "infinitive, ich form, du form, er form, wir form, ihr form, sie form"
        For imperative: "infinitive, du form, ihr form, Sie form, wir form"

        Args:
            record: VerbConjugationRecord data dictionary

        Returns:
            Combined audio text string
        """
        infinitive = record.get("infinitive", "")
        tense = record.get("tense", "")

        parts = [infinitive]

        if tense == "imperative":
            # For imperatives: du form, ihr form, Sie form, wir form
            if record.get("du"):
                parts.append(f"du {record['du']}")
            if record.get("ihr"):
                parts.append(f"ihr {record['ihr']}")
            if record.get("sie"):
                parts.append(f"Sie {record['sie']}")
            if record.get("wir"):
                parts.append(f"wir {record['wir']}")
        else:
            # For conjugations (present/perfect/preterite): all 6 persons
            if record.get("ich"):
                parts.append(f"ich {record['ich']}")
            if record.get("du"):
                parts.append(f"du {record['du']}")
            if record.get("er"):
                parts.append(f"er {record['er']}")
            if record.get("wir"):
                parts.append(f"wir {record['wir']}")
            if record.get("ihr"):
                parts.append(f"ihr {record['ihr']}")
            if record.get("sie"):
                parts.append(f"sie {record['sie']}")

        return ", ".join(parts)

    def _enrich_preposition_record(self, record: dict[str, Any]) -> dict[str, Any]:
        """Enrich preposition record with basic audio support.

        Fields expected in record dict:
        - preposition, english, case, example1, example2
        Populates:
        - word_audio, example1_audio, example2_audio
        """
        # Word audio
        if not record.get("word_audio") and record.get("preposition"):
            audio_path = self._get_or_generate_audio(record["preposition"])
            if audio_path:
                record["word_audio"] = f"[sound:{Path(audio_path).name}]"

        # Example 1 audio
        if not record.get("example1_audio") and record.get("example1"):
            audio_path = self._get_or_generate_audio(record["example1"])
            if audio_path:
                record["example1_audio"] = f"[sound:{Path(audio_path).name}]"

        # Example 2 audio
        if not record.get("example2_audio") and record.get("example2"):
            audio_path = self._get_or_generate_audio(record["example2"])
            if audio_path:
                record["example2_audio"] = f"[sound:{Path(audio_path).name}]"

        return record

    def _enrich_phrase_record(self, record: dict[str, Any]) -> dict[str, Any]:
        """Enrich phrase record with audio and image based on the phrase itself.

        - Image: use the phrase text as the filename/search key; fallback to
          context or english for search terms when available.
        - Audio: generate pronunciation for the full phrase (back-side only).
        """
        # Phrase audio
        if not record.get("phrase_audio") and record.get("phrase"):
            audio_path = self._get_or_generate_audio(record["phrase"])
            if audio_path:
                record["phrase_audio"] = f"[sound:{Path(audio_path).name}]"

        # Phrase image (front-side visual cue). Use phrase for filename and search.
        if not record.get("image") and record.get("phrase"):
            phrase_text = record.get("phrase", "")
            # Prefer context as an assisting hint if present; else english
            fallback_terms = record.get("context") or record.get("english") or ""
            image_path = self._get_or_generate_image(
                word=phrase_text,
                search_terms=phrase_text,
                fallback=fallback_terms,
            )
            if image_path:
                record["image"] = f'<img src="{Path(image_path).name}">'

        return record

    def _enrich_verb_record(self, record: dict[str, Any]) -> dict[str, Any]:
        """Enrich simple verb record with audio and image support."""
        # Prefer example sentence audio and infinitive audio
        if not record.get("example_audio") and record.get("example"):
            audio_path = self._get_or_generate_audio(record["example"])
            if audio_path:
                record["example_audio"] = f"[sound:{Path(audio_path).name}]"

        if not record.get("word_audio") and record.get("verb"):
            # Create domain model to use get_combined_audio_text() for full conjugations
            try:
                from langlearn.models.verb import Verb

                verb_model = Verb(
                    verb=record["verb"],
                    english=record.get("english", ""),
                    present_ich=record.get("present_ich", ""),
                    present_du=record.get("present_du", ""),
                    present_er=record.get("present_er", ""),
                    perfect=record.get("perfect", ""),
                    example=record.get("example", ""),
                )
                # Use combined audio with all conjugated forms and pronouns
                combined_text = verb_model.get_combined_audio_text()
                audio_path = self._get_or_generate_audio(combined_text)
                if audio_path:
                    record["word_audio"] = f"[sound:{Path(audio_path).name}]"
            except Exception as e:
                # Fallback to simple infinitive audio if domain model creation fails
                verb_name = record.get("verb", "unknown")
                verb_fields = [
                    "verb",
                    "english",
                    "present_ich",
                    "present_du",
                    "present_er",
                    "perfect",
                ]
                verb_data = {k: v for k, v in record.items() if k in verb_fields}
                logger.warning(
                    f"Verb model creation failed for '{verb_name}' "
                    f"(type: {type(e).__name__}): {e}. Data: {verb_data}"
                )
                audio_path = self._get_or_generate_audio(record["verb"])
                if audio_path:
                    record["word_audio"] = f"[sound:{Path(audio_path).name}]"

        # Generate image based on example sentence (like nouns do)
        if not record.get("image") and record.get("verb") and record.get("example"):
            verb = record["verb"]
            if not self.image_exists(verb):
                # Use example sentence as search terms for verb image generation
                search_terms = record["example"]
                fallback = record.get("english", verb)
                image_path = self._get_or_generate_image(verb, search_terms, fallback)
                if image_path:
                    record["image"] = f'<img src="{Path(image_path).name}">'
            else:
                # Use existing image without any API calls
                image_filename = self._get_image_filename(verb)
                record["image"] = f'<img src="{image_filename}">'

        return record

    def enrich_records(
        self, record_dicts: list[dict[str, Any]], domain_models: list[Any]
    ) -> list[dict[str, Any]]:
        """Batch enrich multiple records for improved performance.

        Args:
            record_dicts: List of record dictionaries to enrich
            domain_models: Corresponding list of domain models (can contain None)

        Returns:
            List of enriched record dictionaries
        """
        enriched_records = []

        for record_dict, domain_model in zip(record_dicts, domain_models, strict=False):
            try:
                enriched = self.enrich_record(record_dict, domain_model)
                enriched_records.append(enriched)
            except Exception as e:
                word = record_dict.get("word", "unknown")
                logger.warning(f"Record enrichment failed for {word}: {e}")
                enriched_records.append({})

        return enriched_records

    def _get_or_generate_audio(self, text: str) -> str | None:
        """Get existing audio or generate if not exists.

        Ensures filename scheme matches MediaService (md5 hex). Also supports
        legacy filenames (audio_<8charhash>.mp3) for backward compatibility.
        """
        if not text or not text.strip():
            return None

        # Check if audio already exists (support both current and legacy naming)
        existing_filename = self._find_existing_audio_filename(text)
        if existing_filename:
            return str(self._audio_base_path / existing_filename)

        # Generate new audio using MediaService and return its actual path
        return self.generate_audio(text)

    def _get_or_generate_image(
        self, word: str, search_terms: str, fallback: str
    ) -> str | None:
        """Get existing image or generate if not exists."""
        if not word:
            return None

        # Check if image already exists
        if self.image_exists(word):
            # Return existing image path
            image_filename = self._get_image_filename(word)
            return str(self._image_base_path / image_filename)

        # Generate new image
        return self.generate_image(search_terms, fallback)

    def audio_exists(self, text: str) -> bool:
        """Check if audio file exists for given text (current or legacy name)."""
        if not text:
            return False
        return self._find_existing_audio_filename(text) is not None

    def image_exists(self, word: str) -> bool:
        """Check if image file exists for given word."""
        if not word:
            return False

        image_filename = self._get_image_filename(word)
        return (self._image_base_path / image_filename).exists()

    def generate_audio(self, text: str) -> str | None:
        """Generate audio file for text."""
        try:
            return self._media_service.generate_audio(text)  # type: ignore[no-any-return]
        except Exception as e:
            logger.warning(f"Audio generation failed for '{text[:50]}...': {e}")
            return None

    def generate_image(self, search_terms: str, fallback: str) -> str | None:
        """Generate image file for search terms."""
        try:
            return self._media_service.generate_image(search_terms, fallback)  # type: ignore[no-any-return]
        except Exception as e:
            logger.warning(f"Image generation failed for '{search_terms}': {e}")
            return None

    def _get_audio_filename(self, text: str) -> str:
        """Get standardized (legacy) audio filename for text.

        Legacy scheme expected by tests and existing datasets:
        "audio_<first8_of_md5>.mp3". We keep full-md5 variant as a fallback
        in candidate search for forward compatibility.
        """
        import hashlib

        md5_hex = hashlib.md5(text.encode()).hexdigest()
        return f"audio_{md5_hex[:8]}.mp3"

    def _candidate_audio_filenames(self, text: str) -> list[str]:
        """Return possible audio filenames for text (legacy first, then full md5)."""
        import hashlib

        md5_hex = hashlib.md5(text.encode()).hexdigest()
        legacy = f"audio_{md5_hex[:8]}.mp3"
        full_md5 = f"{md5_hex}.mp3"
        return [legacy, full_md5]

    def _find_existing_audio_filename(self, text: str) -> str | None:
        """Find an existing audio filename among known naming schemes.

        Priority order:
        1) The exact name from _get_audio_filename (patchable in tests)
        2) Other known candidates (legacy/full-md5)
        """
        # 1) Try the primary scheme first (supports test patching)
        primary = self._get_audio_filename(text)
        if (self._audio_base_path / primary).exists():
            return primary

        # 2) Try other candidates
        for name in self._candidate_audio_filenames(text):
            if name == primary:
                continue
            if (self._audio_base_path / name).exists():
                return name
        return None

    def _get_image_filename(self, word: str) -> str:
        """Get standardized image filename for word."""
        # Clean word for filename (match existing logic)
        safe_word = (
            "".join(c for c in word.lower() if c.isalnum() or c in (" ", "-", "_"))
            .rstrip()
            .replace(" ", "_")
        )
        return f"{safe_word}.jpg"
