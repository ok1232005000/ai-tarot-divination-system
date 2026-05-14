"""AI tarot card interpretation service using Minimax/OpenAI-compatible APIs."""
import json
import logging
import os
import re
from typing import Any, Dict, List

import requests
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
        self._fast_model = os.getenv("MINIMAX_FAST_MODEL", self._model)
        self._timeout = int(os.getenv("AI_REQUEST_TIMEOUT", "75"))
        self._session = requests.Session()

    def interpret(
        self,
        cards: List[Dict[str, Any]],
        positions: List[Dict[str, str]],
        question: str,
        spread_type: str,
        topic: str = "general",
        tone: str = "warm",
    ) -> str:
        """Generate an interpretation for drawn tarot cards."""
        prompt = self._build_prompt(cards, positions, question, spread_type, topic, tone)
        payload = {
            "model": self._model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是一位经验丰富、表达克制的中文塔罗解读师。"
                        "请结合牌位、正逆位、问题主题和牌之间的关系，给出具体但不制造恐慌的建议。"
                        "不要声称占卜结果必然发生；涉及健康、法律、财务时提醒用户咨询专业人士。"
                        "只输出最终解读，不要输出思考过程、推理过程、标签、JSON 或接口元数据。"
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.72,
            "max_tokens": 1400,
            "stream": False,
        }

        try:
            content = self._chat_completion(payload, timeout=self._timeout)
            return content or self._build_fallback_interpretation(cards, positions, question, topic, tone)
        except Exception as exc:
            logging.exception("[AI Interpretation] Failed to generate interpretation: %s", exc)
            return self._build_fallback_interpretation(cards, positions, question, topic, tone)

    def generate_daily_advice(self, card: Dict[str, Any]) -> str:
        """Generate daily advice for a single card."""
        orientation = "逆位" if card.get("reversed", False) else "正位"
        card_name = card.get("name", "")
        meaning = card.get("reversed_meaning", "") if card.get("reversed") else card.get("upright_meaning", "")
        keywords = ", ".join(card.get("keywords", [])) if card.get("keywords") else ""

        prompt = f"""今日抽到的牌：{card_name}，{orientation}
牌义：{meaning}
关键词：{keywords}

请直接给出 2-3 句简洁的今日运势建议，使用温暖但克制的语气。不要制造焦虑，重点给出当日可行的行动提示。回复控制在 100 字以内。
只输出最终建议，不要输出思考过程、推理过程、<think> 标签、JSON 或接口元数据。"""

        try:
            content = self._chat_completion(
                {
                    "model": self._fast_model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "你是一位简洁高效的中文塔罗解读师，只输出简短温暖的每日建议。",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.6,
                    "max_tokens": 300,
                    "stream": False,
                },
                timeout=min(self._timeout, 45),
            )
            return content or self._build_daily_fallback(card)
        except Exception as exc:
            logging.warning("[Daily Advice] Failed to generate advice: %s", exc)
            return self._build_daily_fallback(card)

    def _chat_completion(self, payload: Dict[str, Any], timeout: int) -> str:
        response = self._session.post(
            f"{self._base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=timeout,
        )
        response.raise_for_status()
        if not response.text.strip():
            return ""
        return self._extract_content(response.json())

    def _extract_content(self, payload: Dict[str, Any]) -> str:
        """Extract visible assistant text from common OpenAI-compatible response shapes."""
        choices = payload.get("choices") or []
        if choices:
            first = choices[0] or {}
            message = first.get("message") or {}
            content = self._content_to_text(message.get("content"))
            if content:
                return self._clean_visible_text(content)

            delta = first.get("delta") or {}
            content = self._content_to_text(delta.get("content"))
            if content:
                return self._clean_visible_text(content)

        for key in ("text", "output_text", "reply"):
            content = self._content_to_text(payload.get(key))
            if content:
                return self._clean_visible_text(content)
        return ""

    def _content_to_text(self, content: Any) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict):
                    value = item.get("text") or item.get("content")
                    if isinstance(value, str):
                        parts.append(value)
            return "\n".join(parts)
        return ""

    def _clean_visible_text(self, text: str) -> str:
        """Remove model reasoning, SSE fragments, and metadata before showing text."""
        if not text:
            return ""

        text = text.replace("\r\n", "\n")
        text = re.sub(r"(?is)<think\b[^>]*>.*?</think>", "", text)
        text = re.sub(r"(?is)<thinking\b[^>]*>.*?</thinking>", "", text)
        text = re.sub(r"(?is)<reasoning\b[^>]*>.*?</reasoning>", "", text)
        text = re.sub(r"(?is)<think\b[^>]*>.*\Z", "", text)
        text = re.sub(r"(?is)<thinking\b[^>]*>.*\Z", "", text)
        text = re.sub(r"(?is)<reasoning\b[^>]*>.*\Z", "", text)

        cleaned_lines = []
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped == "[DONE]":
                continue
            if stripped.startswith("data:"):
                stripped = stripped[5:].strip()
                if not stripped or stripped == "[DONE]":
                    continue
                try:
                    stripped = self._extract_content(json.loads(stripped))
                except json.JSONDecodeError:
                    pass
            if re.match(r'(?i)^"?(?:reasoning_content|reasoning|thinking|thoughts)"?\s*[:：]', stripped):
                continue
            cleaned_lines.append(stripped)

        text = "\n".join(cleaned_lines)
        text = re.sub(r"(?i)</?(?:think|thinking|reasoning)[^>]*>", "", text)
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
        for index, card in enumerate(cards):
            orientation = "逆位" if card.get("reversed", False) else "正位"
            position = positions[index] if index < len(positions) else {}
            pos_name = position.get("name", f"位置 {index + 1}")
            pos_meaning = position.get("meaning", "")
            meaning = card.get("reversed_meaning", "") if card.get("reversed") else card.get("upright_meaning", "")
            keywords = ", ".join(card.get("keywords", []))
            cards_info.append(
                f"- {pos_name}（{pos_meaning}）：{card.get('name', '')}，{orientation}。"
                f"牌义参考：{meaning}。关键词：{keywords}"
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

请避免空泛套话，尽量回应用户原问题。"""

    def _build_fallback_interpretation(
        self,
        cards: List[Dict[str, Any]],
        positions: List[Dict[str, str]],
        question: str,
        topic: str,
        tone: str,
    ) -> str:
        lines = [
            "AI 服务暂时不可用，先根据牌面为你生成一版本地解读。",
            "",
            f"你的问题：{question}",
            "",
            "逐张解读：",
        ]
        for index, card in enumerate(cards):
            position = positions[index] if index < len(positions) else {}
            orientation = "逆位" if card.get("reversed", False) else "正位"
            meaning = card.get("reversed_meaning", "") if card.get("reversed") else card.get("upright_meaning", "")
            pos_name = position.get("name", f"位置 {index + 1}")
            pos_meaning = position.get("meaning", "当前重点")
            lines.append(f"{index + 1}. {pos_name}（{pos_meaning}）：{card.get('name', '')}{orientation}，提示你关注：{meaning}")

        lines.extend(
            [
                "",
                "行动建议：",
                "1. 先把问题拆成今天能推进的一小步，避免一次性做过重决定。",
                "2. 留意牌面关键词对应的现实信号，尤其是反复出现的人、资源或阻力。",
                "3. 如果问题涉及健康、法律或财务，请把这次解读当作自我梳理，并咨询专业人士。",
            ]
        )
        return "\n".join(lines)

    def _build_daily_fallback(self, card: Dict[str, Any]) -> str:
        orientation = "逆位" if card.get("reversed", False) else "正位"
        meaning = card.get("reversed_meaning", "") if card.get("reversed") else card.get("upright_meaning", "")
        card_name = card.get("name", "今日牌")
        return f"今日牌是{card_name}{orientation}。{meaning} 今天适合放慢节奏，把注意力放在一个可执行的小行动上。"
