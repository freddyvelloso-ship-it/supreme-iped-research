import { spawn } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, rmSync } from "node:fs";
import path from "node:path";

function argValue(name, fallback) {
  const index = process.argv.indexOf(name);
  return index >= 0 && process.argv[index + 1] ? process.argv[index + 1] : fallback;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`HTTP ${response.status} for ${url}`);
  return response.json();
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
  if (!found) throw new Error("Chrome/Edge nao encontrado.");
  return found;
}

function readLocalPassword() {
  const seed = readFileSync("seeds/local/clean/sentinela.sql", "utf8");
  const match = seed.match(/Password for local\.master@supreme\.local is:\s*([^\r\n]+)/);
  if (!match) throw new Error("Senha local documentada nao encontrada no seed.");
  return match[1].trim();
}

async function waitForChrome(port) {
  const deadline = Date.now() + 30000;
  while (Date.now() < deadline) {
    try {
      const tabs = await fetchJson(`http://127.0.0.1:${port}/json/list`);
      const page = tabs.find((tab) => tab.type === "page" && tab.webSocketDebuggerUrl);
      if (page) return page.webSocketDebuggerUrl;
    } catch {
      // retry
    }
    await sleep(250);
  }
  throw new Error("Timeout aguardando Chrome DevTools.");
}

class Cdp {
  constructor(wsUrl) {
    this.ws = new WebSocket(wsUrl);
    this.id = 1;
    this.pending = new Map();
  }
  async open() {
    await new Promise((resolve, reject) => {
      const timeout = setTimeout(() => reject(new Error("Timeout abrindo CDP")), 8000);
      this.ws.addEventListener("open", () => {
        clearTimeout(timeout);
        resolve();
      }, { once: true });
      this.ws.addEventListener("error", reject, { once: true });
      this.ws.addEventListener("message", (event) => {
        const message = JSON.parse(event.data);
        if (!message.id || !this.pending.has(message.id)) return;
        const { resolve, reject } = this.pending.get(message.id);
        this.pending.delete(message.id);
        if (message.error) reject(new Error(message.error.message));
        else resolve(message.result || {});
      });
    });
  }
  send(method, params = {}) {
    const id = this.id++;
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error(`Timeout CDP ${method}`));
      }, 30000);
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
      this.ws.send(JSON.stringify({ id, method, params }));
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
      const details = result.exceptionDetails;
      const description = details.exception?.description || details.exception?.value || details.text || "Runtime exception";
      throw new Error(description);
    }
    return result.result?.value;
  }
  async navigate(url) {
    await this.send("Page.navigate", { url });
    const deadline = Date.now() + 30000;
    while (Date.now() < deadline) {
      const ready = await this.evaluate("document.readyState", false);
      if (ready === "complete" || ready === "interactive") return;
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

function assertIncludes(text, needles, label) {
  const normalized = text.toLocaleLowerCase();
  for (const needle of needles) {
    if (!normalized.includes(needle.toLocaleLowerCase())) {
      throw new Error(`${label}: texto esperado ausente: ${needle}; amostra=${text.slice(0, 360).replace(/\s+/g, " ")}`);
    }
  }
}

function assertExcludes(text, needles, label) {
  const normalized = text.toLocaleLowerCase();
  for (const needle of needles) {
    if (normalized.includes(needle.toLocaleLowerCase())) throw new Error(`${label}: mistura indevida encontrada: ${needle}`);
  }
}

async function main() {
  const baseUrl = argValue("--base-url", process.env.SENTINELA_URL || "http://127.0.0.1:18001").replace(/\/$/, "");
  const port = Number(argValue("--cdp-port", String(9700 + Math.floor(Math.random() * 200))));
  const userDataDir = path.join(process.cwd(), "tmp", `sentinela-i18n-${Date.now()}`);
  mkdirSync(userDataDir, { recursive: true });
  const chrome = spawn(findChrome(), [
    "--headless=new",
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${userDataDir}`,
    "--disable-gpu",
    "--no-first-run",
    "--no-default-browser-check",
    "about:blank",
  ], { stdio: "ignore", windowsHide: true });

  let cdp;
  try {
    cdp = new Cdp(await waitForChrome(port));
    await cdp.open();
    await cdp.send("Page.enable");
    await cdp.send("Runtime.enable");
    await cdp.navigate(baseUrl);
    await sleep(1200);

    const loginEvidence = {};
    for (const [locale, expected, forbidden] of [
      ["pt-BR", ["Acesso restrito", "Entrar no console"], ["Restricted access", "Acceso restringido"]],
      ["en-US", ["Restricted access", "Enter console"], ["Acesso restrito", "Acceso restringido"]],
      ["es-ES", ["Acceso restringido", "Entrar en la consola"], ["Restricted access", "Acesso restrito"]],
    ]) {
      const text = await cdp.evaluate(`(async () => {
        document.querySelector('.global-lang-switch button[data-locale="${locale}"]')?.click();
        await new Promise((resolve) => setTimeout(resolve, 450));
        return document.querySelector('#login-screen')?.innerText || '';
      })()`);
      assertIncludes(text, expected, `login ${locale}`);
      assertExcludes(text, forbidden, `login ${locale}`);
      loginEvidence[locale] = expected;
    }

    const password = readLocalPassword();
    const loggedIn = await cdp.evaluate(`(async () => {
      document.querySelector('.global-lang-switch button[data-locale="en-US"]')?.click();
      await new Promise((resolve) => setTimeout(resolve, 250));
      document.querySelector('#login-email').value = 'local.master@supreme.local';
      document.querySelector('#login-email').dispatchEvent(new Event('input', { bubbles: true }));
      document.querySelector('#login-password').value = ${JSON.stringify(password)};
      document.querySelector('#login-password').dispatchEvent(new Event('input', { bubbles: true }));
      document.querySelector('#btn-login').click();
      const deadline = Date.now() + 8000;
      while (Date.now() < deadline) {
        const app = document.querySelector('#app-shell');
        if (app && getComputedStyle(app).display !== 'none') return true;
        await new Promise((resolve) => setTimeout(resolve, 200));
      }
      return false;
    })()`);
    if (!loggedIn) throw new Error("Login local no SENTINELA nao abriu o app-shell.");

    const appEvidence = {};
    for (const [locale, expected, forbidden] of [
      ["en-US", ["Overview", "Participants", "ingestion", "Review participant"], ["Visao Geral", "Aguardando ingestao", "Revisar participante"]],
      ["es-ES", ["Vista General", "Participantes", "ingesta", "Revisar participante"], ["Overview", "Waiting for ingestion", "Visao Geral"]],
      ["pt-BR", ["Vis", "Participantes", "ingest", "Revisar participante"], ["Overview", "Waiting for ingestion", "Acceso restringido"]],
    ]) {
      const text = await cdp.evaluate(`(async () => {
        if (!document.querySelector('#app-lang-switch button[data-locale="${locale}"]')) {
          throw new Error('app language switch unavailable');
        }
        document.querySelector('#app-lang-switch button[data-locale="${locale}"]')?.click();
        await new Promise((resolve) => setTimeout(resolve, 1200));
        return document.querySelector('#app-shell')?.innerText || '';
      })()`);
      assertIncludes(text, expected, `app ${locale}`);
      assertExcludes(text, forbidden, `app ${locale}`);
      appEvidence[locale] = expected;
    }

    const uxProbe = `(() => {
      const visible = (el) => {
        if (!el) return false;
        if (el.closest('details:not([open])')) return false;
        const style = getComputedStyle(el);
        const rect = el.getBoundingClientRect();
        return style.display !== 'none' && style.visibility !== 'hidden' && el.offsetParent !== null && rect.width > 0 && rect.height > 0;
      };
      const kpi = document.querySelector('#kpi-grid');
      const kpiRect = kpi ? kpi.getBoundingClientRect() : null;
      const overviewCards = [...document.querySelectorAll('#section-overview .card')].filter(visible).length;
      return {
        forensicConsole: document.body.classList.contains('forensic-console'),
        commandPanels: !!document.querySelector('#foc-command-panels'),
        deepDivePresent: !!document.querySelector('#overview-deep-dive'),
        deepDiveOpen: document.querySelector('#overview-deep-dive')?.open ?? null,
        hiddenSourceKpis: !!kpiRect && kpiRect.width <= 2 && kpiRect.height <= 2,
        visibleOverviewCards: overviewCards,
        legacyDecisionPanel: !!document.querySelector('.ux-decision-panel'),
        firstAction: document.querySelector('.foc-next-actions button')?.innerText || ''
      };
    })()`;
    const uxEvidence = await cdp.evaluate(uxProbe);
    if (!uxEvidence.forensicConsole) throw new Error("UX: forensic-console class ausente.");
    if (!uxEvidence.commandPanels) throw new Error("UX: Command Center ausente.");
    if (!uxEvidence.deepDivePresent || uxEvidence.deepDiveOpen !== false) throw new Error("UX: detalhes operacionais devem existir e iniciar recolhidos.");
    if (!uxEvidence.hiddenSourceKpis) throw new Error("UX: KPIs antigos continuam visiveis na primeira dobra.");
    if (uxEvidence.visibleOverviewCards > 0) throw new Error("UX: cards graficos antigos continuam visiveis na Visao Geral inicial.");
    if (uxEvidence.legacyDecisionPanel) throw new Error("UX: painel legado ux-decision-panel apareceu na primeira dobra.");

    await sleep(4200);
    const uxEvidenceStable = await cdp.evaluate(uxProbe);
    if (!uxEvidenceStable.commandPanels || uxEvidenceStable.legacyDecisionPanel || uxEvidenceStable.visibleOverviewCards > 0) {
      throw new Error(`UX: regressao apos auto-refresh: ${JSON.stringify(uxEvidenceStable)}`);
    }

    const participantEvidence = await cdp.evaluate(`(async () => {
      if (typeof window.navigateTo === 'function') window.navigateTo('participants');
      const deadline = Date.now() + 9000;
      while (Date.now() < deadline) {
        const tbody = document.querySelector('#participants-tbody');
        const loading = tbody?.querySelector('.loading-msg');
        const rows = tbody?.querySelectorAll('tr') || [];
        if (tbody && rows.length && !loading) break;
        await new Promise((resolve) => setTimeout(resolve, 200));
      }
      const workqueue = document.querySelector('#participants-workqueue');
      const firstCard = document.querySelector('#participants-workqueue .foc-person-card');
      const table = document.querySelector('.foc-participants-table');
      const wrap = document.querySelector('#section-participants .table-wrap');
      const firstButton = document.querySelector('#participants-tbody .foc-table-action');
      const firstRow = document.querySelector('#participants-tbody tr');
      const cells = firstRow ? [...firstRow.children].map((td) => {
        const r = td.getBoundingClientRect();
        return { w: Math.round(r.width), h: Math.round(r.height), scrollW: td.scrollWidth, clientW: td.clientWidth };
      }) : [];
      if (firstCard) firstCard.click();
      else if (firstButton) firstButton.click();
      const panelDeadline = Date.now() + 9000;
      while (Date.now() < panelDeadline) {
        const panel = document.querySelector('#side-panel.open');
        if (panel && getComputedStyle(panel).opacity === '1') break;
        await new Promise((resolve) => setTimeout(resolve, 200));
      }
      const panel = document.querySelector('#side-panel');
      const overlay = document.querySelector('#side-panel-overlay');
      const rect = panel ? panel.getBoundingClientRect() : null;
      const viewport = { w: window.innerWidth, h: window.innerHeight };
      return {
        workqueuePresent: !!workqueue,
        cardPresent: !!firstCard,
        tablePresent: !!table,
        rowPresent: !!firstRow,
        dossierButtonPresent: !!firstButton,
        tableMinWidth: table ? Math.round(table.getBoundingClientRect().width) : 0,
        wrapClientWidth: wrap ? Math.round(wrap.getBoundingClientRect().width) : 0,
        cells,
        panelOpen: panel?.classList.contains('open') || false,
        panelRect: rect ? { left: Math.round(rect.left), top: Math.round(rect.top), width: Math.round(rect.width), height: Math.round(rect.height), bottom: Math.round(rect.bottom) } : null,
        centered: !!rect && Math.abs((rect.left + rect.width / 2) - viewport.w / 2) < 80,
        visibleVertically: !!rect && rect.top >= 0 && rect.bottom <= viewport.h + 1,
        panelZ: panel ? Number(getComputedStyle(panel).zIndex) : 0,
        overlayZ: overlay ? Number(getComputedStyle(overlay).zIndex) : 0
      };
    })()`);
    if (!participantEvidence.workqueuePresent) throw new Error("Participantes: fila operacional visual ausente.");
    if (participantEvidence.rowPresent && !participantEvidence.cardPresent) throw new Error("Participantes: card operacional do participante ausente.");
    if (!participantEvidence.tablePresent) throw new Error("Participantes: tabela operacional ausente.");
    if (participantEvidence.rowPresent && !participantEvidence.dossierButtonPresent) throw new Error("Participantes: botao de dossie ausente.");
    if (participantEvidence.dossierButtonPresent && (!participantEvidence.panelOpen || !participantEvidence.centered || !participantEvidence.visibleVertically)) {
      throw new Error(`Participantes: dossie abriu fora do fluxo visual: ${JSON.stringify(participantEvidence)}`);
    }

    console.log(JSON.stringify({ status: "ok", loginEvidence, appEvidence, uxEvidence, uxEvidenceStable, participantEvidence }, null, 2));
  } finally {
    if (cdp) cdp.close();
    chrome.kill();
    await sleep(800);
    try {
      rmSync(userDataDir, { recursive: true, force: true });
    } catch {
      // Chrome can keep profile files locked for a moment on Windows; this is not test evidence.
    }
  }
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
