// background.js - SafeURL Guard Service Worker

const API_BASE = "https://safeurl-guard.onrender.com";
const SKIP_URLS = [
  "chrome://", "chrome-extension://", "edge://", "about:",
  "moz-extension://", "chrome-search://", "devtools://", "data:", "blob:"
];

const cache = new Map();
const CACHE_TTL = 10 * 60 * 1000;
const userAllowedUrls = new Set();

function shouldSkipUrl(url) {
  return SKIP_URLS.some(function(prefix) { return url.startsWith(prefix); });
}

function getCached(url) {
  var entry = cache.get(url);
  if (!entry) return null;
  if (Date.now() - entry.timestamp > CACHE_TTL) {
    cache.delete(url);
    return null;
  }
  return entry.result;
}

function setCached(url, result) {
  cache.set(url, { result: result, timestamp: Date.now() });
  if (cache.size > 200) {
    var firstKey = cache.keys().next().value;
    cache.delete(firstKey);
  }
}

function normalizeUrl(url) {
  try {
    var u = new URL(url);
    return u.origin + u.pathname;
  } catch(e) {
    return url;
  }
}

async function analyzeUrl(url, guardar) {
  var cached = getCached(url);
  if (cached) return cached;

  try {
    var response = await fetch(API_BASE + "/analizar-url", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: url, guardar: guardar }),
      signal: AbortSignal.timeout(8000),
    });
    if (!response.ok) throw new Error("HTTP " + response.status);
    var data = await response.json();
    setCached(url, data);
    return data;
  } catch(err) {
    console.error("[SafeURL Guard] Error:", err.message);
    return null;
  }
}

chrome.webNavigation.onCompleted.addListener(async function(details) {
  if (details.frameId !== 0) return;

  var url = details.url;
  if (shouldSkipUrl(url)) return;

  var normalizedUrl = normalizeUrl(url);
  if (userAllowedUrls.has(normalizedUrl)) {
    console.log("[SafeURL Guard] URL permitida por usuario:", normalizedUrl);
    return;
  }

  // Leer toda la configuración de una vez
  var config = await chrome.storage.local.get([
    "proteccion_activa", "bloqueo_auto",
    "nivel_sensibilidad", "guardar_historial", "mostrar_advertencias"
  ]);

  var proteccionActiva = config.proteccion_activa !== false;
  var bloqueoAuto = config.bloqueo_auto !== false;
  var nivelSensibilidad = config.nivel_sensibilidad || "alto";
  var guardarHistorial = config.guardar_historial !== false; // respeta la config
  var mostrarAdvertencias = config.mostrar_advertencias !== false;

  if (!proteccionActiva) return;

  var result = await analyzeUrl(url, guardarHistorial);
  if (!result) return;

  await chrome.storage.local.set({ ultimo_resultado: result });

  if (bloqueoAuto && result.accion === "Bloqueado") {
    if (!url.includes("blocked.html")) {
      var params = new URLSearchParams({
        url: url,
        riesgo: result.riesgo.toString(),
        tipo: result.clasificacion,
      });
      var blockedUrl = chrome.runtime.getURL("blocked.html?" + params.toString());
      chrome.tabs.update(details.tabId, { url: blockedUrl });
    }
    return;
  }

  if (mostrarAdvertencias && nivelSensibilidad === "alto" && result.accion === "Advertencia") {
    chrome.notifications.create({
      type: "basic",
      iconUrl: "icons/icon48.png",
      title: "⚠️ SafeURL Guard - Sitio Sospechoso",
      message: result.dominio + " - Riesgo: " + result.riesgo + "% (" + result.clasificacion + ")",
      priority: 1,
    });
  }
}, { url: [{ schemes: ["http", "https"] }] });

chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
  if (message.type === "ANALYZE_URL") {
    chrome.storage.local.get(["guardar_historial"], function(cfg) {
      var guardar = cfg.guardar_historial !== false;
      analyzeUrl(message.url, guardar).then(function(result) {
        if (result) chrome.storage.local.set({ ultimo_resultado: result });
        sendResponse(result);
      });
    });
    return true;
  }

  if (message.type === "GET_STATUS") {
    fetch(API_BASE + "/health")
      .then(function(r) { return r.json(); })
      .then(function(data) { sendResponse({ online: true, modelo: data.modelo }); })
      .catch(function() { sendResponse({ online: false }); });
    return true;
  }

  if (message.type === "ALLOW_URL") {
    var normalized = normalizeUrl(message.url);
    userAllowedUrls.add(normalized);
    setTimeout(function() { userAllowedUrls.delete(normalized); }, 30 * 60 * 1000);
    sendResponse({ ok: true });
    return true;
  }
});