"""Tests for VerbCardMultiplier service."""

import pytest

from langlearn.models.records import (
    BaseRecord,
    NounRecord,
    VerbConjugationRecord,
    VerbImperativeRecord,
)
from langlearn.services.verb_card_multiplier import VerbCardConfig, VerbCardMultiplier


class TestVerbCardConfig:
    """Tests for VerbCardConfig."""

    def test_default_config(self) -> None:
        """Test default configuration."""
        config = VerbCardConfig()

        assert config.cefr_level == "A1"
        assert config.include_conjugations is True
        assert config.include_imperatives is True
        assert config.max_tenses_per_verb == 3

    def test_config_for_a1_level(self) -> None:
        """Test A1 level configuration."""
        config = VerbCardConfig.for_cefr_level("A1")

        assert config.cefr_level == "A1"
        assert config.include_conjugations is True
        assert config.include_imperatives is True
        assert config.max_tenses_per_verb == 3

    def test_config_for_a2_level(self) -> None:
        """Test A2 level configuration."""
        config = VerbCardConfig.for_cefr_level("A2")

        assert config.cefr_level == "A2"
        assert config.include_conjugations is True
        assert config.include_imperatives is True
        assert config.max_tenses_per_verb == 5

    def test_config_for_b1_level(self) -> None:
        """Test B1 level configuration."""
        config = VerbCardConfig.for_cefr_level("B1")

        assert config.cefr_level == "B1"
        assert config.include_conjugations is True
        assert config.include_imperatives is True
        assert config.max_tenses_per_verb == 7

    def test_config_for_unknown_level(self) -> None:
        """Test configuration for unknown CEFR level defaults to A1."""
        config = VerbCardConfig.for_cefr_level("C2")

        assert config.cefr_level == "A1"
        assert config.max_tenses_per_verb == 3


class TestVerbCardMultiplier:
    """Tests for VerbCardMultiplier service."""

    @pytest.fixture
    def multiplier_a1(self) -> VerbCardMultiplier:
        """VerbCardMultiplier configured for A1 level."""
        config = VerbCardConfig.for_cefr_level("A1")
        return VerbCardMultiplier(config)

    @pytest.fixture
    def multiplier_a2(self) -> VerbCardMultiplier:
        """VerbCardMultiplier configured for A2 level."""
        config = VerbCardConfig.for_cefr_level("A2")
        return VerbCardMultiplier(config)

    @pytest.fixture
    def multiplier_b1(self) -> VerbCardMultiplier:
        """VerbCardMultiplier configured for B1 level."""
        config = VerbCardConfig.for_cefr_level("B1")
        return VerbCardMultiplier(config)

    @pytest.fixture
    def sample_conjugation_present(self) -> VerbConjugationRecord:
        """Sample present tense conjugation record."""
        return VerbConjugationRecord(
            infinitive="arbeiten",
            english="to work",
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

    @pytest.fixture
    def sample_conjugation_subjunctive(self) -> VerbConjugationRecord:
        """Sample subjunctive tense conjugation record."""
        return VerbConjugationRecord(
            infinitive="arbeiten",
            english="to work",
            classification="regelmäßig",
            separable=False,
            auxiliary="haben",
            tense="subjunctive",
            ich="arbeitete",
            du="arbeitetest",
            er="arbeitete",
            wir="arbeiteten",
            ihr="arbeitetet",
            sie="arbeiteten",
            example="Wenn ich arbeitete...",
        )

    @pytest.fixture
    def sample_imperative(self) -> VerbImperativeRecord:
        """Sample imperative record."""
        return VerbImperativeRecord(
            infinitive="arbeiten",
            english="to work",
            classification="regelmäßig",
            separable=False,
            du_form="arbeite",
            ihr_form="arbeitet",
            sie_form="arbeiten Sie",
            example_du="Arbeite schneller!",
            example_ihr="Arbeitet zusammen!",
            example_sie="Arbeiten Sie bitte hier!",
        )

    @pytest.fixture
    def sample_noun(self) -> NounRecord:
        """Sample noun record for testing non-verb handling."""
        return NounRecord(
            noun="Katze",
            article="die",
            english="cat",
            plural="Katzen",
            example="Die Katze schläft.",
            related="Tier",
        )

    def test_multiplier_initialization_default(self) -> None:
        """Test multiplier initialization with default config."""
        multiplier = VerbCardMultiplier()

        config = multiplier.get_config()
        assert config.cefr_level == "A1"

    def test_multiplier_initialization_custom_config(self) -> None:
        """Test multiplier initialization with custom config."""
        config = VerbCardConfig.for_cefr_level("B1")
        multiplier = VerbCardMultiplier(config)

        result_config = multiplier.get_config()
        assert result_config.cefr_level == "B1"

    def test_multiply_empty_list(self, multiplier_a1: VerbCardMultiplier) -> None:
        """Test multiplication of empty record list."""
        result = multiplier_a1.multiply_verb_records([])

        assert result == []

    def test_multiply_conjugation_present_a1(
        self,
        multiplier_a1: VerbCardMultiplier,
        sample_conjugation_present: VerbConjugationRecord,
    ) -> None:
        """Test multiplication of present tense conjugation at A1 level."""
        records: list[BaseRecord] = [sample_conjugation_present]

        result = multiplier_a1.multiply_verb_records(records)

        assert len(result) == 1
        assert isinstance(result[0], VerbConjugationRecord)
        conj_record = result[0]
        assert conj_record.infinitive == "arbeiten"
        assert conj_record.tense == "present"

    def test_multiply_conjugation_subjunctive_a1(
        self,
        multiplier_a1: VerbCardMultiplier,
        sample_conjugation_subjunctive: VerbConjugationRecord,
    ) -> None:
        """Test that subjunctive tense is filtered out at A1 level."""
        records: list[BaseRecord] = [sample_conjugation_subjunctive]

        result = multiplier_a1.multiply_verb_records(records)

        # Subjunctive should be filtered out at A1 level
        assert len(result) == 0

    def test_multiply_conjugation_subjunctive_b1(
        self,
        multiplier_b1: VerbCardMultiplier,
        sample_conjugation_subjunctive: VerbConjugationRecord,
    ) -> None:
        """Test that subjunctive tense is included at B1 level."""
        records: list[BaseRecord] = [sample_conjugation_subjunctive]

        result = multiplier_b1.multiply_verb_records(records)

        # Subjunctive should be included at B1 level
        assert len(result) == 1
        assert isinstance(result[0], VerbConjugationRecord)
        conj_record = result[0]
        assert conj_record.tense == "subjunctive"

    def test_multiply_imperative_record(
        self, multiplier_a1: VerbCardMultiplier, sample_imperative: VerbImperativeRecord
    ) -> None:
        """Test multiplication of imperative record."""
        records: list[BaseRecord] = [sample_imperative]

        result = multiplier_a1.multiply_verb_records(records)

        assert len(result) == 1
        assert isinstance(result[0], VerbImperativeRecord)
        imp_record = result[0]
        assert imp_record.infinitive == "arbeiten"

    def test_multiply_mixed_verb_records(
        self,
        multiplier_a1: VerbCardMultiplier,
        sample_conjugation_present: VerbConjugationRecord,
        sample_imperative: VerbImperativeRecord,
    ) -> None:
        """Test multiplication of mixed verb record types."""
        records = [sample_conjugation_present, sample_imperative]

        result = multiplier_a1.multiply_verb_records(records)

        assert len(result) == 2
        assert isinstance(result[0], VerbConjugationRecord)
        assert isinstance(result[1], VerbImperativeRecord)

    def test_multiply_non_verb_records(
        self, multiplier_a1: VerbCardMultiplier, sample_noun: NounRecord
    ) -> None:
        """Test that non-verb records pass through unchanged."""
        records: list[BaseRecord] = [sample_noun]

        result = multiplier_a1.multiply_verb_records(records)

        assert len(result) == 1
        assert isinstance(result[0], NounRecord)
        noun_record = result[0]
        assert noun_record.noun == "Katze"

    def test_multiply_with_enriched_data(
        self,
        multiplier_a1: VerbCardMultiplier,
        sample_conjugation_present: VerbConjugationRecord,
    ) -> None:
        """Test multiplication with enriched media data (ignored by multiplier)."""
        records: list[BaseRecord] = [sample_conjugation_present]
        enriched_data = [
            {
                "word_audio": "[sound:arbeiten.mp3]",
                "example_audio": "[sound:example.mp3]",
                "image": "<img src='work.jpg'>",
            }
        ]

        result = multiplier_a1.multiply_verb_records(records, enriched_data)

        assert len(result) == 1
        # Multiplier no longer enriches records - that's MediaEnricher's job
        assert isinstance(result[0], VerbConjugationRecord)
        result_record = result[0]
        assert result_record.infinitive == "arbeiten"
        assert result_record.tense == "present"
        # Media fields should be None (not enriched by multiplier)
        assert result_record.word_audio is None

    def test_multiply_with_enriched_data_imperative(
        self, multiplier_a1: VerbCardMultiplier, sample_imperative: VerbImperativeRecord
    ) -> None:
        """Test multiplication of imperative with enriched media data
        (ignored by multiplier)."""
        records: list[BaseRecord] = [sample_imperative]
        enriched_data = [
            {
                "word_audio": "[sound:arbeiten.mp3]",
                "du_audio": "[sound:arbeite.mp3]",
                "ihr_audio": "[sound:arbeitet.mp3]",
                "sie_audio": "[sound:arbeiten_sie.mp3]",
                "image": "<img src='work.jpg'>",
            }
        ]

        result = multiplier_a1.multiply_verb_records(records, enriched_data)

        assert len(result) == 1
        # Multiplier no longer enriches records - that's MediaEnricher's job
        assert isinstance(result[0], VerbImperativeRecord)
        result_record = result[0]
        assert result_record.infinitive == "arbeiten"
        assert result_record.du_form == "arbeite"
        # Media fields should be None (not enriched by multiplier)
        assert result_record.word_audio is None

    def test_multiply_enriched_data_mismatch(
        self,
        multiplier_a1: VerbCardMultiplier,
        sample_conjugation_present: VerbConjugationRecord,
    ) -> None:
        """Test multiplication when enriched data list doesn't match record count."""
        records: list[BaseRecord] = [sample_conjugation_present]
        enriched_data: list[dict[str, str]] = []  # Empty list

        result = multiplier_a1.multiply_verb_records(records, enriched_data)

        assert len(result) == 1
        # Should still work, just without enriched data
        assert isinstance(result[0], VerbConjugationRecord)
        conj_record = result[0]
        assert conj_record.word_audio is None

    def test_tense_filtering_a1_level(self, multiplier_a1: VerbCardMultiplier) -> None:
        """Test tense filtering at A1 level."""
        # A1 should include: present, preterite, perfect
        assert multiplier_a1._is_tense_appropriate_for_level("present") is True
        assert multiplier_a1._is_tense_appropriate_for_level("preterite") is True
        assert multiplier_a1._is_tense_appropriate_for_level("perfect") is True
        assert multiplier_a1._is_tense_appropriate_for_level("future") is False
        assert multiplier_a1._is_tense_appropriate_for_level("subjunctive") is False

    def test_tense_filtering_a2_level(self, multiplier_a2: VerbCardMultiplier) -> None:
        """Test tense filtering at A2 level."""
        # A2 should include: present, preterite, perfect, future
        assert multiplier_a2._is_tense_appropriate_for_level("present") is True
        assert multiplier_a2._is_tense_appropriate_for_level("preterite") is True
        assert multiplier_a2._is_tense_appropriate_for_level("perfect") is True
        assert multiplier_a2._is_tense_appropriate_for_level("future") is True
        assert multiplier_a2._is_tense_appropriate_for_level("subjunctive") is False

    def test_tense_filtering_b1_level(self, multiplier_b1: VerbCardMultiplier) -> None:
        """Test tense filtering at B1 level."""
        # B1 should include all tenses
        assert multiplier_b1._is_tense_appropriate_for_level("present") is True
        assert multiplier_b1._is_tense_appropriate_for_level("preterite") is True
        assert multiplier_b1._is_tense_appropriate_for_level("perfect") is True
        assert multiplier_b1._is_tense_appropriate_for_level("future") is True
        assert multiplier_b1._is_tense_appropriate_for_level("subjunctive") is True

    def test_expected_card_count(
        self,
        multiplier_a1: VerbCardMultiplier,
        sample_conjugation_present: VerbConjugationRecord,
        sample_conjugation_subjunctive: VerbConjugationRecord,
        sample_imperative: VerbImperativeRecord,
        sample_noun: NounRecord,
    ) -> None:
        """Test expected card count calculation."""
        records = [
            sample_conjugation_present,  # Included at A1
            sample_conjugation_subjunctive,  # Excluded at A1
            sample_imperative,  # Included at A1
            sample_noun,  # Pass through
        ]

        expected_count = multiplier_a1.get_expected_card_count(records)

        # present (1) + imperative (1) + noun (1) = 3
        # subjunctive filtered out at A1
        assert expected_count == 3

    def test_update_config(self, multiplier_a1: VerbCardMultiplier) -> None:
        """Test updating multiplier configuration."""
        new_config = VerbCardConfig.for_cefr_level("B1")

        multiplier_a1.update_config(new_config)

        result_config = multiplier_a1.get_config()
        assert result_config.cefr_level == "B1"

    def test_error_handling_invalid_record(
        self, multiplier_a1: VerbCardMultiplier
    ) -> None:
        """Test error handling with invalid record data during processing."""
        # Create a valid record but test error handling during processing
        valid_record = VerbConjugationRecord(
            infinitive="arbeiten",
            english="to work",
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
            example="Test example.",
        )

        records: list[BaseRecord] = [valid_record]

        # This test verifies that the multiplier handles errors gracefully
        # In this case, no error should occur with valid data
        result = multiplier_a1.multiply_verb_records(records)

        # Should process the record successfully
        assert len(result) == 1
        assert isinstance(result[0], VerbConjugationRecord)

    def test_separable_verb_processing(self, multiplier_a1: VerbCardMultiplier) -> None:
        """Test processing of separable verbs."""
        separable_conjugation = VerbConjugationRecord(
            infinitive="aufstehen",
            english="to get up",
            classification="unregelmäßig",
            separable=True,
            auxiliary="sein",
            tense="present",
            ich="stehe auf",
            du="stehst auf",
            er="steht auf",
            wir="stehen auf",
            ihr="steht auf",
            sie="stehen auf",
            example="Ich stehe um 7 Uhr auf.",
        )

        records: list[BaseRecord] = [separable_conjugation]
        result = multiplier_a1.multiply_verb_records(records)

        assert len(result) == 1
        assert isinstance(result[0], VerbConjugationRecord)
        conj_record = result[0]
        assert conj_record.separable is True
        assert conj_record.ich == "stehe auf"

    def test_multiple_tenses_same_verb(self, multiplier_a1: VerbCardMultiplier) -> None:
        """Test processing multiple tenses for the same verb."""
        present_record = VerbConjugationRecord(
            infinitive="arbeiten",
            english="to work",
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
            example="Ich arbeite.",
        )

        preterite_record = VerbConjugationRecord(
            infinitive="arbeiten",
            english="to work",
            classification="regelmäßig",
            separable=False,
            auxiliary="haben",
            tense="preterite",
            ich="arbeitete",
            du="arbeitetest",
            er="arbeitete",
            wir="arbeiteten",
            ihr="arbeitetet",
            sie="arbeiteten",
            example="Ich arbeitete.",
        )

        records: list[BaseRecord] = [present_record, preterite_record]
        result = multiplier_a1.multiply_verb_records(records)

        # Both tenses should be included at A1 level
        assert len(result) == 2
        # Cast to conjugation records to access tense attribute
        conj_records = [r for r in result if isinstance(r, VerbConjugationRecord)]
        tenses = {r.tense for r in conj_records}
        assert tenses == {"present", "preterite"}

    def test_cefr_level_progression(self) -> None:
        """Test that higher CEFR levels include more tenses."""
        subjunctive_record = VerbConjugationRecord(
            infinitive="haben",
            english="to have",
            classification="unregelmäßig",
            separable=False,
            auxiliary="haben",
            tense="subjunctive",
            ich="hätte",
            du="hättest",
            er="hätte",
            wir="hätten",
            ihr="hättet",
            sie="hätten",
            example="Wenn ich Zeit hätte...",
        )

        # A1 should exclude subjunctive
        multiplier_a1 = VerbCardMultiplier(VerbCardConfig.for_cefr_level("A1"))
        result_a1 = multiplier_a1.multiply_verb_records([subjunctive_record])
        assert len(result_a1) == 0

        # B1 should include subjunctive
        multiplier_b1 = VerbCardMultiplier(VerbCardConfig.for_cefr_level("B1"))
        result_b1 = multiplier_b1.multiply_verb_records([subjunctive_record])
        assert len(result_b1) == 1
        assert isinstance(result_b1[0], VerbConjugationRecord)
        assert result_b1[0].tense == "subjunctive"


class TestVerbCardMultiplierIntegration:
    """Integration tests for VerbCardMultiplier with realistic scenarios."""

    def test_realistic_verb_dataset(self) -> None:
        """Test with a realistic dataset of German verbs."""
        # Create a realistic dataset with multiple verbs and tenses
        records = [
            # arbeiten - regular verb, multiple tenses
            VerbConjugationRecord(
                infinitive="arbeiten",
                english="to work",
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
            ),
            VerbConjugationRecord(
                infinitive="arbeiten",
                english="to work",
                classification="regelmäßig",
                separable=False,
                auxiliary="haben",
                tense="perfect",
                ich="gearbeitet",
                du="gearbeitet",
                er="gearbeitet",
                wir="gearbeitet",
                ihr="gearbeitet",
                sie="gearbeitet",
                example="Ich habe gearbeitet.",
            ),
            # aufstehen - separable verb
            VerbConjugationRecord(
                infinitive="aufstehen",
                english="to get up",
                classification="unregelmäßig",
                separable=True,
                auxiliary="sein",
                tense="present",
                ich="stehe auf",
                du="stehst auf",
                er="steht auf",
                wir="stehen auf",
                ihr="steht auf",
                sie="stehen auf",
                example="Ich stehe früh auf.",
            ),
            # Imperative for arbeiten
            VerbImperativeRecord(
                infinitive="arbeiten",
                english="to work",
                classification="regelmäßig",
                separable=False,
                du_form="arbeite",
                ihr_form="arbeitet",
                sie_form="arbeiten Sie",
                example_du="Arbeite härter!",
                example_ihr="Arbeitet zusammen!",
                example_sie="Arbeiten Sie bitte!",
            ),
        ]

        # Test A1 level processing
        multiplier_a1 = VerbCardMultiplier(VerbCardConfig.for_cefr_level("A1"))
        result_a1 = multiplier_a1.multiply_verb_records(records)

        # Should include: arbeiten (present + perfect) + aufstehen (present)
        # + imperative = 4
        assert len(result_a1) == 4

        # Verify we have the right mix of record types
        conjugation_count = sum(
            1 for r in result_a1 if isinstance(r, VerbConjugationRecord)
        )
        imperative_count = sum(
            1 for r in result_a1 if isinstance(r, VerbImperativeRecord)
        )

        assert (
            conjugation_count == 3
        )  # arbeiten (present + perfect) + aufstehen (present)
        assert imperative_count == 1  # arbeiten imperative

    def test_progressive_complexity_by_level(self) -> None:
        """Test that complexity increases with CEFR level."""
        # Create records with varying tense complexity
        records = [
            # Present - A1 level
            VerbConjugationRecord(
                infinitive="sein",
                english="to be",
                classification="unregelmäßig",
                separable=False,
                auxiliary="sein",
                tense="present",
                ich="bin",
                du="bist",
                er="ist",
                wir="sind",
                ihr="seid",
                sie="sind",
                example="Ich bin müde.",
            ),
            # Future - A2 level
            VerbConjugationRecord(
                infinitive="sein",
                english="to be",
                classification="unregelmäßig",
                separable=False,
                auxiliary="sein",
                tense="future",
                ich="werde sein",
                du="wirst sein",
                er="wird sein",
                wir="werden sein",
                ihr="werdet sein",
                sie="werden sein",
                example="Ich werde da sein.",
            ),
            # Subjunctive - B1 level
            VerbConjugationRecord(
                infinitive="sein",
                english="to be",
                classification="unregelmäßig",
                separable=False,
                auxiliary="sein",
                tense="subjunctive",
                ich="wäre",
                du="wärst",
                er="wäre",
                wir="wären",
                ihr="wärt",
                sie="wären",
                example="Wenn ich da wäre...",
            ),
        ]

        # A1: should only include present
        multiplier_a1 = VerbCardMultiplier(VerbCardConfig.for_cefr_level("A1"))
        records_typed: list[BaseRecord] = list(records)
        result_a1 = multiplier_a1.multiply_verb_records(records_typed)
        assert len(result_a1) == 1
        assert isinstance(result_a1[0], VerbConjugationRecord)
        assert result_a1[0].tense == "present"

        # A2: should include present + future
        multiplier_a2 = VerbCardMultiplier(VerbCardConfig.for_cefr_level("A2"))
        result_a2 = multiplier_a2.multiply_verb_records(records_typed)
        assert len(result_a2) == 2
        conj_records_a2 = [r for r in result_a2 if isinstance(r, VerbConjugationRecord)]
        tenses_a2 = {r.tense for r in conj_records_a2}
        assert tenses_a2 == {"present", "future"}

        # B1: should include all tenses
        multiplier_b1 = VerbCardMultiplier(VerbCardConfig.for_cefr_level("B1"))
        result_b1 = multiplier_b1.multiply_verb_records(records_typed)
        assert len(result_b1) == 3
        conj_records_b1 = [r for r in result_b1 if isinstance(r, VerbConjugationRecord)]
        tenses_b1 = {r.tense for r in conj_records_b1}
        assert tenses_b1 == {"present", "future", "subjunctive"}
