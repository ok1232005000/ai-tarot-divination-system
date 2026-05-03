"""Tarot domain models."""
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
import uuid


class SuitType(Enum):
    MAJOR_ARCANA = "major_arcana"
    WANDS = "wands"
    CUPS = "cups"
    SWORDS = "swords"
    PENTACLES = "pentacles"


class ArcanaType(Enum):
    MAJOR = "major"
    MINOR = "minor"


class Orientation(Enum):
    UPRIGHT = "upright"
    REVERSED = "reversed"


@dataclass
class TarotCard:
    id: str
    name: str
    suit: SuitType
    number: int
    arcana: ArcanaType
    upright_meaning: str
    reversed_meaning: str
    keywords: List[str]
    symbolism: str
    image_url: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Card name cannot be empty.")
        if not isinstance(self.suit, SuitType):
            raise ValueError("Invalid suit type.")
        if not isinstance(self.arcana, ArcanaType):
            raise ValueError("Invalid arcana type.")
        if not (1 <= self.number <= 78):
            raise ValueError("Card number must be in [1, 78].")
        if not self.upright_meaning or not self.upright_meaning.strip():
            raise ValueError("Upright meaning cannot be empty.")
        if not self.reversed_meaning or not self.reversed_meaning.strip():
            raise ValueError("Reversed meaning cannot be empty.")
        if not self.keywords:
            raise ValueError("Keywords cannot be empty.")
        if not self.symbolism or not self.symbolism.strip():
            raise ValueError("Symbolism cannot be empty.")

    def get_meaning(self, orientation: Orientation) -> str:
        if not isinstance(orientation, Orientation):
            raise ValueError("Invalid orientation.")
        return self.upright_meaning if orientation == Orientation.UPRIGHT else self.reversed_meaning


@dataclass
class CardPosition:
    card: TarotCard
    position_index: int
    position_name: str
    position_meaning: str
    orientation: Orientation

    def __post_init__(self) -> None:
        if not isinstance(self.card, TarotCard):
            raise ValueError("card must be TarotCard.")
        if self.position_index < 0:
            raise ValueError("position_index must be >= 0.")
        if not self.position_name or not self.position_name.strip():
            raise ValueError("position_name cannot be empty.")
        if not self.position_meaning or not self.position_meaning.strip():
            raise ValueError("position_meaning cannot be empty.")
        if not isinstance(self.orientation, Orientation):
            raise ValueError("Invalid orientation.")


@dataclass
class ReadingSession:
    id: str
    question: str
    spread_type: str
    cards_drawn: List[CardPosition]
    interpretation: str
    created_at: str
    feedback_rating: Optional[int] = None
    tags: Optional[List[str]] = None

    def __post_init__(self) -> None:
        q = self.question.strip() if self.question else ""
        if len(q) < 10:
            raise ValueError("Question length must be at least 10.")
        if len(q) > 500:
            raise ValueError("Question length must be <= 500.")
        if not self.spread_type or not self.spread_type.strip():
            raise ValueError("spread_type cannot be empty.")
        if not self.cards_drawn:
            raise ValueError("cards_drawn cannot be empty.")
        if any(not isinstance(pos, CardPosition) for pos in self.cards_drawn):
            raise ValueError("cards_drawn must contain CardPosition.")
        if self.feedback_rating is not None and not (1 <= self.feedback_rating <= 5):
            raise ValueError("feedback_rating must be in [1, 5].")
        card_ids = [pos.card.id for pos in self.cards_drawn]
        if len(card_ids) != len(set(card_ids)):
            raise ValueError("Duplicate cards are not allowed in one session.")

    @classmethod
    def create_new(
        cls,
        question: str,
        spread_type: str,
        cards_drawn: List[CardPosition],
        interpretation: str,
        created_at: str,
    ) -> "ReadingSession":
        return cls(
            id=str(uuid.uuid4()),
            question=question,
            spread_type=spread_type,
            cards_drawn=cards_drawn,
            interpretation=interpretation,
            created_at=created_at,
        )
