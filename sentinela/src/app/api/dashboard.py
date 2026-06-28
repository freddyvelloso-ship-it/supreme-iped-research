"""
api.dashboard
=============
Endpoints do dashboard para pesquisadores.
Master: dados individuais + agregados.
PIBIC:  apenas dados agregados.

Fixes aplicados:
  B4: /overview retorna total_participants, avg_ieo_last_window, avg_psi_last_window,
      active_flags_count, convergence_distribution (campos corretos para o frontend).
  B5: /participants retorna window_count, last_ieo, last_psi, last_convergence_class,
      active_flags (array), prev_ieo (para indicador de tendência).
  B6: /participant/{id}/trajectory retorna chave "ieo_windows" (não "ieo") e inclui
      psi_score e convergence_class em cada janela.
  B8: /ieo-series retorna avg_z_t, avg_z_e, avg_z_v, avg_z_d por janela.
"""
from __future__ import annotations

from datetime import date
from typing import Optional, Literal
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text

from ..auth import assert_participant_scope, require_permission, scoped_id_filter
from ..db import AsyncSession, get_db

log = logging.getLogger("sentinela.dashboard")
router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

# ── Ciclo de vida ──────────────────────────────────────────────────────────────

class LifecycleRequest(BaseModel):
    action: Literal["deactivate", "reactivate", "delete"]


@router.post("/participants/{id_hash}/lifecycle")
async def participant_lifecycle(
    id_hash: str,
    body: LifecycleRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("dashboard:lifecycle")),
):
    """
    Gerencia o ciclo de vida de um participante.
    - deactivate → status = 'inactive'   (descontinua, mantém dados)
    - reactivate → status = 'active'     (reativa participante)
    - delete     → status = 'deleted'    (exclusão lógica, dados preservados)
    Requer role master.
    """
    status_map = {
        "deactivate": "inactive",
        "reactivate": "active",
        "delete":     "deleted",
    }
    new_status = status_map[body.action]

    assert_participant_scope(user, id_hash)
    await db.execute(text("""
        INSERT INTO participant_lifecycle (id_hash, status, updated_at, updated_by)
        VALUES (:id_hash, :status, NOW(), :by)
        ON CONFLICT (id_hash) DO UPDATE SET
            status     = EXCLUDED.status,
            updated_at = NOW(),
            updated_by = EXCLUDED.updated_by
    """), {"id_hash": id_hash, "status": new_status, "by": user.get("email", "system")})
    await db.commit()

    log.info("lifecycle %s → %s by %s", id_hash[:12], new_status, getattr(user, "email", "?"))
    return {"id_hash": id_hash, "status": new_status}


@router.get("/overview")
async def overview(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("dashboard:aggregate")),
):
    """
    Visão geral: métricas agregadas da unidade.
    Fix B4: campos alinhados com o que o frontend espera.
    """
    # Última janela com dados
    scope_where, scope_params = scoped_id_filter(user)
    last_r = await db.execute(text(
        f"SELECT MAX(window_start) FROM ieo_windows WHERE ieo_score IS NOT NULL{scope_where}"
    ), scope_params)
    last_window = last_r.scalar()

    # Estatísticas da última janela
    last_stats: dict = {}
    if last_window:
        r = await db.execute(text(f"""
            SELECT
                ROUND(AVG(ieo_score)::numeric, 3) AS avg_ieo_last_window,
                ROUND(AVG(psi_score)::numeric, 3) AS avg_psi_last_window
            FROM ieo_windows
            WHERE window_start = :lw AND ieo_score IS NOT NULL{scope_where}
        """), {"lw": last_window, **scope_params})
        last_stats = dict(r.mappings().one_or_none() or {})

    # Total de participantes únicos em todo o estudo
    total_r = await db.execute(text(
        f"SELECT COUNT(DISTINCT id_hash) FROM ieo_windows WHERE 1=1{scope_where}"
    ), scope_params)
    total_participants = total_r.scalar() or 0

    # Contagem de red flags na última janela
    active_flags_count = 0
    if last_window:
        flags_r = await db.execute(text(
            f"SELECT COUNT(*) FROM red_flags WHERE window_start = :lw{scope_where}"
        ), {"lw": last_window, **scope_params})
        active_flags_count = flags_r.scalar() or 0

    # Distribuição de convergência na última janela (para gráfico doughnut)
    convergence_distribution: dict = {}
    if last_window:
        conv_r = await db.execute(text(f"""
            SELECT convergence_class, COUNT(*) AS n
            FROM ieo_windows
            WHERE window_start = :lw AND convergence_class IS NOT NULL{scope_where}
            GROUP BY convergence_class
        """), {"lw": last_window, **scope_params})
        convergence_distribution = {
            row["convergence_class"]: row["n"]
            for row in conv_r.mappings()
        }

    profile_scope_where, profile_scope_params = scoped_id_filter(user, "lp.id_hash")
    profile_r = await db.execute(text(f"""
        SELECT profile_class, COUNT(*) AS n
        FROM longitudinal_profiles lp
        WHERE 1=1{profile_scope_where}
        GROUP BY profile_class
        ORDER BY profile_class
    """), profile_scope_params)
    profile_distribution = {row["profile_class"]: row["n"] for row in profile_r.mappings()}

    return {
        "total_participants":        total_participants,
        "avg_ieo_last_window":       last_stats.get("avg_ieo_last_window"),
        "avg_psi_last_window":       last_stats.get("avg_psi_last_window"),
        "active_flags_count":        active_flags_count,
        "convergence_distribution":  convergence_distribution,
        "profile_distribution":      profile_distribution,
        "last_window":               str(last_window) if last_window else None,
    }


@router.get("/participants")
async def list_participants(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("dashboard:participant")),
):
    """
    Lista participantes com último IEO, PSI, convergência e flags.
    Fix B5: campos alinhados com o frontend (window_count, last_ieo, etc.)
    """
    scope_where, scope_params = scoped_id_filter(user, "ld.id_hash")
    r = await db.execute(text(f"""
        WITH last_win AS (
            SELECT id_hash, MAX(window_start) AS last_window
            FROM ieo_windows
            GROUP BY id_hash
        ),
        prev_win AS (
            SELECT iw.id_hash, MAX(iw.window_start) AS prev_window
            FROM ieo_windows iw
            JOIN last_win lw ON iw.id_hash = lw.id_hash
            WHERE iw.window_start < lw.last_window
            GROUP BY iw.id_hash
        ),
        last_data AS (
            SELECT
                iw.id_hash,
                iw.ieo_score            AS last_ieo,
                iw.psi_score            AS last_psi,
                iw.convergence_class    AS last_convergence_class,
                iw.algorithm_version    AS algorithm_version,
                iw.algorithm_parameters AS algorithm_parameters
            FROM ieo_windows iw
            JOIN last_win lw
              ON iw.id_hash = lw.id_hash
             AND iw.window_start = lw.last_window
        ),
        prev_data AS (
            SELECT iw.id_hash, iw.ieo_score AS prev_ieo
            FROM ieo_windows iw
            JOIN prev_win pw
              ON iw.id_hash = pw.id_hash
             AND iw.window_start = pw.prev_window
        ),
        counts AS (
            SELECT id_hash, COUNT(*) AS window_count
            FROM ieo_windows
            GROUP BY id_hash
        ),
        flags AS (
            SELECT rf.id_hash,
                   ARRAY_AGG(DISTINCT rf.flag_type) AS active_flags
            FROM red_flags rf
            JOIN last_win lw
              ON rf.id_hash = lw.id_hash
             AND rf.window_start = lw.last_window
            GROUP BY rf.id_hash
        )
        SELECT
            ld.id_hash,
            c.window_count,
            ld.last_ieo,
            ld.last_psi,
            ld.last_convergence_class,
            pd.prev_ieo,
            COALESCE(f.active_flags, ARRAY[]::text[]) AS active_flags,
            COALESCE(lc.status, 'active') AS status,
            lp.profile_class,
            lp.profile_label,
            lp.profile_confidence,
            lp.classified_at AS profile_classified_at,
            lp.algorithm_version AS profile_algorithm_version,
            lp.algorithm_parameters AS profile_algorithm_parameters
        FROM last_data ld
        JOIN counts c ON c.id_hash = ld.id_hash
        LEFT JOIN prev_data pd ON pd.id_hash = ld.id_hash
        LEFT JOIN flags f ON f.id_hash = ld.id_hash
        LEFT JOIN participant_lifecycle lc ON lc.id_hash = ld.id_hash
        LEFT JOIN longitudinal_profiles lp ON lp.id_hash = ld.id_hash
        WHERE COALESCE(lc.status, 'active') != 'deleted'{scope_where}
        ORDER BY ld.last_ieo DESC NULLS LAST
    """), scope_params)
    rows = []
    for row in r.mappings():
        d = dict(row)
        d["active_flags"] = list(d["active_flags"]) if d["active_flags"] else []
        d["status"] = d.get("status") or "active"
        rows.append(d)
    return rows


@router.get("/participant/{id_hash}/trajectory")
async def participant_trajectory(
    id_hash: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("dashboard:participant")),
):
    """
    Trajetória longitudinal de um participante.
    Fix B6: retorna chave "ieo_windows" (era "ieo") e inclui psi_score,
    convergence_class em cada janela.
    """
    assert_participant_scope(user, id_hash)
    ieo = await db.execute(text("""
        SELECT window_start, ieo_score, psi_score,
               z_t, z_e, z_v, z_d, dq_score, convergence_class,
               algorithm_version, algorithm_parameters
        FROM ieo_windows
        WHERE id_hash = :h
        ORDER BY window_start
    """), {"h": id_hash})

    psico = await db.execute(text("""
        SELECT instrument, score, submitted_at
        FROM psico_submissions
        WHERE id_hash = :h
        ORDER BY submitted_at
    """), {"h": id_hash})

    flags = await db.execute(text("""
        SELECT flag_type, severity, window_start, detail,
               algorithm_version, algorithm_parameters
        FROM red_flags
        WHERE id_hash = :h
        ORDER BY window_start
    """), {"h": id_hash})

    profile = await db.execute(text("""
        SELECT id_hash, profile_class, profile_label, profile_confidence,
               profile_evidence, baseline_version, algorithm_version,
               algorithm_parameters, classified_at
        FROM longitudinal_profiles
        WHERE id_hash = :h
        LIMIT 1
    """), {"h": id_hash})

    profile_row = profile.mappings().one_or_none()
    return {
        "id_hash":       id_hash,
        "ieo_windows":   [dict(r) for r in ieo.mappings()],   # Fix B6: era "ieo"
        "psychometrics": [dict(r) for r in psico.mappings()],
        "red_flags":     [dict(r) for r in flags.mappings()],
        "longitudinal_profile": dict(profile_row) if profile_row else None,
    }


@router.get("/red-flags")
async def list_red_flags(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("dashboard:flags")),
):
    """Todas as red flags. Apenas master."""
    scope_where, scope_params = scoped_id_filter(user)
    r = await db.execute(text(f"""
        SELECT id_hash, flag_type, severity, window_start, created_at, detail,
               algorithm_version, algorithm_parameters
        FROM red_flags
        WHERE 1=1{scope_where}
        ORDER BY created_at DESC
        LIMIT 200
    """), scope_params)
    return [dict(row) for row in r.mappings()]


@router.get("/ieo-series")
async def ieo_series(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("dashboard:aggregate")),
):
    """
    Série temporal de IEO médio da unidade por janela.
    Fix B8: inclui avg_z_t, avg_z_e, avg_z_v, avg_z_d para aba IEO do dashboard.
    """
    scope_where, scope_params = scoped_id_filter(user)
    r = await db.execute(text(f"""
        SELECT
            window_start,
            ROUND(AVG(ieo_score)::numeric, 3) AS avg_ieo,
            ROUND(AVG(psi_score)::numeric,  3) AS avg_psi,
            ROUND(AVG(z_t)::numeric,         3) AS avg_z_t,
            ROUND(AVG(z_e)::numeric,         3) AS avg_z_e,
            ROUND(AVG(z_v)::numeric,         3) AS avg_z_v,
            ROUND(AVG(z_d)::numeric,         3) AS avg_z_d,
            COUNT(DISTINCT id_hash)             AS n_participantes
            , ARRAY_AGG(DISTINCT algorithm_version)
                FILTER (WHERE algorithm_version IS NOT NULL) AS algorithm_versions
        FROM ieo_windows
        WHERE 1=1{scope_where}
        GROUP BY window_start
        ORDER BY window_start
    """), scope_params)
    return [dict(row) for row in r.mappings()]


@router.get("/psychometric-series")
async def psychometric_series(
    instrument: str = Query(None),
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("dashboard:aggregate")),
):
    """Série temporal de score médio por instrumento."""
    scope_where, scope_params = scoped_id_filter(user)
    if instrument:
        r = await db.execute(text(f"""
            SELECT instrument, window_ref,
                   ROUND(AVG(score)::numeric, 2) AS avg_score,
                   COUNT(DISTINCT id_hash)       AS n
            FROM psico_submissions
            WHERE instrument = :inst{scope_where}
            GROUP BY instrument, window_ref
            ORDER BY window_ref
        """), {"inst": instrument, **scope_params})
    else:
        r = await db.execute(text(f"""
            SELECT instrument, window_ref,
                   ROUND(AVG(score)::numeric, 2) AS avg_score,
                   COUNT(DISTINCT id_hash)       AS n
            FROM psico_submissions
            WHERE 1=1{scope_where}
            GROUP BY instrument, window_ref
            ORDER BY instrument, window_ref
        """), scope_params)
    return [dict(row) for row in r.mappings()]
