const params = new URLSearchParams(window.location.search);
const url = decodeURIComponent(params.get("url") || "");
const riesgo = parseInt(params.get("riesgo") || "0");
const tipo = params.get("tipo") || "Desconocido";

document.getElementById("info-url").textContent = url || "URL desconocida";
document.getElementById("info-tipo").textContent = tipo;
document.getElementById("info-fecha").textContent = new Date().toLocaleString("es-PE");
document.getElementById("risk-pct").textContent = riesgo + "%";

setTimeout(() => {
  document.getElementById("risk-bar").style.width = riesgo + "%";
}, 100);

// ¿Es un bloqueo manual del administrador (blacklist) en vez de una
// clasificación del modelo de Machine Learning?
const esBloqueoAdmin = tipo.toLowerCase().includes("admin");

if (tipo === "Malware") {
  document.getElementById("shield-icon").textContent = "";
} else if (tipo === "Defacement") {
  document.getElementById("shield-icon").textContent = "";
} else if (esBloqueoAdmin) {
  document.getElementById("shield-icon").textContent = "🔒";
}

if (esBloqueoAdmin) {
  // ── Bloqueo por regla del administrador ──
  // Morado, sin ningún botón de salida ni de continuar: es una regla fija,
  // no una probabilidad que el usuario pueda decidir saltarse.

  document.getElementById("btn-continue").style.display = "none";
  document.getElementById("btn-back").style.display = "none";
  document.getElementById("admin-block-note").style.display = "block";

  // Inyectamos estilos morados sin tocar blocked.css, para no arriesgar
  // romper el archivo de estilos original.
  const style = document.createElement("style");
  style.textContent = `
    .card-header { background: linear-gradient(180deg, rgba(168,85,247,0.18), rgba(88,28,135,0.06)) !important; }
    .card { border-color: rgba(168,85,247,0.35) !important; }
    h1 { color: #a855f7 !important; }
    .info-value.orange { color: #c084fc !important; }
    .info-value.danger { color: #c084fc !important; }
    .risk-bar-fill { background: linear-gradient(90deg, #7e22ce, #a855f7) !important; }
    .risk-pct { color: #a855f7 !important; }
    #admin-block-note { color: #c084fc !important; }
  `;
  document.head.appendChild(style);
} else {
  // ── Bloqueo por el modelo de ML ──
  // Es una probabilidad, no una certeza absoluta, así que se le permite
  // al usuario decidir bajo su propio riesgo.

  document.getElementById("btn-back").addEventListener("click", () => {
    if (history.length > 1) {
      history.back();
    } else {
      window.location.href = "https://www.google.com";
    }
  });

  document.getElementById("btn-continue").addEventListener("click", () => {
    if (!url) return;
    if (confirm(`⚠️ Estás a punto de acceder a un sitio clasificado como "${tipo}" con ${riesgo}% de riesgo.\n\n¿Deseas continuar de todas formas?`)) {
      // Avisar a background.js que esta URL fue permitida por el usuario,
      // para que no la vuelva a bloquear al navegar hacia ella.
      chrome.runtime.sendMessage({ type: "ALLOW_URL", url: url }, () => {
        window.location.href = url;
      });
    }
  });
}