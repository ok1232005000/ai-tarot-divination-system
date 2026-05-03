"""Spread templates and validations."""
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class SpreadType(Enum):
    SINGLE_CARD = "single_card"
    THREE_CARD = "three_card"
    CELTIC_CROSS = "celtic_cross"


class DifficultyLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass
class Position:
    index: int
    name: str
    meaning: str
    coordinates: Dict[str, float]

    def __post_init__(self) -> None:
        if self.index < 0:
            raise ValueError("index must be >= 0.")
        if not self.name or not self.name.strip():
            raise ValueError("name cannot be empty.")
        if not self.meaning or not self.meaning.strip():
            raise ValueError("meaning cannot be empty.")
        if not isinstance(self.coordinates, dict):
            raise ValueError("coordinates must be dict.")
        if "x" not in self.coordinates or "y" not in self.coordinates:
            raise ValueError("coordinates must contain x and y.")


@dataclass
class SpreadTemplate:
    id: str
    name: str
    description: str
    positions: List[Position]
    card_count: int
    difficulty_level: DifficultyLevel
    usage_instructions: str

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("name cannot be empty.")
        if not self.description or not self.description.strip():
            raise ValueError("description cannot be empty.")
        if self.card_count <= 0:
            raise ValueError("card_count must be > 0.")
        if len(self.positions) != self.card_count:
            raise ValueError("positions count must equal card_count.")
        if not isinstance(self.difficulty_level, DifficultyLevel):
            raise ValueError("invalid difficulty_level.")
        indices = [p.index for p in self.positions]
        if len(indices) != len(set(indices)):
            raise ValueError("position indices must be unique.")
        if set(indices) != set(range(len(self.positions))):
            raise ValueError("position indices must be continuous from 0.")


SPREAD_TEMPLATES = {
    SpreadType.SINGLE_CARD: SpreadTemplate(
        id="single_card",
        name="Single Card",
        description="Draw one card for a quick answer.",
        positions=[Position(0, "Core", "The key answer.", {"x": 0.5, "y": 0.5})],
        card_count=1,
        difficulty_level=DifficultyLevel.BEGINNER,
        usage_instructions="Focus on one clear question.",
    ),
    SpreadType.THREE_CARD: SpreadTemplate(
        id="three_card",
        name="Three Card",
        description="Past, present and future.",
        positions=[
            Position(0, "Past", "Background factors.", {"x": 0.2, "y": 0.5}),
            Position(1, "Present", "Current state.", {"x": 0.5, "y": 0.5}),
            Position(2, "Future", "Likely direction.", {"x": 0.8, "y": 0.5}),
        ],
        card_count=3,
        difficulty_level=DifficultyLevel.BEGINNER,
        usage_instructions="Interpret cards as a timeline.",
    ),
    SpreadType.CELTIC_CROSS: SpreadTemplate(
        id="celtic_cross",
        name="Celtic Cross",
        description="Detailed 10-card diagnostic spread.",
        positions=[
            Position(0, "Present", "Current core issue.", {"x": 0.5, "y": 0.5}),
            Position(1, "Challenge", "Obstacle or tension.", {"x": 0.5, "y": 0.3}),
            Position(2, "Root", "Underlying cause.", {"x": 0.3, "y": 0.5}),
            Position(3, "Recent Past", "Recent influences.", {"x": 0.5, "y": 0.7}),
            Position(4, "Potential", "Possible near result.", {"x": 0.7, "y": 0.5}),
            Position(5, "Near Future", "What comes soon.", {"x": 0.5, "y": 0.1}),
            Position(6, "Self", "Your approach.", {"x": 0.9, "y": 0.8}),
            Position(7, "Environment", "External influences.", {"x": 0.9, "y": 0.6}),
            Position(8, "Hopes/Fears", "Inner expectations.", {"x": 0.9, "y": 0.4}),
            Position(9, "Outcome", "Overall trajectory.", {"x": 0.9, "y": 0.2}),
        ],
        card_count=10,
        difficulty_level=DifficultyLevel.ADVANCED,
        usage_instructions="Use for complex questions and deep interpretation.",
    ),
}


def get_spread_template(spread_type: SpreadType) -> SpreadTemplate:
    if spread_type not in SPREAD_TEMPLATES:
        raise ValueError(f"Unsupported spread type: {spread_type}")
    return SPREAD_TEMPLATES[spread_type]


def validate_card_count(spread_type: SpreadType, actual_count: int) -> bool:
    return get_spread_template(spread_type).card_count == actual_count
