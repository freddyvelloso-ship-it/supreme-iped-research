# SUPREME V4 - Phase 6 SENTINELA Product Execution

Status: 100_PERCENT_COMPLETE

This document records the final Phase 6 acceptance for SENTINELA as a product
surface. Phase 6 is complete after real IPED source instrumentation, rebuilt
SENTINELA container validation, visual desktop/mobile checks and regression
gates.

## Implemented

- Role-oriented workspaces for `master`, `pesquisador`, `auditor`, `operador`
  and `leitura_agregada`.
- Product RBAC permissions:
  `product:studies`, `product:participants`, `product:pipeline`,
  `product:data_quality` and `report:signed`.
- Scope filtering by participant, institution, study and case through
  `participant_registry`.
- Backend product endpoints:
  - `GET /api/product/workspace`
  - `GET /api/product/studies`
  - `GET /api/product/participants`
  - `GET /api/product/pipeline-health`
  - `GET /api/product/data-quality`
  - `GET /api/product/report/html`
  - `GET /api/product/report/pdf`
- Signed backend report headers:
  `X-SENTINELA-Report-Digest` and `X-SENTINELA-Report-Signature`.
- Scientific exports:
  - `GET /api/export/csv`
  - `GET /api/export/json`
  - `GET /api/export/parquet`
  - `GET /api/export/data-dictionary`
- Export signature headers:
  `X-SENTINELA-Export-Digest` and `X-SENTINELA-Export-Signature`.
- Front-end sections:
  `Estudos`, `Pipeline`, `Qualidade` and `Exportacao`.
- Direct-local and reverse-proxy API prefix compatibility:
  direct `http://localhost:18001/` uses no prefix; proxied
  `/sentinela/` uses `/sentinela`.
- SENTINELA remains viewer-only and does not call critical analytical
  calculation functions.
- Desktop/mobile navigation layout was hardened after visual validation.

## Real IPED Acceptance

- Official IPED source in `tmp/iped-src` was instrumented and rebuilt as
  `iped-4.4.0-SNAPSHOT`.
- `ResultTableListener.java`, `ResultTableModel.java` and
  `UICaseDataLoader.java` contain SUPREME audit hooks.
- Real case path used: `C:\iped-test-case`.
- Real audit log created:
  `tmp\iped-audit\supreme_audit.ndjson`.
- Processable real IPED line exists with `event=close`, item `1`, name
  `85f1255.fon`, path `Fonts/85f1255.fon`.
- SUPREME database recorded a recent `events_raw.source_tool='iped'` event.

## Visual Acceptance

- Desktop authenticated viewport:
  - `bodyScrollW == clientW`.
  - Last nav item `📋 Relatório` fully visible at 1280px.
  - No visible text element collapsed below minimum readable bounds.
- Mobile authenticated viewport `390x844`:
  - `bodyScrollW == clientW`.
  - First nav item `Visão Geral` fully visible.
  - Header metadata wraps without creating horizontal page overflow.
  - No visible text element collapsed below minimum readable bounds.

## Commands Run

```powershell
C:\maven\apache-maven-3.9.16\bin\mvn.cmd -pl iped-app -am -DskipTests package
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_iped_source_instrumentation.ps1 -IpedSourceRoot .\tmp\iped-src
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase6_sentinela_product_check.ps1 -Root .
$env:PYTHONPATH='.'; C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest -q tests
docker compose -f docker-compose.production.yml -f docker-compose.local.yml up -d --build sentinela
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\local.ps1 -Action test -PythonExe "C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -TimeoutSeconds 180
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase3_analytics_check.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase5_forensic_custody_check.ps1 -Root . -PythonExe "C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\secret_scan.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\dependency_scan.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\sast_scan.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\generate_sbom.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\production_readiness_check.ps1 -TemplateMode -SkipDockerCompose
```

## Results

- IPED source instrumentation gate: `0 failure(s)`.
- SENTINELA tests: `22 passed, 1 warning`.
- Phase 6 product gate: `0 failure(s), 0 blocker(s)`.
- Local E2E:
  `status=ok`, `events_raw=8`, `events_stored_http=8`,
  `redis_rq_analytics_observed=true`, `pipeline_status=ok`, `ieo_logs=4`,
  `sentinela_ieo_windows=4`, `id_hash=phase1-e2e-1782236286`.
- Phase 3 analytics gate: `Resumo Fase 3: 0 falha(s)`.
- Phase 5 forensic gate: `Resumo Fase 5: 0 falha(s)`.
- Secret scan: `0 critical finding(s)`.
- Dependency scan: `0 critical finding(s)`.
- SAST scan: `0 critical finding(s)`.
- SBOM: generated with `12 component(s)`.
- Production readiness template mode: `Resumo: 0 falha(s), 0 aviso(s)`.

## Decision

PHASE 6 COMPLETE.

Do not start Phase 7 without explicit user confirmation.
