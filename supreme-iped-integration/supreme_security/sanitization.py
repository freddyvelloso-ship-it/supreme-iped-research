from __future__ import annotations

import hashlib
import re
from datetime import date, datetime
from typing import Any


class SanitizationError(ValueError):
    """Raised when a payload contains raw or unsafe forensic data."""


HEX64_RE = re.compile(r"^[a-f0-9]{64}$")
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
CPF_RE = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
PHONE_RE = re.compile(r"(?:\+?55\s*)?(?:\(?\d{2}\)?\s*)?\d{4,5}[-\s]?\d{4}")
WINDOWS_PATH_RE = re.compile(r"\b[A-Za-z]:\\[^:*?\"<>|\r\n]+")
UNIX_PATH_RE = re.compile(r"(?<!https:)\/(?:home|users|var|tmp|mnt|media|evidence|caso|case)\/[^\s]+", re.IGNORECASE)
RAW_HASH_RE = re.compile(r"\b[a-fA-F0-9]{32,128}\b")
MEDIA_EXT_RE = re.compile(r"\.(?:jpg|jpeg|png|gif|webp|bmp|mp4|mov|avi|mkv|wmv|pdf|zip|rar|7z)\b", re.IGNORECASE)

SAFE_HASH_KEYS = {"user_identifier", "id_hash", "event_hash"}
SENSITIVE_KEY_FRAGMENTS = {
    "userid",
    "user_id",
    "operatorid",
    "operator_id",
    "itemid",
    "item_id",
    "sourceid",
    "source_id",
    "path",
    "filename",
    "file_name",
    "name",
    "email",
    "cpf",
    "rg",
    "phone",
    "telefone",
    "address",
    "endereco",
    "raw",
    "payload",
    "line",
    "csv",
    "hash",
}
FORBIDDEN_TEXT = {
    "diagnosis",
    "diagnostico",
    "diagnóstico",
    "ranking",
    "productivity",
    "produtividade",
    "disciplinary",
    "disciplinar",
}

ALLOWED_SUPREME_EVENT_KEYS = {
    "timestamp",
    "event_type",
    "media_type",
    "severity",
    "duration_seconds",
    "user_identifier",
    "source_tool",
    "event_hash",
}


def require_strong_secret(secret: str, name: str, minimum: int = 32) -> None:
    if not secret or len(secret) < minimum:
        raise SanitizationError(f"{name} ausente ou fraco; minimo {minimum} caracteres")


def pseudonymize_identifier(raw_identifier: str, salt: str) -> str:
    require_strong_secret(salt, "SUPREME_SALT")
    if not raw_identifier:
        raise SanitizationError("identificador cru ausente")
    return hashlib.sha256(f"{salt}\0{raw_identifier}".encode("utf-8")).hexdigest()


def safe_reference(raw_value: str, salt: str, prefix: str = "ref") -> str:
    require_strong_secret(salt, "SUPREME_SALT")
    digest = hashlib.sha256(f"{prefix}\0{salt}\0{raw_value}".encode("utf-8")).hexdigest()
    return f"{prefix}_{digest[:16]}"


def sanitize_supreme_event(event: dict[str, Any]) -> dict[str, Any]:
    extra = set(event) - ALLOWED_SUPREME_EVENT_KEYS
    if extra:
        raise SanitizationError(f"evento contem campos nao permitidos: {sorted(extra)}")
    user_identifier = str(event.get("user_identifier", ""))
    if not HEX64_RE.fullmatch(user_identifier):
        raise SanitizationError("user_identifier deve ser pseudonimo SHA-256 hexadecimal")
    event_hash = event.get("event_hash")
    if event_hash is not None and not HEX64_RE.fullmatch(str(event_hash)):
        raise SanitizationError("event_hash deve ser SHA-256 hexadecimal")
    assert_no_sensitive_payload(event)
    return dict(event)


def assert_no_sensitive_payload(payload: Any, path: str = "payload") -> None:
    if isinstance(payload, dict):
        for key, value in payload.items():
            key_text = str(key)
            key_lower = key_text.lower()
            if key_lower not in SAFE_HASH_KEYS and any(
                fragment in key_lower for fragment in SENSITIVE_KEY_FRAGMENTS
            ):
                raise SanitizationError(f"campo proibido em {path}.{key_text}")
            assert_no_sensitive_payload(value, f"{path}.{key_text}")
        return
    if isinstance(payload, (list, tuple, set)):
        for index, value in enumerate(payload):
            assert_no_sensitive_payload(value, f"{path}[{index}]")
        return
    if isinstance(payload, (int, float, bool)) or payload is None:
        return
    if isinstance(payload, (datetime, date)):
        return
    text = str(payload)
    path_lower = path.lower()
    if path_lower.endswith(tuple(SAFE_HASH_KEYS)):
        if not HEX64_RE.fullmatch(text):
            raise SanitizationError(f"pseudonimo/hash invalido em {path}")
        return
    lower = text.lower()
    if any(term in lower for term in FORBIDDEN_TEXT):
        raise SanitizationError(f"texto proibido em {path}")
    if EMAIL_RE.search(text):
        raise SanitizationError(f"email cru em {path}")
    if CPF_RE.search(text):
        raise SanitizationError(f"documento cru em {path}")
    if PHONE_RE.search(text):
        raise SanitizationError(f"telefone cru em {path}")
    if WINDOWS_PATH_RE.search(text) or UNIX_PATH_RE.search(text):
        raise SanitizationError(f"path cru em {path}")
    if MEDIA_EXT_RE.search(text):
        raise SanitizationError(f"referencia de midia/arquivo em {path}")
    if RAW_HASH_RE.search(text):
        raise SanitizationError(f"hash cru em campo nao permitido: {path}")
