"""Auth router — register, login, refresh, me, settings"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional

from app.auth import (
    hash_password, verify_password, create_tokens, get_current_user,
    refresh_access_token, SECRET_KEY,
)
from app.models import user_store, UserSettingsUpdate
from app.crypto import encrypt, decrypt

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterBody(BaseModel):
    username: str
    password: str

class LoginBody(BaseModel):
    username: str
    password: str

class RefreshBody(BaseModel):
    refresh_token: str


@router.post("/register")
async def register(body: RegisterBody):
    if user_store.get_user_by_username(body.username):
        raise HTTPException(400, "Username already exists")
    uid = str(uuid.uuid4())
    user_store.create_user(uid, body.username, hash_password(body.password), "user")
    return {"id": uid, "username": body.username, "role": "user"}


@router.post("/login")
async def login(body: LoginBody):
    user = user_store.get_user_by_username(body.username)
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(401, "Invalid credentials")
    if not user.get("is_active", True):
        raise HTTPException(403, "Account disabled")
    tokens = create_tokens(user["id"], user["role"])
    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "token_type": "bearer",
        "role": user["role"],
    }


@router.post("/refresh")
async def refresh(body: RefreshBody):
    try:
        result = refresh_access_token(body.refresh_token)
        return result
    except Exception as e:
        raise HTTPException(401, str(e))


@router.get("/me")
async def me(current_user=Depends(get_current_user)):
    has_key = bool(current_user.get("api_key"))
    api_base = current_user.get("api_base")
    return {
        "id": current_user["id"],
        "username": current_user["username"],
        "role": current_user["role"],
        "has_api_key": has_key,
        "api_base": api_base or "",
    }


@router.put("/settings")
async def update_settings(body: UserSettingsUpdate, current_user=Depends(get_current_user)):
    updates = {}
    if body.api_key is not None:
        if body.api_key == "":
            updates["api_key"] = None
        else:
            updates["api_key"] = encrypt(body.api_key, SECRET_KEY)
    if body.api_base is not None:
        if body.api_base == "":
            updates["api_base"] = None
        else:
            updates["api_base"] = body.api_base
    if updates:
        user_store.update_user(current_user["id"], updates)
    return {"status": "ok"}


def _decrypt_user_key(user: dict) -> tuple[Optional[str], Optional[str]]:
    """Decrypt user's API key if present. Returns (api_key, api_base) or (None, None)."""
    enc_key = user.get("api_key")
    if not enc_key:
        return None, user.get("api_base")
    try:
        return decrypt(enc_key, SECRET_KEY), user.get("api_base")
    except Exception:
        return None, user.get("api_base")
