const API_BASE = "https://safeurl-guard.onrender.com";
function getRiskLevel(riesgo) {
  if (riesgo >= 70) return "danger";
  if (riesgo >= 40) return "warning";
  return "safe";
}

function getRiskIcon(clasificacion, riesgo) {
  const byClass = {
    "Malware": "☠️", "Phishing": "🎣",
    "Defacement": "💀", "Sospechosa": "⚠️", "Segura": "✅",
  };
  const byLevel = { safe: "✅", warning: "⚠️", danger: "🚨" };
  return byClass[clasificacion] || byLevel[getRiskLevel(riesgo)] || "🔍";
}

function getRiskTitle(clasificacion, riesgo) {
  const level = getRiskLevel(riesgo);
  if (level === "danger") {
    if (clasificacion === "Malware") return "⚠ Malware detectado";
    if (clasificacion === "Phishing") return "⚠ Amenaza detectada";
    if (clasificacion === "Defacement") return "⚠ Sitio comprometido";
    return "⚠ Amenaza detectada";
  }
  if (level === "warning") return "Sitio sospechoso";
  return "Protección activa";
}

function getRiskSubtitle(clasificacion, riesgo) {
  const level = getRiskLevel(riesgo);
  if (level === "danger") return "Esta URL es potencialmente peligrosa";
  if (level === "warning") return "Procede con precaución";
  return "La navegación está segura";
}

function truncateUrl(url, maxLen) {
  maxLen = maxLen || 45;
  if (!url || url.length <= maxLen) return url || "–";
  try {
    var parsed = new URL(url);
    var domain = parsed.hostname;
    if (domain.length > maxLen) return domain.substring(0, maxLen) + "...";
    return domain + (parsed.pathname.length > 1 ? parsed.pathname.substring(0, maxLen - domain.length) + "..." : "");
  } catch(e) {
    return url.substring(0, maxLen) + "...";
  }
}

function getModelLabel(modelo) {
  var labels = {
    "random_forest": "🤖 Random Forest (ML)",
    "heuristico": "📐 Heurístico",
    "whitelist": "✅ Lista blanca",
  };
  return labels[modelo] || modelo || "–";
}

function getClasificacionClass(clasificacion, accion) {
  if (accion === "Bloqueado") return "danger-text";
  if (accion === "Advertencia") return "warning-text";
  return "safe-text";
}

function getAccionClass(accion) {
  if (accion === "Bloqueado") return "danger-text";
  if (accion === "Advertencia") return "warning-text";
  return "safe-text";
}

function renderStatus(result) {
  var card = document.getElementById("status-card");
  var icon = document.getElementById("status-icon");
  var title = document.getElementById("status-title");
  var subtitle = document.getElementById("status-subtitle");
  var riskPct = document.getElementById("risk-pct");
  var riskBar = document.getElementById("risk-bar");
  var infoUrl = document.getElementById("info-url");
  var infoClasificacion = document.getElementById("info-clasificacion");
  var infoAccion = document.getElementById("info-accion");
  var infoModelo = document.getElementById("info-modelo");

  if (!result) {
    card.className = "status-card loading";
    icon.textContent = "🔍";
    title.textContent = "Sin datos";
    subtitle.textContent = "Navega a una página para analizarla";
    riskPct.textContent = "–";
    riskBar.style.width = "0%";
    infoUrl.textContent = "–";
    infoUrl.className = "info-value muted";
    infoClasificacion.textContent = "–";
    infoAccion.textContent = "–";
    infoModelo.textContent = "–";
    return;
  }

  var level = getRiskLevel(result.riesgo);
  card.className = "status-card " + level;
  icon.textContent = getRiskIcon(result.clasificacion, result.riesgo);
  title.textContent = getRiskTitle(result.clasificacion, result.riesgo);
  subtitle.textContent = getRiskSubtitle(result.clasificacion, result.riesgo);
  riskPct.textContent = result.riesgo + "%";
  riskBar.style.width = result.riesgo + "%";
  infoUrl.textContent = truncateUrl(result.url);
  infoUrl.className = "info-value";
  infoUrl.title = result.url;
  infoClasificacion.textContent = result.clasificacion || "–";
  infoClasificacion.className = "info-value " + getClasificacionClass(result.clasificacion, result.accion);
  infoAccion.textContent = result.accion || "–";
  infoAccion.className = "info-value " + getAccionClass(result.accion);
  infoModelo.textContent = getModelLabel(result.modelo);
}

async function checkBackendStatus() {
  var statusEl = document.getElementById("backend-status");
  var labelEl = document.getElementById("backend-label");
  try {
    var resp = await fetch(API_BASE + "/health", { signal: AbortSignal.timeout(3000) });
    var data = await resp.json();
    statusEl.className = "backend-status online";
    var modelLabel = data.modelo === "random_forest" ? "ML activo" : "Modo heurístico";
    labelEl.textContent = "Backend online · " + modelLabel;
  } catch(e) {
    statusEl.className = "backend-status offline";
    labelEl.textContent = "Backend offline — Inicia el servidor Python";
  }
}

async function loadCurrentResult() {
  var data = await chrome.storage.local.get(["ultimo_resultado"]);
  renderStatus(data.ultimo_resultado || null);
}

async function reanalyzeCurrentTab() {
  var btnRe = document.getElementById("btn-reanalizar");
  btnRe.disabled = true;
  btnRe.innerHTML = '<span class="loading-spinner"></span> Analizando...';
  try {
    var tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    var url = tabs[0] && tabs[0].url;
    if (!url) throw new Error("No URL");
    var result = await chrome.runtime.sendMessage({ type: "ANALYZE_URL", url: url });
    if (result) renderStatus(result);
  } catch(err) {
    console.error("Error re-analizando:", err);
  } finally {
    btnRe.disabled = false;
    btnRe.innerHTML = "🔄 Re-analizar página actual";
  }
}

async function clearHistory() {
  if (!confirm("¿Eliminar todo el historial de análisis?")) return;
  try {
    await fetch(API_BASE + "/historial", {
      method: "DELETE",
      signal: AbortSignal.timeout(4000),
    });
    // También limpiar el último resultado guardado localmente
    await chrome.storage.local.remove(["ultimo_resultado"]);
    loadHistory();
    renderStatus(null);
  } catch(e) {
    alert("Error al limpiar el historial. Verifica que el backend esté activo.");
  }
}

async function loadHistory() {
  var listEl = document.getElementById("history-list");
  listEl.innerHTML = '<div class="empty-history">Cargando...</div>';
  try {
    var resp = await fetch(API_BASE + "/historial?limit=30", { signal: AbortSignal.timeout(4000) });
    var items = await resp.json();
    if (!items.length) {
      listEl.innerHTML = '<div class="empty-history">Sin historial aún</div>';
      return;
    }
    listEl.innerHTML = items.map(function(item) {
      var level = getRiskLevel(item.riesgo);
      var domain = item.url;
      try { domain = new URL(item.url).hostname; } catch(e) {}
      return '<div class="history-item">' +
        '<span class="h-dot ' + level + '"></span>' +
        '<span class="h-url" title="' + item.url + '">' + domain + '</span>' +
        '<span class="h-badge ' + level + '">' + item.clasificacion + '</span>' +
        '<span style="font-size:10px;font-weight:700;color:' + (level === 'danger' ? 'var(--red)' : level === 'warning' ? 'var(--yellow)' : 'var(--green)') + '">' + item.riesgo + '%</span>' +
        '</div>';
    }).join("");
  } catch(e) {
    listEl.innerHTML = '<div class="empty-history">No se pudo cargar el historial</div>';
  }
}

async function analyzeManualUrl() {
  var input = document.getElementById("manual-url-input");
  var resultEl = document.getElementById("manual-result");
  var btn = document.getElementById("btn-manual-analyze");
  var url = input.value.trim();
  if (!url) return;
  if (!url.startsWith("http://") && !url.startsWith("https://")) {
    url = "https://" + url;
    input.value = url;
  }
  btn.disabled = true;
  btn.textContent = "Analizando...";
  resultEl.classList.remove("hidden");
  resultEl.textContent = "Consultando al modelo...";
  resultEl.style.color = "var(--text-muted)";
  resultEl.style.borderColor = "var(--border)";
  try {
    var resp = await fetch(API_BASE + "/analizar-url", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: url, guardar: true }),
      signal: AbortSignal.timeout(8000),
    });
    var data = await resp.json();
    var level = getRiskLevel(data.riesgo);
    var colorMap = { safe: "var(--green)", warning: "var(--yellow)", danger: "var(--red)" };
    resultEl.style.borderColor = colorMap[level];
    resultEl.innerHTML = '<strong style="color:' + colorMap[level] + '">' + getRiskIcon(data.clasificacion, data.riesgo) + ' ' + data.clasificacion + '</strong>' +
      ' — Riesgo: <strong style="color:' + colorMap[level] + '">' + data.riesgo + '%</strong>' +
      ' · Acción: <strong>' + data.accion + '</strong>';
  } catch(e) {
    resultEl.textContent = "❌ Error al conectar con el backend";
    resultEl.style.color = "var(--red)";
    resultEl.style.borderColor = "var(--red-border)";
  } finally {
    btn.disabled = false;
    btn.textContent = "🔍 Analizar";
  }
}

function initTabs() {
  document.querySelectorAll(".tab").forEach(function(tab) {
    tab.addEventListener("click", function() {
      var target = tab.dataset.tab;
      document.querySelectorAll(".tab").forEach(function(t) { t.classList.remove("active"); });
      document.querySelectorAll(".tab-content").forEach(function(c) { c.classList.remove("active"); });
      tab.classList.add("active");
      document.getElementById("tab-" + target).classList.add("active");
      if (target === "history") loadHistory();
    });
  });
}

async function initProtectionToggle() {
  var btn = document.getElementById("btn-toggle-protection");
  var data = await chrome.storage.local.get(["proteccion_activa"]);
  var active = data.proteccion_activa !== false;
  btn.textContent = active ? "🔒 Protección activa" : "🔓 Protección inactiva";
  btn.style.color = active ? "var(--green)" : "var(--red)";
  btn.addEventListener("click", async function() {
    var cur = await chrome.storage.local.get(["proteccion_activa"]);
    var newState = !(cur.proteccion_activa !== false);
    await chrome.storage.local.set({ proteccion_activa: newState });
    btn.textContent = newState ? "🔒 Protección activa" : "🔓 Protección inactiva";
    btn.style.color = newState ? "var(--green)" : "var(--red)";
  });
}

document.addEventListener("DOMContentLoaded", async function() {
  initTabs();
  initProtectionToggle();
  await Promise.all([loadCurrentResult(), checkBackendStatus()]);

  document.getElementById("btn-reanalizar").addEventListener("click", reanalyzeCurrentTab);

  document.getElementById("btn-settings").addEventListener("click", function() {
    chrome.tabs.create({ url: chrome.runtime.getURL("settings.html") });
  });

  document.getElementById("btn-clear-history").addEventListener("click", clearHistory);
  document.getElementById("btn-manual-analyze").addEventListener("click", analyzeManualUrl);
  document.getElementById("manual-url-input").addEventListener("keydown", function(e) {
    if (e.key === "Enter") analyzeManualUrl();
  });
});