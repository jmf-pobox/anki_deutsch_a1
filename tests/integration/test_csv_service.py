"""Tests for the CSV data provider service."""

from pathlib import Path

from langlearn.models.adjective import Adjective
from langlearn.models.noun import Noun
from langlearn.models.preposition import Preposition
from langlearn.models.verb import Verb
from langlearn.services.csv_service import CSVService


def test_read_nouns(tmp_path: Path) -> None:
    """Test reading nouns from a CSV file."""
    # Create a temporary CSV file
    csv_content = """noun,article,english,plural,example,related
Haus,das,house,Häuser,Mein Haus ist sehr klein.,die Wohnung (apartment)
Mann,der,man,Männer,Der Mann geht zur Arbeit.,die Frau (woman)"""

    csv_file = tmp_path / "test_nouns.csv"
    csv_file.write_text(csv_content)

    # Create CSV service and read nouns
    service = CSVService()
    nouns = service.read_csv(csv_file, Noun)

    # Verify results
    assert len(nouns) == 2
    assert isinstance(nouns[0], Noun)
    assert nouns[0].noun == "Haus"
    assert nouns[0].article == "das"
    assert nouns[0].english == "house"
    assert nouns[0].plural == "Häuser"
    assert nouns[0].example == "Mein Haus ist sehr klein."
    assert nouns[0].related == "die Wohnung (apartment)"


def test_read_verbs(tmp_path: Path) -> None:
    """Test reading verbs from a CSV file."""
    # Create a temporary CSV file
    csv_content = """verb,english,present_ich,present_du,present_er,perfect,example
sein,to be,bin,bist,ist,ist gewesen,Ich bin zu Hause.
haben,to have,habe,hast,hat,hat gehabt,Ich habe ein Buch."""

    csv_file = tmp_path / "test_verbs.csv"
    csv_file.write_text(csv_content)

    # Create CSV service and read verbs
    service = CSVService()
    verbs = service.read_csv(csv_file, Verb)

    # Verify results
    assert len(verbs) == 2
    assert isinstance(verbs[0], Verb)
    assert verbs[0].verb == "sein"
    assert verbs[0].english == "to be"
    assert verbs[0].present_ich == "bin"
    assert verbs[0].present_du == "bist"
    assert verbs[0].present_er == "ist"
    assert verbs[0].perfect == "ist gewesen"
    assert verbs[0].example == "Ich bin zu Hause."


def test_read_prepositions(tmp_path: Path) -> None:
    """Test reading prepositions from a CSV file."""
    # Create a temporary CSV file
    csv_content = (
        "preposition,english,case,example1,example2\n"
        "in,in,Akkusativ/Dativ,Ich gehe in die Schule. (ACC),"
        "Ich bin in der Schule. (DAT)\n"
        "auf,on,Akkusativ/Dativ,Ich lege das Buch auf den Tisch. (ACC),"
        '"Das Buch liegt auf dem Tisch. (DAT)"'
    )

    csv_file = tmp_path / "test_prepositions.csv"
    csv_file.write_text(csv_content)

    # Create CSV service and read prepositions
    service = CSVService()
    prepositions = service.read_csv(csv_file, Preposition)

    # Verify results
    assert len(prepositions) == 2
    assert isinstance(prepositions[0], Preposition)
    assert prepositions[0].preposition == "in"
    assert prepositions[0].english == "in"
    assert prepositions[0].case == "Akkusativ/Dativ"
    assert prepositions[0].example1 == "Ich gehe in die Schule. (ACC)"
    assert prepositions[0].example2 == "Ich bin in der Schule. (DAT)"


def test_read_adjectives(tmp_path: Path) -> None:
    """Test reading adjectives from a CSV file."""
    # Create a temporary CSV file
    csv_content = """word,english,example,comparative,superlative
groß,big/tall,Er ist sehr groß.,größer,am größten
klein,small,Meine Wohnung ist klein.,kleiner,am kleinsten"""

    csv_file = tmp_path / "test_adjectives.csv"
    csv_file.write_text(csv_content)

    # Create CSV service and read adjectives
    service = CSVService()
    adjectives = service.read_csv(csv_file, Adjective)

    # Verify results
    assert len(adjectives) == 2
    assert isinstance(adjectives[0], Adjective)
    assert adjectives[0].word == "groß"
    assert adjectives[0].english == "big/tall"
    assert adjectives[0].example == "Er ist sehr groß."
    assert adjectives[0].comparative == "größer"
    assert adjectives[0].superlative == "am größten"
