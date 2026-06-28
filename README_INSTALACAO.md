# SUPREME V4 + SENTINELA - Guia de instalacao

Sistema de coleta de eventos operacionais do IPED, processamento analitico no
SUPREME e visualizacao operacional no SENTINELA.

## Componentes

```text
supreme-backend/          SUPREME API, workers, ingestao e pipeline
sentinela/                Dashboard, autenticacao e exportacao
supreme-iped-integration/ Watcher, proxy e patch IPED
LAUNCHER_IPED.ps1         Launcher principal da estacao do perito
SUBIR_LOCAL.ps1           Setup local Windows + Docker Desktop
```

## Fluxo de dados

```text
IPED patched
  -> supreme_audit.ndjson
  -> watcher/proxy
  -> SUPREME /v1/events/ingest
  -> worker IEO/PSI
  -> SENTINELA
```

## Setup local

```powershell
powershell -ExecutionPolicy Bypass -File .\SUBIR_LOCAL.ps1
```

Acessos locais:

- SENTINELA: `https://localhost/sentinela/`
- SUPREME health: `https://localhost/health`
- SENTINELA health: `https://localhost/sentinela/health`
- Grafana: `https://localhost/grafana/`
- Mailpit: `http://localhost:8025/`

O certificado local e autoassinado. Aceite o aviso no navegador apenas em
ambiente local.

## Validacao local

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\local.ps1 -Action all
powershell -ExecutionPolicy Bypass -File scripts\smoke_test.ps1
powershell -ExecutionPolicy Bypass -File scripts\form_flow_e2e.ps1
powershell -ExecutionPolicy Bypass -File scripts\iped_operational_e2e.ps1
```

Roteiro curto da execucao local reproduzivel: `docs\LOCAL_15_MINUTES.md`.

## IPED real

1. Instalar o patch:

```powershell
powershell -ExecutionPolicy Bypass -File .\INSTALAR_PATCH_IPED.ps1
```

2. Verificar ambiente:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\verify_iped_real_environment.ps1
```

3. Executar aceite assistido:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\accept_iped_real_session.ps1
```

## Homologacao e producao

Copie os exemplos e substitua todos os `CHANGE_ME` fora do Git:

```powershell
Copy-Item .env.production.example .env
Copy-Item supreme-backend\.env.production.example supreme-backend\.env.production
Copy-Item sentinela\.env.production.example sentinela\.env.production
```

Perfis de ambiente:

- `env/.env.local.example`
- `env/.env.demo.example`
- `env/.env.homologation.example`
- `env/.env.production.example`

Leia tambem:

- `docs/ENVIRONMENT_PROFILES.md`
- `docs/PHASE_ZERO_RELEASE.md`
- `docs/PRODUCAO_ENTERPRISE.md`
- `docs/DEV_HANDOFF_SUPREME_V4_PHASES_0_7.md`

## Gate de release

Antes de enviar qualquer ZIP:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\phase_zero_audit.ps1 -Root .
powershell -ExecutionPolicy Bypass -File scripts\release_phase_zero_check.ps1 -Root .
```

O pacote de release nao deve conter arquivos reais de ambiente, certificados,
tokens locais, bancos, backups, logs de auditoria, `IPED-local` ou evidencia
IPED real.
