from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Callable, Optional
from uuid import uuid4

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import text

from .config import settings
from .db import AsyncSession, get_db

SESSION_COOKIE_NAME = "sentinela_session"
CANONICAL_ROLES = ("master", "pesquisador", "auditor", "operador", "leitura_agregada")
ROLE_ALIASES = {"pibic": "pesquisador"}

ROLE_PERMISSIONS = {
    "master": {
        "dashboard:aggregate",
        "dashboard:participant",
        "dashboard:flags",
        "dashboard:lifecycle",
        "export:scientific",
        "product:studies",
        "product:participants",
        "product:pipeline",
        "product:data_quality",
        "report:signed",
        "users:manage",
        "audit:read",
    },
    "pesquisador": {
        "dashboard:aggregate",
        "dashboard:participant",
        "dashboard:flags",
        "export:scientific",
        "product:studies",
        "product:participants",
        "product:data_quality",
        "report:signed",
    },
    "auditor": {
        "dashboard:aggregate",
        "dashboard:participant",
        "dashboard:flags",
        "export:scientific",
        "product:studies",
        "product:participants",
        "product:pipeline",
        "product:data_quality",
        "report:signed",
        "audit:read",
    },
    "operador": {
        "dashboard:aggregate",
        "dashboard:participant",
        "dashboard:lifecycle",
        "product:studies",
        "product:participants",
        "product:pipeline",
        "product:data_quality",
    },
    "leitura_agregada": {
        "dashboard:aggregate",
        "product:studies",
        "product:data_quality",
    },
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserOut(BaseModel):
    email: str
    role: str
    scopes: dict[str, list[str]] = {
        "institutions": [],
        "studies": [],
        "cases": [],
        "participants": [],
    }


def canonical_role(role: str) -> str:
    return ROLE_ALIASES.get((role or "").strip().lower(), (role or "").strip().lower())


def validate_role(role: str) -> str:
    normalized = canonical_role(role)
    if normalized not in CANONICAL_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"role deve ser um de {', '.join(CANONICAL_ROLES)}",
        )
    return normalized


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def _legacy_sha256(password: str) -> str:
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain: str, hashed: str) -> bool:
    if hashed.startswith("$2"):
        return pwd_context.verify(plain, hashed)
    # Compatibilidade controlada com usuários antigos; rehash ocorre no login.
    return _legacy_sha256(plain) == hashed


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.now(tz=timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    return jwt.encode({**data, "exp": expire, "jti": str(uuid4())}, settings.secret_key, algorithm=settings.algorithm)


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[dict]:
    result = await db.execute(
        text("SELECT id, email, password_hash, role FROM sentinela_users WHERE email = :e"),
        {"e": email},
    )
    row = result.fetchone()
    if not row:
        return None
    if not verify_password(password, row[2]):
        return None
    if not str(row[2]).startswith("$2"):
        await db.execute(
            text("UPDATE sentinela_users SET password_hash = :p WHERE id = :id"),
            {"p": hash_password(password), "id": row[0]},
        )
        await db.commit()
    return {"id": row[0], "email": row[1], "role": canonical_role(row[3])}


async def fetch_user_security_context(db: AsyncSession, email: str, token_role: str = "") -> dict:
    result = await db.execute(
        text("SELECT id, email, role FROM sentinela_users WHERE email = :e"),
        {"e": email},
    )
    row = result.fetchone()
    if row:
        user_id, user_email, role = row[0], row[1], canonical_role(row[2])
    else:
        user_id, user_email, role = None, email, canonical_role(token_role)
    if role not in CANONICAL_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role invalida")

    scopes: dict[str, set[str]] = {
        "institutions": set(),
        "studies": set(),
        "cases": set(),
        "participants": set(),
    }
    if role == "master":
        for key in scopes:
            scopes[key].add("*")
    elif user_id is not None:
        rows = await db.execute(
            text("""
                SELECT institution_id, study_id, case_id, participant_id
                FROM user_scope_assignments
                WHERE user_id = :user_id
            """),
            {"user_id": user_id},
        )
        for scope in rows.fetchall():
            if scope[0]:
                scopes["institutions"].add(scope[0])
            if scope[1]:
                scopes["studies"].add(scope[1])
            if scope[2]:
                scopes["cases"].add(scope[2])
            if scope[3]:
                scopes["participants"].add(scope[3])

    return {
        "id": user_id,
        "email": user_email,
        "role": role,
        "permissions": sorted(ROLE_PERMISSIONS[role]),
        "scopes": {key: sorted(value) for key, value in scopes.items()},
    }


async def get_current_user(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> dict:
    token = token or request.cookies.get(SESSION_COOKIE_NAME)
    try:
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessao ausente")
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub", "")
        role:  str = canonical_role(payload.get("role", ""))
        if not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido")
        return await fetch_user_security_context(db, email, role)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido")


async def require_master(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "master":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso restrito a master")
    return user


def require_permission(permission: str) -> Callable:
    async def dependency(user: dict = Depends(get_current_user)) -> dict:
        if permission not in user.get("permissions", []):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissao insuficiente")
        return user

    return dependency


def require_roles(*roles: str) -> Callable:
    allowed = {canonical_role(role) for role in roles}

    async def dependency(user: dict = Depends(get_current_user)) -> dict:
        if user["role"] not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role nao autorizada")
        return user

    return dependency


def _scope_allows(values: list[str], candidate: str | None) -> bool:
    return "*" in values or (candidate is not None and candidate in values)


def assert_participant_scope(user: dict, participant_id: str) -> None:
    scopes = user.get("scopes", {})
    if user["role"] == "master":
        return
    if user["role"] == "leitura_agregada":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso individual indisponivel")
    if _scope_allows(scopes.get("participants", []), participant_id):
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Participante fora do escopo")


def scoped_id_filter(user: dict, column: str = "id_hash") -> tuple[str, dict]:
    if user["role"] == "master":
        return "", {}
    scopes = user.get("scopes", {})
    participants = scopes.get("participants", [])
    institutions = scopes.get("institutions", [])
    studies = scopes.get("studies", [])
    cases = scopes.get("cases", [])

    if "*" in participants or "*" in institutions or "*" in studies or "*" in cases:
        return "", {}

    conditions: list[str] = []
    params: dict = {}

    if participants:
        params.update({f"scope_participant_{index}": value for index, value in enumerate(participants)})
        placeholders = ", ".join(f":scope_participant_{index}" for index in range(len(participants)))
        conditions.append(f"{column} IN ({placeholders})")

    def registry_condition(scope_name: str, values: list[str], registry_column: str) -> None:
        if not values:
            return
        keys = [f"scope_{scope_name}_{index}" for index in range(len(values))]
        params.update({key: value for key, value in zip(keys, values)})
        placeholders = ", ".join(f":{key}" for key in keys)
        conditions.append(
            "EXISTS ("
            "SELECT 1 FROM participant_registry pr_scope "
            f"WHERE pr_scope.id_hash = {column} "
            f"AND pr_scope.{registry_column} IN ({placeholders})"
            ")"
        )

    registry_condition("institution", institutions, "institution_id")
    registry_condition("study", studies, "study_id")
    registry_condition("case", cases, "case_id")

    if not conditions:
        return " AND 1=0", {}
    return " AND (" + " OR ".join(conditions) + ")", params
