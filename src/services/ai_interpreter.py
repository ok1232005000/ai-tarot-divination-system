"""AI tarot card interpretation service using Minimax/OpenAI-compatible APIs."""
import json
import logging
import os
import re
import time
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv

load_dotenv()


MAJOR_CARD_NAMES = {
    "The Fool": "愚者",
    "The Magician": "魔术师",
    "The High Priestess": "女祭司",
    "The Empress": "皇后",
    "The Emperor": "皇帝",
    "The Hierophant": "教皇",
    "The Lovers": "恋人",
    "The Chariot": "战车",
    "Strength": "力量",
    "The Hermit": "隐者",
    "Wheel of Fortune": "命运之轮",
    "Justice": "正义",
    "The Hanged Man": "倒吊人",
    "Death": "死神",
    "Temperance": "节制",
    "The Devil": "恶魔",
    "The Tower": "高塔",
    "The Star": "星星",
    "The Moon": "月亮",
    "The Sun": "太阳",
    "Judgement": "审判",
    "The World": "世界",
}

RANK_NAMES = {
    "Ace": "王牌",
    "Two": "二",
    "Three": "三",
    "Four": "四",
    "Five": "五",
    "Six": "六",
    "Seven": "七",
    "Eight": "八",
    "Nine": "九",
    "Ten": "十",
    "Page": "侍从",
    "Knight": "骑士",
    "Queen": "王后",
    "King": "国王",
}

SUIT_NAMES = {
    "Wands": "权杖",
    "Cups": "圣杯",
    "Swords": "宝剑",
    "Pentacles": "星币",
}

POSITION_NAMES = {
    "Core": "核心",
    "Past": "过去",
    "Present": "现在",
    "Future": "未来",
    "Challenge": "挑战",
    "Root": "根源",
    "Recent Past": "近期过去",
    "Potential": "潜在发展",
    "Near Future": "近期未来",
    "Self": "自我状态",
    "Environment": "外部环境",
    "Hopes/Fears": "期待与担忧",
    "Outcome": "结果走向",
}

POSITION_MEANINGS = {
    "The key answer.": "问题的关键答案。",
    "Background factors.": "影响当前状态的背景因素。",
    "Current state.": "你现在正在面对的状态。",
    "Likely direction.": "事情可能发展的方向。",
    "Current core issue.": "当前问题的核心。",
    "Obstacle or tension.": "阻碍、压力或需要面对的张力。",
    "Underlying cause.": "更深层的原因。",
    "Recent influences.": "近期已经发生作用的影响。",
    "Possible near result.": "短期内可能出现的结果。",
    "What comes soon.": "接下来较快会浮现的变化。",
    "Your approach.": "你的态度和应对方式。",
    "External influences.": "外部环境或他人的影响。",
    "Inner expectations.": "内心的期待、担忧或投射。",
    "Overall trajectory.": "整体走向。",
}

SUIT_UPRIGHT_MEANINGS = {
    "Wands": "行动力、热情与主动推进正在成为重点。",
    "Cups": "情绪、人际关系与内在感受需要被认真看见。",
    "Swords": "理性判断、沟通方式和信息取舍会影响结果。",
    "Pentacles": "现实资源、时间安排、金钱或执行细节需要更稳妥。",
}

SUIT_REVERSED_MEANINGS = {
    "Wands": "行动可能被拖延、分散或被一时冲动影响，需要先稳住节奏。",
    "Cups": "情绪容易积压或误读他人反应，适合先厘清自己的真实感受。",
    "Swords": "判断可能受到偏见、压力或沟通不清影响，重要决定要多核对事实。",
    "Pentacles": "现实层面可能有疏漏、资源不足或计划不够落地，需要回到细节。",
}

MAJOR_UPRIGHT_MEANINGS = {
    "The Fool": "新的开始、开放心态与尝试的勇气正在出现。",
    "The Magician": "你拥有把想法落地的工具和主动权。",
    "The High Priestess": "直觉、观察和未说出口的信息很重要。",
    "The Empress": "滋养、创造力和稳定成长是当前主题。",
    "The Emperor": "秩序、边界和清晰安排能带来掌控感。",
    "The Hierophant": "经验、规则或可靠建议值得参考。",
    "The Lovers": "选择、关系与价值观一致性是关键。",
    "The Chariot": "专注目标并控制方向，能推动事情向前。",
    "Strength": "温和但坚定的耐心，比强硬推进更有效。",
    "The Hermit": "暂时退一步思考，会看清真正需要的答案。",
    "Wheel of Fortune": "局势正在变化，顺势调整比固守更重要。",
    "Justice": "公平、事实和后果意识会影响判断。",
    "The Hanged Man": "换个角度或暂缓行动，可能带来新理解。",
    "Death": "旧模式正在结束，留出空间给必要的转变。",
    "Temperance": "平衡、调和和循序渐进会带来稳定。",
    "The Devil": "需要看见执念、依赖或不健康的诱惑。",
    "The Tower": "突发变化会暴露问题，也带来重建机会。",
    "The Star": "希望、恢复和长期愿景正在支持你。",
    "The Moon": "不确定与情绪波动较强，先别急着下结论。",
    "The Sun": "清晰、活力和正向结果更容易显现。",
    "Judgement": "复盘、觉醒和重新选择的时机正在到来。",
    "The World": "阶段性完成、整合与更大格局正在形成。",
}

MAJOR_REVERSED_MEANINGS = {
    "The Fool": "开始前需要多一点准备，避免鲁莽或忽视风险。",
    "The Magician": "资源没有被好好整合，先确认目标和方法是否一致。",
    "The High Priestess": "直觉可能被焦虑干扰，也可能有信息尚未浮现。",
    "The Empress": "过度消耗或缺乏滋养，提醒你先照顾基本需求。",
    "The Emperor": "控制感过强或秩序不足，都可能让事情变僵。",
    "The Hierophant": "别只依赖惯例，确认规则是否真的适合当下。",
    "The Lovers": "选择容易摇摆，关系或价值观需要重新对齐。",
    "The Chariot": "方向感不足或用力过猛，先校准目标再推进。",
    "Strength": "耐心被消耗，容易因急躁而失去柔韧度。",
    "The Hermit": "独处可能变成逃避，需要在思考后重新连接现实。",
    "Wheel of Fortune": "变化不完全可控，先接受波动并保留余地。",
    "Justice": "判断可能失衡，重要事项要回到事实和责任。",
    "The Hanged Man": "停滞太久会消耗机会，需要看清是否该行动。",
    "Death": "抗拒结束会拖慢转变，适合放下已经失效的方式。",
    "Temperance": "节奏失衡，提醒你减少极端做法。",
    "The Devil": "某种执念、压力或依赖正在限制你的自由。",
    "The Tower": "问题可能已在累积，越早调整越能减少冲击。",
    "The Star": "信心不足时，先用小行动恢复方向感。",
    "The Moon": "误解和不安容易放大，先核实信息再回应。",
    "The Sun": "好消息可能被延迟，别因短暂不顺否定整体趋势。",
    "Judgement": "复盘不足会让旧问题重复出现。",
    "The World": "事情尚未完全收尾，需要补齐最后的环节。",
}


class AIInterpreter:
    def __init__(self):
        api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("MINIMAX_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY, MINIMAX_API_KEY, or OPENAI_API_KEY not found in environment variables")

        self._api_key = api_key
        if os.getenv("DEEPSEEK_API_KEY"):
            self._provider = "deepseek"
            default_base_url = "https://api.deepseek.com"
            default_model = "deepseek-v4-flash"
            self._base_url = (os.getenv("DEEPSEEK_BASE_URL") or os.getenv("OPENAI_BASE_URL") or default_base_url).rstrip("/")
            self._model = os.getenv("DEEPSEEK_MODEL") or os.getenv("OPENAI_MODEL") or default_model
            self._fast_model = os.getenv("DEEPSEEK_FAST_MODEL") or self._model
            self._deepseek_thinking = os.getenv("DEEPSEEK_THINKING", "disabled").lower()
        else:
            self._provider = "openai-compatible"
            default_base_url = "https://api.minimaxi.com/v1"
            default_model = "MiniMax-M2.7"
            self._base_url = (os.getenv("MINIMAX_BASE_URL") or os.getenv("OPENAI_BASE_URL") or default_base_url).rstrip("/")
            self._model = os.getenv("MINIMAX_MODEL") or os.getenv("OPENAI_MODEL") or default_model
            self._fast_model = os.getenv("MINIMAX_FAST_MODEL") or self._model
            self._deepseek_thinking = ""
        self._timeout = int(os.getenv("AI_REQUEST_TIMEOUT", "120"))
        self._connect_timeout = int(os.getenv("AI_CONNECT_TIMEOUT", "5"))
        self._session = requests.Session()
        self._session.trust_env = False
        logging.info("[AI Config] provider=%s base_url=%s model=%s", self._provider, self._base_url, self._model)

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
            "max_tokens": 1200,
            "stream": True,
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
                    "stream": True,
                },
                timeout=min(self._timeout, 45),
            )
            return content or self._build_daily_fallback(card)
        except Exception as exc:
            logging.warning("[Daily Advice] Failed to generate advice: %s", exc)
            return self._build_daily_fallback(card)

    def generate_journal_response(self, journal_text: str, daily_card: Dict[str, Any], topic: str = "self") -> str:
        """Generate a reflective companion response for a private tarot journal entry."""
        card_name = daily_card.get("name", "今日牌") if isinstance(daily_card, dict) else "今日牌"
        orientation = "逆位" if isinstance(daily_card, dict) and daily_card.get("reversed") else "正位"
        meaning = ""
        if isinstance(daily_card, dict):
            meaning = daily_card.get("reversed_meaning", "") if daily_card.get("reversed") else daily_card.get("upright_meaning", "")

        prompt = f"""用户今天写下：
{journal_text}

今日抽牌：{card_name}（{orientation}）
牌义参考：{meaning}
自动分类：{topic}

请用中文输出一段“陪伴式塔罗日记回应”。要求：
1. 给今天起一个短标题。
2. 结合今日牌回应用户的情绪，不要说教。
3. 给一个反思问题。
4. 给一个很小、今天就能做的照顾自己的动作。
5. 语气是反思、陪伴、启发，不要包装成心理咨询或绝对预言。
控制在 180-260 字。只输出最终回应，不要输出思考过程。"""

        try:
            content = self._chat_completion(
                {
                    "model": self._fast_model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "你是一个克制、温柔的中文塔罗日记陪伴助手，只做反思和启发，不替代心理咨询。",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.72,
                    "max_tokens": 500,
                    "stream": True,
                },
                timeout=min(self._timeout, 45),
            )
            return content or self._build_journal_fallback(journal_text, card_name, topic)
        except Exception as exc:
            logging.warning("[Journal Response] Failed to generate response: %s", exc)
            return self._build_journal_fallback(journal_text, card_name, topic)

    def generate_monthly_report(self, records: List[Dict[str, Any]], month_label: str = "本月") -> str:
        """Generate an AI monthly tarot report from saved readings."""
        if not records:
            return ""

        compact_records = []
        for record in records[:12]:
            cards = []
            for card in record.get("cards", [])[:10]:
                orientation = "逆位" if card.get("reversed") else "正位"
                cards.append(f"{card.get('name', '')}({orientation})")
            compact_records.append(
                {
                    "date": record.get("createdAt", ""),
                    "question": record.get("question", ""),
                    "topic": record.get("topic", "general"),
                    "spread": record.get("spread", ""),
                    "cards": cards,
                }
            )

        prompt = f"""{month_label}的塔罗记录如下：
{json.dumps(compact_records, ensure_ascii=False)}

请基于这些真实记录，写一份中文月度塔罗报告。要求：
1. 不要套模板，要具体引用重复出现的牌、主题或问题倾向。
2. 包含：本月能量主题、感情/关系关键词、学业/事业提醒、重复出现最多的牌、最常出现的大阿卡那、给本月的你的一封短信。
3. 语气适合年轻用户分享和复盘，但不要绝对预言。
4. 控制在 450-700 字。
只输出最终报告，不要输出思考过程。"""

        try:
            content = self._chat_completion(
                {
                    "model": self._model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "你是一位克制、细腻的中文塔罗复盘报告撰写者，擅长把历史记录总结成具体、温柔、可执行的月度洞察。",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.74,
                    "max_tokens": 1000,
                    "stream": True,
                },
                timeout=self._timeout,
            )
            return content or self._build_monthly_report_fallback(records, month_label)
        except Exception as exc:
            logging.warning("[Monthly Report] Failed to generate report: %s", exc)
            return self._build_monthly_report_fallback(records, month_label)

    def _chat_completion(self, payload: Dict[str, Any], timeout: int) -> str:
        read_timeout = max(1, timeout - self._connect_timeout)
        response = self._post_chat(payload, read_timeout)
        if response.status_code == 429 and str(payload.get("model", "")).endswith("-highspeed"):
            response.close()
            retry_payload = dict(payload)
            retry_payload["model"] = "MiniMax-M2.7"
            response = self._post_chat(retry_payload, read_timeout)
        response.raise_for_status()
        use_stream = bool(payload.get("stream"))
        if use_stream:
            return self._read_streaming_content(response)
        if not response.text.strip():
            return ""
        return self._extract_content(response.json())

    def _post_chat(self, payload: Dict[str, Any], read_timeout: int) -> requests.Response:
        request_payload = dict(payload)
        if self._provider == "deepseek" and self._deepseek_thinking in {"enabled", "disabled"}:
            request_payload.setdefault("thinking", {"type": self._deepseek_thinking})
        use_stream = bool(payload.get("stream"))
        return self._session.post(
            f"{self._base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=(self._connect_timeout, read_timeout),
            stream=use_stream,
        )

    def _read_streaming_content(self, response: requests.Response) -> str:
        parts = []
        finish_reason = None
        started_at = time.monotonic()
        for line in response.iter_lines(decode_unicode=True):
            if time.monotonic() - started_at > self._timeout:
                logging.warning("[AI Interpretation] Stream read exceeded %ss; returning partial content.", self._timeout)
                break
            if not line:
                continue
            line = line.strip()
            if line.startswith("data:"):
                line = line[5:].strip()
            if not line or line == "[DONE]":
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            finish_reason = self._extract_finish_reason(payload) or finish_reason
            content = self._extract_raw_stream_content(payload)
            if content:
                parts.append(content)
        if finish_reason:
            logging.info("[AI Interpretation] Stream finished with reason: %s", finish_reason)
        return self._finalize_stream_text("".join(parts))

    def _finalize_stream_text(self, text: str) -> str:
        text = self._clean_visible_text(text)
        if not text:
            return ""
        if text[-1] in "。！？.!?":
            return text
        for mark in ("。", "！", "？", ".", "!", "?"):
            index = text.rfind(mark)
            if index >= 80:
                text = text[: index + 1]
                break
        return f"{text}\n\n（AI 响应时间较长，以上为本次已完成的解读。）"

    def _extract_finish_reason(self, payload: Dict[str, Any]) -> str:
        choices = payload.get("choices") or []
        if not choices:
            return ""
        first = choices[0] or {}
        reason = first.get("finish_reason")
        return reason if isinstance(reason, str) else ""

    def _extract_raw_stream_content(self, payload: Dict[str, Any]) -> str:
        choices = payload.get("choices") or []
        if not choices:
            return ""
        first = choices[0] or {}
        delta = first.get("delta") or {}
        content = self._content_to_text(delta.get("content"))
        if content:
            return content
        message = first.get("message") or {}
        return self._content_to_text(message.get("content"))

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

    def _display_card_name(self, name: str) -> str:
        if name in MAJOR_CARD_NAMES:
            return MAJOR_CARD_NAMES[name]
        match = re.match(r"^(Ace|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten|Page|Knight|Queen|King) of (Wands|Cups|Swords|Pentacles)$", name)
        if match:
            rank, suit = match.groups()
            return f"{SUIT_NAMES[suit]}{RANK_NAMES[rank]}"
        return name

    def _display_position_name(self, name: str) -> str:
        return POSITION_NAMES.get(name, name)

    def _display_position_meaning(self, meaning: str) -> str:
        return POSITION_MEANINGS.get(meaning, meaning)

    def _display_card_meaning(self, card: Dict[str, Any]) -> str:
        is_reversed = card.get("reversed", False)
        meaning = card.get("reversed_meaning", "") if is_reversed else card.get("upright_meaning", "")
        if meaning and not self._is_placeholder_meaning(meaning):
            return meaning

        name = card.get("name", "")
        if name in MAJOR_CARD_NAMES:
            source = MAJOR_REVERSED_MEANINGS if is_reversed else MAJOR_UPRIGHT_MEANINGS
            return source.get(name, "这张牌提示你关注当下正在变化的核心课题。")

        match = re.match(r"^(Ace|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten|Page|Knight|Queen|King) of (Wands|Cups|Swords|Pentacles)$", name)
        if match:
            _, suit = match.groups()
            source = SUIT_REVERSED_MEANINGS if is_reversed else SUIT_UPRIGHT_MEANINGS
            return source[suit]

        return "这张牌提示你回到现实处境，辨认真正需要处理的重点。"

    def _is_placeholder_meaning(self, meaning: str) -> bool:
        return bool(re.match(r"^(Upright|Reversed) meaning of .+\.$", meaning or ""))

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

请按以下结构输出，控制在 650-900 字内，短但完整：
1. 开场洞察：用 2 句话概括核心能量。
2. 逐张解读：每张牌 2-3 句话，解释它在对应牌位中的含义。
3. 牌面联结：用 1 段说明这些牌之间形成的故事、冲突或机会。
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
            "AI 服务响应较慢，先根据牌面为你生成一版本地解读。",
            "",
            f"你的问题：{question}",
            "",
            "逐张解读：",
        ]
        for index, card in enumerate(cards):
            position = positions[index] if index < len(positions) else {}
            orientation = "逆位" if card.get("reversed", False) else "正位"
            card_name = self._display_card_name(card.get("name", ""))
            pos_name = self._display_position_name(position.get("name", f"位置 {index + 1}"))
            pos_meaning = self._display_position_meaning(position.get("meaning", "当前重点"))
            meaning = self._display_card_meaning(card)
            lines.append(f"{index + 1}. {pos_name}（{pos_meaning}）：{card_name}{orientation}，提示你关注：{meaning}")

        lines.extend(
            [
                "",
                "行动建议：",
                "1. 明天先避免仓促表态，尤其是需要承诺、付款或定计划的事情，先确认事实再回应。",
                "2. 如果遇到沟通阻力，优先把话说清楚、把边界写下来，不要靠猜测推进。",
                "3. 把注意力放在一个能落地的小动作上，例如整理资料、确认时间、补齐细节，而不是一次性解决全部问题。",
            ]
        )
        return "\n".join(lines)

    def _build_journal_fallback(self, journal_text: str, card_name: str, topic: str) -> str:
        title = journal_text.strip().replace("\n", " ")[:14] or "今天的片刻"
        if len(journal_text.strip()) > 14:
            title += "..."
        topic_hint = {
            "感情": "关系里的真实感受",
            "学业/事业": "任务之外的身体负荷",
            "家庭": "亲近关系中的边界",
            "自我": "你对自己的要求",
        }.get(topic, "你当下最需要被看见的部分")
        return (
            f"标题：{title}\n\n"
            f"结合 {card_name}，这段日记更像是在提醒你看见：{topic_hint}。"
            "你不需要立刻把所有情绪整理成答案，先承认此刻的疲惫和混乱，本身就是一种诚实。\n\n"
            "反思问题：今天最消耗你的，是事情本身，还是你一直在心里反复推演它？\n\n"
            "小行动：给自己十分钟，不解决问题，只把下一步能做的一件小事写下来。"
        )

    def _build_monthly_report_fallback(self, records: List[Dict[str, Any]], month_label: str) -> str:
        cards = []
        topics = []
        for record in records:
            topics.append(record.get("topic", "general"))
            cards.extend(record.get("cards", []))
        card_names = [card.get("name", "") for card in cards if card.get("name")]
        major_names = [card.get("name", "") for card in cards if card.get("arcana") == "major"]
        top_card = self._most_common(card_names) or "尚未形成明显重复牌"
        top_major = self._most_common(major_names) or "本月大阿卡那较分散"
        top_topic = self._most_common(topics) or "general"
        topic_labels = {
            "general": "方向与选择",
            "love": "关系、等待与沟通",
            "career": "计划、行动与阶段推进",
            "wealth": "资源、稳定与取舍",
            "growth": "自我觉察与边界",
        }
        theme = topic_labels.get(top_topic, "自我整理")
        return (
            f"{month_label}能量主题：{theme}\n\n"
            f"重复出现最多的牌：{top_card}。最常出现的大阿卡那：{top_major}。\n\n"
            "感情/关系关键词：真实表达、减少脑补、确认边界。若这个月你反复询问关系或情绪问题，牌面更像是在提醒你：不要只在心里推演，也要给现实沟通留出位置。\n\n"
            "学业/事业提醒：把注意力放回可执行的下一步。计划可以小，但要能落地；选择可以慢，但不要一直停在想象里。\n\n"
            "给本月的你：这个月的记录说明，你正在尝试更认真地理解自己。塔罗不是替你决定未来，而是帮你看见哪些情绪、关系和行动模式正在反复出现。下一步，不需要一下子改变全部，只要选一个最常出现的主题，好好回应它。"
        )

    def _most_common(self, values: List[str]) -> str:
        counts = {}
        for value in values:
            if not value:
                continue
            counts[value] = counts.get(value, 0) + 1
        if not counts:
            return ""
        return max(counts.items(), key=lambda item: item[1])[0]

    def _build_daily_fallback(self, card: Dict[str, Any]) -> str:
        orientation = "逆位" if card.get("reversed", False) else "正位"
        meaning = card.get("reversed_meaning", "") if card.get("reversed") else card.get("upright_meaning", "")
        card_name = card.get("name", "今日牌")
        return f"今日牌是{card_name}{orientation}。{meaning} 今天适合放慢节奏，把注意力放在一个可执行的小行动上。"
