"""
app.api.psychometric
====================
Rotas do modulo psicomtrico.
"""

from __future__ import annotations

import base64
import csv
import hashlib
import hmac
import io
import json
import logging
import math
import secrets
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, Response
from pydantic import BaseModel, field_validator

from ..config import get_settings
from ..international import form_messages, normalize_locale
from ..security import require_api_token
from ..db import (
    AsyncSession,
    ensure_schedule_exists,
    fetch_due_instruments,
    fetch_ieo_window,
    fetch_latest_ieo_score,
    fetch_psychometric_history,
    fetch_psi_window,
    fetch_recent_psi_windows,
    fetch_schedule,
    fetch_scores_by_instrument,
    get_db,
    insert_psychometric_submission,
    upsert_psi,
    upsert_analytic_red_flags,
    upsert_schedule,
)
from ...engine.supreme.psi import compute_psi
from ...engine.supreme.algorithm import CURRENT_ALGORITHM_VERSION, algorithm_parameters
from ...engine.supreme.models import IEORecord
from ...engine.supreme.red_flags import PSIWindow, evaluate_red_flags
from ...engine.supreme.sentinela_push import push_ieo, push_psychometric, push_red_flags

log = logging.getLogger("supreme.psychometric")

router       = APIRouter(dependencies=[Depends(require_api_token)], tags=["Psychometric"])
forms_router = APIRouter(tags=["Forms"])

FORMS_DIR = Path(__file__).parent.parent / "forms"

_SCHEDULE: dict[str, timedelta] = {
    "PANAS_SHORT": timedelta(days=2),
    "DASS21":      timedelta(days=14),
    "OLBI":        timedelta(days=30),
    "SRQ20":       timedelta(days=30),
}

_FORM_COOKIE = "supreme_form_token"
_FORM_TTL_SECONDS = 15 * 60
_FORM_PATH_BY_INSTRUMENT = {
    "PANAS_SHORT": "panas",
    "DASS21": "dass21",
    "OLBI": "olbi",
    "SRQ20": "srq20",
}
_INSTRUMENT_BY_FORM_PATH = {path: instrument for instrument, path in _FORM_PATH_BY_INSTRUMENT.items()}
_FORM_LAUNCH_CODES: dict[str, tuple[str, int]] = {}
_FORM_WORLD_ASSET_VERSION = "world-ui-20260626-i18n2"


def _form_cookie_name(instrument: str) -> str:
    return f"{_FORM_COOKIE}_{instrument.lower()}"


def _request_form_ticket(request: Request, instrument: Optional[str] = None) -> Optional[str]:
    if instrument:
        ticket = request.cookies.get(_form_cookie_name(instrument))
        if ticket:
            return ticket
    return request.cookies.get(_FORM_COOKIE)


def _csp_nonce(request: Request) -> str:
    return str(getattr(request.state, "csp_nonce", ""))


def _apply_form_nonce(html: str, nonce: str) -> str:
    if not nonce:
        return html
    return (
        html
        .replace("<style>", f'<style nonce="{nonce}">')
        .replace("<script>", f'<script nonce="{nonce}">')
    )


def _inject_form_i18n(html: str, locale: str, instrument: str) -> str:
    """Inject locale metadata without editing the large static form files."""
    normalized_locale = normalize_locale(locale)
    messages = form_messages(normalized_locale, instrument)
    payload = json.dumps(messages, ensure_ascii=False, separators=(",", ":"))
    script = (
        f'const FORM_LOCALE={json.dumps(normalized_locale)};'
        f"const FORM_I18N={payload};"
        "Object.assign(FORM_CONFIG,FORM_I18N);"
        "document.documentElement.lang=FORM_LOCALE;"
        "document.title='SUPREME V4 - '+(FORM_CONFIG.shortTitle||FORM_CONFIG.title||FORM_CONFIG.instrument);"
        "const _subtitle=document.querySelector('.subtitle');if(_subtitle&&FORM_CONFIG.subtitle)_subtitle.textContent=FORM_CONFIG.subtitle;"
        "const _hint=document.querySelector('.q-hint');if(_hint&&FORM_CONFIG.scaleHint)_hint.textContent=FORM_CONFIG.scaleHint;"
        "const _notice=document.querySelector('.notice p:last-child');if(_notice&&FORM_CONFIG.notice)_notice.textContent=FORM_CONFIG.notice;"
        "const _fine=document.querySelector('.fineprint');if(_fine&&FORM_CONFIG.fineprint)_fine.textContent=FORM_CONFIG.fineprint;"
    )
    css = f"/forms/assets/form-world.css?v={_FORM_WORLD_ASSET_VERSION}"
    js = f"/forms/assets/form-world.js?v={_FORM_WORLD_ASSET_VERSION}"
    html = html.replace("</head>", f'<link rel="stylesheet" href="{css}">\n</head>')
    html = html.replace("</body>", f'<script src="{js}"></script>\n</body>')
    return html.replace("const backend=", script + "const backend=")


def _b64_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii"))


def _sign_form_payload(encoded_payload: str) -> str:
    secret = get_settings().api_secret_key.encode("utf-8")
    digest = hmac.new(secret, encoded_payload.encode("ascii"), hashlib.sha256).digest()
    return _b64_encode(digest)


def _create_form_token(id_hash: str, instrument: str, ttl_seconds: int = _FORM_TTL_SECONDS) -> tuple[str, int]:
    expires_at = int(time.time()) + ttl_seconds
    payload = {
        "typ": "supreme-psychometric-form",
        "id_hash": id_hash,
        "instrument": instrument,
        "exp": expires_at,
    }
    encoded_payload = _b64_encode(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    signature = _sign_form_payload(encoded_payload)
    return f"{encoded_payload}.{signature}", expires_at


def _verify_form_token(token: str) -> dict:
    try:
        encoded_payload, signature = token.split(".", 1)
    except ValueError as exc:
        raise HTTPException(status_code=403, detail="ticket de formulario invalido") from exc

    expected_signature = _sign_form_payload(encoded_payload)
    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=403, detail="ticket de formulario invalido")

    try:
        payload = json.loads(_b64_decode(encoded_payload).decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise HTTPException(status_code=403, detail="ticket de formulario invalido") from exc

    if payload.get("typ") != "supreme-psychometric-form":
        raise HTTPException(status_code=403, detail="ticket de formulario invalido")
    if int(payload.get("exp", 0)) < int(time.time()):
        raise HTTPException(status_code=401, detail="sessao do formulario expirada")
    if payload.get("instrument") not in _FORM_PATH_BY_INSTRUMENT:
        raise HTTPException(status_code=403, detail="ticket de formulario invalido")
    if not payload.get("id_hash"):
        raise HTTPException(status_code=403, detail="ticket de formulario invalido")
    return payload


def _rolling_stats(values: list[float]) -> tuple[Optional[float], Optional[float]]:
    n = len(values)
    if n < 4:
        return None, None
    mean = sum(values) / n
    variance = sum((x - mean) ** 2 for x in values) / (n - 1)
    return mean, math.sqrt(variance) if variance > 1e-9 else None


def _next_due(instrument: str, study_week: int = 0) -> datetime:
    delta = _SCHEDULE.get(instrument, timedelta(days=30))
    if instrument == "DASS21" and study_week >= 12:
        delta = timedelta(days=30)
    return datetime.now(tz=timezone.utc) + delta


async def _compute_and_save_psi(db: AsyncSession, id_hash: str, window_ref: date) -> None:
    dass_hist  = await fetch_scores_by_instrument(db, id_hash, "DASS21")
    olbi_hist  = await fetch_scores_by_instrument(db, id_hash, "OLBI")
    srq_hist   = await fetch_scores_by_instrument(db, id_hash, "SRQ20")
    panas_hist = await fetch_scores_by_instrument(db, id_hash, "PANAS_SHORT")

    dass_raw  = dass_hist[-1]  if dass_hist  else None
    olbi_raw  = olbi_hist[-1]  if olbi_hist  else None
    srq_raw   = srq_hist[-1]   if srq_hist   else None
    panas_raw = panas_hist[-1] if panas_hist  else None

    mean_dass,  sd_dass  = _rolling_stats(dass_hist[:-1]  if len(dass_hist)  > 1 else [])
    mean_olbi,  sd_olbi  = _rolling_stats(olbi_hist[:-1]  if len(olbi_hist)  > 1 else [])
    mean_srq,   sd_srq   = _rolling_stats(srq_hist[:-1]   if len(srq_hist)   > 1 else [])
    mean_panas, sd_panas = _rolling_stats(panas_hist[:-1] if len(panas_hist) > 1 else [])

    oei_score = await fetch_latest_ieo_score(db, id_hash)

    result = compute_psi(
        dass_raw=dass_raw, olbi_raw=olbi_raw, srq_raw=srq_raw, panas_neg_raw=panas_raw,
        mean_dass=mean_dass, sd_dass=sd_dass, mean_olbi=mean_olbi, sd_olbi=sd_olbi,
        mean_srq=mean_srq, sd_srq=sd_srq, mean_panas=mean_panas, sd_panas=sd_panas,
        oei_score=oei_score,
    )

    await upsert_psi(db, {
        "id_hash":           id_hash,
        "window_start":      window_ref,
        "psi_score":         result.psi_score,
        "z_dass":            result.z_dass,
        "z_olbi":            result.z_olbi,
        "z_srq":             result.z_srq,
        "z_panas_neg":       result.z_panas_neg,
        "dass_raw":          result.dass_raw,
        "olbi_raw":          result.olbi_raw,
        "srq_raw":           result.srq_raw,
        "panas_neg_raw":     result.panas_neg_raw,
        "convergence_class": result.convergence_class,
        "algorithm_version": result.algorithm_version,
        "algorithm_parameters": json.dumps(algorithm_parameters()),
    })

    log.info("PSI | id_hash=%.8s window=%s psi=%.3f class=%s",
             id_hash, window_ref, result.psi_score, result.convergence_class)


def _psi_window_from_row(row: Optional[dict]) -> Optional[PSIWindow]:
    if not row:
        return None
    return PSIWindow(
        id_hash=row["id_hash"],
        window_start=row["window_start"],
        psi_score=row.get("psi_score"),
        z_dass=row.get("z_dass"),
        z_olbi=row.get("z_olbi"),
        z_srq=row.get("z_srq"),
        z_panas_neg=row.get("z_panas_neg"),
        convergence_class=row.get("convergence_class"),
    )


async def _recompute_flags_if_ieo_exists(db: AsyncSession, id_hash: str, window_ref: date) -> None:
    ieo_row = await fetch_ieo_window(db, id_hash, window_ref)
    if not ieo_row:
        return

    ieo = IEORecord(
        id_hash=ieo_row["id_hash"],
        window_start=ieo_row["window_start"],
        ieo_score=ieo_row["ieo_score"],
        ieo_linear=ieo_row["ieo_linear"],
        ieo_sat=ieo_row["ieo_sat"],
        z_t=ieo_row["z_t"],
        z_e=ieo_row["z_e"],
        z_v=ieo_row["z_v"],
        z_d=ieo_row["z_d"],
    )
    psi_current = _psi_window_from_row(await fetch_psi_window(db, id_hash, window_ref))
    psi_history = [
        row for row in (
            _psi_window_from_row(r) for r in await fetch_recent_psi_windows(db, id_hash, limit=8)
        )
        if row is not None
    ]
    params = algorithm_parameters()
    flags = evaluate_red_flags(ieo, psi_current, psi_history)
    await upsert_analytic_red_flags(db, flags, params)
    if flags:
        await push_red_flags(flags, params)


class SubmitRequest(BaseModel):
    id_hash:    str
    instrument: str
    responses:  list[float]

    @field_validator("instrument")
    @classmethod
    def validate_instrument(cls, v: str) -> str:
        valid = {"PANAS_SHORT", "DASS21", "OLBI", "SRQ20"}
        if v not in valid:
            raise ValueError(f"instrument deve ser um de {valid}")
        return v


class FormLinkRequest(BaseModel):
    id_hash:    str
    instrument: str

    @field_validator("instrument")
    @classmethod
    def validate_instrument(cls, v: str) -> str:
        valid = set(_FORM_PATH_BY_INSTRUMENT)
        if v not in valid:
            raise ValueError(f"instrument deve ser um de {valid}")
        return v


class FormSessionStartRequest(BaseModel):
    access_code: str


def _authorize_psychometric_submit(request: Request, body: SubmitRequest) -> None:
    settings = get_settings()
    auth_header = request.headers.get("authorization", "")

    if auth_header.lower().startswith("bearer "):
        candidate = auth_header.split(" ", 1)[1].strip()
        if hmac.compare_digest(candidate, settings.api_ingest_token):
            return
        raise HTTPException(status_code=403, detail="token de ingestao invalido")

    ticket = _request_form_ticket(request, body.instrument)
    if not ticket:
        raise HTTPException(status_code=401, detail="sessao do formulario nao encontrada")

    payload = _verify_form_token(ticket)
    if not hmac.compare_digest(str(payload["id_hash"]), body.id_hash):
        raise HTTPException(status_code=403, detail="ticket nao pertence a este usuario")
    if payload["instrument"] != body.instrument:
        raise HTTPException(status_code=403, detail="ticket nao pertence a este instrumento")


@router.get("/schedule/{id_hash}")
async def get_schedule(id_hash: str, db: AsyncSession = Depends(get_db)):
    await ensure_schedule_exists(db, id_hash)
    due      = await fetch_due_instruments(db, id_hash)
    schedule = await fetch_schedule(db, id_hash)
    return {"id_hash": id_hash, "due_now": due, "schedule": schedule}


@router.post("/forms/link")
async def create_form_link(body: FormLinkRequest):
    if not body.id_hash:
        raise HTTPException(status_code=400, detail="id_hash e obrigatorio")

    access_code, expires_at = _create_form_token(body.id_hash, body.instrument)
    form_path = _FORM_PATH_BY_INSTRUMENT[body.instrument]
    launch_id = secrets.token_urlsafe(24)
    _FORM_LAUNCH_CODES[launch_id] = (access_code, expires_at)
    return {
        "url": f"/forms/{form_path}/start",
        "launch_url": f"/forms/{form_path}/launch/{launch_id}",
        "access_code": access_code,
        "expires_at": datetime.fromtimestamp(expires_at, tz=timezone.utc).isoformat(),
        "ttl_seconds": _FORM_TTL_SECONDS,
    }


@forms_router.get("/forms/{instrument}/launch/{launch_id}", include_in_schema=False)
async def launch_form_session(instrument: str, launch_id: str):
    form_path = instrument.lower()
    expected_instrument = _INSTRUMENT_BY_FORM_PATH.get(form_path)
    if expected_instrument is None:
        raise HTTPException(status_code=404, detail="Formulario nao encontrado")

    item = _FORM_LAUNCH_CODES.pop(launch_id, None)
    if item is None:
        raise HTTPException(status_code=404, detail="Link expirado ou ja utilizado")

    access_code, expires_at = item
    now = int(time.time())
    if expires_at < now:
        raise HTTPException(status_code=410, detail="Link expirado")

    payload = _verify_form_token(access_code)
    if payload["instrument"] != expected_instrument:
        raise HTTPException(status_code=403, detail="ticket nao pertence a este formulario")

    response = RedirectResponse(url=f"/forms/{form_path}", status_code=303)
    response.set_cookie(
        key=_form_cookie_name(expected_instrument),
        value=access_code,
        max_age=max(1, expires_at - now),
        httponly=True,
        secure=get_settings().environment.lower() not in {"local", "test", "demo"},
        samesite="strict",
        path="/",
    )
    response.set_cookie(
        key=_FORM_COOKIE,
        value=access_code,
        max_age=max(1, expires_at - now),
        httponly=True,
        secure=get_settings().environment.lower() not in {"local", "test", "demo"},
        samesite="strict",
        path="/",
    )
    return response


@forms_router.get("/forms/{instrument}/start", include_in_schema=False)
async def start_form_page(request: Request, instrument: str):
    form_path = instrument.lower()
    if form_path not in _INSTRUMENT_BY_FORM_PATH:
        raise HTTPException(status_code=404, detail="Formulario nao encontrado")
    nonce = _csp_nonce(request)
    return HTMLResponse(f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>SUPREME V4 - Acesso ao formulario</title>
  <style nonce="{nonce}">
    body{{font-family:Arial,sans-serif;background:#0b1020;color:#e8eefc;display:grid;place-items:center;min-height:100vh;margin:0}}
    main{{width:min(420px,calc(100vw - 32px));border:1px solid #26324d;background:#121a30;padding:24px;border-radius:8px}}
    label,input,button{{display:block;width:100%;box-sizing:border-box}}
    label{{font-size:13px;color:#a8b3cf;margin-bottom:8px}}
    input{{padding:12px;border-radius:6px;border:1px solid #35435f;background:#080d19;color:#fff}}
    button{{margin-top:14px;padding:12px;border:0;border-radius:6px;background:#3b82f6;color:white;font-weight:700;cursor:pointer}}
    #msg{{min-height:20px;margin-top:12px;color:#fca5a5;font-size:13px}}
  </style>
</head>
<body>
  <main>
    <h1>Formulario SUPREME V4</h1>
    <label for="code">Codigo de acesso</label>
    <input id="code" autocomplete="one-time-code" autofocus />
    <button id="go">Iniciar</button>
    <div id="msg"></div>
  </main>
  <script nonce="{nonce}">
    document.getElementById('go').addEventListener('click', async () => {{
      const msg = document.getElementById('msg');
      msg.textContent = '';
      const access_code = document.getElementById('code').value.trim();
      const res = await fetch('/v1/forms/session/start', {{
        method: 'POST',
        credentials: 'same-origin',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{access_code}})
      }});
      if (!res.ok) {{
        msg.textContent = 'Codigo invalido ou expirado.';
        return;
      }}
      window.location.href = '/forms/{form_path}';
    }});
  </script>
</body>
</html>""")


@forms_router.post("/v1/forms/session/start")
async def start_form_session(body: FormSessionStartRequest):
    ticket = body.access_code.strip()
    payload = _verify_form_token(ticket)
    form_path = _FORM_PATH_BY_INSTRUMENT[payload["instrument"]]
    expected_instrument = _INSTRUMENT_BY_FORM_PATH.get(form_path)
    if expected_instrument is None or payload["instrument"] != expected_instrument:
        raise HTTPException(status_code=403, detail="ticket nao pertence a este formulario")

    response = Response(content='{"status":"ok"}', media_type="application/json")
    response.set_cookie(
        key=_form_cookie_name(payload["instrument"]),
        value=ticket,
        max_age=_FORM_TTL_SECONDS,
        httponly=True,
        secure=get_settings().environment.lower() not in {"local", "test", "demo"},
        samesite="strict",
        path="/",
    )
    response.set_cookie(
        key=_FORM_COOKIE,
        value=ticket,
        max_age=_FORM_TTL_SECONDS,
        httponly=True,
        secure=get_settings().environment.lower() not in {"local", "test", "demo"},
        samesite="strict",
        path="/",
    )
    return response


@forms_router.get("/v1/forms/session")
async def get_form_session(request: Request, instrument: Optional[str] = Query(None)):
    ticket = _request_form_ticket(request, instrument)
    if not ticket:
        raise HTTPException(status_code=401, detail="sessao do formulario nao encontrada")
    payload = _verify_form_token(ticket)
    if instrument and payload["instrument"] != instrument:
        raise HTTPException(status_code=403, detail="ticket nao pertence a este instrumento")
    return {
        "id_hash": payload["id_hash"],
        "instrument": payload["instrument"],
        "expires_at": datetime.fromtimestamp(int(payload["exp"]), tz=timezone.utc).isoformat(),
    }


@forms_router.get("/v1/forms/i18n/{locale}")
async def get_form_i18n(locale: str, instrument: str = Query(...)):
    return form_messages(locale, instrument)


@forms_router.get("/forms/assets/{filename}", include_in_schema=False)
async def serve_form_asset(filename: str):
    allowed = {
        "form-world.css": "text/css; charset=utf-8",
        "form-world.js": "application/javascript; charset=utf-8",
    }
    media_type = allowed.get(filename)
    if not media_type:
        raise HTTPException(status_code=404, detail="Asset nao encontrado")
    path = FORMS_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Asset nao encontrado")
    return FileResponse(path, media_type=media_type)


@forms_router.post("/v1/psychometric/submit")
async def submit_psychometric(request: Request, body: SubmitRequest, db: AsyncSession = Depends(get_db)):
    _authorize_psychometric_submit(request, body)

    if not body.id_hash:
        raise HTTPException(status_code=400, detail="id_hash e obrigatorio")

    await ensure_schedule_exists(db, body.id_hash)

    from ...engine.supreme.psi import score_dass21, score_olbi, score_panas_short, score_srq20
    try:
        if body.instrument == "PANAS_SHORT":
            score = score_panas_short(body.responses)["na"]
        elif body.instrument == "DASS21":
            score = score_dass21(body.responses)["total"]
        elif body.instrument == "OLBI":
            score = score_olbi(body.responses)["exhaustion"]
        elif body.instrument == "SRQ20":
            score = float(score_srq20(body.responses)["total"])
        else:
            raise HTTPException(status_code=400, detail="Instrumento invalido")
    except AssertionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    today = date.today()
    # Alinha window_ref com as janelas reais do estudo (study_start + N*window_days).
    # O cálculo anterior (today - today.day % 14) produzia datas arbitrárias que
    # nunca coincidiam com as janelas do IEO, impedindo o link PSI→ieo_windows.
    _s = get_settings()
    _study_start = date.fromisoformat(_s.study_start_date)
    _days = (today - _study_start).days
    _window_num = max(0, _days // _s.window_days)
    window_ref = _study_start + timedelta(days=_window_num * _s.window_days)

    record_id = await insert_psychometric_submission(
        db=db, id_hash=body.id_hash, instrument=body.instrument,
        score=score, window_ref=window_ref, responses=body.responses,
    )

    history    = await fetch_psychometric_history(db, body.id_hash, limit=200)
    study_week = 0
    if history:
        first_ts = min(h["timestamp"] for h in history)
        if first_ts:
            first_date = first_ts.date() if hasattr(first_ts, "date") else first_ts
            study_week = max(0, (today - first_date).days // 7)

    await upsert_schedule(
        db=db, id_hash=body.id_hash, instrument=body.instrument,
        next_due=_next_due(body.instrument, study_week), study_week=study_week,
    )

    log.info("Submissao | id_hash=%.8s instrument=%s score=%.1f record_id=%s",
             body.id_hash, body.instrument, score, record_id)

    # Envia para SENTINELA (fire-and-forget)
    try:
        await push_psychometric(
            id_hash=body.id_hash, instrument=body.instrument,
            score=score, window_ref=window_ref, submitted_at=today,
        )
    except Exception as exc:
        log.warning("SENTINELA push psico falhou: %s", exc)

    psi_result = None
    try:
        await _compute_and_save_psi(db, body.id_hash, window_ref)
        # Busca resultado PSI para incluir no push IEO
        from ..db import fetch_scores_by_instrument
        dass_hist  = await fetch_scores_by_instrument(db, body.id_hash, "DASS21")
        olbi_hist  = await fetch_scores_by_instrument(db, body.id_hash, "OLBI")
        srq_hist   = await fetch_scores_by_instrument(db, body.id_hash, "SRQ20")
        panas_hist = await fetch_scores_by_instrument(db, body.id_hash, "PANAS_SHORT")
        from ...engine.supreme.psi import score_dass21, score_olbi, score_panas_short, score_srq20
        from ..db import fetch_latest_ieo_score
        oei = await fetch_latest_ieo_score(db, body.id_hash)
        mean_dass, sd_dass   = _rolling_stats(dass_hist[:-1]  if len(dass_hist)  > 1 else [])
        mean_olbi, sd_olbi   = _rolling_stats(olbi_hist[:-1]  if len(olbi_hist)  > 1 else [])
        mean_srq,  sd_srq    = _rolling_stats(srq_hist[:-1]   if len(srq_hist)   > 1 else [])
        mean_panas, sd_panas = _rolling_stats(panas_hist[:-1] if len(panas_hist) > 1 else [])
        psi_result = compute_psi(
            dass_raw=dass_hist[-1]  if dass_hist  else None,
            olbi_raw=olbi_hist[-1]  if olbi_hist  else None,
            srq_raw=srq_hist[-1]    if srq_hist   else None,
            panas_neg_raw=panas_hist[-1] if panas_hist else None,
            mean_dass=mean_dass, sd_dass=sd_dass,
            mean_olbi=mean_olbi, sd_olbi=sd_olbi,
            mean_srq=mean_srq,   sd_srq=sd_srq,
            mean_panas=mean_panas, sd_panas=sd_panas,
            oei_score=oei,
        )
    except Exception as exc:
        log.warning("PSI nao calculado: %s", exc)

    # Fix B10: push PSI-only ao SENTINELA apenas se janela IEO já existir.
    # Antes, push_ieo() era chamado com ieo_score=None para todos os casos,
    # criando linhas órfãs no banco do SENTINELA e sobrescrevendo IEO com NULL.
    # Agora: enviamos apenas os campos PSI via push_ieo(); o endpoint do
    # SENTINELA (PSI_ONLY_UPDATE_SQL) só atualiza se a linha já existir.
    if psi_result is not None:
        await _recompute_flags_if_ieo_exists(db, body.id_hash, window_ref)
        try:
            await push_ieo(
                id_hash=body.id_hash,
                window_start=window_ref,
                # IEO fields: None — o endpoint do SENTINELA só fará UPDATE
                # se a linha existir, sem criar órfã nem sobrescrever IEO (Fix B2+B10)
                t_minutes=None, e_events=None, v_volume=None,
                d_density=None, dq_score=None, ieo_score=None,
                ieo_linear=None, ieo_sat=None,
                z_t=None, z_e=None, z_v=None, z_d=None,
                # PSI fields preenchidos
                psi_score=psi_result.psi_score,
                z_dass=psi_result.z_dass,
                z_olbi=psi_result.z_olbi,
                z_srq=psi_result.z_srq,
                z_panas_neg=psi_result.z_panas_neg,
                convergence_class=psi_result.convergence_class,
                algorithm_version=CURRENT_ALGORITHM_VERSION,
                algorithm_parameters=algorithm_parameters(),
            )
        except Exception as exc:
            log.warning("SENTINELA push PSI falhou: %s", exc)

    return {
        "status":     "ok",
        "record_id":  record_id,
        "instrument": body.instrument,
        "score":      score,
        "window_ref": str(window_ref),
    }


@forms_router.get("/forms/{instrument}", include_in_schema=False)
async def serve_form(request: Request, instrument: str, locale: str = Query("pt-BR")):
    mapping = {
        "panas":  "panas.html",
        "dass21": "dass21.html",
        "olbi":   "olbi.html",
        "srq20":  "srq20.html",
    }
    filename = mapping.get(instrument.lower())
    if not filename:
        raise HTTPException(status_code=404, detail=f"Formulario '{instrument}' nao encontrado")
    html_path = FORMS_DIR / filename
    if not html_path.exists():
        raise HTTPException(status_code=500, detail=f"Arquivo {filename} nao encontrado")
    html = html_path.read_text(encoding="utf-8")
    expected_instrument = _INSTRUMENT_BY_FORM_PATH[instrument.lower()]
    html = _inject_form_i18n(html, locale, expected_instrument)
    return HTMLResponse(_apply_form_nonce(html, _csp_nonce(request)))


@router.get("/export", summary="Exportacao CSV para R")
async def export_csv(
    start_date: Optional[date] = Query(None),
    end_date:   Optional[date] = Query(None),
    db:         AsyncSession   = Depends(get_db),
):
    from sqlalchemy import text as sql_text

    date_filter = ""
    params: dict = {}
    if start_date:
        date_filter += " AND wm.window_start >= :start_date"
        params["start_date"] = start_date
    if end_date:
        date_filter += " AND wm.window_start <= :end_date"
        params["end_date"] = end_date

    query = sql_text(f"""
        SELECT
            wm.id_hash, wm.window_start,
            wm.t_minutes, wm.e_events, wm.v_volume, wm.d_density, wm.dq_score,
            il.ieo_score, il.ieo_linear, il.ieo_sat, il.z_t, il.z_e, il.z_v, il.z_d,
            ps.psi_score, ps.z_dass, ps.z_olbi, ps.z_srq, ps.z_panas_neg,
            ps.dass_raw, ps.olbi_raw, ps.srq_raw, ps.panas_neg_raw,
            ps.convergence_class
        FROM window_metrics wm
        LEFT JOIN ieo_logs il ON il.id_hash = wm.id_hash AND il.window_start = wm.window_start
        LEFT JOIN psi_scores ps ON ps.id_hash = wm.id_hash AND ps.window_start = wm.window_start
        WHERE 1=1 {date_filter}
        ORDER BY wm.id_hash, wm.window_start
    """)

    result = await db.execute(query, params)
    rows   = result.fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "id_hash", "window_start",
        "t_minutes", "e_events", "v_volume", "d_density", "dq_score",
        "ieo_score", "ieo_linear", "ieo_sat", "z_t", "z_e", "z_v", "z_d",
        "psi_score", "z_dass", "z_olbi", "z_srq", "z_panas_neg",
        "dass_raw", "olbi_raw", "srq_raw", "panas_neg_raw",
        "convergence_class",
    ])
    for row in rows:
        writer.writerow(list(row))

    filename = f"supreme_export_{date.today().isoformat()}.csv"
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
