# SUPREME V4 - Fase 3 Motor Analitico Unico

Status: 100_PERCENT_COMPLETE em 2026-06-23.

## Objetivo

Eliminar duas verdades analiticas entre SUPREME e SENTINELA.

SUPREME passa a ser a unica fonte de calculo para:

- IEO.
- PSI.
- Red flags tipadas: `reatividade`, `dissonancia`, `cronicidade`.

SENTINELA recebe, persiste e visualiza outputs auditaveis. Ele nao recalcula regra critica.

## Versao do algoritmo

Versao ativa:

```text
SUPREME-ANALYTICS-1.0.0
```

Fonte de verdade:

- `supreme-backend/src/engine/supreme/algorithm.py`

Parametros versionados:

- pesos do IEO;
- parametros logisticos do IEO;
- pesos e thresholds do PSI;
- thresholds de red flags;
- janela minima de historico psicometrico.

Os outputs gravam `algorithm_version` e `algorithm_parameters`.

## Fronteira SUPREME / SENTINELA

SUPREME:

- calcula IEO no worker;
- calcula PSI no backend;
- recalcula red flags quando IEO e PSI estao disponiveis;
- persiste red flags em `analytic_red_flags`;
- envia IEO/PSI/red flags para SENTINELA com versao e parametros.

SENTINELA:

- recebe IEO/PSI em `/api/v1/ingest/ieo`;
- recebe red flags em `/api/v1/ingest/red-flags`;
- grava `algorithm_version` e `algorithm_parameters`;
- nao possui motor local de red flags;
- nao mantem formulas, limiares criticos ou recomendacoes clinicas no HTML/JS;
- dashboards e exports apenas exibem outputs vindos do SUPREME.

## Banco

SUPREME:

- `psi_scores.algorithm_version`
- `psi_scores.algorithm_parameters`
- `analytic_red_flags`
- `algorithm_registry`

SENTINELA:

- `ieo_windows.algorithm_version`
- `ieo_windows.algorithm_parameters`
- `red_flags.algorithm_version`
- `red_flags.algorithm_parameters`

## Validacao local

Compilacao:

```powershell
$env:PYTHON_EXE="C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
& $env:PYTHON_EXE -m py_compile supreme-backend/src/engine/supreme/algorithm.py supreme-backend/src/engine/supreme/red_flags.py supreme-backend/src/engine/supreme/ieo.py supreme-backend/src/engine/supreme/psi.py supreme-backend/src/worker/pipeline.py supreme-backend/src/app/db.py supreme-backend/src/app/api/psychometric.py supreme-backend/src/engine/supreme/sentinela_push.py sentinela/src/app/api/ingest.py
```

Testes matematicos:

```powershell
$env:PYTHONPATH=(Resolve-Path "supreme-backend").Path
& $env:PYTHON_EXE -c "import importlib; mods=['tests.test_unified_ieo_math','tests.test_unified_psi_math','tests.test_unified_red_flags_math']; [getattr(importlib.import_module(m), name)() for m in mods for name in dir(importlib.import_module(m)) if name.startswith('test_')]; print('phase3 math tests ok')"
```

Varredura arquitetural:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase3_analytics_check.ps1 -Root .
```

Resultado esperado: `Resumo Fase 3: 0 falha(s)`.

Health/E2E local:

```powershell
$env:PYTHON_EXE="C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\local.ps1 -Action test -PythonExe $env:PYTHON_EXE -TimeoutSeconds 180
```

## Evidencias capturadas

- SUPREME tests: `20 passed`.
- SENTINELA tests: `15 passed`.
- `scripts/phase3_analytics_check.ps1`: `Resumo Fase 3: 0 falha(s)`.
- `scripts/production_readiness_check.ps1 -TemplateMode -SkipDockerCompose`:
  `Resumo: 0 falha(s), 0 aviso(s)`.
- `scripts/phase2_security_check.ps1`: `Resumo Fase 2 security check: 0 falha(s)`.
- `scripts/secret_scan.ps1`: `0 critical finding(s)`.
- `scripts/dependency_scan.ps1`: `0 critical finding(s)`.
- `scripts/sast_scan.ps1`: `0 critical finding(s)`.
- `scripts/generate_sbom.ps1`: SBOM gerado.
- E2E local: `status=ok`, `events_stored_http=8`, `events_raw=8`,
  `redis_rq_analytics_observed=true`, `pipeline_status=ok`, `ieo_logs=4`,
  `sentinela_ieo_windows=4`.
- Banco SUPREME: `ieo_logs` gravou `SUPREME-ANALYTICS-1.0.0` em 4 janelas
  do evento E2E.
- Banco SENTINELA: `ieo_windows` gravou `SUPREME-ANALYTICS-1.0.0` e
  `algorithm_parameters` em 4 janelas do evento E2E.

## Criterio de aceite

- Mesmo input gera mesmo output.
- IEO, PSI e red flags carregam `SUPREME-ANALYTICS-1.0.0`.
- Parametros do algoritmo acompanham o output.
- SENTINELA nao calcula regra critica.
- Red flags sao reconstruiveis a partir de input, parametros e versao.
