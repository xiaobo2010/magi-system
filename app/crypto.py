"""AES-256-GCM encryption for user API keys"""

import base64
import hashlib
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def _derive_key(secret: str) -> bytes:
    """Derive a 256-bit key from MAGI_SECRET_KEY using SHA-256."""
    return hashlib.sha256(secret.encode("utf-8")).digest()


def encrypt(plaintext: str, secret: str) -> str:
    """Encrypt plaintext with AES-256-GCM, return base64-encoded nonce+ciphertext."""
    key = _derive_key(secret)
    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    ct = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return base64.urlsafe_b64encode(nonce + ct).decode("ascii")


def decrypt(token: str, secret: str) -> str:
    """Decrypt a base64-encoded nonce+ciphertext produced by encrypt()."""
    key = _derive_key(secret)
    raw = base64.urlsafe_b64decode(token)
    nonce, ct = raw[:12], raw[12:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ct, None).decode("utf-8")
