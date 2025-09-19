"""Tests for NamingService."""

from langlearn.core.records.base_record import RecordType
from langlearn.infrastructure.services.naming_service import NamingService
from langlearn.languages.german.records.noun_record import NounRecord


class TestNamingService:
    """Test the NamingService for consistent naming conventions."""

    def test_get_subdeck_name_with_record_instance(self) -> None:
        """Test subdeck name generation with BaseRecord instance."""
        record = NounRecord(
            noun="Haus",
            english="house",
            article="das",
            plural="Häuser",
            example="Das Haus ist groß.",
        )
        result = NamingService.get_subdeck_name(record)
        assert result == "Nouns"

    def test_get_subdeck_name_with_record_type_enum(self) -> None:
        """Test subdeck name generation with RecordType enum."""
        # Test various record types
        assert NamingService.get_subdeck_name(RecordType.NOUN) == "Nouns"
        assert NamingService.get_subdeck_name(RecordType.VERB) == "Verbs"
        assert NamingService.get_subdeck_name(RecordType.VERB_CONJUGATION) == "Verbs"
        assert NamingService.get_subdeck_name(RecordType.VERB_IMPERATIVE) == "Verbs"
        assert NamingService.get_subdeck_name(RecordType.ADJECTIVE) == "Adjectives"
        assert NamingService.get_subdeck_name(RecordType.ADVERB) == "Adverbs"
        assert NamingService.get_subdeck_name(RecordType.PREPOSITION) == "Prepositions"
        assert NamingService.get_subdeck_name(RecordType.PHRASE) == "Phrases"
        assert NamingService.get_subdeck_name(RecordType.NEGATION) == "Negations"
        assert NamingService.get_subdeck_name(RecordType.UNIFIED_ARTICLE) == "Articles"
        assert NamingService.get_subdeck_name(RecordType.ARTICLE) == "Articles"
        assert (
            NamingService.get_subdeck_name(RecordType.INDEFINITE_ARTICLE) == "Articles"
        )
        assert NamingService.get_subdeck_name(RecordType.NEGATIVE_ARTICLE) == "Articles"
        assert NamingService.get_subdeck_name(RecordType.KOREAN_NOUN) == "Nouns"

    def test_get_subdeck_name_with_string_fallback(self) -> None:
        """Test subdeck name generation with string fallback."""
        # Test string input
        assert NamingService.get_subdeck_name("noun") == "Nouns"
        assert NamingService.get_subdeck_name("verb_conjugation") == "Verb Conjugations"
        assert NamingService.get_subdeck_name("custom_type") == "Custom Types"

        # Test string that already ends with 's'
        assert NamingService.get_subdeck_name("words") == "Words"

    def test_get_result_key_with_record_instance(self) -> None:
        """Test result key generation with BaseRecord instance."""
        record = NounRecord(
            noun="Haus",
            english="house",
            article="das",
            plural="Häuser",
            example="Das Haus ist groß.",
        )
        result = NamingService.get_result_key(record)
        assert result == "nouns"

    def test_get_result_key_with_record_type_enum(self) -> None:
        """Test result key generation with RecordType enum."""
        # Test various record types
        assert NamingService.get_result_key(RecordType.NOUN) == "nouns"
        assert NamingService.get_result_key(RecordType.VERB) == "verbs"
        assert NamingService.get_result_key(RecordType.VERB_CONJUGATION) == "verbs"
        assert NamingService.get_result_key(RecordType.VERB_IMPERATIVE) == "verbs"
        assert NamingService.get_result_key(RecordType.ADJECTIVE) == "adjectives"
        assert NamingService.get_result_key(RecordType.ADVERB) == "adverbs"
        assert NamingService.get_result_key(RecordType.PREPOSITION) == "prepositions"
        assert NamingService.get_result_key(RecordType.PHRASE) == "phrases"
        assert NamingService.get_result_key(RecordType.NEGATION) == "negations"
        assert NamingService.get_result_key(RecordType.UNIFIED_ARTICLE) == "articles"
        assert NamingService.get_result_key(RecordType.ARTICLE) == "articles"
        assert NamingService.get_result_key(RecordType.INDEFINITE_ARTICLE) == "articles"
        assert NamingService.get_result_key(RecordType.NEGATIVE_ARTICLE) == "articles"
        assert NamingService.get_result_key(RecordType.KOREAN_NOUN) == "nouns"

    def test_get_result_key_with_string_fallback(self) -> None:
        """Test result key generation with string fallback."""
        # Test string input
        assert NamingService.get_result_key("noun") == "nouns"
        assert NamingService.get_result_key("verb_conjugation") == "verbconjugations"
        assert NamingService.get_result_key("custom_type") == "customtypes"

    def test_get_display_name_with_record_instance(self) -> None:
        """Test display name generation with BaseRecord instance."""
        record = NounRecord(
            noun="Haus",
            english="house",
            article="das",
            plural="Häuser",
            example="Das Haus ist groß.",
        )
        result = NamingService.get_display_name(record)
        assert result == "Noun"

    def test_get_display_name_with_record_type_enum(self) -> None:
        """Test display name generation with RecordType enum."""
        # Test various record types
        assert NamingService.get_display_name(RecordType.NOUN) == "Noun"
        assert NamingService.get_display_name(RecordType.VERB) == "Verb"
        assert (
            NamingService.get_display_name(RecordType.VERB_CONJUGATION)
            == "Verb Conjugation"
        )
        assert (
            NamingService.get_display_name(RecordType.VERB_IMPERATIVE)
            == "Verb Imperative"
        )
        assert NamingService.get_display_name(RecordType.ADJECTIVE) == "Adjective"
        assert NamingService.get_display_name(RecordType.ADVERB) == "Adverbs"
        assert NamingService.get_display_name(RecordType.PREPOSITION) == "Preposition"
        assert NamingService.get_display_name(RecordType.PHRASE) == "Phrase"
        assert NamingService.get_display_name(RecordType.NEGATION) == "Negation"
        assert (
            NamingService.get_display_name(RecordType.UNIFIED_ARTICLE)
            == "Unified Article"
        )
        assert NamingService.get_display_name(RecordType.ARTICLE) == "Article"
        assert (
            NamingService.get_display_name(RecordType.INDEFINITE_ARTICLE)
            == "Indefinite Article"
        )
        assert (
            NamingService.get_display_name(RecordType.NEGATIVE_ARTICLE)
            == "Negative Article"
        )
        assert NamingService.get_display_name(RecordType.KOREAN_NOUN) == "Noun"

    def test_get_display_name_with_string_fallback(self) -> None:
        """Test display name generation with string fallback."""
        # Test string input
        assert NamingService.get_display_name("noun") == "Noun"
        assert NamingService.get_display_name("verb_conjugation") == "Verb Conjugation"
        assert NamingService.get_display_name("custom_type") == "Custom Type"

    def test_get_record_type_from_string_direct_match(self) -> None:
        """Test direct string to RecordType conversion."""
        # Test direct matches
        assert NamingService.get_record_type_from_string("noun") == RecordType.NOUN
        assert NamingService.get_record_type_from_string("verb") == RecordType.VERB
        assert (
            NamingService.get_record_type_from_string("verb_conjugation")
            == RecordType.VERB_CONJUGATION
        )
        assert (
            NamingService.get_record_type_from_string("adjective")
            == RecordType.ADJECTIVE
        )

    def test_get_record_type_from_string_normalized_match(self) -> None:
        """Test normalized string to RecordType conversion."""
        # Test normalized matches (with dashes and spaces)
        assert (
            NamingService.get_record_type_from_string("verb-conjugation")
            == RecordType.VERB_CONJUGATION
        )
        assert (
            NamingService.get_record_type_from_string("verb conjugation")
            == RecordType.VERB_CONJUGATION
        )
        assert (
            NamingService.get_record_type_from_string("unified-article")
            == RecordType.UNIFIED_ARTICLE
        )
        assert (
            NamingService.get_record_type_from_string("unified article")
            == RecordType.UNIFIED_ARTICLE
        )

    def test_get_record_type_from_string_case_insensitive(self) -> None:
        """Test case-insensitive string to RecordType conversion."""
        # Test case insensitive
        assert NamingService.get_record_type_from_string("NOUN") == RecordType.NOUN
        assert NamingService.get_record_type_from_string("Verb") == RecordType.VERB
        assert (
            NamingService.get_record_type_from_string("ADJECTIVE")
            == RecordType.ADJECTIVE
        )

    def test_get_record_type_from_string_not_found(self) -> None:
        """Test string to RecordType conversion when no match found."""
        # Test no match
        assert NamingService.get_record_type_from_string("unknown_type") is None
        assert NamingService.get_record_type_from_string("") is None
        assert NamingService.get_record_type_from_string("invalid") is None

    def test_comprehensive_coverage_all_methods(self) -> None:
        """Comprehensive test to ensure full coverage of all methods."""
        # Test edge cases and remaining branches

        # Test empty string handling
        assert NamingService.get_record_type_from_string("") is None

        # Test case-insensitive normalized matching
        assert (
            NamingService.get_record_type_from_string("VERB-CONJUGATION")
            == RecordType.VERB_CONJUGATION
        )
        assert (
            NamingService.get_record_type_from_string("Unified Article")
            == RecordType.UNIFIED_ARTICLE
        )

        # Test string fallback edge cases
        assert NamingService.get_subdeck_name("test") == "Tests"
        assert NamingService.get_result_key("test_item") == "testitems"
        assert NamingService.get_display_name("test_item") == "Test Item"
