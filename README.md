# 🔴 MAGI System

> **三贤人超级决策系统** — 新世纪福音战士 MAGI 超级计算机复刻

三位 LLM 以不同人格对同一问题进行独立思考和裁决，通过多数决得出最终决策。

## 三贤人

| 单元 | 代号 | 思维模式 | 颜色 |
|:---|:---|:---|:---|
| **MELCHIOR-01** | 科学家 | 绝对理性，数据驱动，逻辑推演 | 🔵 |
| **BALTHASAR-02** | 母亲 | 关怀保护，伦理道德，社会影响 | 🩷 |
| **CASPER-03** | 女人 | 直觉判断，情感感知，人性复杂性 | 🟡 |

## 决策规则

- **2/3 多数承认** → 提案通过 ✅
- **2/3 多数否认** → 提案否决 ❌
- **1-1-1 分歧** → 否决（保守原则）
- **2/3 弃权** → 否决（信息不足原则）

> 就像赤木律子博士说的：*"MAGI 不会犯错，因为它是一个女人。"*

## 快速开始

```bash
# 1. 克隆
git clone https://github.com/xiaobo2010/magi-system.git
cd magi-system

# 2. 配置
cp .env.example .env
# 编辑 .env 填入你的 API Key

# 3. 安装 & 启动
pip install -r requirements.txt
python -m app.main
```

访问 `http://localhost:7777` 即可看到 MAGI 终端界面。

## Docker 部署

```bash
docker build -t magi-system .
docker run -d --name magi \
  -p 7777:7777 \
  --env-file .env \
  magi-system
```

## API

### 提交裁决

```bash
curl -X POST http://localhost:7777/api/judge \
  -H "Content-Type: application/json" \
  -d '{"text": "是否应该在每座城市部署自动化 EVA 维护系统？"}'
```

响应：
```json
{
  "question": "是否应该...",
  "votes": [
    {
      "unit": "melchior",
      "codename": "MELCHIOR-01",
      "role": "科学家",
      "decision": "approve",
      "reasoning": "从技术可行性分析...",
      "confidence": 0.85,
      "latency_ms": 1234
    },
    ...
  ],
  "final_decision": "approve",
  "consensus": "MAGI 最终裁定: ✅ 承认\n...",
  "total_latency_ms": 1567
}
```

### 系统状态

```bash
curl http://localhost:7777/api/status
```

## 配置

每个 MAGI 单元可以单独配置不同的 API 端点和模型：

```env
# 统一配置
MAGI_API_BASE=https://api.vveai.com/v1
MAGI_API_KEY=your-key
MAGI_MODEL=deepseek-v4-pro

# 或分别配置
MAGI_MELCHIOR_API_BASE=https://api.openai.com/v1
MAGI_MELCHIOR_API_KEY=sk-xxx
MAGI_MELCHIOR_MODEL=gpt-4o

MAGI_BALTHASAR_API_BASE=https://api.deepseek.com
MAGI_BALTHASAR_API_KEY=sk-xxx
MAGI_BALTHASAR_MODEL=deepseek-chat

MAGI_CASPER_API_BASE=https://api.vveai.com/v1
MAGI_CASPER_API_KEY=your-key
MAGI_CASPER_MODEL=deepseek-v4-pro
```

## 技术栈

- **FastAPI** — 异步 Web 框架
- **OpenAI SDK** — 兼容所有 OpenAI API 格式的 LLM
- **asyncio** — 三单元并行裁决
- **NERV Terminal UI** — 赛博朋克风格前端

## 致敬

本项目致敬《新世纪福音战士》中赤木直子博士设计的 MAGI 超级计算机系统——人类最后的三位一体决策机关。

*"科学家的我，母亲的我，还有作为一个女人的我……这三种人格构成了 MAGI。"*
— 赤木直子

## License

MIT
