# SUPREME V4 - Handoff consolidado para dev

> Historical note: use `docs/PHASE_EXECUTION_LEDGER.md` as the current
> phase-by-phase execution authority. This handoff can contain older status
> snapshots kept for traceability.

Este e o documento principal para o dev. Documentos anteriores permanecem no
pacote por historico, mas este consolida o roteiro final de fases 0 a 7.

## Como ler o pacote

1. Rodar o release gate em staging limpo:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\release_phase_zero_check.ps1 -Root .
```

2. Validar templates:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\production_readiness_check.ps1 -TemplateMode -SkipDockerCompose
```

3. Subir local:

```powershell
powershell -ExecutionPolicy Bypass -File .\SUBIR_LOCAL.ps1
```

4. Rodar E2E local:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\smoke_test.ps1
powershell -ExecutionPolicy Bypass -File scripts\form_flow_e2e.ps1
powershell -ExecutionPolicy Bypass -File scripts\iped_operational_e2e.ps1
```

5. Validar IPED real:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\verify_iped_real_environment.ps1
powershell -ExecutionPolicy Bypass -File scripts\accept_iped_real_session.ps1
```

6. Rodar auditoria 0-7:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\phase_0_7_audit.ps1
```

## Estado consolidado

- Fase 0: `100_PERCENT_COMPLETE` no ledger.
- Fase 1: `100_PERCENT_COMPLETE` no ledger.
- Fase 2: `100_PERCENT_COMPLETE` no ledger.
- Fase 3: `100_PERCENT_COMPLETE` no ledger.
- Fase 4: `100_PERCENT_COMPLETE` no ledger, com dataset sintetico
  deterministico, ground truth, metricas FP/FN, estabilidade por volume,
  sensibilidade a baixa qualidade de dado, relatorio tecnico e model card.
- Fase 5: `100_PERCENT_COMPLETE` no ledger para cadeia de custodia simulada e
  verificavel, com assinatura de eventos, hash chain, manifesto, replay
  deterministico, relatorio de integridade, auditoria administrativa e export
  forense verificavel.
- Fase 6: `100_PERCENT_COMPLETE` no ledger. O bloqueio historico de IPED real
  foi resolvido por instrumentacao do codigo oficial IPED e aceito em
  `docs/PHASE_FIVE_REAL_IPED_TEST_20260623.md`.
- Fase 7: `100_PERCENT_COMPLETE` no ledger. O pacote final inclui CI/CD,
  staging, backup/restore testado, SLO/runbooks, pacotes de auditoria externa,
  benchmark inspirado no NIST CFTT, whitepaper e ZIP limpo validado em staging
  extraido.

## Ordem recomendada para o dev

1. Ler `docs/PHASE_EXECUTION_LEDGER.md`.
2. Extrair o ZIP final e rodar `scripts\release_phase_zero_check.ps1`.
3. Rodar `scripts\phase7_world_production_check.ps1`.
4. Subir local com `scripts\local.ps1 -Action all`.
5. Para homologacao real, copiar exemplos de staging para um cofre de secrets e
   subir `docker-compose.production.yml` com `docker-compose.staging.yml`.
6. Acionar auditoria externa de seguranca e auditoria estatistica usando os
   pacotes em `docs/audit`.

## Documentos novos desta consolidacao

- `docs/PHASES_0_5_AUDIT_AND_GAPS.md`
- `docs/PHASE_SIX_SENTINELA_PRODUCT.md`
- `docs/PHASE_SEVEN_WORLD_PRODUCTION.md`
- `docs/DEV_HANDOFF_SUPREME_V4_PHASES_0_7.md`
- `docs/PHASE_FOUR_SCIENTIFIC_VALIDATION.md`
- `docs/MODEL_CARD_SUPREME.md`
- `docs/phase4_validation/`
- `docs/PHASE_FIVE_FORENSIC_CUSTODY.md`
- `docs/PHASE_FIVE_REAL_IPED_TEST_20260623.md`
- `docs/phase5_forensic/`

## Scripts novos desta consolidacao

- `scripts/phase_0_7_audit.ps1`
- `scripts/phase4_scientific_validation.py`
- `scripts/phase4_scientific_validation_check.ps1`
- `scripts/phase5_forensic_custody.py`
- `scripts/phase5_forensic_custody_check.ps1`

## Ressalva correta

O pacote esta fechado como entrega tecnica Fases 0-7. Ele prepara auditoria
externa, mas nao afirma que auditoria externa de seguranca, revisao estatistica
independente ou certificacao NIST foram emitidas.
