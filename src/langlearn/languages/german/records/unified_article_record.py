"""UnifiedArticleRecord for unified German articles from CSV."""

from dataclasses import dataclass
from typing import Any

from langlearn.core.records import BaseRecord, RecordType


@dataclass
class UnifiedArticleRecord(BaseRecord):
    """Record for unified German articles from CSV with German terminology."""

    artikel_typ: str
    geschlecht: str
    nominativ: str
    akkusativ: str
    dativ: str
    genitiv: str
    beispiel_nom: str
    beispiel_akk: str
    beispiel_dat: str
    beispiel_gen: str

    # Media fields (populated during enrichment)
    article_audio: str | None = None
    example_audio: str | None = None
    image: str | None = None

    def __post_init__(self) -> None:
        """Post-init validation for dataclass."""
        self.validate()

    def validate(self) -> None:
        """Validate the record after initialization."""
        # Validate article type
        valid_types = {"bestimmt", "unbestimmt", "verneinend"}
        if self.artikel_typ not in valid_types:
            raise ValueError(
                f"Invalid artikel_typ: {self.artikel_typ}. Must be one of {valid_types}"
            )

        # Validate gender
        valid_genders = {"maskulin", "feminin", "neutral", "plural"}
        if self.geschlecht not in valid_genders:
            raise ValueError(
                f"Invalid geschlecht: {self.geschlecht}. Must be one of {valid_genders}"
            )

    @classmethod
    def get_record_type(cls) -> RecordType:
        """Return the record type for unified articles."""
        return RecordType.UNIFIED_ARTICLE

    @classmethod
    def get_expected_field_count(cls) -> int:
        """Number of fields expected from CSV."""
        return 10

    @classmethod
    def from_csv_fields(cls, fields: list[str]) -> "UnifiedArticleRecord":
        """Create UnifiedArticleRecord from CSV fields."""
        if len(fields) != cls.get_expected_field_count():
            expected = cls.get_expected_field_count()
            raise ValueError(
                f"UnifiedArticleRecord expects {expected} fields, got {len(fields)}"
            )

        return cls(
            artikel_typ=fields[0].strip(),
            geschlecht=fields[1].strip(),
            nominativ=fields[2].strip(),
            akkusativ=fields[3].strip(),
            dativ=fields[4].strip(),
            genitiv=fields[5].strip(),
            beispiel_nom=fields[6].strip(),
            beispiel_akk=fields[7].strip(),
            beispiel_dat=fields[8].strip(),
            beispiel_gen=fields[9].strip(),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for media enrichment."""
        return {
            "artikel_typ": self.artikel_typ,
            "geschlecht": self.geschlecht,
            "nominativ": self.nominativ,
            "akkusativ": self.akkusativ,
            "dativ": self.dativ,
            "genitiv": self.genitiv,
            "beispiel_nom": self.beispiel_nom,
            "beispiel_akk": self.beispiel_akk,
            "beispiel_dat": self.beispiel_dat,
            "beispiel_gen": self.beispiel_gen,
            "article_audio": self.article_audio,
            "example_audio": self.example_audio,
            "image": self.image,
        }

    @classmethod
    def get_field_names(cls) -> list[str]:
        """Field names for unified article CSV."""
        return [
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

    # Compatibility properties for legacy ArticlePatternProcessor
    @property
    def gender(self) -> str:
        """Legacy compatibility: geschlecht -> gender."""
        return self.geschlecht

    @property
    def nominative(self) -> str:
        """Legacy compatibility: nominativ -> nominative."""
        return self.nominativ

    @property
    def accusative(self) -> str:
        """Legacy compatibility: akkusativ -> accusative."""
        return self.akkusativ

    @property
    def dative(self) -> str:
        """Legacy compatibility: dativ -> dative."""
        return self.dativ

    @property
    def genitive(self) -> str:
        """Legacy compatibility: genitiv -> genitive."""
        return self.genitiv

    @property
    def example_nom(self) -> str:
        """Legacy compatibility: beispiel_nom -> example_nom."""
        return self.beispiel_nom

    @property
    def example_acc(self) -> str:
        """Legacy compatibility: beispiel_akk -> example_acc."""
        return self.beispiel_akk

    @property
    def example_dat(self) -> str:
        """Legacy compatibility: beispiel_dat -> example_dat."""
        return self.beispiel_dat

    @property
    def example_gen(self) -> str:
        """Legacy compatibility: beispiel_gen -> example_gen."""
        return self.beispiel_gen

    def get_image_search_strategy(self) -> str:
        """Get image search strategy for media generation.

        Returns the most representative example for image searches.
        Uses nominative example as it's typically the clearest form.
        """
        return self.beispiel_nom

    def get_combined_audio_text(self) -> str:
        """Get combined text for audio generation.

        Returns the nominative example as the primary audio content
        since it represents the most basic article usage.
        """
        return self.beispiel_nom
