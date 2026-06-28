from __future__ import annotations

import json
from pathlib import Path
import time
from typing import Iterable

from .config import AgentConfig
from .crypto import decrypt_json, verify
from .mapper import envelopes_to_central_ingest_request, event_to_supreme_record
from .queue import enqueue, read_records


def ingest_plugin_log(config: AgentConfig) -> int:
    if not config.plugin_event_log.exists():
        return 0
    count = 0
    for line in config.plugin_event_log.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        enqueue(config, json.loads(line))
        count += 1
    return count


def build_payloads(config: AgentConfig) -> list[dict]:
    payloads = []
    previous = ""
    for record in read_records(config):
        envelope = decrypt_json(record["encrypted_envelope"], config.encryption_key)
        signature = envelope.pop("signature")
        if not verify(envelope, signature, config.signing_key):
            raise ValueError("Invalid agent signature")
        if envelope["previous_hash"] != previous:
            raise ValueError("Invalid local hash chain")
        previous = envelope["chain_hash"]
        envelope["signature"] = signature
        payloads.append(event_to_supreme_record(envelope))
    return payloads


def build_central_ingest_request(config: AgentConfig) -> dict:
    envelopes = []
    previous = ""
    for record in read_records(config):
        envelope = decrypt_json(record["encrypted_envelope"], config.encryption_key)
        signature = envelope.pop("signature")
        if not verify(envelope, signature, config.signing_key):
            raise ValueError("Invalid agent signature")
        if envelope["previous_hash"] != previous:
            raise ValueError("Invalid local hash chain")
        previous = envelope["chain_hash"]
        envelope["signature"] = signature
        envelopes.append(envelope)
    return envelopes_to_central_ingest_request(envelopes)


def send_payloads(config: AgentConfig, payloads: Iterable[dict]) -> int:
    import requests

    sent = 0
    for payload in payloads:
        response = requests.post(
            config.server_url.rstrip("/") + "/v1/events/ingest",
            json=payload,
            headers={"Authorization": f"Bearer {config.ingest_token}"},
            timeout=10,
        )
        response.raise_for_status()
        sent += 1
    return sent


def send_central_ingest_with_retry(
    config: AgentConfig,
    attempts: int = 3,
    base_delay_seconds: float = 0.25,
    post_func=None,
) -> int:
    if post_func is None:
        import requests

        post_func = requests.post

    payload = build_central_ingest_request(config)
    if not payload["events"]:
        return 0
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            response = post_func(
                config.server_url.rstrip("/") + "/v1/events/ingest",
                json=payload,
                headers={"Authorization": f"Bearer {config.ingest_token}"},
                timeout=10,
            )
            response.raise_for_status()
            body = response.json() if response.content else {}
            return int(body.get("events_stored", len(payload["events"])))
        except Exception as exc:  # pragma: no cover - tested through monkeypatch
            last_error = exc
            if attempt < attempts:
                time.sleep(base_delay_seconds * (2 ** (attempt - 1)))
    raise RuntimeError(f"central ingest failed after {attempts} attempts") from last_error


def load_json_config(path: Path) -> AgentConfig:
    data = json.loads(path.read_text(encoding="utf-8"))
    return AgentConfig(
        agent_id=data["agent_id"],
        institution_id=data["institution_id"],
        study_id=data["study_id"],
        case_id=data["case_id"],
        participant_scope=data["participant_scope"],
        server_url=data["server_url"],
        ingest_token=data["ingest_token"],
        queue_dir=Path(data["queue_dir"]),
        plugin_event_log=Path(data["plugin_event_log"]),
        signing_key=data["signing_key"].encode("utf-8"),
        encryption_key=data["encryption_key"].encode("utf-8"),
    )
