from __future__ import annotations

from typing import Any


SUPPORTED_INGEST_EVENTS = {"file_open", "image_view", "video_play", "classification_event"}


def event_to_supreme_record(envelope: dict[str, Any]) -> dict[str, Any]:
    event = envelope["event"]
    return {
        "schema_version": "SUPREME-FIELD-INGEST-1.0",
        "institution_id": envelope["institution_id"],
        "study_id": envelope["study_id"],
        "case_id": envelope["case_id"],
        "participant_scope": envelope["participant_scope"],
        "agent_id": envelope["agent_id"],
        "event_type": event["event_type"],
        "timestamp": event["timestamp"],
        "source_id": event.get("source_id", ""),
        "item_id": event.get("item_id", ""),
        "item_hash": event.get("item_hash", ""),
        "media_type": event.get("media_type", "unknown"),
        "duration_seconds": float(event.get("duration_seconds") or 0),
        "severity": event.get("severity", ""),
        "plugin_version": event.get("plugin_version", ""),
        "agent_chain_hash": envelope["chain_hash"],
        "agent_previous_hash": envelope["previous_hash"],
        "agent_signature": envelope["signature"],
    }


def event_to_central_ingest_event(envelope: dict[str, Any]) -> dict[str, Any] | None:
    event = envelope["event"]
    event_type = event["event_type"]
    if event_type not in SUPPORTED_INGEST_EVENTS:
        return None
    media_type = str(event.get("media_type", "preview")).lower()
    if media_type.startswith("image"):
        media = "image"
    elif media_type.startswith("video"):
        media = "video"
    else:
        media = "preview"
    try:
        severity = int(event.get("severity") or 1)
    except ValueError:
        severity = 1
    severity = max(1, min(5, severity))
    return {
        "timestamp": event["timestamp"],
        "event_type": event_type,
        "media_type": media,
        "severity": severity,
        "duration_seconds": float(event.get("duration_seconds") or 0),
        "user_identifier": envelope["participant_scope"],
        "source_tool": "iped",
    }


def envelopes_to_central_ingest_request(envelopes: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    events = []
    for envelope in envelopes:
        mapped = event_to_central_ingest_event(envelope)
        if mapped is not None:
            events.append(mapped)
    return {"events": events}
