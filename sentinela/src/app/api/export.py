"""
sentinela.app.api.export
========================
Exportacao CSV para analise em R.
Inclui IEO, PSI, scores brutos e red flags por janela.
"""

from __future__ import annotations

import csv
import io
import json
from datetime import date
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import text

from ..auth import require_permission, scoped_id_filter
from ..db import AsyncSession, get_db
from .product import payload_digest, sign_payload

router = APIRouter(prefix="/api/export", tags=["Export"])

SCIENTIFIC_COLUMNS = [
    "id_hash", "institution_id", "study_id", "case_id", "window_start",
    "t_minutes", "e_events", "v_volume", "d_density", "dq_score",
    "ieo_score", "ieo_linear", "ieo_sat",
    "z_t", "z_e", "z_v", "z_d",
    "psi_score", "z_dass", "z_olbi", "z_srq", "z_panas_neg",
    "convergence_class", "algorithm_version", "algorithm_parameters",
    "profile_class", "profile_label", "profile_confidence",
    "profile_evidence", "profile_classified_at", "profile_algorithm_version",
    "dass_raw", "olbi_raw", "srq_raw", "panas_na_raw",
    "flags", "flag_severities",
]

DATA_DICTIONARY = [
    {"name": "id_hash", "type": "string", "description": "Pseudonymous participant identifier."},
    {"name": "institution_id", "type": "string", "description": "Institution scope from participant registry."},
    {"name": "study_id", "type": "string", "description": "Study scope from participant registry."},
    {"name": "case_id", "type": "string", "description": "Case scope from participant registry."},
    {"name": "window_start", "type": "timestamp", "description": "Analytical window start."},
    {"name": "t_minutes", "type": "float", "description": "Operational time component from SUPREME."},
    {"name": "e_events", "type": "integer", "description": "Event count component from SUPREME."},
    {"name": "v_volume", "type": "float", "description": "Volume component from SUPREME."},
    {"name": "d_density", "type": "float", "description": "Density component from SUPREME."},
    {"name": "dq_score", "type": "float", "description": "Data quality score emitted by SUPREME."},
    {"name": "ieo_score", "type": "float", "description": "IEO output calculated by SUPREME."},
    {"name": "psi_score", "type": "float", "description": "PSI output calculated by SUPREME."},
    {"name": "convergence_class", "type": "string", "description": "SUPREME convergence output."},
    {"name": "algorithm_version", "type": "string", "description": "SUPREME analytical algorithm version."},
    {"name": "algorithm_parameters", "type": "json", "description": "SUPREME analytical parameters used for the output."},
    {"name": "profile_class", "type": "string", "description": "Operational longitudinal expert profile calculated by SUPREME."},
    {"name": "profile_confidence", "type": "float", "description": "Confidence of the operational longitudinal profile."},
    {"name": "profile_evidence", "type": "json", "description": "Audit evidence for the SUPREME profile output."},
    {"name": "flags", "type": "string", "description": "Semicolon-separated red flag types emitted by SUPREME."},
    {"name": "flag_severities", "type": "string", "description": "Semicolon-separated red flag severities emitted by SUPREME."},
]


def _json_default(value):
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return str(value)


def _export_headers(payload: dict, filename: str, media_type: str) -> dict:
    return {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "X-SENTINELA-Export-Digest": payload_digest(payload),
        "X-SENTINELA-Export-Signature": sign_payload(payload),
        "X-SENTINELA-Export-Media-Type": media_type,
    }


async def _scientific_rows(
    db: AsyncSession,
    user: dict,
    start_date: Optional[date],
    end_date: Optional[date],
) -> list[dict]:
    date_filter = ""
    params: dict = {}
    if start_date:
        date_filter += " AND iw.window_start >= :start_date"
        params["start_date"] = start_date
    if end_date:
        date_filter += " AND iw.window_start <= :end_date"
        params["end_date"] = end_date
    scope_where, scope_params = scoped_id_filter(user, "iw.id_hash")
    date_filter += scope_where
    params.update(scope_params)

    query = text(f"""
        SELECT
            iw.id_hash,
            pr.institution_id,
            pr.study_id,
            pr.case_id,
            iw.window_start,
            iw.t_minutes,
            iw.e_events,
            iw.v_volume,
            iw.d_density,
            iw.dq_score,
            iw.ieo_score,
            iw.ieo_linear,
            iw.ieo_sat,
            iw.z_t,
            iw.z_e,
            iw.z_v,
            iw.z_d,
            iw.psi_score,
            iw.z_dass,
            iw.z_olbi,
            iw.z_srq,
            iw.z_panas_neg,
            iw.convergence_class,
            iw.algorithm_version,
            iw.algorithm_parameters,
            lp.profile_class,
            lp.profile_label,
            lp.profile_confidence,
            lp.profile_evidence,
            lp.classified_at AS profile_classified_at,
            lp.algorithm_version AS profile_algorithm_version,
            (SELECT score FROM psico_submissions
             WHERE id_hash = iw.id_hash
               AND instrument = 'DASS21'
               AND window_ref = iw.window_start
             ORDER BY submitted_at DESC LIMIT 1) AS dass_raw,
            (SELECT score FROM psico_submissions
             WHERE id_hash = iw.id_hash
               AND instrument = 'OLBI'
               AND window_ref = iw.window_start
             ORDER BY submitted_at DESC LIMIT 1) AS olbi_raw,
            (SELECT score FROM psico_submissions
             WHERE id_hash = iw.id_hash
               AND instrument = 'SRQ20'
               AND window_ref = iw.window_start
             ORDER BY submitted_at DESC LIMIT 1) AS srq_raw,
            (SELECT score FROM psico_submissions
             WHERE id_hash = iw.id_hash
               AND instrument = 'PANAS_SHORT'
               AND window_ref = iw.window_start
             ORDER BY submitted_at DESC LIMIT 1) AS panas_na_raw,
            (SELECT string_agg(flag_type, ';')
             FROM red_flags rf
             WHERE rf.id_hash = iw.id_hash
               AND rf.window_start = iw.window_start) AS flags,
            (SELECT string_agg(severity, ';')
             FROM red_flags rf
             WHERE rf.id_hash = iw.id_hash
               AND rf.window_start = iw.window_start) AS flag_severities
        FROM ieo_windows iw
        LEFT JOIN participant_registry pr ON pr.id_hash = iw.id_hash
        LEFT JOIN longitudinal_profiles lp ON lp.id_hash = iw.id_hash
        WHERE 1=1 {date_filter}
        ORDER BY iw.id_hash, iw.window_start
    """)
    result = await db.execute(query, params)
    return [dict(row) for row in result.mappings()]


@router.get("/csv", summary="Exportar dados completos para R")
async def export_csv(
    start_date: Optional[date] = Query(None),
    end_date:   Optional[date] = Query(None),
    db:         AsyncSession   = Depends(get_db),
    user:       dict           = Depends(require_permission("export:scientific")),
):
    """
    Exporta todos os dados disponíveis em formato CSV para análise em R.
    Inclui IEO por janela, PSI estimado (quando disponivel), red flags e
    scores psicométricos agregados por janela.

    Disponivel para papeis autorizados por RBAC e escopo.
    """
    rows = await _scientific_rows(db, user, start_date, end_date)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(SCIENTIFIC_COLUMNS)
    for row in rows:
        writer.writerow([row.get(column) for column in SCIENTIFIC_COLUMNS])

    filename = f"sentinela_export_{date.today().isoformat()}.csv"
    manifest = {"format": "csv", "filename": filename, "rows": len(rows), "columns": SCIENTIFIC_COLUMNS}
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers=_export_headers(manifest, filename, "text/csv"),
    )


@router.get("/json", summary="Exportar dados cientificos em JSON")
async def export_json(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_permission("export:scientific")),
):
    rows = await _scientific_rows(db, user, start_date, end_date)
    payload = {
        "format": "json",
        "generated_on": date.today().isoformat(),
        "columns": SCIENTIFIC_COLUMNS,
        "dictionary": DATA_DICTIONARY,
        "rows": rows,
        "limits": ["not_clinical_diagnosis", "not_automatic_causal_nexus"],
    }
    filename = f"sentinela_export_{date.today().isoformat()}.json"
    return Response(
        content=json.dumps(payload, ensure_ascii=False, default=_json_default, indent=2),
        media_type="application/json",
        headers=_export_headers(payload, filename, "application/json"),
    )


@router.get("/parquet", summary="Exportar dados cientificos em Parquet")
async def export_parquet(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_permission("export:scientific")),
):
    rows = await _scientific_rows(db, user, start_date, end_date)
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise HTTPException(
            status_code=503,
            detail="Parquet export requires pyarrow installed in the SENTINELA runtime.",
        ) from exc

    normalized_rows = json.loads(json.dumps(rows, ensure_ascii=False, default=_json_default))
    table = pa.Table.from_pylist(normalized_rows, schema=None)
    output = io.BytesIO()
    pq.write_table(table, output, compression="zstd")
    filename = f"sentinela_export_{date.today().isoformat()}.parquet"
    manifest = {"format": "parquet", "filename": filename, "rows": len(rows), "columns": SCIENTIFIC_COLUMNS}
    return Response(
        content=output.getvalue(),
        media_type="application/vnd.apache.parquet",
        headers=_export_headers(manifest, filename, "application/vnd.apache.parquet"),
    )


@router.get("/data-dictionary", summary="Dicionario de dados da exportacao cientifica")
async def export_data_dictionary(user: dict = Depends(require_permission("export:scientific"))):
    payload = {
        "format": "data_dictionary",
        "role": user["role"],
        "columns": DATA_DICTIONARY,
        "algorithm_metadata_required": ["algorithm_version", "algorithm_parameters"],
        "limits": ["not_clinical_diagnosis", "not_automatic_causal_nexus"],
    }
    filename = f"sentinela_data_dictionary_{date.today().isoformat()}.json"
    return Response(
        content=json.dumps(payload, ensure_ascii=False, indent=2),
        media_type="application/json",
        headers=_export_headers(payload, filename, "application/json"),
    )


@router.get("/psychometric-raw", summary="Exportar submissoes psicometricas brutas")
async def export_psychometric_raw(
    instrument: Optional[str] = Query(None, description="DASS21 | OLBI | SRQ20 | PANAS_SHORT"),
    start_date: Optional[date] = Query(None),
    end_date:   Optional[date] = Query(None),
    db:         AsyncSession   = Depends(get_db),
    user:       dict           = Depends(require_permission("export:scientific")),
):
    filters = ""
    params: dict = {}
    if instrument:
        filters += " AND instrument = :instrument"
        params["instrument"] = instrument
    if start_date:
        filters += " AND submitted_at >= :start_date"
        params["start_date"] = start_date
    if end_date:
        filters += " AND submitted_at <= :end_date"
        params["end_date"] = end_date
    scope_where, scope_params = scoped_id_filter(user, "id_hash")
    filters += scope_where
    params.update(scope_params)

    query = text(f"""
        SELECT id_hash, instrument, score, window_ref, submitted_at
        FROM psico_submissions
        WHERE 1=1 {filters}
        ORDER BY id_hash, submitted_at
    """)
    result = await db.execute(query, params)
    rows = result.fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id_hash", "instrument", "score", "window_ref", "submitted_at"])
    for row in rows:
        writer.writerow(list(row))

    filename = f"sentinela_psico_{date.today().isoformat()}.csv"
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
