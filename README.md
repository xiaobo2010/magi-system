# 🔴 MAGI System

> **三贤人超级决策系统** — 新世纪福音战士 MAGI 超级计算机复刻

三位 LLM 以不同人格对同一问题进行独立思考和裁决，通过多数决得出最终决策。

## ✨ v2.0 新特性

- 🔐 **JWT 用户鉴权** — Access / Refresh Token 双令牌机制，bcrypt 密码哈希
- 👥 **双角色体系** — `admin` / `user`，管理员可管理用户、查看全量记录
- 🚦 **TPM / TPD 限速** — 按 Token 配额控制每分钟 / 每日用量
- 💬 **对话记录存储与导出** — SQLite 持久化，支持 JSON / CSV 导出
- 🎛️ **折叠式配置面板** — 页面底部可动态修改模型和 API Key，无需重启
- 🖥️ **NERV 终端风格前端** — 赛博朋克 UI，三贤人独立投票动画

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
# 编辑 .env 填入你的 API Key 和 JWT 密钥

# 3. 安装 & 启动
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 7777
```

访问 `http://localhost:7777` 即可看到 MAGI 终端界面。

### Render 部署

本项目已适配 Render 平台，启动命令：

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

设置环境变量后直接推送即可部署。

## Docker 部署

```bash
docker build -t magi-system .
docker run -d --name magi \
  -p 7777:7777 \
  --env-file .env \
  magi-system
```

## 用户鉴权

### 注册 & 登录

```bash
# 注册
curl -X POST http://localhost:7777/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "shinji", "password": "eva01"}'

# 登录（返回 access_token 和 refresh_token）
curl -X POST http://localhost:7777/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'username=shinji&password=eva01'

# 刷新令牌
curl -X POST http://localhost:7777/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<your-refresh-token>"}'
```

### 用户管理（管理员）

```bash
# 列出所有用户
curl http://localhost:7777/api/admin/users \
  -H "Authorization: Bearer <admin-access-token>"

# 删除用户
curl -X DELETE http://localhost:7777/api/admin/users/<user_id> \
  -H "Authorization: Bearer <admin-access-token>"
```

## API

### 提交裁决

```bash
curl -X POST http://localhost:7777/api/judge \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access-token>" \
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

### 对话记录

```bash
# 获取历史记录
curl http://localhost:7777/api/conversations \
  -H "Authorization: Bearer <access-token>"

# 导出为 JSON
curl http://localhost:7777/api/conversations/export?format=json \
  -H "Authorization: Bearer <access-token>"

# 导出为 CSV
curl http://localhost:7777/api/conversations/export?format=csv \
  -H "Authorization: Bearer <access-token>"
```

### 系统状态

```bash
curl http://localhost:7777/api/status \
  -H "Authorization: Bearer <access-token>"
```

## 配置

### 环境变量

```env
# JWT 密钥（生产环境务必替换）
MAGI_SECRET_KEY=your-secret-key

# 统一 LLM 配置
MAGI_API_BASE=https://api.vveai.com/v1
MAGI_API_KEY=your-key
MAGI_MODEL=deepseek-v4-pro

# 或分别配置每个 MAGI 单元
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

### 动态配置

页面底部的折叠式配置面板可以实时修改模型和 API Key，修改后立即生效，无需重启服务。

## 项目结构

```
magi-system/
├── app/
│   ├── main.py          # FastAPI 入口，路由挂载
│   ├── magi.py          # 三贤人裁决核心逻辑
│   ├── auth.py          # JWT + bcrypt 鉴权
│   ├── models.py        # 数据模型 & SQLite 存储
│   ├── frontend.py      # NERV 终端风格前端
│   └── routers/
│       ├── auth.py      # 认证路由（注册/登录/刷新）
│       ├── admin.py     # 管理员路由（用户管理）
│       └── conversations.py  # 对话记录路由
├── .env.example
├── requirements.txt
├── Dockerfile
└── README.md
```

## 技术栈

- **FastAPI** — 异步 Web 框架
- **OpenAI SDK** — 兼容所有 OpenAI API 格式的 LLM
- **asyncio** — 三单元并行裁决
- **SQLite** — 对话记录与用户数据持久化
- **JWT (python-jose) + bcrypt** — 安全鉴权
- **NERV Terminal UI** — 赛博朋克风格前端

## 致敬

本项目致敬《新世纪福音战士》中赤木直子博士设计的 MAGI 超级计算机系统——人类最后的三位一体决策机关。

*"科学家的我，母亲的我，还有作为一个女人的我……这三种人格构成了 MAGI。"*
— 赤木直子

## License

MIT
