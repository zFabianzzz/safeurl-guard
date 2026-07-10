// background.js - SafeURL Guard Service Worker

const API_BASE = "https://safeurl-guard.onrender.com";

const SKIP_URLS = [
  "chrome://", "chrome-extension://", "edge://", "about:",
  "moz-extension://", "chrome-search://", "devtools://", "data:", "blob:"
];

const cache = new Map();
const CACHE_TTL = 10 * 60 * 1000;
const userAllowedUrls = new Set();
let blacklistCache = [];
let blacklistLastUpdate = 0;
const BLACKLIST_TTL = 60 * 1000; // actualiza cada 60 segundos

function shouldSkipUrl(url) {
  return SKIP_URLS.some(function(prefix) { return url.startsWith(prefix); });
}

function getCached(url) {
  var entry = cache.get(url);
  if (!entry) return null;
  if (Date.now() - entry.timestamp > CACHE_TTL) { cache.delete(url); return null; }
  return entry.result;
}

function setCached(url, result) {
  cache.set(url, { result: result, timestamp: Date.now() });
  if (cache.size > 200) { var k = cache.keys().next().value; cache.delete(k); }
}

function normalizeUrl(url) {
  try { var u = new URL(url); return u.origin + u.pathname; } catch(e) { return url; }
}

// Generar o recuperar Device ID único
async function getDeviceId() {
  var data = await chrome.storage.local.get(["device_id"]);
  if (data.device_id) return data.device_id;
  var newId = "DEV-" + Date.now().toString(36).toUpperCase() + "-" + Math.random().toString(36).substring(2,8).toUpperCase();
  await chrome.storage.local.set({ device_id: newId });
  return newId;
}

// Actualizar blacklist desde el servidor
async function actualizarBlacklist(deviceId) {
  if (Date.now() - blacklistLastUpdate < BLACKLIST_TTL) return;
  try {
    var r = await fetch(API_BASE + "/blacklist/" + deviceId, { signal: AbortSignal.timeout(5000) });
    if (r.ok) {
      blacklistCache = await r.json();
      blacklistLastUpdate = Date.now();
    }
  } catch(e) {}
}

// Verificar si URL está en blacklist local
function estaEnBlacklist(url) {
  var urlLower = url.toLowerCase();
  for (var i = 0; i < blacklistCache.length; i++) {
    if (urlLower.includes(blacklistCache[i].patron)) {
      return blacklistCache[i].patron;
    }
  }
  return null;
}

async function analyzeUrl(url, deviceId) {
  var cached = getCached(url);
  if (cached) return cached;
  try {
    var response = await fetch(API_BASE + "/analizar-url", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: url, device_id: deviceId, guardar: true }),
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
  if (userAllowedUrls.has(normalizedUrl)) return;

  var deviceId = await getDeviceId();

  var config = await chrome.storage.local.get(["proteccion_activa", "bloqueo_auto", "mostrar_advertencias"]);
  if (config.proteccion_activa === false) return;

  var bloqueoAuto = config.bloqueo_auto !== false;
  var mostrarAdvertencias = config.mostrar_advertencias !== false;

  // Actualizar blacklist
  await actualizarBlacklist(deviceId);

  // Verificar blacklist local PRIMERO (bloqueo inmediato sin botón continuar)
  var patronBloqueado = estaEnBlacklist(url);
  if (patronBloqueado) {
    if (!url.includes("blocked.html")) {
      var params = new URLSearchParams({
        url: url, riesgo: "100", tipo: "Bloqueado por admin",
        patron: patronBloqueado, admin_block: "true"
      });
      var blockedUrl = chrome.runtime.getURL("blocked.html?" + params.toString());
      chrome.tabs.update(details.tabId, { url: blockedUrl });
    }
    return;
  }

  // Análisis ML
  var result = await analyzeUrl(url, deviceId);
  if (!result) return;

  await chrome.storage.local.set({ ultimo_resultado: result });

  // Bloqueo por admin desde el servidor
  if (result.admin_block || result.accion === "Bloqueado" && result.modelo === "blacklist") {
    if (!url.includes("blocked.html")) {
      var params2 = new URLSearchParams({
        url: url, riesgo: "100", tipo: "Bloqueado por admin",
        patron: result.blacklist_patron || "", admin_block: "true"
      });
      chrome.tabs.update(details.tabId, { url: chrome.runtime.getURL("blocked.html?" + params2.toString()) });
    }
    return;
  }

  if (bloqueoAuto && result.accion === "Bloqueado") {
    if (!url.includes("blocked.html")) {
      var params3 = new URLSearchParams({ url: url, riesgo: result.riesgo.toString(), tipo: result.clasificacion });
      chrome.tabs.update(details.tabId, { url: chrome.runtime.getURL("blocked.html?" + params3.toString()) });
    }
    return;
  }

  if (mostrarAdvertencias && result.accion === "Advertencia") {
    chrome.notifications.create({
      type: "basic", iconUrl: "icons/icon48.png",
      title: "SafeURL Guard - Sitio Sospechoso",
      message: result.dominio + " - Riesgo: " + result.riesgo + "% (" + result.clasificacion + ")",
      priority: 1,
    });
  }
}, { url: [{ schemes: ["http", "https"] }] });

chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
  if (message.type === "ANALYZE_URL") {
    getDeviceId().then(function(deviceId) {
      analyzeUrl(message.url, deviceId).then(function(result) {
        if (result) chrome.storage.local.set({ ultimo_resultado: result });
        sendResponse(result);
      });
    });
    return true;
  }
  if (message.type === "GET_DEVICE_ID") {
    getDeviceId().then(function(id) { sendResponse({ device_id: id }); });
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
  if (message.type === "FORCE_BLACKLIST_UPDATE") {
    blacklistLastUpdate = 0;
    getDeviceId().then(function(deviceId) {
      actualizarBlacklist(deviceId).then(function() { sendResponse({ ok: true }); });
    });
    return true;
  }
});