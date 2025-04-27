"""Example script demonstrating how to create a German A1 Anki deck."""

from langlearn.generator import AnkiDeckGenerator, generate_audio


def create_sample_deck() -> None:
    """Create a sample German A1 deck with various types of cards."""
    # Create a new deck generator
    generator = AnkiDeckGenerator("German A1 Goethe-Institut Vocabulary")

    # Add some example words manually
    generator.add_noun(
        noun="Haus",
        article="das",
        english="house",
        plural="Häuser",
        example="Mein Haus ist sehr klein.",
        related="die Wohnung (apartment), das Zimmer (room)",
        audio_filename="Das_ist_mein_Haus._Vicki.mp3",
    )

    generator.add_verb(
        verb="gehen",
        english="to go",
        present_ich="gehe",
        present_du="gehst",
        present_er="geht",
        perfect="ist gegangen",
        example="Ich gehe zur Schule.",
    )

    generator.add_adjective(
        word="klein",
        english="small",
        example="Das ist ein kleines Haus.",
        comparative="kleiner",
    )

    generator.add_preposition(
        preposition="mit",
        english="with",
        case="Dativ",
        example1="Ich fahre mit dem Auto.",
        example2="Sie kommt mit ihrer Freundin.",
    )

    generator.add_phrase(
        phrase="Guten Tag!",
        english="Good day! / Hello!",
        context="Formal greeting, used during the day",
        related="Guten Morgen, Guten Abend",
    )

    # Add audio to a card
    audio_path = generate_audio("Das ist mein Haus.")
    print(f"Generated audio file: {audio_path}")

    # Save the deck to a file
    generator.save_deck("German_A1_Goethe.apkg")


if __name__ == "__main__":
    create_sample_deck()
