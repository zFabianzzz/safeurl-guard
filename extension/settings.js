const API_BASE = "https://safeurl-guard.onrender.com";

async function loadSettings() {
  var data = await chrome.storage.local.get([
    "proteccion_activa", "bloqueo_auto", "mostrar_advertencias", "device_id", "device_name"
  ]);
  document.getElementById("toggle-protection").checked = data.proteccion_activa !== false;
  document.getElementById("toggle-block").checked = data.bloqueo_auto !== false;
  document.getElementById("toggle-notif").checked = data.mostrar_advertencias !== false;

  var deviceEl = document.getElementById("device-id-display");
  if (deviceEl) deviceEl.textContent = data.device_id || "–";

  var nameEl = document.getElementById("device-name-input");
  if (nameEl) nameEl.value = data.device_name || "";
}

document.getElementById("btn-save").addEventListener("click", async function() {
  var nameEl = document.getElementById("device-name-input");
  var nombre = nameEl ? nameEl.value.trim() : "";

  await chrome.storage.local.set({
    proteccion_activa: document.getElementById("toggle-protection").checked,
    bloqueo_auto: document.getElementById("toggle-block").checked,
    mostrar_advertencias: document.getElementById("toggle-notif").checked,
    device_name: nombre,
  });

  if (nombre) {
    var stored = await chrome.storage.local.get(["device_id"]);
    try {
      await fetch(API_BASE + "/dispositivo/nombre", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ device_id: stored.device_id, nombre: nombre }),
        signal: AbortSignal.timeout(5000),
      });
    } catch (e) {
      console.error("[SafeURL Guard] No se pudo actualizar el nombre en el servidor:", e.message);
    }
  }

  var msg = document.getElementById("success-msg");
  msg.style.display = "block";
  setTimeout(function() { msg.style.display = "none"; }, 2500);
});

document.addEventListener("DOMContentLoaded", loadSettings);