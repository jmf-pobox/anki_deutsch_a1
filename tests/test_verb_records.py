"""Tests for VerbConjugationRecord and VerbImperativeRecord."""

import pytest
from pydantic import ValidationError

from langlearn.models.records import (
    VerbConjugationRecord,
    VerbImperativeRecord,
    create_record,
)


class TestVerbConjugationRecord:
    """Tests for VerbConjugationRecord."""

    def test_valid_conjugation_record_creation(self) -> None:
        """Test creating a valid conjugation record."""
        fields = [
            "arbeiten",  # infinitive
            "to work",  # meaning
            "regelmäßig",  # classification
            "false",  # separable
            "haben",  # auxiliary
            "present",  # tense
            "arbeite",  # ich
            "arbeitest",  # du
            "arbeitet",  # er
            "arbeiten",  # wir
            "arbeitet",  # ihr
            "arbeiten",  # sie
            "Ich arbeite jeden Tag.",  # example
        ]

        record = VerbConjugationRecord.from_csv_fields(fields)

        assert record.infinitive == "arbeiten"
        assert record.meaning == "to work"
        assert record.classification == "regelmäßig"
        assert record.separable is False
        assert record.auxiliary == "haben"
        assert record.tense == "present"
        assert record.ich == "arbeite"
        assert record.du == "arbeitest"
        assert record.er == "arbeitet"
        assert record.wir == "arbeiten"
        assert record.ihr == "arbeitet"
        assert record.sie == "arbeiten"
        assert record.example == "Ich arbeite jeden Tag."

    def test_separable_verb_conjugation(self) -> None:
        """Test conjugation record for separable verb."""
        fields = [
            "aufstehen",
            "to get up",
            "unregelmäßig",
            "true",
            "sein",
            "present",
            "stehe auf",
            "stehst auf",
            "steht auf",
            "stehen auf",
            "steht auf",
            "stehen auf",
            "Ich stehe um 7 Uhr auf.",
        ]

        record = VerbConjugationRecord.from_csv_fields(fields)

        assert record.infinitive == "aufstehen"
        assert record.separable is True
        assert record.auxiliary == "sein"
        assert record.ich == "stehe auf"

    def test_irregular_verb_conjugation(self) -> None:
        """Test conjugation record for irregular verb."""
        fields = [
            "sein",
            "to be",
            "unregelmäßig",
            "false",
            "sein",
            "present",
            "bin",
            "bist",
            "ist",
            "sind",
            "seid",
            "sind",
            "Ich bin müde.",
        ]

        record = VerbConjugationRecord.from_csv_fields(fields)

        assert record.classification == "unregelmäßig"
        assert record.ich == "bin"
        assert record.du == "bist"
        assert record.er == "ist"

    def test_mixed_verb_conjugation(self) -> None:
        """Test conjugation record for mixed verb."""
        fields = [
            "bringen",
            "to bring",
            "gemischt",
            "false",
            "haben",
            "preterite",
            "brachte",
            "brachtest",
            "brachte",
            "brachten",
            "brachtet",
            "brachten",
            "Ich brachte das Buch.",
        ]

        record = VerbConjugationRecord.from_csv_fields(fields)

        assert record.classification == "gemischt"
        assert record.tense == "preterite"
        assert record.ich == "brachte"

    def test_conjugation_validation_errors(self) -> None:
        """Test validation errors for conjugation records."""
        # Invalid classification
        with pytest.raises(ValidationError, match="Invalid classification"):
            VerbConjugationRecord(
                infinitive="arbeiten",
                meaning="to work",
                classification="invalid",
                separable=False,
                auxiliary="haben",
                tense="present",
                ich="arbeite",
                du="arbeitest",
                er="arbeitet",
                wir="arbeiten",
                ihr="arbeitet",
                sie="arbeiten",
                example="Test",
            )

        # Invalid auxiliary
        with pytest.raises(ValidationError, match="Invalid auxiliary"):
            VerbConjugationRecord(
                infinitive="arbeiten",
                meaning="to work",
                classification="regelmäßig",
                separable=False,
                auxiliary="invalid",
                tense="present",
                ich="arbeite",
                du="arbeitest",
                er="arbeitet",
                wir="arbeiten",
                ihr="arbeitet",
                sie="arbeiten",
                example="Test",
            )

        # Empty conjugation form
        with pytest.raises(ValidationError, match="Conjugation forms cannot be empty"):
            VerbConjugationRecord(
                infinitive="arbeiten",
                meaning="to work",
                classification="regelmäßig",
                separable=False,
                auxiliary="haben",
                tense="present",
                ich="",
                du="arbeitest",
                er="arbeitet",
                wir="arbeiten",
                ihr="arbeitet",
                sie="arbeiten",
                example="Test",
            )

    def test_conjugation_insufficient_fields(self) -> None:
        """Test error when insufficient fields provided."""
        fields = ["arbeiten", "to work", "regelmäßig"]  # Only 3 fields

        with pytest.raises(ValueError, match="requires at least 12 fields"):
            VerbConjugationRecord.from_csv_fields(fields)

    def test_conjugation_to_dict(self) -> None:
        """Test converting conjugation record to dictionary."""
        record = VerbConjugationRecord(
            infinitive="arbeiten",
            meaning="to work",
            classification="regelmäßig",
            separable=False,
            auxiliary="haben",
            tense="present",
            ich="arbeite",
            du="arbeitest",
            er="arbeitet",
            wir="arbeiten",
            ihr="arbeitet",
            sie="arbeiten",
            example="Ich arbeite jeden Tag.",
        )

        result = record.to_dict()

        assert result["infinitive"] == "arbeiten"
        assert result["meaning"] == "to work"
        assert result["classification"] == "regelmäßig"
        assert result["separable"] is False
        assert result["auxiliary"] == "haben"
        assert result["tense"] == "present"
        assert result["ich"] == "arbeite"
        assert result["du"] == "arbeitest"
        assert result["example"] == "Ich arbeite jeden Tag."

    def test_conjugation_field_names(self) -> None:
        """Test field names for conjugation record."""
        expected = [
            "infinitive",
            "meaning",
            "classification",
            "separable",
            "auxiliary",
            "tense",
            "ich",
            "du",
            "er",
            "wir",
            "ihr",
            "sie",
            "example",
        ]

        assert VerbConjugationRecord.get_field_names() == expected
        assert VerbConjugationRecord.get_expected_field_count() == 13


class TestVerbImperativeRecord:
    """Tests for VerbImperativeRecord."""

    def test_valid_imperative_record_creation(self) -> None:
        """Test creating a valid imperative record."""
        fields = [
            "arbeiten",  # infinitive
            "to work",  # meaning
            "regelmäßig",  # classification
            "false",  # separable
            "arbeite",  # du_form
            "arbeitet",  # ihr_form
            "arbeiten Sie",  # sie_form
            "Arbeite schneller!",  # example_du
            "Arbeitet zusammen!",  # example_ihr
            "Arbeiten Sie bitte hier!",  # example_sie
        ]

        record = VerbImperativeRecord.from_csv_fields(fields)

        assert record.infinitive == "arbeiten"
        assert record.meaning == "to work"
        assert record.classification == "regelmäßig"
        assert record.separable is False
        assert record.du_form == "arbeite"
        assert record.ihr_form == "arbeitet"
        assert record.sie_form == "arbeiten Sie"
        assert record.example_du == "Arbeite schneller!"
        assert record.example_ihr == "Arbeitet zusammen!"
        assert record.example_sie == "Arbeiten Sie bitte hier!"

    def test_separable_imperative(self) -> None:
        """Test imperative record for separable verb."""
        fields = [
            "aufstehen",
            "to get up",
            "unregelmäßig",
            "true",
            "steh auf",
            "steht auf",
            "stehen Sie auf",
            "Steh sofort auf!",
            "Steht bitte auf!",
            "Stehen Sie bitte auf!",
        ]

        record = VerbImperativeRecord.from_csv_fields(fields)

        assert record.infinitive == "aufstehen"
        assert record.separable is True
        assert record.du_form == "steh auf"
        assert record.ihr_form == "steht auf"
        assert record.sie_form == "stehen Sie auf"

    def test_imperative_minimal_fields(self) -> None:
        """Test imperative with minimal required fields."""
        fields = ["gehen", "to go", "unregelmäßig", "false", "geh", "geht", "gehen Sie"]

        record = VerbImperativeRecord.from_csv_fields(fields)

        assert record.infinitive == "gehen"
        assert record.du_form == "geh"
        assert record.ihr_form == "geht"
        assert record.sie_form == "gehen Sie"
        assert record.example_du == ""  # Default empty
        assert record.example_ihr == ""
        assert record.example_sie == ""

    def test_imperative_validation_errors(self) -> None:
        """Test validation errors for imperative records."""
        # Invalid classification
        with pytest.raises(ValidationError, match="Invalid classification"):
            VerbImperativeRecord(
                infinitive="arbeiten",
                meaning="to work",
                classification="invalid",
                separable=False,
                du_form="arbeite",
                ihr_form="arbeitet",
                sie_form="arbeiten Sie",
                example_du="Test",
            )

        # Empty imperative form
        with pytest.raises(ValidationError, match="Imperative forms cannot be empty"):
            VerbImperativeRecord(
                infinitive="arbeiten",
                meaning="to work",
                classification="regelmäßig",
                separable=False,
                du_form="",  # Empty
                ihr_form="arbeitet",
                sie_form="arbeiten Sie",
                example_du="Test",
            )

    def test_imperative_insufficient_fields(self) -> None:
        """Test error when insufficient fields provided."""
        fields = ["arbeiten", "to work"]  # Only 2 fields

        with pytest.raises(ValueError, match="requires at least 7 fields"):
            VerbImperativeRecord.from_csv_fields(fields)

    def test_imperative_to_dict(self) -> None:
        """Test converting imperative record to dictionary."""
        record = VerbImperativeRecord(
            infinitive="arbeiten",
            meaning="to work",
            classification="regelmäßig",
            separable=False,
            du_form="arbeite",
            ihr_form="arbeitet",
            sie_form="arbeiten Sie",
            example_du="Arbeite schneller!",
        )

        result = record.to_dict()

        assert result["infinitive"] == "arbeiten"
        assert result["meaning"] == "to work"
        assert result["classification"] == "regelmäßig"
        assert result["separable"] is False
        assert result["du_form"] == "arbeite"
        assert result["ihr_form"] == "arbeitet"
        assert result["sie_form"] == "arbeiten Sie"
        assert result["example_du"] == "Arbeite schneller!"

    def test_imperative_field_names(self) -> None:
        """Test field names for imperative record."""
        expected = [
            "infinitive",
            "meaning",
            "classification",
            "separable",
            "du_form",
            "ihr_form",
            "sie_form",
            "example_du",
            "example_ihr",
            "example_sie",
        ]

        assert VerbImperativeRecord.get_field_names() == expected
        assert VerbImperativeRecord.get_expected_field_count() == 10


class TestVerbRecordFactory:
    """Tests for verb record creation through factory function."""

    def test_create_conjugation_record(self) -> None:
        """Test creating conjugation record via factory."""
        fields = [
            "arbeiten",
            "to work",
            "regelmäßig",
            "false",
            "haben",
            "present",
            "arbeite",
            "arbeitest",
            "arbeitet",
            "arbeiten",
            "arbeitet",
            "arbeiten",
            "Ich arbeite.",
        ]

        record = create_record("verb_conjugation", fields)

        assert isinstance(record, VerbConjugationRecord)
        assert record.infinitive == "arbeiten"
        assert record.tense == "present"

    def test_create_imperative_record(self) -> None:
        """Test creating imperative record via factory."""
        fields = [
            "arbeiten",
            "to work",
            "regelmäßig",
            "false",
            "arbeite",
            "arbeitet",
            "arbeiten Sie",
            "Arbeite!",
            "Arbeitet!",
            "Arbeiten Sie!",
        ]

        record = create_record("verb_imperative", fields)

        assert isinstance(record, VerbImperativeRecord)
        assert record.infinitive == "arbeiten"
        assert record.du_form == "arbeite"

    def test_unknown_verb_record_type(self) -> None:
        """Test error for unknown verb record type."""
        with pytest.raises(ValueError, match="Unknown model type: unknown_verb"):
            create_record("unknown_verb", ["test"])


class TestVerbRecordIntegration:
    """Integration tests for verb records."""

    def test_conjugation_whitespace_handling(self) -> None:
        """Test that whitespace is properly stripped."""
        fields = [
            "  arbeiten  ",
            "  to work  ",
            "  regelmäßig  ",
            "  false  ",
            "  haben  ",
            "  present  ",
            "  arbeite  ",
            "  arbeitest  ",
            "  arbeitet  ",
            "  arbeiten  ",
            "  arbeitet  ",
            "  arbeiten  ",
            "  Ich arbeite.  ",
        ]

        record = VerbConjugationRecord.from_csv_fields(fields)

        assert record.infinitive == "arbeiten"
        assert record.meaning == "to work"
        assert record.classification == "regelmäßig"
        assert record.ich == "arbeite"

    def test_imperative_whitespace_handling(self) -> None:
        """Test that whitespace is properly stripped in imperatives."""
        fields = [
            "  arbeiten  ",
            "  to work  ",
            "  regelmäßig  ",
            "  false  ",
            "  arbeite  ",
            "  arbeitet  ",
            "  arbeiten Sie  ",
            "  Arbeite!  ",
        ]

        record = VerbImperativeRecord.from_csv_fields(fields)

        assert record.infinitive == "arbeiten"
        assert record.du_form == "arbeite"
        assert record.sie_form == "arbeiten Sie"
        assert record.example_du == "Arbeite!"

    def test_boolean_conversion(self) -> None:
        """Test various boolean representations for separable field."""
        test_cases = [
            ("true", True),
            ("True", True),
            ("1", True),
            ("yes", True),
            ("false", False),
            ("False", False),
            ("0", False),
            ("no", False),
            ("anything_else", False),
        ]

        for bool_str, expected in test_cases:
            fields = [
                "arbeiten",
                "to work",
                "regelmäßig",
                bool_str,
                "haben",
                "present",
                "arbeite",
                "arbeitest",
                "arbeitet",
                "arbeiten",
                "arbeitet",
                "arbeiten",
                "Test",
            ]

            record = VerbConjugationRecord.from_csv_fields(fields)
            assert record.separable is expected, f"Failed for '{bool_str}'"

    def test_media_fields_default_none(self) -> None:
        """Test that media fields default to None."""
        record = VerbConjugationRecord(
            infinitive="arbeiten",
            meaning="to work",
            classification="regelmäßig",
            separable=False,
            auxiliary="haben",
            tense="present",
            ich="arbeite",
            du="arbeitest",
            er="arbeitet",
            wir="arbeiten",
            ihr="arbeitet",
            sie="arbeiten",
            example="Test",
        )

        assert record.word_audio is None
        assert record.example_audio is None
        assert record.image is None

    def test_imperative_media_fields(self) -> None:
        """Test imperative record media fields."""
        record = VerbImperativeRecord(
            infinitive="arbeiten",
            meaning="to work",
            classification="regelmäßig",
            separable=False,
            du_form="arbeite",
            ihr_form="arbeitet",
            sie_form="arbeiten Sie",
            example_du="Test",
        )

        assert record.word_audio is None
        assert record.du_audio is None
        assert record.ihr_audio is None
        assert record.sie_audio is None
        assert record.image is None
