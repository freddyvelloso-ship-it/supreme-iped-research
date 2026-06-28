"""
sentinela.app.api.product
=========================
Product-grade SENTINELA endpoints for role workspaces, study operation,
pipeline health, data quality and signed backend reports.

SENTINELA remains viewer-only: analytical outputs are read from SUPREME
materialized records and are not recalculated here.
"""

from __future__ import annotations

import hashlib
import hmac
import html
import json
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, Response
from sqlalchemy import text

from ..auth import require_permission, scoped_id_filter
from ..config import settings
from ..db import AsyncSession, get_db

router = APIRouter(prefix="/api/product", tags=["SENTINELA Produto"])


ROLE_WORKSPACES = {
    "master": [
        "overview",
        "studies",
        "participants",
        "pipeline",
        "data_quality",
        "reports",
        "exports",
        "users",
        "audit",
    ],
    "pesquisador": ["overview", "studies", "participants", "data_quality", "reports", "exports"],
    "auditor": ["overview", "studies", "participants", "pipeline", "data_quality", "reports", "exports", "audit"],
    "operador": ["overview", "studies", "participants", "pipeline", "data_quality"],
    "leitura_agregada": ["overview", "studies", "data_quality"],
}


def _json_default(value: Any) -> Any:
    if isinstance(value, (datetime,)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return str(value)


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, default=_json_default, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def payload_digest(payload: Any) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def sign_payload(payload: Any) -> str:
    return hmac.new(
        settings.secret_key.encode("utf-8"),
        canonical_json(payload).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def _pdf_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_minimal_pdf(lines: list[str]) -> bytes:
    content_lines = ["BT", "/F1 10 Tf", "50 780 Td"]
    for index, line in enumerate(lines):
        if index:
            content_lines.append("0 -16 Td")
        content_lines.append(f"({_pdf_escape(line[:110])}) Tj")
    content_lines.append("ET")
    stream = "\n".join(content_lines).encode("utf-8")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    body = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, obj in enumerate(objects, start=1):
        offsets.append(len(body))
        body.extend(f"{number} 0 obj\n".encode("ascii"))
        body.extend(obj)
        body.extend(b"\nendobj\n")
    xref_offset = len(body)
    body.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    body.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        body.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    body.extend(
        f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    )
    return bytes(body)


async def _overview_payload(db: AsyncSession, user: dict) -> dict:
    scope_where, scope_params = scoped_id_filter(user, "iw.id_hash")
    overview = await db.execute(text(f"""
        SELECT
            COUNT(DISTINCT iw.id_hash) AS participants,
            COUNT(*) AS windows,
            ROUND(AVG(iw.dq_score)::numeric, 3) AS avg_dq,
            MAX(iw.window_start) AS last_window,
            COUNT(*) FILTER (WHERE iw.algorithm_version IS NULL) AS missing_algorithm_metadata
        FROM ieo_windows iw
        WHERE 1=1{scope_where}
    """), scope_params)
    data = dict(overview.mappings().one_or_none() or {})
    versions = await db.execute(text(f"""
        SELECT iw.algorithm_version, COUNT(*) AS rows
        FROM ieo_windows iw
        WHERE 1=1{scope_where}
        GROUP BY iw.algorithm_version
        ORDER BY iw.algorithm_version
    """), scope_params)
    data["algorithm_versions"] = [dict(row) for row in versions.mappings()]
    return data


@router.get("/workspace")
async def role_workspace(user: dict = Depends(require_permission("dashboard:aggregate"))):
    return {
        "role": user["role"],
        "workspace": ROLE_WORKSPACES.get(user["role"], ["overview"]),
        "permissions": user.get("permissions", []),
        "scopes": user.get("scopes", {}),
    }


@router.get("/studies")
async def studies(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_permission("product:studies")),
):
    scope_where, scope_params = scoped_id_filter(user, "pr.id_hash")
    result = await db.execute(text(f"""
        SELECT
            COALESCE(i.id, pr.institution_id, 'unassigned') AS institution_id,
            COALESCE(i.name, pr.institution_id, 'Sem instituicao') AS institution_name,
            COALESCE(s.id, pr.study_id, 'unassigned') AS study_id,
            COALESCE(s.name, pr.study_id, 'Sem estudo') AS study_name,
            'active' AS study_status,
            COALESCE(c.id, pr.case_id, 'unassigned') AS case_id,
            COALESCE(c.name, pr.case_id, 'Sem caso') AS case_name,
            COUNT(DISTINCT pr.id_hash) AS participants,
            MAX(iw.window_start) AS last_window,
            ARRAY_REMOVE(ARRAY_AGG(DISTINCT iw.algorithm_version), NULL) AS algorithm_versions
        FROM participant_registry pr
        LEFT JOIN institutions i ON i.id = pr.institution_id
        LEFT JOIN studies s ON s.id = pr.study_id
        LEFT JOIN cases c ON c.id = pr.case_id
        LEFT JOIN ieo_windows iw ON iw.id_hash = pr.id_hash
        WHERE 1=1{scope_where}
        GROUP BY
            COALESCE(i.id, pr.institution_id, 'unassigned'),
            COALESCE(i.name, pr.institution_id, 'Sem instituicao'),
            COALESCE(s.id, pr.study_id, 'unassigned'),
            COALESCE(s.name, pr.study_id, 'Sem estudo'),
            COALESCE(c.id, pr.case_id, 'unassigned'),
            COALESCE(c.name, pr.case_id, 'Sem caso')
        ORDER BY institution_name, study_name, case_name
    """), scope_params)
    return {"items": [dict(row) for row in result.mappings()], "empty_state": "Nenhum estudo no escopo atual."}


@router.get("/participants")
async def participants(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_permission("product:participants")),
):
    scope_where, scope_params = scoped_id_filter(user, "pr.id_hash")
    result = await db.execute(text(f"""
        WITH latest AS (
            SELECT DISTINCT ON (id_hash)
                id_hash, window_start, ieo_score, psi_score, convergence_class,
                dq_score, algorithm_version, algorithm_parameters
            FROM ieo_windows
            ORDER BY id_hash, window_start DESC
        )
        SELECT
            pr.id_hash,
            pr.institution_id,
            pr.study_id,
            pr.case_id,
            COALESCE(lc.status, 'active') AS status,
            latest.window_start AS last_window,
            latest.ieo_score AS last_ieo,
            latest.psi_score AS last_psi,
            latest.convergence_class,
            latest.dq_score,
            latest.algorithm_version,
            latest.algorithm_parameters,
            lp.profile_class,
            lp.profile_label,
            lp.profile_confidence,
            lp.classified_at AS profile_classified_at,
            lp.algorithm_version AS profile_algorithm_version,
            lp.algorithm_parameters AS profile_algorithm_parameters
        FROM participant_registry pr
        LEFT JOIN latest ON latest.id_hash = pr.id_hash
        LEFT JOIN participant_lifecycle lc ON lc.id_hash = pr.id_hash
        LEFT JOIN longitudinal_profiles lp ON lp.id_hash = pr.id_hash
        WHERE COALESCE(lc.status, 'active') != 'deleted'{scope_where}
        ORDER BY pr.study_id, pr.case_id, pr.id_hash
    """), scope_params)
    return {"items": [dict(row) for row in result.mappings()], "empty_state": "Nenhum participante no escopo atual."}


@router.get("/pipeline-health")
async def pipeline_health(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_permission("product:pipeline")),
):
    result = await db.execute(text("""
        SELECT
            (SELECT COUNT(*) FROM ieo_windows) AS ieo_windows,
            (SELECT COUNT(*) FROM psico_submissions) AS psychometric_submissions,
            (SELECT COUNT(*) FROM red_flags) AS red_flags,
            (SELECT MAX(window_start) FROM ieo_windows) AS last_analytic_window,
            (SELECT MAX(submitted_at) FROM psico_submissions) AS last_psychometric_submission,
            (SELECT COUNT(DISTINCT algorithm_version) FROM ieo_windows WHERE algorithm_version IS NOT NULL) AS algorithm_versions
    """))
    data = dict(result.mappings().one())
    has_data = any(data.get(key) for key in ("ieo_windows", "psychometric_submissions", "red_flags"))
    data["status"] = "ok" if has_data else "no_data"
    data["source"] = "sentinela_viewer_cache"
    data["checks"] = {
        "supreme_outputs_present": bool(data.get("ieo_windows")),
        "psychometric_outputs_present": bool(data.get("psychometric_submissions")),
        "red_flags_present": bool(data.get("red_flags")),
    }
    return data


@router.get("/data-quality")
async def data_quality(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_permission("product:data_quality")),
):
    scope_where, scope_params = scoped_id_filter(user, "iw.id_hash")
    result = await db.execute(text(f"""
        SELECT
            COUNT(*) AS windows,
            ROUND(AVG(iw.dq_score)::numeric, 3) AS avg_dq,
            COUNT(*) FILTER (WHERE iw.dq_score < 0.5) AS low_quality_windows,
            COUNT(*) FILTER (WHERE iw.algorithm_version IS NULL OR iw.algorithm_parameters IS NULL) AS missing_algorithm_metadata,
            COUNT(DISTINCT iw.id_hash) AS participants
        FROM ieo_windows iw
        WHERE 1=1{scope_where}
    """), scope_params)
    by_version = await db.execute(text(f"""
        SELECT iw.algorithm_version, COUNT(*) AS windows
        FROM ieo_windows iw
        WHERE 1=1{scope_where}
        GROUP BY iw.algorithm_version
        ORDER BY iw.algorithm_version
    """), scope_params)
    data = dict(result.mappings().one())
    data["by_algorithm_version"] = [dict(row) for row in by_version.mappings()]
    data["empty_state"] = "Sem janelas analiticas para avaliar qualidade de dados."
    return data


def _report_html(payload: dict) -> str:
    overview = payload["overview"]
    quality = payload["data_quality"]
    signature = payload["signature"]
    return "\n".join([
        "<!doctype html>",
        "<html><head><meta charset=\"utf-8\"><title>SENTINELA Signed Report</title></head>",
        "<body>",
        "<h1>SENTINELA - Relatorio assinado</h1>",
        f"<p><strong>Gerado em:</strong> {html.escape(payload['generated_at'])}</p>",
        f"<p><strong>Papel:</strong> {html.escape(payload['role'])}</p>",
        f"<p><strong>Participantes:</strong> {html.escape(str(overview.get('participants') or 0))}</p>",
        f"<p><strong>Janelas:</strong> {html.escape(str(overview.get('windows') or 0))}</p>",
        f"<p><strong>DQ medio:</strong> {html.escape(str(quality.get('avg_dq')))}</p>",
        f"<p><strong>Metadados ausentes:</strong> {html.escape(str(quality.get('missing_algorithm_metadata') or 0))}</p>",
        f"<p><strong>Digest:</strong> {html.escape(payload['digest'])}</p>",
        f"<p><strong>Assinatura:</strong> {html.escape(signature)}</p>",
        "<p>Limite: este relatorio nao e diagnostico clinico e nao estabelece nexo causal automatico.</p>",
        "</body></html>",
    ])


async def _signed_report_payload(db: AsyncSession, user: dict) -> dict:
    overview = await _overview_payload(db, user)
    quality_result = await data_quality(db, user)
    base = {
        "report_type": "sentinela_product_summary",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "role": user["role"],
        "scopes": user.get("scopes", {}),
        "overview": overview,
        "data_quality": {key: value for key, value in quality_result.items() if key != "empty_state"},
        "limits": [
            "not_clinical_diagnosis",
            "not_automatic_causal_nexus",
            "viewer_only_supreme_outputs",
        ],
    }
    base["digest"] = payload_digest(base)
    base["signature"] = sign_payload(base)
    return base


@router.get("/report/html")
async def signed_report_html(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_permission("report:signed")),
):
    payload = await _signed_report_payload(db, user)
    return HTMLResponse(
        content=_report_html(payload),
        headers={
            "X-SENTINELA-Report-Digest": payload["digest"],
            "X-SENTINELA-Report-Signature": payload["signature"],
        },
    )


@router.get("/report/pdf")
async def signed_report_pdf(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_permission("report:signed")),
):
    payload = await _signed_report_payload(db, user)
    pdf = build_minimal_pdf([
        "SENTINELA - Relatorio assinado",
        f"Gerado em: {payload['generated_at']}",
        f"Papel: {payload['role']}",
        f"Participantes: {payload['overview'].get('participants') or 0}",
        f"Janelas: {payload['overview'].get('windows') or 0}",
        f"Digest: {payload['digest']}",
        f"Assinatura: {payload['signature']}",
        "Limite: nao diagnostico clinico; nao nexo causal automatico.",
    ])
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="sentinela_report_signed.pdf"',
            "X-SENTINELA-Report-Digest": payload["digest"],
            "X-SENTINELA-Report-Signature": payload["signature"],
        },
    )
