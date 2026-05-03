class EEGEmotionSimulator:
    def __init__(self):
        self.thresholds = {
            "alpha": {"low": 8, "high": 12},
            "beta": {"low": 12, "high": 30},
            "theta": {"low": 4, "high": 8},
        }

    def analyze_emotion(self, alpha, beta, theta):
        if not all(isinstance(value, (int, float)) for value in [alpha, beta, theta]):
            raise ValueError("输入值必须为数字")
        if any(value < 0 for value in [alpha, beta, theta]):
            raise ValueError("输入值不能为负数")

        stress_index = self._calculate_stress_index(alpha, beta, theta)
        emotion = self._determine_emotion(alpha, beta, theta)
        suggestion = self._generate_suggestion(emotion, stress_index)
        return {"emotion": emotion, "stress_index": stress_index, "suggestion": suggestion}

    def _calculate_stress_index(self, alpha, beta, theta):
        beta_ratio = min(beta / 30, 1.0)
        alpha_ratio = max(1.0 - (alpha / 12), 0.0)
        theta_ratio = min(theta / 8, 1.0)
        stress_index = int((beta_ratio * 0.5 + alpha_ratio * 0.3 + theta_ratio * 0.2) * 100)
        return min(stress_index, 100)

    def _determine_emotion(self, alpha, beta, theta):
        if beta > 20 and alpha < 8:
            return "焦虑"
        if beta < 15 and alpha > 10:
            return "放松"
        if theta > 6 and alpha < 8:
            return "疲劳"
        if beta > 15 and alpha > 8:
            return "专注"
        if theta < 5 and alpha > 9:
            return "平静"
        return "中性"

    def _generate_suggestion(self, emotion, stress_index):
        if stress_index > 70:
            return "建议进行深呼吸练习，适当休息，减少工作压力。"
        if stress_index > 40:
            if emotion == "焦虑":
                return "建议进行冥想或瑜伽，缓解焦虑情绪。"
            if emotion == "疲劳":
                return "建议适当休息，保证充足睡眠。"
            return "建议保持当前状态，注意劳逸结合。"
        return "状态良好，继续保持健康的生活方式。"
