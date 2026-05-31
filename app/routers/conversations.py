"""Conversation routes — user & admin"""

from fastapi import APIRouter, Depends

from app.auth import get_current_user, get_current_admin
from app.models import conv_store

router = APIRouter(prefix="/api", tags=["conversations"])


@router.get("/conversations")
async def list_my_conversations(current_user=Depends(get_current_user)):
    return conv_store.list_by_user(current_user["id"], limit=200)


@router.get("/conversations/export")
async def export_my_conversations(current_user=Depends(get_current_user)):
    return conv_store.export_user(current_user["id"])


@router.get("/admin/conversations")
async def list_all_conversations(current_user=Depends(get_current_admin)):
    return conv_store.list_all(limit=500)


@router.get("/admin/conversations/export")
async def export_all_conversations(current_user=Depends(get_current_admin)):
    return conv_store.export_all()
