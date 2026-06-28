# SUPREME V4 - Gestao de segredos e rotacao

## Regra operacional

- `.env`, `.env.production`, certificados, `infra/prometheus/supreme-api-token.local`, `infra/alertmanager/alertmanager.yml` e `.local/` nunca entram em Git, chat, ticket ou pacote de release.
- Em local, `SUBIR_LOCAL.ps1` grava credenciais em `.local/credentials.local.txt`.
- Em homologacao/producao, use o secret manager institucional e injete os valores no deploy.

## Segredos minimos por ambiente

- Orquestracao: `POSTGRES_PASSWORD`, `SENTINELA_POSTGRES_PASSWORD`, `REDIS_PASSWORD`, `GRAFANA_ADMIN_PASSWORD`.
- SUPREME: `API_SECRET_KEY`, `API_INGEST_TOKEN`, `SUPREME_SALT`, `SENTINELA_API_KEY`.
- SENTINELA: `SECRET_KEY`, `SUPREME_API_KEY`.
- Alertas: `ALERTMANAGER_SMTP_HOST`, `ALERTMANAGER_SMTP_FROM`, `ALERTMANAGER_SMTP_USERNAME`, `ALERTMANAGER_SMTP_PASSWORD`, `ALERTMANAGER_EMAIL_TO`.

## Rotacao de tokens API

Rotacionar admin/metrics token:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\rotate_api_tokens.ps1 -RotateAdminToken -ApplyDockerRestart
```

Rotacionar ingestao launcher/watcher/proxy:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\rotate_api_tokens.ps1 -RotateIngestToken -ApplyDockerRestart
```

Rotacionar ambos:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\rotate_api_tokens.ps1 -RotateAdminToken -RotateIngestToken -ApplyDockerRestart
```

O script faz backup local em `.local/rotation-backups/<timestamp>/` e mascara os valores no terminal.

## Nao rotacionar automaticamente

`SUPREME_SALT` nao deve ser rotacionado como token comum. Ele participa da pseudonimizacao. Rotacionar sem plano de migracao separa identidades antigas e novas.

## Go-live

Antes de go-live:

1. Gerar segredos fora do repositório.
2. Renderizar Alertmanager com SMTP real.
3. Criar `infra/prometheus/supreme-api-token.local` com o mesmo valor de `API_SECRET_KEY`.
4. Remover ou esvaziar `BOOTSTRAP_TOKEN` apos bootstrap master.
5. Rodar `scripts\production_readiness_check.ps1` sem `-LocalMode`.
