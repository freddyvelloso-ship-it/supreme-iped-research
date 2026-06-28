# SUPREME V4 - Fase 5: aceite com IPED real

Esta fase substitui o criterio "IPED-like" por um criterio de homologacao real.
O teste sintetico da Fase 4 continua util para diagnostico de pipeline, mas nao
certifica integracao com IPED.

## Objetivo

Validar, em uma estacao com IPED real, o fluxo completo:

```text
IPED real patched
  -> supreme_audit.ndjson real
  -> supreme-iped-watcher/proxy
  -> SUPREME /v1/events/ingest
  -> events_raw
  -> worker RQ
  -> window_metrics/IEO
  -> SENTINELA
```

## Entregas da fase

- `scripts/verify_iped_real_environment.ps1`
- `scripts/accept_iped_real_session.ps1`
- `scripts/watch_iped_audit_tail.ps1`

## Procedimento de homologacao

```powershell
powershell -ExecutionPolicy Bypass -File .\SUBIR_LOCAL.ps1
powershell -ExecutionPolicy Bypass -File .\INSTALAR_PATCH_IPED.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\verify_iped_real_environment.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\watch_iped_audit_tail.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\accept_iped_real_session.ps1
```

No IPED, abrir uma evidencia/caso real de homologacao, selecionar itens,
visualizar imagens/videos/previews, marcar ao menos um bookmark se aplicavel e
fechar o IPED.

## Criterios de aceite

- IPED real detectado, nao bundle simulado.
- `supreme-audit-patch.jar` instalado em `plugins/`.
- `supreme_audit.ndjson` recebe linhas novas durante a sessao.
- Linhas novas contem `event`, `itemId`, `mediaType`, `openTs`, `closeTs`, `userId`.
- Ha ao menos um evento `close` ou `classification_event`.
- Watcher/proxy nao imprime secrets em log.
- `events_raw` recebe eventos `source_tool='iped'` depois do inicio do aceite.
- Worker processa sem dead letter.
- Dados pseudonimizados aparecem no fluxo analitico.

## Nao aprovado se

- O teste usar somente `scripts/iped_operational_e2e.ps1`.
- O log NDJSON for criado manualmente.
- O IPED abrir, mas nao gerar linhas novas.
- O watcher estiver parado.
- Eventos chegarem ao banco com `source_tool` diferente de `iped`.
- O launcher expuser token em URL ou terminal.

## Observacao critica

Esta fase entrega o gate tecnico para homologacao real. A certificacao final
depende de executar o script em uma estacao com IPED real e interacao humana no
caso de teste.
