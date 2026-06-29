# SUPREME-IPED Research + Sentinela - System Health Audit

Data: 2026-06-29
Branch: `codex/system-health-publication-audit`
Base auditada: `4815f33`

## Decisao Final

Status: `healthy_for_publication`

Escopo da decisao: publicacao controlada do codigo, runtime local, fluxo sintetico seguro e documentacao operacional. A validacao de campo com sessao IPED real continua pendente ate existir `supreme_audit.ndjson` real gerado pelo IPED patched em sessao autorizada.

## Comandos Executados

| Comando | Resultado |
| --- | --- |
| `git branch --show-current` | `main`, depois branch criada |
| `git checkout -b codex/system-health-publication-audit` | OK |
| `sentinela: PYTHONPATH=src python -m pytest -q -p no:cacheprovider` | 30 passed |
| `supreme-backend: PYTHONPATH=src python -m pytest -q` | 40 passed |
| `supreme-iped-integration: python -m pytest -q` com `TEMP/TMP` local | 46 passed |
| `python -m pytest -q` na raiz | 7 passed |
| `PYTHONPATH=src python -m pytest -q` na raiz | 7 passed |
| `node --check sentinela/static/sentinela-ux.js` | OK |
| `node --check scripts/iped_journey_gate.mjs` | OK |
| `git diff --check` | OK |
| `scripts/secret_scan.ps1` | 0 critical findings |
| `ruff check .` | Bloqueado: `ruff` nao instalado no ambiente |
| `http://localhost:18001/health` | OK |
| `GET /sentinela` | 200 |
| `POST /sentinela/api/auth/login` | 200 |
| `GET /sentinela/api/auth/me` | 200, role `master` |
| `GET /sentinela/api/dashboard/overview` | 200 |
| `GET /sentinela/api/dashboard/ieo-series` | 200 |
| `GET /sentinela/api/dashboard/red-flags` | 200 |
| `POST /sentinela/api/auth/logout` | 200 |
| `scripts/iped_operational_e2e.py --require-sentinela` | OK: 8 eventos, 4 janelas, Sentinela recebeu 4 |
| `node scripts/iped_journey_gate.mjs --base-url http://localhost:18000` | OK |
| `scripts/verify_iped_real_environment.ps1` | 0 falhas, 4 avisos |

## Bugs Encontrados E Corrigidos

### 1. Login autenticava, mas a tela ficava presa

Sintoma: apos clicar em entrar, o botao ficava em `Entrando...` e a tela de login permanecia visivel.

Causa: o CSS novo da identidade visual usava `display: grid !important` no login. O JavaScript antigo tentava esconder o login com `style.display = 'none'`, mas perdia para o `!important`.

Correcao ja presente na base auditada:
- uso da classe `body.sentinela-authenticated`;
- regra CSS `body.sentinela-authenticated #login-screen.sentinela-lab-login { display: none !important; }`;
- logout/restauracao removem a classe e devolvem o login.

Teste adicionado:
- `test_phase6_login_transition_uses_authenticated_state_not_inline_display`
- `test_sentinela_login_not_hybrid_after_authentication`

### 2. Titulo hero do login nao acompanhava idioma

Sintoma: `Governanca longitudinal da exposicao em pericia digital` permanecia fixo ao trocar PT/EN/ES.

Correcao:
- `h2` recebeu `data-i18n="heroTitle"`;
- chaves `heroTitle` adicionadas em PT/EN/ES.

Teste adicionado:
- `test_phase6_login_hero_title_is_localized_in_all_supported_languages`
- `test_login_i18n_has_no_fixed_hero_title`

### 3. `python -m pytest -q` na raiz quebrava por colisao de pacotes

Sintoma: a raiz coletava testes de varios subprojetos que usam pacote `src`, misturando imports entre Sentinela, SUPREME backend e outro checkout local.

Correcao:
- criado `pytest.ini` na raiz;
- criado `tests/test_workspace_health.py`, que roda cada subprojeto isoladamente;
- `--basetemp` local por subprojeto evita falhas de permissao em temporarios.

Resultado:
- `python -m pytest -q` agora passa na raiz.

### 4. Gate de jornada IPED usava identificador invalido

Sintoma: `scripts/iped_journey_gate.mjs` falhava com HTTP 422 ao ingerir `session_start/session_end`.

Causa: o script usava `journey-gate-${Date.now()}` como `user_identifier`, mas o contrato de ingestao exige pseudonimo SHA-256 hex64.

Correcao:
- adicionado `pseudonymize()` com `node:crypto`;
- `idHash` agora e hex64;
- erro HTTP agora imprime detalhe JSON util.

Teste adicionado:
- `test_iped_journey_gate_uses_hex64_pseudonym_for_ingest_events`

## Status Por Area

### Login

Status: OK

- login valido autentica;
- `/api/auth/me` retorna usuario `master`;
- logout funciona;
- tela de login nao sobrepoe o console apos autenticacao;
- botao nao fica preso em loading nos testes de API/runtime.

### Internacionalizacao

Status: OK

- PT/EN/ES cobertos para hero/login;
- titulo principal do login nao esta mais hardcoded;
- sintaxe JS validada.

### Sentinela Frontend

Status: OK para publicacao controlada

- pagina `/sentinela` retorna 200;
- CSS de login escuro e estado autenticado protegidos por teste;
- dashboards principais respondem 200 apos login;
- nao foi encontrado vazamento critico no secret scan.

### Questionarios Psicométricos

Status: OK em fluxo sintetico controlado

- gate validou pre-sessao antes da liberacao;
- PANAS permanece somente como pos-sessao;
- gerar links nao marca instrumentos como submetidos;
- submissao chega ao SUPREME e a Sentinela.

### IPED

Status: ambiente detectado, validacao real pendente

- IPED real detectado em ambiente local;
- launcher/JAR IPED encontrado;
- patch Java SUPREME detectado;
- `IPED_AUDIT_DIR` aponta para o arquivo esperado;
- pendencia: `supreme_audit.ndjson` real ainda nao existe nesta sessao auditada.

### Integracao SUPREME -> Sentinela

Status: OK em E2E sintetico seguro

- 8 eventos sinteticos ingeridos;
- 4 janelas calculadas;
- pipeline status `ok`;
- Sentinela recebeu 4 janelas.

### Docker

Status: OK

Servicos relevantes em execucao:
- `supreme-api`: healthy;
- `sentinela`: healthy;
- `supreme-db`: healthy;
- `sentinela-db`: healthy;
- `supreme-redis`: healthy;
- watcher/proxy presentes no stack local.

## Auditoria De Seguranca E Sanitizacao

Status: OK para publicacao controlada

- `scripts/secret_scan.ps1`: 0 critical findings;
- nao foram commitados dados reais, outputs locais, tokens, secrets ou midia nova;
- `.env`, outputs locais e temporarios seguem ignorados;
- os dados usados nos gates sao pseudonimos ou eventos sinteticos.

Observacao: alguns arquivos de exemplo usam placeholders `dev_`, `test_` ou `CHANGE_ME`, o que e esperado para templates.

## Bloqueios E Pendencias Reais

1. `ruff` nao esta instalado neste ambiente.
   - Impacto: lint formal nao executado.
   - Mitigacao: testes, `node --check`, `git diff --check` e secret scan executados.

2. `supreme_audit.ndjson` real ainda nao foi gerado por uma sessao IPED patched.
   - Impacto: publicacao controlada OK, validacao de campo real ainda pendente.
   - Proxima acao: abrir IPED pelo launcher patched, trabalhar em uma sessao autorizada e confirmar geracao de eventos reais sanitizados.

3. O verificador IPED real reportou avisos sobre checagem de compose por contexto/projeto.
   - Impacto: nao bloqueante, pois `docker ps` mostrou os servicos do projeto local em execucao e saudaveis.

## Checklist Final

- [x] Login valido funciona.
- [x] Login nao fica preso em `Entrando...`.
- [x] Logout e restauracao de sessao possuem estado visual seguro.
- [x] Internacionalizacao do hero/login coberta.
- [x] Sentinela nao exibe login hibrido no estado autenticado.
- [x] Questionarios pre/pos-sessao validados em gate sintetico.
- [x] PANAS permanece restrito ao pos-sessao.
- [x] Gate IPED usa pseudonimo hex64 valido.
- [x] E2E SUPREME -> Sentinela passou.
- [x] Secret scan sem achados criticos.
- [x] Testes passam por subprojeto e pela raiz.
- [ ] `ruff` pendente por ferramenta ausente.
- [ ] Sessao IPED real com `supreme_audit.ndjson` pendente.

## Conclusao

O sistema esta saudavel para publicacao controlada do pacote de pesquisa e demonstracao operacional local. A publicacao nao deve afirmar validacao de campo real ate que uma sessao IPED real patched gere `supreme_audit.ndjson`, seja ingerida, e os resultados sejam registrados em relatorio de campo.
