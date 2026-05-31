"""MAGI System - Core judgment + consult logic"""

import asyncio
import os
import re
import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional

from openai import AsyncOpenAI


class Decision(Enum):
    APPROVE = "approve"
    DENY = "deny"
    ABSTAIN = "abstain"


UNIT_CONFIG = {
    "melchior": {
        "codename": "MELCHIOR-01",
        "role": "科学家",
        "color": "#00d4ff",
        "prompt": (
            "你是 MELCHIOR-01，MAGI 系统的第一单元——科学家。"
            "你以绝对理性、数据驱动和逻辑推演来分析问题。"
            "请基于事实、数据和逻辑链给出你的判断。"
            "明确在回答结尾用【承认】、【否认】或【弃权】标明你的决定。"
        ),
    },
    "balthasar": {
        "codename": "BALTHASAR-02",
        "role": "母亲",
        "color": "#ff69b4",
        "prompt": (
            "你是 BALTHASAR-02，MAGI 系统的第二单元——母亲。"
            "你以关怀保护、伦理道德和社会影响来审视问题。"
            "请基于伦理、道德和社会责任感给出你的判断。"
            "明确在回答结尾用【承认】、【否认】或【弃权】标明你的决定。"
        ),
    },
    "casper": {
        "codename": "CASPER-03",
        "role": "女人",
        "color": "#ffd700",
        "prompt": (
            "你是 CASPER-03，MAGI 系统的第三单元——女人。"
            "你以直觉判断、情感感知和人性复杂性来洞察问题。"
            "请基于直觉、情感和人性洞察给出你的判断。"
            "明确在回答结尾用【承认】、【否认】或【弃权】标明你的决定。"
        ),
    },
}

# Thinking tag markers (ASCII-safe for Python 3.10 re compatibility)
THINK_START = "<think>"
THINK_END = "</think>"


@dataclass
class Vote:
    unit: str
    codename: str
    role: str
    decision: Decision
    reasoning: str
    thinking: str = ""
    confidence: float = 0.0
    latency_ms: int = 0


@dataclass
class Judgment:
    question: str
    votes: list[Vote] = field(default_factory=list)
    final_decision: Decision = Decision.DENY
    consensus: str = ""
    total_latency_ms: int = 0


@dataclass
class ConsultResult:
    unit: str
    codename: str
    role: str
    response: str
    thinking: str = ""
    confidence: float = 0.0
    latency_ms: int = 0


def _extract_thinking(text: str) -> tuple[str, str]:
    """Split <think>...</think> block from response. Returns (thinking, rest)."""
    pattern = re.escape(THINK_START) + r"(.*?)" + re.escape(THINK_END)
    m = re.search(pattern, text, re.DOTALL)
    if m:
        thinking = m.group(1).strip()
        rest = (text[:m.start()] + text[m.end():]).strip()
        return thinking, rest
    return "", text


def _parse_decision(text: str) -> tuple[Decision, str, str, float]:
    """Parse LLM response -> (decision, reasoning, thinking, confidence)."""
    thinking, body = _extract_thinking(text)
    conf = 0.8

    tail = body[-40:] if len(body) > 40 else body
    if "承认" in tail:
        dec = Decision.APPROVE
    elif "否认" in tail:
        dec = Decision.DENY
    elif "弃权" in tail:
        dec = Decision.ABSTAIN
    else:
        a = body.lower().count("承认")
        d = body.lower().count("否认")
        dec = Decision.APPROVE if a > d else (Decision.DENY if d > a else Decision.ABSTAIN)

    m = re.search(r'(?:置信度|confidence|conf)[:\s]*(\d+\.?\d*)', body, re.I)
    if m:
        conf = min(1.0, max(0.0, float(m.group(1))))

    return dec, body, thinking, conf


def _parse_consult(text: str) -> tuple[str, str, float]:
    """Parse consult response -> (response, thinking, confidence)."""
    thinking, body = _extract_thinking(text)
    conf = 0.8
    m = re.search(r'(?:置信度|confidence|conf)[:\s]*(\d+\.?\d*)', body, re.I)
    if m:
        conf = min(1.0, max(0.0, float(m.group(1))))
    return body, thinking, conf


class MagiSystem:
    def __init__(self):
        self.units = {uid: UNIT_CONFIG[uid] for uid in UNIT_CONFIG}

    def _get_unit_env(self, unit_id: str) -> tuple[str, str, str]:
        uid = unit_id.upper()
        base = os.getenv(f"MAGI_{uid}_API_BASE",
                         os.getenv("MAGI_API_BASE", "https://api.vveai.com/v1"))
        key = os.getenv(f"MAGI_{uid}_API_KEY",
                        os.getenv("MAGI_API_KEY", ""))
        model = os.getenv(f"MAGI_{uid}_MODEL",
                          os.getenv("MAGI_MODEL", "deepseek-v4-pro"))
        return base, key, model

    def _resolve_creds(self, unit_id: str, user_key=None, user_base=None, global_config=None):
        """Priority: user key -> global config -> env."""
        env_base, env_key, env_model = self._get_unit_env(unit_id)

        g_base, g_key = env_base, env_key
        if global_config and isinstance(global_config, dict):
            g_base = global_config.get("api_base") or env_base
            g_key = global_config.get("api_key") or env_key
            g_units = global_config.get("units", {})
            if unit_id in g_units:
                gu = g_units[unit_id]
                g_base = gu.get("api_base", g_base)
                g_key = gu.get("api_key", g_key)
                env_model = gu.get("model", env_model)

        final_key = user_key or g_key or env_key
        final_base = user_base or g_base or env_base
        return final_base, final_key, env_model

    def _effort_kwargs(self, reasoning_effort: Optional[str] = None) -> dict:
        if reasoning_effort and reasoning_effort in ("low", "medium", "high"):
            return {"extra_body": {"reasoning_effort": reasoning_effort}}
        return {}

    async def _call_unit(self, unit_id: str, question: str,
                         user_key=None, user_base=None, global_config=None,
                         reasoning_effort=None) -> tuple[str, int]:
        base, key, model = self._resolve_creds(unit_id, user_key, user_base, global_config)
        client = AsyncOpenAI(api_key=key, base_url=base)
        cfg = self.units[unit_id]
        ek = self._effort_kwargs(reasoning_effort)
        t0 = time.time()
        resp = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": cfg["prompt"]},
                {"role": "user", "content": question},
            ],
            **ek,
        )
        elapsed = int((time.time() - t0) * 1000)
        return resp.choices[0].message.content or "", elapsed

    async def _judge_unit(self, unit_id: str, question: str,
                          user_key=None, user_base=None, global_config=None,
                          reasoning_effort=None) -> Vote:
        text, elapsed = await self._call_unit(
            unit_id, question, user_key, user_base, global_config, reasoning_effort)
        dec, reasoning, thinking, conf = _parse_decision(text)
        cfg = self.units[unit_id]
        return Vote(
            unit=unit_id, codename=cfg["codename"], role=cfg["role"],
            decision=dec, reasoning=reasoning, thinking=thinking,
            confidence=conf, latency_ms=elapsed,
        )

    async def judge(self, question: str, user_key=None, user_base=None,
                    global_config=None, reasoning_effort=None) -> Judgment:
        tasks = [
            self._judge_unit(uid, question, user_key, user_base,
                             global_config, reasoning_effort)
            for uid in self.units
        ]
        votes = await asyncio.gather(*tasks)
        total_ms = sum(v.latency_ms for v in votes)

        approves = sum(1 for v in votes if v.decision == Decision.APPROVE)
        denies = sum(1 for v in votes if v.decision == Decision.DENY)

        if approves >= 2:
            final, label = Decision.APPROVE, "承认"
        elif denies >= 2:
            final, label = Decision.DENY, "否决"
        else:
            final, label = Decision.DENY, "否决"

        lines = []
        for v in votes:
            lines.append(f"{v.codename}({v.role}): {v.decision.value} (置信度{v.confidence:.0%})")
        consensus = f"MAGI 最终裁定: {'✅' if final==Decision.APPROVE else '❌'} {label}\n\n" + "\n".join(lines)

        return Judgment(
            question=question, votes=list(votes), final_decision=final,
            consensus=consensus, total_latency_ms=total_ms,
        )

    async def consult(self, unit_id: str, question: str, user_key=None,
                      user_base=None, global_config=None,
                      reasoning_effort=None) -> ConsultResult:
        text, elapsed = await self._call_unit(
            unit_id, question, user_key, user_base, global_config, reasoning_effort)
        response, thinking, conf = _parse_consult(text)
        cfg = self.units[unit_id]
        return ConsultResult(
            unit=unit_id, codename=cfg["codename"], role=cfg["role"],
            response=response, thinking=thinking,
            confidence=conf, latency_ms=elapsed,
        )
