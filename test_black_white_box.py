import unittest

from eeg_emotion_simulator import EEGEmotionSimulator


class TestBlackBox(unittest.TestCase):
    def setUp(self):
        self.simulator = EEGEmotionSimulator()

    def test_emotion_detection(self):
        test_cases = [
            (6, 25, 7, "焦虑"),
            (11, 14, 4, "放松"),
            (7, 13, 7, "疲劳"),
            (10, 18, 5, "专注"),
            (9, 16, 4, "专注"),
        ]
        for alpha, beta, theta, expected_emotion in test_cases:
            result = self.simulator.analyze_emotion(alpha, beta, theta)
            self.assertEqual(result["emotion"], expected_emotion)

    def test_stress_index_range(self):
        for alpha, beta, theta in [(5, 30, 8), (12, 12, 4), (8, 15, 6)]:
            result = self.simulator.analyze_emotion(alpha, beta, theta)
            self.assertGreaterEqual(result["stress_index"], 0)
            self.assertLessEqual(result["stress_index"], 100)


class TestWhiteBox(unittest.TestCase):
    def setUp(self):
        self.simulator = EEGEmotionSimulator()

    def test_calculate_stress_index(self):
        self.assertGreater(self.simulator._calculate_stress_index(5, 28, 7), 70)
        self.assertLess(self.simulator._calculate_stress_index(11, 13, 4), 40)
        middle = self.simulator._calculate_stress_index(9, 16, 5)
        self.assertGreater(middle, 40)
        self.assertLess(middle, 70)

    def test_generate_suggestion(self):
        self.assertIn("深呼吸练习", self.simulator._generate_suggestion("焦虑", 80))
        self.assertIn("适当休息", self.simulator._generate_suggestion("疲劳", 60))
        self.assertIn("状态良好", self.simulator._generate_suggestion("放松", 30))


if __name__ == "__main__":
    unittest.main()
