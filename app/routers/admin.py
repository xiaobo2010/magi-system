"""Admin routes — user management, global config, conversation oversight"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import get_current_admin, hash_password
from app.models import (
    user_store,
    global_config_store,
    UserCreate,
    UserUpdate,
    GlobalConfigUpdate,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ─── User Management ─────────────────────────────────────

@router.get("/users")
async def list_users(_: dict = Depends(get_current_admin)):
    users = user_store.list_users()
    # Strip password_hash from response
    return [
        {k: v for k, v in u.items() if k != "password_hash"}
        for u in users
    ]


@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(body: UserCreate, _: dict = Depends(get_current_admin)):
    if user_store.get_user_by_username(body.username):
        raise HTTPException(400, "Username already exists")
    user_id = str(uuid.uuid4())
    user = user_store.create_user(
        user_id=user_id,
        username=body.username,
        password_hash=hash_password(body.password),
        role=body.role,
    )
    return {k: v for k, v in user.items() if k != "password_hash"}


@router.put("/users/{user_id}")
async def update_user(user_id: str, body: UserUpdate, admin: dict = Depends(get_current_admin)):
    existing = user_store.get_user(user_id)
    if not existing:
        raise HTTPException(404, "User not found")
    updates = body.model_dump(exclude_none=True)
    # Handle password separately
    if "password" in updates:
        updates["password_hash"] = hash_password(updates.pop("password"))
    updated = user_store.update_user(user_id, updates)
    if not updated:
        raise HTTPException(500, "Update failed")
    return {k: v for k, v in updated.items() if k != "password_hash"}


@router.delete("/users/{user_id}")
async def delete_user(user_id: str, admin: dict = Depends(get_current_admin)):
    user = user_store.get_user(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    if user["username"] == "admin":
        raise HTTPException(403, "Cannot delete the default admin")
    if not user_store.delete_user(user_id):
        raise HTTPException(500, "Delete failed")
    return {"ok": True}


# ─── Global Config ───────────────────────────────────────

@router.get("/config")
async def get_config(_: dict = Depends(get_current_admin)):
    return global_config_store.get_masked()


@router.put("/config")
async def update_config(body: GlobalConfigUpdate, _: dict = Depends(get_current_admin)):
    updates = body.model_dump(exclude_none=True)
    updated = global_config_store.update(updates)
    return global_config_store.get_masked()
