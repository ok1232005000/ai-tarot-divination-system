import unittest

from eeg_emotion_simulator import EEGEmotionSimulator
from src.models.tarot_card import ArcanaType, CardPosition, Orientation, ReadingSession, SuitType, TarotCard


class TestDecisionTableCases(unittest.TestCase):
    def setUp(self):
        self.simulator = EEGEmotionSimulator()
        self.card = TarotCard(
            id="d1",
            name="Decision Card",
            suit=SuitType.MAJOR_ARCANA,
            number=1,
            arcana=ArcanaType.MAJOR,
            upright_meaning="U",
            reversed_meaning="R",
            keywords=["k1"],
            symbolism="S",
        )

    def test_emotion_decision_table(self):
        table = [
            ((6, 25, 7), "焦虑"),
            ((11, 14, 4), "放松"),
            ((7, 13, 7), "疲劳"),
            ((10, 18, 5), "专注"),
            ((11, 13, 5), "放松"),
        ]
        for inputs, expected in table:
            with self.subTest(inputs=inputs):
                self.assertEqual(self.simulator.analyze_emotion(*inputs)["emotion"], expected)

    def test_reading_session_decision_table(self):
        pos = CardPosition(self.card, 0, "Core", "Meaning", Orientation.UPRIGHT)
        valid_question = "A valid question over ten chars."
        ReadingSession("ok", valid_question, "single_card", [pos], "i", "2026-01-01")
        with self.assertRaises(ValueError):
            ReadingSession("short", "short", "single_card", [pos], "i", "2026-01-01")
        with self.assertRaises(ValueError):
            ReadingSession("none", valid_question, "", [pos], "i", "2026-01-01")
        with self.assertRaises(ValueError):
            ReadingSession("nocard", valid_question, "single_card", [], "i", "2026-01-01")


if __name__ == "__main__":
    unittest.main()
