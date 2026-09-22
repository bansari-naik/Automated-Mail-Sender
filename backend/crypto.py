"""Stateless session crypto.

No database: each user's Gmail tokens live in their own encrypted HttpOnly
cookie. The server stores nothing about who is using the app.

- ENCRYPTION_KEY = Fernet key sealing the auth cookie. Set it in production
  so sessions survive restarts. If missing, an ephemeral key is generated
  (sessions die on restart — fine for local dev).
"""
import json
import logging
import os

log = logging.getLogger("mailhunt")

_fernet = None


def get_fernet():
    global _fernet
    if _fernet is not None:
        return _fernet
    key = os.getenv("ENCRYPTION_KEY", "").strip()
    from cryptography.fernet import Fernet

    if not key:
        _fernet = Fernet(Fernet.generate_key())
        log.warning("ENCRYPTION_KEY not set — using ephemeral key (sessions die on restart).")
        return _fernet
    try:
        _fernet = Fernet(key.encode() if isinstance(key, str) else key)
    except Exception:
        _fernet = Fernet(Fernet.generate_key())
        log.warning("ENCRYPTION_KEY invalid — using ephemeral key.")
    return _fernet


def seal_session(data: dict) -> str:
    raw = json.dumps(data).encode()
    return get_fernet().encrypt(raw).decode()


def unseal_session(token: str | None) -> dict | None:
    if not token:
        return None
    try:
        raw = get_fernet().decrypt(token.encode())
        data = json.loads(raw.decode())
        return data if isinstance(data, dict) else None
    except Exception:
        return None
