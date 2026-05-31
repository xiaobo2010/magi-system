"""MAGI System — FastAPI Web Interface"""

import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from app.magi import MagiSystem, Decision

app = FastAPI(
    title="MAGI System",
    description="新世纪福音战士 MAGI 超级计算机复刻 — 三位一体多数决决策系统",
    version="1.0.0",
)

magi = MagiSystem()

# ─── API Models ──────────────────────────────────────────

class Question(BaseModel):
    text: str


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
  .header {
    text-align: center;
    margin: 20px 0;
  }
  .header h1 {
    font-size: 2.5em;
    color: #ff0040;
    text-shadow: 0 0 20px #ff0040, 0 0 40px #ff004066;
    letter-spacing: 8px;
  }
  .header . subtitle {
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
  .unit-name {
    font-size: 1.1em;
    font-weight: bold;
    margin-bottom: 4px;
  }
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
  .latency { font-size: 0.75em; color: #00ff4166; margin-top: 8px; }
  .scan-line {
    position: fixed; top: 0; left: 0; right: 0; height: 2px;
    background: #00ff4133; animation: scan 3s linear infinite; z-index: 999;
  }
  @keyframes scan { 0% { top: 0; } 100% { top: 100vh; } }
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
  <textarea id="question" placeholder="向 MAGI 提交提案...&#10;&#10;例：是否应该在每个城市部署自动化的 EVA 维护系统？">&#10;</textarea>
  <br>
  <button id="submit" onclick="submitQuestion()">提交裁决</button>
</div>

<script>
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
</script>
</body>
</html>"""
    return HTMLResponse(html)


# ─── API Routes ──────────────────────────────────────────

@app.post("/api/judge", response_model=JudgmentResponse)
async def judge(question: Question):
    """提交问题给 MAGI 三贤人系统裁决"""
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


@app.get("/api/status")
async def status():
    """查看 MAGI 系统状态"""
    return {
        "status": "online",
        "units": [
            {"id": "melchior", "codename": "MELCHIOR-01", "role": "科学家", "status": "ready"},
            {"id": "balthasar", "codename": "BALTHASAR-02", "role": "母亲", "status": "ready"},
            {"id": "casper", "codename": "CASPER-03", "role": "女人", "status": "ready"},
        ],
        "decision_rule": "2/3 majority required",
    }


# ─── Entry ───────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("MAGI_HOST", "0.0.0.0")
    port = int(os.getenv("MAGI_PORT", "7777"))
    print("🔬 MAGI System 启动中...")
    print(f"   MELCHIOR-01 (科学家) → {os.getenv('MAGI_MELCHIOR_MODEL', os.getenv('MAGI_MODEL', 'default'))}")
    print(f"   BALTHASAR-02 (母亲) → {os.getenv('MAGI_BALTHASAR_MODEL', os.getenv('MAGI_MODEL', 'default'))}")
    print(f"   CASPER-03 (女人) → {os.getenv('MAGI_CASPER_MODEL', os.getenv('MAGI_MODEL', 'default'))}")
    uvicorn.run(app, host=host, port=port)
