import unittest

from src.data.tarot_deck import create_standard_deck, get_card_by_id
from src.models.tarot_card import (
    ArcanaType,
    CardPosition,
    Orientation,
    ReadingSession,
    SuitType,
    TarotCard,
)


def build_card(card_id: str = "test_1") -> TarotCard:
    return TarotCard(
        id=card_id,
        name="Test Card",
        suit=SuitType.MAJOR_ARCANA,
        number=1,
        arcana=ArcanaType.MAJOR,
        upright_meaning="Upright",
        reversed_meaning="Reversed",
        keywords=["test", "card"],
        symbolism="Symbolism",
    )


class TestTarotCardUnit(unittest.TestCase):
    def test_valid_tarot_card_creation(self):
        card = build_card()
        self.assertEqual(card.name, "Test Card")
        self.assertEqual(card.get_meaning(Orientation.UPRIGHT), "Upright")
        self.assertEqual(card.get_meaning(Orientation.REVERSED), "Reversed")

    def test_invalid_card_name(self):
        with self.assertRaises(ValueError):
            TarotCard(
                id="x",
                name="",
                suit=SuitType.MAJOR_ARCANA,
                number=1,
                arcana=ArcanaType.MAJOR,
                upright_meaning="Upright",
                reversed_meaning="Reversed",
                keywords=["k"],
                symbolism="s",
            )

    def test_invalid_card_number(self):
        with self.assertRaises(ValueError):
            TarotCard(
                id="x",
                name="A",
                suit=SuitType.MAJOR_ARCANA,
                number=79,
                arcana=ArcanaType.MAJOR,
                upright_meaning="Upright",
                reversed_meaning="Reversed",
                keywords=["k"],
                symbolism="s",
            )


class TestReadingSessionBlackBox(unittest.TestCase):
    def test_valid_session(self):
        position = CardPosition(
            card=build_card(),
            position_index=0,
            position_name="Core",
            position_meaning="Meaning",
            orientation=Orientation.UPRIGHT,
        )
        session = ReadingSession(
            id="session_1",
            question="Is this question valid enough?",
            spread_type="single_card",
            cards_drawn=[position],
            interpretation="Interpretation",
            created_at="2026-01-01T00:00:00Z",
        )
        self.assertEqual(len(session.cards_drawn), 1)

    def test_duplicate_card_rejected(self):
        card = build_card("dup")
        positions = [
            CardPosition(card, 0, "P1", "M1", Orientation.UPRIGHT),
            CardPosition(card, 1, "P2", "M2", Orientation.REVERSED),
        ]
        with self.assertRaises(ValueError):
            ReadingSession(
                id="session_1",
                question="A valid question with enough length.",
                spread_type="three_card",
                cards_drawn=positions,
                interpretation="Interpretation",
                created_at="2026-01-01T00:00:00Z",
            )


class TestReadingSessionWhiteBoxDecisionTable(unittest.TestCase):
    def test_question_boundaries(self):
        position = CardPosition(build_card(), 0, "Core", "Meaning", Orientation.UPRIGHT)
        with self.assertRaises(ValueError):
            ReadingSession("s1", "short", "single_card", [position], "i", "2026-01-01")
        valid_10 = "1234567890"
        session = ReadingSession("s2", valid_10, "single_card", [position], "i", "2026-01-01")
        self.assertEqual(session.question, valid_10)
        too_long = "a" * 501
        with self.assertRaises(ValueError):
            ReadingSession("s3", too_long, "single_card", [position], "i", "2026-01-01")

    def test_feedback_rating_boundaries(self):
        position = CardPosition(build_card(), 0, "Core", "Meaning", Orientation.UPRIGHT)
        ReadingSession(
            "s1",
            "A valid question with enough length.",
            "single_card",
            [position],
            "i",
            "2026-01-01",
            feedback_rating=1,
        )
        ReadingSession(
            "s2",
            "A valid question with enough length.",
            "single_card",
            [position],
            "i",
            "2026-01-01",
            feedback_rating=5,
        )
        with self.assertRaises(ValueError):
            ReadingSession(
                "s3",
                "A valid question with enough length.",
                "single_card",
                [position],
                "i",
                "2026-01-01",
                feedback_rating=0,
            )


class TestDeckUnit(unittest.TestCase):
    def test_standard_deck_properties(self):
        deck = create_standard_deck()
        self.assertEqual(len(deck), 78)
        self.assertEqual(len({c.id for c in deck}), 78)
        self.assertEqual(len({c.number for c in deck}), 78)
        self.assertEqual(len([c for c in deck if c.arcana == ArcanaType.MAJOR]), 22)
        self.assertEqual(len([c for c in deck if c.arcana == ArcanaType.MINOR]), 56)

    def test_get_card_by_id(self):
        card = get_card_by_id("major_0")
        self.assertEqual(card.name, "The Fool")
        with self.assertRaises(ValueError):
            get_card_by_id("not_exists")


if __name__ == "__main__":
    unittest.main()
