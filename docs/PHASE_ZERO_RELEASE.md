# SUPREME V4 - Phase 0 Release Notes

Esta entrega executa a Fase 0: limpeza de pacote, identidade unica e gate minimo de release.

## Decisoes

- A identidade tecnica e comercial foi padronizada como `SUPREME V4`.
- Arquivos reais de ambiente, certificados privados e tokens locais nao fazem parte do release.
- ZIPs aninhados foram removidos para impedir entrega de artefatos antigos dentro do pacote atual.
- O diretorio `IPED-local/` nao entra no release limpo. IPED deve ser instalado e validado separadamente.
- Perfis de execucao foram separados em `env/`: local, demo, homologation e production.
- Comentarios corrompidos por encoding foram removidos dos arquivos criticos de release.

## Removido do pacote de trabalho

- `.env`
- `certs/fullchain.pem`
- `certs/privkey.pem`
- `SUPREME_FINAL_LIMPO_PARA_CODEX_DEV.zip`

## Gate de release

Antes de gerar ou enviar um pacote, execute:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\release_phase_zero_check.ps1
```

Para auditar a Fase 0 inteira em um staging limpo:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\phase_zero_audit.ps1 -Root .
```

O gate falha se encontrar:

- `.env` ou `.env.production` reais;
- certificados TLS reais ou chave privada;
- token local do Prometheus;
- diretorio `IPED-local`;
- ZIP aninhado;
- banco local, dump, backup ou arquivo de evidencia forense;
- referencias `SUPREME V5`, `SUPREME_V5` ou `V4/V5`;
- padroes obvios de segredo real em arquivos que nao sejam exemplos/documentacao.

O gate tambem exige:

- `.env.example`;
- `.env.production.example`;
- `supreme-backend/.env.production.example`;
- `sentinela/.env.production.example`;
- `env/.env.local.example`;
- `env/.env.demo.example`;
- `env/.env.homologation.example`;
- `env/.env.production.example`;
- `docs/ENVIRONMENT_PROFILES.md`.

## Proxima fase

A Fase 1 deve validar execucao local reprodutivel: compose local, healthchecks e E2E IPED simulado -> SUPREME -> fila -> banco -> SENTINELA.
