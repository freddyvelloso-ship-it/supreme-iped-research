# SUPREME V4 Enterprise — Produção de alto nível

Esta versão adiciona a camada operacional necessária para sair de piloto controlado e entrar em produção institucional.

## Mudanças aplicadas

1. **Build / Dependências**
   - Dependência `prometheus-client` adicionada ao backend.
   - Dockerfile do SUPREME roda com usuário não-root.
   - CI GitHub Actions com build, testes e imagem Docker.

2. **Segurança**
   - `/docs` e `/redoc` desativáveis por variável de ambiente.
   - `/metrics` protegido por bearer token.
   - Endpoints analíticos protegidos por `API_SECRET_KEY`.
   - Endpoint de ingestão protegido por `API_INGEST_TOKEN`.
   - Headers OWASP mínimos adicionados.
   - Nginx com rate limit e proxy reverso.
   - CORS falha fechado em produção se usar `*`.

3. **Banco de Dados**
   - Migração `005_enterprise_production.sql` adiciona:
     - `audit_log`;
     - `algorithm_registry`;
     - `algorithm_version` e `algorithm_parameters` em `ieo_logs`.
   - Compose de produção usa TimescaleDB/PostgreSQL.
   - Scripts de backup/restore adicionados.

4. **Arquitetura**
   - `docker-compose.production.yml` separa:
     - API;
     - Workers;
     - Redis persistente;
     - Banco transacional/temporal;
     - Observabilidade;
     - Nginx.
   - Workers podem escalar por `SUPREME_WORKER_REPLICAS`.

5. **Produto**
   - Endpoint LGPD: `DELETE /v1/governance/subjects/{id_hash}`.
   - Trilha de auditoria para apagamento.
   - Versionamento explícito do algoritmo IEO por cálculo.

6. **Escalabilidade**
   - API com múltiplos workers Uvicorn.
   - Redis com AOF/RDB habilitado.
   - Workers RQ replicáveis.
   - Observabilidade com Prometheus, Grafana e Loki.

## Checklist Go/No-Go

- [ ] `.env.production` criado com segredos fortes.
- [ ] `POSTGRES_PASSWORD`, `API_SECRET_KEY`, `API_INGEST_TOKEN`, `SUPREME_SALT` e `GRAFANA_ADMIN_PASSWORD` definidos.
- [ ] `ALLOWED_ORIGINS` fechado para domínios/IPs reais.
- [ ] Migrações aplicadas em banco limpo.
- [ ] `scripts/smoke_test.ps1` no Windows ou `scripts/smoke_test.sh` no Linux/CI passando.
- [ ] `scripts/form_flow_e2e.ps1` ou `scripts/form_flow_e2e.py` passando contra a stack alvo.
- [ ] `scripts/iped_operational_e2e.ps1` passando contra a stack alvo.
- [ ] `scripts/verify_iped_real_environment.ps1` passando na estacao com IPED real.
- [ ] `scripts/accept_iped_real_session.ps1` aprovado com interacao real no IPED.
- [ ] `scripts/observability_check.ps1` passando.
- [ ] `scripts/render_alertmanager_config.ps1` executado com SMTP real ou destino local validado.
- [ ] Plano de rotacao executado/testado com `scripts/rotate_api_tokens.ps1`.
- [ ] Backup gerado com `scripts/backup_postgres.ps1`.
- [ ] Dumps validados com `scripts/verify_postgres_backup.ps1`.
- [ ] Restore testado em ambiente descartavel com `scripts/restore_postgres.ps1 -ConfirmRestore`.
- [ ] Dashboard Grafana visível.
- [ ] Plano de retenção LGPD aprovado.
- [ ] Política de acesso ao SENTINELA definida.

## Comandos

```bash
cp .env.production.example .env
cp supreme-backend/.env.production.example supreme-backend/.env.production
cp sentinela/.env.production.example sentinela/.env.production
# editar segredos

docker compose -f docker-compose.production.yml up -d --build
API_SECRET_KEY=<token> BASE_URL=http://localhost scripts/smoke_test.sh
# Windows:
# powershell -ExecutionPolicy Bypass -File scripts/smoke_test.ps1
# powershell -ExecutionPolicy Bypass -File scripts/form_flow_e2e.ps1
# powershell -ExecutionPolicy Bypass -File scripts/iped_operational_e2e.ps1
# powershell -ExecutionPolicy Bypass -File scripts/verify_iped_real_environment.ps1
# powershell -ExecutionPolicy Bypass -File scripts/accept_iped_real_session.ps1
# powershell -ExecutionPolicy Bypass -File scripts/observability_check.ps1
scripts/backup_postgres.sh
```

## Arquivos de ambiente e secrets

- `.env.production.example` contem apenas variaveis de orquestracao do Docker Compose.
- `supreme-backend/.env.production.example` contem variaveis da API SUPREME e do worker.
- `sentinela/.env.production.example` contem variaveis da aplicacao SENTINELA.
- `infra/prometheus/supreme-api-token.local` deve conter o mesmo valor de `API_SECRET_KEY` e permanece ignorado pelo git.
- `infra/alertmanager/alertmanager.yml` e gerado a partir do `.env` e permanece ignorado pelo git quando contem SMTP real.
- Arquivos `.env`, `.env.production`, chaves privadas, certificados e tokens locais nao devem ser versionados.

## Limitações remanescentes

- TLS automático depende de domínio e certificado real; o compose inclui Nginx, mas os certificados devem ser provisionados.
- MFA ainda deve ser integrado ao provedor institucional de identidade.
- Promtail/agent de logs pode ser adicionado conforme o runtime real.
- Teste de carga deve ser executado com volumetria real do piloto.

## Gate final de producao

Antes do go-live, execute no servidor alvo:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\production_readiness_check.ps1
```

Durante revisao de PR, valide apenas os templates versionados:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\production_readiness_check.ps1 -TemplateMode -SkipDockerCompose
```

O gate final falha se:

- `.env`, `supreme-backend/.env.production`, `sentinela/.env.production`, certificados TLS reais ou token local do Prometheus estiverem ausentes.
- Algum secret continuar como placeholder ou com tamanho inseguro.
- `ALLOWED_ORIGINS`, `SENTINELA_URL` ou `GRAFANA_ROOT_URL` apontarem para valor local ou de exemplo.
- A chave compartilhada `SENTINELA_API_KEY`/`SUPREME_API_KEY` estiver divergente.
- `infra/prometheus/supreme-api-token.local` nao bater com `API_SECRET_KEY`.
- `BOOTSTRAP_TOKEN` continuar definido depois do bootstrap inicial.
- Arquivos sensiveis aparecerem versionados no Git.

## Gate IPED real

O teste `scripts/iped_operational_e2e.ps1` valida o pipeline com evento
controlado, mas nao homologa IPED real. Para producao com peritos, a Fase 5
exige execucao assistida de:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\verify_iped_real_environment.ps1
powershell -ExecutionPolicy Bypass -File scripts\accept_iped_real_session.ps1
```

O aceite reprova se o IPED real nao gerar `supreme_audit.ndjson` novo ou se os
eventos nao chegarem em `events_raw` como `source_tool='iped'`.

## Consolidacao Fases 0 a 7

Antes de enviar a versao para um dev externo, use o handoff consolidado:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\phase_0_7_audit.ps1
```

Documentos principais:

- `docs/DEV_HANDOFF_SUPREME_V4_PHASES_0_7.md`
- `docs/PHASES_0_5_AUDIT_AND_GAPS.md`
- `docs/PHASE_SIX_SENTINELA_PRODUCT.md`
- `docs/PHASE_SEVEN_WORLD_PRODUCTION.md`

As Fases 6 e 7 ainda devem ser tratadas como backlog de produto/producao
mundial, nao como implementacao completa ja entregue.
