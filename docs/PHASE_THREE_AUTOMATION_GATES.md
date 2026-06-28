# SUPREME V4 - Fase 3 automacao e gates

Data: 2026-06-22

## Entregas

- CI passa a rodar `production_readiness_check.ps1 -TemplateMode -SkipDockerCompose`.
- CI passa a rodar `release_phase_zero_check.ps1 -Root .`.
- Readiness valida variaveis SMTP do Alertmanager e arquivo renderizado.
- Readiness de producao rejeita Alertmanager apontando para Mailpit, localhost ou noop.
- `scripts/rotate_api_tokens.ps1` rotaciona `API_SECRET_KEY` e/ou `API_INGEST_TOKEN` com backup local.
- `docs/SECRET_MANAGEMENT.md` define politica operacional de segredos e rotacao.
- `scripts/form_flow_e2e.py` e `scripts/form_flow_e2e.ps1` validam o fluxo assinado dos quatro formularios.
- Testes unitarios cobrem token de formulario HMAC, expiracao, cookie e bearer de ingestao.
- `.env.production.example` foi limpo para usar nomes SMTP consistentes com o render do Alertmanager.

## Evidencias locais

- Compile Python dos arquivos alterados: OK.
- Template readiness: 0 falhas.
- Local readiness: 0 falhas.
- Smoke test local HTTPS: OK.
- E2E dos formularios:
  - SRQ20: OK.
  - DASS21: OK.
  - OLBI: OK.
  - PANAS_SHORT: OK.
  - Submit sem sessao: 401 esperado.

## Observacoes

- `pytest` nao estava instalado no Python local embutido usado nesta maquina, mas o CI instala `.[dev]` antes de rodar `pytest -q`.
- O release gate deve ser executado em pacote/staging limpo. No diretorio local em execucao ele falha corretamente por encontrar `.env`, certificados e arquivos gerados.

## Pendencias externas

- Inserir SMTP institucional real em homologacao/producao.
- Integrar secret manager do ambiente alvo no pipeline de deploy.
- Rodar teste E2E com IPED real e carga operacional.
