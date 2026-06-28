import json
import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "supreme-proxy"))
sys.path.insert(0, str(ROOT / "supreme-watcher"))

import proxy as proxy_module  # noqa: E402
import watcher as watcher_module  # noqa: E402


STRONG_SALT = "research-validation-salt-00000000000001"


def test_proxy_health_does_not_expose_audit_log_path(monkeypatch) -> None:
    monkeypatch.setattr(proxy_module, "IPED_API_URL", "http://127.0.0.1:9")
    client = TestClient(proxy_module.app)

    response = client.get("/health")

    payload = response.json()
    assert "audit_log_path" not in payload
    assert payload["audit_log_configured"] is True
    assert "supreme_audit" not in response.text


def test_watcher_builds_only_allowlisted_safe_event(monkeypatch) -> None:
    monkeypatch.setattr(watcher_module, "SALT", STRONG_SALT)
    entry = {
        "event": "close",
        "userId": "perito.real@instituicao.example",
        "itemId": "C:\\caso\\midia_real.jpg",
        "openTs": 1780000000000,
        "closeTs": 1780000010000,
        "mediaType": "image/jpeg",
        "nudityClass": "3",
    }

    event = watcher_module.build_supreme_event(entry)
    serialized = json.dumps(event, sort_keys=True)

    assert set(event) == {
        "timestamp",
        "event_type",
        "media_type",
        "severity",
        "duration_seconds",
        "user_identifier",
        "source_tool",
        "event_hash",
    }
    assert len(event["user_identifier"]) == 64
    assert "perito.real" not in serialized
    assert "midia_real" not in serialized
    assert "C:\\caso" not in serialized


def test_proxy_sanitizer_blocks_extra_raw_fields(monkeypatch) -> None:
    monkeypatch.setattr(proxy_module, "SALT", STRONG_SALT)
    event = {
        "timestamp": "2026-01-01T00:00:00+00:00",
        "event_type": "image_view",
        "media_type": "image",
        "severity": 3,
        "duration_seconds": 1.0,
        "user_identifier": proxy_module.pseudonymize("operator-1"),
        "source_tool": "iped",
        "_iped_item_id": "raw-item",
    }

    try:
        proxy_module.sanitize_supreme_event(event)
    except Exception as exc:
        assert "campos nao permitidos" in str(exc)
    else:
        raise AssertionError("raw extra field was not blocked")
