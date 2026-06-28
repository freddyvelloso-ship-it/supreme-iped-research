"""Forensic custody primitives for SUPREME V4.

The functions in this module are deterministic by design: the same event
payload, versions and algorithm parameters always produce the same replay and
the same verifiable export.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from datetime import date, datetime, timezone
from typing import Any, Iterable, Mapping, Sequence

from .algorithm import CURRENT_ALGORITHM_VERSION, algorithm_parameters
from .ieo import compute_baseline, compute_ieo
from .metrics import compute_window_metrics
from .models import EventRecord, SessionRecord

SIGNATURE_ALGORITHM = "HMAC-SHA256"
ZERO_HASH = "0" * 64


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, ensure_ascii=True, separators=(",", ":"), default=str)


def sha256_hex(payload: Any) -> str:
    raw = payload if isinstance(payload, str) else canonical_json(payload)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def hmac_sha256(payload: Mapping[str, Any], signing_material: str) -> str:
    return hmac.new(
        signing_material.encode("utf-8"),
        canonical_json(payload).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def _event_payload(event: EventRecord) -> dict[str, Any]:
    return {
        "timestamp": event.timestamp.isoformat(),
        "event_type": event.event_type.value,
        "media_type": event.media_type.value,
        "severity": event.severity,
        "duration_seconds": event.duration_seconds,
        "user_identifier": event.user_identifier,
        "source_tool": event.source_tool.value,
        "event_hash": event.event_hash,
    }


def sign_event(
    event: EventRecord,
    signing_material: str,
    *,
    key_id: str,
    signed_at: str = "2026-06-23T00:00:00+00:00",
    trusted_capture_point: str = "supreme-ingest-first-trusted-capture",
) -> dict[str, Any]:
    payload = _event_payload(event)
    envelope = {
        "payload": payload,
        "event_hash": event.event_hash,
        "payload_hash": sha256_hex(payload),
        "signature_algorithm": SIGNATURE_ALGORITHM,
        "key_id": key_id,
        "signed_at": signed_at,
        "trusted_capture_point": trusted_capture_point,
    }
    envelope["signature"] = hmac_sha256(envelope, signing_material)
    return envelope


def verify_signed_event(envelope: Mapping[str, Any], signing_material: str) -> bool:
    signature = str(envelope.get("signature", ""))
    candidate = dict(envelope)
    candidate.pop("signature", None)
    expected = hmac_sha256(candidate, signing_material)
    if not hmac.compare_digest(signature, expected):
        raise ValueError("event signature mismatch")
    payload_hash = sha256_hex(candidate["payload"])
    if payload_hash != candidate.get("payload_hash"):
        raise ValueError("event payload hash mismatch")
    return True


def build_hash_chain(records: Sequence[Mapping[str, Any]], *, chain_id: str) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    previous_hash = ZERO_HASH
    for index, record in enumerate(records):
        payload_hash = sha256_hex(record)
        chain_payload = {
            "chain_id": chain_id,
            "index": index,
            "payload_hash": payload_hash,
            "previous_hash": previous_hash,
        }
        chain_hash = sha256_hex(chain_payload)
        entries.append({
            **chain_payload,
            "chain_hash": chain_hash,
            "record": dict(record),
        })
        previous_hash = chain_hash
    return entries


def verify_hash_chain(entries: Sequence[Mapping[str, Any]], *, chain_id: str) -> bool:
    previous_hash = ZERO_HASH
    for expected_index, entry in enumerate(entries):
        if entry.get("chain_id") != chain_id:
            raise ValueError(f"{chain_id}: unexpected chain id at index {expected_index}")
        if entry.get("index") != expected_index:
            raise ValueError(f"{chain_id}: unexpected index {entry.get('index')}")
        if entry.get("previous_hash") != previous_hash:
            raise ValueError(f"{chain_id}: previous hash mismatch at index {expected_index}")
        if sha256_hex(entry.get("record")) != entry.get("payload_hash"):
            raise ValueError(f"{chain_id}: payload hash mismatch at index {expected_index}")
        chain_payload = {
            "chain_id": entry["chain_id"],
            "index": entry["index"],
            "payload_hash": entry["payload_hash"],
            "previous_hash": entry["previous_hash"],
        }
        if sha256_hex(chain_payload) != entry.get("chain_hash"):
            raise ValueError(f"{chain_id}: chain hash mismatch at index {expected_index}")
        previous_hash = str(entry["chain_hash"])
    return True


def chain_tip(entries: Sequence[Mapping[str, Any]]) -> str:
    return str(entries[-1]["chain_hash"]) if entries else ZERO_HASH


def deterministic_sessions(events: Sequence[EventRecord]) -> list[SessionRecord]:
    grouped: dict[tuple[str, date], list[EventRecord]] = {}
    for event in events:
        window_start = _window_start(event.timestamp.date())
        grouped.setdefault((event.user_identifier, window_start), []).append(event)

    sessions: list[SessionRecord] = []
    for (id_hash, window_start), rows in sorted(grouped.items(), key=lambda item: (item[0][0], item[0][1])):
        ordered = sorted(rows, key=lambda row: row.timestamp)
        start = ordered[0].timestamp
        end = ordered[-1].timestamp
        duration = max((end - start).total_seconds() / 60.0, 5.0 / 60.0)
        session_key = f"{id_hash}:{window_start.isoformat()}:{ordered[0].event_hash}:{ordered[-1].event_hash}"
        sessions.append(SessionRecord(
            session_id=sha256_hex(session_key)[:32],
            id_hash=id_hash,
            session_start=start,
            session_end=end,
            duration_minutes=round(duration, 6),
            event_count=len(ordered),
        ))
    return sessions


def _window_start(day: date) -> date:
    base = date(2026, 1, 1)
    offset = ((day - base).days // 14) * 14
    return date.fromordinal(base.toordinal() + offset)


def replay_pipeline(events: Sequence[EventRecord]) -> dict[str, Any]:
    if not events:
        raise ValueError("replay requires at least one event")
    id_hashes = {event.user_identifier for event in events}
    if len(id_hashes) != 1:
        raise ValueError("phase 5 deterministic replay expects one pseudonymous subject")
    id_hash = sorted(id_hashes)[0]
    sessions = deterministic_sessions(events)
    windows = sorted({_window_start(event.timestamp.date()) for event in events})
    metrics = [
        compute_window_metrics(id_hash, window_start, events, sessions)
        for window_start in windows
    ]
    baseline = compute_baseline(id_hash, metrics[:4])
    outputs = []
    for item in metrics:
        ieo = compute_ieo(item, baseline)
        events_in_window = [
            event.event_hash for event in sorted(events, key=lambda row: row.timestamp)
            if _window_start(event.timestamp.date()) == item.window_start
        ]
        outputs.append({
            "output_type": "ieo_window",
            "id_hash": ieo.id_hash,
            "window_start": ieo.window_start.isoformat(),
            "ieo_score": ieo.ieo_score,
            "ieo_linear": ieo.ieo_linear,
            "ieo_sat": ieo.ieo_sat,
            "z_t": ieo.z_t,
            "z_e": ieo.z_e,
            "z_v": ieo.z_v,
            "z_d": ieo.z_d,
            "source_event_hashes": events_in_window,
            "algorithm_version": CURRENT_ALGORITHM_VERSION,
            "algorithm_parameters": algorithm_parameters(),
        })
    processing = [
        {"stage": "events_loaded", "event_count": len(events)},
        {"stage": "sessions_derived", "session_count": len(sessions)},
        {"stage": "windows_computed", "window_count": len(metrics)},
        {"stage": "baseline_computed", "baseline_window_count": baseline.baseline_window_count},
        {"stage": "outputs_computed", "output_count": len(outputs), "algorithm_version": CURRENT_ALGORITHM_VERSION},
    ]
    return {
        "id_hash": id_hash,
        "sessions": [_model_dump(item) for item in sessions],
        "window_metrics": [_model_dump(item) for item in metrics],
        "processing": processing,
        "outputs": outputs,
    }


def build_manifest(
    *,
    session_id: str,
    evidence_mode: str,
    versions: Mapping[str, str],
    input_chain: Sequence[Mapping[str, Any]],
    processing_chain: Sequence[Mapping[str, Any]],
    output_chain: Sequence[Mapping[str, Any]],
    admin_audit_chain: Sequence[Mapping[str, Any]],
    generated_at: str = "2026-06-23T00:00:00+00:00",
    real_iped_available: bool = False,
) -> dict[str, Any]:
    manifest = {
        "manifest_version": "SUPREME-PHASE5-MANIFEST-1.0.0",
        "session_id": session_id,
        "evidence_mode": evidence_mode,
        "real_iped_available": real_iped_available,
        "generated_at": generated_at,
        "versions": dict(versions),
        "algorithm_parameters_digest": sha256_hex(algorithm_parameters()),
        "input_chain_tip": chain_tip(input_chain),
        "processing_chain_tip": chain_tip(processing_chain),
        "output_chain_tip": chain_tip(output_chain),
        "admin_audit_chain_tip": chain_tip(admin_audit_chain),
    }
    manifest["manifest_hash"] = sha256_hex({k: v for k, v in manifest.items() if k != "manifest_hash"})
    return manifest


def build_integrity_report(
    *,
    manifest: Mapping[str, Any],
    signed_events: Sequence[Mapping[str, Any]],
    input_chain: Sequence[Mapping[str, Any]],
    processing_chain: Sequence[Mapping[str, Any]],
    output_chain: Sequence[Mapping[str, Any]],
    admin_audit_chain: Sequence[Mapping[str, Any]],
    replay: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "report_version": "SUPREME-PHASE5-INTEGRITY-1.0.0",
        "status": "verifiable",
        "session_id": manifest["session_id"],
        "evidence_mode": manifest["evidence_mode"],
        "signed_event_count": len(signed_events),
        "output_count": len(replay["outputs"]),
        "input_chain_tip": chain_tip(input_chain),
        "processing_chain_tip": chain_tip(processing_chain),
        "output_chain_tip": chain_tip(output_chain),
        "admin_audit_chain_tip": chain_tip(admin_audit_chain),
        "manifest_hash": manifest["manifest_hash"],
        "versions": manifest["versions"],
        "algorithm_parameters_digest": manifest["algorithm_parameters_digest"],
        "replay_digest": sha256_hex(replay["outputs"]),
        "reconstruction_rule": "verify signatures, verify hash chains, replay signed payloads, compare output chain tip",
    }


def build_forensic_export(
    *,
    manifest: Mapping[str, Any],
    signed_events: Sequence[Mapping[str, Any]],
    input_chain: Sequence[Mapping[str, Any]],
    processing_chain: Sequence[Mapping[str, Any]],
    output_chain: Sequence[Mapping[str, Any]],
    admin_audit_chain: Sequence[Mapping[str, Any]],
    integrity_report: Mapping[str, Any],
) -> dict[str, Any]:
    export = {
        "export_version": "SUPREME-PHASE5-FORENSIC-EXPORT-1.0.0",
        "manifest": dict(manifest),
        "signed_events": list(signed_events),
        "chains": {
            "input": list(input_chain),
            "processing": list(processing_chain),
            "output": list(output_chain),
            "admin_audit": list(admin_audit_chain),
        },
        "integrity_report": dict(integrity_report),
    }
    export["export_hash"] = sha256_hex({k: v for k, v in export.items() if k != "export_hash"})
    return export


def verify_forensic_export(export: Mapping[str, Any], signing_material: str) -> bool:
    if sha256_hex({k: v for k, v in export.items() if k != "export_hash"}) != export.get("export_hash"):
        raise ValueError("forensic export hash mismatch")
    for event in export["signed_events"]:
        verify_signed_event(event, signing_material)
    chains = export["chains"]
    verify_hash_chain(chains["input"], chain_id="phase5-input")
    verify_hash_chain(chains["processing"], chain_id="phase5-processing")
    verify_hash_chain(chains["output"], chain_id="phase5-output")
    verify_hash_chain(chains["admin_audit"], chain_id="phase5-admin-audit")
    manifest = export["manifest"]
    expected_manifest_hash = sha256_hex({k: v for k, v in manifest.items() if k != "manifest_hash"})
    if expected_manifest_hash != manifest.get("manifest_hash"):
        raise ValueError("manifest hash mismatch")
    report = export["integrity_report"]
    expected = {
        "input_chain_tip": chain_tip(chains["input"]),
        "processing_chain_tip": chain_tip(chains["processing"]),
        "output_chain_tip": chain_tip(chains["output"]),
        "admin_audit_chain_tip": chain_tip(chains["admin_audit"]),
        "manifest_hash": manifest["manifest_hash"],
    }
    for key, value in expected.items():
        if report.get(key) != value:
            raise ValueError(f"integrity report mismatch: {key}")
        if manifest.get(key) != value and key != "manifest_hash":
            raise ValueError(f"manifest mismatch: {key}")
    payloads = [EventRecord(**event["payload"]) for event in export["signed_events"]]
    replay = replay_pipeline(payloads)
    replay_chain = build_hash_chain(replay["outputs"], chain_id="phase5-output")
    if chain_tip(replay_chain) != report.get("output_chain_tip"):
        raise ValueError("deterministic replay output chain diverged")
    if sha256_hex(replay["outputs"]) != report.get("replay_digest"):
        raise ValueError("deterministic replay digest diverged")
    return True


def _model_dump(value: Any) -> dict[str, Any]:
    dumped = value.model_dump(mode="json")
    return json.loads(canonical_json(dumped))


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

