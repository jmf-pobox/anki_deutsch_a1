"""
Tests for Record types in the Clean Pipeline Architecture.

This module tests the pure data container records that represent structured CSV data.
"""

import pytest

from langlearn.models.records import (
    RECORD_TYPE_REGISTRY,
    AdjectiveRecord,
    AdverbRecord,
    BaseRecord,
    NegationRecord,
    NounRecord,
    create_record,
)


class TestBaseRecord:
    """Test BaseRecord abstract interface."""

    def test_base_record_is_abstract(self):
        """Test that BaseRecord cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseRecord()  # Should raise TypeError for abstract class


class TestNounRecord:
    """Test NounRecord data container."""

    @pytest.fixture
    def sample_noun_fields(self):
        """Sample noun CSV fields."""
        return [
            "Katze",  # noun
            "die",  # article
            "cat",  # english
            "Katzen",  # plural
            "Die Katze ist süß.",  # example
            "Tier, Haustier",  # related
        ]

    def test_noun_record_creation_complete(self, sample_noun_fields):
        """Test creating NounRecord with all fields."""
        record = NounRecord.from_csv_fields(sample_noun_fields)

        assert record.noun == "Katze"
        assert record.article == "die"
        assert record.english == "cat"
        assert record.plural == "Katzen"
        assert record.example == "Die Katze ist süß."
        assert record.related == "Tier, Haustier"

        # Media fields should be None by default
        assert record.image is None
        assert record.word_audio is None
        assert record.example_audio is None

    def test_noun_record_creation_minimal(self):
        """Test creating NounRecord with minimum required fields."""
        fields = ["Hund", "der", "dog", "Hunde", "Der Hund bellt.", ""]
        record = NounRecord.from_csv_fields(fields)

        assert record.noun == "Hund"
        assert record.article == "der"
        assert record.english == "dog"
        assert record.plural == "Hunde"
        assert record.example == "Der Hund bellt."
        assert record.related == ""

    def test_noun_record_insufficient_fields(self):
        """Test NounRecord creation with insufficient fields."""
        fields = ["Katze", "die", "cat"]  # Only 3 fields, need 6

        with pytest.raises(ValueError, match="requires at least 6 fields"):
            NounRecord.from_csv_fields(fields)

    def test_noun_record_whitespace_handling(self):
        """Test that whitespace is stripped from fields."""
        fields = [" Katze ", "  die  ", " cat ", " Katzen ", " Example ", " Related "]
        record = NounRecord.from_csv_fields(fields)

        assert record.noun == "Katze"
        assert record.article == "die"
        assert record.english == "cat"
        assert record.plural == "Katzen"
        assert record.example == "Example"
        assert record.related == "Related"

    def test_noun_record_to_dict(self, sample_noun_fields):
        """Test converting NounRecord to dictionary."""
        record = NounRecord.from_csv_fields(sample_noun_fields)
        record.image = "<img src='cat.jpg'>"
        record.word_audio = "[sound:cat.mp3]"
        record.example_audio = "[sound:example.mp3]"

        result = record.to_dict()

        expected = {
            "noun": "Katze",
            "article": "die",
            "english": "cat",
            "plural": "Katzen",
            "example": "Die Katze ist süß.",
            "related": "Tier, Haustier",
            "image": "<img src='cat.jpg'>",
            "word_audio": "[sound:cat.mp3]",
            "example_audio": "[sound:example.mp3]",
        }
        assert result == expected

    def test_noun_record_field_count(self):
        """Test expected field count for nouns."""
        assert NounRecord.get_expected_field_count() == 6

    def test_noun_record_field_names(self):
        """Test field names for nouns."""
        expected = ["noun", "article", "english", "plural", "example", "related"]
        assert NounRecord.get_field_names() == expected


class TestAdjectiveRecord:
    """Test AdjectiveRecord data container."""

    @pytest.fixture
    def sample_adjective_fields(self):
        """Sample adjective CSV fields."""
        return [
            "schön",  # word
            "beautiful",  # english
            "Das ist schön.",  # example
            "schöner",  # comparative
            "am schönsten",  # superlative
        ]

    def test_adjective_record_creation_complete(self, sample_adjective_fields):
        """Test creating AdjectiveRecord with all fields."""
        record = AdjectiveRecord.from_csv_fields(sample_adjective_fields)

        assert record.word == "schön"
        assert record.english == "beautiful"
        assert record.example == "Das ist schön."
        assert record.comparative == "schöner"
        assert record.superlative == "am schönsten"

        # Media fields should be None by default
        assert record.image is None
        assert record.word_audio is None
        assert record.example_audio is None

    def test_adjective_record_creation_minimal(self):
        """Test creating AdjectiveRecord with minimum required fields."""
        fields = ["gut", "good", "Das ist gut.", "besser"]
        record = AdjectiveRecord.from_csv_fields(fields)

        assert record.word == "gut"
        assert record.english == "good"
        assert record.example == "Das ist gut."
        assert record.comparative == "besser"
        assert record.superlative == ""

    def test_adjective_record_insufficient_fields(self):
        """Test AdjectiveRecord creation with insufficient fields."""
        fields = ["schön", "beautiful"]  # Only 2 fields, need 4

        with pytest.raises(ValueError, match="requires at least 4 fields"):
            AdjectiveRecord.from_csv_fields(fields)

    def test_adjective_record_to_dict(self, sample_adjective_fields):
        """Test converting AdjectiveRecord to dictionary."""
        record = AdjectiveRecord.from_csv_fields(sample_adjective_fields)
        record.image = "<img src='beautiful.jpg'>"

        result = record.to_dict()

        assert result["word"] == "schön"
        assert result["english"] == "beautiful"
        assert result["image"] == "<img src='beautiful.jpg'>"

    def test_adjective_record_field_count(self):
        """Test expected field count for adjectives."""
        assert AdjectiveRecord.get_expected_field_count() == 5

    def test_adjective_record_field_names(self):
        """Test field names for adjectives."""
        expected = ["word", "english", "example", "comparative", "superlative"]
        assert AdjectiveRecord.get_field_names() == expected


class TestAdverbRecord:
    """Test AdverbRecord data container."""

    @pytest.fixture
    def sample_adverb_fields(self):
        """Sample adverb CSV fields."""
        return [
            "hier",  # word
            "here",  # english
            "location",  # type
            "Ich bin hier.",  # example
        ]

    def test_adverb_record_creation(self, sample_adverb_fields):
        """Test creating AdverbRecord."""
        record = AdverbRecord.from_csv_fields(sample_adverb_fields)

        assert record.word == "hier"
        assert record.english == "here"
        assert record.type == "location"
        assert record.example == "Ich bin hier."

        # Media fields should be None by default
        assert record.image is None
        assert record.word_audio is None
        assert record.example_audio is None

    def test_adverb_record_insufficient_fields(self):
        """Test AdverbRecord creation with insufficient fields."""
        fields = ["hier", "here"]  # Only 2 fields, need 4

        with pytest.raises(ValueError, match="requires at least 4 fields"):
            AdverbRecord.from_csv_fields(fields)

    def test_adverb_record_to_dict(self, sample_adverb_fields):
        """Test converting AdverbRecord to dictionary."""
        record = AdverbRecord.from_csv_fields(sample_adverb_fields)

        result = record.to_dict()

        expected = {
            "word": "hier",
            "english": "here",
            "type": "location",
            "example": "Ich bin hier.",
            "image": None,
            "word_audio": None,
            "example_audio": None,
        }
        assert result == expected

    def test_adverb_record_field_count(self):
        """Test expected field count for adverbs."""
        assert AdverbRecord.get_expected_field_count() == 4

    def test_adverb_record_field_names(self):
        """Test field names for adverbs."""
        expected = ["word", "english", "type", "example"]
        assert AdverbRecord.get_field_names() == expected


class TestNegationRecord:
    """Test NegationRecord data container."""

    @pytest.fixture
    def sample_negation_fields(self):
        """Sample negation CSV fields."""
        return [
            "nicht",  # word
            "not",  # english
            "general",  # type
            "Das ist nicht gut.",  # example
        ]

    def test_negation_record_creation(self, sample_negation_fields):
        """Test creating NegationRecord."""
        record = NegationRecord.from_csv_fields(sample_negation_fields)

        assert record.word == "nicht"
        assert record.english == "not"
        assert record.type == "general"
        assert record.example == "Das ist nicht gut."

        # Media fields should be None by default
        assert record.image is None
        assert record.word_audio is None
        assert record.example_audio is None

    def test_negation_record_insufficient_fields(self):
        """Test NegationRecord creation with insufficient fields."""
        fields = ["nicht", "not"]  # Only 2 fields, need 4

        with pytest.raises(ValueError, match="requires at least 4 fields"):
            NegationRecord.from_csv_fields(fields)

    def test_negation_record_to_dict(self, sample_negation_fields):
        """Test converting NegationRecord to dictionary."""
        record = NegationRecord.from_csv_fields(sample_negation_fields)

        result = record.to_dict()

        expected = {
            "word": "nicht",
            "english": "not",
            "type": "general",
            "example": "Das ist nicht gut.",
            "image": None,
            "word_audio": None,
            "example_audio": None,
        }
        assert result == expected

    def test_negation_record_field_count(self):
        """Test expected field count for negations."""
        assert NegationRecord.get_expected_field_count() == 4

    def test_negation_record_field_names(self):
        """Test field names for negations."""
        expected = ["word", "english", "type", "example"]
        assert NegationRecord.get_field_names() == expected


class TestRecordTypeRegistry:
    """Test record type registry and factory function."""

    def test_registry_contains_all_types(self):
        """Test that registry contains all expected record types."""
        expected_types = {"noun", "adjective", "adverb", "negation"}
        assert set(RECORD_TYPE_REGISTRY.keys()) == expected_types

        assert RECORD_TYPE_REGISTRY["noun"] == NounRecord
        assert RECORD_TYPE_REGISTRY["adjective"] == AdjectiveRecord
        assert RECORD_TYPE_REGISTRY["adverb"] == AdverbRecord
        assert RECORD_TYPE_REGISTRY["negation"] == NegationRecord

    def test_create_record_noun(self):
        """Test creating noun record via factory function."""
        fields = ["Katze", "die", "cat", "Katzen", "Example", "Related"]
        record = create_record("noun", fields)

        assert isinstance(record, NounRecord)
        assert record.noun == "Katze"
        assert record.article == "die"

    def test_create_record_adjective(self):
        """Test creating adjective record via factory function."""
        fields = ["schön", "beautiful", "Example", "schöner", "am schönsten"]
        record = create_record("adjective", fields)

        assert isinstance(record, AdjectiveRecord)
        assert record.word == "schön"
        assert record.english == "beautiful"

    def test_create_record_adverb(self):
        """Test creating adverb record via factory function."""
        fields = ["hier", "here", "location", "Example"]
        record = create_record("adverb", fields)

        assert isinstance(record, AdverbRecord)
        assert record.word == "hier"
        assert record.type == "location"

    def test_create_record_negation(self):
        """Test creating negation record via factory function."""
        fields = ["nicht", "not", "general", "Example"]
        record = create_record("negation", fields)

        assert isinstance(record, NegationRecord)
        assert record.word == "nicht"
        assert record.type == "general"

    def test_create_record_unknown_type(self):
        """Test creating record with unknown type."""
        fields = ["test", "test"]

        with pytest.raises(ValueError, match="Unknown model type: unknown"):
            create_record("unknown", fields)

    def test_create_record_invalid_fields(self):
        """Test creating record with invalid fields."""
        fields = ["insufficient"]

        with pytest.raises(ValueError, match="requires at least"):
            create_record("noun", fields)


class TestRecordDataIntegrity:
    """Test record data integrity and validation."""

    def test_pydantic_validation_noun(self):
        """Test Pydantic validation for noun records."""
        # Test with valid data
        record = NounRecord(
            noun="Test",
            article="der",
            english="test",
            plural="Tests",
            example="Example",
            related="Related",
        )
        assert record.noun == "Test"

        # Test with missing required field (Pydantic allows empty strings)
        # So we test missing field instead
        with pytest.raises(ValueError):
            NounRecord(
                # noun missing - should fail
                article="der",
                english="test",
                plural="Tests",
                example="Example",
            )

    def test_record_immutability(self):
        """Test that records can be modified after creation (they're not frozen)."""
        fields = ["Katze", "die", "cat", "Katzen", "Example", "Related"]
        record = create_record("noun", fields)

        # Should be able to modify media fields after creation
        record.image = "<img src='test.jpg'>"
        record.word_audio = "[sound:test.mp3]"

        assert record.image == "<img src='test.jpg'>"
        assert record.word_audio == "[sound:test.mp3]"

    def test_record_serialization(self):
        """Test that records can be serialized to JSON."""
        fields = ["schön", "beautiful", "Example", "schöner", "am schönsten"]
        record = create_record("adjective", fields)

        # Should be serializable
        json_data = record.model_dump()
        assert json_data["word"] == "schön"
        assert json_data["english"] == "beautiful"

        # Should be deserializable
        new_record = AdjectiveRecord(**json_data)
        assert new_record.word == record.word
        assert new_record.english == record.english
