(function () {
  const LOCALES = [
    { code: "pt-BR", label: "PT" },
    { code: "en-US", label: "EN" },
    { code: "es-ES", label: "ES" },
  ];

  const I18N = {
    "pt-BR": {
      brand: "SENTINELA",
      loginSub: "SUPREME Longitudinal Console",
      accessTitle: "Acesso restrito",
      accessBody: "Entre para revisar sinais agregados, priorizar acompanhamento e registrar decisões responsáveis.",
      heroBadge: "Ambiente local seguro",
      heroBody:
        "Centro de acompanhamento para exposição ocupacional em perícia digital. Leitura longitudinal, dados pseudonimizados e acesso sob responsabilidade designada.",
      heroApiStatus: "conectada",
      heroData: "Dados",
      heroDataStatus: "pseudonimizados",
      heroUse: "Uso",
      heroUseStatus: "pesquisa e governança",
      loginEmailLabel: "Identificação",
      loginPasswordLabel: "Chave de Acesso",
      rememberAccess: "Lembrar acesso neste dispositivo",
      loginButton: "Entrar no console",
      noClinicalTitle: "Sem diagnóstico clínico automático",
      noClinicalBody: "O sistema apoia triagem e governança; decisões exigem responsável humano.",
      privacyTitle: "Privacidade por desenho",
      privacyBody: "Identificadores são tratados de forma pseudonimizada no fluxo operacional.",
      logout: "Sair",
      warRoom: "Sala de Crise",
      nextDecisionTitle: "Priorizar triagem dos participantes com sinal ativo",
      nextDecisionBody:
        "Comece por convergência IEO/PSI, depois dissonância. O objetivo da tela é reduzir o tempo até a primeira ação responsável.",
      nextDecision: "Próxima decisão recomendada",
      evidenceFlags: "red flags",
      evidenceIeo: "IEO médio",
      evidencePsi: "PSI médio",
      actions: ["Revisar participantes em convergência", "Abrir detalhes das red flags", "Registrar decisão no relatório"],
      order: "Ordem sugerida:",
      orderText: "Use a lista como fila de trabalho, não como tabela neutra.",
      riskConvergence: "convergência",
      riskDissonance: "dissonância",
      riskResidual: "carga residual",
      riskBaseline: "linha de base",
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
        baseline: "Linha de Base",
        longitudinal: "Longitudinal",
        exports: "Exportação",
        report: "Relatório",
      },
      cycle: ["Verificar dados", "Priorizar risco", "Registrar conduta", "Reavaliar janela"],
      foc: {
        zones: {
          command: "Central de Comando",
          case: "Área de Casos",
          audit: "Auditoria Forense",
        },
        jurisdictionAria: "Selecionar jurisdição",
        jurisdictions: { BR: "Brasil", EU: "União Europeia", US: "EUA", INT: "Internacional" },
        sidebarSubtitle: "Console de Operações Forenses",
        scope: "Escopo atual",
        pipelineNominal: "Pipeline nominal",
        waitingIngestion: "Aguardando ingestão",
        lastIngestion: "Última ingestão",
        operationalStatus: "Status Operacional",
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
        riskEvidenceMatrix: "Matriz de Risco e Evidência",
        currentWindow: "janela atual",
        participants: "participantes",
        redFlags: "red flags",
        nominal: "nominal",
        dissonance: "dissonância",
        chronicity: "cronicidade",
        reactivity: "reatividade",
        noData: "sem dado",
        nextActions: "Próximas Ações",
        queue: "fila",
        reviewParticipant: "Revisar participante",
        openStudy: "Abrir estudo",
        generateReport: "Gerar relatório",
        verifyCollectionFailure: "Verificar falha de coleta",
        sessionFeed: "Fluxo da Sessão",
        ipedAgent: "IPED/agente",
        ingestionActive: "Ingestão ativa",
        manifestValid: "Manifesto válido",
        replayAvailable: "Replay disponível",
        custodyIntegrity: "Integridade da Custódia",
        verifiable: "verificável",
        signatureVerified: "Assinatura verificada",
        ipedRegistered: "IPED registrado",
        psychometricGate: "Portão Psicométrico",
        session: "sessão",
        completed: "concluído",
        postSession: "pós-sessão",
        dataQuality: "Qualidade dos Dados",
        control: "controle",
        validWindows: "Janelas válidas",
        gapsMonitored: "Lacunas monitoradas",
        lowQuality: "Baixa qualidade",
        discardedEvents: "Eventos descartados",
        evidenceQueue: "Fila de Evidências",
        human: "humano",
        criticalFlags: "Red flags críticas",
        psychometricDissonance: "Dissonância psicométrica",
        degradedIntegrity: "Integridade degradada",
        elevatedRisk: "Risco agregado elevado",
        overviewSub: "Coleta, risco e próxima ação operacional.",
        studiesSub: "Matriz de instituição, estudo, caso, coleta e integridade.",
        participantsSub: "Matriz operacional por participante pseudonimizado.",
      },
      pipeline: {
        title: "Saúde do Pipeline",
        sub: "Estado de ingestão e disponibilidade dos outputs recebidos do SUPREME",
        status: "Status",
        ieoWindows: "Janelas IEO",
        psychometrics: "Psicometria",
        redFlags: "Red Flags",
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
        overviewDeepSub: "Gráficos deslocados da primeira decisão",
        chartSeries: "Evolução IEO x PSI",
        chartConvergence: "Distribuição de Convergência",
        chartFlags: "Red Flags por Tipo",
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
        noProfile: "Sem perfil longitudinal recebido do SUPREME. Classificação indisponível para esta pessoa."
      },
      report: {
        title: "Relatório Técnico",
        sub: "Relatório operacional auditável em formato imprimível",
        cardTitle: "Relatório Técnico SUPREME V4",
        cardBody: "Gera relatório narrativo com dados reais do estudo: IEO, PSI, red flags, convergência, participantes e recomendações.",
        generate: "Gerar relatório completo",
        hint: "Busca dados dos endpoints, gera relatório narrativo e permite impressão/PDF",
        modalTitle: "Relatório Técnico — SUPREME V4",
        modalSub: "Programa de Pesquisa · Exposição Ocupacional em Perícia Digital",
        loading: "Carregando dados...",
        loadingEndpoints: "Buscando dados dos endpoints...",
        generatedAt: "Gerado em:",
        print: "Imprimir / PDF",
        copy: "Copiar texto",
        close: "Fechar",
        copied: "Relatório copiado para a área de transferência.",
        copyManual: "Selecione e copie manualmente.",
        notInformed: "não informado",
        noFlags: "SEM FLAGS ATIVAS",
        flagsReceived: "FLAGS RECEBIDAS",
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
          program: "Programa",
          generated: "Relatório gerado em",
          monitored: "Participantes monitorados",
          windows: "Janelas processadas",
          period: "Período coberto",
          instruments: "Instrumentos psicométricos",
          activeFlags: "Red flags ativas",
          responsible: "Responsável",
          analyticSource: "Fonte analítica",
          sentinelaRole: "Papel do SENTINELA",
          algorithmVersion: "Versão do algoritmo",
          parameters: "Parâmetros recebidos",
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
          clinicalDiagnosis: "Diagnóstico clínico",
          causalNexus: "Nexo causal",
          autonomousDecisions: "Decisões autônomas",
        },
        values: {
          programName: "SUPREME V4 — Exposição Ocupacional em Perícia Digital",
          calculatedClass: "Classe recebida do SUPREME",
          valueFromSupreme: "Valor recebido do SUPREME",
          recordsFromSupreme: "Registros recebidos do SUPREME",
          sentinelaRole: "Receber, persistir e visualizar outputs auditáveis",
          noClinical: "NÃO realizado",
          noCausal: "NÃO estabelecido",
          noAutonomous: "NÃO — todas as ações dependem de responsável designado",
          noParticipants: "Nenhum participante com dados disponíveis.",
          noRedFlags: "Nenhuma red flag registrada.",
          fortnightly: "quinzenais · 14 dias cada",
          stable: "Estável",
          increasing: "Crescente — atenção redobrada",
          decreasing: "Decrescente — sinal positivo",
        },
        warning: "Este laudo é instrumento de gestão de risco — não constitui diagnóstico clínico, avaliação psicológica ou nexo causal.",
        auditLimit: "Os participantes são identificados por hash pseudonimizado. O uso deste relatório deve seguir os protocolos éticos do CEP aprovado.",
        signatures: {
          responsible: "Pesquisador Responsável / Data: ____________________",
          reviewer: "Revisor / Data: ____________________",
        },
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
          limitation: "Este relatório é instrumento operacional auditável. Não constitui diagnóstico clínico, avaliação psicológica, nexo causal ou decisão autônoma. Qualquer medida individual depende de revisão humana, autorização institucional e protocolo aprovado.",
        },
        recommendations: [
          "Conferir os registros de red flag recebidos do SUPREME e registrar a decisão do responsável.",
          "Manter IEO, PSI, convergência e red flags como outputs do backend SUPREME, sem recomputação local no SENTINELA.",
          "Usar este relatório como evidência operacional auditável; qualquer ação individual exige revisão humana e protocolo aprovado.",
        ],
      },
    },
    "en-US": {
      brand: "SENTINEL",
      loginSub: "SUPREME V4 - Research console",
      accessTitle: "Restricted access",
      accessBody: "Sign in to review aggregate signals, prioritize follow-up and record accountable decisions.",
      heroBadge: "Local environment active",
      heroBody:
        "Monitoring center for occupational exposure in digital forensics. Longitudinal reading, pseudonymized data and designated-responsibility access.",
      heroApiStatus: "connected",
      heroData: "Data",
      heroDataStatus: "pseudonymized",
      heroUse: "Use",
      heroUseStatus: "research and governance",
      loginEmailLabel: "Identification",
      loginPasswordLabel: "Access Key",
      rememberAccess: "Remember access on this device",
      loginButton: "Enter console",
      noClinicalTitle: "No automatic clinical diagnosis",
      noClinicalBody: "The system supports screening and governance; decisions require a responsible human.",
      privacyTitle: "Privacy by design",
      privacyBody: "Identifiers are handled pseudonymously in the operational flow.",
      logout: "Log out",
      warRoom: "War Room",
      nextDecisionTitle: "Prioritize triage for participants with active signal",
      nextDecisionBody:
        "Start with IEO/PSI convergence, then dissonance. The screen is designed to shorten the path to accountable action.",
      nextDecision: "Recommended next decision",
      evidenceFlags: "red flags",
      evidenceIeo: "avg IEO",
      evidencePsi: "avg PSI",
      actions: ["Review participants in convergence", "Open red flag details", "Record decision in report"],
      order: "Suggested order:",
      orderText: "Use the list as a work queue, not as a neutral table.",
      riskConvergence: "convergence",
      riskDissonance: "dissonance",
      riskResidual: "residual load",
      riskBaseline: "baseline",
      tabs: {
        overview: "Overview",
        studies: "Studies",
        pipeline: "Pipeline",
        dataquality: "Data Quality",
        ieo: "IEO",
        participants: "Participants",
        flags: "Red Flags",
        psycho: "Psychometrics",
        history: "History",
        baseline: "Baseline",
        longitudinal: "Longitudinal",
        exports: "Exports",
        report: "Report",
      },
      cycle: ["Check data", "Prioritize risk", "Record action", "Review window"],
      foc: {
        zones: {
          command: "Command Center",
          case: "Case Workspace",
          audit: "Forensic Audit",
        },
        jurisdictionAria: "Select jurisdiction",
        jurisdictions: { BR: "Brazil", EU: "European Union", US: "United States", INT: "International" },
        sidebarSubtitle: "Forensic Operations Console",
        scope: "Current scope",
        pipelineNominal: "Pipeline nominal",
        waitingIngestion: "Waiting for ingestion",
        lastIngestion: "Last ingestion",
        operationalStatus: "Operational Status",
        connected: "connected",
        agent: "Agent",
        localAgent: "local active",
        lastSession: "Last session",
        waiting: "waiting",
        custody: "Custody",
        chainOk: "hash chain intact",
        events: "Events",
        data: "Data",
        monitored: "monitored",
        riskEvidenceMatrix: "Risk & Evidence Matrix",
        currentWindow: "current window",
        participants: "participants",
        redFlags: "red flags",
        nominal: "nominal",
        dissonance: "dissonance",
        chronicity: "chronicity",
        reactivity: "reactivity",
        noData: "no data",
        nextActions: "Next Actions",
        queue: "queue",
        reviewParticipant: "Review participant",
        openStudy: "Open study",
        generateReport: "Generate report",
        verifyCollectionFailure: "Check collection failure",
        sessionFeed: "Session Feed",
        ipedAgent: "IPED/agent",
        ingestionActive: "Active ingestion",
        manifestValid: "Manifest valid",
        replayAvailable: "Replay available",
        custodyIntegrity: "Custody Integrity",
        verifiable: "verifiable",
        signatureVerified: "Signature verified",
        ipedRegistered: "IPED registered",
        psychometricGate: "Psychometric Gate",
        session: "session",
        completed: "completed",
        postSession: "post-session",
        dataQuality: "Data Quality",
        control: "control",
        validWindows: "Valid windows",
        gapsMonitored: "Gaps monitored",
        lowQuality: "Low quality",
        discardedEvents: "Discarded events",
        evidenceQueue: "Evidence Queue",
        human: "human",
        criticalFlags: "Critical red flags",
        psychometricDissonance: "Psychometric dissonance",
        degradedIntegrity: "Degraded integrity",
        elevatedRisk: "Elevated aggregate risk",
        overviewSub: "Collection, risk and next operational action.",
        studiesSub: "Institution, study, case, collection and integrity matrix.",
        participantsSub: "Operational matrix by pseudonymized participant.",
      },
      pipeline: {
        title: "Pipeline Health",
        sub: "Ingestion status and availability of outputs received from SUPREME",
        status: "Status",
        ieoWindows: "IEO windows",
        psychometrics: "Psychometrics",
        redFlags: "Red Flags",
        checks: "Checks",
        loading: "Loading...",
        noChecks: "No checks available.",
        ok: "ok",
        noData: "no data",
        labels: {
          supreme_outputs_present: "SUPREME outputs present",
          psychometric_outputs_present: "psychometric outputs present",
          red_flags_present: "red flags present",
        },
      },
      workspace: {
        overviewDeepTitle: "Operational details",
        overviewDeepSub: "Charts moved away from the first decision",
        chartSeries: "IEO x PSI evolution",
        chartConvergence: "Convergence distribution",
        chartFlags: "Red Flags by Type",
        studiesHeaders: ["Institution", "Study", "Case", "Expert", "Collection", "Participants", "IPED sessions", "Last event", "Integrity", "Actions"],
        participantsHeaders: ["ID", "Group", "Psychometrics", "Behavioral", "Profile", "Red Flags", "Quality", "Last session", "Windows", "Action"],
        studiesEmpty: "No active study in the current scope. Waiting for the first processed IPED session.",
        participantsEmpty: "No participant requiring attention. Waiting for baseline and valid sessions.",
        unassigned: "unassigned",
        notInformed: "not informed",
        none: "none",
        collectionComplete: "Session closed",
        insufficientData: "Insufficient data",
        integrityOk: "Hash chain intact",
        integrityPending: "Integrity pending",
        open: "Open",
        export: "Export",
        openDossier: "Open dossier",
        panasPending: "PANAS pending",
        noWindow: "no window",
        profileInsufficient: "Insufficient data",
        profileOperational: "longitudinal operational",
        noProfile: "No longitudinal profile received from SUPREME. Classification unavailable for this person."
      },
      report: {
        title: "Technical Report",
        sub: "Auditable operational report in printable format",
        cardTitle: "SUPREME V4 Technical Report",
        cardBody: "Generates a narrative report with study data: IEO, PSI, red flags, convergence, participants and recommendations.",
        generate: "Generate full report",
        hint: "Queries endpoints, builds a narrative report and enables print/PDF",
        modalTitle: "Technical Report — SUPREME V4",
        modalSub: "Research Program · Occupational Exposure in Digital Forensics",
        loading: "Loading data...",
        loadingEndpoints: "Fetching endpoint data...",
        generatedAt: "Generated at:",
        print: "Print / PDF",
        copy: "Copy text",
        close: "Close",
        copied: "Report copied to clipboard.",
        copyManual: "Select and copy manually.",
        notInformed: "not informed",
        noFlags: "NO ACTIVE FLAGS",
        flagsReceived: "FLAGS RECEIVED",
        outputStatus: "Output Status",
        outputSub: "SENTINELA displays auditable outputs calculated by SUPREME",
        sections: {
          narrative: "Narrative Brief",
          identification: "Study Identification",
          methodology: "Methodology",
          global: "Global Result",
          participants: "Participant Analysis — Latest Window",
          redFlags: "Red Flags — Complete Log",
          longitudinal: "Longitudinal Analysis",
          recommendations: "Recommendations",
          auditability: "Auditability and Limits",
        },
        fields: {
          program: "Program",
          generated: "Report generated at",
          monitored: "Participants monitored",
          windows: "Windows processed",
          period: "Covered period",
          instruments: "Psychometric instruments",
          activeFlags: "Active red flags",
          responsible: "Responsible user",
          analyticSource: "Analytic source",
          sentinelaRole: "SENTINELA role",
          algorithmVersion: "Algorithm version",
          parameters: "Received parameters",
          value: "Value",
          status: "Status",
          class: "Class",
          description: "Description",
          severity: "Severity",
          participant: "Participant",
          window: "Window",
          detail: "Detail",
          trend: "Trend",
          analyzedWindows: "Windows analyzed",
          system: "System",
          clinicalDiagnosis: "Clinical diagnosis",
          causalNexus: "Causal nexus",
          autonomousDecisions: "Autonomous decisions",
        },
        values: {
          programName: "SUPREME V4 — Occupational Exposure in Digital Forensics",
          calculatedClass: "Class received from SUPREME",
          valueFromSupreme: "Value received from SUPREME",
          recordsFromSupreme: "Records received from SUPREME",
          sentinelaRole: "Receive, persist and display auditable outputs",
          noClinical: "NOT performed",
          noCausal: "NOT established",
          noAutonomous: "NO — every action depends on a designated responsible user",
          noParticipants: "No participant data available.",
          noRedFlags: "No red flag registered.",
          fortnightly: "fortnightly · 14 days each",
          stable: "Stable",
          increasing: "Increasing — closer attention",
          decreasing: "Decreasing — positive signal",
        },
        warning: "This brief is a risk-management instrument — it is not a clinical diagnosis, psychological assessment or causal nexus.",
        auditLimit: "Participants are identified by pseudonymized hash. Use of this report must follow the approved ethics protocol.",
        signatures: {
          responsible: "Responsible Researcher / Date: ____________________",
          reviewer: "Reviewer / Date: ____________________",
        },
        narrative: {
          title: "AUDITABLE TECHNICAL REPORT",
          frontier: "ANALYTIC BOUNDARY",
          viewerOnly: "SENTINELA displays outputs calculated by the SUPREME backend. This screen does not recalculate IEO, PSI, convergence or red flags.",
          algorithm: "Algorithm version received:",
          outputs: "OUTPUTS RECEIVED",
          ieo: "Average IEO received for latest window:",
          psi: "Average PSI received for latest window:",
          flags: "Red flags received:",
          distribution: "Convergence distribution received:",
          flagTypes: "Red flag types received:",
          trend: "Longitudinal IEO trend:",
          mean: "Overall mean:",
          limitation: "This report is an auditable operational instrument. It is not a clinical diagnosis, psychological assessment, causal nexus or autonomous decision. Any individual measure depends on human review, institutional authorization and an approved protocol.",
        },
        recommendations: [
          "Review the red flag records received from SUPREME and record the responsible user's decision.",
          "Keep IEO, PSI, convergence and red flags as SUPREME backend outputs, with no local recomputation in SENTINELA.",
          "Use this report as auditable operational evidence; any individual action requires human review and an approved protocol.",
        ],
      },
    },
    "es-ES": {
      brand: "SENTINELA",
      loginSub: "SUPREME V4 - Consola de investigación",
      accessTitle: "Acceso restringido",
      accessBody: "Ingrese para revisar señales agregadas, priorizar seguimiento y registrar decisiones responsables.",
      heroBadge: "Entorno local activo",
      heroBody:
        "Centro de seguimiento para exposición ocupacional en pericia digital. Lectura longitudinal, datos seudonimizados y acceso bajo responsabilidad designada.",
      heroApiStatus: "conectada",
      heroData: "Datos",
      heroDataStatus: "seudonimizados",
      heroUse: "Uso",
      heroUseStatus: "investigación y gobernanza",
      loginEmailLabel: "Identificación",
      loginPasswordLabel: "Clave de acceso",
      rememberAccess: "Recordar acceso en este dispositivo",
      loginButton: "Entrar en la consola",
      noClinicalTitle: "Sin diagnóstico clínico automático",
      noClinicalBody: "El sistema apoya cribado y gobernanza; las decisiones exigen responsable humano.",
      privacyTitle: "Privacidad por diseño",
      privacyBody: "Los identificadores se tratan de forma seudonimizada en el flujo operativo.",
      logout: "Salir",
      warRoom: "Sala de Crisis",
      nextDecisionTitle: "Priorizar triaje de participantes con señal activa",
      nextDecisionBody:
        "Comience por convergencia IEO/PSI y luego disonancia. La pantalla reduce el tiempo hasta la primera acción responsable.",
      nextDecision: "Próxima decisión recomendada",
      evidenceFlags: "red flags",
      evidenceIeo: "IEO medio",
      evidencePsi: "PSI medio",
      actions: ["Revisar participantes en convergencia", "Abrir detalles de red flags", "Registrar decisión en el informe"],
      order: "Orden sugerido:",
      orderText: "Use la lista como cola de trabajo, no como tabla neutra.",
      riskConvergence: "convergencia",
      riskDissonance: "disonancia",
      riskResidual: "carga residual",
      riskBaseline: "línea base",
      tabs: {
        overview: "Vista General",
        studies: "Estudios",
        pipeline: "Pipeline",
        dataquality: "Calidad",
        ieo: "IEO",
        participants: "Participantes",
        flags: "Red Flags",
        psycho: "Psicométricos",
        history: "Historial",
        baseline: "Línea Base",
        longitudinal: "Longitudinal",
        exports: "Exportación",
        report: "Informe",
      },
      cycle: ["Verificar datos", "Priorizar riesgo", "Registrar conducta", "Reevaluar ventana"],
      foc: {
        zones: {
          command: "Centro de Comando",
          case: "Espacio de Casos",
          audit: "Auditoría Forense",
        },
        jurisdictionAria: "Seleccionar jurisdicción",
        jurisdictions: { BR: "Brasil", EU: "Unión Europea", US: "Estados Unidos", INT: "Internacional" },
        sidebarSubtitle: "Consola de Operaciones Forenses",
        scope: "Alcance actual",
        pipelineNominal: "Pipeline nominal",
        waitingIngestion: "Esperando ingesta",
        lastIngestion: "Última ingesta",
        operationalStatus: "Estado Operacional",
        connected: "conectado",
        agent: "Agente",
        localAgent: "local activo",
        lastSession: "Última sesión",
        waiting: "esperando",
        custody: "Custodia",
        chainOk: "hash chain íntegra",
        events: "Eventos",
        data: "Datos",
        monitored: "monitorizados",
        riskEvidenceMatrix: "Matriz de Riesgo y Evidencia",
        currentWindow: "ventana actual",
        participants: "participantes",
        redFlags: "red flags",
        nominal: "nominal",
        dissonance: "disonancia",
        chronicity: "cronicidad",
        reactivity: "reactividad",
        noData: "sin datos",
        nextActions: "Próximas Acciones",
        queue: "cola",
        reviewParticipant: "Revisar participante",
        openStudy: "Abrir estudio",
        generateReport: "Generar informe",
        verifyCollectionFailure: "Verificar falla de recolección",
        sessionFeed: "Flujo de Sesión",
        ipedAgent: "IPED/agente",
        ingestionActive: "Ingesta activa",
        manifestValid: "Manifiesto válido",
        replayAvailable: "Replay disponible",
        custodyIntegrity: "Integridad de Custodia",
        verifiable: "verificable",
        signatureVerified: "Firma verificada",
        ipedRegistered: "IPED registrado",
        psychometricGate: "Puerta Psicométrica",
        session: "sesión",
        completed: "concluido",
        postSession: "post-sesión",
        dataQuality: "Calidad de Datos",
        control: "control",
        validWindows: "Ventanas válidas",
        gapsMonitored: "Lagunas monitorizadas",
        lowQuality: "Baja calidad",
        discardedEvents: "Eventos descartados",
        evidenceQueue: "Cola de Evidencias",
        human: "humano",
        criticalFlags: "Red flags críticas",
        psychometricDissonance: "Disonancia psicométrica",
        degradedIntegrity: "Integridad degradada",
        elevatedRisk: "Riesgo agregado elevado",
        overviewSub: "Recolección, riesgo y próxima acción operacional.",
        studiesSub: "Matriz de institución, estudio, caso, recolección e integridad.",
        participantsSub: "Matriz operacional por participante seudonimizado.",
      },
      pipeline: {
        title: "Salud del Pipeline",
        sub: "Estado de ingesta y disponibilidad de outputs recibidos de SUPREME",
        status: "Estado",
        ieoWindows: "Ventanas IEO",
        psychometrics: "Psicometría",
        redFlags: "Red Flags",
        checks: "Verificaciones",
        loading: "Cargando...",
        noChecks: "Sin verificaciones disponibles.",
        ok: "ok",
        noData: "sin datos",
        labels: {
          supreme_outputs_present: "outputs SUPREME presentes",
          psychometric_outputs_present: "outputs psicométricos presentes",
          red_flags_present: "red flags presentes",
        },
      },
      workspace: {
        overviewDeepTitle: "Detalles operacionales",
        overviewDeepSub: "Gráficos desplazados de la primera decisión",
        chartSeries: "Evolución IEO x PSI",
        chartConvergence: "Distribución de Convergencia",
        chartFlags: "Red Flags por Tipo",
        studiesHeaders: ["Institución", "Estudio", "Caso", "Perito", "Recolección", "Participantes", "Sesiones IPED", "Último evento", "Integridad", "Acciones"],
        participantsHeaders: ["ID", "Grupo", "Psicometría", "Comportamental", "Perfil", "Red Flags", "Calidad", "Última sesión", "Ventanas", "Acción"],
        studiesEmpty: "Ningún estudio activo en el alcance actual. Esperando la primera sesión IPED procesada.",
        participantsEmpty: "Ningún participante en atención. Esperando baseline y sesiones válidas.",
        unassigned: "no asignado",
        notInformed: "no informado",
        none: "ninguno",
        collectionComplete: "Sesión cerrada",
        insufficientData: "Datos insuficientes",
        integrityOk: "Hash chain íntegra",
        integrityPending: "Integridad pendiente",
        open: "Abrir",
        export: "Exportar",
        openDossier: "Abrir expediente",
        panasPending: "PANAS pendiente",
        noWindow: "sin ventana",
        profileInsufficient: "Datos insuficientes",
        profileOperational: "operacional longitudinal",
        noProfile: "Sin perfil longitudinal recibido de SUPREME. Clasificación no disponible para esta persona."
      },
      report: {
        title: "Informe Técnico",
        sub: "Informe operacional auditable en formato imprimible",
        cardTitle: "Informe Técnico SUPREME V4",
        cardBody: "Genera un informe narrativo con datos del estudio: IEO, PSI, red flags, convergencia, participantes y recomendaciones.",
        generate: "Generar informe completo",
        hint: "Consulta endpoints, genera informe narrativo y permite impresión/PDF",
        modalTitle: "Informe Técnico — SUPREME V4",
        modalSub: "Programa de Investigación · Exposición Ocupacional en Pericia Digital",
        loading: "Cargando datos...",
        loadingEndpoints: "Consultando datos de endpoints...",
        generatedAt: "Generado en:",
        print: "Imprimir / PDF",
        copy: "Copiar texto",
        close: "Cerrar",
        copied: "Informe copiado al portapapeles.",
        copyManual: "Seleccione y copie manualmente.",
        notInformed: "no informado",
        noFlags: "SIN FLAGS ACTIVAS",
        flagsReceived: "FLAGS RECIBIDAS",
        outputStatus: "Estado del Output",
        outputSub: "SENTINELA visualiza outputs auditables calculados por SUPREME",
        sections: {
          narrative: "Informe Narrativo",
          identification: "Identificación del Estudio",
          methodology: "Metodología",
          global: "Resultado Global",
          participants: "Análisis por Participante — Última Ventana",
          redFlags: "Red Flags — Registro Completo",
          longitudinal: "Análisis Longitudinal",
          recommendations: "Recomendaciones",
          auditability: "Auditabilidad y Límites",
        },
        fields: {
          program: "Programa",
          generated: "Informe generado en",
          monitored: "Participantes monitorizados",
          windows: "Ventanas procesadas",
          period: "Período cubierto",
          instruments: "Instrumentos psicométricos",
          activeFlags: "Red flags activas",
          responsible: "Responsable",
          analyticSource: "Fuente analítica",
          sentinelaRole: "Papel de SENTINELA",
          algorithmVersion: "Versión del algoritmo",
          parameters: "Parámetros recibidos",
          value: "Valor",
          status: "Estado",
          class: "Clase",
          description: "Descripción",
          severity: "Severidad",
          participant: "Participante",
          window: "Ventana",
          detail: "Detalle",
          trend: "Tendencia",
          analyzedWindows: "Ventanas analizadas",
          system: "Sistema",
          clinicalDiagnosis: "Diagnóstico clínico",
          causalNexus: "Nexo causal",
          autonomousDecisions: "Decisiones autónomas",
        },
        values: {
          programName: "SUPREME V4 — Exposición Ocupacional en Pericia Digital",
          calculatedClass: "Clase recibida de SUPREME",
          valueFromSupreme: "Valor recibido de SUPREME",
          recordsFromSupreme: "Registros recibidos de SUPREME",
          sentinelaRole: "Recibir, persistir y visualizar outputs auditables",
          noClinical: "NO realizado",
          noCausal: "NO establecido",
          noAutonomous: "NO — todas las acciones dependen de un responsable designado",
          noParticipants: "No hay datos de participantes disponibles.",
          noRedFlags: "Ninguna red flag registrada.",
          fortnightly: "quincenales · 14 días cada una",
          stable: "Estable",
          increasing: "Creciente — atención reforzada",
          decreasing: "Decreciente — señal positiva",
        },
        warning: "Este informe es un instrumento de gestión de riesgo — no constituye diagnóstico clínico, evaluación psicológica ni nexo causal.",
        auditLimit: "Los participantes se identifican por hash seudonimizado. El uso de este informe debe seguir el protocolo ético aprobado.",
        signatures: {
          responsible: "Investigador Responsable / Fecha: ____________________",
          reviewer: "Revisor / Fecha: ____________________",
        },
        narrative: {
          title: "INFORME TÉCNICO AUDITABLE",
          frontier: "FRONTERA ANALÍTICA",
          viewerOnly: "SENTINELA visualiza outputs calculados por el backend SUPREME. Esta pantalla no recalcula IEO, PSI, convergencia ni red flags.",
          algorithm: "Versión del algoritmo recibida:",
          outputs: "OUTPUTS RECIBIDOS",
          ieo: "IEO medio recibido en la última ventana:",
          psi: "PSI medio recibido en la última ventana:",
          flags: "Red flags recibidas:",
          distribution: "Distribución de convergencia recibida:",
          flagTypes: "Tipos de red flag recibidos:",
          trend: "Tendencia longitudinal del IEO:",
          mean: "Media general:",
          limitation: "Este informe es un instrumento operacional auditable. No constituye diagnóstico clínico, evaluación psicológica, nexo causal ni decisión autónoma. Cualquier medida individual depende de revisión humana, autorización institucional y protocolo aprobado.",
        },
        recommendations: [
          "Revisar los registros de red flag recibidos de SUPREME y registrar la decisión del responsable.",
          "Mantener IEO, PSI, convergencia y red flags como outputs del backend SUPREME, sin recomputación local en SENTINELA.",
          "Usar este informe como evidencia operacional auditable; cualquier acción individual exige revisión humana y protocolo aprobado.",
        ],
      },
    },
  };

  Object.assign(I18N["pt-BR"], {
    loginSub: "SUPREME Longitudinal Console",
    accessBody: "Entre para revisar sinais agregados, bloqueios de governança e evidências longitudinais.",
    heroBadge: "Ambiente local seguro",
    heroBody:
      "Centro visual para IEO/OEI, PSI, baselines, red flags e evidências, exibindo apenas dados analíticos pseudonimizados.",
    noClinicalTitle: "Sem diagnóstico automático",
    noClinicalBody: "O console apoia governança e revisão humana.",
    privacyBody: "Sem mídia, paths ou identificadores crus.",
  });

  Object.assign(I18N["en-US"], {
    loginSub: "SUPREME Longitudinal Console",
    accessBody: "Sign in to review aggregate signals, governance locks and longitudinal evidence.",
    heroBadge: "Local secure environment",
    heroBody:
      "Visual center for IEO/OEI, PSI, baselines, red flags and evidence, showing only pseudonymized analytic data.",
    noClinicalTitle: "No automatic diagnosis",
    noClinicalBody: "The console supports governance and mandatory human review.",
    privacyBody: "No media, paths or raw identifiers.",
  });

  Object.assign(I18N["es-ES"], {
    loginSub: "SUPREME Longitudinal Console",
    accessBody: "Ingrese para revisar señales agregadas, bloqueos de gobernanza y evidencias longitudinales.",
    heroBadge: "Entorno local seguro",
    heroBody:
      "Centro visual para IEO/OEI, PSI, baselines, red flags y evidencias, mostrando solo datos analíticos seudonimizados.",
    noClinicalTitle: "Sin diagnóstico automático",
    noClinicalBody: "La consola apoya gobernanza y revisión humana obligatoria.",
    privacyTitle: "Privacidad por diseño",
    privacyBody: "Sin medios, paths ni identificadores crudos.",
  });

  function getCookie(name) {
    return document.cookie
      .split(";")
      .map((item) => item.trim())
      .find((item) => item.startsWith(name + "="))
      ?.split("=")[1];
  }

  function setLocaleCookie(locale) {
    document.cookie = "supreme_locale=" + encodeURIComponent(locale) + "; path=/; max-age=31536000; samesite=strict";
  }

  function setJurisdictionCookie(jurisdiction) {
    document.cookie = "sentinela_jurisdiction=" + encodeURIComponent(jurisdiction) + "; path=/; max-age=31536000; samesite=strict";
  }

  function normalizeLocale(locale) {
    return LOCALES.some((item) => item.code === locale) ? locale : "pt-BR";
  }

  function normalizeJurisdiction(jurisdiction) {
    return JURISDICTIONS.some((item) => item.id === jurisdiction) ? jurisdiction : "BR";
  }

  let activeLocale = normalizeLocale(decodeURIComponent(getCookie("supreme_locale") || "pt-BR"));

  function copy() {
    return I18N[activeLocale] || I18N["pt-BR"];
  }

  const FALLBACK_COPY = { foc: I18N["pt-BR"].foc };

  function currentCopy() {
    if (typeof window.SENTINELA_UX_COPY === "function") return window.SENTINELA_UX_COPY();
    return FALLBACK_COPY;
  }

  function focCopy() {
    return currentCopy().foc || FALLBACK_COPY.foc;
  }

  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn, { once: true });
    } else {
      fn();
    }
  }

  function text(id, fallback) {
    const el = document.getElementById(id);
    return el && el.textContent.trim() ? el.textContent.trim() : fallback;
  }

  function makeDecisionPanel(scope) {
    const flags = text("kpi-flags", text("kpiFlags", "3"));
    const ieo = text("kpi-ieo", text("kpiIeo", "--"));
    const psi = text("kpi-psi", text("kpiPsi", "--"));
    const c = copy();

    const panel = document.createElement("section");
    panel.className = "ux-decision-panel";
    panel.innerHTML = `
      <div class="ux-decision-copy">
        <div class="ux-eyebrow">${c.nextDecision}</div>
        <h2>${c.nextDecisionTitle}</h2>
        <p>${c.nextDecisionBody}</p>
        <div class="ux-evidence-row">
          <span><b>${flags}</b> ${c.evidenceFlags}</span>
          <span><b>${ieo}</b> ${c.evidenceIeo}</span>
          <span><b>${psi}</b> ${c.evidencePsi}</span>
        </div>
      </div>
      <div class="ux-action-stack" aria-label="Suggested action queue">
        <button type="button" data-target="participants">1. ${c.actions[0]}</button>
        <button type="button" data-target="flags">2. ${c.actions[1]}</button>
        <button type="button" data-target="report">3. ${c.actions[2]}</button>
      </div>
    `;

    panel.addEventListener("click", (event) => {
      const btn = event.target.closest("button[data-target]");
      if (!btn) return;
      const target = btn.getAttribute("data-target");
      if (window.navigateTo && scope === "dashboard") {
        window.navigateTo(target);
        return;
      }
      const warMap = { participants: "participantes", flags: "participantes", report: "relatorio" };
      if (window.switchTab && scope === "war") {
        const tab = warMap[target] || "missao";
        const tabButton = [...document.querySelectorAll(".tab-btn")].find((b) =>
          (b.getAttribute("onclick") || "").includes(`'${tab}'`)
        );
        window.switchTab(tab, tabButton || null);
      }
    });

    return panel;
  }

  function addDashboardUX() {
    const overview = document.getElementById("section-overview");
    if (!overview || overview.querySelector(".ux-decision-panel")) return;
    const sub = overview.querySelector(".section-sub") || overview.querySelector(".section-title");
    sub.insertAdjacentElement("afterend", makeDecisionPanel("dashboard"));

    const participants = document.getElementById("section-participants");
    if (participants && !participants.querySelector(".ux-filter-brief")) {
      const subP = participants.querySelector(".section-sub") || participants.querySelector(".section-title");
      const c = copy();
      const brief = document.createElement("div");
      brief.className = "ux-filter-brief";
      brief.innerHTML = `
        <strong>${c.order}</strong>
        <span class="ux-risk-dot red"></span> ${c.riskConvergence}
        <span class="ux-risk-dot purple"></span> ${c.riskDissonance}
        <span class="ux-risk-dot amber"></span> ${c.riskResidual}
        <span class="ux-risk-dot green"></span> ${c.riskBaseline}.
        <span>${c.orderText}</span>
      `;
      subP.insertAdjacentElement("afterend", brief);
    }
  }

  function addWarRoomUX() {
    const mission = document.getElementById("panel-missao");
    if (!mission || mission.querySelector(".ux-decision-panel")) return;
    mission.insertAdjacentElement("afterbegin", makeDecisionPanel("war"));

    const pipeline = document.getElementById("pipeline");
    if (pipeline && !document.querySelector(".ux-command-cycle")) {
      const cycle = document.createElement("div");
      cycle.className = "ux-command-cycle";
      cycle.innerHTML = copy().cycle.map((item, i) => `<span><b>${i + 1}</b>${item}</span>`).join("");
      pipeline.insertAdjacentElement("beforebegin", cycle);
    }
  }

  function refreshEvidence() {
    const c = copy();
    document.querySelectorAll(".ux-decision-panel").forEach((panel) => {
      const row = panel.querySelector(".ux-evidence-row");
      if (!row) return;
      row.innerHTML = `
        <span><b>${text("kpi-flags", text("kpiFlags", "0"))}</b> ${c.evidenceFlags}</span>
        <span><b>${text("kpi-ieo", text("kpiIeo", "--"))}</b> ${c.evidenceIeo}</span>
        <span><b>${text("kpi-psi", text("kpiPsi", "--"))}</b> ${c.evidencePsi}</span>
      `;
    });
  }

  function renderLanguageSwitches() {
    document.querySelectorAll(".global-lang-switch").forEach((wrap) => {
      wrap.innerHTML = "";
      LOCALES.forEach((item) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.textContent = item.label;
        btn.dataset.locale = item.code;
        btn.classList.toggle("active", item.code === activeLocale);
        btn.setAttribute("aria-pressed", item.code === activeLocale ? "true" : "false");
        btn.addEventListener("click", () => {
          activeLocale = item.code;
          setLocaleCookie(activeLocale);
          applyLocale();
        });
        wrap.appendChild(btn);
      });
    });
  }

  function updateTextNodes() {
    const c = copy();
    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      if (c[key]) el.textContent = c[key];
    });
    document.documentElement.lang = activeLocale;
    document.querySelectorAll(".nav-tab").forEach((tab) => {
      const id = tab.dataset.tab;
      if (id && c.tabs[id]) {
        const label = tab.querySelector(".foc-nav-text");
        if (label) label.textContent = c.tabs[id];
        else tab.textContent = c.tabs[id];
      }
    });
    document.querySelectorAll(".section").forEach((section) => {
      const id = (section.id || "").replace("section-", "");
      const title = section.querySelector(":scope > .section-title");
      if (title && id && c.tabs[id]) title.textContent = c.tabs[id];
    });
    if (typeof TABS !== "undefined") {
      TABS.forEach((tab) => {
        if (c.tabs[tab.id]) tab.label = c.tabs[tab.id];
      });
    }
  }

  function updateDecisionPanels() {
    document.querySelectorAll(".ux-decision-panel").forEach((panel) => panel.remove());
    document.querySelectorAll(".ux-filter-brief").forEach((panel) => panel.remove());
    document.querySelectorAll(".ux-command-cycle").forEach((panel) => panel.remove());
  }

  function applyLocale() {
    renderLanguageSwitches();
    updateTextNodes();
    updateDecisionPanels();
    window.SENTINELA_ACTIVE_LOCALE = activeLocale;
    window.SENTINELA_UX_COPY = copy;
    window.dispatchEvent(new CustomEvent("sentinela:locale-changed", { detail: { locale: activeLocale } }));
  }

  ready(() => {
    applyLocale();
    setInterval(refreshEvidence, 3000);
  });
})();

(function () {
  const NAV_META = {
    overview: { icon: "CC", zone: "Command Center", label: "Visão Geral" },
    studies: { icon: "CS", zone: "Case Workspace", label: "Estudos" },
    participants: { icon: "PT", zone: "Case Workspace", label: "Participantes" },
    pipeline: { icon: "PL", zone: "Command Center", label: "Pipeline" },
    dataquality: { icon: "DQ", zone: "Command Center", label: "Qualidade" },
    flags: { icon: "RF", zone: "Command Center", label: "Red Flags" },
    psycho: { icon: "PG", zone: "Case Workspace", label: "Psicometria" },
    history: { icon: "TL", zone: "Forensic Audit", label: "Histórico" },
    baseline: { icon: "BL", zone: "Forensic Audit", label: "Baseline" },
    longitudinal: { icon: "LG", zone: "Forensic Audit", label: "Longitudinal" },
    exports: { icon: "EX", zone: "Forensic Audit", label: "Relatórios" },
    report: { icon: "RP", zone: "Forensic Audit", label: "Relatório" },
    ieo: { icon: "IE", zone: "Command Center", label: "IEO" },
  };

  const JURISDICTIONS = [
    { id: "BR", label: "Brasil" },
    { id: "EU", label: "União Europeia" },
    { id: "US", label: "EUA" },
    { id: "INT", label: "Internacional" },
  ];

  const FOC_FALLBACK_COPY = {
    foc: {
      zones: { command: "Central de Comando", case: "Área de Casos", audit: "Auditoria Forense" },
      jurisdictionAria: "Selecionar jurisdição",
      jurisdictions: { BR: "Brasil", EU: "União Europeia", US: "EUA", INT: "Internacional" },
      sidebarSubtitle: "Console de Operações Forenses",
      scope: "Escopo atual",
      pipelineNominal: "Pipeline nominal",
      waitingIngestion: "Aguardando ingestão",
      lastIngestion: "Última ingestão",
      operationalStatus: "Status Operacional",
      connected: "conectado",
      agent: "Agente",
      localAgent: "local ativo",
      lastSession: "Última sessão",
      waiting: "aguardando",
      custody: "Custódia",
      chainOk: "hash chain íntegra",
      events: "Eventos",
      data: "Dados",
      monitored: "monitored",
      riskEvidenceMatrix: "Matriz de Risco e Evidência",
      currentWindow: "janela atual",
      participants: "participants",
      redFlags: "red flags",
      nominal: "nominal",
      dissonance: "dissonância",
      chronicity: "cronicidade",
      reactivity: "reatividade",
      noData: "sem dado",
      nextActions: "Próximas Ações",
      queue: "fila",
      reviewParticipant: "Revisar participante",
      openStudy: "Abrir estudo",
      generateReport: "Gerar relatório",
      verifyCollectionFailure: "Verificar falha de coleta",
      sessionFeed: "Fluxo da Sessão",
      ipedAgent: "IPED/agente",
      ingestionActive: "Ingestão ativa",
      manifestValid: "Manifesto válido",
      replayAvailable: "Replay disponível",
      custodyIntegrity: "Integridade da Custódia",
      verifiable: "verificável",
      signatureVerified: "Assinatura verificada",
      ipedRegistered: "IPED registered",
      psychometricGate: "Portão Psicométrico",
      session: "sessão",
      completed: "concluído",
      postSession: "pós-sessão",
      dataQuality: "Qualidade dos Dados",
      control: "controle",
      validWindows: "Janelas válidas",
      gapsMonitored: "Lacunas monitoradas",
      lowQuality: "Baixa qualidade",
      discardedEvents: "Eventos descartados",
      evidenceQueue: "Fila de Evidências",
      human: "humano",
      criticalFlags: "Red flags críticas",
      psychometricDissonance: "Dissonância psicométrica",
      degradedIntegrity: "Integridade degradada",
      elevatedRisk: "Risco agregado elevado",
      overviewSub: "Coleta, risco e próxima ação operacional.",
      studiesSub: "Matriz de instituição, estudo, caso, coleta e integridade.",
      participantsSub: "Matriz operacional por participante pseudonimizado.",
    },
  };

  function currentFocCopy() {
    if (typeof window.SENTINELA_UX_COPY === "function") return window.SENTINELA_UX_COPY();
    return FOC_FALLBACK_COPY;
  }

  function focCopy() {
    return currentFocCopy().foc || FOC_FALLBACK_COPY.foc;
  }

  function getCookie(name) {
    return document.cookie
      .split(";")
      .map((item) => item.trim())
      .find((item) => item.startsWith(name + "="))
      ?.split("=")[1];
  }

  function setJurisdictionCookie(jurisdiction) {
    document.cookie = "sentinela_jurisdiction=" + encodeURIComponent(jurisdiction) + "; path=/; max-age=31536000; samesite=strict";
  }

  function normalizeJurisdiction(jurisdiction) {
    return JURISDICTIONS.some((item) => item.id === jurisdiction) ? jurisdiction : "BR";
  }

  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn, { once: true });
    } else {
      fn();
    }
  }

  function visible(el) {
    if (!el) return false;
    const style = getComputedStyle(el);
    return style.display !== "none" && style.visibility !== "hidden" && Number(style.opacity || "1") > 0;
  }

  function shortText(id, fallback) {
    const el = document.getElementById(id);
    const value = el && el.textContent ? el.textContent.trim() : "";
    return value && value !== "—" ? value : fallback;
  }

  function navigate(target) {
    if (typeof window.navigateTo === "function") window.navigateTo(target);
  }

  function ensureLocalizedJurisdictionSwitch() {
    const actions = document.querySelector(".header-actions");
    if (!actions) return;
    const c = focCopy();
    const current = normalizeJurisdiction(decodeURIComponent(getCookie("sentinela_jurisdiction") || "BR"));
    let wrap = document.getElementById("foc-jurisdiction-switch");
    if (!wrap) {
      wrap = document.createElement("div");
      wrap.id = "foc-jurisdiction-switch";
      wrap.className = "foc-jurisdiction-switch";
      actions.appendChild(wrap);
    }
    wrap.setAttribute("aria-label", c.jurisdictionAria);
    wrap.innerHTML = JURISDICTIONS.map((item) =>
      `<button type="button" data-jurisdiction="${item.id}" class="${item.id === current ? "active" : ""}">${c.jurisdictions[item.id] || item.label || item.id}</button>`
    ).join("");
    if (wrap.dataset.bound !== "1") {
      wrap.dataset.bound = "1";
      wrap.addEventListener("click", (event) => {
        const btn = event.target.closest("button[data-jurisdiction]");
        if (!btn) return;
        setJurisdictionCookie(normalizeJurisdiction(btn.dataset.jurisdiction));
        wrap.querySelectorAll("button").forEach((item) => item.classList.toggle("active", item === btn));
        const topJurisdiction = document.getElementById("foc-topbar-jurisdiction");
        if (topJurisdiction) topJurisdiction.textContent = btn.textContent.trim();
      });
    }
  }

  function ensureLocalizedTopbar() {
    const headerTop = document.querySelector(".header-top");
    const meta = document.querySelector(".header-meta");
    if (!headerTop || !meta) return;
    const c = focCopy();
    let strip = document.getElementById("foc-topbar-strip");
    if (!strip) {
      strip = document.createElement("div");
      strip.id = "foc-topbar-strip";
      strip.className = "foc-topbar-strip";
      headerTop.insertBefore(strip, meta);
    }
    const jurisdiction = normalizeJurisdiction(decodeURIComponent(getCookie("sentinela_jurisdiction") || "BR"));
    strip.innerHTML = `
      <span><b>ENV</b><em>LOCAL</em></span>
      <span><b>INST</b><em id="foc-topbar-institution">${c.scope}</em></span>
      <span><b>SYNC</b><em id="foc-topbar-sync">${c.pipelineNominal}</em></span>
      <span><b>IPED</b><em id="foc-topbar-iped">${c.waitingIngestion}</em></span>
      <span><b>JUR</b><em id="foc-topbar-jurisdiction">${c.jurisdictions[jurisdiction] || jurisdiction}</em></span>
    `;
  }

  function localizedCommandPanelHtml() {
    const c = focCopy();
    return `
      <div class="foc-command-panels" id="foc-command-panels">
        <section class="foc-panel foc-operational">
          <div class="foc-panel-head"><span>${c.operationalStatus}</span><b id="foc-status-mode">${c.pipelineNominal}</b></div>
          <div class="foc-status-grid">
            <span><b>IPED</b><em id="foc-iped-status">${c.connected}</em></span>
            <span><b>${c.agent}</b><em>${c.localAgent}</em></span>
            <span><b>${c.lastSession}</b><em id="foc-last-session">${c.waiting}</em></span>
            <span><b>${c.custody}</b><em id="foc-chain-status">${c.chainOk}</em></span>
            <span><b>${c.events}</b><em id="foc-events-count">0</em></span>
            <span><b>${c.data}</b><em id="foc-data-quality">${c.monitored}</em></span>
          </div>
        </section>

        <section class="foc-panel foc-risk">
          <div class="foc-panel-head"><span>${c.riskEvidenceMatrix}</span><b>${c.currentWindow}</b></div>
          <div class="foc-risk-grid">
            <span><b id="foc-risk-participants">0</b><em>${c.participants}</em></span>
            <span><b id="foc-risk-flags">0</b><em>${c.redFlags}</em></span>
            <span><b id="foc-risk-convergence">--</b><em>IEO/PSI</em></span>
            <span><b id="foc-risk-dissonance">${c.nominal}</b><em>${c.dissonance}</em></span>
            <span><b id="foc-risk-chronicity">${c.noData}</b><em>${c.chronicity}</em></span>
            <span><b id="foc-risk-reactivity">${c.noData}</b><em>${c.reactivity}</em></span>
          </div>
        </section>

        <aside class="foc-panel foc-next-actions">
          <div class="foc-panel-head"><span>${c.nextActions}</span><b>${c.queue}</b></div>
          <button type="button" data-target="participants">${c.reviewParticipant}</button>
          <button type="button" data-target="studies">${c.openStudy}</button>
          <button type="button" data-target="report">${c.generateReport}</button>
          <button type="button" data-target="pipeline">${c.verifyCollectionFailure}</button>
        </aside>

        <section class="foc-panel foc-session-feed">
          <div class="foc-panel-head"><span>${c.sessionFeed}</span><b>${c.ipedAgent}</b></div>
          <ol>
            <li><time id="foc-feed-time">--:--</time><span>${c.ingestionActive}</span></li>
            <li><time>sys</time><span>${c.manifestValid}</span></li>
            <li><time>audit</time><span>${c.replayAvailable}</span></li>
          </ol>
        </section>

        <section class="foc-panel foc-custody">
          <div class="foc-panel-head"><span>${c.custodyIntegrity}</span><b>${c.verifiable}</b></div>
          <div class="foc-mini-grid">
            <span>${c.chainOk}</span><span>${c.signatureVerified}</span><span>${c.replayAvailable}</span><span>${c.manifestValid}</span><span>${c.ipedRegistered}</span>
          </div>
        </section>

        <section class="foc-panel foc-psych-gate">
          <div class="foc-panel-head"><span>${c.psychometricGate}</span><b>${c.session}</b></div>
          <div class="foc-gate-row"><span>SRQ-20</span><b>${c.completed}</b></div>
          <div class="foc-gate-row"><span>DASS-21</span><b>${c.completed}</b></div>
          <div class="foc-gate-row"><span>OLBI</span><b>${c.completed}</b></div>
          <div class="foc-gate-row pending"><span>PANAS</span><b>${c.postSession}</b></div>
        </section>

        <section class="foc-panel foc-data-quality-panel">
          <div class="foc-panel-head"><span>${c.dataQuality}</span><b>${c.control}</b></div>
          <div class="foc-mini-grid">
            <span>${c.validWindows}</span><span>${c.gapsMonitored}</span><span>${c.lowQuality}</span><span>${c.discardedEvents}</span>
          </div>
        </section>

        <section class="foc-panel foc-evidence-queue">
          <div class="foc-panel-head"><span>${c.evidenceQueue}</span><b>${c.human}</b></div>
          <ol>
            <li>${c.criticalFlags}</li>
            <li>${c.psychometricDissonance}</li>
            <li>${c.degradedIntegrity}</li>
          </ol>
        </section>
      </div>
    `;
  }

  function localizedRelativeUpdate(raw) {
    const c = focCopy();
    const text = String(raw || "").trim();
    if (!text || text === c.waiting) return c.waiting;
    if (/^(agora mesmo|just now|ahora mismo)$/i.test(text)) {
      return ({ "pt-BR": "agora mesmo", "en-US": "just now", "es-ES": "ahora mismo" })[activeLocale()] || text;
    }
    const minuteMatch = text.match(/(?:ha|h[áa]|hace)?\s*(\d+)\s*min(?:\s*ago)?/i);
    if (minuteMatch) {
      const minutes = minuteMatch[1];
      return ({ "pt-BR": `há ${minutes}min`, "en-US": `${minutes}min ago`, "es-ES": `hace ${minutes}min` })[activeLocale()] || text;
    }
    return text;
  }

  function refreshLocalizedCommandCenter() {
    if (!document.getElementById("foc-command-panels")) return;
    const c = focCopy();
    const participants = shortText("kpi-participants", "0");
    const flags = shortText("kpi-flags", "0");
    const ieo = shortText("kpi-ieo", "--");
    const psi = shortText("kpi-psi", "--");
    const lastWindow = shortText("kpi-window", c.waiting);
    const lastUpdate = localizedRelativeUpdate(shortText("last-update-label", c.waiting));
    const set = (id, value) => {
      const el = document.getElementById(id);
      if (el) el.textContent = value;
    };
    set("foc-risk-participants", participants);
    set("foc-risk-flags", flags);
    set("foc-risk-convergence", `${ieo}/${psi}`);
    set("foc-events-count", participants);
    set("foc-last-session", lastWindow);
    set("foc-topbar-iped", lastUpdate === c.waiting ? c.waitingIngestion : `${c.lastIngestion} ${lastUpdate}`);
    set("foc-feed-time", lastUpdate);
    set("foc-status-mode", Number(flags) > 0 ? c.elevatedRisk : c.pipelineNominal);
  }

  function enhanceLocalizedSectionLanguage() {
    const c = focCopy();
    const overviewSub = document.querySelector("#section-overview .section-sub");
    if (overviewSub) overviewSub.textContent = c.overviewSub;
    const studiesSub = document.querySelector("#section-studies .section-sub");
    if (studiesSub) studiesSub.textContent = c.studiesSub;
    const participantsSub = document.querySelector("#section-participants .section-sub");
    if (participantsSub) participantsSub.textContent = c.participantsSub;
    const full = currentFocCopy();
    const pipeline = full.pipeline;
    if (pipeline) {
      const section = document.getElementById("section-pipeline");
      if (section) {
        const title = section.querySelector(":scope > .section-title");
        const sub = section.querySelector(":scope > .section-sub");
        const labels = section.querySelectorAll(".kpi-label");
        const cardTitle = section.querySelector(".card-title");
        if (title) title.textContent = pipeline.title;
        if (sub) sub.textContent = pipeline.sub;
        if (labels[0]) labels[0].textContent = pipeline.status;
        if (labels[1]) labels[1].textContent = pipeline.ieoWindows;
        if (labels[2]) labels[2].textContent = pipeline.psychometrics;
        if (labels[3]) labels[3].textContent = pipeline.redFlags;
        if (cardTitle) cardTitle.textContent = pipeline.checks;
        const loading = section.querySelector("#pipeline-checks .loading-msg");
        if (loading) loading.innerHTML = `<div class="spinner"></div> ${pipeline.loading}`;
      }
    }
    if (full.report) {
      const section = document.getElementById("section-report");
      if (section) {
        const title = section.querySelector(":scope > .section-title");
        const sub = section.querySelector(":scope > .section-sub");
        const heading = section.querySelector("[data-report-card-title]");
        const body = section.querySelector("[data-report-card-body]");
        const button = section.querySelector("[data-report-generate]");
        const hint = section.querySelector("[data-report-hint]");
        if (title) title.textContent = full.report.title;
        if (sub) sub.textContent = full.report.sub;
        if (heading) heading.textContent = full.report.cardTitle;
        if (body) body.textContent = full.report.cardBody;
        if (button) button.textContent = full.report.generate;
        if (hint) hint.textContent = full.report.hint;
      }
      const modalTitle = document.querySelector("#rpt-head .rpt-title");
      const modalSub = document.querySelector("#rpt-head .rpt-sub");
      const footButtons = document.querySelectorAll("#rpt-foot button");
      if (modalTitle) modalTitle.textContent = full.report.modalTitle;
      if (modalSub && modalSub.id === "rpt-ts" && !modalSub.dataset.generated) modalSub.textContent = full.report.modalSub;
      if (footButtons[0]) footButtons[0].textContent = full.report.print;
      if (footButtons[1]) footButtons[1].textContent = full.report.copy;
      if (footButtons[2]) footButtons[2].textContent = full.report.close;
    }
  }

  function ensureJurisdictionSwitch() {
    return ensureLocalizedJurisdictionSwitch();
    const actions = document.querySelector(".header-actions");
    if (!actions || document.getElementById("foc-jurisdiction-switch")) return;
    const current = normalizeJurisdiction(decodeURIComponent(getCookie("sentinela_jurisdiction") || "BR"));
    const wrap = document.createElement("div");
    wrap.id = "foc-jurisdiction-switch";
    wrap.className = "foc-jurisdiction-switch";
    wrap.setAttribute("aria-label", "Selecionar jurisdição");
    wrap.innerHTML = JURISDICTIONS.map((item) =>
      `<button type="button" data-jurisdiction="${item.id}" class="${item.id === current ? "active" : ""}">${item.label}</button>`
    ).join("");
    wrap.addEventListener("click", (event) => {
      const btn = event.target.closest("button[data-jurisdiction]");
      if (!btn) return;
      setJurisdictionCookie(normalizeJurisdiction(btn.dataset.jurisdiction));
      wrap.querySelectorAll("button").forEach((item) => item.classList.toggle("active", item === btn));
      const topJurisdiction = document.getElementById("foc-topbar-jurisdiction");
      if (topJurisdiction) topJurisdiction.textContent = btn.textContent.trim();
    });
    actions.appendChild(wrap);
  }

  function ensureTopbar() {
    return ensureLocalizedTopbar();
    const headerTop = document.querySelector(".header-top");
    const meta = document.querySelector(".header-meta");
    if (!headerTop || !meta) return;
    let strip = document.getElementById("foc-topbar-strip");
    if (!strip) {
      strip = document.createElement("div");
      strip.id = "foc-topbar-strip";
      strip.className = "foc-topbar-strip";
      strip.innerHTML = `
        <span><b>ENV</b><em>LOCAL</em></span>
        <span><b>INST</b><em id="foc-topbar-institution">Escopo atual</em></span>
        <span><b>SYNC</b><em id="foc-topbar-sync">Pipeline nominal</em></span>
        <span><b>IPED</b><em id="foc-topbar-iped">Aguardando ingestão</em></span>
        <span><b>JUR</b><em id="foc-topbar-jurisdiction">Brasil</em></span>
      `;
      headerTop.insertBefore(strip, meta);
    }
  }

  function enhanceNav() {
    const nav = document.getElementById("nav");
    if (!nav) return;
    const c = focCopy();
    const zoneMap = {
      "Command Center": c.zones.command,
      "Case Workspace": c.zones.case,
      "Forensic Audit": c.zones.audit,
    };
    const localZone = (zone) => zoneMap[zone] || zone || c.zones.command;
    const app = document.getElementById("app-shell");
    const header = document.querySelector(".header");
    if (app && header && nav.parentElement === header) {
      app.insertBefore(nav, header);
    }
    if (!nav.querySelector(".foc-sidebar-brand")) {
      nav.insertAdjacentHTML("afterbegin", `
        <div class="foc-sidebar-brand">
          <div class="foc-brand-mark">S4</div>
          <div><strong>SENTINELA</strong><span>${c.sidebarSubtitle}</span></div>
        </div>
        <div class="foc-zone-title">${c.zones.command}</div>
      `);
    } else {
      const subtitle = nav.querySelector(".foc-sidebar-brand span");
      if (subtitle) subtitle.textContent = c.sidebarSubtitle;
      const firstZone = nav.querySelector(".foc-zone-title");
      if (firstZone) firstZone.textContent = c.zones.command;
    }
    let lastZone = c.zones.command;
    [...nav.querySelectorAll(".nav-tab")].forEach((tab) => {
      const meta = NAV_META[tab.dataset.tab] || { icon: "OP", zone: "Command Center", label: tab.textContent.trim() };
      const localizedZone = localZone(meta.zone);
      tab.dataset.zone = localizedZone;
      if (!tab.querySelector(".foc-nav-code")) {
        const label = tab.textContent.trim();
        tab.innerHTML = `<span class="foc-nav-code">${meta.icon}</span><span class="foc-nav-text">${label}</span>`;
      }
      if (localizedZone !== lastZone && !tab.previousElementSibling?.classList.contains("foc-zone-title")) {
        const title = document.createElement("div");
        title.className = "foc-zone-title";
        title.textContent = localizedZone;
        tab.insertAdjacentElement("beforebegin", title);
      } else if (tab.previousElementSibling?.classList.contains("foc-zone-title")) {
        tab.previousElementSibling.textContent = localizedZone;
      }
      lastZone = localizedZone;
    });
  }

  function commandPanelHtml() {
    return localizedCommandPanelHtml();
  }

  function ensureCommandCenter() {
    const overview = document.getElementById("section-overview");
    if (!overview || document.getElementById("foc-command-panels")) return;
    overview.querySelectorAll(".ux-decision-panel").forEach((node) => node.remove());
    const sub = overview.querySelector(".section-sub") || overview.querySelector(".section-title");
    sub.insertAdjacentHTML("afterend", commandPanelHtml());
    document.getElementById("foc-command-panels").addEventListener("click", (event) => {
      const btn = event.target.closest("button[data-target]");
      if (btn) navigate(btn.dataset.target);
    });
  }

  function refreshCommandCenter() {
    return refreshLocalizedCommandCenter();
    if (!document.getElementById("foc-command-panels")) return;
    const participants = shortText("kpi-participants", "0");
    const flags = shortText("kpi-flags", "0");
    const ieo = shortText("kpi-ieo", "--");
    const psi = shortText("kpi-psi", "--");
    const lastWindow = shortText("kpi-window", "aguardando");
    const lastUpdate = shortText("last-update-label", "aguardando");
    const set = (id, value) => {
      const el = document.getElementById(id);
      if (el) el.textContent = value;
    };
    set("foc-risk-participants", participants);
    set("foc-risk-flags", flags);
    set("foc-risk-convergence", `${ieo}/${psi}`);
    set("foc-events-count", participants);
    set("foc-last-session", lastWindow);
    set("foc-topbar-iped", lastUpdate === "aguardando" ? "Aguardando ingestão" : `Última ingestão ${lastUpdate}`);
    set("foc-feed-time", lastUpdate);
    set("foc-status-mode", Number(flags) > 0 ? "Risco agregado elevado" : "Pipeline nominal");
  }

  function enhanceSectionLanguage() {
    return enhanceLocalizedSectionLanguage();
    const overviewSub = document.querySelector("#section-overview .section-sub");
    if (overviewSub) overviewSub.textContent = "Coleta, risco e próxima ação operacional.";
    const studiesSub = document.querySelector("#section-studies .section-sub");
    if (studiesSub) studiesSub.textContent = "Matriz de instituição, estudo, caso, coleta e integridade.";
    const participantsSub = document.querySelector("#section-participants .section-sub");
    if (participantsSub) participantsSub.textContent = "Matriz operacional por participante pseudonimizado.";
  }

  function wireTableActions() {
    if (document.body.dataset.focTableActions === "1") return;
    document.body.dataset.focTableActions = "1";
    document.addEventListener("click", (event) => {
      const btn = event.target.closest(".foc-table-action[data-target]");
      if (!btn) return;
      event.preventDefault();
      event.stopPropagation();
      navigate(btn.dataset.target);
    });
  }

  function enhanceForensicConsole() {
    const app = document.getElementById("app-shell");
    if (!app || !visible(app)) return;
    document.body.classList.add("forensic-console");
    ensureJurisdictionSwitch();
    ensureTopbar();
    enhanceNav();
    ensureCommandCenter();
    enhanceSectionLanguage();
    wireTableActions();
    refreshCommandCenter();
  }

  window.SENTINELA_FORensicConsole = { enhance: enhanceForensicConsole, refresh: refreshCommandCenter };

  ready(() => {
    enhanceForensicConsole();
    window.addEventListener("sentinela:locale-changed", () => {
      const panels = document.getElementById("foc-command-panels");
      if (panels) panels.remove();
      enhanceForensicConsole();
    });
    setInterval(enhanceForensicConsole, 1200);
    setInterval(refreshCommandCenter, 1500);
  });
})();
