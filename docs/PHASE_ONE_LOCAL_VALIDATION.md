# SUPREME V4 - Fase 1: Execucao Local Reprodutivel

Data: 2026-06-22

## Objetivo

Qualquer dev deve conseguir subir o sistema local sem adivinhar ordem de comandos, nomes de arquivos ou tokens.

## Entregas

- `docker-compose.local.yml` funciona como override local explicito sobre `docker-compose.production.yml`.
- `scripts\local.ps1` concentra setup, reset, subida, healthcheck, seed e E2E.
- `scripts\setup_env_local.ps1` gera secrets locais sem imprimir tokens no terminal.
- `seeds\local\clean` e `seeds\local\demo` separam base limpa de demonstracao.
- `scripts\validate_local_health.ps1` valida SUPREME, SENTINELA, Redis, Postgres e NGINX.
- `scripts\local_e2e_iped_to_sentinela.ps1` executa o E2E deterministico:
  evento IPED simulado -> SUPREME -> Redis/RQ -> Postgres -> SENTINELA.
- `docs\LOCAL_15_MINUTES.md` documenta o fluxo local curto.

## Comando de aceite

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\local.ps1 -Action all -RegenerateSecrets -PythonExe "C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -TimeoutSeconds 300
```

Esse comando deve terminar sem erro e imprimir JSON `status: ok` do E2E.

## Evidencias de aceite rigido

Executado em ambiente local com Docker Desktop:

- `docker compose -f docker-compose.production.yml -f docker-compose.local.yml config --quiet`: OK.
- `scripts\local.ps1 -Action all -RegenerateSecrets ...`: OK.
- `scripts\production_readiness_check.ps1 -LocalMode -SkipDockerCompose`: `Resumo: 0 falha(s), 0 aviso(s)`.
- `scripts\local.ps1 -Action health ...`: todos os healthchecks OK.
- `scripts\local.ps1 -Action seed-demo`: dados demo aplicados nos dois bancos.
- `scripts\local.ps1 -Action seed-clean`: dados `phase1-*` removidos dos dois bancos.
- `scripts\local.ps1 -Action test ...`: E2E final `status: ok`.

## Evidencias esperadas do E2E

O JSON final deve conter:

- `events_stored_http >= 8`
- `events_raw >= 8`
- `redis_rq_analytics_observed = true`
- `pipeline_status = ok`
- `window_metrics_at_least_4 = true`
- `ieo_logs >= 1`
- `sentinela_ieo_windows >= 1`

## Escopo

A Fase 1 valida reprodutibilidade local. Ela nao certifica seguranca de producao, auditoria externa, hardening final ou metodologia estatistica.
