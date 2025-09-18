"""Korean grammar service with particle and honorific system support."""

import logging
from typing import Any, ClassVar

logger = logging.getLogger(__name__)


class KoreanParticleService:
    """Service for Korean particle system management."""

    # Common particle mappings
    TOPIC_PARTICLES: ClassVar[dict[str, str]] = {
        "은": "consonant_ending",
        "는": "vowel_ending",
    }
    SUBJECT_PARTICLES: ClassVar[dict[str, str]] = {
        "이": "consonant_ending",
        "가": "vowel_ending",
    }
    OBJECT_PARTICLES: ClassVar[dict[str, str]] = {
        "을": "consonant_ending",
        "를": "vowel_ending",
    }

    # Location and direction particles
    LOCATION_PARTICLES: ClassVar[dict[str, str]] = {
        "에": "at/to (location/time)",
        "에서": "from/at (location of action)",
        "로": "by means of/toward (vowel ending)",
        "으로": "by means of/toward (consonant ending)",
        "까지": "until/as far as",
        "부터": "from (starting point)",
        "와": "with/and (vowel ending)",
        "과": "with/and (consonant ending)",
    }

    @classmethod
    def get_topic_particle(cls, hangul_word: str) -> str:
        """Get appropriate topic particle (은/는) for the word."""
        if cls._ends_with_consonant(hangul_word):
            return f"{hangul_word}은"
        else:
            return f"{hangul_word}는"

    @classmethod
    def get_subject_particle(cls, hangul_word: str) -> str:
        """Get appropriate subject particle (이/가) for the word."""
        if cls._ends_with_consonant(hangul_word):
            return f"{hangul_word}이"
        else:
            return f"{hangul_word}가"

    @classmethod
    def get_object_particle(cls, hangul_word: str) -> str:
        """Get appropriate object particle (을/를) for the word."""
        if cls._ends_with_consonant(hangul_word):
            return f"{hangul_word}을"
        else:
            return f"{hangul_word}를"

    @classmethod
    def _ends_with_consonant(cls, hangul_word: str) -> bool:
        """Check if Korean word ends with a consonant."""
        if not hangul_word:
            return False

        last_char = hangul_word[-1]
        char_code = ord(last_char)

        # Check if it's in the Hangul syllables range (가-힣)
        if 0xAC00 <= char_code <= 0xD7A3:
            # Calculate final consonant (jongseong)
            # Formula: (character_code - base) % 28
            # If result is 0, no final consonant
            final_consonant = (char_code - 0xAC00) % 28
            return final_consonant != 0

        return False


class KoreanCounterService:
    """Service for Korean counter system management."""

    # Common Korean counters with their usage
    COUNTERS: ClassVar[dict[str, str]] = {
        "개": "general objects",
        "명": "people (neutral)",
        "분": "people (honorific)",
        "사람": "people (informal)",
        "마리": "animals",
        "대": "vehicles, machines",
        "장": "flat objects (paper, tickets)",
        "권": "books, magazines",
        "잔": "cups, glasses",
        "병": "bottles",
        "그루": "trees",
        "송이": "flowers, bunches",
        "벌": "sets of clothing",
        "켤레": "pairs (shoes, socks)",
        "채": "buildings, houses",
        "층": "floors of building",
        "번": "times, turns",
    }

    # Category to counter mapping
    CATEGORY_COUNTERS: ClassVar[dict[str, str]] = {
        "person": "명",
        "animal": "마리",
        "object": "개",
        "book": "권",
        "vehicle": "대",
        "building": "채",
        "clothing": "벌",
        "container": "잔",
        "plant": "그루",
    }

    @classmethod
    def get_counter_for_category(cls, category: str) -> str:
        """Get appropriate counter for semantic category."""
        return cls.CATEGORY_COUNTERS.get(category, "개")  # Default to 개

    @classmethod
    def get_counter_examples(cls, noun: str, counter: str) -> list[str]:
        """Generate counting examples with the noun."""
        examples = []
        korean_numbers = ["하나", "둘", "셋", "넷", "다섯"]
        sino_numbers = ["일", "이", "삼", "사", "오"]

        # Use appropriate number system based on counter
        if counter in ["개", "마리", "명"]:  # Use Korean numbers
            for _i, num in enumerate(korean_numbers[:3], 1):
                if counter == "명" and num == "하나":
                    num = "한"  # Special form for people counting
                elif counter == "개" and num == "하나":
                    num = "한"  # Special form for object counting
                examples.append(f"{noun} {num} {counter}")
        else:  # Use Sino-Korean numbers
            for _i, num in enumerate(sino_numbers[:3], 1):
                examples.append(f"{noun} {num} {counter}")

        return examples


class KoreanHonorificService:
    """Service for Korean honorific system management."""

    # Common honorific transformations
    HONORIFIC_FORMS: ClassVar[dict[str, str]] = {
        "사람": "분",  # person -> honorific person
        "나이": "연세",  # age -> honorific age
        "집": "댁",  # house -> honorific house
        "말": "말씀",  # word/speech -> honorific speech
        "이름": "성함",  # name -> honorific name
    }

    # Honorific particles and endings
    HONORIFIC_PARTICLES: ClassVar[dict[str, str]] = {
        "께서": "honorific subject particle (instead of 이/가)",
        "께": "honorific location/direction particle (instead of 에게)",
        "시": "honorific verbal infix",
    }

    @classmethod
    def get_honorific_form(cls, base_word: str) -> str | None:
        """Get honorific form if it exists."""
        return cls.HONORIFIC_FORMS.get(base_word)

    @classmethod
    def has_honorific_form(cls, word: str) -> bool:
        """Check if word has an honorific form."""
        return word in cls.HONORIFIC_FORMS


class KoreanPhonologyService:
    """Service for Korean phonological rules and sound changes."""

    # Consonant cluster simplification rules
    CONSONANT_CLUSTERS: ClassVar[dict[str, str]] = {
        "ㄳ": "ㄱ",  # gs -> g
        "ㄵ": "ㄴ",  # nj -> n
        "ㄶ": "ㄴ",  # nh -> n
        "ㄺ": "ㄱ",  # lg -> g
        "ㄻ": "ㅁ",  # lm -> m
        "ㄼ": "ㄹ",  # lb -> l
        "ㄽ": "ㄹ",  # ls -> l
        "ㄾ": "ㄹ",  # lt -> l
        "ㄿ": "ㄹ",  # lp -> l
        "ㅀ": "ㄹ",  # lh -> l
        "ㅄ": "ㅂ",  # bs -> b
    }

    @classmethod
    def get_pronunciation_notes(cls, hangul_word: str) -> list[str]:
        """Get pronunciation notes for complex consonant clusters."""
        notes = []

        for char in hangul_word:
            if char in cls.CONSONANT_CLUSTERS:
                notes.append(f"{char}: {cls.CONSONANT_CLUSTERS[char]}")

        return notes

    @classmethod
    def analyze_final_consonant(cls, hangul_word: str) -> dict[str, Any]:
        """Analyze the final consonant for particle selection."""
        if not hangul_word:
            return {"has_final": False, "consonant": None}

        last_char = hangul_word[-1]
        char_code = ord(last_char)

        if 0xAC00 <= char_code <= 0xD7A3:
            final_consonant_code = (char_code - 0xAC00) % 28
            has_final = final_consonant_code != 0

            return {
                "has_final": has_final,
                "consonant_code": final_consonant_code if has_final else None,
                "simplified_sound": cls._get_final_consonant_sound(final_consonant_code)
                if has_final
                else None,
            }

        return {"has_final": False, "consonant": None}

    @classmethod
    def _get_final_consonant_sound(cls, consonant_code: int) -> str:
        """Get the actual sound of the final consonant."""
        # Mapping from consonant code to actual pronunciation
        sounds = {
            1: "ㄱ",
            2: "ㄲ",
            3: "ㄳ",
            4: "ㄴ",
            5: "ㄵ",
            6: "ㄶ",
            7: "ㄷ",
            8: "ㄹ",
            9: "ㄺ",
            10: "ㄻ",
            11: "ㄼ",
            12: "ㄽ",
            13: "ㄾ",
            14: "ㄿ",
            15: "ㅀ",
            16: "ㅁ",
            17: "ㅂ",
            18: "ㅄ",
            19: "ㅅ",
            20: "ㅆ",
            21: "ㅇ",
            22: "ㅈ",
            23: "ㅊ",
            24: "ㅋ",
            25: "ㅌ",
            26: "ㅍ",
            27: "ㅎ",
        }
        return sounds.get(consonant_code, "")


def get_particle_forms(hangul_word: str) -> dict[str, str]:
    """Get all particle forms for a Korean word."""
    return {
        "topic": KoreanParticleService.get_topic_particle(hangul_word),
        "subject": KoreanParticleService.get_subject_particle(hangul_word),
        "object": KoreanParticleService.get_object_particle(hangul_word),
        "possessive": f"{hangul_word}의",
    }


def analyze_korean_noun(
    hangul: str, semantic_category: str = "object"
) -> dict[str, Any]:
    """Comprehensive analysis of Korean noun for flashcard creation."""
    return {
        "particles": get_particle_forms(hangul),
        "counter": KoreanCounterService.get_counter_for_category(semantic_category),
        "honorific": KoreanHonorificService.get_honorific_form(hangul),
        "phonology": KoreanPhonologyService.analyze_final_consonant(hangul),
    }


