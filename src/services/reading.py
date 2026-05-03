"""Tarot reading service handling card drawing logic."""
from datetime import date
import random
from typing import List, Dict, Any, Tuple

from src.data.tarot_deck import create_standard_deck
from src.models.spread import SPREAD_TEMPLATES, SpreadType


class ReadingService:
    def __init__(self):
        self._deck = create_standard_deck()
        self._shuffled_indices = list(range(len(self._deck)))
        self._shuffled_orientations = [False] * len(self._deck)
        self.shuffle_deck()

    def shuffle_deck(self) -> None:
        """Shuffle the deck and randomize card orientations for blind drawing."""
        random.shuffle(self._shuffled_indices)
        self._shuffled_orientations = [self._is_reversed() for _ in self._deck]

    def get_deck_info(self) -> List[Dict[str, str]]:
        """Get basic info about all 78 cards (for display purposes only)."""
        return [
            {
                "id": card.id,
                "name": card.name,
                "suit": card.suit.value,
                "arcana": card.arcana.value,
                "number": card.number,
            }
            for card in self._deck
        ]

    def get_spread_info(self) -> List[Dict[str, Any]]:
        """Return available spread templates with front-end friendly metadata."""
        return [
            {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "card_count": template.card_count,
                "difficulty": template.difficulty_level.value,
                "usage_instructions": template.usage_instructions,
                "positions": [
                    {
                        "index": position.index,
                        "name": position.name,
                        "meaning": position.meaning,
                        "coordinates": position.coordinates,
                    }
                    for position in template.positions
                ],
            }
            for template in SPREAD_TEMPLATES.values()
        ]

    def get_daily_card(self) -> Dict[str, Any]:
        """Return a stable card for the current calendar day."""
        today = date.today().isoformat()
        rng = random.Random(today)
        card = rng.choice(self._deck)
        is_reversed = rng.choice([True, False])
        return {
            "date": today,
            "id": card.id,
            "name": card.name,
            "number": card.number,
            "suit": card.suit.value,
            "arcana": card.arcana.value,
            "orientation": "reversed" if is_reversed else "upright",
            "reversed": is_reversed,
            "upright_meaning": card.upright_meaning,
            "reversed_meaning": card.reversed_meaning,
            "keywords": card.keywords,
            "symbolism": card.symbolism,
        }

    def get_blind_deck(self) -> List[Dict[str, Any]]:
        """Get deck as blind cards (cards shown face down, user doesn't see which is which)."""
        return [
            {
                "blind_id": idx,  # Internal index, not the actual card
                "position": idx + 1,
            }
            for idx in self._shuffled_indices
        ]

    def reveal_cards(self, blind_ids: List[int]) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
        """Reveal actual cards from blind IDs."""
        if len(blind_ids) <= 0 or len(blind_ids) > len(self._deck):
            raise ValueError(f"Invalid card count: {len(blind_ids)}")

        if any(idx < 0 or idx >= len(self._shuffled_indices) for idx in blind_ids):
            raise ValueError("Invalid blind IDs")

        # Get actual cards from shuffled indices
        actual_cards = [self._deck[self._shuffled_indices[idx]] for idx in blind_ids]
        actual_orientations = [self._shuffled_orientations[idx] for idx in blind_ids]
        spread_type = self._infer_spread_type(len(actual_cards))
        template = SPREAD_TEMPLATES[spread_type]

        cards_data = []
        positions_data = []

        for i, card in enumerate(actual_cards):
            is_reversed = actual_orientations[i]
            orientation = "reversed" if is_reversed else "upright"

            cards_data.append({
                "id": card.id,
                "name": card.name,
                "number": card.number,
                "suit": card.suit.value,
                "arcana": card.arcana.value,
                "orientation": orientation,
                "upright_meaning": card.upright_meaning,
                "reversed_meaning": card.reversed_meaning,
                "reversed": is_reversed,
                "keywords": card.keywords,
                "symbolism": card.symbolism,
            })

            if i < len(template.positions):
                positions_data.append({
                    "index": template.positions[i].index,
                    "name": template.positions[i].name,
                    "meaning": template.positions[i].meaning,
                })

        return cards_data, positions_data

    def _infer_spread_type(self, count: int) -> SpreadType:
        """Infer spread type from card count."""
        if count == 1:
            return SpreadType.SINGLE_CARD
        elif count == 3:
            return SpreadType.THREE_CARD
        elif count == 10:
            return SpreadType.CELTIC_CROSS
        return SpreadType.SINGLE_CARD

    def draw_cards_auto(self, spread_type: SpreadType, count: int) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
        """Draw random cards for the given spread type (auto mode)."""
        if count <= 0 or count > len(self._deck):
            raise ValueError(f"Invalid card count: {count}")

        drawn_indices = random.sample(range(len(self._deck)), count)
        drawn_cards = [self._deck[i] for i in drawn_indices]
        template = SPREAD_TEMPLATES[spread_type]

        cards_data = []
        positions_data = []

        for i, card in enumerate(drawn_cards):
            is_reversed = self._is_reversed()
            orientation = "reversed" if is_reversed else "upright"

            cards_data.append({
                "id": card.id,
                "name": card.name,
                "number": card.number,
                "suit": card.suit.value,
                "arcana": card.arcana.value,
                "orientation": orientation,
                "upright_meaning": card.upright_meaning,
                "reversed_meaning": card.reversed_meaning,
                "reversed": is_reversed,
                "keywords": card.keywords,
                "symbolism": card.symbolism,
            })

            if i < len(template.positions):
                positions_data.append({
                    "index": template.positions[i].index,
                    "name": template.positions[i].name,
                    "meaning": template.positions[i].meaning,
                })

        return cards_data, positions_data

    def _is_reversed(self) -> bool:
        """Return whether a card is reversed with equal upright/reversed odds."""
        return random.choice([True, False])
