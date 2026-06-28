# SUPREME V4 - Key And Token Rotation

## Tokens

- `API_SECRET_KEY`: admin/metrics token used by SUPREME protected endpoints and Prometheus bearer file.
- `API_INGEST_TOKEN`: ingestion token used by IPED watcher/proxy to send events to SUPREME.
- `SUPREME_SALT`: offline pseudonymization salt. Rotate only under incident response because it changes identifiers.
- `SENTINELA_API_KEY` / `SUPREME_API_KEY`: shared service credential for SUPREME to push outputs into SENTINELA.
- `SECRET_KEY`: SENTINELA session signing key. Rotation invalidates active dashboard sessions.

## Operational Rotation

Use:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\rotate_api_tokens.ps1 -RotateAdminToken
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\rotate_api_tokens.ps1 -RotateIngestToken
```

The script creates local backups under `.local/rotation-backups`, updates affected env files and masks values in terminal output.

## Production Rules

- Do not print full tokens, salts or passwords in terminal, docs or logs.
- Do not leave `BOOTSTRAP_TOKEN` populated after the first master user is created.
- Rotate service tokens after suspected exposure, staff offboarding or environment promotion.
- Record rotation metadata in `token_rotation_history` or the external change-management system.
- Re-run readiness and security gates after rotation.
