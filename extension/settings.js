async function loadSettings() {
  var data = await chrome.storage.local.get([
    "proteccion_activa", "bloqueo_auto", "mostrar_advertencias", "device_id"
  ]);
  document.getElementById("toggle-protection").checked = data.proteccion_activa !== false;
  document.getElementById("toggle-block").checked = data.bloqueo_auto !== false;
  document.getElementById("toggle-notif").checked = data.mostrar_advertencias !== false;
  var deviceEl = document.getElementById("device-id-display");
  if (deviceEl) deviceEl.textContent = data.device_id || "–";
}

document.getElementById("btn-save").addEventListener("click", async function() {
  await chrome.storage.local.set({
    proteccion_activa: document.getElementById("toggle-protection").checked,
    bloqueo_auto: document.getElementById("toggle-block").checked,
    mostrar_advertencias: document.getElementById("toggle-notif").checked,
  });
  var msg = document.getElementById("success-msg");
  msg.style.display = "block";
  setTimeout(function() { msg.style.display = "none"; }, 2500);
});

document.addEventListener("DOMContentLoaded", loadSettings);