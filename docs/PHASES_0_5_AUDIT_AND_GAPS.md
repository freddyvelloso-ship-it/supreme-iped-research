# SUPREME V4 - Auditoria das Fases 0 a 5

> Historical snapshot: use `docs/PHASE_EXECUTION_LEDGER.md` as the current
> phase-by-phase execution authority. This document is retained to preserve the
> audit trail of earlier gaps. The Phase 5 gaps below were closed by
> `docs/PHASE_FIVE_FORENSIC_CUSTODY.md` and
> `scripts/phase5_forensic_custody_check.ps1`.

Data: 2026-06-22

Este documento audita o pacote atual contra o roteiro de produto definido para
as fases 0 a 5. O objetivo e separar o que esta entregue, o que esta parcialmente
entregue e o que ainda deve virar implementacao de produto.

## Resumo executivo

| Fase | Status | Leitura honesta |
|---|---:|---|
| 0 - Limpeza e verdade do pacote | Parcial forte | O gate de release existe e o ZIP limpo remove segredos, mas ainda ha mojibake em arquivos legados. |
| 1 - Execucao local reprodutivel | Forte | Stack local, secrets locais, healthchecks e E2E operacional existem. |
| 2 - Seguranca seria | Parcial | Ha hardening importante, mas RBAC granular, ASVS completo, SBOM/SAST/dependency scan e sessao web mais segura ainda precisam evoluir. |
| 3 - Motor analitico unico | Parcial | SUPREME concentra IEO/PSI/risk, mas SENTINELA ainda contem codigo analitico/legado e o contrato precisa ser travado. |
| 4 - Validacao cientifica | Inicial | Existe E2E operacional, mas ainda faltam dataset com ground truth, metricas FP/FN, model card e relatorio cientifico reproduzivel. |
| 5 - Cadeia de custodia/auditoria forense | Historico, superado | Este snapshot dizia que assinatura, hash chain e replay faltavam; o ledger atual registra a implementacao forense deterministica e verificavel da Fase 5. |

## Fase 0 - Limpeza e verdade do pacote

Entregue:

- `scripts/release_phase_zero_check.ps1` falha em release quando encontra `.env`,
  certificados privados, tokens locais, backups ou ZIP aninhado fora de `IPED-local`.
- `.env.production.example` existe na raiz, SUPREME e SENTINELA.
- Pacotes anteriores foram gerados sem `.env`, certificados privados e tokens locais.
- Identidade principal permanece SUPREME V4.

Lacunas:

- Ha mojibake em documentos e HTML legados. Nao bloqueia execucao,
  mas bloqueia polimento institucional.
- Ainda ha muitos documentos historicos com estados antigos. O dev deve tratar
  `docs/DEV_HANDOFF_SUPREME_V4_PHASES_0_7.md` como documento consolidado.

Aceite atual: aprovado para pacote tecnico, pendente para acabamento editorial.

## Fase 1 - Execucao local reprodutivel

Entregue:

- `SUBIR_LOCAL.ps1` sobe stack local com secrets, certificados locais, bootstrap e
  remocao de `BOOTSTRAP_TOKEN`.
- `docker-compose.production.yml` + `docker-compose.local.yml` compoem a stack.
- `scripts/smoke_test.ps1`, `scripts/form_flow_e2e.ps1` e
  `scripts/iped_operational_e2e.ps1` existem.
- Healthchecks cobrem SUPREME, SENTINELA, Postgres, Redis e NGINX.
- `docs/PHASE_ONE_LOCAL_VALIDATION.md` registra evidencias locais.

Lacunas:

- Seed limpo e seed demo ainda nao estao formalmente separados como comando unico.
- O roteiro "como rodar em 15 minutos" existe de forma espalhada; precisa virar
  uma pagina unica final para dev externo.

Aceite atual: aprovado para dev que recebeu handoff; melhorar onboarding.

## Fase 2 - Seguranca seria

Entregue:

- Separacao entre `API_SECRET_KEY` e `API_INGEST_TOKEN`.
- Bootstrap SENTINELA de uso unico.
- JWT com `jti`.
- Dockerfiles com usuario nao-root no SUPREME.
- Rate limit no NGINX.
- Readiness falha em segredos fracos, CORS aberto, Bootstrap token remanescente e
  SMTP falso em producao.
- Rotacao de tokens em `scripts/rotate_api_tokens.ps1`.

Lacunas:

- SENTINELA ainda usa papéis simples (`master`, `pibic`), nao o RBAC granular do
  roteiro (`master`, pesquisador, auditor, operador, leitura agregada).
- Escopo por instituicao, estudo, caso e participante ainda nao esta modelado.
- Estrategia de sessao precisa sair de token JS/localStorage para cookie seguro
  HttpOnly/SameSite ou BFF.
- CI nao possui SBOM, dependency scan, secret scan externo, SAST dedicado nem
  mapa OWASP ASVS com evidencias.

Aceite atual: aprovado para hardening local/homologacao; nao aprovado como ASVS.

## Fase 3 - Motor analitico unico

Entregue:

- SUPREME contem `ieo.py`, `psi.py`, `risk.py`, `metrics.py` e versionamento via
  `algorithm_registry`/`algorithm_version`.
- SENTINELA recebe e visualiza janelas/flags.
- Testes matematicos iniciais cobrem identidade de hash e seguranca.

Lacunas:

- SENTINELA ainda possui `sentinela/src/engine/red_flags.py`; deve virar legado
  removido ou claramente nao executado em producao.
- Faltam testes matematicos formais de IEO, PSI, convergencia, dissonancia,
  cronicidade e reatividade.
- O contrato "SENTINELA apenas visualiza outputs auditaveis" ainda precisa virar
  gate automatizado.

Aceite atual: parcialmente aprovado; exige travar fronteira analitica.

## Fase 4 - Validacao cientifica

Entregue:

- `scripts/iped_operational_e2e.py` valida pipeline operacional com evento
  controlado.
- `algorithm_registry` registra a versao ativa do algoritmo.
- `docs/PHASE_FOUR_OPERATIONS_DR.md` cobre operacao, DR e observabilidade.

Lacunas:

- Ainda falta dataset sintetico com ground truth.
- Ainda faltam cenarios formais: baixo risco, reatividade, dissonancia,
  cronicidade e convergencia critica.
- Ainda faltam metricas de falso positivo/falso negativo, estabilidade por volume
  e sensibilidade a baixa qualidade de dado.
- Ainda faltam relatorio tecnico de validacao e model card.

Aceite atual: operacional aprovado; cientifico ainda em fase inicial.

## Fase 5 - Cadeia de custodia e auditoria forense

Atualizacao 2026-06-23: as lacunas historicas abaixo foram fechadas para o
fluxo IPED simulado/deterministico por `scripts/phase5_forensic_custody.py`,
`scripts/phase5_forensic_custody_check.ps1`,
`docs/phase5_forensic/forensic_export.json` e
`docs/PHASE_FIVE_FORENSIC_CUSTODY.md`. IPED real continua dependente de ambiente
autorizado quando disponivel.

Entregue:

- IPED real detectado por `scripts/verify_iped_real_environment.ps1`.
- Aceite assistido por `scripts/accept_iped_real_session.ps1`.
- Monitor de NDJSON por `scripts/watch_iped_audit_tail.ps1`.
- `events_raw` local contem 4 eventos `source_tool='iped'`.
- `audit_log`, `subject_consents`, `algorithm_registry` e `dead_letter_queue`
  existem e foram verificados localmente.

Lacunas:

- Eventos ainda nao sao assinados criptograficamente na origem.
- Ainda nao ha hash chain formal para NDJSON, ingestao e outputs.
- Ainda nao ha manifesto por sessao com versoes IPED/patch/proxy/watcher.
- Ainda nao ha replay deterministico completo do pipeline.
- Historico: neste snapshot, exportacao forense verificavel ainda nao estava
  implementada. Estado atual: implementada e verificada pela Fase 5 no ledger.

Aceite atual historico: gate real IPED aprovado em dry-run e ambiente local.
Estado atual deve ser lido no ledger: cadeia forense simulada/verificavel
implementada e gateada; sessao IPED real depende de ambiente autorizado.
# Historical Notice

This file is a historical audit snapshot. The current source of truth is
`docs/PHASE_EXECUTION_LEDGER.md`; Phase 2 replaces the older `master/pibic`
and browser-storage session notes with granular RBAC and HttpOnly cookies.
