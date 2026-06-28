# SUPREME V4 - Parte 4 operacao, DR e observabilidade

Data: 2026-06-22

## Entregas

- Backup PowerShell nativo para Windows/Docker Desktop: `scripts/backup_postgres.ps1`.
- Verificacao de dump com `pg_restore --list`: `scripts/verify_postgres_backup.ps1`.
- Restore destrutivo com trava explicita: `scripts/restore_postgres.ps1 -ConfirmRestore`.
- Check de observabilidade: `scripts/observability_check.ps1`.
- E2E operacional tipo IPED: `scripts/iped_operational_e2e.py` e `.ps1`.
- Loki local exposto em `http://localhost:3111` pelo clone local.
- Readiness passa a exigir scripts de backup, restore, verificacao, observabilidade e E2E operacional.

## Evidencias locais

- `scripts/iped_operational_e2e.ps1`: OK.
  - `events_raw`: 2 eventos.
  - `window_metrics`: 1 janela.
  - `system_health_logs`: pipeline `ok`.
- `scripts/backup_postgres.ps1`: OK.
  - SUPREME dump gerado.
  - SENTINELA dump gerado.
  - Manifest SHA256 gerado.
- `scripts/verify_postgres_backup.ps1`: OK.
  - SUPREME: 94 tabelas detectadas.
  - SENTINELA: 12 tabelas detectadas.
- `scripts/observability_check.ps1`: OK.
  - Prometheus ready.
  - Targets `supreme-api`, `postgres-exporter`, `redis-exporter` UP.
  - Loki ready.
  - Grafana API health OK.

## Comandos

Backup:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\backup_postgres.ps1 -OutputDir .\backups\postgres
```

Verificar dump:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\verify_postgres_backup.ps1 -DumpPath .\backups\postgres\supreme_YYYY.dump -Database supreme
powershell -ExecutionPolicy Bypass -File scripts\verify_postgres_backup.ps1 -DumpPath .\backups\postgres\sentinela_YYYY.dump -Database sentinela
```

Restore, destrutivo:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\restore_postgres.ps1 -DumpPath .\backups\postgres\supreme_YYYY.dump -Database supreme -ConfirmRestore
```

Observabilidade:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\observability_check.ps1
```

E2E operacional:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\iped_operational_e2e.ps1 -BaseUrl https://localhost
```

Para homologacao real com espelho no SENTINELA:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\iped_operational_e2e.ps1 -BaseUrl https://seu-dominio -RequireSentinela
```

## Pendencias externas

- Testar com IPED real gerando `supreme_audit.ndjson` em estacao de perito.
- Executar restore em ambiente descartavel antes de homologacao institucional.
- Definir RPO/RTO formal com o cliente.

## Relacao com a Fase 5

O E2E IPED-like desta fase e apenas diagnostico de pipeline. Ele prova que a
API, o banco, o worker e a metrica aceitam eventos no contrato SUPREME, mas nao
prova que o IPED real esta emitindo eventos.

A homologacao real fica na Fase 5:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\verify_iped_real_environment.ps1
powershell -ExecutionPolicy Bypass -File scripts\accept_iped_real_session.ps1
```
