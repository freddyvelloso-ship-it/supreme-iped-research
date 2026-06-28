"""
api.ingest
==========
Recebe dados do SUPREME V4 via push autenticado por API key.

Fixes aplicados:
  B2: COALESCE em todos os campos IEO â€” nunca sobrescreve dado existente com NULL.
  B3: Recebe red flags auditaveis calculadas pelo SUPREME.
  B10: Push PSI-only (ieo_score=None) nÃ£o cria linha Ã³rfÃ£ nem sobrescreve IEO.
"""
from __future__ import annotations

import json
import hmac
from datetime import date, datetime
from typing import Optional
import logging

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import text

from ..config import settings
from ..db import AsyncSession, get_db
from ..sanitization import fail_if_sensitive, validate_id_hash

log = logging.getLogger("sentinela.ingest")
router = APIRouter(prefix="/api/v1/ingest", tags=["Ingest"])


def _check_api_key(x_api_key: str = Header(...)):
    if not hmac.compare_digest(x_api_key.encode(), settings.supreme_api_key.encode()):
        raise HTTPException(status_code=403, detail="API key invalida")


class IEOPayload(BaseModel):
    id_hash:      str
    window_start: date
    t_minutes:    Optional[float] = None
    e_events:     Optional[int]   = None
    v_volume:     Optional[float] = None
    d_density:    Optional[float] = None
    dq_score:     Optional[float] = None
    ieo_score:    Optional[float] = None
    ieo_linear:   Optional[float] = None
    ieo_sat:      Optional[float] = None
    z_t:          Optional[float] = None
    z_e:          Optional[float] = None
    z_v:          Optional[float] = None
    z_d:          Optional[float] = None
    psi_score:         Optional[float] = None
    z_dass:            Optional[float] = None
    z_olbi:            Optional[float] = None
    z_srq:             Optional[float] = None
    z_panas_neg:       Optional[float] = None
    convergence_class: Optional[str]   = None
    algorithm_version: Optional[str]   = None
    algorithm_parameters: Optional[dict] = None

    model_config = ConfigDict(extra="forbid")

    @field_validator("id_hash")
    @classmethod
    def id_hash_is_safe(cls, value: str) -> str:
        return validate_id_hash(value)


class PsicoPayload(BaseModel):
    id_hash:      str
    instrument:   str
    score:        float = Field(ge=0.0, le=100.0)
    window_ref:   date
    submitted_at: date

    model_config = ConfigDict(extra="forbid")

    @field_validator("id_hash")
    @classmethod
    def id_hash_is_safe(cls, value: str) -> str:
        return validate_id_hash(value)


class RedFlagPayload(BaseModel):
    id_hash: str
    window_start: date
    flag_type: str
    severity: str
    detail: dict = {}
    algorithm_version: str
    algorithm_parameters: dict = {}

    model_config = ConfigDict(extra="forbid")

    @field_validator("id_hash")
    @classmethod
    def id_hash_is_safe(cls, value: str) -> str:
        return validate_id_hash(value)


class RedFlagsPayload(BaseModel):
    flags: list[RedFlagPayload]


class LongitudinalProfilePayload(BaseModel):
    id_hash: str
    profile_class: str
    profile_label: str
    profile_confidence: float
    profile_evidence: dict = {}
    baseline_version: Optional[int] = None
    algorithm_version: str
    algorithm_parameters: dict = {}
    classified_at: datetime

    model_config = ConfigDict(extra="forbid")

    @field_validator("id_hash")
    @classmethod
    def id_hash_is_safe(cls, value: str) -> str:
        return validate_id_hash(value)


# Fix B2: COALESCE em todos os campos IEO â€” jamais sobrescreve dado real com NULL.
# Antes os campos IEO eram sobrescritos sem COALESCE, apagando valores quando
# push_ieo() era chamado com ieo_score=None apÃ³s submissÃ£o psicomÃ©trica.
IEO_FULL_UPSERT_SQL = (
    "INSERT INTO ieo_windows"
    " (id_hash, window_start, t_minutes, e_events, v_volume, d_density,"
    " dq_score, ieo_score, ieo_linear, ieo_sat, z_t, z_e, z_v, z_d,"
    " psi_score, z_dass, z_olbi, z_srq, z_panas_neg, convergence_class,"
    " algorithm_version, algorithm_parameters)"
    " VALUES"
    " (:id_hash, :window_start, :t_minutes, :e_events, :v_volume, :d_density,"
    " :dq_score, :ieo_score, :ieo_linear, :ieo_sat, :z_t, :z_e, :z_v, :z_d,"
    " :psi_score, :z_dass, :z_olbi, :z_srq, :z_panas_neg, :convergence_class,"
    " :algorithm_version, cast(:algorithm_parameters as jsonb))"
    " ON CONFLICT (id_hash, window_start) DO UPDATE SET"
    " ieo_score    = COALESCE(EXCLUDED.ieo_score,    ieo_windows.ieo_score),"
    " ieo_linear   = COALESCE(EXCLUDED.ieo_linear,   ieo_windows.ieo_linear),"
    " ieo_sat      = COALESCE(EXCLUDED.ieo_sat,      ieo_windows.ieo_sat),"
    " t_minutes    = COALESCE(EXCLUDED.t_minutes,    ieo_windows.t_minutes),"
    " e_events     = COALESCE(EXCLUDED.e_events,     ieo_windows.e_events),"
    " v_volume     = COALESCE(EXCLUDED.v_volume,     ieo_windows.v_volume),"
    " d_density    = COALESCE(EXCLUDED.d_density,    ieo_windows.d_density),"
    " dq_score     = COALESCE(EXCLUDED.dq_score,     ieo_windows.dq_score),"
    " z_t          = COALESCE(EXCLUDED.z_t,          ieo_windows.z_t),"
    " z_e          = COALESCE(EXCLUDED.z_e,          ieo_windows.z_e),"
    " z_v          = COALESCE(EXCLUDED.z_v,          ieo_windows.z_v),"
    " z_d          = COALESCE(EXCLUDED.z_d,          ieo_windows.z_d),"
    " psi_score    = COALESCE(EXCLUDED.psi_score,    ieo_windows.psi_score),"
    " z_dass       = COALESCE(EXCLUDED.z_dass,       ieo_windows.z_dass),"
    " z_olbi       = COALESCE(EXCLUDED.z_olbi,       ieo_windows.z_olbi),"
    " z_srq        = COALESCE(EXCLUDED.z_srq,        ieo_windows.z_srq),"
    " z_panas_neg  = COALESCE(EXCLUDED.z_panas_neg,  ieo_windows.z_panas_neg),"
    " convergence_class = COALESCE(EXCLUDED.convergence_class, ieo_windows.convergence_class),"
    " algorithm_version = COALESCE(EXCLUDED.algorithm_version, ieo_windows.algorithm_version),"
    " algorithm_parameters = COALESCE(EXCLUDED.algorithm_parameters, ieo_windows.algorithm_parameters)"
)

# Fix B10 (revisado): quando sÃ³ PSI chegou (ieo_score=None), faz UPSERT apenas
# dos campos PSI. Se linha IEO jÃ¡ existe â†’ atualiza PSI via COALESCE sem tocar
# ieo_score. Se linha ainda nÃ£o existe â†’ cria com ieo_score=NULL; quando o IEO
# chegar pelo IEO_FULL_UPSERT_SQL os campos IEO sÃ£o preenchidos sem sobrescrever
# o PSI jÃ¡ salvo. Resolve o caso de PSI submetido antes do pipeline IEO rodar.
PSI_ONLY_UPDATE_SQL = (
    "INSERT INTO ieo_windows"
    " (id_hash, window_start, psi_score, z_dass, z_olbi, z_srq, z_panas_neg, convergence_class,"
    " algorithm_version, algorithm_parameters)"
    " VALUES"
    " (:id_hash, :window_start, :psi_score, :z_dass, :z_olbi, :z_srq, :z_panas_neg, :convergence_class,"
    " :algorithm_version, cast(:algorithm_parameters as jsonb))"
    " ON CONFLICT (id_hash, window_start) DO UPDATE SET"
    " psi_score        = COALESCE(EXCLUDED.psi_score,        ieo_windows.psi_score),"
    " z_dass           = COALESCE(EXCLUDED.z_dass,           ieo_windows.z_dass),"
    " z_olbi           = COALESCE(EXCLUDED.z_olbi,           ieo_windows.z_olbi),"
    " z_srq            = COALESCE(EXCLUDED.z_srq,            ieo_windows.z_srq),"
    " z_panas_neg      = COALESCE(EXCLUDED.z_panas_neg,      ieo_windows.z_panas_neg),"
    " convergence_class = COALESCE(EXCLUDED.convergence_class, ieo_windows.convergence_class),"
    " algorithm_version = COALESCE(EXCLUDED.algorithm_version, ieo_windows.algorithm_version),"
    " algorithm_parameters = COALESCE(EXCLUDED.algorithm_parameters, ieo_windows.algorithm_parameters)"
)

PSICO_INSERT_SQL = (
    "INSERT INTO psico_submissions (id_hash, instrument, score, window_ref, submitted_at)"
    " VALUES (:id_hash, :instrument, :score, :window_ref, :submitted_at)"
    " ON CONFLICT (id_hash, instrument, window_ref) DO UPDATE SET"
    " score        = EXCLUDED.score,"
    " submitted_at = EXCLUDED.submitted_at"
)

LONGITUDINAL_PROFILE_UPSERT_SQL = (
    "INSERT INTO longitudinal_profiles"
    " (id_hash, profile_class, profile_label, profile_confidence, profile_evidence,"
    " baseline_version, algorithm_version, algorithm_parameters, classified_at)"
    " VALUES"
    " (:id_hash, :profile_class, :profile_label, :profile_confidence, cast(:profile_evidence as jsonb),"
    " :baseline_version, :algorithm_version, cast(:algorithm_parameters as jsonb), :classified_at)"
    " ON CONFLICT (id_hash) DO UPDATE SET"
    " profile_class = EXCLUDED.profile_class,"
    " profile_label = EXCLUDED.profile_label,"
    " profile_confidence = EXCLUDED.profile_confidence,"
    " profile_evidence = EXCLUDED.profile_evidence,"
    " baseline_version = EXCLUDED.baseline_version,"
    " algorithm_version = EXCLUDED.algorithm_version,"
    " algorithm_parameters = EXCLUDED.algorithm_parameters,"
    " classified_at = EXCLUDED.classified_at,"
    " received_at = NOW()"
)



@router.post("/ieo")
async def receive_ieo(
    payload: IEOPayload,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(_check_api_key),
):
    fail_if_sensitive(payload.model_dump())
    p = payload.model_dump()
    p["algorithm_parameters"] = json.dumps(p.get("algorithm_parameters") or {})

    if payload.ieo_score is None:
        # Fix B10: PSI-only â€” sÃ³ atualiza linha existente, nÃ£o cria Ã³rfÃ£
        await db.execute(text(PSI_ONLY_UPDATE_SQL), p)
        log.info("PSI-only update | id=%.8s window=%s psi=%s",
                 payload.id_hash, payload.window_start,
                 f"{payload.psi_score:.3f}" if payload.psi_score else "None")
    else:
        # Fix B2: upsert completo com COALESCE em todos os campos
        await db.execute(text(IEO_FULL_UPSERT_SQL), p)
        log.info("IEO recebido | id=%.8s window=%s ieo=%.3f",
                 payload.id_hash, payload.window_start, payload.ieo_score)

    await db.commit()

    # Red flags are computed by SUPREME and received through /red-flags.

    return {"status": "ok", "kind": "ieo", "id_hash": payload.id_hash, "window_start": payload.window_start.isoformat()}


@router.post("/red-flags")
async def receive_red_flags(
    payload: RedFlagsPayload,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(_check_api_key),
):
    """Recebe red flags calculadas pelo SUPREME.

    SENTINELA persiste e visualiza. Nao calcula regra critica.
    """
    fail_if_sensitive(payload.model_dump())
    for flag in payload.flags:
        await db.execute(text("""
            INSERT INTO red_flags
                (id_hash, window_start, flag_type, severity, detail,
                 algorithm_version, algorithm_parameters)
            VALUES
                (:id_hash, :window_start, :flag_type, :severity, cast(:detail as jsonb),
                 :algorithm_version, cast(:algorithm_parameters as jsonb))
            ON CONFLICT (id_hash, window_start, flag_type) DO UPDATE SET
                severity = EXCLUDED.severity,
                detail = EXCLUDED.detail,
                algorithm_version = EXCLUDED.algorithm_version,
                algorithm_parameters = EXCLUDED.algorithm_parameters
        """), {
            **flag.model_dump(exclude={"detail", "algorithm_parameters"}),
            "detail": json.dumps(flag.detail),
            "algorithm_parameters": json.dumps(flag.algorithm_parameters),
        })
    await db.commit()
    return {"status": "ok", "kind": "red_flags", "received": len(payload.flags)}


@router.post("/longitudinal-profile")
async def receive_longitudinal_profile(
    payload: LongitudinalProfilePayload,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(_check_api_key),
):
    """Recebe perfil longitudinal calculado pelo SUPREME.

    SENTINELA persiste e visualiza. Nao recalcula perfil nem thresholds.
    """
    fail_if_sensitive(payload.model_dump())
    if payload.profile_class not in {"medio", "resiliente", "vulneravel", "junior", "senior"}:
        raise HTTPException(status_code=422, detail="profile_class invalido")
    p = payload.model_dump()
    p["profile_evidence"] = json.dumps(p.get("profile_evidence") or {})
    p["algorithm_parameters"] = json.dumps(p.get("algorithm_parameters") or {})
    await db.execute(text(LONGITUDINAL_PROFILE_UPSERT_SQL), p)
    await db.commit()
    return {"status": "ok", "kind": "longitudinal_profile", "id_hash": payload.id_hash}


@router.post("/psychometric")
async def receive_psychometric(
    payload: PsicoPayload,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(_check_api_key),
):
    """Recebe uma submissao psicometrica agregada enviada pelo SUPREME.

    O contrato aceita apenas escore agregado por instrumento e janela. Respostas
    item-a-item, nomes, paths e identificadores crus sao rejeitados por sanitizacao.
    """
    fail_if_sensitive(payload.model_dump())
    await db.execute(text(PSICO_INSERT_SQL), payload.model_dump())
    await db.commit()
    log.info(
        "Psicometrico recebido | id=%.8s instrument=%s score=%.3f window=%s",
        payload.id_hash,
        payload.instrument,
        payload.score,
        payload.window_ref,
    )
    return {
        "status": "ok",
        "kind": "psychometric",
        "id_hash": payload.id_hash,
        "instrument": payload.instrument,
        "window_ref": payload.window_ref.isoformat(),
    }
