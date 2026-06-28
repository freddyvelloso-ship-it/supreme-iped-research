from __future__ import annotations

import json
from typing import Any

from .config import AgentConfig
from .crypto import encrypt_json, sha256_hex, sign


def enqueue(config: AgentConfig, event: dict[str, Any]) -> dict[str, Any]:
    config.queue_dir.mkdir(parents=True, exist_ok=True)
    previous_hash = config.chain_file.read_text(encoding="utf-8").strip() if config.chain_file.exists() else ""
    envelope = {
        "agent_id": config.agent_id,
        "institution_id": config.institution_id,
        "study_id": config.study_id,
        "case_id": config.case_id,
        "participant_scope": config.participant_scope,
        "previous_hash": previous_hash,
        "event": event,
    }
    envelope["chain_hash"] = sha256_hex(json.dumps(envelope, sort_keys=True))
    envelope["signature"] = sign(envelope, config.signing_key)
    record = {
        "schema_version": "SUPREME-AGENT-QUEUE-1.0",
        "encrypted_envelope": encrypt_json(envelope, config.encryption_key),
    }
    with config.queue_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    config.chain_file.write_text(envelope["chain_hash"], encoding="utf-8")
    return envelope


def read_records(config: AgentConfig) -> list[dict[str, Any]]:
    if not config.queue_file.exists():
        return []
    return [json.loads(line) for line in config.queue_file.read_text(encoding="utf-8").splitlines() if line.strip()]
