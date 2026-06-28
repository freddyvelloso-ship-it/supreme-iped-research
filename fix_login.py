import asyncio
import getpass
import os

from passlib.context import CryptContext
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


engine = create_async_engine(os.environ["DATABASE_URL"])
Session = sessionmaker(engine, class_=AsyncSession)
ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def main():
    email = os.environ.get("SENTINELA_MASTER_EMAIL", "admin@local.test")
    password = os.environ.get("SENTINELA_MASTER_PASSWORD") or getpass.getpass(
        "Senha do usuario master SENTINELA: "
    )
    if not password:
        raise SystemExit("Senha vazia.")

    password_hash = ctx.hash(password)
    async with Session() as db:
        await db.execute(
            text(
                "INSERT INTO sentinela_users (email, password_hash, role) VALUES (:e,:h,:r) "
                "ON CONFLICT (email) DO UPDATE SET password_hash=EXCLUDED.password_hash, role=EXCLUDED.role"
            ),
            {"e": email, "h": password_hash, "r": "master"},
        )
        await db.execute(
            text(
                "INSERT INTO system_config(key,value) VALUES('bootstrap_used','true') "
                "ON CONFLICT(key) DO UPDATE SET value='true'"
            )
        )
        await db.commit()
    print(f"OK - usuario master atualizado: {email}")


asyncio.run(main())
