"""Test dataclass-based record implementations."""

import pytest

from langlearn.core.records.base_record_dataclass import RecordType
from langlearn.languages.german.records.adverb_record_dataclass import AdverbRecord
from langlearn.languages.german.records.noun_record_dataclass import NounRecord
from langlearn.languages.german.records.verb_conjugation_record_dataclass import (
    VerbConjugationRecord,
)


class TestAdverbRecord:
    """Test AdverbRecord dataclass implementation."""

    def test_create_from_csv_fields(self) -> None:
        """Test creating AdverbRecord from CSV fields."""
        fields = ["hier", "here", "location", "Ich bin hier."]
        record = AdverbRecord.from_csv_fields(fields)

        assert record.word == "hier"
        assert record.english == "here"
        assert record.type == "location"
        assert record.example == "Ich bin hier."
        assert record.image is None
        assert record.word_audio is None
        assert record.example_audio is None

    def test_to_dict(self) -> None:
        """Test converting AdverbRecord to dictionary."""
        record = AdverbRecord(
            word="schnell",
            english="fast",
            type="manner",
            example="Er läuft schnell.",
        )
        result = record.to_dict()

        assert result["word"] == "schnell"
        assert result["english"] == "fast"
        assert result["type"] == "manner"
        assert result["example"] == "Er läuft schnell."
        assert result["image"] is None

    def test_get_record_type(self) -> None:
        """Test getting record type."""
        assert AdverbRecord.get_record_type() == RecordType.ADVERB

    def test_insufficient_fields_error(self) -> None:
        """Test error on insufficient CSV fields."""
        fields = ["hier", "here", "location"]  # Missing example
        with pytest.raises(ValueError, match="requires at least 4 fields"):
            AdverbRecord.from_csv_fields(fields)


class TestNounRecord:
    """Test NounRecord dataclass implementation."""

    def test_create_from_csv_fields(self) -> None:
        """Test creating NounRecord from CSV fields."""
        fields = ["Haus", "das", "house", "Häuser", "Das ist ein Haus.", "Gebäude"]
        record = NounRecord.from_csv_fields(fields)

        assert record.noun == "Haus"
        assert record.article == "das"
        assert record.english == "house"
        assert record.plural == "Häuser"
        assert record.example == "Das ist ein Haus."
        assert record.related == "Gebäude"

    def test_create_without_related_field(self) -> None:
        """Test creating NounRecord without related field."""
        fields = ["Haus", "das", "house", "Häuser", "Das ist ein Haus.", ""]
        record = NounRecord.from_csv_fields(fields)
        assert record.related == ""

    def test_get_field_names(self) -> None:
        """Test getting field names."""
        expected = ["noun", "article", "english", "plural", "example", "related"]
        assert NounRecord.get_field_names() == expected

    def test_get_subdeck_name(self) -> None:
        """Test getting subdeck name."""
        assert NounRecord.get_subdeck_name() == "Nouns"


class TestVerbConjugationRecord:
    """Test VerbConjugationRecord dataclass with validation."""

    def test_create_valid_present_tense(self) -> None:
        """Test creating valid present tense conjugation."""
        fields = [
            "gehen",
            "to go",
            "unregelmäßig",
            "false",
            "sein",
            "present",
            "gehe",
            "gehst",
            "geht",
            "gehen",
            "geht",
            "gehen",
            "Ich gehe zur Schule.",
        ]
        record = VerbConjugationRecord.from_csv_fields(fields)

        assert record.infinitive == "gehen"
        assert record.english == "to go"
        assert record.classification == "unregelmäßig"
        assert record.separable is False
        assert record.auxiliary == "sein"
        assert record.tense == "present"
        assert record.ich == "gehe"

    def test_invalid_classification(self) -> None:
        """Test validation error for invalid classification."""
        fields = [
            "gehen",
            "to go",
            "invalid",  # Invalid classification
            "false",
            "sein",
            "present",
            "gehe",
            "gehst",
            "geht",
            "gehen",
            "geht",
            "gehen",
            "Example",
        ]
        with pytest.raises(ValueError, match="Invalid classification"):
            VerbConjugationRecord.from_csv_fields(fields)

    def test_invalid_auxiliary(self) -> None:
        """Test validation error for invalid auxiliary."""
        fields = [
            "gehen",
            "to go",
            "unregelmäßig",
            "false",
            "werden",  # Invalid auxiliary
            "present",
            "gehe",
            "gehst",
            "geht",
            "gehen",
            "geht",
            "gehen",
            "Example",
        ]
        with pytest.raises(ValueError, match="Invalid auxiliary"):
            VerbConjugationRecord.from_csv_fields(fields)

    def test_invalid_tense(self) -> None:
        """Test validation error for invalid tense."""
        fields = [
            "gehen",
            "to go",
            "unregelmäßig",
            "false",
            "sein",
            "past",  # Invalid tense
            "gehe",
            "gehst",
            "geht",
            "gehen",
            "geht",
            "gehen",
            "Example",
        ]
        with pytest.raises(ValueError, match="Invalid tense"):
            VerbConjugationRecord.from_csv_fields(fields)

    def test_missing_present_tense_forms(self) -> None:
        """Test validation error for missing present tense forms."""
        fields = [
            "gehen",
            "to go",
            "unregelmäßig",
            "false",
            "sein",
            "present",
            "gehe",
            "gehst",
            "",  # Missing er form
            "gehen",
            "geht",
            "gehen",
            "Example",
        ]
        with pytest.raises(ValueError, match="present tense requires all persons"):
            VerbConjugationRecord.from_csv_fields(fields)

    def test_imperative_tense_validation(self) -> None:
        """Test imperative tense requires only du and ihr forms."""
        fields = [
            "gehen",
            "to go",
            "unregelmäßig",
            "false",
            "sein",
            "imperative",
            "",  # ich can be empty
            "geh",  # du required
            "",  # er can be empty
            "",  # wir can be empty
            "geht",  # ihr required
            "gehen Sie",  # sie optional
            "Geh nach Hause!",
        ]
        record = VerbConjugationRecord.from_csv_fields(fields)
        assert record.du == "geh"
        assert record.ihr == "geht"

    def test_imperative_missing_du_form(self) -> None:
        """Test imperative validation error for missing du form."""
        fields = [
            "gehen",
            "to go",
            "unregelmäßig",
            "false",
            "sein",
            "imperative",
            "",
            "",  # Missing du form
            "",
            "",
            "geht",
            "",
            "Example",
        ]
        with pytest.raises(ValueError, match="Imperative tense requires 'du' form"):
            VerbConjugationRecord.from_csv_fields(fields)

    def test_perfect_tense_validation(self) -> None:
        """Test perfect tense requires auxiliary form in sie field."""
        fields = [
            "gehen",
            "to go",
            "unregelmäßig",
            "false",
            "sein",
            "perfect",
            "",  # Forms can be empty for perfect
            "",
            "",
            "",
            "",
            "bin gegangen",  # Auxiliary form required in sie field
            "Ich bin gegangen.",
        ]
        record = VerbConjugationRecord.from_csv_fields(fields)
        assert record.sie == "bin gegangen"

    def test_impersonal_verb_validation(self) -> None:
        """Test impersonal verb only needs sie form."""
        fields = [
            "regnen",
            "to rain",
            "regelmäßig",
            "false",
            "haben",
            "present",
            "",  # ich can be empty
            "",  # du can be empty
            "",  # er can be empty
            "",  # wir can be empty
            "",  # ihr can be empty
            "regnet",  # sie required for impersonal
            "Es regnet heute.",
        ]
        record = VerbConjugationRecord.from_csv_fields(fields)
        assert record.sie == "regnet"

    def test_get_result_key(self) -> None:
        """Test getting result key for statistics."""
        assert VerbConjugationRecord.get_result_key() == "verbs"
