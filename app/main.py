"""MAGI System — FastAPI Web Interface (v2.0 with Auth)"""

import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from app.magi import MagiSystem
from app.auth import get_current_user, get_current_admin
from app.models import (
    user_store,
    conv_store,
    global_config_store,
    rate_limiter,
    build_conversation_record,
)

app = FastAPI(
    title="MAGI System",
    description="新世纪福音战士 MAGI 超级计算机复刻 — 三位一体多数决决策系统",
    version="2.0.0",
)

from app.routers import auth as auth_router
from app.routers import admin as admin_router
from app.routers import conversations as conv_router

app.include_router(auth_router.router)
app.include_router(admin_router.router)
app.include_router(conv_router.router)

magi = MagiSystem()


@app.on_event("startup")
async def startup():
    from app.auth import hash_password
    import uuid
    if not user_store.get_user_by_username("admin"):
        user_store.create_user(
            user_id=str(uuid.uuid4()),
            username="admin",
            password_hash=hash_password("admin123"),
            role="admin",
        )
        print(">> Default admin account created (admin / admin123)")


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


# ─── Existing API Routes (modified) ──────────────────────

@app.post("/api/judge", response_model=JudgmentResponse)
async def judge(question: Question, current_user=Depends(get_current_user)):
    tpm = current_user.get("tpm_limit", 0)
    tpd = current_user.get("tpd_limit", 0)
    limit_msg = rate_limiter.check(current_user["id"], tpm, tpd)
    if limit_msg:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=limit_msg)

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

    record = build_conversation_record(
        user_id=current_user["id"],
        question=question.text,
        votes=[v.model_dump() for v in votes],
        final_decision=result.final_decision.value,
        consensus=result.consensus,
        total_latency_ms=result.total_latency_ms,
        token_usage=0,
    )
    conv_store.save(record)

    return JudgmentResponse(
        question=result.question,
        votes=votes,
        final_decision=result.final_decision.value,
        consensus=result.consensus,
        total_latency_ms=result.total_latency_ms,
    )


# Config routes moved to /api/admin/config (admin router)
# Kept for backward compat — proxies to admin config
@app.get("/api/config")
async def get_config_compat(_: dict = Depends(get_current_admin)):
    return global_config_store.get_masked()


@app.put("/api/config")
async def update_config_compat(config: ConfigUpdate, _: dict = Depends(get_current_admin)):
    updates = {}
    if config.api_base:
        updates["api_base"] = config.api_base
    if config.api_key:
        updates["api_key"] = config.api_key
    if config.units:
        updates["units"] = config.units
    global_config_store.update(updates)
    magi.update_config(global_config_store.get())
    return global_config_store.get_masked()


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


# ─── Frontend ────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index():
    from app.frontend import render_html
    return HTMLResponse(render_html())


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("MAGI_HOST", "0.0.0.0")
    port = int(os.getenv("MAGI_PORT", "7777"))
    print(">> MAGI System v2.0 starting...")
    print(f"   MELCHIOR-01 -> {magi.units['melchior'].model}")
    print(f"   BALTHASAR-02 -> {magi.units['balthasar'].model}")
    print(f"   CASPER-03 -> {magi.units['casper'].model}")
    uvicorn.run(app, host=host, port=port)
