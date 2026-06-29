import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";

const PRE_INSTRUMENTS = {
  SRQ20: Array(20).fill(0),
  DASS21: Array(21).fill(1),
  OLBI: Array(16).fill(2),
};
const POST_INSTRUMENT = { PANAS_SHORT: Array(10).fill(2) };

function readEnvValue(filePath, key) {
  for (const line of readFileSync(filePath, "utf8").split(/\r?\n/)) {
    if (line.startsWith(`${key}=`)) return line.split("=").slice(1).join("=").trim().replace(/^['"]|['"]$/g, "");
  }
  return undefined;
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function requestJson(url, { method = "GET", token, body } = {}) {
  const response = await fetch(url, {
    method,
    headers: {
      ...(body ? { "Content-Type": "application/json" } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  const text = await response.text();
  const payload = text ? JSON.parse(text) : {};
  if (!response.ok) {
    const detail = payload.detail ? JSON.stringify(payload.detail) : text;
    throw new Error(`HTTP ${response.status} ${url}: ${detail}`);
  }
  return payload;
}

function pseudonymize(value) {
  return createHash("sha256").update(value, "utf8").digest("hex");
}

function composePsql(service, database, user, sql) {
  const project = process.env.COMPOSE_PROJECT_NAME || "supreme-v4-test-clone";
  return execFileSync("docker", [
    "compose",
    "-p",
    project,
    "-f",
    "docker-compose.production.yml",
    "-f",
    "docker-compose.local.yml",
    "exec",
    "-T",
    service,
    "psql",
    "-U",
    user,
    "-d",
    database,
    "-tAc",
    sql,
  ], { encoding: "utf8" }).trim();
}

function assertLauncherOrdering() {
  const launcher = readFileSync("LAUNCHER_IPED.ps1", "utf8");
  const preStart = launcher.indexOf("$preInstruments = @(");
  const preEnd = launcher.indexOf(")", preStart);
  const preBlock = launcher.slice(preStart, preEnd);
  assert(preStart >= 0 && preEnd > preStart, "Bloco preInstruments nao encontrado no launcher.");
  for (const instrument of Object.keys(PRE_INSTRUMENTS)) {
    assert(preBlock.includes(instrument), `Launcher nao lista ${instrument} como pre-sessao.`);
  }
  assert(!preBlock.includes("PANAS_SHORT"), "PANAS_SHORT apareceu no bloco pre-sessao.");

  const sessionStartIndex = launcher.indexOf('event_type":"session_start"');
  const ipedStartIndex = launcher.indexOf("Start-Process", sessionStartIndex);
  const sessionEndIndex = launcher.indexOf('event_type":"session_end"');
  const panasIndex = launcher.indexOf('New-FormLink "PANAS_SHORT"');
  assert(sessionStartIndex > 0, "Launcher nao registra session_start.");
  assert(ipedStartIndex > sessionStartIndex, "Launcher nao abre IPED depois de session_start.");
  assert(sessionEndIndex > ipedStartIndex, "Launcher nao registra session_end depois da sessao IPED.");
  assert(panasIndex > sessionEndIndex, "PANAS nao esta restrito ao bloco pos-sessao.");
}

async function dueNow(baseUrl, apiSecret, idHash) {
  const schedule = await requestJson(`${baseUrl}/v1/schedule/${encodeURIComponent(idHash)}`, { token: apiSecret });
  return new Set(schedule.due_now || []);
}

async function createLinksWithoutSubmit(baseUrl, apiSecret, idHash) {
  const links = {};
  for (const instrument of [...Object.keys(PRE_INSTRUMENTS), ...Object.keys(POST_INSTRUMENT)]) {
    const link = await requestJson(`${baseUrl}/v1/forms/link`, {
      method: "POST",
      token: apiSecret,
      body: { id_hash: idHash, instrument },
    });
    assert(!String(link.launch_url).includes("token="), `token em URL de formulario ${instrument}`);
    assert(!String(link.launch_url).includes("ticket="), `ticket em URL de formulario ${instrument}`);
    links[instrument] = link.launch_url;
  }
  return links;
}

async function submitInstrument(baseUrl, ingestToken, idHash, instrument, responses) {
  return requestJson(`${baseUrl}/v1/psychometric/submit`, {
    method: "POST",
    token: ingestToken,
    body: { id_hash: idHash, instrument, responses },
  });
}

async function ingestSessionEvent(baseUrl, ingestToken, idHash, eventType) {
  const timestamp = new Date().toISOString();
  return requestJson(`${baseUrl}/v1/events/ingest`, {
    method: "POST",
    token: ingestToken,
    body: {
      events: [{
        user_identifier: idHash,
        timestamp,
        event_type: eventType,
        media_type: "preview",
        severity: 1,
        duration_seconds: 0,
        source_tool: "iped",
      }],
    },
  });
}

async function main() {
  const baseUrlArgIndex = process.argv.indexOf("--base-url");
  const baseUrlInput = baseUrlArgIndex >= 0 && process.argv[baseUrlArgIndex + 1]
    ? process.argv[baseUrlArgIndex + 1]
    : process.env.BASE_URL || "http://127.0.0.1:18000";
  const baseUrl = baseUrlInput.replace(/\/$/, "");
  const apiSecret = process.env.API_SECRET_KEY || readEnvValue("supreme-backend/.env.production", "API_SECRET_KEY");
  const ingestToken = process.env.API_INGEST_TOKEN || readEnvValue("supreme-backend/.env.production", "API_INGEST_TOKEN");
  assert(apiSecret, "API_SECRET_KEY ausente.");
  assert(ingestToken, "API_INGEST_TOKEN ausente.");

  assertLauncherOrdering();

  const idHash = pseudonymize(`journey-gate-${Date.now()}`);
  const initialDue = await dueNow(baseUrl, apiSecret, idHash);
  for (const instrument of Object.keys(PRE_INSTRUMENTS)) {
    assert(initialDue.has(instrument), `Agenda inicial nao marcou ${instrument} como devido.`);
  }

  const links = await createLinksWithoutSubmit(baseUrl, apiSecret, idHash);
  const dueAfterLinks = await dueNow(baseUrl, apiSecret, idHash);
  for (const instrument of Object.keys(PRE_INSTRUMENTS)) {
    assert(dueAfterLinks.has(instrument), `Gerar/abrir link liberou indevidamente ${instrument}.`);
  }

  await submitInstrument(baseUrl, ingestToken, idHash, "SRQ20", PRE_INSTRUMENTS.SRQ20);
  await submitInstrument(baseUrl, ingestToken, idHash, "DASS21", PRE_INSTRUMENTS.DASS21);
  const dueAfterPartial = await dueNow(baseUrl, apiSecret, idHash);
  assert(dueAfterPartial.has("OLBI"), "IPED seria liberado antes de OLBI.");

  await submitInstrument(baseUrl, ingestToken, idHash, "OLBI", PRE_INSTRUMENTS.OLBI);
  const dueAfterPre = await dueNow(baseUrl, apiSecret, idHash);
  for (const instrument of Object.keys(PRE_INSTRUMENTS)) {
    assert(!dueAfterPre.has(instrument), `Pre-sessao ainda pendente apos submissao: ${instrument}`);
  }
  assert(dueAfterPre.has("PANAS_SHORT"), "PANAS nao permaneceu como instrumento pos-sessao devido.");

  await ingestSessionEvent(baseUrl, ingestToken, idHash, "session_start");
  await ingestSessionEvent(baseUrl, ingestToken, idHash, "session_end");
  await submitInstrument(baseUrl, ingestToken, idHash, "PANAS_SHORT", POST_INSTRUMENT.PANAS_SHORT);

  const safeId = idHash.replace(/'/g, "''");
  const supremeInstruments = composePsql(
    "supreme-db",
    "supreme",
    "supreme",
    `SELECT instrument FROM psychometric_submissions WHERE id_hash='${safeId}' ORDER BY instrument;`
  ).split(/\r?\n/).filter(Boolean);
  const supremeEvents = composePsql(
    "supreme-db",
    "supreme",
    "supreme",
    `SELECT event_type FROM events_raw WHERE id_hash='${safeId}' AND event_type IN ('session_start','session_end') ORDER BY event_type;`
  ).split(/\r?\n/).filter(Boolean);
  const sentinelaInstruments = composePsql(
    "sentinela-db",
    "sentinela",
    "sentinela",
    `SELECT instrument FROM psico_submissions WHERE id_hash='${safeId}' ORDER BY instrument;`
  ).split(/\r?\n/).filter(Boolean);

  for (const instrument of [...Object.keys(PRE_INSTRUMENTS), ...Object.keys(POST_INSTRUMENT)]) {
    assert(supremeInstruments.includes(instrument), `SUPREME nao persistiu ${instrument}.`);
    assert(sentinelaInstruments.includes(instrument), `SENTINELA nao recebeu ${instrument}.`);
  }
  assert(supremeEvents.includes("session_start"), "SUPREME nao persistiu session_start.");
  assert(supremeEvents.includes("session_end"), "SUPREME nao persistiu session_end.");

  console.log(JSON.stringify({
    status: "ok",
    id_hash: idHash,
    generated_links: Object.keys(links),
    initial_due: [...initialDue].sort(),
    due_after_links: [...dueAfterLinks].sort(),
    due_after_partial: [...dueAfterPartial].sort(),
    due_after_pre: [...dueAfterPre].sort(),
    supreme_instruments: supremeInstruments,
    sentinela_instruments: sentinelaInstruments,
    supreme_session_events: supremeEvents,
  }, null, 2));
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
