"""Admin router — user management + global config"""

from fastapi import APIRouter, Depends, HTTPException
from app.auth import require_admin, hash_password
from app.models import user_store, global_config_store, UserUpdate, GlobalConfigUpdate

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users")
async def list_users(admin=Depends(require_admin)):
    users = user_store.list_users()
    result = []
    for u in users:
        result.append({
            "id": u["id"],
            "username": u["username"],
            "role": u["role"],
            "is_active": u.get("is_active", True),
            "tpm_limit": u.get("tpm_limit", 0),
            "tpd_limit": u.get("tpd_limit", 0),
            "has_api_key": bool(u.get("api_key")),
            "created_at": u.get("created_at", 0),
        })
    return result


@router.put("/users/{user_id}")
async def update_user(user_id: str, body: UserUpdate, admin=Depends(require_admin)):
    updates = {}
    if body.username is not None:
        updates["username"] = body.username
    if body.password is not None:
        updates["password_hash"] = hash_password(body.password)
    if body.role is not None:
        updates["role"] = body.role
    if body.is_active is not None:
        updates["is_active"] = body.is_active
    if body.tpm_limit is not None:
        updates["tpm_limit"] = body.tpm_limit
    if body.tpd_limit is not None:
        updates["tpd_limit"] = body.tpd_limit
    user = user_store.update_user(user_id, updates)
    if not user:
        raise HTTPException(404, "User not found")
    return {"status": "ok"}


@router.delete("/users/{user_id}")
async def delete_user(user_id: str, admin=Depends(require_admin)):
    ok = user_store.delete_user(user_id)
    if not ok:
        raise HTTPException(404, "User not found")
    return {"status": "ok"}


@router.get("/config")
async def get_config(admin=Depends(require_admin)):
    return global_config_store.get()


@router.put("/config")
async def update_config(body: GlobalConfigUpdate, admin=Depends(require_admin)):
    updates = {}
    if body.api_base is not None:
        updates["api_base"] = body.api_base
    if body.api_key is not None:
        updates["api_key"] = body.api_key
    if body.units is not None:
        updates["units"] = body.units
    if body.reasoning_effort is not None:
        if body.reasoning_effort not in ("low", "medium", "high"):
            raise HTTPException(400, "reasoning_effort must be low/medium/high")
        updates["reasoning_effort"] = body.reasoning_effort
    config = global_config_store.update(updates)
    return config
