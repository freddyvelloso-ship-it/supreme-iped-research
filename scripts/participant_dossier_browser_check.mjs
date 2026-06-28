import { spawn } from "node:child_process";
import { existsSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";

const baseUrl = process.argv[2] || "http://127.0.0.1:18001/?v=participants2";
const baseOrigin = new URL(baseUrl).origin;

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function chromePath() {
  const candidates = [
    process.env.CHROME_PATH,
    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
    "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
    "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
  ].filter(Boolean);
  const found = candidates.find((candidate) => existsSync(candidate));
  if (!found) throw new Error("Chrome/Edge nao encontrado.");
  return found;
}

function localPassword() {
  const seed = readFileSync("seeds/local/clean/sentinela.sql", "utf8");
  const match = seed.match(/Password for local\.master@supreme\.local is:\s*([^\r\n]+)/);
  if (!match) throw new Error("Senha local documentada nao encontrada no seed.");
  return match[1].trim();
}

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`HTTP ${response.status} em ${url}`);
  return response.json();
}

async function waitForPage(port) {
  const deadline = Date.now() + 30000;
  while (Date.now() < deadline) {
    try {
      const pages = await fetchJson(`http://127.0.0.1:${port}/json/list`);
      const page = pages.find((p) => p.type === "page" && p.webSocketDebuggerUrl);
      if (page) return page.webSocketDebuggerUrl;
    } catch {
      // retry
    }
    await sleep(250);
  }
  throw new Error("Timeout aguardando CDP.");
}

class Cdp {
  constructor(url) {
    this.ws = new WebSocket(url);
    this.id = 1;
    this.pending = new Map();
  }

  async open() {
    await new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error("Timeout abrindo websocket CDP.")), 8000);
      this.ws.addEventListener("open", () => {
        clearTimeout(timer);
        resolve();
      }, { once: true });
      this.ws.addEventListener("error", reject, { once: true });
      this.ws.addEventListener("message", (event) => {
        const message = JSON.parse(event.data);
        if (!message.id || !this.pending.has(message.id)) return;
        const callbacks = this.pending.get(message.id);
        this.pending.delete(message.id);
        if (message.error) callbacks.reject(new Error(message.error.message));
        else callbacks.resolve(message.result || {});
      });
    });
  }

  send(method, params = {}) {
    const id = this.id++;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error(`Timeout CDP ${method}`));
      }, 30000);
      this.pending.set(id, {
        resolve: (value) => {
          clearTimeout(timer);
          resolve(value);
        },
        reject: (error) => {
          clearTimeout(timer);
          reject(error);
        },
      });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  async evaluate(expression) {
    const result = await this.send("Runtime.evaluate", {
      expression,
      awaitPromise: true,
      returnByValue: true,
    });
    if (result.exceptionDetails) {
      throw new Error(result.exceptionDetails.text || "Erro em Runtime.evaluate.");
    }
    return result.result?.value;
  }

  close() {
    this.ws.close();
  }
}

const port = 9411 + Math.floor(Math.random() * 400);
const profile = path.join(tmpdir(), `sentinela-participants-${Date.now()}`);
const chrome = spawn(chromePath(), [
  "--headless=new",
  `--remote-debugging-port=${port}`,
  `--user-data-dir=${profile}`,
  "--disable-gpu",
  "--no-first-run",
  "--no-default-browser-check",
  baseUrl,
], { stdio: "ignore" });

let cdp;
try {
  const wsUrl = await waitForPage(port);
  cdp = new Cdp(wsUrl);
  await cdp.open();
  await cdp.send("Runtime.enable");
  await cdp.send("Page.enable");
  await cdp.send("Page.navigate", { url: baseUrl });
  await sleep(1600);

  const password = localPassword();
  const loginEvidence = await cdp.evaluate(`(async () => {
    const loginResponse = await fetch('${baseOrigin}/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ email: 'local.master@supreme.local', password: ${JSON.stringify(password)} })
    });
    return { loginOk: loginResponse.ok, status: loginResponse.status };
  })()`);
  if (!loginEvidence.loginOk) throw new Error(`Login falhou no browser check: ${JSON.stringify(loginEvidence)}`);

  await cdp.send("Page.navigate", { url: `${baseOrigin}/?v=participants2` });
  await sleep(1600);

  const evidence = await cdp.evaluate(`(async () => {
    async function waitFor(fn, timeout = 12000) {
      const deadline = Date.now() + timeout;
      while (Date.now() < deadline) {
        const value = fn();
        if (value) return value;
        await new Promise((resolve) => setTimeout(resolve, 200));
      }
      return null;
    }

    await waitFor(() => typeof window.navigateTo === 'function');
    window.navigateTo('participants');

    await waitFor(() => {
      const rows = document.querySelectorAll('#participants-tbody tr');
      const loading = document.querySelector('#participants-tbody .loading-msg');
      return rows.length && !loading;
    }, 14000);

    const workqueue = document.querySelector('#participants-workqueue');
    const card = document.querySelector('#participants-workqueue .foc-person-card');
    const rawTable = document.querySelector('.foc-participant-raw-table');
    const table = document.querySelector('.foc-participants-table');
    const cardRect = card?.getBoundingClientRect();
    const childOverflow = card ? [...card.querySelectorAll('*')].some((el) => {
      const r = el.getBoundingClientRect();
      return r.width > 0 && (r.left < cardRect.left - 2 || r.right > cardRect.right + 2);
    }) : false;

    if (card) card.click();
    await waitFor(() => document.querySelector('#side-panel.open') && getComputedStyle(document.querySelector('#side-panel')).opacity === '1', 12000);

    const panel = document.querySelector('#side-panel');
    const overlay = document.querySelector('#side-panel-overlay');
    const panelRect = panel?.getBoundingClientRect();
    const viewport = { width: innerWidth, height: innerHeight };
    const panelStyle = panel ? getComputedStyle(panel) : null;
    const overlayStyle = overlay ? getComputedStyle(overlay) : null;

    return {
      workqueueDisplay: workqueue ? getComputedStyle(workqueue).display : null,
      cardCount: document.querySelectorAll('#participants-workqueue .foc-person-card').length,
      cardOverflow: childOverflow,
      rawTableInitiallyOpen: rawTable?.open ?? null,
      tableStillAvailable: !!table,
      bodyModalClass: document.body.classList.contains('participant-dossier-open'),
      panelOpen: panel?.classList.contains('open') || false,
      panelDisplay: panelStyle?.display || null,
      overlayDisplay: overlayStyle?.display || null,
      panelRect: panelRect ? {
        left: Math.round(panelRect.left),
        top: Math.round(panelRect.top),
        width: Math.round(panelRect.width),
        height: Math.round(panelRect.height),
        right: Math.round(panelRect.right),
        bottom: Math.round(panelRect.bottom),
      } : null,
      centered: !!panelRect && Math.abs((panelRect.left + panelRect.width / 2) - viewport.width / 2) < 40,
      visible: !!panelRect && panelRect.top >= 0 && panelRect.left >= 0 && panelRect.bottom <= viewport.height + 1 && panelRect.right <= viewport.width + 1,
      largeEnough: !!panelRect && panelRect.width >= Math.min(900, viewport.width * 0.7) && panelRect.height >= viewport.height * 0.65,
      viewport,
    };
  })()`);

  if (evidence.workqueueDisplay !== "grid") throw new Error(`Fila de participantes nao esta em grid: ${JSON.stringify(evidence)}`);
  if (!evidence.cardCount) throw new Error(`Cards de participante ausentes: ${JSON.stringify(evidence)}`);
  if (evidence.cardOverflow) throw new Error(`Conteudo do card esta vazando/sobreposto: ${JSON.stringify(evidence)}`);
  if (evidence.rawTableInitiallyOpen) throw new Error(`Matriz tecnica deve iniciar recolhida: ${JSON.stringify(evidence)}`);
  if (!evidence.tableStillAvailable) throw new Error(`Tabela tecnica desapareceu: ${JSON.stringify(evidence)}`);
  if (!evidence.bodyModalClass || !evidence.panelOpen || evidence.panelDisplay !== "flex" || evidence.overlayDisplay === "none") {
    throw new Error(`Dossie nao abriu como modal: ${JSON.stringify(evidence)}`);
  }
  if (!evidence.centered || !evidence.visible || !evidence.largeEnough) {
    throw new Error(`Dossie fora da jornada visual esperada: ${JSON.stringify(evidence)}`);
  }

  console.log(JSON.stringify({ status: "ok", loginEvidence, evidence }, null, 2));
} finally {
  if (cdp) cdp.close();
  chrome.kill();
  await sleep(600);
  try {
    rmSync(profile, { recursive: true, force: true });
  } catch {
    // Chrome can keep files locked briefly on Windows; visual evidence is already collected.
  }
}
