"""Standard tarot deck data helpers."""
from typing import List

from src.models.tarot_card import ArcanaType, SuitType, TarotCard


def _build_major_arcana() -> List[TarotCard]:
    major_names = [
        "The Fool",
        "The Magician",
        "The High Priestess",
        "The Empress",
        "The Emperor",
        "The Hierophant",
        "The Lovers",
        "The Chariot",
        "Strength",
        "The Hermit",
        "Wheel of Fortune",
        "Justice",
        "The Hanged Man",
        "Death",
        "Temperance",
        "The Devil",
        "The Tower",
        "The Star",
        "The Moon",
        "The Sun",
        "Judgement",
        "The World",
    ]
    cards: List[TarotCard] = []
    for index, name in enumerate(major_names):
        cards.append(
            TarotCard(
                id=f"major_{index}",
                name=name,
                suit=SuitType.MAJOR_ARCANA,
                number=index + 1,
                arcana=ArcanaType.MAJOR,
                upright_meaning=f"Upright meaning of {name}.",
                reversed_meaning=f"Reversed meaning of {name}.",
                keywords=[name.split()[0].lower(), "major", "insight"],
                symbolism=f"{name} symbolizes a key stage in growth.",
            )
        )
    return cards


def _build_minor_suit(suit: SuitType, start_number: int) -> List[TarotCard]:
    ranks = [
        "Ace",
        "Two",
        "Three",
        "Four",
        "Five",
        "Six",
        "Seven",
        "Eight",
        "Nine",
        "Ten",
        "Page",
        "Knight",
        "Queen",
        "King",
    ]
    cards: List[TarotCard] = []
    for index, rank in enumerate(ranks):
        name = f"{rank} of {suit.value.title()}"
        cards.append(
            TarotCard(
                id=f"{suit.value}_{index + 1}",
                name=name,
                suit=suit,
                number=start_number + index,
                arcana=ArcanaType.MINOR,
                upright_meaning=f"Upright meaning of {name}.",
                reversed_meaning=f"Reversed meaning of {name}.",
                keywords=[rank.lower(), suit.value, "minor"],
                symbolism=f"{name} reflects practical life themes.",
            )
        )
    return cards


def create_standard_deck() -> List[TarotCard]:
    deck = _build_major_arcana()
    deck.extend(_build_minor_suit(SuitType.WANDS, 23))
    deck.extend(_build_minor_suit(SuitType.CUPS, 37))
    deck.extend(_build_minor_suit(SuitType.SWORDS, 51))
    deck.extend(_build_minor_suit(SuitType.PENTACLES, 65))
    return deck


def get_card_by_id(card_id: str) -> TarotCard:
    for card in create_standard_deck():
        if card.id == card_id:
            return card
    raise ValueError(f"Card not found: {card_id}")


def get_cards_by_suit(suit: SuitType) -> List[TarotCard]:
    return [card for card in create_standard_deck() if card.suit == suit]


def get_cards_by_arcana(arcana: ArcanaType) -> List[TarotCard]:
    return [card for card in create_standard_deck() if card.arcana == arcana]
