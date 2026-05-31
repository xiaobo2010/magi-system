"""Data models & stores — users, conversations, rate limiting, global config"""

import json
import os
import time
import uuid
from pathlib import Path
from threading import Lock
from typing import Optional

from pydantic import BaseModel

DATA_DIR = Path(os.getenv("MAGI_DATA_DIR", "data"))
USERS_FILE = DATA_DIR / "users.json"
CONV_DIR = DATA_DIR / "conversations"
CONFIG_FILE = DATA_DIR / "global_config.json"

_user_lock = Lock()
_conv_lock = Lock()
_config_lock = Lock()


# ─── Pydantic schemas ────────────────────────────────────

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    tpm_limit: Optional[int] = None
    tpd_limit: Optional[int] = None

class UserSettingsUpdate(BaseModel):
    api_key: Optional[str] = None
    api_base: Optional[str] = None

class GlobalConfigUpdate(BaseModel):
    api_base: Optional[str] = None
    api_key: Optional[str] = None
    units: Optional[dict] = None
    reasoning_effort: Optional[str] = None

class ConsultRequest(BaseModel):
    text: str
    unit: str  # melchior | balthasar | casper


# ─── User store ──────────────────────────────────────────

class UserStore:
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.users = {}
        self._load()

    def _load(self):
        if USERS_FILE.exists():
            with _user_lock:
                with open(USERS_FILE, "r") as f:
                    self.users = json.load(f)
                # migrate: add api_key / api_base fields if missing
                for u in self.users.values():
                    u.setdefault("api_key", None)
                    u.setdefault("api_base", None)
        else:
            self.users = {}
            self._save()

    def _save(self):
        with _user_lock:
            with open(USERS_FILE, "w") as f:
                json.dump(self.users, f, indent=2, ensure_ascii=False)

    def get_user(self, user_id: str) -> Optional[dict]:
        return self.users.get(user_id)

    def get_user_by_username(self, username: str) -> Optional[dict]:
        for u in self.users.values():
            if u["username"] == username:
                return u
        return None

    def list_users(self) -> list[dict]:
        return list(self.users.values())

    def create_user(self, user_id: str, username: str, password_hash: str, role: str = "user") -> dict:
        user = {
            "id": user_id,
            "username": username,
            "password_hash": password_hash,
            "role": role,
            "is_active": True,
            "tpm_limit": 0,
            "tpd_limit": 0,
            "api_key": None,
            "api_base": None,
            "created_at": time.time(),
        }
        self.users[user_id] = user
        self._save()
        return user

    def update_user(self, user_id: str, updates: dict) -> Optional[dict]:
        user = self.users.get(user_id)
        if not user:
            return None
        for k, v in updates.items():
            if v is not None:
                user[k] = v
        self._save()
        return user

    def delete_user(self, user_id: str) -> bool:
        if user_id in self.users:
            del self.users[user_id]
            self._save()
            return True
        return False


user_store = UserStore()


# ─── Conversation store ──────────────────────────────────

class ConversationStore:
    def __init__(self):
        CONV_DIR.mkdir(parents=True, exist_ok=True)

    def _user_dir(self, user_id: str) -> Path:
        d = CONV_DIR / user_id
        d.mkdir(parents=True, exist_ok=True)
        return d

    def save(self, record: dict):
        user_id = record["user_id"]
        fname = f"{record['timestamp']:.0f}_{record['id']}.json"
        with _conv_lock:
            with open(self._user_dir(user_id) / fname, "w") as f:
                json.dump(record, f, indent=2, ensure_ascii=False)

    def list_by_user(self, user_id: str, limit: int = 50) -> list[dict]:
        d = self._user_dir(user_id)
        files = sorted(d.glob("*.json"), reverse=True)[:limit]
        results = []
        with _conv_lock:
            for fp in files:
                with open(fp, "r") as f:
                    results.append(json.load(f))
        return results

    def list_all(self, limit: int = 100) -> list[dict]:
        results = []
        all_files = sorted(CONV_DIR.rglob("*.json"), key=lambda p: p.name, reverse=True)[:limit]
        with _conv_lock:
            for fp in all_files:
                with open(fp, "r") as f:
                    results.append(json.load(f))
        return results

    def export_user(self, user_id: str) -> list[dict]:
        return self.list_by_user(user_id, limit=999999)

    def export_all(self) -> list[dict]:
        return self.list_all(limit=999999)


conv_store = ConversationStore()


def build_conversation_record(user_id: str, question: str, votes: list, final_decision: str, consensus: str, total_latency_ms: int, token_usage: int = 0) -> dict:
    return {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "question": question,
        "votes": votes,
        "final_decision": final_decision,
        "consensus": consensus,
        "total_latency_ms": total_latency_ms,
        "token_usage": token_usage,
        "timestamp": time.time(),
    }


# ─── Global config store (admin-level defaults) ──────────

class GlobalConfigStore:
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.config = {}
        self._load()

    def _load(self):
        if CONFIG_FILE.exists():
            with _config_lock:
                with open(CONFIG_FILE, "r") as f:
                    self.config = json.load(f)
                # migrate: add reasoning_effort if missing
                self.config.setdefault("reasoning_effort", None)
        else:
            self.config = {
                "api_base": os.getenv("MAGI_API_BASE", "https://api.vveai.com/v1"),
                "api_key": os.getenv("MAGI_API_KEY", ""),
                "reasoning_effort": None,
                "units": {
                    "melchior": {"model": os.getenv("MAGI_MELCHIOR_MODEL", os.getenv("MAGI_MODEL", "deepseek-v4-pro"))},
                    "balthasar": {"model": os.getenv("MAGI_BALTHASAR_MODEL", os.getenv("MAGI_MODEL", "deepseek-v4-pro"))},
                    "casper": {"model": os.getenv("MAGI_CASPER_MODEL", os.getenv("MAGI_MODEL", "deepseek-v4-pro"))},
                },
            }
            self._save()

    def _save(self):
        with _config_lock:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)

    def get(self) -> dict:
        return self.config

    def update(self, updates: dict):
        if "api_base" in updates and updates["api_base"]:
            self.config["api_base"] = updates["api_base"]
        if "api_key" in updates and updates["api_key"]:
            self.config["api_key"] = updates["api_key"]
        if "reasoning_effort" in updates:
            self.config["reasoning_effort"] = updates["reasoning_effort"]
        if "units" in updates and updates["units"]:
            for uid, ucfg in updates["units"].items():
                if uid in self.config["units"]:
                    self.config["units"][uid].update(ucfg)
        self._save()
        return self.config

    def get_masked(self) -> dict:
        cfg = self.config.copy()
        key = cfg.get("api_key", "")
        masked = key[:4] + "***" + key[-4:] if len(key) > 8 else "***" if key else ""
        return {
            "api_base": cfg["api_base"],
            "api_key_masked": masked,
            "reasoning_effort": cfg.get("reasoning_effort"),
            "units": cfg["units"],
        }


global_config_store = GlobalConfigStore()


# ─── Rate limiter (sliding window, in-memory) ────────────

class RateLimiter:
    def __init__(self):
        self._windows: dict[str, list[float]] = {}

    def _cleanup(self, key: str, window: float):
        now = time.time()
        self._windows[key] = [t for t in self._windows.get(key, []) if now - t < window]

    def check(self, user_id: str, tpm: int, tpd: int) -> Optional[str]:
        if tpm <= 0 and tpd <= 0:
            return None
        now = time.time()
        minute_key = f"{user_id}:m"
        day_key = f"{user_id}:d"
        self._cleanup(minute_key, 60)
        self._cleanup(day_key, 86400)
        if tpm > 0 and len(self._windows.get(minute_key, [])) >= tpm:
            return "每分钟请求次数已达上限"
        if tpd > 0 and len(self._windows.get(day_key, [])) >= tpd:
            return "每日请求次数已达上限"
        self._windows.setdefault(minute_key, []).append(now)
        self._windows.setdefault(day_key, []).append(now)
        return None


rate_limiter = RateLimiter()
