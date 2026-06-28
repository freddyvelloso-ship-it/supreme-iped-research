from __future__ import annotations

import json
from pathlib import Path

import pytest

from supreme_agent.agent import (
    build_central_ingest_request,
    build_payloads,
    ingest_plugin_log,
    send_central_ingest_with_retry,
)
from supreme_agent.config import AgentConfig
from supreme_agent.journey import next_step
from supreme_agent.pairing import issue_device_credential, revoke_fingerprint, validate_device_credential
from supreme_agent.queue import enqueue


def cfg(tmp_path: Path) -> AgentConfig:
    return AgentConfig(
        agent_id="agent-test",
        institution_id="inst",
        study_id="study",
        case_id="case",
        participant_scope="operator",
        server_url="https://sentinela.example.invalid",
        ingest_token="local-test-token",
        queue_dir=tmp_path / "queue",
        plugin_event_log=tmp_path / "plugin.ndjson",
        signing_key=b"signing-key-test",
        encryption_key=b"encryption-key-test",
    )


def sample_event(kind: str = "image_view") -> dict:
    return {
        "schema_version": "SUPREME-FIELD-EVENTS-1.0",
        "plugin_version": "SUPREME-IPED-PLUGIN-1.0.0",
        "event_type": kind,
        "timestamp": "2026-06-23T12:00:00Z",
        "source_id": "1",
        "item_id": "7",
        "item_hash": "abc",
        "media_type": "image",
        "duration_seconds": "1.250",
        "severity": "3",
    }


def test_agent_signs_encrypts_and_maps_queue(tmp_path: Path) -> None:
    config = cfg(tmp_path)
    enqueue(config, sample_event())
    payloads = build_payloads(config)
    assert payloads[0]["schema_version"] == "SUPREME-FIELD-INGEST-1.0"
    assert payloads[0]["event_type"] == "image_view"
    assert payloads[0]["agent_signature"]
    assert payloads[0]["agent_chain_hash"]


def test_agent_builds_central_ingest_payload(tmp_path: Path) -> None:
    config = cfg(tmp_path)
    enqueue(config, sample_event("image_view"))
    enqueue(config, sample_event("session_start"))
    payload = build_central_ingest_request(config)
    assert len(payload["events"]) == 1
    assert payload["events"][0]["event_type"] == "image_view"
    assert payload["events"][0]["source_tool"] == "iped"


def test_ingest_plugin_log(tmp_path: Path) -> None:
    config = cfg(tmp_path)
    config.plugin_event_log.write_text(json.dumps(sample_event("item_close")) + "\n", encoding="utf-8")
    assert ingest_plugin_log(config) == 1
    assert build_payloads(config)[0]["event_type"] == "item_close"


def test_tampered_chain_fails(tmp_path: Path) -> None:
    config = cfg(tmp_path)
    enqueue(config, sample_event())
    record = json.loads(config.queue_file.read_text(encoding="utf-8"))
    token = record["encrypted_envelope"]
    record["encrypted_envelope"] = token[:-2] + ("A" if token[-2] != "A" else "B") + token[-1]
    config.queue_file.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(Exception):
        build_payloads(config)


def test_behavioral_journey_keeps_panas_after_iped_close() -> None:
    assert next_step(set(), False) == "open_form:SRQ20"
    assert next_step({"SRQ20", "DASS21", "OLBI"}, True) == "wait_iped_close"
    assert next_step({"SRQ20", "DASS21", "OLBI"}, False) == "open_form:PANAS_SHORT"
    assert next_step({"SRQ20", "DASS21", "OLBI", "PANAS_SHORT"}, False) == "complete"


def test_device_pairing_credential_is_scoped_and_verifiable() -> None:
    credential = issue_device_credential(
        device_id="device-001",
        institution_id="inst",
        study_id="study",
        case_id="case",
        participant_scope="operator",
        server_key=b"server-pairing-key",
    )
    assert validate_device_credential(credential, b"server-pairing-key")
    assert not validate_device_credential(credential, b"wrong-key")
    assert len(revoke_fingerprint(credential)) == 64


def test_central_ingest_retries_after_transient_failure(tmp_path: Path) -> None:
    config = cfg(tmp_path)
    enqueue(config, sample_event("image_view"))
    calls = {"count": 0}

    class Response:
        content = b"{}"

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"events_stored": 1}

    def flaky_post(*args, **kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            raise OSError("offline")
        return Response()

    assert send_central_ingest_with_retry(config, attempts=2, base_delay_seconds=0, post_func=flaky_post) == 1
    assert calls["count"] == 2
