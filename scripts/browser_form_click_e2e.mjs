import { execFileSync, spawn } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";

const INSTRUMENTS = {
  SRQ20: { form: "srq20", choiceIndex: 0, minimumScore: 0 },
  DASS21: { form: "dass21", choiceIndex: 1, minimumScore: 0 },
  OLBI: { form: "olbi", choiceIndex: 1, minimumScore: 0 },
  PANAS_SHORT: { form: "panas", choiceIndex: 1, minimumScore: 0 },
};

function argValue(name, fallback) {
  const index = process.argv.indexOf(name);
  return index >= 0 && process.argv[index + 1] ? process.argv[index + 1] : fallback;
}

function readEnvValue(filePath, key) {
  if (!existsSync(filePath)) return undefined;
  for (const line of readFileSync(filePath, "utf8").split(/\r?\n/)) {
    if (line.startsWith(`${key}=`)) {
      return line.split("=").slice(1).join("=").trim().replace(/^['"]|['"]$/g, "");
    }
  }
  return undefined;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  const text = await response.text();
  let body = {};
  if (text) {
    try {
      body = JSON.parse(text);
    } catch {
      body = { raw: text };
    }
  }
  if (!response.ok) {
    throw new Error(`HTTP ${response.status} for ${url}: ${body.detail || body.raw || "no body"}`);
  }
  return body;
}

function findChrome() {
  const candidates = [
    process.env.CHROME_PATH,
    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
    "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
    "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
  ].filter(Boolean);
  const found = candidates.find((candidate) => existsSync(candidate));
  if (!found) {
    throw new Error("Chrome/Edge nao encontrado para teste de navegador.");
  }
  return found;
}

async function waitForChrome(port, timeoutMs = 12000) {
  const deadline = Date.now() + timeoutMs;
  let lastError;
  while (Date.now() < deadline) {
    try {
      const tabs = await fetchJson(`http://127.0.0.1:${port}/json/list`);
      const page = tabs.find((tab) => tab.type === "page" && tab.webSocketDebuggerUrl);
      if (page) return page.webSocketDebuggerUrl;
    } catch (error) {
      lastError = error;
    }
    await sleep(250);
  }
  throw new Error(`Timeout aguardando Chrome DevTools: ${lastError?.message || "sem resposta"}`);
}

class Cdp {
  constructor(wsUrl) {
    this.ws = new WebSocket(wsUrl);
    this.id = 1;
    this.pending = new Map();
    this.events = [];
  }

  async open() {
    await new Promise((resolve, reject) => {
      const timeout = setTimeout(() => reject(new Error("Timeout abrindo WebSocket CDP")), 8000);
      this.ws.addEventListener("open", () => {
        clearTimeout(timeout);
        resolve();
      }, { once: true });
      this.ws.addEventListener("error", reject, { once: true });
      this.ws.addEventListener("message", (event) => {
        const message = JSON.parse(event.data);
        if (message.id && this.pending.has(message.id)) {
          const { resolve, reject } = this.pending.get(message.id);
          this.pending.delete(message.id);
          if (message.error) reject(new Error(message.error.message));
          else resolve(message.result || {});
          return;
        }
        if (message.method) this.events.push(message);
      });
    });
  }

  send(method, params = {}) {
    const id = this.id++;
    const payload = JSON.stringify({ id, method, params });
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error(`Timeout CDP ${method}`));
      }, 12000);
      this.pending.set(id, {
        resolve: (value) => {
          clearTimeout(timeout);
          resolve(value);
        },
        reject: (error) => {
          clearTimeout(timeout);
          reject(error);
        },
      });
      this.ws.send(payload);
    });
  }

  async evaluate(expression, awaitPromise = true) {
    const result = await this.send("Runtime.evaluate", {
      expression,
      awaitPromise,
      returnByValue: true,
      userGesture: true,
    });
    if (result.exceptionDetails) {
      throw new Error(result.exceptionDetails.text || "Runtime.evaluate exception");
    }
    return result.result?.value;
  }

  async navigate(url) {
    await this.send("Page.navigate", { url });
    const deadline = Date.now() + 12000;
    while (Date.now() < deadline) {
      const state = await this.evaluate("document.readyState", false);
      if (state === "complete" || state === "interactive") return;
      await sleep(150);
    }
    throw new Error(`Timeout carregando ${url}`);
  }

  close() {
    try {
      this.ws.close();
    } catch {
      // best effort
    }
  }
}

function dockerComposeExec(service, sql) {
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
    service === "supreme-db" ? "supreme" : "sentinela",
    "-d",
    service === "supreme-db" ? "supreme" : "sentinela",
    "-tAc",
    sql,
  ], { encoding: "utf8" }).trim();
}

async function waitForDatabaseRecord(service, table, idHash, instrument) {
  const deadline = Date.now() + 20000;
  const safeIdHash = idHash.replace(/'/g, "''");
  const safeInstrument = instrument.replace(/'/g, "''");
  const sql = `SELECT COUNT(*) FROM ${table} WHERE id_hash='${safeIdHash}' AND instrument='${safeInstrument}';`;
  let last = "0";
  while (Date.now() < deadline) {
    last = dockerComposeExec(service, sql);
    if (Number(last) >= 1) return Number(last);
    await sleep(500);
  }
  throw new Error(`Registro ausente em ${service}.${table} para ${instrument}; ultimo count=${last}`);
}

async function main() {
  const baseUrl = argValue("--base-url", process.env.BASE_URL || "http://127.0.0.1:18000").replace(/\/$/, "");
  const envFile = argValue("--env-file", "supreme-backend/.env.production");
  const apiSecret = process.env.API_SECRET_KEY || readEnvValue(envFile, "API_SECRET_KEY");
  if (!apiSecret) throw new Error("API_SECRET_KEY ausente.");

  const chromePath = findChrome();
  const port = Number(argValue("--cdp-port", String(9300 + Math.floor(Math.random() * 500))));
  const runId = `browser-form-${Date.now()}`;
  const userDataDir = path.join(process.cwd(), "tmp", runId);
  mkdirSync(userDataDir, { recursive: true });

  const chrome = spawn(chromePath, [
    "--headless=new",
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${userDataDir}`,
    "--disable-gpu",
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-background-networking",
    "about:blank",
  ], { stdio: "ignore", windowsHide: true });

  const results = [];
  let cdp;
  try {
    const wsUrl = await waitForChrome(port);
    cdp = new Cdp(wsUrl);
    await cdp.open();
    await cdp.send("Page.enable");
    await cdp.send("Runtime.enable");

    for (const [instrument, config] of Object.entries(INSTRUMENTS)) {
      const idHash = `${runId}-${instrument.toLowerCase().replace(/_/g, "-")}`;
      const link = await fetchJson(`${baseUrl}/v1/forms/link`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${apiSecret}`,
        },
        body: JSON.stringify({ id_hash: idHash, instrument }),
      });

      if (String(link.launch_url).includes("token=") || String(link.launch_url).includes("ticket=")) {
        throw new Error(`URL insegura gerada para ${instrument}`);
      }

      await cdp.navigate(`${baseUrl}${link.launch_url}`);
      await sleep(700);

      const clickResult = await cdp.evaluate(`(async () => {
        const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
        const text = (selector) => (document.querySelector(selector)?.textContent || "").trim();
        const button = (selector) => document.querySelector(selector);
        const total = Number((text("#count").split("/")[1] || "0").trim());
        const initial = {
          title: document.title,
          current: text("#q-index"),
          count: text("#count"),
          submitDisabled: Boolean(button("#submit")?.disabled)
        };
        const choices = () => Array.from(document.querySelectorAll("button.choice"));
        if (!total || choices().length < 1) throw new Error("Formulario sem botoes de escolha renderizados.");

        choices()[${config.choiceIndex}]?.click();
        await sleep(260);
        const afterChoice = { current: text("#q-index"), count: text("#count") };

        button("#back")?.click();
        await sleep(160);
        const afterBack = { current: text("#q-index"), count: text("#count") };

        button("#next")?.click();
        await sleep(160);
        const afterNext = { current: text("#q-index"), count: text("#count") };

        let guard = 0;
        while (Number(text("#count").split("/")[0]) < total && guard < total + 3) {
          const available = choices();
          if (!available.length) throw new Error("Botoes de resposta desapareceram.");
          available[Math.min(${config.choiceIndex}, available.length - 1)].click();
          await sleep(245);
          guard += 1;
        }

        const beforeSubmit = {
          current: text("#q-index"),
          count: text("#count"),
          submitDisabled: Boolean(button("#submit")?.disabled),
          submitLabel: text("#submit")
        };
        if (beforeSubmit.submitDisabled) throw new Error("Botao finalizar continuou desabilitado apos preencher tudo.");

        button("#submit")?.click();
        const deadline = Date.now() + 7000;
        while (Date.now() < deadline) {
          const msg = text("#msg");
          if (msg.includes("transmitid") || msg.includes("submitted") || msg.includes("transmitidas")) break;
          if (msg.startsWith("Erro:")) throw new Error(msg);
          await sleep(200);
        }
        const finalMessage = text("#msg");
        if (!finalMessage) throw new Error("Formulario nao exibiu mensagem final.");
        if (finalMessage.startsWith("Erro:")) throw new Error(finalMessage);
        return {
          instrument: "${instrument}",
          total,
          initial,
          afterChoice,
          afterBack,
          afterNext,
          beforeSubmit,
          finalMessage,
          submitDisplay: getComputedStyle(button("#submit")).display
        };
      })()`);

      const supremeCount = await waitForDatabaseRecord("supreme-db", "psychometric_submissions", idHash, instrument);
      const sentinelaCount = await waitForDatabaseRecord("sentinela-db", "psico_submissions", idHash, instrument);
      results.push({
        instrument,
        id_hash: idHash,
        clicked_total: clickResult.total,
        navigation: {
          after_choice: clickResult.afterChoice.current,
          after_back: clickResult.afterBack.current,
          after_next: clickResult.afterNext.current,
        },
        final_count: clickResult.beforeSubmit.count,
        final_message_present: Boolean(clickResult.finalMessage),
        supreme_records: supremeCount,
        sentinela_records: sentinelaCount,
      });
    }

    console.log(JSON.stringify({ status: "ok", base_url: baseUrl, validated: results }, null, 2));
  } finally {
    if (cdp) cdp.close();
    chrome.kill();
    await sleep(800);
    try {
      rmSync(userDataDir, { recursive: true, force: true });
    } catch {
      // Chrome can keep profile files locked briefly on Windows; this is not test evidence.
    }
  }
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
