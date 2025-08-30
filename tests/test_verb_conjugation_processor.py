"""Tests for VerbConjugationProcessor service."""

from unittest.mock import Mock

from langlearn.models.records import VerbConjugationRecord
from langlearn.services.card_builder import CardBuilder
from langlearn.services.verb_conjugation_processor import VerbConjugationProcessor


class TestVerbConjugationProcessor:
    """Test VerbConjugationProcessor service."""

    def test_initialization(self) -> None:
        """Test processor initializes correctly."""
        mock_card_builder = Mock(spec=CardBuilder)
        processor = VerbConjugationProcessor(mock_card_builder)

        assert processor._card_builder is mock_card_builder

    def test_group_records_by_infinitive(self) -> None:
        """Test grouping records by infinitive verb."""
        mock_card_builder = Mock(spec=CardBuilder)
        processor = VerbConjugationProcessor(mock_card_builder)

        # Create test records for same verb but different tenses
        records = [
            VerbConjugationRecord(
                infinitive="gehen",
                english="to go",
                classification="unregelmäßig",
                separable=False,
                auxiliary="sein",
                tense="present",
                ich="gehe",
                du="gehst",
                er="geht",
                wir="gehen",
                ihr="geht",
                sie="gehen",
                example="Ich gehe nach Hause.",
            ),
            VerbConjugationRecord(
                infinitive="gehen",
                english="to go",
                classification="unregelmäßig",
                separable=False,
                auxiliary="sein",
                tense="perfect",
                ich="",
                du="",
                er="",
                wir="",
                ihr="",
                sie="bin gegangen",  # Perfect tense format
                example="Ich bin nach Hause gegangen.",
            ),
            VerbConjugationRecord(
                infinitive="machen",
                english="to make",
                classification="regelmäßig",
                separable=False,
                auxiliary="haben",
                tense="present",
                ich="mache",
                du="machst",
                er="macht",
                wir="machen",
                ihr="macht",
                sie="machen",
                example="Ich mache Hausaufgaben.",
            ),
        ]

        groups = processor._group_records_by_infinitive(records)

        # Should group by infinitive
        assert len(groups) == 2
        assert "gehen" in groups
        assert "machen" in groups

        # gehen should have 2 tense records
        assert len(groups["gehen"]) == 2
        assert len(groups["machen"]) == 1

    def test_sort_records_by_tense_priority(self) -> None:
        """Test tense priority sorting for A1 pedagogy."""
        mock_card_builder = Mock(spec=CardBuilder)
        processor = VerbConjugationProcessor(mock_card_builder)

        # Create mock records in random tense order
        record1 = Mock(spec=VerbConjugationRecord)
        record1.tense = "preterite"
        record2 = Mock(spec=VerbConjugationRecord)
        record2.tense = "imperative"
        record3 = Mock(spec=VerbConjugationRecord)
        record3.tense = "present"
        record4 = Mock(spec=VerbConjugationRecord)
        record4.tense = "perfect"

        records = [record1, record2, record3, record4]

        sorted_records = processor._sort_records_by_tense_priority(records)  # type: ignore[arg-type]

        # Should be sorted: present, perfect, imperative, preterite
        expected_order = ["present", "perfect", "imperative", "preterite"]
        actual_order = [r.tense for r in sorted_records]

        assert actual_order == expected_order

    def test_should_create_card_for_tense(self) -> None:
        """Test tense filtering logic for A1 level."""
        mock_card_builder = Mock(spec=CardBuilder)
        processor = VerbConjugationProcessor(mock_card_builder)

        # Core A1 tenses should always be included
        present_record = Mock(spec=VerbConjugationRecord)
        present_record.tense = "present"
        perfect_record = Mock(spec=VerbConjugationRecord)
        perfect_record.tense = "perfect"
        imperative_record = Mock(spec=VerbConjugationRecord)
        imperative_record.tense = "imperative"

        assert processor._should_create_card_for_tense(present_record) is True
        assert processor._should_create_card_for_tense(perfect_record) is True
        assert processor._should_create_card_for_tense(imperative_record) is True

        # Preterite only for high-frequency irregulars
        preterite_high_freq = Mock(spec=VerbConjugationRecord)
        preterite_high_freq.tense = "preterite"
        preterite_high_freq.infinitive = "sein"
        preterite_high_freq.classification = "unregelmäßig"

        preterite_regular = Mock(spec=VerbConjugationRecord)
        preterite_regular.tense = "preterite"
        preterite_regular.infinitive = "spielen"
        preterite_regular.classification = "regelmäßig"

        preterite_unknown = Mock(spec=VerbConjugationRecord)
        preterite_unknown.tense = "preterite"
        preterite_unknown.infinitive = "xyz"
        preterite_unknown.classification = "unregelmäßig"

        assert processor._should_create_card_for_tense(preterite_high_freq) is True
        assert processor._should_create_card_for_tense(preterite_regular) is False
        assert processor._should_create_card_for_tense(preterite_unknown) is False

    def test_get_expected_card_count(self) -> None:
        """Test expected card count calculation."""
        mock_card_builder = Mock(spec=CardBuilder)
        processor = VerbConjugationProcessor(mock_card_builder)

        # Create test records: 2 verbs, 3 tenses each (all A1 core)
        records = []
        for infinitive in ["gehen", "machen"]:
            for tense in ["present", "perfect", "imperative"]:
                record = Mock(spec=VerbConjugationRecord)
                record.infinitive = infinitive
                record.tense = tense
                record.classification = "regelmäßig"
                records.append(record)

        # Should expect 6 cards (2 verbs x 3 tenses)
        expected_count = processor.get_expected_card_count(records)  # type: ignore[arg-type]
        assert expected_count == 6

    def test_get_supported_tenses(self) -> None:
        """Test supported tense list."""
        mock_card_builder = Mock(spec=CardBuilder)
        processor = VerbConjugationProcessor(mock_card_builder)

        supported_tenses = processor.get_supported_tenses()

        assert supported_tenses == ["present", "perfect", "imperative", "preterite"]

    def test_validate_records_for_processing_valid(self) -> None:
        """Test validation passes for valid records."""
        mock_card_builder = Mock(spec=CardBuilder)
        processor = VerbConjugationProcessor(mock_card_builder)

        # Create valid test records
        records = []
        for i in range(15):  # Ensure > 10 verbs
            record = Mock(spec=VerbConjugationRecord)
            record.infinitive = f"verb{i}"
            record.english = f"meaning{i}"
            record.tense = "present"
            records.append(record)

        errors = processor.validate_records_for_processing(records)  # type: ignore[arg-type]

        assert errors == []

    def test_validate_records_for_processing_errors(self) -> None:
        """Test validation catches common errors."""
        mock_card_builder = Mock(spec=CardBuilder)
        processor = VerbConjugationProcessor(mock_card_builder)

        # Test empty records
        errors = processor.validate_records_for_processing([])
        assert "No records provided for processing" in errors

        # Test missing fields
        bad_record1 = Mock(spec=VerbConjugationRecord)
        bad_record1.infinitive = ""
        bad_record1.english = "test"
        bad_record1.tense = "present"

        bad_record2 = Mock(spec=VerbConjugationRecord)
        bad_record2.infinitive = "test"
        bad_record2.english = ""
        bad_record2.tense = "present"

        bad_record3 = Mock(spec=VerbConjugationRecord)
        bad_record3.infinitive = "test"
        bad_record3.english = "test"
        bad_record3.tense = ""

        bad_records = [bad_record1, bad_record2, bad_record3]

        errors = processor.validate_records_for_processing(bad_records)  # type: ignore[arg-type]

        assert "Record 0: Missing infinitive" in errors
        assert "Record 1: Missing english" in errors
        assert "Record 2: Missing tense" in errors
        assert "Very few verbs (2) - expected at least 10" in errors

    def test_create_conjugation_card_delegates_to_card_builder(self) -> None:
        """Test conjugation card creation delegates to CardBuilder."""
        mock_card_builder = Mock(spec=CardBuilder)
        mock_card_builder.build_card_from_record.return_value = (
            ["field1", "field2"],
            Mock(),
        )

        processor = VerbConjugationProcessor(mock_card_builder)

        mock_record = Mock()
        mock_enriched_data = {"test": "data"}

        result = processor._create_conjugation_card(mock_record, mock_enriched_data)

        # Should delegate to CardBuilder
        mock_card_builder.build_card_from_record.assert_called_once_with(
            mock_record, mock_enriched_data
        )

        assert result == (
            ["field1", "field2"],
            mock_card_builder.build_card_from_record.return_value[1],
        )

    def test_map_imperative_field_to_data_key(self) -> None:
        """Test imperative field mapping."""
        mock_card_builder = Mock(spec=CardBuilder)
        processor = VerbConjugationProcessor(mock_card_builder)

        # Test known mappings per PROD-CARD-SPEC.md
        assert processor._map_imperative_field_to_data_key("Infinitive") == "infinitive"
        assert processor._map_imperative_field_to_data_key("English") == "english"
        assert processor._map_imperative_field_to_data_key("Du") == "du"
        assert processor._map_imperative_field_to_data_key("Sie") == "sie"

        # Test fallback for unknown fields
        assert (
            processor._map_imperative_field_to_data_key("UnknownField")
            == "unknownfield"
        )
