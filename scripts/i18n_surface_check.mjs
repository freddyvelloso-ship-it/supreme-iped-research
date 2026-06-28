import { readFileSync } from "node:fs";
import vm from "node:vm";

const LOCALES = ["pt-BR", "en-US", "es-ES"];
const INSTRUMENTS = {
  SRQ20: 20,
  DASS21: 21,
  OLBI: 16,
  PANAS_SHORT: 10,
};

const REQUIRED_FORM_KEYS = [
  "title",
  "subtitle",
  "instruction",
  "scaleHint",
  "scale",
  "questions",
  "session_secure",
  "session_unavailable",
  "back",
  "next",
  "submit",
  "item_label",
  "of_label",
  "complete_before_submit",
  "submitting",
  "retry",
  "submitted",
  "fineprint",
  "notice",
];

const REQUIRED_SENTINELA_KEYS = [
  "brand",
  "loginSub",
  "accessTitle",
  "accessBody",
  "heroBadge",
  "heroBody",
  "heroApiStatus",
  "heroData",
  "heroDataStatus",
  "heroUse",
  "heroUseStatus",
  "loginEmailLabel",
  "loginPasswordLabel",
  "rememberAccess",
  "loginButton",
  "logout",
  "warRoom",
  "nextDecision",
  "nextDecisionTitle",
  "nextDecisionBody",
  "actions",
  "tabs",
  "cycle",
  "foc",
  "pipeline",
  "report",
];

const REQUIRED_TABS = [
  "overview",
  "studies",
  "pipeline",
  "dataquality",
  "ieo",
  "participants",
  "flags",
  "psycho",
  "history",
  "baseline",
  "longitudinal",
  "exports",
  "report",
];

const REQUIRED_FOC_KEYS = [
  "jurisdictionAria",
  "jurisdictions",
  "sidebarSubtitle",
  "scope",
  "pipelineNominal",
  "waitingIngestion",
  "operationalStatus",
  "connected",
  "agent",
  "localAgent",
  "lastSession",
  "custody",
  "chainOk",
  "events",
  "data",
  "riskEvidenceMatrix",
  "currentWindow",
  "participants",
  "redFlags",
  "nominal",
  "dissonance",
  "chronicity",
  "reactivity",
  "nextActions",
  "reviewParticipant",
  "openStudy",
  "generateReport",
  "verifyCollectionFailure",
  "sessionFeed",
  "ipedAgent",
  "custodyIntegrity",
  "psychometricGate",
  "dataQuality",
  "evidenceQueue",
  "overviewSub",
  "studiesSub",
  "participantsSub",
];

const REQUIRED_PIPELINE_KEYS = [
  "title",
  "sub",
  "status",
  "ieoWindows",
  "psychometrics",
  "redFlags",
  "checks",
  "loading",
  "noChecks",
  "ok",
  "noData",
  "labels",
];

const REQUIRED_PIPELINE_LABELS = [
  "supreme_outputs_present",
  "psychometric_outputs_present",
  "red_flags_present",
];

const REQUIRED_REPORT_KEYS = [
  "title",
  "sub",
  "cardTitle",
  "cardBody",
  "generate",
  "hint",
  "modalTitle",
  "modalSub",
  "loading",
  "loadingEndpoints",
  "generatedAt",
  "print",
  "copy",
  "close",
  "sections",
  "fields",
  "values",
  "warning",
  "auditLimit",
  "signatures",
  "narrative",
  "recommendations",
];

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function containsMojibake(value) {
  if (typeof value === "string") return /Ã[\u0080-\u00bf]|Â[\u0080-\u00bf]|â€|â€”|â€¦|�/.test(value);
  if (Array.isArray(value)) return value.some(containsMojibake);
  if (value && typeof value === "object") return Object.values(value).some(containsMojibake);
  return false;
}

function flattenStrings(value, acc = []) {
  if (typeof value === "string") acc.push(value);
  else if (Array.isArray(value)) value.forEach((item) => flattenStrings(item, acc));
  else if (value && typeof value === "object") Object.values(value).forEach((item) => flattenStrings(item, acc));
  return acc;
}

const FORBIDDEN_FOC_COPY = {
  "pt-BR": [
    "Operational Status",
    "Risk & Evidence Matrix",
    "Next Actions",
    "Session Feed",
    "Custody Integrity",
    "Psychometric Gate",
    "Data Quality",
    "Evidence Queue",
    "Forensic Operations Console",
    "Command Center",
    "Case Workspace",
    "Forensic Audit",
  ],
  "es-ES": [
    "Operational Status",
    "Risk & Evidence Matrix",
    "Next Actions",
    "Session Feed",
    "Custody Integrity",
    "Psychometric Gate",
    "Data Quality",
    "Evidence Queue",
    "Forensic Operations Console",
    "Command Center",
    "Case Workspace",
    "Forensic Audit",
  ],
};

function extractObjectSource(source, marker) {
  const markerIndex = source.indexOf(marker);
  assert(markerIndex >= 0, `marker not found: ${marker}`);
  const start = source.indexOf("{", markerIndex);
  assert(start >= 0, `object start not found for ${marker}`);
  let depth = 0;
  let quote = "";
  let escaped = false;
  for (let index = start; index < source.length; index += 1) {
    const ch = source[index];
    if (quote) {
      if (escaped) escaped = false;
      else if (ch === "\\") escaped = true;
      else if (ch === quote) quote = "";
      continue;
    }
    if (ch === '"' || ch === "'" || ch === "`") {
      quote = ch;
      continue;
    }
    if (ch === "{") depth += 1;
    if (ch === "}") {
      depth -= 1;
      if (depth === 0) return source.slice(start, index + 1);
    }
  }
  throw new Error(`object end not found for ${marker}`);
}

async function checkFormI18n(baseUrl) {
  const validated = [];
  for (const locale of LOCALES) {
    for (const [instrument, expectedQuestions] of Object.entries(INSTRUMENTS)) {
      const url = `${baseUrl}/v1/forms/i18n/${encodeURIComponent(locale)}?instrument=${encodeURIComponent(instrument)}`;
      const response = await fetch(url);
      assert(response.ok, `form i18n HTTP ${response.status}: ${locale}/${instrument}`);
      const payload = await response.json();
      for (const key of REQUIRED_FORM_KEYS) {
        assert(payload[key] !== undefined && payload[key] !== null && payload[key] !== "", `missing form key ${locale}/${instrument}/${key}`);
      }
      assert(payload.locale === locale, `unexpected locale ${payload.locale} for ${locale}/${instrument}`);
      assert(Array.isArray(payload.questions), `questions not array for ${locale}/${instrument}`);
      assert(payload.questions.length === expectedQuestions, `wrong question count for ${locale}/${instrument}`);
      assert(Array.isArray(payload.scale) && payload.scale.length >= 2, `invalid scale for ${locale}/${instrument}`);
      assert(!containsMojibake(payload), `mojibake in form payload ${locale}/${instrument}`);
      validated.push(`${locale}/${instrument}`);
    }
  }
  return validated;
}

function checkSentinelaI18n(sourcePath) {
  const source = readFileSync(sourcePath, "utf8");
  const dashboardSource = readFileSync("sentinela/static/index.html", "utf8");
  const i18n = vm.runInNewContext(`(${extractObjectSource(source, "const I18N =")})`);
  const validated = [];
  for (const locale of LOCALES) {
    const payload = i18n[locale];
    assert(payload, `missing SENTINELA locale ${locale}`);
    for (const key of REQUIRED_SENTINELA_KEYS) {
      assert(payload[key] !== undefined, `missing SENTINELA key ${locale}/${key}`);
    }
    for (const tab of REQUIRED_TABS) {
      assert(payload.tabs[tab], `missing SENTINELA tab ${locale}/${tab}`);
    }
    for (const key of REQUIRED_FOC_KEYS) {
      assert(payload.foc[key] !== undefined, `missing SENTINELA foc key ${locale}/${key}`);
    }
    for (const key of REQUIRED_PIPELINE_KEYS) {
      assert(payload.pipeline[key] !== undefined, `missing SENTINELA pipeline key ${locale}/${key}`);
    }
    for (const key of REQUIRED_PIPELINE_LABELS) {
      assert(payload.pipeline.labels[key], `missing SENTINELA pipeline label ${locale}/${key}`);
    }
    for (const key of REQUIRED_REPORT_KEYS) {
      assert(payload.report[key] !== undefined, `missing SENTINELA report key ${locale}/${key}`);
    }
    for (const jurisdiction of ["BR", "EU", "US", "INT"]) {
      assert(payload.foc.jurisdictions[jurisdiction], `missing SENTINELA jurisdiction ${locale}/${jurisdiction}`);
    }
    assert(Array.isArray(payload.actions) && payload.actions.length === 3, `invalid SENTINELA actions ${locale}`);
    assert(Array.isArray(payload.cycle) && payload.cycle.length === 4, `invalid SENTINELA cycle ${locale}`);
    assert(!containsMojibake(payload), `mojibake in SENTINELA i18n ${locale}`);
    for (const forbidden of FORBIDDEN_FOC_COPY[locale] || []) {
      assert(!flattenStrings(payload.foc).includes(forbidden), `foreign FOC label in ${locale}: ${forbidden}`);
    }
    validated.push(locale);
  }
  assert(!dashboardSource.includes("key.replaceAll('_', ' ')"), "pipeline renders raw API keys instead of localized labels");
  assert(!dashboardSource.includes("supreme outputs present"), "raw pipeline label found in dashboard source");
  assert(!dashboardSource.includes("psychometric outputs present"), "raw pipeline label found in dashboard source");
  assert(!dashboardSource.includes("red flags present sem dado"), "mixed raw pipeline label found in dashboard source");
  return validated;
}

async function main() {
  const baseUrlArgIndex = process.argv.indexOf("--base-url");
  const baseUrlInput = baseUrlArgIndex >= 0 && process.argv[baseUrlArgIndex + 1]
    ? process.argv[baseUrlArgIndex + 1]
    : process.env.BASE_URL || "http://127.0.0.1:18000";
  const baseUrl = baseUrlInput.replace(/\/$/, "");
  const forms = await checkFormI18n(baseUrl);
  const sentinela = checkSentinelaI18n("sentinela/static/sentinela-ux.js");
  console.log(JSON.stringify({ status: "ok", forms_validated: forms.length, sentinela_locales: sentinela }, null, 2));
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
