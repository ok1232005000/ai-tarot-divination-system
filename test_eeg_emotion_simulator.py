import unittest
from eeg_emotion_simulator import EEGEmotionSimulator

class TestEEGEmotionSimulator(unittest.TestCase):
    def setUp(self):
        self.simulator = EEGEmotionSimulator()
    
    def test_normal_inputs(self):
        # 测试正常输入情况下的情绪判断
        test_cases = [
            # (alpha, beta, theta, expected_emotion)
            (10, 18, 5, "专注"),
            (6, 25, 7, "焦虑"),
            (11, 14, 4, "放松"),
            (7, 13, 7, "疲劳"),
            (9, 16, 4, "专注")
        ]
        
        for alpha, beta, theta, expected_emotion in test_cases:
            result = self.simulator.analyze_emotion(alpha, beta, theta)
            self.assertEqual(result['emotion'], expected_emotion)
            self.assertIn('stress_index', result)
            self.assertIn('suggestion', result)
    
    def test_boundary_values(self):
        # 测试边界值
        # 测试alpha边界
        result1 = self.simulator.analyze_emotion(8, 15, 5)
        result2 = self.simulator.analyze_emotion(12, 15, 5)
        
        # 测试beta边界
        result3 = self.simulator.analyze_emotion(10, 12, 5)
        result4 = self.simulator.analyze_emotion(10, 30, 5)
        
        # 测试theta边界
        result5 = self.simulator.analyze_emotion(10, 15, 4)
        result6 = self.simulator.analyze_emotion(10, 15, 8)
        
        # 确保所有结果都有效
        for result in [result1, result2, result3, result4, result5, result6]:
            self.assertIn('emotion', result)
            self.assertIn('stress_index', result)
            self.assertIn('suggestion', result)
    
    def test_stress_index_calculation(self):
        # 测试压力指数计算
        # 高beta和低alpha应该产生高压力指数
        result1 = self.simulator.analyze_emotion(5, 25, 7)
        self.assertGreater(result1['stress_index'], 70)
        
        # 低beta和高alpha应该产生低压力指数
        result2 = self.simulator.analyze_emotion(11, 13, 4)
        self.assertLess(result2['stress_index'], 40)
    
    def test_invalid_inputs(self):
        # 测试无效输入
        # 非数字输入
        with self.assertRaises(ValueError):
            self.simulator.analyze_emotion("10", 15, 5)
        
        # 负数输入
        with self.assertRaises(ValueError):
            self.simulator.analyze_emotion(-5, 15, 5)
        
        with self.assertRaises(ValueError):
            self.simulator.analyze_emotion(10, -5, 5)
        
        with self.assertRaises(ValueError):
            self.simulator.analyze_emotion(10, 15, -5)

if __name__ == '__main__':
    unittest.main()