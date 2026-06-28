# SUPREME V4 - Phase Execution Ledger

This file is the execution source of truth for phase-by-phase work. Older audit
documents are historical snapshots unless they are explicitly referenced here as
current evidence.

## Operating Rule

- Work one phase at a time.
- Do not advance while the current phase has a failed acceptance criterion.
- A phase is 100% only when its required commands pass and evidence is recorded.
- Local development state is not the same thing as a clean release package.

## Phase 0 - Limpeza e Verdade do Pacote

Status: 100_PERCENT_COMPLETE

Criteria:

- Real/local `.env` files are not present in the release package.
- Safe and complete `.env.example` files exist.
- SUPREME V4 is the only current product identity.
- Critical release files do not contain mojibake.
- Local, demo, homologation and production profiles are separated.
- Release gate fails on secrets, tokens, salts, certificates, local databases,
  backups, dumps, nested ZIP files and sensitive IPED artifacts.
- A new clean ZIP is generated.
- The ZIP is extracted to temporary staging.
- The release gate and independent phase-zero audit pass inside staging.

Evidence required:

- Path to generated ZIP.
- Path to staging extraction.
- `scripts/release_phase_zero_check.ps1 -Root <staging>` exits 0.
- `scripts/phase_zero_audit.ps1 -Root <staging>` exits 0.

Commands:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build_phase_zero_release.ps1
powershell -ExecutionPolicy Bypass -File scripts\release_phase_zero_check.ps1 -Root <staging>
powershell -ExecutionPolicy Bypass -File scripts\phase_zero_audit.ps1 -Root <staging>
```

Result: PASSED

Evidence captured on 2026-06-22:

- Project root:
  `C:\Users\nunas\Documents\Codex\2026-06-18\files-mentioned-by-the-user-nexus\work\supreme-v4-audit`
- Generated clean ZIP:
  `C:\Users\nunas\Documents\Codex\2026-06-18\files-mentioned-by-the-user-nexus\outputs\supreme-v4-phase-zero-100-20260622-235326.zip`
- ZIP size: `3152317` bytes.
- Staging extraction:
  `C:\Users\nunas\Documents\Codex\2026-06-18\files-mentioned-by-the-user-nexus\tmp\phase-zero-release\staging-20260622-235326`
- Staging root item count: `31`.
- Forbidden artifact scan inside staging returned no results for `.env`,
  `.env.production`, `.zip`, `.dump`, `.bak`, `.db`, TLS certs, private keys,
  Prometheus local token, `IPED-local` or `backups`.

Commands executed:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\build_phase_zero_release.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\release_phase_zero_check.ps1 -Root "C:\Users\nunas\Documents\Codex\2026-06-18\files-mentioned-by-the-user-nexus\tmp\phase-zero-release\staging-20260622-235326"
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase_zero_audit.ps1 -Root "C:\Users\nunas\Documents\Codex\2026-06-18\files-mentioned-by-the-user-nexus\tmp\phase-zero-release\staging-20260622-235326"
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\production_readiness_check.ps1 -TemplateMode -SkipDockerCompose
```

Gate results:

- `release_phase_zero_check.ps1`: `Resumo: 0 falha(s)`.
- `phase_zero_audit.ps1`: `Resumo Fase 0: 0 falha(s), 0 aviso(s)`.
- `production_readiness_check.ps1 -TemplateMode -SkipDockerCompose`:
  `Resumo: 0 falha(s), 0 aviso(s)`.

Decision: PHASE 0 COMPLETE. DO NOT ADVANCE TO PHASE 1 WITHOUT USER CONFIRMATION.

## Phase 1 - Execucao Local Reprodutivel

Status: 100_PERCENT_COMPLETE

Criteria:

- `docker-compose.local.yml` validates as an explicit local override over
  `docker-compose.production.yml`.
- One command can setup, reset, start, seed, test and simulate the local system.
- Local secrets are generated automatically without printing secret values.
- Clean and demo seeds are separate and executable.
- Healthchecks validate SUPREME, SENTINELA, Redis, Postgres and NGINX.
- Deterministic E2E validates simulated IPED event -> SUPREME -> Redis/RQ ->
  Postgres -> SENTINELA.
- `docs/LOCAL_15_MINUTES.md` documents the short local workflow.
- The one-command flow runs from zero with regenerated secrets and reset volumes.

Evidence captured on 2026-06-22:

- `docker compose -f docker-compose.production.yml -f docker-compose.local.yml config --quiet`: passed.
- `scripts\setup_env_local.ps1` generates `.env`,
  `supreme-backend\.env.production`, `sentinela\.env.production`,
  `infra\prometheus\supreme-api-token.local` and
  `infra\alertmanager\alertmanager.yml`; command output lists paths only, not
  secret values.
- `scripts\production_readiness_check.ps1 -LocalMode -SkipDockerCompose`:
  `Resumo: 0 falha(s), 0 aviso(s)`.
- `scripts\local.ps1 -Action health ...`: SUPREME API, SENTINELA, NGINX HTTPS,
  SUPREME Postgres, SENTINELA Postgres and Redis all OK.
- `scripts\local.ps1 -Action seed-demo`: applied demo seed; database checks
  showed `2` `phase1-*` demo records in SUPREME and `2` in SENTINELA.
- `scripts\local.ps1 -Action seed-clean`: removed demo/e2e records; database
  checks showed `0` `phase1-*` records in SUPREME and SENTINELA before final E2E.
- `scripts\local.ps1 -Action all -RegenerateSecrets ...`: passed from zero.
- Final `scripts\local.ps1 -Action test ...`: E2E JSON:
  `status=ok`, `events_stored_http=8`, `events_raw=8`,
  `redis_rq_analytics_observed=true`, `pipeline_status=ok`,
  `window_metrics_at_least_4=true`, `ieo_logs=4`,
  `sentinela_ieo_windows=4`, `id_hash=phase1-e2e-1782185179`.

Commands executed:

```powershell
docker compose -f docker-compose.production.yml -f docker-compose.local.yml config --quiet
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\local.ps1 -Action all -RegenerateSecrets -PythonExe "C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -TimeoutSeconds 300
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\production_readiness_check.ps1 -LocalMode -SkipDockerCompose
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\local.ps1 -Action health -PythonExe "C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -TimeoutSeconds 180
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\local.ps1 -Action seed-demo
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\local.ps1 -Action seed-clean
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\local.ps1 -Action test -PythonExe "C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -TimeoutSeconds 180
```

Operational note:

- In this Codex desktop environment, commands that invoke `docker exec` required
  Docker access outside the restricted sandbox. The product scripts themselves
  are deterministic; the permission requirement is host-execution specific.

Decision: PHASE 1 COMPLETE. DO NOT ADVANCE TO PHASE 2 WITHOUT USER CONFIRMATION.

## Phase 2 - Seguranca Seria

Status: 100_PERCENT_COMPLETE

Criteria:

- Browser session no longer stores tokens in `localStorage` or `sessionStorage`.
- SENTINELA login uses HttpOnly/SameSite cookie session.
- RBAC roles exist: `master`, `pesquisador`, `auditor`, `operador`,
  `leitura_agregada`.
- Scope model exists for institution, study, case and participant.
- Sensitive dashboard/export routes require permission and scope.
- Login rate limit is implemented and tested.
- Token/key rotation procedure is documented.
- Docker runtime uses pinned Python base images, non-root app users and compose
  healthchecks.
- CI/local scripts run secret scan, dependency scan, SAST and SBOM generation.
- Production readiness rejects bootstrap residue, open CORS, weak placeholders,
  fake/local SMTP, local-noop Alertmanager and token/ticket in URL patterns.
- Public psychometric forms do not receive a global browser token and generated
  form URLs do not include tickets/tokens in query string.
- Logs/scripts avoid printing full passwords, tokens or salts.

Evidence captured on 2026-06-23:

- Fase 0 and Fase 1 were confirmed as `100_PERCENT_COMPLETE` before work began.
- Session hardening:
  `sentinela/static/index.html` and `sentinela/static/war_room.html` use
  cookie-backed `fetch(..., credentials: 'same-origin')`; no browser storage is
  used for session tokens.
- Login validation against local SENTINELA:
  `POST http://localhost:18001/api/auth/login` returned HTTP 200, set
  `sentinela_session` with `HttpOnly` and `SameSite=strict`, returned no
  `access_token` field, and `GET /api/auth/me` returned `role=master` with
  wildcard scopes.
- RBAC/scope evidence:
  `sentinela/src/app/auth.py`, `sentinela/src/app/api/auth_router.py`,
  `sentinela/src/app/api/dashboard.py`, `sentinela/src/app/api/export.py`,
  `sentinela/migrations/004_security_rbac_scopes.sql`.
- Form URL hardening:
  `supreme-backend/src/app/api/psychometric.py` returns `/forms/<instrument>/start`
  plus a separate access code; session is established by POST body and cookie.
- Docker evidence:
  `sentinela/Dockerfile` and `supreme-backend/Dockerfile` use
  `python:3.11.9-slim` and `USER appuser`; compose healthchecks remain present.
- Security docs:
  `docs/OWASP_ASVS_PHASE2.md`, `docs/SECURITY_KEY_ROTATION.md`.
- Generated reports:
  `reports/security/secret_scan.json`,
  `reports/security/dependency_scan.json`,
  `reports/security/sast_scan.json`,
  `reports/security/sbom.cyclonedx.json`.

Commands executed:

```powershell
C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m compileall -q sentinela\src supreme-backend\src
$env:PYTHONPATH='.'; C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest -q tests   # in sentinela
$env:PYTHONPATH='.'; C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest -q tests   # in supreme-backend
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\secret_scan.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\dependency_scan.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\sast_scan.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\generate_sbom.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase2_security_check.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\production_readiness_check.ps1 -TemplateMode -SkipDockerCompose
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\production_readiness_check.ps1 -LocalMode -SkipDockerCompose
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\local.ps1 -Action health -PythonExe "C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -TimeoutSeconds 180
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\local.ps1 -Action test -PythonExe "C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -TimeoutSeconds 180
```

Gate results:

- SENTINELA tests: `12 passed`.
- SUPREME backend tests: `19 passed`.
- Compileall: passed.
- `secret_scan.ps1`: `0 critical finding(s)`.
- `dependency_scan.ps1`: `0 critical finding(s)`.
- `sast_scan.ps1`: `0 critical finding(s)`.
- `phase2_security_check.ps1`: `Resumo Fase 2 security check: 0 falha(s)`.
- `production_readiness_check.ps1 -TemplateMode -SkipDockerCompose`:
  `Resumo: 0 falha(s), 0 aviso(s)`.
- `production_readiness_check.ps1 -LocalMode -SkipDockerCompose`:
  `Resumo: 0 falha(s), 0 aviso(s)`.
- Local health:
  SUPREME API, SENTINELA, NGINX HTTPS, SUPREME Postgres, SENTINELA Postgres and
  Redis all OK.
- Local E2E:
  `status=ok`, `events_stored_http=8`, `events_raw=8`,
  `redis_rq_analytics_observed=true`, `pipeline_status=ok`,
  `window_metrics_at_least_4=true`, `ieo_logs=4`,
  `sentinela_ieo_windows=4`, `id_hash=phase1-e2e-1782188671`.

Operational note:

- Docker access in this Codex desktop environment required escalation for
  `docker exec`/local E2E commands. The first non-escalated E2E attempt failed
  on host Docker permissions; the escalated health/test gates passed.
- A first long `local.ps1 -Action all` run timed out at the shell wrapper limit,
  but logs showed containers rebuilt, reset volumes and applied
  `004_security_rbac_scopes.sql`; final `health` and `test` gates passed.

Decision: PHASE 2 COMPLETE. DO NOT ADVANCE TO PHASE 3 WITHOUT USER CONFIRMATION.

## Phase 3 - Motor Analitico Unico

Status: 100_PERCENT_COMPLETE

Criteria:

- IEO, PSI and red flags are centralized in SUPREME backend.
- Critical calculations are removed from SENTINELA/frontend.
- SENTINELA only receives, persists, exports and visualizes auditable outputs.
- `check_critical_load` uses psychometric values derived from the backend
  psychometric windows.
- Algorithm version, weights, thresholds and parameters are centralized in
  `supreme-backend/src/engine/supreme/algorithm.py`.
- Automated math tests cover IEO, PSI, convergence, dissonance, chronicity and
  reactivity.
- Same input produces same output.
- Analytical outputs carry `algorithm_version` and `algorithm_parameters`.
- SENTINELA reports/exports use SUPREME outputs and do not recompute critical
  rules.

Evidence captured on 2026-06-23:

- Fase 0, Fase 1 and Fase 2 were confirmed as `100_PERCENT_COMPLETE`.
- Phase 3 started from `NOT_STARTED`.
- SUPREME source of truth:
  `supreme-backend/src/engine/supreme/algorithm.py`,
  `supreme-backend/src/engine/supreme/ieo.py`,
  `supreme-backend/src/engine/supreme/psi.py`,
  `supreme-backend/src/engine/supreme/red_flags.py`.
- SUPREME pipeline evidence:
  `supreme-backend/src/worker/pipeline.py` computes IEO/PSI/red flags, passes
  psychometric windows into `check_critical_load`, and emits
  `SUPREME-ANALYTICS-1.0.0` plus parameters.
- SENTINELA viewer-only evidence:
  `sentinela/src/app/api/ingest.py`, `sentinela/src/app/api/dashboard.py`,
  `sentinela/src/app/api/export.py`, `sentinela/static/index.html`,
  `sentinela/static/war_room.html`.
- Regression gates added:
  `scripts/phase3_analytics_check.ps1`,
  `supreme-backend/tests/test_phase3_determinism_and_versioning.py`,
  `sentinela/tests/test_phase3_viewer_only.py`.
- CI runs `scripts/phase3_analytics_check.ps1`.
- E2E local JSON:
  `status=ok`, `events_stored_http=8`, `events_raw=8`,
  `redis_rq_analytics_observed=true`, `pipeline_status=ok`,
  `window_metrics_at_least_4=true`, `ieo_logs=4`,
  `sentinela_ieo_windows=4`, `id_hash=phase1-e2e-1782211909`.
- Database evidence for E2E id `phase1-e2e-1782211909`:
  SUPREME `ieo_logs` had `SUPREME-ANALYTICS-1.0.0` for `4` rows; SENTINELA
  `ieo_windows` had `SUPREME-ANALYTICS-1.0.0` for `4` rows and
  `algorithm_parameters` present in `4` rows.

Commands executed:

```powershell
C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m compileall -q sentinela\src supreme-backend\src
$env:PYTHONPATH='.'; C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest -q tests   # in supreme-backend
$env:PYTHONPATH='.'; C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest -q tests   # in sentinela
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase3_analytics_check.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\production_readiness_check.ps1 -TemplateMode -SkipDockerCompose
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase2_security_check.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\secret_scan.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\dependency_scan.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\sast_scan.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\generate_sbom.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\local.ps1 -Action test -PythonExe "C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -TimeoutSeconds 180
docker compose -f docker-compose.production.yml -f docker-compose.local.yml exec -T sentinela-db psql -U sentinela -d sentinela -c "SELECT algorithm_version, COUNT(*) FROM ieo_windows WHERE id_hash='phase1-e2e-1782211909' GROUP BY algorithm_version;"
docker compose -f docker-compose.production.yml -f docker-compose.local.yml exec -T sentinela-db psql -U sentinela -d sentinela -c "SELECT COUNT(*) AS rows_with_params FROM ieo_windows WHERE id_hash='phase1-e2e-1782211909' AND algorithm_parameters IS NOT NULL;"
docker compose -f docker-compose.production.yml -f docker-compose.local.yml exec -T supreme-db psql -U supreme -d supreme -c "SELECT algorithm_version, COUNT(*) FROM ieo_logs WHERE id_hash='phase1-e2e-1782211909' GROUP BY algorithm_version;"
```

Gate results:

- Compileall: passed.
- SUPREME backend tests: `20 passed`.
- SENTINELA tests: `15 passed`.
- `phase3_analytics_check.ps1`: `Resumo Fase 3: 0 falha(s)`.
- `production_readiness_check.ps1 -TemplateMode -SkipDockerCompose`:
  `Resumo: 0 falha(s), 0 aviso(s)`.
- `phase2_security_check.ps1`: `Resumo Fase 2 security check: 0 falha(s)`.
- `secret_scan.ps1`: `0 critical finding(s)`.
- `dependency_scan.ps1`: `0 critical finding(s)`.
- `sast_scan.ps1`: `0 critical finding(s)`.
- `generate_sbom.ps1`: SBOM generated.
- Local health/E2E: passed with `status=ok`.

Warnings:

- Pytest could not write cache in `supreme-backend/.pytest_cache` because of
  host file permission. This did not affect test execution or results.

Decision: PHASE 3 COMPLETE. DO NOT ADVANCE TO PHASE 4 WITHOUT USER CONFIRMATION.

## Phase 4 - Validacao Cientifica

Status: 100_PERCENT_COMPLETE

Criteria:

- Synthetic dataset with explicit ground truth exists and is deterministic.
- Required scenarios exist: `baixo_risco`, `reatividade`, `dissonancia`,
  `cronicidade`, `convergencia_critica`.
- False positive and false negative metrics are computed by scenario and in
  aggregate.
- Stability by sample volume is measured.
- Sensitivity to low-data-quality windows is measured.
- Technical validation report exists in `docs/`.
- SUPREME model card exists in `docs/`.
- Limits are documented: no clinical diagnosis, no psychological assessment as
  standalone proof, no automatic causal nexus.
- Reproducible scripts generate dataset, metrics and docs.
- Automated tests verify reproducibility of dataset and metrics.
- Results record algorithm version, algorithm parameters, seed and deterministic
  dataset digest.
- Validation uses only synthetic data and contains no real IPED data, secrets,
  salts, tokens or local artifacts.

Evidence captured on 2026-06-23:

- Preconditions checked first: Phase 0, Phase 1, Phase 2 and Phase 3 were all
  `100_PERCENT_COMPLETE`.
- Phase 4 started from `NOT_STARTED`.
- Synthetic dataset:
  `docs/phase4_validation/synthetic_ground_truth_dataset.jsonl`.
- Ground truth documentation:
  `docs/phase4_validation/GROUND_TRUTH.md`.
- Validation metrics:
  `docs/phase4_validation/validation_metrics.json`.
- Technical report:
  `docs/PHASE_FOUR_SCIENTIFIC_VALIDATION.md`.
- Model card:
  `docs/MODEL_CARD_SUPREME.md`.
- Reproducibility script:
  `scripts/phase4_scientific_validation.py`.
- Phase 4 gate:
  `scripts/phase4_scientific_validation_check.ps1`.
- Automated tests:
  `supreme-backend/tests/test_phase4_scientific_validation.py`.
- CI runs `scripts/phase4_scientific_validation_check.ps1`.
- Dataset digest:
  `845ef619dc74bc5fa30475a89e96ab044412ae3c6bf84370498cd37f728f17a3`.
- Dataset records: `240`; evaluation windows: `120`; seed: `424242`;
  algorithm version: `SUPREME-ANALYTICS-1.0.0`.

Metrics:

- Aggregate true positives: `72`.
- Aggregate false positives: `0`.
- Aggregate false negatives: `0`.
- Aggregate true negatives: `288`.
- Precision: `1.000000`.
- Recall: `1.000000`.
- F1: `1.000000`.
- False positive rate: `0.000000`.
- False negative rate: `0.000000`.
- Scenario convergence match rate: `1.000000` for all five required scenarios.
- Stability by volume: F1 stayed `1.000000` for `5`, `20` and `100` samples
  per scenario; max F1 delta `0.000000`.
- Low-quality sensitivity: DQ `1.0`, `0.7` and `0.4` all produced F1
  `1.000000`; max F1 drop `0.000000`.

Commands executed:

```powershell
Get-Content -LiteralPath docs\PHASE_EXECUTION_LEDGER.md
rg -n "Phase 4|Fase 4|validacao|validação|validation|model card|model_card|ground truth|synthetic|sintetico|falso positivo|false positive|false_negative|stability|sensibilidade|baixa qualidade" docs scripts supreme-backend sentinela -S
C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts\phase4_scientific_validation.py all
C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m compileall -q sentinela\src supreme-backend\src scripts\phase4_scientific_validation.py
$env:PYTHONPATH='.'; C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest -q tests   # in supreme-backend
$env:PYTHONPATH='.'; C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest -q tests   # in sentinela
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase4_scientific_validation_check.ps1 -Root . -PythonExe "C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\secret_scan.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\dependency_scan.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\sast_scan.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\generate_sbom.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\production_readiness_check.ps1 -TemplateMode -SkipDockerCompose
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase3_analytics_check.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\local.ps1 -Action test -PythonExe "C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -TimeoutSeconds 180
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\build_phase_zero_release.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\release_phase_zero_check.ps1 -Root "C:\Users\nunas\Documents\Codex\2026-06-18\files-mentioned-by-the-user-nexus\tmp\phase-zero-release\src-20260623-080447"
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase_zero_audit.ps1 -Root "C:\Users\nunas\Documents\Codex\2026-06-18\files-mentioned-by-the-user-nexus\tmp\phase-zero-release\src-20260623-080447"
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase4_scientific_validation_check.ps1 -Root "C:\Users\nunas\Documents\Codex\2026-06-18\files-mentioned-by-the-user-nexus\tmp\phase-zero-release\src-20260623-080447" -PythonExe "C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
```

Gate results:

- Dataset/validation generation: `status=ok`, F1 `1.0`, FP rate `0.0`,
  FN rate `0.0`.
- Compileall: passed.
- SUPREME backend tests: `23 passed`.
- SENTINELA tests: `15 passed`.
- `phase4_scientific_validation_check.ps1`: `Resumo Fase 4: 0 falha(s)`.
- `secret_scan.ps1`: `0 critical finding(s)`.
- `dependency_scan.ps1`: `0 critical finding(s)`.
- `sast_scan.ps1`: `0 critical finding(s)`.
- `generate_sbom.ps1`: SBOM generated.
- `production_readiness_check.ps1 -TemplateMode -SkipDockerCompose`:
  `Resumo: 0 falha(s), 0 aviso(s)`.
- `phase3_analytics_check.ps1`: `Resumo Fase 3: 0 falha(s)`.
- Local E2E: `status=ok`, `events_raw=8`, `events_stored_http=8`,
  `redis_rq_analytics_observed=true`, `pipeline_status=ok`, `ieo_logs=4`,
  `sentinela_ieo_windows=4`, `id_hash=phase1-e2e-1782212788`.
- Clean staging release gate:
  `release_phase_zero_check.ps1` returned `Resumo: 0 falha(s)`.
- Clean staging Phase 0 audit:
  `phase_zero_audit.ps1` returned `Resumo Fase 0: 0 falha(s), 0 aviso(s)`.
- Clean staging Phase 4 gate:
  `phase4_scientific_validation_check.ps1` returned
  `Resumo Fase 4: 0 falha(s)`.
- Final clean release ZIP:
  `C:\Users\nunas\Documents\Codex\2026-06-18\files-mentioned-by-the-user-nexus\outputs\supreme-v4-phase-zero-100-20260623-080745.zip`.
- Final clean staging path:
  `C:\Users\nunas\Documents\Codex\2026-06-18\files-mentioned-by-the-user-nexus\tmp\phase-zero-release\src-20260623-080745`.

Operational notes:

- An initial `release_phase_zero_check.ps1 -Root .` run failed because it was
  intentionally pointed at the local development root, which contains `.env`,
  local certificates, IPED-local and backups. That root is not a clean release
  package. The applicable gate was rerun on clean staging and passed with zero
  failures.
- `scripts/build_phase_zero_release.ps1` was hardened to ignore inaccessible
  generated test caches during release staging.
- Pytest reported a cache-write warning on `.pytest_cache` due host file
  permissions. This did not affect test execution or results.
- External independent scientific/statistical validation is explicitly not
  claimed as complete in Phase 4. It remains a later external audit/publication
  activity, not a blocker for this internal synthetic validation phase.

Decision: PHASE 4 COMPLETE. DO NOT ADVANCE TO PHASE 5 WITHOUT USER CONFIRMATION.

## Phase 5 - Cadeia de Custodia e Auditoria Forense

Status: 100_PERCENT_COMPLETE

Criteria:

- Events are signed at the first trusted SUPREME capture point.
- Input, processing, output and administrative audit records use verifiable hash
  chains.
- IPED, patch, proxy, watcher, SUPREME, SENTINELA and algorithm versions are
  registered in a session manifest.
- A deterministic pipeline replay reconstructs outputs from signed payloads.
- An integrity report records input, processing, output, versions and hashes.
- Administrative changes are represented in a chained audit log fixture.
- A forensic export can be independently verified.
- Simulated IPED evidence is covered end-to-end; real IPED execution is
  explicitly separated and remains dependent on an authorized IPED workstation
  when available.
- Verifiers fail if signature, hash chain, manifest, version or replay diverges.
- Clean release/staging gates confirm no secrets, local IPED artifacts or real
  sensitive data are shipped.

Evidence captured on 2026-06-23:

- Preconditions checked first: Phase 0, Phase 1, Phase 2, Phase 3 and Phase 4
  were all `100_PERCENT_COMPLETE`.
- Phase 5 started from `NOT_STARTED`.
- Forensic module:
  `supreme-backend/src/engine/supreme/forensic.py`.
- Forensic generator/verifier:
  `scripts/phase5_forensic_custody.py`.
- Phase 5 gate:
  `scripts/phase5_forensic_custody_check.ps1`.
- Automated tests:
  `supreme-backend/tests/test_phase5_forensic_custody.py`.
- CI runs `scripts/phase5_forensic_custody_check.ps1`.
- Documentation:
  `docs/PHASE_FIVE_FORENSIC_CUSTODY.md`.
- Generated forensic artifacts:
  `docs/phase5_forensic/signed_events.jsonl`,
  `docs/phase5_forensic/input_hash_chain.json`,
  `docs/phase5_forensic/processing_hash_chain.json`,
  `docs/phase5_forensic/output_hash_chain.json`,
  `docs/phase5_forensic/admin_audit_log.jsonl`,
  `docs/phase5_forensic/session_manifest.json`,
  `docs/phase5_forensic/integrity_report.json`,
  `docs/phase5_forensic/forensic_export.json`.
- Manifest hash:
  `7a7abc1ccd94281c1f49b8040611bcbcde590335d3ad7b52a97383986b6bdaef`.
- Export hash:
  `c69dabecbafb68619021b4086e2f21037da847dd63ff24f560edb50708fd9fe4`.
- Input chain tip:
  `ef62b4f9e76024ac4f9ceec4dc3f32ac716fe11a0e6821bd5d8839b136a56ac7`.
- Processing chain tip:
  `b2f3ccb8b61b3393438e0849642c0d08606138c50e42dc4e4d4d785b432b66ff`.
- Output chain tip:
  `bed9ce4c36bd00de0c85140ff6f9500b6dfc3bcd5d09500414d01b08b857bfe8`.
- Admin audit chain tip:
  `be18c20f8498950e3563e7fad4a881a3f2138acf025690138f60a23500f8d893`.
- Replay digest:
  `d2ab408079987d2b1cb9d5e8a7ce1152332ee22dd0ee6932153ab3bd8fce01de`.
- Signed events: `8`; deterministic outputs: `4`.
- Evidence mode: `simulated_iped`; `real_iped_available=false` because no
  authorized real IPED workstation/session was provided in this Codex
  environment.
- Final clean release ZIP:
  `C:\Users\nunas\Documents\Codex\2026-06-18\files-mentioned-by-the-user-nexus\outputs\supreme-v4-phase-zero-100-20260623-082405.zip`.
- Final clean staging path:
  `C:\Users\nunas\Documents\Codex\2026-06-18\files-mentioned-by-the-user-nexus\tmp\phase-zero-release\src-20260623-082405`.

Commands executed:

```powershell
C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts\phase5_forensic_custody.py all
C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m compileall -q sentinela\src supreme-backend\src scripts\phase5_forensic_custody.py
$env:PYTHONPATH='.'; C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest -q tests   # in supreme-backend
$env:PYTHONPATH='.'; C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest -q tests   # in sentinela
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase5_forensic_custody_check.ps1 -Root . -PythonExe "C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\secret_scan.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\dependency_scan.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\sast_scan.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\generate_sbom.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\production_readiness_check.ps1 -TemplateMode -SkipDockerCompose
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase4_scientific_validation_check.ps1 -Root . -PythonExe "C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase3_analytics_check.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\local.ps1 -Action test -PythonExe "C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -TimeoutSeconds 180
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\build_phase_zero_release.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\release_phase_zero_check.ps1 -Root "C:\Users\nunas\Documents\Codex\2026-06-18\files-mentioned-by-the-user-nexus\tmp\phase-zero-release\src-20260623-082405"
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase_zero_audit.ps1 -Root "C:\Users\nunas\Documents\Codex\2026-06-18\files-mentioned-by-the-user-nexus\tmp\phase-zero-release\src-20260623-082405"
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\nunas\Documents\Codex\2026-06-18\files-mentioned-by-the-user-nexus\tmp\phase-zero-release\src-20260623-082405\scripts\phase5_forensic_custody_check.ps1" -Root "C:\Users\nunas\Documents\Codex\2026-06-18\files-mentioned-by-the-user-nexus\tmp\phase-zero-release\src-20260623-082405" -PythonExe "C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\nunas\Documents\Codex\2026-06-18\files-mentioned-by-the-user-nexus\tmp\phase-zero-release\src-20260623-082405\scripts\secret_scan.ps1" -Root "C:\Users\nunas\Documents\Codex\2026-06-18\files-mentioned-by-the-user-nexus\tmp\phase-zero-release\src-20260623-082405"
```

Gate results:

- Forensic artifact generation/check: `status=ok`, signed events `8`.
- Compileall: passed.
- SUPREME backend tests: `29 passed`.
- SENTINELA tests: `15 passed`.
- `phase5_forensic_custody_check.ps1`: `Resumo Fase 5: 0 falha(s)`.
- `secret_scan.ps1`: `0 critical finding(s)`.
- `dependency_scan.ps1`: `0 critical finding(s)`.
- `sast_scan.ps1`: `0 critical finding(s)`.
- `generate_sbom.ps1`: SBOM generated.
- `production_readiness_check.ps1 -TemplateMode -SkipDockerCompose`:
  `Resumo: 0 falha(s), 0 aviso(s)`.
- `phase4_scientific_validation_check.ps1`: `Resumo Fase 4: 0 falha(s)`.
- `phase3_analytics_check.ps1`: `Resumo Fase 3: 0 falha(s)`.
- Local E2E: `status=ok`, `events_raw=8`, `events_stored_http=8`,
  `redis_rq_analytics_observed=true`, `pipeline_status=ok`, `ieo_logs=4`,
  `sentinela_ieo_windows=4`, `id_hash=phase1-e2e-1782213614`.
- Clean staging release gate:
  `release_phase_zero_check.ps1` returned `Resumo: 0 falha(s)`.
- Clean staging Phase 0 audit:
  `phase_zero_audit.ps1` returned `Resumo Fase 0: 0 falha(s), 0 aviso(s)`.
- Clean staging Phase 5 gate:
  `phase5_forensic_custody_check.ps1` returned `Resumo Fase 5: 0 falha(s)`.
- Clean staging secret scan:
  `0 critical finding(s)`.

Operational notes:

- Real IPED evidence is not claimed as executed in this Codex environment. The
  implementation covers the simulated IPED evidence flow and provides manifest
  fields and acceptance scripts for an authorized real IPED workstation when
  available.
- A real IPED acceptance attempt was performed before Phase 6 on 2026-06-23.
  It is recorded in `docs/PHASE_FIVE_REAL_IPED_TEST_20260623.md`.
  Result: real IPED opened, but no `supreme_audit.ndjson` was generated and no
  new `events_raw.source_tool='iped'` row reached SUPREME. The blocker is
  source-level IPED instrumentation: `supreme-audit-patch.jar` is present, but
  the running IPED UI does not call `SupremeAuditLogger`.
- Pytest reported a cache-write warning on `.pytest_cache` due host file
  permissions. This did not affect test execution or results.

Decision: PHASE 5 SIMULATED FORENSIC CUSTODY COMPLETE. REAL IPED ACCEPTANCE IS
BLOCKED BEFORE PHASE 6. DO NOT ADVANCE TO PHASE 6 UNTIL THE IPED INSTRUMENTATION
BLOCKER IS FIXED AND `scripts\accept_iped_real_session.ps1` PASSES.

## Phase 6 - SENTINELA Produto

Status: 100_PERCENT_COMPLETE

Criteria:

- SENTINELA UX is reorganized by role: gestor/pesquisador/auditor/operador
  mapped to the current canonical roles.
- Interface is cleaner and role-oriented, with professional empty states.
- Backend signed HTML/PDF reports exist.
- Studies/cases screen exists.
- Participants screen exists with permission and scope enforcement.
- Pipeline health panel exists.
- Data quality panel exists.
- Scientific export supports CSV, JSON, Parquet and data dictionary.
- Dashboard does not calculate critical rules.
- Outputs include algorithm version, parameters and signatures/hashes where
  applicable.
- Scope segregation covers institution, study, case and participant.
- Real study operation depends on real IPED -> SUPREME auditable outputs.

Evidence captured on 2026-06-23:

- Phase 6 implementation report:
  `docs/PHASE_SIX_SENTINELA_PRODUCT_EXECUTION.md`.
- Product API:
  `sentinela/src/app/api/product.py`.
- Export API:
  `sentinela/src/app/api/export.py`.
- RBAC and scope filter:
  `sentinela/src/app/auth.py`.
- Front-end product sections:
  `sentinela/static/index.html`.
- Tests:
  `sentinela/tests/test_phase6_product.py`.
- Gate:
  `scripts/phase6_sentinela_product_check.ps1`.
- Real IPED acceptance:
  `docs/PHASE_FIVE_REAL_IPED_TEST_20260623.md`.
- Visual acceptance:
  browser validation on desktop `1280x720` and mobile `390x844`.

Commands executed:

```powershell
C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m compileall -q sentinela\src
$env:PYTHONPATH='.'; C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest -q tests
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase6_sentinela_product_check.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase3_analytics_check.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase5_forensic_custody_check.ps1 -Root . -PythonExe "C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\secret_scan.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\dependency_scan.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\sast_scan.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\generate_sbom.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\production_readiness_check.ps1 -TemplateMode -SkipDockerCompose
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\local.ps1 -Action test -PythonExe "C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -TimeoutSeconds 180
docker compose -f docker-compose.production.yml -f docker-compose.local.yml up -d --build sentinela
C:\maven\apache-maven-3.9.16\bin\mvn.cmd -pl iped-app -am -DskipTests package
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_iped_source_instrumentation.ps1 -IpedSourceRoot .\tmp\iped-src
```

Gate results:

- Compileall: passed.
- SENTINELA tests: `22 passed, 1 warning`.
- Phase 6 product gate: `0 failure(s), 0 blocker(s)`.
- Phase 3 analytics gate: `Resumo Fase 3: 0 falha(s)`.
- Phase 5 forensic gate: `Resumo Fase 5: 0 falha(s)`.
- Secret scan: `0 critical finding(s)`.
- Dependency scan: `0 critical finding(s)`.
- SAST scan: `0 critical finding(s)`.
- SBOM generated with `12 component(s)`.
- Production readiness template mode: `Resumo: 0 falha(s), 0 aviso(s)`.
- Local E2E after rebuilt SENTINELA container:
  `status=ok`, `events_raw=8`, `events_stored_http=8`,
  `redis_rq_analytics_observed=true`, `pipeline_status=ok`,
  `ieo_logs=4`, `sentinela_ieo_windows=4`,
  `id_hash=phase1-e2e-1782236286`.
- Real IPED audit log:
  `tmp\iped-audit\supreme_audit.ndjson` contains a processable `close`
  entry for item `1`, `Fonts/85f1255.fon`.
- SUPREME database:
  `1` recent `events_raw.source_tool='iped'` event confirmed by the Phase 6
  product gate.
- Visual desktop:
  `bodyScrollW == clientW`, last nav item fully visible, no collapsed text.
- Visual mobile `390x844`:
  `bodyScrollW == clientW`, first nav item fully visible, no collapsed text.

Decision: PHASE 6 COMPLETE. DO NOT ADVANCE TO PHASE 7 WITHOUT USER CONFIRMATION.

## Phase 7 - Producao Mundial

Status: 100_PERCENT_COMPLETE

Criteria:

- CI/CD runs readiness, release, security scans, SBOM, Phase 2-7 gates, tests,
  Docker builds and versioned image digest artifacts.
- Staging mirrors production with the production compose stack plus
  `docker-compose.staging.yml`, staging env templates and isolated volumes.
- Backup and restore are tested without destroying the active databases.
- Observability defines SLOs, burn-rate alerts and runbooks.
- Developer, researcher, auditor and operator documentation exists.
- External security and statistical/methodological audit packages exist.
- NIST CFTT-inspired benchmark is reproducible and records metrics.
- Whitepaper exists with limits and responsible-use boundaries.
- Production readiness rejects unsafe local/production configuration.
- Clean release ZIP is generated, extracted and tested in staging.
- SENTINELA remains viewer-only and outputs preserve algorithm metadata.
- Real IPED acceptance is recorded as approved before Phase 7.

Evidence captured on 2026-06-23:

- Preconditions checked first: Phase 0, Phase 1, Phase 2, Phase 3, Phase 4,
  Phase 5 and Phase 6 were all `100_PERCENT_COMPLETE`.
- CI/CD:
  `.github/workflows/ci.yml` runs readiness, release, Phase 2-7 gates, secret
  scan, dependency scan, SAST, SBOM, backend tests, SENTINELA tests, Docker
  builds and image digest artifact upload.
- Staging:
  `docker-compose.staging.yml`, `env/.env.staging.example`,
  `supreme-backend/.env.staging.example`, `sentinela/.env.staging.example`.
- SLO and runbooks:
  `docs/SLO_OBSERVABILITY.md`, `infra/prometheus/alert_rules.yml`,
  `docs/runbooks/*.md`.
- Backup/restore:
  `scripts/phase7_backup_restore_check.ps1` restored SUPREME and SENTINELA
  dumps into temporary databases and dropped them after verification.
- Audit packages:
  `docs/audit/SECURITY_EXTERNAL_AUDIT_PACKAGE.md`,
  `docs/audit/STATISTICAL_METHODOLOGICAL_AUDIT_PACKAGE.md`.
- Role docs:
  `docs/roles/DEVELOPER.md`, `docs/roles/RESEARCHER.md`,
  `docs/roles/AUDITOR.md`, `docs/roles/OPERATOR.md`.
- Benchmark:
  `scripts/phase7_nist_cftt_benchmark.py`,
  `docs/phase7_benchmark/benchmark_report.json`.
- Whitepaper:
  `docs/WHITEPAPER_SUPREME_V4.md`.
- Release provenance:
  `reports/phase7/release_provenance.json`.
- Final clean release ZIP:
  generated by `scripts\build_phase7_world_release.ps1` under the workspace
  `outputs` directory with prefix `supreme-v4-phase-seven-world-production`.
- Final extracted staging:
  generated from the release ZIP under the workspace `tmp\phase7-release`
  directory before final gates.

Metrics and hashes:

- Phase 7 benchmark: `status=ok`, F1 `1.0`, false positive rate `0.0`,
  false negative rate `0.0`.
- Dataset digest:
  `845ef619dc74bc5fa30475a89e96ab044412ae3c6bf84370498cd37f728f17a3`.
- Forensic export hash:
  `c69dabecbafb68619021b4086e2f21037da847dd63ff24f560edb50708fd9fe4`.
- Backup/restore manifest:
  `.\backups\phase7\phase7_backup_restore_20260623T175657Z.json`.
- SUPREME backup SHA256:
  `52bb94e88839d9efac239c512aa4c3f25fc4b4ed8102c4ad21c21ae09e65a0f9`.
- SENTINELA backup SHA256:
  `f94e3b00ba883f57217184dec276b831aab43d6147c2cd74187be2664e93866b`.
- Local E2E id:
  `phase1-e2e-1782237583`.

Commands executed:

```powershell
C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts\phase4_scientific_validation.py all
C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts\phase7_nist_cftt_benchmark.py --root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase7_release_provenance.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase7_observability_slo_check.ps1 -Root .
docker compose --env-file env\.env.staging.example -f docker-compose.production.yml -f docker-compose.staging.yml config --quiet
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase7_backup_restore_check.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase7_world_production_check.ps1 -Root . -PythonExe "C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m compileall -q sentinela\src supreme-backend\src scripts\phase7_nist_cftt_benchmark.py
$env:PYTHONPATH='.'; C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest -q tests   # in supreme-backend
$env:PYTHONPATH='.'; C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest -q tests   # in sentinela
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase2_security_check.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase3_analytics_check.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase4_scientific_validation_check.ps1 -Root . -PythonExe "C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase5_forensic_custody_check.ps1 -Root . -PythonExe "C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase6_sentinela_product_check.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\production_readiness_check.ps1 -TemplateMode -SkipDockerCompose
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\production_readiness_check.ps1 -LocalMode -SkipDockerCompose
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\secret_scan.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\dependency_scan.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\sast_scan.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\generate_sbom.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\local.ps1 -Action test -PythonExe "C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -TimeoutSeconds 180
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\build_phase7_world_release.ps1 -Root . -PythonExe "C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\release_phase_zero_check.ps1 -Root "<extracted-phase7-release>"
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase_zero_audit.ps1 -Root "<extracted-phase7-release>"
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase7_world_production_check.ps1 -Root "<extracted-phase7-release>" -PythonExe "C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\secret_scan.ps1 -Root "<extracted-phase7-release>"
```

Gate results:

- Compileall: passed.
- SUPREME backend tests: `29 passed, 1 warning`.
- SENTINELA tests: `22 passed, 1 warning`.
- Phase 2 security gate: `0 falha(s)`.
- Phase 3 analytics gate: `Resumo Fase 3: 0 falha(s)`.
- Phase 4 scientific validation gate: `Resumo Fase 4: 0 falha(s)`.
- Phase 5 forensic custody gate: `Resumo Fase 5: 0 falha(s)`.
- Phase 6 product gate: `0 failure(s), 0 blocker(s)`.
- Phase 7 SLO gate: `Resumo Fase 7 SLO: 0 falha(s)`.
- Phase 7 world production gate: `Resumo Fase 7: 0 falha(s)`.
- Staging compose config: passed.
- Backup/restore: `status=ok`, both restores used temporary databases.
- Production readiness template mode: `Resumo: 0 falha(s), 0 aviso(s)`.
- Production readiness local mode: `Resumo: 0 falha(s), 0 aviso(s)`.
- Secret scan: `0 critical finding(s)`.
- Dependency scan: `0 critical finding(s)`.
- SAST scan: `0 critical finding(s)`.
- SBOM: generated with `12 component(s)`.
- Local E2E:
  `status=ok`, `events_raw=8`, `events_stored_http=8`,
  `redis_rq_analytics_observed=true`, `pipeline_status=ok`, `ieo_logs=4`,
  `sentinela_ieo_windows=4`, `id_hash=phase1-e2e-1782237583`.
- Extracted ZIP release gate:
  `Resumo: 0 falha(s)`.
- Extracted ZIP Phase 0 audit:
  `Resumo Fase 0: 0 falha(s), 0 aviso(s)`.
- Extracted ZIP Phase 7 gate:
  `Resumo Fase 7: 0 falha(s)`.
- Extracted ZIP secret scan:
  `0 critical finding(s)`.

Operational notes:

- External security audit, external statistical/methodological audit and NIST
  certification are not claimed as completed. Phase 7 prepares the packages and
  evidence required for those third-party activities.
- Docker access in this Codex desktop environment required escalated host
  execution for compose, backup/restore and E2E commands.
- Pytest cache warnings were host permission warnings and did not affect test
  execution.

Decision: PHASE 7 COMPLETE. NO LATER PHASE WAS STARTED.

## Phase 8 - Field Forensic Architecture

Status: BLOCKED_PRODUCTION_PREREQUISITES.

Decision: PHASE 8 NOT 100_PERCENT_COMPLETE. No later phase was started.

Scope executed:

- Confirmed Phase 0 through Phase 7 are recorded as `100_PERCENT_COMPLETE`.
- Read the official local IPED source and confirmed the usable extension path:
  `plugins` classpath, `conf/ResultSetViewersConf.xml`,
  `iped.viewers.api.ResultSetViewer`, `PluginConfig.getPluginJars()` and
  bootstrap plugin loading.
- Created `supreme-iped-plugin` as the non-patch path. The plugin implements
  `ResultSetViewer`, observes table selection/model changes and emits
  privacy-minimized NDJSON events with event hash/hash chain fields.
- Created build, verification and installation scripts for the plugin.
- Created `supreme-agent-windows` with encrypted persistent queue, HMAC signed
  envelopes, hash-chain validation, central ingest mapping, retry/backoff,
  scoped device credential helpers and deterministic psychometric journey:
  `SRQ20/DASS21/OLBI -> IPED -> PANAS_SHORT`.
- Generated a clean evidence ZIP and validated it in extracted staging.

Artifacts:

- Plugin JAR:
  `supreme-iped-plugin/dist/supreme-iped-plugin.jar`
- Plugin manifest:
  `supreme-iped-plugin/dist/supreme-iped-plugin-manifest.json`
- Plugin SHA-256:
  `8fb5d2686d220564fa3c5a3bb204bb6a30a988b775508b8ad6e1d6c94243d07c`
- Clean evidence ZIP:
  `C:\Users\nunas\Documents\Codex\2026-06-18\files-mentioned-by-the-user-nexus\outputs\supreme-v4-phase8-field-forensic-blocked-20260623-183926.zip`
- Clean evidence ZIP SHA-256:
  `8547746A0220F1BA19A2B22054851A0C5165389422DE0A4C5901486918D0A8B4`
- Field replay report:
  `reports/phase8/field_replay_report.json`
- Field replay final chain hash:
  `772c6174c9f11866a796beb56f01374c02addb5e974591f149b157bfd7306e76`
- Field replay output hash:
  `163a2d4dc91c8fe222604dd9d4013c35f31b564850329cf16eb623ad0c1bf725`

Commands executed:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\build_supreme_iped_plugin.ps1 -Root . -Javac "C:\Program Files\BellSoft\LibericaJDK-11-Full\bin\javac.exe"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify_supreme_iped_plugin.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test_phase8_plugin_install.ps1 -Root .
$env:PYTHONPATH='supreme-agent-windows'; C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest -q supreme-agent-windows\tests
C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m compileall -q supreme-agent-windows\supreme_agent scripts\phase8_field_forensic_replay.py
C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts\phase8_field_forensic_replay.py --root .
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\phase8_field_forensic_architecture_check.ps1 -Root . -PythonExe "C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\phase8_field_forensic_architecture_check.ps1 -Root . -PythonExe "C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -RequireProductionPrereqs
$env:PYTHONPATH='.'; C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest -q tests   # in supreme-backend
$env:PYTHONPATH='.'; C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest -q tests   # in sentinela
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\production_readiness_check.ps1 -TemplateMode -SkipDockerCompose
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\production_readiness_check.ps1 -LocalMode -SkipDockerCompose
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\secret_scan.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\dependency_scan.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\sast_scan.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\generate_sbom.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\build_phase_zero_release.ps1 -Root . -OutputDir ..\..\outputs -WorkDir ..\..\tmp\phase8-release -NamePrefix "supreme-v4-phase8-field-forensic-blocked"
powershell -NoProfile -ExecutionPolicy Bypass -File "<extracted-phase8-release>\scripts\release_phase_zero_check.ps1" -Root "<extracted-phase8-release>"
powershell -NoProfile -ExecutionPolicy Bypass -File "<extracted-phase8-release>\scripts\secret_scan.ps1" -Root "<extracted-phase8-release>"
powershell -NoProfile -ExecutionPolicy Bypass -File "<extracted-phase8-release>\scripts\phase8_field_forensic_architecture_check.ps1" -Root "<extracted-phase8-release>" -PythonExe "C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
```

Gate results:

- Plugin build: passed outside sandbox; JAR generated.
- Plugin verification: `0 falha(s)`.
- Plugin install test against temporary IPED config: passed.
- Agent tests: `7 passed, 1 warning`.
- SUPREME backend tests: `29 passed, 1 warning`.
- SENTINELA tests: `22 passed, 1 warning`.
- Production readiness template mode: `0 falha(s), 0 aviso(s)`.
- Production readiness local mode: `0 falha(s), 0 aviso(s)`.
- Secret scan: `0 critical finding(s)`.
- Dependency scan: `0 critical finding(s)`.
- SAST scan: `0 critical finding(s)`.
- SBOM: generated with `12 component(s)`.
- Phase 8 architecture gate without production prereqs:
  `0 falha(s), 1 bloqueio(s)`.
- Phase 8 architecture gate with production prereqs:
  `0 falha(s), 3 bloqueio(s)`.
- Extracted ZIP release check:
  `Resumo: 0 falha(s)`.
- Extracted ZIP secret scan:
  `0 critical finding(s)`.
- Extracted ZIP Phase 8 architecture gate:
  `0 falha(s), 1 bloqueio(s)`.

Blocking production prerequisites:

- No real code-signing certificate/keystore was supplied. The plugin manifest is
  `signing_mode=unsigned-dev`; production requires `jarsigner` or an equivalent
  trusted signing process.
- No real external SUPREME/SENTINELA domain/TLS endpoint was supplied.
- No central production device-pairing authority and revocation store was
  provisioned.

Important limitation:

- The existing central `/v1/events/ingest` endpoint accepts behavioral event
  types (`file_open`, `image_view`, `video_play`, `classification_event`).
  Field lifecycle events (`session_start`, `session_end`, `item_close`) are
  preserved in the plugin/agent custody path and replay evidence, but require a
  native central field-session endpoint before full production certification.
