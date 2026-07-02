(function () {
  "use strict";

  const LOCALES = [
    { code: "pt-BR", label: "PT" },
    { code: "en-US", label: "EN" },
    { code: "es-ES", label: "ES" },
  ];

  const JURISDICTIONS = [
    { id: "BR", label: { "pt-BR": "Brasil", "en-US": "Brazil", "es-ES": "Brasil" } },
    { id: "EU", label: { "pt-BR": "União Europeia", "en-US": "European Union", "es-ES": "Unión Europea" } },
    { id: "US", label: { "pt-BR": "EUA", "en-US": "United States", "es-ES": "Estados Unidos" } },
    { id: "INT", label: { "pt-BR": "Internacional", "en-US": "International", "es-ES": "Internacional" } },
  ];

  const I18N = {
    "pt-BR": {
      brand: "Sentinela",
      loginSub: "SUPREME Longitudinal Console",
      accessTitle: "Acesso restrito",
      accessBody: "Entre para revisar sinais agregados, bloqueios de governança e evidências longitudinais.",
      heroBadge: "Ambiente local seguro",
      heroTitle: "Governança longitudinal da exposição em perícia digital",
      heroBody: "Centro visual para IEO/OEI, PSI, baselines, red flags e evidências, exibindo apenas dados analíticos pseudonimizados.",
      loginEmailLabel: "Identificação",
      loginPasswordLabel: "Chave de acesso",
      rememberAccess: "Lembrar acesso neste dispositivo",
      loginButton: "Entrar no console",
      noClinicalTitle: "Sem diagnóstico automático",
      noClinicalBody: "O console apoia governança e revisão humana.",
      privacyTitle: "Privacidade por desenho",
      privacyBody: "Sem mídia, paths ou identificadores crus.",
      logout: "Sair",
      warRoom: "War Room",
      topbarTitle: "Gestão longitudinal da exposição",
      topbarSubtitle: "IPED, IEO/OEI, PSI, baseline, red flags e evidência operacional.",
      tabs: {
        overview: "Visão Geral",
        studies: "Estudos",
        pipeline: "Pipeline",
        dataquality: "Qualidade",
        ieo: "IEO",
        participants: "Participantes",
        flags: "Red Flags",
        psycho: "Psicométricos",
        history: "Histórico",
        baseline: "Baseline",
        longitudinal: "Longitudinal",
        exports: "Exportação",
        report: "Relatório",
      },
      foc: {
        zones: { command: "Central", case: "Acompanhamento", audit: "Evidência" },
        sidebarSubtitle: "Console longitudinal",
        jurisdictionAria: "Selecionar jurisdição",
        operationalStatus: "Status operacional",
        riskEvidenceMatrix: "Matriz IEO/OEI x PSI",
        nextActions: "Próximas ações",
        sessionFeed: "Linha operacional",
        custodyIntegrity: "Integridade",
        psychometricGate: "Gate psicométrico",
        dataQuality: "Qualidade dos dados",
        evidenceQueue: "Fila de evidências",
        scope: "Escopo atual",
        pipelineNominal: "Pipeline nominal",
        waitingIngestion: "Aguardando ingestão",
        lastIngestion: "Última ingestão",
        connected: "conectado",
        agent: "Agente",
        localAgent: "local ativo",
        lastSession: "Última sessão",
        waiting: "aguardando",
        custody: "Custódia",
        chainOk: "hash chain íntegra",
        events: "Eventos",
        data: "Dados",
        monitored: "monitorados",
        currentWindow: "janela atual",
        participants: "participantes",
        redFlags: "red flags",
        nominal: "nominal",
        dissonance: "dissonância",
        chronicity: "cronicidade",
        reactivity: "reatividade",
        noData: "sem dado",
        queue: "fila",
        reviewParticipant: "Revisar participante",
        openStudy: "Abrir estudo",
        generateReport: "Gerar relatório",
        verifyCollectionFailure: "Verificar coleta",
        ipedAgent: "IPED/agente",
        ingestionActive: "Ingestão ativa",
        manifestValid: "Manifesto válido",
        replayAvailable: "Replay disponível",
        verifiable: "verificável",
        signatureVerified: "Assinatura verificada",
        ipedRegistered: "IPED registrado",
        session: "sessão",
        completed: "concluído",
        postSession: "pós-sessão",
        control: "controle",
        validWindows: "Janelas válidas",
        gapsMonitored: "Lacunas monitoradas",
        lowQuality: "Baixa qualidade",
        discardedEvents: "Eventos descartados",
        human: "humano",
        criticalFlags: "Red flags críticas",
        psychometricDissonance: "Dissonância psicométrica",
        degradedIntegrity: "Integridade degradada",
        elevatedRisk: "Risco agregado elevado",
        overviewSub: "Leitura intraindividual, risco agregado e próxima ação responsável.",
        studiesSub: "Instituição, estudo, caso, coleta e integridade.",
        participantsSub: "Acompanhamento por participante pseudonimizado.",
      },
      pipeline: {
        title: "Saúde do Pipeline",
        sub: "Estado de ingestão e disponibilidade dos outputs recebidos do SUPREME",
        checks: "Checagens",
        loading: "Carregando...",
        noChecks: "Sem checagens disponíveis.",
        ok: "ok",
        noData: "sem dado",
        labels: {
          supreme_outputs_present: "outputs SUPREME presentes",
          psychometric_outputs_present: "outputs psicométricos presentes",
          red_flags_present: "red flags presentes",
        },
      },
      workspace: {
        overviewDeepTitle: "Detalhes operacionais",
        overviewDeepSub: "Gráficos de apoio",
        chartSeries: "Evolução IEO x PSI",
        chartConvergence: "Distribuição de convergência",
        chartFlags: "Red Flags por tipo",
        studiesHeaders: ["Instituição", "Estudo", "Caso", "Perito", "Coleta", "Participantes", "Sessões IPED", "Último evento", "Integridade", "Ações"],
        participantsHeaders: ["ID", "Grupo", "Psicometria", "Comportamental", "Perfil", "Red Flags", "Qualidade", "Última sessão", "Janelas", "Ação"],
        studiesEmpty: "Nenhum estudo ativo no escopo atual. Aguardando primeira sessão IPED processada.",
        participantsEmpty: "Nenhum participante em atenção. Aguardando baseline e sessões válidas.",
        unassigned: "não atribuído",
        notInformed: "não informado",
        none: "nenhum",
        collectionComplete: "Sessão encerrada",
        insufficientData: "Dado insuficiente",
        integrityOk: "Hash chain íntegra",
        integrityPending: "Integridade pendente",
        open: "Abrir",
        export: "Exportar",
        openDossier: "Abrir dossiê",
        panasPending: "PANAS pendente",
        noWindow: "sem janela",
        profileInsufficient: "Dado insuficiente",
        profileOperational: "operacional longitudinal",
        noProfile: "Sem perfil longitudinal recebido do SUPREME. Classificação indisponível para esta pessoa.",
      },
      report: {
        title: "Relatório Técnico",
        sub: "Relatório operacional auditável em formato imprimível",
        cardTitle: "Relatório Técnico SUPREME V4",
        cardBody: "Gera relatório narrativo com dados do estudo: IEO, PSI, red flags, convergência, participantes e recomendações.",
        generate: "Gerar relatório completo",
        hint: "Busca dados dos endpoints, gera relatório narrativo e permite impressão/PDF",
        modalTitle: "Relatório Técnico — SUPREME V4",
        modalSub: "Programa de Pesquisa · Exposição Ocupacional em Perícia Digital",
        print: "Imprimir / PDF",
        copy: "Copiar texto",
        close: "Fechar",
        copied: "Relatório copiado para a área de transferência.",
        copyManual: "Selecione e copie manualmente.",
        notInformed: "não informado",
        noFlags: "SEM FLAGS ATIVAS",
        outputStatus: "Status do Output",
        outputSub: "SENTINELA visualiza outputs auditáveis calculados pelo SUPREME",
        sections: {
          narrative: "Laudo Narrativo",
          identification: "Identificação do Estudo",
          methodology: "Metodologia",
          global: "Resultado Global",
          participants: "Análise por Participante — Última Janela",
          redFlags: "Red Flags — Registro Completo",
          longitudinal: "Análise Longitudinal",
          recommendations: "Recomendações",
          auditability: "Auditabilidade e Limitações",
        },
        fields: {
          value: "Valor",
          status: "Status",
          class: "Classe",
          description: "Descrição",
          severity: "Severidade",
          participant: "Participante",
          window: "Janela",
          detail: "Detalhe",
          trend: "Tendência",
          analyzedWindows: "Janelas analisadas",
          system: "Sistema",
          generated: "Gerado em",
          clinicalDiagnosis: "Diagnóstico clínico",
          causalNexus: "Nexo causal",
          autonomousDecisions: "Decisões autônomas",
        },
        values: {
          valueFromSupreme: "Valor recebido do SUPREME",
          recordsFromSupreme: "Registros recebidos do SUPREME",
          noClinical: "NÃO realizado",
          noCausal: "NÃO estabelecido",
          noAutonomous: "NÃO — todas as ações dependem de responsável designado",
          noParticipants: "Nenhum participante com dados disponíveis.",
          noRedFlags: "Nenhuma red flag registrada.",
          stable: "Estável",
          increasing: "Crescente — atenção redobrada",
          decreasing: "Decrescente — sinal positivo",
        },
        warning: "Este laudo é instrumento de gestão de risco — não constitui diagnóstico clínico, avaliação psicológica ou nexo causal.",
        auditLimit: "Os participantes são identificados por hash pseudonimizado. O uso deste relatório deve seguir os protocolos éticos aprovados.",
        signatures: {
          responsible: "Pesquisador Responsável / Data: ____________________",
          reviewer: "Revisor / Data: ____________________",
        },
        recommendations: [
          "Conferir os registros de red flag recebidos do SUPREME e registrar a decisão responsável.",
          "Manter IEO, PSI, convergência e red flags como outputs do backend SUPREME.",
          "Qualquer ação individual exige revisão humana e protocolo aprovado.",
        ],
        narrative: {
          title: "RELATÓRIO TÉCNICO AUDITÁVEL",
          frontier: "FRONTEIRA ANALÍTICA",
          viewerOnly: "O SENTINELA visualiza outputs calculados pelo backend SUPREME. Esta tela não recalcula IEO, PSI, convergência ou red flags.",
          algorithm: "Versão do algoritmo recebida:",
          outputs: "OUTPUTS RECEBIDOS",
          ieo: "IEO médio recebido na última janela:",
          psi: "PSI médio recebido na última janela:",
          flags: "Red flags recebidas:",
          distribution: "Distribuição de convergência recebida:",
          flagTypes: "Tipos de red flag recebidos:",
          trend: "Tendência longitudinal do IEO:",
          mean: "Média geral:",
          limitation: "Este relatório é instrumento operacional auditável. Não constitui diagnóstico clínico, avaliação psicológica, nexo causal ou decisão autônoma.",
        },
      },
    },
    "en-US": {
      brand: "Sentinel",
      loginSub: "SUPREME Longitudinal Console",
      accessTitle: "Restricted access",
      accessBody: "Sign in to review aggregate signals, governance locks and longitudinal evidence.",
      heroBadge: "Local secure environment",
      heroTitle: "Longitudinal governance of digital forensics exposure",
      heroBody: "Visual center for IEO/OEI, PSI, baselines, red flags and evidence, showing only pseudonymized analytic data.",
      loginEmailLabel: "Identification",
      loginPasswordLabel: "Access key",
      rememberAccess: "Remember access on this device",
      loginButton: "Enter console",
      noClinicalTitle: "No automatic diagnosis",
      noClinicalBody: "The console supports governance and mandatory human review.",
      privacyTitle: "Privacy by design",
      privacyBody: "No media, paths or raw identifiers.",
      logout: "Log out",
      warRoom: "War Room",
      topbarTitle: "Longitudinal exposure management",
      topbarSubtitle: "IPED, IEO/OEI, PSI, baseline, red flags and operational evidence.",
      tabs: {
        overview: "Overview",
        studies: "Studies",
        pipeline: "Pipeline",
        dataquality: "Quality",
        ieo: "IEO",
        participants: "Participants",
        flags: "Red Flags",
        psycho: "Psychometrics",
        history: "History",
        baseline: "Baseline",
        longitudinal: "Longitudinal",
        exports: "Export",
        report: "Report",
      },
    },
    "es-ES": {
      brand: "Sentinela",
      loginSub: "SUPREME Longitudinal Console",
      accessTitle: "Acceso restringido",
      accessBody: "Ingrese para revisar señales agregadas, bloqueos de gobernanza y evidencias longitudinales.",
      heroBadge: "Entorno local seguro",
      heroTitle: "Gobernanza longitudinal de la exposición en pericia digital",
      heroBody: "Centro visual para IEO/OEI, PSI, baselines, red flags y evidencias, mostrando solo datos analíticos seudonimizados.",
      loginEmailLabel: "Identificación",
      loginPasswordLabel: "Clave de acceso",
      rememberAccess: "Recordar acceso en este dispositivo",
      loginButton: "Entrar al console",
      noClinicalTitle: "Sin diagnóstico automático",
      noClinicalBody: "La consola apoya gobernanza y revisión humana obligatoria.",
      privacyTitle: "Privacidad por diseño",
      privacyBody: "Sin medios, paths ni identificadores crudos.",
      logout: "Salir",
      warRoom: "War Room",
      topbarTitle: "Gestión longitudinal de exposición",
      topbarSubtitle: "IPED, IEO/OEI, PSI, baseline, red flags y evidencia operacional.",
      tabs: {
        overview: "Vista General",
        studies: "Estudios",
        pipeline: "Pipeline",
        dataquality: "Calidad",
        ieo: "IEO",
        participants: "Participantes",
        flags: "Red Flags",
        psycho: "Psicométricos",
        history: "Histórico",
        baseline: "Baseline",
        longitudinal: "Longitudinal",
        exports: "Exportación",
        report: "Informe",
      },
    },
  };

  I18N["en-US"].foc = { ...I18N["pt-BR"].foc, zones: { command: "Command", case: "Follow-up", audit: "Evidence" }, operationalStatus: "Operational status", nextActions: "Next actions", custodyIntegrity: "Integrity", pipelineNominal: "Pipeline nominal", participants: "participants", redFlags: "red flags", currentWindow: "current window", reviewParticipant: "Review participant", openStudy: "Open study", generateReport: "Generate report", human: "human", criticalFlags: "Critical red flags", verifiable: "verifiable", chainOk: "Hash chain intact", manifestValid: "Valid manifest", signatureVerified: "Signature verified", overviewSub: "Intraindividual reading, aggregate risk and next responsible action.", studiesSub: "Institution, study, case, collection and integrity.", participantsSub: "Follow-up by pseudonymized participant." };
  I18N["en-US"].pipeline = { ...I18N["pt-BR"].pipeline, title: "Pipeline Health", checks: "Checks", loading: "Loading...", noChecks: "No checks available.", noData: "no data" };
  I18N["en-US"].workspace = { ...I18N["pt-BR"].workspace, overviewDeepTitle: "Operational details", overviewDeepSub: "Supporting charts", chartSeries: "IEO x PSI evolution", chartConvergence: "Convergence distribution", chartFlags: "Red flags by type" };
  I18N["en-US"].report = { ...I18N["pt-BR"].report, title: "Technical Report", generate: "Generate full report", print: "Print / PDF", copy: "Copy text", close: "Close" };

  I18N["es-ES"].foc = { ...I18N["pt-BR"].foc, zones: { command: "Central", case: "Seguimiento", audit: "Evidencia" }, operationalStatus: "Estado operacional", nextActions: "Proximas acciones", custodyIntegrity: "Integridad", pipelineNominal: "Pipeline nominal", participants: "participantes", redFlags: "red flags", currentWindow: "ventana actual", reviewParticipant: "Revisar participante", openStudy: "Abrir estudio", generateReport: "Generar informe", human: "humano", criticalFlags: "Red flags criticas", verifiable: "verificable", chainOk: "Hash chain integra", manifestValid: "Manifiesto valido", signatureVerified: "Firma verificada", overviewSub: "Lectura intraindividual, riesgo agregado y proxima accion responsable.", studiesSub: "Institucion, estudio, caso, recoleccion e integridad.", participantsSub: "Seguimiento por participante seudonimizado." };
  I18N["es-ES"].pipeline = { ...I18N["pt-BR"].pipeline, title: "Salud del Pipeline", checks: "Verificaciones", loading: "Cargando...", noChecks: "Sin verificaciones disponibles.", noData: "sin dato" };
  I18N["es-ES"].workspace = { ...I18N["pt-BR"].workspace, overviewDeepTitle: "Detalles operacionales", overviewDeepSub: "Gráficos de apoyo", chartSeries: "Evolución IEO x PSI", chartConvergence: "Distribución de convergencia", chartFlags: "Red flags por tipo" };
  I18N["es-ES"].report = { ...I18N["pt-BR"].report, title: "Informe Técnico", generate: "Generar informe completo", print: "Imprimir / PDF", copy: "Copiar texto", close: "Cerrar" };

  const NAV_META = {
    overview: { icon: "DB", zone: "command" },
    studies: { icon: "CS", zone: "case" },
    pipeline: { icon: "PL", zone: "command" },
    dataquality: { icon: "DQ", zone: "command" },
    ieo: { icon: "IE", zone: "command" },
    participants: { icon: "PT", zone: "case" },
    flags: { icon: "RF", zone: "command" },
    psycho: { icon: "PS", zone: "case" },
    history: { icon: "TL", zone: "audit" },
    baseline: { icon: "BL", zone: "audit" },
    longitudinal: { icon: "LG", zone: "audit" },
    exports: { icon: "EX", zone: "audit" },
    report: { icon: "RP", zone: "audit" },
  };

  function getCookie(name) {
    return document.cookie
      .split(";")
      .map((item) => item.trim())
      .find((item) => item.startsWith(name + "="))
      ?.split("=")[1];
  }

  function setCookie(name, value) {
    document.cookie = `${name}=${encodeURIComponent(value)}; path=/; max-age=31536000; samesite=strict`;
  }

  function normalizeLocale(locale) {
    return LOCALES.some((item) => item.code === locale) ? locale : "pt-BR";
  }

  let activeLocale = normalizeLocale(decodeURIComponent(getCookie("supreme_locale") || "pt-BR"));

  function copy() {
    return I18N[activeLocale] || I18N["pt-BR"];
  }

  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn, { once: true });
    } else {
      fn();
    }
  }

  function visible(el) {
    return !!el && getComputedStyle(el).display !== "none";
  }

  function shortText(id, fallback) {
    const el = document.getElementById(id);
    return el && el.textContent.trim() ? el.textContent.trim() : fallback;
  }

  function renderLanguageSwitches() {
    document.querySelectorAll(".global-lang-switch").forEach((wrap) => {
      wrap.innerHTML = "";
      LOCALES.forEach((item) => {
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = item.label;
        button.dataset.locale = item.code;
        button.classList.toggle("active", item.code === activeLocale);
        button.setAttribute("aria-pressed", item.code === activeLocale ? "true" : "false");
        button.addEventListener("click", () => {
          activeLocale = item.code;
          setCookie("supreme_locale", activeLocale);
          applyLocale();
        });
        wrap.appendChild(button);
      });
    });
  }

  function updateTextNodes() {
    const c = copy();
    document.documentElement.lang = activeLocale;
    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      if (c[key]) el.textContent = c[key];
    });
    document.querySelectorAll(".nav-tab").forEach((tab) => {
      const id = tab.dataset.tab;
      const text = c.tabs[id];
      if (!id || !text) return;
      const label = tab.querySelector(".sentinela-nav-text");
      if (label) label.textContent = text;
      else tab.textContent = text;
    });
    document.querySelectorAll(".section").forEach((section) => {
      const id = section.id.replace("section-", "");
      const title = section.querySelector(":scope > .section-title");
      if (title && c.tabs[id]) title.textContent = c.tabs[id];
    });
    if (Array.isArray(window.TABS)) {
      window.TABS.forEach((tab) => {
        if (c.tabs[tab.id]) tab.label = c.tabs[tab.id];
      });
    }
  }

  function ensureLabShell() {
    document.body.classList.add("sentinela-lab-primary");
    document.body.classList.remove("forensic-console");
    document.querySelectorAll(".ux-decision-panel, .ux-filter-brief, .ux-command-cycle, .foc-command-panels, .foc-zone-title, .foc-sidebar-brand, .foc-topbar-strip, #foc-jurisdiction-switch").forEach((node) => node.remove());
  }

  function enhanceHeader() {
    const headerTop = document.querySelector(".header-top");
    const meta = document.querySelector(".header-meta");
    if (!headerTop || !meta || document.getElementById("lab-context-strip")) return;
    const c = copy();
    const strip = document.createElement("div");
    strip.id = "lab-context-strip";
    strip.className = "lab-context-strip";
    strip.innerHTML = `
      <span><b>SUPREME</b><em>IPED Research</em></span>
      <span><b>SENTINELA</b><em>${c.topbarTitle}</em></span>
      <span><b>STATUS</b><em>${c.foc.pipelineNominal}</em></span>
      <span><b>GUARDRAILS</b><em>no diagnosis · no ranking</em></span>
    `;
    headerTop.insertBefore(strip, meta);
  }

  function enhanceNav() {
    const nav = document.getElementById("nav");
    if (!nav) return;
    const c = copy();
    [...nav.querySelectorAll(".nav-tab")].forEach((tab) => {
      const meta = NAV_META[tab.dataset.tab] || { icon: "SL", zone: "command" };
      tab.dataset.zone = c.foc.zones[meta.zone] || meta.zone;
      const label = c.tabs[tab.dataset.tab] || tab.textContent.trim();
      tab.innerHTML = `<span class="sentinela-nav-code">${meta.icon}</span><span class="sentinela-nav-text">${label}</span>`;
    });
  }

  function labOverviewHtml() {
    const c = copy();
    return `
      <div class="lab-overview" id="lab-overview">
        <article class="lab-panel lab-panel-wide">
          <div class="lab-panel-head"><span>${c.foc.operationalStatus}</span><b id="lab-status-mode">${c.foc.pipelineNominal}</b></div>
          <div class="lab-metric-grid">
            <span><b id="lab-participants">${shortText("kpi-participants", "0")}</b><em>${c.foc.participants}</em></span>
            <span><b id="lab-ieo">${shortText("kpi-ieo", "--")}</b><em>IEO/OEI</em></span>
            <span><b id="lab-psi">${shortText("kpi-psi", "--")}</b><em>PSI</em></span>
            <span><b id="lab-flags">${shortText("kpi-flags", "0")}</b><em>${c.foc.redFlags}</em></span>
            <span><b id="lab-window">${shortText("kpi-window", "--")}</b><em>${c.foc.currentWindow}</em></span>
          </div>
        </article>
        <article class="lab-panel">
          <div class="lab-panel-head"><span>${c.foc.nextActions}</span><b>${c.foc.human}</b></div>
          <button type="button" data-target="participants">${c.foc.reviewParticipant}</button>
          <button type="button" data-target="flags">${c.foc.criticalFlags}</button>
          <button type="button" data-target="report">${c.foc.generateReport}</button>
        </article>
        <article class="lab-panel">
          <div class="lab-panel-head"><span>${c.foc.custodyIntegrity}</span><b>${c.foc.verifiable}</b></div>
          <div class="lab-list">
            <span>${c.foc.chainOk}</span>
            <span>${c.foc.manifestValid}</span>
            <span>${c.foc.signatureVerified}</span>
          </div>
        </article>
      </div>
    `;
  }

  function ensureOverview() {
    const overview = document.getElementById("section-overview");
    if (!overview) return;
    overview.querySelectorAll(".ux-decision-panel, .foc-command-panels").forEach((node) => node.remove());
    let lab = document.getElementById("lab-overview");
    if (!lab) {
      const sub = overview.querySelector(".section-sub") || overview.querySelector(".section-title");
      sub.insertAdjacentHTML("afterend", labOverviewHtml());
      lab = document.getElementById("lab-overview");
      lab.addEventListener("click", (event) => {
        const btn = event.target.closest("button[data-target]");
        if (btn && typeof window.navigateTo === "function") window.navigateTo(btn.dataset.target);
      });
    }
  }

  function refreshOverview() {
    const set = (id, value) => {
      const el = document.getElementById(id);
      if (el) el.textContent = value;
    };
    set("lab-participants", shortText("kpi-participants", "0"));
    set("lab-ieo", shortText("kpi-ieo", "--"));
    set("lab-psi", shortText("kpi-psi", "--"));
    set("lab-flags", shortText("kpi-flags", "0"));
    set("lab-window", shortText("kpi-window", "--"));
  }

  function enhanceSections() {
    const c = copy();
    const overviewSub = document.querySelector("#section-overview .section-sub");
    const studiesSub = document.querySelector("#section-studies .section-sub");
    const participantsSub = document.querySelector("#section-participants .section-sub");
    if (overviewSub) overviewSub.textContent = c.foc.overviewSub;
    if (studiesSub) studiesSub.textContent = c.foc.studiesSub;
    if (participantsSub) participantsSub.textContent = c.foc.participantsSub;
  }

  function enhanceConsole() {
    const app = document.getElementById("app-shell");
    if (!app || !visible(app)) return;
    ensureLabShell();
    enhanceHeader();
    enhanceNav();
    enhanceSections();
    ensureOverview();
    refreshOverview();
  }

  function applyLocale() {
    window.SENTINELA_ACTIVE_LOCALE = activeLocale;
    window.SENTINELA_UX_COPY = copy;
    renderLanguageSwitches();
    updateTextNodes();
    enhanceConsole();
    window.dispatchEvent(new CustomEvent("sentinela:locale-changed", { detail: { locale: activeLocale } }));
  }

  window.SENTINELA_LAB_PRIMARY = {
    applyLocale,
    enhance: enhanceConsole,
    refresh: refreshOverview,
  };

  ready(() => {
    applyLocale();
    setInterval(enhanceConsole, 1200);
    setInterval(refreshOverview, 1500);
  });
})();
