"""German language service for context-aware processing and text generation."""

import re
from typing import Protocol

from langlearn.models.adjective import Adjective
from langlearn.models.noun import Noun


class GermanWordModel(Protocol):
    """Protocol for German word models."""

    word: str
    english: str


class GermanNounModel(Protocol):
    """Protocol for German noun models."""

    noun: str
    article: str
    plural: str
    english: str


class GermanLanguageService:
    """Handles German-specific language patterns and context extraction.

    This service encapsulates German grammar rules, context analysis,
    and text generation for audio and image search queries.
    """

    def extract_context_from_sentence(
        self, sentence: str, word: str, english_word: str
    ) -> str:
        """Extract context from German example sentence to create better
        image search query.

        This method analyzes German sentence patterns to create more relevant
        image search queries that consider the linguistic and semantic context.

        Args:
            sentence: German example sentence
            word: German word being illustrated
            english_word: English translation of the word

        Returns:
            Enhanced search query with context
        """
        if not sentence:
            return english_word

        # Convert to lowercase for analysis
        sentence_lower = sentence.lower()

        # Common German context patterns that improve image relevance
        context_patterns = {
            # People and actions
            r"(er|sie|mann|frau|kind|junge|mädchen).*"
            r"(ist|geht|arbeitet|spielt|läuft|sitzt|steht|kauft|liest)": "person",
            r"(ich|du|wir).*(bin|bist|sind|gehe|arbeite|spiele|laufe|sitze|steht"
            r"e|kaufe|lese)": "person",
            # Locations and settings
            r"(im|in der|in einem|auf dem|am).*"
            r"(park|haus|küche|zimmer|büro|schule|restaurant|café)": "location",
            r"(zu|zur|nach).*(hause|arbeit|schule|stadt)": "location",
            # Objects and their contexts
            r"(das|ein|eine).*(haus|auto|buch|telefon|computer).*ist": "object",
            r"(steht|liegt|hängt).*(im|in der|auf dem|an der)": "object_placement",
            # Activities and states
            r"(spielt|arbeitet|kocht|isst|trinkt|schläft|lernt)": "activity",
            r"(sehr|zu).*(groß|klein|alt|jung|schön|hässlich)": "descriptor",
            # Weather and nature
            r"(wetter|sonne|regen|schnee|wind)": "weather",
            r"(baum|blume|tier|hund|katze)": "nature",
            # Food and eating
            r"(essen|trinken|brot|kaffee|wasser).*schmeckt": "food",
            # Time contexts
            r"(heute|morgen|gestern|immer|oft|nie)": "time",
        }

        # Extract key context words from the sentence
        context_type = None
        for pattern, ctx_type in context_patterns.items():
            if re.search(pattern, sentence_lower):
                context_type = ctx_type
                break

        # Create enhanced search queries based on context and word type
        if context_type == "person":
            return self._enhance_person_context(word, english_word, sentence_lower)

        elif context_type == "activity":
            return self._enhance_activity_context(word, english_word, sentence_lower)

        elif context_type == "location":
            return self._enhance_location_context(word, english_word, sentence_lower)

        elif context_type == "object":
            return self._enhance_object_context(word, english_word, sentence_lower)

        elif context_type == "food":
            return self._enhance_food_context(english_word)

        elif context_type == "weather":
            return self._enhance_weather_context(word, english_word, sentence_lower)

        elif context_type == "nature":
            return self._enhance_nature_context(word, english_word, sentence_lower)

        # Special handling for specific word + context combinations
        return self._enhance_specific_combinations(word, english_word, sentence_lower)

    def _enhance_person_context(
        self, word: str, english_word: str, sentence_lower: str
    ) -> str:
        """Enhance search query for person-related contexts."""
        if "tall" in english_word or "groß" in word:
            return "tall person man"
        elif "young" in english_word or "jung" in word:
            return "young person"
        elif "old" in english_word or "alt" in word:
            return "elderly person senior"
        elif "beautiful" in english_word or "schön" in word:
            return "beautiful person"
        elif "happy" in english_word or "glücklich" in word:
            return "happy person smiling"
        elif "sad" in english_word or "traurig" in word:
            return "sad person"
        else:
            return f"{english_word} person"

    def _enhance_activity_context(
        self, word: str, english_word: str, sentence_lower: str
    ) -> str:
        """Enhance search query for activity-related contexts."""
        if "child" in english_word or "kind" in word:
            if "spielt" in sentence_lower:
                return "child playing playground"
            elif "lernt" in sentence_lower:
                return "child learning studying"
        elif "man" in english_word or "mann" in word:
            if "arbeitet" in sentence_lower:
                return "man working office business"
            elif "geht" in sentence_lower:
                return "man walking"
        elif "woman" in english_word or "frau" in word:
            if "kauft" in sentence_lower:
                return "woman shopping"
            elif "kocht" in sentence_lower:
                return "woman cooking kitchen"
        return f"{english_word} activity"

    def _enhance_location_context(
        self, word: str, english_word: str, sentence_lower: str
    ) -> str:
        """Enhance search query for location-related contexts."""
        if "house" in english_word or "haus" in word:
            if "klein" in sentence_lower:
                return "small house home"
            elif "groß" in sentence_lower:
                return "big house large home"
        elif "kitchen" in english_word or "küche" in word:
            return "modern kitchen"
        elif "park" in sentence_lower:
            return f"{english_word} park outdoor"
        return f"{english_word} indoor location"

    def _enhance_object_context(
        self, word: str, english_word: str, sentence_lower: str
    ) -> str:
        """Enhance search query for object-related contexts."""
        if "table" in english_word and "küche" in sentence_lower:
            return "kitchen table"
        elif "chair" in english_word:
            return "comfortable chair furniture"
        elif "car" in english_word and "neu" in sentence_lower:
            return "new car automobile"
        elif "book" in english_word and "interessant" in sentence_lower:
            return "interesting book reading"
        return f"{english_word} object"

    def _enhance_food_context(self, english_word: str) -> str:
        """Enhance search query for food-related contexts."""
        if "bread" in english_word:
            return "fresh bread bakery"
        elif "coffee" in english_word:
            return "coffee cup hot drink"
        elif "water" in english_word:
            return "glass of water drink"
        return f"{english_word} food"

    def _enhance_weather_context(
        self, word: str, english_word: str, sentence_lower: str
    ) -> str:
        """Enhance search query for weather-related contexts."""
        if "weather" in english_word and "schön" in sentence_lower:
            return "beautiful sunny weather"
        elif "weather" in english_word and "schlecht" in sentence_lower:
            return "bad rainy weather storm"
        elif "sun" in english_word:
            return "bright sun sunshine"
        elif "rain" in english_word:
            return "rain drops weather"
        return f"{english_word} weather"

    def _enhance_nature_context(
        self, word: str, english_word: str, sentence_lower: str
    ) -> str:
        """Enhance search query for nature-related contexts."""
        if "flower" in english_word and "schön" in sentence_lower:
            return "beautiful flower garden"
        elif "tree" in english_word and "groß" in sentence_lower:
            return "big tree tall oak"
        elif "dog" in english_word:
            return "friendly dog pet"
        elif "cat" in english_word:
            return "cute cat pet"
        return f"{english_word} nature"

    def _enhance_specific_combinations(
        self, word: str, english_word: str, sentence_lower: str
    ) -> str:
        """Handle special combinations of words and contexts."""
        # Special handling for specific word + context combinations
        if "blume" in sentence_lower and "beautiful" in english_word:
            return "beautiful flower garden"
        elif "haus" in sentence_lower and "klein" in sentence_lower:
            return "small house home cozy"
        elif "haus" in sentence_lower and ("alt" in word or "old" in english_word):
            return "old historic house building"
        elif "arbeitet" in sentence_lower or "arbeit" in sentence_lower:
            if "man" in english_word:
                return "businessman working office professional"
            elif "woman" in english_word:
                return "businesswoman working office professional"
        elif "spielt" in sentence_lower and "park" in sentence_lower:
            if "child" in english_word:
                return "child playing playground park outdoor"
        elif "kauft" in sentence_lower and "buch" in sentence_lower:
            if "woman" in english_word:
                return "woman reading bookstore shopping"
        elif "buch" in sentence_lower and "liest" in sentence_lower:
            return "person reading book library"
        elif "sehr" in sentence_lower and ("groß" in word or "tall" in english_word):
            return "very tall person height"
        elif "sehr" in sentence_lower and ("klein" in word or "small" in english_word):
            return "very small tiny object"

        # Fallback to enhanced basic search
        return english_word

    def get_combined_adjective_audio_text(self, adjective: Adjective) -> str:
        """Generate text for combined adjective forms audio.

        Args:
            adjective: Adjective model with base, comparative, and superlative forms

        Returns:
            Combined text for audio generation
        """
        parts = [adjective.word]
        if adjective.comparative:
            parts.append(adjective.comparative)
        if adjective.superlative:
            parts.append(adjective.superlative)
        return ", ".join(parts)

    def get_combined_noun_audio_text(self, noun: Noun) -> str:
        """Generate text for combined noun audio (article + noun + plural).

        Args:
            noun: Noun model with article, noun, and plural forms

        Returns:
            Combined text for audio generation
        """
        # Check if plural already includes article
        if noun.plural.startswith(("der ", "die ", "das ")):
            return f"{noun.article} {noun.noun}, {noun.plural}"
        else:
            return f"{noun.article} {noun.noun}, die {noun.plural}"

    def get_conceptual_image_search_terms(
        self, word_type: str, word: str, english: str
    ) -> str:
        """Generate conceptual search terms for abstract words.

        Used for adverbs, negations, and other abstract concepts that need
        visual representation through related concrete imagery.

        Args:
            word_type: Type of word (adverb, negation, etc.)
            word: German word
            english: English translation

        Returns:
            Search terms for conceptual imagery
        """
        if word_type == "adverb":
            return self._get_adverb_search_terms(word, english)
        elif word_type == "negation":
            return self._get_negation_search_terms(word, english)
        else:
            return english

    def _get_adverb_search_terms(self, word: str, english: str) -> str:
        """Generate search terms for adverb concepts."""
        # Time adverbs
        if word in ["heute", "morgen", "gestern", "jetzt", "später", "früh", "spät"]:
            if "today" in english:
                return "calendar today date"
            elif "tomorrow" in english:
                return "calendar tomorrow future"
            elif "yesterday" in english:
                return "calendar yesterday past"
            elif "now" in english:
                return "clock time now present"
            elif "early" in english:
                return "sunrise early morning"
            elif "late" in english:
                return "sunset late evening"

        # Manner adverbs
        if word in ["schnell", "langsam", "gut", "schlecht", "gern"]:
            if "fast" in english or "quickly" in english:
                return "speed fast motion blur"
            elif "slow" in english or "slowly" in english:
                return "slow motion turtle snail"
            elif "well" in english or "good" in english:
                return "thumbs up good quality"
            elif "bad" in english or "badly" in english:
                return "thumbs down bad quality"

        # Frequency adverbs
        if word in ["oft", "manchmal", "nie", "immer", "selten"]:
            if "often" in english or "frequently" in english:
                return "repeat pattern frequency"
            elif "sometimes" in english:
                return "maybe question uncertain"
            elif "never" in english:
                return "prohibition stop sign never"
            elif "always" in english:
                return "infinity always continuous"

        return f"{english} concept abstract"

    def _get_negation_search_terms(self, word: str, english: str) -> str:
        """Generate search terms for negation concepts."""
        if word in ["nicht", "kein", "keine"]:
            if "not" in english or "no" in english:
                return "stop sign prohibition no red"
        elif word in ["niemand", "nichts"] and (
            "nobody" in english or "nothing" in english
        ):
            return "empty void nothing zero"

        return f"prohibition stop {english} negative"

    def is_concrete_noun(self, noun_str: str) -> bool:
        """Determine if a German noun represents a concrete object.

        DEPRECATED: Use Noun.is_concrete() method directly when you have a Noun model.
        This method is kept for backward compatibility during refactoring.

        Args:
            noun_str: German noun string to evaluate

        Returns:
            True if the noun likely represents a concrete object
        """
        # For backward compatibility, create a temporary Noun model
        # In practice, callers should use the Noun.is_concrete() method directly
        from langlearn.models.noun import Noun

        # Create minimal noun for classification
        temp_noun = Noun(
            noun=noun_str,
            article="der",  # Placeholder - not used for classification
            english="",  # Placeholder - not used for classification
            plural="",  # Placeholder - not used for classification
            example="",  # Placeholder - not used for classification
            word_audio="",
            example_audio="",
            image_path="",
        )
        return temp_noun.is_concrete()
