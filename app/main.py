"""MAGI System — FastAPI application"""

import os
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from app.magi import MagiSystem, UNIT_CONFIG
from app.auth import get_current_user, require_admin, hash_password
from app.models import (
    user_store, conv_store, global_config_store, rate_limiter,
    ConsultRequest, build_conversation_record,
)
from app.routers import auth as auth_router
from app.routers import admin as admin_router
from app.routers import conversations as conv_router
from app.routers.auth import _decrypt_user_key
from app.frontend import render_html


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create default admin on first run."""
    if not user_store.get_user_by_username("admin"):
        user_store.create_user(
            "__admin__", "admin",
            hash_password("admin123"), "admin",
        )
    yield


app = FastAPI(title="MAGI System", version="2.1", lifespan=lifespan)
magi = MagiSystem()

app.include_router(auth_router.router)
app.include_router(admin_router.router)
app.include_router(conv_router.router)


# ─── Judge endpoint ────────────────────────────────────

@app.post("/api/judge")
async def judge(question: str, current_user=Depends(get_current_user)):
    # Rate limit
    tpm = current_user.get("tpm_limit", 0)
    tpd = current_user.get("tpd_limit", 0)
    err = rate_limiter.check(current_user["id"], tpm, tpd)
    if err:
        raise HTTPException(429, err)

    # Resolve user API key
    user_key, user_base = _decrypt_user_key(current_user)
    gcfg = global_config_store.get()
    effort = gcfg.get("reasoning_effort")

    result = await magi.judge(
        question, user_key=user_key, user_base=user_base,
        global_config=gcfg, reasoning_effort=effort,
    )

    # Save conversation
    record = build_conversation_record(
        user_id=current_user["id"],
        question=result.question,
        votes=[{
            "unit": v.unit, "codename": v.codename, "role": v.role,
            "decision": v.decision.value, "reasoning": v.reasoning,
            "thinking": v.thinking, "confidence": v.confidence,
            "latency_ms": v.latency_ms,
        } for v in result.votes],
        final_decision=result.final_decision.value,
        consensus=result.consensus,
        total_latency_ms=result.total_latency_ms,
    )
    conv_store.save(record)

    return {
        "question": result.question,
        "votes": [{
            "unit": v.unit, "codename": v.codename, "role": v.role,
            "decision": v.decision.value, "reasoning": v.reasoning,
            "thinking": v.thinking, "confidence": v.confidence,
            "latency_ms": v.latency_ms,
        } for v in result.votes],
        "final_decision": result.final_decision.value,
        "consensus": result.consensus,
        "total_latency_ms": result.total_latency_ms,
    }


# ─── Consult endpoint (single unit) ────────────────────

@app.post("/api/consult")
async def consult(body: ConsultRequest, current_user=Depends(get_current_user)):
    if body.unit not in UNIT_CONFIG:
        raise HTTPException(400, f"Unknown unit: {body.unit}. Must be melchior/balthasar/casper")

    tpm = current_user.get("tpm_limit", 0)
    tpd = current_user.get("tpd_limit", 0)
    err = rate_limiter.check(current_user["id"], tpm, tpd)
    if err:
        raise HTTPException(429, err)

    user_key, user_base = _decrypt_user_key(current_user)
    gcfg = global_config_store.get()
    effort = gcfg.get("reasoning_effort")

    result = await magi.consult(
        body.unit, body.text,
        user_key=user_key, user_base=user_base,
        global_config=gcfg, reasoning_effort=effort,
    )
    return {
        "unit": result.unit, "codename": result.codename,
        "role": result.role, "response": result.response,
        "thinking": result.thinking, "confidence": result.confidence,
        "latency_ms": result.latency_ms,
    }


# ─── Status endpoint ───────────────────────────────────

@app.get("/api/status")
async def status(current_user=Depends(get_current_user)):
    gcfg = global_config_store.get()
    return {
        "status": "online",
        "units": {uid: {"codename": UNIT_CONFIG[uid]["codename"], "role": UNIT_CONFIG[uid]["role"]}
                  for uid in UNIT_CONFIG},
        "reasoning_effort": gcfg.get("reasoning_effort"),
        "global_api_base": gcfg.get("api_base", ""),
    }


# ─── Frontend ──────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def frontend():
    return render_html()
