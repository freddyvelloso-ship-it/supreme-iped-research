# UI/UX Full Audit Report

Data/hora da auditoria: 2026-07-02, America/Sao_Paulo

Branch/local auditado: `main`, clone local em `C:\Users\nunas\Documents\Codex\2026-06-27\co\work\supreme-iped-research`

URL testada:
- `http://localhost:18001/sentinela`
- `http://localhost:18001/sentinela/static/war_room.html?audit=uiux-20260702`

Decisao final: `ui_publication_blocked`

## Estado Do Working Tree

O clone local ja estava com alteracoes nao commitadas antes desta auditoria:

- `sentinela/static/index.html`
- `sentinela/static/sentinela-ux.js`
- `sentinela/static/war_room.html`

Nenhuma correcao de UI foi aplicada nesta auditoria. Este arquivo foi criado apenas para registrar o diagnostico.

## Arquivos Auditados

- `sentinela/static/index.html`
- `sentinela/static/sentinela-ux.js`
- `sentinela/static/sentinela-lab-primary.css`
- `sentinela/static/sentinela-redesign.css`
- `sentinela/static/war_room.html`
- `sentinela/tests/test_phase6_product.py`
- `tests/test_publication_static_health.py`

## Telas Auditadas

- Login
- Visao Geral
- Menu principal
- Troca de idioma PT/EN/ES
- Participantes
- Dossie/painel de participante
- War Room
- KPIs do War Room
- Distribuicao de Convergencia
- Serie Temporal IEO x PSI
- Relatorio tecnico

## Evidencias De Execucao

Comandos executados:

```powershell
git status --short --branch
rg -n "Participante|KPIs em Tempo Real|Série Temporal|Distribuição de Convergência|Próximas ações|Revisar participante|Red flags críticas|Gerar relatório|data-war-i18n|sidePanel|bottom|modal|drawer|locale|i18n" sentinela/static sentinela/tests tests
C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe --check sentinela\static\sentinela-ux.js
git diff --check
C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest sentinela\tests -q
C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest tests\test_publication_static_health.py -q
Invoke-WebRequest -UseBasicParsing http://localhost:18001/health
Invoke-WebRequest -UseBasicParsing http://localhost:18001/sentinela/static/war_room.html
```

Resultados:

- `node --check sentinela/static/sentinela-ux.js`: passou.
- `git diff --check`: passou, com avisos de LF/CRLF em `index.html` e `war_room.html`.
- `pytest sentinela/tests`: bloqueado no ambiente local porque o Python informado nao tem `pytest` instalado.
- `pytest tests/test_publication_static_health.py`: bloqueado pelo mesmo motivo.
- `/health`: respondeu `{"status":"ok","service":"sentinela"}`.
- `/sentinela/static/war_room.html`: HTTP 200.
- Endpoints `/api/dashboard/overview` e `/api/dashboard/participants` responderam `Sessao ausente` quando chamados fora da sessao autenticada do navegador, comportamento esperado para chamada direta sem cookie.

## Bugs Criticos

### 1. Painel "Participante" aparece como bloco inferior no War Room

Severidade: critico.

Evidencia visual: a tela mostra um bloco inferior com titulo `Participante`, botao `x` e spinner/carregamento, mesmo sem abertura valida de dossie.

Evidencia DOM:

- `#sidePanel` existe no War Room.
- `#sidePanel` nao estava com classe `.open`.
- Mesmo assim, seu retangulo apareceu no fluxo da pagina:
  - `position: relative`
  - `display: block`
  - `y: 1177`
  - `h: 155`
  - `transform: matrix(1, 0, 0, 1, 520, 0)`

Provavel causa tecnica:

- `sentinela/static/war_room.html` define `.side-panel` como painel fixo lateral.
- `sentinela/static/sentinela-redesign.css` possui regra global:

```css
.modal,
#rpt-modal,
#side-panel,
.side-panel {
  position: relative !important;
  overflow: hidden !important;
}
```

Essa regra global atinge tambem `.side-panel` do War Room. Como o War Room usa `.side-panel` sem namespace, o painel deixa de ser drawer fixo e entra no fluxo da pagina.

Arquivos provaveis envolvidos:

- `sentinela/static/war_room.html`
- `sentinela/static/sentinela-redesign.css`

Plano recomendado:

1. Isolar CSS do War Room com namespace proprio ou remover dependencia do CSS global da Sentinela.
2. Renomear `.side-panel` do War Room para classe especifica, por exemplo `.war-side-panel`.
3. Garantir que painel fechado tenha `display: none` ou fique fora do fluxo.
4. Adicionar teste estatico garantindo que `.side-panel` generico nao vaze para War Room.

### 2. War Room esta com encoding/mojibake em texto e icones

Severidade: critico.

Evidencia textual em arquivo/DOM:

- `MÃ©dio`
- `DistribuiÃ§Ã£o`
- `ConvergÃªncia`
- `ðŸ—‚`
- `â†’`
- `Â·`

Impacto:

- A interface nao esta publicavel em portugues.
- A traducao fica instavel porque parte do texto dinamico nasce corrompida.
- Icones e setas quebradas pioram a percepcao de produto.

Arquivos provaveis envolvidos:

- `sentinela/static/war_room.html`

Plano recomendado:

1. Regravar `war_room.html` em UTF-8 limpo.
2. Substituir caracteres corrompidos por texto correto ou entidades seguras.
3. Adicionar teste estatico contra padroes `MÃ`, `Ã£`, `Â`, `â`, `ð`.

## Bugs Altos

### 3. Internacionalizacao incompleta no console principal

Severidade: alto.

Evidencia apos login:

Mesmo tentando mudar idioma, permaneceram em PT:

- `Próximas ações`
- `humano`
- `Revisar participante`
- `Red flags críticas`
- `Gerar relatório`
- `Visão Geral`
- `Participantes`
- `Relatório`
- `Gestão longitudinal da exposição`

Provavel causa tecnica:

- Ha duas camadas competindo:
  - `sentinela-ux.js` cria o shell visual e os textos do bloco operacional.
  - `index.html` tenta aplicar uma camada `RUNTIME_FALLBACK_COPY`.
- `labOverviewHtml()` em `sentinela-ux.js` gera textos dinamicamente a partir de `c.foc`.
- A camada runtime em `index.html` tenta corrigir depois, mas nao e a fonte unica da verdade.
- Ha dois conjuntos de botoes de idioma PT/EN/ES visiveis no DOM: login e app. Isso aumenta o risco de seletor ambiguo, flicker e estado divergente.

Arquivos provaveis envolvidos:

- `sentinela/static/index.html`
- `sentinela/static/sentinela-ux.js`

Plano recomendado:

1. Consolidar uma unica fonte de i18n para o console.
2. Evitar `Object.assign` corretivo no HTML se `sentinela-ux.js` ja possui o dicionario.
3. Garantir que `applyLocale()` atualize textos dinamicos e nao apenas `[data-i18n]`.
4. Reduzir duplicidade visual dos botoes de idioma ou escopar corretamente login/app.

### 4. Internacionalizacao incompleta no War Room

Severidade: alto.

Evidencia no War Room:

Continuam estaticos ou parcialmente estaticos:

- `Participantes Ativos`
- `total no estudo`
- `IEO Medio (ultima janela)`
- `Indice de Exposicao Ocupacional`
- `PSI Medio (ultima janela)`
- `Pressao Psicometrica Integrada`
- `Red Flags Ativas`
- `flags em monitoramento`
- `Baseline`
- `Carga Residual`
- `Convergencia`
- `Divergencia`
- `Clique em ... para ordenar`
- `Carregando participantes...`
- textos do relatorio tecnico gerado dinamicamente

Provavel causa tecnica:

- O War Room mistura:
  - HTML estatico em PT.
  - `WAR_ROOM_I18N`.
  - `WAR_ROOM_STATIC_COPY`.
  - strings PT hardcoded dentro de funcoes como `buildReportHTML()`, `buildNarrative()`, `renderLongitudinal()`, `openParticipant()` e handlers de erro.
- `applyWarRoomLocale()` nao cobre todos os seletores, e algumas funcoes renderizam texto apos a aplicacao de locale.

Arquivos provaveis envolvidos:

- `sentinela/static/war_room.html`

Plano recomendado:

1. Transformar War Room em uma view i18n-first.
2. Adicionar `data-war-i18n` aos elementos estaticos.
3. Remover hardcoded PT dos templates dinamicos.
4. Chamar `applyWarRoomLocale()` apos cada render que altera DOM.
5. Criar teste que troca PT/EN/ES e verifica ausencia dos principais termos PT quando EN esta ativo.

### 5. Flicker/duplicidade na troca de idioma

Severidade: alto.

Evidencia:

- Ha dois grupos de botoes `button[data-locale]` visiveis no DOM.
- A tentativa de acionar EN encontrou duplicidade.
- A troca de idioma foi percebida pelo usuario como "pisca".

Provavel causa tecnica:

- Login e app shell mantem switches simultaneamente no DOM.
- A troca de idioma re-renderiza componentes do shell, nav e blocos dinamicos.
- Alguns textos sao escritos pela camada nova e depois reescritos pela camada antiga.

Arquivos provaveis envolvidos:

- `sentinela/static/index.html`
- `sentinela/static/sentinela-ux.js`

Plano recomendado:

1. Escopar switches por container visivel.
2. Evitar re-render completo do shell para simples troca de copy.
3. Atualizar apenas texto, sem recriar blocos estruturais quando possivel.

## Bugs Medios

### 6. Cards de convergencia visualmente amontoados

Severidade: medio.

Evidencia visual:

- Cards de `BASELINE`, `CARGA RESIDUAL`, `CONVERGENCIA` e `DIVERGENCIA` aparecem com texto colado, destaque azul agressivo e muito espaco vazio dentro dos cards.
- A hierarquia visual e ruim: numero, percentual e descricao competem pelo mesmo bloco.

Provavel causa tecnica:

- CSS global da Sentinela aplica estilos de card de outra identidade visual.
- War Room tem CSS proprio, mas recebe override externo.
- Tamanho minimo, padding e labels nao estao calibrados para dados vazios.

Arquivos provaveis envolvidos:

- `sentinela/static/war_room.html`
- `sentinela/static/sentinela-redesign.css`
- `sentinela/static/sentinela-lab-primary.css`

Plano recomendado:

1. Remover vazamento de CSS global sobre War Room.
2. Ajustar grid de convergencia com altura minima estavel e labels separadas.
3. Criar estado vazio visual correto para valores zero.

### 7. Grafico IEO x PSI aparece vazio sem estado explicativo forte

Severidade: medio.

Evidencia visual:

- Area de grafico aparece branca/vazia no War Room.
- Nao ha mensagem clara de "sem dados na janela atual" no proprio grafico.

Provavel causa tecnica:

- O canvas e renderizado mesmo quando os endpoints retornam dataset vazio.
- Estado vazio nao substitui a area grafica.

Arquivos provaveis envolvidos:

- `sentinela/static/war_room.html`

Plano recomendado:

1. Quando series vierem vazias, substituir canvas por empty state.
2. Distinguir "sem dados" de "erro de API" e "carregando".

### 8. Termos de dominio misturam "participante", "perito" e "digital forensics expert"

Severidade: medio.

Evidencia:

- Console principal usa `Participantes`.
- Historico e dossie usam `Participante`.
- Conversa de produto exige "digital forensics experts" em partes da UI.

Impacto:

- A experiencia internacional fica inconsistente.
- O usuario pode nao entender se o acompanhamento e de participante de estudo, perito, ou expert pseudonimizado.

Arquivos provaveis envolvidos:

- `sentinela/static/index.html`
- `sentinela/static/sentinela-ux.js`
- `sentinela/static/war_room.html`

Plano recomendado:

1. Definir vocabulário por contexto:
   - PT: "Peritos digitais" ou "Participantes do estudo", mas nao alternar sem criterio.
   - EN: "Digital forensics experts" quando o publico for operacional.
2. Centralizar labels em i18n.

## Bugs Baixos

### 9. Avisos LF/CRLF no diff check

Severidade: baixo.

Evidencia:

- `git diff --check` passou, mas emitiu avisos de LF/CRLF para:
  - `sentinela/static/index.html`
  - `sentinela/static/war_room.html`

Plano recomendado:

1. Definir `.gitattributes` para normalizar arquivos web como LF.
2. Evitar commits com churn de line ending.

## Componentes Antigos Ainda Ativos

Foram encontrados seletores e camadas antigas/concorrentes:

- `.forensic-console`
- `.sentinela-lab-primary`
- `.ux-decision-panel`
- `.foc-command-panels`
- `.foc-zone-title`
- `.foc-sidebar-brand`
- regras globais para `.modal`, `.side-panel`, `.card`, `.kpi-card`

Risco:

- A UI nova e a UI antiga ainda competem por shell, cards, paineis, modal e navegacao.
- Isso explica "layout antigo reaparecendo", "visual hibrido" e "painel preso".

## Conflitos CSS/JS

Principais conflitos:

1. CSS global de `sentinela-redesign.css` atinge War Room por seletores genericos.
2. `sentinela-lab-primary.css` e `sentinela-redesign.css` ambos possuem regras para dossier/painel.
3. `index.html` e `sentinela-ux.js` ambos tentam controlar runtime i18n.
4. `war_room.html` possui i18n proprio, mas tambem carrega `sentinela-ux.js`.

## Problemas De Responsividade

Nao foi executada uma matriz visual completa de viewport nesta rodada, mas os problemas ja detectados sao independentes de largura:

- painel fechado entra no fluxo da pagina;
- cards de convergencia ficam amontoados;
- CSS global altera posicao de modais/drawers;
- botoes de idioma duplicados causam ambiguidade.

Recomendacao:

- Na etapa de correcao, validar explicitamente desktop, notebook e largura estreita.

## Ordem Segura De Correcao Recomendada

1. Congelar estado atual e nao adicionar feature.
2. Separar War Room da folha global que muda `.side-panel`, `.modal`, `.card` e `.kpi-card`.
3. Corrigir o painel inferior `Participante` garantindo que painel fechado nao ocupa layout.
4. Corrigir encoding UTF-8 do `war_room.html`.
5. Centralizar i18n do console principal em uma fonte unica.
6. Centralizar i18n do War Room e remover strings hardcoded PT dos renders dinamicos.
7. Corrigir empty states dos graficos e cards.
8. Ajustar UX dos cards de convergencia.
9. Rodar testes estaticos e browser smoke test.
10. So entao avaliar publicacao.

## O Que Nao Deve Ser Mexido Agora

- Regras de negocio do SUPREME.
- Calculo IEO/OEI.
- Calculo PSI.
- Gate de producao.
- Guardrails de nao diagnostico, nao ranking, nao produtividade e nao disciplina.
- Fluxo IPED.
- Backend, exceto se for comprovado que um endpoint visual esta quebrado.
- Dados reais ou dados locais de teste.

## Decisao

`ui_publication_blocked`

Motivo: ha bugs visuais e de estado em tela principal de produto, i18n incompleto, encoding quebrado no War Room e vazamento de CSS global que transforma o painel de participante em bloco inferior visivel.

O produto nao deve ser publicado visualmente ate a camada Sentinela/War Room ser estabilizada como uma UI unica, sem CSS/JS concorrente e com i18n centralizado.

## Correções Locais Aplicadas

Data/hora: 2026-07-02, America/Sao_Paulo

Escopo: correções aplicadas somente no clone local e copiadas para o container local `supreme-v4-test-clone-sentinela-1` para teste manual. Nao houve commit e nao houve push.

### Arquivos Alterados

- `sentinela/static/war_room.html`
- `sentinela/static/index.html`
- `sentinela/static/sentinela-ux.js`
- `tests/test_publication_static_health.py`
- `docs/UI_UX_FULL_AUDIT_REPORT.md`

### Bugs Corrigidos

1. Painel inferior `Participante` no War Room:
   - Removida a dependencia do War Room sobre `/sentinela/static/sentinela-redesign.css`.
   - O drawer de participante do War Room foi isolado com classes proprias:
     - `.war-side-panel`
     - `.war-side-panel-overlay`
     - `.war-side-panel-header`
     - `.war-side-panel-body`
   - O painel fechado agora permanece `position: fixed`, fora do fluxo visual, com `visibility: hidden` e sem conteudo inicial.

2. War Room com i18n incompleto:
   - Adicionada cobertura explicita para KPIs, distribuicao de convergencia, serie temporal, filtros, tabela, drawer de participante e estados vazios.
   - Titulos criticos agora usam `data-war-i18n` em vez de seletores frageis por posicao.
   - `applyWarRoomLocale()` e reaplicado apos render dinamico de overview/convergencia.

3. Grafico vazio no War Room:
   - `renderMissaoChart()` agora destrói canvas anterior e mostra estado vazio quando nao houver serie.
   - Estado vazio: `Sem dados suficientes nesta janela` / `Not enough data in this window` / `No hay datos suficientes en esta ventana`.

4. Console principal com termos presos em PT:
   - A camada runtime agora fornece traducoes para os textos criticos do bloco operacional:
     - `Próximas ações`
     - `humano`
     - `Revisar participante`
     - `Red flags críticas`
     - `Gerar relatório`
     - integridade/custodia
   - `applyRuntimeLocaleText()` agora prefere esses textos runtime por locale antes de cair no `foc`.

5. Regressao estatica:
   - `tests/test_publication_static_health.py` ganhou verificacoes para:
     - War Room nao importar `sentinela-redesign.css`;
     - War Room nao usar `.side-panel` generico;
     - War Room possuir i18n de KPIs/convergencia/estado vazio.

### Validação Executada

Comandos:

```powershell
C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe --check sentinela\static\sentinela-ux.js
C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe -e "const fs=require('fs'); const html=fs.readFileSync('sentinela/static/war_room.html','utf8'); const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]); scripts.forEach((s,i)=>{new Function(s);}); console.log('inline scripts ok', scripts.length);"
git diff --check
Invoke-WebRequest -UseBasicParsing http://localhost:18001/health
Invoke-WebRequest -UseBasicParsing http://localhost:18001/sentinela/static/war_room.html
docker cp sentinela\static\index.html supreme-v4-test-clone-sentinela-1:/app/static/index.html
docker cp sentinela\static\sentinela-ux.js supreme-v4-test-clone-sentinela-1:/app/static/sentinela-ux.js
docker cp sentinela\static\war_room.html supreme-v4-test-clone-sentinela-1:/app/static/war_room.html
```

Resultados:

- `node --check sentinela/static/sentinela-ux.js`: passou.
- Checagem de scripts inline do `war_room.html`: passou, `inline scripts ok 3`.
- `git diff --check`: passou, com avisos LF/CRLF em arquivos modificados.
- `/health`: `{"status":"ok","service":"sentinela"}`.
- `/sentinela/static/war_room.html`: HTTP 200.
- `pytest sentinela/tests -q`: nao executou porque o Python indicado nao possui `pytest` instalado.
- `pytest tests/test_publication_static_health.py -q`: nao executou pelo mesmo motivo.

### Validação Manual/Local No Navegador

URL validada:

- `http://localhost:18001/sentinela`
- `http://localhost:18001/sentinela/static/war_room.html?fresh=ui-fix-20260702-b`

Credenciais locais:

- `local.master@supreme.local`
- `supreme-local-admin`

Resultado observado:

- Console principal autenticado sem login sobreposto.
- Troca para EN atualizou os termos criticos:
  - `Next actions`
  - `Review participant`
  - `Generate report`
  - `Overview`
  - `Longitudinal exposure management`
- Troca para ES atualizou os termos criticos:
  - `Próximas acciones`
  - `Generar informe`
  - `Vista General`
- War Room em EN:
  - sem painel `Participant` no rodape;
  - `#sidePanel` permanece fechado, `position: fixed`, `visibility: hidden`;
  - sem mojibake visivel no texto renderizado;
  - KPIs, convergencia e serie temporal traduzidos;
  - estado vazio do grafico exibido como `Not enough data in this window`.
- War Room em ES:
  - KPIs, convergencia, serie temporal e estado vazio traduzidos;
  - sem termos PT criticos detectados na amostra visual.

### Pendências

- `pytest` precisa estar instalado no Python indicado para validar a suite automatizada completa localmente.
- Os avisos LF/CRLF permanecem como baixa severidade e podem ser tratados depois com `.gitattributes`.
- O relatorio tecnico gerado pelo War Room ainda contem uma grande quantidade de texto narrativo e deve receber uma etapa dedicada de i18n completa antes de publicacao internacional final.

### Decisão Final Local

`ui_local_test_ready`

Motivo: os bloqueios visuais centrais foram corrigidos localmente: painel inferior removido, War Room sem mojibake visivel na tela principal, PT/EN/ES funcionando nos fluxos principais, estados vazios claros e UI nova dominante no console. A publicacao oficial ainda deve aguardar execucao da suite `pytest` em ambiente com dependencia instalada.
