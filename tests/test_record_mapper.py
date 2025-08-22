"""Tests for RecordMapper service.

This module tests the RecordMapper service that converts CSV field arrays
to Record instances in the Clean Pipeline Architecture.
"""

from pathlib import Path

import pytest

from langlearn.models.records import (
    AdjectiveRecord,
    AdverbRecord,
    NegationRecord,
    NounRecord,
)
from langlearn.services.record_mapper import RecordMapper


class TestRecordMapper:
    """Test RecordMapper functionality."""

    @pytest.fixture
    def record_mapper(self) -> RecordMapper:
        """Create RecordMapper instance for testing."""
        return RecordMapper()

    def test_record_mapper_initialization(self) -> None:
        """Test RecordMapper initialization."""
        mapper = RecordMapper()
        assert mapper is not None

        # Test with custom project root
        custom_root = Path("/custom/path")
        mapper_with_root = RecordMapper(custom_root)
        assert mapper_with_root._project_root == custom_root

    def test_map_fields_to_record_noun(self, record_mapper: RecordMapper) -> None:
        """Test mapping fields to noun record."""
        fields = ["Katze", "die", "cat", "Katzen", "Die Katze ist süß.", "Tier"]

        record = record_mapper.map_fields_to_record("noun", fields)

        assert isinstance(record, NounRecord)
        assert record.noun == "Katze"
        assert record.article == "die"
        assert record.english == "cat"
        assert record.plural == "Katzen"
        assert record.example == "Die Katze ist süß."
        assert record.related == "Tier"

    def test_map_fields_to_record_adjective(self, record_mapper: RecordMapper) -> None:
        """Test mapping fields to adjective record."""
        fields = ["schön", "beautiful", "Das ist schön.", "schöner", "am schönsten"]

        record = record_mapper.map_fields_to_record("adjective", fields)

        assert isinstance(record, AdjectiveRecord)
        assert record.word == "schön"
        assert record.english == "beautiful"
        assert record.example == "Das ist schön."
        assert record.comparative == "schöner"
        assert record.superlative == "am schönsten"

    def test_map_fields_to_record_adverb(self, record_mapper: RecordMapper) -> None:
        """Test mapping fields to adverb record."""
        fields = ["hier", "here", "location", "Ich bin hier."]

        record = record_mapper.map_fields_to_record("adverb", fields)

        assert isinstance(record, AdverbRecord)
        assert record.word == "hier"
        assert record.english == "here"
        assert record.type == "location"
        assert record.example == "Ich bin hier."

    def test_map_fields_to_record_negation(self, record_mapper: RecordMapper) -> None:
        """Test mapping fields to negation record."""
        fields = ["nicht", "not", "general", "Das ist nicht gut."]

        record = record_mapper.map_fields_to_record("negation", fields)

        assert isinstance(record, NegationRecord)
        assert record.word == "nicht"
        assert record.english == "not"
        assert record.type == "general"
        assert record.example == "Das ist nicht gut."

    def test_map_fields_to_record_unsupported_type(
        self, record_mapper: RecordMapper
    ) -> None:
        """Test mapping fields with unsupported record type."""
        fields = ["test", "test", "test"]

        with pytest.raises(ValueError, match="Unknown model type: unknown"):
            record_mapper.map_fields_to_record("unknown", fields)

    def test_map_fields_to_record_insufficient_fields(
        self, record_mapper: RecordMapper
    ) -> None:
        """Test mapping with insufficient fields."""
        fields = ["insufficient"]  # Not enough fields for any record type

        with pytest.raises(ValueError, match="requires at least"):
            record_mapper.map_fields_to_record("noun", fields)

    def test_map_csv_row_to_record_noun(self, record_mapper: RecordMapper) -> None:
        """Test mapping CSV row dictionary to noun record."""
        csv_row = {
            "noun": "Hund",
            "article": "der",
            "english": "dog",
            "plural": "Hunde",
            "example": "Der Hund bellt.",
            "related": "Tier",
        }

        record = record_mapper.map_csv_row_to_record("noun", csv_row)

        assert isinstance(record, NounRecord)
        assert record.noun == "Hund"
        assert record.article == "der"
        assert record.english == "dog"

    def test_map_csv_row_to_record_adjective(self, record_mapper: RecordMapper) -> None:
        """Test mapping CSV row dictionary to adjective record."""
        csv_row = {
            "word": "gut",
            "english": "good",
            "example": "Das ist gut.",
            "comparative": "besser",
            "superlative": "am besten",
        }

        record = record_mapper.map_csv_row_to_record("adjective", csv_row)

        assert isinstance(record, AdjectiveRecord)
        assert record.word == "gut"
        assert record.english == "good"
        assert record.comparative == "besser"

    def test_map_csv_row_to_record_adverb(self, record_mapper: RecordMapper) -> None:
        """Test mapping CSV row dictionary to adverb record."""
        csv_row = {
            "word": "oft",
            "english": "often",
            "type": "frequency",
            "example": "Ich komme oft hier.",
        }

        record = record_mapper.map_csv_row_to_record("adverb", csv_row)

        assert isinstance(record, AdverbRecord)
        assert record.word == "oft"
        assert record.type == "frequency"

    def test_map_csv_row_to_record_negation(self, record_mapper: RecordMapper) -> None:
        """Test mapping CSV row dictionary to negation record."""
        csv_row = {
            "word": "niemals",
            "english": "never",
            "type": "temporal",
            "example": "Das werde ich niemals tun.",
        }

        record = record_mapper.map_csv_row_to_record("negation", csv_row)

        assert isinstance(record, NegationRecord)
        assert record.word == "niemals"
        assert record.type == "temporal"

    def test_map_csv_row_missing_fields(self, record_mapper: RecordMapper) -> None:
        """Test mapping CSV row with missing fields uses empty strings."""
        csv_row = {
            "word": "langsam",
            "english": "slowly",
            # Missing 'type' and 'example' fields
        }

        record = record_mapper.map_csv_row_to_record("adverb", csv_row)

        assert isinstance(record, AdverbRecord)
        assert record.word == "langsam"
        assert record.english == "slowly"
        assert record.type == ""  # Missing field becomes empty string
        assert record.example == ""  # Missing field becomes empty string

    def test_map_csv_row_unsupported_type(self, record_mapper: RecordMapper) -> None:
        """Test mapping CSV row with unsupported record type."""
        csv_row = {"field": "value"}

        with pytest.raises(ValueError, match="Unsupported record type: unknown"):
            record_mapper.map_csv_row_to_record("unknown", csv_row)

    def test_get_supported_record_types(self, record_mapper: RecordMapper) -> None:
        """Test getting supported record types."""
        types = record_mapper.get_supported_record_types()

        expected_types = {
            "noun",
            "adjective",
            "adverb",
            "negation",
            "verb",
            "preposition",
            "phrase",
            "verb_conjugation",
            "verb_imperative",
            "article",
            "indefinite_article",
            "negative_article",
        }
        assert set(types) == expected_types

    def test_is_supported_record_type(self, record_mapper: RecordMapper) -> None:
        """Test checking if record type is supported."""
        assert record_mapper.is_supported_record_type("noun") is True
        assert record_mapper.is_supported_record_type("adjective") is True
        assert record_mapper.is_supported_record_type("adverb") is True
        assert record_mapper.is_supported_record_type("negation") is True
        assert record_mapper.is_supported_record_type("verb") is True
        assert record_mapper.is_supported_record_type("preposition") is True
        assert record_mapper.is_supported_record_type("phrase") is True
        assert record_mapper.is_supported_record_type("verb_conjugation") is True
        assert record_mapper.is_supported_record_type("verb_imperative") is True

        assert record_mapper.is_supported_record_type("unknown") is False
        assert record_mapper.is_supported_record_type("") is False

    def test_validate_fields_for_record_type_valid(
        self, record_mapper: RecordMapper
    ) -> None:
        """Test field validation for valid fields."""
        # Valid noun fields
        noun_fields = ["Katze", "die", "cat", "Katzen", "Example", "Related"]
        assert (
            record_mapper.validate_fields_for_record_type("noun", noun_fields) is True
        )

        # Valid adjective fields
        adj_fields = ["schön", "beautiful", "Example", "schöner", "am schönsten"]
        assert (
            record_mapper.validate_fields_for_record_type("adjective", adj_fields)
            is True
        )

    def test_validate_fields_for_record_type_invalid(
        self, record_mapper: RecordMapper
    ) -> None:
        """Test field validation for invalid fields."""
        # Too few fields for noun
        insufficient_fields = ["only", "two"]
        assert (
            record_mapper.validate_fields_for_record_type("noun", insufficient_fields)
            is False
        )

    def test_validate_fields_unsupported_type(
        self, record_mapper: RecordMapper
    ) -> None:
        """Test field validation with unsupported record type."""
        fields = ["test", "fields"]

        with pytest.raises(ValueError, match="Unsupported record type: unknown"):
            record_mapper.validate_fields_for_record_type("unknown", fields)

    def test_get_field_names_for_record_type(self, record_mapper: RecordMapper) -> None:
        """Test getting field names for record types."""
        noun_fields = record_mapper.get_field_names_for_record_type("noun")
        expected_noun = ["noun", "article", "english", "plural", "example", "related"]
        assert noun_fields == expected_noun

        adj_fields = record_mapper.get_field_names_for_record_type("adjective")
        expected_adj = ["word", "english", "example", "comparative", "superlative"]
        assert adj_fields == expected_adj

        adverb_fields = record_mapper.get_field_names_for_record_type("adverb")
        expected_adverb = ["word", "english", "type", "example"]
        assert adverb_fields == expected_adverb

    def test_get_field_names_unsupported_type(
        self, record_mapper: RecordMapper
    ) -> None:
        """Test getting field names for unsupported type."""
        with pytest.raises(ValueError, match="Unsupported record type: unknown"):
            record_mapper.get_field_names_for_record_type("unknown")

    def test_get_expected_field_count_for_record_type(
        self, record_mapper: RecordMapper
    ) -> None:
        """Test getting expected field count for record types."""
        assert record_mapper.get_expected_field_count_for_record_type("noun") == 6
        assert record_mapper.get_expected_field_count_for_record_type("adjective") == 5
        assert record_mapper.get_expected_field_count_for_record_type("adverb") == 4
        assert record_mapper.get_expected_field_count_for_record_type("negation") == 4

    def test_get_expected_field_count_unsupported_type(
        self, record_mapper: RecordMapper
    ) -> None:
        """Test getting field count for unsupported type."""
        with pytest.raises(ValueError, match="Unsupported record type: unknown"):
            record_mapper.get_expected_field_count_for_record_type("unknown")


class TestRecordMapperIntegration:
    """Test RecordMapper integration scenarios."""

    def test_complete_csv_processing_workflow(self) -> None:
        """Test complete workflow from CSV row to Record."""
        mapper = RecordMapper()

        # Simulate CSV rows for different record types
        test_cases = [
            (
                "noun",
                {
                    "noun": "Buch",
                    "article": "das",
                    "english": "book",
                    "plural": "Bücher",
                    "example": "Das Buch ist interessant.",
                    "related": "Literatur",
                },
            ),
            (
                "adjective",
                {
                    "word": "groß",
                    "english": "big",
                    "example": "Er ist groß.",
                    "comparative": "größer",
                    "superlative": "am größten",
                },
            ),
            (
                "adverb",
                {
                    "word": "schnell",
                    "english": "quickly",
                    "type": "manner",
                    "example": "Er läuft schnell.",
                },
            ),
            (
                "negation",
                {
                    "word": "kein",
                    "english": "no",
                    "type": "article",
                    "example": "Ich habe kein Auto.",
                },
            ),
        ]

        for record_type, csv_row in test_cases:
            # Test CSV row mapping
            record = mapper.map_csv_row_to_record(record_type, csv_row)

            # Verify record was created successfully
            assert record is not None

            # Verify record can be converted to dict
            record_dict = record.to_dict()
            assert isinstance(record_dict, dict)

            # Verify key fields are present
            if record_type == "noun":
                assert record_dict["noun"] == csv_row["noun"]
                assert record_dict["article"] == csv_row["article"]
            else:
                assert record_dict["word"] == csv_row["word"]

            assert record_dict["english"] == csv_row["english"]

    def test_error_handling_and_logging(self) -> None:
        """Test error handling and logging behavior."""
        mapper = RecordMapper()

        # Test various error conditions
        with pytest.raises(ValueError):
            mapper.map_fields_to_record("unknown", ["test"])

        with pytest.raises(ValueError):
            mapper.map_fields_to_record("noun", [])  # Empty fields

        with pytest.raises(ValueError):
            mapper.map_csv_row_to_record("unknown", {"test": "value"})

        # Test validation methods with invalid data
        assert mapper.validate_fields_for_record_type("noun", []) is False

        with pytest.raises(ValueError):
            mapper.get_field_names_for_record_type("unknown")

        with pytest.raises(ValueError):
            mapper.get_expected_field_count_for_record_type("unknown")
