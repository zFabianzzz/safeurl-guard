const API_BASE = "https://safeurl-guard.onrender.com";

function getRiskLevel(riesgo) {
  if (riesgo >= 70) return "danger";
  if (riesgo >= 40) return "warning";
  return "safe";
}

function getRiskIcon(clasificacion, riesgo) {
  var icons = { "Malware":"☠️","Phishing":"🎣","Defacement":"💀","Sospechosa":"⚠️","Segura":"✅","Bloqueado por admin":"🚫" };
  return icons[clasificacion] || (getRiskLevel(riesgo)==="danger"?"🚨":getRiskLevel(riesgo)==="warning"?"⚠️":"✅");
}

function truncateUrl(url, max) {
  max = max || 45;
  if (!url || url.length <= max) return url || "–";
  try { var h = new URL(url).hostname; return h.length > max ? h.substring(0,max)+"..." : h; } catch(e) { return url.substring(0,max)+"..."; }
}

function getModelLabel(m) {
  return {"random_forest":"🤖 Random Forest (ML)","heuristico":"📐 Heurístico","whitelist":"✅ Lista blanca","blacklist":"🚫 Blacklist admin"}[m] || m || "–";
}

function renderStatus(result) {
  var card = document.getElementById("status-card");
  var icon = document.getElementById("status-icon");
  var title = document.getElementById("status-title");
  var sub = document.getElementById("status-subtitle");
  var pct = document.getElementById("risk-pct");
  var bar = document.getElementById("risk-bar");
  var infoUrl = document.getElementById("info-url");
  var infoClasif = document.getElementById("info-clasificacion");
  var infoAccion = document.getElementById("info-accion");
  var infoModelo = document.getElementById("info-modelo");
  if (!result) {
    card.className = "status-card loading";
    icon.textContent = "🔍"; title.textContent = "Sin datos";
    sub.textContent = "Navega a una página para analizarla";
    pct.textContent = "–"; bar.style.width = "0%";
    infoUrl.textContent = "–"; infoUrl.className = "info-value muted";
    infoClasif.textContent = "–"; infoClasif.className = "info-value";
    infoAccion.textContent = "–"; infoAccion.className = "info-value";
    infoModelo.textContent = "–";
    return;
  }
  var level = result.admin_block ? "danger" : getRiskLevel(result.riesgo);
  card.className = "status-card " + level;
  icon.textContent = getRiskIcon(result.clasificacion, result.riesgo);
  title.textContent = result.admin_block ? "🚫 Bloqueado por administrador" :
    level === "danger" ? "⚠ Amenaza detectada" :
    level === "warning" ? "Sitio sospechoso" : "Protección activa";
  sub.textContent = result.admin_block ? "El administrador ha bloqueado esta URL" :
    level === "danger" ? "Esta URL es potencialmente peligrosa" :
    level === "warning" ? "Procede con precaución" : "La navegación está segura";
  pct.textContent = result.riesgo + "%";
  bar.style.width = result.riesgo + "%";
  infoUrl.textContent = truncateUrl(result.url);
  infoUrl.className = "info-value"; infoUrl.title = result.url;
  infoClasif.textContent = result.clasificacion || "–";
  infoClasif.className = "info-value " + (level==="danger"?"danger-text":level==="warning"?"warning-text":"safe-text");
  infoAccion.textContent = result.accion || "–";
  infoAccion.className = "info-value " + (result.accion==="Bloqueado"?"danger-text":result.accion==="Advertencia"?"warning-text":"safe-text");
  infoModelo.textContent = getModelLabel(result.modelo);
}

async function checkBackendStatus() {
  var el = document.getElementById("backend-status");
  var label = document.getElementById("backend-label");
  try {
    var r = await fetch(API_BASE + "/health", { signal: AbortSignal.timeout(3000) });
    var d = await r.json();
    el.className = "backend-status online";
    label.textContent = "Backend online · " + (d.modelo === "random_forest" ? "ML activo" : "Modo heurístico");
  } catch(e) {
    el.className = "backend-status offline";
    label.textContent = "Backend offline";
  }
}

async function loadDeviceId() {
  var data = await chrome.storage.local.get(["device_id"]);
  var id = data.device_id || "–";
  var el = document.getElementById("device-id-display");
  if (el) el.textContent = id.length > 20 ? id.substring(0, 20) + "..." : id;
  el.title = id;
}

async function reanalyzeCurrentTab() {
  var btn = document.getElementById("btn-reanalizar");
  btn.disabled = true;
  btn.innerHTML = '<span class="loading-spinner"></span> Analizando...';
  try {
    var tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    var url = tabs[0] && tabs[0].url;
    if (!url) throw new Error("No URL");
    var result = await chrome.runtime.sendMessage({ type: "ANALYZE_URL", url: url });
    if (result) renderStatus(result);
  } catch(e) { console.error(e); }
  finally {
    btn.disabled = false;
    btn.innerHTML = "🔄 Re-analizar página actual";
  }
}

async function analyzeManualUrl() {
  var input = document.getElementById("manual-url-input");
  var resultEl = document.getElementById("manual-result");
  var btn = document.getElementById("btn-manual-analyze");
  var url = input.value.trim();
  if (!url) return;
  if (!url.startsWith("http://") && !url.startsWith("https://")) { url = "https://" + url; input.value = url; }
  btn.disabled = true; btn.textContent = "Analizando...";
  resultEl.classList.remove("hidden");
  resultEl.textContent = "Consultando al modelo...";
  resultEl.style.color = "var(--text-muted)"; resultEl.style.borderColor = "var(--border)";
  try {
    var data = await chrome.storage.local.get(["device_id"]);
    var r = await fetch(API_BASE + "/analizar-url", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: url, device_id: data.device_id || "manual", guardar: false }),
      signal: AbortSignal.timeout(8000),
    });
    var res = await r.json();
    var level = getRiskLevel(res.riesgo);
    var colors = { safe:"var(--green)", warning:"var(--yellow)", danger:"var(--red)" };
    resultEl.style.borderColor = colors[level];
    resultEl.innerHTML = '<strong style="color:' + colors[level] + '">' + getRiskIcon(res.clasificacion, res.riesgo) + ' ' + res.clasificacion + '</strong>' +
      ' — Riesgo: <strong style="color:' + colors[level] + '">' + res.riesgo + '%</strong>' +
      ' · Acción: <strong>' + res.accion + '</strong>';
  } catch(e) {
    resultEl.textContent = "❌ Error al conectar con el backend";
    resultEl.style.color = "var(--red)";
  } finally { btn.disabled = false; btn.textContent = "🔍 Analizar"; }
}

async function initProtectionToggle() {
  var btn = document.getElementById("btn-toggle-protection");
  var data = await chrome.storage.local.get(["proteccion_activa"]);
  var active = data.proteccion_activa !== false;
  btn.textContent = active ? "🔒 Protección activa" : "🔓 Inactiva";
  btn.style.color = active ? "var(--green)" : "var(--red)";
  btn.addEventListener("click", async function() {
    var cur = await chrome.storage.local.get(["proteccion_activa"]);
    var newState = !(cur.proteccion_activa !== false);
    await chrome.storage.local.set({ proteccion_activa: newState });
    btn.textContent = newState ? "🔒 Protección activa" : "🔓 Inactiva";
    btn.style.color = newState ? "var(--green)" : "var(--red)";
  });
}

document.querySelectorAll(".tab").forEach(function(tab) {
  tab.addEventListener("click", function() {
    var target = tab.dataset.tab;
    document.querySelectorAll(".tab").forEach(function(t) { t.classList.remove("active"); });
    document.querySelectorAll(".tab-content").forEach(function(c) { c.classList.remove("active"); });
    tab.classList.add("active");
    document.getElementById("tab-" + target).classList.add("active");
  });
});

document.addEventListener("DOMContentLoaded", async function() {
  await loadDeviceId();
  await initProtectionToggle();
  var data = await chrome.storage.local.get(["ultimo_resultado"]);
  renderStatus(data.ultimo_resultado || null);
  checkBackendStatus();
  document.getElementById("btn-reanalizar").addEventListener("click", reanalyzeCurrentTab);
  document.getElementById("btn-settings").addEventListener("click", function() {
    chrome.tabs.create({ url: chrome.runtime.getURL("settings.html") });
  });
  document.getElementById("btn-manual-analyze").addEventListener("click", analyzeManualUrl);
  document.getElementById("manual-url-input").addEventListener("keydown", function(e) {
    if (e.key === "Enter") analyzeManualUrl();
  });
});