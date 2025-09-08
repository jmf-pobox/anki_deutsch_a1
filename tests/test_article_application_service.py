"""Tests for ArticleApplicationService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest

from langlearn.languages.german.records.factory import NounRecord
from langlearn.services.article_application_service import ArticleApplicationService
from langlearn.services.card_builder import CardBuilder
from langlearn.services.template_service import TemplateService


class TestArticleApplicationService:
    """Test cases for ArticleApplicationService functionality."""

    @pytest.fixture
    def mock_template_service(self) -> Mock:
        """Mock template service."""
        mock_service = Mock(spec=TemplateService)
        mock_service.get_template.return_value = Mock()
        return mock_service

    @pytest.fixture
    def mock_card_builder(self, mock_template_service: Mock) -> Mock:
        """Mock card builder."""
        mock_builder = Mock(spec=CardBuilder)
        mock_builder._template_service = mock_template_service
        mock_builder._create_note_type_for_record.return_value = Mock()
        mock_builder._extract_field_values.return_value = ["field1", "field2", "field3"]
        return mock_builder

    @pytest.fixture
    def service(self, mock_card_builder: Mock) -> ArticleApplicationService:
        """ArticleApplicationService instance."""
        return ArticleApplicationService(mock_card_builder)

    @pytest.fixture
    def sample_noun_records(self) -> list[NounRecord]:
        """Sample noun records for testing."""
        return [
            NounRecord(
                noun="Haus",
                article="das",
                english="house",
                plural="Häuser",
                example="Das Haus ist groß.",
                related="die Wohnung",
            ),
            NounRecord(
                noun="Mann",
                article="der",
                english="man",
                plural="Männer",
                example="Der Mann arbeitet.",
                related="die Frau",
            ),
            NounRecord(
                noun="Frau",
                article="die",
                english="woman",
                plural="Frauen",
                example="Die Frau liest.",
                related="der Mann",
            ),
        ]

    def test_service_initialization(self, mock_card_builder: Mock) -> None:
        """Test service initialization."""
        service = ArticleApplicationService(mock_card_builder)
        assert service._card_builder is mock_card_builder

    def test_generate_noun_article_cards_single_noun(
        self, service: ArticleApplicationService, sample_noun_records: list[NounRecord]
    ) -> None:
        """Test generating cards for a single noun."""
        single_noun = [sample_noun_records[0]]  # Just "Haus"

        cards = service.generate_noun_article_cards(single_noun)

        # Should generate 5 cards per noun: 1 recognition + 4 cases
        assert len(cards) == 5

        # Each card should be a tuple of (field_values, note_type)
        for card in cards:
            assert isinstance(card, tuple)
            assert len(card) == 2
            assert isinstance(card[0], list)  # field_values

    def test_generate_noun_article_cards_multiple_nouns(
        self, service: ArticleApplicationService, sample_noun_records: list[NounRecord]
    ) -> None:
        """Test generating cards for multiple nouns."""
        cards = service.generate_noun_article_cards(sample_noun_records)

        # Should generate 5 cards per noun: 3 nouns * 5 cards = 15 cards
        assert len(cards) == 15

    def test_generate_noun_article_cards_with_enriched_data(
        self, service: ArticleApplicationService, sample_noun_records: list[NounRecord]
    ) -> None:
        """Test generating cards with enriched data."""
        enriched_data = [
            {"word_audio": "haus.mp3", "image": "haus.jpg"},
            {"word_audio": "mann.mp3", "image": "mann.jpg"},
            {"word_audio": "frau.mp3", "image": "frau.jpg"},
        ]

        cards = service.generate_noun_article_cards(sample_noun_records, enriched_data)

        assert len(cards) == 15  # 3 nouns * 5 cards each

    def test_get_expected_card_count(
        self, service: ArticleApplicationService, sample_noun_records: list[NounRecord]
    ) -> None:
        """Test calculating expected card count."""
        # Test with different numbers of nouns
        assert service.get_expected_card_count([]) == 0
        assert service.get_expected_card_count([sample_noun_records[0]]) == 5
        assert service.get_expected_card_count(sample_noun_records) == 15

    def test_get_article_forms_for_noun_der(
        self, service: ArticleApplicationService
    ) -> None:
        """Test getting article forms for masculine noun."""
        forms = service._get_article_forms_for_noun("der")

        expected = {
            "nominativ": "der",
            "akkusativ": "den",
            "dativ": "dem",
            "genitiv": "des",
        }
        assert forms == expected

    def test_get_article_forms_for_noun_die(
        self, service: ArticleApplicationService
    ) -> None:
        """Test getting article forms for feminine noun."""
        forms = service._get_article_forms_for_noun("die")

        expected = {
            "nominativ": "die",
            "akkusativ": "die",
            "dativ": "der",
            "genitiv": "der",
        }
        assert forms == expected

    def test_get_article_forms_for_noun_das(
        self, service: ArticleApplicationService
    ) -> None:
        """Test getting article forms for neuter noun."""
        forms = service._get_article_forms_for_noun("das")

        expected = {
            "nominativ": "das",
            "akkusativ": "das",
            "dativ": "dem",
            "genitiv": "des",
        }
        assert forms == expected

    def test_get_article_forms_for_noun_unknown(
        self, service: ArticleApplicationService
    ) -> None:
        """Test getting article forms for unknown article."""
        forms = service._get_article_forms_for_noun("unknown")

        # Should fallback to same article for all cases
        expected = {
            "nominativ": "unknown",
            "akkusativ": "unknown",
            "dativ": "unknown",
            "genitiv": "unknown",
        }
        assert forms == expected

    def test_get_gender_from_article(self, service: ArticleApplicationService) -> None:
        """Test getting gender from article."""
        assert service._get_gender_from_article("der") == "Maskulin"
        assert service._get_gender_from_article("die") == "Feminin"
        assert service._get_gender_from_article("das") == "Neutral"
        assert service._get_gender_from_article("unknown") == "Unbekannt"

    def test_generate_case_examples(self, service: ArticleApplicationService) -> None:
        """Test generating case example sentences."""
        examples = service._generate_case_examples("Haus", "das", "nominativ")

        # Should return all 4 cases
        assert len(examples) == 4
        assert "nominativ" in examples
        assert "akkusativ" in examples
        assert "dativ" in examples
        assert "genitiv" in examples

        # Check specific examples
        assert "das Haus ist hier" in examples["nominativ"]
        assert "Ich sehe das Haus" in examples["akkusativ"]
        assert "Mit das Haus" in examples["dativ"]
        assert "das Hauses" in examples["genitiv"]

    def test_create_article_recognition_card(
        self,
        service: ArticleApplicationService,
        sample_noun_records: list[NounRecord],
        mock_card_builder: Mock,
    ) -> None:
        """Test creating article recognition card."""
        noun = sample_noun_records[0]  # "Haus"

        service._create_article_recognition_card(noun)

        # Should call template service and card builder
        mock_card_builder._template_service.get_template.assert_called_with(
            "noun_article_recognition"
        )
        mock_card_builder._create_note_type_for_record.assert_called()
        mock_card_builder._extract_field_values.assert_called()

    def test_create_noun_case_card_nominativ(
        self, service: ArticleApplicationService, sample_noun_records: list[NounRecord]
    ) -> None:
        """Test creating nominative case card."""
        noun = sample_noun_records[0]  # "Haus" (das)

        card = service._create_noun_case_card(noun, "nominativ")

        # Card should be tuple of (field_values, note_type)
        assert isinstance(card, tuple)
        assert len(card) == 2

    def test_create_noun_case_card_accusative(
        self, service: ArticleApplicationService, sample_noun_records: list[NounRecord]
    ) -> None:
        """Test creating accusative case card."""
        noun = sample_noun_records[1]  # "Mann" (der → den)

        card = service._create_noun_case_card(noun, "akkusativ")

        assert isinstance(card, tuple)
        assert len(card) == 2

    def test_create_noun_case_card_dative(
        self, service: ArticleApplicationService, sample_noun_records: list[NounRecord]
    ) -> None:
        """Test creating dative case card."""
        noun = sample_noun_records[2]  # "Frau" (die → der)

        card = service._create_noun_case_card(noun, "dativ")

        assert isinstance(card, tuple)
        assert len(card) == 2

    def test_create_noun_case_card_genitive(
        self, service: ArticleApplicationService, sample_noun_records: list[NounRecord]
    ) -> None:
        """Test creating genitive case card."""
        noun = sample_noun_records[0]  # "Haus" (das → des)

        card = service._create_noun_case_card(noun, "genitiv")

        assert isinstance(card, tuple)
        assert len(card) == 2

    @patch("re.sub")
    def test_case_insensitive_article_replacement(
        self,
        mock_re_sub: Mock,
        service: ArticleApplicationService,
        sample_noun_records: list[NounRecord],
    ) -> None:
        """Test case-insensitive article replacement in context cards."""
        mock_re_sub.return_value = "___ Haus ist hier."

        noun = sample_noun_records[0]  # "Haus"
        service._create_noun_case_card(noun, "nominativ")

        # Should call re.sub with case-insensitive flag
        mock_re_sub.assert_called()
        call_args = mock_re_sub.call_args
        assert call_args[1]["flags"]  # Should have re.IGNORECASE flag

    def test_card_data_structure_article_recognition(
        self,
        service: ArticleApplicationService,
        sample_noun_records: list[NounRecord],
        mock_card_builder: Mock,
    ) -> None:
        """Test card data structure for article recognition cards."""
        noun = sample_noun_records[0]  # "Haus"

        # Mock the extract field values to capture card data
        def capture_card_data(
            record_type: str, card_data: dict[str, Any], note_type: Any
        ) -> list[str]:
            # Verify the card data structure
            assert card_data["card_type"] == "noun_article_recognition"
            assert card_data["front_text"] == "Haus"
            assert card_data["back_text"] == "das Haus"
            assert card_data["english_meaning"] == "house"
            return ["front", "back", "english"]

        mock_card_builder._extract_field_values.side_effect = capture_card_data

        service._create_article_recognition_card(noun)

    def test_card_data_structure_case_context(
        self,
        service: ArticleApplicationService,
        sample_noun_records: list[NounRecord],
        mock_card_builder: Mock,
    ) -> None:
        """Test card data structure for case context cards."""
        noun = sample_noun_records[1]  # "Mann" (der)

        # Mock the extract field values to capture card data
        def capture_card_data(
            record_type: str, card_data: dict[str, Any], note_type: Any
        ) -> list[str]:
            # Verify the card data structure for accusative case
            if card_data.get("case") == "akkusativ":
                assert card_data["card_type"] == "noun_case_context"
                assert card_data["case"] == "akkusativ"
                assert card_data["article_form"] == "den"  # der → den in accusative
                assert card_data["case_rule"] == "Maskulin akkusativ = den"
                assert card_data["case_usage"] == "das direkte Objekt"
                assert card_data["case_akkusativ"] == "true"
                assert card_data["case_nominativ"] == ""
            return ["front", "back", "case"]

        mock_card_builder._extract_field_values.side_effect = capture_card_data

        service._create_noun_case_card(noun, "akkusativ")

    def test_error_handling_empty_noun_list(
        self, service: ArticleApplicationService
    ) -> None:
        """Test handling empty noun list."""
        cards = service.generate_noun_article_cards([])
        assert len(cards) == 0

    def test_error_handling_none_enriched_data(
        self, service: ArticleApplicationService, sample_noun_records: list[NounRecord]
    ) -> None:
        """Test handling None enriched data."""
        cards = service.generate_noun_article_cards(sample_noun_records, None)
        assert len(cards) == 15  # Should still work without enriched data

    def test_logging_functionality(
        self,
        service: ArticleApplicationService,
        sample_noun_records: list[NounRecord],
        caplog: Any,
    ) -> None:
        """Test logging output."""
        with caplog.at_level("INFO"):
            service.generate_noun_article_cards(sample_noun_records)

        # Should log start and completion
        assert "Building noun-article cards from 3 noun records" in caplog.text
        assert "Generated 15 total noun-article cards" in caplog.text
