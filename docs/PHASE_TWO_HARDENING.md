# SUPREME V4 - Fase 2 hardening inicial

Data: 2026-06-22

## Correcoes entregues

- Alertmanager deixou de usar receiver noop. A config agora e renderizada por `scripts/render_alertmanager_config.ps1`.
- Ambiente local envia alertas reais para Mailpit em `http://localhost:8025/`.
- `SUBIR_LOCAL.ps1` nao imprime mais senhas/tokens completos no terminal.
- Credenciais locais ficam em `.local/credentials.local.txt`, ignorado pelo git.
- `BOOTSTRAP_TOKEN` e esvaziado em `sentinela/.env.production` apos login master validado, com recriacao do container.
- `scripts/smoke_test.ps1` virou o smoke test nativo para Windows, sem bash/grep.
- Launcher removeu `API_INGEST_TOKEN` das URLs de formulario.
- Formularios agora usam link assinado curto, cookie HTTP-only e submit sem token global no navegador.
- Submit sem cookie/token retorna 401.
- Integrações servidor-servidor ainda podem usar `Bearer API_INGEST_TOKEN` para compatibilidade controlada.

## Evidencias locais

- `python -m compileall supreme-backend\src\app\api\psychometric.py`: OK.
- `scripts\smoke_test.ps1` contra `https://localhost`: OK.
- Fluxo `/v1/forms/link` -> `/forms/srq20/start` -> `/v1/forms/session` -> `/v1/psychometric/submit`: OK.
- Submit de formulario sem sessao: 401.
- Alertmanager recebeu alerta de teste e Mailpit armazenou e-mail com assunto `[FIRING:1] Fase2AlertmanagerTeste warning (phase2)`.
- `scripts\production_readiness_check.ps1 -LocalMode`: 0 falhas.
- `scripts\production_readiness_check.ps1 -TemplateMode`: 0 falhas.

## Pendencias para fase seguinte

- Configurar SMTP institucional real em ambiente de homologacao/producao.
- Adicionar rotação operacional de `API_SECRET_KEY` e `API_INGEST_TOKEN`.
- Substituir credenciais locais por secret manager no deploy real.
- Incluir testes automatizados de browser para os formularios.
