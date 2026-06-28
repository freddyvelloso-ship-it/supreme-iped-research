# SUPREME V4 - Staging Deployment

Staging must mirror production services and configuration shape while using
isolated volumes, staging domains, staging SMTP and synthetic or anonymized data.

## Required Files

- `docker-compose.production.yml`
- `docker-compose.staging.yml`
- `env/.env.staging.example`
- `supreme-backend/.env.staging.example`
- `sentinela/.env.staging.example`

## Procedure

1. Copy example env values into an untracked secret store or deployment vault.
2. Set `SUPREME_ENV_FILE` and `SENTINELA_ENV_FILE` to staging env files.
3. Validate configuration:

```powershell
docker compose --env-file env\.env.staging.example -f docker-compose.production.yml -f docker-compose.staging.yml config --quiet
```

4. Start staging:

```powershell
docker compose --env-file <secure-staging-env> -f docker-compose.production.yml -f docker-compose.staging.yml up -d --build
```

5. Run Phase 1 E2E, Phase 3 analytics gate, Phase 5 custody gate, Phase 6 product
gate and Phase 7 world production gate.

Real IPED is enabled through the `iped-real` profile and must point
`IPED_AUDIT_DIR` to a controlled audit directory.

