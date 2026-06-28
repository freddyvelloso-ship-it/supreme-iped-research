import os

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://supreme:supreme@localhost:5432/supreme_test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("API_SECRET_KEY", "test-api-secret-key-abcdefghijklmnopqrstuvwxyz-123456")
os.environ.setdefault("API_INGEST_TOKEN", "test-ingest-token-abcdefghijklmnopqrstuvwxyz-123456789")
os.environ.setdefault("SUPREME_SALT", "test-supreme-salt-abcdefghijklmnopqrstuvwxyz-123456789")
os.environ.setdefault("SENTINELA_API_KEY", "test-sentinela-api-key-abcdefghijklmnopqrstuvwxyz-123456")
os.environ.setdefault("SENTINELA_URL", "http://sentinela.test")
