"""AI tarot card interpretation service using Minimax."""
import os
from typing import Any, Dict, List

import requests
import re
from dotenv import load_dotenv

load_dotenv()


class AIInterpreter:
    def __init__(self):
        api_key = os.getenv("MINIMAX_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("MINIMAX_API_KEY or OPENAI_API_KEY not found in environment variables")

        self._api_key = api_key
        self._base_url = os.getenv("MINIMAX_BASE_URL", "https://api.minimaxi.com/v1").rstrip("/")
        self._model = os.getenv("MINIMAX_MODEL", "MiniMax-M2.7")
        self._session = requests.Session()
        self._session.trust_env = False

    def interpret(
        self,
        cards: List[Dict[str, Any]],
        positions: List[Dict[str, str]],
        question: str,
        spread_type: str,
        topic: str = "general",
        tone: str = "warm",
    ) -> str:
        """Generate AI interpretation for drawn tarot cards."""
        prompt = self._build_prompt(cards, positions, question, spread_type, topic, tone)

        try:
            response = self._session.post(
                f"{self._base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self._model,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "你是一位经验丰富、表达克制的中文塔罗解读师。"
                                "请结合牌位、正逆位、问题主题和牌之间的关系，给出具体但不制造恐惧的建议。"
                                "不要声称占卜结果必然发生；涉及健康、法律、财务时提醒用户咨询专业人士。"
                                "输出使用中文，分段清晰，带有神秘但可靠的语气。"
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.72,
                    "max_tokens": 1400,
                },
                timeout=60,
            )
            response.raise_for_status()
            if not response.text.strip():
                return "解读出错：Minimax 返回了空响应，请稍后重试。"

            payload = response.json()
            content = self._extract_content(payload)
            if content:
                content = self._strip_thinking(content)
                return content

            return "解读出错：Minimax 返回内容中没有可展示的解读文本，请检查模型名称或稍后重试。"
        except Exception as e:
            error_msg = str(e)
            if "timed out" in error_msg.lower() or "timeout" in error_msg.lower():
                return "错误：Minimax API 请求超时，请检查网络连接后重试。"
            if "401" in error_msg or "authentication" in error_msg.lower() or "api_key" in error_msg.lower():
                return "错误：API 密钥无效或已过期。"
            if "quota" in error_msg.lower():
                return "错误：API 配额已用尽。"
            if "502" in error_msg or "bad gateway" in error_msg.lower():
                return "错误：Minimax 服务暂时异常，请稍后重试。"
            return f"解读出错：{error_msg}"

    def generate_daily_advice(self, card: Dict[str, Any]) -> str:
        """Generate a daily advice for a single card."""
        orientation = "逆位" if card.get("reversed", False) else "正位"
        card_name = card.get("name", "")
        meaning = card.get("reversed_meaning", "") if card.get("reversed") else card.get("upright_meaning", "")
        keywords = ", ".join(card.get("keywords", [])) if card.get("keywords") else ""

        prompt = f"""今日抽到的牌：{card_name}，{orientation}
牌义：{meaning}
关键词：{keywords}

请给出 2-3 句简洁的今日运势建议，使用温暖但克制的语气。不要制造焦虑，重点给出当日可行的行动提示。回复应该控制在 100 字以内。"""

        try:
            response = self._session.post(
                f"{self._base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self._model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "你是一位简洁高效的中文塔罗解读师，输出简短温暖的每日建议。",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.6,
                    "max_tokens": 300,
                },
                timeout=30,
            )
            response.raise_for_status()
            if not response.text.strip():
                return ""
            payload = response.json()
            content = self._extract_content(payload)
            if content:
                # Remove thinking tags if present
                content = self._strip_thinking(content)
                return content
            return ""
        except Exception as e:
            return ""

    def _extract_content(self, payload: Dict[str, Any]) -> str:
        """Extract assistant text from common OpenAI-compatible response shapes."""
        choices = payload.get("choices") or []
        if choices:
            first = choices[0] or {}
            message = first.get("message") or {}
            content = message.get("content")
            if isinstance(content, str) and content.strip():
                return content.strip()
            if isinstance(content, list):
                parts = [
                    item.get("text", "")
                    for item in content
                    if isinstance(item, dict) and item.get("text")
                ]
                if parts:
                    return "\n".join(parts).strip()
            text = first.get("text")
            if isinstance(text, str) and text.strip():
                return text.strip()

        output = payload.get("output")
        if isinstance(output, str) and output.strip():
            return output.strip()

        return ""

    def _strip_thinking(self, text: str) -> str:
        """Remove thinking blocks from text."""
        import re
        # Correctly strip <think>...</think> blocks.
        # The previous implementation was buggy and too aggressive.
        text = re.sub(r"<thinking>.*?</thinking>", "", text, flags=re.DOTALL)
        return text.strip()

    def _build_prompt(
        self,
        cards: List[Dict[str, Any]],
        positions: List[Dict[str, str]],
        question: str,
        spread_type: str,
        topic: str,
        tone: str,
    ) -> str:
        spread_names = {
            "single_card": "单牌指引",
            "three_card": "三牌牌阵",
            "celtic_cross": "凯尔特十字",
        }
        topic_names = {
            "general": "综合",
            "love": "感情",
            "career": "事业",
            "wealth": "财务",
            "growth": "个人成长",
        }
        tone_names = {
            "warm": "温柔鼓励",
            "direct": "直接清晰",
            "deep": "深入洞察",
        }

        cards_info = []
        for i, card in enumerate(cards):
            orientation = "逆位" if card.get("reversed", False) else "正位"
            pos = positions[i] if i < len(positions) else {}
            pos_name = pos.get("name", f"位置 {i + 1}")
            pos_meaning = pos.get("meaning", "")
            meaning = card.get("reversed_meaning", "") if card.get("reversed") else card.get("upright_meaning", "")
            keywords = ", ".join(card.get("keywords", []))
            cards_info.append(
                f"- {pos_name}（{pos_meaning}）：{card['name']}，{orientation}。牌义参考：{meaning}。关键词：{keywords}"
            )

        return f"""用户问题：{question}

问题主题：{topic_names.get(topic, "综合")}
解读风格：{tone_names.get(tone, "温柔鼓励")}
使用牌阵：{spread_names.get(spread_type, spread_type)}

抽到的牌：
{chr(10).join(cards_info)}

请按以下结构输出：
1. 开场洞察：用 2-3 句话概括这组牌的核心能量。
2. 逐张解读：解释每张牌在对应牌位中的含义。
3. 牌面联结：说明这些牌之间形成的故事、冲突或机会。
4. 行动建议：给出 3 条可以执行的建议。
5. 提醒：用一句话说明塔罗是自我觉察工具，不替代专业决策。

请避免空泛鸡汤，尽量回应用户原问题。"""
