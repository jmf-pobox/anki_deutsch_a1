from pathlib import Path
from typing import Any

import pytest

from langlearn.backends import AnkiBackend, CardTemplate, NoteType


class StubEnricher:
    def __init__(self, image_name: str = "x.png", audio_name: str = "x.mp3") -> None:
        self.image_name = image_name
        self.audio_name = audio_name

    def enrich_record(
        self, record: dict[str, Any], domain_model: Any
    ) -> dict[str, Any]:
        # Return the same record with non-empty media to prove wiring
        enriched = dict(record)
        enriched.setdefault("image", f'<img src="{self.image_name}">')
        enriched.setdefault("audio", f"[sound:{self.audio_name}]")
        return enriched


@pytest.mark.parametrize(
    "note_type_name",
    [
        "German Artikel Gender Cloze",
        "German Artikel Context Cloze",
    ],
)
def test_cloze_article_backend_mapping_returns_media(
    tmp_path: Path, note_type_name: str
) -> None:
    backend = AnkiBackend("Test Deck")

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
