from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from .config import settings

engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    import pathlib
    migrations_dir = pathlib.Path("/app/migrations")
    migrations = sorted(migrations_dir.glob("*.sql")) if migrations_dir.exists() else []
    async with engine.begin() as conn:
        for p in migrations:
            migration_sql = p.read_text(encoding="utf-8")
            statements = [s.strip() for s in migration_sql.split(";") if s.strip()]
            for stmt in statements:
                await conn.execute(text(stmt))
