from __future__ import annotations

from pathlib import Path

from src.app.auth import ROLE_PERMISSIONS, scoped_id_filter
from src.app.api import export, product


ROOT = Path(__file__).resolve().parents[1]


def test_phase6_product_permissions_by_role():
    assert "product:studies" in ROLE_PERMISSIONS["master"]
    assert "product:participants" in ROLE_PERMISSIONS["pesquisador"]
    assert "product:pipeline" in ROLE_PERMISSIONS["auditor"]
    assert "product:pipeline" in ROLE_PERMISSIONS["operador"]
    assert "product:participants" not in ROLE_PERMISSIONS["leitura_agregada"]
    assert "report:signed" in ROLE_PERMISSIONS["auditor"]


def test_phase6_scoped_filter_covers_institution_study_case_and_participant():
    user = {
        "role": "pesquisador",
        "scopes": {
            "institutions": ["inst-1"],
            "studies": ["study-1"],
            "cases": ["case-1"],
            "participants": ["participant-1"],
        },
    }
    where, params = scoped_id_filter(user, "iw.id_hash")
    assert "participant_registry pr_scope" in where
    assert "pr_scope.institution_id" in where
    assert "pr_scope.study_id" in where
    assert "pr_scope.case_id" in where
    assert "iw.id_hash IN" in where
    assert params["scope_institution_0"] == "inst-1"
    assert params["scope_study_0"] == "study-1"
    assert params["scope_case_0"] == "case-1"
    assert params["scope_participant_0"] == "participant-1"


def test_phase6_product_router_exposes_required_workspaces():
    paths = {route.path for route in product.router.routes}
    assert "/api/product/workspace" in paths
    assert "/api/product/studies" in paths
    assert "/api/product/participants" in paths
    assert "/api/product/pipeline-health" in paths
    assert "/api/product/data-quality" in paths
    assert "/api/product/report/html" in paths
    assert "/api/product/report/pdf" in paths


def test_phase6_report_signing_and_pdf_are_backend_generated():
    payload = {"b": 2, "a": 1}
    assert product.canonical_json(payload) == '{"a":1,"b":2}'
    assert product.sign_payload(payload) == product.sign_payload(payload)
    pdf = product.build_minimal_pdf(["SENTINELA signed report", "digest abc"])
    assert pdf.startswith(b"%PDF-1.4")
    assert b"%%EOF" in pdf


def test_phase6_export_router_exposes_scientific_formats_and_dictionary():
    paths = {route.path for route in export.router.routes}
    assert "/api/export/csv" in paths
    assert "/api/export/json" in paths
    assert "/api/export/parquet" in paths
    assert "/api/export/data-dictionary" in paths
    names = {item["name"] for item in export.DATA_DICTIONARY}
    assert "algorithm_version" in names
    assert "algorithm_parameters" in names


def test_phase6_sentinela_remains_viewer_only():
    files = [
        ROOT / "src" / "app" / "api" / "dashboard.py",
        ROOT / "src" / "app" / "api" / "export.py",
        ROOT / "src" / "app" / "api" / "product.py",
        ROOT / "static" / "index.html",
        ROOT / "static" / "war_room.html",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in files)
    forbidden = [
        "compute_ieo(",
        "compute_psi(",
        "evaluate_red_flags(",
        "check_critical_load(",
    ]
    assert [pattern for pattern in forbidden if pattern in combined] == []


def test_phase6_frontend_has_role_oriented_sections_and_empty_states():
    index = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    for section in [
        "section-studies",
        "section-pipeline",
        "section-dataquality",
        "section-exports",
    ]:
        assert section in index
    assert "Nenhum estudo" in index
    assert "Sem dados de qualidade" in index
    assert "/api/product/report/pdf" in index


def test_phase6_war_room_dashboard_return_does_not_flash_login():
    index = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    war_room = (ROOT / "static" / "war_room.html").read_text(encoding="utf-8")

    assert '<body class="auth-restoring">' in index
    assert "body.auth-restoring #login-screen" in index
    assert "const INITIAL_SECTION" in index
    assert "navigateTo(INITIAL_SECTION)" in index

    assert 'href="/sentinela/?section=overview&from=warroom"' in war_room
    assert "const DASHBOARD_URL = '/sentinela/?section=overview&from=warroom';" in war_room
    assert "window.location.href = '/';" not in war_room


def test_phase6_login_transition_uses_authenticated_state_not_inline_display():
    index = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    css = (ROOT / "static" / "sentinela-redesign.css").read_text(encoding="utf-8")

    assert "document.body.classList.add('sentinela-authenticated')" in index
    assert "document.body.classList.remove('sentinela-authenticated')" in index
    assert "body.sentinela-authenticated #login-screen.sentinela-lab-login" in css
    assert "display: none !important" in css
    assert "document.getElementById('login-screen').style.display = 'none'" not in index
    assert "document.getElementById('login-screen').style.display = 'flex'" not in index


def test_phase6_login_hero_title_is_localized_in_all_supported_languages():
    index = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    ux = (ROOT / "static" / "sentinela-ux.js").read_text(encoding="utf-8")

    assert 'data-i18n="heroTitle"' in index
    assert 'heroTitle: "Governança longitudinal da exposição em perícia digital"' in ux
    assert 'heroTitle: "Longitudinal governance of digital forensics exposure"' in ux
    assert 'heroTitle: "Gobernanza longitudinal de la exposición en pericia digital"' in ux
