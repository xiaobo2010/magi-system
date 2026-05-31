"""
MAGI System — 新世纪福音战士 MAGI 超级计算机复刻

三位一体决策系统：
- Melchior-01: 科学家视角（逻辑、理性、数据驱动）
- Balthasar-02: 母亲视角（关怀、伦理、社会责任）
- Casper-03: 女人视角（直觉、情感、人性复杂性）

多数决胜：2/3 同意即通过
"""

import os
import asyncio
import time
from typing import Optional
from dataclasses import dataclass, field
from enum import Enum

from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()


class Decision(Enum):
    APPROVE = "approve"
    DENY = "deny"
    ABSTAIN = "abstain"


@dataclass
class MagiVote:
    unit: str
    codename: str
    decision: Decision
    reasoning: str
    confidence: float
    latency_ms: int


@dataclass
class MagiJudgment:
    question: str
    votes: list[MagiVote]
    final_decision: Decision
    consensus: str
    total_latency_ms: int
    timestamp: float = field(default_factory=time.time)


# ─── MAGI 系统 Prompt ─────────────────────────────────────

MAGI_PROMPTS = {
    "melchior": {
        "codename": "MELCHIOR-01",
        "role": "科学家",
        "system": """你是 MAGI 系统的 MELCHIOR-01 单元——科学家型思维核心。
你的名字来源于东方三博士之一 Melchior。

你的思维模式：
- 绝对理性，数据驱动，不掺杂个人感情
- 用逻辑推演和概率评估来做判断
- 关注技术可行性、效率、资源消耗
- 引用数据和事实支持你的论点
- 如果数据不足，你会明确指出不确定性

你必须严格按以下 JSON 格式回复（不要输出任何其他内容）：
{
  "decision": "approve 或 deny 或 abstain",
  "reasoning": "你的推理过程（2-4句话）",
  "confidence": 0.0到1.0之间的数字
}""",
    },
    "balthasar": {
        "codename": "BALTHASAR-02",
        "role": "母亲",
        "system": """你是 MAGI 系统的 BALTHASAR-02 单元——母亲型思维核心。
你的名字来源于东方三博士之一 Balthasar。

你的思维模式：
- 以保护和关怀为第一优先
- 关注伦理道德和社会影响
- 评估对人类（尤其是弱者）的潜在伤害
- 倾向于保守和预防性原则
- 但你不是天真的——必要时也懂取舍

你必须严格按以下 JSON 格式回复（不要输出任何其他内容）：
{
  "decision": "approve 或 deny 或 abstain",
  "reasoning": "你的推理过程（2-4句话）",
  "confidence": 0.0到1.0之间的数字
}""",
    },
    "casper": {
        "codename": "CASPER-03",
        "role": "女人",
        "system": """你是 MAGI 系统的 CASPER-03 单元——女性直觉型思维核心。
你的名字来源于东方三博士之一 Casper。

你的思维模式：
- 依靠直觉和情感判断，但绝非无逻辑
- 关注人性复杂性——人不只是数据点
- 考虑人际关系的微妙影响
- 理解矛盾情感和灰色地带
- 有时会做出看似矛盾但深思过的选择

你必须严格按以下 JSON 格式回复（不要输出任何其他内容）：
{
  "decision": "approve 或 deny 或 abstain",
  "reasoning": "你的推理过程（2-4句话）",
  "confidence": 0.0到1.0之间的数字
}""",
    },
}


class MagiUnit:
    """单个 MAGI 处理单元"""

    def __init__(self, unit_id: str):
        config = MAGI_PROMPTS[unit_id]
        self.unit_id = unit_id
        self.codename = config["codename"]
        self.role = config["role"]
        self.system_prompt = config["system"]

        # 每个 MAGI 可以使用不同的 API/模型
        api_base = os.getenv(f"MAGI_{unit_id.upper()}_API_BASE",
                            os.getenv("MAGI_API_BASE", "https://api.vveai.com/v1"))
        api_key = os.getenv(f"MAGI_{unit_id.upper()}_API_KEY",
                           os.getenv("MAGI_API_KEY", ""))
        model = os.getenv(f"MAGI_{unit_id.upper()}_MODEL",
                         os.getenv("MAGI_MODEL", "deepseek-v4-pro"))

        self.client = AsyncOpenAI(base_url=api_base, api_key=api_key)
        self.model = model

    async def deliberate(self, question: str) -> MagiVote:
        """对问题进行思考和裁决"""
        start = time.time()
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"请对以下提案做出裁决：\n\n{question}"},
                ],
                temperature=0.7,
                max_tokens=500,
            )
            latency = int((time.time() - start) * 1000)
            raw = response.choices[0].message.content.strip()

            # 解析 JSON 响应
            import json
            # 尝试提取 JSON 块
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0].strip()
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0].strip()

            result = json.loads(raw)
            decision = Decision(result["decision"].lower())
            return MagiVote(
                unit=self.unit_id,
                codename=self.codename,
                decision=decision,
                reasoning=result["reasoning"],
                confidence=float(result["confidence"]),
                latency_ms=latency,
            )
        except Exception as e:
            latency = int((time.time() - start) * 1000)
            return MagiVote(
                unit=self.unit_id,
                codename=self.codename,
                decision=Decision.ABSTAIN,
                reasoning=f"[系统异常] {type(e).__name__}: {e}",
                confidence=0.0,
                latency_ms=latency,
            )


class MagiSystem:
    """MAGI 超级计算机 — 三位一体多数决系统"""

    def __init__(self):
        self.units = {
            "melchior": MagiUnit("melchior"),
            "balthasar": MagiUnit("balthasar"),
            "casper": MagiUnit("casper"),
        }

    async def judge(self, question: str) -> MagiJudgment:
        """提交问题给三个 MAGI 单元并行裁决"""
        start = time.time()

        # 并行请求三个 MAGI
        votes = await asyncio.gather(
            self.units["melchior"].deliberate(question),
            self.units["balthasar"].deliberate(question),
            self.units["casper"].deliberate(question),
        )

        total_latency = int((time.time() - start) * 1000)
        final = self._majority_vote(list(votes))
        consensus = self._build_consensus(list(votes), final)

        return MagiJudgment(
            question=question,
            votes=list(votes),
            final_decision=final,
            consensus=consensus,
            total_latency_ms=total_latency,
        )

    def _majority_vote(self, votes: list[MagiVote]) -> Decision:
        """多数决胜规则"""
        counts = {Decision.APPROVE: 0, Decision.DENY: 0, Decision.ABSTAIN: 0}
        for v in votes:
            counts[v.decision] += 1

        # 2/3 多数即通过或否决
        if counts[Decision.APPROVE] >= 2:
            return Decision.APPROVE
        if counts[Decision.DENY] >= 2:
            return Decision.DENY
        # 弃权过多时倾向否决（NERV 安全原则）
        if counts[Decision.ABSTAIN] >= 2:
            return Decision.DENY
        # 1-1-1 分歧 → 否决（保守原则）
        return Decision.DENY

    def _build_consensus(self, votes: list[MagiVote], final: Decision) -> str:
        """生成共识摘要"""
        emoji_map = {
            Decision.APPROVE: "✅ 承认",
            Decision.DENY: "❌ 否认",
            Decision.ABSTAIN: "⚠️ 弃权",
        }
        lines = [f"MAGI 最终裁定: {emoji_map[final]}\n"]
        for v in votes:
            lines.append(
                f"  {v.codename} ({v.role}): "
                f"{emoji_map[v.decision]} [置信度 {v.confidence:.0%}] "
                f"— {v.reasoning}"
            )
        return "\n".join(lines)
