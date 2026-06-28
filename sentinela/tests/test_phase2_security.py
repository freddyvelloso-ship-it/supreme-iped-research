from pathlib import Path

import pytest
from fastapi import HTTPException

from src.app.auth import CANONICAL_ROLES, assert_participant_scope, scoped_id_filter
from src.app.api import auth_router


class DummyClient:
    host = "127.0.0.1"


class DummyRequest:
    headers = {}
    client = DummyClient()


def test_phase2_roles_are_granular():
    assert set(CANONICAL_ROLES) == {
        "master",
        "pesquisador",
        "auditor",
        "operador",
        "leitura_agregada",
    }


def test_phase2_participant_scope_blocks_out_of_scope_access():
    user = {
        "role": "pesquisador",
        "scopes": {
            "institutions": [],
            "studies": [],
            "cases": [],
            "participants": ["participant-a"],
        },
    }
    assert_participant_scope(user, "participant-a")
    with pytest.raises(HTTPException) as exc:
        assert_participant_scope(user, "participant-b")
    assert exc.value.status_code == 403


def test_phase2_aggregate_role_cannot_access_individual_participant():
    user = {
        "role": "leitura_agregada",
        "scopes": {
            "institutions": ["*"],
            "studies": ["*"],
            "cases": ["*"],
            "participants": ["*"],
        },
    }
    with pytest.raises(HTTPException) as exc:
        assert_participant_scope(user, "participant-a")
    assert exc.value.status_code == 403


def test_phase2_scoped_query_filter_is_fail_closed_without_scope():
    user = {"role": "pesquisador", "scopes": {"participants": []}}
    where, params = scoped_id_filter(user)
    assert where == " AND 1=0"
    assert params == {}


def test_phase2_login_rate_limit_blocks_repeated_attempts():
    auth_router._LOGIN_ATTEMPTS.clear()
    request = DummyRequest()
    for _ in range(auth_router.LOGIN_RATE_LIMIT_MAX_ATTEMPTS):
        auth_router._check_login_rate_limit(request, "user@example.org")
    with pytest.raises(HTTPException) as exc:
        auth_router._check_login_rate_limit(request, "user@example.org")
    assert exc.value.status_code == 429
    auth_router._LOGIN_ATTEMPTS.clear()


def test_phase2_frontend_does_not_store_session_token_in_web_storage():
    static_root = Path(__file__).resolve().parents[1] / "static"
    combined = "\n".join(path.read_text(encoding="utf-8") for path in static_root.glob("*.html"))
    assert "sentinela_token" not in combined
    assert "localStorage" not in combined
    assert "sessionStorage" not in combined


def test_phase2_login_sets_httponly_cookie_instead_of_returning_browser_token():
    source = (Path(__file__).resolve().parents[1] / "src/app/api/auth_router.py").read_text(encoding="utf-8")
    assert "response.set_cookie" in source
    assert "httponly=True" in source
    assert "samesite=\"strict\"" in source
    assert '"access_token"' not in source
    assert "'access_token'" not in source
