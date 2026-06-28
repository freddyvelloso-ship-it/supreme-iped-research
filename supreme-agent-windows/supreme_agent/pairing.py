from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone

from .crypto import sha256_hex, sign, verify


@dataclass(frozen=True)
class DeviceCredential:
    device_id: str
    institution_id: str
    study_id: str
    case_id: str
    participant_scope: str
    issued_at: str
    key_id: str
    signature: str

    def as_payload(self) -> dict[str, str]:
        return {
            "device_id": self.device_id,
            "institution_id": self.institution_id,
            "study_id": self.study_id,
            "case_id": self.case_id,
            "participant_scope": self.participant_scope,
            "issued_at": self.issued_at,
            "key_id": self.key_id,
        }


def issue_device_credential(
    *,
    device_id: str,
    institution_id: str,
    study_id: str,
    case_id: str,
    participant_scope: str,
    server_key: bytes,
    key_id: str = "server-device-pairing-v1",
) -> DeviceCredential:
    issued_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    payload = {
        "device_id": device_id,
        "institution_id": institution_id,
        "study_id": study_id,
        "case_id": case_id,
        "participant_scope": participant_scope,
        "issued_at": issued_at,
        "key_id": key_id,
    }
    return DeviceCredential(signature=sign(payload, server_key), **payload)


def validate_device_credential(credential: DeviceCredential, server_key: bytes) -> bool:
    return verify(credential.as_payload(), credential.signature, server_key)


def revoke_fingerprint(credential: DeviceCredential) -> str:
    return sha256_hex(json.dumps(credential.as_payload(), sort_keys=True))
