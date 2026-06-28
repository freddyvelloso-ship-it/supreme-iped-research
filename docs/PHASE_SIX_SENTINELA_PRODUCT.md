# SUPREME V4 - Fase 6: SENTINELA Produto

Objetivo: transformar o SENTINELA em produto operacional profissional, sem
calcular regra critica no front-end e capaz de operar um estudo real.

## Principio arquitetural

O SUPREME e a fonte analitica. O SENTINELA e a camada de operacao, visualizacao,
relatorio e governanca. Nenhuma regra critica de IEO, PSI, red flag,
convergencia, dissonancia, cronicidade ou reatividade deve viver no front-end.

## Papeis de produto

| Papel | Pode ver | Pode fazer | Nao pode |
|---|---|---|---|
| Gestor | Agregados, saude operacional, qualidade de dados | Exportar relatorio agregado | Ver participante individual sem permissao explicita |
| Pesquisador | Dados pseudonimizados por estudo/caso | Exportar dataset cientifico | Alterar usuarios ou politicas |
| Auditor | Trilhas, manifests, hashes, versoes | Exportar evidencias | Editar dados |
| Operador | Pipeline, ingestao, falhas, DLQ | Reprocessar/abrir incidente | Ver psicometria individual sensivel |
| Master | Tudo, com auditoria | Administrar usuarios/escopos | Apagar trilha auditavel |

## Telas obrigatorias

1. Estudos
   - Lista de estudos.
   - Status: ativo, pausado, encerrado.
   - Janela de coleta, protocolo, responsavel e instituicao.

2. Casos
   - Caso vinculado a estudo.
   - Fonte de dados: IPED/proxy/watcher.
   - Versoes: IPED, patch, proxy, watcher, algoritmo.

3. Participantes
   - Lista pseudonimizada.
   - Status: ativo, inativo, revogado, excluido logicamente.
   - Permissao por papel e escopo.

4. Saude do pipeline
   - API, worker, Redis, banco, watcher, proxy.
   - Dead letter queue.
   - Ultimo processamento por estagio.

5. Qualidade de dados
   - DQ por janela.
   - Janelas insuficientes.
   - Gaps de coleta.
   - Baixa qualidade por participante/estudo/caso.

6. Relatorios
   - HTML e PDF gerados no backend.
   - Assinatura/hash do relatorio.
   - Versao do algoritmo e parametros.

7. Exportacao cientifica
   - CSV.
   - JSON.
   - Parquet.
   - Dicionario de dados.
   - Manifesto de exportacao com hash.

## Status atual

Este arquivo nasceu como especificacao. O estado executado da Fase 6 esta em
`docs/PHASE_SIX_SENTINELA_PRODUCT_EXECUTION.md` e no ledger.

Implementado nesta fase:

- Exportacao CSV, JSON, Parquet e dicionario de dados.
- RBAC de produto para `master`, `pesquisador`, `auditor`, `operador` e
  `leitura_agregada`.
- Escopo por instituicao, estudo, caso e participante.
- Endpoints de estudos/casos, participantes, saude do pipeline, qualidade de
  dados e relatorios assinados.
- Secoes de dashboard por papel com estados vazios.

Nao concluido:

- Aceite de estudo real depende de IPED real emitindo eventos auditaveis para
  SUPREME. O bloqueio atual esta em
  `docs/PHASE_FIVE_REAL_IPED_TEST_20260623.md`.
- Verificacao visual em container reconstruido depende de Docker Desktop voltar
  a expor o engine local.

## Entregaveis para o dev

- Modelagem: `institutions`, `studies`, `cases`, `participants`,
  `role_assignments`, `report_exports`, `data_exports`.
- Endpoints:
  - `GET /api/studies`
  - `POST /api/studies`
  - `GET /api/cases`
  - `POST /api/cases`
  - `GET /api/participants`
  - `GET /api/pipeline/health`
  - `GET /api/data-quality`
  - `POST /api/reports`
  - `GET /api/export/{format}`
- Front-end:
  - navegacao por papel;
  - telas de estudo/caso/participante;
  - paineis de saude e qualidade;
  - exports com manifest.

## Criterio de aceite

- SENTINELA nao contem calculo critico novo no front-end.
- Gestor, pesquisador, auditor e operador veem experiencias diferentes.
- Um estudo real pode ser cadastrado, operado e auditado.
- Exportacao cientifica sai com manifesto e dicionario de dados.
- Relatorio PDF/HTML e gerado no backend e possui hash verificavel.
# Historical Notice

This file predates Phase 2 hardening. Current RBAC roles are `master`,
`pesquisador`, `auditor`, `operador` and `leitura_agregada`; current session
handling uses HttpOnly cookies. See `docs/PHASE_EXECUTION_LEDGER.md`.
