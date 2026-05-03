import unittest

from src.models.spread import (
    DifficultyLevel,
    Position,
    SpreadTemplate,
    SpreadType,
    get_spread_template,
    validate_card_count,
)


class TestSpreadBlackBox(unittest.TestCase):
    def test_predefined_templates(self):
        self.assertEqual(get_spread_template(SpreadType.SINGLE_CARD).card_count, 1)
        self.assertEqual(get_spread_template(SpreadType.THREE_CARD).card_count, 3)
        self.assertEqual(get_spread_template(SpreadType.CELTIC_CROSS).card_count, 10)

    def test_validate_card_count(self):
        self.assertTrue(validate_card_count(SpreadType.THREE_CARD, 3))
        self.assertFalse(validate_card_count(SpreadType.THREE_CARD, 2))


class TestSpreadWhiteBox(unittest.TestCase):
    def test_position_validation(self):
        with self.assertRaises(ValueError):
            Position(-1, "A", "B", {"x": 0.1, "y": 0.2})
        with self.assertRaises(ValueError):
            Position(0, "", "B", {"x": 0.1, "y": 0.2})
        with self.assertRaises(ValueError):
            Position(0, "A", "B", {"x": 0.1})

    def test_template_index_continuity(self):
        positions = [
            Position(0, "A", "A", {"x": 0.1, "y": 0.1}),
            Position(2, "B", "B", {"x": 0.2, "y": 0.2}),
        ]
        with self.assertRaises(ValueError):
            SpreadTemplate(
                id="bad",
                name="Bad",
                description="Bad",
                positions=positions,
                card_count=2,
                difficulty_level=DifficultyLevel.BEGINNER,
                usage_instructions="x",
            )


if __name__ == "__main__":
    unittest.main()
