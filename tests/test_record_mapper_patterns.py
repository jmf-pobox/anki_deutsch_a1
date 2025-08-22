"""Tests for pattern-specific RecordMapper functionality."""

import csv
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from langlearn.models.records import (
    NounRecord,
    VerbConjugationRecord,
    VerbImperativeRecord,
)
from langlearn.services.record_mapper import RecordMapper


class TestRecordMapperPatternDetection:
    """Tests for CSV pattern auto-detection."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mapper = RecordMapper()

    def create_temp_csv(self, headers: list[str], rows: list[list[str]]) -> Path:
        """Create a temporary CSV file for testing."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as temp_file:
            writer = csv.writer(temp_file)
            writer.writerow(headers)
            for row in rows:
                writer.writerow(row)
            temp_file_name = temp_file.name

        return Path(temp_file_name)

    def test_detect_verb_conjugation_csv(self) -> None:
        """Test detection of verb conjugation CSV format."""
        headers = [
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
        rows = [
            [
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
        ]

        csv_path = self.create_temp_csv(headers, rows)

        try:
            result = self.mapper.detect_csv_record_type(csv_path)
            assert result == "verb_conjugation"
        finally:
            csv_path.unlink()

    def test_detect_verb_imperative_csv(self) -> None:
        """Test detection of verb imperative CSV format."""
        headers = [
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
        rows = [
            [
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
        ]

        csv_path = self.create_temp_csv(headers, rows)

        try:
            result = self.mapper.detect_csv_record_type(csv_path)
            assert result == "verb_imperative"
        finally:
            csv_path.unlink()

    def test_detect_noun_csv(self) -> None:
        """Test detection of noun CSV format."""
        headers = ["noun", "article", "english", "plural", "example", "related"]
        rows = [["Katze", "die", "cat", "Katzen", "Die Katze schläft.", "Tier"]]

        csv_path = self.create_temp_csv(headers, rows)

        try:
            result = self.mapper.detect_csv_record_type(csv_path)
            assert result == "noun"
        finally:
            csv_path.unlink()

    def test_detect_adjective_csv(self) -> None:
        """Test detection of adjective CSV format."""
        headers = ["word", "english", "example", "comparative", "superlative"]
        rows = [["gut", "good", "Das ist gut.", "besser", "am besten"]]

        csv_path = self.create_temp_csv(headers, rows)

        try:
            result = self.mapper.detect_csv_record_type(csv_path)
            assert result == "adjective"
        finally:
            csv_path.unlink()

    def test_detect_adverb_csv_by_filename(self) -> None:
        """Test detection of adverb CSV by filename pattern."""
        headers = ["word", "english", "type", "example"]
        rows = [["schnell", "fast", "manner", "Er läuft schnell."]]

        # Create file with 'adverb' in name
        with tempfile.NamedTemporaryFile(
            mode="w", suffix="_adverbs.csv", delete=False, encoding="utf-8"
        ) as temp_file:
            writer = csv.writer(temp_file)
            writer.writerow(headers)
            writer.writerow(rows[0])
            temp_file_name = temp_file.name

        csv_path = Path(temp_file_name)

        try:
            result = self.mapper.detect_csv_record_type(csv_path)
            assert result == "adverb"
        finally:
            csv_path.unlink()

    def test_detect_negation_csv_by_filename(self) -> None:
        """Test detection of negation CSV by filename pattern."""
        headers = ["word", "english", "type", "example"]
        rows = [["nicht", "not", "general", "Ich bin nicht müde."]]

        # Create file with 'negation' in name
        with tempfile.NamedTemporaryFile(
            mode="w", suffix="_negations.csv", delete=False, encoding="utf-8"
        ) as temp_file:
            writer = csv.writer(temp_file)
            writer.writerow(headers)
            writer.writerow(rows[0])
            temp_file_name = temp_file.name

        csv_path = Path(temp_file_name)

        try:
            result = self.mapper.detect_csv_record_type(csv_path)
            assert result == "negation"
        finally:
            csv_path.unlink()

    def test_detect_unknown_csv_format(self) -> None:
        """Test error handling for unknown CSV format."""
        headers = ["unknown", "format", "columns"]
        rows = [["data1", "data2", "data3"]]

        csv_path = self.create_temp_csv(headers, rows)

        try:
            with pytest.raises(ValueError, match="Cannot detect record type"):
                self.mapper.detect_csv_record_type(csv_path)
        finally:
            csv_path.unlink()

    def test_detect_nonexistent_csv(self) -> None:
        """Test error handling for non-existent CSV file."""
        nonexistent_path = Path("/nonexistent/file.csv")

        with pytest.raises(FileNotFoundError):
            self.mapper.detect_csv_record_type(nonexistent_path)

    def test_detect_empty_csv(self) -> None:
        """Test handling of empty CSV file."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as temp_file:
            temp_file_name = temp_file.name

        csv_path = Path(temp_file_name)

        try:
            with pytest.raises(ValueError):
                self.mapper.detect_csv_record_type(csv_path)
        finally:
            csv_path.unlink()


class TestRecordMapperVerbSupport:
    """Tests for verb record mapping functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mapper = RecordMapper()

    def test_updated_supported_record_types(self) -> None:
        """Test that verb record types are in supported list."""
        supported = self.mapper.get_supported_record_types()

        assert "verb_conjugation" in supported
        assert "verb_imperative" in supported
        assert (
            len(supported) == 12
        )  # noun, adjective, adverb, negation, verb, preposition, phrase + 2 verb types + 3 article types

    def test_is_supported_verb_record_types(self) -> None:
        """Test verb record type support checking."""
        assert self.mapper.is_supported_record_type("verb_conjugation")
        assert self.mapper.is_supported_record_type("verb_imperative")
        assert not self.mapper.is_supported_record_type("unknown_verb")

    def test_map_verb_conjugation_row(self) -> None:
        """Test mapping CSV row to verb conjugation record."""
        row = {
            "infinitive": "arbeiten",
            "english": "to work",
            "classification": "regelmäßig",
            "separable": "false",
            "auxiliary": "haben",
            "tense": "present",
            "ich": "arbeite",
            "du": "arbeitest",
            "er": "arbeitet",
            "wir": "arbeiten",
            "ihr": "arbeitet",
            "sie": "arbeiten",
            "example": "Ich arbeite jeden Tag.",
        }

        record = self.mapper.map_csv_row_to_record("verb_conjugation", row)

        assert isinstance(record, VerbConjugationRecord)
        assert record.infinitive == "arbeiten"
        assert record.english == "to work"
        assert record.tense == "present"
        assert record.ich == "arbeite"
        assert record.separable is False

    def test_map_verb_imperative_row(self) -> None:
        """Test mapping CSV row to verb imperative record."""
        row = {
            "infinitive": "arbeiten",
            "english": "to work",
            "classification": "regelmäßig",
            "separable": "false",
            "du_form": "arbeite",
            "ihr_form": "arbeitet",
            "sie_form": "arbeiten Sie",
            "example_du": "Arbeite schneller!",
            "example_ihr": "Arbeitet zusammen!",
            "example_sie": "Arbeiten Sie hier!",
        }

        record = self.mapper.map_csv_row_to_record("verb_imperative", row)

        assert isinstance(record, VerbImperativeRecord)
        assert record.infinitive == "arbeiten"
        assert record.du_form == "arbeite"
        assert record.ihr_form == "arbeitet"
        assert record.sie_form == "arbeiten Sie"

    def test_get_field_names_for_verb_types(self) -> None:
        """Test getting field names for verb record types."""
        conj_fields = self.mapper.get_field_names_for_record_type("verb_conjugation")
        imp_fields = self.mapper.get_field_names_for_record_type("verb_imperative")

        assert "infinitive" in conj_fields
        assert "tense" in conj_fields
        assert "ich" in conj_fields
        assert len(conj_fields) == 13

        assert "infinitive" in imp_fields
        assert "du_form" in imp_fields
        assert "ihr_form" in imp_fields
        assert len(imp_fields) == 10

    def test_get_expected_field_count_for_verb_types(self) -> None:
        """Test getting field counts for verb record types."""
        conj_count = self.mapper.get_expected_field_count_for_record_type(
            "verb_conjugation"
        )
        imp_count = self.mapper.get_expected_field_count_for_record_type(
            "verb_imperative"
        )

        assert conj_count == 13
        assert imp_count == 10


class TestRecordMapperCSVLoading:
    """Tests for CSV loading with auto-detection."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mapper = RecordMapper()

    def create_temp_csv(self, headers: list[str], rows: list[list[str]]) -> Path:
        """Create a temporary CSV file for testing."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as temp_file:
            writer = csv.writer(temp_file)
            writer.writerow(headers)
            for row in rows:
                writer.writerow(row)
            temp_file_name = temp_file.name

        return Path(temp_file_name)

    def test_load_verb_conjugation_records(self) -> None:
        """Test loading verb conjugation records from CSV."""
        headers = [
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
        rows = [
            [
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
            ],
            [
                "arbeiten",
                "to work",
                "regelmäßig",
                "false",
                "haben",
                "preterite",
                "arbeitete",
                "arbeitetest",
                "arbeitete",
                "arbeiteten",
                "arbeitetet",
                "arbeiteten",
                "Ich arbeitete.",
            ],
        ]

        csv_path = self.create_temp_csv(headers, rows)

        try:
            records = self.mapper.load_records_from_csv(csv_path)

            assert len(records) == 2
            assert all(isinstance(r, VerbConjugationRecord) for r in records)
            # Cast to specific type after isinstance check
            conj_records = [r for r in records if isinstance(r, VerbConjugationRecord)]
            assert conj_records[0].tense == "present"
            assert conj_records[1].tense == "preterite"
            assert conj_records[0].infinitive == "arbeiten"
            assert conj_records[1].infinitive == "arbeiten"
        finally:
            csv_path.unlink()

    def test_load_verb_imperative_records(self) -> None:
        """Test loading verb imperative records from CSV."""
        headers = [
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
        rows = [
            [
                "arbeiten",
                "to work",
                "regelmäßig",
                "false",
                "arbeite",
                "arbeitet",
                "arbeiten Sie",
                "Arbeite schneller!",
                "Arbeitet zusammen!",
                "Arbeiten Sie hier!",
            ],
            [
                "gehen",
                "to go",
                "unregelmäßig",
                "false",
                "geh",
                "geht",
                "gehen Sie",
                "Geh nach Hause!",
                "Geht zusammen!",
                "Gehen Sie bitte!",
            ],
        ]

        csv_path = self.create_temp_csv(headers, rows)

        try:
            records = self.mapper.load_records_from_csv(csv_path)

            assert len(records) == 2
            assert all(isinstance(r, VerbImperativeRecord) for r in records)
            # Cast to specific type after isinstance check
            imp_records = [r for r in records if isinstance(r, VerbImperativeRecord)]
            assert imp_records[0].infinitive == "arbeiten"
            assert imp_records[1].infinitive == "gehen"
            assert imp_records[0].du_form == "arbeite"
            assert imp_records[1].du_form == "geh"
        finally:
            csv_path.unlink()

    def test_load_noun_records_with_auto_detection(self) -> None:
        """Test loading noun records with auto-detection."""
        headers = ["noun", "article", "english", "plural", "example", "related"]
        rows = [["Katze", "die", "cat", "Katzen", "Die Katze schläft.", "Tier"]]

        csv_path = self.create_temp_csv(headers, rows)

        try:
            records = self.mapper.load_records_from_csv(csv_path)

            assert len(records) == 1
            assert isinstance(records[0], NounRecord)
            assert records[0].noun == "Katze"
        finally:
            csv_path.unlink()

    def test_load_records_with_invalid_data(self) -> None:
        """Test error handling for invalid record data."""
        headers = [
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
        rows = [
            [
                "arbeiten",
                "to work",
                "INVALID_CLASS",
                "false",
                "haben",  # Invalid classification
                "present",
                "arbeite",
                "arbeitest",
                "arbeitet",
                "arbeiten",
                "arbeitet",
                "arbeiten",
                "Ich arbeite.",
            ]
        ]

        csv_path = self.create_temp_csv(headers, rows)

        try:
            with pytest.raises(
                ValueError, match="Invalid verb_conjugation data at row 2"
            ):
                self.mapper.load_records_from_csv(csv_path)
        finally:
            csv_path.unlink()

    def test_load_records_nonexistent_file(self) -> None:
        """Test error handling for non-existent file."""
        nonexistent_path = Path("/nonexistent/file.csv")

        with pytest.raises(FileNotFoundError):
            self.mapper.load_records_from_csv(nonexistent_path)


class TestRecordMapperIntegration:
    """Integration tests for RecordMapper functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mapper = RecordMapper()

    def create_temp_csv(self, headers: list[str], rows: list[list[str]]) -> Path:
        """Create a temporary CSV file for testing."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as temp_file:
            writer = csv.writer(temp_file)
            writer.writerow(headers)
            for row in rows:
                writer.writerow(row)
            temp_file_name = temp_file.name

        return Path(temp_file_name)

    def test_hybrid_verb_approach_integration(self) -> None:
        """Test the hybrid approach with multiple tenses per verb."""
        headers = [
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
        rows = [
            # Multiple rows for the same verb (arbeiten)
            [
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
                "Ich arbeite jeden Tag.",
            ],
            [
                "arbeiten",
                "to work",
                "regelmäßig",
                "false",
                "haben",
                "preterite",
                "arbeitete",
                "arbeitetest",
                "arbeitete",
                "arbeiteten",
                "arbeitetet",
                "arbeiteten",
                "Ich arbeitete gestern.",
            ],
            [
                "arbeiten",
                "to work",
                "regelmäßig",
                "false",
                "haben",
                "perfect",
                "gearbeitet",
                "gearbeitet",
                "gearbeitet",
                "gearbeitet",
                "gearbeitet",
                "gearbeitet",
                "Ich habe gearbeitet.",
            ],
            # Different verb (gehen)
            [
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
                "Ich gehe nach Hause.",
            ],
        ]

        csv_path = self.create_temp_csv(headers, rows)

        try:
            # Test auto-detection
            detected_type = self.mapper.detect_csv_record_type(csv_path)
            assert detected_type == "verb_conjugation"

            # Test loading records
            records = self.mapper.load_records_from_csv(csv_path)

            # Should create 4 records (one per row)
            assert len(records) == 4

            # Check that we have records for both verbs and multiple tenses
            # Cast to verb records after filtering
            verb_records = [r for r in records if isinstance(r, VerbConjugationRecord)]
            arbeiten_records = [r for r in verb_records if r.infinitive == "arbeiten"]
            gehen_records = [r for r in verb_records if r.infinitive == "gehen"]

            assert len(arbeiten_records) == 3  # present, preterite, perfect
            assert len(gehen_records) == 1  # present

            # Check tense variety
            tenses = {r.tense for r in arbeiten_records}
            assert tenses == {"present", "preterite", "perfect"}

        finally:
            csv_path.unlink()

    def test_separable_verb_handling(self) -> None:
        """Test handling of separable verbs across record types."""
        # Test conjugation record with separable verb
        conj_headers = [
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
        conj_rows = [
            [
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
                "Ich stehe um 7 auf.",
            ]
        ]

        conj_csv = self.create_temp_csv(conj_headers, conj_rows)

        # Test imperative record with separable verb
        imp_headers = [
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
        imp_rows = [
            [
                "aufstehen",
                "to get up",
                "unregelmäßig",
                "true",
                "steh auf",
                "steht auf",
                "stehen Sie auf",
                "Steh sofort auf!",
                "Steht bitte auf!",
                "Stehen Sie auf!",
            ]
        ]

        imp_csv = self.create_temp_csv(imp_headers, imp_rows)

        try:
            # Test conjugation record
            conj_records = self.mapper.load_records_from_csv(conj_csv)
            assert len(conj_records) == 1
            assert isinstance(conj_records[0], VerbConjugationRecord)
            conj_record = conj_records[0]
            assert conj_record.separable is True
            assert conj_record.ich == "stehe auf"

            # Test imperative record
            imp_records = self.mapper.load_records_from_csv(imp_csv)
            assert len(imp_records) == 1
            assert isinstance(imp_records[0], VerbImperativeRecord)
            imp_record = imp_records[0]
            assert imp_record.separable is True
            assert imp_record.du_form == "steh auf"

        finally:
            conj_csv.unlink()
            imp_csv.unlink()

    def test_error_recovery_and_logging(self) -> None:
        """Test error handling and logging during record loading."""
        headers = [
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
        rows = [
            # Valid record
            [
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
            ],
            # Invalid record (bad classification)
            [
                "gehen",
                "to go",
                "INVALID",
                "false",
                "sein",
                "present",
                "gehe",
                "gehst",
                "geht",
                "gehen",
                "geht",
                "gehen",
                "Ich gehe.",
            ],
        ]

        csv_path = self.create_temp_csv(headers, rows)

        try:
            with patch("langlearn.services.record_mapper.logger") as mock_logger:
                with pytest.raises(
                    ValueError, match="Invalid verb_conjugation data at row 3"
                ):
                    self.mapper.load_records_from_csv(csv_path)

                # Check that appropriate error logging occurred
                mock_logger.error.assert_called()
        finally:
            csv_path.unlink()
