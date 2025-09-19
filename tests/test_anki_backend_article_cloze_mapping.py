from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest

from langlearn.infrastructure.backends import AnkiBackend, CardTemplate, NoteType
from langlearn.languages.german.language import GermanLanguage


class StubEnricher:
    def __init__(self, image_name: str = "x.png", audio_name: str = "x.mp3") -> None:
        self.image_name = image_name
        self.audio_name = audio_name

    def enrich_with_media(self, domain_model: Any) -> dict[str, Any]:
        # Return media data to prove wiring works
        return {
            "image": self.image_name,
            "word_audio": self.audio_name,
            "phrase_audio": self.audio_name,  # For articles treated as phrases
        }


@pytest.mark.parametrize(
    "note_type_name",
    [
        "German Artikel Gender Cloze",
        "German Artikel Context Cloze",
    ],
)
def test_cloze_article_backend_mapping_returns_media(
    tmp_path: Path, note_type_name: str, mock_media_service: Mock
) -> None:
    backend = AnkiBackend("Test Deck", mock_media_service, GermanLanguage())

    # Inject stub enricher and an in-memory media service to avoid side effects
    # Monkeypatch the backend's media enricher with a stub that supplies media
    object.__setattr__(backend, "_media_enricher", StubEnricher())

    # Create a minimal note type with the given name
    note_type = NoteType(
        name=note_type_name,
        fields=["Text", "Explanation", "Image", "Audio"],
        templates=[
            CardTemplate(
                name="Card 1", front_html="{{Text}}", back_html="{{Image}}{{Audio}}"
            )
        ],
    )
    note_type_id = backend.create_note_type(note_type)  # returns string id

    # Fields: Text, Explanation, Image, Audio
    fields = ["{{c1::Der}} Mann ist hier", "Maskulin - Geschlecht erkennen", "", ""]

    # Private helper used intentionally for focused mapping test
    processed = backend._process_fields_with_media(note_type_id, fields)

    # Assert mapping preserved text/explanation and filled media
    assert processed[0] == fields[0]
    assert processed[1] == fields[1]
    assert processed[2].startswith('<img src="')
    assert processed[3].startswith("[sound:")
