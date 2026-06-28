# SUPREME V4 - Audit of Phases 0 and 1

Date: 2026-06-22

## Executive Result

Phases 0 and 1 are valid for the intended scope:

- Phase 0: clean distributable baseline.
- Phase 1: local Docker stack validated end to end.

They are not production go-live approval. Phase 2 must harden production identity, notification, secrets handling, public exposure, and CI/E2E.

## Phase 0 Audit

Status: approved for clean handoff.

Evidence:

- `supreme-v4-phase-zero-clean.zip` exists.
- Size: 563,656,150 bytes.
- Entries: 1,977.
- Release gate passed inside the clean package.
- No `.env`, `.env.production`, private TLS key, local Prometheus token, Python cache, or nested ZIP outside `IPED-local`.
- Environment examples are preserved:
  - `.env.production.example`
  - `supreme-backend/.env.production.example`
  - `sentinela/.env.production.example`
- Identity cleanup is in place: no active references to a later major version outside allowed documentation/gate references.

Residual notes:

- IPED-local contains its own internal ZIP files. This is accepted by the gate because they are part of the IPED bundle.
- Phase 0 package does not include the Phase 1 validation report, by design.

## Phase 1 Audit

Status: approved for local validation.

Evidence:

- `supreme-v4-phase-one-local-validated.zip` exists.
- Size: 563,656,741 bytes.
- Entries: 1,979.
- Clean package gate passed.
- Template readiness passed with 0 failures and 0 warnings.
- Local readiness passed with 0 failures and 0 warnings.
- Python `compileall` passed.
- Local Docker stack is running with 15 services.
- Healthy services include:
  - `supreme-api`
  - `sentinela`
  - `supreme-db`
  - `sentinela-db`
  - `supreme-redis`
- HTTP checks passed:
  - `https://localhost/health`
  - `https://localhost/v1/health`
  - `https://localhost/sentinela/health`
  - `http://localhost:9090/-/ready`
  - `http://localhost:9093/-/ready`
  - `http://localhost:3000/login`
- Prometheus targets are all `up`:
  - `supreme-api`
  - `postgres-exporter`
  - `redis-exporter`
  - `prometheus`
  - `alertmanager`
- Recent logs show `/metrics` returning `200 OK`.

## Findings

### P1 - Not production-ready alert delivery

Status Phase 2: resolved for local/homologation. Alertmanager now uses rendered SMTP config and sends to Mailpit locally.

Former impact: no email, webhook, Slack, Teams, PagerDuty, or escalation path in production.

Required before production: run `scripts/render_alertmanager_config.ps1` with institutional SMTP or replace the rendered file through the deployment secret mechanism, then validate delivery.

### P1 - Local setup prints secrets to terminal

Status Phase 2: resolved in `SUBIR_LOCAL.ps1`. Full secrets are saved to `.local/credentials.local.txt`; terminal output is masked/path-only.

Impact: acceptable for single-machine local bootstrap, unsafe for shared terminals, recordings, support sessions, logs, or production-like environments.

Required before production: keep `.local/`, `.env` and generated configs out of version control and support captures.

### P1 - Bootstrap token remains in local env after bootstrap

Status Phase 2: resolved in `SUBIR_LOCAL.ps1`. After login succeeds, `BOOTSTRAP_TOKEN` is blanked in `sentinela/.env.production` and the container is recreated.

Impact: safe only for local validation. Production must remove or blank `BOOTSTRAP_TOKEN` after master creation.

Required before production: keep the production readiness gate rejecting non-empty `BOOTSTRAP_TOKEN`.

### P2 - Smoke test depends on shell tooling

Status Phase 2: resolved for Windows. `scripts/smoke_test.ps1` is now the canonical local smoke test and uses PowerShell/JSON parsing, with an optional Python fallback for self-signed TLS issues.

Impact: local PowerShell validation passed, but the shell smoke script is not universally portable on Windows.

Recommended: keep `scripts/smoke_test.sh` for Linux/CI and `scripts/smoke_test.ps1` for Windows local validation.

### P2 - Production readiness and local readiness are now distinct

`-LocalMode` intentionally permits localhost and bootstrap token. This is useful, but dangerous if confused with go-live approval.

Impact: a dev could mistakenly cite local readiness as production readiness.

Recommended: documentation and CI should name it explicitly as local-only.

### P2 - Launcher still exposes ingest token in form URLs

The documentation and launcher flow still use `?token=` for some form URLs.

Impact: token can appear in browser history, logs, screenshots, referrers, and support artifacts.

Required before production-grade field use: replace URL token with short-lived per-user/per-instrument signed link.

## Go / No-Go

Go for Phase 2: yes.

No-go for production: yes, still no production release.

The next phase should focus on:

- real alerting path;
- secret output masking;
- production bootstrap cleanup;
- Windows-native smoke test;
- signed form links;
- CI pipeline running template gate, local smoke equivalent, and package cleanliness checks.
