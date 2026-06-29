# SUPREME-IPED Research Full System Production Health Audit

Date: 2026-06-29

Branch: `codex/full-system-production-health-audit`

Base branch: `codex/restore-sentinela-lab-ui`

Related PR stack:

- `codex/system-health-publication-audit`
- `codex/restore-sentinela-lab-ui`
- `codex/full-system-production-health-audit`

## Decision

`healthy_for_publication`

The source tree is healthy for controlled publication after this branch is merged. Phase Zero was validated from a clean clone and passed. The local development workstation still contains ignored release-blocking artifacts (`.env`, production env files, TLS certificates, `IPED-local`, and `tmp/pytest`), so final release packaging must be run from a clean clone or after removing those ignored local artifacts from the working copy.

## Bugs Found

- Sentinela login state could leave `#login-screen` visible or restorable after authentication.
- Sentinela navigation could load sections without a confirmed authenticated session.
- The lab UI layer was rendered, but old layout rules still controlled the authenticated shell.
- The `nav` lived inside the legacy `header`; the header grew to nearly a full viewport and pushed `Visao Geral` down.
- The top context strip wrapped vertically and made the header too tall.
- `IPED-local` was tracked by Git even though IPED must be a local/external dependency.
- Root `ruff check .` exposed lint debt outside the backend-only check.
- IPED integration pytest used the default Windows temp root, which was permission-blocked on this workstation.

## Bugs Fixed

- Added explicit authenticated/login shell functions in `sentinela/static/index.html`.
- Guarded navigation, section loading, refresh timer, and locale refresh behind authenticated session state.
- Ensured logout returns to login and restore-session failure does not leave a hybrid shell.
- Made Sentinela lab UI the dominant authenticated layer.
- Changed the lab shell layout so `header`, `nav`, and `main` no longer fight the old page flow.
- Made the header use `display: contents` in the lab layer and positioned `header-top`, `nav`, and `main` in the app grid.
- Prevented the context strip from wrapping vertically.
- Added regression tests for login shell state, lab UI dominance, menu flow, and no old KPI layer visibility.
- Removed `IPED-local` from Git tracking while keeping local files on disk.
- Updated `.gitignore` so `IPED-local/` remains local and ignored.
- Fixed root ruff findings in scientific validation scripts, forensic custody script, Sentinela dashboard API, proxy, and integration tests.

## Architecture Decisions

- IPED is treated as an external/local dependency, not repository content.
- `IPED-local/` is ignored and must not be committed.
- Sentinela authenticated UI now has a single dominant lab visual layer.
- The legacy UI can remain as compatibility markup, but executable/visible control must stay with the lab layer.
- Local release gates that scan the full filesystem tree must be run from a clean checkout for final packaging.

## Validation Executed

### Backend

- `C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m ruff check src tests`
  - Result: passed.
- `C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest -q`
  - Directory: `supreme-backend`
  - Result: `40 passed`.
- `docker build -t supreme-backend:ci .`
  - Directory: `supreme-backend`
  - Result: passed.

### Sentinela

- `C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest -q`
  - Directory: `sentinela`
  - Result: `31 passed`, one upstream deprecation warning from `python-jose`.
- `docker build -t sentinela:ci .`
  - Directory: `sentinela`
  - Result: passed.

### Root / Integration

- `C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest -q`
  - Directory: repository root
  - Result: `8 passed`.
- `C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m ruff check .`
  - Result: passed.
- `C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest -q --basetemp tmp\pytest\supreme-iped-integration-health`
  - Directory: `supreme-iped-integration`
  - Result: `46 passed`.
- `node --check sentinela/static/sentinela-ux.js`
  - Result: passed.
- `node --check scripts/iped_journey_gate.mjs`
  - Result: passed.
- `git diff --check`
  - Result: passed, with line-ending warnings only.

### Gates

- `scripts\production_readiness_check.ps1 -TemplateMode -SkipDockerCompose`
  - Result: passed.
- `scripts\phase2_security_check.ps1 -Root .`
  - Result: passed.
- `scripts\phase3_analytics_check.ps1 -Root .`
  - Result: passed.
- `scripts\phase4_scientific_validation_check.ps1 -Root .`
  - Result: passed.
- `scripts\phase5_forensic_custody_check.ps1 -Root .`
  - Result: passed.
- `scripts\phase6_sentinela_product_check.ps1 -Root .`
  - Result: passed with one expected publication-control blocker: real IPED audit evidence was not present locally.
- `scripts\phase7_observability_slo_check.ps1 -Root .`
  - Result: passed.
- `scripts\phase7_world_production_check.ps1 -Root . -SkipDockerChecks`
  - Result: passed.
- `scripts\secret_scan.ps1 -Root .`
  - Result: `0 critical finding(s)`.
- `scripts\dependency_scan.ps1 -Root .`
  - Result: `0 critical finding(s)`.
- `scripts\sast_scan.ps1 -Root .`
  - Result: `0 critical finding(s)`.
- `scripts\generate_sbom.ps1 -Root .`
  - Result: SBOM generated.

### Phase 0 Release Gate

- `scripts\release_phase_zero_check.ps1`
  - Result: failed in this local working copy because ignored local artifacts are present:
    - `.env`
    - `supreme-backend/.env.production`
    - `sentinela/.env.production`
    - `certs/fullchain.pem`
    - `certs/privkey.pem`
    - `infra/prometheus/supreme-api-token.local`
    - `infra/alertmanager/alertmanager.yml`
    - `IPED-local`
    - `tmp/pytest`
  - Git verification:
    - env/cert/tmp files are not tracked.
    - `IPED-local` was tracked before this audit and is removed from Git tracking in this branch.

### Clean Clone Release Validation

Clean clone path: `C:\Users\nunas\Documents\Codex\2026-06-27\co\release-clean-check\supreme-iped-research`

Validated branch: `codex/full-system-production-health-audit`

Validated commit: `b2c4a802ddc26ac000ffdee73d3b47ba9c27edc8`

Commands executed:

- `git clone https://github.com/freddyvelloso-ship-it/supreme-iped-research C:\Users\nunas\Documents\Codex\2026-06-27\co\release-clean-check\supreme-iped-research`
- `git checkout codex/full-system-production-health-audit`
- `git ls-files IPED-local`
- `git ls-files .env supreme-backend/.env.production sentinela/.env.production certs/fullchain.pem certs/privkey.pem tmp`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\release_phase_zero_check.ps1`
- `C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest -q`
- `C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m ruff check .`
- `git diff --check`

Results:

- `IPED-local` tracked files in clean clone: `0`.
- `.env`, production env files, certificates and `tmp` tracked files in clean clone: `0`.
- `release_phase_zero_check.ps1`: passed with `0 falha(s)`.
- Root pytest: passed with `8 passed`.
- Root ruff: passed.
- `git diff --check`: passed.

Conclusion:

The previous Phase Zero failure was caused by ignored local development artifacts on the workstation, not by tracked release content. The clean clone is ready for Phase Zero release packaging.

Decision: `phase_zero_release_ready`

## Manual / Local UI Validation

Validated against `http://localhost:18001/sentinela`.

Local credentials used:

- login: `local.master@supreme.local`
- password: local development credential

Observed state after fix:

- Login screen hidden after authenticated session restore.
- App shell visible as grid.
- Body classes: `sentinela-authenticated sentinela-lab-primary`.
- `Visao Geral` remains in the lab UI layer after navigation away and back.
- Old KPI layer remains hidden.
- Menu is visible, not clipped, and remains in the app grid.
- `#section-overview` starts below the header instead of being pushed below the viewport.

## Status By Area

Frontend Sentinela: healthy after lab shell fix.

Backend SUPREME: healthy.

IPED integration: healthy in automated tests when temp root is controlled with `--basetemp`; local IPED remains an external dependency.

Docker: backend and Sentinela images build successfully.

Security/sanitization: scans passed with zero critical findings.

Production gates: passed. Phase Zero also passes in a clean clone; local release-packaging blockers remain only in this workstation because ignored development artifacts are present on disk.

## Remaining Publication Notes

- Run final release packaging from a clean clone, not from a development checkout containing `.env`, certificates, `IPED-local`, or pytest temp artifacts.
- Keep IPED as a local/external dependency configured by environment or launcher, not as repository content.
- Real IPED evidence remains a field-validation requirement, not a source-code health blocker.
- No diagnosis, ranking, productivity scoring, or disciplinary recommendation was introduced.
