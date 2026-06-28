from __future__ import annotations

import base64
import hashlib
import hmac
import json
from typing import Any

from cryptography.fernet import Fernet


def sha256_hex(value: str | bytes) -> str:
    data = value if isinstance(value, bytes) else value.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def fernet_key(raw: bytes) -> bytes:
    return base64.urlsafe_b64encode(hashlib.sha256(raw).digest())


def sign(payload: dict[str, Any], key: bytes) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hmac.new(key, body, hashlib.sha256).hexdigest()


def verify(payload: dict[str, Any], signature: str, key: bytes) -> bool:
    return hmac.compare_digest(sign(payload, key), signature)


def encrypt_json(payload: dict[str, Any], key: bytes) -> str:
    token = Fernet(fernet_key(key)).encrypt(json.dumps(payload, sort_keys=True).encode("utf-8"))
    return token.decode("ascii")


def decrypt_json(token: str, key: bytes) -> dict[str, Any]:
    data = Fernet(fernet_key(key)).decrypt(token.encode("ascii"))
    return json.loads(data.decode("utf-8"))
