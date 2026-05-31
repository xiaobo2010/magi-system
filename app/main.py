"""MAGI System — FastAPI Web Interface"""

import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from app.magi import MagiSystem, Decision

app = FastAPI(
    title="MAGI System",
    description="新世纪福音战士 MAGI 超级计算机复刻 — 三位一体多数决决策系统",
    version="1.1.0",
)

magi = MagiSystem()

# ─── API Models ──────────────────────────────────────────

class Question(BaseModel):
    text: str


class ConfigUpdate(BaseModel):
    api_base: str | None = None
    api_key: str | None = None
    units: dict | None = None


class VoteResponse(BaseModel):
    unit: str
    codename: str
    role: str
    decision: str
    reasoning: str
    confidence: float
    latency_ms: int


class JudgmentResponse(BaseModel):
    question: str
    votes: list[VoteResponse]
    final_decision: str
    consensus: str
    total_latency_ms: int


# ─── Web Routes ──────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index():
    html = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MAGI System</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: #0a0a12;
    color: #00ff41;
    font-family: 'Courier New', monospace;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20px;
  }
  .header { text-align: center; margin: 20px 0; }
  .header h1 {
    font-size: 2.5em;
    color: #ff0040;
    text-shadow: 0 0 20px #ff0040, 0 0 40px #ff004066;
    letter-spacing: 8px;
  }
  .header .subtitle {
    font-size: 0.9em;
    color: #00ff4188;
    margin-top: 5px;
  }
  .units {
    display: flex;
    gap: 20px;
    margin: 30px 0;
    flex-wrap: wrap;
    justify-content: center;
  }
  .unit {
    border: 1px solid #00ff4144;
    background: #0d0d1a;
    border-radius: 8px;
    padding: 20px;
    width: 280px;
    min-height: 200px;
    transition: all 0.3s;
  }
  .unit:hover { border-color: #00ff41; box-shadow: 0 0 15px #00ff4122; }
  .unit.melchior { border-top: 3px solid #00bfff; }
  .unit.balthasar { border-top: 3px solid #ff69b4; }
  .unit.casper { border-top: 3px solid #ffd700; }
  .unit-name { font-size: 1.1em; font-weight: bold; margin-bottom: 4px; }
  .unit-role { font-size: 0.8em; color: #00ff4188; margin-bottom: 12px; }
  .unit-result { font-size: 0.85em; line-height: 1.6; color: #ccc; }
  .thinking { color: #00ff4188; animation: blink 1s infinite; }
  @keyframes blink { 50% { opacity: 0.3; } }
  .decision-approve { color: #00ff41; font-weight: bold; }
  .decision-deny { color: #ff0040; font-weight: bold; }
  .decision-abstain { color: #ffd700; font-weight: bold; }
  .verdict {
    margin: 20px 0;
    padding: 20px 40px;
    border: 2px solid;
    border-radius: 8px;
    font-size: 1.5em;
    text-align: center;
    min-width: 300px;
    transition: all 0.5s;
  }
  .verdict.approve { border-color: #00ff41; color: #00ff41; background: #00ff4111; text-shadow: 0 0 10px #00ff4144; }
  .verdict.deny { border-color: #ff0040; color: #ff0040; background: #ff004011; text-shadow: 0 0 10px #ff004044; }
  .input-area {
    width: 100%;
    max-width: 900px;
    margin: 20px 0;
  }
  textarea {
    width: 100%;
    height: 100px;
    background: #0d0d1a;
    border: 1px solid #00ff4144;
    color: #00ff41;
    font-family: 'Courier New', monospace;
    font-size: 1em;
    padding: 15px;
    border-radius: 8px;
    resize: vertical;
  }
  textarea:focus { outline: none; border-color: #00ff41; }
  input[type="text"] {
    width: 100%;
    background: #0d0d1a;
    border: 1px solid #00ff4144;
    color: #00ff41;
    font-family: 'Courier New', monospace;
    font-size: 0.9em;
    padding: 8px 12px;
    border-radius: 4px;
  }
  input[type="text"]:focus { outline: none; border-color: #00ff41; }
  button {
    margin-top: 10px;
    padding: 12px 40px;
    background: #ff0040;
    color: #fff;
    border: none;
    border-radius: 8px;
    font-family: 'Courier New', monospace;
    font-size: 1em;
    cursor: pointer;
    letter-spacing: 2px;
    transition: all 0.3s;
  }
  button:hover { background: #ff0040cc; box-shadow: 0 0 20px #ff004044; }
  button:disabled { background: #333; cursor: not-allowed; }
  button.secondary { background: #00ff4133; border: 1px solid #00ff4166; color: #00ff41; }
  button.secondary:hover { background: #00ff4144; }
  .latency { font-size: 0.75em; color: #00ff4166; margin-top: 8px; }
  .scan-line {
    position: fixed; top: 0; left: 0; right: 0; height: 2px;
    background: #00ff4133; animation: scan 3s linear infinite; z-index: 999;
  }
  @keyframes scan { 0% { top: 0; } 100% { top: 100vh; } }

  /* ─── 配置面板 ─── */
  .config-panel {
    width: 100%;
    max-width: 900px;
    margin: 30px 0 20px;
    border: 1px solid #00ff4133;
    border-radius: 8px;
    overflow: hidden;
  }
  .config-header {
    padding: 12px 20px;
    background: #0d0d1a;
    border-bottom: 1px solid #00ff4133;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    user-select: none;
  }
  .config-header:hover { background: #111128; }
  .config-header h3 { color: #00ff4188; font-size: 0.95em; letter-spacing: 2px; }
  .config-arrow { color: #00ff4188; transition: transform 0.3s; }
  .config-arrow.open { transform: rotate(180deg); }
  .config-body {
    display: none;
    padding: 20px;
    background: #0a0a14;
  }
  .config-body.open { display: block; }
  .config-row {
    display: flex;
    gap: 12px;
    margin-bottom: 12px;
    align-items: center;
  }
  .config-row label {
    width: 120px;
    font-size: 0.85em;
    color: #00ff4188;
    flex-shrink: 0;
  }
  .config-row input { flex: 1; }
  .config-section {
    margin: 16px 0 8px;
    padding-top: 12px;
    border-top: 1px solid #00ff4122;
  }
  .config-section-title {
    font-size: 0.85em;
    color: #00ff4144;
    margin-bottom: 10px;
    letter-spacing: 1px;
  }
  .config-row .unit-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
  }
</style>
</head>
<body>
<div class="scan-line"></div>
<div class="header">
  <h1>MAGI SYSTEM</h1>
  <div class="subtitle">三贤人超级决策系统 — MELCHIOR · BALTHASAR · CASPER</div>
</div>

<div class="units">
  <div class="unit melchior" id="unit-melchior">
    <div class="unit-name" style="color:#00bfff">MELCHIOR-01</div>
    <div class="unit-role">科学家 · 逻辑 · 理性</div>
    <div class="unit-result" id="result-melchior"><span class="thinking">待机中...</span></div>
  </div>
  <div class="unit balthasar" id="unit-balthasar">
    <div class="unit-name" style="color:#ff69b4">BALTHASAR-02</div>
    <div class="unit-role">母亲 · 关怀 · 伦理</div>
    <div class="unit-result" id="result-balthasar"><span class="thinking">待机中...</span></div>
  </div>
  <div class="unit casper" id="unit-casper">
    <div class="unit-name" style="color:#ffd700">CASPER-03</div>
    <div class="unit-role">女人 · 直觉 · 情感</div>
    <div class="unit-result" id="result-casper"><span class="thinking">待机中...</span></div>
  </div>
</div>

<div class="verdict" id="verdict">AWAITING INPUT</div>

<div class="input-area">
  <textarea id="question" placeholder="向 MAGI 提交提案...&#10;&#10;例：是否应该在每个城市部署自动化的 EVA 维护系统？"></textarea>
  <br>
  <button id="submit" onclick="submitQuestion()">提交裁决</button>
  <span style="margin-left:12px;font-size:0.75em;color:#00ff4144">Ctrl+Enter 快捷提交</span>
</div>

<!-- ─── 配置面板 ─── -->
<div class="config-panel">
  <div class="config-header" onclick="toggleConfig()">
    <h3>⚙ MAGI 配置</h3>
    <span class="config-arrow" id="config-arrow">▼</span>
  </div>
  <div class="config-body" id="config-body">
    <div class="config-row">
      <label>API Base URL</label>
      <input type="text" id="cfg-api-base" placeholder="https://api.vveai.com/v1">
    </div>
    <div class="config-row">
      <label>API Key</label>
      <input type="text" id="cfg-api-key" placeholder="sk-*** (仅在修改时填入)">
    </div>

    <div class="config-section">
      <div class="config-section-title">── 三贤人模型配置 ──</div>
    </div>

    <div class="config-row">
      <div class="unit-dot" style="background:#00bfff"></div>
      <label style="width:100px">MELCHIOR-01</label>
      <input type="text" id="cfg-melchior" placeholder="模型名，如 deepseek-v4-pro">
    </div>
    <div class="config-row">
      <div class="unit-dot" style="background:#ff69b4"></div>
      <label style="width:100px">BALTHASAR-02</label>
      <input type="text" id="cfg-balthasar" placeholder="模型名，如 claude-sonnet-4-20250514">
    </div>
    <div class="config-row">
      <div class="unit-dot" style="background:#ffd700"></div>
      <label style="width:100px">CASPER-03</label>
      <input type="text" id="cfg-casper" placeholder="模型名，如 gpt-4o">
    </div>

    <div style="margin-top:16px; display:flex; gap:10px;">
      <button class="secondary" onclick="loadConfig()">刷新配置</button>
      <button class="secondary" onclick="saveConfig()">保存配置</button>
    </div>
    <div id="config-msg" style="margin-top:8px; font-size:0.8em; color:#00ff4144; min-height:1.2em;"></div>
  </div>
</div>

<script>
async function loadConfig() {
  try {
    const resp = await fetch('/api/config');
    const cfg = await resp.json();
    document.getElementById('cfg-api-base').value = cfg.api_base || '';
    document.getElementById('cfg-api-key').value = '';
    document.getElementById('cfg-api-key').placeholder = cfg.api_key_masked || '未设置';
    document.getElementById('cfg-melchior').value = cfg.units?.melchior?.model || '';
    document.getElementById('cfg-balthasar').value = cfg.units?.balthasar?.model || '';
    document.getElementById('cfg-casper').value = cfg.units?.casper?.model || '';
  } catch(e) {
    console.error('Failed to load config', e);
  }
}

async function saveConfig() {
  const cfg = { units: {} };
  const apiBase = document.getElementById('cfg-api-base').value.trim();
  const apiKey = document.getElementById('cfg-api-key').value.trim();
  if (apiBase) cfg.api_base = apiBase;
  if (apiKey) cfg.api_key = apiKey;

  const m = document.getElementById('cfg-melchior').value.trim();
  const b = document.getElementById('cfg-balthasar').value.trim();
  const c = document.getElementById('cfg-casper').value.trim();
  if (m) cfg.units.melchior = { model: m };
  if (b) cfg.units.balthasar = { model: b };
  if (c) cfg.units.casper = { model: c };

  const msgEl = document.getElementById('config-msg');
  try {
    const resp = await fetch('/api/config', {
      method: 'PUT',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(cfg)
    });
    const result = await resp.json();
    msgEl.style.color = '#00ff41';
    msgEl.textContent = '✅ 配置已更新';
    setTimeout(() => { msgEl.textContent = ''; }, 3000);
    loadConfig();
  } catch(e) {
    msgEl.style.color = '#ff0040';
    msgEl.textContent = '⚠️ 保存失败: ' + e.message;
  }
}

function toggleConfig() {
  const body = document.getElementById('config-body');
  const arrow = document.getElementById('config-arrow');
  const isOpen = body.classList.toggle('open');
  arrow.classList.toggle('open', isOpen);
  if (isOpen) loadConfig();
}

async function submitQuestion() {
  const question = document.getElementById('question').value.trim();
  if (!question) return;
  const btn = document.getElementById('submit');
  btn.disabled = true;
  btn.textContent = 'MAGI 思考中...';
  document.getElementById('verdict').textContent = '审议中...';
  document.getElementById('verdict').className = 'verdict';
  ['melchior','balthasar','casper'].forEach(u => {
    document.getElementById('result-'+u).innerHTML = '<span class="thinking">⟳ 思考中...</span>';
  });
  try {
    const resp = await fetch('/api/judge', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({text: question})
    });
    const data = await resp.json();
    const emoji = {'approve':'✅ 承认','deny':'❌ 否认','abstain':'⚠️ 弃权'};
    const cls = {'approve':'decision-approve','deny':'decision-deny','abstain':'decision-abstain'};
    data.votes.forEach(v => {
      document.getElementById('result-'+v.unit).innerHTML =
        `<div class="${cls[v.decision]}">${emoji[v.decision]}</div>` +
        `<div style="margin-top:6px">${v.reasoning}</div>` +
        `<div class="latency">置信度 ${Math.round(v.confidence*100)}% · ${v.latency_ms}ms</div>`;
    });
    const vCls = data.final_decision === 'approve' ? 'approve' : 'deny';
    const vText = data.final_decision === 'approve' ? '✅ 提案承认' : '❌ 提案否认';
    document.getElementById('verdict').textContent = vText;
    document.getElementById('verdict').className = 'verdict ' + vCls;
  } catch(e) {
    document.getElementById('verdict').textContent = '⚠️ 系统异常';
    ['melchior','balthasar','casper'].forEach(u => {
      document.getElementById('result-'+u).innerHTML = '<span style="color:#ff0040">通信错误</span>';
    });
  }
  btn.disabled = false;
  btn.textContent = '提交裁决';
}

document.getElementById('question').addEventListener('keydown', e => {
  if (e.ctrlKey && e.key === 'Enter') submitQuestion();
});

// 页面加载时预加载配置
loadConfig();
</script>
</body>
</html>"""
    return HTMLResponse(html)


# ─── API Routes ──────────────────────────────────────────

@app.post("/api/judge", response_model=JudgmentResponse)
async def judge(question: Question):
    result = await magi.judge(question.text)
    role_map = {"melchior": "科学家", "balthasar": "母亲", "casper": "女人"}
    votes = []
    for v in result.votes:
        votes.append(VoteResponse(
            unit=v.unit,
            codename=v.codename,
            role=role_map.get(v.unit, ""),
            decision=v.decision.value,
            reasoning=v.reasoning,
            confidence=v.confidence,
            latency_ms=v.latency_ms,
        ))
    return JudgmentResponse(
        question=result.question,
        votes=votes,
        final_decision=result.final_decision.value,
        consensus=result.consensus,
        total_latency_ms=result.total_latency_ms,
    )


@app.get("/api/config")
async def get_config():
    return magi.get_config()


@app.put("/api/config")
async def update_config(config: ConfigUpdate):
    update = {}
    if config.api_base:
        update["api_base"] = config.api_base
    if config.api_key:
        update["api_key"] = config.api_key
    if config.units:
        update["units"] = config.units
    magi.update_config(update)
    return {"status": "ok", "config": magi.get_config()}


@app.get("/api/status")
async def status():
    return {
        "status": "online",
        "units": [
            {"id": "melchior", "codename": "MELCHIOR-01", "role": "科学家", "model": magi.units["melchior"].model, "status": "ready"},
            {"id": "balthasar", "codename": "BALTHASAR-02", "role": "母亲", "model": magi.units["balthasar"].model, "status": "ready"},
            {"id": "casper", "codename": "CASPER-03", "role": "女人", "model": magi.units["casper"].model, "status": "ready"},
        ],
        "decision_rule": "2/3 majority required",
    }


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("MAGI_HOST", "0.0.0.0")
    port = int(os.getenv("MAGI_PORT", "7777"))
    print("🔬 MAGI System 启动中...")
    print(f"   MELCHIOR-01 → {magi.units['melchior'].model}")
    print(f"   BALTHASAR-02 → {magi.units['balthasar'].model}")
    print(f"   CASPER-03 → {magi.units['casper'].model}")
    uvicorn.run(app, host=host, port=port)
