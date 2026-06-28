(function () {
  document.documentElement.classList.add("form-i18n-loading");

  const LOCALES = [
    { code: "pt-BR", label: "PT" },
    { code: "en-US", label: "EN" },
    { code: "es-ES", label: "ES" },
  ];

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

  function normalize(locale) {
    return LOCALES.some((item) => item.code === locale) ? locale : "pt-BR";
  }

  const BASE_FORM_CONFIG =
    typeof FORM_CONFIG !== "undefined" ? JSON.parse(JSON.stringify(FORM_CONFIG)) : {};

  function setTextIfChanged(node, text) {
    if (!node || typeof text === "undefined" || text === null) return false;
    const next = String(text);
    if (node.textContent === next) return false;
    node.textContent = next;
    return true;
  }

  let currentLocale = normalize(
    typeof FORM_LOCALE !== "undefined"
      ? FORM_LOCALE
      : decodeURIComponent(getCookie("supreme_locale") || "pt-BR")
  );

  function ensureSwitcher() {
    if (document.querySelector(".form-lang-switch")) return;
    const meta = document.querySelector(".meta");
    if (!meta) return;
    const wrap = document.createElement("div");
    wrap.className = "form-lang-switch";
    wrap.setAttribute("aria-label", "Selecionar idioma");
    LOCALES.forEach((item) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = item.label;
      btn.dataset.locale = item.code;
      btn.addEventListener("click", () => setLocale(item.code));
      wrap.appendChild(btn);
    });
    meta.prepend(wrap);
    refreshSwitcher();
  }

  function refreshSwitcher() {
    document.querySelectorAll(".form-lang-switch button").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.locale === currentLocale);
      btn.setAttribute("aria-pressed", btn.dataset.locale === currentLocale ? "true" : "false");
    });
  }

  function applyCopy() {
    if (typeof FORM_CONFIG === "undefined") return;
    document.documentElement.lang = currentLocale;
    document.title = "SUPREME V4 - " + (FORM_CONFIG.shortTitle || FORM_CONFIG.title || FORM_CONFIG.instrument);
    const title = document.querySelector(".top h1");
    setTextIfChanged(title, FORM_CONFIG.shortTitle || FORM_CONFIG.title || FORM_CONFIG.instrument);
    const subtitle = document.querySelector(".subtitle");
    if (subtitle && FORM_CONFIG.subtitle) setTextIfChanged(subtitle, FORM_CONFIG.subtitle);
    const hint = document.querySelector(".q-hint");
    if (hint && FORM_CONFIG.scaleHint) setTextIfChanged(hint, FORM_CONFIG.scaleHint);
    const noticeStrong = document.querySelector(".notice p:first-child strong");
    if (noticeStrong && FORM_CONFIG.subtitle) setTextIfChanged(noticeStrong, FORM_CONFIG.subtitle + ".");
    const noticeInstruction = document.querySelector(".notice p:first-child");
    if (noticeInstruction && FORM_CONFIG.instruction) {
      const strong = noticeInstruction.querySelector("strong");
      noticeInstruction.textContent = "";
      if (strong) noticeInstruction.appendChild(strong);
      noticeInstruction.append(" " + FORM_CONFIG.instruction);
    }
    const scaleText = document.querySelector(".notice p:nth-child(2)");
    if (scaleText && FORM_CONFIG.scaleHint) setTextIfChanged(scaleText, FORM_CONFIG.scaleHint + ".");
    const notice = document.querySelector(".notice p:last-child");
    if (notice && FORM_CONFIG.notice) setTextIfChanged(notice, FORM_CONFIG.notice);
    const fine = document.querySelector(".fineprint");
    if (fine && FORM_CONFIG.fineprint) setTextIfChanged(fine, FORM_CONFIG.fineprint);
    const status = document.getElementById("session-status");
    if (status && status.textContent.trim() && FORM_CONFIG.session_secure) setTextIfChanged(status, FORM_CONFIG.session_secure);
    if (typeof render === "function") render();
    relabelDynamicCopy();
    document.documentElement.classList.remove("form-i18n-loading");
  }

  function relabelDynamicCopy() {
    if (typeof FORM_CONFIG === "undefined") return;
    const back = document.getElementById("back");
    const next = document.getElementById("next");
    const submit = document.getElementById("submit");
    if (back && FORM_CONFIG.back) setTextIfChanged(back, FORM_CONFIG.back);
    if (next && FORM_CONFIG.next) setTextIfChanged(next, FORM_CONFIG.next);
    if (submit && FORM_CONFIG.submit && !submit.dataset.submitting) setTextIfChanged(submit, FORM_CONFIG.submit);

    const index = document.getElementById("q-index");
    const match = index ? index.textContent.match(/(\d+).+?(\d+)/) : null;
    if (index && match) {
      const item = FORM_CONFIG.item_label || "Item";
      const of = FORM_CONFIG.of_label || "de";
      setTextIfChanged(index, item + " " + match[1] + " " + of + " " + match[2]);
    }

    const review = document.getElementById("review");
    const reviewMatch = review ? review.textContent.match(/(\d+)/) : null;
    if (review && reviewMatch && FORM_CONFIG.missing_prefix && FORM_CONFIG.missing_suffix) {
      setTextIfChanged(review, FORM_CONFIG.missing_prefix + " " + reviewMatch[1] + " " + FORM_CONFIG.missing_suffix);
    }
  }

  function patchRuntimeCopy() {
    if (typeof render === "function" && !render.__supremeWorldWrapped) {
      const originalRender = render;
      window.render = function () {
        const result = originalRender.apply(this, arguments);
        relabelDynamicCopy();
        return result;
      };
      window.render.__supremeWorldWrapped = true;
    }

    if (typeof showMessage === "function" && !showMessage.__supremeWorldWrapped) {
      const originalShowMessage = showMessage;
      window.showMessage = function (type, text) {
        let translated = text;
        if (typeof text === "string") {
          if (text.includes("Complete este item") && FORM_CONFIG.complete_before_submit) translated = FORM_CONFIG.complete_before_submit;
          if (text.includes("Respostas transmitidas") && FORM_CONFIG.submitted) translated = FORM_CONFIG.submitted;
          if (text.startsWith("Erro:")) translated = text.replace("Erro:", FORM_CONFIG.error_prefix || "Error:");
          if (text.startsWith("Error:")) translated = text.replace("Error:", FORM_CONFIG.error_prefix || "Error:");
        }
        return originalShowMessage.call(this, type, translated);
      };
      window.showMessage.__supremeWorldWrapped = true;
    }
  }

  function resetConfig(payload) {
    Object.keys(FORM_CONFIG).forEach((key) => delete FORM_CONFIG[key]);
    Object.assign(FORM_CONFIG, BASE_FORM_CONFIG, payload || {});
  }

  function translateKnownDynamicText() {
    if (typeof FORM_CONFIG === "undefined") return;
    const submit = document.getElementById("submit");
    if (submit) {
      const text = submit.textContent.trim();
      const isSubmitting = ["Transmitindo...", "Submitting...", "Enviando..."].includes(text);
      if (isSubmitting && FORM_CONFIG.submitting) setTextIfChanged(submit, FORM_CONFIG.submitting);
      if (!isSubmitting && FORM_CONFIG.submit && !submit.disabled) setTextIfChanged(submit, FORM_CONFIG.submit);
    }

    const status = document.getElementById("session-status");
    if (status) {
      const text = status.textContent.trim();
      if (["Sessão segura", "Sessao segura", "Secure session", "Sesión segura", "Sesion segura"].includes(text) && FORM_CONFIG.session_secure) {
        setTextIfChanged(status, FORM_CONFIG.session_secure);
      }
      if (
        ["Sessão indisponível", "Sessao indisponivel", "Session unavailable", "Sesión no disponible", "Sesion no disponible"].includes(text) &&
        FORM_CONFIG.session_unavailable
      ) {
        setTextIfChanged(status, FORM_CONFIG.session_unavailable);
      }
    }
  }

  let refreshTimer = 0;

  function scheduleCopyRefresh() {
    window.clearTimeout(refreshTimer);
    refreshTimer = window.setTimeout(() => {
      translateKnownDynamicText();
      relabelDynamicCopy();
    }, 0);
  }

  function observeDynamicText() {
    document.addEventListener("click", scheduleCopyRefresh, true);
    document.addEventListener("keydown", scheduleCopyRefresh, true);
    document.addEventListener("submit", scheduleCopyRefresh, true);
  }

  async function setLocale(locale) {
    currentLocale = normalize(locale);
    setLocaleCookie(currentLocale);
    refreshSwitcher();
    try {
      const url = "/v1/forms/i18n/" + encodeURIComponent(currentLocale) + "?instrument=" + encodeURIComponent(FORM_CONFIG.instrument);
      const response = await fetch(url, { credentials: "same-origin" });
      if (!response.ok) throw new Error("locale unavailable");
      const payload = await response.json();
      resetConfig(payload);
      applyCopy();
      const cleanUrl = new URL(window.location.href);
      cleanUrl.searchParams.set("locale", currentLocale);
      window.history.replaceState({}, "", cleanUrl.toString());
    } catch (_) {
      resetConfig(typeof FORM_I18N !== "undefined" ? FORM_I18N : {});
      applyCopy();
    }
  }

  function enhanceSubmitFeedback() {
    const submit = document.getElementById("submit");
    if (!submit) return;
    submit.addEventListener("click", () => {
      if (!submit.disabled) submit.dataset.lastLabel = submit.textContent;
    });
  }

  ensureSwitcher();
  patchRuntimeCopy();
  observeDynamicText();
  setLocale(currentLocale);
  enhanceSubmitFeedback();
})();
