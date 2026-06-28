# LEIA PRIMEIRO - SUPREME V4 handoff

Documento principal para o desenvolvedor:

```text
docs/DEV_HANDOFF_SUPREME_V4_PHASES_0_7.md
```

Para a Fase 0, validar primeiro:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\phase_zero_audit.ps1 -Root .
powershell -ExecutionPolicy Bypass -File scripts\release_phase_zero_check.ps1 -Root .
```

O pacote de release nao pode conter:

- `.env` real;
- `.env.production` real;
- certificados privados;
- token local do Prometheus;
- configuracao real do Alertmanager;
- backups;
- banco local;
- `supreme_audit.ndjson`;
- evidencia IPED real;
- ZIP antigo aninhado.

Para subir localmente:

```powershell
powershell -ExecutionPolicy Bypass -File .\SUBIR_LOCAL.ps1
```

Para validar IPED real:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\verify_iped_real_environment.ps1
powershell -ExecutionPolicy Bypass -File scripts\accept_iped_real_session.ps1
```

Antes de qualquer producao real, rotacionar todos os segredos e executar o gate
de readiness em ambiente alvo.
