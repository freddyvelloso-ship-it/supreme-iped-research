import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from src.app.api.ingest import IEOPayload, PsicoPayload
from src.app.sanitization import fail_if_sensitive


SAFE_ID = "b" * 64


def test_sentinela_rejects_raw_id_hash() -> None:
    with pytest.raises(ValidationError):
        IEOPayload(id_hash="operator-real", window_start="2026-01-01", ieo_score=1.0)


def test_sentinela_rejects_item_level_psychometric_extra_field() -> None:
    with pytest.raises(ValidationError):
        PsicoPayload(
            id_hash=SAFE_ID,
            instrument="SRQ20",
            score=10,
            window_ref="2026-01-01",
            submitted_at="2026-01-02",
            raw_answers=[1, 0, 1],
        )


def test_sentinela_rejects_paths_inside_nested_payload() -> None:
    with pytest.raises(HTTPException):
        fail_if_sensitive({"detail": {"safe_label": "C:\\caso\\midia.jpg"}})


def test_sentinela_accepts_aggregate_psychometric_payload() -> None:
    payload = PsicoPayload(
        id_hash=SAFE_ID,
        instrument="SRQ20",
        score=10,
        window_ref="2026-01-01",
        submitted_at="2026-01-02",
    )
    fail_if_sensitive(payload.model_dump())
