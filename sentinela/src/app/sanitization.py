from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any

from fastapi import HTTPException


HEX64_RE = re.compile(r"^[a-f0-9]{64}$")
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
CPF_RE = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
WINDOWS_PATH_RE = re.compile(r"\b[A-Za-z]:\\[^:*?\"<>|\r\n]+")
UNIX_PATH_RE = re.compile(r"(?<!https:)\/(?:home|users|var|tmp|mnt|media|evidence|caso|case)\/[^\s]+", re.IGNORECASE)
MEDIA_EXT_RE = re.compile(r"\.(?:jpg|jpeg|png|gif|webp|bmp|mp4|mov|avi|mkv|wmv|pdf|zip|rar|7z)\b", re.IGNORECASE)
RAW_HASH_RE = re.compile(r"\b[a-fA-F0-9]{32,128}\b")

SAFE_HASH_KEYS = {"id_hash", "event_hash"}
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


def validate_id_hash(value: str) -> str:
    if not HEX64_RE.fullmatch(value or ""):
        raise ValueError("id_hash deve ser pseudonimo SHA-256 hexadecimal")
    return value


def fail_if_sensitive(payload: Any) -> None:
    try:
        assert_no_sensitive_payload(payload)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"payload inseguro: {exc}") from exc


def assert_no_sensitive_payload(payload: Any, path: str = "payload") -> None:
    if isinstance(payload, dict):
        for key, value in payload.items():
            key_text = str(key)
            key_lower = key_text.lower()
            if key_lower not in SAFE_HASH_KEYS and any(
                fragment in key_lower for fragment in SENSITIVE_KEY_FRAGMENTS
            ):
                raise ValueError(f"campo proibido em {path}.{key_text}")
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
        validate_id_hash(text)
        return
    lower = text.lower()
    if any(term in lower for term in FORBIDDEN_TEXT):
        raise ValueError(f"texto proibido em {path}")
    if EMAIL_RE.search(text) or CPF_RE.search(text):
        raise ValueError(f"identificador cru em {path}")
    if WINDOWS_PATH_RE.search(text) or UNIX_PATH_RE.search(text):
        raise ValueError(f"path cru em {path}")
    if MEDIA_EXT_RE.search(text):
        raise ValueError(f"referencia de midia/arquivo em {path}")
    if RAW_HASH_RE.search(text):
        raise ValueError(f"hash cru em campo nao permitido: {path}")
