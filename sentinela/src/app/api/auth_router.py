"""
sentinela.app.api.auth_router
=============================
Login e gestao de usuarios (apenas master pode criar usuarios).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hmac

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status
from pydantic import BaseModel
from sqlalchemy import text

from ..auth import (
    CANONICAL_ROLES, SESSION_COOKIE_NAME, UserOut,
    authenticate_user, create_access_token,
    fetch_user_security_context, get_current_user, hash_password, require_master, validate_role,
)
from ..config import settings
from ..db import AsyncSession, get_db

router = APIRouter(prefix="/api/auth", tags=["Auth"])

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8 horas
LOGIN_RATE_LIMIT_MAX_ATTEMPTS = 5
LOGIN_RATE_LIMIT_WINDOW_SECONDS = 60
_LOGIN_ATTEMPTS: dict[str, list[datetime]] = {}


class LoginRequest(BaseModel):
    email: str
    password: str


class CreateUserRequest(BaseModel):
    email: str
    password: str
    role: str = "pesquisador"


class SessionOut(UserOut):
    status: str = "ok"


class ScopeAssignmentRequest(BaseModel):
    role: str | None = None
    institution_id: str | None = None
    study_id: str | None = None
    case_id: str | None = None
    participant_id: str | None = None


def _cookie_secure() -> bool:
    return settings.environment.lower() not in {"local", "test", "demo"}


def _rate_limit_key(request: Request, email: str) -> str:
    forwarded = request.headers.get("x-forwarded-for", "").split(",", 1)[0].strip()
    ip = forwarded or (request.client.host if request.client else "unknown")
    return f"{ip}:{email.strip().lower()}"


def _check_login_rate_limit(request: Request, email: str) -> None:
    now = datetime.now(tz=timezone.utc)
    cutoff = now - timedelta(seconds=LOGIN_RATE_LIMIT_WINDOW_SECONDS)
    key = _rate_limit_key(request, email)
    attempts = [ts for ts in _LOGIN_ATTEMPTS.get(key, []) if ts > cutoff]
    if len(attempts) >= LOGIN_RATE_LIMIT_MAX_ATTEMPTS:
        raise HTTPException(status_code=429, detail="Muitas tentativas de login. Aguarde e tente novamente.")
    attempts.append(now)
    _LOGIN_ATTEMPTS[key] = attempts


def _clear_login_rate_limit(request: Request, email: str) -> None:
    _LOGIN_ATTEMPTS.pop(_rate_limit_key(request, email), None)


@router.post("/login", response_model=SessionOut)
async def login(body: LoginRequest, response: Response, request: Request, db: AsyncSession = Depends(get_db)):
    _check_login_rate_limit(request, body.email)
    user = await authenticate_user(db, body.email, body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais invalidas",
        )
    _clear_login_rate_limit(request, body.email)
    token = create_access_token(
        data={"sub": user["email"], "role": user["role"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=_cookie_secure(),
        samesite="strict",
        path="/",
    )
    current = await fetch_user_security_context(db, user["email"], user["role"])
    return {"status": "ok", "email": current["email"], "role": current["role"], "scopes": current["scopes"]}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        path="/",
        httponly=True,
        secure=_cookie_secure(),
        samesite="strict",
    )
    return {"status": "ok"}


@router.get("/me", response_model=UserOut)
async def me(current_user: dict = Depends(get_current_user)):
    return current_user


@router.post("/bootstrap", status_code=201, summary="Criar primeiro usuario master (uso unico)")
async def bootstrap_master(
    body: CreateUserRequest,
    db: AsyncSession = Depends(get_db),
    x_bootstrap_token: str = Header(default=""),
):
    flag = await db.execute(text("SELECT value FROM system_config WHERE key = 'bootstrap_used'"))
    if flag.fetchone():
        raise HTTPException(status_code=410, detail="Bootstrap ja utilizado e permanentemente desabilitado.")
    if not settings.bootstrap_token:
        raise HTTPException(status_code=403, detail="Bootstrap desabilitado.")
    if not hmac.compare_digest(x_bootstrap_token.encode(), settings.bootstrap_token.encode()):
        raise HTTPException(status_code=403, detail="Bootstrap token invalido.")

    existing = await db.execute(text("SELECT id FROM sentinela_users WHERE role = 'master'"))
    if existing.fetchone():
        await db.execute(text("INSERT INTO system_config(key, value) VALUES ('bootstrap_used', 'true') ON CONFLICT (key) DO UPDATE SET value='true', updated_at=NOW()"))
        await db.commit()
        raise HTTPException(status_code=409, detail="Ja existe um master. Use o login normal.")

    pw_hash = hash_password(body.password)
    await db.execute(
        text("INSERT INTO sentinela_users (email, password_hash, role) VALUES (:e, :p, 'master')"),
        {"e": body.email, "p": pw_hash},
    )
    await db.execute(text("INSERT INTO system_config(key, value) VALUES ('bootstrap_used', 'true') ON CONFLICT (key) DO UPDATE SET value='true', updated_at=NOW()"))
    await db.commit()
    return {"status": "ok", "message": "Master criado. Remova BOOTSTRAP_TOKEN do .env."}


@router.post("/users", status_code=201)
async def create_user(
    body: CreateUserRequest,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_master),
):
    role = validate_role(body.role)
    existing = await db.execute(
        text("SELECT id FROM sentinela_users WHERE email = :e"), {"e": body.email}
    )
    if existing.fetchone():
        raise HTTPException(status_code=409, detail="Email ja cadastrado")
    pw_hash = hash_password(body.password)
    await db.execute(
        text("INSERT INTO sentinela_users (email, password_hash, role) VALUES (:email, :pw, :role)"),
        {"email": body.email, "pw": pw_hash, "role": role},
    )
    await db.commit()
    return {"status": "ok", "email": body.email, "role": role}


@router.get("/users")
async def list_users(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_master),
):
    result = await db.execute(
        text("""
            SELECT u.id, u.email, u.role, u.created_at,
                   COALESCE(json_agg(json_build_object(
                       'institution_id', s.institution_id,
                       'study_id', s.study_id,
                       'case_id', s.case_id,
                       'participant_id', s.participant_id
                   )) FILTER (WHERE s.id IS NOT NULL), '[]'::json) AS scopes
            FROM sentinela_users u
            LEFT JOIN user_scope_assignments s ON s.user_id = u.id
            GROUP BY u.id, u.email, u.role, u.created_at
            ORDER BY u.created_at
        """)
    )
    rows = result.fetchall()
    return [{"id": r[0], "email": r[1], "role": r[2], "created_at": str(r[3]), "scopes": r[4]} for r in rows]


@router.post("/users/{user_id}/scopes", status_code=201)
async def assign_user_scope(
    user_id: int,
    body: ScopeAssignmentRequest,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_master),
):
    if body.role is not None:
        role = validate_role(body.role)
        await db.execute(text("UPDATE sentinela_users SET role = :role WHERE id = :id"), {"role": role, "id": user_id})
    if not any([body.institution_id, body.study_id, body.case_id, body.participant_id]):
        await db.commit()
        return {"status": "ok", "user_id": user_id, "scope": None}
    existing = await db.execute(text("SELECT id FROM sentinela_users WHERE id = :id"), {"id": user_id})
    if not existing.fetchone():
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    await db.execute(
        text("""
            INSERT INTO user_scope_assignments
                (user_id, institution_id, study_id, case_id, participant_id)
            VALUES
                (:user_id, :institution_id, :study_id, :case_id, :participant_id)
            ON CONFLICT DO NOTHING
        """),
        {
            "user_id": user_id,
            "institution_id": body.institution_id,
            "study_id": body.study_id,
            "case_id": body.case_id,
            "participant_id": body.participant_id,
        },
    )
    await db.commit()
    return {"status": "ok", "user_id": user_id}


@router.get("/roles")
async def list_roles(_: dict = Depends(require_master)):
    return {"roles": list(CANONICAL_ROLES)}
