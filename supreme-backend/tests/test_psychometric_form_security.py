import pytest
from fastapi import HTTPException
from starlette.requests import Request

from src.app.api import psychometric
from src.app.api.psychometric import SubmitRequest


class Settings:
    api_secret_key = "a" * 64
    api_ingest_token = "b" * 64


def make_request(headers=None):
    raw_headers = []
    for key, value in (headers or {}).items():
        raw_headers.append((key.lower().encode("latin-1"), value.encode("latin-1")))
    return Request({"type": "http", "method": "POST", "path": "/", "headers": raw_headers})


@pytest.fixture(autouse=True)
def settings(monkeypatch):
    monkeypatch.setattr(psychometric, "get_settings", lambda: Settings())


def test_form_token_roundtrip():
    token, expires_at = psychometric._create_form_token("user-1", "SRQ20")
    payload = psychometric._verify_form_token(token)

    assert expires_at == payload["exp"]
    assert payload["id_hash"] == "user-1"
    assert payload["instrument"] == "SRQ20"


def test_form_token_rejects_tampering():
    token, _ = psychometric._create_form_token("user-1", "SRQ20")
    tampered = token[:-1] + ("a" if token[-1] != "a" else "b")

    with pytest.raises(HTTPException) as exc:
        psychometric._verify_form_token(tampered)

    assert exc.value.status_code == 403


def test_form_token_rejects_expired_ticket():
    token, _ = psychometric._create_form_token("user-1", "SRQ20", ttl_seconds=-1)

    with pytest.raises(HTTPException) as exc:
        psychometric._verify_form_token(token)

    assert exc.value.status_code == 401


def test_submit_allows_ingest_bearer_token():
    request = make_request({"authorization": "Bearer " + Settings.api_ingest_token})
    body = SubmitRequest(id_hash="user-1", instrument="SRQ20", responses=[0] * 20)

    assert psychometric._authorize_psychometric_submit(request, body) is None


def test_submit_requires_cookie_or_bearer_token():
    request = make_request()
    body = SubmitRequest(id_hash="user-1", instrument="SRQ20", responses=[0] * 20)

    with pytest.raises(HTTPException) as exc:
        psychometric._authorize_psychometric_submit(request, body)

    assert exc.value.status_code == 401


def test_submit_allows_matching_form_cookie():
    token, _ = psychometric._create_form_token("user-1", "SRQ20")
    request = make_request({"cookie": f"supreme_form_token={token}"})
    body = SubmitRequest(id_hash="user-1", instrument="SRQ20", responses=[0] * 20)

    assert psychometric._authorize_psychometric_submit(request, body) is None


def test_submit_rejects_cookie_for_different_instrument():
    token, _ = psychometric._create_form_token("user-1", "DASS21")
    request = make_request({"cookie": f"supreme_form_token={token}"})
    body = SubmitRequest(id_hash="user-1", instrument="SRQ20", responses=[0] * 20)

    with pytest.raises(HTTPException) as exc:
        psychometric._authorize_psychometric_submit(request, body)

    assert exc.value.status_code == 403
