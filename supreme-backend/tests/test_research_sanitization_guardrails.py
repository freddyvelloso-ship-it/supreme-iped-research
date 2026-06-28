from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from src.engine.supreme.models import EventRecord, IngestRequest


SAFE_ID = "a" * 64


def base_event(**overrides):
    payload = {
        "timestamp": datetime(2026, 1, 1, 12, tzinfo=timezone.utc),
        "event_type": "image_view",
        "media_type": "image",
        "severity": 3,
        "duration_seconds": 10.0,
        "user_identifier": SAFE_ID,
        "source_tool": "iped",
    }
    payload.update(overrides)
    return payload


def test_event_record_requires_safe_pseudonym() -> None:
    with pytest.raises(ValidationError):
        EventRecord(**base_event(user_identifier="perito-real"))


def test_event_record_rejects_extra_iped_identifiers() -> None:
    with pytest.raises(ValidationError):
        EventRecord(**base_event(_iped_item_id="12345"))


def test_ingest_request_rejects_extra_raw_payload() -> None:
    with pytest.raises(ValidationError):
        IngestRequest(events=[base_event()], raw_csv_line="C:\\caso\\midia.jpg")


def test_event_record_accepts_safe_allowlist() -> None:
    event = EventRecord(**base_event())
    assert event.user_identifier == SAFE_ID
    assert event.event_hash is not None
    assert len(event.event_hash) == 64
