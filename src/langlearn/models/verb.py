from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from langlearn.protocols.media_generation_protocol import MediaGenerationCapable

if TYPE_CHECKING:
    from collections.abc import Callable

    from langlearn.protocols.image_query_generation_protocol import (
        ImageQueryGenerationProtocol,
    )

logger = logging.getLogger(__name__)


"""German Verb Domain Model.

This module contains the domain model for German verbs with specialized logic for
German language learning applications. The module is responsible for:

CORE RESPONSIBILITIES:
    - Modeling German verb data (infinitive, English, conjugations, tense, example)
    - Implementing MediaGenerationCapable protocol for media enrichment
    - Providing German-specific linguistic validation and conjugation patterns
    - Contributing domain expertise for image search term generation
    - Supporting audio generation with proper conjugation pronunciation and SSML

DESIGN PRINCIPLES:
    - Domain model is SMART: Contains German verb expertise and linguistic knowledge
    - Services are DUMB: External services receive rich context, no domain logic
    - Single Responsibility: Verb logic stays in Verb model, not in services
    - Dependency Injection: Protocol-based design for loose coupling

GERMAN LINGUISTIC FEATURES:
    - Conjugation system across all tenses (present, preterite, perfect, imperative)
    - Verb classifications (regelmäßig, unregelmäßig, gemischt)
    - Separable vs non-separable verb patterns
    - Auxiliary verb selection (haben vs sein) for perfect tenses
    - Context-aware search term generation using action/concept visualization
    - SSML-enhanced audio generation with German tense labels

INTEGRATION POINTS:
    - MediaGenerationCapable protocol for image/audio media enrichment
    - AnthropicServiceProtocol for AI-powered search term generation
    - MediaEnricher service for coordinated media asset generation

Usage:
    Basic usage:
        >>> verb = Verb(
        ...     verb="arbeiten",
        ...     english="to work",
        ...     classification="regelmäßig",
        ...     present_ich="arbeite",
        ...     present_du="arbeitest",
        ...     present_er="arbeitet",
        ...     perfect="hat gearbeitet",
        ...     example="Er arbeitet in einer Bank."
        ... )

    Media generation with dependency injection:
        >>> strategy = verb.get_image_search_strategy(anthropic_service)
        >>> search_terms = strategy()  # Returns context-aware search terms
        >>> audio_text = verb.get_combined_audio_text()  # SSML conjugation audio
"""


@dataclass
class Verb(MediaGenerationCapable):
    """German verb domain model with linguistic expertise and media generation.

    Represents a German verb with its properties, German linguistic knowledge,
    and specialized logic for media enrichment. German verbs are characterized
    by their complex conjugation patterns, tense systems, auxiliary selection,
    and separable/non-separable distinctions.

    This model implements MediaGenerationCapable protocol to contribute domain
    expertise for image and audio generation, using action-based strategies
    for verb concept visualization and SSML for conjugation pronunciation.

    Attributes:
        verb: The German verb in infinitive form (e.g., "arbeiten", "gehen")
        english: English translation (e.g., "to work", "to go")
        classification: Verb classification (regelmäßig, unregelmäßig, gemischt)
        present_ich/du/er: Present tense conjugations
        präteritum: Preterite form (3rd person singular)
        auxiliary: Auxiliary verb for perfect tense (haben or sein)
        perfect: Perfect tense form
        example: German example sentence demonstrating usage
        separable: Whether the verb is separable (true/false)

    Note:
        This model follows the design principle that domain models are SMART
        (contain expertise) while services are DUMB (execute instructions).
    """

    verb: str
    english: str
    present_ich: str
    present_du: str
    present_er: str
    perfect: str
    example: str
    classification: str = field(default="")
    präteritum: str = field(default="")
    auxiliary: str = field(default="")
    separable: bool = field(default=False)

    def __post_init__(self) -> None:
        """Validate the verb data after initialization."""
        # Validate core required fields
        required_fields = [
            "verb",
            "english",
            "present_ich",
            "present_du",
            "present_er",
            "perfect",
            "example",
        ]
        for field_name in required_fields:
            value = getattr(self, field_name)
            if value is None or (isinstance(value, str) and not value.strip()):
                raise ValueError(f"Required field '{field_name}' cannot be empty")

        # Validate separable is boolean
        if not isinstance(self.separable, bool):
            raise ValueError(
                f"Field 'separable' must be a boolean, got {type(self.separable)}"
            )

        # Validate auxiliary if provided (should be haben or sein)
        if (
            self.auxiliary
            and self.auxiliary.strip()
            and self.auxiliary not in {"haben", "sein"}
        ):
            raise ValueError(
                f"Invalid auxiliary verb: {self.auxiliary}. Must be 'haben' or 'sein'."
            )

    def get_image_search_strategy(
        self, anthropic_service: ImageQueryGenerationProtocol
    ) -> Callable[[], str]:
        """Get strategy for generating image search terms with domain expertise.

        Creates a callable that uses this verb's domain knowledge to generate
        context-aware image search terms. The verb contributes German linguistic
        expertise (action concepts, separable patterns, tense context) while
        the anthropic service executes the actual AI processing.

        Design: Domain model is SMART (provides rich context), service is DUMB
        (processes whatever context it receives).

        Args:
            anthropic_service: Service implementing ImageQueryGenerationProtocol for
                AI-powered search term generation.

        Returns:
            Callable that when invoked returns image search terms as string.
            Falls back to direct English translation if service fails.

        Example:
            >>> verb = Verb(verb="arbeiten", english="to work",
            ...             present_ich="arbeite", present_du="arbeitest",
            ...             present_er="arbeitet", perfect="hat gearbeitet",
            ...             example="Er arbeitet in einer Bank.")
            >>> strategy = verb.get_image_search_strategy(anthropic_service)
            >>> search_terms = strategy()  # Returns context-aware search terms
        """

        def generate_search_terms() -> str:
            """Execute search term generation strategy with verb context."""
            logger.debug(f"Generating search terms for verb: '{self.verb}'")

            try:
                # Use domain expertise to build rich context for the service
                context = self._build_search_context()
                result = anthropic_service.generate_image_query(context)
                if result and result.strip():
                    ai_generated_terms = result.strip()
                    logger.info(f"AI terms for '{self.verb}': '{ai_generated_terms}'")
                    return ai_generated_terms
            except Exception as e:
                logger.warning(f"AI generation failed for '{self.verb}': {e}")
                # Service failed, use fallback
                pass

            # Fallback to direct English translation
            logger.info(f"Fallback terms for '{self.verb}': '{self.english}'")
            return self.english

        return generate_search_terms

    def get_combined_audio_text(self) -> str:
        """Get combined text for verb conjugation audio with German tense labels.

        Returns:
            Combined text with German labels, conjugations, and SSML pause tags:
            "arbeiten, Präsens ich arbeite, du arbeitest, Perfekt hat gearbeitet"
            Or for imperatives: "arbeiten, Imperativ du fahr ab"
        """
        parts = [self.verb]

        # Check if this is an imperative (indicated by placeholder values)
        is_imperative = (
            self.present_ich == "[imperative]"
            or self.perfect == "[imperative]"
            or (
                self.present_ich == "[imperative]" and self.present_er == "[imperative]"
            )
        )

        if is_imperative:
            # For imperatives, only include the actual imperative forms
            parts.append("<break strength='strong'/>Imperativ")
            if self.present_du and self.present_du != "[imperative]":
                parts.append(f"du {self.present_du}")
            # Note: other imperative forms (ihr, Sie, wir) not in basic Verb model
            return ", ".join(parts)

        # Regular conjugation handling (not imperative)
        # Präsens (Present tense) with German label
        if self.present_ich or self.present_du or self.present_er:
            parts.append("<break strength='strong'/>Präsens")
            if self.present_ich:
                parts.append(f"ich {self.present_ich}")
            if self.present_du:
                parts.append(f"du {self.present_du}")
            if self.present_er:
                parts.append(f"er sie es {self.present_er}")

        # Präteritum with German label
        if self.präteritum:
            parts.extend(
                ["<break strength='strong'/>Präteritum", f"er sie es {self.präteritum}"]
            )

        # Perfekt with German label
        if self.perfect:
            # The perfect form typically already includes the auxiliary verb
            parts.extend(
                ["<break strength='strong'/>Perfekt", f"er sie es {self.perfect}"]
            )

        return ", ".join(parts)

    def get_audio_segments(self) -> dict[str, str]:
        """Get all audio segments needed for verb cards.

        Verbs require multiple audio segments including conjugation forms:
        - word_audio: Complete conjugation with tense labels
        - example_audio: Example sentence demonstrating usage
        - du_audio: 2nd person singular form (if available)
        - ihr_audio: 2nd person plural form (if available)
        - sie_audio: 3rd person plural form (if available)
        - wir_audio: 1st person plural form (if available)

        Returns:
            Dictionary mapping audio field names to text content
        """
        audio_segments = {
            "word_audio": self.get_combined_audio_text(),
            "example_audio": self.example,
        }

        # Add conjugation-specific audio if forms are available
        if self.present_du:
            audio_segments["du_audio"] = f"du {self.present_du}"

        # For verb models that have additional conjugations, add them
        # These fields may not be present in all verb instances
        if hasattr(self, "present_ihr") and self.present_ihr:
            audio_segments["ihr_audio"] = f"ihr {self.present_ihr}"
        if hasattr(self, "present_sie") and self.present_sie:
            audio_segments["sie_audio"] = f"sie {self.present_sie}"
        if hasattr(self, "present_wir") and self.present_wir:
            audio_segments["wir_audio"] = f"wir {self.present_wir}"

        return audio_segments

    def _build_search_context(self) -> str:
        """Build rich context for image search using German verb expertise.

        Constructs visualization guidance based on German linguistic knowledge.
        Considers verb action concepts, separable patterns, and tense context to
        provide action-focused strategies for representing verb concepts visually.

        This method embodies the domain model's expertise about German verbs and
        their visualization challenges, providing rich context that services can
        use without needing to understand German conjugation patterns.

        Returns:
            Formatted context string with:
            - Verb details (German infinitive, English translation, classification)
            - Action-based visualization strategy
            - Example usage and conjugation context
            - Instructions for generating appropriate search terms

        Example:
            For action verb "arbeiten":
                "Focus on the action being performed, show people working"
            For motion verb "gehen":
                "Focus on movement and direction, show people walking"

        Note:
            This is a private method called by get_image_search_strategy() to
            contribute domain expertise to the search term generation process.
        """
        # Determine visualization strategy based on verb action concept
        action_strategy = self._get_action_visualization_strategy()

        # Add classification context (German linguistic feature)
        classification_info = self.classification or "standard verb"

        # Add separable context if applicable
        separable_info = "separable" if self.separable else "non-separable"

        return f"""
        German verb: {self.verb} ({separable_info}, {classification_info})
        English: {self.english}
        Example usage: {self.example}
        Conjugations available: {self._get_available_conjugations()}

        Challenge: Generate search terms for images representing this verb action.
        Visual strategy: {action_strategy}

        Generate search terms that photographers would use to tag images of
        people performing this action or demonstrating this concept.
        """

    def _get_action_visualization_strategy(self) -> str:
        """Get action-focused visualization strategy for verb concepts.

        Returns:
            Strategic guidance for visualizing verb actions based on German
            verb semantics and common usage patterns.
        """
        english_lower = self.english.lower()

        # Motion verbs - focus on movement and direction
        motion_verbs = {
            "go",
            "come",
            "walk",
            "run",
            "drive",
            "travel",
            "move",
            "leave",
            "arrive",
            "return",
            "follow",
            "lead",
            "jump",
            "climb",
            "fall",
        }

        # Work/activity verbs - focus on people performing tasks
        work_verbs = {
            "work",
            "study",
            "learn",
            "teach",
            "write",
            "read",
            "cook",
            "clean",
            "build",
            "make",
            "create",
            "fix",
            "help",
            "serve",
            "sell",
            "buy",
        }

        # Communication verbs - focus on social interaction
        communication_verbs = {
            "speak",
            "talk",
            "say",
            "tell",
            "ask",
            "answer",
            "call",
            "listen",
            "explain",
            "discuss",
            "argue",
            "agree",
            "disagree",
        }

        # Emotion/state verbs - use symbolic or contextual representation
        state_verbs = {
            "be",
            "have",
            "feel",
            "think",
            "believe",
            "know",
            "understand",
            "remember",
            "forget",
            "hope",
            "want",
            "need",
            "like",
            "love",
            "hate",
        }

        verb_strategies = [
            (
                motion_verbs,
                "Focus on movement and direction. Show people or objects "
                "in motion, emphasizing movement from one place to another.",
            ),
            (
                work_verbs,
                "Focus on people actively performing the task or activity. "
                "Show clear action shots with visible tools or environment.",
            ),
            (
                communication_verbs,
                "Focus on social interaction and communication. "
                "Show people engaged in conversation or expressing.",
            ),
            (
                state_verbs,
                "Use contextual scenes that imply the mental or emotional "
                "state. Show situations where this feeling would be evident.",
            ),
        ]

        for verb_type, strategy in verb_strategies:
            if any(verb in english_lower for verb in verb_type):
                return strategy

        # Default action-focused strategy
        return (
            "Focus on the physical action being performed. Show people actively "
            "engaged in the activity with clear visual demonstration of concept."
        )

    def _get_available_conjugations(self) -> str:
        """Get summary of available conjugation data for context.

        Returns:
            String describing which tenses and forms are available for this verb.
        """
        conjugations = []

        if self.present_ich or self.present_du or self.present_er:
            conjugations.append("present tense")

        if self.präteritum:
            conjugations.append("preterite")

        if self.perfect:
            conjugations.append("perfect")

        if self.auxiliary:
            conjugations.append(f"auxiliary: {self.auxiliary}")

        return ", ".join(conjugations) if conjugations else "basic forms"
