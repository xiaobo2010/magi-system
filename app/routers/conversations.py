"""Conversation router — history, export"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from app.auth import get_current_user
from app.models import conv_store, rate_limiter
import csv, io, json

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.get("")
async def list_conversations(user=Depends(get_current_user)):
    limit = 50
    if user["role"] == "admin":
        return conv_store.list_all(limit)
    return conv_store.list_by_user(user["id"], limit)


@router.get("/export")
async def export_conversations(format: str = "json", user=Depends(get_current_user)):
    if user["role"] == "admin":
        data = conv_store.export_all()
    else:
        data = conv_store.export_user(user["id"])

    if format == "csv":
        output = io.StringIO()
        if data:
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=magi_conversations.csv"},
        )
    return JSONResponse(content=data)
