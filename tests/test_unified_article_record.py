"""Tests for UnifiedArticleRecord class."""

import pytest
from pydantic import ValidationError

from langlearn.models.records import UnifiedArticleRecord


class TestUnifiedArticleRecord:
    """Test cases for UnifiedArticleRecord functionality."""

    def test_create_valid_record(self) -> None:
        """Test creating a valid UnifiedArticleRecord."""
        record = UnifiedArticleRecord(
            artikel_typ="bestimmt",
            geschlecht="maskulin",
            nominativ="der",
            akkusativ="den",
            dativ="dem",
            genitiv="des",
            beispiel_nom="Der Mann ist hier",
            beispiel_akk="Ich sehe den Mann",
            beispiel_dat="mit dem Mann",
            beispiel_gen="das Auto des Mannes",
        )

        assert record.artikel_typ == "bestimmt"
        assert record.geschlecht == "maskulin"
        assert record.nominativ == "der"
        assert record.akkusativ == "den"
        assert record.dativ == "dem"
        assert record.genitiv == "des"

    def test_create_feminine_record(self) -> None:
        """Test creating feminine article record."""
        record = UnifiedArticleRecord(
            artikel_typ="bestimmt",
            geschlecht="feminin",
            nominativ="die",
            akkusativ="die",
            dativ="der",
            genitiv="der",
            beispiel_nom="Die Frau ist hier",
            beispiel_akk="Ich sehe die Frau",
            beispiel_dat="mit der Frau",
            beispiel_gen="das Auto der Frau",
        )

        assert record.geschlecht == "feminin"
        assert record.nominativ == "die"
        assert record.dativ == "der"

    def test_create_indefinite_article_record(self) -> None:
        """Test creating indefinite article record."""
        record = UnifiedArticleRecord(
            artikel_typ="unbestimmt",
            geschlecht="neutral",
            nominativ="ein",
            akkusativ="ein",
            dativ="einem",
            genitiv="eines",
            beispiel_nom="Ein Kind spielt",
            beispiel_akk="Ich sehe ein Kind",
            beispiel_dat="mit einem Kind",
            beispiel_gen="das Spielzeug eines Kindes",
        )

        assert record.artikel_typ == "unbestimmt"
        assert record.geschlecht == "neutral"

    def test_create_negative_article_record(self) -> None:
        """Test creating negative article record."""
        record = UnifiedArticleRecord(
            artikel_typ="verneinend",
            geschlecht="plural",
            nominativ="keine",
            akkusativ="keine",
            dativ="keinen",
            genitiv="keiner",
            beispiel_nom="Keine Kinder sind da",
            beispiel_akk="Ich sehe keine Kinder",
            beispiel_dat="mit keinen Kindern",
            beispiel_gen="das Spielzeug keiner Kinder",
        )

        assert record.artikel_typ == "verneinend"
        assert record.geschlecht == "plural"

    def test_invalid_artikel_typ(self) -> None:
        """Test validation error for invalid artikel_typ."""
        with pytest.raises(ValidationError) as exc_info:
            UnifiedArticleRecord(
                artikel_typ="invalid",
                geschlecht="maskulin",
                nominativ="der",
                akkusativ="den",
                dativ="dem",
                genitiv="des",
                beispiel_nom="Der Mann ist hier",
                beispiel_akk="Ich sehe den Mann",
                beispiel_dat="mit dem Mann",
                beispiel_gen="das Auto des Mannes",
            )

        error = exc_info.value.errors()[0]
        assert error["type"] == "value_error"
        assert "Invalid artikel_typ: invalid" in str(error["ctx"])

    def test_invalid_geschlecht(self) -> None:
        """Test validation error for invalid geschlecht."""
        with pytest.raises(ValidationError) as exc_info:
            UnifiedArticleRecord(
                artikel_typ="bestimmt",
                geschlecht="invalid",
                nominativ="der",
                akkusativ="den",
                dativ="dem",
                genitiv="des",
                beispiel_nom="Der Mann ist hier",
                beispiel_akk="Ich sehe den Mann",
                beispiel_dat="mit dem Mann",
                beispiel_gen="das Auto des Mannes",
            )

        error = exc_info.value.errors()[0]
        assert error["type"] == "value_error"
        assert "Invalid geschlecht: invalid" in str(error["ctx"])

    def test_from_csv_fields_valid(self) -> None:
        """Test creating record from CSV fields."""
        fields = [
            "bestimmt",
            "maskulin",
            "der",
            "den",
            "dem",
            "des",
            "Der Mann ist hier",
            "Ich sehe den Mann",
            "mit dem Mann",
            "das Auto des Mannes",
        ]

        record = UnifiedArticleRecord.from_csv_fields(fields)

        assert record.artikel_typ == "bestimmt"
        assert record.geschlecht == "maskulin"
        assert record.nominativ == "der"
        assert record.beispiel_nom == "Der Mann ist hier"

    def test_from_csv_fields_wrong_count(self) -> None:
        """Test error with wrong number of CSV fields."""
        fields = ["bestimmt", "maskulin", "der"]  # Too few fields

        with pytest.raises(ValueError) as exc_info:
            UnifiedArticleRecord.from_csv_fields(fields)

        assert "expects 10 fields, got 3" in str(exc_info.value)

    def test_to_dict(self) -> None:
        """Test converting record to dictionary."""
        record = UnifiedArticleRecord(
            artikel_typ="bestimmt",
            geschlecht="maskulin",
            nominativ="der",
            akkusativ="den",
            dativ="dem",
            genitiv="des",
            beispiel_nom="Der Mann ist hier",
            beispiel_akk="Ich sehe den Mann",
            beispiel_dat="mit dem Mann",
            beispiel_gen="das Auto des Mannes",
        )

        result = record.to_dict()

        assert result["artikel_typ"] == "bestimmt"
        assert result["geschlecht"] == "maskulin"
        assert result["nominativ"] == "der"
        assert result["article_audio"] is None  # Default media field
        assert result["example_audio"] is None
        assert result["image"] is None

    def test_get_field_names(self) -> None:
        """Test getting field names for CSV header."""
        expected_fields = [
            "artikel_typ",
            "geschlecht",
            "nominativ",
            "akkusativ",
            "dativ",
            "genitiv",
            "beispiel_nom",
            "beispiel_akk",
            "beispiel_dat",
            "beispiel_gen",
        ]

        assert UnifiedArticleRecord.get_field_names() == expected_fields

    def test_get_expected_field_count(self) -> None:
        """Test getting expected field count."""
        assert UnifiedArticleRecord.get_expected_field_count() == 10

    def test_all_valid_artikel_types(self) -> None:
        """Test all valid article types."""
        valid_types = ["bestimmt", "unbestimmt", "verneinend"]

        for artikel_typ in valid_types:
            record = UnifiedArticleRecord(
                artikel_typ=artikel_typ,
                geschlecht="maskulin",
                nominativ="der",
                akkusativ="den",
                dativ="dem",
                genitiv="des",
                beispiel_nom="Der Mann ist hier",
                beispiel_akk="Ich sehe den Mann",
                beispiel_dat="mit dem Mann",
                beispiel_gen="das Auto des Mannes",
            )
            assert record.artikel_typ == artikel_typ

    def test_all_valid_geschlechts(self) -> None:
        """Test all valid genders."""
        valid_genders = ["maskulin", "feminin", "neutral", "plural"]

        for geschlecht in valid_genders:
            record = UnifiedArticleRecord(
                artikel_typ="bestimmt",
                geschlecht=geschlecht,
                nominativ="der",
                akkusativ="den",
                dativ="dem",
                genitiv="des",
                beispiel_nom="Der Mann ist hier",
                beispiel_akk="Ich sehe den Mann",
                beispiel_dat="mit dem Mann",
                beispiel_gen="das Auto des Mannes",
            )
            assert record.geschlecht == geschlecht

    def test_with_enriched_media_data(self) -> None:
        """Test record with enriched media fields."""
        record = UnifiedArticleRecord(
            artikel_typ="bestimmt",
            geschlecht="maskulin",
            nominativ="der",
            akkusativ="den",
            dativ="dem",
            genitiv="des",
            beispiel_nom="Der Mann ist hier",
            beispiel_akk="Ich sehe den Mann",
            beispiel_dat="mit dem Mann",
            beispiel_gen="das Auto des Mannes",
            article_audio="audio_der.mp3",
            example_audio="example_mann.mp3",
            image="mann.jpg",
        )

        assert record.article_audio == "audio_der.mp3"
        assert record.example_audio == "example_mann.mp3"
        assert record.image == "mann.jpg"

        result = record.to_dict()
        assert result["article_audio"] == "audio_der.mp3"
        assert result["example_audio"] == "example_mann.mp3"
        assert result["image"] == "mann.jpg"
