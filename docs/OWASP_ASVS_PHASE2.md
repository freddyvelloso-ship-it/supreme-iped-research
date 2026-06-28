# SUPREME V4 - OWASP ASVS Phase 2 Mapping

Status: initial evidence map for Phase 2 security gates.

## Scope

Applies to SUPREME backend, SENTINELA dashboard/API, local/demo/homologation/production profiles, Docker packaging and CI gates.

## Evidence Map

| ASVS area | Phase 2 control | Evidence |
| --- | --- | --- |
| V2 Authentication | Login uses password hashing, rate limit and generic failure message. | `sentinela/src/app/api/auth_router.py`, `sentinela/tests/test_phase2_security.py` |
| V3 Session Management | Browser session token is stored only in HttpOnly SameSite cookie. | `sentinela/src/app/api/auth_router.py`, `sentinela/static/index.html`, `scripts/phase2_security_check.ps1` |
| V4 Access Control | RBAC roles: `master`, `pesquisador`, `auditor`, `operador`, `leitura_agregada`. | `sentinela/src/app/auth.py`, `sentinela/migrations/004_security_rbac_scopes.sql` |
| V4 Access Control | Scopes exist for institution, study, case and participant. | `sentinela/migrations/004_security_rbac_scopes.sql`, `sentinela/src/app/auth.py` |
| V5 Validation | Form session ticket is submitted in POST body, not URL. | `supreme-backend/src/app/api/psychometric.py`, `scripts/phase2_security_check.ps1` |
| V7 Error Handling | Login and token checks avoid secret disclosure. | `sentinela/src/app/api/auth_router.py`, `scripts/secret_scan.ps1` |
| V8 Data Protection | Local/prod secrets remain ignored and secret scan fails on critical leaks. | `.gitignore`, `scripts/secret_scan.ps1` |
| V10 Malicious Code | SAST baseline blocks eval/exec/shell=True/pickle/token-in-URL patterns. | `scripts/sast_scan.ps1` |
| V12 File/Resource | Docker services use pinned bases, non-root app users and compose healthchecks. | `sentinela/Dockerfile`, `supreme-backend/Dockerfile`, `docker-compose.production.yml` |
| V14 Configuration | Production readiness rejects open CORS, weak placeholders, SMTP fake/local, Alertmanager local noop and bootstrap token residue. | `scripts/production_readiness_check.ps1` |
| V14 Dependency | Dependency scan and SBOM are generated in CI and local gates. | `scripts/dependency_scan.ps1`, `scripts/generate_sbom.ps1`, `.github/workflows/ci.yml` |

## Current Phase 2 Acceptance Gates

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase2_security_check.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\production_readiness_check.ps1 -TemplateMode -SkipDockerCompose
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\production_readiness_check.ps1 -LocalMode -SkipDockerCompose
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\secret_scan.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\dependency_scan.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\sast_scan.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\generate_sbom.ps1 -Root .
```

## Limits

This is an initial ASVS evidence map, not an external certification. External security review, penetration testing and formal ASVS scoring remain production governance activities.
