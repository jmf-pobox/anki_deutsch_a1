"""Tests for German domain model factory functionality."""

import pytest

from langlearn.languages.german.language import GermanLanguage
from langlearn.languages.german.models.adjective import Adjective
from langlearn.languages.german.models.adverb import Adverb
from langlearn.languages.german.models.negation import Negation
from langlearn.languages.german.models.noun import Noun
from langlearn.languages.german.models.phrase import Phrase
from langlearn.languages.german.models.preposition import Preposition
from langlearn.languages.german.models.verb import Verb
from langlearn.languages.german.records.adjective_record import AdjectiveRecord
from langlearn.languages.german.records.adverb_record import AdverbRecord
from langlearn.languages.german.records.negation_record import NegationRecord
from langlearn.languages.german.records.noun_record import NounRecord
from langlearn.languages.german.records.phrase_record import PhraseRecord
from langlearn.languages.german.records.preposition_record import PrepositionRecord
from langlearn.languages.german.records.verb_record import VerbRecord
from langlearn.protocols.domain_model_protocol import LanguageDomainModel


class TestGermanDomainModelFactory:
    """Test German domain model factory functionality."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.german_language = GermanLanguage()

    def test_create_noun_domain_model(self) -> None:
        """Test creating German noun domain model."""
        noun_record = NounRecord(
            noun="Hund",
            article="der",
            english="dog",
            example="Der Hund ist groß",
            plural="die Hunde",
        )

        domain_model = self.german_language.create_domain_model("noun", noun_record)

        # Verify it returns correct type and implements protocol
        assert isinstance(domain_model, Noun)
        assert isinstance(domain_model, LanguageDomainModel)

        # Verify data is preserved correctly - use concrete type assertion
        noun_model = domain_model
        assert isinstance(noun_model, Noun)
        assert noun_model.noun == "Hund"
        assert noun_model.article == "der"
        assert noun_model.english == "dog"
        assert noun_model.example == "Der Hund ist groß"
        assert noun_model.plural == "die Hunde"

        # Verify protocol methods work
        assert "Hund" in domain_model.get_combined_audio_text()
        assert domain_model.get_primary_word() == "Hund"
        assert isinstance(domain_model.get_audio_segments(), dict)

    def test_create_verb_domain_model(self) -> None:
        """Test creating German verb domain model."""
        verb_record = VerbRecord(
            verb="laufen",
            english="to run",
            classification="unregelmäßig",
            present_ich="laufe",
            present_du="läufst",
            present_er="läuft",
            präteritum="lief",
            auxiliary="sein",
            perfect="ist gelaufen",
            example="Ich laufe schnell",
            separable=False,
        )

        domain_model = self.german_language.create_domain_model("verb", verb_record)

        assert isinstance(domain_model, Verb)
        assert isinstance(domain_model, LanguageDomainModel)

        # Access concrete attributes via type assertion
        verb_model = domain_model
        assert isinstance(verb_model, Verb)
        assert verb_model.verb == "laufen"
        assert verb_model.english == "to run"
        assert verb_model.separable is False

    def test_create_adjective_domain_model(self) -> None:
        """Test creating German adjective domain model."""
        adjective_record = AdjectiveRecord(
            word="groß",
            english="big",
            example="Das Haus ist groß",
            comparative="größer",
            superlative="am größten",
        )

        domain_model = self.german_language.create_domain_model(
            "adjective", adjective_record
        )

        assert isinstance(domain_model, Adjective)
        assert isinstance(domain_model, LanguageDomainModel)

        # Access concrete attributes
        adj_model = domain_model
        assert isinstance(adj_model, Adjective)
        assert adj_model.word == "groß"
        assert adj_model.english == "big"

    def test_create_adverb_domain_model(self) -> None:
        """Test creating German adverb domain model."""
        adverb_record = AdverbRecord(
            word="schnell",
            english="quickly",
            type="Modaladverb",
            example="Er läuft schnell",
        )

        domain_model = self.german_language.create_domain_model("adverb", adverb_record)

        assert isinstance(domain_model, Adverb)
        assert isinstance(domain_model, LanguageDomainModel)

        # Access concrete attributes
        adv_model = domain_model
        assert isinstance(adv_model, Adverb)
        assert adv_model.word == "schnell"

    def test_create_negation_domain_model(self) -> None:
        """Test creating German negation domain model."""
        negation_record = NegationRecord(
            word="nicht",
            english="not",
            type="general",
            example="Ich bin nicht müde",
        )

        domain_model = self.german_language.create_domain_model(
            "negation", negation_record
        )

        assert isinstance(domain_model, Negation)
        assert isinstance(domain_model, LanguageDomainModel)

        # Access concrete attributes
        neg_model = domain_model
        assert isinstance(neg_model, Negation)
        assert neg_model.word == "nicht"
        # Compare enum values properly
        from langlearn.languages.german.models.negation import NegationType

        assert (
            neg_model.type == NegationType.GENERAL
        )  # STANDARD_NEGATION maps to GENERAL

    def test_create_phrase_domain_model(self) -> None:
        """Test creating German phrase domain model."""
        phrase_record = PhraseRecord(
            phrase="Guten Tag",
            english="Good day",
            context="Greeting during daytime",
            related="Guten Morgen, Guten Abend",
        )

        domain_model = self.german_language.create_domain_model("phrase", phrase_record)

        assert isinstance(domain_model, Phrase)
        assert isinstance(domain_model, LanguageDomainModel)

        # Access concrete attributes
        phrase_model = domain_model
        assert isinstance(phrase_model, Phrase)
        assert phrase_model.phrase == "Guten Tag"

    def test_create_preposition_domain_model(self) -> None:
        """Test creating German preposition domain model."""
        preposition_record = PrepositionRecord(
            preposition="mit",
            english="with",
            case="Dative",
            example1="Ich gehe mit dir",
            example2="Mit dem Auto fahren",
        )

        domain_model = self.german_language.create_domain_model(
            "preposition", preposition_record
        )

        assert isinstance(domain_model, Preposition)
        assert isinstance(domain_model, LanguageDomainModel)

        # Access concrete attributes
        prep_model = domain_model
        assert isinstance(prep_model, Preposition)
        assert prep_model.preposition == "mit"
        assert prep_model.case == "Dative"

    def test_create_domain_model_unsupported_type(self) -> None:
        """Test creating domain model with unsupported record type."""
        noun_record = NounRecord(
            noun="Test",
            article="der",
            english="test",
            example="Ein Test",
            plural="Tests",
        )

        with pytest.raises(ValueError) as exc_info:
            self.german_language.create_domain_model("unsupported_type", noun_record)

        assert "Unsupported record type 'unsupported_type'" in str(exc_info.value)
        assert "German language" in str(exc_info.value)
        assert "noun" in str(exc_info.value)  # Should list supported types

    def test_all_protocol_methods_implemented(self) -> None:
        """Test that all created domain models fully implement the protocol."""
        test_cases = [
            (
                "noun",
                NounRecord(
                    noun="Katze",
                    article="die",
                    english="cat",
                    example="Die Katze schläft",
                    plural="die Katzen",
                ),
            ),
            (
                "verb",
                VerbRecord(
                    verb="schlafen",
                    english="to sleep",
                    classification="unregelmäßig",
                    present_ich="schlafe",
                    present_du="schläfst",
                    present_er="schläft",
                    präteritum="schlief",
                    auxiliary="haben",
                    perfect="hat geschlafen",
                    example="Ich schlafe",
                    separable=False,
                ),
            ),
            (
                "adjective",
                AdjectiveRecord(
                    word="klein",
                    english="small",
                    example="Das kleine Haus",
                    comparative="kleiner",
                    superlative="am kleinsten",
                ),
            ),
        ]

        for record_type, record in test_cases:
            domain_model = self.german_language.create_domain_model(record_type, record)

            # Test all protocol methods
            audio_text = domain_model.get_combined_audio_text()
            assert isinstance(audio_text, str)
            assert len(audio_text) > 0

            audio_segments = domain_model.get_audio_segments()
            assert isinstance(audio_segments, dict)
            assert len(audio_segments) > 0

            primary_word = domain_model.get_primary_word()
            assert isinstance(primary_word, str)
            assert len(primary_word) > 0

            # Mock AI service for image search strategy test
            from unittest.mock import Mock

            from langlearn.protocols.image_query_generation_protocol import (
                ImageQueryGenerationProtocol,
            )

            mock_ai_service = Mock(spec=ImageQueryGenerationProtocol)
            strategy = domain_model.get_image_search_strategy(mock_ai_service)
            assert callable(strategy)

    def test_domain_model_creation_preserves_record_data(self) -> None:
        """Test that domain model creation preserves all record data correctly."""
        # Use a complex noun record to test data preservation
        noun_record = NounRecord(
            noun="Universität",
            article="die",
            english="university",
            example="Die Universität ist groß",
            plural="die Universitäten",
        )

        domain_model = self.german_language.create_domain_model("noun", noun_record)

        # Verify all record fields are preserved in domain model
        noun_model = domain_model
        assert isinstance(noun_model, Noun)
        assert noun_model.noun == noun_record.noun
        assert noun_model.article == noun_record.article
        assert noun_model.english == noun_record.english
        assert noun_model.example == noun_record.example
        assert noun_model.plural == noun_record.plural

    def test_supported_record_types_match_factory(self) -> None:
        """Test that get_supported_record_types matches factory implementation."""
        supported_types = self.german_language.get_supported_record_types()

        # All supported types should be creatable via factory
        test_records = {
            "noun": NounRecord(
                noun="test",
                article="der",
                english="test",
                example="test",
                plural="tests",
            ),
            "verb": VerbRecord(
                verb="test",
                english="test",
                classification="regelmäßig",
                present_ich="teste",
                present_du="testest",
                present_er="testet",
                präteritum="testete",
                auxiliary="haben",
                perfect="hat getestet",
                example="test",
                separable=False,
            ),
            "adjective": AdjectiveRecord(
                word="test",
                english="test",
                example="test",
                comparative="tester",
                superlative="am testesten",
            ),
            "adverb": AdverbRecord(
                word="test", english="test", type="Modaladverb", example="test"
            ),
            "negation": NegationRecord(
                word="test",
                english="test",
                type="general",
                example="test",
            ),
            "phrase": PhraseRecord(
                phrase="test", english="test", context="test", related="related phrases"
            ),
            "preposition": PrepositionRecord(
                preposition="test",
                english="test",
                case="Accusative",
                example1="test",
                example2="test",
            ),
        }

        for record_type in supported_types:
            if record_type in test_records:
                # Should not raise exception
                domain_model = self.german_language.create_domain_model(
                    record_type, test_records[record_type]
                )
                assert isinstance(domain_model, LanguageDomainModel)
