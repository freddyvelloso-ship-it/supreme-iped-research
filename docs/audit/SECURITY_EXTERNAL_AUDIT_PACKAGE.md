# SUPREME V4 - External Security Audit Package

Provide this package to an independent security auditor:

- `docs/OWASP_ASVS_PHASE2.md`
- `scripts/production_readiness_check.ps1`
- `scripts/phase2_security_check.ps1`
- `scripts/secret_scan.ps1`
- `scripts/dependency_scan.ps1`
- `scripts/sast_scan.ps1`
- `scripts/generate_sbom.ps1`
- `reports/security/*.json`
- `docker-compose.production.yml`
- `docker-compose.staging.yml`
- `docs/runbooks/*.md`

Audit scope:

- Auth/session and HttpOnly cookies.
- RBAC and institution/study/case/participant scope.
- Secret management and rotation.
- Docker hardening and dependency posture.
- Production readiness rejection rules.
- Logging redaction.
- Incident and breach handling.

