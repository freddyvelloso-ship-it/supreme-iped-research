from __future__ import annotations

from pathlib import Path

from datetime import datetime, timezone

from src.app.api.ingest import (
    IEO_FULL_UPSERT_SQL,
    LONGITUDINAL_PROFILE_UPSERT_SQL,
    LongitudinalProfilePayload,
    PSI_ONLY_UPDATE_SQL,
)


ROOT = Path(__file__).resolve().parents[1]
STATIC_FILES = [ROOT / "static" / "index.html", ROOT / "static" / "war_room.html"]


def _static_text() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in STATIC_FILES)


def test_sentinela_static_has_no_critical_formulas_or_threshold_rules():
    text = _static_text()
    forbidden = [
        "IEO_linear",
        "IEO_sat",
        "IEO_final",
        "PSI =",
        "threshold crítico",
        "IEO >",
        "IEO_z >",
        "1.5σ",
        "clinicamente elevada",
        "avaliação clínica",
        "Nível de Risco",
    ]
    missing = [pattern for pattern in forbidden if pattern in text]
    assert missing == []


def test_sentinela_dashboard_surfaces_algorithm_metadata_without_recomputing():
    dashboard = (ROOT / "src" / "app" / "api" / "dashboard.py").read_text(encoding="utf-8")
    export = (ROOT / "src" / "app" / "api" / "export.py").read_text(encoding="utf-8")
    static = _static_text()

    assert "algorithm_version" in dashboard
    assert "algorithm_parameters" in dashboard
    assert "algorithm_version" in export
    assert "algorithm_parameters" in export
    assert "longitudinal_profile" in dashboard
    assert "classify_longitudinal_profile" not in dashboard
    assert "classifyLongitudinalProfile" not in static
    assert "compute_ieo" not in dashboard
    assert "compute_psi" not in dashboard
    assert "evaluate_red_flags" not in dashboard


def test_ingest_persists_supreme_algorithm_metadata_viewer_only():
    assert "algorithm_version" in IEO_FULL_UPSERT_SQL
    assert "algorithm_parameters" in IEO_FULL_UPSERT_SQL
    assert "algorithm_version" in PSI_ONLY_UPDATE_SQL
    assert "algorithm_parameters" in PSI_ONLY_UPDATE_SQL


def test_ingest_contract_accepts_supreme_longitudinal_profile_output():
    payload = LongitudinalProfilePayload(
        id_hash="a" * 64,
        profile_class="resiliente",
        profile_label="Resiliente",
        profile_confidence=0.78,
        profile_evidence={"classification_basis": "operational_longitudinal_profile"},
        baseline_version=2,
        algorithm_version="SUPREME-ANALYTICS-1.0.0",
        algorithm_parameters={"longitudinal_profile": {"min_history_windows": 4}},
        classified_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
    )

    assert payload.profile_class == "resiliente"
    assert "longitudinal_profiles" in LONGITUDINAL_PROFILE_UPSERT_SQL
    assert "profile_evidence" in LONGITUDINAL_PROFILE_UPSERT_SQL
    assert "algorithm_parameters" in LONGITUDINAL_PROFILE_UPSERT_SQL
