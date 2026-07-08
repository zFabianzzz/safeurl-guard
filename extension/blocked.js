const params = new URLSearchParams(window.location.search);
const url = decodeURIComponent(params.get("url") || "");
const riesgo = parseInt(params.get("riesgo") || "0");
const tipo = params.get("tipo") || "Desconocido";

document.getElementById("info-url").textContent = url || "URL desconocida";
document.getElementById("info-tipo").textContent = tipo;
document.getElementById("info-fecha").textContent = new Date().toLocaleString("es-PE");
document.getElementById("risk-pct").textContent = riesgo + "%";

setTimeout(function() {
  document.getElementById("risk-bar").style.width = riesgo + "%";
}, 100);

if (tipo === "Malware") {
  document.getElementById("shield-icon").textContent = "☠️";
} else if (tipo === "Defacement") {
  document.getElementById("shield-icon").textContent = "💀";
}

document.getElementById("btn-back").addEventListener("click", function() {
  if (history.length > 1) {
    history.back();
  } else {
    window.location.href = "https://www.google.com";
  }
});

document.getElementById("btn-continue").addEventListener("click", function() {
  if (!url) return;
  if (confirm("⚠️ Estás a punto de acceder a un sitio clasificado como " + tipo + " con " + riesgo + "% de riesgo.\n\n¿Deseas continuar de todas formas?")) {
    // Avisar al background que el usuario aprobó esta URL para no re-bloquearla
    chrome.runtime.sendMessage({ type: "ALLOW_URL", url: url }, function() {
      window.location.href = url;
    });
  }
});