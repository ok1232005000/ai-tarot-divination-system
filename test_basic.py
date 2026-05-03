"""Lightweight smoke tests runnable without pytest."""
import sys
import unittest

from src.data.tarot_deck import create_standard_deck
from src.models.spread import SpreadType, validate_card_count


class TestSmoke(unittest.TestCase):
    def test_deck_size(self):
        self.assertEqual(len(create_standard_deck()), 78)

    def test_spread_validation(self):
        self.assertTrue(validate_card_count(SpreadType.SINGLE_CARD, 1))
        self.assertFalse(validate_card_count(SpreadType.CELTIC_CROSS, 9))


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestSmoke)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
