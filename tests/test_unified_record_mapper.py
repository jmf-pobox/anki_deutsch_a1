"""Tests for RecordMapper with UnifiedArticleRecord support."""

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from langlearn.languages.german.records.records import UnifiedArticleRecord
from langlearn.services.record_mapper import RecordMapper


class TestRecordMapperUnifiedArticles:
    """Test cases for RecordMapper with unified article support."""

    @pytest.fixture
    def record_mapper(self) -> RecordMapper:
        """RecordMapper instance."""
        return RecordMapper()

    @pytest.fixture
    def unified_article_csv_content(self) -> str:
        """Sample unified article CSV content."""
        return (
            "artikel_typ,geschlecht,nominativ,akkusativ,dativ,genitiv,beispiel_nom,"
            "beispiel_akk,beispiel_dat,beispiel_gen\n"
            "bestimmt,maskulin,der,den,dem,des,Der Mann ist hier,Ich sehe den Mann,"
            "mit dem Mann,das Auto des Mannes\n"
            "bestimmt,feminin,die,die,der,der,Die Frau ist hier,Ich sehe die Frau,"
            "mit der Frau,das Auto der Frau\n"
            "bestimmt,neutral,das,das,dem,des,Das Kind ist hier,Ich sehe das Kind,"
            "mit dem Kind,das Spielzeug des Kindes\n"
            "unbestimmt,maskulin,ein,einen,einem,eines,Ein Mann kommt,"
            "Ich sehe einen Mann,mit einem Mann,das Auto eines Mannes\n"
            "verneinend,feminin,keine,keine,keiner,keiner,Keine Frau ist da,"
            "Ich sehe keine Frau,mit keiner Frau,das Auto keiner Frau"
        )

    @pytest.fixture
    def unified_article_csv_file(
        self, unified_article_csv_content: str
    ) -> Generator[Path, None, None]:
        """Temporary unified article CSV file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(unified_article_csv_content)
            f.flush()
            yield Path(f.name)
        Path(f.name).unlink(missing_ok=True)

    def test_detect_unified_article_csv_format(
        self, record_mapper: RecordMapper, unified_article_csv_file: Path
    ) -> None:
        """Test detection of unified article CSV format."""
        detected_type = record_mapper.detect_csv_record_type(unified_article_csv_file)
        assert detected_type == "unified_article"

    def test_is_supported_record_type_unified_article(
        self, record_mapper: RecordMapper
    ) -> None:
        """Test unified_article is supported record type."""
        assert record_mapper.is_supported_record_type("unified_article")

    def test_map_csv_row_to_unified_article_record(
        self, record_mapper: RecordMapper
    ) -> None:
        """Test mapping CSV row to UnifiedArticleRecord."""
        csv_row = {
            "artikel_typ": "bestimmt",
            "geschlecht": "maskulin",
            "nominativ": "der",
            "akkusativ": "den",
            "dativ": "dem",
            "genitiv": "des",
            "beispiel_nom": "Der Mann ist hier",
            "beispiel_akk": "Ich sehe den Mann",
            "beispiel_dat": "mit dem Mann",
            "beispiel_gen": "das Auto des Mannes",
        }

        record = record_mapper.map_csv_row_to_record("unified_article", csv_row)

        assert isinstance(record, UnifiedArticleRecord)
        assert record.artikel_typ == "bestimmt"
        assert record.geschlecht == "maskulin"
        assert record.nominativ == "der"
        assert record.akkusativ == "den"
        assert record.beispiel_nom == "Der Mann ist hier"

    def test_map_fields_to_unified_article_record(
        self, record_mapper: RecordMapper
    ) -> None:
        """Test mapping field array to UnifiedArticleRecord."""
        fields = [
            "unbestimmt",
            "feminin",
            "eine",
            "eine",
            "einer",
            "einer",
            "Eine Frau kommt",
            "Ich sehe eine Frau",
            "mit einer Frau",
            "das Auto einer Frau",
        ]

        record = record_mapper.map_fields_to_record("unified_article", fields)

        assert isinstance(record, UnifiedArticleRecord)
        assert record.artikel_typ == "unbestimmt"
        assert record.geschlecht == "feminin"
        assert record.nominativ == "eine"

    def test_load_records_from_unified_article_csv(
        self, record_mapper: RecordMapper, unified_article_csv_file: Path
    ) -> None:
        """Test loading records from unified article CSV file."""
        records = record_mapper.load_records_from_csv(unified_article_csv_file)

        assert len(records) == 5  # 5 records in the sample

        # Check first record (masculine definite)
        assert isinstance(records[0], UnifiedArticleRecord)
        assert records[0].artikel_typ == "bestimmt"
        assert records[0].geschlecht == "maskulin"
        assert records[0].nominativ == "der"

        # Check indefinite article record
        indefinite_record = records[3]  # 4th record is indefinite
        assert isinstance(indefinite_record, UnifiedArticleRecord)
        assert indefinite_record.artikel_typ == "unbestimmt"
        assert indefinite_record.nominativ == "ein"

        # Check negative article record
        negative_record = records[4]  # 5th record is negative
        assert isinstance(negative_record, UnifiedArticleRecord)
        assert negative_record.artikel_typ == "verneinend"
        assert negative_record.nominativ == "keine"

    def test_csv_detection_priority_unified_over_legacy(
        self, record_mapper: RecordMapper
    ) -> None:
        """Test that unified format is detected over legacy format."""
        # Create CSV with both unified and legacy headers
        content = (
            "artikel_typ,geschlecht,gender,nominativ,nominative,akkusativ,accusative,"
            "dativ,dative,genitiv,genitive,beispiel_nom,beispiel_akk,beispiel_dat,"
            "beispiel_gen,example_nom,example_acc,example_dat,example_gen\n"
            "bestimmt,maskulin,masculine,der,der,den,den,dem,dem,des,des,Der Mann,"
            "Ich sehe den Mann,mit dem Mann,des Mannes,Der Mann,I see the man,"
            "with the man,of the man"
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(content)
            f.flush()
            csv_path = Path(f.name)

        try:
            detected_type = record_mapper.detect_csv_record_type(csv_path)
            assert detected_type == "unified_article"  # Should prefer unified format
        finally:
            csv_path.unlink(missing_ok=True)

    def test_map_csv_row_missing_unified_fields(
        self, record_mapper: RecordMapper
    ) -> None:
        """Test mapping CSV row with missing unified article fields."""
        csv_row = {
            "artikel_typ": "bestimmt",
            "geschlecht": "maskulin",
            # Missing other required fields - should use empty strings
        }

        record = record_mapper.map_csv_row_to_record("unified_article", csv_row)

        assert isinstance(record, UnifiedArticleRecord)
        assert record.artikel_typ == "bestimmt"
        assert record.geschlecht == "maskulin"
        assert record.nominativ == ""  # Should default to empty string
        assert record.akkusativ == ""

    def test_unsupported_record_type_error(self, record_mapper: RecordMapper) -> None:
        """Test error for unsupported record type."""
        fields = ["some", "fields"]

        with pytest.raises(ValueError) as exc_info:
            record_mapper.map_fields_to_record("unsupported_type", fields)

        assert "Unknown model type: unsupported_type" in str(exc_info.value)

    def test_wrong_field_count_error(self, record_mapper: RecordMapper) -> None:
        """Test error for wrong number of fields."""
        fields = ["bestimmt", "maskulin"]  # Too few fields for unified_article

        with pytest.raises(ValueError) as exc_info:
            record_mapper.map_fields_to_record("unified_article", fields)

        assert "expects 10 fields, got 2" in str(exc_info.value)

    def test_detect_csv_record_type_with_minimal_headers(
        self, record_mapper: RecordMapper
    ) -> None:
        """Test CSV detection with just the minimal required headers."""
        # Create CSV with only the essential unified article headers
        content = (
            "artikel_typ,geschlecht,nominativ,akkusativ,dativ,genitiv,beispiel_nom,"
            "beispiel_akk,beispiel_dat,beispiel_gen\n"
            "bestimmt,maskulin,der,den,dem,des,Example1,Example2,Example3,Example4"
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(content)
            f.flush()
            csv_path = Path(f.name)

        try:
            detected_type = record_mapper.detect_csv_record_type(csv_path)
            assert detected_type == "unified_article"
        finally:
            csv_path.unlink(missing_ok=True)

    def test_csv_detection_with_extra_headers(
        self, record_mapper: RecordMapper
    ) -> None:
        """Test CSV detection works with extra headers beyond required ones."""
        # Create CSV with extra headers that shouldn't affect detection
        content = (
            "extra1,artikel_typ,geschlecht,nominativ,akkusativ,dativ,genitiv,"
            "beispiel_nom,beispiel_akk,beispiel_dat,beispiel_gen,extra2\n"
            "value1,bestimmt,maskulin,der,den,dem,des,Example1,Example2,"
            "Example3,Example4,value2"
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(content)
            f.flush()
            csv_path = Path(f.name)

        try:
            detected_type = record_mapper.detect_csv_record_type(csv_path)
            assert detected_type == "unified_article"
        finally:
            csv_path.unlink(missing_ok=True)

    def test_all_artikel_types_validation(self, record_mapper: RecordMapper) -> None:
        """Test mapping all valid artikel_typ values."""
        artikel_types = ["bestimmt", "unbestimmt", "verneinend"]

        for artikel_typ in artikel_types:
            fields = [
                artikel_typ,
                "maskulin",
                "test",
                "test",
                "test",
                "test",
                "Test sentence",
                "Test sentence",
                "Test sentence",
                "Test sentence",
            ]

            record = record_mapper.map_fields_to_record("unified_article", fields)
            assert isinstance(record, UnifiedArticleRecord)
            assert record.artikel_typ == artikel_typ

    def test_all_geschlecht_values_validation(
        self, record_mapper: RecordMapper
    ) -> None:
        """Test mapping all valid geschlecht values."""
        geschlechts = ["maskulin", "feminin", "neutral", "plural"]

        for geschlecht in geschlechts:
            fields = [
                "bestimmt",
                geschlecht,
                "test",
                "test",
                "test",
                "test",
                "Test sentence",
                "Test sentence",
                "Test sentence",
                "Test sentence",
            ]

            record = record_mapper.map_fields_to_record("unified_article", fields)
            assert isinstance(record, UnifiedArticleRecord)
            assert record.geschlecht == geschlecht

    def test_csv_field_whitespace_handling(self, record_mapper: RecordMapper) -> None:
        """Test that CSV fields are properly stripped of whitespace."""
        fields = [
            "  bestimmt  ",
            " maskulin ",
            " der ",
            " den ",
            " dem ",
            " des ",
            " Der Mann ist hier ",
            " Ich sehe den Mann ",
            " mit dem Mann ",
            " das Auto des Mannes ",
        ]

        record = record_mapper.map_fields_to_record("unified_article", fields)

        # All fields should be stripped
        assert isinstance(record, UnifiedArticleRecord)
        assert record.artikel_typ == "bestimmt"
        assert record.geschlecht == "maskulin"
        assert record.nominativ == "der"
        assert record.beispiel_nom == "Der Mann ist hier"

    def test_load_empty_unified_csv(self, record_mapper: RecordMapper) -> None:
        """Test loading empty unified article CSV."""
        content = (
            "artikel_typ,geschlecht,nominativ,akkusativ,dativ,genitiv,beispiel_nom,"
            "beispiel_akk,beispiel_dat,beispiel_gen"
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(content)
            f.flush()
            csv_path = Path(f.name)

        try:
            records = record_mapper.load_records_from_csv(csv_path)
            assert len(records) == 0
        finally:
            csv_path.unlink(missing_ok=True)
